#!/usr/bin/env python3
"""
Advanced PyTorch Models with Autograd Integration

This module provides advanced neural network architectures with
comprehensive autograd support and modern deep learning techniques.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import TransformerEncoder, TransformerDecoder
import math
from typing import Optional, Tuple, List, Dict, Any
import numpy as np


class SelfAttention(nn.Module):
    """Self-attention mechanism with autograd support.
    
    This module implements scaled dot-product attention with
    full gradient tracking for backpropagation.
    """
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        """Initialize self-attention module.
        
        Args:
            d_model: Model dimension
            num_heads: Number of attention heads
            dropout: Dropout probability
        """
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # Linear projections for Q, K, V
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = math.sqrt(self.d_k)
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass with autograd support.
        
        Args:
            query: Query tensor (batch_size, seq_len, d_model)
            key: Key tensor (batch_size, seq_len, d_model)
            value: Value tensor (batch_size, seq_len, d_model)
            mask: Optional attention mask
            
        Returns:
            Tuple of (output, attention_weights) with gradient tracking
        """
        batch_size = query.size(0)
        
        # Linear transformations with autograd
        Q = self.w_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        context = torch.matmul(attention_weights, V)
        context = context.transpose(1, 2).contiguous().view(
            batch_size, -1, self.d_model
        )
        
        # Final linear projection
        output = self.w_o(context)
        
        return output, attention_weights


class MultiHeadAttention(nn.Module):
    """Multi-head attention with residual connection and layer normalization.
    
    This module combines multiple attention heads with proper
    gradient flow and normalization.
    """
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        """Initialize multi-head attention.
        
        Args:
            d_model: Model dimension
            num_heads: Number of attention heads
            dropout: Dropout probability
        """
        super().__init__()
        
        self.attention = SelfAttention(d_model, num_heads, dropout)
        self.layer_norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass with residual connection.
        
        Args:
            query: Query tensor
            key: Key tensor
            value: Value tensor
            mask: Optional attention mask
            
        Returns:
            Output tensor with gradient tracking
        """
        # Residual connection
        residual = query
        
        # Self-attention
        output, _ = self.attention(query, key, value, mask)
        output = self.dropout(output)
        
        # Add residual and normalize
        output = self.layer_norm(residual + output)
        
        return output


class FeedForward(nn.Module):
    """Feed-forward network with residual connection.
    
    This module implements a two-layer feed-forward network
    with proper gradient flow and normalization.
    """
    
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        """Initialize feed-forward network.
        
        Args:
            d_model: Model dimension
            d_ff: Feed-forward dimension
            dropout: Dropout probability
        """
        super().__init__()
        
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(d_model)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with residual connection.
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor with gradient tracking
        """
        residual = x
        
        # Feed-forward computation
        x = F.relu(self.linear1(x))
        x = self.dropout(x)
        x = self.linear2(x)
        x = self.dropout(x)
        
        # Add residual and normalize
        x = self.layer_norm(residual + x)
        
        return x


