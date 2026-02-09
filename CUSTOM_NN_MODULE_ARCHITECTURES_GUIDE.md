# 🏗️ Custom nn.Module Architectures Guide

## Overview

This guide covers comprehensive custom `nn.Module` implementations for deep learning models, including transformers, CNNs, RNNs, and hybrid architectures. All implementations follow PyTorch best practices and are production-ready.

## 🎯 Key Principles

### **1. Proper Inheritance**
- Always inherit from `nn.Module`
- Call `super().__init__()` in constructor
- Implement `forward()` method

### **2. Weight Initialization**
- Use appropriate initialization methods for different layer types
- Follow PyTorch conventions (Xavier, Kaiming, etc.)
- Initialize biases to zero

### **3. Module Organization**
- Use `nn.ModuleList` for variable numbers of layers
- Group related layers in `nn.Sequential`
- Implement proper forward pass with clear flow

## 🚀 Custom Transformer Architecture

### **CustomTransformerBlock**

```python
class CustomTransformerBlock(nn.Module):
    """Custom transformer block with configurable attention and feed-forward layers."""
    
    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_ff = d_ff
        
        # Multi-head self-attention
        self.attention = nn.MultiheadAttention(
            d_model, n_heads, dropout=dropout, batch_first=True
        )
        
        # Feed-forward network
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
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
        """Forward pass with residual connections and layer normalization."""
        # Self-attention with residual connection
        attn_output, _ = self.attention(x, x, x, attn_mask=mask)
        x = self.norm1(x + self.dropout(attn_output))
        
        # Feed-forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm2(x + ff_output)
        
        return x
```

**Key Features:**
- ✅ Multi-head attention with configurable heads
- ✅ Residual connections for gradient flow
- ✅ Layer normalization for training stability
- ✅ Dropout for regularization
- ✅ GELU activation for better performance

### **CustomTransformerModel**

```python
class CustomTransformerModel(nn.Module):
    """Custom transformer model with configurable architecture."""
    
    def __init__(self, vocab_size: int, d_model: int = 512, n_layers: int = 6, 
                 n_heads: int = 8, d_ff: int = 2048, max_seq_len: int = 512, 
                 dropout: float = 0.1, num_labels: int = 2):
        super().__init__()
        
        # Token embedding
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        
        # Positional encoding
        self.pos_encoding = nn.Parameter(torch.randn(1, max_seq_len, d_model))
        
        # Transformer blocks
        self.transformer_blocks = nn.ModuleList([
            CustomTransformerBlock(d_model, n_heads, d_ff, dropout)
            for _ in range(n_layers)
        ])
        
        # Output head
        self.classifier = nn.Linear(d_model, num_labels)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights with proper initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
```

**Key Features:**
- ✅ Configurable model dimensions and depth
- ✅ Learnable positional encodings
- ✅ Stacked transformer blocks
- ✅ Proper weight initialization
- ✅ Classification head for downstream tasks

## 🖼️ Custom CNN Architecture

### **CustomCNNModel**

```python
class CustomCNNModel(nn.Module):
    """Custom CNN model for sequence classification."""
    
    def __init__(self, vocab_size: int, embed_dim: int = 128, num_filters: int = 128, 
                 filter_sizes: List[int] = [3, 4, 5], num_labels: int = 2, dropout: float = 0.5):
        super().__init__()
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        
        # Convolutional layers with different kernel sizes
        self.convs = nn.ModuleList([
            nn.Conv1d(embed_dim, num_filters, kernel_size=k, padding=k//2)
            for k in filter_sizes
        ])
        
        # Global pooling layers
        self.global_max_pool = nn.AdaptiveMaxPool1d(1)
        self.global_avg_pool = nn.AdaptiveAvgPool1d(1)
        
        # Classification head
        self.classifier = nn.Linear(num_filters * len(filter_sizes) * 2, num_labels)
    
    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None,
                labels: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        # Embedding
        x = self.embedding(input_ids)
        
        # Transpose for convolution
        x = x.transpose(1, 2)
        
        # Apply convolutions and pooling
        conv_outputs = []
        for conv in self.convs:
            conv_out = F.relu(conv(x))
            
            # Global max pooling
            max_pool = self.global_max_pool(conv_out).squeeze(-1)
            
            # Global average pooling
            avg_pool = self.global_avg_pool(conv_out).squeeze(-1)
            
            # Concatenate both pooling results
            pool_out = torch.cat([max_pool, avg_pool], dim=1)
            conv_outputs.append(pool_out)
        
        # Concatenate all convolution outputs
        x = torch.cat(conv_outputs, dim=1)
        
        # Classification
        logits = self.classifier(x)
        
        return {"logits": logits}
```

