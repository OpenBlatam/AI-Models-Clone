from __future__ import annotations

import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, random_split


@dataclass
class Config:
    input_dim: int = int(os.getenv("INPUT_DIM", "128"))
    hidden: Tuple[int, int] = tuple(int(x) for x in os.getenv("HIDDEN", "256,256").split(","))  # type: ignore[assignment]
    num_classes: int = int(os.getenv("NUM_CLASSES", "10"))
    dropout: float = float(os.getenv("DROPOUT", "0.0"))

    samples: int = int(os.getenv("SAMPLES", "12000"))
    val_samples: int = int(os.getenv("VAL_SAMPLES", "2000"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "256"))
    workers: int = int(os.getenv("WORKERS", "4"))
    pin_memory: bool = bool(int(os.getenv("PIN_MEMORY", "1")))

    epochs: int = int(os.getenv("EPOCHS", "10"))
    lr: float = float(os.getenv("LR", "3e-4"))
    wd: float = float(os.getenv("WD", "1e-2"))
    clip: float = float(os.getenv("CLIP", "1.0"))
    amp: bool = bool(int(os.getenv("AMP", "1")))
    accum: int = int(os.getenv("ACCUM", "1"))

    sched: str = os.getenv("SCHED", "cosine")  # cosine|steplr|reduceonplateau|none
    step_size: int = int(os.getenv("STEP_SIZE", "5"))
    gamma: float = float(os.getenv("GAMMA", "0.5"))

    patience: int = int(os.getenv("PATIENCE", "3"))
    out_dir: str = os.getenv("OUT", "checkpoints/early_stop_lr")
    seed: int = int(os.getenv("SEED", "123"))


class ToyDataset(Dataset):
    def __init__(self, n: int, d: int, c: int, seed: int) -> None:
        g = torch.Generator().manual_seed(seed)
        self.x = torch.randn(n, d, generator=g)
        W = torch.randn(c, d, generator=g)
        y_log = self.x @ W.T
        self.y = y_log.argmax(dim=1)

    def __len__(self) -> int:
        return self.x.shape[0]

    def __getitem__(self, i: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.x[i], self.y[i]


class MLP(nn.Module):
    def __init__(self, d: int, hidden: Tuple[int, ...], c: int, p: float) -> None:
        super().__init__()
        blocks = []
        prev = d
        for h in hidden:
            blocks += [nn.Linear(prev, h), nn.ReLU(inplace=True)]
            if p > 0:
                blocks += [nn.Dropout(p)]
            prev = h
        blocks += [nn.Linear(prev, c)]
        self.net = nn.Sequential(*blocks)
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, a=math.sqrt(5))
                if m.bias is not None:
                    fan_in, _ = nn.init._calculate_fan_in_and_fan_out(m.weight)
                    bound = 1 / math.sqrt(fan_in)
                    nn.init.uniform_(m.bias, -bound, bound)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class EarlyStopping:
    def __init__(self, patience: int) -> None:
        self.patience = patience
        self.best = float("inf")
        self.bad = 0

    def step(self, val_loss: float) -> bool:
        if val_loss < self.best - 1e-8:
            self.best = val_loss
            self.bad = 0
            return False
        self.bad += 1
        return self.bad > self.patience


def build_scheduler(optimizer: torch.optim.Optimizer, cfg: Config):
    s = cfg.sched.lower()
    if s == "cosine":
        return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.epochs)
    if s == "steplr":
        return torch.optim.lr_scheduler.StepLR(optimizer, step_size=cfg.step_size, gamma=cfg.gamma)
    if s == "reduceonplateau":
        return torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=cfg.gamma, patience=1)
    return None


def evaluate(model: nn.Module, loader: DataLoader, device: str) -> float:
    model.eval()
    total = 0
    loss_sum = 0.0
    crit = nn.CrossEntropyLoss()
    with torch.no_grad():
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            loss = crit(model(xb), yb)
            loss_sum += float(loss) * xb.size(0)
            total += xb.size(0)
    return loss_sum / max(1, total)


