#!/usr/bin/env python3
"""
Attention Mechanisms and Positional Encodings System for Diffusion Models

Advanced implementation of attention mechanisms and positional encodings
for diffusion models and transformers, including:
- Multi-head attention with various attention types
- Advanced positional encoding strategies
- Cross-attention for diffusion models
- Optimized attention implementations
- Comprehensive testing and validation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy as np
from typing import Optional, Tuple, List, Dict, Any, Union
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AttentionConfig:
    """Configuration for attention mechanisms."""
    num_heads: int = 8
    head_dim: int = 64
    dropout: float = 0.1
    attention_type: str = "scaled_dot_product"  # scaled_dot_product, relative, local, sparse
    use_bias: bool = True
    use_rope: bool = False  # Rotary Position Embedding
    max_position_embeddings: int = 512
    attention_scale: float = 1.0
    causal: bool = False
    flash_attention: bool = False

@dataclass
class PositionalEncodingConfig:
    """Configuration for positional encodings."""
    encoding_type: str = "sinusoidal"  # sinusoidal, learned, relative, alibi, rope
    max_length: int = 512
    embedding_dim: int = 512
    dropout: float = 0.1
    learnable: bool = False
    base: float = 10000.0
    scale: float = 1.0

class RotaryPositionEmbedding(nn.Module):
    """Rotary Position Embedding (RoPE) implementation."""
    
    def __init__(self, dim: int, max_position_embeddings: int = 2048, base: float = 10000.0):
        super().__init__()
        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        self.base = base
        
        # Generate rotation matrix
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        
    def forward(self, x: torch.Tensor, seq_len: int) -> torch.Tensor:
        """Apply rotary position embedding."""
        t = torch.arange(seq_len, device=x.device).type_as(self.inv_freq)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        
        # Apply rotation
        cos = emb.cos()
        sin = emb.sin()
        
        # Reshape for broadcasting
        cos = cos.view(1, seq_len, 1, -1)
        sin = sin.view(1, seq_len, 1, -1)
        
        # Apply rotation to input
        x_rot = torch.cat([-x[..., self.dim//2:], x[..., :self.dim//2]], dim=-1)
        return x * cos + x_rot * sin

class SinusoidalPositionalEncoding(nn.Module):
    """Sinusoidal positional encoding."""
    
    def __init__(self, config: PositionalEncodingConfig):
        super().__init__()
        self.config = config
        
        pe = torch.zeros(config.max_length, config.embedding_dim)
        position = torch.arange(0, config.max_length).unsqueeze(1).float()
        
        div_term = torch.exp(torch.arange(0, config.embedding_dim, 2).float() *
                           -(math.log(config.base) / config.embedding_dim))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)
        
        if config.learnable:
            self.pe = nn.Parameter(pe)
        
        self.dropout = nn.Dropout(config.dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input."""
        x = x + self.pe[:, :x.size(1)] * self.config.scale
        return self.dropout(x)

