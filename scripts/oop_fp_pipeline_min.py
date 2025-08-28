from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Tuple

import torch
import torch.nn as nn


# OOP model
class ResidualMLP(nn.Module):
    def __init__(self, d_in: int, d_hid: int, num_layers: int, d_out: int) -> None:
        super().__init__()
        self.inp = nn.Linear(d_in, d_hid)
        self.blocks = nn.ModuleList([nn.Sequential(nn.ReLU(), nn.Linear(d_hid, d_hid)) for _ in range(num_layers)])
        self.out = nn.Linear(d_hid, d_out)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.inp(x)
        for block in self.blocks:
            h = h + block(h)
        return self.out(torch.relu(h))


# Functional pipeline
TensorPair = Tuple[torch.Tensor, torch.Tensor]

def compose(*funcs: Callable[[TensorPair], TensorPair]) -> Callable[[TensorPair], TensorPair]:
    def apply(pair: TensorPair) -> TensorPair:
        for f in funcs:
            pair = f(pair)
        return pair
    return apply


def to_device(device: str) -> Callable[[TensorPair], TensorPair]:
    def fn(pair: TensorPair) -> TensorPair:
        x, y = pair
        return x.to(device, non_blocking=True), y.to(device, non_blocking=True)
    return fn


def normalize(mean: float = 0.0, std: float = 1.0) -> Callable[[TensorPair], TensorPair]:
    def fn(pair: TensorPair) -> TensorPair:
        x, y = pair
        return (x - mean) / max(std, 1e-8), y
    return fn


def add_gaussian_noise(std: float = 0.01) -> Callable[[TensorPair], TensorPair]:
    def fn(pair: TensorPair) -> TensorPair:
        x, y = pair
        return x + torch.randn_like(x) * std, y
    return fn


@dataclass
class TrainStep:
    model: nn.Module
    optimizer: torch.optim.Optimizer
    loss_fn: nn.Module

    def __call__(self, batch: TensorPair) -> float:
        x, y = batch
        logits = self.model(x)
        loss = self.loss_fn(logits, y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()
        self.optimizer.zero_grad(set_to_none=True)
        return float(loss.detach().item())


def main() -> None:
    torch.manual_seed(0)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ResidualMLP(64, 128, 2, 4).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4)
    loss = nn.CrossEntropyLoss()

    x = torch.randn(4096, 64)
    y = (x @ torch.randn(64, 4)).argmax(dim=1)

    pipeline = compose(
        to_device(device),
        normalize(0.0, 1.0),
        add_gaussian_noise(0.01),
    )

    step = TrainStep(model, opt, loss)
    for _ in range(5):
        xb, yb = pipeline((x, y))
        _ = step((xb, yb))


if __name__ == "__main__":
    main()



