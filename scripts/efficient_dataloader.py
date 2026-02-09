from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Iterable, List, Tuple

import torch
from torch.utils.data import DataLoader, Dataset, get_worker_info


@dataclass
class LoaderConfig:
    samples: int = int(os.getenv("SAMPLES", "100000"))
    feature_dim: int = int(os.getenv("FEATURE_DIM", "512"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "1024"))
    num_workers: int = int(os.getenv("NUM_WORKERS", "4"))
    prefetch_factor: int = int(os.getenv("PREFETCH", "2"))
    persistent_workers: bool = bool(int(os.getenv("PERSISTENT", "1")))
    pin_memory: bool = bool(int(os.getenv("PIN_MEMORY", "1")))
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    epochs: int = int(os.getenv("EPOCHS", "2"))
    seed: int = int(os.getenv("SEED", "42"))


class SyntheticStreamingDataset(Dataset):
    def __init__(self, num_samples: int, feature_dim: int, seed: int) -> None:
        self.num_samples = num_samples
        self.feature_dim = feature_dim
        self.base_seed = seed

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, torch.Tensor]:
        info = get_worker_info()
        worker_id = info.id if info is not None else 0
        local_seed = self.base_seed + worker_id * 9973 + index * 17
        gen = torch.Generator().manual_seed(local_seed)
        x = torch.randn(self.feature_dim, generator=gen)
        y = torch.randint(0, 10, (1,), generator=gen).squeeze(0)
        return x, y


def collate_fn(batch: List[Tuple[torch.Tensor, torch.Tensor]]) -> Tuple[torch.Tensor, torch.Tensor]:
    xs, ys = zip(*batch)
    return torch.stack(list(xs), dim=0), torch.tensor(ys, dtype=torch.long)


def worker_init_fn(worker_id: int) -> None:  # deterministic workers
    base_seed = int(os.getenv("SEED", "42"))
    torch.manual_seed(base_seed + worker_id)
    torch.cuda.manual_seed_all(base_seed + worker_id)


def build_loader(cfg: LoaderConfig) -> DataLoader:
    dataset = SyntheticStreamingDataset(cfg.samples, cfg.feature_dim, seed=cfg.seed)
    return DataLoader(
        dataset,
        batch_size=cfg.batch_size,
        shuffle=True,
        num_workers=cfg.num_workers,
        pin_memory=cfg.pin_memory,
        persistent_workers=cfg.persistent_workers if cfg.num_workers > 0 else False,
        prefetch_factor=cfg.prefetch_factor if cfg.num_workers > 0 else None,  # type: ignore[arg-type]
        worker_init_fn=worker_init_fn if cfg.num_workers > 0 else None,
        collate_fn=collate_fn,
        drop_last=True,
    )


def benchmark_loader(loader: DataLoader, device: str, epochs: int) -> None:
    total_batches = 0
    start = time.perf_counter()
    for _ in range(epochs):
        for x, y in loader:
            if device == "cuda":
                x = x.pin_memory() if x.is_pinned() is False else x
                y = y.pin_memory() if y.is_pinned() is False else y
                x = x.to(device, non_blocking=True)
                y = y.to(device, non_blocking=True)
                torch.cuda.current_stream().synchronize()
            else:
                _ = x, y
            total_batches += 1
    elapsed = time.perf_counter() - start
    items = total_batches * loader.batch_size
    print(f"batches={total_batches} items={items} time_s={elapsed:.2f} items_per_s={items/elapsed:.1f}")


def main() -> None:
    cfg = LoaderConfig()
    torch.manual_seed(cfg.seed)
    if cfg.device == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.set_float32_matmul_precision("high")

    loader = build_loader(cfg)
    benchmark_loader(loader, cfg.device, cfg.epochs)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import os
import random
import time
from dataclasses import dataclass
from typing import Callable, Iterable, List, Tuple

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset, get_worker_info


@dataclass
class LoaderConfig:
    num_samples: int = 200_000
    input_dim: int = 1024
    batch_size: int = 512
    num_workers: int = max(2, (os.cpu_count() or 4) // 2)
    pin_memory: bool = True
    persistent_workers: bool = True
    prefetch_factor: int = 4
    io_sleep_ms: int = 0
    cpu_ops: int = 1
    seed: int = 1337


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


class SyntheticIOHeavyDataset(Dataset[Tuple[torch.Tensor, torch.Tensor]]):
    def __init__(self, num_samples: int, input_dim: int, io_sleep_ms: int, cpu_ops: int) -> None:
        super().__init__()
        self.num_samples = num_samples
        self.input_dim = input_dim
        self.io_sleep_ms = int(max(0, io_sleep_ms))
        self.cpu_ops = int(max(0, cpu_ops))

        # Pre-generate base tensors (simulate memory-mapped arrays)
        generator = torch.Generator().manual_seed(42)
        self.features = torch.randn(num_samples, input_dim, generator=generator)
        weights = torch.randn(input_dim, 10, generator=generator)
        logits = self.features @ weights
        self.targets = torch.multinomial(logits.softmax(-1), 1).squeeze(-1)

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, torch.Tensor]:
        # Simulate disk latency or heavy deserialization
        if self.io_sleep_ms > 0:
            time.sleep(self.io_sleep_ms / 1000.0)

        x = self.features[index]
        y = self.targets[index]
        # Simulate CPU-bound preprocessing
        for _ in range(self.cpu_ops):
            x = x.tanh().add_(0.1).mul_(1.1).relu_()
        return x, y


