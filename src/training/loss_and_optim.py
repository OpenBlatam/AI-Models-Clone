from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Optional

import torch
import torch.nn.functional as F
from torch import nn


class FocalLoss(nn.Module):
    def __init__(self, gamma: float = 2.0, alpha: Optional[float] = None, reduction: str = "mean") -> None:
        super().__init__()
        self.gamma = float(gamma)
        self.alpha = alpha
        self.reduction = reduction

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        if logits.ndim == 1 or logits.shape[-1] == 1:
            # binary case
            logits = logits.view(-1)
            targets = targets.float().view(-1)
            bce = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")
            p = torch.sigmoid(logits)
            pt = torch.where(targets == 1, p, 1 - p)
            loss = (1 - pt) ** self.gamma * bce
            if self.alpha is not None:
                alpha_t = torch.where(targets == 1, self.alpha, 1 - self.alpha)
                loss = alpha_t * loss
        else:
            # multi-class CE-based focal
            log_probs = F.log_softmax(logits, dim=-1)
            ce = F.nll_loss(log_probs, targets, reduction="none")
            probs = torch.exp(-ce)
            loss = (1 - probs) ** self.gamma * ce
            if self.alpha is not None:
                # optional class weighting via alpha
                if isinstance(self.alpha, float):
                    loss = self.alpha * loss
        if self.reduction == "mean":
            return loss.mean()
        if self.reduction == "sum":
            return loss.sum()
        return loss


class DiceLoss(nn.Module):
    def __init__(self, eps: float = 1e-6) -> None:
        super().__init__()
        self.eps = eps

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        # binary dice over last dim or per-pixel
        probs = torch.sigmoid(logits)
        probs = probs.view(-1)
        targets = targets.float().view(-1)
        inter = (probs * targets).sum()
        union = probs.sum() + targets.sum()
        dice = (2 * inter + self.eps) / (union + self.eps)
        return 1 - dice


def build_loss(name: Literal["ce", "bce", "focal", "dice", "mse"] = "ce", **kwargs) -> nn.Module:
    if name == "ce":
        return nn.CrossEntropyLoss()
    if name == "bce":
        return nn.BCEWithLogitsLoss()
    if name == "focal":
        return FocalLoss(gamma=kwargs.get("gamma", 2.0), alpha=kwargs.get("alpha"))
    if name == "dice":
        return DiceLoss()
    if name == "mse":
        return nn.MSELoss()
    raise ValueError(f"Unknown loss: {name}")


def build_optimizer(
    parameters: Iterable[nn.Parameter],
    name: Literal["adamw", "adam", "sgd", "rmsprop"] = "adamw",
    lr: float = 3e-4,
    weight_decay: float = 0.01,
    momentum: float = 0.9,
) -> torch.optim.Optimizer:
    if name == "adamw":
        return torch.optim.AdamW(parameters, lr=lr, weight_decay=weight_decay, foreach=True)
    if name == "adam":
        return torch.optim.Adam(parameters, lr=lr, weight_decay=weight_decay, foreach=True)
    if name == "sgd":
        return torch.optim.SGD(parameters, lr=lr, momentum=momentum, weight_decay=weight_decay, nesterov=True)
    if name == "rmsprop":
        return torch.optim.RMSprop(parameters, lr=lr, momentum=momentum, weight_decay=weight_decay, centered=True)
    raise ValueError(f"Unknown optimizer: {name}")


def build_scheduler(
    optimizer: torch.optim.Optimizer,
    name: Literal["cosine", "onecycle", "steplr", "none"] = "cosine",
    total_steps: int = 10000,
    warmup_steps: int = 1000,
    step_size: int = 1000,
    gamma: float = 0.1,
):
    if name == "none":
        return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lambda step: 1.0)
    if name == "cosine":
        def schedule(step: int) -> float:
            if step < warmup_steps:
                return (step + 1) / max(1, warmup_steps)
            progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
            progress = min(max(progress, 0.0), 1.0)
            return 0.5 * (1.0 + torch.cos(torch.tensor(progress * torch.pi))).item()
        return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=schedule)
    if name == "onecycle":
        # Note: requires max_lr; map lr as max_lr and steps_per_epoch ~1 with total_steps epochs
        return torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=max(p["lr"] for p in optimizer.param_groups), total_steps=total_steps, pct_start=warmup_steps / max(1, total_steps))
    if name == "steplr":
        return torch.optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)
    raise ValueError(f"Unknown scheduler: {name}")