class TransformerBlock(nn.Module):
    """Complete transformer block with attention and feed-forward.
    
    This module combines multi-head attention and feed-forward
    networks with proper gradient flow.
    """
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1):
        """Initialize transformer block.
        
        Args:
            d_model: Model dimension
            num_heads: Number of attention heads
            d_ff: Feed-forward dimension
            dropout: Dropout probability
        """
        super().__init__()
        
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
    
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass through transformer block.
        
        Args:
            x: Input tensor
            mask: Optional attention mask
            
        Returns:
            Output tensor with gradient tracking
        """
        # Self-attention
        x = self.attention(x, x, x, mask)
        
        # Feed-forward
        x = self.feed_forward(x)
        
        return x


class AdvancedTransformer(nn.Module):
    """Advanced transformer model with multiple blocks and autograd.
    
    This model implements a complete transformer architecture
    with full gradient tracking and modern optimizations.
    """
    
    def __init__(
        self,
        vocab_size: int,
        d_model: int = 512,
        num_heads: int = 8,
        num_layers: int = 6,
        d_ff: int = 2048,
        max_seq_length: int = 512,
        dropout: float = 0.1
    ):
        """Initialize advanced transformer.
        
        Args:
            vocab_size: Size of vocabulary
            d_model: Model dimension
            num_heads: Number of attention heads
            num_layers: Number of transformer layers
            d_ff: Feed-forward dimension
            max_seq_length: Maximum sequence length
            dropout: Dropout probability
        """
        super().__init__()
        
        self.d_model = d_model
        self.max_seq_length = max_seq_length
        
        # Embedding layers
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = nn.Parameter(
            torch.randn(max_seq_length, d_model)
        )
        
        # Transformer blocks
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        # Output projection
        self.output_projection = nn.Linear(d_model, vocab_size)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        self._initialize_weights()
    
    def _initialize_weights(self) -> None:
        """Initialize transformer weights."""
        nn.init.normal_(self.embedding.weight, mean=0, std=0.02)
        nn.init.normal_(self.pos_encoding, mean=0, std=0.02)
        
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def create_positional_encoding(self, seq_length: int) -> torch.Tensor:
        """Create positional encoding for sequences.
        
        Args:
            seq_length: Length of sequence
            
        Returns:
            Positional encoding tensor
        """
        pos_encoding = torch.zeros(seq_length, self.d_model)
        position = torch.arange(0, seq_length).unsqueeze(1).float()
        
        div_term = torch.exp(
            torch.arange(0, self.d_model, 2).float() *
            -(math.log(10000.0) / self.d_model)
        )
        
        pos_encoding[:, 0::2] = torch.sin(position * div_term)
        pos_encoding[:, 1::2] = torch.cos(position * div_term)
        
        return pos_encoding
    
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass with autograd support.
        
        Args:
            x: Input tensor (batch_size, seq_length)
            mask: Optional attention mask
            
        Returns:
            Output tensor with gradient tracking
        """
        batch_size, seq_length = x.shape
        
        # Ensure input requires gradients
        if not x.requires_grad:
            x.requires_grad_(True)
        
        # Embedding and positional encoding
        x = self.embedding(x) * math.sqrt(self.d_model)
        
        # Add positional encoding
        pos_encoding = self.create_positional_encoding(seq_length).to(x.device)
        x = x + pos_encoding[:seq_length, :].unsqueeze(0)
        
        # Apply dropout
        x = self.dropout(x)
        
        # Pass through transformer blocks
        for transformer_block in self.transformer_blocks:
            x = transformer_block(x, mask)
        
        # Output projection
        x = self.output_projection(x)
        
        return x


class ResidualBlock(nn.Module):
    """Residual block with batch normalization and autograd.
    
    This module implements a residual connection with
    proper gradient flow for deep networks.
    """
    
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        """Initialize residual block.
        
        Args:
            in_channels: Number of input channels
            out_channels: Number of output channels
            stride: Stride for convolution
        """
        super().__init__()
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # Shortcut connection
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with residual connection.
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor with gradient tracking
        """
        residual = x
        
        # Main path
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        
        # Add residual connection
        out += self.shortcut(residual)
        out = F.relu(out)
        
        return out


class ResNet(nn.Module):
    """ResNet architecture with autograd support.
    
    This module implements a ResNet architecture with
    residual connections and full gradient tracking.
    """
    
    def __init__(self, block: nn.Module, num_blocks: List[int], num_classes: int = 10):
        """Initialize ResNet.
        
        Args:
            block: Residual block type
            num_blocks: Number of blocks in each layer
            num_classes: Number of output classes
        """
        super().__init__()
        
        self.in_channels = 64
        
        # Initial convolution
        self.conv1 = nn.Conv2d(3, 64, 3, 1, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        
        # Residual layers
        self.layer1 = self._make_layer(block, 64, num_blocks[0], 1)
        self.layer2 = self._make_layer(block, 128, num_blocks[1], 2)
        self.layer3 = self._make_layer(block, 256, num_blocks[2], 2)
        self.layer4 = self._make_layer(block, 512, num_blocks[3], 2)
        
        # Global average pooling and classification
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)
    
    def _make_layer(
        self,
        block: nn.Module,
        out_channels: int,
        num_blocks: int,
        stride: int
    ) -> nn.Sequential:
        """Create a layer of residual blocks.
        
        Args:
            block: Residual block type
            out_channels: Number of output channels
            num_blocks: Number of blocks
            stride: Stride for first block
            
        Returns:
            Sequential layer of residual blocks
        """
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        
        for stride in strides:
            layers.append(block(self.in_channels, out_channels, stride))
            self.in_channels = out_channels
        
        return nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with autograd support.
        
        Args:
            x: Input tensor (batch_size, channels, height, width)
            
        Returns:
            Output tensor with gradient tracking
        """
        # Ensure input requires gradients
        if not x.requires_grad:
            x.requires_grad_(True)
        
        # Initial convolution
        x = F.relu(self.bn1(self.conv1(x)))
        
        # Residual layers
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        # Global average pooling
        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        
        # Classification
        x = self.fc(x)
        
        return x


