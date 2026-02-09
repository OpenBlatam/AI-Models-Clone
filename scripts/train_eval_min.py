from __future__ import annotations

import os
from dataclasses import dataclass

import torch
import torch.nn as nn

from src.models.mlp_classifier import MLPClassifier
from src.data.synthetic import build_dataloaders
from src.training.engine import train_one_epoch, evaluate
from src.utils.tracking import Tracker, TrackingConfig
from src.utils.checkpoint import CheckpointManager, CheckpointConfig


@dataclass
class Cfg:
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
    lr: float = float(os.getenv("LR", "3e-4"))
    wd: float = float(os.getenv("WD", "1e-2"))
    clip: float = float(os.getenv("CLIP", "1.0"))
    amp: bool = bool(int(os.getenv("AMP", "1")))
    log_dir: str = os.getenv("LOG_DIR", "experiments/min")
    ckpt_dir: str = os.getenv("CKPT_DIR", "checkpoints/min")


def main() -> None:
    cfg = Cfg()
    torch.manual_seed(42)
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
        seed=42,
    )

    model = MLPClassifier(cfg.input_dim, cfg.hidden_dims, cfg.num_classes, dropout=cfg.dropout).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.wd)
    loss_fn = nn.CrossEntropyLoss()

    tracker = Tracker(TrackingConfig(tensorboard=True, log_dir=cfg.log_dir, use_wandb=False))
    tracker.start()
    ckpt = CheckpointManager(CheckpointConfig(directory=cfg.ckpt_dir, monitor="val/loss", mode="min", save_top_k=1, save_every=1))

    for epoch in range(cfg.epochs):
        train_loss, train_acc = train_one_epoch(
            model, train_loader, optimizer, loss_fn, device=device, use_amp=cfg.amp, grad_clip_norm=cfg.clip
        )
        val_loss, val_acc = evaluate(model, val_loader, loss_fn, device=device)
        metrics = {"train/loss": train_loss, "train/acc": train_acc, "val/loss": val_loss, "val/acc": val_acc}
        tracker.log_metrics(metrics, step=epoch)
        saved = ckpt.maybe_save(epoch, metrics, model, optimizer)
        print(f"epoch={epoch} metrics={metrics} saved={saved}")

    tracker.finish()


if __name__ == "__main__":
    main()



