from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import torch
import torch.nn as nn
from torch.optim import Optimizer
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional, Union, Callable, Iterator
from dataclasses import dataclass, field
import logging
from pathlib import Path
import time
import json
import pickle
from enum import Enum
import os
import math
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import warnings
from typing import Any, List, Dict, Optional
import asyncio
#!/usr/bin/env python3
"""
Gradient Clipping and NaN/Inf Value Handling System
Comprehensive gradient clipping and numerical stability implementation.
"""

warnings.filterwarnings('ignore')


class ClippingType(Enum):
    """Types of gradient clipping."""
    NORM = "norm"  # L2 norm clipping
    VALUE = "value"  # Value clipping
    GLOBAL_NORM = "global_norm"  # Global norm clipping
    ADAPTIVE = "adaptive"  # Adaptive clipping


class NaNHandlingType(Enum):
    """Types of NaN/Inf handling."""
    DETECT = "detect"  # Detect and log
    REPLACE = "replace"  # Replace with safe values
    SKIP = "skip"  # Skip update
    RESTORE = "restore"  # Restore from checkpoint
    GRADIENT_ZEROING = "gradient_zeroing"  # Zero gradients


@dataclass
class GradientClippingConfig:
    """Configuration for gradient clipping."""
    # Clipping type
    clipping_type: ClippingType = ClippingType.NORM
    
    # Clipping parameters
    max_norm: float = 1.0
    max_value: float = 1.0
    clip_ratio: float = 0.1
    
    # Adaptive clipping
    adaptive_threshold: float = 0.1
    adaptive_factor: float = 2.0
    
    # Monitoring
    monitor_clipping: bool = True
    log_clipping_stats: bool = True
    save_clipping_history: bool = True
    clipping_history_file: str = "gradient_clipping_history.json"
    
    # Advanced settings
    clip_grad_norm: bool = True
    clip_grad_value: bool = False
    use_global_norm: bool = False
    
    # Performance
    efficient_clipping: bool = True
    parallel_clipping: bool = False


@dataclass
class NaNHandlingConfig:
    """Configuration for NaN/Inf handling."""
    # Handling type
    handling_type: NaNHandlingType = NaNHandlingType.DETECT
    
    # Detection settings
    detect_nan: bool = True
    detect_inf: bool = True
    detect_overflow: bool = True
    
    # Replacement values
    nan_replacement: float = 0.0
    inf_replacement: float = 1e6
    overflow_replacement: float = 1e6
    
    # Thresholds
    nan_threshold: float = 1e-6
    inf_threshold: float = 1e6
    overflow_threshold: float = 1e6
    
    # Monitoring
    monitor_nan: bool = True
    log_nan_stats: bool = True
    save_nan_history: bool = True
    nan_history_file: str = "nan_handling_history.json"
    
    # Advanced settings
    gradient_zeroing: bool = True
    parameter_checking: bool = True
    loss_checking: bool = True
    
    # Performance
    efficient_detection: bool = True
    batch_detection: bool = True


class GradientClipper:
    """Advanced gradient clipping implementation."""
    
    def __init__(self, config: GradientClippingConfig):
        
    """__init__ function."""
