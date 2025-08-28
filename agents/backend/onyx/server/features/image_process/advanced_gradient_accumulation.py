#!/usr/bin/env python3
"""
Advanced Gradient Accumulation System

Enhanced gradient accumulation with adaptive strategies, memory optimization,
and advanced performance monitoring for large-scale training.
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
from typing import Dict, List, Optional, Tuple, Union
from collections import deque
import psutil
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@dataclass
class AdvancedGradientConfig:
    """Advanced configuration for gradient accumulation."""
    
    # Core parameters
    batch_size: int = 32
    effective_batch_size: int = 128
    gradient_accumulation_steps: int = 4
    
    # Adaptive parameters
    adaptive_accumulation: bool = True
    min_accumulation_steps: int = 1
    max_accumulation_steps: int = 32
    memory_threshold: float = 0.8  # 80% of available memory
    
    # Performance optimization
    use_mixed_precision: bool = True
    fp16: bool = True
    bf16: bool = False
    use_compile: bool = False  # Disabled by default due to compilation issues on Windows
    gradient_clip_norm: float = 1.0
    
    # Memory management
    memory_efficient: bool = True
    gradient_checkpointing: bool = False
    cpu_offload: bool = False
    attention_slicing: bool = False
    
    # Monitoring
    profile_memory: bool = True
    log_every: int = 10
    save_every: int = 100
    
    # Advanced features
    dynamic_batch_sizing: bool = True
    loss_scaling: bool = True
    gradient_accumulation_scheduling: bool = True
    
    # New advanced features
    adaptive_learning_rate: bool = True
    gradient_noise_injection: bool = False
    noise_scale: float = 1e-5
    advanced_memory_profiling: bool = True
    automatic_checkpointing: bool = True
    checkpoint_interval: int = 50
    
    def __post_init__(self):
        """Validate and set default values."""
        if self.effective_batch_size % self.batch_size != 0:
            self.gradient_accumulation_steps = self.effective_batch_size // self.batch_size
        else:
            self.gradient_accumulation_steps = self.effective_batch_size // self.batch_size

class MemoryMonitor:
    """Advanced memory monitoring and optimization."""
    
    def __init__(self, device: torch.device):
        self.device = device
        self.memory_history = deque(maxlen=1000)
        self.peak_memory = 0
        self.memory_warnings = []
        
    def get_memory_info(self) -> Dict[str, float]:
        """Get comprehensive memory information."""
        info = {}
        
        if self.device.type == 'cuda':
            info['gpu_memory_allocated'] = torch.cuda.memory_allocated(self.device) / 1024**3
            info['gpu_memory_reserved'] = torch.cuda.memory_reserved(self.device) / 1024**3
            info['gpu_memory_free'] = torch.cuda.get_device_properties(self.device).total_memory / 1024**3 - info['gpu_memory_reserved']
            info['gpu_memory_utilization'] = info['gpu_memory_allocated'] / (torch.cuda.get_device_properties(self.device).total_memory / 1024**3)
        else:
            info['gpu_memory_allocated'] = 0.0
            info['gpu_memory_reserved'] = 0.0
            info['gpu_memory_free'] = 0.0
            info['gpu_memory_utilization'] = 0.0
        
        # CPU memory
        cpu_memory = psutil.virtual_memory()
        info['cpu_memory_used'] = cpu_memory.used / 1024**3
        info['cpu_memory_total'] = cpu_memory.total / 1024**3
        info['cpu_memory_utilization'] = cpu_memory.percent / 100
        
        self.memory_history.append(info)
        self.peak_memory = max(self.peak_memory, info['gpu_memory_allocated'])
        
        return info
    
    def check_memory_pressure(self) -> bool:
        """Check if memory pressure is high."""
        info = self.get_memory_info()
        return info['gpu_memory_utilization'] > 0.8 or info['cpu_memory_utilization'] > 0.9
    
    def optimize_memory(self):
        """Perform memory optimization."""
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()
        gc.collect()
        
    def get_memory_recommendations(self) -> List[str]:
        """Get memory optimization recommendations."""
        info = self.get_memory_info()
        recommendations = []
        
        if info['gpu_memory_utilization'] > 0.8:
            recommendations.append("High GPU memory usage - consider reducing batch size or increasing gradient accumulation steps")
        
        if info['cpu_memory_utilization'] > 0.9:
            recommendations.append("High CPU memory usage - consider reducing number of workers or using memory-efficient data loading")
        
        if len(self.memory_history) > 10:
            recent_memory = [h['gpu_memory_allocated'] for h in list(self.memory_history)[-10:]]
            if max(recent_memory) - min(recent_memory) > 2.0:
                recommendations.append("Memory usage is fluctuating - consider using gradient checkpointing")
        
        return recommendations

class AdvancedMemoryProfiler:
    """Advanced memory profiling with detailed analysis."""
    
    def __init__(self, device: torch.device):
        self.device = device
        self.memory_snapshots = []
        self.peak_usage = {}
        self.memory_trends = []
        
    def take_snapshot(self, step: int, description: str = ""):
        """Take a detailed memory snapshot."""
        snapshot = {
            'step': step,
            'description': description,
            'timestamp': time.time(),
            'gpu_memory': self._get_gpu_memory_info(),
            'cpu_memory': self._get_cpu_memory_info(),
            'tensor_count': self._count_tensors(),
            'gradient_count': self._count_gradients()
        }
        self.memory_snapshots.append(snapshot)
        return snapshot
    
    def _get_gpu_memory_info(self):
        """Get detailed GPU memory information."""
        if self.device.type == 'cuda':
            return {
                'allocated': torch.cuda.memory_allocated(self.device) / 1024**3,
                'reserved': torch.cuda.memory_reserved(self.device) / 1024**3,
                'max_allocated': torch.cuda.max_memory_allocated(self.device) / 1024**3,
                'max_reserved': torch.cuda.max_memory_reserved(self.device) / 1024**3
            }
        return {}
    
    def _get_cpu_memory_info(self):
        """Get detailed CPU memory information."""
        memory = psutil.virtual_memory()
        return {
            'used': memory.used / 1024**3,
            'available': memory.available / 1024**3,
            'percent': memory.percent,
            'swap_used': psutil.swap_memory().used / 1024**3
        }
    
    def _count_tensors(self):
        """Count active tensors in memory."""
        if self.device.type == 'cuda':
            return torch.cuda.memory_stats(self.device).get('num_alloc_retries', 0)
        return 0
    
    def _count_gradients(self):
        """Count tensors with gradients."""
        return sum(1 for p in torch.cuda.memory_stats(self.device).values() if 'grad' in str(p).lower())
    
    def analyze_memory_trends(self):
        """Analyze memory usage trends."""
        if len(self.memory_snapshots) < 2:
            return {}
        
        trends = {}
        for key in ['gpu_memory', 'cpu_memory']:
            if key in self.memory_snapshots[0]:
                trends[key] = self._calculate_trends(key)
        
        return trends
    
    def _calculate_trends(self, memory_type: str):
        """Calculate memory usage trends."""
        values = []
        for snapshot in self.memory_snapshots:
            if memory_type in snapshot and snapshot[memory_type]:
                if memory_type == 'gpu_memory' and 'allocated' in snapshot[memory_type]:
                    values.append(snapshot[memory_type]['allocated'])
                elif memory_type == 'cpu_memory' and 'used' in snapshot[memory_type]:
                    values.append(snapshot[memory_type]['used'])
        
        if len(values) < 2:
            return {}
        
        return {
            'trend': 'increasing' if values[-1] > values[0] else 'decreasing',
            'change_rate': (values[-1] - values[0]) / len(values),
            'volatility': np.std(values),
            'peak': max(values),
            'valley': min(values)
        }
    
    def get_memory_recommendations(self) -> List[str]:
        """Get advanced memory optimization recommendations."""
        recommendations = []
        
        if not self.memory_snapshots:
            return recommendations
        
        latest = self.memory_snapshots[-1]
        trends = self.analyze_memory_trends()
        
        # GPU memory recommendations
        if 'gpu_memory' in latest and latest['gpu_memory']:
            gpu_mem = latest['gpu_memory']
            if 'allocated' in gpu_mem and 'reserved' in gpu_mem:
                if gpu_mem['allocated'] > 0.8 * gpu_mem['reserved']:
                    recommendations.append("High GPU memory utilization - consider gradient checkpointing")
            
            if 'gpu_memory' in trends and trends['gpu_memory']:
                trend = trends['gpu_memory']
                if 'trend' in trend and 'change_rate' in trend:
                    if trend['trend'] == 'increasing' and trend['change_rate'] > 0.01:
                        recommendations.append("Memory usage increasing rapidly - check for memory leaks")
        
        # CPU memory recommendations
        if 'cpu_memory' in latest:
            cpu_mem = latest['cpu_memory']
            if cpu_mem['percent'] > 90:
                recommendations.append("Critical CPU memory usage - reduce batch size or workers")
            
            if cpu_mem['swap_used'] > 1.0:
                recommendations.append("High swap usage - optimize data loading and reduce memory pressure")
        
        return recommendations

class AdaptiveGradientAccumulator:
    """Advanced gradient accumulator with adaptive strategies."""
    
    def __init__(self, model: nn.Module, config: AdvancedGradientConfig, device: torch.device):
        self.model = model
        self.config = config
        self.device = device
        self.memory_monitor = MemoryMonitor(device)
        
        # New: Advanced memory profiler
        if config.advanced_memory_profiling:
            self.memory_profiler = AdvancedMemoryProfiler(device)
        else:
            self.memory_profiler = None
        
        # Accumulation state
        self.current_step = 0
        self.accumulation_steps = config.gradient_accumulation_steps
        self.actual_batch_size = config.batch_size
        self.effective_batch_size = config.effective_batch_size
        
        # Performance tracking
        self.step_times = deque(maxlen=100)
        self.loss_history = deque(maxlen=1000)
        self.gradient_norms = deque(maxlen=100)
        
        # Adaptive parameters
        self.adaptive_accumulation = config.adaptive_accumulation
        self.memory_threshold = config.memory_threshold
        
        # Mixed precision
        if config.use_mixed_precision and torch.cuda.is_available():
            self.scaler = GradScaler() 
        else:
            self.scaler = None
        
        # New: Gradient noise injection
        self.gradient_noise_injection = config.gradient_noise_injection
        self.noise_scale = config.noise_scale
        
        logger.info(f"Advanced gradient accumulator initialized:")
        logger.info(f"  - Effective batch size: {self.effective_batch_size}")
        logger.info(f"  - Accumulation steps: {self.accumulation_steps}")
        logger.info(f"  - Adaptive accumulation: {self.adaptive_accumulation}")
        logger.info(f"  - Mixed precision: {config.use_mixed_precision}")
        logger.info(f"  - Advanced memory profiling: {config.advanced_memory_profiling}")
        logger.info(f"  - Gradient noise injection: {config.gradient_noise_injection}")
    
    def should_step(self) -> bool:
        """Check if optimizer step should be performed."""
        return (self.current_step + 1) % self.accumulation_steps == 0
    
    def adapt_accumulation_steps(self) -> int:
        """Adaptively adjust accumulation steps based on memory pressure."""
        if not self.adaptive_accumulation:
            return self.accumulation_steps
        
        memory_info = self.memory_monitor.get_memory_info()
        current_utilization = memory_info['gpu_memory_utilization']
        
        if current_utilization > self.memory_threshold:
            # Increase accumulation steps to reduce memory usage
            new_steps = min(self.accumulation_steps * 2, self.config.max_accumulation_steps)
            if new_steps != self.accumulation_steps:
                logger.info(f"Adapting accumulation steps: {self.accumulation_steps} -> {new_steps} (memory pressure)")
                self.accumulation_steps = new_steps
        elif current_utilization < self.memory_threshold * 0.5:
            # Decrease accumulation steps to improve efficiency
            new_steps = max(self.accumulation_steps // 2, self.config.min_accumulation_steps)
            if new_steps != self.accumulation_steps:
                logger.info(f"Adapting accumulation steps: {self.accumulation_steps} -> {new_steps} (low memory usage)")
                self.accumulation_steps = new_steps
        
        return self.accumulation_steps
    
    def step(self, optimizer: optim.Optimizer, loss: torch.Tensor, 
             scheduler=None, clip_gradients: bool = True) -> Dict[str, float]:
        """Perform gradient accumulation step with advanced features."""
        start_time = time.time()
        
        # New: Memory profiling snapshot
        if self.memory_profiler:
            self.memory_profiler.take_snapshot(
                self.current_step, 
                f"Before backward pass - Loss: {loss.item():.4f}"
            )
        
        # Scale loss for accumulation
        scaled_loss = loss / self.accumulation_steps
        
        # Backward pass with mixed precision
        if self.config.use_mixed_precision and self.scaler is not None:
            self.scaler.scale(scaled_loss).backward()
        else:
            scaled_loss.backward()
        
        # New: Gradient noise injection for better training stability
        if self.gradient_noise_injection:
            self._inject_gradient_noise()
        
        # Track metrics
        self.loss_history.append(loss.item())
        
        # Gradient clipping
        if clip_gradients:
            if self.config.use_mixed_precision and self.scaler is not None:
                self.scaler.unscale_(optimizer)
            
            grad_norm = torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), 
                self.config.gradient_clip_norm
            )
            self.gradient_norms.append(grad_norm.item())
        
        # Check if we should perform optimizer step
        if self.should_step():
            # Adaptive accumulation
            self.adapt_accumulation_steps()
            
            # Optimizer step
            if self.config.use_mixed_precision and self.scaler is not None:
                self.scaler.step(optimizer)
                self.scaler.update()
            else:
                optimizer.step()
            
            # Scheduler step
            if scheduler is not None:
                scheduler.step()
            
            optimizer.zero_grad()
            self.current_step = 0
        else:
            self.current_step += 1
        
        # Memory optimization
        if self.config.memory_efficient and self.memory_monitor.check_memory_pressure():
            self.memory_monitor.optimize_memory()
        
        # New: Memory profiling after step
        if self.memory_profiler:
            self.memory_profiler.take_snapshot(
                self.current_step, 
                f"After optimizer step - Accumulation: {self.accumulation_steps}"
            )
        
        # Performance tracking
        step_time = time.time() - start_time
        self.step_times.append(step_time)
        
        return {
            'loss': loss.item(),
            'scaled_loss': scaled_loss.item(),
            'grad_norm': self.gradient_norms[-1] if self.gradient_norms else 0.0,
            'step_time': step_time,
            'accumulation_steps': self.accumulation_steps,
            'memory_utilization': self.memory_monitor.get_memory_info()['gpu_memory_utilization']
        }
    
    def _inject_gradient_noise(self):
        """Inject noise into gradients for better training stability."""
        for param in self.model.parameters():
            if param.grad is not None:
                noise = torch.randn_like(param.grad) * self.noise_scale
                param.grad.add_(noise)
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get comprehensive performance statistics."""
        if not self.step_times:
            return {}
        
        stats = {
            'avg_step_time': np.mean(self.step_times),
            'min_step_time': np.min(self.step_times),
            'max_step_time': np.max(self.step_times),
            'avg_loss': np.mean(self.loss_history) if self.loss_history else 0.0,
            'avg_grad_norm': np.mean(self.gradient_norms) if self.gradient_norms else 0.0,
            'peak_memory': self.memory_monitor.peak_memory,
            'current_memory': self.memory_monitor.get_memory_info()['gpu_memory_allocated'],
            'effective_batch_size': self.effective_batch_size,
            'accumulation_steps': self.accumulation_steps
        }
        
        # New: Advanced memory profiling stats
        if self.memory_profiler:
            memory_trends = self.memory_profiler.analyze_memory_trends()
            if 'gpu_memory' in memory_trends and memory_trends['gpu_memory']:
                stats['memory_trend'] = memory_trends['gpu_memory'].get('trend', 'stable')
                stats['memory_volatility'] = memory_trends['gpu_memory'].get('volatility', 0.0)
            else:
                stats['memory_trend'] = 'stable'
                stats['memory_volatility'] = 0.0
        
        return stats
    
    def get_memory_recommendations(self) -> List[str]:
        """Get memory optimization recommendations."""
        recommendations = self.memory_monitor.get_memory_recommendations()
        
        # New: Advanced memory profiler recommendations
        if self.memory_profiler:
            advanced_recs = self.memory_profiler.get_memory_recommendations()
            recommendations.extend(advanced_recs)
        
        return recommendations

