#!/usr/bin/env python3
"""
Early Stopping and Learning Rate Scheduling System for Diffusion Models.

This module provides comprehensive early stopping and learning rate scheduling
capabilities specifically designed for diffusion model training.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from pathlib import Path
import json
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LRSchedulerType(Enum):
    """Types of learning rate schedulers."""
    STEP = "step"
    MULTI_STEP = "multi_step"
    EXPONENTIAL = "exponential"
    COSINE = "cosine"
    COSINE_WARM_RESTART = "cosine_warm_restart"
    COSINE_ANNEALING = "cosine_annealing"
    ONE_CYCLE = "one_cycle"
    PLATEAU = "plateau"
    LINEAR = "linear"
    POLYNOMIAL = "polynomial"
    CUSTOM = "custom"

class EarlyStoppingMode(Enum):
    """Early stopping modes."""
    MIN = "min"  # Stop when metric stops decreasing
    MAX = "max"  # Stop when metric stops increasing

class MetricType(Enum):
    """Types of metrics for early stopping."""
    LOSS = "loss"
    VALIDATION_LOSS = "validation_loss"
    PSNR = "psnr"
    SSIM = "ssim"
    FID = "fid"
    LPIPS = "lpips"
    CUSTOM = "custom"

@dataclass
class LRSchedulerConfig:
    """Configuration for learning rate schedulers."""
    scheduler_type: LRSchedulerType = LRSchedulerType.COSINE
    initial_lr: float = 1e-4
    min_lr: float = 1e-7
    max_lr: float = 1e-3
    
    # Step scheduler parameters
    step_size: int = 30
    gamma: float = 0.1
    
    # Multi-step scheduler parameters
    milestones: List[int] = field(default_factory=lambda: [30, 60, 90])
    
    # Exponential scheduler parameters
    decay_rate: float = 0.95
    
    # Cosine scheduler parameters
    T_max: int = 100
    eta_min: float = 1e-7
    
    # Cosine warm restart parameters
    T_0: int = 10
    T_mult: int = 2
    
    # One cycle scheduler parameters
    epochs: int = 100
    steps_per_epoch: int = 100
    pct_start: float = 0.3
    anneal_strategy: str = "cos"
    
    # Plateau scheduler parameters
    mode: str = "min"
    factor: float = 0.1
    patience: int = 10
    threshold: float = 1e-4
    threshold_mode: str = "rel"
    
    # Polynomial scheduler parameters
    power: float = 1.0
    
    # Custom scheduler parameters
    custom_schedule: Optional[Callable] = None

@dataclass
class EarlyStoppingConfig:
    """Configuration for early stopping."""
    mode: EarlyStoppingMode = EarlyStoppingMode.MIN
    patience: int = 20
    min_delta: float = 0.0
    restore_best_weights: bool = True
    verbose: bool = True
    
    # Metric configuration
    metric_type: MetricType = MetricType.VALIDATION_LOSS
    custom_metric: Optional[Callable] = None
    
    # Advanced parameters
    min_epochs: int = 10  # Minimum epochs before early stopping
    max_epochs: int = 1000  # Maximum epochs
    cooldown: int = 0  # Cooldown period after early stopping
    min_improvement: float = 0.0  # Minimum improvement required

@dataclass
class TrainingConfig:
    """Configuration for training with early stopping and LR scheduling."""
    # Training parameters
    epochs: int = 100
    batch_size: int = 32
    gradient_accumulation_steps: int = 1
    
    # Learning rate parameters
    initial_lr: float = 1e-4
    weight_decay: float = 1e-4
    
    # Early stopping parameters
    early_stopping: bool = True
    early_stopping_config: EarlyStoppingConfig = field(default_factory=EarlyStoppingConfig)
    
    # LR scheduling parameters
    lr_scheduling: bool = True
    lr_scheduler_config: LRSchedulerConfig = field(default_factory=LRSchedulerConfig)
    
    # Monitoring parameters
    save_checkpoints: bool = True
    checkpoint_dir: str = "checkpoints"
    log_interval: int = 10
    eval_interval: int = 5

class LRScheduler:
    """Learning rate scheduler with multiple strategies."""
    
    def __init__(self, optimizer: optim.Optimizer, config: LRSchedulerConfig):
        self.optimizer = optimizer
        self.config = config
        self.scheduler = None
        self.current_lr = config.initial_lr
        self.lr_history = []
        
        self._create_scheduler()
    
    def _create_scheduler(self):
        """Create the appropriate learning rate scheduler."""
        if self.config.scheduler_type == LRSchedulerType.STEP:
            self.scheduler = optim.lr_scheduler.StepLR(
                self.optimizer, 
                step_size=self.config.step_size, 
                gamma=self.config.gamma
            )
        
        elif self.config.scheduler_type == LRSchedulerType.MULTI_STEP:
            self.scheduler = optim.lr_scheduler.MultiStepLR(
                self.optimizer, 
                milestones=self.config.milestones, 
                gamma=self.config.gamma
            )
        
        elif self.config.scheduler_type == LRSchedulerType.EXPONENTIAL:
            self.scheduler = optim.lr_scheduler.ExponentialLR(
                self.optimizer, 
                gamma=self.config.decay_rate
            )
        
        elif self.config.scheduler_type == LRSchedulerType.COSINE:
            self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer, 
                T_max=self.config.T_max, 
                eta_min=self.config.eta_min
            )
        
        elif self.config.scheduler_type == LRSchedulerType.COSINE_WARM_RESTART:
            self.scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
                self.optimizer, 
                T_0=self.config.T_0, 
                T_mult=self.config.T_mult, 
                eta_min=self.config.eta_min
            )
        
        elif self.config.scheduler_type == LRSchedulerType.COSINE_ANNEALING:
            self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer, 
                T_max=self.config.T_max, 
                eta_min=self.config.eta_min
            )
        
        elif self.config.scheduler_type == LRSchedulerType.ONE_CYCLE:
            self.scheduler = optim.lr_scheduler.OneCycleLR(
                self.optimizer,
                max_lr=self.config.max_lr,
                epochs=self.config.epochs,
                steps_per_epoch=self.config.steps_per_epoch,
                pct_start=self.config.pct_start,
                anneal_strategy=self.config.anneal_strategy
            )
        
        elif self.config.scheduler_type == LRSchedulerType.PLATEAU:
            self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode=self.config.mode,
                factor=self.config.factor,
                patience=self.config.config.patience,
                threshold=self.config.threshold,
                threshold_mode=self.config.threshold_mode,
                min_lr=self.config.min_lr
            )
        
        elif self.config.scheduler_type == LRSchedulerType.LINEAR:
            self.scheduler = self._create_linear_scheduler()
        
        elif self.config.scheduler_type == LRSchedulerType.POLYNOMIAL:
            self.scheduler = self._create_polynomial_scheduler()
        
        elif self.config.scheduler_type == LRSchedulerType.CUSTOM:
            if self.config.custom_schedule is None:
                raise ValueError("Custom schedule function must be provided for custom scheduler type")
            self.scheduler = self._create_custom_scheduler()
        
        else:
            raise ValueError(f"Unknown scheduler type: {self.config.scheduler_type}")
    
    def _create_linear_scheduler(self):
        """Create a custom linear learning rate scheduler."""
        def linear_lr_lambda(epoch):
            if epoch >= self.config.T_max:
                return self.config.min_lr / self.config.initial_lr
            return 1.0 - (1.0 - self.config.min_lr / self.config.initial_lr) * epoch / self.config.T_max
        
        return optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda=linear_lr_lambda)
    
    def _create_polynomial_scheduler(self):
        """Create a custom polynomial learning rate scheduler."""
        def polynomial_lr_lambda(epoch):
            if epoch >= self.config.T_max:
                return self.config.min_lr / self.config.initial_lr
            return (1.0 - epoch / self.config.T_max) ** self.config.power
        
        return optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda=polynomial_lr_lambda)
    
    def _create_custom_scheduler(self):
        """Create a custom learning rate scheduler."""
        return optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda=self.config.custom_schedule)
    
    def step(self, metric: Optional[float] = None):
        """Step the learning rate scheduler."""
        if self.scheduler is None:
            return
        
        # Handle different scheduler types
        if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
            if metric is not None:
                self.scheduler.step(metric)
        else:
            self.scheduler.step()
        
        # Update current learning rate and history
        self.current_lr = self.optimizer.param_groups[0]['lr']
        self.lr_history.append(self.current_lr)
    
    def get_lr(self) -> float:
        """Get current learning rate."""
        return self.current_lr
    
    def get_lr_history(self) -> List[float]:
        """Get learning rate history."""
        return self.lr_history.copy()
    
    def plot_lr_schedule(self, save_path: Optional[str] = None):
        """Plot the learning rate schedule."""
        plt.figure(figsize=(10, 6))
        plt.plot(self.lr_history)
        plt.title(f'Learning Rate Schedule: {self.config.scheduler_type.value}')
        plt.xlabel('Step')
        plt.ylabel('Learning Rate')
        plt.yscale('log')
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        plt.close()

class EarlyStopping:
    """Early stopping mechanism for training."""
    
    def __init__(self, config: EarlyStoppingConfig):
        self.config = config
        self.best_score = None
        self.best_epoch = None
        self.counter = 0
        self.best_weights = None
        self.should_stop = False
        self.metric_history = []
        
        # Initialize best score based on mode
        if self.config.mode == EarlyStoppingMode.MIN:
            self.best_score = float('inf')
        else:
            self.best_score = float('-inf')
    
    def __call__(self, metric: float, epoch: int, model: nn.Module) -> bool:
        """Check if training should stop early."""
        self.metric_history.append(metric)
        
        # Check if we have enough epochs
        if epoch < self.config.min_epochs:
            return False
        
        # Check if we've exceeded max epochs
        if epoch >= self.config.max_epochs:
            if self.config.verbose:
                logger.info(f"Stopping: reached maximum epochs ({self.config.max_epochs})")
            return True
        
        # Determine if metric improved
        if self.config.mode == EarlyStoppingMode.MIN:
            improved = metric < self.best_score - self.config.min_delta
        else:
            improved = metric > self.best_score + self.config.min_delta
        
        if improved:
            self.best_score = metric
            self.best_epoch = epoch
            self.counter = 0
            
            # Save best weights if requested
            if self.config.restore_best_weights:
                self.best_weights = {name: param.clone() for name, param in model.named_parameters()}
            
            if self.config.verbose:
                logger.info(f"Metric improved to {metric:.6f} at epoch {epoch}")
        else:
            self.counter += 1
            if self.config.verbose:
                logger.info(f"Metric did not improve for {self.counter} epochs")
        
        # Check if we should stop
        if self.counter >= self.config.patience:
            if self.config.verbose:
                logger.info(f"Early stopping triggered after {self.config.patience} epochs without improvement")
            self.should_stop = True
            return True
        
        return False
    
    def restore_best_weights(self, model: nn.Module):
        """Restore the best weights to the model."""
        if self.best_weights is not None:
            for name, param in model.named_parameters():
                if name in self.best_weights:
                    param.data = self.best_weights[name].data
            logger.info("Restored best weights from early stopping")
    
    def get_best_score(self) -> float:
        """Get the best score achieved."""
        return self.best_score
    
    def get_best_epoch(self) -> int:
        """Get the epoch with the best score."""
        return self.best_epoch
    
    def plot_metric_history(self, save_path: Optional[str] = None):
        """Plot the metric history."""
        plt.figure(figsize=(10, 6))
        plt.plot(self.metric_history)
        plt.axhline(y=self.best_score, color='r', linestyle='--', alpha=0.7, label=f'Best: {self.best_score:.6f}')
        if self.best_epoch is not None:
            plt.axvline(x=self.best_epoch, color='g', linestyle=':', alpha=0.7, label=f'Best Epoch: {self.best_epoch}')
        plt.title('Training Metric History')
        plt.xlabel('Epoch')
        plt.ylabel('Metric')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        plt.close()

class TrainingManager:
    """Manages training with early stopping and learning rate scheduling."""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.early_stopping = None
        self.lr_scheduler = None
        self.training_history = {
            'train_loss': [],
            'val_loss': [],
            'learning_rate': [],
            'epochs': []
        }
        
        if self.config.early_stopping:
            self.early_stopping = EarlyStopping(self.config.early_stopping_config)
    
    def setup_training(self, model: nn.Module, train_loader, val_loader=None):
        """Setup training components."""
        # Setup optimizer
        self.optimizer = optim.AdamW(
            model.parameters(),
            lr=self.config.initial_lr,
            weight_decay=self.config.weight_decay
        )
        
        # Setup learning rate scheduler
        if self.config.lr_scheduling:
            lr_config = self.config.lr_scheduler_config
            lr_config.initial_lr = self.config.initial_lr
            lr_config.epochs = self.config.epochs
            lr_config.steps_per_epoch = len(train_loader)
            
            self.lr_scheduler = LRScheduler(self.optimizer, lr_config)
        
        # Setup data loaders
        self.train_loader = train_loader
        self.val_loader = val_loader
        
        # Setup checkpoint directory
        if self.config.save_checkpoints:
            Path(self.config.checkpoint_dir).mkdir(exist_ok=True)
    
    def train_epoch(self, model: nn.Module, epoch: int) -> Dict[str, float]:
        """Train for one epoch."""
        model.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch_idx, (data, target) in enumerate(self.train_loader):
            # Forward pass
            self.optimizer.zero_grad()
            output = model(data)
            loss = F.mse_loss(output, target)  # Assuming MSE loss for diffusion
            
            # Backward pass
            loss.backward()
            
            # Gradient accumulation
            if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                self.optimizer.step()
                
                # Step LR scheduler if using OneCycle
                if (self.config.lr_scheduling and 
                    self.config.lr_scheduler_config.scheduler_type == LRSchedulerType.ONE_CYCLE):
                    self.lr_scheduler.step()
            
            total_loss += loss.item()
            num_batches += 1
            
            # Log progress
            if batch_idx % self.config.log_interval == 0:
                logger.info(f'Epoch {epoch}, Batch {batch_idx}/{len(self.train_loader)}, Loss: {loss.item():.6f}')
        
        avg_loss = total_loss / num_batches
        return {'train_loss': avg_loss}
    
    def validate_epoch(self, model: nn.Module, epoch: int) -> Dict[str, float]:
        """Validate for one epoch."""
        if self.val_loader is None:
            return {}
        
        model.eval()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for data, target in self.val_loader:
                output = model(data)
                loss = F.mse_loss(output, target)
                total_loss += loss.item()
                num_batches += 1
        
        avg_loss = total_loss / num_batches
        return {'val_loss': avg_loss}
    
    def train(self, model: nn.Module) -> Dict[str, Any]:
        """Main training loop with early stopping and LR scheduling."""
        logger.info("Starting training...")
        start_time = time.time()
        
        for epoch in range(self.config.epochs):
            epoch_start_time = time.time()
            
            # Training phase
            train_metrics = self.train_epoch(model, epoch)
            
            # Validation phase
            val_metrics = self.validate_epoch(model, epoch)
            
            # Combine metrics
            metrics = {**train_metrics, **val_metrics}
            
            # Step learning rate scheduler
            if self.config.lr_scheduling and self.lr_scheduler:
                if self.config.lr_scheduler_config.scheduler_type == LRSchedulerType.PLATEAU:
                    val_loss = val_metrics.get('val_loss', float('inf'))
                    self.lr_scheduler.step(val_loss)
                elif self.config.lr_scheduler_config.scheduler_type != LRSchedulerType.ONE_CYCLE:
                    self.lr_scheduler.step()
            
            # Update training history
            self.training_history['train_loss'].append(metrics.get('train_loss', 0.0))
            self.training_history['val_loss'].append(metrics.get('val_loss', 0.0))
            self.training_history['learning_rate'].append(self.optimizer.param_groups[0]['lr'])
            self.training_history['epochs'].append(epoch)
            
            # Log epoch results
            epoch_time = time.time() - epoch_start_time
            logger.info(f'Epoch {epoch}: Train Loss: {metrics.get("train_loss", 0.0):.6f}, '
                       f'Val Loss: {metrics.get("val_loss", 0.0):.6f}, '
                       f'LR: {self.optimizer.param_groups[0]["lr"]:.2e}, '
                       f'Time: {epoch_time:.2f}s')
            
            # Check early stopping
            if self.config.early_stopping and self.early_stopping:
                stop_metric = metrics.get('val_loss', metrics.get('train_loss', 0.0))
                if self.early_stopping(stop_metric, epoch, model):
                    logger.info("Early stopping triggered")
                    break
            
            # Save checkpoint
            if self.config.save_checkpoints and epoch % 10 == 0:
                self.save_checkpoint(model, epoch, metrics)
        
        # Restore best weights if early stopping was used
        if self.config.early_stopping and self.early_stopping:
            self.early_stopping.restore_best_weights(model)
        
        # Training completed
        total_time = time.time() - start_time
        logger.info(f"Training completed in {total_time:.2f}s")
        
        return {
            'training_history': self.training_history,
            'best_epoch': self.early_stopping.get_best_epoch() if self.early_stopping else None,
            'best_score': self.early_stopping.get_best_score() if self.early_stopping else None,
            'total_time': total_time
        }
    
    def save_checkpoint(self, model: nn.Module, epoch: int, metrics: Dict[str, float]):
        """Save a training checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'metrics': metrics,
            'training_history': self.training_history,
            'config': self.config
        }
        
        if self.lr_scheduler:
            checkpoint['lr_scheduler_state_dict'] = self.lr_scheduler.scheduler.state_dict()
        
        checkpoint_path = Path(self.config.checkpoint_dir) / f"checkpoint_epoch_{epoch}.pt"
        torch.save(checkpoint, checkpoint_path)
        logger.info(f"Checkpoint saved: {checkpoint_path}")
    
    def load_checkpoint(self, model: nn.Module, checkpoint_path: str):
        """Load a training checkpoint."""
        checkpoint = torch.load(checkpoint_path)
        model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        if 'lr_scheduler_state_dict' in checkpoint and self.lr_scheduler:
            self.lr_scheduler.scheduler.load_state_dict(checkpoint['lr_scheduler_state_dict'])
        
        self.training_history = checkpoint['training_history']
        logger.info(f"Checkpoint loaded: {checkpoint_path}")
        
        return checkpoint['epoch'], checkpoint['metrics']
    
    def plot_training_history(self, save_dir: Optional[str] = None):
        """Plot training history."""
        if save_dir:
            Path(save_dir).mkdir(exist_ok=True)
        
        # Plot losses
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        plt.plot(self.training_history['epochs'], self.training_history['train_loss'], label='Train Loss')
        if self.training_history['val_loss']:
            plt.plot(self.training_history['epochs'], self.training_history['val_loss'], label='Val Loss')
        plt.title('Training and Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 3, 2)
        plt.plot(self.training_history['epochs'], self.training_history['learning_rate'])
        plt.title('Learning Rate Schedule')
        plt.xlabel('Epoch')
        plt.ylabel('Learning Rate')
        plt.yscale('log')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 3, 3)
        if self.early_stopping:
            self.early_stopping.plot_metric_history()
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(Path(save_dir) / 'training_history.png', dpi=300, bbox_inches='tight')
        else:
            plt.show()
        plt.close()

# ============================================================================
# Utility Functions
# ============================================================================

def create_lr_scheduler_config(
    scheduler_type: LRSchedulerType,
    initial_lr: float = 1e-4,
    **kwargs
) -> LRSchedulerConfig:
    """Create a learning rate scheduler configuration."""
    config = LRSchedulerConfig(
        scheduler_type=scheduler_type,
        initial_lr=initial_lr,
        **kwargs
    )
    return config

def create_early_stopping_config(
    mode: EarlyStoppingMode = EarlyStoppingMode.MIN,
    patience: int = 20,
    **kwargs
) -> EarlyStoppingConfig:
    """Create an early stopping configuration."""
    config = EarlyStoppingConfig(
        mode=mode,
        patience=patience,
        **kwargs
    )
    return config

def create_training_config(
    epochs: int = 100,
    early_stopping: bool = True,
    lr_scheduling: bool = True,
    **kwargs
) -> TrainingConfig:
    """Create a training configuration."""
    config = TrainingConfig(
        epochs=epochs,
        early_stopping=early_stopping,
        lr_scheduling=lr_scheduling,
        **kwargs
    )
    return config 