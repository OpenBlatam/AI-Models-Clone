#!/usr/bin/env python3
"""
LoRA (Low-Rank Adaptation) Fine-tuning Module

Efficient fine-tuning using low-rank matrix decomposition to reduce
trainable parameters while maintaining performance.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Any, List, Tuple
import math
import logging

logger = logging.getLogger(__name__)


class LoRALayer(nn.Module):
    """LoRA layer for efficient fine-tuning."""
    
    def __init__(self, base_layer: nn.Module, r: int = 16, alpha: float = 32.0, 
                 dropout: float = 0.1, bias: bool = False):
        super().__init__()
        self.base_layer = base_layer
        self.r = r
        self.alpha = alpha
        self.dropout = dropout
        self.bias = bias
        
        # Get layer dimensions
        if hasattr(base_layer, 'in_features') and hasattr(base_layer, 'out_features'):
            self.in_features = base_layer.in_features
            self.out_features = base_layer.out_features
        else:
            raise ValueError("Unsupported layer type")
        
        # Initialize LoRA matrices
        self.lora_A = nn.Parameter(torch.randn(r, self.in_features) * 0.02)
        self.lora_B = nn.Parameter(torch.zeros(self.out_features, r))
        
        # Scaling factor
        self.scaling = alpha / r
        
        # Dropout
        self.lora_dropout = nn.Dropout(dropout)
        
        # Optional bias
        if bias and hasattr(base_layer, 'bias') and base_layer.bias is not None:
            self.lora_bias = nn.Parameter(torch.zeros_like(base_layer.bias))
        else:
            self.lora_bias = None
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize LoRA weights."""
        nn.init.zeros_(self.lora_B)
        if self.lora_bias is not None:
            nn.init.zeros_(self.lora_bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with LoRA adaptation."""
        # Base layer output
        base_output = self.base_layer(x)
        
        # LoRA adaptation
        x_dropped = self.lora_dropout(x)
        lora_output = x_dropped @ self.lora_A.T @ self.lora_B.T
        lora_output = lora_output * self.scaling
        
        # Add bias if enabled
        if self.lora_bias is not None:
            lora_output = lora_output + self.lora_bias
        
        return base_output + lora_output


class LoRAFineTuner:
    """Main LoRA fine-tuning class."""
    
    def __init__(self, model: nn.Module, target_modules: List[str], 
                 r: int = 16, alpha: float = 32.0, dropout: float = 0.1):
        self.model = model
        self.target_modules = target_modules
        self.r = r
        self.alpha = alpha
        self.dropout = dropout
        
        self.lora_layers = {}
        self._apply_lora()
    
    def _apply_lora(self):
        """Apply LoRA to target modules."""
        for name, module in self.model.named_modules():
            if any(target in name for target in self.target_modules):
                if isinstance(module, nn.Linear):
                    # Create LoRA layer
                    lora_layer = LoRALayer(module, self.r, self.alpha, self.dropout)
                    
                    # Replace module
                    parent_name = '.'.join(name.split('.')[:-1])
                    child_name = name.split('.')[-1]
                    parent_module = dict(self.model.named_modules())[parent_name]
                    setattr(parent_module, child_name, lora_layer)
                    
                    self.lora_layers[name] = lora_layer
        
        logger.info(f"Applied LoRA to {len(self.lora_layers)} layers")
    
    def freeze_base_model(self):
        """Freeze base model parameters."""
        for param in self.model.parameters():
            param.requires_grad = False
        
        # Unfreeze LoRA parameters
        for lora_layer in self.lora_layers.values():
            for param in lora_layer.parameters():
                param.requires_grad = True
        
        logger.info("Base model frozen, LoRA parameters trainable")
    
    def get_trainable_parameters(self) -> List[nn.Parameter]:
        """Get trainable parameters."""
        trainable_params = []
        for lora_layer in self.lora_layers.values():
            trainable_params.extend(lora_layer.parameters())
        return trainable_params
    
    def get_parameter_stats(self) -> Dict[str, int]:
        """Get parameter statistics."""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.get_trainable_parameters())
        
        return {
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'frozen_parameters': total_params - trainable_params,
            'efficiency_ratio': trainable_params / total_params
        }


# Example usage
if __name__ == "__main__":
    # Test model
    model = nn.Sequential(
        nn.Linear(100, 200),
        nn.ReLU(),
        nn.Linear(200, 100)
    )
    
    # Initialize LoRA fine-tuner
    fine_tuner = LoRAFineTuner(
        model=model,
        target_modules=['0', '2'],  # Apply to first and last linear layers
        r=16,
        alpha=32.0
    )
    
    # Freeze base model
    fine_tuner.freeze_base_model()
    
    # Get statistics
    stats = fine_tuner.get_parameter_stats()
    print("Parameter Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nLoRA fine-tuning module ready!")