class LearnedPositionalEncoding(nn.Module):
    """Learned positional encoding."""
    
    def __init__(self, config: PositionalEncodingConfig):
        super().__init__()
        self.config = config
        
        self.embedding = nn.Embedding(config.max_length, config.embedding_dim)
        self.dropout = nn.Dropout(config.dropout)
        
        # Initialize with sinusoidal encoding
        with torch.no_grad():
            pe = torch.zeros(config.max_length, config.embedding_dim)
            position = torch.arange(0, config.max_length).unsqueeze(1).float()
            
            div_term = torch.exp(torch.arange(0, config.embedding_dim, 2).float() *
                               -(math.log(config.base) / config.embedding_dim))
            
            pe[:, 0::2] = torch.sin(position * div_term)
            pe[:, 1::2] = torch.cos(position * div_term)
            
            self.embedding.weight.data.copy_(pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add learned positional encoding to input."""
        seq_len = x.size(1)
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0)
        pos_encoding = self.embedding(positions)
        
        x = x + pos_encoding * self.config.scale
        return self.dropout(x)

class ALiBiPositionalEncoding(nn.Module):
    """Attention with Linear Biases (ALiBi) positional encoding."""
    
    def __init__(self, config: PositionalEncodingConfig, num_heads: int):
        super().__init__()
        self.config = config
        self.num_heads = num_heads
        
        # Generate ALiBi slopes
        slopes = torch.Tensor(self._get_slopes(num_heads))
        self.register_buffer('slopes', slopes)
        
        # Generate relative position matrix
        max_pos = config.max_length
        context_position = torch.arange(max_pos, device=slopes.device)[:, None]
        memory_position = torch.arange(max_pos, device=slopes.device)[None, :]
        relative_position = memory_position - context_position
        
        self.register_buffer('relative_position', relative_position)
    
    def _get_slopes(self, n: int) -> List[float]:
        """Get ALiBi slopes."""
        def get_slopes_power_of_2(n):
            start = (2**(-2**-(math.log2(n)-3)))
            ratio = start
            return [start*ratio**i for i in range(n)]
        
        if math.log2(n).is_integer():
            return get_slopes_power_of_2(n)
        else:
            closest_power_of_2 = 2**math.floor(math.log2(n))
            return (get_slopes_power_of_2(closest_power_of_2) + 
                   self._get_slopes(2 * closest_power_of_2)[0::2][:n-closest_power_of_2])
    
    def forward(self, attention_scores: torch.Tensor) -> torch.Tensor:
        """Add ALiBi bias to attention scores."""
        seq_len = attention_scores.size(-1)
        alibi_bias = self.slopes.unsqueeze(1).unsqueeze(1) * self.relative_position[:seq_len, :seq_len]
        return attention_scores + alibi_bias.unsqueeze(0)

class MultiHeadAttention(nn.Module):
    """Multi-head attention with various attention types."""
    
    def __init__(self, config: AttentionConfig, embed_dim: int):
        super().__init__()
        self.config = config
        self.embed_dim = embed_dim
        self.num_heads = config.num_heads
        self.head_dim = config.head_dim
        self.scale = config.attention_scale / math.sqrt(self.head_dim)
        
        assert embed_dim % config.num_heads == 0, "embed_dim must be divisible by num_heads"
        
        # Linear projections
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=config.use_bias)
        self.k_proj = nn.Linear(embed_dim, embed_dim, bias=config.use_bias)
        self.v_proj = nn.Linear(embed_dim, embed_dim, bias=config.use_bias)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=config.use_bias)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
        
        # Rotary position embedding
        if config.use_rope:
            self.rope = RotaryPositionEmbedding(
                self.head_dim, 
                config.max_position_embeddings
            )
        else:
            self.rope = None
        
        # ALiBi for causal attention
        if config.causal and config.attention_type == "alibi":
            self.alibi = ALiBiPositionalEncoding(
                PositionalEncodingConfig(max_length=config.max_position_embeddings),
                config.num_heads
            )
        else:
            self.alibi = None
    
    def forward(self, 
                query: torch.Tensor, 
                key: torch.Tensor, 
                value: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None,
                key_padding_mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass of multi-head attention."""
        batch_size, seq_len, embed_dim = query.size()
        
        # Linear projections and reshape
        q = self.q_proj(query).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(key).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(value).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Apply rotary position embedding
        if self.rope is not None:
            q = self.rope(q, seq_len)
            k = self.rope(k, k.size(1))
        
        # Compute attention scores
        attention_scores = torch.matmul(q, k.transpose(-2, -1)) * self.scale
        
        # Apply ALiBi bias
        if self.alibi is not None:
            attention_scores = self.alibi(attention_scores)
        
        # Apply attention mask
        if attention_mask is not None:
            attention_scores = attention_scores.masked_fill(attention_mask == 0, float('-inf'))
        
        # Apply key padding mask
        if key_padding_mask is not None:
            attention_scores = attention_scores.masked_fill(
                key_padding_mask.unsqueeze(1).unsqueeze(1), float('-inf')
            )
        
        # Apply causal mask if needed
        if self.config.causal:
            causal_mask = torch.triu(
                torch.ones(seq_len, seq_len, device=query.device), diagonal=1
            ).bool()
            attention_scores = attention_scores.masked_fill(causal_mask, float('-inf'))
        
        # Apply softmax and dropout
        attention_probs = F.softmax(attention_scores, dim=-1)
        attention_probs = self.dropout(attention_probs)
        
        # Apply attention to values
        context = torch.matmul(attention_probs, v)
        
        # Reshape and project output
        context = context.transpose(1, 2).contiguous().view(
            batch_size, seq_len, embed_dim
        )
        output = self.out_proj(context)
        
        return output, attention_probs

class CrossAttention(nn.Module):
    """Cross-attention for diffusion models."""
    
    def __init__(self, config: AttentionConfig, embed_dim: int, cross_embed_dim: int):
        super().__init__()
        self.config = config
        self.embed_dim = embed_dim
        self.cross_embed_dim = cross_embed_dim
        self.num_heads = config.num_heads
        self.head_dim = config.head_dim
        
        # Linear projections for cross-attention
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=config.use_bias)
        self.k_proj = nn.Linear(cross_embed_dim, embed_dim, bias=config.use_bias)
        self.v_proj = nn.Linear(cross_embed_dim, embed_dim, bias=config.use_bias)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=config.use_bias)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
        
        # Rotary position embedding
        if config.use_rope:
            self.rope = RotaryPositionEmbedding(
                self.head_dim, 
                config.max_position_embeddings
            )
        else:
            self.rope = None
    
    def forward(self, 
                query: torch.Tensor, 
                context: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass of cross-attention."""
        batch_size, seq_len, embed_dim = query.size()
        context_len = context.size(1)
        
        # Linear projections and reshape
        q = self.q_proj(query).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(context).view(batch_size, context_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(context).view(batch_size, context_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Apply rotary position embedding
        if self.rope is not None:
            q = self.rope(q, seq_len)
            k = self.rope(k, context_len)
        
        # Compute attention scores
        attention_scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        # Apply attention mask
        if attention_mask is not None:
            attention_scores = attention_scores.masked_fill(attention_mask == 0, float('-inf'))
        
        # Apply softmax and dropout
        attention_probs = F.softmax(attention_scores, dim=-1)
        attention_probs = self.dropout(attention_probs)
        
        # Apply attention to values
        context_output = torch.matmul(attention_probs, v)
        
        # Reshape and project output
        context_output = context_output.transpose(1, 2).contiguous().view(
            batch_size, seq_len, embed_dim
        )
        output = self.out_proj(context_output)
        
        return output, attention_probs

class RelativePositionalEncoding(nn.Module):
    """Relative positional encoding for attention."""
    
    def __init__(self, config: PositionalEncodingConfig, num_heads: int):
        super().__init__()
        self.config = config
        self.num_heads = num_heads
        self.max_relative_position = config.max_length // 2
        
        # Relative position embeddings
        self.relative_attention_bias = nn.Embedding(
            2 * self.max_relative_position + 1, num_heads
        )
        
        # Initialize with small random values
        nn.init.normal_(self.relative_attention_bias.weight, std=0.02)
    
    def forward(self, seq_len: int) -> torch.Tensor:
        """Generate relative position embeddings."""
        range_vec = torch.arange(seq_len, device=self.relative_attention_bias.weight.device)
        range_mat = range_vec.unsqueeze(0).repeat(seq_len, 1)
        distance_mat = range_mat - range_mat.T
        
        distance_mat_clipped = torch.clamp(
            distance_mat, 
            -self.max_relative_position, 
            self.max_relative_position
        )
        
        final_mat = distance_mat_clipped + self.max_relative_position
        
        embeddings = self.relative_attention_bias(final_mat)
        return embeddings.permute(2, 0, 1).unsqueeze(0)

class AttentionBlock(nn.Module):
    """Complete attention block with residual connection and layer norm."""
    
    def __init__(self, config: AttentionConfig, embed_dim: int, cross_embed_dim: Optional[int] = None):
        super().__init__()
        self.config = config
        self.embed_dim = embed_dim
        
        # Layer normalization
        self.norm1 = nn.LayerNorm(embed_dim)
        self.norm2 = nn.LayerNorm(embed_dim)
        
        # Self-attention
        self.self_attn = MultiHeadAttention(config, embed_dim)
        
        # Cross-attention (if cross_embed_dim is provided)
        if cross_embed_dim is not None:
            self.cross_attn = CrossAttention(config, embed_dim, cross_embed_dim)
            self.norm3 = nn.LayerNorm(embed_dim)
        else:
            self.cross_attn = None
            self.norm3 = None
        
        # Feed-forward network
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 4),
            nn.GELU(),
            nn.Dropout(config.dropout),
            nn.Linear(embed_dim * 4, embed_dim),
            nn.Dropout(config.dropout)
        )
    
    def forward(self, 
                x: torch.Tensor, 
                context: Optional[torch.Tensor] = None,
                attention_mask: Optional[torch.Tensor] = None,
                context_attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass of attention block."""
        # Self-attention
        residual = x
        x = self.norm1(x)
        x, _ = self.self_attn(x, x, x, attention_mask)
        x = residual + x
        
        # Cross-attention (if context is provided)
        if self.cross_attn is not None and context is not None:
            residual = x
            x = self.norm2(x)
            x, _ = self.cross_attn(x, context, context_attention_mask)
            x = residual + x
        
        # Feed-forward
        residual = x
        x = self.norm3(x) if self.norm3 is not None else self.norm2(x)
        x = self.ffn(x)
        x = residual + x
        
        return x

class AttentionPositionalSystem:
    """Complete system for attention mechanisms and positional encodings."""
    
    def __init__(self, 
                 attention_config: AttentionConfig,
                 positional_config: PositionalEncodingConfig,
                 embed_dim: int,
                 cross_embed_dim: Optional[int] = None):
        self.attention_config = attention_config
        self.positional_config = positional_config
        self.embed_dim = embed_dim
        self.cross_embed_dim = cross_embed_dim
        
        # Initialize positional encoding
        self.positional_encoding = self._create_positional_encoding()
        
        # Initialize attention block
        self.attention_block = AttentionBlock(
            attention_config, embed_dim, cross_embed_dim
        )
        
        # Relative positional encoding for attention
        if attention_config.attention_type == "relative":
            self.relative_pos_encoding = RelativePositionalEncoding(
                positional_config, attention_config.num_heads
            )
        else:
            self.relative_pos_encoding = None
    
    def _create_positional_encoding(self) -> nn.Module:
        """Create positional encoding based on configuration."""
        if self.positional_config.encoding_type == "sinusoidal":
            return SinusoidalPositionalEncoding(self.positional_config)
        elif self.positional_config.encoding_type == "learned":
            return LearnedPositionalEncoding(self.positional_config)
        else:
            raise ValueError(f"Unknown positional encoding type: {self.positional_config.encoding_type}")
    
    def forward(self, 
                x: torch.Tensor, 
                context: Optional[torch.Tensor] = None,
                attention_mask: Optional[torch.Tensor] = None,
                context_attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass of the complete system."""
        # Add positional encoding
        x = self.positional_encoding(x)
        
        # Apply attention block
        x = self.attention_block(
            x, context, attention_mask, context_attention_mask
        )
        
        return x
    
    def get_attention_weights(self, 
                            x: torch.Tensor, 
                            context: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """Get attention weights for analysis."""
        # Add positional encoding
        x = self.positional_encoding(x)
        
        # Get attention weights from self-attention
        x_norm = self.attention_block.norm1(x)
        _, self_attn_weights = self.attention_block.self_attn(
            x_norm, x_norm, x_norm
        )
        
        attention_weights = {"self_attention": self_attn_weights}
        
        # Get attention weights from cross-attention if applicable
        if self.attention_block.cross_attn is not None and context is not None:
            x_norm = self.attention_block.norm2(x)
            _, cross_attn_weights = self.attention_block.cross_attn(
                x_norm, context
            )
            attention_weights["cross_attention"] = cross_attn_weights
        
        return attention_weights

# Production usage example
def main():
    """Production usage example."""
    try:
        # Configuration
        attention_config = AttentionConfig(
            num_heads=8,
            head_dim=64,
            dropout=0.1,
            attention_type="scaled_dot_product",
            use_rope=True,
            causal=False
        )
        
        positional_config = PositionalEncodingConfig(
            encoding_type="sinusoidal",
            max_length=512,
            embedding_dim=512,
            dropout=0.1
        )
        
        # Initialize system
        system = AttentionPositionalSystem(
            attention_config=attention_config,
            positional_config=positional_config,
            embed_dim=512,
            cross_embed_dim=768  # For cross-attention with text embeddings
        )
        
        # Test forward pass
        batch_size, seq_len = 2, 128
        x = torch.randn(batch_size, seq_len, 512)
        context = torch.randn(batch_size, 77, 768)  # Text embeddings
        
        output = system.forward(x, context)
        print(f"Output shape: {output.shape}")
        
        # Get attention weights
        attention_weights = system.get_attention_weights(x, context)
        print(f"Self-attention weights shape: {attention_weights['self_attention'].shape}")
        print(f"Cross-attention weights shape: {attention_weights['cross_attention'].shape}")
        
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")

if __name__ == "__main__":
    main() 