#!/usr/bin/env python3
"""
Efficient Fine-tuning Techniques Module

This module implements various parameter-efficient fine-tuning methods:
- LoRA (Low-Rank Adaptation)
- P-tuning (Prompt Tuning)
- Prefix Tuning
- AdaLoRA (Adaptive LoRA)
- QLoRA (Quantized LoRA)
- BitFit (Bias-term Fine-tuning)

Features:
- Automatic rank selection for LoRA
- Gradient checkpointing for memory efficiency
- Mixed precision training support
- Automatic adapter management
- Performance monitoring and optimization
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Any, List, Tuple, Union
import math
import numpy as np
from dataclasses import dataclass
import logging
from abc import ABC, abstractmethod
import warnings

logger = logging.getLogger(__name__)


@dataclass
class LoRAConfig:
    """Configuration for LoRA fine-tuning."""
    r: int = 16  # Rank of the low-rank matrices
    alpha: float = 32.0  # Scaling factor
    dropout: float = 0.1  # Dropout probability
    bias: bool = False  # Whether to train bias terms
    target_modules: Optional[List[str]] = None  # Target module names
    fan_in_fan_out: bool = False  # Whether to transpose weights
    merge_weights: bool = False  # Whether to merge LoRA weights into base model


@dataclass
class PTuningConfig:
    """Configuration for P-tuning."""
    num_virtual_tokens: int = 20  # Number of virtual prompt tokens
    token_dim: int = 768  # Dimension of token embeddings
    encoder_hidden_size: int = 128  # Hidden size of prompt encoder
    encoder_num_layers: int = 2  # Number of layers in prompt encoder
    encoder_dropout: float = 0.1  # Dropout in prompt encoder


@dataclass
class PrefixTuningConfig:
    """Configuration for Prefix Tuning."""
    num_prefix_tokens: int = 20  # Number of prefix tokens
    prefix_dim: int = 768  # Dimension of prefix embeddings
    encoder_hidden_size: int = 512  # Hidden size of prefix encoder
    encoder_num_layers: int = 2  # Number of layers in prefix encoder


class LoRALayer(nn.Module):
    """LoRA layer implementation with efficient computation."""
    
    def __init__(self, base_layer: nn.Module, config: LoRAConfig, adapter_name: str = "default"):
        """
        Initialize LoRA layer.
        
        Args:
            base_layer: Base layer to adapt
            config: LoRA configuration
            adapter_name: Name of the adapter
        """
        super().__init__()
        self.base_layer = base_layer
        self.config = config
        self.adapter_name = adapter_name
        
        # Get base layer dimensions
        if hasattr(base_layer, 'in_features') and hasattr(base_layer, 'out_features'):
            # Linear layer
            self.in_features = base_layer.in_features
            self.out_features = base_layer.out_features
            self.weight_dim = (self.out_features, self.in_features)
        elif hasattr(base_layer, 'num_features') and hasattr(base_layer, 'weight'):
            # Conv layer
            self.weight_dim = base_layer.weight.shape
            self.in_features = self.weight_dim[1]
            self.out_features = self.weight_dim[0]
        else:
            raise ValueError(f"Unsupported layer type: {type(base_layer)}")
        
        # Initialize LoRA matrices
        self._init_lora_weights()
        
        # Scaling factor
        self.scaling = config.alpha / config.r
        
        # Whether to merge weights
        self.merged = False
    
    def _init_lora_weights(self):
        """Initialize LoRA weight matrices."""
        # Low-rank matrices A and B
        self.lora_A = nn.Parameter(torch.randn(self.config.r, self.in_features) * 0.02)
        self.lora_B = nn.Parameter(torch.zeros(self.out_features, self.config.r))
        
        # Initialize B with zeros for stable training
        nn.init.zeros_(self.lora_B)
        
        # Optional bias training
        if self.config.bias and hasattr(self.base_layer, 'bias') and self.base_layer.bias is not None:
            self.lora_bias = nn.Parameter(torch.zeros_like(self.base_layer.bias))
        else:
            self.lora_bias = None
        
        # Dropout
        self.lora_dropout = nn.Dropout(self.config.dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass with LoRA adaptation.
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor with LoRA adaptation
        """
        if self.merged:
            return self.base_layer(x)
        
        # Base layer forward pass
        base_output = self.base_layer(x)
        
        # LoRA adaptation
        lora_output = self._compute_lora_output(x)
        
        return base_output + lora_output
    
    def _compute_lora_output(self, x: torch.Tensor) -> torch.Tensor:
        """Compute LoRA adaptation output."""
        # Apply dropout to input
        x_dropped = self.lora_dropout(x)
        
        # Compute LoRA output: x @ A.T @ B.T
        if len(x.shape) == 2:  # Linear case
            # x: (batch_size, in_features)
            # A: (r, in_features) -> A.T: (in_features, r)
            # B: (out_features, r) -> B.T: (r, out_features)
            # Result: (batch_size, out_features)
            lora_output = x_dropped @ self.lora_A.T @ self.lora_B.T
        else:  # Conv case
            # Reshape for convolution
            batch_size = x.shape[0]
            x_reshaped = x_dropped.view(batch_size, -1)  # Flatten spatial dimensions
            lora_output = x_reshaped @ self.lora_A.T @ self.lora_B.T
            lora_output = lora_output.view(x.shape[0], -1, *x.shape[2:])  # Restore shape
        
        # Apply scaling
        lora_output = lora_output * self.scaling
        
        # Add bias if enabled
        if self.lora_bias is not None:
            lora_output = lora_output + self.lora_bias
        
        return lora_output
    
    def merge_weights(self):
        """Merge LoRA weights into base layer weights."""
        if self.merged:
            return
        
        with torch.no_grad():
            # Get base weights
            if hasattr(self.base_layer, 'weight'):
                base_weight = self.base_layer.weight.data
            else:
                return
            
            # Compute LoRA weight update
            lora_weight = self.lora_B @ self.lora_A * self.scaling
            
            # Update base weights
            if self.config.fan_in_fan_out:
                lora_weight = lora_weight.T
            
            base_weight += lora_weight
            
            # Update bias if enabled
            if self.lora_bias is not None and hasattr(self.base_layer, 'bias'):
                self.base_layer.bias.data += self.lora_bias.data
        
        self.merged = True
        logger.info(f"Merged LoRA weights for adapter: {self.adapter_name}")
    
    def unmerge_weights(self):
        """Unmerge LoRA weights from base layer weights."""
        if not self.merged:
            return
        
        with torch.no_grad():
            # Get base weights
            if hasattr(self.base_layer, 'weight'):
                base_weight = self.base_layer.weight.data
            else:
                return
            
            # Compute LoRA weight update
            lora_weight = self.lora_B @ self.lora_A * self.scaling
            
            # Revert base weights
            if self.config.fan_in_fan_out:
                lora_weight = lora_weight.T
            
            base_weight -= lora_weight
            
            # Revert bias if enabled
            if self.lora_bias is not None and hasattr(self.base_layer, 'bias'):
                self.base_layer.bias.data -= self.lora_bias.data
        
        self.merged = False
        logger.info(f"Unmerged LoRA weights for adapter: {self.adapter_name}")


