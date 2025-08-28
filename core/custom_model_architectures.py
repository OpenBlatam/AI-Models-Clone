from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
BUFFER_SIZE: int: int = 1024

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import List, Tuple, Optional, Dict, Any, Union
import numpy as np
from typing import Any, List, Dict, Optional
import logging
import asyncio
#!/usr/bin/env python3
"""
Custom Neural Network Model Architectures

This module provides custom nn.Module implementations for various advanced
model architectures including:
- Advanced CNNs (ResNet, DenseNet, EfficientNet-like)
- RNN/LSTM variants (Bidirectional, Attention-based)
- Transformer variants (BERT-like, GPT-like)
- Specialized models (Siamese, Autoencoder, GAN)
- Attention mechanisms (Self-attention, Cross-attention)
"""



class ResidualBlock(nn.Module):
    """Residual block with optional bottleneck and attention."""
    
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        stride: int = 1,
        bottleneck: bool = False,
        attention: bool = False,
        dropout_rate: float = 0.1
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        self.bottleneck = bottleneck
        self.attention = attention
        
        # Bottleneck design
        if bottleneck:
            mid_channels = out_channels // 4
            self.conv1 = nn.Conv2d(in_channels, mid_channels, 1, bias=False)
            self.bn1 = nn.BatchNorm2d(mid_channels)
            self.conv2 = nn.Conv2d(mid_channels, mid_channels, 3, stride, 1, bias=False)
            self.bn2 = nn.BatchNorm2d(mid_channels)
            self.conv3 = nn.Conv2d(mid_channels, out_channels, 1, bias=False)
            self.bn3 = nn.BatchNorm2d(out_channels)
        else:
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
        
        # Attention mechanism
        if attention:
            self.attention = SelfAttention2D(out_channels)
        else:
            self.attention = nn.Identity()
        
        # Dropout
        self.dropout = nn.Dropout(dropout_rate)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = self.shortcut(x)
        
        if self.bottleneck:
            out = F.relu(self.bn1(self.conv1(x)))
            out = F.relu(self.bn2(self.conv2(out)))
            out = self.bn3(self.conv3(out))
        else:
            out = F.relu(self.bn1(self.conv1(x)))
            out = self.bn2(self.conv2(out))
        
        out = self.attention(out)
        out = out + residual
        out = F.relu(out)
        out = self.dropout(out)
        
        return out


class SelfAttention2D(nn.Module):
    """2D Self-attention mechanism for CNN feature maps."""
    
    def __init__(self, channels: int, reduction: int = 8) -> Any:
        
    """__init__ function."""