def resnet18(num_classes: int = 10) -> ResNet:
    """Create ResNet-18 model.
    
    Args:
        num_classes: Number of output classes
        
    Returns:
        ResNet-18 model with autograd support
    """
    return ResNet(ResidualBlock, [2, 2, 2, 2], num_classes)


def resnet34(num_classes: int = 10) -> ResNet:
    """Create ResNet-34 model.
    
    Args:
        num_classes: Number of output classes
        
    Returns:
        ResNet-34 model with autograd support
    """
    return ResNet(ResidualBlock, [3, 4, 6, 3], num_classes)


class AttentionMechanism(nn.Module):
    """General attention mechanism with autograd.
    
    This module implements a flexible attention mechanism
    that can be used in various architectures.
    """
    
    def __init__(self, d_model: int, d_k: int, d_v: int):
        """Initialize attention mechanism.
        
        Args:
            d_model: Model dimension
            d_k: Key dimension
            d_v: Value dimension
        """
        super().__init__()
        
        self.d_k = d_k
        self.d_v = d_v
        
        # Linear projections
        self.w_q = nn.Linear(d_model, d_k)
        self.w_k = nn.Linear(d_model, d_k)
        self.w_v = nn.Linear(d_model, d_v)
        self.w_o = nn.Linear(d_v, d_model)
        
        self.scale = math.sqrt(d_k)
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass with attention computation.
        
        Args:
            query: Query tensor
            key: Key tensor
            value: Value tensor
            mask: Optional attention mask
            
        Returns:
            Tuple of (output, attention_weights) with gradient tracking
        """
        # Linear transformations
        Q = self.w_q(query)
        K = self.w_k(key)
        V = self.w_v(value)
        
        # Attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        # Attention weights
        attention_weights = F.softmax(scores, dim=-1)
        
        # Apply attention to values
        context = torch.matmul(attention_weights, V)
        
        # Output projection
        output = self.w_o(context)
        
        return output, attention_weights


class CustomLoss(nn.Module):
    """Custom loss function with autograd support.
    
    This module demonstrates how to create custom loss functions
    that work seamlessly with PyTorch's autograd system.
    """
    
    def __init__(self, alpha: float = 0.5):
        """Initialize custom loss.
        
        Args:
            alpha: Weight for combining losses
        """
        super().__init__()
        self.alpha = alpha
        self.ce_loss = nn.CrossEntropyLoss()
    
    def forward(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        features: torch.Tensor
    ) -> torch.Tensor:
        """Forward pass with custom loss computation.
        
        Args:
            predictions: Model predictions
            targets: Target labels
            features: Feature representations
            
        Returns:
            Combined loss with gradient tracking
        """
        # Cross-entropy loss
        ce_loss = self.ce_loss(predictions, targets)
        
        # Feature regularization loss
        feature_norm = torch.norm(features, p=2, dim=1).mean()
        reg_loss = 0.1 * feature_norm
        
        # Combined loss
        total_loss = self.alpha * ce_loss + (1 - self.alpha) * reg_loss
        
        return total_loss


# Example usage and demonstration
def demonstrate_advanced_models():
    """Demonstrate advanced PyTorch models with autograd."""
    print("Demonstrating Advanced PyTorch Models with Autograd...")
    
    # Create sample data
    batch_size, seq_length, vocab_size = 4, 10, 1000
    x = torch.randint(0, vocab_size, (batch_size, seq_length))
    
    # Test Advanced Transformer
    transformer = AdvancedTransformer(vocab_size, d_model=128, num_layers=2)
    output = transformer(x)
    print(f"Transformer output shape: {output.shape}")
    
    # Test ResNet
    resnet = resnet18(num_classes=10)
    x_resnet = torch.randn(2, 3, 32, 32)
    output_resnet = resnet(x_resnet)
    print(f"ResNet output shape: {output_resnet.shape}")
    
    # Test custom loss
    loss_fn = CustomLoss()
    predictions = torch.randn(4, 10)
    targets = torch.randint(0, 10, (4,))
    features = torch.randn(4, 128)
    loss = loss_fn(predictions, targets, features)
    print(f"Custom loss: {loss.item()}")
    
    print("Advanced models demonstration completed!")


if __name__ == "__main__":
    demonstrate_advanced_models() 