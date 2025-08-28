#!/usr/bin/env python3
"""
Refactored Advanced Gradient Accumulation System

Enhanced architecture with:
- Clean separation of concerns
- Improved performance optimizations
- Better error handling and logging
- Advanced memory management strategies
- Production-ready optimizations
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import GradScaler, autocast
import numpy as np
import logging
import time
import gc
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from collections import deque
import psutil
import threading
from contextlib import contextmanager
from abc import ABC, abstractmethod
import warnings
from pathlib import Path
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress warnings for production
warnings.filterwarnings("ignore", category=UserWarning)

@dataclass
class MemoryConfig:
    """Memory management configuration."""
    threshold_gpu: float = 0.8
    threshold_cpu: float = 0.9
    optimization_interval: int = 10
    snapshot_history: int = 1000
    enable_advanced_profiling: bool = True
    enable_auto_cleanup: bool = True

@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""
    enable_mixed_precision: bool = True
    enable_gradient_clipping: bool = True
    gradient_clip_norm: float = 1.0
    enable_adaptive_accumulation: bool = True
    enable_noise_injection: bool = False
    noise_scale: float = 1e-5
    enable_learning_rate_scheduling: bool = True
    enable_automatic_checkpointing: bool = True
    checkpoint_interval: int = 50

@dataclass
class AdvancedGradientConfig:
    """Refactored advanced configuration for gradient accumulation."""
    
    # Core parameters
    batch_size: int = 32
    effective_batch_size: int = 128
    gradient_accumulation_steps: int = 4
    
    # Memory configuration
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    
    # Performance configuration
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Advanced features
    enable_compile: bool = False
    enable_attention_slicing: bool = False
    enable_gradient_checkpointing: bool = False
    enable_cpu_offload: bool = False
    
    # Monitoring
    log_every: int = 10
    save_every: int = 100
    profile_interval: int = 5
    
    def __post_init__(self):
        """Validate and set default values."""
        if self.effective_batch_size % self.batch_size != 0:
            self.gradient_accumulation_steps = self.effective_batch_size // self.batch_size
        else:
            self.gradient_accumulation_steps = self.effective_batch_size // self.batch_size

class MemoryStrategy(ABC):
    """Abstract base class for memory management strategies."""
    
    @abstractmethod
    def optimize(self, device: torch.device) -> Dict[str, float]:
        """Optimize memory usage."""
        pass
    
    @abstractmethod
    def get_status(self, device: torch.device) -> Dict[str, float]:
        """Get current memory status."""
        pass

class GPUMemoryStrategy(MemoryStrategy):
    """GPU-specific memory optimization strategy."""
    
    def optimize(self, device: torch.device) -> Dict[str, float]:
        """Optimize GPU memory usage."""
        if device.type == 'cuda':
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        return self.get_status(device)
    
    def get_status(self, device: torch.device) -> Dict[str, float]:
        """Get GPU memory status."""
        if device.type == 'cuda':
            return {
                'allocated': torch.cuda.memory_allocated(device) / 1024**3,
                'reserved': torch.cuda.memory_reserved(device) / 1024**3,
                'max_allocated': torch.cuda.max_memory_allocated(device) / 1024**3,
                'utilization': torch.cuda.memory_allocated(device) / torch.cuda.get_device_properties(device).total_memory
            }
        return {}

class CPUMemoryStrategy(MemoryStrategy):
    """CPU-specific memory optimization strategy."""
    
    def optimize(self, device: torch.device) -> Dict[str, float]:
        """Optimize CPU memory usage."""
        gc.collect()
        return self.get_status(device)
    
    def get_status(self, device: torch.device) -> Dict[str, float]:
        """Get CPU memory status."""
        memory = psutil.virtual_memory()
        return {
            'used': memory.used / 1024**3,
            'available': memory.available / 1024**3,
            'percent': memory.percent / 100,
            'swap_used': psutil.swap_memory().used / 1024**3
        }

class HybridMemoryStrategy(MemoryStrategy):
    """Hybrid memory optimization strategy for both GPU and CPU."""
    
    def __init__(self):
        self.gpu_strategy = GPUMemoryStrategy()
        self.cpu_strategy = CPUMemoryStrategy()
    
    def optimize(self, device: torch.device) -> Dict[str, float]:
        """Optimize both GPU and CPU memory."""
        gpu_status = self.gpu_strategy.optimize(device)
        cpu_status = self.cpu_strategy.optimize(device)
        
        return {
            'gpu': gpu_status,
            'cpu': cpu_status,
            'timestamp': time.time()
        }
    
    def get_status(self, device: torch.device) -> Dict[str, float]:
        """Get hybrid memory status."""
        return {
            'gpu': self.gpu_strategy.get_status(device),
            'cpu': self.cpu_strategy.get_status(device),
            'timestamp': time.time()
        }

class AdvancedMemoryManager:
    """Refactored advanced memory manager with strategy pattern."""
    
    def __init__(self, device: torch.device, config: MemoryConfig):
        self.device = device
        self.config = config
        self.strategy = self._select_strategy()
        self.memory_history = deque(maxlen=config.snapshot_history)
        self.optimization_counter = 0
        
    def _select_strategy(self) -> MemoryStrategy:
        """Select appropriate memory strategy based on device."""
        if self.device.type == 'cuda':
            return HybridMemoryStrategy()
        else:
            return CPUMemoryStrategy()
    
    def take_snapshot(self, step: int, description: str = "") -> Dict[str, Any]:
        """Take comprehensive memory snapshot."""
        snapshot = {
            'step': step,
            'description': description,
            'timestamp': time.time(),
            'memory_status': self.strategy.get_status(self.device),
            'optimization_counter': self.optimization_counter
        }
        self.memory_history.append(snapshot)
        return snapshot
    
    def optimize_if_needed(self) -> bool:
        """Optimize memory if thresholds are exceeded."""
        status = self.strategy.get_status(self.device)
        
        should_optimize = False
        if self.device.type == 'cuda' and 'gpu' in status:
            gpu_status = status['gpu']
            if gpu_status.get('utilization', 0) > self.config.threshold_gpu:
                should_optimize = True
        
        if 'cpu' in status:
            cpu_status = status['cpu']
            if cpu_status.get('percent', 0) > self.config.threshold_cpu:
                should_optimize = True
        
        if should_optimize:
            self.strategy.optimize(self.device)
            self.optimization_counter += 1
            logger.info(f"Memory optimization performed (count: {self.optimization_counter})")
        
        return should_optimize
    
    def get_memory_recommendations(self) -> List[str]:
        """Get intelligent memory optimization recommendations."""
        recommendations = []
        
        if not self.memory_history:
            return recommendations
        
        latest = self.memory_history[-1]
        status = latest['memory_status']
        
        # GPU recommendations
        if 'gpu' in status and status['gpu']:
            gpu_status = status['gpu']
            if gpu_status.get('utilization', 0) > 0.8:
                recommendations.append("High GPU memory usage - consider reducing batch size")
            if gpu_status.get('allocated', 0) > 0.9 * gpu_status.get('reserved', 1):
                recommendations.append("GPU memory fragmentation detected - enable gradient checkpointing")
        
        # CPU recommendations
        if 'cpu' in status:
            cpu_status = status['cpu']
            if cpu_status.get('percent', 0) > 0.9:
                recommendations.append("Critical CPU memory usage - reduce data loading workers")
            if cpu_status.get('swap_used', 0) > 1.0:
                recommendations.append("High swap usage - optimize data pipeline")
        
        # Historical analysis
        if len(self.memory_history) > 10:
            recent_optimizations = [h['optimization_counter'] for h in list(self.memory_history)[-10:]]
            if max(recent_optimizations) - min(recent_optimizations) > 5:
                recommendations.append("Frequent memory optimizations - review batch size strategy")
        
        return recommendations

class GradientAccumulationStrategy(ABC):
    """Abstract base class for gradient accumulation strategies."""
    
    @abstractmethod
    def should_accumulate(self, current_step: int, target_steps: int) -> bool:
        """Determine if gradients should be accumulated."""
        pass
    
    @abstractmethod
    def adapt_steps(self, current_steps: int, memory_pressure: float) -> int:
        """Adapt accumulation steps based on conditions."""
        pass

class FixedAccumulationStrategy(GradientAccumulationStrategy):
    """Fixed gradient accumulation strategy."""
    
    def should_accumulate(self, current_step: int, target_steps: int) -> bool:
        """Fixed accumulation logic."""
        return (current_step + 1) % target_steps == 0
    
    def adapt_steps(self, current_steps: int, memory_pressure: float) -> int:
        """No adaptation for fixed strategy."""
        return current_steps

class AdaptiveAccumulationStrategy(GradientAccumulationStrategy):
    """Adaptive gradient accumulation strategy."""
    
    def __init__(self, min_steps: int = 1, max_steps: int = 32, threshold: float = 0.8):
        self.min_steps = min_steps
        self.max_steps = max_steps
        self.threshold = threshold
    
    def should_accumulate(self, current_step: int, target_steps: int) -> bool:
        """Adaptive accumulation logic."""
        return (current_step + 1) % target_steps == 0
    
    def adapt_steps(self, current_steps: int, memory_pressure: float) -> int:
        """Adapt steps based on memory pressure."""
        if memory_pressure > self.threshold:
            new_steps = min(current_steps * 2, self.max_steps)
            if new_steps != current_steps:
                logger.info(f"Adapting accumulation steps: {current_steps} -> {new_steps} (memory pressure)")
            return new_steps
        elif memory_pressure < self.threshold * 0.5:
            new_steps = max(current_steps // 2, self.min_steps)
            if new_steps != current_steps:
                logger.info(f"Adapting accumulation steps: {current_steps} -> {new_steps} (low memory usage)")
            return new_steps
        return current_steps

class RefactoredGradientAccumulator:
    """Refactored gradient accumulator with improved architecture."""
    
    def __init__(self, model: nn.Module, config: AdvancedGradientConfig, device: torch.device):
        self.model = model
        self.config = config
        self.device = device
        
        # Initialize components
        self.memory_manager = AdvancedMemoryManager(device, config.memory)
        self.accumulation_strategy = self._select_accumulation_strategy()
        
        # State management
        self.current_step = 0
        self.accumulation_steps = config.gradient_accumulation_steps
        self.performance_metrics = self._initialize_performance_tracking()
        
        # Mixed precision setup
        self.scaler = self._setup_mixed_precision()
        
        logger.info(f"Refactored gradient accumulator initialized:")
        logger.info(f"  - Device: {device}")
        logger.info(f"  - Accumulation strategy: {type(self.accumulation_strategy).__name__}")
        logger.info(f"  - Memory manager: {type(self.memory_manager).__name__}")
    
    def _select_accumulation_strategy(self) -> GradientAccumulationStrategy:
        """Select appropriate accumulation strategy."""
        if self.config.performance.enable_adaptive_accumulation:
            return AdaptiveAccumulationStrategy()
        else:
            return FixedAccumulationStrategy()
    
    def _setup_mixed_precision(self) -> Optional[GradScaler]:
        """Setup mixed precision training."""
        if (self.config.performance.enable_mixed_precision and 
            torch.cuda.is_available()):
            return GradScaler()
        return None
    
    def _initialize_performance_tracking(self) -> Dict[str, deque]:
        """Initialize performance tracking structures."""
        return {
            'step_times': deque(maxlen=100),
            'loss_history': deque(maxlen=1000),
            'gradient_norms': deque(maxlen=100),
            'memory_usage': deque(maxlen=100)
        }
    
    def step(self, optimizer: optim.Optimizer, loss: torch.Tensor, 
             scheduler=None, clip_gradients: bool = True) -> Dict[str, float]:
        """Perform gradient accumulation step with refactored logic."""
        start_time = time.time()
        
        # Memory snapshot
        self.memory_manager.take_snapshot(
            self.current_step, 
            f"Before backward pass - Loss: {loss.item():.4f}"
        )
        
        # Scale loss for accumulation
        scaled_loss = loss / self.accumulation_steps
        
        # Backward pass with mixed precision
        if self.scaler is not None:
            self.scaler.scale(scaled_loss).backward()
        else:
            scaled_loss.backward()
        
        # Gradient noise injection
        if self.config.performance.enable_noise_injection:
            self._inject_gradient_noise()
        
        # Track metrics
        self.performance_metrics['loss_history'].append(loss.item())
        
        # Gradient clipping
        if clip_gradients and self.config.performance.enable_gradient_clipping:
            grad_norm = self._clip_gradients(optimizer)
            self.performance_metrics['gradient_norms'].append(grad_norm)
        
        # Check if optimizer step should be performed
        if self.accumulation_strategy.should_accumulate(self.current_step, self.accumulation_steps):
            # Adapt accumulation steps if needed
            memory_status = self.memory_manager.strategy.get_status(self.device)
            if self.device.type == 'cuda' and 'gpu' in memory_status:
                memory_pressure = memory_status['gpu'].get('utilization', 0)
                self.accumulation_steps = self.accumulation_strategy.adapt_steps(
                    self.accumulation_steps, memory_pressure
                )
            
            # Optimizer step
            self._perform_optimizer_step(optimizer, scheduler)
            self.current_step = 0
        else:
            self.current_step += 1
        
        # Memory optimization
        if self.config.memory.enable_auto_cleanup:
            self.memory_manager.optimize_if_needed()
        
        # Final memory snapshot
        self.memory_manager.take_snapshot(
            self.current_step, 
            f"After optimizer step - Accumulation: {self.accumulation_steps}"
        )
        
        # Performance tracking
        step_time = time.time() - start_time
        self.performance_metrics['step_times'].append(step_time)
        
        return self._generate_step_metrics(loss, scaled_loss, step_time)
    
    def _inject_gradient_noise(self):
        """Inject noise into gradients for training stability."""
        for param in self.model.parameters():
            if param.grad is not None:
                noise = torch.randn_like(param.grad) * self.config.performance.noise_scale
                param.grad.add_(noise)
    
    def _clip_gradients(self, optimizer: optim.Optimizer) -> float:
        """Clip gradients with proper mixed precision handling."""
        if self.scaler is not None:
            self.scaler.unscale_(optimizer)
        
        grad_norm = torch.nn.utils.clip_grad_norm_(
            self.model.parameters(), 
            self.config.performance.gradient_clip_norm
        )
        
        return grad_norm.item()
    
    def _perform_optimizer_step(self, optimizer: optim.Optimizer, scheduler=None):
        """Perform optimizer step with proper mixed precision handling."""
        if self.scaler is not None:
            self.scaler.step(optimizer)
            self.scaler.update()
        else:
            optimizer.step()
        
        if scheduler is not None:
            scheduler.step()
        
        optimizer.zero_grad()
    
    def _generate_step_metrics(self, loss: torch.Tensor, scaled_loss: torch.Tensor, 
                              step_time: float) -> Dict[str, float]:
        """Generate comprehensive step metrics."""
        memory_status = self.memory_manager.strategy.get_status(self.device)
        
        return {
            'loss': loss.item(),
            'scaled_loss': scaled_loss.item(),
            'grad_norm': self.performance_metrics['gradient_norms'][-1] if self.performance_metrics['gradient_norms'] else 0.0,
            'step_time': step_time,
            'accumulation_steps': self.accumulation_steps,
            'memory_utilization': memory_status.get('gpu', {}).get('utilization', 0.0) if self.device.type == 'cuda' else 0.0
        }
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get comprehensive performance statistics."""
        if not self.performance_metrics['step_times']:
            return {}
        
        stats = {
            'avg_step_time': np.mean(self.performance_metrics['step_times']),
            'min_step_time': np.min(self.performance_metrics['step_times']),
            'max_step_time': np.max(self.performance_metrics['step_times']),
            'avg_loss': np.mean(self.performance_metrics['loss_history']) if self.performance_metrics['loss_history'] else 0.0,
            'avg_grad_norm': np.mean(self.performance_metrics['gradient_norms']) if self.performance_metrics['gradient_norms'] else 0.0,
            'accumulation_steps': self.accumulation_steps,
            'optimization_count': self.memory_manager.optimization_counter
        }
        
        return stats
    
    def get_memory_recommendations(self) -> List[str]:
        """Get memory optimization recommendations."""
        return self.memory_manager.get_memory_recommendations()

