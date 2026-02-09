from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch
from torch import nn

# Ensure project root on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.utils.config import DataConfig, ModelConfig, TrainConfig
from src.utils.config_loader import load_yaml_config, build_configs
from src.utils.tracking import Tracker
from src.utils.checkpoint import CheckpointManager
from src.data.synthetic import build_dataloaders
from src.models.mlp_classifier import MLPClassifier
from src.training.engine import train_one_epoch, evaluate, save_checkpoint


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Modular training entrypoint")
    p.add_argument("--config", type=str, default="config/train.yaml")
    p.add_argument("--epochs", type=int, default=None)
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--weight-decay", type=float, default=None)
    p.add_argument("--amp", action="store_true")
    p.add_argument("--accum", type=int, default=None)
    p.add_argument("--grad-clip", type=float, default=None)
    p.add_argument("--input-dim", type=int, default=None)
    p.add_argument("--num-classes", type=int, default=None)
    p.add_argument("--num-workers", type=int, default=None)
    p.add_argument("--dropout", type=float, default=None)
    p.add_argument("--checkpoint", type=str, default="checkpoints/modular_mlp.pt")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")
    torch.backends.cudnn.benchmark = (device.type == "cuda")

    # Load YAML and build configs
    yaml_cfg = load_yaml_config(args.config)
    model_cfg, data_cfg, train_cfg, tracking_cfg, ckpt_cfg = build_configs(yaml_cfg)

    # CLI overrides
    if args.epochs is not None:
        train_cfg.epochs = args.epochs
    if args.batch_size is not None:
        data_cfg.batch_size = args.batch_size
    if args.lr is not None:
        train_cfg.learning_rate = args.lr
    if args.weight_decay is not None:
        train_cfg.weight_decay = args.weight_decay
    if args.accum is not None:
        train_cfg.grad_accum_steps = args.accum
    if args.grad_clip is not None:
        train_cfg.grad_clip_norm = args.grad_clip
    if args.input_dim is not None:
        model_cfg.input_dim = args.input_dim
    if args.num_classes is not None:
        model_cfg.num_classes = args.num_classes
    if args.num_workers is not None:
        data_cfg.num_workers = args.num_workers
    if args.dropout is not None:
        model_cfg.dropout = args.dropout
    # --amp flag only enables AMP (never disables if YAML true)
    if args.amp:
        train_cfg.amp = True

    train_loader, val_loader = build_dataloaders(
        train_samples=data_cfg.train_samples,
        val_samples=data_cfg.val_samples,
        input_dim=model_cfg.input_dim,
        num_classes=model_cfg.num_classes,
        batch_size=data_cfg.batch_size,
        num_workers=data_cfg.num_workers,
        pin_memory=(data_cfg.pin_memory and device.type == "cuda"),
        persistent_workers=data_cfg.persistent_workers,
        prefetch_factor=data_cfg.prefetch_factor,
    )

    model = MLPClassifier(model_cfg.input_dim, list(model_cfg.hidden_dims), model_cfg.num_classes, model_cfg.dropout).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=train_cfg.learning_rate, weight_decay=train_cfg.weight_decay)
    loss_fn = nn.CrossEntropyLoss()

    tracker = Tracker(tracking_cfg)
    tracker.start()
    ckpt_mgr = CheckpointManager(ckpt_cfg)

    for epoch in range(train_cfg.epochs):
        train_loss = train_one_epoch(
            model=model,
            loader=train_loader,
            optimizer=optimizer,
            loss_fn=loss_fn,
            device=device,
            use_amp=train_cfg.amp,
            grad_clip_norm=train_cfg.grad_clip_norm,
            grad_accum_steps=train_cfg.grad_accum_steps,
        )
        metrics = evaluate(model, val_loader, loss_fn, device)
        print(f"epoch={epoch} train_loss={train_loss:.4f} val_loss={metrics['loss']:.4f} val_acc={metrics['accuracy']:.4f}")
        tracker.log_metrics({"train/loss": train_loss, "val/loss": metrics["loss"], "val/accuracy": metrics["accuracy"]}, step=epoch)
        ckpt_path = ckpt_mgr.maybe_save(epoch=epoch, metrics={"val/loss": metrics["loss"], "val/accuracy": metrics["accuracy"]}, model=model, optimizer=optimizer)
    tracker.finish()


if __name__ == "__main__":
    main()


