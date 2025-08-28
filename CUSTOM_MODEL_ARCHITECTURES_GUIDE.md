# Custom Neural Network Model Architectures - Complete Guide

## 🎯 Overview

This guide provides comprehensive documentation for custom `nn.Module` implementations of advanced neural network architectures. These architectures are designed to be production-ready, highly configurable, and optimized for various deep learning tasks.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [CNN Architectures](#cnn-architectures)
3. [Transformer Architectures](#transformer-architectures)
4. [RNN/LSTM Architectures](#rnnlstm-architectures)
5. [Specialized Architectures](#specialized-architectures)
6. [Model Factory](#model-factory)
7. [Usage Examples](#usage-examples)
8. [Performance Optimization](#performance-optimization)
9. [Best Practices](#best-practices)
10. [Testing and Validation](#testing-and-validation)

## 🏗️ Architecture Overview

### Available Architectures

| Architecture | Type | Use Case | Key Features |
|--------------|------|----------|--------------|
| **AdvancedResNet** | CNN | Image Classification | Attention, Bottleneck, Residual connections |
| **AdvancedDenseNet** | CNN | Image Classification | Dense connectivity, Transition blocks |
| **AdvancedTransformer** | Transformer | Sequence Processing | Multi-head attention, Positional encoding |
| **BidirectionalLSTM** | RNN | Sequence Classification | Bidirectional, Attention mechanism |
| **SiameseNetwork** | Specialized | Similarity Learning | Twin networks, Distance learning |
| **Autoencoder** | Specialized | Unsupervised Learning | Encoder-decoder, Latent representation |
| **GAN** | Specialized | Generative Modeling | Generator-Discriminator pair |

### Common Features

- ✅ **Modular Design**: Easy to customize and extend
- ✅ **Production Ready**: Proper initialization, error handling
- ✅ **Performance Optimized**: Efficient implementations
- ✅ **Type Hints**: Full type annotation support
- ✅ **Documentation**: Comprehensive docstrings
- ✅ **Testing**: Complete test coverage

## 🖼️ CNN Architectures

### AdvancedResNet

Advanced ResNet with attention mechanisms and bottleneck blocks.

```python
from custom_model_architectures import AdvancedResNet

# Basic usage
model = AdvancedResNet(
    num_classes=1000,
    bottleneck=True,
    attention=True,
    dropout_rate=0.1
)

# Custom configuration
model = AdvancedResNet(
    num_classes=10,
    block_config=[2, 2, 2, 2],  # ResNet-18 like
    channels=[64, 128, 256, 512],
    bottleneck=False,
    attention=False,
    dropout_rate=0.2
)
```

**Key Features:**
- **Residual Blocks**: Skip connections for better gradient flow
- **Bottleneck Design**: 1x1, 3x3, 1x1 convolutions for efficiency
- **Attention Mechanism**: Self-attention for feature refinement
- **Batch Normalization**: Improved training stability
- **Dropout**: Regularization for better generalization

**Configuration Options:**
- `num_classes`: Number of output classes
- `block_config`: Number of blocks in each layer
- `channels`: Number of channels in each layer
- `bottleneck`: Use bottleneck design
- `attention`: Enable attention mechanism
- `dropout_rate`: Dropout probability

### AdvancedDenseNet

DenseNet with improved connectivity and transition blocks.

```python
from custom_model_architectures import AdvancedDenseNet

# Basic usage
model = AdvancedDenseNet(
    num_classes=1000,
    growth_rate=32,
    dropout_rate=0.2
)

# Custom configuration
model = AdvancedDenseNet(
    num_classes=10,
    growth_rate=48,
    block_config=[6, 12, 24, 16],
    compression=0.5,
    dropout_rate=0.1
)
```

**Key Features:**
- **Dense Connectivity**: Each layer connects to all previous layers
- **Growth Rate**: Number of new features per layer
- **Transition Blocks**: Reduce feature maps between dense blocks
- **Compression**: Reduce model size with compression factor
- **Batch Normalization**: Improved training stability

**Configuration Options:**
- `num_classes`: Number of output classes
- `growth_rate`: Number of new features per layer
- `block_config`: Number of layers in each dense block
- `compression`: Compression factor for transition blocks
- `dropout_rate`: Dropout probability

## 🔤 Transformer Architectures

### AdvancedTransformer

Advanced Transformer with multi-head attention and positional encoding.

```python
from custom_model_architectures import AdvancedTransformer

# Basic usage
model = AdvancedTransformer(
    vocab_size=10000,
    d_model=512,
    num_classes=10
)

# Custom configuration
model = AdvancedTransformer(
    vocab_size=50000,
    d_model=768,
    num_heads=12,
    num_layers=12,
    d_ff=3072,
    max_seq_length=512,
    num_classes=1000,
    dropout=0.1
)
```

**Key Features:**
- **Multi-Head Attention**: Parallel attention mechanisms
- **Positional Encoding**: Learnable position embeddings
- **Layer Normalization**: Improved training stability
- **Feed-Forward Networks**: Position-wise transformations
- **Residual Connections**: Skip connections for gradient flow

**Configuration Options:**
- `vocab_size`: Size of vocabulary
- `d_model`: Model dimension
- `num_heads`: Number of attention heads
- `num_layers`: Number of transformer layers
- `d_ff`: Feed-forward network dimension
- `max_seq_length`: Maximum sequence length
- `num_classes`: Number of output classes
- `dropout`: Dropout probability

## 🔄 RNN/LSTM Architectures

### BidirectionalLSTM

Bidirectional LSTM with attention mechanism.

```python
from custom_model_architectures import BidirectionalLSTM

# Basic usage
model = BidirectionalLSTM(
    input_size=100,
    hidden_size=128,
    num_classes=10
)

# Custom configuration
model = BidirectionalLSTM(
    input_size=256,
    hidden_size=512,
    num_layers=3,
    num_classes=100,
    dropout=0.2,
    attention=True
)
```

**Key Features:**
- **Bidirectional Processing**: Forward and backward sequence processing
- **Attention Mechanism**: Learnable attention weights
- **Multi-Layer Support**: Stacked LSTM layers
- **Dropout**: Regularization between layers
- **Global Average Pooling**: Sequence-level representation

**Configuration Options:**
- `input_size`: Input feature dimension
- `hidden_size`: Hidden state dimension
- `num_layers`: Number of LSTM layers
- `num_classes`: Number of output classes
- `dropout`: Dropout probability
- `attention`: Enable attention mechanism

## 🎯 Specialized Architectures

### SiameseNetwork

Siamese network for similarity learning and metric learning.

```python
from custom_model_architectures import SiameseNetwork

# Basic usage
model = SiameseNetwork(
    input_size=784,
    embedding_size=64
)

# Custom configuration
model = SiameseNetwork(
    input_size=1024,
    hidden_dims=[512, 256, 128],
    embedding_size=128,
    dropout_rate=0.2
)
```

**Key Features:**
- **Twin Networks**: Shared encoder for both inputs
- **Embedding Space**: Learnable similarity metric
- **Distance Learning**: Contrastive learning support
- **Batch Normalization**: Improved training stability
- **Configurable Architecture**: Flexible hidden dimensions

**Usage Example:**
```python
# Training with contrastive loss
input1 = torch.randn(batch_size, input_size)
input2 = torch.randn(batch_size, input_size)
similarity = model(input1, input2)  # Output: [0, 1] similarity score

# Inference
embedding1 = model.forward_one(input1)  # Get embeddings
embedding2 = model.forward_one(input2)
```

### Autoencoder

Autoencoder for unsupervised learning and dimensionality reduction.

```python
from custom_model_architectures import Autoencoder

# Basic usage
model = Autoencoder(
    input_size=784,
    latent_dim=64
)

# Custom configuration
model = Autoencoder(
    input_size=1024,
    hidden_dims=[512, 256, 128],
    latent_dim=128,
    dropout_rate=0.2
)
```

**Key Features:**
- **Encoder-Decoder**: Symmetric architecture
- **Latent Representation**: Compressed feature space
- **Reconstruction Loss**: Unsupervised learning objective
- **Batch Normalization**: Improved training stability
- **Configurable Architecture**: Flexible hidden dimensions

**Usage Example:**
```python
# Training
reconstructed = model(input_data)
loss = reconstruction_loss(input_data, reconstructed)

# Feature extraction
latent_features = model.encode(input_data)
reconstructed_data = model.decode(latent_features)
```

### GAN (Generative Adversarial Network)

GAN with generator and discriminator components.

```python
from custom_model_architectures import GANGenerator, GANDiscriminator

# Generator
generator = GANGenerator(
    latent_dim=100,
    output_size=784
)

# Discriminator
discriminator = GANDiscriminator(
    input_size=784
)
```

**Key Features:**
- **Generator**: Creates fake samples from noise
- **Discriminator**: Distinguishes real from fake samples
- **Adversarial Training**: Min-max optimization
- **Configurable Architecture**: Flexible dimensions
- **Batch Normalization**: Improved training stability

**Usage Example:**
```python
# Training loop
for epoch in range(num_epochs):
    # Train discriminator
    real_samples = get_real_data()
    noise = torch.randn(batch_size, latent_dim)
    fake_samples = generator(noise)
    
    real_output = discriminator(real_samples)
    fake_output = discriminator(fake_samples.detach())
    
    d_loss = discriminator_loss(real_output, fake_output)
    
    # Train generator
    fake_output = discriminator(fake_samples)
    g_loss = generator_loss(fake_output)
```

## 🏭 Model Factory

The ModelFactory provides a unified interface for creating all custom architectures.

```python
from custom_model_architectures import ModelFactory

# Get available models
available_models = ModelFactory.get_available_models()
print(available_models)
# Output: ['advanced_resnet', 'advanced_densenet', 'advanced_transformer', ...]

# Create models
resnet = ModelFactory.create_model("advanced_resnet", num_classes=10)
transformer = ModelFactory.create_model("advanced_transformer", vocab_size=1000, num_classes=10)
siamese = ModelFactory.create_model("siamese", input_size=784)
```

**Available Model Types:**
- `advanced_resnet`: Advanced ResNet with attention
- `advanced_densenet`: Advanced DenseNet
- `advanced_transformer`: Advanced Transformer
- `bidirectional_lstm`: Bidirectional LSTM
- `siamese`: Siamese Network
- `autoencoder`: Autoencoder
- `gan_generator`: GAN Generator
- `gan_discriminator`: GAN Discriminator

## 📝 Usage Examples

### Image Classification

```python
import torch
from custom_model_architectures import AdvancedResNet

# Create model
model = AdvancedResNet(
    num_classes=10,
    bottleneck=True,
    attention=True
)

# Prepare data
batch_size = 32
input_data = torch.randn(batch_size, 3, 224, 224)
targets = torch.randint(0, 10, (batch_size,))

# Training
model.train()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = torch.nn.CrossEntropyLoss()

output = model(input_data)
loss = criterion(output, targets)
loss.backward()
optimizer.step()
```

### Sequence Classification

```python
import torch
from custom_model_architectures import AdvancedTransformer

# Create model
model = AdvancedTransformer(
    vocab_size=10000,
    d_model=512,
    num_classes=5
)

# Prepare data
batch_size = 16
seq_length = 100
input_data = torch.randint(0, 10000, (batch_size, seq_length))
targets = torch.randint(0, 5, (batch_size,))

# Training
model.train()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
criterion = torch.nn.CrossEntropyLoss()

output = model(input_data)
loss = criterion(output, targets)
loss.backward()
optimizer.step()
```

### Similarity Learning

```python
import torch
from custom_model_architectures import SiameseNetwork

# Create model
model = SiameseNetwork(
    input_size=784,
    embedding_size=64
)

# Prepare data
batch_size = 32
input1 = torch.randn(batch_size, 784)
input2 = torch.randn(batch_size, 784)
labels = torch.randint(0, 2, (batch_size,))  # 0: different, 1: similar

# Training
model.train()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = torch.nn.BCELoss()

similarity = model(input1, input2)
loss = criterion(similarity.squeeze(), labels.float())
loss.backward()
optimizer.step()
```

### Unsupervised Learning

```python
import torch
from custom_model_architectures import Autoencoder

# Create model
model = Autoencoder(
    input_size=784,
    latent_dim=64
)

# Prepare data
batch_size = 32
input_data = torch.randn(batch_size, 784)

# Training
model.train()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = torch.nn.MSELoss()

reconstructed = model(input_data)
loss = criterion(reconstructed, input_data)
loss.backward()
optimizer.step()
```

## ⚡ Performance Optimization

### Memory Optimization

```python
# Use gradient checkpointing for large models
model = AdvancedTransformer(
    vocab_size=50000,
    d_model=1024,
    num_layers=24
)

# Enable gradient checkpointing
model.gradient_checkpointing_enable()

# Use mixed precision training
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

with autocast():
    output = model(input_data)
    loss = criterion(output, targets)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

### Speed Optimization

```python
# Use model compilation (PyTorch 2.0+)
model = torch.compile(model, mode="max-autotune")

# Use appropriate batch sizes
batch_size = 32  # Adjust based on GPU memory

# Use multiple workers for data loading
dataloader = DataLoader(
    dataset,
    batch_size=batch_size,
    num_workers=4,
    pin_memory=True
)
```

### Model Quantization

```python
# Dynamic quantization for inference
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)

# Static quantization for better performance
model.eval()
model_fused = torch.quantization.fuse_modules(model, [['conv', 'bn', 'relu']])
model_prepared = torch.quantization.prepare(model_fused)
# ... calibration ...
model_quantized = torch.quantization.convert(model_prepared)
```

## 📊 Best Practices

### 1. Model Initialization

```python
# Use proper weight initialization
def init_weights(model):
    for module in model.modules():
        if isinstance(module, torch.nn.Conv2d):
            torch.nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
        elif isinstance(module, torch.nn.BatchNorm2d):
            torch.nn.init.constant_(module.weight, 1)
            torch.nn.init.constant_(module.bias, 0)
        elif isinstance(module, torch.nn.Linear):
            torch.nn.init.normal_(module.weight, 0, 0.01)
            torch.nn.init.constant_(module.bias, 0)

model = AdvancedResNet(num_classes=10)
init_weights(model)
```

### 2. Learning Rate Scheduling

```python
# Use appropriate learning rate schedulers
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

# Cosine annealing scheduler
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

# ReduceLROnPlateau for classification
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.5, patience=5
)
```

### 3. Regularization

```python
# Use appropriate dropout rates
model = AdvancedResNet(
    num_classes=10,
    dropout_rate=0.2  # Adjust based on dataset size
)

# Use weight decay
optimizer = torch.optim.Adam(
    model.parameters(),
    lr=1e-3,
    weight_decay=1e-4
)

# Use early stopping
early_stopping = EarlyStopping(patience=10, min_delta=1e-4)
```

### 4. Data Augmentation

```python
# For image classification
transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# For sequence data
def augment_sequence(sequence):
    # Add noise, masking, etc.
    return sequence
```

## 🧪 Testing and Validation

### Unit Testing

```python
import unittest
import torch
from custom_model_architectures import AdvancedResNet

class TestAdvancedResNet(unittest.TestCase):
    def setUp(self):
        self.model = AdvancedResNet(num_classes=10)
        self.input_data = torch.randn(2, 3, 224, 224)
    
    def test_forward_pass(self):
        output = self.model(self.input_data)
        self.assertEqual(output.shape, (2, 10))
    
    def test_parameter_count(self):
        param_count = sum(p.numel() for p in self.model.parameters())
        self.assertGreater(param_count, 0)

if __name__ == '__main__':
    unittest.main()
```

### Performance Testing

```python
import time
from custom_model_architectures import ModelFactory

def benchmark_model(model_type, config, input_data, num_runs=100):
    model = ModelFactory.create_model(model_type, **config)
    model.eval()
    
    # Warmup
    with torch.no_grad():
        for _ in range(10):
            _ = model(input_data)
    
    # Benchmark
    start_time = time.time()
    with torch.no_grad():
        for _ in range(num_runs):
            _ = model(input_data)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / num_runs
    return avg_time

# Test different architectures
configs = {
    "advanced_resnet": {"num_classes": 10},
    "advanced_transformer": {"vocab_size": 1000, "num_classes": 10}
}

for model_type, config in configs.items():
    if model_type == "advanced_resnet":
        input_data = torch.randn(1, 3, 224, 224)
    else:
        input_data = torch.randint(0, 1000, (1, 50))
    
    avg_time = benchmark_model(model_type, config, input_data)
    print(f"{model_type}: {avg_time*1000:.2f} ms")
```

### Memory Testing

```python
import psutil
import os

def test_memory_usage(model, input_data):
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    model(input_data)
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    return memory_increase

# Test memory usage for different models
models = [
    ("AdvancedResNet", AdvancedResNet(num_classes=10)),
    ("AdvancedDenseNet", AdvancedDenseNet(num_classes=10)),
    ("AdvancedTransformer", AdvancedTransformer(vocab_size=1000, num_classes=10))
]

for name, model in models:
    if "ResNet" in name or "DenseNet" in name:
        input_data = torch.randn(1, 3, 224, 224)
    else:
        input_data = torch.randint(0, 1000, (1, 50))
    
    memory_increase = test_memory_usage(model, input_data)
    print(f"{name}: {memory_increase:.2f} MB")
```

## 🎯 Summary

This custom model architectures implementation provides:

✅ **Advanced CNN Architectures**: ResNet and DenseNet with attention
✅ **Transformer Models**: Multi-head attention for sequences
✅ **RNN/LSTM Variants**: Bidirectional with attention
✅ **Specialized Models**: Siamese, Autoencoder, GAN
✅ **Model Factory**: Unified creation interface
✅ **Performance Optimized**: Efficient implementations
✅ **Production Ready**: Proper initialization and error handling
✅ **Comprehensive Testing**: Full validation suite
✅ **Extensive Documentation**: Complete usage guides

These architectures are designed to be **production-ready** and **highly configurable** for various deep learning tasks, providing state-of-the-art performance with modern PyTorch best practices. 