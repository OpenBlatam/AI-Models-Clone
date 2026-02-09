# ATTENTION MECHANISMS AND POSITIONAL ENCODINGS

# ============================================================================
# CORRECT ATTENTION MECHANISMS IMPLEMENTATION
# ============================================================================

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass

class ScaledDotProductAttention(nn.Module):
    """Scaled Dot-Product Attention with proper masking."""
    
    def __init__(self, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None, temperature: float = 1.0) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of scaled dot-product attention.
        
        Args:
            query: Query tensor [batch_size, seq_len, d_model] or [batch_size, num_heads, seq_len, d_k]
            key: Key tensor [batch_size, seq_len, d_model] or [batch_size, num_heads, seq_len, d_k]
            value: Value tensor [batch_size, seq_len, d_model] or [batch_size, num_heads, seq_len, d_v]
            mask: Attention mask [batch_size, seq_len, seq_len] or [batch_size, num_heads, seq_len, seq_len]
            temperature: Temperature for scaling attention scores
        
        Returns:
            Tuple of (attention_output, attention_weights)
        """
        d_k = query.size(-1)
        
        # Compute attention scores
        scores = torch.matmul(query, key.transpose(-2, -1)) / (math.sqrt(d_k) * temperature)
        
        # Apply mask if provided
        if mask is not None:
            # Handle different mask dimensions
            if mask.dim() == 3 and scores.dim() == 4:
                # Broadcast mask to match scores dimensions
                mask = mask.unsqueeze(1)  # [batch_size, 1, seq_len, seq_len]
            elif mask.dim() == 2 and scores.dim() == 4:
                # Expand mask for batch and head dimensions
                mask = mask.unsqueeze(0).unsqueeze(0)  # [1, 1, seq_len, seq_len]
            
            # Apply mask (0 means masked positions)
            scores = scores.masked_fill(mask == 0, float('-inf'))
        
        # Apply softmax
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        attention_output = torch.matmul(attention_weights, value)
        
        return attention_output, attention_weights

class MultiHeadAttention(nn.Module):
    """Multi-Head Attention with proper dimension handling."""
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # Linear layers for Q, K, V projections
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)
        
        # Attention mechanism
        self.attention = ScaledDotProductAttention(dropout)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights with Xavier uniform distribution."""
        for module in [self.w_q, self.w_k, self.w_v, self.w_o]:
            nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
    
    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of multi-head attention.
        
        Args:
            query: Query tensor [batch_size, seq_len, d_model]
            key: Key tensor [batch_size, seq_len, d_model]
            value: Value tensor [batch_size, seq_len, d_model]
            mask: Attention mask [batch_size, seq_len, seq_len]
        
        Returns:
            Tuple of (output, attention_weights)
        """
        batch_size, seq_len, d_model = query.size()
        
        # Linear projections
        Q = self.w_q(query)  # [batch_size, seq_len, d_model]
        K = self.w_k(key)    # [batch_size, seq_len, d_model]
        V = self.w_v(value)  # [batch_size, seq_len, d_model]
        
        # Reshape for multi-head attention
        Q = Q.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)  # [batch_size, num_heads, seq_len, d_k]
        K = K.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)  # [batch_size, num_heads, seq_len, d_k]
        V = V.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)  # [batch_size, num_heads, seq_len, d_k]
        
        # Apply attention
        attention_output, attention_weights = self.attention(Q, K, V, mask)
        
        # Concatenate heads
        attention_output = attention_output.transpose(1, 2).contiguous().view(
            batch_size, seq_len, d_model
        )
        
        # Final linear projection
        output = self.w_o(attention_output)
        
        return output, attention_weights

# ============================================================================
# POSITIONAL ENCODINGS
# ============================================================================

class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding for Transformer models."""
    
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        
        self.dropout = nn.Dropout(dropout)
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        # Create division term for sinusoidal encoding
        div_term = torch.exp(torch.arange(0, d_model, 2, dtype=torch.float) * 
                           -(math.log(10000.0) / d_model))
        
        # Apply sine to even indices
        pe[:, 0::2] = torch.sin(position * div_term)
        
        # Apply cosine to odd indices
        pe[:, 1::2] = torch.cos(position * div_term)
        
        # Add batch dimension and register as buffer
        pe = pe.unsqueeze(0).transpose(0, 1)  # [max_len, 1, d_model]
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Add positional encoding to input embeddings.
        
        Args:
            x: Input tensor [seq_len, batch_size, d_model]
        
        Returns:
            Output tensor with positional encoding added
        """
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)

class LearnablePositionalEncoding(nn.Module):
    """Learnable positional encoding."""
    
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        
        self.dropout = nn.Dropout(dropout)
        self.position_embeddings = nn.Embedding(max_len, d_model)
        
        # Initialize with small values
        nn.init.normal_(self.position_embeddings.weight, mean=0, std=0.02)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Add learnable positional encoding to input embeddings.
        
        Args:
            x: Input tensor [batch_size, seq_len, d_model]
        
        Returns:
            Output tensor with positional encoding added
        """
        batch_size, seq_len, d_model = x.size()
        
        # Create position indices
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        
        # Add positional embeddings
        position_embeddings = self.position_embeddings(positions)
        x = x + position_embeddings
        
        return self.dropout(x)