class RefactoredTrainer:
    """Refactored advanced trainer with improved architecture."""
    
    def __init__(self, model: nn.Module, config: AdvancedGradientConfig, 
                 optimizer: optim.Optimizer = None, scheduler = None):
        self.model = model
        self.config = config
        self.device = next(model.parameters()).device
        
        # Initialize components
        self.optimizer = optimizer or self._setup_optimizer()
        self.scheduler = scheduler or self._setup_scheduler()
        self.gradient_accumulator = RefactoredGradientAccumulator(model, config, self.device)
        
        # Training state
        self.training_history = []
        self.checkpoint_counter = 0
        self.last_checkpoint_step = 0
        
        # Model compilation
        if config.enable_compile and hasattr(torch, 'compile'):
            self._compile_model()
        
        logger.info(f"Refactored trainer initialized on {self.device}")
    
    def _setup_optimizer(self) -> optim.Optimizer:
        """Setup optimizer with advanced features."""
        if self.config.performance.enable_mixed_precision:
            try:
                import bitsandbytes as bnb
                return bnb.optim.AdamW8bit(
                    self.model.parameters(),
                    lr=1e-4,
                    weight_decay=0.01,
                    betas=(0.9, 0.999)
                )
            except ImportError:
                logger.warning("bitsandbytes not available, using standard AdamW")
        
        return optim.AdamW(
            self.model.parameters(),
            lr=1e-4,
            weight_decay=0.01,
            betas=(0.9, 0.999)
        )
    
    def _setup_scheduler(self):
        """Setup learning rate scheduler with advanced features."""
        if self.config.performance.enable_learning_rate_scheduling:
            from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
            return CosineAnnealingWarmRestarts(
                self.optimizer, 
                T_0=100, 
                T_mult=2,
                eta_min=1e-6
            )
        else:
            from torch.optim.lr_scheduler import CosineAnnealingLR
            return CosineAnnealingLR(self.optimizer, T_max=1000)
    
    def _compile_model(self):
        """Compile model for improved performance."""
        try:
            self.model = torch.compile(self.model)
            logger.info("Model compiled successfully")
        except Exception as e:
            logger.warning(f"Model compilation failed: {e}")
    
    def train_step(self, batch: torch.Tensor, targets: torch.Tensor = None) -> Dict[str, float]:
        """Single training step with refactored logic."""
        self.model.train()
        
        # Move data to device
        batch = batch.to(self.device)
        if targets is not None:
            targets = targets.to(self.device)
        
        # Forward pass with mixed precision
        loss = self._compute_loss(batch, targets)
        
        # Gradient accumulation step
        step_metrics = self.gradient_accumulator.step(
            self.optimizer, loss, self.scheduler
        )
        
        # Automatic checkpointing
        if self.config.performance.enable_automatic_checkpointing:
            self._check_automatic_checkpoint()
        
        # Logging and history
        if self.config.log_every > 0 and len(self.training_history) % self.config.log_every == 0:
            self._log_training_metrics(step_metrics)
        
        self.training_history.append(step_metrics)
        
        return step_metrics
    
    def _compute_loss(self, batch: torch.Tensor, targets: torch.Tensor = None) -> torch.Tensor:
        """Compute loss with proper mixed precision handling."""
        if (self.config.performance.enable_mixed_precision and 
            torch.cuda.is_available() and self.gradient_accumulator.scaler is not None):
            with autocast():
                outputs = self.model(batch)
                if targets is not None:
                    loss = nn.functional.cross_entropy(outputs, targets)
                else:
                    loss = outputs.mean()
        else:
            outputs = self.model(batch)
            if targets is not None:
                loss = nn.functional.cross_entropy(outputs, targets)
            else:
                loss = outputs.mean()
        
        return loss
    
    def _check_automatic_checkpoint(self):
        """Check if automatic checkpoint should be saved."""
        if (len(self.training_history) - self.last_checkpoint_step >= 
            self.config.performance.checkpoint_interval):
            self.save_checkpoint(f"auto_checkpoint_step_{len(self.training_history)}.pt")
            self.last_checkpoint_step = len(self.training_history)
    
    def _log_training_metrics(self, metrics: Dict[str, float]):
        """Log training metrics with improved formatting."""
        logger.info(f"Step {len(self.training_history)}:")
        logger.info(f"  Loss: {metrics['loss']:.4f}")
        logger.info(f"  Grad Norm: {metrics['grad_norm']:.4f}")
        logger.info(f"  Step Time: {metrics['step_time']:.4f}s")
        logger.info(f"  Memory: {metrics['memory_utilization']:.2%}")
        logger.info(f"  Accumulation Steps: {metrics['accumulation_steps']}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        stats = self.gradient_accumulator.get_performance_stats()
        recommendations = self.gradient_accumulator.get_memory_recommendations()
        
        summary = {
            **stats,
            'recommendations': recommendations,
            'total_steps': len(self.training_history),
            'config': {
                'effective_batch_size': self.config.effective_batch_size,
                'adaptive_accumulation': self.config.performance.enable_adaptive_accumulation,
                'mixed_precision': self.config.performance.enable_mixed_precision,
                'memory_optimization_count': self.gradient_accumulator.memory_manager.optimization_counter
            }
        }
        
        return summary
    
    def save_checkpoint(self, path: str):
        """Save training checkpoint with improved structure."""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'gradient_accumulator_state': {
                'current_step': self.gradient_accumulator.current_step,
                'accumulation_steps': self.gradient_accumulator.accumulation_steps
            },
            'config': self.config,
            'training_history': self.training_history,
            'performance_stats': self.get_performance_summary()
        }
        
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        torch.save(checkpoint, path)
        logger.info(f"Checkpoint saved to {path}")
    
    def load_checkpoint(self, path: str):
        """Load training checkpoint with error handling."""
        try:
            checkpoint = torch.load(path, map_location=self.device)
            
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            if checkpoint['scheduler_state_dict'] and self.scheduler:
                self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
            
            # Restore gradient accumulator state
            acc_state = checkpoint['gradient_accumulator_state']
            self.gradient_accumulator.current_step = acc_state['current_step']
            self.gradient_accumulator.accumulation_steps = acc_state['accumulation_steps']
            
            self.training_history = checkpoint.get('training_history', [])
            logger.info(f"Checkpoint loaded from {path}")
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint from {path}: {e}")
            raise

