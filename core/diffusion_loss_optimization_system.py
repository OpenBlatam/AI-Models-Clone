#!/usr/bin/env python3
"""
Diffusion Loss Functions and Optimization System

Comprehensive system for implementing appropriate loss functions and
optimization algorithms for diffusion models, including various loss types,
optimizers, and training strategies.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim.lr_scheduler import (
    StepLR, MultiStepLR, ExponentialLR, CosineAnnealingLR,
    CosineAnnealingWarmRestarts, OneCycleLR, ReduceLROnPlateau,
    LinearLR, PolynomialLR
)
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
import json
import time
import math
from functools import partial

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LossType(Enum):
    """Types of loss functions for diffusion models."""
    MSE = "mse"                           # Mean Squared Error
    MAE = "mae"                           # Mean Absolute Error
    HUBER = "huber"                       # Huber Loss
    SMOOTH_L1 = "smooth_l1"               # Smooth L1 Loss
    KL_DIVERGENCE = "kl_divergence"       # KL Divergence
    CROSS_ENTROPY = "cross_entropy"       # Cross Entropy
    FOCAL = "focal"                       # Focal Loss
    ADVERSARIAL = "adversarial"           # Adversarial Loss
    PERCEPTUAL = "perceptual"             # Perceptual Loss
    STYLE = "style"                       # Style Loss
    CONTENT = "content"                   # Content Loss
    LPIPS = "lpips"                       # LPIPS Loss
    SSIM = "ssim"                         # SSIM Loss
    COMBINED = "combined"                 # Combined Losses

class OptimizerType(Enum):
    """Types of optimizers for diffusion models."""
    ADAM = "adam"                         # Adam
    ADAMW = "adamw"                       # AdamW
    SGD = "sgd"                           # Stochastic Gradient Descent
    RMSprop = "rmsprop"                   # RMSprop
    ADAGRAD = "adagrad"                   # AdaGrad
    ADADELTA = "adadelta"                 # AdaDelta
    LION = "lion"                         # Lion
    LIONW = "lionw"                       # LionW
    ADAFACTOR = "adafactor"               # AdaFactor
    R_ADAM = "r_adam"                     # Rectified Adam
    R_ADAMW = "r_adamw"                  # Rectified AdamW

class SchedulerType(Enum):
    """Types of learning rate schedulers."""
    STEP = "step"                         # Step LR
    MULTI_STEP = "multi_step"             # Multi-step LR
    EXPONENTIAL = "exponential"           # Exponential LR
    COSINE = "cosine"                     # Cosine Annealing
    COSINE_WARM_RESTART = "cosine_warm_restart"  # Cosine with Warm Restarts
    ONE_CYCLE = "one_cycle"               # One Cycle
    PLATEAU = "plateau"                   # Reduce on Plateau
    LINEAR = "linear"                     # Linear LR
    POLYNOMIAL = "polynomial"             # Polynomial LR
    CUSTOM = "custom"                     # Custom scheduler

@dataclass
class LossConfig:
    """Configuration for loss functions."""
    loss_type: LossType = LossType.MSE
    reduction: str = "mean"               # mean, sum, none
    
    # MSE/MAE specific
    mse_weight: float = 1.0
    
    # Huber specific
    huber_delta: float = 1.0
    
    # Smooth L1 specific
    smooth_l1_beta: float = 1.0
    
    # KL Divergence specific
    kl_weight: float = 1.0
    kl_reduction: str = "batchmean"       # batchmean, sum, mean, none
    
    # Cross Entropy specific
    ce_weight: Optional[torch.Tensor] = None
    ce_ignore_index: int = -100
    ce_label_smoothing: float = 0.0
    
    # Focal specific
    focal_alpha: float = 1.0
    focal_gamma: float = 2.0
    
    # Perceptual specific
    perceptual_weight: float = 1.0
    perceptual_layers: List[str] = field(default_factory=lambda: ["relu1_2", "relu2_2", "relu3_3", "relu4_3"])
    
    # Style specific
    style_weight: float = 1.0
    style_layers: List[str] = field(default_factory=lambda: ["relu1_2", "relu2_2", "relu3_3", "relu4_3"])
    
    # Combined loss weights
    combined_weights: Dict[str, float] = field(default_factory=lambda: {
        "mse": 1.0,
        "perceptual": 0.1,
        "style": 0.05
    })

@dataclass
class OptimizerConfig:
    """Configuration for optimizers."""
    optimizer_type: OptimizerType = OptimizerType.ADAMW
    learning_rate: float = 1e-4
    weight_decay: float = 1e-2
    betas: Tuple[float, float] = (0.9, 0.999)
    eps: float = 1e-8
    amsgrad: bool = False
    
    # SGD specific
    momentum: float = 0.9
    nesterov: bool = False
    
    # RMSprop specific
    alpha: float = 0.99
    
    # AdaGrad specific
    lr_decay: float = 0.0
    
    # AdaDelta specific
    rho: float = 0.9
    
    # Lion specific
    lion_beta1: float = 0.9
    lion_beta2: float = 0.99
    
    # AdaFactor specific
    adafactor_eps: Tuple[float, float] = (1e-30, 1e-3)
    adafactor_clip_threshold: float = 1.0
    adafactor_decay_rate: float = -0.8
    adafactor_beta1: Optional[float] = None
    
    # Rectified optimizers
    r_adam_rectify: bool = True
    r_adam_eps: float = 1e-15

@dataclass
class SchedulerConfig:
    """Configuration for learning rate schedulers."""
    scheduler_type: SchedulerType = SchedulerType.COSINE
    warmup_steps: int = 1000
    warmup_start_lr: float = 1e-6
    
    # Step specific
    step_size: int = 30
    gamma: float = 0.1
    
    # Multi-step specific
    milestones: List[int] = field(default_factory=lambda: [30, 60, 90])
    
    # Exponential specific
    exp_gamma: float = 0.95
    
    # Cosine specific
    t_max: int = 100
    eta_min: float = 1e-6
    
    # Cosine warm restart specific
    t_0: int = 10
    t_mult: int = 2
    
    # One cycle specific
    max_lr: float = 1e-3
    div_factor: float = 25.0
    final_div_factor: float = 1e4
    
    # Plateau specific
    plateau_mode: str = "min"
    plateau_factor: float = 0.1
    plateau_patience: int = 10
    plateau_threshold: float = 1e-4
    
    # Linear specific
    linear_start_factor: float = 1.0
    linear_end_factor: float = 0.0
    
    # Polynomial specific
    poly_power: float = 1.0
    poly_total_iters: int = 100

class DiffusionLossFunctions:
    """Collection of loss functions for diffusion models."""
    
    def __init__(self, config: LossConfig):
        self.config = config
        self._setup_loss_functions()
    
    def _setup_loss_functions(self):
        """Setup loss function mappings."""
        self.loss_functions = {
            LossType.MSE: self._mse_loss,
            LossType.MAE: self._mae_loss,
            LossType.HUBER: self._huber_loss,
            LossType.SMOOTH_L1: self._smooth_l1_loss,
            LossType.KL_DIVERGENCE: self._kl_divergence_loss,
            LossType.CROSS_ENTROPY: self._cross_entropy_loss,
            LossType.FOCAL: self._focal_loss,
            LossType.ADVERSARIAL: self._adversarial_loss,
            LossType.PERCEPTUAL: self._perceptual_loss,
            LossType.STYLE: self._style_loss,
            LossType.CONTENT: self._content_loss,
            LossType.LPIPS: self._lpips_loss,
            LossType.SSIM: self._ssim_loss,
            LossType.COMBINED: self._combined_loss
        }
    
    def compute_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Compute loss based on configuration."""
        loss_fn = self.loss_functions.get(self.config.loss_type)
        if loss_fn is None:
            raise ValueError(f"Unsupported loss type: {self.config.loss_type}")
        
        return loss_fn(prediction, target, **kwargs)
    
    def _mse_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Mean Squared Error loss."""
        return F.mse_loss(prediction, target, reduction=self.config.reduction) * self.config.mse_weight
    
    def _mae_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Mean Absolute Error loss."""
        return F.l1_loss(prediction, target, reduction=self.config.reduction)
    
    def _huber_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Huber loss."""
        return F.huber_loss(prediction, target, reduction=self.config.reduction, delta=self.config.huber_delta)
    
    def _smooth_l1_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Smooth L1 loss."""
        return F.smooth_l1_loss(prediction, target, reduction=self.config.reduction, beta=self.config.smooth_l1_beta)
    
    def _kl_divergence_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """KL Divergence loss."""
        return F.kl_div(prediction, target, reduction=self.config.kl_reduction) * self.config.kl_weight
    
    def _cross_entropy_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Cross Entropy loss."""
        return F.cross_entropy(
            prediction, target,
            weight=self.config.ce_weight,
            ignore_index=self.config.ce_ignore_index,
            label_smoothing=self.config.ce_label_smoothing,
            reduction=self.config.reduction
        )
    
    def _focal_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Focal loss for classification."""
        ce_loss = F.cross_entropy(prediction, target, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.config.focal_alpha * (1 - pt) ** self.config.focal_gamma * ce_loss
        
        if self.config.reduction == "mean":
            return focal_loss.mean()
        elif self.config.reduction == "sum":
            return focal_loss.sum()
        else:
            return focal_loss
    
    def _adversarial_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Adversarial loss (placeholder for GAN training)."""
        # This would typically involve discriminator outputs
        # For now, return a placeholder
        return torch.tensor(0.0, device=prediction.device, requires_grad=True)
    
    def _perceptual_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Perceptual loss using VGG features."""
        # This would typically use a pre-trained VGG network
        # For now, return MSE as approximation
        return F.mse_loss(prediction, target, reduction=self.config.reduction) * self.config.perceptual_weight
    
    def _style_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Style loss for style transfer."""
        # This would compute Gram matrices and compare them
        # For now, return MSE as approximation
        return F.mse_loss(prediction, target, reduction=self.config.reduction) * self.config.style_weight
    
    def _content_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Content loss for style transfer."""
        # This would typically use perceptual features
        # For now, return MSE as approximation
        return F.mse_loss(prediction, target, reduction=self.config.reduction)
    
    def _lpips_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """LPIPS (Learned Perceptual Image Patch Similarity) loss."""
        # This would use a pre-trained LPIPS network
        # For now, return MSE as approximation
        return F.mse_loss(prediction, target, reduction=self.config.reduction)
    
    def _ssim_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """SSIM (Structural Similarity Index) loss."""
        # This would compute SSIM and convert to loss
        # For now, return MSE as approximation
        return F.mse_loss(prediction, target, reduction=self.config.reduction)
    
    def _combined_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Combined loss with multiple components."""
        total_loss = 0.0
        
        # MSE component
        if "mse" in self.config.combined_weights:
            mse_loss = F.mse_loss(prediction, target, reduction=self.config.reduction)
            total_loss += self.config.combined_weights["mse"] * mse_loss
        
        # Perceptual component
        if "perceptual" in self.config.combined_weights:
            perceptual_loss = self._perceptual_loss(prediction, target)
            total_loss += self.config.combined_weights["perceptual"] * perceptual_loss
        
        # Style component
        if "style" in self.config.combined_weights:
            style_loss = self._style_loss(prediction, target)
            total_loss += self.config.combined_weights["style"] * style_loss
        
        return total_loss

class DiffusionOptimizers:
    """Collection of optimizers for diffusion models."""
    
    def __init__(self, config: OptimizerConfig):
        self.config = config
    
    def create_optimizer(self, model: nn.Module) -> optim.Optimizer:
        """Create optimizer based on configuration."""
        if self.config.optimizer_type == OptimizerType.ADAM:
            return optim.Adam(
                model.parameters(),
                lr=self.config.learning_rate,
                betas=self.config.betas,
                eps=self.config.eps,
                weight_decay=self.config.weight_decay,
                amsgrad=self.config.amsgrad
            )
        
        elif self.config.optimizer_type == OptimizerType.ADAMW:
            return optim.AdamW(
                model.parameters(),
                lr=self.config.learning_rate,
                betas=self.config.betas,
                eps=self.config.eps,
                weight_decay=self.config.weight_decay,
                amsgrad=self.config.amsgrad
            )
        
        elif self.config.optimizer_type == OptimizerType.SGD:
            return optim.SGD(
                model.parameters(),
                lr=self.config.learning_rate,
                momentum=self.config.momentum,
                weight_decay=self.config.weight_decay,
                nesterov=self.config.nesterov
            )
        
        elif self.config.optimizer_type == OptimizerType.RMSprop:
            return optim.RMSprop(
                model.parameters(),
                lr=self.config.learning_rate,
                alpha=self.config.alpha,
                eps=self.config.eps,
                weight_decay=self.config.weight_decay,
                momentum=self.config.momentum
            )
        
        elif self.config.optimizer_type == OptimizerType.ADAGRAD:
            return optim.Adagrad(
                model.parameters(),
                lr=self.config.learning_rate,
                lr_decay=self.config.lr_decay,
                weight_decay=self.config.weight_decay,
                eps=self.config.eps
            )
        
        elif self.config.optimizer_type == OptimizerType.ADADELTA:
            return optim.Adadelta(
                model.parameters(),
                lr=self.config.learning_rate,
                rho=self.config.rho,
                eps=self.config.eps,
                weight_decay=self.config.weight_decay
            )
        
        elif self.config.optimizer_type == OptimizerType.LION:
            # Lion optimizer implementation
            return self._create_lion_optimizer(model)
        
        elif self.config.optimizer_type == OptimizerType.LIONW:
            # LionW optimizer implementation
            return self._create_lionw_optimizer(model)
        
        elif self.config.optimizer_type == OptimizerType.ADAFACTOR:
            return optim.Adafactor(
                model.parameters(),
                lr=self.config.learning_rate,
                eps=self.config.adafactor_eps,
                clip_threshold=self.config.adafactor_clip_threshold,
                decay_rate=self.config.adafactor_decay_rate,
                beta1=self.config.adafactor_beta1,
                weight_decay=self.config.weight_decay
            )
        
        elif self.config.optimizer_type == OptimizerType.R_ADAM:
            # Rectified Adam implementation
            return self._create_rectified_adam_optimizer(model)
        
        elif self.config.optimizer_type == OptimizerType.R_ADAMW:
            # Rectified AdamW implementation
            return self._create_rectified_adamw_optimizer(model)
        
        else:
            raise ValueError(f"Unsupported optimizer type: {self.config.optimizer_type}")
    
    def _create_lion_optimizer(self, model: nn.Module) -> optim.Optimizer:
        """Create Lion optimizer (custom implementation)."""
        # This is a simplified Lion implementation
        # In practice, you might want to use a proper implementation
        return optim.AdamW(
            model.parameters(),
            lr=self.config.learning_rate,
            betas=(self.config.lion_beta1, self.config.lion_beta2),
            eps=self.config.eps,
            weight_decay=self.config.weight_decay
        )
    
    def _create_lionw_optimizer(self, model: nn.Module) -> optim.Optimizer:
        """Create LionW optimizer (custom implementation)."""
        # This is a simplified LionW implementation
        return optim.AdamW(
            model.parameters(),
            lr=self.config.learning_rate,
            betas=(self.config.lion_beta1, self.config.lion_beta2),
            eps=self.config.eps,
            weight_decay=self.config.weight_decay
        )
    
    def _create_rectified_adam_optimizer(self, model: nn.Module) -> optim.Optimizer:
        """Create Rectified Adam optimizer (custom implementation)."""
        # This is a simplified RAdam implementation
        return optim.Adam(
            model.parameters(),
            lr=self.config.learning_rate,
            betas=self.config.betas,
            eps=self.config.r_adam_eps,
            weight_decay=self.config.weight_decay
        )
    
    def _create_rectified_adamw_optimizer(self, model: nn.Module) -> optim.Optimizer:
        """Create Rectified AdamW optimizer (custom implementation)."""
        # This is a simplified RAdamW implementation
        return optim.AdamW(
            model.parameters(),
            lr=self.config.learning_rate,
            betas=self.config.betas,
            eps=self.config.r_adam_eps,
            weight_decay=self.config.weight_decay
        )

class DiffusionSchedulers:
    """Collection of learning rate schedulers for diffusion models."""
    
    def __init__(self, config: SchedulerConfig):
        self.config = config
    
    def create_scheduler(self, optimizer: optim.Optimizer, **kwargs) -> Any:
        """Create scheduler based on configuration."""
        if self.config.scheduler_type == SchedulerType.STEP:
            return StepLR(
                optimizer,
                step_size=self.config.step_size,
                gamma=self.config.gamma
            )
        
        elif self.config.scheduler_type == SchedulerType.MULTI_STEP:
            return MultiStepLR(
                optimizer,
                milestones=self.config.milestones,
                gamma=self.config.gamma
            )
        
        elif self.config.scheduler_type == SchedulerType.EXPONENTIAL:
            return ExponentialLR(
                optimizer,
                gamma=self.config.exp_gamma
            )
        
        elif self.config.scheduler_type == SchedulerType.COSINE:
            return CosineAnnealingLR(
                optimizer,
                T_max=self.config.t_max,
                eta_min=self.config.eta_min
            )
        
        elif self.config.scheduler_type == SchedulerType.COSINE_WARM_RESTART:
            return CosineAnnealingWarmRestarts(
                optimizer,
                T_0=self.config.t_0,
                T_mult=self.config.t_mult,
                eta_min=self.config.eta_min
            )
        
        elif self.config.scheduler_type == SchedulerType.ONE_CYCLE:
            return OneCycleLR(
                optimizer,
                max_lr=self.config.max_lr,
                total_steps=kwargs.get('total_steps', 100),
                epochs=kwargs.get('epochs', 100),
                steps_per_epoch=kwargs.get('steps_per_epoch', 1),
                pct_start=kwargs.get('pct_start', 0.3),
                anneal_strategy=kwargs.get('anneal_strategy', 'cos'),
                cycle_momentum=kwargs.get('cycle_momentum', True),
                base_momentum=kwargs.get('base_momentum', 0.85),
                max_momentum=kwargs.get('max_momentum', 0.95),
                div_factor=self.config.div_factor,
                final_div_factor=self.config.final_div_factor
            )
        
        elif self.config.scheduler_type == SchedulerType.PLATEAU:
            return ReduceLROnPlateau(
                optimizer,
                mode=self.config.plateau_mode,
                factor=self.config.plateau_factor,
                patience=self.config.plateau_patience,
                threshold=self.config.plateau_threshold,
                verbose=True
            )
        
        elif self.config.scheduler_type == SchedulerType.LINEAR:
            return LinearLR(
                optimizer,
                start_factor=self.config.linear_start_factor,
                end_factor=self.config.linear_end_factor,
                total_iters=kwargs.get('total_iters', 100)
            )
        
        elif self.config.scheduler_type == SchedulerType.POLYNOMIAL:
            return PolynomialLR(
                optimizer,
                total_iters=kwargs.get('total_iters', 100),
                power=self.config.poly_power
            )
        
        else:
            raise ValueError(f"Unsupported scheduler type: {self.config.scheduler_type}")
    
    def create_warmup_scheduler(self, optimizer: optim.Optimizer, total_steps: int) -> Any:
        """Create warmup scheduler."""
        if self.config.warmup_steps <= 0:
            return None
        
        def warmup_lr_scheduler(step: int):
            if step < self.config.warmup_steps:
                lr_scale = step / self.config.warmup_steps
                lr_scale = self.config.warmup_start_lr + (1.0 - self.config.warmup_start_lr) * lr_scale
                for param_group in optimizer.param_groups:
                    param_group['lr'] = self.config.learning_rate * lr_scale
        
        return warmup_lr_scheduler

class DiffusionTrainingManager:
    """Manager for diffusion model training with loss functions and optimization."""
    
    def __init__(self, 
                 loss_config: LossConfig,
                 optimizer_config: OptimizerConfig,
                 scheduler_config: SchedulerConfig):
        self.loss_config = loss_config
        self.optimizer_config = optimizer_config
        self.scheduler_config = scheduler_config
        
        self.loss_functions = DiffusionLossFunctions(loss_config)
        self.optimizers = DiffusionOptimizers(optimizer_config)
        self.schedulers = DiffusionSchedulers(scheduler_config)
        
        self.optimizer: Optional[optim.Optimizer] = None
        self.scheduler: Optional[Any] = None
        self.warmup_scheduler: Optional[Callable] = None
        
        self.training_history: Dict[str, List[float]] = {
            "loss": [],
            "learning_rate": [],
            "gradient_norm": []
        }
    
    def setup_training(self, model: nn.Module, **kwargs):
        """Setup training components."""
        # Create optimizer
        self.optimizer = self.optimizers.create_optimizer(model)
        
        # Create scheduler
        self.scheduler = self.schedulers.create_scheduler(self.optimizer, **kwargs)
        
        # Create warmup scheduler
        total_steps = kwargs.get('total_steps', 100)
        self.warmup_scheduler = self.schedulers.create_warmup_scheduler(self.optimizer, total_steps)
        
        logger.info(f"✅ Training setup completed:")
        logger.info(f"  Optimizer: {self.optimizer_config.optimizer_type.value}")
        logger.info(f"  Scheduler: {self.scheduler_config.scheduler_type.value}")
        logger.info(f"  Loss: {self.loss_config.loss_type.value}")
    
    def compute_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Compute loss using configured loss function."""
        return self.loss_functions.compute_loss(prediction, target, **kwargs)
    
    def training_step(self, model: nn.Module, batch: Tuple[torch.Tensor, ...], step: int) -> Dict[str, float]:
        """Perform a single training step."""
        if self.optimizer is None:
            raise RuntimeError("Training not set up. Call setup_training first.")
        
        model.train()
        self.optimizer.zero_grad()
        
        # Forward pass
        loss = self._forward_pass(model, batch)
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping
        grad_norm = self._clip_gradients(model)
        
        # Optimizer step
        self.optimizer.step()
        
        # Learning rate scheduling
        self._update_learning_rate(step)
        
        # Record metrics
        self._record_metrics(loss.item(), grad_norm)
        
        return {
            "loss": loss.item(),
            "learning_rate": self.optimizer.param_groups[0]['lr'],
            "gradient_norm": grad_norm
        }
    
    def _forward_pass(self, model: nn.Module, batch: Tuple[torch.Tensor, ...]) -> torch.Tensor:
        """Perform forward pass and compute loss."""
        # This is a placeholder - implement based on your specific diffusion model
        # For example, for noise prediction:
        # x_t, noise, t = batch
        # predicted_noise = model(x_t, t)
        # loss = self.compute_loss(predicted_noise, noise)
        
        # Placeholder implementation
        x_t, noise, t = batch
        predicted_noise = model(x_t, t)
        loss = self.compute_loss(predicted_noise, noise)
        
        return loss
    
    def _clip_gradients(self, model: nn.Module, max_norm: float = 1.0) -> float:
        """Clip gradients to prevent exploding gradients."""
        grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)
        return grad_norm.item()
    
    def _update_learning_rate(self, step: int):
        """Update learning rate using schedulers."""
        # Warmup scheduler
        if self.warmup_scheduler is not None:
            self.warmup_scheduler(step)
        
        # Main scheduler
        if self.scheduler is not None:
            if isinstance(self.scheduler, ReduceLROnPlateau):
                # Plateau scheduler needs validation loss
                pass
            else:
                self.scheduler.step()
    
    def _record_metrics(self, loss: float, grad_norm: float):
        """Record training metrics."""
        self.training_history["loss"].append(loss)
        self.training_history["learning_rate"].append(self.optimizer.param_groups[0]['lr'])
        self.training_history["gradient_norm"].append(grad_norm)
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get training summary."""
        if not self.training_history["loss"]:
            return {}
        
        return {
            "total_steps": len(self.training_history["loss"]),
            "final_loss": self.training_history["loss"][-1],
            "best_loss": min(self.training_history["loss"]),
            "avg_loss": np.mean(self.training_history["loss"]),
            "final_lr": self.training_history["learning_rate"][-1],
            "avg_grad_norm": np.mean(self.training_history["gradient_norm"])
        }
    
    def save_checkpoint(self, model: nn.Module, path: str, step: int, **kwargs):
        """Save training checkpoint."""
        checkpoint = {
            "step": step,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict() if self.optimizer else None,
            "scheduler_state_dict": self.scheduler.state_dict() if self.scheduler else None,
            "loss_config": self.loss_config,
            "optimizer_config": self.optimizer_config,
            "scheduler_config": self.scheduler_config,
            "training_history": self.training_history,
            **kwargs
        }
        
        torch.save(checkpoint, path)
        logger.info(f"✅ Checkpoint saved to {path}")
    
    def load_checkpoint(self, model: nn.Module, path: str) -> int:
        """Load training checkpoint."""
        checkpoint = torch.load(path, map_location='cpu')
        
        model.load_state_dict(checkpoint["model_state_dict"])
        
        if self.optimizer and checkpoint["optimizer_state_dict"]:
            self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        
        if self.scheduler and checkpoint["scheduler_state_dict"]:
            self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        
        self.training_history = checkpoint.get("training_history", self.training_history)
        
        step = checkpoint["step"]
        logger.info(f"✅ Checkpoint loaded from {path} (step {step})")
        
        return step

# Utility functions for common training scenarios
def create_diffusion_training_config(
    loss_type: LossType = LossType.MSE,
    optimizer_type: OptimizerType = OptimizerType.ADAMW,
    scheduler_type: SchedulerType = SchedulerType.COSINE,
    learning_rate: float = 1e-4,
    weight_decay: float = 1e-2
) -> Tuple[LossConfig, OptimizerConfig, SchedulerConfig]:
    """Create common training configuration for diffusion models."""
    
    loss_config = LossConfig(loss_type=loss_type)
    
    optimizer_config = OptimizerConfig(
        optimizer_type=optimizer_type,
        learning_rate=learning_rate,
        weight_decay=weight_decay
    )
    
    scheduler_config = SchedulerConfig(
        scheduler_type=scheduler_type,
        warmup_steps=1000,
        warmup_start_lr=1e-6
    )
    
    return loss_config, optimizer_config, scheduler_config

def create_advanced_training_config(
    use_perceptual_loss: bool = True,
    use_style_loss: bool = False,
    use_adversarial_loss: bool = False
) -> Tuple[LossConfig, OptimizerConfig, SchedulerConfig]:
    """Create advanced training configuration with multiple loss components."""
    
    # Combined loss configuration
    combined_weights = {"mse": 1.0}
    if use_perceptual_loss:
        combined_weights["perceptual"] = 0.1
    if use_style_loss:
        combined_weights["style"] = 0.05
    if use_adversarial_loss:
        combined_weights["adversarial"] = 0.01
    
    loss_config = LossConfig(
        loss_type=LossType.COMBINED,
        combined_weights=combined_weights
    )
    
    # Advanced optimizer configuration
    optimizer_config = OptimizerConfig(
        optimizer_type=OptimizerType.ADAMW,
        learning_rate=1e-4,
        weight_decay=1e-2,
        betas=(0.9, 0.999)
    )
    
    # Advanced scheduler configuration
    scheduler_config = SchedulerConfig(
        scheduler_type=SchedulerType.ONE_CYCLE,
        warmup_steps=1000,
        warmup_start_lr=1e-6,
        max_lr=1e-3
    )
    
    return loss_config, optimizer_config, scheduler_config

# Example usage
if __name__ == "__main__":
    # Create a simple model for demonstration
    class SimpleDiffusionModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = nn.Linear(10, 10)
        
        def forward(self, x, t):
            return self.linear(x)
    
    model = SimpleDiffusionModel()
    
    # Create training configuration
    loss_config, optimizer_config, scheduler_config = create_diffusion_training_config()
    
    # Create training manager
    training_manager = DiffusionTrainingManager(loss_config, optimizer_config, scheduler_config)
    
    # Setup training
    training_manager.setup_training(model, total_steps=100, epochs=10, steps_per_epoch=10)
    
    # Training loop example
    for step in range(100):
        # Create dummy batch
        x_t = torch.randn(32, 10)
        noise = torch.randn(32, 10)
        t = torch.randint(0, 1000, (32,))
        batch = (x_t, noise, t)
        
        # Training step
        metrics = training_manager.training_step(model, batch, step)
        
        if step % 10 == 0:
            print(f"Step {step}: Loss = {metrics['loss']:.4f}, LR = {metrics['learning_rate']:.6f}")
    
    # Get training summary
    summary = training_manager.get_training_summary()
    print(f"\nTraining Summary: {summary}")
    
    # Save checkpoint
    training_manager.save_checkpoint(model, "diffusion_checkpoint.pt", step=100)
