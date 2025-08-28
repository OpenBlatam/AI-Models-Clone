from __future__ import annotations

import dataclasses
from dataclasses import asdict
from typing import Any, Dict

import yaml

from src.utils.config import DataConfig, ModelConfig, TrainConfig
from src.utils.tracking import TrackingConfig
from src.utils.checkpoint import CheckpointConfig


def _merge_dict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge_dict(out[k], v)
        else:
            out[k] = v
    return out


def load_yaml_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def build_configs(cfg: Dict[str, Any]) -> tuple[ModelConfig, DataConfig, TrainConfig, TrackingConfig, CheckpointConfig]:
    model = cfg.get("model", {})
    data = cfg.get("data", {})
    train = cfg.get("train", {})
    tracking = cfg.get("tracking", {})
    checkpointing = cfg.get("checkpointing", {})

    model_cfg = ModelConfig(
        input_dim=int(model.get("input_dim", ModelConfig.input_dim)),
        hidden_dims=tuple(int(x) for x in model.get("hidden_dims", list(ModelConfig.hidden_dims))),
        num_classes=int(model.get("num_classes", ModelConfig.num_classes)),
        dropout=float(model.get("dropout", ModelConfig.dropout)),
    )
    data_cfg = DataConfig(
        train_samples=int(data.get("train_samples", DataConfig.train_samples)),
        val_samples=int(data.get("val_samples", DataConfig.val_samples)),
        batch_size=int(data.get("batch_size", DataConfig.batch_size)),
        num_workers=int(data.get("num_workers", DataConfig.num_workers)),
        pin_memory=bool(data.get("pin_memory", DataConfig.pin_memory)),
        persistent_workers=bool(data.get("persistent_workers", DataConfig.persistent_workers)),
        prefetch_factor=int(data.get("prefetch_factor", DataConfig.prefetch_factor)),
    )
    train_cfg = TrainConfig(
        epochs=int(train.get("epochs", TrainConfig.epochs)),
        learning_rate=float(train.get("learning_rate", TrainConfig.learning_rate)),
        weight_decay=float(train.get("weight_decay", TrainConfig.weight_decay)),
        grad_clip_norm=float(train.get("grad_clip_norm", TrainConfig.grad_clip_norm)),
        amp=bool(train.get("amp", TrainConfig.amp)),
        grad_accum_steps=int(train.get("grad_accum_steps", TrainConfig.grad_accum_steps)),
    )
    tracking_cfg = TrackingConfig(
        use_wandb=bool(tracking.get("use_wandb", False)),
        tensorboard=bool(tracking.get("tensorboard", True)),
        log_dir=str(tracking.get("log_dir", "experiments")),
        run_name=tracking.get("run_name"),
        wandb_project=(tracking.get("wandb", {}) or {}).get("project"),
        wandb_entity=(tracking.get("wandb", {}) or {}).get("entity"),
    )
    ckpt_cfg = CheckpointConfig(
        directory=str(checkpointing.get("dir", "checkpoints")),
        monitor=str(checkpointing.get("monitor", "val/loss")),
        mode=str(checkpointing.get("mode", "min")),
        save_top_k=int(checkpointing.get("save_top_k", 1)),
        save_every=int(checkpointing.get("save_every", 1)),
    )
    return model_cfg, data_cfg, train_cfg, tracking_cfg, ckpt_cfg


