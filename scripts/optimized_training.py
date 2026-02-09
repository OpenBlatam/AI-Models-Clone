from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Iterable, Iterator, Tuple

import torch
from torch import nn
from torch.utils.data import DataLoader

# Ensure project root on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.data.synthetic import build_dataloaders
from src.models.mlp_classifier import MLPClassifier


@dataclass
class OptConfig:
    epochs: int = 5
    batch_size: int = 512
    learning_rate: float = 3e-4
    weight_decay: float = 0.01
    grad_accum_steps: int = 1
    grad_clip_norm: float = 1.0
    num_workers: int = max(2, (os.cpu_count() or 4) // 2)
    pin_memory: bool = True
    persistent_workers: bool = True
    prefetch_factor: int = 4
    use_amp: bool = True
    prefer_bf16: bool = True
    use_compile: bool = True
    allow_tf32: bool = True
    input_dim: int = 128
    num_classes: int = 10


class CUDAPrefetcher:
    def __init__(self, loader: DataLoader, device: torch.device) -> None:
        self.loader = loader
        self.device = device
        self.stream = torch.cuda.Stream(device=self.device)
        self.it: Iterator = iter(self.loader)
        self._next: Tuple[torch.Tensor, torch.Tensor] | None = None
        self._preload()

    def _preload(self) -> None:
        try:
            batch = next(self.it)
        except StopIteration:
            self._next = None
            return
        with torch.cuda.stream(self.stream):
            xb, yb = batch
            xb = xb.to(self.device, non_blocking=True)
            yb = yb.to(self.device, non_blocking=True)
            self._next = (xb, yb)

    def __iter__(self) -> "CUDAPrefetcher":
        return self

    def __next__(self) -> Tuple[torch.Tensor, torch.Tensor]:
        torch.cuda.current_stream(self.device).wait_stream(self.stream)
        if self._next is None:
            raise StopIteration
        batch = self._next
        self._preload()
        return batch


def set_global_optimizations(cfg: OptConfig, device: torch.device) -> None:
    if device.type == "cuda":
        if cfg.allow_tf32:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.benchmark = True
        # PyTorch 2.0+ matmul precision hint for Ampere+ GPUs
        try:
            torch.set_float32_matmul_precision("high")
        except Exception:
            pass


def build_loaders(cfg: OptConfig, device: torch.device) -> Tuple[Iterable, DataLoader]:
    train_loader, val_loader = build_dataloaders(
        train_samples=80_000,
        val_samples=8_000,
        input_dim=cfg.input_dim,
        num_classes=cfg.num_classes,
        batch_size=cfg.batch_size,
        num_workers=cfg.num_workers,
        pin_memory=(cfg.pin_memory and device.type == "cuda"),
        persistent_workers=(cfg.persistent_workers and cfg.num_workers > 0),
        prefetch_factor=cfg.prefetch_factor,
    )
    if device.type == "cuda":
        return CUDAPrefetcher(train_loader, device), val_loader
    return train_loader, val_loader


def main() -> None:
    ap = argparse.ArgumentParser(description="Optimized training entrypoint")
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--batch-size", type=int, default=512)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--weight-decay", type=float, default=0.01)
    ap.add_argument("--accum", type=int, default=1)
    ap.add_argument("--grad-clip", type=float, default=1.0)
    ap.add_argument("--num-workers", type=int, default=max(2, (os.cpu_count() or 4) // 2))
    ap.add_argument("--no-amp", dest="use_amp", action="store_false")
    ap.add_argument("--bf16", action="store_true")
    ap.add_argument("--no-compile", dest="use_compile", action="store_false")
    ap.add_argument("--no-tf32", dest="allow_tf32", action="store_false")
    args = ap.parse_args()

    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")
    cfg = OptConfig(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        weight_decay=args.weight_decay,
        grad_accum_steps=args.accum,
        grad_clip_norm=args.grad_clip,
        num_workers=args.num_workers,
        use_amp=args.use_amp,
        prefer_bf16=args.bf16,
        use_compile=args.use_compile,
        allow_tf32=args.allow_tf32,
    )

    set_global_optimizations(cfg, device)

    train_iterable, val_loader = build_loaders(cfg, device)

    model = MLPClassifier(cfg.input_dim, [512, 512], cfg.num_classes, 0.0).to(device)
    if cfg.use_compile and hasattr(torch, "compile"):
        try:
            model = torch.compile(model, mode="max-autotune")  # type: ignore[assignment]
        except Exception:
            pass

    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay, foreach=True)
    loss_fn = nn.CrossEntropyLoss()

    amp_enabled = (cfg.use_amp and device.type == "cuda")
    use_bf16 = (amp_enabled and cfg.prefer_bf16 and torch.cuda.is_bf16_supported())
    amp_dtype = torch.bfloat16 if use_bf16 else torch.float16
    scaler = torch.cuda.amp.GradScaler(enabled=(amp_enabled and amp_dtype == torch.float16))

    for epoch in range(cfg.epochs):
        model.train()
        running = 0.0
        optimizer.zero_grad(set_to_none=True)

        for step, (xb, yb) in enumerate(train_iterable, start=1):
            with torch.cuda.amp.autocast(enabled=amp_enabled, dtype=amp_dtype):
                logits = model(xb)
                loss = loss_fn(logits, yb) / max(1, cfg.grad_accum_steps)

            scaler.scale(loss).backward()

            if step % cfg.grad_accum_steps == 0:
                scaler.unscale_(optimizer)
                nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip_norm)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)

            running += float(loss.item())

        # validation
        model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb = xb.to(device, non_blocking=True)
                yb = yb.to(device, non_blocking=True)
                logits = model(xb)
                total_loss += float(loss_fn(logits, yb).item())
                correct += (logits.argmax(-1) == yb).sum().item()
                total += yb.size(0)
        val_loss = total_loss / max(len(val_loader), 1)
        val_acc = correct / max(total, 1)
        print(f"epoch={epoch} train_loss={running/max(1,len(getattr(train_iterable,'loader',val_loader))):.4f} val_loss={val_loss:.4f} val_acc={val_acc:.4f}")


if __name__ == "__main__":
    main()



