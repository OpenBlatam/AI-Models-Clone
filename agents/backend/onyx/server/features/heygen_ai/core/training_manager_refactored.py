"""
Refactored Training Manager for HeyGen AI

This module provides clean, efficient training following deep learning best practices
with proper error handling, mixed precision, gradient accumulation, and experiment tracking.
Now enhanced with UltraPerformanceOptimizer for maximum speed improvements.
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
import warnings

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torch.optim import Optimizer, AdamW
from torch.optim.lr_scheduler import LambdaLR, CosineAnnealingLR, LinearLR
from torch.cuda.amp import autocast, GradScaler
from torch.nn.utils import clip_grad_norm_
import numpy as np
from tqdm import tqdm

from transformers import (
    get_linear_schedule_with_warmup,
    get_cosine_schedule_with_warmup,
    get_polynomial_decay_schedule_with_warmup
)

# Import the ultra performance optimizer
from .ultra_performance_optimizer import (
    UltraPerformanceOptimizer, 
    UltraPerformanceConfig,
    PerformanceProfiler
)

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """Configuration for training."""
    
    # General Settings
    seed: int = 42
    num_epochs: int = 10
    batch_size: int = 8
    gradient_accumulation_steps: int = 4
    max_grad_norm: float = 1.0
    warmup_steps: int = 100
    save_steps: int = 500
    eval_steps: int = 500
    logging_steps: int = 100
    
    # Learning Rate
    initial_lr: float = 5e-5
    min_lr: float = 1e-6
    scheduler_type: str = "cosine"  # cosine, linear, constant, polynomial
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    
    # Mixed Precision
    mixed_precision_enabled: bool = True
    dtype: str = "fp16"  # fp16, bf16, fp32
    autocast: bool = True
    scaler: bool = True
    
    # Early Stopping
    early_stopping_enabled: bool = True
    patience: int = 3
    min_delta: float = 0.001
    monitor: str = "val_loss"
    mode: str = "min"  # min or max
    
    # Checkpointing
    save_best_only: bool = True
    save_last_checkpoint: bool = True
    checkpoint_dir: str = "checkpoints"
    
    # Validation
    validation_interval: int = 1
    eval_accumulation_steps: int = 1
    
    # Logging
    log_interval: int = 100
    tensorboard_logging: bool = True
    wandb_logging: bool = False
    project_name: str = "heygen-ai"
    run_name: str = "training-run"
    
    # Ultra Performance Settings
    enable_ultra_performance: bool = True
    performance_mode: str = "balanced"  # maximum, balanced, memory-efficient
    enable_torch_compile: bool = True
    enable_flash_attention: bool = True
    enable_memory_optimization: bool = True
    enable_dynamic_batching: bool = True
    enable_performance_profiling: bool = True


class EarlyStopping:
    """Early stopping implementation with best practices."""
    
    def __init__(
        self,
        patience: int = 3,
        min_delta: float = 0.001,
        monitor: str = "val_loss",
        mode: str = "min"
    ):
        self.patience = patience
        self.min_delta = min_delta
        self.monitor = monitor
        self.mode = mode
        self.best_score = None
        self.counter = 0
        self.best_epoch = 0
        
    def __call__(self, current_score: float, epoch: int) -> bool:
        """Check if training should stop early."""
        if self.best_score is None:
            self.best_score = current_score
            self.best_epoch = epoch
            return False
            
        if self.mode == "min":
            is_better = current_score < self.best_score - self.min_delta
        else:
            is_better = current_score > self.best_score + self.min_delta
            
        if is_better:
            self.best_score = current_score
            self.counter = 0
            self.best_epoch = epoch
        else:
            self.counter += 1
            
        return self.counter >= self.patience


class TrainingMetrics:
    """Training metrics tracking and visualization."""
    
    def __init__(self):
        self.train_losses = []
        self.val_losses = []
        self.learning_rates = []
        self.grad_norms = []
        self.training_times = []
        self.memory_usage = []
        
    def update(
        self,
        train_loss: float,
        val_loss: Optional[float] = None,
        lr: Optional[float] = None,
        grad_norm: Optional[float] = None,
        training_time: Optional[float] = None,
        memory: Optional[float] = None
    ):
        """Update metrics."""
        self.train_losses.append(train_loss)
        if val_loss is not None:
            self.val_losses.append(val_loss)
        if lr is not None:
            self.learning_rates.append(lr)
        if grad_norm is not None:
            self.grad_norms.append(grad_norm)
        if training_time is not None:
            self.training_times.append(training_time)
        if memory is not None:
            self.memory_usage.append(memory)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get training summary."""
        return {
            "total_epochs": len(self.train_losses),
            "final_train_loss": self.train_losses[-1] if self.train_losses else None,
            "final_val_loss": self.val_losses[-1] if self.val_losses else None,
            "best_val_loss": min(self.val_losses) if self.val_losses else None,
            "total_training_time": sum(self.training_times) if self.training_times else 0,
            "avg_memory_usage": np.mean(self.memory_usage) if self.memory_usage else 0
        }


