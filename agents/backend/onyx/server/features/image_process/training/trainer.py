"""
🏋️ Advanced Trainer Implementation
=================================

Comprehensive trainer with mixed precision training, optimization strategies,
and enterprise-grade features for the optimized image processing system.
"""

import time
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager

import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import GradScaler, autocast
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import numpy as np
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainerConfig:
    """Configuration for the trainer."""
    # Model and data
    model: nn.Module
    train_loader: DataLoader
    val_loader: Optional[DataLoader] = None
    test_loader: Optional[DataLoader] = None
    
    # Training parameters
    num_epochs: int = 100
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    gradient_clip_val: float = 1.0
    accumulation_steps: int = 1
    
    # Mixed precision
    use_mixed_precision: bool = True
    amp_dtype: torch.dtype = torch.float16
    
    # Optimization
    optimizer_name: str = "adamw"
    scheduler_name: str = "cosine"
    warmup_steps: int = 1000
    warmup_ratio: float = 0.1
    
    # Loss and metrics
    loss_function: Optional[Callable] = None
    metrics: List[str] = field(default_factory=lambda: ["accuracy", "loss"])
    
    # Checkpointing
    save_dir: str = "checkpoints"
    save_every: int = 10
    save_best: bool = True
    monitor_metric: str = "val_loss"
    monitor_mode: str = "min"  # "min" or "max"
    
    # Logging and monitoring
    log_every: int = 100
    log_dir: str = "logs"
    use_tensorboard: bool = True
    use_wandb: bool = False
    project_name: str = "image_processing_training"
    
    # Device and performance
    device: str = "auto"  # "auto", "cpu", "cuda", "mps"
    num_workers: int = 4
    pin_memory: bool = True
    
    # Early stopping
    early_stopping_patience: int = 10
    early_stopping_min_delta: float = 1e-4
    
    # Validation
    val_every: int = 1
    val_steps: Optional[int] = None
    
    # Debugging
    debug: bool = False
    deterministic: bool = False
    
    def __post_init__(self):
        """Post-initialization setup."""
        # Setup device
        if self.device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        
        # Create directories
        Path(self.save_dir).mkdir(parents=True, exist_ok=True)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        
        # Setup deterministic training if requested
        if self.deterministic:
            torch.manual_seed(42)
            torch.cuda.manual_seed_all(42)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