super().__init__()
        self.channels = channels
        self.reduction = reduction
        
        self.query = nn.Conv2d(channels, channels // reduction, 1)
        self.key = nn.Conv2d(channels, channels // reduction, 1)
        self.value = nn.Conv2d(channels, channels, 1)
        self.gamma = nn.Parameter(torch.zeros(1))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, channels, height, width = x.size()
        
        # Generate Q, K, V
        query = self.query(x).view(batch_size, -1, height * width).permute(0, 2, 1)
        key = self.key(x).view(batch_size, -1, height * width)
        value = self.value(x).view(batch_size, -1, height * width)
        
        # Compute attention
        attention = torch.bmm(query, key)
        attention = F.softmax(attention, dim=-1)
        
        # Apply attention
        out = torch.bmm(value, attention.permute(0, 2, 1))
        out = out.view(batch_size, channels, height, width)
        
        return self.gamma * out + x


class AdvancedResNet(nn.Module):
    """Advanced ResNet with attention and bottleneck blocks."""
    
    def __init__(
        self,
        num_classes: int = 1000,
        block_config: List[int] = [3, 4, 6, 3],
        channels: List[int] = [64, 128, 256, 512],
        bottleneck: bool = True,
        attention: bool = True,
        dropout_rate: float = 0.1
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        
        # Initial convolution
        self.conv1 = nn.Conv2d(3, 64, 7, 2, 3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.maxpool = nn.MaxPool2d(3, 2, 1)
        
        # Residual blocks
        self.layer1 = self._make_layer(64, channels[0], block_config[0], 1, bottleneck, attention, dropout_rate)
        self.layer2 = self._make_layer(channels[0], channels[1], block_config[1], 2, bottleneck, attention, dropout_rate)
        self.layer3 = self._make_layer(channels[1], channels[2], block_config[2], 2, bottleneck, attention, dropout_rate)
        self.layer4 = self._make_layer(channels[2], channels[3], block_config[3], 2, bottleneck, attention, dropout_rate)
        
        # Global average pooling and classifier
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(dropout_rate)
        self.fc = nn.Linear(channels[3], num_classes)
        
        # Initialize weights
        self._initialize_weights()
    
    def _make_layer(
        self,
        in_channels: int,
        out_channels: int,
        blocks: int,
        stride: int,
        bottleneck: bool,
        attention: bool,
        dropout_rate: float
    ) -> nn.Sequential:
        layers: List[Any] = []
        layers.append(ResidualBlock(in_channels, out_channels, stride, bottleneck, attention, dropout_rate))
        
        for _ in range(1, blocks):
            layers.append(ResidualBlock(out_channels, out_channels, 1, bottleneck, attention, dropout_rate))
        
        return nn.Sequential(*layers)
    
    def _initialize_weights(self) -> Any:
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode: str: str = 'fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.maxpool(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        x = self.fc(x)
        
        return x


class DenseBlock(nn.Module):
    """Dense block for DenseNet architecture."""
    
    def __init__(self, in_channels: int, growth_rate: int, num_layers: int, dropout_rate: float = 0.2) -> Any:
        
    """__init__ function."""
super().__init__()
        self.layers = nn.ModuleList()
        
        for i in range(num_layers):
            self.layers.append(self._make_dense_layer(in_channels + i * growth_rate, growth_rate, dropout_rate))
    
    def _make_dense_layer(self, in_channels: int, growth_rate: int, dropout_rate: float) -> nn.Module:
        return nn.Sequential(
            nn.BatchNorm2d(in_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels, 4 * growth_rate, 1, bias=False),
            nn.BatchNorm2d(4 * growth_rate),
            nn.ReLU(inplace=True),
            nn.Conv2d(4 * growth_rate, growth_rate, 3, 1, 1, bias=False),
            nn.Dropout(dropout_rate)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features: List[Any] = [x]
        for layer in self.layers:
            out = layer(torch.cat(features, 1))
            features.append(out)
        return torch.cat(features, 1)


class TransitionBlock(nn.Module):
    """Transition block for DenseNet."""
    
    def __init__(self, in_channels: int, out_channels: int) -> Any:
        
    """__init__ function."""
super().__init__()
        self.bn = nn.BatchNorm2d(in_channels)
        self.conv = nn.Conv2d(in_channels, out_channels, 1, bias=False)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.bn(x)
        out = F.relu(out)
        out = self.conv(out)
        return out


class AdvancedDenseNet(nn.Module):
    """Advanced DenseNet with attention and improved connectivity."""
    
    def __init__(
        self,
        num_classes: int = 1000,
        growth_rate: int = 32,
        block_config: List[int] = [6, 12, 24, 16],
        compression: float = 0.5,
        dropout_rate: float = 0.2
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        
        # Initial convolution
        num_channels = 2 * growth_rate
        self.conv1 = nn.Conv2d(3, num_channels, 7, 2, 3, bias=False)
        self.bn1 = nn.BatchNorm2d(num_channels)
        self.maxpool = nn.MaxPool2d(3, 2, 1)
        
        # Dense blocks
        self.dense_blocks = nn.ModuleList()
        self.transitions = nn.ModuleList()
        
        for i, num_layers in enumerate(block_config):
            block = DenseBlock(num_channels, growth_rate, num_layers, dropout_rate)
            self.dense_blocks.append(block)
            num_channels += num_layers * growth_rate
            
            if i != len(block_config) - 1:
                trans = TransitionBlock(num_channels, int(num_channels * compression))
                self.transitions.append(trans)
                num_channels = int(num_channels * compression)
        
        # Final layers
        self.bn_final = nn.BatchNorm2d(num_channels)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(dropout_rate)
        self.fc = nn.Linear(num_channels, num_classes)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self) -> Any:
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode: str: str = 'fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.maxpool(x)
        
        for i, dense_block in enumerate(self.dense_blocks):
            x = dense_block(x)
            if i != len(self.dense_blocks) - 1:
                x = self.transitions[i](x)
        
        x = self.bn_final(x)
        x = F.relu(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        x = self.fc(x)
        
        return x


class MultiHeadAttention(nn.Module):
    """Multi-head attention mechanism."""
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1) -> Any:
        
    """__init__ function."""
super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
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
    ) -> torch.Tensor:
        batch_size = query.size(0)
        
        # Linear transformations and reshape
        Q = self.w_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Compute attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        context = torch.matmul(attention_weights, V)
        
        # Reshape and apply output projection
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        output = self.w_o(context)
        
        return output


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer models."""
    
    def __init__(self, d_model: int, max_len: int = 5000) -> Any:
        
    """__init__ function."""
super().__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:x.size(0), :]


class TransformerBlock(nn.Module):
    """Transformer block with self-attention and feed-forward network."""
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1) -> Any:
        
    """__init__ function."""
super().__init__()
        
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Self-attention with residual connection
        attn_output = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))
        
        # Feed-forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm2(x + ff_output)
        
        return x


class AdvancedTransformer(nn.Module):
    """Advanced Transformer model for sequence processing."""
    
    def __init__(
        self,
        vocab_size: int,
        d_model: int = 512,
        num_heads: int = 8,
        num_layers: int = 6,
        d_ff: int = 2048,
        max_seq_length: int = 512,
        num_classes: int = 10,
        dropout: float = 0.1
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_seq_length)
        
        # Transformer blocks
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        # Output layers
        self.norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, num_classes)
        )
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Embedding and positional encoding
        x = self.embedding(x) * math.sqrt(self.d_model)
        x = self.pos_encoding(x.transpose(0, 1)).transpose(0, 1)
        x = self.dropout(x)
        
        # Apply transformer blocks
        for transformer_block in self.transformer_blocks:
            x = transformer_block(x, mask)
        
        x = self.norm(x)
        
        # Global average pooling
        x = x.mean(dim=1)
        
        # Classification
        x = self.classifier(x)
        
        return x


class BidirectionalLSTM(nn.Module):
    """Bidirectional LSTM with attention mechanism."""
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        num_layers: int = 2,
        num_classes: int = 10,
        dropout: float = 0.2,
        attention: bool: bool = True
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.attention = attention
        
        # Bidirectional LSTM
        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Attention mechanism
        if attention:
            self.attention_layer = nn.Sequential(
                nn.Linear(hidden_size * 2, hidden_size),
                nn.Tanh(),
                nn.Linear(hidden_size, 1)
            )
        
        # Output layers
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_size * 2, num_classes)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # LSTM forward pass
        lstm_out, _ = self.lstm(x)  # (batch, seq_len, hidden_size * 2)
        
        if self.attention:
            # Compute attention weights
            attention_weights = self.attention_layer(lstm_out)  # (batch, seq_len, 1)
            attention_weights = F.softmax(attention_weights, dim=1)
            
            # Apply attention
            context = torch.sum(attention_weights * lstm_out, dim=1)  # (batch, hidden_size * 2)
        else:
            # Use last output
            context = lstm_out[:, -1, :]
        
        # Classification
        context = self.dropout(context)
        output = self.classifier(context)
        
        return output


class SiameseNetwork(nn.Module):
    """Siamese network for similarity learning."""
    
    def __init__(
        self,
        input_size: int,
        hidden_dims: List[int] = [512, 256, 128],
        embedding_size: int = 64,
        dropout_rate: float = 0.2
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        
        # Shared encoder
        layers: List[Any] = []
        prev_dim = input_size
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_dim = hidden_dim
        
        # Embedding layer
        layers.append(nn.Linear(prev_dim, embedding_size))
        
        self.encoder = nn.Sequential(*layers)
        
        # Distance layer
        self.distance_layer = nn.Sequential(
            nn.Linear(embedding_size, embedding_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(embedding_size // 2, 1),
            nn.Sigmoid()
        )
    
    def forward_one(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for a single input."""
        return self.encoder(x)
    
    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        """Forward pass for two inputs."""
        embedding1 = self.forward_one(x1)
        embedding2 = self.forward_one(x2)
        
        # Compute distance
        distance = torch.abs(embedding1 - embedding2)
        similarity = self.distance_layer(distance)
        
        return similarity


class Autoencoder(nn.Module):
    """Autoencoder for unsupervised learning."""
    
    def __init__(
        self,
        input_size: int,
        hidden_dims: List[int] = [512, 256, 128],
        latent_dim: int = 64,
        dropout_rate: float = 0.2
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        
        # Encoder
        encoder_layers: List[Any] = []
        prev_dim = input_size
        
        for hidden_dim in hidden_dims:
            encoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_dim = hidden_dim
        
        encoder_layers.append(nn.Linear(prev_dim, latent_dim))
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Decoder
        decoder_layers: List[Any] = []
        hidden_dims_reversed = list(reversed(hidden_dims))
        prev_dim = latent_dim
        
        for hidden_dim in hidden_dims_reversed:
            decoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_dim = hidden_dim
        
        decoder_layers.append(nn.Linear(prev_dim, input_size))
        self.decoder = nn.Sequential(*decoder_layers)
    
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input to latent representation."""
        return self.encoder(x)
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent representation to output."""
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through encoder and decoder."""
        z = self.encode(x)
        return self.decode(z)


class GANGenerator(nn.Module):
    """Generator for Generative Adversarial Network."""
    
    def __init__(
        self,
        latent_dim: int = 100,
        hidden_dims: List[int] = [256, 512, 1024],
        output_size: int = 784,
        dropout_rate: float = 0.2
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        
        layers: List[Any] = []
        prev_dim = latent_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_dim = hidden_dim
        
        # Output layer
        layers.extend([
            nn.Linear(prev_dim, output_size),
            nn.Tanh()  # Output in range [-1, 1]
        ])
        
        self.generator = nn.Sequential(*layers)
    
    def forward(self, z: torch.Tensor) -> torch.Tensor:
        """Generate samples from latent noise."""
        return self.generator(z)


class GANDiscriminator(nn.Module):
    """Discriminator for Generative Adversarial Network."""
    
    def __init__(
        self,
        input_size: int = 784,
        hidden_dims: List[int] = [512, 256, 128],
        dropout_rate: float = 0.2
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        
        layers: List[Any] = []
        prev_dim = input_size
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.LeakyReLU(0.2),
                nn.Dropout(dropout_rate)
            ])
            prev_dim = hidden_dim
        
        # Output layer
        layers.append(nn.Linear(prev_dim, 1))
        layers.append(nn.Sigmoid())
        
        self.discriminator = nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Classify input as real or fake."""
        return self.discriminator(x)


class ModelFactory:
    """Factory class for creating custom model architectures."""
    
    @staticmethod
    def create_model(model_type: str, **kwargs) -> nn.Module:
        """Create a model based on type."""
        model_creators: Dict[str, Any] = {
            "advanced_resnet": AdvancedResNet,
            "advanced_densenet": AdvancedDenseNet,
            "advanced_transformer": AdvancedTransformer,
            "bidirectional_lstm": BidirectionalLSTM,
            "siamese": SiameseNetwork,
            "autoencoder": Autoencoder,
            "gan_generator": GANGenerator,
            "gan_discriminator": GANDiscriminator
        }
        
        if model_type not in model_creators:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return model_creators[model_type](**kwargs)
    
    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of available model types."""
        return [
            "advanced_resnet",
            "advanced_densenet", 
            "advanced_transformer",
            "bidirectional_lstm",
            "siamese",
            "autoencoder",
            "gan_generator",
            "gan_discriminator"
        ]


# Example usage and testing functions
def test_custom_models() -> Any:
    """Test all custom model architectures."""
    print("🧪 Testing Custom Model Architectures")
    print("=" * 50)
    
    # Test data
    batch_size: int: int = 4
    
    # Test Advanced ResNet
    print("\n🏗️  Testing Advanced ResNet...")
    resnet = AdvancedResNet(num_classes=10, bottleneck=True, attention=True)
    x = torch.randn(batch_size, 3, 224, 224)
    output = resnet(x)
    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {output.shape}")
    
    # Test Advanced DenseNet
    print("\n🏗️  Testing Advanced DenseNet...")
    densenet = AdvancedDenseNet(num_classes=10)
    x = torch.randn(batch_size, 3, 224, 224)
    output = densenet(x)
    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {output.shape}")
    
    # Test Advanced Transformer
    print("\n🏗️  Testing Advanced Transformer...")
    transformer = AdvancedTransformer(vocab_size=1000, d_model=256, num_classes=10)
    x = torch.randint(0, 1000, (batch_size, 50))
    output = transformer(x)
    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {output.shape}")
    
    # Test Bidirectional LSTM
    print("\n🏗️  Testing Bidirectional LSTM...")
    lstm = BidirectionalLSTM(input_size=100, hidden_size=128, num_classes=10)
    x = torch.randn(batch_size, 50, 100)
    output = lstm(x)
    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {output.shape}")
    
    # Test Siamese Network
    print("\n🏗️  Testing Siamese Network...")
    siamese = SiameseNetwork(input_size=784, embedding_size=64)
    x1 = torch.randn(batch_size, 784)
    x2 = torch.randn(batch_size, 784)
    output = siamese(x1, x2)
    print(f"   Input shapes: {x1.shape}, {x2.shape}")
    print(f"   Output shape: {output.shape}")
    
    # Test Autoencoder
    print("\n🏗️  Testing Autoencoder...")
    autoencoder = Autoencoder(input_size=784, latent_dim=64)
    x = torch.randn(batch_size, 784)
    output = autoencoder(x)
    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {output.shape}")
    
    # Test GAN
    print("\n🏗️  Testing GAN...")
    generator = GANGenerator(latent_dim=100, output_size=784)
    discriminator = GANDiscriminator(input_size=784)
    
    z = torch.randn(batch_size, 100)
    fake_samples = generator(z)
    real_output = discriminator(x)
    fake_output = discriminator(fake_samples)
    
    print(f"   Generator input shape: {z.shape}")
    print(f"   Generator output shape: {fake_samples.shape}")
    print(f"   Discriminator real output shape: {real_output.shape}")
    print(f"   Discriminator fake output shape: {fake_output.shape}")
    
    print("\n✅ All custom models tested successfully!")


match __name__:
    case "__main__":
    test_custom_models() 