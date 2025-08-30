"""
Enhanced Transformer Models for HeyGen AI

This module provides enhanced transformer models with advanced features:
- Multi-head attention with optimized implementations
- Positional encoding
- LoRA support for efficient fine-tuning
- Ultra performance optimizations
- Comprehensive training utilities
"""

import logging
import math
import warnings
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import Parameter
from torch.cuda.amp import autocast
import numpy as np

from transformers import (
    AutoTokenizer, 
    AutoModel, 
    AutoModelForCausalLM,
    PreTrainedModel,
    PreTrainedTokenizer
)

# Import ultra performance optimizer
from .ultra_performance_optimizer import (
    UltraPerformanceOptimizer,
    UltraPerformanceConfig
)

logger = logging.getLogger(__name__)


@dataclass
class TransformerConfig:
    """Configuration for transformer models."""
    
    # Model Architecture
    vocab_size: int = 50257
    hidden_size: int = 768
    num_layers: int = 12
    num_attention_heads: int = 12
    intermediate_size: int = 3072
    max_position_embeddings: int = 1024
    dropout: float = 0.1
    attention_dropout: float = 0.1
    activation_function: str = "gelu"  # gelu, relu, swish
    
    # LoRA Configuration
    enable_lora: bool = False
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    
    # Performance Settings
    enable_ultra_performance: bool = True
    performance_mode: str = "balanced"  # maximum, balanced, memory-efficient
    enable_torch_compile: bool = True
    enable_flash_attention: bool = True
    enable_memory_optimization: bool = True
    enable_attention_slicing: bool = False
    enable_gradient_checkpointing: bool = False
    
    # Training Settings
    mixed_precision: bool = True
    dtype: str = "fp16"  # fp16, bf16, fp32


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer models."""
    
    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input."""
        return x + self.pe[:x.size(0), :]


class MultiHeadAttention(nn.Module):
    """Multi-head attention with performance optimizations."""
    
    def __init__(
        self,
        hidden_size: int,
        num_attention_heads: int,
        dropout: float = 0.1,
        enable_flash_attention: bool = True
    ):
        super().__init__()
        
        self.hidden_size = hidden_size
        self.num_attention_heads = num_attention_heads
        self.head_dim = hidden_size // num_attention_heads
        self.enable_flash_attention = enable_flash_attention
        
        assert hidden_size % num_attention_heads == 0, "hidden_size must be divisible by num_attention_heads"
        
        self.q_proj = nn.Linear(hidden_size, hidden_size)
        self.k_proj = nn.Linear(hidden_size, hidden_size)
        self.v_proj = nn.Linear(hidden_size, hidden_size)
        self.out_proj = nn.Linear(hidden_size, hidden_size)
        self.dropout = nn.Dropout(dropout)
        
        # Try to import flash attention
        self.flash_attn_available = False
        if enable_flash_attention:
            try:
                import flash_attn
                self.flash_attn_available = True
                logger.info("Flash Attention available for MultiHeadAttention")
            except ImportError:
                logger.warning("Flash Attention not available, using standard attention")
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor, torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        """Forward pass with optional flash attention."""
        batch_size, seq_len, hidden_size = query.size()
        
        # Project queries, keys, and values
        q = self.q_proj(query).view(batch_size, seq_len, self.num_attention_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(key).view(batch_size, seq_len, self.num_attention_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(value).view(batch_size, seq_len, self.num_attention_heads, self.head_dim).transpose(1, 2)
        
        # Handle past key-value states
        if past_key_value is not None:
            past_k, past_v = past_key_value
            k = torch.cat([past_k, k], dim=2)
            v = torch.cat([past_v, v], dim=2)
        
        # Use flash attention if available and conditions are met
        if (self.flash_attn_available and 
            self.enable_flash_attention and 
            attention_mask is None and 
            query.dtype in [torch.float16, torch.bfloat16]):
            
            try:
                import flash_attn
                # Flash attention expects (batch, seqlen, nheads, headdim)
                q_flash = q.transpose(1, 2)
                k_flash = k.transpose(1, 2)
                v_flash = v.transpose(1, 2)
                
                output = flash_attn.flash_attn_func(q_flash, k_flash, v_flash, dropout_p=self.dropout.p)
                output = output.transpose(1, 2)  # Back to (batch, nheads, seqlen, headdim)
                
                # Reshape and project output
                output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, hidden_size)
                output = self.out_proj(output)
                
                return output, (k, v)
                
            except Exception as e:
                logger.warning(f"Flash attention failed, falling back to standard: {e}")
                self.flash_attn_available = False
        
        # Standard attention computation
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        if attention_mask is not None:
            scores = scores + attention_mask
        
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        attn_output = torch.matmul(attn_weights, v)
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, seq_len, hidden_size)
        attn_output = self.out_proj(attn_output)
        
        return attn_output, (k, v)