def main() -> None:
    cfg = Config()
    torch.manual_seed(cfg.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    ds = ToyDataset(cfg.samples, cfg.input_dim, cfg.num_classes, cfg.seed)
    train_len = cfg.samples - cfg.val_samples
    val_len = cfg.val_samples
    train_ds, val_ds = random_split(ds, [train_len, val_len], generator=torch.Generator().manual_seed(cfg.seed))
    train_loader = DataLoader(train_ds, batch_size=cgf.batch_size if (cgf := cfg) else cfg.batch_size, shuffle=True, num_workers=cfg.workers, pin_memory=cfg.pin_memory)
    val_loader = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=cfg.workers, pin_memory=cfg.pin_memory)

    model = MLP(cfg.input_dim, cfg.hidden, cfg.num_classes, cfg.dropout).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.wd)
    sched = build_scheduler(opt, cfg)
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.amp and device == "cuda")
    crit = nn.CrossEntropyLoss()
    stopper = EarlyStopping(cfg.patience)

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    best_path = out_dir / "best.pt"

    for epoch in range(cfg.epochs):
        model.train()
        opt.zero_grad(set_to_none=True)
        for step, (xb, yb) in enumerate(train_loader):
            xb = xb.to(device)
            yb = yb.to(device)
            with torch.cuda.amp.autocast(enabled=cfg.amp and device == "cuda"):
                loss = crit(model(xb), yb) / cfg.accum
            scaler.scale(loss).backward()

            if (step + 1) % cfg.accum == 0:
                scaler.unscale_(opt)
                nn.utils.clip_grad_norm_(model.parameters(), cfg.clip)
                scaler.step(opt)
                scaler.update()
                opt.zero_grad(set_to_none=True)

        val_loss = evaluate(model, val_loader, device)
        if isinstance(sched, torch.optim.lr_scheduler.ReduceLROnPlateau):
            sched.step(val_loss)
        elif sched is not None:
            sched.step()

        torch.save({"model": model.state_dict(), "val_loss": val_loss, "epoch": epoch}, best_path)
        print(f"epoch={epoch} val_loss={val_loss:.4f}")
        if stopper.step(val_loss):
            break


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


@dataclass
class TrainCfg:
    epochs: int = 50
    batch_size: int = 256
    learning_rate: float = 3e-4
    weight_decay: float = 0.01
    grad_clip_norm: float = 1.0
    warmup_steps: int = 1000
    max_steps: int = 20_000
    patience: int = 5
    min_delta: float = 1e-4
    amp: bool = True
    input_dim: int = 128
    num_classes: int = 10
    num_workers: int = 2


