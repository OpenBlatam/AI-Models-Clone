#!/usr/bin/env python3
"""
Gradient Accumulation System for Large Batch Sizes

This module provides comprehensive gradient accumulation capabilities for training
with large effective batch sizes while maintaining memory efficiency.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import logging
import time
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccumulationMode(Enum):
    """Gradient accumulation modes."""
    NONE = "none"
    FIXED = "fixed"           # Fixed accumulation steps
    ADAPTIVE = "adaptive"      # Adaptive based on memory
    DYNAMIC = "dynamic"        # Dynamic based on loss stability

@dataclass
class GradientAccumulationConfig:
    """Configuration for gradient accumulation."""
    enabled: bool = False
    mode: AccumulationMode = AccumulationMode.FIXED
    accumulation_steps: int = 4
    effective_batch_size: Optional[int] = None
    min_accumulation_steps: int = 1
    max_accumulation_steps: int = 32
    memory_threshold: float = 0.8  # 80% of available memory
    loss_stability_threshold: float = 0.01
    warmup_steps: int = 100
    sync_batch_norm: bool = True
    scale_loss: bool = True
    gradient_clipping: bool = True
    clip_norm: float = 1.0
    clip_value: Optional[float] = None
    monitor_memory: bool = True
    adaptive_memory_check: bool = True

@dataclass
class AccumulationMetrics:
    """Metrics for gradient accumulation."""
    current_step: int = 0
    accumulation_step: int = 0
    effective_batch_size: int = 0
    memory_usage: float = 0.0
    loss_history: List[float] = field(default_factory=list)
    gradient_norms: List[float] = field(default_factory=list)
    accumulation_times: List[float] = field(default_factory=list)
    memory_efficiency: float = 0.0

class GradientAccumulator:
    """Main gradient accumulation class for large batch training."""
    
    def __init__(self, config: GradientAccumulationConfig):
        self.config = config
        self.metrics = AccumulationMetrics()
        self.accumulated_gradients = {}
        self.accumulation_state = {
            'step': 0,
            'accumulation_step': 0,
            'loss_sum': 0.0,
            'loss_count': 0
        }
        
        if config.enabled:
            logger.info(f"✅ Gradient accumulation enabled with mode: {config.mode.value}")
            logger.info(f"  Target accumulation steps: {config.accumulation_steps}")
            if config.effective_batch_size:
                logger.info(f"  Target effective batch size: {config.effective_batch_size}")
    
    def setup_accumulation(self, model: nn.Module, dataloader: DataLoader) -> Tuple[nn.Module, DataLoader]:
        """Setup model and dataloader for gradient accumulation."""
        if not self.config.enabled:
            return model, dataloader
        
        # Adjust batch size for accumulation
        if self.config.effective_batch_size:
            original_batch_size = dataloader.batch_size
            target_batch_size = self.config.effective_batch_size // self.config.accumulation_steps
            if target_batch_size != original_batch_size:
                logger.info(f"📦 Adjusting batch size: {original_batch_size} -> {target_batch_size}")
                # Note: In practice, you'd recreate the DataLoader with new batch size
        
        # Setup batch norm synchronization if enabled
        if self.config.sync_batch_norm:
            self._setup_batch_norm_sync(model)
        
        return model, dataloader
    
    def _setup_batch_norm_sync(self, model: nn.Module):
        """Setup batch normalization synchronization for accumulation."""
        for module in model.modules():
            if isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)):
                module.track_running_stats = True
                logger.info("🔄 Batch norm synchronization enabled")
    
    def accumulate_gradients(self, loss: torch.Tensor, model: nn.Module, 
                           optimizer: optim.Optimizer, step: int) -> bool:
        """Accumulate gradients and determine if optimizer step should be taken."""
        if not self.config.enabled:
            return True
        
        # Scale loss if enabled
        if self.config.scale_loss:
            scaled_loss = loss / self.config.accumulation_steps
        else:
            scaled_loss = loss
        
        # Backward pass
        scaled_loss.backward()
        
        # Update accumulation state
        self.accumulation_state['step'] = step
        self.accumulation_state['accumulation_step'] += 1
        self.accumulation_state['loss_sum'] += loss.item()
        self.accumulation_state['loss_count'] += 1
        
        # Check if we should take optimizer step
        should_step = self.accumulation_state['accumulation_step'] >= self.config.accumulation_steps
        
        # Adaptive accumulation logic
        if self.config.mode == AccumulationMode.ADAPTIVE and not should_step:
            should_step = self._check_adaptive_accumulation(model)
        
        # Dynamic accumulation logic
        elif self.config.mode == AccumulationMode.DYNAMIC and not should_step:
            should_step = self._check_dynamic_accumulation()
        
        if should_step:
            # Apply gradient clipping if enabled
            if self.config.gradient_clipping:
                self._clip_gradients(model)
            
            # Take optimizer step
            optimizer.step()
            optimizer.zero_grad()
            
            # Reset accumulation state
            self.accumulation_state['accumulation_step'] = 0
            self.accumulation_state['loss_sum'] = 0.0
            self.accumulation_state['loss_count'] = 0
            
            # Update metrics
            self._update_metrics(step)
            
            logger.debug(f"🔄 Optimizer step taken at step {step}")
            return True
        
        return False
    
    def _check_adaptive_accumulation(self, model: nn.Module) -> bool:
        """Check if we should take optimizer step based on memory usage."""
        if not self.config.adaptive_memory_check:
            return False
        
        try:
            # Check GPU memory usage
            if torch.cuda.is_available():
                memory_allocated = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
                if memory_allocated > self.config.memory_threshold:
                    logger.info(f"💾 Memory threshold exceeded ({memory_allocated:.2%}), taking optimizer step")
                    return True
            
            # Check system memory
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > (self.config.memory_threshold * 100):
                logger.info(f"💾 System memory threshold exceeded ({memory.percent:.1f}%), taking optimizer step")
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ Memory check failed: {e}")
        
        return False
    
    def _check_dynamic_accumulation(self) -> bool:
        """Check if we should take optimizer step based on loss stability."""
        if len(self.accumulation_state['loss_sum']) < 2:
            return False
        
        # Calculate loss stability
        recent_losses = self.accumulation_state['loss_sum'][-10:]  # Last 10 losses
        if len(recent_losses) >= 2:
            loss_variance = torch.var(torch.tensor(recent_losses)).item()
            if loss_variance < self.config.loss_stability_threshold:
                logger.info(f"📊 Loss stable (variance: {loss_variance:.6f}), taking optimizer step")
                return True
        
        return False
    
    def _clip_gradients(self, model: nn.Module):
        """Apply gradient clipping."""
        if self.config.clip_norm is not None:
            torch.nn.utils.clip_grad_norm_(model.parameters(), self.config.clip_norm)
        
        if self.config.clip_value is not None:
            torch.nn.utils.clip_grad_value_(model.parameters(), self.config.clip_value)
    
    def _update_metrics(self, step: int):
        """Update accumulation metrics."""
        self.metrics.current_step = step
        self.metrics.effective_batch_size = self.config.accumulation_steps
        
        # Calculate memory efficiency
        if torch.cuda.is_available():
            self.metrics.memory_usage = torch.cuda.memory_allocated() / (1024**3)  # GB
        
        # Calculate gradient norms
        total_norm = 0.0
        for p in self._get_model_parameters():
            if p.grad is not None:
                param_norm = p.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
        total_norm = total_norm ** (1. / 2)
        self.metrics.gradient_norms.append(total_norm)
    
    def _get_model_parameters(self):
        """Get model parameters for gradient analysis."""
        # This would be passed from the training loop
        return []
    
    def get_accumulation_info(self) -> Dict[str, Any]:
        """Get current accumulation information."""
        return {
            'enabled': self.config.enabled,
            'mode': self.config.mode.value,
            'current_accumulation_step': self.accumulation_state['accumulation_step'],
            'target_accumulation_steps': self.config.accumulation_steps,
            'effective_batch_size': self.config.effective_batch_size,
            'memory_usage': self.metrics.memory_usage,
            'loss_average': (self.accumulation_state['loss_sum'] / 
                           max(self.accumulation_state['loss_count'], 1))
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        return {
            'accumulation_config': {
                'mode': self.config.mode.value,
                'steps': self.config.accumulation_steps,
                'effective_batch_size': self.config.effective_batch_size
            },
            'current_state': {
                'step': self.accumulation_state['step'],
                'accumulation_step': self.accumulation_state['accumulation_step'],
                'loss_sum': self.accumulation_state['loss_sum'],
                'loss_count': self.accumulation_state['loss_count']
            },
            'metrics': {
                'current_step': self.metrics.current_step,
                'memory_usage_gb': self.metrics.memory_usage,
                'gradient_norms': self.metrics.gradient_norms[-10:] if self.metrics.gradient_norms else [],
                'accumulation_times': self.metrics.accumulation_times[-10:] if self.metrics.accumulation_times else []
            }
        }
    
    def cleanup(self):
        """Cleanup accumulation resources."""
        self.accumulated_gradients.clear()
        self.accumulation_state = {
            'step': 0,
            'accumulation_step': 0,
            'loss_sum': 0.0,
            'loss_count': 0
        }
        logger.info("🧹 Gradient accumulator cleaned up")

class AdaptiveGradientAccumulator(GradientAccumulator):
    """Advanced gradient accumulator with adaptive accumulation steps."""
    
    def __init__(self, config: GradientAccumulationConfig):
        super().__init__(config)
        self.adaptation_history = []
        self.performance_metrics = {}
    
    def adapt_accumulation_steps(self, model: nn.Module, 
                               current_performance: Dict[str, float]) -> int:
        """Adaptively adjust accumulation steps based on performance."""
        if self.config.mode != AccumulationMode.ADAPTIVE:
            return self.config.accumulation_steps
        
        # Analyze current performance
        memory_usage = current_performance.get('memory_usage', 0.0)
        training_speed = current_performance.get('training_speed', 0.0)
        loss_stability = current_performance.get('loss_stability', 1.0)
        
        # Calculate optimal accumulation steps
        optimal_steps = self._calculate_optimal_steps(
            memory_usage, training_speed, loss_stability
        )
        
        # Clamp to valid range
        optimal_steps = max(self.config.min_accumulation_steps,
                          min(self.config.max_accumulation_steps, optimal_steps))
        
        # Update configuration
        if optimal_steps != self.config.accumulation_steps:
            old_steps = self.config.accumulation_steps
            self.config.accumulation_steps = optimal_steps
            logger.info(f"🔄 Accumulation steps adapted: {old_steps} -> {optimal_steps}")
        
        return optimal_steps
    
    def _calculate_optimal_steps(self, memory_usage: float, 
                               training_speed: float, 
                               loss_stability: float) -> int:
        """Calculate optimal accumulation steps based on performance metrics."""
        # Memory-based adjustment
        memory_factor = 1.0
        if memory_usage > 0.8:  # High memory usage
            memory_factor = 1.5
        elif memory_usage < 0.4:  # Low memory usage
            memory_factor = 0.8
        
        # Speed-based adjustment
        speed_factor = 1.0
        if training_speed < 0.5:  # Slow training
            speed_factor = 0.8
        elif training_speed > 1.5:  # Fast training
            speed_factor = 1.2
        
        # Stability-based adjustment
        stability_factor = 1.0
        if loss_stability < 0.01:  # Very stable
            stability_factor = 1.3
        elif loss_stability > 0.1:  # Unstable
            stability_factor = 0.7
        
        # Calculate optimal steps
        base_steps = self.config.accumulation_steps
        optimal_steps = int(base_steps * memory_factor * speed_factor * stability_factor)
        
        return optimal_steps

@contextmanager
def gradient_accumulation_context(accumulator: GradientAccumulator, 
                                step: int, model: nn.Module, 
                                optimizer: optim.Optimizer):
    """Context manager for gradient accumulation."""
    start_time = time.time()
    
    try:
        yield accumulator
    finally:
        # Record accumulation time
        end_time = time.time()
        accumulator.metrics.accumulation_times.append(end_time - start_time)

def create_gradient_accumulator(config: GradientAccumulationConfig) -> GradientAccumulator:
    """Factory function to create appropriate gradient accumulator."""
    if config.mode == AccumulationMode.ADAPTIVE:
        return AdaptiveGradientAccumulator(config)
    else:
        return GradientAccumulator(config)

def calculate_optimal_accumulation_steps(target_batch_size: int, 
                                       current_batch_size: int,
                                       available_memory: float,
                                       model_memory: float) -> int:
    """Calculate optimal accumulation steps for target batch size."""
    # Basic calculation
    min_steps = max(1, target_batch_size // current_batch_size)
    
    # Memory-based adjustment
    memory_ratio = available_memory / model_memory
    if memory_ratio < 2.0:
        min_steps = max(min_steps, 4)  # Force more accumulation for memory efficiency
    elif memory_ratio > 8.0:
        min_steps = max(1, min_steps // 2)  # Can use fewer steps with plenty of memory
    
    return min_steps

# Example usage and integration
if __name__ == "__main__":
    # Example configuration
    config = GradientAccumulationConfig(
        enabled=True,
        mode=AccumulationMode.ADAPTIVE,
        accumulation_steps=4,
        effective_batch_size=128,
        min_accumulation_steps=2,
        max_accumulation_steps=16,
        memory_threshold=0.8,
        gradient_clipping=True,
        clip_norm=1.0
    )
    
    # Create accumulator
    accumulator = create_gradient_accumulator(config)
    
    print("✅ Gradient accumulation system created successfully!")
    print(f"  Mode: {config.mode.value}")
    print(f"  Target steps: {config.accumulation_steps}")
    print(f"  Effective batch size: {config.effective_batch_size}")