class Trainer:
    """
    Advanced trainer with mixed precision training and comprehensive features.
    
    Features:
    - Mixed precision training with torch.cuda.amp
    - Multiple optimizers and schedulers
    - Comprehensive logging and monitoring
    - Checkpoint management
    - Early stopping
    - Performance optimization
    - Enterprise-grade features
    """
    
    def __init__(self, config: TrainerConfig):
        """
        Initialize the trainer.
        
        Args:
            config: Trainer configuration
        """
        self.config = config
        self.device = torch.device(config.device)
        
        # Setup model
        self.model = config.model.to(self.device)
        
        # Setup mixed precision
        self.scaler = GradScaler() if config.use_mixed_precision else None
        
        # Setup optimizer and scheduler
        self.optimizer = self._setup_optimizer()
        self.scheduler = self._setup_scheduler()
        
        # Setup loss function
        self.criterion = config.loss_function or nn.CrossEntropyLoss()
        
        # Training state
        self.current_epoch = 0
        self.global_step = 0
        self.best_metric = float('inf') if config.monitor_mode == "min" else float('-inf')
        self.early_stopping_counter = 0
        
        # Metrics tracking
        self.train_metrics = {}
        self.val_metrics = {}
        self.test_metrics = {}
        
        # Setup logging
        self.writer = None
        if config.use_tensorboard:
            self.writer = SummaryWriter(config.log_dir)
        
        # Setup wandb if requested
        if config.use_wandb:
            self._setup_wandb()
        
        logger.info(f"Trainer initialized on device: {self.device}")
        logger.info(f"Mixed precision: {config.use_mixed_precision}")
        logger.info(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def _setup_optimizer(self) -> optim.Optimizer:
        """Setup the optimizer."""
        optimizer_map = {
            "adam": optim.Adam,
            "adamw": optim.AdamW,
            "sgd": optim.SGD,
            "rmsprop": optim.RMSprop,
            "adagrad": optim.Adagrad,
            "adamax": optim.Adamax
        }
        
        optimizer_class = optimizer_map.get(self.config.optimizer_name.lower(), optim.AdamW)
        
        if self.config.optimizer_name.lower() == "sgd":
            optimizer = optimizer_class(
                self.model.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay,
                momentum=0.9
            )
        else:
            optimizer = optimizer_class(
                self.model.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )
        
        logger.info(f"Using optimizer: {self.config.optimizer_name}")
        return optimizer
    
    def _setup_scheduler(self) -> Optional[optim.lr_scheduler._LRScheduler]:
        """Setup the learning rate scheduler."""
        if self.config.scheduler_name.lower() == "none":
            return None
        
        # Calculate total steps
        total_steps = len(self.config.train_loader) * self.config.num_epochs
        
        scheduler_map = {
            "cosine": optim.lr_scheduler.CosineAnnealingLR,
            "cosine_warmup": optim.lr_scheduler.CosineAnnealingWarmRestarts,
            "step": optim.lr_scheduler.StepLR,
            "exponential": optim.lr_scheduler.ExponentialLR,
            "plateau": optim.lr_scheduler.ReduceLROnPlateau,
            "linear": optim.lr_scheduler.LinearLR,
            "polynomial": optim.lr_scheduler.PolynomialLR
        }
        
        scheduler_class = scheduler_map.get(self.config.scheduler_name.lower())
        
        if scheduler_class is None:
            logger.warning(f"Unknown scheduler: {self.config.scheduler_name}")
            return None
        
        if self.config.scheduler_name.lower() == "cosine":
            scheduler = scheduler_class(
                self.optimizer,
                T_max=total_steps,
                eta_min=1e-6
            )
        elif self.config.scheduler_name.lower() == "cosine_warmup":
            scheduler = scheduler_class(
                self.optimizer,
                T_0=self.config.warmup_steps,
                T_mult=2
            )
        elif self.config.scheduler_name.lower() == "step":
            scheduler = scheduler_class(
                self.optimizer,
                step_size=total_steps // 10,
                gamma=0.1
            )
        elif self.config.scheduler_name.lower() == "exponential":
            scheduler = scheduler_class(
                self.optimizer,
                gamma=0.95
            )
        elif self.config.scheduler_name.lower() == "plateau":
            scheduler = scheduler_class(
                self.optimizer,
                mode=self.config.monitor_mode,
                patience=5,
                factor=0.5,
                min_lr=1e-6
            )
        elif self.config.scheduler_name.lower() == "linear":
            scheduler = scheduler_class(
                self.optimizer,
                start_factor=1.0,
                end_factor=0.1,
                total_iters=total_steps
            )
        elif self.config.scheduler_name.lower() == "polynomial":
            scheduler = scheduler_class(
                self.optimizer,
                total_iters=total_steps,
                power=2.0
            )
        
        logger.info(f"Using scheduler: {self.config.scheduler_name}")
        return scheduler
    
    def _setup_wandb(self):
        """Setup Weights & Biases logging."""
        try:
            import wandb
            wandb.init(
                project=self.config.project_name,
                config=vars(self.config),
                name=f"training_{int(time.time())}"
            )
            logger.info("Weights & Biases logging enabled")
        except ImportError:
            logger.warning("Weights & Biases not installed. Skipping wandb logging.")
    
    @contextmanager
    def _mixed_precision_context(self):
        """Context manager for mixed precision training."""
        if self.config.use_mixed_precision and self.device.type == "cuda":
            with autocast(dtype=self.config.amp_dtype):
                yield
        else:
            yield
    
    def _train_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Perform a single training step."""
        # Move batch to device
        batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                for k, v in batch.items()}
        
        # Forward pass with mixed precision
        with self._mixed_precision_context():
            outputs = self.model(batch)
            loss = self.criterion(outputs, batch['labels'])
        
        # Backward pass with gradient scaling
        if self.config.use_mixed_precision and self.device.type == "cuda":
            self.scaler.scale(loss).backward()
        else:
            loss.backward()
        
        # Gradient accumulation
        if (self.global_step + 1) % self.config.accumulation_steps == 0:
            # Gradient clipping
            if self.config.gradient_clip_val > 0:
                if self.config.use_mixed_precision and self.device.type == "cuda":
                    self.scaler.unscale_(self.optimizer)
                
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.gradient_clip_val
                )
            
            # Optimizer step
            if self.config.use_mixed_precision and self.device.type == "cuda":
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                self.optimizer.step()
            
            # Scheduler step
            if self.scheduler is not None:
                if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                    # Plateau scheduler needs validation loss
                    pass
                else:
                    self.scheduler.step()
            
            self.optimizer.zero_grad()
        
        return {
            'loss': loss.item(),
            'learning_rate': self.optimizer.param_groups[0]['lr']
        }
    
    def _validation_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Perform a single validation step."""
        # Move batch to device
        batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                for k, v in batch.items()}
        
        with torch.no_grad():
            with self._mixed_precision_context():
                outputs = self.model(batch)
                loss = self.criterion(outputs, batch['labels'])
        
        # Calculate additional metrics
        metrics = {
            'val_loss': loss.item(),
            'val_accuracy': self._calculate_accuracy(outputs, batch['labels'])
        }
        
        return metrics
    
    def _calculate_accuracy(self, outputs: torch.Tensor, targets: torch.Tensor) -> float:
        """Calculate accuracy metric."""
        if outputs.dim() > 1:
            predictions = torch.argmax(outputs, dim=1)
        else:
            predictions = (outputs > 0.5).float()
        
        correct = (predictions == targets).float().sum()
        accuracy = correct / targets.size(0)
        return accuracy.item()
    
    def _log_metrics(self, metrics: Dict[str, float], step: int, prefix: str = ""):
        """Log metrics to various backends."""
        # Console logging
        if step % self.config.log_every == 0:
            metric_str = ", ".join([f"{k}: {v:.4f}" for k, v in metrics.items()])
            logger.info(f"{prefix} Step {step}: {metric_str}")
        
        # TensorBoard logging
        if self.writer is not None:
            for key, value in metrics.items():
                self.writer.add_scalar(f"{prefix}/{key}", value, step)
        
        # Weights & Biases logging
        if self.config.use_wandb:
            try:
                import wandb
                wandb.log({f"{prefix}_{k}": v for k, v in metrics.items()}, step=step)
            except ImportError:
                pass
    
    def _save_checkpoint(self, epoch: int, metrics: Dict[str, float], is_best: bool = False):
        """Save model checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'global_step': self.global_step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'scaler_state_dict': self.scaler.state_dict() if self.scaler else None,
            'metrics': metrics,
            'config': vars(self.config)
        }
        
        # Save regular checkpoint
        if epoch % self.config.save_every == 0:
            checkpoint_path = Path(self.config.save_dir) / f"checkpoint_epoch_{epoch}.pt"
            torch.save(checkpoint, checkpoint_path)
            logger.info(f"Saved checkpoint: {checkpoint_path}")
        
        # Save best checkpoint
        if is_best and self.config.save_best:
            best_path = Path(self.config.save_dir) / "best_model.pt"
            torch.save(checkpoint, best_path)
            logger.info(f"Saved best model: {best_path}")
    
    def _should_stop_early(self, current_metric: float) -> bool:
        """Check if training should stop early."""
        if self.config.early_stopping_patience <= 0:
            return False
        
        if self.config.monitor_mode == "min":
            improved = current_metric < self.best_metric - self.config.early_stopping_min_delta
        else:
            improved = current_metric > self.best_metric + self.config.early_stopping_min_delta
        
        if improved:
            self.best_metric = current_metric
            self.early_stopping_counter = 0
            return False
        else:
            self.early_stopping_counter += 1
            return self.early_stopping_counter >= self.config.early_stopping_patience
    
    def train(self) -> Dict[str, Any]:
        """
        Train the model.
        
        Returns:
            Dictionary containing training results and metrics
        """
        logger.info("Starting training...")
        start_time = time.time()
        
        for epoch in range(self.current_epoch, self.config.num_epochs):
            self.current_epoch = epoch
            
            # Training phase
            train_metrics = self._train_epoch()
            
            # Validation phase
            val_metrics = {}
            if self.config.val_loader is not None and epoch % self.config.val_every == 0:
                val_metrics = self._validate_epoch()
            
            # Logging
            self._log_metrics(train_metrics, self.global_step, "train")
            if val_metrics:
                self._log_metrics(val_metrics, self.global_step, "val")
            
            # Checkpointing
            current_metric = val_metrics.get(self.config.monitor_metric, float('inf'))
            is_best = (
                (self.config.monitor_mode == "min" and current_metric < self.best_metric) or
                (self.config.monitor_mode == "max" and current_metric > self.best_metric)
            )
            
            self._save_checkpoint(epoch, {**train_metrics, **val_metrics}, is_best)
            
            # Early stopping
            if self._should_stop_early(current_metric):
                logger.info(f"Early stopping triggered after {epoch + 1} epochs")
                break
        
        # Final evaluation
        test_metrics = {}
        if self.config.test_loader is not None:
            test_metrics = self._test_epoch()
        
        training_time = time.time() - start_time
        
        # Final results
        results = {
            'final_epoch': self.current_epoch,
            'total_steps': self.global_step,
            'training_time': training_time,
            'best_metric': self.best_metric,
            'final_train_metrics': train_metrics,
            'final_val_metrics': val_metrics,
            'final_test_metrics': test_metrics
        }
        
        logger.info(f"Training completed in {training_time:.2f}s")
        logger.info(f"Best {self.config.monitor_metric}: {self.best_metric:.4f}")
        
        return results
    
    def _train_epoch(self) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        epoch_metrics = []
        
        progress_bar = tqdm(
            self.config.train_loader,
            desc=f"Epoch {self.current_epoch + 1}/{self.config.num_epochs}",
            leave=False
        )
        
        for batch_idx, batch in enumerate(progress_bar):
            step_metrics = self._train_step(batch)
            epoch_metrics.append(step_metrics)
            
            # Update progress bar
            progress_bar.set_postfix({
                'loss': f"{step_metrics['loss']:.4f}",
                'lr': f"{step_metrics['learning_rate']:.2e}"
            })
            
            self.global_step += 1
        
        # Calculate epoch averages
        avg_metrics = {}
        for key in epoch_metrics[0].keys():
            avg_metrics[key] = np.mean([m[key] for m in epoch_metrics])
        
        return avg_metrics
    
    def _validate_epoch(self) -> Dict[str, float]:
        """Validate for one epoch."""
        self.model.eval()
        epoch_metrics = []
        
        val_loader = self.config.val_loader
        if self.config.val_steps is not None:
            val_loader = list(val_loader)[:self.config.val_steps]
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validation", leave=False):
                step_metrics = self._validation_step(batch)
                epoch_metrics.append(step_metrics)
        
        # Calculate epoch averages
        avg_metrics = {}
        for key in epoch_metrics[0].keys():
            avg_metrics[key] = np.mean([m[key] for m in epoch_metrics])
        
        return avg_metrics
    
    def _test_epoch(self) -> Dict[str, float]:
        """Test for one epoch."""
        self.model.eval()
        epoch_metrics = []
        
        with torch.no_grad():
            for batch in tqdm(self.config.test_loader, desc="Testing", leave=False):
                step_metrics = self._validation_step(batch)
                epoch_metrics.append(step_metrics)
        
        # Calculate epoch averages
        avg_metrics = {}
        for key in epoch_metrics[0].keys():
            avg_metrics[key] = np.mean([m[key] for m in epoch_metrics])
        
        return avg_metrics
    
    def load_checkpoint(self, checkpoint_path: str):
        """Load a checkpoint."""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        if checkpoint['scheduler_state_dict'] and self.scheduler:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        if checkpoint['scaler_state_dict'] and self.scaler:
            self.scaler.load_state_dict(checkpoint['scaler_state_dict'])
        
        self.current_epoch = checkpoint['epoch']
        self.global_step = checkpoint['global_step']
        
        logger.info(f"Loaded checkpoint from epoch {self.current_epoch}")
    
    def __del__(self):
        """Cleanup when trainer is destroyed."""
        if self.writer is not None:
            self.writer.close()