class MLP(nn.Module):
    def __init__(self, input_dim: int, hidden=(256, 256), num_classes: int = 10):
        super().__init__()
        layers: list[nn.Module] = []
        last = input_dim
        for h in hidden:
            layers += [nn.Linear(last, h), nn.GELU()]
            last = h
        layers.append(nn.Linear(last, num_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


@torch.no_grad()
def evaluate(model: nn.Module, loader: DataLoader, loss_fn: nn.Module, device: torch.device) -> dict:
    model.eval()
    loss_sum = 0.0
    correct = 0
    total = 0
    for xb, yb in loader:
        xb, yb = xb.to(device, non_blocking=True), yb.to(device, non_blocking=True)
        logits = model(xb)
        loss_sum += float(loss_fn(logits, yb))
        correct += (logits.argmax(-1) == yb).sum().item()
        total += yb.size(0)
    return {"loss": loss_sum / max(1, len(loader)), "accuracy": correct / max(1, total)}


def build_warmup_cosine(optimizer: torch.optim.Optimizer, warmup_steps: int, max_steps: int):
    def schedule(step: int) -> float:
        if step < warmup_steps:
            return (step + 1) / max(1, warmup_steps)
        progress = (step - warmup_steps) / max(1, max_steps - warmup_steps)
        progress = min(max(progress, 0.0), 1.0)
        return 0.5 * (1.0 + math.cos(math.pi * progress))
    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=schedule)


def main() -> None:
    ap = argparse.ArgumentParser(description="Early stopping + LR warmup-cosine")
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--weight-decay", type=float, default=0.01)
    ap.add_argument("--grad-clip", type=float, default=1.0)
    ap.add_argument("--warmup-steps", type=int, default=1000)
    ap.add_argument("--max-steps", type=int, default=20000)
    ap.add_argument("--patience", type=int, default=5)
    ap.add_argument("--min-delta", type=float, default=1e-4)
    args = ap.parse_args()

    cfg = TrainCfg(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        weight_decay=args.weight_decay,
        grad_clip_norm=args.grad_clip,
        warmup_steps=args.warmup_steps,
        max_steps=args.max_steps,
        patience=args.patience,
        min_delta=args.min_delta,
    )

    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")
    torch.backends.cudnn.benchmark = (device.type == "cuda")

    # synthetic classification
    n_train, n_val = 60_000, 6_000
    xtr = torch.randn(n_train, cfg.input_dim)
    w = torch.randn(cfg.input_dim, cfg.num_classes)
    ytr = torch.multinomial((xtr @ w).softmax(-1), 1).squeeze(-1)
    xva = torch.randn(n_val, cfg.input_dim)
    yva = torch.multinomial((xva @ w).softmax(-1), 1).squeeze(-1)

    train_loader = DataLoader(
        TensorDataset(xtr, ytr),
        batch_size=cfg.batch_size,
        shuffle=True,
        num_workers=cfg.num_workers,
        pin_memory=(device.type == "cuda"),
        persistent_workers=True,
        prefetch_factor=2,
    )
    val_loader = DataLoader(
        TensorDataset(xva, yva),
        batch_size=cfg.batch_size,
        shuffle=False,
        num_workers=cfg.num_workers,
        pin_memory=(device.type == "cuda"),
        persistent_workers=True,
        prefetch_factor=2,
    )

    model = MLP(cfg.input_dim, (256, 256), cfg.num_classes).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay, foreach=True)
    loss_fn = nn.CrossEntropyLoss()

    total_steps = cfg.epochs * max(1, len(train_loader)) if cfg.max_steps <= 0 else cfg.max_steps
    scheduler = build_warmup_cosine(optimizer, cfg.warmup_steps, total_steps)
    scaler = torch.cuda.amp.GradScaler(enabled=(cfg.amp and device.type == "cuda"))

    best_val = float("inf")
    bad_epochs = 0
    global_step = 0

    for epoch in range(cfg.epochs):
        model.train()
        running = 0.0
        optimizer.zero_grad(set_to_none=True)
        for xb, yb in train_loader:
            xb, yb = xb.to(device, non_blocking=True), yb.to(device, non_blocking=True)
            with torch.cuda.amp.autocast(enabled=(cfg.amp and device.type == "cuda")):
                logits = model(xb)
                loss = loss_fn(logits, yb)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip_norm)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)
            scheduler.step()
            global_step += 1
            running += float(loss)

        val_metrics = evaluate(model, val_loader, loss_fn, device)
        train_loss = running / max(1, len(train_loader))
        print({"epoch": epoch, "train_loss": round(train_loss, 4), **{k: round(v, 4) for k, v in val_metrics.items()}, "lr": round(scheduler.get_last_lr()[0], 8)})

        if val_metrics["loss"] < best_val - cfg.min_delta:
            best_val = val_metrics["loss"]
            bad_epochs = 0
            torch.save({"model": model.state_dict(), "epoch": epoch, "val_loss": best_val}, "checkpoints/best.pt")
        else:
            bad_epochs += 1
            if bad_epochs >= cfg.patience:
                break


if __name__ == "__main__":
    main()