self.config = config
        self.logger = self._setup_logging()
        
        # Clipping history
        self.clipping_history = {
            'steps': [],
            'clipping_ratios': [],
            'gradient_norms': [],
            'clipped_norms': [],
            'clipping_types': []
        }
        
        # Current step
        self.current_step = 0
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def clip_gradients(self, model: nn.Module, optimizer: Optimizer) -> Dict[str, float]:
        """Clip gradients based on configuration."""
        self.current_step += 1
        
        if self.config.clipping_type == ClippingType.NORM:
            return self._clip_grad_norm(model, optimizer)
        
        elif self.config.clipping_type == ClippingType.VALUE:
            return self._clip_grad_value(model, optimizer)
        
        elif self.config.clipping_type == ClippingType.GLOBAL_NORM:
            return self._clip_global_norm(model, optimizer)
        
        elif self.config.clipping_type == ClippingType.ADAPTIVE:
            return self._clip_adaptive(model, optimizer)
        
        else:
            raise ValueError(f"Unknown clipping type: {self.config.clipping_type}")
    
    def _clip_grad_norm(self, model: nn.Module, optimizer: Optimizer) -> Dict[str, float]:
        """Clip gradients by norm."""
        # Get all gradients
        gradients = []
        for param in model.parameters():
            if param.grad is not None:
                gradients.append(param.grad.data.view(-1))
        
        if not gradients:
            return {'clipping_ratio': 0.0, 'gradient_norm': 0.0, 'clipped_norm': 0.0}
        
        # Concatenate gradients
        all_gradients = torch.cat(gradients)
        
        # Calculate norm
        total_norm = all_gradients.norm(2)
        
        # Clip if necessary
        clip_coef = self.config.max_norm / (total_norm + 1e-6)
        clip_coef = min(clip_coef, 1.0)
        
        # Apply clipping
        if clip_coef < 1.0:
            for param in model.parameters():
                if param.grad is not None:
                    param.grad.data.mul_(clip_coef)
        
        # Update history
        self._update_clipping_history(total_norm.item(), total_norm.item() * clip_coef, 'norm')
        
        return {
            'clipping_ratio': 1.0 - clip_coef,
            'gradient_norm': total_norm.item(),
            'clipped_norm': total_norm.item() * clip_coef
        }
    
    def _clip_grad_value(self, model: nn.Module, optimizer: Optimizer) -> Dict[str, float]:
        """Clip gradients by value."""
        total_norm = 0.0
        clipped_norm = 0.0
        clipped_count = 0
        
        for param in model.parameters():
            if param.grad is not None:
                # Calculate norm before clipping
                param_norm = param.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
                
                # Clip gradients
                param.grad.data.clamp_(-self.config.max_value, self.config.max_value)
                
                # Calculate norm after clipping
                clipped_param_norm = param.grad.data.norm(2)
                clipped_norm += clipped_param_norm.item() ** 2
                
                if param_norm.item() > self.config.max_value:
                    clipped_count += 1
        
        total_norm = math.sqrt(total_norm)
        clipped_norm = math.sqrt(clipped_norm)
        
        # Update history
        self._update_clipping_history(total_norm, clipped_norm, 'value')
        
        return {
            'clipping_ratio': clipped_count / len(list(model.parameters())),
            'gradient_norm': total_norm,
            'clipped_norm': clipped_norm
        }
    
    def _clip_global_norm(self, model: nn.Module, optimizer: Optimizer) -> Dict[str, float]:
        """Clip gradients using global norm."""
        # Get all gradients
        gradients = []
        for param in model.parameters():
            if param.grad is not None:
                gradients.append(param.grad.data.view(-1))
        
        if not gradients:
            return {'clipping_ratio': 0.0, 'gradient_norm': 0.0, 'clipped_norm': 0.0}
        
        # Concatenate gradients
        all_gradients = torch.cat(gradients)
        
        # Calculate global norm
        global_norm = all_gradients.norm(2)
        
        # Clip if necessary
        clip_coef = self.config.max_norm / (global_norm + 1e-6)
        clip_coef = min(clip_coef, 1.0)
        
        # Apply clipping
        if clip_coef < 1.0:
            for param in model.parameters():
                if param.grad is not None:
                    param.grad.data.mul_(clip_coef)
        
        # Update history
        self._update_clipping_history(global_norm.item(), global_norm.item() * clip_coef, 'global_norm')
        
        return {
            'clipping_ratio': 1.0 - clip_coef,
            'gradient_norm': global_norm.item(),
            'clipped_norm': global_norm.item() * clip_coef
        }
    
    def _clip_adaptive(self, model: nn.Module, optimizer: Optimizer) -> Dict[str, float]:
        """Adaptive gradient clipping."""
        # Get all gradients
        gradients = []
        for param in model.parameters():
            if param.grad is not None:
                gradients.append(param.grad.data.view(-1))
        
        if not gradients:
            return {'clipping_ratio': 0.0, 'gradient_norm': 0.0, 'clipped_norm': 0.0}
        
        # Concatenate gradients
        all_gradients = torch.cat(gradients)
        
        # Calculate norm
        total_norm = all_gradients.norm(2)
        
        # Adaptive threshold
        adaptive_threshold = self.config.adaptive_threshold
        if len(self.clipping_history['gradient_norms']) > 0:
            avg_norm = np.mean(self.clipping_history['gradient_norms'][-10:])
            adaptive_threshold = avg_norm * self.config.adaptive_factor
        
        # Clip if necessary
        clip_coef = adaptive_threshold / (total_norm + 1e-6)
        clip_coef = min(clip_coef, 1.0)
        
        # Apply clipping
        if clip_coef < 1.0:
            for param in model.parameters():
                if param.grad is not None:
                    param.grad.data.mul_(clip_coef)
        
        # Update history
        self._update_clipping_history(total_norm.item(), total_norm.item() * clip_coef, 'adaptive')
        
        return {
            'clipping_ratio': 1.0 - clip_coef,
            'gradient_norm': total_norm.item(),
            'clipped_norm': total_norm.item() * clip_coef,
            'adaptive_threshold': adaptive_threshold
        }
    
    def _update_clipping_history(self, gradient_norm: float, clipped_norm: float, clipping_type: str):
        """Update clipping history."""
        self.clipping_history['steps'].append(self.current_step)
        self.clipping_history['gradient_norms'].append(gradient_norm)
        self.clipping_history['clipped_norms'].append(clipped_norm)
        self.clipping_history['clipping_types'].append(clipping_type)
        
        # Calculate clipping ratio
        if gradient_norm > 0:
            clipping_ratio = 1.0 - (clipped_norm / gradient_norm)
        else:
            clipping_ratio = 0.0
        
        self.clipping_history['clipping_ratios'].append(clipping_ratio)
        
        # Log if enabled
        if self.config.log_clipping_stats:
            self.logger.info(f"Step {self.current_step}: Gradient norm = {gradient_norm:.6f}, "
                           f"Clipped norm = {clipped_norm:.6f}, Clipping ratio = {clipping_ratio:.4f}")
    
    def save_history(self) -> Any:
        """Save clipping history."""
        if self.config.save_clipping_history:
            history_data = {
                'history': self.clipping_history,
                'config': self.config,
                'current_step': self.current_step
            }
            
            with open(self.config.clipping_history_file, 'w') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                json.dump(history_data, f, indent=2, default=str)
            
            self.logger.info(f"Clipping history saved to {self.config.clipping_history_file}")
    
    def plot_clipping_history(self, save_path: Optional[str] = None):
        """Plot gradient clipping history."""
        if not self.clipping_history['steps']:
            self.logger.warning("No clipping history to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot gradient norms
        axes[0, 0].plot(self.clipping_history['steps'], self.clipping_history['gradient_norms'], 
                        label='Gradient Norm', alpha=0.7)
        axes[0, 0].plot(self.clipping_history['steps'], self.clipping_history['clipped_norms'], 
                        label='Clipped Norm', alpha=0.7)
        axes[0, 0].set_title('Gradient Norms Over Time')
        axes[0, 0].set_xlabel('Step')
        axes[0, 0].set_ylabel('Norm')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        axes[0, 0].set_yscale('log')
        
        # Plot clipping ratios
        axes[0, 1].plot(self.clipping_history['steps'], self.clipping_history['clipping_ratios'], 
                        label='Clipping Ratio', color='red')
        axes[0, 1].set_title('Clipping Ratios Over Time')
        axes[0, 1].set_xlabel('Step')
        axes[0, 1].set_ylabel('Clipping Ratio')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Plot clipping ratio distribution
        axes[1, 0].hist(self.clipping_history['clipping_ratios'], bins=30, alpha=0.7, 
                        edgecolor='black', color='red')
        axes[1, 0].set_title('Clipping Ratio Distribution')
        axes[1, 0].set_xlabel('Clipping Ratio')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].grid(True)
        
        # Plot gradient norm distribution
        axes[1, 1].hist(self.clipping_history['gradient_norms'], bins=30, alpha=0.7, 
                        edgecolor='black', color='blue')
        axes[1, 1].set_title('Gradient Norm Distribution')
        axes[1, 1].set_xlabel('Gradient Norm')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_xscale('log')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Clipping history plot saved to {save_path}")
        
        plt.show()