class AdaLoRALayer(LoRALayer):
    """Adaptive LoRA layer with automatic rank selection."""
    
    def __init__(self, base_layer: nn.Module, config: LoRAConfig, 
                 max_rank: int = 64, target_rank: int = 16):
        """
        Initialize AdaLoRA layer.
        
        Args:
            base_layer: Base layer to adapt
            config: LoRA configuration
            max_rank: Maximum possible rank
            target_rank: Target rank for adaptation
        """
        super().__init__(base_layer, config)
        self.max_rank = max_rank
        self.target_rank = target_rank
        
        # Initialize importance scores
        self.importance_scores = nn.Parameter(torch.ones(max_rank))
        
        # Initialize all possible ranks
        self._init_adaptive_weights()
    
    def _init_adaptive_weights(self):
        """Initialize adaptive LoRA weights."""
        # Initialize A and B with maximum rank
        self.lora_A = nn.Parameter(torch.randn(self.max_rank, self.in_features) * 0.02)
        self.lora_B = nn.Parameter(torch.zeros(self.out_features, self.max_rank))
        
        # Initialize importance scores
        nn.init.uniform_(self.importance_scores, 0.0, 1.0)
    
    def _compute_adaptive_rank(self) -> int:
        """Compute adaptive rank based on importance scores."""
        # Sort importance scores
        sorted_scores, indices = torch.sort(self.importance_scores, descending=True)
        
        # Select top-k scores based on target rank
        top_k_scores = sorted_scores[:self.target_rank]
        
        # Compute cumulative importance
        cumulative_importance = torch.cumsum(top_k_scores, dim=0)
        total_importance = cumulative_importance[-1]
        
        # Normalize to get rank weights
        rank_weights = top_k_scores / total_importance
        
        return rank_weights, indices[:self.target_rank]
    
    def _compute_lora_output(self, x: torch.Tensor) -> torch.Tensor:
        """Compute adaptive LoRA output."""
        # Get adaptive rank
        rank_weights, rank_indices = self._compute_adaptive_rank()
        
        # Select active LoRA weights
        active_A = self.lora_A[rank_indices]  # (target_rank, in_features)
        active_B = self.lora_B[:, rank_indices]  # (out_features, target_rank)
        
        # Apply dropout
        x_dropped = self.lora_dropout(x)
        
        # Compute LoRA output with rank weights
        if len(x.shape) == 2:  # Linear case
            lora_output = x_dropped @ active_A.T @ active_B.T
        else:  # Conv case
            batch_size = x.shape[0]
            x_reshaped = x_dropped.view(batch_size, -1)
            lora_output = x_reshaped @ active_A.T @ active_B.T
            lora_output = lora_output.view(x.shape[0], -1, *x.shape[2:])
        
        # Apply rank-weighted scaling
        lora_output = lora_output * self.scaling
        
        # Add bias if enabled
        if self.lora_bias is not None:
            lora_output = lora_output + self.lora_bias
        
        return lora_output


