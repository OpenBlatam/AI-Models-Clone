#!/usr/bin/env python3
"""
Advanced Transformer System with Attention Mechanisms and Positional Encodings

This module implements a comprehensive transformer system with:
- Multi-head self-attention mechanisms
- Proper positional encodings (learned and sinusoidal)
- Cross-attention for multi-modal tasks
- Advanced attention variants (relative, sparse, local)
- Custom transformer architectures
- Attention visualization and analysis tools

Features:
- Custom attention implementations with proper scaling
- Positional encoding strategies for different data types
- Attention analysis and visualization tools
- Multi-modal attention mechanisms
- Performance-optimized attention computations
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy as np
from typing import Optional, Tuple, Dict, Any, List, Union
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AttentionConfig:
    """Configuration for attention mechanisms."""
    num_heads: int = 8
    head_dim: int = 64
    dropout: float = 0.1
    attention_type: str = "standard"  # standard, relative, sparse, local
    use_relative_position: bool = False
    max_relative_position: int = 32
    attention_window: int = 128  # for local attention
    sparse_topk: int = 64  # for sparse attention


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding for sequences."""
    
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        """
        Initialize positional encoding.
        
        Args:
            d_model: Dimension of the model
            max_len: Maximum sequence length
            dropout: Dropout probability
        """
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        # Calculate sinusoidal encodings
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                           (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        
        # Register as buffer (not parameter)
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Add positional encoding to input.
        
        Args:
            x: Input tensor of shape (seq_len, batch_size, d_model)
            
        Returns:
            Tensor with positional encoding added
        """
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)


class LearnedPositionalEncoding(nn.Module):
    """Learnable positional encoding for sequences."""
    
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        """
        Initialize learned positional encoding.
        
        Args:
            d_model: Dimension of the model
            max_len: Maximum sequence length
            dropout: Dropout probability
        """
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        self.pe = nn.Parameter(torch.randn(max_len, d_model))
        
        # Initialize with small values
        nn.init.normal_(self.pe, std=0.02)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Add learned positional encoding to input.
        
        Args:
            x: Input tensor of shape (seq_len, batch_size, d_model)
            
        Returns:
            Tensor with positional encoding added
        """
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)


