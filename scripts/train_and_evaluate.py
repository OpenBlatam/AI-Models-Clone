from __future__ import annotations

import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, random_split


def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def maybe_compile(model: nn.Module) -> nn.Module:
    if hasattr(torch, "compile"):
        try:
            return torch.compile(model, mode=os.getenv("TORCH_COMPILE_MODE", "max-autotune"))
        except Exception:
            return model
    return model


@dataclass
class TrainConfig:
    input_dim: int = int(os.getenv("INPUT_DIM", "128"))
    hidden_dims: Tuple[int, int] = tuple(int(x) for x in os.getenv("HIDDEN_DIMS", "256,256").split(","))  # type: ignore[assignment]
    num_classes: int = int(os.getenv("NUM_CLASSES", "10"))
    dropout: float = float(os.getenv("DROPOUT", "0.0"))

    train_samples: int = int(os.getenv("TRAIN_SAMPLES", "6000"))
    val_samples: int = int(os.getenv("VAL_SAMPLES", "1000"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "256"))
    num_workers: int = int(os.getenv("NUM_WORKERS", "4"))
    pin_memory: bool = bool(int(os.getenv("PIN_MEMORY", "1")))
    persistent_workers: bool = bool(int(os.getenv("PERSISTENT_WORKERS", "1")))
    prefetch_factor: int = int(os.getenv("PREFETCH", "2"))

    epochs: int = int(os.getenv("EPOCHS", "5"))
    learning_rate: float = float(os.getenv("LR", "3e-4"))
    weight_decay: float = float(os.getenv("WD", "1e-2"))
    grad_clip_norm: float = float(os.getenv("CLIP", "1.0"))
    amp: bool = bool(int(os.getenv("AMP", "1")))
    grad_accum_steps: int = int(os.getenv("ACCUM", "1"))

    scheduler: str = os.getenv("SCHED", "cosine")  # cosine|steplr|none
    step_size: int = int(os.getenv("STEP_SIZE", "5"))
    gamma: float = float(os.getenv("GAMMA", "0.5"))

    patience: int = int(os.getenv("PATIENCE", "3"))
    out_dir: str = os.getenv("OUT", "checkpoints/train_min")
    seed: int = int(os.getenv("SEED", "42"))


class SyntheticClassificationDataset(Dataset):
    def __init__(self, num_samples: int, input_dim: int, num_classes: int, seed: int) -> None:
        g = torch.Generator().manual_seed(seed)
        self.features = torch.randn(num_samples, input_dim, generator=g)
        # Create random linear separators per class
        weights = torch.randn(num_classes, input_dim, generator=g)
        logits = self.features @ weights.T
        self.labels = logits.argmax(dim=1)

    def __len__(self) -> int:
        return self.features.shape[0]

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.features[idx], self.labels[idx]


class MLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: Tuple[int, ...], num_classes: int, dropout: float) -> None:
        super().__init__()
        layers = []
        prev = input_dim
        for h in hidden_dims:
            layers += [nn.Linear(prev, h), nn.ReLU(inplace=True)]
            if dropout > 0:
                layers += [nn.Dropout(p=dropout)]
            prev = h
        layers += [nn.Linear(prev, num_classes)]
        self.net = nn.Sequential(*layers)

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
        self.bad_epochs = 0

    def step(self, val_loss: float) -> bool:
        if val_loss < self.best - 1e-8:
            self.best = val_loss
            self.bad_epochs = 0
            return False
        self.bad_epochs += 1
        return self.bad_epochs > self.patience


def build_loaders(cfg: TrainConfig) -> tuple[DataLoader, DataLoader]:
    ds = SyntheticClassificationDataset(
        num_samples=cfg.train_samples + cfg.val_samples,
        input_dim=cfg.input_dim,
        num_classes=cfg.num_classes,
        seed=cfg.seed,
    )
    train_len = cfg.train_samples
    val_len = len(ds) - train_len
    train_ds, val_ds = random_split(ds, [train_len, val_len], generator=torch.Generator().manual_seed(cfg.seed))
    train_loader = DataLoader(
        train_ds,
        batch_size=cfg.batch_size,
        shuffle=True,
        num_workers=cfg.num_workers,
        pin_memory=cfg.pin_memory,
        persistent_workers=cfg.persistent_workers if cfg.num_workers > 0 else False,
        prefetch_factor=cfg.prefetch_factor if cfg.num_workers > 0 else None,  # type: ignore[arg-type]
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=cfg.batch_size,
        shuffle=False,
        num_workers=cfg.num_workers,
        pin_memory=cfg.pin_memory,
        persistent_workers=cfg.persistent_workers if cfg.num_workers > 0 else False,
        prefetch_factor=cfg.prefetch_factor if cfg.num_workers > 0 else None,  # type: ignore[arg-type]
    )
    return train_loader, val_loader


def build_scheduler(optimizer: torch.optim.Optimizer, cfg: TrainConfig):
    name = cfg.scheduler.lower()
    if name == "cosine":
        return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.epochs)
    if name == "steplr":
        return torch.optim.lr_scheduler.StepLR(optimizer, step_size=cfg.step_size, gamma=cfg.gamma)
    return None


def evaluate(model: nn.Module, loader: DataLoader, device: str) -> tuple[float, float]:
    model.eval()
    total = 0
    correct = 0
    total_loss = 0.0
    loss_fn = nn.CrossEntropyLoss()
    with torch.no_grad():
        for features, labels in loader:
            features = features.to(device)
            labels = labels.to(device)
            logits = model(features)
            loss = loss_fn(logits, labels)
            total_loss += float(loss) * features.size(0)
            preds = logits.argmax(dim=1)
            correct += int((preds == labels).sum())
            total += features.size(0)
    return total_loss / max(total, 1), correct / max(total, 1)


def train() -> None:
    cfg = TrainConfig()
    torch.manual_seed(cfg.seed)
    device = get_device()

    model = MLP(cfg.input_dim, cfg.hidden_dims, cfg.num_classes, cfg.dropout).to(device)
    model = maybe_compile(model)

    train_loader, val_loader = build_loaders(cfg)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay)
    scheduler = build_scheduler(optimizer, cfg)
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.amp and device == "cuda")
    loss_fn = nn.CrossEntropyLoss()
    early = EarlyStopping(patience=cfg.patience)

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    best_path = out_dir / "best.pt"

    global_step = 0
    for epoch in range(cfg.epochs):
        model.train()
        running = 0.0
        for step, (features, labels) in enumerate(train_loader):
            features = features.to(device)
            labels = labels.to(device)
            with torch.cuda.amp.autocast(enabled=cfg.amp and device == "cuda"):
                logits = model(features)
                loss = loss_fn(logits, labels) / cfg.grad_accum_steps

            scaler.scale(loss).backward()

            if (step + 1) % cfg.grad_accum_steps == 0:
                scaler.unscale_(optimizer)
                nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip_norm)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)
                global_step += 1
            running += float(loss) * features.size(0)

        if scheduler is not None:
            scheduler.step()

        val_loss, val_acc = evaluate(model, val_loader, device)
        should_stop = early.step(val_loss)
        torch.save({"model": model.state_dict(), "epoch": epoch, "val_loss": val_loss, "val_acc": val_acc}, best_path)
        print(f"epoch={epoch} val_loss={val_loss:.4f} val_acc={val_acc:.4f}")
        if should_stop:
            break


if __name__ == "__main__":
    train()



