# PyTorch Primary Framework - Complete Guide

## 🚀 Overview

This guide demonstrates how to use **PyTorch as the primary deep learning framework** for all your machine learning and deep learning tasks. The framework provides a comprehensive, production-ready solution with advanced features, optimizations, and best practices.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Framework Architecture](#framework-architecture)
3. [Model Architectures](#model-architectures)
4. [Training Pipeline](#training-pipeline)
5. [Advanced Features](#advanced-features)
6. [Performance Optimization](#performance-optimization)
7. [Deployment](#deployment)
8. [Best Practices](#best-practices)
9. [Examples](#examples)
10. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Installation

```bash
# Install PyTorch primary framework
pip install -r requirements_pytorch_primary.txt

# Or install core dependencies only
pip install torch torchvision torchaudio
```

### Basic Usage

```python
from pytorch_primary_framework import PyTorchPrimaryFramework, PyTorchConfig

# Initialize framework
config = PyTorchConfig(
    device="auto",
    use_mixed_precision=True,
    use_compile=True
)
framework = PyTorchPrimaryFramework(config)

# Create sample data
data = torch.randn(1000, 784)
targets = torch.randint(0, 10, (1000,))

# Create dataloaders
train_loader, val_loader = framework.create_dataloaders(data, targets)

# Create and train model
model = framework.create_model("mlp", input_dim=784, hidden_dims=[512, 256], output_dim=10)
history = framework.train(model, train_loader, val_loader, num_epochs=10)

# Evaluate model
test_loader, _ = framework.create_dataloaders(data, targets)
metrics = framework.evaluate(model, test_loader)
print(f"Test Accuracy: {metrics['accuracy']:.2f}%")
```

## 🏗️ Framework Architecture

### Core Components

1. **PyTorchConfig**: Configuration management
2. **PyTorchDeviceManager**: Device and memory management
3. **AdvancedModelArchitectures**: Pre-built model architectures
4. **OptimizedTrainingEngine**: Training pipeline with optimizations
5. **PyTorchPrimaryFramework**: Main interface

### Configuration Options

```python
@dataclass
class PyTorchConfig:
    # Device configuration
    device: str = "auto"  # "auto", "cuda", "cpu", "mps"
    use_mixed_precision: bool = True
    use_compile: bool = True
    deterministic: bool = False
    benchmark: bool = True
    
    # Memory management
    memory_fraction: float = 0.9
    gradient_clip_norm: float = 1.0
    pin_memory: bool = True
    num_workers: int = 4
    
    # Training configuration
    default_batch_size: int = 32
    default_learning_rate: float = 1e-3
    default_weight_decay: float = 1e-4
```

## 🧠 Model Architectures

### Multi-Layer Perceptron (MLP)

```python
# Create advanced MLP
model = framework.create_model(
    "mlp",
    input_dim=784,
    hidden_dims=[512, 256, 128],
    output_dim=10,
    dropout_rate=0.2,
    activation="relu",
    batch_norm=True
)
```

### Convolutional Neural Network (CNN)

```python
# Create CNN with ResNet-like architecture
model = framework.create_model(
    "cnn",
    input_channels=3,
    num_classes=10,
    architecture="resnet_like"  # or "simple"
)
```

### Transformer

```python
# Create Transformer model
model = framework.create_model(
    "transformer",
    vocab_size=1000,
    d_model=512,
    nhead=8,
    num_layers=6,
    num_classes=10,
    max_seq_length=512
)
```

### Custom Model

```python
import torch.nn as nn

class CustomModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x):
        return self.layers(x)

# Use custom model with framework
model = CustomModel(784, 256, 10)
model = model.to(framework.device_manager.device)
```

## 🎯 Training Pipeline

### Basic Training

```python
# Create data
data = torch.randn(1000, 784)
targets = torch.randint(0, 10, (1000,))
train_loader, val_loader = framework.create_dataloaders(data, targets)

# Create model
model = framework.create_model("mlp", input_dim=784, hidden_dims=[512, 256], output_dim=10)

# Train model
history = framework.train(
    model, train_loader, val_loader,
    num_epochs=10,
    learning_rate=1e-3,
    save_best=True
)
```

### Advanced Training with Custom Configuration

```python
# Custom training configuration
config = PyTorchConfig(
    device="cuda",
    use_mixed_precision=True,
    use_compile=True,
    gradient_clip_norm=1.0,
    default_batch_size=64
)

framework = PyTorchPrimaryFramework(config)

# Training with custom parameters
history = framework.train(
    model, train_loader, val_loader,
    num_epochs=20,
    learning_rate=5e-4,
    save_best=True
)
```

### Training with Callbacks

```python
class TrainingCallback:
    def on_epoch_end(self, epoch, metrics):
        print(f"Epoch {epoch}: Loss={metrics['loss']:.4f}, Acc={metrics['accuracy']:.2f}%")
    
    def on_training_end(self, history):
        print("Training completed!")

# Custom training loop
callback = TrainingCallback()
history = framework.train_with_callbacks(
    model, train_loader, val_loader,
    num_epochs=10,
    callbacks=[callback]
)
```

## ⚡ Advanced Features

### Mixed Precision Training

```python
# Automatic mixed precision (enabled by default)
config = PyTorchConfig(use_mixed_precision=True)
framework = PyTorchPrimaryFramework(config)

# Manual mixed precision
scaler = torch.cuda.amp.GradScaler()
with torch.cuda.amp.autocast():
    output = model(data)
    loss = criterion(output, target)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

### Model Compilation

```python
# Automatic model compilation (enabled by default)
config = PyTorchConfig(use_compile=True)
framework = PyTorchPrimaryFramework(config)

# Manual compilation
model = torch.compile(model, mode="max-autotune")
```

### Distributed Training

```python
# Multi-GPU training
config = PyTorchConfig(use_distributed=True)
framework = PyTorchPrimaryFramework(config)

# Model will be automatically wrapped with DistributedDataParallel
model = framework.create_model("mlp", input_dim=784, hidden_dims=[512], output_dim=10)
```

### Gradient Checkpointing

```python
# Enable gradient checkpointing for memory efficiency
config = PyTorchConfig(use_gradient_checkpointing=True)
framework = PyTorchPrimaryFramework(config)
```

## 🚀 Performance Optimization

### Memory Management

```python
# Monitor memory usage
memory_info = framework.device_manager.get_memory_info()
print(f"GPU Memory: {memory_info['allocated']:.2f} GB")

# Clear memory
framework.device_manager.clear_memory()
```

### Data Loading Optimization

```python
# Optimized dataloader configuration
config = PyTorchConfig(
    pin_memory=True,
    num_workers=4,
    default_batch_size=64
)

# Use prefetch_factor for faster data loading
train_loader = DataLoader(
    dataset,
    batch_size=64,
    pin_memory=True,
    num_workers=4,
    prefetch_factor=2
)
```

### Model Optimization

```python
# Optimize model for inference
model.eval()
with torch.no_grad():
    # Use torch.jit for model optimization
    traced_model = torch.jit.trace(model, example_input)
    traced_model.save("optimized_model.pt")
```

## 🚀 Deployment

### Model Saving and Loading

```python
# Save model
framework.save_model(model, "my_model.pth")

# Load model
loaded_model = framework.load_model(model, "my_model.pth")
```

### ONNX Export

```python
# Export to ONNX
import torch.onnx

dummy_input = torch.randn(1, 784)
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    export_params=True,
    opset_version=11,
    do_constant_folding=True,
    input_names=['input'],
    output_names=['output']
)
```

### TorchServe Deployment

```python
# Create TorchServe model archive
import torch
from torch.utils.model_zoo import _download_url_to_file

# Save model
torch.save(model.state_dict(), "model.pth")

# Create model archive
# torch-model-archiver --model-name mymodel --version 1.0 --model-file model.pth --handler image_classifier
```

### FastAPI Deployment

```python
from fastapi import FastAPI
import torch

app = FastAPI()

@app.post("/predict")
async def predict(data: List[float]):
    # Load model
    model = framework.load_model(model, "best_model.pth")
    model.eval()
    
    # Make prediction
    input_tensor = torch.tensor(data).unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)
        prediction = torch.argmax(output, dim=1).item()
    
    return {"prediction": prediction}
```

## 📊 Best Practices

### 1. Configuration Management

```python
# Use configuration files
import yaml

with open("config.yaml", "r") as f:
    config_dict = yaml.safe_load(f)

config = PyTorchConfig(**config_dict)
```

### 2. Experiment Tracking

```python
# Use TensorBoard
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter("runs/experiment_1")
writer.add_scalar("Loss/Train", loss, epoch)
writer.add_scalar("Accuracy/Validation", accuracy, epoch)
```

### 3. Model Checkpointing

```python
# Save checkpoints
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
    'config': config
}
torch.save(checkpoint, f"checkpoint_epoch_{epoch}.pth")
```

### 4. Error Handling

```python
try:
    history = framework.train(model, train_loader, val_loader, num_epochs=10)
except RuntimeError as e:
    if "out of memory" in str(e):
        print("GPU out of memory. Try reducing batch size.")
        framework.device_manager.clear_memory()
    else:
        raise e
```

### 5. Reproducibility

```python
# Set random seeds
import torch
import numpy as np
import random

def set_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True

set_seed(42)
```

## 📝 Examples

### Image Classification

```python
# Load image data
from torchvision import datasets, transforms

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

dataset = datasets.ImageFolder("path/to/images", transform=transform)
train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

# Create CNN model
model = framework.create_model("cnn", input_channels=3, num_classes=1000)

# Train
history = framework.train(model, train_loader, val_loader, num_epochs=10)
```

### Text Classification

```python
# Create transformer for text classification
model = framework.create_model(
    "transformer",
    vocab_size=10000,
    d_model=256,
    nhead=8,
    num_layers=4,
    num_classes=5
)

# Prepare text data
text_data = torch.randint(0, 10000, (1000, 100))  # (batch, seq_len)
labels = torch.randint(0, 5, (1000,))

train_loader, val_loader = framework.create_dataloaders(text_data, labels)
history = framework.train(model, train_loader, val_loader, num_epochs=10)
```

### Transfer Learning

```python
# Load pre-trained model
from torchvision import models

pretrained_model = models.resnet18(pretrained=True)
# Freeze early layers
for param in pretrained_model.parameters():
    param.requires_grad = False

# Modify final layer
pretrained_model.fc = nn.Linear(512, num_classes)

# Train only the final layer
optimizer = optim.Adam(pretrained_model.fc.parameters(), lr=1e-3)
```

## 🔧 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   ```python
   # Reduce batch size
   config = PyTorchConfig(default_batch_size=16)
   
   # Enable gradient checkpointing
   config.use_gradient_checkpointing = True
   
   # Clear memory
   framework.device_manager.clear_memory()
   ```

2. **Model Compilation Errors**
   ```python
   # Disable compilation
   config = PyTorchConfig(use_compile=False)
   ```

3. **Slow Training**
   ```python
   # Enable mixed precision
   config.use_mixed_precision = True
   
   # Increase num_workers
   config.num_workers = 8
   
   # Enable pin_memory
   config.pin_memory = True
   ```

4. **Reproducibility Issues**
   ```python
   # Enable deterministic mode
   config.deterministic = True
   config.benchmark = False
   ```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use deterministic mode for debugging
config = PyTorchConfig(deterministic=True)
```

## 📚 Additional Resources

- [PyTorch Documentation](https://pytorch.org/docs/)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [PyTorch Lightning](https://lightning.ai/)
- [Hugging Face Transformers](https://huggingface.co/transformers/)

## 🎯 Summary

This PyTorch Primary Framework provides:

- ✅ **Complete Integration**: All PyTorch components unified
- ✅ **Advanced Architectures**: MLP, CNN, Transformer models
- ✅ **Performance Optimization**: Mixed precision, compilation, memory management
- ✅ **Production Ready**: Deployment, monitoring, error handling
- ✅ **Best Practices**: Configuration management, experiment tracking
- ✅ **Comprehensive Documentation**: Examples, troubleshooting, best practices

**PyTorch is now your primary deep learning framework** with all the tools and optimizations needed for efficient development and deployment. 