class NaNHandler:
    """Advanced NaN/Inf value handling."""
    
    def __init__(self, config: NaNHandlingConfig):
        
    """__init__ function."""
self.config = config
        self.logger = self._setup_logging()
        
        # NaN history
        self.nan_history = {
            'steps': [],
            'nan_counts': [],
            'inf_counts': [],
            'overflow_counts': [],
            'handling_actions': []
        }
        
        # Current step
        self.current_step = 0
        
        # Statistics
        self.total_nan_detected = 0
        self.total_inf_detected = 0
        self.total_overflow_detected = 0
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def check_and_handle(self, model: nn.Module, loss: torch.Tensor, 
                         optimizer: Optimizer) -> Dict[str, Any]:
        """Check for NaN/Inf values and handle them."""
        self.current_step += 1
        
        nan_detected = False
        inf_detected = False
        overflow_detected = False
        handling_action = "none"
        
        # Check loss
        if self.config.loss_checking:
            loss_nan, loss_inf, loss_overflow = self._check_tensor(loss, "loss")
            nan_detected |= loss_nan
            inf_detected |= loss_inf
            overflow_detected |= loss_overflow
        
        # Check parameters
        if self.config.parameter_checking:
            param_nan, param_inf, param_overflow = self._check_parameters(model)
            nan_detected |= param_nan
            inf_detected |= param_inf
            overflow_detected |= param_overflow
        
        # Check gradients
        grad_nan, grad_inf, grad_overflow = self._check_gradients(model)
        nan_detected |= grad_nan
        inf_detected |= grad_inf
        overflow_detected |= grad_overflow
        
        # Handle if detected
        if nan_detected or inf_detected or overflow_detected:
            handling_action = self._handle_numerical_issues(model, optimizer, 
                                                          nan_detected, inf_detected, overflow_detected)
        
        # Update statistics
        if nan_detected:
            self.total_nan_detected += 1
        if inf_detected:
            self.total_inf_detected += 1
        if overflow_detected:
            self.total_overflow_detected += 1
        
        # Update history
        self._update_nan_history(nan_detected, inf_detected, overflow_detected, handling_action)
        
        return {
            'nan_detected': nan_detected,
            'inf_detected': inf_detected,
            'overflow_detected': overflow_detected,
            'handling_action': handling_action,
            'total_nan': self.total_nan_detected,
            'total_inf': self.total_inf_detected,
            'total_overflow': self.total_overflow_detected
        }
    
    def _check_tensor(self, tensor: torch.Tensor, name: str) -> Tuple[bool, bool, bool]:
        """Check tensor for NaN/Inf values."""
        nan_detected = torch.isnan(tensor).any().item()
        inf_detected = torch.isinf(tensor).any().item()
        overflow_detected = (tensor.abs() > self.config.overflow_threshold).any().item()
        
        if nan_detected or inf_detected or overflow_detected:
            if self.config.log_nan_stats:
                self.logger.warning(f"Step {self.current_step}: {name} has "
                                  f"NaN={nan_detected}, Inf={inf_detected}, Overflow={overflow_detected}")
        
        return nan_detected, inf_detected, overflow_detected
    
    def _check_parameters(self, model: nn.Module) -> Tuple[bool, bool, bool]:
        """Check model parameters for NaN/Inf values."""
        nan_detected = False
        inf_detected = False
        overflow_detected = False
        
        for name, param in model.named_parameters():
            param_nan, param_inf, param_overflow = self._check_tensor(param.data, f"parameter {name}")
            nan_detected |= param_nan
            inf_detected |= param_inf
            overflow_detected |= param_overflow
        
        return nan_detected, inf_detected, overflow_detected
    
    def _check_gradients(self, model: nn.Module) -> Tuple[bool, bool, bool]:
        """Check model gradients for NaN/Inf values."""
        nan_detected = False
        inf_detected = False
        overflow_detected = False
        
        for name, param in model.named_parameters():
            if param.grad is not None:
                grad_nan, grad_inf, grad_overflow = self._check_tensor(param.grad.data, f"gradient {name}")
                nan_detected |= grad_nan
                inf_detected |= grad_inf
                overflow_detected |= grad_overflow
        
        return nan_detected, inf_detected, overflow_detected
    
    def _handle_numerical_issues(self, model: nn.Module, optimizer: Optimizer,
                                nan_detected: bool, inf_detected: bool, 
                                overflow_detected: bool) -> str:
        """Handle numerical issues based on configuration."""
        if self.config.handling_type == NaNHandlingType.DETECT:
            return "detected"
        
        elif self.config.handling_type == NaNHandlingType.REPLACE:
            self._replace_numerical_issues(model)
            return "replaced"
        
        elif self.config.handling_type == NaNHandlingType.SKIP:
            optimizer.zero_grad()
            return "skipped"
        
        elif self.config.handling_type == NaNHandlingType.RESTORE:
            # This would require checkpoint management
            self.logger.warning("Restore handling requires checkpoint management")
            return "restore_failed"
        
        elif self.config.handling_type == NaNHandlingType.GRADIENT_ZEROING:
            if self.config.gradient_zeroing:
                self._zero_gradients(model)
            return "gradients_zeroed"
        
        else:
            return "unknown"
    
    def _replace_numerical_issues(self, model: nn.Module):
        """Replace NaN/Inf values with safe values."""
        for name, param in model.named_parameters():
            if param.grad is not None:
                # Replace NaN gradients
                if torch.isnan(param.grad.data).any():
                    param.grad.data = torch.where(torch.isnan(param.grad.data),
                                                torch.tensor(self.config.nan_replacement),
                                                param.grad.data)
                
                # Replace Inf gradients
                if torch.isinf(param.grad.data).any():
                    param.grad.data = torch.where(torch.isinf(param.grad.data),
                                                torch.tensor(self.config.inf_replacement),
                                                param.grad.data)
                
                # Replace overflow gradients
                overflow_mask = param.grad.data.abs() > self.config.overflow_threshold
                if overflow_mask.any():
                    param.grad.data = torch.where(overflow_mask,
                                                torch.tensor(self.config.overflow_replacement),
                                                param.grad.data)
    
    def _zero_gradients(self, model: nn.Module):
        """Zero gradients with numerical issues."""
        for name, param in model.named_parameters():
            if param.grad is not None:
                # Zero gradients with NaN/Inf
                nan_inf_mask = torch.isnan(param.grad.data) | torch.isinf(param.grad.data)
                if nan_inf_mask.any():
                    param.grad.data[nan_inf_mask] = 0.0
    
    def _update_nan_history(self, nan_detected: bool, inf_detected: bool, 
                           overflow_detected: bool, handling_action: str):
        """Update NaN handling history."""
        self.nan_history['steps'].append(self.current_step)
        self.nan_history['nan_counts'].append(1 if nan_detected else 0)
        self.nan_history['inf_counts'].append(1 if inf_detected else 0)
        self.nan_history['overflow_counts'].append(1 if overflow_detected else 0)
        self.nan_history['handling_actions'].append(handling_action)
    
    def save_history(self) -> Any:
        """Save NaN handling history."""
        if self.config.save_nan_history:
            history_data = {
                'history': self.nan_history,
                'config': self.config,
                'current_step': self.current_step,
                'total_nan': self.total_nan_detected,
                'total_inf': self.total_inf_detected,
                'total_overflow': self.total_overflow_detected
            }
            
            with open(self.config.nan_history_file, 'w') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                json.dump(history_data, f, indent=2, default=str)
            
            self.logger.info(f"NaN handling history saved to {self.config.nan_history_file}")
    
    def plot_nan_history(self, save_path: Optional[str] = None):
        """Plot NaN handling history."""
        if not self.nan_history['steps']:
            self.logger.warning("No NaN history to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot NaN/Inf/Overflow counts over time
        axes[0, 0].plot(self.nan_history['steps'], self.nan_history['nan_counts'], 
                        label='NaN', alpha=0.7, color='red')
        axes[0, 0].plot(self.nan_history['steps'], self.nan_history['inf_counts'], 
                        label='Inf', alpha=0.7, color='orange')
        axes[0, 0].plot(self.nan_history['steps'], self.nan_history['overflow_counts'], 
                        label='Overflow', alpha=0.7, color='yellow')
        axes[0, 0].set_title('Numerical Issues Over Time')
        axes[0, 0].set_xlabel('Step')
        axes[0, 0].set_ylabel('Count')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Plot cumulative counts
        cumulative_nan = np.cumsum(self.nan_history['nan_counts'])
        cumulative_inf = np.cumsum(self.nan_history['inf_counts'])
        cumulative_overflow = np.cumsum(self.nan_history['overflow_counts'])
        
        axes[0, 1].plot(self.nan_history['steps'], cumulative_nan, 
                        label='Cumulative NaN', color='red')
        axes[0, 1].plot(self.nan_history['steps'], cumulative_inf, 
                        label='Cumulative Inf', color='orange')
        axes[0, 1].plot(self.nan_history['steps'], cumulative_overflow, 
                        label='Cumulative Overflow', color='yellow')
        axes[0, 1].set_title('Cumulative Numerical Issues')
        axes[0, 1].set_xlabel('Step')
        axes[0, 1].set_ylabel('Cumulative Count')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Plot handling actions distribution
        action_counts = {}
        for action in self.nan_history['handling_actions']:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        if action_counts:
            actions = list(action_counts.keys())
            counts = list(action_counts.values())
            axes[1, 0].bar(actions, counts, alpha=0.7)
            axes[1, 0].set_title('Handling Actions Distribution')
            axes[1, 0].set_xlabel('Action')
            axes[1, 0].set_ylabel('Count')
            axes[1, 0].tick_params(axis='x', rotation=45)
            axes[1, 0].grid(True)
        
        # Plot numerical issues distribution
        total_issues = np.array(self.nan_history['nan_counts']) + \
                      np.array(self.nan_history['inf_counts']) + \
                      np.array(self.nan_history['overflow_counts'])
        
        axes[1, 1].hist(total_issues, bins=range(int(max(total_issues)) + 2), 
                        alpha=0.7, edgecolor='black')
        axes[1, 1].set_title('Total Numerical Issues Distribution')
        axes[1, 1].set_xlabel('Total Issues per Step')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"NaN history plot saved to {save_path}")
        
        plt.show()


