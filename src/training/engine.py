from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    *,
    device: str,
    use_amp: bool,
    grad_clip_norm: float,
) -> Tuple[float, float]:
    model.train()
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp and device == "cuda")
    total_loss = 0.0
    total_correct = 0
    total_examples = 0

    for features, labels in loader:
        features = features.to(device)
        labels = labels.to(device)
        with torch.cuda.amp.autocast(enabled=use_amp and device == "cuda"):
            logits = model(features)
            loss = loss_fn(logits, labels)
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        if grad_clip_norm > 0:
            nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)

        total_loss += float(loss) * features.size(0)
        total_correct += int((logits.argmax(dim=1) == labels).sum())
        total_examples += features.size(0)

    avg_loss = total_loss / max(total_examples, 1)
    avg_acc = total_correct / max(total_examples, 1)
    return avg_loss, avg_acc


def evaluate(model: nn.Module, loader: DataLoader, loss_fn: nn.Module, *, device: str) -> Tuple[float, float]:
    model.eval()
    total_loss = 0.0
    total_correct = 0
    total_examples = 0
    with torch.no_grad():
        for features, labels in loader:
            features = features.to(device)
            labels = labels.to(device)
            logits = model(features)
            loss = loss_fn(logits, labels)
            total_loss += float(loss) * features.size(0)
            total_correct += int((logits.argmax(dim=1) == labels).sum())
            total_examples += features.size(0)
    return total_loss / max(total_examples, 1), total_correct / max(total_examples, 1)

from __future__ import annotations

from typing import Dict

import torch
from torch import nn
from torch.utils.data import DataLoader

from src.evaluation.metrics import compute_accuracy, compute_loss


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    device: torch.device,
    use_amp: bool,
    grad_clip_norm: float,
    grad_accum_steps: int,
) -> float:
    model.train()
    scaler = torch.cuda.amp.GradScaler(enabled=(use_amp and device.type == "cuda"))
    optimizer.zero_grad(set_to_none=True)
    running_loss: float = 0.0

    for step, (xb, yb) in enumerate(loader, start=1):
        xb = xb.to(device, non_blocking=True)
        yb = yb.to(device, non_blocking=True)

        with torch.cuda.amp.autocast(enabled=(use_amp and device.type == "cuda")):
            logits = model(xb)
            loss = compute_loss(loss_fn, logits, yb) / max(1, grad_accum_steps)

        scaler.scale(loss).backward()

        if step % grad_accum_steps == 0:
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)

        running_loss += float(loss.item())

    # flush remainder
    if (step % grad_accum_steps) != 0:
        scaler.unscale_(optimizer)
        nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)

    return running_loss / max(len(loader), 1)


@torch.no_grad()
def evaluate(model: nn.Module, loader: DataLoader, loss_fn: nn.Module, device: torch.device) -> Dict[str, float]:
    model.eval()
    total_loss: float = 0.0
    correct: int = 0
    total: int = 0

    for xb, yb in loader:
        xb = xb.to(device, non_blocking=True)
        yb = yb.to(device, non_blocking=True)
        logits = model(xb)
        total_loss += float(loss_fn(logits, yb).item())
        correct += (logits.argmax(-1) == yb).sum().item()
        total += yb.size(0)

    return {
        "loss": total_loss / max(len(loader), 1),
        "accuracy": correct / max(total, 1),
    }


def save_checkpoint(path: str, model: nn.Module, optimizer: torch.optim.Optimizer, epoch: int) -> None:
    obj = {
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "epoch": epoch,
    }
    torch.save(obj, path)


def load_checkpoint(path: str, model: nn.Module, optimizer: torch.optim.Optimizer | None = None) -> int:
    ckpt = torch.load(path, map_location="cpu")
    model.load_state_dict(ckpt["model"])  # type: ignore[arg-type]
    if optimizer is not None:
        optimizer.load_state_dict(ckpt["optimizer"])  # type: ignore[arg-type]
    return int(ckpt.get("epoch", 0))


