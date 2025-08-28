#!/usr/bin/env python3
"""
Optimized Attention Mechanisms Implementation
===========================================

Production-ready attention mechanisms with:
- Multi-head attention with optimizations
- Flash attention support
- Efficient memory usage
- Comprehensive error handling
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Union
import logging

# =============================================================================
# Optimized Multi-Head Attention
# =============================================================================

class OptimizedMultiHeadAttention(nn.Module):
    """Optimized multi-head attention with performance enhancements."""
    
    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        dropout: float = 0.0,
        bias: bool = True,
        batch_first: bool = True,
        use_flash_attention: bool = True
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.dropout = dropout
        self.batch_first = batch_first
        self.use_flash_attention = use_flash_attention
        
        # Validate dimensions
        if self.head_dim * num_heads != embed_dim:
            raise ValueError(f"embed_dim must be divisible by num_heads, got {embed_dim} and {num_heads}")
        
        # Linear projections
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.k_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.v_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        
        # Dropout layers
        self.attn_dropout = nn.Dropout(dropout)
        self.out_dropout = nn.Dropout(dropout)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize attention weights for optimal performance."""
        # Xavier initialization for linear layers
        for module in [self.q_proj, self.k_proj, self.v_proj, self.out_proj]:
            nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        attn_mask: Optional[torch.Tensor] = None,
        key_padding_mask: Optional[torch.Tensor] = None,
        need_weights: bool = False,
        is_causal: bool = False
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """Forward pass with optimizations."""
        
        # Handle batch dimension
        if not self.batch_first:
            query = query.transpose(0, 1)
            key = key.transpose(0, 1)
            value = value.transpose(0, 1)
        
        batch_size, seq_len, embed_dim = query.shape
        
        # Project queries, keys, and values
        q = self.q_proj(query).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(key).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(value).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Use flash attention if available and enabled
        if self.use_flash_attention and hasattr(F, 'scaled_dot_product_attention'):
            try:
                output = F.scaled_dot_product_attention(
                    q, k, v,
                    attn_mask=attn_mask,
                    dropout_p=self.dropout if self.training else 0.0,
                    is_causal=is_causal
                )
                output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, embed_dim)
                output = self.out_proj(output)
                output = self.out_dropout(output)
                
                if not self.batch_first:
                    output = output.transpose(0, 1)
                
                return output, None
                
            except Exception as e:
                logging.warning(f"Flash attention failed, falling back to standard attention: {e}")
        
        # Standard attention implementation
        return self._standard_attention(q, k, v, attn_mask, key_padding_mask, need_weights)
    
    def _standard_attention(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        attn_mask: Optional[torch.Tensor] = None,
        key_padding_mask: Optional[torch.Tensor] = None,
        need_weights: bool = False
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """Standard attention implementation with optimizations."""
        
        batch_size, num_heads, seq_len, head_dim = q.shape
        key_len = k.size(2)
        
        # Compute attention scores
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(head_dim)
        
        # Apply attention mask
        if attn_mask is not None:
            scores = scores.masked_fill(attn_mask == 0, float('-inf'))
        
        # Apply key padding mask
        if key_padding_mask is not None:
            # Expand mask to match attention scores shape
            key_padding_mask = key_padding_mask.unsqueeze(1).unsqueeze(2)
            scores = scores.masked_fill(key_padding_mask, float('-inf'))
        
        # Apply softmax
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.attn_dropout(attn_weights)
        
        # Apply attention weights to values
        output = torch.matmul(attn_weights, v)
        
        # Reshape and project output
        output = output.transpose(1, 2).contiguous().view(
            batch_size, seq_len, self.embed_dim
        )
        output = self.out_proj(output)
        output = self.out_dropout(output)
        
        # Handle batch dimension
        if not self.batch_first:
            output = output.transpose(0, 1)
        
        return output, attn_weights if need_weights else None

# =============================================================================
# Optimized Positional Encoding
# =============================================================================

class OptimizedPositionalEncoding(nn.Module):
    """Optimized positional encoding with caching."""
    
    def __init__(self, embed_dim: int, max_seq_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.embed_dim = embed_dim
        self.max_seq_len = max_seq_len
        self.dropout = nn.Dropout(dropout)
        
        # Pre-compute positional encodings
        self.register_buffer('pos_encoding', self._create_positional_encoding())
    
    def _create_positional_encoding(self) -> torch.Tensor:
        """Create positional encoding matrix."""
        pos_encoding = torch.zeros(self.max_seq_len, self.embed_dim)
        position = torch.arange(0, self.max_seq_len, dtype=torch.float).unsqueeze(1)
        
        div_term = torch.exp(
            torch.arange(0, self.embed_dim, 2).float() * 
            (-math.log(10000.0) / self.embed_dim)
        )
        
        pos_encoding[:, 0::2] = torch.sin(position * div_term)
        pos_encoding[:, 1::2] = torch.cos(position * div_term)
        
        return pos_encoding.unsqueeze(0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input."""
        seq_len = x.size(1)
        
        if seq_len > self.max_seq_len:
            raise ValueError(f"Sequence length {seq_len} exceeds maximum {self.max_seq_len}")
        
        x = x + self.pos_encoding[:, :seq_len, :]
        return self.dropout(x)

# =============================================================================
# Optimized Transformer Block
# =============================================================================

class OptimizedTransformerBlock(nn.Module):
    """Optimized transformer block with layer normalization and residual connections."""
    
    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        ff_dim: int,
        dropout: float = 0.1,
        activation: str = "gelu",
        layer_norm_eps: float = 1e-5,
        use_flash_attention: bool = True
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        
        # Multi-head attention
        self.self_attn = OptimizedMultiHeadAttention(
            embed_dim=embed_dim,
            num_heads=num_heads,
            dropout=dropout,
            use_flash_attention=use_flash_attention
        )
        
        # Layer normalization
        self.norm1 = nn.LayerNorm(embed_dim, eps=layer_norm_eps)
        self.norm2 = nn.LayerNorm(embed_dim, eps=layer_norm_eps)
        
        # Feed-forward network
        self.ff_network = nn.Sequential(
            nn.Linear(embed_dim, ff_dim),
            self._get_activation(activation),
            nn.Dropout(dropout),
            nn.Linear(ff_dim, embed_dim),
            nn.Dropout(dropout)
        )
        
        # Initialize weights
        self._initialize_weights()
    
    def _get_activation(self, activation: str) -> nn.Module:
        """Get activation function."""
        if activation.lower() == "gelu":
            return nn.GELU()
        elif activation.lower() == "relu":
            return nn.ReLU()
        elif activation.lower() == "swish":
            return nn.SiLU()
        else:
            raise ValueError(f"Unsupported activation: {activation}")
    
    def _initialize_weights(self):
        """Initialize transformer block weights."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(
        self,
        x: torch.Tensor,
        attn_mask: Optional[torch.Tensor] = None,
        key_padding_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass with residual connections."""
        
        # Self-attention with residual connection
        attn_output, _ = self.self_attn(
            query=x,
            key=x,
            value=x,
            attn_mask=attn_mask,
            key_padding_mask=key_padding_mask
        )
        x = self.norm1(x + attn_output)
        
        # Feed-forward network with residual connection
        ff_output = self.ff_network(x)
        x = self.norm2(x + ff_output)
        
        return x

# =============================================================================
# Optimized Transformer Model
# =============================================================================

class OptimizedTransformerModel(nn.Module):
    """Complete optimized transformer model."""
    
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int,
        num_layers: int,
        num_heads: int,
        ff_dim: int,
        max_seq_len: int = 512,
        dropout: float = 0.1,
        activation: str = "gelu",
        use_flash_attention: bool = True
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.num_layers = num_layers
        self.max_seq_len = max_seq_len
        
        # Token embedding
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        
        # Positional encoding
        self.pos_encoding = OptimizedPositionalEncoding(
            embed_dim=embed_dim,
            max_seq_len=max_seq_len,
            dropout=dropout
        )
        
        # Transformer layers
        self.layers = nn.ModuleList([
            OptimizedTransformerBlock(
                embed_dim=embed_dim,
                num_heads=num_heads,
                ff_dim=ff_dim,
                dropout=dropout,
                activation=activation,
                use_flash_attention=use_flash_attention
            )
            for _ in range(num_layers)
        ])
        
        # Output projection
        self.output_projection = nn.Linear(embed_dim, vocab_size, bias=False)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize model weights."""
        # Token embedding initialization
        nn.init.normal_(self.token_embedding.weight, mean=0.0, std=0.02)
        
        # Output projection initialization
        nn.init.normal_(self.output_projection.weight, mean=0.0, std=0.02)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None
    ) -> dict:
        """Forward pass with optional loss computation."""
        
        batch_size, seq_len = input_ids.shape
        
        # Token embeddings
        x = self.token_embedding(input_ids)
        
        # Add positional encoding
        x = self.pos_encoding(x)
        
        # Apply transformer layers
        for layer in self.layers:
            x = layer(x, attn_mask=attention_mask)
        
        # Output projection
        logits = self.output_projection(x)
        
        # Compute loss if labels are provided
        loss = None
        if labels is not None:
            # Shift sequences for language modeling
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(shift_logits.view(-1, self.vocab_size), shift_labels.view(-1))
        
        return {"loss": loss, "logits": logits} if loss is not None else {"logits": logits}
    
    def generate(
        self,
        input_ids: torch.Tensor,
        max_length: int,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 0.9,
        do_sample: bool = True,
        pad_token_id: int = 0,
        eos_token_id: int = 1
    ) -> torch.Tensor:
        """Generate text with optimized sampling."""
        
        batch_size = input_ids.shape[0]
        current_length = input_ids.shape[1]
        
        # Ensure we don't exceed max_length
        max_length = min(max_length, self.max_seq_len)
        
        with torch.no_grad():
            for _ in range(max_length - current_length):
                # Get model predictions
                outputs = self.forward(input_ids)
                next_token_logits = outputs["logits"][:, -1, :] / temperature
                
                # Apply top-k filtering
                if top_k > 0:
                    top_k_logits, top_k_indices = torch.topk(next_token_logits, top_k)
                    next_token_logits = torch.full_like(next_token_logits, float('-inf'))
                    next_token_logits.scatter_(1, top_k_indices, top_k_logits)
                
                # Apply top-p (nucleus) filtering
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                    
                    # Remove tokens with cumulative probability above the threshold
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
                
                # Append to input_ids
                input_ids = torch.cat([input_ids, next_token], dim=-1)
                
                # Check for EOS token
                if (next_token == eos_token_id).any():
                    break
        
        return input_ids

# =============================================================================
# Usage Example
# =============================================================================

def main():
    """Example usage of optimized attention mechanisms."""
    
    # Configuration
    vocab_size = 50000
    embed_dim = 512
    num_layers = 6
    num_heads = 8
    ff_dim = 2048
    batch_size = 4
    seq_len = 128
    
    # Create model
    model = OptimizedTransformerModel(
        vocab_size=vocab_size,
        embed_dim=embed_dim,
        num_layers=num_layers,
        num_heads=num_heads,
        ff_dim=ff_dim
    )
    
    # Create sample input
    input_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
    attention_mask = torch.ones(batch_size, seq_len)
    
    # Forward pass
    outputs = model(input_ids, attention_mask=attention_mask)
    print(f"Output shape: {outputs['logits'].shape}")
    
    # Generate text
    generated = model.generate(
        input_ids=input_ids[:, :10],  # Start with first 10 tokens
        max_length=50,
        temperature=0.8,
        do_sample=True
    )
    print(f"Generated shape: {generated.shape}")

if __name__ == "__main__":
    main()


