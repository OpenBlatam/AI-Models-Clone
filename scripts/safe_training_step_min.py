from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


@dataclass
class SafeConfig:
    input_dim: int = int(os.getenv("INPUT_DIM", "256"))
    hidden_dim: int = int(os.getenv("HIDDEN", "512"))
    num_classes: int = int(os.getenv("CLASSES", "10"))

    batch_size: int = int(os.getenv("BATCH_SIZE", "512"))
    steps: int = int(os.getenv("STEPS", "200"))
    lr: float = float(os.getenv("LR", "3e-4"))
    wd: float = float(os.getenv("WD", "1e-2"))
    amp: bool = bool(int(os.getenv("AMP", "1")))

    clip_norm: float = float(os.getenv("CLIP_NORM", "1.0"))
    clip_value: float = float(os.getenv("CLIP_VALUE", "0.0"))  # 0 disables value clipping
    detect_anomaly: bool = bool(int(os.getenv("ANOMALY", "0")))
    seed: int = int(os.getenv("SEED", "1234"))


class RandomDataset(Dataset):
    def __init__(self, num_samples: int, input_dim: int, num_classes: int, seed: int) -> None:
        g = torch.Generator().manual_seed(seed)
        self.x = torch.randn(num_samples, input_dim, generator=g)
        w = torch.randn(num_classes, input_dim, generator=g)
        self.y = (self.x @ w.T).argmax(dim=1)

    def __len__(self) -> int:
        return self.x.size(0)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.x[idx], self.y[idx]


class MLP(nn.Module):
    def __init__(self, d_in: int, d_hid: int, num_classes: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_in, d_hid), nn.ReLU(inplace=True), nn.Linear(d_hid, num_classes)
        )
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, a=math.sqrt(5))
                if m.bias is not None:
                    fan_in, _ = nn.init._calculate_fan_in_and_fan_out(m.weight)
                    bound = 1 / math.sqrt(fan_in)
                    nn.init.uniform_(m.bias, -bound, bound)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def replace_nonfinite_grads_with_zero(model: nn.Module) -> bool:
    found_nonfinite = False
    for p in model.parameters():
        if p.grad is None:
            continue
        grad = p.grad
        mask = ~torch.isfinite(grad)
        if mask.any():
            grad[mask] = 0.0
            found_nonfinite = True
    return found_nonfinite


def total_grad_norm(model: nn.Module) -> torch.Tensor:
    norms = []
    for p in model.parameters():
        if p.grad is not None:
            norms.append(p.grad.detach().norm())
    if not norms:
        return torch.tensor(0.0)
    return torch.linalg.vector_norm(torch.stack(norms))


def train_safe_step() -> None:
    cfg = SafeConfig()
    torch.manual_seed(cfg.seed)
    device = get_device()

    if cfg.detect_anomaly:
        torch.autograd.set_detect_anomaly(True)

    ds = RandomDataset(num_samples=10_000, input_dim=cfg.input_dim, num_classes=cfg.num_classes, seed=cfg.seed)
    loader = DataLoader(ds, batch_size=cfg.batch_size, shuffle=True, drop_last=True, num_workers=0)

    model = MLP(cfg.input_dim, cfg.hidden_dim, cfg.num_classes).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.wd)
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.amp and device == "cuda")
    crit = nn.CrossEntropyLoss()

    step = 0
    for xb, yb in loader:
        xb = xb.to(device)
        yb = yb.to(device)

        with torch.cuda.amp.autocast(enabled=cfg.amp and device == "cuda"):
            logits = model(xb)
            loss = crit(logits, yb)

        if not torch.isfinite(loss):
            opt.zero_grad(set_to_none=True)
            continue

        scaler.scale(loss).backward()

        scaler.unscale_(opt)

        nonfinite = replace_nonfinite_grads_with_zero(model)
        if cfg.clip_value > 0:
            nn.utils.clip_grad_value_(model.parameters(), cfg.clip_value)
        if cfg.clip_norm > 0:
            nn.utils.clip_grad_norm_(model.parameters(), cfg.clip_norm)

        gnorm = total_grad_norm(model)
        if nonfinite or not torch.isfinite(gnorm):
            opt.zero_grad(set_to_none=True)
            scaler.update()  # keep scaler state moving
            step += 1
            if step >= cfg.steps:
                break
            continue

        scaler.step(opt)
        scaler.update()
        opt.zero_grad(set_to_none=True)

        step += 1
        if step % 20 == 0:
            print(f"step={step} loss={float(loss):.4f} grad_norm={float(gnorm):.4f}")
        if step >= cfg.steps:
            break


if __name__ == "__main__":
    train_safe_step()



