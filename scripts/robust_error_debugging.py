from __future__ import annotations

import logging
import math
import os
import time
from dataclasses import dataclass
from typing import Callable, Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


def setup_logger(name: str = "trainer", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


@dataclass
class DebugConfig:
    input_dim: int = int(os.getenv("INPUT_DIM", "128"))
    hidden_dim: int = int(os.getenv("HIDDEN", "256"))
    num_classes: int = int(os.getenv("CLASSES", "8"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "512"))
    steps: int = int(os.getenv("STEPS", "400"))
    lr: float = float(os.getenv("LR", "3e-4"))
    wd: float = float(os.getenv("WD", "1e-2"))
    amp: bool = bool(int(os.getenv("AMP", "1")))
    clip_norm: float = float(os.getenv("CLIP", "1.0"))
    retries: int = int(os.getenv("RETRIES", "2"))
    anomaly: bool = bool(int(os.getenv("ANOMALY", "0")))
    seed: int = int(os.getenv("SEED", "0"))


class RandomDataset(Dataset):
    def __init__(self, n: int, d: int, c: int, seed: int) -> None:
        g = torch.Generator().manual_seed(seed)
        self.x = torch.randn(n, d, generator=g)
        W = torch.randn(c, d, generator=g)
        self.y = (self.x @ W.T).argmax(dim=1)

    def __len__(self) -> int:
        return self.x.size(0)

    def __getitem__(self, i: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.x[i], self.y[i]


class MLP(nn.Module):
    def __init__(self, d: int, h: int, c: int) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, h), nn.ReLU(inplace=True), nn.Linear(h, c))
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, a=math.sqrt(5))
                if m.bias is not None:
                    fan_in, _ = nn.init._calculate_fan_in_and_fan_out(m.weight)
                    bound = 1 / math.sqrt(fan_in)
                    nn.init.uniform_(m.bias, -bound, bound)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def retry(max_retries: int, exceptions: Tuple[type[BaseException], ...], logger: logging.Logger):
    def decorator(fn: Callable):
        def wrapper(*args, **kwargs):
            delay = 0.5
            for attempt in range(max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_retries:
                        logger.error(f"Operation failed after {attempt+1} attempts: {e}")
                        raise
                    logger.warning(f"Error: {e}. Retrying in {delay:.1f}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(delay)
                    delay = min(delay * 2, 5.0)
        return wrapper
    return decorator


def train_with_debug() -> None:
    cfg = DebugConfig()
    logger = setup_logger()
    torch.manual_seed(cfg.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    if cfg.anomaly:
        torch.autograd.set_detect_anomaly(True)
        logger.info("Enabled autograd anomaly detection")

    ds = RandomDataset(20_000, cfg.input_dim, cfg.num_classes, seed=cfg.seed)
    loader = DataLoader(ds, batch_size=cfg.batch_size, shuffle=True, drop_last=True)
    model = MLP(cfg.input_dim, cfg.hidden_dim, cfg.num_classes).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.wd)
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.amp and device == "cuda")
    crit = nn.CrossEntropyLoss()

    @retry(cfg.retries, (RuntimeError,), logger)
    def step_batch(xb: torch.Tensor, yb: torch.Tensor) -> float:
        nonlocal model, opt, scaler
        xb = xb.to(device)
        yb = yb.to(device)
        with torch.cuda.amp.autocast(enabled=cfg.amp and device == "cuda"):
            logits = model(xb)
            loss = crit(logits, yb)
        if not torch.isfinite(loss):
            raise RuntimeError("Non-finite loss detected")
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        nn.utils.clip_grad_norm_(model.parameters(), cfg.clip_norm)
        scaler.step(opt)
        scaler.update()
        opt.zero_grad(set_to_none=True)
        return float(loss.detach().cpu())

    step = 0
    for xb, yb in loader:
        try:
            loss_val = step_batch(xb, yb)
            step += 1
            if step % 50 == 0:
                logger.info(f"step={step} loss={loss_val:.4f}")
            if step >= cfg.steps:
                break
        except Exception as e:
            logger.exception(f"Unrecoverable error at step={step}: {e}")
            break


if __name__ == "__main__":
    train_with_debug()

from __future__ import annotations

import functools
import os
import random
import time
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 0.2,
    jitter: float = 0.1,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt > max_retries:
                        raise
                    delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, jitter)
                    time.sleep(delay)
        return wrapper
    return decorator


@retry_with_backoff(max_retries=4, base_delay=0.1, jitter=0.05)
def flaky_operation(x: int) -> int:
    if random.random() < 0.5:
        raise RuntimeError("Transient failure")
    return x * 2


def main() -> None:
    random.seed(int(os.getenv("SEED", "0")))
    successes = 0
    trials = 20
    for i in range(trials):
        try:
            y = flaky_operation(i)
            successes += 1
        except Exception:
            pass
    print(f"successes={successes}/{trials}")


if __name__ == "__main__":
    main()


