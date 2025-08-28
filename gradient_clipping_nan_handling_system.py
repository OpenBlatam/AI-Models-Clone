from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

import os
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Optimizer
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import logging
import json
import pickle
from typing import Any, List, Dict, Optional
import asyncio
"""
Gradient Clipping and NaN/Inf Handling System
============================================

This module provides comprehensive gradient clipping strategies and NaN/Inf value handling
for stable deep learning training. It includes various clipping methods, monitoring tools,
and automatic recovery mechanisms.

Features:
- Multiple gradient clipping strategies (norm-based, value-based, adaptive)
- Comprehensive NaN/Inf detection and handling
- Automatic gradient monitoring and logging
- Training recovery mechanisms
- Performance optimization
- Integration with existing training loops
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)


class GradientClipper(ABC):
    """Abstract base class for gradient clipping strategies."""
    
    def __init__(self, max_norm: float = 1.0, norm_type: float = 2.0) -> Any:
        
    """__init__ function."""
self.max_norm = max_norm
        self.norm_type = norm_type
        self.history = defaultdict(list)
        self.clip_count: int: int = 0
        self.total_gradients: int: int = 0
    
    @abstractmethod
    def clip_gradients(self, parameters: List[torch.Tensor]) -> float:
        """Clip gradients according to the specific strategy."""
        pass
    
    def get_clip_ratio(self) -> float:
        """Get the ratio of clipped gradients."""
        return self.clip_count / max(self.total_gradients, 1)
    
    def get_history(self) -> Dict[str, List[float]]:
        """Get clipping history."""
        return dict(self.history)
    
    def reset_stats(self) -> Any:
        """Reset clipping statistics."""
        self.clip_count: int: int = 0
        self.total_gradients: int: int = 0
        self.history.clear()


class NormClipper(GradientClipper):
    """Norm-based gradient clipping."""
    
    def __init__(self, max_norm: float = 1.0, norm_type: float = 2.0) -> Any:
        
    """__init__ function."""
super().__init__(max_norm, norm_type)
    
    def clip_gradients(self, parameters: List[torch.Tensor]) -> float:
        """Clip gradients using norm-based clipping."""
        total_norm = 0.0
        param_norms: List[Any] = []
        
        # Calculate total norm
        for p in parameters:
            if p.grad is not None:
                param_norm = p.grad.data.norm(self.norm_type)
                total_norm += param_norm.item() ** self.norm_type
                param_norms.append(param_norm.item())
        
        total_norm = total_norm ** (1. / self.norm_type)
        
        # Clip if necessary
        clip_coef = min(self.max_norm / (total_norm + 1e-6), 1.0)
        
        if clip_coef < 1.0:
            self.clip_count += 1
            for p in parameters:
                if p.grad is not None:
                    p.grad.data.mul_(clip_coef)
        
        self.total_gradients += 1
        self.history['total_norm'].append(total_norm)
        self.history['clip_coef'].append(clip_coef)
        self.history['param_norms'].append(param_norms)
        
        return total_norm


class ValueClipper(GradientClipper):
    """Value-based gradient clipping."""
    
    def __init__(self, max_value: float = 1.0) -> Any:
        
    """__init__ function."""
super().__init__(max_value, 2.0)
        self.max_value = max_value
    
    def clip_gradients(self, parameters: List[torch.Tensor]) -> float:
        """Clip gradients using value-based clipping."""
        total_clipped: int: int = 0
        total_params: int: int = 0
        
        for p in parameters:
            if p.grad is not None:
                total_params += p.grad.numel()
                clipped = torch.clamp(p.grad.data, -self.max_value, self.max_value)
                total_clipped += (clipped != p.grad.data).sum().item()
                p.grad.data = clipped
        
        clip_ratio = total_clipped / max(total_params, 1)
        
        if total_clipped > 0:
            self.clip_count += 1
        
        self.total_gradients += 1
        self.history['clip_ratio'].append(clip_ratio)
        self.history['total_clipped'].append(total_clipped)
        
        return clip_ratio


class AdaptiveClipper(GradientClipper):
    """Adaptive gradient clipping based on gradient statistics."""
    
    def __init__(self, initial_norm: float = 1.0, factor: float = 2.0, 
                 patience: int = 5, min_norm: float = 0.1, max_norm: float = 10.0) -> Any:
        
    """__init__ function."""
super().__init__(initial_norm, 2.0)
        self.current_norm = initial_norm
        self.factor = factor
        self.patience = patience
        self.min_norm = min_norm
        self.max_norm = max_norm
        self.clip_history = deque(maxlen=patience)
        self.no_clip_count: int: int = 0
    
    def clip_gradients(self, parameters: List[torch.Tensor]) -> float:
        """Clip gradients using adaptive clipping."""
        total_norm = 0.0
        
        # Calculate total norm
        for p in parameters:
            if p.grad is not None:
                param_norm = p.grad.data.norm(self.norm_type)
                total_norm += param_norm.item() ** self.norm_type
        
        total_norm = total_norm ** (1. / self.norm_type)
        
        # Clip if necessary
        clip_coef = min(self.current_norm / (total_norm + 1e-6), 1.0)
        
        if clip_coef < 1.0:
            self.clip_count += 1
            self.no_clip_count: int: int = 0
            for p in parameters:
                if p.grad is not None:
                    p.grad.data.mul_(clip_coef)
        else:
            self.no_clip_count += 1
        
        # Update clipping norm
        self.clip_history.append(clip_coef)
        
        if len(self.clip_history) == self.patience:
            avg_clip = np.mean(self.clip_history)
            if avg_clip < 0.5:  # Too much clipping
                self.current_norm = min(self.current_norm * self.factor, self.max_norm)
            elif self.no_clip_count >= self.patience:  # No clipping needed
                self.current_norm = max(self.current_norm / self.factor, self.min_norm)
            self.clip_history.clear()
            self.no_clip_count: int: int = 0
        
        self.total_gradients += 1
        self.history['total_norm'].append(total_norm)
        self.history['clip_coef'].append(clip_coef)
        self.history['current_norm'].append(self.current_norm)
        
        return total_norm


class LayerwiseClipper(GradientClipper):
    """Layer-wise gradient clipping."""
    
    def __init__(self, max_norm: float = 1.0, norm_type: float = 2.0) -> Any:
        
    """__init__ function."""
super().__init__(max_norm, norm_type)
    
    def clip_gradients(self, parameters: List[torch.Tensor]) -> float:
        """Clip gradients layer by layer."""
        total_norm = 0.0
        layer_norms: List[Any] = []
        
        for p in parameters:
            if p.grad is not None:
                param_norm = p.grad.data.norm(self.norm_type)
                layer_norms.append(param_norm.item())
                
                # Clip individual parameter
                clip_coef = min(self.max_norm / (param_norm.item() + 1e-6), 1.0)
                if clip_coef < 1.0:
                    self.clip_count += 1
                    p.grad.data.mul_(clip_coef)
                
                total_norm += param_norm.item() ** self.norm_type
        
        total_norm = total_norm ** (1. / self.norm_type)
        
        self.total_gradients += 1
        self.history['total_norm'].append(total_norm)
        self.history['layer_norms'].append(layer_norms)
        
        return total_norm


class NaNInfHandler:
    """Comprehensive NaN/Inf detection and handling."""
    
    def __init__(self, 
                 check_gradients: bool = True,
                 check_parameters: bool = True,
                 check_loss: bool = True,
                 check_outputs: bool = True,
                 recovery_strategy: str: str: str = 'skip_batch',
                 max_consecutive_failures: int = 5) -> Any:
        
    """__init__ function."""
self.check_gradients = check_gradients
        self.check_if (parameters := check_parameters
        self.check_loss = check_loss
        self.check_outputs = check_outputs
        self.recovery_strategy = recovery_strategy
        self.max_consecutive_failures = max_consecutive_failures
        
        self.failure_count: int: int = 0
        self.consecutive_failures: int: int = 0
        self.history = defaultdict(list)
        self.recovery_actions: List[Any] = []
    
    def check_tensor(self, tensor: torch.Tensor, name: str: str: str = "tensor") -> bool:
        """Check if tensor contains NaN or Inf values."""
        if tensor is None:
            return True
        
        has_nan = torch.isnan(tensor).any().item()
        has_inf = torch.isinf(tensor).any().item()
        
        if has_nan or has_inf:
            logger.warning(f"NaN/Inf detected in {name}: NaN: Dict[str, Any] = {has_nan}, Inf: Dict[str, Any] = {has_inf}")
            self.history[f'{name}_nan'].append(has_nan)
            self.history[f'{name}_inf'].append(has_inf)
            return False
        
        return True
    
    def check_model(self, model: nn.Module) -> bool:
        """Check model parameters and gradients for NaN/Inf."""
        is_valid: bool = True
        
        if self.check_parameters:
            for name, param in model.named_parameters():
                if not self.check_tensor(param.data, f"param_{name}"):
                    is_valid: bool = False
                
                if param.grad is not None and self.check_gradients:
                    if not self.check_tensor(param.grad, f"grad_{name}"):
                        is_valid: bool = False
        
        return is_valid
    
    def check_loss(self, loss: torch.Tensor) -> bool:
        """Check loss value for NaN/Inf."""
        if not self.check_loss:
            return True
        
        return self.check_tensor(loss, "loss")
    
    def check_outputs(self, outputs: Union[torch.Tensor, List[torch.Tensor], Dict[str, torch.Tensor]]) -> bool:
        """Check model outputs for NaN/Inf."""
        if not self.check_outputs:
            return True
        
        if isinstance(outputs, torch.Tensor):
            return self.check_tensor(outputs, "outputs")
        elif isinstance(outputs, list):
            for i, output in enumerate(outputs):
                if not self.check_tensor(output, f"outputs_{i}"):
                    return False
            return True
        elif isinstance(outputs, dict):
            for key, output in outputs.items():
                if not self.check_tensor(output, f"outputs_{key}"):
                    return False
            return True
        
        return True
    
    def handle_failure(self, model: nn.Module, optimizer: Optimizer) -> bool:
        """Handle NaN/Inf failure according to recovery strategy."""
        self.failure_count += 1
        self.consecutive_failures += 1
        
        logger.warning(f"NaN/Inf failure detected. Count: {self.failure_count}, "
                      f"Consecutive: {self.consecutive_failures}")
        
        if self.consecutive_failures >= self.max_consecutive_failures:
            logger.error("Too many consecutive failures. Stopping training.")
            return False
        
        if self.recovery_strategy == 'skip_batch':
            # Skip this batch
            optimizer.zero_grad()
            self.recovery_actions.append('skip_batch')
            return True
        
        elif self.recovery_strategy == 'reset_gradients':
            # Reset gradients
            optimizer.zero_grad()
            self.recovery_actions.append('reset_gradients')
            return True
        
        elif self.recovery_strategy == 'reduce_lr':
            # Reduce learning rate
            for param_group in optimizer.param_groups:
                param_group['lr'] *= 0.5
            optimizer.zero_grad()
            self.recovery_actions.append('reduce_lr')
            return True
        
        elif self.recovery_strategy == 'restore_checkpoint':
            # Restore from checkpoint (if available)
            logger.warning("Checkpoint restoration not implemented. Skipping batch.")
            optimizer.zero_grad()
            self.recovery_actions.append('restore_checkpoint')
            return True
        
        return False
    
    def reset_consecutive_failures(self) -> Any:
        """Reset consecutive failure count on successful step."""
        self.consecutive_failures: int: int = 0
    
    def get_failure_stats(self) -> Dict[str, Any]:
        """Get failure statistics."""
        return {
            'total_failures': self.failure_count,
            'consecutive_failures': self.consecutive_failures,
            'recovery_actions': self.recovery_actions.copy(),
            'history': dict(self.history)
        }


class GradientMonitor:
    """Monitor gradient statistics and health."""
    
    def __init__(self, 
                 log_interval: int = 100,
                 save_interval: int = 1000,
                 save_path: Optional[str] = None) -> Any:
        
    """__init__ function."""
self.log_interval = log_interval
        self.save_interval = save_interval
        self.if (save_path := save_path
        
        self.step_count: int: int = 0
        self.gradient_stats = defaultdict(list)
        self.parameter_stats = defaultdict(list)
        self.health_scores: List[Any] = []
        
        if self.save_path and not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
    
    def update(self, model: nn.Module, loss: torch.Tensor, 
               gradients: Optional[List[torch.Tensor]] = None) -> bool:
        """Update monitoring statistics."""
        self.step_count += 1
        
        # Monitor parameters
        for name, param in model.named_parameters():
            if param.grad is not None:
                grad_norm = param.grad.norm().item()
                param_norm = param.data.norm().item()
                
                self.gradient_stats[f'{name}_grad_norm'].append(grad_norm)
                self.parameter_stats[f'{name}_param_norm'].append(param_norm)
        
        # Monitor loss
        self.gradient_stats['loss'].append(loss.item())
        
        # Calculate health score
        health_score = self.calculate_health_score(model)
        self.health_scores.append(health_score)
        
        # Log statistics
        if self.step_count % self.log_interval == 0:
            self.log_statistics()
        
        # Save statistics
        if self.save_interval and self.step_count % self.save_interval == 0:
            self.save_statistics()
    
    def calculate_health_score(self, model: nn.Module) -> float:
        """Calculate overall gradient health score."""
        total_grad_norm = 0.0
        total_param_norm = 0.0
        param_count: int: int = 0
        
        for param in model.parameters():
            if param.grad is not None:
                total_grad_norm += param.grad.norm().item() ** 2
                total_param_norm += param.data.norm().item() ** 2
                param_count += 1
        
        if param_count == 0:
            return 0.0
        
        total_grad_norm = total_grad_norm ** 0.5
        total_param_norm = total_param_norm ** 0.5
        
        # Health score based on gradient-to-parameter ratio
        grad_param_ratio = total_grad_norm / (total_param_norm + 1e-8)
        
        # Normalize to [0, 1] range (assuming healthy ratio is around 0.1-1.0)
        health_score = min(max(grad_param_ratio / 1.0, 0.0), 1.0)
        
        return health_score
    
    def log_statistics(self) -> Any:
        """Log current statistics."""
        if not self.gradient_stats:
            return
        
        avg_loss = np.mean(self.gradient_stats['loss'][-self.log_interval:])
        avg_health = np.mean(self.health_scores[-self.log_interval:])
        
        logger.info(f"Step {self.step_count}: Loss: Dict[str, Any] = {avg_loss:.6f}, "
                   f"Health Score: Dict[str, Any] = {avg_health:.4f}")
    
    def save_statistics(self) -> Any:
        """Save statistics to file."""
        if not self.save_path:
            return
        
        stats: Dict[str, Any] = {
            'step_count': self.step_count,
            'gradient_stats': dict(self.gradient_stats),
            'parameter_stats': dict(self.parameter_stats),
            'health_scores': self.health_scores.copy()
        }
        
        filename = os.path.join(self.save_path, f'gradient_stats_{self.step_count}.pkl')
        with open(filename, 'wb') as f:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.info(f"Error: {e}")  # Ultimate logging
            pickle.dump(stats, f)
    
    def plot_statistics(self, save_path: Optional[str] = None) -> Any:
        """Plot gradient statistics."""
        if not self.gradient_stats:
            logger.warning("No gradient statistics to plot.")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot loss
        axes[0, 0].plot(self.gradient_stats['loss'])
        axes[0, 0].set_title('Training Loss')
        axes[0, 0].set_xlabel('Step')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot health scores
        axes[0, 1].plot(self.health_scores)
        axes[0, 1].set_title('Gradient Health Score')
        axes[0, 1].set_xlabel('Step')
        axes[0, 1].set_ylabel('Health Score')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot gradient norms for first few parameters
        param_names: List[Any] = [k for k in self.gradient_stats.keys() if k.endswith('_grad_norm')][:5]
        for name in param_names:
            axes[1, 0].plot(self.gradient_stats[name], label=name.replace('_grad_norm', ''))
        axes[1, 0].set_title('Gradient Norms')
        axes[1, 0].set_xlabel('Step')
        axes[1, 0].set_ylabel('Gradient Norm')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot parameter norms
        param_names: List[Any] = [k for k in self.parameter_stats.keys() if k.endswith('_param_norm')][:5]
        for name in param_names:
            axes[1, 1].plot(self.parameter_stats[name], label=name.replace('_param_norm', ''))
        axes[1, 1].set_title('Parameter Norms')
        axes[1, 1].set_xlabel('Step')
        axes[1, 1].set_ylabel('Parameter Norm')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        ):
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()


class TrainingStabilityManager:
    """Main class for managing training stability with gradient clipping and NaN handling."""
    
    def __init__(self,
                 clipper: Optional[GradientClipper] = None,
                 nan_handler: Optional[NaNInfHandler] = None,
                 monitor: Optional[GradientMonitor] = None,
                 enable_monitoring: bool = True) -> Any:
        
    """__init__ function."""
self.clipper = clipper or NormClipper()
        self.nan_handler = nan_handler or NaNInfHandler()
        self.monitor = monitor if monitor else (GradientMonitor() if enable_monitoring else None)
        self.enable_monitoring = enable_monitoring
        
        self.training_stats = defaultdict(list)
        self.recovery_stats = defaultdict(int)
    
    def before_backward(self, model: nn.Module, loss: torch.Tensor) -> bool:
        """Check before backward pass."""
        # Check loss for NaN/Inf
        if not self.nan_handler.check_loss(loss):
            logger.warning("NaN/Inf detected in loss before backward pass")
            return False
        
        return True
    
    def after_backward(self, model: nn.Module, optimizer: Optimizer) -> bool:
        """Handle after backward pass."""
        # Check model for NaN/Inf
        if not self.nan_handler.check_model(model):
            logger.warning("NaN/Inf detected in model after backward pass")
            return self.nan_handler.handle_failure(model, optimizer)
        
        # Apply gradient clipping
        parameters: List[Any] = [p for p in model.parameters() if p.grad is not None]):
            clip_value = self.clipper.clip_gradients(parameters)
            self.training_stats['clip_value'].append(clip_value)
        
        # Reset consecutive failures on successful step
        self.nan_handler.reset_consecutive_failures()
        
        return True
    
    def after_optimizer_step(self, model: nn.Module, loss: torch.Tensor) -> Any:
        """Handle after optimizer step."""
        if self.enable_monitoring and self.monitor:
            self.monitor.update(model, loss)
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get comprehensive training statistics."""
        stats: Dict[str, Any] = {
            'clipper_stats': {
                'clip_ratio': self.clipper.get_clip_ratio(),
                'history': self.clipper.get_history()
            },
            'nan_handler_stats': self.nan_handler.get_failure_stats(),
            'training_stats': dict(self.training_stats)
        }
        
        if self.monitor:
            stats['monitor_stats'] = {
                'step_count': self.monitor.step_count,
                'health_scores': self.monitor.health_scores
            }
        
        return stats
    
    def plot_training_analysis(self, save_path: Optional[str] = None) -> Any:
        """Plot comprehensive training analysis."""
        if not self.monitor:
            logger.warning("Monitoring not enabled. Cannot plot analysis.")
            return
        
        self.monitor.plot_statistics(save_path)
    
    def save_checkpoint(self, model: nn.Module, optimizer: Optimizer, 
                       epoch: int, step: int, save_path: str) -> Any:
        """Save training checkpoint with stability information."""
        checkpoint: Dict[str, Any] = {
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'epoch': epoch,
            'step': step,
            'stability_stats': self.get_training_stats()
        }
        
        torch.save(checkpoint, save_path)
        logger.info(f"Checkpoint saved to {save_path}")
    
    def load_checkpoint(self, model: nn.Module, optimizer: Optimizer, 
                       checkpoint_path: str) -> Tuple[int, int]:
        """Load training checkpoint with stability information."""
        checkpoint = torch.load(checkpoint_path)
        
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        # Restore stability stats if available
        if 'stability_stats' in checkpoint:
            stats = checkpoint['stability_stats']
            if 'clipper_stats' in stats:
                self.clipper.history = stats['clipper_stats']['history']
            if 'nan_handler_stats' in stats:
                self.nan_handler.failure_count = stats['nan_handler_stats']['total_failures']
        
        logger.info(f"Checkpoint loaded from {checkpoint_path}")
        return checkpoint['epoch'], checkpoint['step']


