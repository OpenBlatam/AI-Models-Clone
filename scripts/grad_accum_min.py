from __future__ import annotations

import math
import os
from dataclasses import dataclass

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


@dataclass
class Cfg:
    dim: int = int(os.getenv("DIM", "128"))
    classes: int = int(os.getenv("CLASSES", "10"))
    batch: int = int(os.getenv("BATCH", "512"))
    steps: int = int(os.getenv("STEPS", "200"))
    lr: float = float(os.getenv("LR", "3e-4"))
    wd: float = float(os.getenv("WD", "1e-2"))
    amp: bool = bool(int(os.getenv("AMP", "1")))
    accum: int = int(os.getenv("ACCUM", "4"))
    seed: int = int(os.getenv("SEED", "0"))


class ToyDS(Dataset):
    def __init__(self, n: int, d: int, c: int, seed: int) -> None:
        g = torch.Generator().manual_seed(seed)
        self.x = torch.randn(n, d, generator=g)
        W = torch.randn(c, d, generator=g)
        self.y = (self.x @ W.T).argmax(dim=1)
    def __len__(self) -> int: return self.x.size(0)
    def __getitem__(self, i: int): return self.x[i], self.y[i]


class MLP(nn.Module):
    def __init__(self, d: int, c: int) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, 256), nn.ReLU(inplace=True), nn.Linear(256, c))
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, a=math.sqrt(5))
                if m.bias is not None:
                    fan_in, _ = nn.init._calculate_fan_in_and_fan_out(m.weight)
                    bound = 1 / math.sqrt(fan_in)
                    nn.init.uniform_(m.bias, -bound, bound)
    def forward(self, x): return self.net(x)


def main() -> None:
    cfg = Cfg()
    torch.manual_seed(cfg.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ds = ToyDS(cfg.batch * 40, cfg.dim, cfg.classes, seed=cfg.seed)
    loader = DataLoader(ds, batch_size=cfg.batch, shuffle=True, drop_last=True)

    model = MLP(cfg.dim, cfg.classes).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.wd)
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.amp and device == "cuda")
    crit = nn.CrossEntropyLoss()

    step = 0
    opt.zero_grad(set_to_none=True)
    for i, (xb, yb) in enumerate(loader):
        xb = xb.to(device, non_blocking=True)
        yb = yb.to(device, non_blocking=True)
        with torch.cuda.amp.autocast(enabled=cfg.amp and device == "cuda"):
            logits = model(xb)
            loss = crit(logits, yb) / cfg.accum
        scaler.scale(loss).backward()

        if (i + 1) % cfg.accum == 0:
            scaler.unscale_(opt)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt)
            scaler.update()
            opt.zero_grad(set_to_none=True)
            step += 1
            if step >= cfg.steps:
                break


if __name__ == "__main__":
    main()



