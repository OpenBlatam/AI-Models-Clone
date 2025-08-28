from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelConfig:
    input_dim: int = 128
    hidden_dims: tuple[int, ...] = (256, 256)
    num_classes: int = 10
    dropout: float = 0.0


@dataclass
class DataConfig:
    train_samples: int = 60000
    val_samples: int = 6000
    batch_size: int = 256
    num_workers: int = 2
    pin_memory: bool = True
    persistent_workers: bool = False
    prefetch_factor: int = 2


@dataclass
class TrainConfig:
    epochs: int = 5
    learning_rate: float = 3e-4
    weight_decay: float = 0.01
    grad_clip_norm: float = 1.0
    amp: bool = True
    grad_accum_steps: int = 1