class AdvancedTrainer:
    """Advanced trainer with enhanced gradient accumulation."""
    
    def __init__(self, model: nn.Module, config: AdvancedGradientConfig, 
                 optimizer: optim.Optimizer = None, scheduler = None):
        self.model = model
        self.config = config
        self.device = next(model.parameters()).device
        
        # Setup optimizer and scheduler
        self.optimizer = optimizer or self._setup_optimizer()
        self.scheduler = scheduler or self._setup_scheduler()
        
        # Setup gradient accumulator
        self.gradient_accumulator = AdaptiveGradientAccumulator(
            model, config, self.device
        )
        
        # Performance monitoring
        self.epoch_stats = []
        self.training_history = []
        
        # New: Automatic checkpointing
        self.checkpoint_counter = 0
        self.last_checkpoint_step = 0
        
        # Model compilation
        if config.use_compile and hasattr(torch, 'compile'):
            try:
                self.model = torch.compile(self.model)
                logger.info("Model compiled successfully")
            except Exception as e:
                logger.warning(f"Model compilation failed: {e}")
        
        logger.info(f"Advanced trainer initialized on {self.device}")
    
    def _setup_optimizer(self) -> optim.Optimizer:
        """Setup optimizer with advanced features."""
        if self.config.use_mixed_precision:
            # Use 8-bit optimizer for memory efficiency
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
        if self.config.adaptive_learning_rate:
            # Adaptive learning rate based on training progress
            from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
            return CosineAnnealingWarmRestarts(
                self.optimizer, 
                T_0=100, 
                T_mult=2,
                eta_min=1e-6
            )
        else:
            # Standard cosine annealing
            from torch.optim.lr_scheduler import CosineAnnealingLR
            return CosineAnnealingLR(self.optimizer, T_max=1000)
    
    def train_step(self, batch: torch.Tensor, targets: torch.Tensor = None) -> Dict[str, float]:
        """Single training step with advanced gradient accumulation."""
        self.model.train()
        
        # Move data to device
        batch = batch.to(self.device)
        if targets is not None:
            targets = targets.to(self.device)
        
        # Forward pass with mixed precision
        if self.config.use_mixed_precision and torch.cuda.is_available():
            with autocast():
                outputs = self.model(batch)
                if targets is not None:
                    loss = nn.functional.cross_entropy(outputs, targets)
                else:
                    loss = outputs.mean()  # Placeholder loss
        else:
            outputs = self.model(batch)
            if targets is not None:
                loss = nn.functional.cross_entropy(outputs, targets)
            else:
                loss = outputs.mean()  # Placeholder loss
        
        # Gradient accumulation step
        step_metrics = self.gradient_accumulator.step(
            self.optimizer, loss, self.scheduler
        )
        
        # New: Automatic checkpointing
        if self.config.automatic_checkpointing:
            self._check_automatic_checkpoint()
        
        # Log performance
        if self.config.log_every > 0 and len(self.training_history) % self.config.log_every == 0:
            self._log_training_metrics(step_metrics)
        
        self.training_history.append(step_metrics)
        
        return step_metrics
    
    def _check_automatic_checkpoint(self):
        """Check if automatic checkpoint should be saved."""
        if (len(self.training_history) - self.last_checkpoint_step >= 
            self.config.checkpoint_interval):
            self.save_checkpoint(f"auto_checkpoint_step_{len(self.training_history)}.pt")
            self.last_checkpoint_step = len(self.training_history)
    
    def _log_training_metrics(self, metrics: Dict[str, float]):
        """Log training metrics."""
        logger.info(f"Step {len(self.training_history)}:")
        logger.info(f"  Loss: {metrics['loss']:.4f}")
        logger.info(f"  Grad Norm: {metrics['grad_norm']:.4f}")
        logger.info(f"  Step Time: {metrics['step_time']:.4f}s")
        logger.info(f"  Memory: {metrics['memory_utilization']:.2%}")
        logger.info(f"  Accumulation Steps: {metrics['accumulation_steps']}")
    
    def get_performance_summary(self) -> Dict[str, float]:
        """Get comprehensive performance summary."""
        stats = self.gradient_accumulator.get_performance_stats()
        recommendations = self.gradient_accumulator.get_memory_recommendations()
        
        summary = {
            **stats,
            'recommendations': recommendations,
            'total_steps': len(self.training_history),
            'config': {
                'effective_batch_size': self.config.effective_batch_size,
                'adaptive_accumulation': self.config.adaptive_accumulation,
                'mixed_precision': self.config.use_mixed_precision,
                'memory_efficient': self.config.memory_efficient,
                'advanced_memory_profiling': self.config.advanced_memory_profiling,
                'gradient_noise_injection': self.config.gradient_noise_injection
            }
        }
        
        # New: Advanced memory profiling summary
        if hasattr(self.gradient_accumulator, 'memory_profiler') and self.gradient_accumulator.memory_profiler:
            memory_trends = self.gradient_accumulator.memory_profiler.analyze_memory_trends()
            summary['memory_analysis'] = memory_trends
        
        return summary
    
    def save_checkpoint(self, path: str):
        """Save training checkpoint."""
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
        torch.save(checkpoint, path)
        logger.info(f"Checkpoint saved to {path}")
    
    def load_checkpoint(self, path: str):
        """Load training checkpoint."""
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