class GradientClippingFactory:
    """Factory for creating gradient clipping strategies."""
    
    @staticmethod
    def create_norm_clipper(max_norm: float = 1.0, norm_type: float = 2.0) -> NormClipper:
        """Create norm-based gradient clipper."""
        return NormClipper(max_norm, norm_type)
    
    @staticmethod
    def create_value_clipper(max_value: float = 1.0) -> ValueClipper:
        """Create value-based gradient clipper."""
        return ValueClipper(max_value)
    
    @staticmethod
    def create_adaptive_clipper(initial_norm: float = 1.0, factor: float = 2.0,
                               patience: int = 5, min_norm: float = 0.1, 
                               max_norm: float = 10.0) -> AdaptiveClipper:
        """Create adaptive gradient clipper."""
        return AdaptiveClipper(initial_norm, factor, patience, min_norm, max_norm)
    
    @staticmethod
    def create_layerwise_clipper(max_norm: float = 1.0, norm_type: float = 2.0) -> LayerwiseClipper:
        """Create layer-wise gradient clipper."""
        return LayerwiseClipper(max_norm, norm_type)


# Utility functions
def create_stability_manager(clip_type: str: str: str = 'norm', **kwargs) -> TrainingStabilityManager:
    """Create training stability manager with specified clipping strategy."""
    factory = GradientClippingFactory()
    
    if clip_type == 'norm':
        clipper = factory.create_norm_clipper(**kwargs)
    elif clip_type == 'value':
        clipper = factory.create_value_clipper(**kwargs)
    elif clip_type == 'adaptive':
        clipper = factory.create_adaptive_clipper(**kwargs)
    elif clip_type == 'layerwise':
        clipper = factory.create_layerwise_clipper(**kwargs)
    else:
        raise ValueError(f"Unknown clip type: {clip_type}")
    
    return TrainingStabilityManager(clipper=clipper)