class TransformerBlock(nn.Module):
    """Transformer block with performance optimizations."""
    
    def __init__(
        self,
        hidden_size: int,
        num_attention_heads: int,
        intermediate_size: int,
        dropout: float = 0.1,
        activation_function: str = "gelu",
        enable_flash_attention: bool = True,
        enable_gradient_checkpointing: bool = False
    ):
        super().__init__()
        
        self.hidden_size = hidden_size
        self.enable_gradient_checkpointing = enable_gradient_checkpointing
        
        # Layer normalization
        self.input_layernorm = nn.LayerNorm(hidden_size)
        self.post_attention_layernorm = nn.LayerNorm(hidden_size)
        
        # Multi-head attention
        self.attention = MultiHeadAttention(
            hidden_size=hidden_size,
            num_attention_heads=num_attention_heads,
            dropout=dropout,
            enable_flash_attention=enable_flash_attention
        )
        
        # Feed-forward network
        self.mlp = nn.Sequential(
            nn.Linear(hidden_size, intermediate_size),
            self._get_activation(activation_function),
            nn.Dropout(dropout),
            nn.Linear(intermediate_size, hidden_size),
            nn.Dropout(dropout)
        )
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
    
    def _get_activation(self, activation_function: str) -> nn.Module:
        """Get activation function."""
        if activation_function == "gelu":
            return nn.GELU()
        elif activation_function == "relu":
            return nn.ReLU()
        elif activation_function == "swish":
            return nn.SiLU()
        else:
            return nn.GELU()
    
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor, torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        """Forward pass with optional gradient checkpointing."""
        if self.enable_gradient_checkpointing and self.training:
            return self._gradient_checkpointing_forward(hidden_states, attention_mask, past_key_value)
        
        return self._forward_impl(hidden_states, attention_mask, past_key_value)
    
    def _forward_impl(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor, torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        """Implementation of forward pass."""
        # Self-attention
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        
        attention_output, present_key_value = self.attention(
            hidden_states, hidden_states, hidden_states, attention_mask, past_key_value
        )
        attention_output = self.dropout(attention_output)
        hidden_states = residual + attention_output
        
        # Feed-forward
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states
        
        return hidden_states, present_key_value
    
    def _gradient_checkpointing_forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor, torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        """Forward pass with gradient checkpointing."""
        def create_custom_forward(module):
            def custom_forward(*inputs):
                return module._forward_impl(*inputs)
            return custom_forward
        
        return torch.utils.checkpoint.checkpoint(
            create_custom_forward(self),
            hidden_states,
            attention_mask,
            past_key_value,
            use_reentrant=False
        )


class TransformerModel(nn.Module):
    """Enhanced transformer model with ultra performance optimizations."""
    
    def __init__(self, config: TransformerConfig):
        super().__init__()
        
        self.config = config
        self.hidden_size = config.hidden_size
        self.num_layers = config.num_layers
        
        # Token embeddings
        self.token_embedding = nn.Embedding(config.vocab_size, config.hidden_size)
        
        # Positional encoding
        self.positional_encoding = PositionalEncoding(config.hidden_size, config.max_position_embeddings)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
        
        # Transformer blocks
        self.layers = nn.ModuleList([
            TransformerBlock(
                hidden_size=config.hidden_size,
                num_attention_heads=config.num_attention_heads,
                intermediate_size=config.intermediate_size,
                dropout=config.dropout,
                activation_function=config.activation_function,
                enable_flash_attention=config.enable_flash_attention,
                enable_gradient_checkpointing=config.enable_gradient_checkpointing
            )
            for _ in range(config.num_layers)
        ])
        
        # Final layer normalization
        self.final_layernorm = nn.LayerNorm(config.hidden_size)
        
        # Language model head
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        
        # Initialize weights
        self._init_weights()
        
        # Ultra performance optimizer
        self.ultra_performance_optimizer = None
        if config.enable_ultra_performance:
            self._setup_ultra_performance()
    
    def _setup_ultra_performance(self):
        """Setup ultra performance optimizations."""
        try:
            performance_config = UltraPerformanceConfig(
                enable_torch_compile=self.config.enable_torch_compile,
                enable_flash_attention=self.config.enable_flash_attention,
                enable_memory_efficient_forward=self.config.enable_memory_optimization,
                enable_attention_slicing=self.config.enable_attention_slicing,
                enable_gradient_checkpointing=self.config.enable_gradient_checkpointing
            )
            
            self.ultra_performance_optimizer = UltraPerformanceOptimizer(
                config=performance_config,
                device=next(self.parameters()).device
            )
            
            logger.info("Ultra performance optimizations enabled for TransformerModel")
            
        except Exception as e:
            logger.warning(f"Failed to setup ultra performance optimizations: {e}")
            self.ultra_performance_optimizer = None
    
    def _init_weights(self):
        """Initialize model weights."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if module.bias is not None:
                    torch.nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            elif isinstance(module, nn.LayerNorm):
                torch.nn.init.zeros_(module.bias)
                torch.nn.init.ones_(module.weight)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_values: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = None,
        use_cache: bool = False
    ) -> Dict[str, torch.Tensor]:
        """Forward pass with ultra performance optimizations."""
        batch_size, seq_len = input_ids.size()
        
        # Get device
        device = input_ids.device
        
        # Create attention mask if not provided
        if attention_mask is None:
            attention_mask = torch.ones(batch_size, seq_len, device=device)
        
        # Convert attention mask to causal mask for language modeling
        causal_mask = torch.triu(
            torch.ones(seq_len, seq_len, device=device, dtype=torch.bool),
            diagonal=1
        )
        attention_mask = attention_mask.masked_fill(causal_mask, 0)
        
        # Embeddings
        hidden_states = self.token_embedding(input_ids)
        hidden_states = self.positional_encoding(hidden_states.transpose(0, 1)).transpose(0, 1)
        hidden_states = self.dropout(hidden_states)
        
        # Apply ultra performance optimizations if available
        if self.ultra_performance_optimizer:
            try:
                hidden_states = self.ultra_performance_optimizer.optimize_forward_pass(
                    hidden_states, attention_mask
                )
            except Exception as e:
                logger.warning(f"Failed to apply ultra performance optimizations: {e}")
        
        # Transformer layers
        present_key_values = [] if use_cache else None
        
        for i, layer in enumerate(self.layers):
            past_key_value = past_key_values[i] if past_key_values is not None else None
            
            hidden_states, present_key_value = layer(
                hidden_states, attention_mask, past_key_value
            )
            
            if use_cache:
                present_key_values.append(present_key_value)
        
        # Final layer normalization
        hidden_states = self.final_layernorm(hidden_states)
        
        # Language model head
        logits = self.lm_head(hidden_states)
        
        # Calculate loss if labels are provided
        loss = None
        if hasattr(self, 'labels') and self.labels is not None:
            # Shift logits and labels for next token prediction
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = self.labels[..., 1:].contiguous()
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
        
        return {
            "loss": loss,
            "logits": logits,
            "hidden_states": hidden_states,
            "past_key_values": present_key_values
        }
    
    def generate(
        self,
        input_ids: torch.Tensor,
        max_length: int = 100,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 0.9,
        do_sample: bool = True,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[int] = None
    ) -> torch.Tensor:
        """Generate text with the model."""
        self.eval()
        
        with torch.no_grad():
            current_ids = input_ids.clone()
            
            for _ in range(max_length - input_ids.size(1)):
                # Get model outputs
                outputs = self(current_ids)
                next_token_logits = outputs["logits"][:, -1, :] / temperature
                
                # Apply top-k and top-p filtering
                if top_k > 0:
                    top_k_logits, top_k_indices = torch.topk(next_token_logits, top_k)
                    next_token_logits = torch.full_like(next_token_logits, float('-inf'))
                    next_token_logits.scatter_(1, top_k_indices, top_k_logits)
                
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    
                    indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                    next_token_logits[indices_to_remove] = float('-inf')
                
                # Sample next token
                if do_sample:
                    probs = F.softmax(next_token_logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)
                else:
                    next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
                
                # Append next token
                current_ids = torch.cat([current_ids, next_token], dim=1)
                
                # Check for end of sequence
                if eos_token_id is not None and (next_token == eos_token_id).any():
                    break
            
            return current_ids
    
    def apply_lora(self, lora_config: Dict[str, Any]):
        """Apply LoRA to the model."""
        if not self.config.enable_lora:
            logger.warning("LoRA not enabled in config")
            return
        
        try:
            from peft import get_peft_model, LoraConfig, TaskType
            
            peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=self.config.lora_rank,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                target_modules=["q_proj", "v_proj", "k_proj", "out_proj"]
            )
            
            self.lora_model = get_peft_model(self, peft_config)
            logger.info("LoRA applied successfully")
            
        except ImportError:
            logger.error("PEFT library not available for LoRA")
        except Exception as e:
            logger.error(f"Failed to apply LoRA: {e}")
    
    def setup_training(self, config: Dict[str, Any]):
        """Setup training configuration."""
        # Enable gradient checkpointing if specified
        if config.get("enable_gradient_checkpointing", False):
            self.gradient_checkpointing_enable()
            logger.info("Gradient checkpointing enabled")
        
        # Apply ultra performance optimizations
        if self.ultra_performance_optimizer:
            try:
                self.ultra_performance_optimizer.pre_training_optimization(self)
                logger.info("Pre-training optimizations applied")
            except Exception as e:
                logger.warning(f"Failed to apply pre-training optimizations: {e}")
    
    def gradient_checkpointing_enable(self):
        """Enable gradient checkpointing."""
        self.config.enable_gradient_checkpointing = True
        for layer in self.layers:
            layer.enable_gradient_checkpointing = True
    
    def get_trainable_parameters(self) -> List[Parameter]:
        """Get trainable parameters."""
        return [p for p in self.parameters() if p.requires_grad]
    
    def count_parameters(self) -> Dict[str, int]:
        """Count model parameters."""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        return {
            "total": total_params,
            "trainable": trainable_params,
            "non_trainable": total_params - trainable_params
        }


# Factory functions for different model configurations
def create_gpt2_model(
    model_size: str = "base",
    enable_ultra_performance: bool = True,
    enable_lora: bool = False
) -> TransformerModel:
    """Create a GPT-2 style model."""
    size_configs = {
        "small": {"hidden_size": 768, "num_layers": 12, "num_attention_heads": 12},
        "base": {"hidden_size": 768, "num_layers": 12, "num_attention_heads": 12},
        "medium": {"hidden_size": 1024, "num_layers": 24, "num_attention_heads": 16},
        "large": {"hidden_size": 1280, "num_layers": 36, "num_attention_heads": 20},
        "xl": {"hidden_size": 1600, "num_layers": 48, "num_attention_heads": 25}
    }
    
    config_dict = size_configs.get(model_size, size_configs["base"])
    
    config = TransformerConfig(
        vocab_size=50257,
        hidden_size=config_dict["hidden_size"],
        num_layers=config_dict["num_layers"],
        num_attention_heads=config_dict["num_attention_heads"],
        intermediate_size=config_dict["hidden_size"] * 4,
        enable_ultra_performance=enable_ultra_performance,
        enable_lora=enable_lora
    )
    
    return TransformerModel(config)


def create_bert_model(
    model_size: str = "base",
    enable_ultra_performance: bool = True,
    enable_lora: bool = False
) -> TransformerModel:
    """Create a BERT style model."""
    size_configs = {
        "tiny": {"hidden_size": 312, "num_layers": 6, "num_attention_heads": 12},
        "mini": {"hidden_size": 384, "num_layers": 6, "num_attention_heads": 12},
        "small": {"hidden_size": 512, "num_layers": 6, "num_attention_heads": 8},
        "base": {"hidden_size": 768, "num_layers": 12, "num_attention_heads": 12},
        "large": {"hidden_size": 1024, "num_layers": 24, "num_attention_heads": 16}
    }
    
    config_dict = size_configs.get(model_size, size_configs["base"])
    
    config = TransformerConfig(
        vocab_size=30522,
        hidden_size=config_dict["hidden_size"],
        num_layers=config_dict["num_layers"],
        num_attention_heads=config_dict["num_attention_heads"],
        intermediate_size=config_dict["hidden_size"] * 4,
        enable_ultra_performance=enable_ultra_performance,
        enable_lora=enable_lora
    )
    
    return TransformerModel(config)


def create_custom_transformer(
    vocab_size: int,
    hidden_size: int,
    num_layers: int,
    num_attention_heads: int,
    enable_ultra_performance: bool = True,
    enable_lora: bool = False,
    **kwargs
) -> TransformerModel:
    """Create a custom transformer model."""
    config = TransformerConfig(
        vocab_size=vocab_size,
        hidden_size=hidden_size,
        num_layers=num_layers,
        num_attention_heads=num_attention_heads,
        enable_ultra_performance=enable_ultra_performance,
        enable_lora=enable_lora,
        **kwargs
    )
    
    return TransformerModel(config)


# Example usage
if __name__ == "__main__":
    # Create a GPT-2 style model
    model = create_gpt2_model("base", enable_ultra_performance=True)
    
    # Print model info
    param_counts = model.count_parameters()
    print(f"Model created successfully!")
    print(f"Total parameters: {param_counts['total']:,}")
    print(f"Trainable parameters: {param_counts['trainable']:,}")
    
    # Test forward pass
    batch_size, seq_len = 2, 10
    input_ids = torch.randint(0, 50257, (batch_size, seq_len))
    
    with torch.no_grad():
        outputs = model(input_ids)
        print(f"Output shape: {outputs['logits'].shape}")
        print(f"Loss: {outputs['loss']}")
