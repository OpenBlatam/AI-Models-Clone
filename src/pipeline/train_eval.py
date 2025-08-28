from __future__ import annotations

import os
from typing import Dict

import torch
from torch import nn

from src.utils.config_loader import load_yaml_config, build_configs
from src.data.synthetic import build_dataloaders
from src.models.mlp_classifier import MLPClassifier
from src.training.engine import train_one_epoch, evaluate


def run(config_path: str = "config/train.yaml") -> Dict[str, float]:
    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True

    yaml_cfg = load_yaml_config(config_path)
    model_cfg, data_cfg, train_cfg, tracking_cfg, ckpt_cfg = build_configs(yaml_cfg)

    train_loader, val_loader = build_dataloaders(
        train_samples=data_cfg.train_samples,
        val_samples=data_cfg.val_samples,
        input_dim=model_cfg.input_dim,
        num_classes=model_cfg.num_classes,
        batch_size=data_cfg.batch_size,
        num_workers=data_cfg.num_workers,
        pin_memory=(data_cfg.pin_memory and device.type == "cuda"),
        persistent_workers=data_cfg.persistent_workers,
        prefetch_factor=data_cfg.prefetch_factor,
    )

    model = MLPClassifier(model_cfg.input_dim, list(model_cfg.hidden_dims), model_cfg.num_classes, model_cfg.dropout).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=train_cfg.learning_rate, weight_decay=train_cfg.weight_decay)
    loss_fn = nn.CrossEntropyLoss()

    last_metrics: Dict[str, float] = {}
    for epoch in range(train_cfg.epochs):
        _ = train_one_epoch(
            model=model,
            loader=train_loader,
            optimizer=optimizer,
            loss_fn=loss_fn,
            device=device,
            use_amp=train_cfg.amp,
            grad_clip_norm=train_cfg.grad_clip_norm,
            grad_accum_steps=train_cfg.grad_accum_steps,
        )
        last_metrics = evaluate(model, val_loader, loss_fn, device)
    return last_metrics


if __name__ == "__main__":
    print(run(os.environ.get("CONFIG", "config/train.yaml")))