**Key Features:**
- ✅ Multiple filter sizes for different n-gram patterns
- ✅ Global max and average pooling
- ✅ Concatenation of different pooling results
- ✅ Configurable embedding and filter dimensions

## 🔄 Custom RNN Architecture

### **CustomRNNModel**

```python
class CustomRNNModel(nn.Module):
    """Custom RNN model with LSTM/GRU support."""
    
    def __init__(self, vocab_size: int, embed_dim: int = 128, hidden_dim: int = 256, 
                 num_layers: int = 2, rnn_type: str = "lstm", bidirectional: bool = True,
                 num_labels: int = 2, dropout: float = 0.5):
        super().__init__()
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        
        # RNN layer with configurable type
        if self.rnn_type == "lstm":
            self.rnn = nn.LSTM(
                embed_dim, hidden_dim, num_layers, 
                bidirectional=bidirectional, dropout=dropout if num_layers > 1 else 0,
                batch_first=True
            )
        elif self.rnn_type == "gru":
            self.rnn = nn.GRU(
                embed_dim, hidden_dim, num_layers,
                bidirectional=bidirectional, dropout=dropout if num_layers > 1 else 0,
                batch_first=True
            )
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            self.output_dim, num_heads=8, batch_first=True
        )
        
        # Classification head
        self.classifier = nn.Linear(self.output_dim, num_labels)
    
    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None,
                labels: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        # Embedding
        x = self.embedding(input_ids)
        
        # RNN forward pass
        rnn_output, _ = self.rnn(x)
        
        # Apply attention
        attn_output, _ = self.attention(rnn_output, rnn_output, rnn_output)
        
        # Global average pooling
        x = attn_output.mean(dim=1)
        
        # Classification
        logits = self.classifier(x)
        
        return {"logits": logits}
```

**Key Features:**
- ✅ Support for both LSTM and GRU
- ✅ Bidirectional RNN support
- ✅ Multi-head attention mechanism
- ✅ Configurable number of layers
- ✅ Proper dropout handling

## 🔀 Custom Hybrid Architecture

### **CustomHybridModel**

```python
class CustomHybridModel(nn.Module):
    """Custom hybrid model combining CNN, RNN, and Transformer components."""
    
    def __init__(self, vocab_size: int, embed_dim: int = 128, hidden_dim: int = 256,
                 num_filters: int = 128, filter_sizes: List[int] = [3, 4, 5],
                 num_layers: int = 2, num_heads: int = 8, num_labels: int = 2, 
                 dropout: float = 0.5):
        super().__init__()
        
        # Shared embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        
        # CNN branch
        self.cnn_convs = nn.ModuleList([
            nn.Conv1d(embed_dim, num_filters, kernel_size=k, padding=k//2)
            for k in filter_sizes
        ])
        
        # RNN branch
        self.rnn = nn.LSTM(
            embed_dim, hidden_dim, num_layers, 
            bidirectional=True, dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Transformer branch
        self.transformer_block = CustomTransformerBlock(
            embed_dim, num_heads, hidden_dim, dropout
        )
        
        # Feature fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(total_features, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        # Classification head
        self.classifier = nn.Linear(hidden_dim // 2, num_labels)
    
    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None,
                labels: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        # Shared embedding
        x = self.embedding(input_ids)
        
        # CNN branch
        x_cnn = x.transpose(1, 2)
        cnn_outputs = []
        for conv in self.cnn_convs:
            conv_out = F.relu(conv(x_cnn))
            pool_out = F.adaptive_max_pool1d(conv_out, 1).squeeze(-1)
            cnn_outputs.append(pool_out)
        cnn_features = torch.cat(cnn_outputs, dim=1)
        
        # RNN branch
        rnn_output, _ = self.rnn(x)
        rnn_features = rnn_output.mean(dim=1)
        
        # Transformer branch
        transformer_features = self.transformer_block(x)
        transformer_features = transformer_features.mean(dim=1)
        
        # Feature fusion
        combined_features = torch.cat([cnn_features, rnn_features, transformer_features], dim=1)
        fused_features = self.fusion(combined_features)
        
        # Classification
        logits = self.classifier(fused_features)
        
        return {"logits": logits}
```