@contextmanager
def refactored_gradient_accumulation_context(model: nn.Module, config: AdvancedGradientConfig):
    """Context manager for refactored gradient accumulation training."""
    trainer = RefactoredTrainer(model, config)
    try:
        yield trainer
    finally:
        # Cleanup
        if hasattr(trainer, 'gradient_accumulator'):
            trainer.gradient_accumulator.memory_manager.strategy.optimize(trainer.device)

def create_refactored_config(
    batch_size: int = 32,
    effective_batch_size: int = 128,
    adaptive: bool = True,
    mixed_precision: bool = True,
    memory_efficient: bool = True,
    advanced_features: bool = True
) -> AdvancedGradientConfig:
    """Create refactored gradient accumulation configuration."""
    
    memory_config = MemoryConfig(
        threshold_gpu=0.8 if memory_efficient else 0.9,
        threshold_cpu=0.9 if memory_efficient else 0.95,
        enable_advanced_profiling=advanced_features,
        enable_auto_cleanup=memory_efficient
    )
    
    performance_config = PerformanceConfig(
        enable_mixed_precision=mixed_precision,
        enable_adaptive_accumulation=adaptive,
        enable_noise_injection=advanced_features,
        enable_learning_rate_scheduling=advanced_features,
        enable_automatic_checkpointing=advanced_features
    )
    
    return AdvancedGradientConfig(
        batch_size=batch_size,
        effective_batch_size=effective_batch_size,
        gradient_accumulation_steps=effective_batch_size // batch_size,
        memory=memory_config,
        performance=performance_config,
        enable_compile=False,  # Disabled by default for compatibility
        log_every=10,
        profile_interval=5
    )

