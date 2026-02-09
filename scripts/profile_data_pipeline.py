from __future__ import annotations

import argparse
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset, TensorDataset


@dataclass
class ProfileConfig:
    steps: int = 200
    batch_size: int = 256
    num_workers: int = 4
    pin_memory: bool = True
    persistent_workers: bool = True
    prefetch_factor: int = 2
    io_sleep_ms: int = 0
    cpu_ops: int = 2
    input_dim: int = 128
    num_classes: int = 10
    amp: bool = True
    profile: bool = True
    trace_dir: str = "runs/profiler"


class SyntheticPreprocDataset(Dataset):
    def __init__(self, length: int, input_dim: int, num_classes: int, io_sleep_ms: int, cpu_ops: int):
        self.length = length
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.io_sleep_ms = io_sleep_ms
        self.cpu_ops = max(int(cpu_ops), 0)

        gen_features = torch.randn(length, input_dim)
        weights = torch.randn(input_dim, num_classes)
        logits = gen_features @ weights
        targets = torch.multinomial(logits.softmax(-1), 1).squeeze(-1)

        self.features = gen_features
        self.targets = targets

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        if self.io_sleep_ms > 0:
            time.sleep(self.io_sleep_ms / 1000.0)

        x = self.features[idx]
        # CPU-bound preprocessing
        for _ in range(self.cpu_ops):
            x = (x.tanh().add(0.1).mul(1.1)).relu()
        y = self.targets[idx]
        return x, y


class MLP(nn.Module):
    def __init__(self, in_dim: int, hidden: List[int], out_dim: int):
        super().__init__()
        layers: List[nn.Module] = []
        last = in_dim
        for h in hidden:
            layers += [nn.Linear(last, h), nn.GELU()]
            last = h
        layers.append(nn.Linear(last, out_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


@torch.no_grad()
def _sync_if_cuda(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def benchmark_pipeline(cfg: ProfileConfig) -> Dict[str, float]:
    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")
    torch.backends.cudnn.benchmark = (device.type == "cuda")

    dataset_len = cfg.steps * cfg.batch_size * 2
    ds = SyntheticPreprocDataset(
        length=dataset_len,
        input_dim=cfg.input_dim,
        num_classes=cfg.num_classes,
        io_sleep_ms=cfg.io_sleep_ms,
        cpu_ops=cfg.cpu_ops,
    )

    loader = DataLoader(
        ds,
        batch_size=cfg.batch_size,
        shuffle=False,
        num_workers=cfg.num_workers,
        pin_memory=(cfg.pin_memory and device.type == "cuda"),
        persistent_workers=(cfg.persistent_workers and cfg.num_workers > 0),
        prefetch_factor=max(cfg.prefetch_factor, 2) if cfg.num_workers > 0 else None,
    )

    model = MLP(cfg.input_dim, [256, 256], cfg.num_classes).to(device)
    loss_fn = nn.CrossEntropyLoss()
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    scaler = torch.cuda.amp.GradScaler(enabled=(cfg.amp and device.type == "cuda"))

    times_copy: List[float] = []
    times_fwd: List[float] = []
    times_total: List[float] = []
    num_samples: int = 0

    use_profiler = (cfg.profile and (device.type in {"cuda", "cpu"}))
    activities = []
    try:
        from torch.profiler import ProfilerActivity
        activities = [ProfilerActivity.CPU]
        if device.type == "cuda":
            activities.append(ProfilerActivity.CUDA)
    except Exception:
        use_profiler = False

    prof_ctx = nullcontext()
    if use_profiler:
        from torch.profiler import profile, schedule, tensorboard_trace_handler
        prof_ctx = profile(
            activities=activities,
            schedule=schedule(wait=2, warmup=3, active=10, repeat=1),
            on_trace_ready=tensorboard_trace_handler(cfg.trace_dir),
            record_shapes=True,
            with_stack=True,
            profile_memory=True,
        )

    with prof_ctx as prof:
        for step, (xb, yb) in enumerate(loader, start=1):
            if step > cfg.steps:
                break

            t0 = time.perf_counter()
            # HtoD copy
            xb = xb.to(device, non_blocking=True)
            yb = yb.to(device, non_blocking=True)
            _sync_if_cuda(device)
            t1 = time.perf_counter()

            with torch.cuda.amp.autocast(enabled=(cfg.amp and device.type == "cuda")):
                logits = model(xb)
                loss = loss_fn(logits, yb)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            opt.zero_grad(set_to_none=True)
            _sync_if_cuda(device)
            t2 = time.perf_counter()

            times_copy.append((t1 - t0) * 1000.0)
            times_fwd.append((t2 - t1) * 1000.0)
            times_total.append((t2 - t0) * 1000.0)
            num_samples += xb.size(0)

            if use_profiler:
                prof.step()

    copy_ms = sum(times_copy) / max(len(times_copy), 1)
    fwd_ms = sum(times_fwd) / max(len(times_fwd), 1)
    total_ms = sum(times_total) / max(len(times_total), 1)
    samples_per_s = (num_samples / (sum(times_total) / 1000.0)) if times_total else 0.0

    return {
        "avg_copy_ms": copy_ms,
        "avg_forward_ms": fwd_ms,
        "avg_total_ms": total_ms,
        "throughput_samples_per_s": samples_per_s,
    }


class nullcontext:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


def parse_args() -> ProfileConfig:
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=200)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--pin-memory", action="store_true")
    p.add_argument("--no-pin-memory", dest="pin_memory", action="store_false")
    p.set_defaults(pin_memory=True)
    p.add_argument("--persistent-workers", action="store_true")
    p.add_argument("--no-persistent-workers", dest="persistent_workers", action="store_false")
    p.set_defaults(persistent_workers=True)
    p.add_argument("--prefetch-factor", type=int, default=2)
    p.add_argument("--io-sleep-ms", type=int, default=0)
    p.add_argument("--cpu-ops", type=int, default=2)
    p.add_argument("--input-dim", type=int, default=128)
    p.add_argument("--num-classes", type=int, default=10)
    p.add_argument("--no-amp", dest="amp", action="store_false")
    p.set_defaults(amp=True)
    p.add_argument("--no-profile", dest="profile", action="store_false")
    p.set_defaults(profile=True)
    p.add_argument("--trace-dir", type=str, default="runs/profiler")
    a = p.parse_args()
    return ProfileConfig(
        steps=a.steps,
        batch_size=a.batch_size,
        num_workers=a.num_workers,
        pin_memory=a.pin_memory,
        persistent_workers=a.persistent_workers,
        prefetch_factor=a.prefetch_factor,
        io_sleep_ms=a.io_sleep_ms,
        cpu_ops=a.cpu_ops,
        input_dim=a.input_dim,
        num_classes=a.num_classes,
        amp=a.amp,
        profile=a.profile,
        trace_dir=a.trace_dir,
    )


def main() -> None:
    cfg = parse_args()
    os.makedirs(cfg.trace_dir, exist_ok=True)
    metrics = benchmark_pipeline(cfg)
    print({k: round(v, 3) for k, v in metrics.items()})


if __name__ == "__main__":
    main()



