from __future__ import annotations

import os
import time
from dataclasses import dataclass

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


def enable_gpu_perf_knobs() -> None:
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        try:
            torch.set_float32_matmul_precision(os.getenv("MM_PRECISION", "high"))
        except Exception:
            pass


@dataclass
class Cfg:
    batch: int = int(os.getenv("BATCH", "1024"))
    steps: int = int(os.getenv("STEPS", "200"))
    dim: int = int(os.getenv("DIM", "1024"))
    classes: int = int(os.getenv("CLASSES", "1000"))
    amp: bool = bool(int(os.getenv("AMP", "1")))
    workers: int = int(os.getenv("WORKERS", "4"))
    pin_memory: bool = bool(int(os.getenv("PIN_MEMORY", "1")))
    prefetch: int = int(os.getenv("PREFETCH", "2"))
    persistent: bool = bool(int(os.getenv("PERSISTENT_WORKERS", "1")))
    compile_mode: str = os.getenv("COMPILE_MODE", "max-autotune")
    channels_last: bool = bool(int(os.getenv("CHANNELS_LAST", "1")))
    seed: int = int(os.getenv("SEED", "0"))


class ToyDS(Dataset):
    def __init__(self, n: int, d: int, c: int, seed: int) -> None:
        g = torch.Generator().manual_seed(seed)
        self.x = torch.randn(n, d, generator=g)
        self.y = (self.x @ torch.randn(d, c, generator=g)).argmax(dim=1)
    def __len__(self) -> int: return self.x.size(0)
    def __getitem__(self, i: int): return self.x[i], self.y[i]


class MLP(nn.Module):
    def __init__(self, d: int, c: int) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, 4096), nn.ReLU(True), nn.Linear(4096, 2048), nn.ReLU(True), nn.Linear(2048, c))
    def forward(self, x: torch.Tensor) -> torch.Tensor: return self.net(x)


def maybe_compile(model: nn.Module, mode: str) -> nn.Module:
    if hasattr(torch, "compile"):
        try:
            return torch.compile(model, mode=mode)
        except Exception:
            return model
    return model


def main() -> None:
    cfg = Cfg()
    torch.manual_seed(cfg.seed)
    enable_gpu_perf_knobs()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # DataLoader tuned for HtoD overlap and host pinning
    ds = ToyDS(cfg.batch * 40, cfg.dim, cfg.classes, cfg.seed)
    loader = DataLoader(
        ds,
        batch_size=cfg.batch,
        shuffle=True,
        num_workers=cfg.workers,
        pin_memory=cfg.pin_memory,
        persistent_workers=cfg.persistent if cfg.workers > 0 else False,
        prefetch_factor=cfg.prefetch if cfg.workers > 0 else None,  # type: ignore[arg-type]
        drop_last=True,
    )

    model = MLP(cfg.dim, cfg.classes).to(device)
    model = maybe_compile(model, cfg.compile_mode)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-2, fused=(device == "cuda"))
    crit = nn.CrossEntropyLoss()
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.amp and device == "cuda")

    num_items = 0
    start = time.perf_counter()
    for step, (xb, yb) in enumerate(loader):
        # Efficient HtoD: pin memory + non_blocking
        if device == "cuda":
            if cfg.pin_memory:
                xb = xb.pin_memory() if not xb.is_pinned() else xb
                yb = yb.pin_memory() if not yb.is_pinned() else yb
        xb = xb.to(device, non_blocking=True)
        yb = yb.to(device, non_blocking=True)

        with torch.cuda.amp.autocast(enabled=cfg.amp and device == "cuda"):
            logits = model(xb)
            loss = crit(logits, yb)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt)
        scaler.update()
        opt.zero_grad(set_to_none=True)

        num_items += xb.size(0)
        if step + 1 >= cfg.steps:
            break

    if device == "cuda":
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    print(f"items={num_items} time_s={elapsed:.2f} items_per_s={num_items/elapsed:.1f} amp={cfg.amp} tf32={getattr(torch.backends.cuda.matmul, 'allow_tf32', False)}")


if __name__ == "__main__":
    main()