def create_experimental_refactored_config(
    batch_size: int = 16,
    effective_batch_size: int = 256,
    noise_scale: float = 1e-4
) -> AdvancedGradientConfig:
    """Create experimental refactored configuration with all advanced features."""
    
    memory_config = MemoryConfig(
        threshold_gpu=0.75,
        threshold_cpu=0.85,
        enable_advanced_profiling=True,
        enable_auto_cleanup=True
    )
    
    performance_config = PerformanceConfig(
        enable_mixed_precision=True,
        enable_adaptive_accumulation=True,
        enable_noise_injection=True,
        noise_scale=noise_scale,
        enable_learning_rate_scheduling=True,
        enable_automatic_checkpointing=True,
        checkpoint_interval=25
    )
    
    return AdvancedGradientConfig(
        batch_size=batch_size,
        effective_batch_size=effective_batch_size,
        gradient_accumulation_steps=effective_batch_size // batch_size,
        memory=memory_config,
        performance=performance_config,
        log_every=5,
        profile_interval=3
    )

# Example usage
if __name__ == "__main__":
    # Create a simple model for demonstration
    model = nn.Sequential(
        nn.Linear(100, 50),
        nn.ReLU(),
        nn.Linear(50, 10)
    )
    
    # Create refactored configuration
    config = create_refactored_config(
        batch_size=8,
        effective_batch_size=64,
        adaptive=True,
        mixed_precision=True
    )
    
    # Train with refactored gradient accumulation
    with refactored_gradient_accumulation_context(model, config) as trainer:
        # Simulate training
        for step in range(100):
            batch = torch.randn(8, 100)
            targets = torch.randint(0, 10, (8,))
            
            metrics = trainer.train_step(batch, targets)
            
            if step % 20 == 0:
                print(f"Step {step}: Loss = {metrics['loss']:.4f}, "
                      f"Memory = {metrics['memory_utilization']:.2%}")
        
        # Get performance summary
        summary = trainer.get_performance_summary()
        print("\nPerformance Summary:")
        for key, value in summary.items():
            if key != 'recommendations':
                print(f"  {key}: {value}")
        
        if summary['recommendations']:
            print("\nRecommendations:")
            for rec in summary['recommendations']:
                print(f"  - {rec}")