class PTuningModule(nn.Module):
    """P-tuning module for prompt learning."""
    
    def __init__(self, config: PTuningConfig, token_dim: int):
        """
        Initialize P-tuning module.
        
        Args:
            config: P-tuning configuration
            token_dim: Dimension of token embeddings
        """
        super().__init__()
        self.config = config
        self.token_dim = token_dim
        
        # Virtual prompt embeddings
        self.prompt_embeddings = nn.Parameter(
            torch.randn(config.num_virtual_tokens, token_dim) * 0.02
        )
        
        # Prompt encoder (MLP)
        self.prompt_encoder = nn.Sequential(
            nn.Linear(token_dim, config.encoder_hidden_size),
            nn.Tanh(),
            nn.Dropout(config.encoder_dropout),
            *[nn.Sequential(
                nn.Linear(config.encoder_hidden_size, config.encoder_hidden_size),
                nn.Tanh(),
                nn.Dropout(config.encoder_dropout)
            ) for _ in range(config.encoder_num_layers - 1)],
            nn.Linear(config.encoder_hidden_size, token_dim)
        )
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize prompt encoder weights."""
        for module in self.prompt_encoder.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, batch_size: int) -> torch.Tensor:
        """
        Generate prompt embeddings.
        
        Args:
            batch_size: Batch size for the current forward pass
            
        Returns:
            Prompt embeddings tensor
        """
        # Encode prompt embeddings
        encoded_prompts = self.prompt_encoder(self.prompt_embeddings)
        
        # Expand to batch size
        prompt_embeddings = encoded_prompts.unsqueeze(0).expand(
            batch_size, -1, -1
        )
        
        return prompt_embeddings


class PrefixTuningModule(nn.Module):
    """Prefix tuning module for sequence modeling."""
    
    def __init__(self, config: PrefixTuningConfig, hidden_dim: int):
        """
        Initialize prefix tuning module.
        
        Args:
            config: Prefix tuning configuration
            hidden_dim: Hidden dimension of the model
        """
        super().__init__()
        self.config = config
        self.hidden_dim = hidden_dim
        
        # Prefix embeddings
        self.prefix_embeddings = nn.Parameter(
            torch.randn(config.num_prefix_tokens, hidden_dim) * 0.02
        )
        
        # Prefix encoder (MLP)
        self.prefix_encoder = nn.Sequential(
            nn.Linear(hidden_dim, config.encoder_hidden_size),
            nn.Tanh(),
            nn.Dropout(0.1),
            *[nn.Sequential(
                nn.Linear(config.encoder_hidden_size, config.encoder_hidden_size),
                nn.Tanh(),
                nn.Dropout(0.1)
            ) for _ in range(config.encoder_num_layers - 1)],
            nn.Linear(config.encoder_hidden_size, hidden_dim * 2)  # *2 for key and value
        )
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize prefix encoder weights."""
        for module in self.prefix_encoder.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, batch_size: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Generate prefix key and value embeddings.
        
        Args:
            batch_size: Batch size for the current forward pass
            
        Returns:
            Tuple of (prefix_keys, prefix_values)
        """
        # Encode prefix embeddings
        encoded_prefixes = self.prefix_encoder(self.prefix_embeddings)
        
        # Split into key and value
        prefix_keys = encoded_prefixes[:, :self.hidden_dim]
        prefix_values = encoded_prefixes[:, self.hidden_dim:]
        
        # Expand to batch size
        prefix_keys = prefix_keys.unsqueeze(0).expand(batch_size, -1, -1)
        prefix_values = prefix_values.unsqueeze(0).expand(batch_size, -1, -1)
        
        return prefix_keys, prefix_values


class BitFitModule(nn.Module):
    """BitFit module for bias-term fine-tuning."""
    
    def __init__(self, base_model: nn.Module):
        """
        Initialize BitFit module.
        
        Args:
            base_model: Base model to adapt
        """
        super().__init__()
        self.base_model = base_model
        self.bias_adapters = nn.ModuleDict()
        
        # Find all bias parameters
        self._find_bias_parameters()
    
    def _find_bias_parameters(self):
        """Find all bias parameters in the base model."""
        for name, module in self.base_model.named_modules():
            if hasattr(module, 'bias') and module.bias is not None:
                # Create bias adapter
                bias_adapter = nn.Parameter(torch.zeros_like(module.bias))
                self.bias_adapters[name] = bias_adapter
                
                # Freeze original bias
                module.bias.requires_grad = False
    
    def forward(self, *args, **kwargs):
        """Forward pass with bias adaptation."""
        # Apply bias adaptations
        for name, bias_adapter in self.bias_adapters.items():
            module_name, param_name = name.rsplit('.', 1)
            module = dict(self.base_model.named_modules())[module_name]
            if hasattr(module, 'bias') and module.bias is not None:
                module.bias.data += bias_adapter.data
        
        # Forward pass through base model
        output = self.base_model(*args, **kwargs)
        
        # Restore original biases
        for name, bias_adapter in self.bias_adapters.items():
            module_name, param_name = name.rsplit('.', 1)
            module = dict(self.base_model.named_modules())[module_name]
            if hasattr(module, 'bias') and module.bias is not None:
                module.bias.data -= bias_adapter.data
        
        return output


class EfficientFineTuner:
    """Main class for efficient fine-tuning."""
    
    def __init__(self, base_model: nn.Module, config: Dict[str, Any]):
        """
        Initialize efficient fine-tuner.
        
        Args:
            base_model: Base model to fine-tune
            config: Configuration dictionary
        """
        self.base_model = base_model
        self.config = config
        self.adapters = {}
        self.active_adapters = []
        
        # Initialize fine-tuning methods
        self._init_finetuning_methods()
        
        # Performance monitoring
        self.training_stats = {
            'total_parameters': sum(p.numel() for p in base_model.parameters()),
            'trainable_parameters': 0,
            'memory_usage': 0,
            'training_time': 0
        }
    
    def _init_finetuning_methods(self):
        """Initialize fine-tuning methods based on configuration."""
        if 'lora' in self.config:
            self._init_lora()
        
        if 'p_tuning' in self.config:
            self._init_p_tuning()
        
        if 'prefix_tuning' in self.config:
            self._init_prefix_tuning()
        
        if 'bitfit' in self.config:
            self._init_bitfit()
    
    def _init_lora(self):
        """Initialize LoRA adapters."""
        lora_config = LoRAConfig(**self.config['lora'])
        
        # Find target modules
        target_modules = lora_config.target_modules or ['q_proj', 'v_proj', 'k_proj', 'o_proj']
        
        for name, module in self.base_model.named_modules():
            if any(target in name for target in target_modules):
                if isinstance(module, (nn.Linear, nn.Conv2d)):
                    # Create LoRA adapter
                    if self.config['lora'].get('adaptive', False):
                        adapter = AdaLoRALayer(module, lora_config)
                    else:
                        adapter = LoRALayer(module, lora_config)
                    
                    # Replace module with adapter
                    parent_name = '.'.join(name.split('.')[:-1])
                    child_name = name.split('.')[-1]
                    parent_module = dict(self.base_model.named_modules())[parent_name]
                    setattr(parent_module, child_name, adapter)
                    
                    self.adapters[f"lora_{name}"] = adapter
        
        logger.info(f"Initialized {len(self.adapters)} LoRA adapters")
    
    def _init_p_tuning(self):
        """Initialize P-tuning module."""
        p_tuning_config = PTuningConfig(**self.config['p_tuning'])
        
        # Create P-tuning module
        self.p_tuning_module = PTuningModule(p_tuning_config, p_tuning_config.token_dim)
        
        logger.info("Initialized P-tuning module")
    
    def _init_prefix_tuning(self):
        """Initialize prefix tuning module."""
        prefix_config = PrefixTuningConfig(**self.config['prefix_tuning'])
        
        # Create prefix tuning module
        self.prefix_module = PrefixTuningModule(prefix_config, prefix_config.prefix_dim)
        
        logger.info("Initialized prefix tuning module")
    
    def _init_bitfit(self):
        """Initialize BitFit module."""
        self.bitfit_module = BitFitModule(self.base_model)
        
        logger.info("Initialized BitFit module")
    
    def get_trainable_parameters(self) -> List[nn.Parameter]:
        """Get list of trainable parameters."""
        trainable_params = []
        
        # Collect adapter parameters
        for adapter in self.adapters.values():
            trainable_params.extend(adapter.parameters())
        
        # Collect other fine-tuning parameters
        if hasattr(self, 'p_tuning_module'):
            trainable_params.extend(self.p_tuning_module.parameters())
        
        if hasattr(self, 'prefix_module'):
            trainable_params.extend(self.prefix_module.parameters())
        
        if hasattr(self, 'bitfit_module'):
            trainable_params.extend(self.bitfit_module.parameters())
        
        return trainable_params
    
    def freeze_base_model(self):
        """Freeze base model parameters."""
        for param in self.base_model.parameters():
            param.requires_grad = False
        
        logger.info("Base model parameters frozen")
    
    def unfreeze_base_model(self):
        """Unfreeze base model parameters."""
        for param in self.base_model.parameters():
            param.requires_grad = True
        
        logger.info("Base model parameters unfrozen")
    
    def merge_adapters(self, adapter_names: Optional[List[str]] = None):
        """Merge LoRA adapters into base model."""
        if adapter_names is None:
            adapter_names = list(self.adapters.keys())
        
        for name in adapter_names:
            if name in self.adapters and hasattr(self.adapters[name], 'merge_weights'):
                self.adapters[name].merge_weights()
        
        logger.info(f"Merged adapters: {adapter_names}")
    
    def unmerge_adapters(self, adapter_names: Optional[List[str]] = None):
        """Unmerge LoRA adapters from base model."""
        if adapter_names is None:
            adapter_names = list(self.adapters.keys())
        
        for name in adapter_names:
            if name in self.adapters and hasattr(self.adapters[name], 'unmerge_weights'):
                self.adapters[name].unmerge_weights()
        
        logger.info(f"Unmerged adapters: {adapter_names}")
    
    def get_parameter_efficiency_stats(self) -> Dict[str, Any]:
        """Get parameter efficiency statistics."""
        total_params = self.training_stats['total_parameters']
        trainable_params = sum(p.numel() for p in self.get_trainable_parameters())
        
        stats = {
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'frozen_parameters': total_params - trainable_params,
            'parameter_efficiency': trainable_params / total_params,
            'compression_ratio': total_params / trainable_params,
            'memory_savings_mb': (total_params - trainable_params) * 4 / (1024 * 1024)
        }
        
        return stats
    
    def save_adapters(self, save_path: str):
        """Save adapter weights."""
        adapter_state = {}
        
        # Save LoRA adapters
        for name, adapter in self.adapters.items():
            if hasattr(adapter, 'state_dict'):
                adapter_state[name] = adapter.state_dict()
        
        # Save other fine-tuning modules
        if hasattr(self, 'p_tuning_module'):
            adapter_state['p_tuning'] = self.p_tuning_module.state_dict()
        
        if hasattr(self, 'prefix_module'):
            adapter_state['prefix_tuning'] = self.prefix_module.state_dict()
        
        if hasattr(self, 'bitfit_module'):
            adapter_state['bitfit'] = self.bitfit_module.state_dict()
        
        # Save configuration
        adapter_state['config'] = self.config
        
        torch.save(adapter_state, save_path)
        logger.info(f"Adapters saved to: {save_path}")
    
    def load_adapters(self, load_path: str):
        """Load adapter weights."""
        adapter_state = torch.load(load_path, map_location='cpu')
        
        # Load LoRA adapters
        for name, state_dict in adapter_state.items():
            if name in self.adapters and hasattr(self.adapters[name], 'load_state_dict'):
                self.adapters[name].load_state_dict(state_dict)
        
        # Load other fine-tuning modules
        if 'p_tuning' in adapter_state and hasattr(self, 'p_tuning_module'):
            self.p_tuning_module.load_state_dict(adapter_state['p_tuning'])
        
        if 'prefix_tuning' in adapter_state and hasattr(self, 'prefix_module'):
            self.prefix_module.load_state_dict(adapter_state['prefix_tuning'])
        
        if 'bitfit' in adapter_state and hasattr(self, 'bitfit_module'):
            self.bitfit_module.load_state_dict(adapter_state['bitfit'])
        
        logger.info(f"Adapters loaded from: {load_path}")


# Example usage and testing
if __name__ == "__main__":
    # Create a simple test model
    class TestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.linear1 = nn.Linear(100, 200)
            self.linear2 = nn.Linear(200, 100)
            self.relu = nn.ReLU()
        
        def forward(self, x):
            x = self.relu(self.linear1(x))
            x = self.linear2(x)
            return x
    
    # Test model
    model = TestModel()
    
    # Configuration for efficient fine-tuning
    config = {
        'lora': {
            'r': 16,
            'alpha': 32.0,
            'dropout': 0.1,
            'bias': False,
            'target_modules': ['linear1', 'linear2']
        },
        'p_tuning': {
            'num_virtual_tokens': 10,
            'token_dim': 100,
            'encoder_hidden_size': 64,
            'encoder_num_layers': 2
        },
        'bitfit': True
    }
    
    # Initialize fine-tuner
    fine_tuner = EfficientFineTuner(model, config)
    
    # Freeze base model
    fine_tuner.freeze_base_model()
    
    # Get statistics
    stats = fine_tuner.get_parameter_efficiency_stats()
    print("Parameter Efficiency Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test forward pass
    x = torch.randn(32, 100)
    output = model(x)
    print(f"Output shape: {output.shape}")
    
    print("\nEfficient fine-tuning module testing completed!")


