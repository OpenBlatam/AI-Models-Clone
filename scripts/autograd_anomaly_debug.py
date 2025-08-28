from __future__ import annotations

import math
import os
from typing import Callable

import torch
import torch.nn as nn


class NaNGradientDetector:
    def __init__(self) -> None:
        self.found_nan = False

    def hook(self, module: nn.Module, grad_input, grad_output):  # type: ignore[no-untyped-def]
        for g in grad_input:
            if g is not None and not torch.isfinite(g).all():
                self.found_nan = True


class TinyBadNet(nn.Module):
    def __init__(self, d: int = 16) -> None:
        super().__init__()
        self.fc1 = nn.Linear(d, d)
        self.bn = nn.BatchNorm1d(d)
        self.fc2 = nn.Linear(d, d)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.bn(x)
        x = torch.relu(x)
        x = self.fc2(x)
        return x


def induce_problem(x: torch.Tensor, mode: str) -> torch.Tensor:
    if mode == "divide_by_zero":
        return x / 0.0
    if mode == "log_of_negative":
        return torch.log(x - 10.0)
    if mode == "overflow":
        return x * 1e308
    return x


def run_with_anomaly_detection(induce: str = "log_of_negative") -> None:
    torch.manual_seed(int(os.getenv("SEED", "0")))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = TinyBadNet().to(device)
    crit = nn.MSELoss()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)

    detector = NaNGradientDetector()
    handles = []
    for m in model.modules():
        if isinstance(m, (nn.Linear, nn.BatchNorm1d)):
            handles.append(m.register_backward_hook(detector.hook))

    x = torch.randn(32, 16, device=device)
    y = torch.zeros(32, 16, device=device)

    torch.autograd.set_detect_anomaly(True)
    try:
        out = model(x)
        out = induce_problem(out, induce)
        loss = crit(out, y)
        loss.backward()
        if detector.found_nan:
            print("Detected non-finite gradients via hook.")
        opt.step()
    except RuntimeError as e:
        print(f"Anomaly caught: {e}")
    finally:
        for h in handles:
            h.remove()


if __name__ == "__main__":
    run_with_anomaly_detection()

from __future__ import annotations

import contextlib
import time
from dataclasses import dataclass
from typing import Callable, Dict, Tuple

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


@dataclass
class DebugCfg:
    batch_size: int = 256
    input_dim: int = 128
    num_classes: int = 10
    steps: int = 200
    inject_nan_step: int = 50  # set <=0 to disable


class DebugMLP(nn.Module):
    def __init__(self, input_dim: int, hidden=(256, 256), num_classes: int = 10):
        super().__init__()
        layers: list[nn.Module] = []
        last = input_dim
        for h in hidden:
            layers += [nn.Linear(last, h), nn.GELU()]
            last = h
        layers.append(nn.Linear(last, num_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def register_nan_hooks(module: nn.Module) -> None:
    def check_grad(module: nn.Module, grad_input, grad_output):  # type: ignore[no-untyped-def]
        for gi in grad_input:
            if gi is not None and torch.isnan(gi).any():
                print(f"[HOOK] NaN in grad_input of {module.__class__.__name__}")
        for go in grad_output:
            if go is not None and torch.isnan(go).any():
                print(f"[HOOK] NaN in grad_output of {module.__class__.__name__}")

    for m in module.modules():
        if any(p.requires_grad for p in m.parameters(recurse=False)):
            m.register_backward_hook(check_grad)  # type: ignore[attr-defined]


@contextlib.contextmanager
def timed(label: str):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        dt = time.perf_counter() - t0
        print({"section": label, "seconds": round(dt, 4)})


def main() -> None:
    cfg = DebugCfg()
    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")
    torch.backends.cudnn.benchmark = (device.type == "cuda")

    # synthetic
    x = torch.randn(10_000, cfg.input_dim)
    w = torch.randn(cfg.input_dim, cfg.num_classes)
    y = torch.multinomial((x @ w).softmax(-1), 1).squeeze(-1)
    loader = DataLoader(TensorDataset(x, y), batch_size=cfg.batch_size, shuffle=True)

    model = DebugMLP(cfg.input_dim, (256, 256), cfg.num_classes).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    loss_fn = nn.CrossEntropyLoss()

    register_nan_hooks(model)

    # Enable anomaly detection for autograd to pin-point the op that created NaN/Inf
    with torch.autograd.set_detect_anomaly(True):
        it = iter(loader)
        for step in range(1, cfg.steps + 1):
            try:
                xb, yb = next(it)
            except StopIteration:
                it = iter(loader)
                xb, yb = next(it)
            xb = xb.to(device, non_blocking=True)
            yb = yb.to(device, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)

            with timed("forward+loss"):
                logits = model(xb)
                loss = loss_fn(logits, yb)

            # Inject NaN to demonstrate anomaly detection
            if cfg.inject_nan_step > 0 and step == cfg.inject_nan_step:
                loss = loss * torch.tensor(float("nan"), device=loss.device)

            with timed("backward"):
                loss.backward()  # anomaly detection will print stack trace on NaN/Inf
            with timed("step"):
                optimizer.step()

            if step % 20 == 0:
                print({"step": step, "loss": round(float(loss.detach().cpu().item()), 4)})


if __name__ == "__main__":
    main()