**Key Features:**
- ✅ Multiple architectural branches
- ✅ Feature fusion mechanism
- ✅ Shared embedding layer
- ✅ Configurable component dimensions
- ✅ Comprehensive feature extraction

## 🎭 Custom Attention Mechanism

### **CustomAttentionMechanism**

```python
class CustomAttentionMechanism(nn.Module):
    """Custom attention mechanism for sequence modeling."""
    
    def __init__(self, d_model: int, num_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # Linear transformations
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)
        
        # Layer normalization
        self.norm = nn.LayerNorm(d_model)
    
    def scaled_dot_product_attention(self, Q: torch.Tensor, K: torch.Tensor, 
                                   V: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Scaled dot-product attention."""
        # Calculate attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        # Apply mask if provided
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        # Apply softmax
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        output = torch.matmul(attention_weights, V)
        
        return output
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch_size, seq_len, d_model = x.shape
        
        # Linear transformations
        Q = self.w_q(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        
        # Apply attention
        attention_output = self.scaled_dot_product_attention(Q, K, V, mask)
        
        # Reshape and apply output projection
        attention_output = attention_output.transpose(1, 2).contiguous().view(
            batch_size, seq_len, d_model
        )
        output = self.w_o(attention_output)
        
        # Residual connection and layer normalization
        output = self.norm(x + output)
        
        return output
```

**Key Features:**
- ✅ Multi-head attention implementation
- ✅ Scaled dot-product attention
- ✅ Support for attention masks
- ✅ Residual connections
- ✅ Layer normalization

## 🏭 Model Factory Pattern

### **CustomModelFactory**

```python
class CustomModelFactory:
    """Factory class for creating custom model architectures."""
    
    @staticmethod
    def create_model(model_type: str, config: UltraTrainingConfig, **kwargs) -> nn.Module:
        """Create a model based on the specified type."""
        if model_type == "transformer":
            return CustomTransformerModel(
                vocab_size=kwargs.get('vocab_size', 50000),
                d_model=kwargs.get('d_model', 512),
                n_layers=kwargs.get('n_layers', 6),
                n_heads=kwargs.get('n_heads', 8),
                d_ff=kwargs.get('d_ff', 2048),
                max_seq_len=config.max_length,
                dropout=kwargs.get('dropout', 0.1),
                num_labels=kwargs.get('num_labels', 2)
            )
        
        elif model_type == "cnn":
            return CustomCNNModel(
                vocab_size=kwargs.get('vocab_size', 50000),
                embed_dim=kwargs.get('embed_dim', 128),
                num_filters=kwargs.get('num_filters', 128),
                filter_sizes=kwargs.get('filter_sizes', [3, 4, 5]),
                num_labels=kwargs.get('num_labels', 2),
                dropout=kwargs.get('dropout', 0.5)
            )
        
        elif model_type == "rnn":
            return CustomRNNModel(
                vocab_size=kwargs.get('vocab_size', 50000),
                embed_dim=kwargs.get('embed_dim', 128),
                hidden_dim=kwargs.get('hidden_dim', 256),
                num_layers=kwargs.get('num_layers', 2),
                rnn_type=kwargs.get('rnn_type', 'lstm'),
                bidirectional=kwargs.get('bidirectional', True),
                num_labels=kwargs.get('num_labels', 2),
                dropout=kwargs.get('dropout', 0.5)
            )
        
        elif model_type == "hybrid":
            return CustomHybridModel(
                vocab_size=kwargs.get('vocab_size', 50000),
                embed_dim=kwargs.get('embed_dim', 128),
                hidden_dim=kwargs.get('hidden_dim', 256),
                num_filters=kwargs.get('num_filters', 128),
                filter_sizes=kwargs.get('filter_sizes', [3, 4, 5]),
                num_layers=kwargs.get('num_layers', 2),
                num_heads=kwargs.get('num_heads', 8),
                num_labels=kwargs.get('num_labels', 2),
                dropout=kwargs.get('dropout', 0.5)
            )
        
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
```

