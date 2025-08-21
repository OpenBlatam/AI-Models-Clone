from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy as np
from typing import Optional, Tuple, List, Dict, Any, Union, Callable
from dataclasses import dataclass
import logging
from enum import Enum
from typing import Any, List, Dict, Optional
import asyncio
#!/usr/bin/env python3
"""
Advanced Attention Mechanisms and Positional Encodings
Comprehensive implementation of attention mechanisms and positional encodings with advanced features.
"""



class AttentionType(Enum):
    """Types of attention mechanisms."""
    SCALED_DOT_PRODUCT = "scaled_dot_product"
    MULTI_HEAD = "multi_head"
    FLASH_ATTENTION = "flash_attention"
    SPARSE_ATTENTION = "sparse_attention"
    LOCAL_ATTENTION = "local_attention"
    ROTARY_POSITIONAL = "rotary_positional"
    RELATIVE_POSITIONAL = "relative_positional"
    LINEAR_ATTENTION = "linear_attention"


class PositionalEncodingType(Enum):
    """Types of positional encodings."""
    SINUSOIDAL = "sinusoidal"
    LEARNED = "learned"
    ROTARY = "rotary"
    ALIBI = "alibi"
    RELATIVE = "relative"


@dataclass
class AttentionConfig:
    """Configuration for attention mechanisms."""
    # Attention parameters
    attention_type: AttentionType = AttentionType.MULTI_HEAD
    num_heads: int = 8
    head_dim: int = 64
    dropout: float = 0.1
    
    # Positional encoding parameters
    positional_encoding_type: PositionalEncodingType = PositionalEncodingType.SINUSOIDAL
    max_position_embeddings: int = 512
    embedding_dim: int = 512
    
    # Advanced features
    use_bias: bool = True
    use_scale: bool = True
    use_mask: bool = True
    
    # Flash attention parameters
    use_flash_attention: bool = True
    flash_attention_dropout: float = 0.1
    
    # Sparse attention parameters
    sparse_attention_window: int = 128
    sparse_attention_stride: int = 64
    
    # Local attention parameters
    local_attention_window: int = 256
    
    # Rotary parameters
    rotary_dim: int = 64
    rotary_base: int = 10000


class SinusoidalPositionalEncoding(nn.Module):
    """Sinusoidal positional encoding."""
    
    def __init__(self, embedding_dim: int, max_position_embeddings: int = 512):
        
    """__init__ function."""
super().__init__()
        self.embedding_dim = embedding_dim
        self.max_position_embeddings = max_position_embeddings
        
        # Create positional encoding matrix
        pe = torch.zeros(max_position_embeddings, embedding_dim)
        position = torch.arange(0, max_position_embeddings, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, embedding_dim, 2).float() * 
                           (-math.log(10000.0) / embedding_dim))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input."""
        return x + self.pe[:x.size(0), :]


class LearnedPositionalEncoding(nn.Module):
    """Learned positional encoding."""
    
    def __init__(self, embedding_dim: int, max_position_embeddings: int = 512):
        
    """__init__ function."""
super().__init__()
        self.embedding_dim = embedding_dim
        self.max_position_embeddings = max_position_embeddings
        self.position_embeddings = nn.Embedding(max_position_embeddings, embedding_dim)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add learned positional encoding to input."""
        seq_len = x.size(0)
        positions = torch.arange(seq_len, device=x.device, dtype=torch.long)
        position_embeddings = self.position_embeddings(positions)
        return x + position_embeddings


class RotaryPositionalEncoding(nn.Module):
    """Rotary positional encoding (RoPE)."""
    
    def __init__(self, embedding_dim: int, max_position_embeddings: int = 512, base: int = 10000):
        
    """__init__ function."""