class TrainingManager:
    """Enhanced training manager with ultra performance optimizations."""
    
    def __init__(
        self,
        config: TrainingConfig,
        model: nn.Module,
        train_dataloader: DataLoader,
        val_dataloader: Optional[DataLoader] = None,
        device: Optional[torch.device] = None
    ):
        self.config = config
        self.model = model
        self.train_dataloader = train_dataloader
        self.val_dataloader = val_dataloader
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize ultra performance optimizer
        self.ultra_performance_optimizer = None
        if self.config.enable_ultra_performance:
            self._setup_ultra_performance()
        
        # Initialize components
        self.early_stopping = EarlyStopping(
            patience=self.config.patience,
            min_delta=self.config.min_delta,
            monitor=self.config.monitor,
            mode=self.config.mode
        )
        self.metrics = TrainingMetrics()
        
        # Setup model, optimizer, and scheduler
        self._setup_training_components()
        
        # Performance profiling
        self.performance_profiler = None
        if self.config.enable_performance_profiling:
            self._setup_performance_profiling()
    
    def _setup_ultra_performance(self):
        """Setup ultra performance optimizations."""
        try:
            performance_config = UltraPerformanceConfig(
                enable_torch_compile=self.config.enable_torch_compile,
                enable_flash_attention=self.config.enable_flash_attention,
                enable_memory_efficient_forward=self.config.enable_memory_optimization,
                enable_dynamic_batch_size=self.config.enable_dynamic_batching,
                enable_performance_profiling=self.config.enable_performance_profiling
            )
            
            self.ultra_performance_optimizer = UltraPerformanceOptimizer(
                config=performance_config,
                device=self.device
            )
            
            logger.info("Ultra performance optimizations enabled successfully")
            
        except Exception as e:
            logger.warning(f"Failed to setup ultra performance optimizations: {e}")
            self.ultra_performance_optimizer = None
    
    def _setup_performance_profiling(self):
        """Setup performance profiling."""
        try:
            self.performance_profiler = PerformanceProfiler(
                enable_torch_profiler=True,
                enable_memory_profiler=True,
                enable_gpu_profiler=True
            )
            logger.info("Performance profiling enabled")
        except Exception as e:
            logger.warning(f"Failed to setup performance profiling: {e}")
            self.performance_profiler = None
    
    def _setup_training_components(self):
        """Setup model, optimizer, and scheduler."""
        # Move model to device
        self.model = self.model.to(self.device)
        
        # Apply ultra performance optimizations to model
        if self.ultra_performance_optimizer:
            try:
                self.model = self.ultra_performance_optimizer.optimize_model(self.model)
                logger.info("Model optimized with ultra performance techniques")
            except Exception as e:
                logger.warning(f"Failed to optimize model: {e}")
        
        # Setup optimizer with parameter grouping
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in self.model.named_parameters() 
                          if not any(nd in n for nd in no_decay)],
                "weight_decay": self.config.weight_decay,
            },
            {
                "params": [p for n, p in self.model.named_parameters() 
                          if any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
        ]
        
        self.optimizer = AdamW(
            optimizer_grouped_parameters,
            lr=self.config.initial_lr,
            weight_decay=self.config.weight_decay
        )
        
        # Setup learning rate scheduler
        total_steps = len(self.train_dataloader) * self.config.num_epochs // self.config.gradient_accumulation_steps
        
        if self.config.scheduler_type == "cosine":
            self.scheduler = get_cosine_schedule_with_warmup(
                self.optimizer,
                num_warmup_steps=self.config.warmup_steps,
                num_training_steps=total_steps
            )
        elif self.config.scheduler_type == "linear":
            self.scheduler = get_linear_schedule_with_warmup(
                self.optimizer,
                num_warmup_steps=self.config.warmup_steps,
                num_training_steps=total_steps
            )
        elif self.config.scheduler_type == "polynomial":
            self.scheduler = get_polynomial_decay_schedule_with_warmup(
                self.optimizer,
                num_warmup_steps=self.config.warmup_steps,
                num_training_steps=total_steps,
                lr_end=self.config.min_lr,
                power=2.0
            )
        else:
            self.scheduler = None
        
        # Setup mixed precision
        if self.config.mixed_precision_enabled:
            self.scaler = GradScaler()
        else:
            self.scaler = None
        
        # Setup checkpoint directory
        self.checkpoint_dir = Path(self.config.checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        logger.info(f"Training components setup complete. Device: {self.device}")
        logger.info(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def _get_mixed_precision_dtype(self) -> torch.dtype:
        """Get mixed precision dtype."""
        if self.config.dtype == "fp16":
            return torch.float16
        elif self.config.dtype == "bf16":
            return torch.bfloat16
        else:
            return torch.float32
    
    def _save_checkpoint(self, epoch: int, is_best: bool = False):
        """Save model checkpoint."""
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict() if self.scheduler else None,
            "config": self.config,
            "metrics": self.metrics,
            "best_val_loss": min(self.metrics.val_losses) if self.metrics.val_losses else float('inf')
        }
        
        # Save latest checkpoint
        if self.config.save_last_checkpoint:
            latest_path = self.checkpoint_dir / "latest_checkpoint.pt"
            torch.save(checkpoint, latest_path)
        
        # Save best checkpoint
        if is_best and self.config.save_best_only:
            best_path = self.checkpoint_dir / "best_checkpoint.pt"
            torch.save(checkpoint, best_path)
            logger.info(f"New best checkpoint saved at epoch {epoch}")
        
        # Save epoch checkpoint
        epoch_path = self.checkpoint_dir / f"checkpoint_epoch_{epoch}.pt"
        torch.save(checkpoint, epoch_path)
    
    def _load_checkpoint(self, checkpoint_path: str):
        """Load model checkpoint."""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        if self.scheduler and checkpoint["scheduler_state_dict"]:
            self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        
        start_epoch = checkpoint["epoch"] + 1
        logger.info(f"Checkpoint loaded from epoch {checkpoint['epoch']}")
        return start_epoch
    
    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """Train for one epoch with ultra performance optimizations."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        # Start performance profiling
        if self.performance_profiler:
            self.performance_profiler.start_profiling()
        
        epoch_start_time = time.time()
        
        progress_bar = tqdm(
            self.train_dataloader,
            desc=f"Epoch {epoch + 1}/{self.config.num_epochs}",
            leave=False
        )
        
        for batch_idx, batch in enumerate(progress_bar):
            batch_start_time = time.time()
            
            try:
                # Move batch to device
                if isinstance(batch, (list, tuple)):
                    batch = [b.to(self.device) if torch.is_tensor(b) else b for b in batch]
                elif torch.is_tensor(batch):
                    batch = batch.to(self.device)
                
                # Forward pass with mixed precision
                with autocast(enabled=self.config.autocast):
                    if isinstance(batch, (list, tuple)):
                        loss = self.model(*batch)
                    else:
                        loss = self.model(batch)
                
                # Scale loss for gradient accumulation
                loss = loss / self.config.gradient_accumulation_steps
                
                # Backward pass
                if self.scaler:
                    self.scaler.scale(loss).backward()
                else:
                    loss.backward()
                
                # Gradient accumulation
                if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                    # Gradient clipping
                    if self.scaler:
                        self.scaler.unscale_(self.optimizer)
                        clip_grad_norm_(self.model.parameters(), self.config.max_grad_norm)
                        self.scaler.step(self.optimizer)
                        self.scaler.update()
                    else:
                        clip_grad_norm_(self.model.parameters(), self.config.max_grad_norm)
                        self.optimizer.step()
                    
                    # Update learning rate
                    if self.scheduler:
                        self.scheduler.step()
                    
                    # Zero gradients
                    self.optimizer.zero_grad()
                
                # Update metrics
                total_loss += loss.item() * self.config.gradient_accumulation_steps
                num_batches += 1
                
                # Update progress bar
                progress_bar.set_postfix({
                    "loss": f"{loss.item():.4f}",
                    "lr": f"{self.optimizer.param_groups[0]['lr']:.2e}"
                })
                
                # Logging
                if batch_idx % self.config.logging_steps == 0:
                    logger.info(
                        f"Epoch {epoch + 1}, Batch {batch_idx}, "
                        f"Loss: {loss.item():.4f}, "
                        f"LR: {self.optimizer.param_groups[0]['lr']:.2e}"
                    )
                
                # Memory optimization
                if self.ultra_performance_optimizer:
                    self.ultra_performance_optimizer.optimize_memory()
                
            except Exception as e:
                logger.error(f"Error in batch {batch_idx}: {e}")
                continue
            
            # Batch timing
            batch_time = time.time() - batch_start_time
            if batch_idx % 100 == 0:
                logger.debug(f"Batch {batch_idx} took {batch_time:.3f}s")
        
        # Stop performance profiling
        if self.performance_profiler:
            profiling_results = self.performance_profiler.stop_profiling()
            logger.info(f"Performance profiling results: {profiling_results}")
        
        epoch_time = time.time() - epoch_start_time
        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
        
        # Update metrics
        self.metrics.update(
            train_loss=avg_loss,
            training_time=epoch_time,
            lr=self.optimizer.param_groups[0]['lr']
        )
        
        return {
            "train_loss": avg_loss,
            "epoch_time": epoch_time,
            "num_batches": num_batches
        }
    
    def validate(self) -> Dict[str, float]:
        """Validate the model."""
        if not self.val_dataloader:
            return {"val_loss": float('inf')}
        
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch in self.val_dataloader:
                try:
                    # Move batch to device
                    if isinstance(batch, (list, tuple)):
                        batch = [b.to(self.device) if torch.is_tensor(b) else b for b in batch]
                    elif torch.is_tensor(batch):
                        batch = batch.to(self.device)
                    
                    # Forward pass
                    with autocast(enabled=self.config.autocast):
                        if isinstance(batch, (list, tuple)):
                            loss = self.model(*batch)
                        else:
                            loss = self.model(batch)
                    
                    total_loss += loss.item()
                    num_batches += 1
                    
                except Exception as e:
                    logger.error(f"Error in validation batch: {e}")
                    continue
        
        avg_val_loss = total_loss / num_batches if num_batches > 0 else float('inf')
        self.metrics.update(val_loss=avg_val_loss)
        
        return {"val_loss": avg_val_loss}
    
    def train(self, resume_from: Optional[str] = None) -> Dict[str, Any]:
        """Main training loop with ultra performance optimizations."""
        start_epoch = 0
        
        # Resume from checkpoint if specified
        if resume_from:
            start_epoch = self._load_checkpoint(resume_from)
        
        # Pre-training optimization
        if self.ultra_performance_optimizer:
            try:
                self.ultra_performance_optimizer.pre_training_optimization(self.model)
                logger.info("Pre-training optimizations applied")
            except Exception as e:
                logger.warning(f"Failed to apply pre-training optimizations: {e}")
        
        logger.info(f"Starting training from epoch {start_epoch}")
        training_start_time = time.time()
        
        best_val_loss = float('inf')
        
        for epoch in range(start_epoch, self.config.num_epochs):
            epoch_start_time = time.time()
            
            # Train epoch
            train_results = self.train_epoch(epoch)
            
            # Validate
            if epoch % self.config.validation_interval == 0:
                val_results = self.validate()
                current_val_loss = val_results["val_loss"]
                
                logger.info(
                    f"Epoch {epoch + 1} - "
                    f"Train Loss: {train_results['train_loss']:.4f}, "
                    f"Val Loss: {current_val_loss:.4f}, "
                    f"Time: {train_results['epoch_time']:.2f}s"
                )
                
                # Check if this is the best model
                is_best = current_val_loss < best_val_loss
                if is_best:
                    best_val_loss = current_val_loss
                
                # Save checkpoint
                if epoch % self.config.save_steps == 0:
                    self._save_checkpoint(epoch, is_best)
                
                # Early stopping check
                if self.config.early_stopping_enabled:
                    if self.early_stopping(current_val_loss, epoch):
                        logger.info(f"Early stopping triggered at epoch {epoch + 1}")
                        break
            else:
                logger.info(
                    f"Epoch {epoch + 1} - "
                    f"Train Loss: {train_results['train_loss']:.4f}, "
                    f"Time: {train_results['epoch_time']:.2f}s"
                )
            
            # Post-epoch optimization
            if self.ultra_performance_optimizer:
                try:
                    self.ultra_performance_optimizer.post_epoch_optimization(self.model)
                except Exception as e:
                    logger.warning(f"Failed to apply post-epoch optimizations: {e}")
        
        # Final optimization
        if self.ultra_performance_optimizer:
            try:
                self.ultra_performance_optimizer.post_training_optimization(self.model)
                logger.info("Post-training optimizations applied")
            except Exception as e:
                logger.warning(f"Failed to apply post-training optimizations: {e}")
        
        total_training_time = time.time() - training_start_time
        
        # Save final checkpoint
        self._save_checkpoint(self.config.num_epochs - 1, False)
        
        # Get final summary
        summary = self.metrics.get_summary()
        summary["total_training_time"] = total_training_time
        summary["best_val_loss"] = best_val_loss
        
        logger.info("Training completed successfully!")
        logger.info(f"Training summary: {summary}")
        
        return summary
    
    def get_model(self) -> nn.Module:
        """Get the trained model."""
        return self.model
    
    def get_metrics(self) -> TrainingMetrics:
        """Get training metrics."""
        return self.metrics
    
    def cleanup(self):
        """Cleanup resources."""
        if self.performance_profiler:
            self.performance_profiler.cleanup()
        
        if self.ultra_performance_optimizer:
            self.ultra_performance_optimizer.cleanup()
        
        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
