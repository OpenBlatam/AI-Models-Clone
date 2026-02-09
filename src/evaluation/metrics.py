from __future__ import annotations

import torch


def accuracy_from_logits(logits: torch.Tensor, labels: torch.Tensor) -> float:
    preds = logits.argmax(dim=1)
    correct = (preds == labels).float().sum().item()
    return float(correct / max(labels.numel(), 1))

from __future__ import annotations

import torch
from torch import nn


def compute_accuracy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    if logits.numel() == 0:
        return 0.0
    preds = logits.argmax(dim=-1)
    correct = (preds == targets).sum().item()
    total = targets.numel()
    return correct / max(total, 1)


def compute_loss(loss_fn: nn.Module, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    return loss_fn(logits, targets)