**Usage Example:**
```python
# Create different model types
transformer_model = CustomModelFactory.create_model("transformer", config)
cnn_model = CustomModelFactory.create_model("cnn", config)
rnn_model = CustomModelFactory.create_model("rnn", config)
hybrid_model = CustomModelFactory.create_model("hybrid", config)
```

## 📊 Best Practices for Custom nn.Module

### **1. Constructor Best Practices**
```python
def __init__(self, config):
    super().__init__()
    self.config = config
    
    # Use ModuleList for variable numbers of layers
    self.layers = nn.ModuleList([
        CustomLayer(config.d_model) for _ in range(config.num_layers)
    ])
    
    # Group related layers in Sequential
    self.classifier = nn.Sequential(
        nn.Linear(config.d_model, config.hidden_dim),
        nn.ReLU(),
        nn.Dropout(config.dropout),
        nn.Linear(config.hidden_dim, config.num_labels)
    )
    
    # Initialize weights
    self._init_weights()
```

### **2. Forward Method Best Practices**
```python
def forward(self, x, mask=None, labels=None):
    # Clear input validation
    if x.dim() != 2:
        raise ValueError(f"Expected 2D input, got {x.dim()}D")
    
    # Use proper tensor operations
    x = self.embedding(x)
    
    # Apply layers with proper error handling
    for layer in self.layers:
        x = layer(x, mask)
    
    # Return consistent output format
    output = {"logits": self.classifier(x)}
    
    if labels is not None:
        loss = F.cross_entropy(output["logits"], labels)
        output["loss"] = loss
    
    return output
```

### **3. Weight Initialization Best Practices**
```python
def _init_weights(self):
    """Initialize weights with proper initialization."""
    for module in self.modules():
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Conv1d):
            nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            nn.init.ones_(module.weight)
            nn.init.zeros_(module.bias)
```

### **4. Model Configuration Best Practices**
```python
@dataclass
class ModelConfig:
    """Configuration for custom models."""
    # Architecture parameters
    vocab_size: int = 50000
    d_model: int = 512
    n_layers: int = 6
    n_heads: int = 8
    d_ff: int = 2048
    
    # Training parameters
    dropout: float = 0.1
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    
    # Hardware parameters
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    use_mixed_precision: bool = True
```

## 🧪 Testing Custom Models