class RotaryPositionalEncoding(nn.Module):
    """Rotary Positional Encoding (RoPE) for enhanced positional understanding."""
    
    def __init__(self, d_model: int, max_len: int = 5000, base: float = 10000.0):
        super().__init__()
        
        self.d_model = d_model
        self.max_len = max_len
        self.base = base
        
        # Precompute frequency bands
        inv_freq = 1.0 / (base ** (torch.arange(0, d_model, 2).float() / d_model))
        self.register_buffer('inv_freq', inv_freq)
    
    def forward(self, x: torch.Tensor, seq_len: Optional[int] = None) -> torch.Tensor:
        """
        Apply rotary positional encoding.
        
        Args:
            x: Input tensor [batch_size, num_heads, seq_len, head_dim]
            seq_len: Sequence length (if different from x.size(2))
        
        Returns:
            Output tensor with rotary encoding applied
        """
        if seq_len is None:
            seq_len = x.size(2)
        
        # Create position indices
        t = torch.arange(seq_len, device=x.device, dtype=self.inv_freq.dtype)
        freqs = torch.outer(t, self.inv_freq)
        
        # Create rotation matrices
        cos = torch.cos(freqs)
        sin = torch.sin(freqs)
        
        # Apply rotation
        x1, x2 = x[..., ::2], x[..., 1::2]
        
        # Rotate
        rotated_x1 = x1 * cos - x2 * sin
        rotated_x2 = x1 * sin + x2 * cos
        
        # Interleave
        rotated_x = torch.stack([rotated_x1, rotated_x2], dim=-1)
        rotated_x = rotated_x.view(*x.shape)
        
        return rotated_x

