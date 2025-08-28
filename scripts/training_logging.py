from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


@dataclass
class LogConfig:
    out_dir: str = os.getenv("LOG_DIR", "logs/training")
    steps: int = int(os.getenv("STEPS", "100"))
    batch: int = int(os.getenv("BATCH", "512"))
    dim: int = int(os.getenv("DIM", "128"))
    classes: int = int(os.getenv("CLASSES", "10"))


class ToyDS(Dataset):
    def __init__(self, n: int, d: int, c: int) -> None:
        g = torch.Generator().manual_seed(0)
        self.x = torch.randn(n, d, generator=g)
        W = torch.randn(c, d, generator=g)
        self.y = (self.x @ W.T).argmax(dim=1)

    def __len__(self) -> int: return self.x.size(0)
    def __getitem__(self, i: int): return self.x[i], self.y[i]


class SmallMLP(nn.Module):
    def __init__(self, d: int, c: int) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, 256), nn.ReLU(), nn.Linear(256, c))
    def forward(self, x): return self.net(x)


def log_event(path: Path, kind: str, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ts": time.time(), "kind": kind, **payload}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def main() -> None:
    cfg = LogConfig()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SmallMLP(cfg.dim, cfg.classes).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4)
    crit = nn.CrossEntropyLoss()

    loader = DataLoader(ToyDS(cfg.batch * 20, cfg.dim, cfg.classes), batch_size=cfg.batch, shuffle=True)
    log_path = Path(cfg.out_dir) / "events.jsonl"

    step = 0
    for xb, yb in loader:
        xb = xb.to(device)
        yb = yb.to(device)
        logits = model(xb)
        loss = crit(logits, yb)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()

        acc = float((logits.argmax(dim=1) == yb).float().mean().item())
        log_event(log_path, "train_step", {"step": step, "loss": float(loss.item()), "acc": acc})
        step += 1
        if step >= cfg.steps:
            break


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


@dataclass
class LogCfg:
    out_dir: str = "logs"
    jsonl_file: str = "train.jsonl"
    epochs: int = 3
    batch_size: int = 256
    input_dim: int = 128
    num_classes: int = 10


def log_jsonl(path: Path, record: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


class TinyMLP(nn.Module):
    def __init__(self, input_dim: int, num_classes: int) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(input_dim, 256), nn.GELU(), nn.Linear(256, num_classes))

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # type: ignore[override]
        return self.net(x)


def main() -> None:
    cfg = LogCfg()
    out = Path(cfg.out_dir) / cfg.jsonl_file
    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")

    x = torch.randn(50_000, cfg.input_dim)
    w = torch.randn(cfg.input_dim, cfg.num_classes)
    y = torch.multinomial((x @ w).softmax(-1), 1).squeeze(-1)
    loader = DataLoader(TensorDataset(x, y), batch_size=cfg.batch_size, shuffle=True)

    model = TinyMLP(cfg.input_dim, cfg.num_classes).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    loss_fn = nn.CrossEntropyLoss()

    global_step = 0
    t0 = time.perf_counter()
    for epoch in range(cfg.epochs):
        model.train()
        running = 0.0
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            logits = model(xb)
            loss = loss_fn(logits, yb)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            running += float(loss)
            global_step += 1

        dt = time.perf_counter() - t0
        rec = {"epoch": epoch, "train_loss": round(running / max(1, len(loader)), 4), "elapsed_s": round(dt, 2)}
        print(rec)
        log_jsonl(out, rec)


if __name__ == "__main__":
    main()


