"""
Unified Trainer for TruthGPT
============================

Comprehensive training engine that integrates model training, validation,
EMA weight management, and robust error handling.
"""

import logging
import time
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple, Callable
from dataclasses import dataclass, field

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torch.cuda.amp import autocast, GradScaler
from tqdm import tqdm

try:
    import wandb
except ImportError:
    wandb = None

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """Standardized training configuration."""
    # Data parameters
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    shuffle: bool = True
    random_seed: int = 42
    
    # Optimizer parameters
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    betas: Tuple[float, float] = (0.9, 0.999)
    eps: float = 1e-8
    
    # Training parameters
    batch_size: int = 32
    gradient_accumulation_steps: int = 4
    num_epochs: int = 100
    warmup_steps: int = 1000
    max_grad_norm: float = 1.0
    
    # EMA (Exponential Moving Average) parameters
    use_ema: bool = True
    ema_decay: float = 0.999
    
    # Early stopping
    early_stopping_patience: int = 10
    min_delta: float = 1e-4
    
    # Evaluation & Checkpointing
    eval_interval: int = 500
    save_best_only: bool = True
    monitor_metric: str = "val_loss"
    mode: str = "min"  # min or max
    checkpoint_dir: str = "checkpoints"
    
    # Logging
    log_interval: int = 100
    use_wandb: bool = False
    wandb_project: str = "truthgpt"
    experiment_name: str = "truthgpt_unified"
    
    # Hardware
    device: str = "auto"
    num_workers: int = 4
    pin_memory: bool = True
    use_mixed_precision: bool = True
    
    def __post_init__(self):
        if self.device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"

class EMAManager:
    """Internal EMA manager for Trainer."""
    def __init__(self, model: nn.Module, decay: float = 0.999):
        self.decay = decay
        self.shadow = {}
        self.backup = {}
        for name, param in model.named_parameters():
            if param.requires_grad:
                self.shadow[name] = param.data.clone()

    def update(self, model: nn.Module):
        with torch.no_grad():
            for name, param in model.named_parameters():
                if name in self.shadow:
                    self.shadow[name].copy_(
                        self.decay * self.shadow[name] + (1.0 - self.decay) * param.data
                    )

    def apply_to_model(self, model: nn.Module):
        for name, param in model.named_parameters():
            if name in self.shadow:
                self.backup[name] = param.data.clone()
                param.data.copy_(self.shadow[name])

    def restore_from_backup(self, model: nn.Module):
        for name, param in model.named_parameters():
            if name in self.backup:
                param.data.copy_(self.backup[name])
        self.backup = {}

class Trainer:
    """Unified Trainer implementation."""
    def __init__(self, model: nn.Module, config: TrainingConfig):
        self.model = model
        self.config = config
        self.device = torch.device(config.device)
        self.model.to(self.device)
        
        self.scaler = GradScaler() if config.use_mixed_precision else None
        self.ema = EMAManager(model, config.ema_decay) if config.use_ema else None
        
        self.current_epoch = 0
        self.global_step = 0
        self.best_metric = float('inf') if config.mode == "min" else float('-inf')
        self.patience_counter = 0
        
        # Ensure checkpoint dir exists
        os.makedirs(config.checkpoint_dir, exist_ok=True)
        
        if config.use_wandb and wandb:
            self._init_wandb()

    def _init_wandb(self):
        wandb.init(project=self.config.wandb_project, name=self.config.experiment_name, config=self.config.__dict__)

    def train_step(self, batch, optimizer, scheduler) -> float:
        self.model.train()
        batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
        
        with autocast(enabled=self.config.use_mixed_precision):
            outputs = self.model(**batch)
            loss = (outputs.loss if hasattr(outputs, 'loss') else outputs['loss']) / self.config.gradient_accumulation_steps
            
        if self.scaler:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()
            
        if (self.global_step + 1) % self.config.gradient_accumulation_steps == 0:
            if self.scaler:
                self.scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.max_grad_norm)
                self.scaler.step(optimizer)
                self.scaler.update()
            else:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.max_grad_norm)
                optimizer.step()
            
            if self.ema:
                self.ema.update(self.model)
                
            optimizer.zero_grad()
            if scheduler: scheduler.step()
            
        return loss.item() * self.config.gradient_accumulation_steps

    def train(self, train_loader: DataLoader, val_loader: DataLoader, optimizer, scheduler=None):
        history = {'train_loss': [], 'val_loss': []}
        
        for epoch in range(self.config.num_epochs):
            self.current_epoch = epoch
            epoch_loss = 0
            progress_bar = tqdm(train_loader, desc=f"Epoch {epoch}")
            
            for batch in progress_bar:
                loss = self.train_step(batch, optimizer, scheduler)
                epoch_loss += loss
                self.global_step += 1
                progress_bar.set_postfix({'loss': f"{loss:.4f}"})
                
            val_metrics = self.validate(val_loader)
            avg_train_loss = epoch_loss / len(train_loader)
            
            history['train_loss'].append(avg_train_loss)
            history['val_loss'].append(val_metrics['loss'])
            
            logger.info(f"Epoch {epoch} summary: Train Loss {avg_train_loss:.4f}, Val Loss {val_metrics['loss']:.4f}")
            
            if self.config.use_wandb and wandb:
                wandb.log({"train_loss": avg_train_loss, "val_loss": val_metrics['loss'], "epoch": epoch})
            
            if self._is_better(val_metrics['loss']):
                self.best_metric = val_metrics['loss']
                self.patience_counter = 0
                self.save_checkpoint("best.pt")
            else:
                self.patience_counter += 1
                
            if self.patience_counter >= self.config.early_stopping_patience:
                logger.info("Early stopping triggered")
                break
        return history

    def validate(self, val_loader: DataLoader) -> Dict[str, float]:
        self.model.eval()
        if self.ema: self.ema.apply_to_model(self.model)
        
        total_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
                with autocast(enabled=self.config.use_mixed_precision):
                    outputs = self.model(**batch)
                    loss = outputs.loss if hasattr(outputs, 'loss') else outputs['loss']
                    total_loss += loss.item()
        
        if self.ema: self.ema.restore_from_backup(self.model)
        return {'loss': total_loss / max(1, len(val_loader))}

    def _is_better(self, metric: float) -> bool:
        if self.config.mode == "min":
            return metric < self.best_metric - self.config.min_delta
        return metric > self.best_metric + self.config.min_delta

    def save_checkpoint(self, filename: str):
        path = Path(self.config.checkpoint_dir) / filename
        state = {
            'epoch': self.current_epoch,
            'model_state': self.model.state_dict(),
            'best_metric': self.best_metric,
            'config': self.config.__dict__
        }
        if self.ema:
            state['ema_state'] = self.ema.shadow
        torch.save(state, path)
        logger.info(f"Saved checkpoint to {path}")
