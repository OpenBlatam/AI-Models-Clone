from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Dict

import torch
from torch import nn
from torch.utils.data import DataLoader
from accelerate import Accelerator

# Ensure project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.data.synthetic import build_dataloaders
from src.models.mlp_classifier import MLPClassifier
from src.utils.config_loader import load_yaml_config, build_configs


@torch.no_grad()
def evaluate(accelerator: Accelerator, model: nn.Module, loader: DataLoader, loss_fn: nn.Module) -> Dict[str, float]:
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    for xb, yb in loader:
        logits = model(xb)
        loss = loss_fn(logits, yb)
        total_loss += accelerator.gather_for_metrics(loss.detach()).sum().item()
        preds = logits.argmax(-1)
        correct += accelerator.gather_for_metrics((preds == yb).sum()).sum().item()
        total += accelerator.gather_for_metrics(torch.tensor(yb.size(0), device=yb.device)).sum().item()
    num_batches = accelerator.gather_for_metrics(torch.tensor(len(loader), device=loader.device if hasattr(loader, 'device') else next(model.parameters()).device)).max().item()
    return {
        "loss": total_loss / max(num_batches, 1),
        "accuracy": correct / max(total, 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Accelerate-based optimized training")
    ap.add_argument("--config", type=str, default="config/train.yaml")
    ap.add_argument("--epochs", type=int, default=None)
    ap.add_argument("--grad-accum", type=int, default=None)
    ap.add_argument("--compile", action="store_true")
    ap.add_argument("--log-with", type=str, nargs="*", default=None)  # e.g. tensorboard wandb
    args = ap.parse_args()

    yaml_cfg = load_yaml_config(args.config)
    model_cfg, data_cfg, train_cfg, tracking_cfg, ckpt_cfg = build_configs(yaml_cfg)

    if args.epochs is not None:
        train_cfg.epochs = args.epochs
    if args.grad_accum is not None:
        train_cfg.grad_accum_steps = args.grad_accum

    mixed_precision = "bf16" if (train_cfg.amp and torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else ("fp16" if train_cfg.amp and torch.cuda.is_available() else "no")
    accelerator = Accelerator(
        gradient_accumulation_steps=max(1, train_cfg.grad_accum_steps),
        mixed_precision=mixed_precision,
        log_with=(args.log_with if args.log_with else (["tensorboard"] if tracking_cfg.tensorboard else None)),
        project_dir=tracking_cfg.log_dir,
    )

    if accelerator.is_main_process and accelerator.log_with is not None:
        accelerator.init_trackers(
            project_name=(tracking_cfg.wandb_project or "accelerate_run"),
            config={
                "epochs": train_cfg.epochs,
                "batch_size": data_cfg.batch_size,
                "lr": train_cfg.learning_rate,
                "weight_decay": train_cfg.weight_decay,
                "grad_accum": train_cfg.grad_accum_steps,
            },
            init_kwargs={"wandb": {"entity": tracking_cfg.wandb_entity, "name": tracking_cfg.run_name}},
        )

    # Data
    train_loader, val_loader = build_dataloaders(
        train_samples=data_cfg.train_samples,
        val_samples=data_cfg.val_samples,
        input_dim=model_cfg.input_dim,
        num_classes=model_cfg.num_classes,
        batch_size=data_cfg.batch_size,
        num_workers=data_cfg.num_workers,
        pin_memory=(data_cfg.pin_memory and accelerator.device.type == "cuda"),
        persistent_workers=(data_cfg.persistent_workers and data_cfg.num_workers > 0),
        prefetch_factor=data_cfg.prefetch_factor,
    )

    # Model
    model = MLPClassifier(model_cfg.input_dim, list(model_cfg.hidden_dims), model_cfg.num_classes, model_cfg.dropout)
    if args.compile and hasattr(torch, "compile"):
        try:
            model = torch.compile(model, mode="max-autotune")  # type: ignore[assignment]
        except Exception:
            pass

    # Optimizer (try bitsandbytes)
    try:
        import bitsandbytes as bnb  # type: ignore

        optimizer = bnb.optim.AdamW8bit(model.parameters(), lr=train_cfg.learning_rate, weight_decay=train_cfg.weight_decay)
    except Exception:
        optimizer = torch.optim.AdamW(model.parameters(), lr=train_cfg.learning_rate, weight_decay=train_cfg.weight_decay, foreach=True)

    loss_fn = nn.CrossEntropyLoss()

    model, optimizer, train_loader, val_loader = accelerator.prepare(model, optimizer, train_loader, val_loader)

    for epoch in range(train_cfg.epochs):
        model.train()
        running = 0.0
        for step, (xb, yb) in enumerate(train_loader, start=1):
            with accelerator.autocast():
                logits = model(xb)
                loss = loss_fn(logits, yb)
            accelerator.backward(loss)
            if accelerator.sync_gradients:
                accelerator.clip_grad_norm_(model.parameters(), train_cfg.grad_clip_norm)
            optimizer.step()
            optimizer.zero_grad(set_to_none=True)
            running += loss.detach().float().item()

        metrics = evaluate(accelerator, model, val_loader, loss_fn)
        if accelerator.is_main_process:
            accelerator.print(f"epoch={epoch} train_loss={running/max(len(train_loader),1):.4f} val_loss={metrics['loss']:.4f} val_acc={metrics['accuracy']:.4f}")
            if accelerator.log_with is not None:
                accelerator.log({"train/loss": running/max(len(train_loader),1), "val/loss": metrics["loss"], "val/accuracy": metrics["accuracy"]}, step=epoch)
            # checkpoint
            ckpt_dir = Path(ckpt_cfg.directory)
            ckpt_dir.mkdir(parents=True, exist_ok=True)
            unwrapped = accelerator.unwrap_model(model)
            torch.save({"model": unwrapped.state_dict(), "optimizer": optimizer.state_dict(), "epoch": epoch, "metrics": metrics}, ckpt_dir / f"epoch{epoch:04d}.pt")

    if accelerator.is_main_process and accelerator.log_with is not None:
        accelerator.end_training()


if __name__ == "__main__":
    main()