class NumericalStabilityManager:
    """Comprehensive numerical stability manager."""
    
    def __init__(self, clipping_config: GradientClippingConfig, 
                 nan_config: NaNHandlingConfig):
        
    """__init__ function."""
self.clipping_config = clipping_config
        self.nan_config = nan_config
        self.logger = self._setup_logging()
        
        # Initialize components
        self.gradient_clipper = GradientClipper(clipping_config)
        self.nan_handler = NaNHandler(nan_config)
        
        # Training state
        self.current_step = 0
        self.stability_history = {
            'steps': [],
            'clipping_stats': [],
            'nan_stats': [],
            'stability_scores': []
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def step(self, model: nn.Module, loss: torch.Tensor, 
             optimizer: Optimizer) -> Dict[str, Any]:
        """Perform one step with numerical stability checks."""
        self.current_step += 1
        
        # Check for NaN/Inf values
        nan_stats = self.nan_handler.check_and_handle(model, loss, optimizer)
        
        # Apply gradient clipping
        clipping_stats = self.gradient_clipper.clip_gradients(model, optimizer)
        
        # Calculate stability score
        stability_score = self._calculate_stability_score(nan_stats, clipping_stats)
        
        # Update history
        self._update_stability_history(nan_stats, clipping_stats, stability_score)
        
        # Log if issues detected
        if nan_stats['nan_detected'] or nan_stats['inf_detected'] or nan_stats['overflow_detected']:
            self.logger.warning(f"Step {self.current_step}: Numerical issues detected - "
                              f"NaN: {nan_stats['nan_detected']}, "
                              f"Inf: {nan_stats['inf_detected']}, "
                              f"Overflow: {nan_stats['overflow_detected']}")
        
        return {
            'nan_stats': nan_stats,
            'clipping_stats': clipping_stats,
            'stability_score': stability_score
        }
    
    def _calculate_stability_score(self, nan_stats: Dict[str, Any], 
                                  clipping_stats: Dict[str, float]) -> float:
        """Calculate numerical stability score."""
        score = 1.0
        
        # Penalize for numerical issues
        if nan_stats['nan_detected']:
            score -= 0.3
        if nan_stats['inf_detected']:
            score -= 0.2
        if nan_stats['overflow_detected']:
            score -= 0.1
        
        # Penalize for excessive clipping
        if 'clipping_ratio' in clipping_stats:
            score -= clipping_stats['clipping_ratio'] * 0.1
        
        return max(0.0, score)
    
    def _update_stability_history(self, nan_stats: Dict[str, Any], 
                                 clipping_stats: Dict[str, float], 
                                 stability_score: float):
        """Update stability history."""
        self.stability_history['steps'].append(self.current_step)
        self.stability_history['nan_stats'].append(nan_stats)
        self.stability_history['clipping_stats'].append(clipping_stats)
        self.stability_history['stability_scores'].append(stability_score)
    
    def save_histories(self) -> Any:
        """Save all histories."""
        self.gradient_clipper.save_history()
        self.nan_handler.save_history()
    
    def plot_stability_history(self, save_path: Optional[str] = None):
        """Plot numerical stability history."""
        if not self.stability_history['steps']:
            self.logger.warning("No stability history to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot stability scores
        axes[0, 0].plot(self.stability_history['steps'], self.stability_history['stability_scores'], 
                        label='Stability Score', color='green')
        axes[0, 0].set_title('Numerical Stability Score Over Time')
        axes[0, 0].set_xlabel('Step')
        axes[0, 0].set_ylabel('Stability Score')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Plot clipping ratios
        clipping_ratios = [stats.get('clipping_ratio', 0.0) for stats in self.stability_history['clipping_stats']]
        axes[0, 1].plot(self.stability_history['steps'], clipping_ratios, 
                        label='Clipping Ratio', color='blue')
        axes[0, 1].set_title('Gradient Clipping Ratio Over Time')
        axes[0, 1].set_xlabel('Step')
        axes[0, 1].set_ylabel('Clipping Ratio')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Plot numerical issues
        nan_counts = [stats['nan_detected'] for stats in self.stability_history['nan_stats']]
        inf_counts = [stats['inf_detected'] for stats in self.stability_history['nan_stats']]
        overflow_counts = [stats['overflow_detected'] for stats in self.stability_history['nan_stats']]
        
        axes[1, 0].plot(self.stability_history['steps'], nan_counts, 
                        label='NaN', color='red', alpha=0.7)
        axes[1, 0].plot(self.stability_history['steps'], inf_counts, 
                        label='Inf', color='orange', alpha=0.7)
        axes[1, 0].plot(self.stability_history['steps'], overflow_counts, 
                        label='Overflow', color='yellow', alpha=0.7)
        axes[1, 0].set_title('Numerical Issues Over Time')
        axes[1, 0].set_xlabel('Step')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Plot stability score distribution
        axes[1, 1].hist(self.stability_history['stability_scores'], bins=20, alpha=0.7, 
                        edgecolor='black', color='green')
        axes[1, 1].set_title('Stability Score Distribution')
        axes[1, 1].set_xlabel('Stability Score')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Stability history plot saved to {save_path}")
        
        plt.show()


def demonstrate_gradient_clipping_nan_handling():
    """Demonstrate gradient clipping and NaN handling capabilities."""
    print("Gradient Clipping and NaN Handling Demonstration")
    print("=" * 50)
    
    # Create sample model
    class SimpleModel(nn.Module):
        def __init__(self) -> Any:
            super(SimpleModel, self).__init__()
            self.fc1 = nn.Linear(10, 20)
            self.fc2 = nn.Linear(20, 10)
            self.fc3 = nn.Linear(10, 1)
            self.relu = nn.ReLU()
        
        def forward(self, x) -> Any:
            x = self.relu(self.fc1(x))
            x = self.relu(self.fc2(x))
            x = self.fc3(x)
            return x
    
    # Create configurations
    clipping_config = GradientClippingConfig(
        clipping_type=ClippingType.NORM,
        max_norm=1.0,
        monitor_clipping=True,
        log_clipping_stats=True
    )
    
    nan_config = NaNHandlingConfig(
        handling_type=NaNHandlingType.DETECT,
        detect_nan=True,
        detect_inf=True,
        detect_overflow=True,
        monitor_nan=True,
        log_nan_stats=True
    )
    
    # Create stability manager
    stability_manager = NumericalStabilityManager(clipping_config, nan_config)
    
    # Create model and optimizer
    model = SimpleModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    # Test different scenarios
    scenarios = [
        {
            'name': 'Normal Training',
            'input_data': torch.randn(32, 10),
            'target': torch.randn(32, 1),
            'introduce_nan': False
        },
        {
            'name': 'High Gradient Training',
            'input_data': torch.randn(32, 10) * 10,
            'target': torch.randn(32, 1) * 10,
            'introduce_nan': False
        },
        {
            'name': 'NaN Introduction',
            'input_data': torch.randn(32, 10),
            'target': torch.randn(32, 1),
            'introduce_nan': True
        }
    ]
    
    results = {}
    
    for i, scenario in enumerate(scenarios):
        print(f"\nTesting scenario {i+1}: {scenario['name']}")
        
        try:
            # Forward pass
            output = model(scenario['input_data'])
            loss = nn.MSELoss()(output, scenario['target'])
            
            # Introduce NaN if requested
            if scenario['introduce_nan']:
                # Introduce NaN in gradients
                for param in model.parameters():
                    if param.grad is not None:
                        param.grad.data[0, 0] = float('nan')
            
            # Backward pass
            loss.backward()
            
            # Apply numerical stability measures
            stability_result = stability_manager.step(model, loss, optimizer)
            
            # Optimizer step
            optimizer.step()
            optimizer.zero_grad()
            
            print(f"  Loss: {loss.item():.6f}")
            print(f"  Stability Score: {stability_result['stability_score']:.4f}")
            print(f"  Clipping Ratio: {stability_result['clipping_stats'].get('clipping_ratio', 0.0):.4f}")
            print(f"  NaN Detected: {stability_result['nan_stats']['nan_detected']}")
            print(f"  Inf Detected: {stability_result['nan_stats']['inf_detected']}")
            
            results[f"scenario_{i}"] = {
                'scenario': scenario,
                'stability_result': stability_result,
                'success': True
            }
            
        except Exception as e:
            print(f"  Error: {e}")
            results[f"scenario_{i}"] = {
                'scenario': scenario,
                'error': str(e),
                'success': False
            }
    
    # Save and plot results
    stability_manager.save_histories()
    stability_manager.plot_stability_history("stability_history.png")
    
    return results


if __name__ == "__main__":
    # Demonstrate gradient clipping and NaN handling
    results = demonstrate_gradient_clipping_nan_handling()
    print("\nGradient clipping and NaN handling demonstration completed!") 