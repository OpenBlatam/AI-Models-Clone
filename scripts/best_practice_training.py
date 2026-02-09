from __future__ import annotations

import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, random_split

from src.utils.tracking import Tracker, TrackingConfig
from src.utils.checkpoint import CheckpointManager, CheckpointConfig


def seed_everything(seed: int) -> None:
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def enable_perf() -> None:
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        try:
            torch.set_float32_matmul_precision("high")
        except Exception:
            pass


@dataclass
class Cfg:
    input_dim: int = int(os.getenv("INPUT_DIM", "128"))
    hidden: Tuple[int, int] = tuple(int(x) for x in os.getenv("HIDDEN", "256,256").split(","))  # type: ignore[assignment]
    num_classes: int = int(os.getenv("NUM_CLASSES", "10"))
    dropout: float = float(os.getenv("DROPOUT", "0.0"))

    samples: int = int(os.getenv("SAMPLES", "20000"))
    val_ratio: float = float(os.getenv("VAL_RATIO", "0.1"))
    batch: int = int(os.getenv("BATCH", "256"))
    workers: int = int(os.getenv("WORKERS", "4"))
    pin_memory: bool = bool(int(os.getenv("PIN_MEMORY", "1")))
    persistent_workers: bool = bool(int(os.getenv("PERSISTENT_WORKERS", "1")))
    prefetch: int = int(os.getenv("PREFETCH", "2"))

    epochs: int = int(os.getenv("EPOCHS", "8"))
    lr: float = float(os.getenv("LR", "3e-4"))
    wd: float = float(os.getenv("WD", "1e-2"))
    clip: float = float(os.getenv("CLIP", "1.0"))
    amp: bool = bool(int(os.getenv("AMP", "1")))
    accum: int = int(os.getenv("ACCUM", "1"))

    warmup_ratio: float = float(os.getenv("WARMUP_RATIO", "0.05"))
    channels_last: bool = bool(int(os.getenv("CHANNELS_LAST", "0")))
    compile_mode: str = os.getenv("COMPILE_MODE", "max-autotune")

    log_dir: str = os.getenv("LOG_DIR", "experiments/best_practice")
    ckpt_dir: str = os.getenv("CKPT_DIR", "checkpoints/best_practice")
    seed: int = int(os.getenv("SEED", "42"))


class SyntheticDS(Dataset):
    def __init__(self, n: int, d: int, c: int, seed: int) -> None:
        g = torch.Generator().manual_seed(seed)
        self.x = torch.randn(n, d, generator=g)
        W = torch.randn(c, d, generator=g)
        self.y = (self.x @ W.T).argmax(dim=1)
    def __len__(self) -> int: return self.x.size(0)
    def __getitem__(self, i: int): return self.x[i], self.y[i]


class MLP(nn.Module):
    def __init__(self, d: int, hidden: Tuple[int, ...], c: int, p: float) -> None:
        super().__init__()
        layers = []
        prev = d
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU(inplace=True)]
            if p > 0: layers += [nn.Dropout(p)]
            prev = h
        layers += [nn.Linear(prev, c)]
        self.net = nn.Sequential(*layers)
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, a=math.sqrt(5))
                if m.bias is not None:
                    fan_in, _ = nn.init._calculate_fan_in_and_fan_out(m.weight)
                    bound = 1 / math.sqrt(max(fan_in, 1))
                    nn.init.uniform_(m.bias, -bound, bound)
    def forward(self, x): return self.net(x)


class EarlyStopping:
    def __init__(self, patience: int = 3) -> None:
        self.best = float("inf")
        self.bad = 0
        self.patience = patience
    def step(self, val_loss: float) -> bool:
        if val_loss < self.best - 1e-8:
            self.best = val_loss
            self.bad = 0
            return False
        self.bad += 1
        return self.bad > self.patience


def build_loaders(cfg: Cfg) -> tuple[DataLoader, DataLoader]:
    ds = SyntheticDS(cfg.samples, cfg.input_dim, cfg.num_classes, cfg.seed)
    val_len = max(1, int(len(ds) * cfg.val_ratio))
    train_len = len(ds) - val_len
    train_ds, val_ds = random_split(ds, [train_len, val_len], generator=torch.Generator().manual_seed(cfg.seed))
    train_loader = DataLoader(
        train_ds, batch_size=cfg.batch, shuffle=True, num_workers=cfg.workers, pin_memory=cfg.pin_memory,
        persistent_workers=cfg.persistent_workers if cfg.workers > 0 else False,
        prefetch_factor=cfg.prefetch if cfg.workers > 0 else None, drop_last=True,  # type: ignore[arg-type]
    )
    val_loader = DataLoader(
        val_ds, batch_size=cfg.batch, shuffle=False, num_workers=cfg.workers, pin_memory=cfg.pin_memory,
        persistent_workers=cfg.persistent_workers if cfg.workers > 0 else False,
        prefetch_factor=cfg.prefetch if cfg.workers > 0 else None,  # type: ignore[arg-type]
    )
    return train_loader, val_loader


