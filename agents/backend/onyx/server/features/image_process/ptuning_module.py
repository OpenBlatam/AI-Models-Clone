#!/usr/bin/env python3
"""
P-tuning Module for Prompt Learning

Efficient fine-tuning using learnable virtual tokens (prompts)
to adapt pre-trained models to specific tasks.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class PromptEncoder(nn.Module):
    """Prompt encoder using MLP for P-tuning."""
    
    def __init__(self, token_dim: int, hidden_size: int, num_layers: int = 2, 
                 dropout: float = 0.1):
        super().__init__()
        self.token_dim = token_dim
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Build MLP layers
        layers = []
        layers.append(nn.Linear(token_dim, hidden_size))
        layers.append(nn.Tanh())
        layers.append(nn.Dropout(dropout))
        
        for _ in range(num_layers - 1):
            layers.append(nn.Linear(hidden_size, hidden_size))
            layers.append(nn.Tanh())
            layers.append(nn.Dropout(dropout))
        
        layers.append(nn.Linear(hidden_size, token_dim))
        
        self.mlp = nn.Sequential(*layers)
        self._init_weights()
    
    def _init_weights(self):
        """Initialize prompt encoder weights."""
        for module in self.mlp.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, prompt_embeddings: torch.Tensor) -> torch.Tensor:
        """
        Encode prompt embeddings.
        
        Args:
            prompt_embeddings: Raw prompt embeddings
            
        Returns:
            Encoded prompt embeddings
        """
        return self.mlp(prompt_embeddings)


class PTuningModule(nn.Module):
    """P-tuning module for learnable prompts."""
    
    def __init__(self, num_virtual_tokens: int, token_dim: int, 
                 encoder_hidden_size: int = 128, encoder_num_layers: int = 2,
                 encoder_dropout: float = 0.1):
        super().__init__()
        self.num_virtual_tokens = num_virtual_tokens
        self.token_dim = token_dim
        
        # Virtual prompt embeddings
        self.prompt_embeddings = nn.Parameter(
            torch.randn(num_virtual_tokens, token_dim) * 0.02
        )
        
        # Prompt encoder
        self.prompt_encoder = PromptEncoder(
            token_dim=token_dim,
            hidden_size=encoder_hidden_size,
            num_layers=encoder_num_layers,
            dropout=encoder_dropout
        )
        
        logger.info(f"P-tuning module initialized with {num_virtual_tokens} virtual tokens")
    
    def forward(self, batch_size: int) -> torch.Tensor:
        """
        Generate prompt embeddings for a batch.
        
        Args:
            batch_size: Batch size for the current forward pass
            
        Returns:
            Prompt embeddings tensor of shape (batch_size, num_virtual_tokens, token_dim)
        """
        # Encode prompt embeddings
        encoded_prompts = self.prompt_encoder(self.prompt_embeddings)
        
        # Expand to batch size
        prompt_embeddings = encoded_prompts.unsqueeze(0).expand(
            batch_size, -1, -1
        )
        
        return prompt_embeddings
    
    def get_prompt_tokens(self) -> torch.Tensor:
        """Get raw prompt token embeddings."""
        return self.prompt_embeddings
    
    def set_prompt_tokens(self, new_tokens: torch.Tensor):
        """Set prompt token embeddings."""
        if new_tokens.shape != self.prompt_embeddings.shape:
            raise ValueError(f"Expected shape {self.prompt_embeddings.shape}, got {new_tokens.shape}")
        self.prompt_embeddings.data = new_tokens.clone()


class PTuningFineTuner:
    """Main P-tuning fine-tuning class."""
    
    def __init__(self, model: nn.Module, config: Dict[str, Any]):
        self.model = model
        self.config = config
        
        # Initialize P-tuning module
        self.p_tuning_module = PTuningModule(
            num_virtual_tokens=config.get('num_virtual_tokens', 20),
            token_dim=config.get('token_dim', 768),
            encoder_hidden_size=config.get('encoder_hidden_size', 128),
            encoder_num_layers=config.get('encoder_num_layers', 2),
            encoder_dropout=config.get('encoder_dropout', 0.1)
        )
        
        # Freeze base model
        self._freeze_base_model()
        
        logger.info("P-tuning fine-tuner initialized")
    
    def _freeze_base_model(self):
        """Freeze base model parameters."""
        for param in self.model.parameters():
            param.requires_grad = False
        
        # Unfreeze P-tuning parameters
        for param in self.p_tuning_module.parameters():
            param.requires_grad = True
        
        logger.info("Base model frozen, P-tuning parameters trainable")
    
    def get_trainable_parameters(self) -> List[nn.Parameter]:
        """Get trainable parameters."""
        return list(self.p_tuning_module.parameters())
    
    def get_parameter_stats(self) -> Dict[str, Any]:
        """Get parameter statistics."""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.get_trainable_parameters())
        
        return {
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'frozen_parameters': total_params - trainable_params,
            'efficiency_ratio': trainable_params / total_params,
            'compression_ratio': total_params / trainable_params,
            'virtual_tokens': self.p_tuning_module.num_virtual_tokens,
            'token_dimension': self.p_tuning_module.token_dim
        }
    
    def add_prompts_to_input(self, input_embeddings: torch.Tensor) -> torch.Tensor:
        """
        Add learnable prompts to input embeddings.
        
        Args:
            input_embeddings: Input token embeddings
            
        Returns:
            Input embeddings with prompts prepended
        """
        batch_size = input_embeddings.shape[0]
        
        # Get prompt embeddings
        prompt_embeddings = self.p_tuning_module(batch_size)
        
        # Concatenate prompts with input
        # prompt_embeddings: (batch_size, num_virtual_tokens, token_dim)
        # input_embeddings: (batch_size, seq_len, token_dim)
        # Result: (batch_size, num_virtual_tokens + seq_len, token_dim)
        combined_embeddings = torch.cat([prompt_embeddings, input_embeddings], dim=1)
        
        return combined_embeddings
    
    def extract_prompt_outputs(self, model_outputs: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Extract prompt and content outputs from model outputs.
        
        Args:
            model_outputs: Full model outputs including prompts
            
        Returns:
            Tuple of (prompt_outputs, content_outputs)
        """
        num_prompts = self.p_tuning_module.num_virtual_tokens
        
        # Split outputs
        prompt_outputs = model_outputs[:, :num_prompts, :]
        content_outputs = model_outputs[:, num_prompts:, :]
        
        return prompt_outputs, content_outputs
    
    def save_prompts(self, save_path: str):
        """Save prompt embeddings."""
        torch.save({
            'prompt_embeddings': self.p_tuning_module.prompt_embeddings.data,
            'config': self.config
        }, save_path)
        logger.info(f"Prompts saved to: {save_path}")
    
    def load_prompts(self, load_path: str):
        """Load prompt embeddings."""
        checkpoint = torch.load(load_path, map_location='cpu')
        
        if 'prompt_embeddings' in checkpoint:
            self.p_tuning_module.set_prompt_tokens(checkpoint['prompt_embeddings'])
            logger.info(f"Prompts loaded from: {load_path}")
        else:
            logger.warning("No prompt embeddings found in checkpoint")


# Example usage
if __name__ == "__main__":
    # Test configuration
    config = {
        'num_virtual_tokens': 10,
        'token_dim': 256,
        'encoder_hidden_size': 64,
        'encoder_num_layers': 2,
        'encoder_dropout': 0.1
    }
    
    # Mock model (in practice, this would be a real transformer model)
    class MockModel(nn.Module):
        def __init__(self, token_dim):
            super().__init__()
            self.token_dim = token_dim
        
        def forward(self, x):
            # Mock forward pass
            return x
    
    model = MockModel(token_dim=256)
    
    # Initialize P-tuning fine-tuner
    fine_tuner = PTuningFineTuner(model, config)
    
    # Get statistics
    stats = fine_tuner.get_parameter_stats()
    print("P-tuning Parameter Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test prompt addition
    batch_size = 4
    seq_len = 20
    input_embeddings = torch.randn(batch_size, seq_len, 256)
    
    combined_embeddings = fine_tuner.add_prompts_to_input(input_embeddings)
    print(f"\nInput shape: {input_embeddings.shape}")
    print(f"Combined shape: {combined_embeddings.shape}")
    
    print("\nP-tuning module ready!")


