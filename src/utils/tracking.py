from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from torch.utils.tensorboard import SummaryWriter


@dataclass
class TrackingConfig:
    use_wandb: bool = False
    tensorboard: bool = True
    log_dir: str = "experiments"
    run_name: Optional[str] = None
    wandb_project: Optional[str] = None
    wandb_entity: Optional[str] = None


class Tracker:
    def __init__(self, cfg: TrackingConfig) -> None:
        self.cfg = cfg
        self.tb: Optional[SummaryWriter] = None
        self._wb = None

    def start(self) -> None:
        if self.cfg.tensorboard:
            os.makedirs(self.cfg.log_dir, exist_ok=True)
            self.tb = SummaryWriter(log_dir=self.cfg.log_dir)
        if self.cfg.use_wandb:
            try:
                import wandb

                self._wb = wandb
                wandb.init(project=self.cfg.wandb_project or "project", entity=self.cfg.wandb_entity, name=self.cfg.run_name)
            except Exception:
                self._wb = None

    def log_metrics(self, metrics: Dict[str, float], step: int, prefix: str = "") -> None:
        if prefix:
            metrics = {f"{prefix}/{k}": v for k, v in metrics.items()}
        if self.tb is not None:
            for k, v in metrics.items():
                self.tb.add_scalar(k, v, step)
        if self._wb is not None:
            try:
                self._wb.log(metrics, step=step)
            except Exception:
                pass

    def finish(self) -> None:
        if self.tb is not None:
            self.tb.flush()
            self.tb.close()
            self.tb = None
        if self._wb is not None:
            try:
                self._wb.finish()
            except Exception:
                pass
            self._wb = None



