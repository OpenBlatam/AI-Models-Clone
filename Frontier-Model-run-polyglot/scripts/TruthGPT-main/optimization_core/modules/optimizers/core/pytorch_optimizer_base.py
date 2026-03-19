"""
PyTorch Optimizer Base Class
Migrated from optimization_core.core.pytorch_optimizer_base
"""

import torch
import torch.nn as nn
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field

@dataclass
class OptimizationConfig:
    """Base configuration for python optimizers"""
    enabled: bool = True
    verbose: bool = False
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    precision: str = "float32"

class PyTorchOptimizerBase:
    """
    Base class for PyTorch-based optimizers.
    Provides common functionality for configuration and device management.
    """
    
    def __init__(self, config: Union[Dict[str, Any], OptimizationConfig] = None):
        if config is None:
            self.config = OptimizationConfig()
        elif isinstance(config, dict):
            self.config = OptimizationConfig(**config)
        else:
            self.config = config
            
        self.device = torch.device(self.config.device if hasattr(self.config, 'device') else 'cpu')
        
    def optimize(self, model: nn.Module) -> nn.Module:
        """
        Apply optimization to the model.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement optimize()")
        
    def to(self, device: Union[str, torch.device]):
        """Move optimizer resources to device"""
        self.device = torch.device(device)
        return self