class ALiBiPositionalBias(nn.Module):
    """Attention with Linear Biases (ALiBi) for length extrapolation."""
    
    def __init__(self, num_heads: int, max_len: int = 5000):
        super().__init__()
        
        self.num_heads = num_heads
        self.max_len = max_len
        
        # Compute slopes for each head
        slopes = torch.tensor(self._get_slopes(num_heads))
        self.register_buffer('slopes', slopes)
    
    def _get_slopes(self, num_heads: int) -> List[float]:
        """Get slopes for ALiBi bias."""
        
        def get_slopes_power_of_2(n: int) -> List[float]:
            start = (2 ** (-2 ** -(math.log2(n) - 3)))
            ratio = start
            return [start * ratio ** i for i in range(n)]
        
        if math.log2(num_heads).is_integer():
            return get_slopes_power_of_2(num_heads)
        else:
            closest_power_of_2 = 2 ** math.floor(math.log2(num_heads))
            slopes = get_slopes_power_of_2(closest_power_of_2)
            slopes.extend(get_slopes_power_of_2(2 * closest_power_of_2)[:num_heads - closest_power_of_2])
            return slopes
    
    def forward(self, attention_scores: torch.Tensor) -> torch.Tensor:
        """
        Add ALiBi bias to attention scores.
        
        Args:
            attention_scores: Attention scores [batch_size, num_heads, seq_len, seq_len]
        
        Returns:
            Biased attention scores
        """
        batch_size, num_heads, seq_len, _ = attention_scores.shape
        
        # Create position matrix
        range_tensor = torch.arange(seq_len, device=attention_scores.device)
        range_tensor = range_tensor.unsqueeze(0) - range_tensor.unsqueeze(1)
        
        # Apply slopes
        alibi_bias = range_tensor.unsqueeze(0).unsqueeze(0) * self.slopes.view(1, -1, 1, 1)
        
        return attention_scores + alibi_bias[:, :num_heads, :seq_len, :seq_len]

# ============================================================================
# ADVANCED ATTENTION MECHANISMS
# ============================================================================

class SelfAttention(nn.Module):
    """Self-attention mechanism with proper masking."""
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Self-attention forward pass."""
        return self.attention(x, x, x, mask)

class CrossAttention(nn.Module):
    """Cross-attention mechanism for encoder-decoder architectures."""
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
    
    def forward(self, query: torch.Tensor, key_value: torch.Tensor, 
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Cross-attention forward pass."""
        return self.attention(query, key_value, key_value, mask)