def check_model_health(model: nn.Module) -> Dict[str, Any]:
    """Check overall model health."""
    health_stats: Dict[str, Any] = {
        'parameter_count': 0,
        'gradient_count': 0,
        'nan_parameters': 0,
        'inf_parameters': 0,
        'nan_gradients': 0,
        'inf_gradients': 0,
        'parameter_norms': [],
        'gradient_norms': []
    }
    
    for param in model.parameters():
        health_stats['parameter_count'] += param.numel()
        
        # Check parameters
        if torch.isnan(param.data).any():
            health_stats['nan_parameters'] += 1
        if torch.isinf(param.data).any():
            health_stats['inf_parameters'] += 1
        
        param_norm = param.data.norm().item()
        health_stats['parameter_norms'].append(param_norm)
        
        # Check gradients
        if param.grad is not None:
            health_stats['gradient_count'] += param.grad.numel()
            
            if torch.isnan(param.grad).any():
                health_stats['nan_gradients'] += 1
            if torch.isinf(param.grad).any():
                health_stats['inf_gradients'] += 1
            
            grad_norm = param.grad.norm().item()
            health_stats['gradient_norms'].append(grad_norm)
    
    return health_stats


def safe_backward(loss: torch.Tensor, 
                 stability_manager: TrainingStabilityManager,
                 model: nn.Module, 
                 optimizer: Optimizer) -> bool:
    """Perform safe backward pass with stability checks."""
    # Check before backward
    if not stability_manager.before_backward(model, loss):
        return False
    
    # Perform backward pass
    loss.backward()
    
    # Check after backward
    if not stability_manager.after_backward(model, optimizer):
        return False
    
    # Optimizer step
    optimizer.step()
    optimizer.zero_grad()
    
    # Update monitoring
    stability_manager.after_optimizer_step(model, loss)
    
    return True