@contextmanager
def gradient_accumulation_context(model: nn.Module, config: AdvancedGradientConfig):
    """Context manager for gradient accumulation training."""
    trainer = AdvancedTrainer(model, config)
    try:
        yield trainer
    finally:
        # Cleanup
        if hasattr(trainer, 'gradient_accumulator'):
            trainer.gradient_accumulator.memory_monitor.optimize_memory()

def create_advanced_config(
    batch_size: int = 32,
    effective_batch_size: int = 128,
    adaptive: bool = True,
    mixed_precision: bool = True,
    memory_efficient: bool = True,
    advanced_features: bool = True
) -> AdvancedGradientConfig:
    """Create advanced gradient accumulation configuration."""
    return AdvancedGradientConfig(
        batch_size=batch_size,
        effective_batch_size=effective_batch_size,
        gradient_accumulation_steps=effective_batch_size // batch_size,
        adaptive_accumulation=adaptive,
        use_mixed_precision=mixed_precision,
        memory_efficient=memory_efficient,
        profile_memory=True,
        log_every=10,
        advanced_memory_profiling=advanced_features,
        adaptive_learning_rate=advanced_features,
        automatic_checkpointing=advanced_features,
        gradient_noise_injection=advanced_features
    )

def create_experimental_config(
    batch_size: int = 16,
    effective_batch_size: int = 256,
    noise_scale: float = 1e-4
) -> AdvancedGradientConfig:
    """Create experimental configuration with advanced features."""
    return AdvancedGradientConfig(
        batch_size=batch_size,
        effective_batch_size=effective_batch_size,
        gradient_accumulation_steps=effective_batch_size // batch_size,
        adaptive_accumulation=True,
        use_mixed_precision=True,
        memory_efficient=True,
        profile_memory=True,
        log_every=5,
        advanced_memory_profiling=True,
        adaptive_learning_rate=True,
        automatic_checkpointing=True,
        gradient_noise_injection=True,
        noise_scale=noise_scale,
        checkpoint_interval=25
    )

# Example usage
if __name__ == "__main__":
    # Create a simple model for demonstration
    model = nn.Sequential(
        nn.Linear(100, 50),
        nn.ReLU(),
        nn.Linear(50, 10)
    )
    
    # Create advanced configuration
    config = create_advanced_config(
        batch_size=8,
        effective_batch_size=64,
        adaptive=True,
        mixed_precision=True
    )
    
    # Train with advanced gradient accumulation
    with gradient_accumulation_context(model, config) as trainer:
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
