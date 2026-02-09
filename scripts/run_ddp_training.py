from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, Tuple

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler

# Ensure project root on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.data.synthetic import SyntheticClassification
from src.models.mlp_classifier import MLPClassifier
from src.utils.config_loader import load_yaml_config, build_configs
from src.utils.tracking import Tracker
from src.utils.checkpoint import CheckpointManager


def setup_ddp() -> Tuple[int, int, int, torch.device]:
    rank = int(os.environ.get("RANK", "0"))
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    local_rank = int(os.environ.get("LOCAL_RANK", str(rank)))
    backend = "nccl" if torch.cuda.is_available() else "gloo"
    if torch.cuda.is_available():
        torch.cuda.set_device(local_rank)
        device = torch.device(f"cuda:{local_rank}")
        torch.backends.cudnn.benchmark = True
        try:
            torch.set_float32_matmul_precision("high")
        except Exception:
            pass
    else:
        device = torch.device("cpu")
    dist.init_process_group(backend=backend, init_method="env://")
    return rank, world_size, local_rank, device


@torch.no_grad()
def evaluate(model: nn.Module, loader: DataLoader, loss_fn: nn.Module, device: torch.device) -> Dict[str, float]:
    model.eval()
    total_loss = torch.tensor(0.0, device=device)
    num_batches = torch.tensor(0.0, device=device)
    correct = torch.tensor(0.0, device=device)
    total = torch.tensor(0.0, device=device)
    for xb, yb in loader:
        xb = xb.to(device, non_blocking=True)
        yb = yb.to(device, non_blocking=True)
        logits = model(xb)
        total_loss += loss_fn(logits, yb)
        correct += (logits.argmax(-1) == yb).sum()
        total += yb.size(0)
        num_batches += 1.0
    dist.all_reduce(total_loss, op=dist.ReduceOp.SUM)
    dist.all_reduce(num_batches, op=dist.ReduceOp.SUM)
    dist.all_reduce(correct, op=dist.ReduceOp.SUM)
    dist.all_reduce(total, op=dist.ReduceOp.SUM)
    avg_loss = (total_loss / torch.clamp(num_batches, min=1)).item()
    acc = (correct / torch.clamp(total, min=1)).item()
    return {"loss": float(avg_loss), "accuracy": float(acc)}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="DDP training entrypoint (torchrun)")
    p.add_argument("--config", type=str, default="config/train.yaml")
    p.add_argument("--epochs", type=int, default=None)
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--weight-decay", type=float, default=None)
    p.add_argument("--accum", type=int, default=None)
    p.add_argument("--grad-clip", type=float, default=None)
    p.add_argument("--amp", action="store_true")
    return p.parse_args()


def main() -> None:
    rank, world_size, local_rank, device = setup_ddp()
    is_master = rank == 0

    args = parse_args()
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
    if args.amp:
        train_cfg.amp = True

    # Datasets and distributed loaders
    train_ds = SyntheticClassification(data_cfg.train_samples, model_cfg.input_dim, model_cfg.num_classes)
    val_ds = SyntheticClassification(data_cfg.val_samples, model_cfg.input_dim, model_cfg.num_classes)

    train_sampler = DistributedSampler(train_ds, num_replicas=world_size, rank=rank, shuffle=True, drop_last=True)
    val_sampler = DistributedSampler(val_ds, num_replicas=world_size, rank=rank, shuffle=False, drop_last=False)
    train_loader = DataLoader(
        train_ds,
        batch_size=data_cfg.batch_size,
        sampler=train_sampler,
        num_workers=data_cfg.num_workers,
        pin_memory=(data_cfg.pin_memory and device.type == "cuda"),
        persistent_workers=(data_cfg.persistent_workers and data_cfg.num_workers > 0),
        prefetch_factor=data_cfg.prefetch_factor if data_cfg.num_workers > 0 else None,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=data_cfg.batch_size,
        sampler=val_sampler,
        num_workers=data_cfg.num_workers,
        pin_memory=(data_cfg.pin_memory and device.type == "cuda"),
        persistent_workers=(data_cfg.persistent_workers and data_cfg.num_workers > 0),
        prefetch_factor=data_cfg.prefetch_factor if data_cfg.num_workers > 0 else None,
    )

    # Model / Optim
    model = MLPClassifier(model_cfg.input_dim, list(model_cfg.hidden_dims), model_cfg.num_classes, model_cfg.dropout).to(device)
    ddp_model = DDP(model, device_ids=[device.index] if device.type == "cuda" else None, output_device=(device.index if device.type == "cuda" else None), broadcast_buffers=False)
    optimizer = torch.optim.AdamW(ddp_model.parameters(), lr=train_cfg.learning_rate, weight_decay=train_cfg.weight_decay)
    loss_fn = nn.CrossEntropyLoss()
    scaler = torch.cuda.amp.GradScaler(enabled=(train_cfg.amp and device.type == "cuda"))

    tracker = Tracker(tracking_cfg) if is_master else None
    if tracker is not None:
        tracker.start()
    ckpt_mgr = CheckpointManager(ckpt_cfg) if is_master else None

    for epoch in range(train_cfg.epochs):
        ddp_model.train()
        train_sampler.set_epoch(epoch)
        optimizer.zero_grad(set_to_none=True)

        running_loss = 0.0
        for step, (xb, yb) in enumerate(train_loader, start=1):
            xb = xb.to(device, non_blocking=True)
            yb = yb.to(device, non_blocking=True)
            with torch.cuda.amp.autocast(enabled=(train_cfg.amp and device.type == "cuda")):
                logits = ddp_model(xb)
                loss = loss_fn(logits, yb) / max(1, train_cfg.grad_accum_steps)
            scaler.scale(loss).backward()

            if step % train_cfg.grad_accum_steps == 0:
                scaler.unscale_(optimizer)
                nn.utils.clip_grad_norm_(ddp_model.parameters(), train_cfg.grad_clip_norm)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)
            running_loss += float(loss.item())

        metrics = evaluate(ddp_model, val_loader, loss_fn, device)
        if is_master:
            print(f"epoch={epoch} train_loss={running_loss/max(len(train_loader),1):.4f} val_loss={metrics['loss']:.4f} val_acc={metrics['accuracy']:.4f}")
            if tracker is not None:
                tracker.log_metrics({"train/loss": running_loss/max(len(train_loader),1), "val/loss": metrics["loss"], "val/accuracy": metrics["accuracy"]}, step=epoch)
            if ckpt_mgr is not None:
                ckpt_mgr.maybe_save(epoch=epoch, metrics={"val/loss": metrics["loss"], "val/accuracy": metrics["accuracy"]}, model=ddp_model.module, optimizer=optimizer)

    if is_master and tracker is not None:
        tracker.finish()
    dist.barrier()
    dist.destroy_process_group()


if __name__ == "__main__":
    main()



