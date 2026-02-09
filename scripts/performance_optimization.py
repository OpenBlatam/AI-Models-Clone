from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def enable_perf_knobs() -> None:
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        try:
            torch.set_float32_matmul_precision(os.getenv("MM_PRECISION", "high"))
        except Exception:
            pass


@dataclass
class OptimCfg:
    batch: int = int(os.getenv("BATCH", "512"))
    steps: int = int(os.getenv("STEPS", "300"))
    lr: float = float(os.getenv("LR", "3e-4"))
    wd: float = float(os.getenv("WD", "1e-2"))
    amp: bool = bool(int(os.getenv("AMP", "1")))
    img_size: int = int(os.getenv("SIZE", "128"))
    channels: int = int(os.getenv("CHANNELS", "3"))
    classes: int = int(os.getenv("CLASSES", "100"))
    workers: int = int(os.getenv("WORKERS", "4"))
    pin_memory: bool = bool(int(os.getenv("PIN", "1")))
    prefetch: int = int(os.getenv("PREFETCH", "2"))
    persistent: bool = bool(int(os.getenv("PERSISTENT", "1")))
    compile_mode: str = os.getenv("COMPILE_MODE", "max-autotune")
    fused_adamw: bool = bool(int(os.getenv("FUSED_ADAMW", "1")))
    channels_last: bool = bool(int(os.getenv("CHANNELS_LAST", "1")))
    seed: int = int(os.getenv("SEED", "0"))


class RandImageDS(Dataset):
    def __init__(self, n: int, c: int, h: int, w: int, seed: int) -> None:
        g = torch.Generator().manual_seed(seed)
        self.x = torch.randn(n, c, h, w, generator=g)
        self.y = torch.randint(0, 1000, (n,), generator=g)

    def __len__(self) -> int: return self.x.size(0)
    def __getitem__(self, i: int): return self.x[i], self.y[i]


class SmallCNN(nn.Module):
    def __init__(self, c: int, num_classes: int) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(c, 64, 7, stride=2, padding=3), nn.ReLU(inplace=True), nn.MaxPool2d(3, stride=2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(inplace=True), nn.MaxPool2d(2),
            nn.Conv2d(128, 256, 3, padding=1), nn.ReLU(inplace=True), nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Linear(256, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = x.flatten(1)
        return self.classifier(x)


def maybe_compile(model: nn.Module, mode: str) -> nn.Module:
    if hasattr(torch, "compile"):
        try:
            return torch.compile(model, mode=mode)
        except Exception:
            return model
    return model


def build_loader(cfg: OptimCfg) -> DataLoader:
    ds = RandImageDS(cfg.batch * 20, cfg.channels, cfg.img_size, cfg.img_size, seed=cfg.seed)
    return DataLoader(
        ds,
        batch_size=cfg.batch,
        shuffle=True,
        num_workers=cfg.workers,
        pin_memory=cfg.pin_memory,
        persistent_workers=cfg.persistent if cfg.workers > 0 else False,
        prefetch_factor=cfg.prefetch if cfg.workers > 0 else None,  # type: ignore[arg-type]
        drop_last=True,
    )


def main() -> None:
    cfg = OptimCfg()
    torch.manual_seed(cfg.seed)
    enable_perf_knobs()
    device = get_device()

    model = SmallCNN(cfg.channels, cfg.classes).to(device)
    if cfg.channels_last and device == "cuda":
        model = model.to(memory_format=torch.channels_last)
    model = maybe_compile(model, cfg.compile_mode)

    # Fused AdamW if supported (PyTorch 2.2+ on CUDA)
    fused_kw = {"fused": True} if (cfg.fused_adamw and device == "cuda") else {}
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.wd, **fused_kw)
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.amp and device == "cuda")
    loss_fn = nn.CrossEntropyLoss()

    loader = build_loader(cfg)
    start = time.perf_counter()
    num_items = 0
    for step, (xb, yb) in enumerate(loader):
        if cfg.channels_last and device == "cuda":
            xb = xb.to(memory_format=torch.channels_last)
        if device == "cuda":
            xb = xb.pin_memory() if not xb.is_pinned() else xb
            yb = yb.pin_memory() if not yb.is_pinned() else yb
        xb = xb.to(device, non_blocking=True)
        yb = yb.to(device, non_blocking=True)

        with torch.cuda.amp.autocast(enabled=cfg.amp and device == "cuda"):
            logits = model(xb)
            loss = loss_fn(logits, yb)
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)

        num_items += xb.size(0)
        if step + 1 >= cfg.steps:
            break

    if device == "cuda":
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    print(f"items={num_items} time_s={elapsed:.2f} items_per_s={num_items/elapsed:.1f}")


if __name__ == "__main__":
    main()



