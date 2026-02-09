from __future__ import annotations

import os
from dataclasses import dataclass

import torch
import torch.nn as nn

from src.models.mlp_classifier import MLPClassifier
from src.data.synthetic import build_dataloaders
from src.training.engine import train_one_epoch, evaluate


@dataclass
class Config:
    input_dim: int = int(os.getenv("INPUT_DIM", "128"))
    hidden_dims: tuple[int, int] = tuple(int(x) for x in os.getenv("HIDDEN_DIMS", "256,256").split(","))  # type: ignore[assignment]
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
    seed: int = int(os.getenv("SEED", "42"))


def main() -> None:
    cfg = Config()
    torch.manual_seed(cfg.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    train_loader, val_loader = build_dataloaders(
        input_dim=cfg.input_dim,
        num_classes=cfg.num_classes,
        train_samples=cfg.train_samples,
        val_samples=cfg.val_samples,
        batch_size=cfg.batch_size,
        num_workers=cfg.num_workers,
        pin_memory=cfg.pin_memory,
        persistent_workers=cfg.persistent_workers,
        prefetch_factor=cfg.prefetch_factor,
        seed=cfg.seed,
    )

    model = MLPClassifier(cfg.input_dim, cfg.hidden_dims, cfg.num_classes, dropout=cfg.dropout).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay)
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(cfg.epochs):
        train_loss, train_acc = train_one_epoch(
            model,
            train_loader,
            optimizer,
            loss_fn,
            device=device,
            use_amp=cfg.amp,
            grad_clip_norm=cfg.grad_clip_norm,
        )
        val_loss, val_acc = evaluate(model, val_loader, loss_fn, device=device)
        print(f"epoch={epoch} train_loss={train_loss:.4f} train_acc={train_acc:.4f} val_loss={val_loss:.4f} val_acc={val_acc:.4f}")


if __name__ == "__main__":
    main()



