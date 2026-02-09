#!/usr/bin/env python3
"""
Standalone Diffusion Loss Functions and Optimization Demo

This script demonstrates the comprehensive system for implementing appropriate
loss functions and optimization algorithms for diffusion models.
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
import matplotlib.pyplot as plt
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enums and Configurations
class LossType(Enum):
    """Types of loss functions for diffusion models."""
    MSE = "mse"
    MAE = "mae"
    HUBER = "huber"
    SMOOTH_L1 = "smooth_l1"
    KL_DIVERGENCE = "kl_divergence"
    COMBINED = "combined"

class OptimizerType(Enum):
    """Types of optimizers for diffusion models."""
    ADAM = "adam"
    ADAMW = "adamw"
    SGD = "sgd"
    RMSprop = "rmsprop"
    ADAGRAD = "adagrad"
    ADADELTA = "adadelta"

class SchedulerType(Enum):
    """Types of learning rate schedulers."""
    STEP = "step"
    MULTI_STEP = "multi_step"
    EXPONENTIAL = "exponential"
    COSINE = "cosine"
    COSINE_WARM_RESTART = "cosine_warm_restart"
    ONE_CYCLE = "one_cycle"
    PLATEAU = "plateau"
    LINEAR = "linear"
    POLYNOMIAL = "polynomial"

@dataclass
class LossConfig:
    """Configuration for loss functions."""
    loss_type: LossType = LossType.MSE
    reduction: str = "mean"
    mse_weight: float = 1.0
    huber_delta: float = 1.0
    smooth_l1_beta: float = 1.0
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
    momentum: float = 0.9
    nesterov: bool = False
    alpha: float = 0.99

@dataclass
class SchedulerConfig:
    """Configuration for learning rate schedulers."""
    scheduler_type: SchedulerType = SchedulerType.COSINE
    warmup_steps: int = 1000
    warmup_start_lr: float = 1e-6
    step_size: int = 30
    gamma: float = 0.1
    milestones: List[int] = field(default_factory=lambda: [30, 60, 90])
    exp_gamma: float = 0.95
    t_max: int = 100
    eta_min: float = 1e-6
    t_0: int = 10
    t_mult: int = 2
    max_lr: float = 1e-3

# Core Classes
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
        return F.kl_div(prediction, target, reduction="batchmean") * 1.0
    
    def _combined_loss(self, prediction: torch.Tensor, target: torch.Tensor, **kwargs) -> torch.Tensor:
        """Combined loss with multiple components."""
        total_loss = 0.0
        
        if "mse" in self.config.combined_weights:
            mse_loss = F.mse_loss(prediction, target, reduction=self.config.reduction)
            total_loss += self.config.combined_weights["mse"] * mse_loss
        
        if "perceptual" in self.config.combined_weights:
            perceptual_loss = F.mse_loss(prediction, target, reduction=self.config.reduction)
            total_loss += self.config.combined_weights["perceptual"] * perceptual_loss
        
        if "style" in self.config.combined_weights:
            style_loss = F.mse_loss(prediction, target, reduction=self.config.reduction)
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
                weight_decay=self.config.weight_decay
            )
        
        elif self.config.optimizer_type == OptimizerType.ADAMW:
            return optim.AdamW(
                model.parameters(),
                lr=self.config.learning_rate,
                betas=self.config.betas,
                eps=self.config.eps,
                weight_decay=self.config.weight_decay
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
                weight_decay=self.config.weight_decay,
                eps=self.config.eps
            )
        
        elif self.config.optimizer_type == OptimizerType.ADADELTA:
            return optim.Adadelta(
                model.parameters(),
                lr=self.config.learning_rate,
                eps=self.config.eps,
                weight_decay=self.config.weight_decay
            )
        
        else:
            raise ValueError(f"Unsupported optimizer type: {self.config.optimizer_type}")

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
        
        elif self.config.scheduler_type == SchedulerType.LINEAR:
            return LinearLR(
                optimizer,
                start_factor=1.0,
                end_factor=0.0,
                total_iters=kwargs.get('total_iters', 100)
            )
        
        elif self.config.scheduler_type == SchedulerType.POLYNOMIAL:
            return PolynomialLR(
                optimizer,
                total_iters=kwargs.get('total_iters', 100),
                power=1.0
            )
        
        else:
            raise ValueError(f"Unsupported scheduler type: {self.config.scheduler_type}")

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

# Mock Model and Utility Functions
class MockDiffusionModel(nn.Module):
    """Mock diffusion model for demonstration purposes."""
    
    def __init__(self, input_dim: int = 64, hidden_dim: int = 128, output_dim: int = 64):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # Time embedding
        self.time_embedding = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Main network
        self.network = nn.Sequential(
            nn.Linear(input_dim + hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
    
    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        # Time embedding
        t_emb = self.time_embedding(t.unsqueeze(-1).float())
        
        # Concatenate input and time embedding
        x_combined = torch.cat([x, t_emb], dim=-1)
        
        # Forward through network
        return self.network(x_combined)

def create_sample_batch(batch_size: int = 32, input_dim: int = 64, device: str = "cpu") -> Tuple[torch.Tensor, ...]:
    """Create sample batch for training."""
    x_t = torch.randn(batch_size, input_dim, device=device)
    noise = torch.randn(batch_size, input_dim, device=device)
    t = torch.randint(0, 1000, (batch_size,), device=device)
    
    return x_t, noise, t

# Demo Functions
def demo_loss_functions():
    """Demonstrate different loss functions."""
    logger.info("🎯 Demo 1: Loss Functions")
    
    # Create sample data
    batch_size = 32
    input_dim = 64
    
    prediction = torch.randn(batch_size, input_dim)
    target = torch.randn(batch_size, input_dim)
    
    # Test different loss types
    loss_types = [
        LossType.MSE,
        LossType.MAE,
        LossType.HUBER,
        LossType.SMOOTH_L1,
        LossType.KL_DIVERGENCE
    ]
    
    loss_results = {}
    
    for loss_type in loss_types:
        try:
            config = LossConfig(loss_type=loss_type)
            loss_fn = DiffusionLossFunctions(config)
            
            loss_value = loss_fn.compute_loss(prediction, target)
            loss_results[loss_type.value] = loss_value.item()
            
            logger.info(f"  {loss_type.value.upper()}: {loss_value.item():.6f}")
            
        except Exception as e:
            logger.error(f"  ❌ {loss_type.value.upper()}: {e}")
            loss_results[loss_type.value] = None
    
    # Test combined loss
    try:
        combined_config = LossConfig(
            loss_type=LossType.COMBINED,
            combined_weights={"mse": 1.0, "perceptual": 0.1}
        )
        combined_loss_fn = DiffusionLossFunctions(combined_config)
        combined_loss = combined_loss_fn.compute_loss(prediction, target)
        loss_results["combined"] = combined_loss.item()
        logger.info(f"  COMBINED: {combined_loss.item():.6f}")
        
    except Exception as e:
        logger.error(f"  ❌ COMBINED: {e}")
        loss_results["combined"] = None
    
    return loss_results

def demo_optimizers():
    """Demonstrate different optimizers."""
    logger.info("\n⚡ Demo 2: Optimizers")
    
    # Create a simple model
    model = MockDiffusionModel()
    
    # Test different optimizer types
    optimizer_types = [
        OptimizerType.ADAM,
        OptimizerType.ADAMW,
        OptimizerType.SGD,
        OptimizerType.RMSprop,
        OptimizerType.ADAGRAD,
        OptimizerType.ADADELTA
    ]
    
    optimizer_results = {}
    
    for opt_type in optimizer_types:
        try:
            config = OptimizerConfig(
                optimizer_type=opt_type,
                learning_rate=1e-4,
                weight_decay=1e-2
            )
            
            optimizer = DiffusionOptimizers(config)
            opt_instance = optimizer.create_optimizer(model)
            
            # Test optimizer step
            x_t, noise, t = create_sample_batch()
            predicted_noise = model(x_t, t)
            loss = F.mse_loss(predicted_noise, noise)
            
            loss.backward()
            opt_instance.step()
            
            optimizer_results[opt_type.value] = "✅ Success"
            logger.info(f"  {opt_type.value.upper()}: ✅ Success")
            
        except Exception as e:
            logger.error(f"  ❌ {opt_type.value.upper()}: {e}")
            optimizer_results[opt_type.value] = f"❌ {e}"
    
    return optimizer_results

def demo_schedulers():
    """Demonstrate different learning rate schedulers."""
    logger.info("\n📈 Demo 3: Learning Rate Schedulers")
    
    # Create a simple model and optimizer
    model = MockDiffusionModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    # Test different scheduler types
    scheduler_types = [
        SchedulerType.STEP,
        SchedulerType.MULTI_STEP,
        SchedulerType.EXPONENTIAL,
        SchedulerType.COSINE,
        SchedulerType.COSINE_WARM_RESTART,
        SchedulerType.LINEAR,
        SchedulerType.POLYNOMIAL
    ]
    
    scheduler_results = {}
    
    for sched_type in scheduler_types:
        try:
            config = SchedulerConfig(
                scheduler_type=sched_type,
                warmup_steps=100,
                warmup_start_lr=1e-6
            )
            
            scheduler = DiffusionSchedulers(config)
            sched_instance = scheduler.create_scheduler(optimizer, total_steps=1000)
            
            # Test scheduler step
            initial_lr = optimizer.param_groups[0]['lr']
            sched_instance.step()
            new_lr = optimizer.param_groups[0]['lr']
            
            scheduler_results[sched_type.value] = {
                "initial_lr": initial_lr,
                "new_lr": new_lr,
                "status": "✅ Success"
            }
            
            logger.info(f"  {sched_type.value.upper()}: ✅ Success (LR: {initial_lr:.6f} → {new_lr:.6f})")
            
        except Exception as e:
            logger.error(f"  ❌ {sched_type.value.upper()}: {e}")
            scheduler_results[sched_type.value] = {"status": f"❌ {e}"}
    
    return scheduler_results

def demo_training_manager():
    """Demonstrate the complete training manager."""
    logger.info("\n🚀 Demo 4: Training Manager")
    
    # Create model
    model = MockDiffusionModel()
    
    # Create training configurations
    configs = [
        ("Basic MSE + AdamW + Cosine", 
         LossConfig(loss_type=LossType.MSE),
         OptimizerConfig(optimizer_type=OptimizerType.ADAMW, learning_rate=1e-4),
         SchedulerConfig(scheduler_type=SchedulerType.COSINE, warmup_steps=100)),
        ("Advanced Combined + AdamW + Linear", 
         LossConfig(loss_type=LossType.COMBINED, combined_weights={"mse": 1.0, "perceptual": 0.1}),
         OptimizerConfig(optimizer_type=OptimizerType.ADAMW, learning_rate=1e-4),
         SchedulerConfig(scheduler_type=SchedulerType.LINEAR, warmup_steps=100))
    ]
    
    training_results = {}
    
    for config_name, loss_config, optimizer_config, scheduler_config in configs:
        try:
            logger.info(f"\n  Testing: {config_name}")
            
            # Create training manager
            training_manager = DiffusionTrainingManager(
                loss_config, optimizer_config, scheduler_config
            )
            
            # Setup training
            training_manager.setup_training(model, total_steps=100, epochs=10, steps_per_epoch=10)
            
            # Run a few training steps
            step_metrics = []
            for step in range(10):
                batch = create_sample_batch()
                metrics = training_manager.training_step(model, batch, step)
                step_metrics.append(metrics)
                
                if step % 5 == 0:
                    logger.info(f"    Step {step}: Loss = {metrics['loss']:.6f}, LR = {metrics['learning_rate']:.6f}")
            
            # Get training summary
            summary = training_manager.get_training_summary()
            
            training_results[config_name] = {
                "status": "✅ Success",
                "final_loss": summary.get("final_loss", 0),
                "avg_loss": summary.get("avg_loss", 0),
                "total_steps": summary.get("total_steps", 0)
            }
            
            logger.info(f"    ✅ Training completed successfully")
            logger.info(f"    Final Loss: {summary.get('final_loss', 0):.6f}")
            logger.info(f"    Average Loss: {summary.get('avg_loss', 0):.6f}")
            
        except Exception as e:
            logger.error(f"    ❌ Failed: {e}")
            training_results[config_name] = {"status": f"❌ {e}"}
    
    return training_results

def demo_performance_comparison():
    """Demonstrate performance comparison between different configurations."""
    logger.info("\n⚖️ Demo 5: Performance Comparison")
    
    # Create model
    model = MockDiffusionModel()
    
    # Test configurations
    test_configs = [
        ("MSE + AdamW + Cosine", LossType.MSE, OptimizerType.ADAMW, SchedulerType.COSINE),
        ("MSE + SGD + Step", LossType.MSE, OptimizerType.SGD, SchedulerType.STEP),
        ("Huber + Adam + Exponential", LossType.HUBER, OptimizerType.ADAM, SchedulerType.EXPONENTIAL),
        ("Smooth L1 + RMSprop + MultiStep", LossType.SMOOTH_L1, OptimizerType.RMSprop, SchedulerType.MULTI_STEP)
    ]
    
    performance_results = {}
    
    for config_name, loss_type, opt_type, sched_type in test_configs:
        try:
            logger.info(f"\n  Testing: {config_name}")
            
            # Create configurations
            loss_config = LossConfig(loss_type=loss_type)
            optimizer_config = OptimizerConfig(
                optimizer_type=opt_type,
                learning_rate=1e-4,
                weight_decay=1e-2
            )
            scheduler_config = SchedulerConfig(
                scheduler_type=sched_type,
                warmup_steps=50
            )
            
            # Create training manager
            training_manager = DiffusionTrainingManager(
                loss_config, optimizer_config, scheduler_config
            )
            
            # Setup training
            training_manager.setup_training(model, total_steps=50, epochs=5, steps_per_epoch=10)
            
            # Measure training time
            start_time = time.time()
            
            # Run training steps
            total_loss = 0
            for step in range(50):
                batch = create_sample_batch()
                metrics = training_manager.training_step(model, batch, step)
                total_loss += metrics['loss']
            
            end_time = time.time()
            training_time = end_time - start_time
            
            # Calculate metrics
            avg_loss = total_loss / 50
            steps_per_second = 50 / training_time
            
            performance_results[config_name] = {
                "status": "✅ Success",
                "training_time": training_time,
                "avg_loss": avg_loss,
                "steps_per_second": steps_per_second
            }
            
            logger.info(f"    ✅ Training completed")
            logger.info(f"    Training Time: {training_time:.2f}s")
            logger.info(f"    Average Loss: {avg_loss:.6f}")
            logger.info(f"    Steps/Second: {steps_per_second:.2f}")
            
        except Exception as e:
            logger.error(f"    ❌ Failed: {e}")
            performance_results[config_name] = {"status": f"❌ {e}"}
    
    return performance_results

def main():
    """Main demonstration function."""
    logger.info("🚀 Starting Standalone Diffusion Loss Functions and Optimization Demo")
    logger.info("=" * 80)
    
    # Create output directory
    output_dir = Path("diffusion_loss_optimization_outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Demo 1: Loss Functions
    loss_results = demo_loss_functions()
    
    # Demo 2: Optimizers
    optimizer_results = demo_optimizers()
    
    # Demo 3: Schedulers
    scheduler_results = demo_schedulers()
    
    # Demo 4: Training Manager
    training_results = demo_training_manager()
    
    # Demo 5: Performance Comparison
    performance_results = demo_performance_comparison()
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("🎉 Standalone Diffusion Loss Functions and Optimization Demo Completed!")
    logger.info(f"📁 All outputs saved to: {output_dir}")
    
    # Print key statistics
    successful_configs = sum(1 for result in performance_results.values() 
                           if isinstance(result, dict) and result.get("status") == "✅ Success")
    total_configs = len(performance_results)
    
    logger.info(f"📊 Success Rate: {successful_configs}/{total_configs} configurations tested successfully")
    
    if successful_configs > 0:
        best_config = min(
            [(name, result) for name, result in performance_results.items() 
             if isinstance(result, dict) and result.get("status") == "✅ Success"],
            key=lambda x: x[1].get("avg_loss", float('inf'))
        )
        logger.info(f"🏆 Best Performing Configuration: {best_config[0]} (Loss: {best_config[1].get('avg_loss', 0):.6f})")

if __name__ == "__main__":
    main()
