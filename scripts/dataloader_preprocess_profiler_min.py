from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import torch
import torch.nn.functional as F
from torch.profiler import ProfilerActivity, profile, record_function, schedule
from torch.utils.data import DataLoader, Dataset, get_worker_info


@dataclass
class ProfileCfg:
    samples: int = int(os.getenv("SAMPLES", "32768"))
    batch_size: int = int(os.getenv("BATCH", "1024"))
    channels: int = int(os.getenv("C", "3"))
    height: int = int(os.getenv("H", "64"))
    width: int = int(os.getenv("W", "64"))
    workers: int = int(os.getenv("WORKERS", "4"))
    prefetch: int = int(os.getenv("PREFETCH", "2"))
    persistent: bool = bool(int(os.getenv("PERSISTENT", "1")))
    pin_memory: bool = bool(int(os.getenv("PIN", "1")))
    steps: int = int(os.getenv("STEPS", "20"))
    export_trace: bool = bool(int(os.getenv("EXPORT_TRACE", "0")))
    out_dir: str = os.getenv("OUT", "outputs/profile")


class PreprocessDataset(Dataset):
    def __init__(self, n: int, c: int, h: int, w: int, seed: int = 0) -> None:
        self.n = n
        self.c = c
        self.h = h
        self.w = w
        self.seed = seed

    def __len__(self) -> int:
        return self.n

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        # Simulate CPU-side "decode" and "preprocess"
        info = get_worker_info()
        worker = info.id if info is not None else 0
        g = torch.Generator().manual_seed(self.seed + 31 * worker + 17 * idx)
        x = torch.randn(self.c, self.h, self.w, generator=g)
        # Lightweight augmentations on CPU
        if (idx + worker) % 2 == 0:
            x = torch.flip(x, dims=[-1])  # horizontal flip
        x = (x - 0.5) / 0.5  # normalize
        # Small blur via avg pool to simulate filter
        x = F.avg_pool2d(x.unsqueeze(0), kernel_size=3, stride=1, padding=1).squeeze(0)
        y = torch.randint(0, 10, (1,), generator=g).squeeze(0)
        return x, y


def build_loader(cfg: ProfileCfg) -> DataLoader:
    ds = PreprocessDataset(cfg.samples, cfg.channels, cfg.height, cfg.width, seed=0)
    return DataLoader(
        ds,
        batch_size=cfg.batch_size,
        shuffle=True,
        num_workers=cfg.workers,
        pin_memory=cfg.pin_memory,
        persistent_workers=cfg.persistent if cfg.workers > 0 else False,
        prefetch_factor=cfg.prefetch if cfg.workers > 0 else None,  # type: ignore[arg-type]
        drop_last=True,
    )


def main() -> None:
    cfg = ProfileCfg()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    loader = build_loader(cfg)

    # Simple wall-clock breakdown
    fetch_times, h2d_times = [], []
    total_start = time.perf_counter()
    it = iter(loader)
    for step in range(cfg.steps):
        t0 = time.perf_counter()
        with record_function("dataloader_next"):
            xb, yb = next(it)
        t1 = time.perf_counter()
        fetch_times.append(t1 - t0)

        with record_function("h2d_copy"):
            if device == "cuda":
                if cfg.pin_memory:
                    xb = xb.pin_memory() if not xb.is_pinned() else xb
                    yb = yb.pin_memory() if not yb.is_pinned() else yb
                xb = xb.to(device, non_blocking=True)
                yb = yb.to(device, non_blocking=True)
                torch.cuda.current_stream().synchronize()
        t2 = time.perf_counter()
        h2d_times.append(t2 - t1)

    total_elapsed = time.perf_counter() - total_start
    items = cfg.steps * cfg.batch_size
    print(
        f"steps={cfg.steps} items={items} total_s={total_elapsed:.3f} fetch_ms={1000*sum(fetch_times)/len(fetch_times):.2f} "
        f"h2d_ms={1000*sum(h2d_times)/len(h2d_times):.2f} items_per_s={items/total_elapsed:.1f}"
    )

    # Optional torch.profiler trace
    if cfg.export_trace:
        activities = [ProfilerActivity.CPU]
        if device == "cuda":
            activities.append(ProfilerActivity.CUDA)
        sched = schedule(wait=1, warmup=1, active=3, repeat=1)
        trace_path = out_dir / "trace.json"
        with profile(activities=activities, schedule=sched, record_shapes=True, profile_memory=True, with_stack=False) as prof:
            it = iter(loader)
            for _ in range(5):
                prof.step()
                xb, yb = next(it)
                if device == "cuda":
                    xb = xb.to(device, non_blocking=True)
                    yb = yb.to(device, non_blocking=True)
                # Minimal no-op forward to register HtoD and CPU kernels
                _ = xb.mean() + (yb.float().mean() if yb.dtype.is_floating_point else yb.float().mean())
        prof.export_chrome_trace(str(trace_path))
        print(f"Exported chrome trace to {trace_path}")


if __name__ == "__main__":
    main()



