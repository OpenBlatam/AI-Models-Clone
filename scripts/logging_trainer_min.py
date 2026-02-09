from __future__ import annotations

import json
import logging
import math
import os
from dataclasses import dataclass
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


def setup_loggers(log_dir: Path) -> tuple[logging.Logger, Path, Path]:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("trainer_min")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(ch)
    events_path = log_dir / "events.jsonl"
    errors_path = log_dir / "errors.jsonl"
    return logger, events_path, errors_path


def write_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


@dataclass
class Cfg:
    dim: int = int(os.getenv("DIM", "128"))
    classes: int = int(os.getenv("CLASSES", "10"))
    batch: int = int(os.getenv("BATCH", "512"))
    steps: int = int(os.getenv("STEPS", "200"))
    lr: float = float(os.getenv("LR", "3e-4"))
    wd: float = float(os.getenv("WD", "1e-2"))
    clip: float = float(os.getenv("CLIP", "1.0"))
    amp: bool = bool(int(os.getenv("AMP", "1")))
    log_dir: str = os.getenv("LOG_DIR", "logs/trainer_min")


class ToyDS(Dataset):
    def __init__(self, n: int, d: int, c: int) -> None:
        g = torch.Generator().manual_seed(0)
        self.x = torch.randn(n, d, generator=g)
        W = torch.randn(c, d, generator=g)
        self.y = (self.x @ W.T).argmax(dim=1)
    def __len__(self) -> int: return self.x.size(0)
    def __getitem__(self, i: int): return self.x[i], self.y[i]


class MLP(nn.Module):
    def __init__(self, d: int, c: int) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, 256), nn.ReLU(), nn.Linear(256, c))
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
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger, events_path, errors_path = setup_loggers(Path(cfg.log_dir))

    model = MLP(cfg.dim, cfg.classes).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.wd)
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.amp and device == "cuda")
    crit = nn.CrossEntropyLoss()
    loader = DataLoader(ToyDS(cfg.batch * 20, cfg.dim, cfg.classes), batch_size=cfg.batch, shuffle=True)

    step = 0
    for xb, yb in loader:
        try:
            xb = xb.to(device)
            yb = yb.to(device)
            with torch.cuda.amp.autocast(enabled=cfg.amp and device == "cuda"):
                logits = model(xb)
                loss = crit(logits, yb)
            if not torch.isfinite(loss):
                raise RuntimeError("non-finite loss")
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            nn.utils.clip_grad_norm_(model.parameters(), cfg.clip)
            scaler.step(opt)
            scaler.update()
            opt.zero_grad(set_to_none=True)

            acc = float((logits.argmax(dim=1) == yb).float().mean().item())
            if step % 10 == 0:
                logger.info(f"step={step} loss={float(loss.item()):.4f} acc={acc:.4f}")
            write_jsonl(events_path, {"step": step, "loss": float(loss.item()), "acc": acc})
        except Exception as e:
            logger.exception(f"error at step={step}: {e}")
            write_jsonl(errors_path, {"step": step, "error": str(e)})
        finally:
            step += 1
            if step >= cfg.steps:
                break


if __name__ == "__main__":
    main()



