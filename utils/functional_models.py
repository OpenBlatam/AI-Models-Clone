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
from typing import Dict, Any, Tuple, Optional, Callable
from functools import partial
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Functional Model Creation for Deep Learning Framework
Uses pure functions instead of classes for model creation
"""


def create_linear_layer(input_size: int, output_size: int, bias: bool = True) -> nn.Linear:
    """Create a linear layer with proper initialization."""
    layer = nn.Linear(input_size, output_size, bias=bias)
    nn.init.xavier_uniform_(layer.weight)
    if bias:
        nn.init.zeros_(layer.bias)
    return layer

def create_conv_layer(in_channels: int, out_channels: int, kernel_size: int = 3, 
                     stride: int = 1, padding: int = 1) -> nn.Conv2d:
    """Create a convolutional layer with proper initialization."""
    layer = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding)
    nn.init.kaiming_normal_(layer.weight, mode: str: str = 'fan_out', nonlinearity='relu')
    return layer

def create_attention_layer(hidden_size: int, num_heads: int, dropout: float = 0.1) -> nn.Module:
    """Create a multi-head attention layer."""
    return nn.MultiheadAttention(hidden_size, num_heads, dropout=dropout, batch_first=True)

def create_transformer_block(hidden_size: int, num_heads: int, ff_size: int, 
                           dropout: float = 0.1) -> nn.Module:
    """Create a transformer block."""
    return nn.Sequential(
        nn.LayerNorm(hidden_size),
        create_attention_layer(hidden_size, num_heads, dropout),
        nn.LayerNorm(hidden_size),
        nn.Linear(hidden_size, ff_size),
        nn.GELU(),
        nn.Dropout(dropout),
        nn.Linear(ff_size, hidden_size),
        nn.Dropout(dropout)
    )

def create_simple_classifier(input_size: int, num_classes: int, 
                           hidden_sizes: Tuple[int, ...] = (512, 256)) -> nn.Module:
    """Create a simple classifier using functional composition."""
    layers: List[Any] = []
    prev_size = input_size
    
    for hidden_size in hidden_sizes:
        layers.extend([
            create_linear_layer(prev_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2)
        ])
        prev_size = hidden_size
    
    layers.append(create_linear_layer(prev_size, num_classes))
    return nn.Sequential(*layers)

def create_cnn_classifier(input_channels: int, num_classes: int, 
                        conv_channels: Tuple[int, ...] = (32, 64, 128)) -> nn.Module:
    """Create a CNN classifier using functional composition."""
    layers: List[Any] = []
    prev_channels = input_channels
    
    for channels in conv_channels:
        layers.extend([
            create_conv_layer(prev_channels, channels),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.BatchNorm2d(channels)
        ])
        prev_channels = channels
    
    # Calculate flattened size
    flattened_size = prev_channels * 4 * 4  # Assuming 32x32 input
    
    layers.extend([
        nn.AdaptiveAvgPool2d((4, 4)),
        nn.Flatten(),
        create_linear_layer(flattened_size, num_classes)
    ])
    
    return nn.Sequential(*layers)

def create_transformer_classifier(vocab_size: int, num_classes: int, 
                                hidden_size: int = 768, num_layers: int = 6,
                                num_heads: int = 12, max_length: int = 512) -> nn.Module:
    """Create a transformer classifier."""
    return nn.Sequential(
        nn.Embedding(vocab_size, hidden_size),
        nn.LayerNorm(hidden_size),
        *[create_transformer_block(hidden_size, num_heads, hidden_size * 4) 
          for _ in range(num_layers)],
        nn.LayerNorm(hidden_size),
        nn.AdaptiveAvgPool1d(1),
        nn.Flatten(),
        create_linear_layer(hidden_size, num_classes)
    )

def create_autoencoder(input_size: int, latent_size: int, 
                      encoder_sizes: Tuple[int, ...] = (512, 256),
                      decoder_sizes: Tuple[int, ...] = (256, 512)) -> Tuple[nn.Module, nn.Module]:
    """Create encoder and decoder for autoencoder."""
    
    # Encoder
    encoder_layers: List[Any] = []
    prev_size = input_size
    for size in encoder_sizes:
        encoder_layers.extend([
            create_linear_layer(prev_size, size),
            nn.ReLU(),
            nn.BatchNorm1d(size)
        ])
        prev_size = size
    
    encoder_layers.append(create_linear_layer(prev_size, latent_size))
    encoder = nn.Sequential(*encoder_layers)
    
    # Decoder
    decoder_layers: List[Any] = []
    prev_size = latent_size
    for size in decoder_sizes:
        decoder_layers.extend([
            create_linear_layer(prev_size, size),
            nn.ReLU(),
            nn.BatchNorm1d(size)
        ])
        prev_size = size
    
    decoder_layers.append(create_linear_layer(prev_size, input_size))
    decoder = nn.Sequential(*decoder_layers)
    
    return encoder, decoder

def create_model_by_type(model_type: str, config: Dict[str, Any]) -> nn.Module:
    """Create model based on type using functional approach."""
    model_creators: Dict[str, Any] = {
        "classifier": lambda: create_simple_classifier(
            config.get("input_size", 784),
            config.get("num_classes", 10),
            config.get("hidden_sizes", (512, 256))
        ),
        "cnn": lambda: create_cnn_classifier(
            config.get("input_channels", 3),
            config.get("num_classes", 10),
            config.get("conv_channels", (32, 64, 128))
        ),
        "transformer": lambda: create_transformer_classifier(
            config.get("vocab_size", 1000),
            config.get("num_classes", 10),
            config.get("hidden_size", 768),
            config.get("num_layers", 6),
            config.get("num_heads", 12)
        )
    }
    
    creator = model_creators.get(model_type)
    if creator is None:
        raise ValueError(f"Unknown model type: {model_type}")
    
    return creator()

def count_parameters(model: nn.Module) -> int:
    """Count trainable parameters in model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def get_model_summary(model: nn.Module, input_shape: Tuple[int, ...]) -> Dict[str, Any]:
    """Get model summary information."""
    total_params = count_parameters(model)
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    # Test forward pass to get output shape
    with torch.no_grad():
        dummy_input = torch.randn(1, *input_shape)
        output = model(dummy_input)
        output_shape = output.shape[1:]
    
    return {
        "total_parameters": total_params,
        "trainable_parameters": trainable_params,
        "input_shape": input_shape,
        "output_shape": output_shape,
        "model_size_mb": total_params * 4 / (1024 * 1024)  # Assuming float32
    }

# Usage examples
if __name__ == "__main__":
    # Create different model types
    classifier = create_simple_classifier(784, 10)
    cnn = create_cnn_classifier(3, 10)
    transformer = create_transformer_classifier(1000, 10)
    
    # Create autoencoder
    encoder, decoder = create_autoencoder(784, 64)
    
    # Create model by type
    config: Dict[str, Any] = {"input_size": 784, "num_classes": 10}
    model = create_model_by_type("classifier", config)
    
    # Get model summary
    summary = get_model_summary(model, (784,))
    print(f"Model summary: {summary}") 