class CausalSelfAttention(nn.Module):
    """Causal self-attention with lower triangular mask."""
    
    def __init__(self, d_model: int, num_heads: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        
        # Register causal mask
        causal_mask = torch.tril(torch.ones(max_len, max_len))
        self.register_buffer('causal_mask', causal_mask)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Causal self-attention forward pass.
        
        Args:
            x: Input tensor [batch_size, seq_len, d_model]
            mask: Optional additional mask
        
        Returns:
            Tuple of (output, attention_weights)
        """
        batch_size, seq_len, d_model = x.size()
        
        # Get causal mask for current sequence length
        causal_mask = self.causal_mask[:seq_len, :seq_len]
        
        # Combine with additional mask if provided
        if mask is not None:
            if mask.dim() == 2:
                mask = mask.unsqueeze(0)  # Add batch dimension
            combined_mask = mask * causal_mask.unsqueeze(0)
        else:
            combined_mask = causal_mask.unsqueeze(0)
        
        return self.attention(x, x, x, combined_mask)

class FlashAttention(nn.Module):
    """Memory-efficient Flash Attention implementation."""
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1, 
                 block_size: int = 128):
        super().__init__()
        
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.block_size = block_size
        
        # Linear layers
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Flash attention forward pass with memory optimization.
        
        Note: This is a simplified version. For production use,
        consider using the official Flash Attention implementation.
        """
        batch_size, seq_len, d_model = query.size()
        
        # Linear projections
        Q = self.w_q(query).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        
        # Compute attention with memory efficiency
        output = self._flash_attention_forward(Q, K, V, mask)
        
        # Reshape and project
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)
        output = self.w_o(output)
        
        return output
    
    def _flash_attention_forward(self, Q: torch.Tensor, K: torch.Tensor, V: torch.Tensor,
                                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Memory-efficient attention computation."""
        
        # For this simplified implementation, fall back to standard attention
        # In practice, this would use tiling and recomputation strategies
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        if mask is not None:
            if mask.dim() == 3:
                mask = mask.unsqueeze(1)
            scores = scores.masked_fill(mask == 0, float('-inf'))
        
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        output = torch.matmul(attention_weights, V)
        
        return output

# ============================================================================
# MASK UTILITIES
# ============================================================================

class MaskUtils:
    """Utilities for creating and handling attention masks."""
    
    @staticmethod
    def create_padding_mask(input_ids: torch.Tensor, pad_token_id: int = 0) -> torch.Tensor:
        """
        Create padding mask from input token IDs.
        
        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            pad_token_id: Padding token ID
        
        Returns:
            Padding mask [batch_size, seq_len, seq_len]
        """
        # Create mask where non-padding tokens are 1
        mask = (input_ids != pad_token_id).float()
        
        # Expand to attention mask shape
        batch_size, seq_len = input_ids.shape
        attention_mask = mask.unsqueeze(1).expand(batch_size, seq_len, seq_len)
        
        return attention_mask
    
    @staticmethod
    def create_causal_mask(seq_len: int, device: torch.device = None) -> torch.Tensor:
        """
        Create causal (lower triangular) mask.
        
        Args:
            seq_len: Sequence length
            device: Device to create mask on
        
        Returns:
            Causal mask [seq_len, seq_len]
        """
        mask = torch.tril(torch.ones(seq_len, seq_len, device=device))
        return mask
    
    @staticmethod
    def create_look_ahead_mask(seq_len: int, device: torch.device = None) -> torch.Tensor:
        """
        Create look-ahead mask (upper triangular zeros).
        
        Args:
            seq_len: Sequence length
            device: Device to create mask on
        
        Returns:
            Look-ahead mask [seq_len, seq_len]
        """
        mask = 1 - torch.triu(torch.ones(seq_len, seq_len, device=device), diagonal=1)
        return mask
    
    @staticmethod
    def combine_masks(*masks: torch.Tensor) -> torch.Tensor:
        """
        Combine multiple masks using element-wise multiplication.
        
        Args:
            *masks: Variable number of masks to combine
        
        Returns:
            Combined mask
        """
        if not masks:
            return None
        
        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask = combined_mask * mask
        
        return combined_mask

# ============================================================================
# TRANSFORMER LAYER WITH PROPER ATTENTION
# ============================================================================

class TransformerEncoderLayer(nn.Module):
    """Transformer encoder layer with proper attention and positional encoding."""
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1,
                 activation: str = 'relu', norm_first: bool = False):
        super().__init__()
        
        self.d_model = d_model
        self.norm_first = norm_first
        
        # Multi-head attention
        self.self_attention = MultiHeadAttention(d_model, num_heads, dropout)
        
        # Feed-forward network
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU() if activation == 'relu' else nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )
        
        # Layer normalization
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass through transformer encoder layer.
        
        Args:
            x: Input tensor [batch_size, seq_len, d_model]
            mask: Attention mask
        
        Returns:
            Output tensor [batch_size, seq_len, d_model]
        """
        if self.norm_first:
            # Pre-normalization
            attn_output, _ = self.self_attention(self.norm1(x), self.norm1(x), self.norm1(x), mask)
            x = x + self.dropout(attn_output)
            
            ff_output = self.feed_forward(self.norm2(x))
            x = x + ff_output
        else:
            # Post-normalization
            attn_output, _ = self.self_attention(x, x, x, mask)
            x = self.norm1(x + self.dropout(attn_output))
            
            ff_output = self.feed_forward(x)
            x = self.norm2(x + ff_output)
        
        return x

class TransformerDecoderLayer(nn.Module):
    """Transformer decoder layer with self-attention and cross-attention."""
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1,
                 activation: str = 'relu', norm_first: bool = False):
        super().__init__()
        
        self.d_model = d_model
        self.norm_first = norm_first
        
        # Self-attention (causal)
        self.self_attention = CausalSelfAttention(d_model, num_heads, dropout=dropout)
        
        # Cross-attention
        self.cross_attention = CrossAttention(d_model, num_heads, dropout)
        
        # Feed-forward network
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU() if activation == 'relu' else nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )
        
        # Layer normalization
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, encoder_output: torch.Tensor,
                self_attn_mask: Optional[torch.Tensor] = None,
                cross_attn_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass through transformer decoder layer.
        
        Args:
            x: Input tensor [batch_size, seq_len, d_model]
            encoder_output: Encoder output [batch_size, src_seq_len, d_model]
            self_attn_mask: Self-attention mask
            cross_attn_mask: Cross-attention mask
        
        Returns:
            Output tensor [batch_size, seq_len, d_model]
        """
        if self.norm_first:
            # Pre-normalization
            # Self-attention
            self_attn_output, _ = self.self_attention(self.norm1(x), self_attn_mask)
            x = x + self.dropout(self_attn_output)
            
            # Cross-attention
            cross_attn_output, _ = self.cross_attention(self.norm2(x), encoder_output, cross_attn_mask)
            x = x + self.dropout(cross_attn_output)
            
            # Feed-forward
            ff_output = self.feed_forward(self.norm3(x))
            x = x + ff_output
        else:
            # Post-normalization
            # Self-attention
            self_attn_output, _ = self.self_attention(x, self_attn_mask)
            x = self.norm1(x + self.dropout(self_attn_output))
            
            # Cross-attention
            cross_attn_output, _ = self.cross_attention(x, encoder_output, cross_attn_mask)
            x = self.norm2(x + self.dropout(cross_attn_output))
            
            # Feed-forward
            ff_output = self.feed_forward(x)
            x = self.norm3(x + ff_output)
        
        return x

# ============================================================================
# COMPLETE TRANSFORMER MODEL
# ============================================================================

class TransformerModel(nn.Module):
    """Complete Transformer model with proper attention and positional encoding."""
    
    def __init__(self, vocab_size: int, d_model: int = 512, num_heads: int = 8,
                 num_encoder_layers: int = 6, num_decoder_layers: int = 6,
                 d_ff: int = 2048, max_len: int = 5000, dropout: float = 0.1,
                 pad_token_id: int = 0, positional_encoding: str = 'sinusoidal'):
        super().__init__()
        
        self.d_model = d_model
        self.pad_token_id = pad_token_id
        
        # Embeddings
        self.src_embedding = nn.Embedding(vocab_size, d_model)
        self.tgt_embedding = nn.Embedding(vocab_size, d_model)
        
        # Positional encoding
        if positional_encoding == 'sinusoidal':
            self.pos_encoding = PositionalEncoding(d_model, max_len, dropout)
        elif positional_encoding == 'learnable':
            self.pos_encoding = LearnablePositionalEncoding(d_model, max_len, dropout)
        else:
            raise ValueError(f"Unknown positional encoding: {positional_encoding}")
        
        # Transformer layers
        self.encoder_layers = nn.ModuleList([
            TransformerEncoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_encoder_layers)
        ])
        
        self.decoder_layers = nn.ModuleList([
            TransformerDecoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_decoder_layers)
        ])
        
        # Output projection
        self.output_projection = nn.Linear(d_model, vocab_size)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize model weights."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.normal_(module.weight, mean=0, std=0.02)
    
    def forward(self, src: torch.Tensor, tgt: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through transformer.
        
        Args:
            src: Source sequence [batch_size, src_seq_len]
            tgt: Target sequence [batch_size, tgt_seq_len]
        
        Returns:
            Output logits [batch_size, tgt_seq_len, vocab_size]
        """
        # Create masks
        src_mask = MaskUtils.create_padding_mask(src, self.pad_token_id)
        tgt_mask = MaskUtils.create_padding_mask(tgt, self.pad_token_id)
        
        # Encode
        encoder_output = self.encode(src, src_mask)
        
        # Decode
        decoder_output = self.decode(tgt, encoder_output, tgt_mask, src_mask)
        
        # Output projection
        logits = self.output_projection(decoder_output)
        
        return logits
    
    def encode(self, src: torch.Tensor, src_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Encode source sequence."""
        # Embeddings
        x = self.src_embedding(src) * math.sqrt(self.d_model)
        
        # Add positional encoding
        x = x.transpose(0, 1)  # [seq_len, batch_size, d_model] for pos encoding
        x = self.pos_encoding(x)
        x = x.transpose(0, 1)  # Back to [batch_size, seq_len, d_model]
        
        # Encoder layers
        for layer in self.encoder_layers:
            x = layer(x, src_mask)
        
        return x
    
    def decode(self, tgt: torch.Tensor, encoder_output: torch.Tensor,
               tgt_mask: Optional[torch.Tensor] = None,
               src_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Decode target sequence."""
        # Embeddings
        x = self.tgt_embedding(tgt) * math.sqrt(self.d_model)
        
        # Add positional encoding
        x = x.transpose(0, 1)  # [seq_len, batch_size, d_model] for pos encoding
        x = self.pos_encoding(x)
        x = x.transpose(0, 1)  # Back to [batch_size, seq_len, d_model]
        
        # Decoder layers
        for layer in self.decoder_layers:
            x = layer(x, encoder_output, tgt_mask, src_mask)
        
        return x

# ============================================================================
# DEMO AND TESTING
# ============================================================================

def test_attention_mechanisms():
    """Test attention mechanisms with proper dimensions."""
    
    print("Testing Attention Mechanisms and Positional Encodings")
    print("=" * 60)
    
    # Test parameters
    batch_size = 2
    seq_len = 10
    d_model = 64
    num_heads = 8
    vocab_size = 1000
    
    # Create test data
    x = torch.randn(batch_size, seq_len, d_model)
    input_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
    
    print(f"Test data shape: {x.shape}")
    print(f"Input IDs shape: {input_ids.shape}")
    
    # Test Multi-Head Attention
    print("\n1. Testing Multi-Head Attention:")
    mha = MultiHeadAttention(d_model, num_heads)
    
    # Create proper mask
    mask = MaskUtils.create_padding_mask(input_ids, pad_token_id=0)
    print(f"   Mask shape: {mask.shape}")
    
    try:
        output, attention_weights = mha(x, x, x, mask)
        print(f"   ✓ Output shape: {output.shape}")
        print(f"   ✓ Attention weights shape: {attention_weights.shape}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Positional Encodings
    print("\n2. Testing Positional Encodings:")
    
    # Sinusoidal PE
    print("   Sinusoidal Positional Encoding:")
    pe_sin = PositionalEncoding(d_model)
    x_transposed = x.transpose(0, 1)  # [seq_len, batch_size, d_model]
    try:
        output_sin = pe_sin(x_transposed)
        print(f"   ✓ Output shape: {output_sin.shape}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Learnable PE
    print("   Learnable Positional Encoding:")
    pe_learn = LearnablePositionalEncoding(d_model)
    try:
        output_learn = pe_learn(x)
        print(f"   ✓ Output shape: {output_learn.shape}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Transformer Layer
    print("\n3. Testing Transformer Encoder Layer:")
    encoder_layer = TransformerEncoderLayer(d_model, num_heads, d_ff=256)
    try:
        output_enc = encoder_layer(x, mask)
        print(f"   ✓ Output shape: {output_enc.shape}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Complete Model
    print("\n4. Testing Complete Transformer Model:")
    model = TransformerModel(
        vocab_size=vocab_size,
        d_model=d_model,
        num_heads=num_heads,
        num_encoder_layers=2,
        num_decoder_layers=2,
        d_ff=256,
        max_len=100
    )
    
    src_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
    tgt_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
    
    try:
        logits = model(src_ids, tgt_ids)
        print(f"   ✓ Logits shape: {logits.shape}")
        print(f"   ✓ Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")

if __name__ == "__main__":
    test_attention_mechanisms()
