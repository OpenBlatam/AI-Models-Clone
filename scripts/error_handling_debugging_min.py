from __future__ import annotations

import json
import logging
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


def setup_logger(name: str = "trainer") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S")
        )
        logger.addHandler(handler)
    return logger


def write_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": time.time(), **record}) + "\n")


def zero_nonfinite_grads(model: nn.Module) -> bool:
    found = False
    for p in model.parameters():
        if p.grad is None:
            continue
        mask = ~torch.isfinite(p.grad)
        if mask.any():
            p.grad[mask] = 0.0
            found = True
    return found


class NaNGradientHook:
    def __init__(self) -> None:
        self.detected = False

    def hook(self, module: nn.Module, grad_input, grad_output):  # type: ignore[no-untyped-def]
        for g in grad_input:
            if g is not None and not torch.isfinite(g).all():
                self.detected = True


@dataclass
class Cfg:
    dim: int = int(os.getenv("DIM", "128"))
    classes: int = int(os.getenv("CLASSES", "10"))
    batch: int = int(os.getenv("BATCH", "512"))
    steps: int = int(os.getenv("STEPS", "200"))
    lr: float = float(os.getenv("LR", "3e-4"))
    wd: float = float(os.getenv("WD", "1e-2"))
    amp: bool = bool(int(os.getenv("AMP", "1")))
    clip: float = float(os.getenv("CLIP", "1.0"))
    anomaly: bool = bool(int(os.getenv("ANOMALY", "0")))
    export_trace: bool = bool(int(os.getenv("EXPORT_TRACE", "0")))
    log_dir: str = os.getenv("LOG_DIR", "logs/error_debug_min")
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
        self.net = nn.Sequential(nn.Linear(d, 256), nn.ReLU(True), nn.Linear(256, c))
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, a=math.sqrt(5))
                if m.bias is not None:
                    fan_in, _ = nn.init._calculate_fan_in_and_fan_out(m.weight)
                    bound = 1 / math.sqrt(max(1, fan_in))
                    nn.init.uniform_(m.bias, -bound, bound)
    def forward(self, x: torch.Tensor) -> torch.Tensor: return self.net(x)


def main() -> None:
    cfg = Cfg()
    logger = setup_logger()
    torch.manual_seed(cfg.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if cfg.anomaly:
        torch.autograd.set_detect_anomaly(True)
        logger.info("autograd anomaly detection enabled")

    ds = ToyDS(cfg.batch * 40, cfg.dim, cfg.classes, cfg.seed)
    loader = DataLoader(ds, batch_size=cfg.batch, shuffle=True, drop_last=True)

    model = MLP(cfg.dim, cfg.classes).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.wd)
    crit = nn.CrossEntropyLoss()
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.amp and device == "cuda")

    hook = NaNGradientHook()
    handles = []
    for m in model.modules():
        if isinstance(m, nn.Linear):
            handles.append(m.register_backward_hook(hook.hook))

    events = Path(cfg.log_dir) / "events.jsonl"
    errors = Path(cfg.log_dir) / "errors.jsonl"

    profiler_ctx = (
        torch.profiler.profile(
            activities=[torch.profiler.ProfilerActivity.CPU] + ([torch.profiler.ProfilerActivity.CUDA] if device == "cuda" else []),
            record_shapes=True,
            profile_memory=True,
        )
        if cfg.export_trace
        else nullcontext()
    )

    step = 0
    try:
        with profiler_ctx as prof:  # type: ignore[attr-defined]
            for xb, yb in loader:
                xb = xb.to(device, non_blocking=True)
                yb = yb.to(device, non_blocking=True)
                try:
                    with torch.cuda.amp.autocast(enabled=cfg.amp and device == "cuda"):
                        logits = model(xb)
                        loss = crit(logits, yb)
                    if not torch.isfinite(loss):
                        raise RuntimeError("non-finite loss")
                    scaler.scale(loss).backward()
                    scaler.unscale_(opt)
                    zero_nonfinite_grads(model)
                    if cfg.clip > 0:
                        nn.utils.clip_grad_norm_(model.parameters(), cfg.clip)
                    scaler.step(opt)
                    scaler.update()
                    opt.zero_grad(set_to_none=True)

                    acc = float((logits.argmax(1) == yb).float().mean().item())
                    write_jsonl(events, {"step": step, "loss": float(loss.item()), "acc": acc, "nan_hook": hook.detected})
                    if step % 50 == 0:
                        logger.info(f"step={step} loss={float(loss.item()):.4f} acc={acc:.4f} nan_hook={hook.detected}")
                except RuntimeError as e:
                    write_jsonl(errors, {"step": step, "error": str(e)})
                    logger.warning(f"recoverable error at step={step}: {e}")
                    opt.zero_grad(set_to_none=True)
                finally:
                    step += 1
                    if cfg.export_trace and prof is not None:
                        prof.step()  # type: ignore[call-arg]
                    if step >= cfg.steps:
                        break
    finally:
        for h in handles:
            h.remove()
        if cfg.export_trace and profiler_ctx is not None and hasattr(profiler_ctx, "export_chrome_trace"):
            # best-effort export
            try:
                out = Path(cfg.log_dir) / "trace.json"
                profiler_ctx.export_chrome_trace(str(out))  # type: ignore[union-attr]
            except Exception:
                pass


class nullcontext:
    def __enter__(self):
        return None
    def __exit__(self, *args):
        return False


if __name__ == "__main__":
    main()