def worker_init_fn(worker_id: int) -> None:
    info = get_worker_info()
    if info is None:
        return
    base_seed = info.seed
    random.seed(base_seed)
    np.random.seed(base_seed % (2**32 - 1))
    torch.manual_seed(base_seed)


def collate_and_pin(batch: List[Tuple[torch.Tensor, torch.Tensor]]) -> Tuple[torch.Tensor, torch.Tensor]:
    xs, ys = zip(*batch)
    x = torch.stack(xs, dim=0)
    y = torch.stack([yy.long() for yy in ys], dim=0)
    return x, y


def measure_throughput(loader: Iterable[Tuple[torch.Tensor, torch.Tensor]], device: torch.device, steps: int) -> float:
    model = nn.Linear(1024, 10).to(device)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-2)
    scaler = torch.cuda.amp.GradScaler(enabled=(device.type == "cuda"))

    num_seen = 0
    t0 = time.perf_counter()
    it = iter(loader)
    for _ in range(steps):
        try:
            xb, yb = next(it)
        except StopIteration:
            it = iter(loader)
            xb, yb = next(it)
        xb = xb.to(device, non_blocking=True)
        yb = yb.to(device, non_blocking=True)
        with torch.cuda.amp.autocast(enabled=(device.type == "cuda")):
            logits = model(xb)
            loss = loss_fn(logits, yb)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        num_seen += xb.size(0)
    t1 = time.perf_counter()
    return num_seen / (t1 - t0)


def main() -> None:
    ap = argparse.ArgumentParser(description="Efficient DataLoader demo with robust knobs")
    ap.add_argument("--num-samples", type=int, default=200_000)
    ap.add_argument("--input-dim", type=int, default=1024)
    ap.add_argument("--batch-size", type=int, default=512)
    ap.add_argument("--num-workers", type=int, default=max(2, (os.cpu_count() or 4) // 2))
    ap.add_argument("--pin-memory", action="store_true")
    ap.add_argument("--no-pin-memory", dest="pin_memory", action="store_false")
    ap.set_defaults(pin_memory=True)
    ap.add_argument("--persistent-workers", action="store_true")
    ap.add_argument("--no-persistent-workers", dest="persistent_workers", action="store_false")
    ap.set_defaults(persistent_workers=True)
    ap.add_argument("--prefetch-factor", type=int, default=4)
    ap.add_argument("--io-sleep-ms", type=int, default=0)
    ap.add_argument("--cpu-ops", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--measure-steps", type=int, default=400)
    args = ap.parse_args()

    cfg = LoaderConfig(
        num_samples=args.num_samples,
        input_dim=args.input_dim,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        pin_memory=args.pin_memory,
        persistent_workers=args.persistent_workers,
        prefetch_factor=args.prefetch_factor,
        io_sleep_ms=args.io_sleep_ms,
        cpu_ops=args.cpu_ops,
        seed=args.seed,
    )

    set_global_seed(cfg.seed)
    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")

    dataset = SyntheticIOHeavyDataset(cfg.num_samples, cfg.input_dim, cfg.io_sleep_ms, cfg.cpu_ops)
    loader = DataLoader(
        dataset,
        batch_size=cfg.batch_size,
        shuffle=True,
        num_workers=cfg.num_workers,
        pin_memory=(cfg.pin_memory and device.type == "cuda"),
        persistent_workers=(cfg.persistent_workers and cfg.num_workers > 0),
        prefetch_factor=cfg.prefetch_factor if cfg.num_workers > 0 else None,
        collate_fn=collate_and_pin,
        worker_init_fn=worker_init_fn,
    )

    throughput = measure_throughput(loader, device, steps=args.measure_steps)
    print({"throughput_samples_per_s": round(throughput, 2), "batch_size": cfg.batch_size, "num_workers": cfg.num_workers, "pin_memory": cfg.pin_memory, "prefetch_factor": cfg.prefetch_factor})


if __name__ == "__main__":
    main()