def make_warmup_cosine(optimizer: torch.optim.Optimizer, warmup_steps: int, total_steps: int):
    def lr_lambda(step: int) -> float:
        if step < warmup_steps:
            return max(1e-8, step / max(1, warmup_steps))
        progress = (step - warmup_steps) / max(1, (total_steps - warmup_steps))
        return 0.5 * (1.0 + math.cos(math.pi * min(max(progress, 0.0), 1.0)))
    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lr_lambda)


def maybe_compile(model: nn.Module, mode: str) -> nn.Module:
    if hasattr(torch, "compile"):
        try:
            return torch.compile(model, mode=mode)
        except Exception:
            return model
    return model


def main() -> None:
    cfg = Cfg()
    seed_everything(cfg.seed)
    enable_perf()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    train_loader, val_loader = build_loaders(cfg)
    model = MLP(cfg.input_dim, cfg.hidden, cfg.num_classes, cfg.dropout).to(device)
    if cfg.channels_last and device == "cuda":
        model = model.to(memory_format=torch.channels_last)
    model = maybe_compile(model, cfg.compile_mode)

    fused_kw = {"fused": True} if (device == "cuda") else {}
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.wd, **fused_kw)
    loss_fn = nn.CrossEntropyLoss()

    total_steps = math.ceil(len(train_loader) / max(1, cfg.accum)) * cfg.epochs
    warmup_steps = int(total_steps * cfg.warmup_ratio)
    scheduler = make_warmup_cosine(optimizer, warmup_steps, total_steps)
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.amp and device == "cuda")
    stopper = EarlyStopping(patience=3)

    tracker = Tracker(TrackingConfig(tensorboard=True, log_dir=cfg.log_dir, use_wandb=False))
    tracker.start()
    ckpt = CheckpointManager(CheckpointConfig(directory=cfg.ckpt_dir, monitor="val/loss", mode="min", save_top_k=1, save_every=1))

    global_step = 0
    for epoch in range(cfg.epochs):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        running = 0.0
        correct = 0
        seen = 0
        for step, (xb, yb) in enumerate(train_loader):
            if cfg.channels_last and device == "cuda":
                xb = xb.to(memory_format=torch.channels_last)
            xb = xb.to(device, non_blocking=True)
            yb = yb.to(device, non_blocking=True)
            with torch.cuda.amp.autocast(enabled=cfg.amp and device == "cuda"):
                logits = model(xb)
                loss = loss_fn(logits, yb) / cfg.accum
            scaler.scale(loss).backward()
            if (step + 1) % cfg.accum == 0:
                scaler.unscale_(optimizer)
                if cfg.clip > 0:
                    nn.utils.clip_grad_norm_(model.parameters(), cfg.clip)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)
                scheduler.step()
                global_step += 1
            running += float(loss) * xb.size(0)
            correct += int((logits.argmax(dim=1) == yb).sum())
            seen += xb.size(0)

        train_loss = running / max(1, seen)
        train_acc = correct / max(1, seen)

        model.eval()
        v_loss = 0.0
        v_corr = 0
        v_seen = 0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb = xb.to(device, non_blocking=True)
                yb = yb.to(device, non_blocking=True)
                logits = model(xb)
                loss = loss_fn(logits, yb)
                v_loss += float(loss) * xb.size(0)
                v_corr += int((logits.argmax(dim=1) == yb).sum())
                v_seen += xb.size(0)
        val_loss = v_loss / max(1, v_seen)
        val_acc = v_corr / max(1, v_seen)

        tracker.log_metrics({"train/loss": train_loss, "train/acc": train_acc, "val/loss": val_loss, "val/acc": val_acc}, step=epoch)
        saved = ckpt.maybe_save(epoch, {"val/loss": val_loss, "val/acc": val_acc}, model, optimizer)
        print(f"epoch={epoch} train_loss={train_loss:.4f} train_acc={train_acc:.4f} val_loss={val_loss:.4f} val_acc={val_acc:.4f} saved={saved}")
        if stopper.step(val_loss):
            break

    tracker.finish()


if __name__ == "__main__":
    main()



