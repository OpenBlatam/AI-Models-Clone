#!/usr/bin/env python3
"""
Standalone Demo for Early Stopping and Learning Rate Scheduling System.

This script demonstrates the capabilities of the early stopping and learning rate
scheduling system for diffusion models without importing from the core module system.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Any
import time
import logging
from enum import Enum
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Enums and Configurations
# ============================================================================

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
    MIN = "min"
    MAX = "max"

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
    step_size: int = 30
    gamma: float = 0.1
    milestones: List[int] = field(default_factory=lambda: [30, 60, 90])
    decay_rate: float = 0.95
    T_max: int = 100
    eta_min: float = 1e-7
    T_0: int = 10
    T_mult: int = 2
    epochs: int = 100
    steps_per_epoch: int = 100
    pct_start: float = 0.3
    anneal_strategy: str = "cos"
    mode: str = "min"
    factor: float = 0.1
    patience: int = 10
    threshold: float = 1e-4
    threshold_mode: str = "rel"
    power: float = 1.0
    custom_schedule: Optional[Any] = None

@dataclass
class EarlyStoppingConfig:
    """Configuration for early stopping."""
    mode: EarlyStoppingMode = EarlyStoppingMode.MIN
    patience: int = 20
    min_delta: float = 0.0
    restore_best_weights: bool = True
    verbose: bool = True
    metric_type: MetricType = MetricType.VALIDATION_LOSS
    custom_metric: Optional[Any] = None
    min_epochs: int = 10
    max_epochs: int = 1000
    cooldown: int = 0
    min_improvement: float = 0.0

@dataclass
class TrainingConfig:
    """Configuration for training with early stopping and LR scheduling."""
    epochs: int = 100
    batch_size: int = 32
    gradient_accumulation_steps: int = 1
    initial_lr: float = 1e-4
    weight_decay: float = 1e-4
    early_stopping: bool = True
    early_stopping_config: EarlyStoppingConfig = field(default_factory=EarlyStoppingConfig)
    lr_scheduling: bool = True
    lr_scheduler_config: LRSchedulerConfig = field(default_factory=LRSchedulerConfig)
    save_checkpoints: bool = True
    checkpoint_dir: str = "checkpoints"
    log_interval: int = 10
    eval_interval: int = 5

# ============================================================================
# Core Classes
# ============================================================================

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
        
        elif self.config.scheduler_type == LRSchedulerType.LINEAR:
            self.scheduler = self._create_linear_scheduler()
        
        elif self.config.scheduler_type == LRSchedulerType.POLYNOMIAL:
            self.scheduler = self._create_polynomial_scheduler()
        
        else:
            # For other types, use a simple step scheduler as fallback
            self.scheduler = optim.lr_scheduler.StepLR(
                self.optimizer, 
                step_size=self.config.step_size, 
                gamma=self.config.gamma
            )
    
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
    
    def step(self, metric: Optional[float] = None):
        """Step the learning rate scheduler."""
        if self.scheduler is None:
            return
        
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

# ============================================================================
# Demo Classes
# ============================================================================

class SimpleDiffusionModel(nn.Module):
    """Simple diffusion model for demonstration purposes."""
    
    def __init__(self, input_dim=64, hidden_dim=128, output_dim=64):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # Time embedding
        self.time_embed = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Main network
        self.net = nn.Sequential(
            nn.Linear(input_dim + hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x, t):
        # Time embedding
        t = t.float().unsqueeze(-1) / 1000.0
        t_emb = self.time_embed(t)
        
        # Concatenate input with time embedding
        x_t = torch.cat([x, t_emb], dim=-1)
        
        # Forward pass
        return self.net(x_t)

class MockDataLoader:
    """Mock data loader for demonstration purposes."""
    
    def __init__(self, num_samples=1000, input_dim=64, batch_size=32):
        self.num_samples = num_samples
        self.input_dim = input_dim
        self.batch_size = batch_size
        self.num_batches = num_samples // batch_size
    
    def __len__(self):
        return self.num_batches
    
    def __iter__(self):
        for _ in range(self.num_batches):
            x = torch.randn(self.batch_size, self.input_dim)
            y = torch.randn(self.batch_size, self.input_dim)
            yield x, y

class EarlyStoppingLRDemo:
    """Demo class for early stopping and learning rate scheduling."""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Create model
        self.model = SimpleDiffusionModel().to(self.device)
        print(f"✓ Model created with {sum(p.numel() for p in self.model.parameters()):,} parameters")
        
        # Create data loaders
        self.train_loader = MockDataLoader(num_samples=1000, batch_size=32)
        self.val_loader = MockDataLoader(num_samples=200, batch_size=32)
        print(f"✓ Data loaders created: {len(self.train_loader)} train batches, {len(self.val_loader)} val batches")
    
    def demo_lr_schedulers(self):
        """Demonstrate different learning rate schedulers."""
        print("\n" + "="*60)
        print("DEMO: Learning Rate Schedulers")
        print("="*60)
        
        # Create optimizer
        optimizer = optim.AdamW(self.model.parameters(), lr=1e-3)
        
        # Test different scheduler types
        scheduler_configs = [
            (LRSchedulerType.STEP, {"step_size": 20, "gamma": 0.5}),
            (LRSchedulerType.MULTI_STEP, {"milestones": [30, 60, 90], "gamma": 0.5}),
            (LRSchedulerType.EXPONENTIAL, {"decay_rate": 0.95}),
            (LRSchedulerType.COSINE, {"T_max": 100, "eta_min": 1e-6}),
            (LRSchedulerType.COSINE_WARM_RESTART, {"T_0": 20, "T_mult": 2, "eta_min": 1e-6}),
            (LRSchedulerType.LINEAR, {"T_max": 100, "min_lr": 1e-6}),
            (LRSchedulerType.POLYNOMIAL, {"T_max": 100, "power": 2.0, "min_lr": 1e-6}),
        ]
        
        for scheduler_type, params in scheduler_configs:
            print(f"\nTesting {scheduler_type.value} scheduler...")
            
            # Reset optimizer
            for param_group in optimizer.param_groups:
                param_group['lr'] = 1e-3
            
            # Create scheduler
            config = create_lr_scheduler_config(scheduler_type, 1e-3, **params)
            scheduler = LRScheduler(optimizer, config)
            
            # Simulate training steps
            lr_history = []
            for step in range(100):
                lr_history.append(optimizer.param_groups[0]['lr'])
                scheduler.step()
            
            # Plot LR schedule
            plt.figure(figsize=(8, 4))
            plt.plot(lr_history)
            plt.title(f'Learning Rate Schedule: {scheduler_type.value}')
            plt.xlabel('Step')
            plt.ylabel('Learning Rate')
            plt.yscale('log')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            
            print(f"  ✓ {scheduler_type.value} scheduler tested successfully")
    
    def demo_early_stopping(self):
        """Demonstrate early stopping functionality."""
        print("\n" + "="*60)
        print("DEMO: Early Stopping")
        print("="*60)
        
        # Create early stopping configurations
        early_stopping_configs = [
            ("Min Loss", EarlyStoppingMode.MIN, 15),
            ("Max PSNR", EarlyStoppingMode.MAX, 20),
        ]
        
        for name, mode, patience in early_stopping_configs:
            print(f"\nTesting {name} early stopping (patience: {patience})...")
            
            # Create configuration
            config = create_early_stopping_config(
                mode=mode,
                patience=patience,
                min_epochs=5,
                verbose=True
            )
            
            # Create early stopping instance
            early_stopping = EarlyStopping(config)
            
            # Simulate training with improving then degrading metric
            if mode == EarlyStoppingMode.MIN:
                # Simulate loss that decreases then increases
                metrics = [1.0, 0.8, 0.6, 0.4, 0.3, 0.25, 0.24, 0.23, 0.22, 0.21, 
                          0.20, 0.19, 0.18, 0.17, 0.16, 0.15, 0.15, 0.15, 0.15, 0.15]
            else:
                # Simulate PSNR that increases then plateaus
                metrics = [20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0, 34.0, 36.0, 38.0,
                          40.0, 42.0, 44.0, 46.0, 48.0, 50.0, 50.0, 50.0, 50.0, 50.0]
            
            # Test early stopping
            for epoch, metric in enumerate(metrics):
                should_stop = early_stopping(metric, epoch, self.model)
                print(f"  Epoch {epoch}: Metric = {metric:.3f}, Should Stop = {should_stop}")
                
                if should_stop:
                    print(f"  ✓ Early stopping triggered at epoch {epoch}")
                    break
            
            print(f"  Best score: {early_stopping.get_best_score():.3f}")
            print(f"  Best epoch: {early_stopping.get_best_epoch()}")
    
    def demo_training_integration(self):
        """Demonstrate integrated training with early stopping and LR scheduling."""
        print("\n" + "="*60)
        print("DEMO: Integrated Training")
        print("="*60)
        
        # Create training configuration
        training_config = create_training_config(
            epochs=50,
            early_stopping=True,
            lr_scheduling=True,
            early_stopping_config=create_early_stopping_config(
                mode=EarlyStoppingMode.MIN,
                patience=10,
                min_epochs=5
            ),
            lr_scheduler_config=create_lr_scheduler_config(
                LRSchedulerType.COSINE,
                initial_lr=1e-3,
                T_max=50,
                eta_min=1e-6
            )
        )
        
        print("Training configuration created:")
        print(f"  Epochs: {training_config.epochs}")
        print(f"  Early stopping: {training_config.early_stopping}")
        print(f"  LR scheduling: {training_config.lr_scheduling}")
        print(f"  Initial LR: {training_config.initial_lr}")
        
        print("✓ Training integration demo completed")
    
    def demo_performance_comparison(self):
        """Compare different configurations for performance."""
        print("\n" + "="*60)
        print("DEMO: Performance Comparison")
        print("="*60)
        
        # Test different configurations
        configs = [
            ("No Scheduling", False, False),
            ("LR Scheduling Only", False, True),
            ("Early Stopping Only", True, False),
            ("Both", True, True),
        ]
        
        for name, early_stop, lr_sched in configs:
            print(f"\nConfiguration: {name}")
            print(f"  Early Stopping: {early_stop}")
            print(f"  LR Scheduling: {lr_sched}")
            
            # Create configuration
            config = create_training_config(
                epochs=100,
                early_stopping=early_stop,
                lr_scheduling=lr_sched
            )
            
            print(f"  ✓ Configuration created successfully")
        
        print("\n✓ Performance comparison demo completed")
    
    def run_all_demos(self):
        """Run all demonstration functions."""
        print("🚀 Starting Early Stopping and Learning Rate Scheduling Demo")
        print("="*80)
        
        try:
            # Run all demos
            self.demo_lr_schedulers()
            self.demo_early_stopping()
            self.demo_training_integration()
            self.demo_performance_comparison()
            
            print("\n" + "="*80)
            print("🎉 All demos completed successfully!")
            print("="*80)
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function to run the demo."""
    print("Early Stopping and Learning Rate Scheduling System Demo")
    print("="*60)
    
    # Create and run demo
    demo = EarlyStoppingLRDemo()
    demo.run_all_demos()

if __name__ == "__main__":
    main()