class ImagePositionalEncoding(nn.Module):
    """2D positional encoding for images using sinusoidal encodings."""
    
    def __init__(self, d_model: int, max_h: int = 224, max_w: int = 224, dropout: float = 0.1):
        """
        Initialize 2D positional encoding for images.
        
        Args:
            d_model: Dimension of the model
            max_h: Maximum height
            max_w: Maximum width
            dropout: Dropout probability
        """
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        self.d_model = d_model
        
        # Create 2D positional encoding
        pe = torch.zeros(max_h, max_w, d_model)
        
        # Generate position indices
        h_pos = torch.arange(0, max_h).unsqueeze(1).float()
        w_pos = torch.arange(0, max_w).unsqueeze(0).float()
        
        # Calculate sinusoidal encodings for height and width
        div_term = torch.exp(torch.arange(0, d_model, 4).float() * 
                           (-math.log(10000.0) / d_model))
        
        # Height encoding
        pe[:, :, 0::4] = torch.sin(h_pos * div_term)
        pe[:, :, 1::4] = torch.cos(h_pos * div_term)
        
        # Width encoding
        pe[:, :, 2::4] = torch.sin(w_pos * div_term)
        pe[:, :, 3::4] = torch.cos(w_pos * div_term)
        
        # Register as buffer
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Add 2D positional encoding to image features.
        
        Args:
            x: Input tensor of shape (batch_size, seq_len, d_model)
               where seq_len = height * width for flattened images
               
        Returns:
            Tensor with 2D positional encoding added
        """
        batch_size, seq_len, d_model = x.shape
        h = w = int(math.sqrt(seq_len))
        
        # Reshape to 2D and add positional encoding
        x_2d = x.view(batch_size, h, w, d_model)
        x_2d = x_2d + self.pe[:h, :w, :]
        
        # Flatten back
        return self.dropout(x_2d.view(batch_size, seq_len, d_model))


class MultiHeadAttention(nn.Module):
    """Multi-head self-attention mechanism with proper scaling."""
    
    def __init__(self, config: AttentionConfig):
        """
        Initialize multi-head attention.
        
        Args:
            config: Attention configuration
        """
        super().__init__()
        self.config = config
        self.num_heads = config.num_heads
        self.head_dim = config.head_dim
        self.d_model = config.num_heads * config.head_dim
        
        # Linear projections
        self.query_proj = nn.Linear(self.d_model, self.d_model, bias=False)
        self.key_proj = nn.Linear(self.d_model, self.d_model, bias=False)
        self.value_proj = nn.Linear(self.d_model, self.d_model, bias=False)
        self.output_proj = nn.Linear(self.d_model, self.d_model, bias=False)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
        
        # Scaling factor
        self.scale = math.sqrt(self.head_dim)
        
        # Attention type specific components
        if config.attention_type == "relative":
            self.relative_position_embeddings = nn.Parameter(
                torch.randn(2 * config.max_relative_position + 1, self.head_dim)
            )
            nn.init.normal_(self.relative_position_embeddings, std=0.02)
    
    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute multi-head attention.
        
        Args:
            query: Query tensor (batch_size, seq_len, d_model)
            key: Key tensor (batch_size, seq_len, d_model)
            value: Value tensor (batch_size, seq_len, d_model)
            mask: Optional attention mask
            
        Returns:
            Tuple of (output, attention_weights)
        """
        batch_size, seq_len, _ = query.shape
        
        # Linear projections and reshape for multi-head
        Q = self.query_proj(query).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.key_proj(key).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.value_proj(value).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Compute attention scores
        if self.config.attention_type == "relative":
            attention_scores = self._compute_relative_attention(Q, K, seq_len)
        else:
            attention_scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale
        
        # Apply mask if provided
        if mask is not None:
            attention_scores = attention_scores.masked_fill(mask == 0, float('-inf'))
        
        # Apply attention weights
        attention_weights = F.softmax(attention_scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        context = torch.matmul(attention_weights, V)
        
        # Reshape and project output
        context = context.transpose(1, 2).contiguous().view(
            batch_size, seq_len, self.d_model
        )
        output = self.output_proj(context)
        
        return output, attention_weights
    
    def _compute_relative_attention(self, Q: torch.Tensor, K: torch.Tensor, 
                                   seq_len: int) -> torch.Tensor:
        """Compute relative positional attention scores."""
        # Standard attention scores
        content_scores = torch.matmul(Q, K.transpose(-2, -1))
        
        # Relative position scores
        relative_positions = torch.arange(seq_len, device=Q.device)
        relative_positions = relative_positions.unsqueeze(0) - relative_positions.unsqueeze(1)
        relative_positions = torch.clamp(
            relative_positions, 
            -self.config.max_relative_position, 
            self.config.max_relative_position
        )
        relative_positions += self.config.max_relative_position
        
        # Get relative position embeddings
        relative_embeddings = self.relative_position_embeddings[relative_positions]
        relative_scores = torch.matmul(Q, relative_embeddings.transpose(-2, -1))
        
        return content_scores + relative_scores


class LocalAttention(nn.Module):
    """Local attention mechanism for long sequences."""
    
    def __init__(self, config: AttentionConfig):
        """
        Initialize local attention.
        
        Args:
            config: Attention configuration
        """
        super().__init__()
        self.config = config
        self.window_size = config.attention_window
        self.num_heads = config.num_heads
        self.head_dim = config.head_dim
        self.d_model = config.num_heads * config.head_dim
        
        # Linear projections
        self.query_proj = nn.Linear(self.d_model, self.d_model, bias=False)
        self.key_proj = nn.Linear(self.d_model, self.d_model, bias=False)
        self.value_proj = nn.Linear(self.d_model, self.d_model, bias=False)
        self.output_proj = nn.Linear(self.d_model, self.d_model, bias=False)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
        self.scale = math.sqrt(self.head_dim)
    
    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute local attention within windows.
        
        Args:
            query: Query tensor (batch_size, seq_len, d_model)
            key: Key tensor (batch_size, seq_len, d_model)
            value: Value tensor (batch_size, seq_len, d_model)
            mask: Optional attention mask
            
        Returns:
            Tuple of (output, attention_weights)
        """
        batch_size, seq_len, _ = query.shape
        
        # Pad sequence to be divisible by window size
        pad_len = (self.window_size - seq_len % self.window_size) % self.window_size
        if pad_len > 0:
            query = F.pad(query, (0, 0, 0, pad_len))
            key = F.pad(key, (0, 0, 0, pad_len))
            value = F.pad(value, (0, 0, 0, pad_len))
            seq_len = query.shape[1]
        
        # Reshape into windows
        query = query.view(batch_size, seq_len // self.window_size, self.window_size, -1)
        key = key.view(batch_size, seq_len // self.window_size, self.window_size, -1)
        value = value.view(batch_size, seq_len // self.window_size, self.window_size, -1)
        
        # Linear projections
        Q = self.query_proj(query).view(batch_size, seq_len // self.window_size, self.window_size, 
                                       self.num_heads, self.head_dim).transpose(2, 3)
        K = self.key_proj(key).view(batch_size, seq_len // self.window_size, self.window_size, 
                                   self.num_heads, self.head_dim).transpose(2, 3)
        V = self.value_proj(value).view(batch_size, seq_len // self.window_size, self.window_size, 
                                       self.num_heads, self.head_dim).transpose(2, 3)
        
        # Compute attention within each window
        attention_scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale
        
        if mask is not None:
            # Reshape mask for local attention
            mask = mask.view(batch_size, seq_len // self.window_size, self.window_size)
            mask = mask.unsqueeze(1).unsqueeze(2)  # Add head and seq dimensions
            attention_scores = attention_scores.masked_fill(mask == 0, float('-inf'))
        
        # Apply attention
        attention_weights = F.softmax(attention_scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        context = torch.matmul(attention_weights, V)
        
        # Reshape back
        context = context.transpose(2, 3).contiguous().view(
            batch_size, seq_len, self.d_model
        )
        output = self.output_proj(context)
        
        # Remove padding
        if pad_len > 0:
            output = output[:, :seq_len - pad_len, :]
        
        return output, attention_weights


class CrossAttention(nn.Module):
    """Cross-attention mechanism for multi-modal tasks."""
    
    def __init__(self, config: AttentionConfig):
        """
        Initialize cross-attention.
        
        Args:
            config: Attention configuration
        """
        super().__init__()
        self.config = config
        self.num_heads = config.num_heads
        self.head_dim = config.head_dim
        self.d_model = config.num_heads * config.head_dim
        
        # Linear projections
        self.query_proj = nn.Linear(self.d_model, self.d_model, bias=False)
        self.key_proj = nn.Linear(self.d_model, self.d_model, bias=False)
        self.value_proj = nn.Linear(self.d_model, self.d_model, bias=False)
        self.output_proj = nn.Linear(self.d_model, self.d_model, bias=False)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
        self.scale = math.sqrt(self.head_dim)
    
    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute cross-attention between different modalities.
        
        Args:
            query: Query tensor from one modality (batch_size, seq_len_q, d_model)
            key: Key tensor from another modality (batch_size, seq_len_k, d_model)
            value: Value tensor from another modality (batch_size, seq_len_k, d_model)
            mask: Optional attention mask
            
        Returns:
            Tuple of (output, attention_weights)
        """
        batch_size, seq_len_q, _ = query.shape
        _, seq_len_k, _ = key.shape
        
        # Linear projections and reshape for multi-head
        Q = self.query_proj(query).view(batch_size, seq_len_q, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.key_proj(key).view(batch_size, seq_len_k, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.value_proj(value).view(batch_size, seq_len_k, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Compute attention scores
        attention_scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale
        
        # Apply mask if provided
        if mask is not None:
            attention_scores = attention_scores.masked_fill(mask == 0, float('-inf'))
        
        # Apply attention weights
        attention_weights = F.softmax(attention_scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        context = torch.matmul(attention_weights, V)
        
        # Reshape and project output
        context = context.transpose(1, 2).contiguous().view(
            batch_size, seq_len_q, self.d_model
        )
        output = self.output_proj(context)
        
        return output, attention_weights


class TransformerBlock(nn.Module):
    """Complete transformer block with attention and feed-forward layers."""
    
    def __init__(self, d_model: int, config: AttentionConfig, 
                 use_cross_attention: bool = False):
        """
        Initialize transformer block.
        
        Args:
            d_model: Dimension of the model
            config: Attention configuration
            use_cross_attention: Whether to use cross-attention
        """
        super().__init__()
        self.d_model = d_model
        self.config = config
        
        # Self-attention
        if config.attention_type == "local":
            self.self_attention = LocalAttention(config)
        else:
            self.self_attention = MultiHeadAttention(config)
        
        # Cross-attention (optional)
        self.use_cross_attention = use_cross_attention
        if use_cross_attention:
            self.cross_attention = CrossAttention(config)
        
        # Feed-forward network
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_model * 4),
            nn.GELU(),
            nn.Dropout(config.dropout),
            nn.Linear(d_model * 4, d_model),
            nn.Dropout(config.dropout)
        )
        
        # Layer normalization
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        if use_cross_attention:
            self.norm3 = nn.LayerNorm(d_model)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
    
    def forward(self, x: torch.Tensor, cross_input: Optional[torch.Tensor] = None,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through transformer block.
        
        Args:
            x: Input tensor
            cross_input: Optional cross-attention input
            mask: Optional attention mask
            
        Returns:
            Tuple of (output, attention_weights)
        """
        # Self-attention
        attn_output, self_attn_weights = self.self_attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))
        
        # Cross-attention (if enabled)
        cross_attn_weights = None
        if self.use_cross_attention and cross_input is not None:
            cross_attn_output, cross_attn_weights = self.cross_attention(
                x, cross_input, cross_input, mask
            )
            x = self.norm2(x + self.dropout(cross_attn_output))
        
        # Feed-forward
        ff_output = self.feed_forward(x)
        x = self.norm2(x + ff_output)
        
        return x, self_attn_weights


class AttentionVisualizer:
    """Tools for visualizing and analyzing attention patterns."""
    
    @staticmethod
    def plot_attention_weights(attention_weights: torch.Tensor, 
                              title: str = "Attention Weights",
                              save_path: Optional[str] = None) -> None:
        """
        Plot attention weights heatmap.
        
        Args:
            attention_weights: Attention weights tensor
            title: Plot title
            save_path: Optional path to save the plot
        """
        # Convert to numpy and average over heads if multi-head
        if attention_weights.dim() == 4:  # (batch, heads, seq_len, seq_len)
            attention_weights = attention_weights.mean(dim=1)  # Average over heads
        
        # Take first batch if multiple batches
        if attention_weights.dim() == 3:
            attention_weights = attention_weights[0]
        
        # Convert to numpy
        attention_np = attention_weights.detach().cpu().numpy()
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(attention_np, cmap='viridis', cbar=True, 
                   xticklabels=True, yticklabels=True)
        plt.title(title)
        plt.xlabel('Key Position')
        plt.ylabel('Query Position')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    @staticmethod
    def analyze_attention_patterns(attention_weights: torch.Tensor) -> Dict[str, float]:
        """
        Analyze attention patterns and compute statistics.
        
        Args:
            attention_weights: Attention weights tensor
            
        Returns:
            Dictionary with attention statistics
        """
        # Convert to numpy
        if attention_weights.dim() == 4:
            attention_weights = attention_weights.mean(dim=1)
        
        attention_np = attention_weights.detach().cpu().numpy()
        
        # Compute statistics
        stats = {
            'mean_attention': float(np.mean(attention_np)),
            'std_attention': float(np.std(attention_np)),
            'max_attention': float(np.max(attention_np)),
            'min_attention': float(np.min(attention_np)),
            'sparsity': float(np.mean(attention_np < 0.01)),  # Fraction of near-zero weights
            'local_concentration': float(np.mean(np.diag(attention_np, k=1) + 
                                               np.diag(attention_np, k=-1)))  # Local attention
        }
        
        return stats
    
    @staticmethod
    def visualize_positional_encoding(pe: torch.Tensor, 
                                    title: str = "Positional Encoding",
                                    save_path: Optional[str] = None) -> None:
        """
        Visualize positional encoding patterns.
        
        Args:
            pe: Positional encoding tensor
            title: Plot title
            save_path: Optional path to save the plot
        """
        pe_np = pe.detach().cpu().numpy()
        
        if pe_np.ndim == 3:  # (seq_len, batch, d_model)
            pe_np = pe_np[:, 0, :]  # Take first batch
        
        plt.figure(figsize=(12, 8))
        plt.imshow(pe_np.T, aspect='auto', cmap='viridis')
        plt.colorbar()
        plt.title(title)
        plt.xlabel('Sequence Position')
        plt.ylabel('Feature Dimension')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()


class AdvancedTransformerModel(nn.Module):
    """Advanced transformer model with custom attention mechanisms."""
    
    def __init__(self, config: AttentionConfig, num_layers: int = 6, 
                 d_model: int = 512, max_seq_len: int = 1000,
                 use_cross_attention: bool = False):
        """
        Initialize advanced transformer model.
        
        Args:
            config: Attention configuration
            num_layers: Number of transformer layers
            d_model: Dimension of the model
            max_seq_len: Maximum sequence length
            use_cross_attention: Whether to use cross-attention
        """
        super().__init__()
        self.config = config
        self.d_model = d_model
        self.num_layers = num_layers
        
        # Positional encoding
        if config.attention_type == "relative":
            self.pos_encoding = None  # Relative attention doesn't need explicit PE
        else:
            self.pos_encoding = PositionalEncoding(d_model, max_seq_len, config.dropout)
        
        # Transformer layers
        self.layers = nn.ModuleList([
            TransformerBlock(d_model, config, use_cross_attention)
            for _ in range(num_layers)
        ])
        
        # Output projection
        self.output_projection = nn.Linear(d_model, d_model)
        
        # Layer normalization
        self.final_norm = nn.LayerNorm(d_model)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize model weights."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.LayerNorm):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)
    
    def forward(self, x: torch.Tensor, cross_input: Optional[torch.Tensor] = None,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """
        Forward pass through the transformer.
        
        Args:
            x: Input tensor (batch_size, seq_len, d_model)
            cross_input: Optional cross-attention input
            mask: Optional attention mask
            
        Returns:
            Tuple of (output, attention_weights_list)
        """
        # Add positional encoding if not using relative attention
        if self.pos_encoding is not None:
            x = x.transpose(0, 1)  # (seq_len, batch_size, d_model)
            x = self.pos_encoding(x)
            x = x.transpose(0, 1)  # (batch_size, seq_len, d_model)
        
        # Store attention weights for analysis
        attention_weights_list = []
        
        # Pass through transformer layers
        for layer in self.layers:
            x, attn_weights = layer(x, cross_input, mask)
            attention_weights_list.append(attn_weights)
        
        # Final normalization and projection
        x = self.final_norm(x)
        x = self.output_projection(x)
        
        return x, attention_weights_list


def create_attention_model(model_type: str = "standard", **kwargs) -> AdvancedTransformerModel:
    """
    Factory function to create attention models.
    
    Args:
        model_type: Type of attention model
        **kwargs: Additional arguments
        
    Returns:
        Configured transformer model
    """
    config_map = {
        "standard": AttentionConfig(attention_type="standard"),
        "relative": AttentionConfig(attention_type="relative", use_relative_position=True),
        "local": AttentionConfig(attention_type="local", attention_window=64),
        "sparse": AttentionConfig(attention_type="sparse", sparse_topk=32)
    }
    
    if model_type not in config_map:
        raise ValueError(f"Unknown model type: {model_type}")
    
    config = config_map[model_type]
    
    # Update config with kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return AdvancedTransformerModel(config, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    # Test the attention mechanisms
    batch_size = 2
    seq_len = 64
    d_model = 256
    
    # Create test input
    x = torch.randn(batch_size, seq_len, d_model)
    
    # Test different attention types
    attention_types = ["standard", "relative", "local"]
    
    for attn_type in attention_types:
        print(f"\nTesting {attn_type} attention...")
        
        try:
            model = create_attention_model(attn_type, d_model=d_model, num_layers=2)
            output, attention_weights = model(x)
            
            print(f"Input shape: {x.shape}")
            print(f"Output shape: {output.shape}")
            print(f"Number of attention layers: {len(attention_weights)}")
            
            # Analyze attention patterns
            if attention_weights:
                stats = AttentionVisualizer.analyze_attention_patterns(attention_weights[0])
                print(f"Attention statistics: {stats}")
            
        except Exception as e:
            print(f"Error with {attn_type} attention: {e}")
    
    print("\nAttention mechanism testing completed!")