### **Model Testing Example**
```python
import pytest
import torch

def test_custom_transformer():
    """Test custom transformer model."""
    config = ModelConfig()
    model = CustomTransformerModel(
        vocab_size=1000,
        d_model=64,
        n_layers=2,
        n_heads=4,
        d_ff=128,
        max_seq_len=32,
        num_labels=2
    )
    
    # Test input
    input_ids = torch.randint(0, 1000, (2, 16))
    
    # Test forward pass
    with torch.no_grad():
        output = model(input_ids)
    
    assert "logits" in output
    assert output["logits"].shape == (2, 2)
    
    # Test with labels
    labels = torch.randint(0, 2, (2,))
    output_with_loss = model(input_ids, labels=labels)
    
    assert "loss" in output_with_loss
    assert output_with_loss["loss"].item() > 0

def test_model_gradients():
    """Test model gradient computation."""
    config = ModelConfig()
    model = CustomTransformerModel(
        vocab_size=1000,
        d_model=64,
        n_layers=2,
        n_heads=4,
        d_ff=128,
        max_seq_len=32,
        num_labels=2
    )
    
    input_ids = torch.randint(0, 1000, (2, 16))
    labels = torch.randint(0, 2, (2,))
    
    output = model(input_ids, labels=labels)
    loss = output["loss"]
    loss.backward()
    
    # Check gradients
    for name, param in model.named_parameters():
        if param.requires_grad:
            assert param.grad is not None, f"Gradient missing for {name}"
```

## 🚀 Performance Optimization

### **1. Memory Optimization**
```python
def optimize_memory_usage(self):
    """Optimize memory usage for the model."""
    # Use gradient checkpointing for large models
    if hasattr(self, 'transformer_blocks'):
        for block in self.transformer_blocks:
            block.gradient_checkpointing_enable()
    
    # Use mixed precision
    if self.config.use_mixed_precision:
        self = self.half()
    
    # Use channels last memory format
    if torch.cuda.is_available():
        self = self.to(memory_format=torch.channels_last)
```

### **2. Inference Optimization**
```python
def optimize_for_inference(self):
    """Optimize model for inference."""
    # Set to evaluation mode
    self.eval()
    
    # Use torch.compile if available
    if hasattr(torch, 'compile'):
        self = torch.compile(self, mode="reduce-overhead")
    
    # Use TorchScript if needed
    if self.config.use_torchscript:
        example_input = torch.randint(0, 1000, (1, 32))
        self = torch.jit.script(self)
    
    return self
```

## 📈 Model Monitoring and Debugging

### **1. Model Information**
```python
def get_model_info(self) -> Dict[str, Any]:
    """Get comprehensive model information."""
    total_params = sum(p.numel() for p in self.parameters())
    trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    return {
        'total_parameters': total_params,
        'trainable_parameters': trainable_params,
        'model_size_mb': sum(p.numel() * p.element_size() for p in self.parameters()) / 1024**2,
        'layers': len(list(self.modules())),
        'device': next(self.parameters()).device,
        'dtype': next(self.parameters()).dtype
    }
```

### **2. Gradient Monitoring**
```python
def monitor_gradients(self):
    """Monitor gradient statistics."""
    grad_norms = []
    for name, param in self.named_parameters():
        if param.grad is not None:
            grad_norm = param.grad.norm().item()
            grad_norms.append((name, grad_norm))
    
    return grad_norms
```

## 🎯 Implementation Checklist

- [ ] Inherit from `nn.Module`
- [ ] Implement `__init__` with proper layer initialization
- [ ] Implement `forward` method with clear flow
- [ ] Add proper weight initialization
- [ ] Include dropout and regularization
- [ ] Add residual connections where appropriate
- [ ] Implement proper error handling
- [ ] Add model validation and testing
- [ ] Include performance optimization features
- [ ] Add comprehensive documentation

## 🔗 Additional Resources

- [PyTorch nn.Module Documentation](https://pytorch.org/docs/stable/generated/torch.nn.Module.html)
- [PyTorch Custom Modules Tutorial](https://pytorch.org/tutorials/beginner/examples_autograd/two_layer_net_custom_function.html)
- [PyTorch Best Practices](https://pytorch.org/docs/stable/notes/faq.html)
- [PyTorch Model Optimization](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html)

This guide provides a comprehensive foundation for implementing custom `nn.Module` architectures with production-ready best practices and PyTorch optimizations.