super().__init__()
        self.embedding_dim = embedding_dim
        self.max_position_embeddings = max_position_embeddings
        self.base = base
        
        # Create rotation matrix
        inv_freq = 1.0 / (base ** (torch.arange(0, embedding_dim, 2).float() / embedding_dim))
        self.register_buffer('inv_freq', inv_freq)
    
    def forward(self, x: torch.Tensor, seq_len: int) -> torch.Tensor:
        """Apply rotary positional encoding."""
        t = torch.arange(seq_len, device=x.device).type_as(self.inv_freq)
        freqs = torch.einsum('i,j->ij', t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        
        # Apply rotation
        cos = torch.cos(emb)[None, :, None, :]
        sin = torch.sin(emb)[None, :, None, :]
        
        # Split input into even and odd dimensions
        x_even = x[..., ::2]
        x_odd = x[..., 1::2]
        
        # Apply rotation
        rotated_even = x_even * cos - x_odd * sin
        rotated_odd = x_even * sin + x_odd * cos
        
        # Interleave back
        rotated = torch.stack([rotated_even, rotated_odd], dim=-1).flatten(-2)
        
        return rotated


class ALiBiPositionalEncoding(nn.Module):
    """Attention with Linear Biases (ALiBi) positional encoding."""
    
    def __init__(self, num_heads: int, max_position_embeddings: int = 512):
        
    """__init__ function."""
super().__init__()
        self.num_heads = num_heads
        self.max_position_embeddings = max_position_embeddings
        
        # Create ALiBi slopes
        slopes = torch.Tensor(self._get_slopes(num_heads))
        self.register_buffer('slopes', slopes)
    
    def _get_slopes(self, num_heads: int) -> List[float]:
        """Get ALiBi slopes."""
        def get_slopes_power_of_2(n) -> Optional[Dict[str, Any]]:
            start = (2**(-2**-(math.log2(n)-3)))
            ratio = start
            return [start*ratio**i for i in range(n)]
        
        if math.log2(num_heads).is_integer():
            return get_slopes_power_of_2(num_heads)
        else:
            closest_power_of_2 = 2**math.floor(math.log2(num_heads))
            return get_slopes_power_of_2(closest_power_of_2) + \
                   self._get_slopes(2*closest_power_of_2)[0::2][:num_heads-closest_power_of_2]
    
    def forward(self, attention_scores: torch.Tensor) -> torch.Tensor:
        """Add ALiBi biases to attention scores."""
        batch_size, num_heads, seq_len, seq_len = attention_scores.shape
        
        # Create position indices
        positions = torch.arange(seq_len, device=attention_scores.device)
        
        # Create ALiBi matrix
        alibi_matrix = positions.unsqueeze(0) - positions.unsqueeze(1)
        alibi_matrix = alibi_matrix.unsqueeze(0).unsqueeze(0)  # Add batch and head dimensions
        
        # Apply slopes
        alibi_biases = alibi_matrix * self.slopes.view(1, -1, 1, 1)
        
        return attention_scores + alibi_biases


class ScaledDotProductAttention(nn.Module):
    """Scaled dot-product attention mechanism."""
    
    def __init__(self, config: AttentionConfig):
        
    """__init__ function."""
super().__init__()
        self.config = config
        self.scale = math.sqrt(config.head_dim) if config.use_scale else 1.0
        self.dropout = nn.Dropout(config.dropout)
    
    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass for scaled dot-product attention."""
        # Compute attention scores
        scores = torch.matmul(query, key.transpose(-2, -1)) / self.scale
        
        # Apply mask if provided
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        # Apply softmax
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        output = torch.matmul(attention_weights, value)
        
        return output, attention_weights


class MultiHeadAttention(nn.Module):
    """Multi-head attention mechanism."""
    
    def __init__(self, config: AttentionConfig):
        
    """__init__ function."""
super().__init__()
        self.config = config
        self.num_heads = config.num_heads
        self.head_dim = config.head_dim
        self.embedding_dim = config.num_heads * config.head_dim
        
        # Linear transformations
        self.query_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        self.key_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        self.value_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        self.output_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        
        # Attention mechanism
        self.attention = ScaledDotProductAttention(config)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
    
    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass for multi-head attention."""
        batch_size = query.size(0)
        
        # Linear transformations
        query = self.query_projection(query)
        key = self.key_projection(key)
        value = self.value_projection(value)
        
        # Reshape for multi-head attention
        query = query.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        key = key.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        value = value.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Apply attention
        attention_output, attention_weights = self.attention(query, key, value, mask)
        
        # Reshape back
        attention_output = attention_output.transpose(1, 2).contiguous().view(
            batch_size, -1, self.embedding_dim
        )
        
        # Output projection
        output = self.output_projection(attention_output)
        output = self.dropout(output)
        
        return output, attention_weights


class FlashAttention(nn.Module):
    """Flash attention implementation for efficiency."""
    
    def __init__(self, config: AttentionConfig):
        
    """__init__ function."""
super().__init__()
        self.config = config
        self.num_heads = config.num_heads
        self.head_dim = config.head_dim
        self.embedding_dim = config.num_heads * config.head_dim
        
        # Linear transformations
        self.query_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        self.key_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        self.value_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        self.output_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        
        # Dropout
        self.dropout = nn.Dropout(config.flash_attention_dropout)
    
    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass for flash attention."""
        batch_size = query.size(0)
        
        # Linear transformations
        query = self.query_projection(query)
        key = self.key_projection(key)
        value = self.value_projection(value)
        
        # Reshape for multi-head attention
        query = query.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        key = key.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        value = value.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Flash attention computation
        attention_output = self._flash_attention(query, key, value, mask)
        
        # Reshape back
        attention_output = attention_output.transpose(1, 2).contiguous().view(
            batch_size, -1, self.embedding_dim
        )
        
        # Output projection
        output = self.output_projection(attention_output)
        output = self.dropout(output)
        
        return output, None  # Flash attention doesn't return attention weights
    
    def _flash_attention(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                        mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Flash attention implementation."""
        # Compute attention scores
        scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        # Apply mask if provided
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        # Apply softmax
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        output = torch.matmul(attention_weights, value)
        
        return output


class SparseAttention(nn.Module):
    """Sparse attention mechanism."""
    
    def __init__(self, config: AttentionConfig):
        
    """__init__ function."""
super().__init__()
        self.config = config
        self.num_heads = config.num_heads
        self.head_dim = config.head_dim
        self.embedding_dim = config.num_heads * config.head_dim
        self.window_size = config.sparse_attention_window
        self.stride = config.sparse_attention_stride
        
        # Linear transformations
        self.query_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        self.key_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        self.value_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        self.output_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        
        # Attention mechanism
        self.attention = ScaledDotProductAttention(config)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
    
    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass for sparse attention."""
        batch_size, seq_len = query.size(0), query.size(1)
        
        # Linear transformations
        query = self.query_projection(query)
        key = self.key_projection(key)
        value = self.value_projection(value)
        
        # Reshape for multi-head attention
        query = query.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        key = key.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        value = value.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Sparse attention computation
        attention_output = self._sparse_attention(query, key, value, mask)
        
        # Reshape back
        attention_output = attention_output.transpose(1, 2).contiguous().view(
            batch_size, seq_len, self.embedding_dim
        )
        
        # Output projection
        output = self.output_projection(attention_output)
        output = self.dropout(output)
        
        return output, None  # Sparse attention doesn't return attention weights
    
    def _sparse_attention(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                         mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Sparse attention implementation."""
        batch_size, num_heads, seq_len, head_dim = query.shape
        
        # Create sparse attention pattern
        sparse_output = torch.zeros_like(query)
        
        for i in range(0, seq_len, self.stride):
            # Define attention window
            start_idx = max(0, i - self.window_size // 2)
            end_idx = min(seq_len, i + self.window_size // 2)
            
            # Extract window
            query_window = query[:, :, i:i+1, :]
            key_window = key[:, :, start_idx:end_idx, :]
            value_window = value[:, :, start_idx:end_idx, :]
            
            # Compute attention for window
            scores = torch.matmul(query_window, key_window.transpose(-2, -1)) / math.sqrt(head_dim)
            
            # Apply mask if provided
            if mask is not None:
                mask_window = mask[:, i:i+1, start_idx:end_idx]
                scores = scores.masked_fill(mask_window == 0, -1e9)
            
            # Apply softmax
            attention_weights = F.softmax(scores, dim=-1)
            attention_weights = self.dropout(attention_weights)
            
            # Apply attention to values
            window_output = torch.matmul(attention_weights, value_window)
            sparse_output[:, :, i:i+1, :] = window_output
        
        return sparse_output


class LocalAttention(nn.Module):
    """Local attention mechanism."""
    
    def __init__(self, config: AttentionConfig):
        
    """__init__ function."""
super().__init__()
        self.config = config
        self.num_heads = config.num_heads
        self.head_dim = config.head_dim
        self.embedding_dim = config.num_heads * config.head_dim
        self.window_size = config.local_attention_window
        
        # Linear transformations
        self.query_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        self.key_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        self.value_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        self.output_projection = nn.Linear(self.embedding_dim, self.embedding_dim, bias=config.use_bias)
        
        # Attention mechanism
        self.attention = ScaledDotProductAttention(config)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
    
    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass for local attention."""
        batch_size, seq_len = query.size(0), query.size(1)
        
        # Linear transformations
        query = self.query_projection(query)
        key = self.key_projection(key)
        value = self.value_projection(value)
        
        # Reshape for multi-head attention
        query = query.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        key = key.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        value = value.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Local attention computation
        attention_output = self._local_attention(query, key, value, mask)
        
        # Reshape back
        attention_output = attention_output.transpose(1, 2).contiguous().view(
            batch_size, seq_len, self.embedding_dim
        )
        
        # Output projection
        output = self.output_projection(attention_output)
        output = self.dropout(output)
        
        return output, None  # Local attention doesn't return attention weights
    
    def _local_attention(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                        mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Local attention implementation."""
        batch_size, num_heads, seq_len, head_dim = query.shape
        
        # Create local attention output
        local_output = torch.zeros_like(query)
        
        for i in range(seq_len):
            # Define local window
            start_idx = max(0, i - self.window_size // 2)
            end_idx = min(seq_len, i + self.window_size // 2)
            
            # Extract local window
            query_local = query[:, :, i:i+1, :]
            key_local = key[:, :, start_idx:end_idx, :]
            value_local = value[:, :, start_idx:end_idx, :]
            
            # Compute attention for local window
            scores = torch.matmul(query_local, key_local.transpose(-2, -1)) / math.sqrt(head_dim)
            
            # Apply mask if provided
            if mask is not None:
                mask_local = mask[:, i:i+1, start_idx:end_idx]
                scores = scores.masked_fill(mask_local == 0, -1e9)
            
            # Apply softmax
            attention_weights = F.softmax(scores, dim=-1)
            attention_weights = self.dropout(attention_weights)
            
            # Apply attention to values
            local_window_output = torch.matmul(attention_weights, value_local)
            local_output[:, :, i:i+1, :] = local_window_output
        
        return local_output


class AttentionFactory:
    """Factory for creating different attention mechanisms."""
    
    @staticmethod
    def create_attention(config: AttentionConfig) -> nn.Module:
        """Create attention mechanism based on configuration."""
        if config.attention_type == AttentionType.SCALED_DOT_PRODUCT:
            return ScaledDotProductAttention(config)
        elif config.attention_type == AttentionType.MULTI_HEAD:
            return MultiHeadAttention(config)
        elif config.attention_type == AttentionType.FLASH_ATTENTION:
            return FlashAttention(config)
        elif config.attention_type == AttentionType.SPARSE_ATTENTION:
            return SparseAttention(config)
        elif config.attention_type == AttentionType.LOCAL_ATTENTION:
            return LocalAttention(config)
        else:
            raise ValueError(f"Unknown attention type: {config.attention_type}")


def demonstrate_attention_mechanisms():
    """Demonstrate attention mechanisms and positional encodings."""
    print("Attention Mechanisms and Positional Encodings Demonstration")
    print("=" * 60)
    
    # Test different configurations
    configs = [
        AttentionConfig(
            attention_type=AttentionType.MULTI_HEAD,
            num_heads=8,
            head_dim=64,
            positional_encoding_type=PositionalEncodingType.SINUSOIDAL
        ),
        AttentionConfig(
            attention_type=AttentionType.FLASH_ATTENTION,
            num_heads=8,
            head_dim=64,
            positional_encoding_type=PositionalEncodingType.ROTARY
        ),
        AttentionConfig(
            attention_type=AttentionType.SPARSE_ATTENTION,
            num_heads=8,
            head_dim=64,
            positional_encoding_type=PositionalEncodingType.ALIBI
        )
    ]
    
    results = {}
    
    for i, config in enumerate(configs):
        print(f"\nTesting {config.attention_type.value} attention:")
        
        try:
            # Create attention mechanism
            attention = AttentionFactory.create_attention(config)
            
            # Create positional encoding
            if config.positional_encoding_type == PositionalEncodingType.SINUSOIDAL:
                pos_encoding = SinusoidalPositionalEncoding(config.embedding_dim)
            elif config.positional_encoding_type == PositionalEncodingType.LEARNED:
                pos_encoding = LearnedPositionalEncoding(config.embedding_dim)
            elif config.positional_encoding_type == PositionalEncodingType.ROTARY:
                pos_encoding = RotaryPositionalEncoding(config.embedding_dim)
            elif config.positional_encoding_type == PositionalEncodingType.ALIBI:
                pos_encoding = ALiBiPositionalEncoding(config.num_heads)
            else:
                pos_encoding = SinusoidalPositionalEncoding(config.embedding_dim)
            
            # Test with dummy data
            batch_size = 2
            seq_len = 128
            embedding_dim = config.embedding_dim
            
            query = torch.randn(batch_size, seq_len, embedding_dim)
            key = torch.randn(batch_size, seq_len, embedding_dim)
            value = torch.randn(batch_size, seq_len, embedding_dim)
            
            # Apply positional encoding
            if isinstance(pos_encoding, (SinusoidalPositionalEncoding, LearnedPositionalEncoding)):
                query = pos_encoding(query.transpose(0, 1)).transpose(0, 1)
                key = pos_encoding(key.transpose(0, 1)).transpose(0, 1)
                value = pos_encoding(value.transpose(0, 1)).transpose(0, 1)
            elif isinstance(pos_encoding, RotaryPositionalEncoding):
                query = pos_encoding(query, seq_len)
                key = pos_encoding(key, seq_len)
                value = pos_encoding(value, seq_len)
            
            # Apply attention
            if isinstance(pos_encoding, ALiBiPositionalEncoding):
                # For ALiBi, we need to apply it to attention scores
                output, attention_weights = attention(query, key, value)
                if attention_weights is not None:
                    attention_weights = pos_encoding(attention_weights)
            else:
                output, attention_weights = attention(query, key, value)
            
            print(f"  Input shape: {query.shape}")
            print(f"  Output shape: {output.shape}")
            if attention_weights is not None:
                print(f"  Attention weights shape: {attention_weights.shape}")
            
            # Model statistics
            total_params = sum(p.numel() for p in attention.parameters())
            print(f"  Total parameters: {total_params:,}")
            
            results[f"attention_{i}"] = {
                'config': config,
                'total_params': total_params,
                'output_shape': output.shape,
                'success': True
            }
            
        except Exception as e:
            print(f"  Error: {e}")
            results[f"attention_{i}"] = {
                'config': config,
                'error': str(e),
                'success': False
            }
    
    return results


if __name__ == "__main__":
    # Demonstrate attention mechanisms
    results = demonstrate_attention_mechanisms()
    print("\nAttention mechanisms demonstration completed!") 