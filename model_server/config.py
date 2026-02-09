from __future__ import annotations

import os
from dataclasses import dataclass


def _get_bool(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass
class ServerConfig:
    host: str = os.environ.get("HOST", "0.0.0.0")
    port: int = int(os.environ.get("PORT", "8000"))
    log_level: str = os.environ.get("LOG_LEVEL", "info")
    workers: int = int(os.environ.get("WORKERS", "1"))


@dataclass
class ModelConfig:
    input_dim: int = int(os.environ.get("MODEL_INPUT_DIM", "128"))
    num_classes: int = int(os.environ.get("MODEL_NUM_CLASSES", "10"))
    hidden_dims: tuple[int, ...] = tuple(int(x) for x in os.environ.get("MODEL_HIDDEN_DIMS", "256,256").split(",") if x)
    dropout: float = float(os.environ.get("MODEL_DROPOUT", "0.0"))
    checkpoint_path: str | None = os.environ.get("MODEL_CHECKPOINT")
    device: str = os.environ.get("DEVICE", "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") not in {"", None} else "cpu")
    amp: bool = _get_bool("AMP", True)


@dataclass
class BatchConfig:
    max_batch_size: int = int(os.environ.get("BATCH_MAX_SIZE", "32"))
    max_delay_ms: int = int(os.environ.get("BATCH_MAX_DELAY_MS", "4"))