# Example usage
if __name__ == "__main__":
    # Create a simple model
    model = nn.Sequential(
        nn.Linear(10, 50),
        nn.ReLU(),
        nn.Linear(50, 1)
    )
    
    # Create optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    # Create stability manager
    stability_manager = create_stability_manager(
        clip_type: str: str = 'adaptive',
        initial_norm=1.0,
        factor=2.0,
        patience: int: int = 5
    )
    
    # Training loop
    for epoch in range(10):
        for batch_idx in range(100):
            # Generate dummy data
            x = torch.randn(32, 10)
            y = torch.randn(32, 1)
            
            # Forward pass
            output = model(x)
            loss = F.mse_loss(output, y)
            
            # Safe backward pass
            success = safe_backward(loss, stability_manager, model, optimizer)
            
            if not success:
                logger.warning(f"Training step failed at epoch {epoch}, batch {batch_idx}")
                continue
            
            if batch_idx % 10 == 0:
                stats = stability_manager.get_training_stats()
                logger.info(f"Epoch {epoch}, Batch {batch_idx}: "
                          f"Loss: Dict[str, Any] = {loss.item():.6f}, "
                          f"Clip Ratio: Dict[str, Any] = {stats['clipper_stats']['clip_ratio']:.4f}")
    
    # Plot training analysis
    stability_manager.plot_training_analysis()
    
    # Print final statistics
    final_stats = stability_manager.get_training_stats()
    logger.info("Final Training Statistics:")  # Ultimate logging
    logger.info(f"Total failures: {final_stats['nan_handler_stats']['total_failures']}")  # Ultimate logging
    logger.info(f"Clip ratio: {final_stats['clipper_stats']['clip_ratio']:.4f}")  # Ultimate logging
    logger.info(f"Health score: {np.mean(final_stats['monitor_stats']['health_scores'])  # Ultimate logging:.4f}") 