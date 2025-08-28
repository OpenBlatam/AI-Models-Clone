# Gradient Accumulation for Large Batch Sizes

## Overview

This module implements advanced gradient accumulation techniques to enable training with large effective batch sizes while maintaining memory efficiency. This is particularly useful for training large diffusion models and transformer architectures where memory constraints limit the maximum batch size.

## Features

### 🚀 Core Functionality
- **Gradient Accumulation**: Accumulate gradients over multiple forward/backward passes
- **Memory Efficiency**: Train with large effective batch sizes using minimal GPU memory
- **Mixed Precision Training**: Automatic mixed precision (AMP) support for faster training
- **Dynamic Batch Size Optimization**: Automatically adjust batch sizes based on available memory
- **Performance Monitoring**: Real-time memory usage and training metrics tracking

### 📊 Advanced Features
- **Multiple Accumulation Strategies**: Compare different gradient accumulation configurations
- **Memory Analysis**: Detailed memory efficiency analysis and optimization recommendations
- **Training Visualization**: Real-time plots of loss curves and memory usage
- **Gradio Interface**: Interactive web interface for experimentation

## Architecture

### GradientAccumulator Class
```python
class GradientAccumulator:
    """Handles gradient accumulation for large effective batch sizes."""
    
    def __init__(self, model: nn.Module, config: TrainingConfig):
        self.accumulation_steps = config.gradient_accumulation_steps
        self.effective_batch_size = config.effective_batch_size
        self.actual_batch_size = self.effective_batch_size // self.accumulation_steps
```

### AdvancedTrainer Class
```python
class AdvancedTrainer:
    """Advanced trainer with gradient accumulation and mixed precision."""
    
    def __init__(self, model: nn.Module, config: TrainingConfig):
        self.gradient_accumulator = GradientAccumulator(model, config)
        self.use_mixed_precision = config.use_mixed_precision
        self.scaler = GradScaler() if self.use_mixed_precision else None
```

## Usage Examples

### Basic Gradient Accumulation

```python
from advanced_training_system import TrainingConfig, AdvancedTrainer

# Configuration with gradient accumulation
config = TrainingConfig(
    batch_size=16,
    effective_batch_size=128,  # Target effective batch size
    gradient_accumulation_steps=8,  # Accumulate over 8 steps
    use_mixed_precision=True,
    learning_rate=1e-4
)

# Create trainer
trainer = AdvancedTrainer(model, config)

# Train with large effective batch size
results = trainer.train(dataloader, num_epochs=10)
```

### Diffusion Models with Gradient Accumulation

```python
from advanced_diffusion_system import DiffusionConfig, DiffusionTrainer

# Diffusion model configuration
config = DiffusionConfig(
    model_type="unet",
    image_size=64,
    batch_size=4,
    gradient_accumulation_steps=8,  # Effective batch size = 4 * 8 = 32
    effective_batch_size=32,
    learning_rate=1e-4
)

# Create diffusion trainer
trainer = DiffusionTrainer(model, config)

# Train diffusion model
results = trainer.train(dataloader, num_epochs=100)
```

### Memory Optimization

```python
# Get memory usage information
memory_info = trainer.get_memory_usage()
print(f"GPU Memory: {memory_info['gpu_memory_allocated']:.2f} GB")

# Optimize batch size based on available memory
optimal_batch_size = trainer.optimize_batch_size(target_memory_gb=8.0)
print(f"Optimal batch size: {optimal_batch_size}")
```

## Configuration Options

### TrainingConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `batch_size` | int | 32 | Actual batch size per forward pass |
| `effective_batch_size` | int | 128 | Target effective batch size |
| `gradient_accumulation_steps` | int | 4 | Number of steps to accumulate gradients |
| `use_mixed_precision` | bool | True | Enable automatic mixed precision |
| `fp16` | bool | True | Use FP16 precision |
| `bf16` | bool | False | Use BF16 precision |
| `learning_rate` | float | 1e-4 | Learning rate |
| `weight_decay` | float | 0.01 | Weight decay |
| `max_grad_norm` | float | 1.0 | Gradient clipping norm |

### DiffusionConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `batch_size` | int | 32 | Actual batch size |
| `gradient_accumulation_steps` | int | 1 | Gradient accumulation steps |
| `effective_batch_size` | int | 32 | Effective batch size |
| `learning_rate` | float | 1e-4 | Learning rate |
| `gradient_clip` | float | 1.0 | Gradient clipping value |

## Performance Benefits

### Memory Efficiency
- **Reduced Memory Usage**: Train with large effective batch sizes using minimal GPU memory
- **Memory Scaling**: Linear scaling of effective batch size with accumulation steps
- **Dynamic Optimization**: Automatic batch size adjustment based on available memory

### Training Stability
- **Consistent Gradients**: More stable gradients with larger effective batch sizes
- **Better Convergence**: Improved training stability and convergence
- **Reduced Variance**: Lower gradient variance with larger effective batch sizes

### Speed Improvements
- **Mixed Precision**: 2x speedup with automatic mixed precision training
- **Efficient Memory**: Better GPU utilization and reduced memory transfers
- **Optimized Scheduling**: Learning rate scheduling optimized for accumulation

## Demo Applications

### Interactive Gradio Demo
```bash
python run_gradient_accumulation_demo.py
```

The demo provides:
- **Configuration Selection**: Choose from different training configurations
- **Real-time Training**: Watch training progress with live metrics
- **Memory Analysis**: Compare memory efficiency across configurations
- **Visualization**: Interactive plots of training curves and memory usage

### Command Line Demo
```bash
python gradient_accumulation_demo.py
```

Features:
- **Batch Size Comparison**: Compare different batch size configurations
- **Memory Usage Analysis**: Detailed memory efficiency analysis
- **Performance Metrics**: Training time and loss comparison
- **Result Visualization**: Generate comparison plots

## Best Practices

### 1. Configuration Guidelines
```python
# For memory-constrained environments
config = TrainingConfig(
    batch_size=8,
    gradient_accumulation_steps=16,  # Effective batch size = 128
    effective_batch_size=128,
    use_mixed_precision=True
)

# For high-memory environments
config = TrainingConfig(
    batch_size=32,
    gradient_accumulation_steps=4,   # Effective batch size = 128
    effective_batch_size=128,
    use_mixed_precision=True
)
```

### 2. Learning Rate Scaling
```python
# Scale learning rate with effective batch size
base_lr = 1e-4
effective_batch_size = 128
scaled_lr = base_lr * (effective_batch_size / 32)  # Scale from batch size 32
```

### 3. Memory Management
```python
# Monitor memory usage
memory_info = trainer.get_memory_usage()
if memory_info['gpu_memory_allocated'] > 0.8:  # 80% of GPU memory
    # Reduce batch size or increase accumulation steps
    pass

# Optimize batch size dynamically
optimal_size = trainer.optimize_batch_size(target_memory_gb=8.0)
```

## Troubleshooting

### Common Issues

1. **Out of Memory (OOM)**
   ```python
   # Solution: Increase gradient accumulation steps
   config.gradient_accumulation_steps *= 2
   config.effective_batch_size = config.batch_size * config.gradient_accumulation_steps
   ```

2. **Slow Training**
   ```python
   # Solution: Enable mixed precision
   config.use_mixed_precision = True
   config.fp16 = True
   ```

3. **Unstable Training**
   ```python
   # Solution: Adjust learning rate and gradient clipping
   config.learning_rate *= 0.5
   config.max_grad_norm = 0.5
   ```

### Performance Tips

1. **Optimal Accumulation Steps**: Use 4-16 accumulation steps for best performance
2. **Memory Monitoring**: Regularly check memory usage and optimize batch sizes
3. **Mixed Precision**: Always enable mixed precision for faster training
4. **Gradient Clipping**: Use appropriate gradient clipping values (0.5-1.0)

## Dependencies

### Required Packages
```
torch>=2.0.0
torchvision>=0.15.0
gradio>=4.0.0
matplotlib>=3.6.0
numpy>=1.24.0
tqdm>=4.65.0
```

### Optional Packages
```
tensorboard>=2.13.0  # For advanced logging
wandb>=0.15.0       # For experiment tracking
```

## Examples

### Complete Training Pipeline
```python
from advanced_training_system import TrainingPipeline, TrainingConfig

# Create configuration
config = TrainingConfig(
    batch_size=16,
    effective_batch_size=128,
    gradient_accumulation_steps=8,
    use_mixed_precision=True,
    use_lora=True,
    use_compile=True
)

# Create pipeline
pipeline = TrainingPipeline(config)
pipeline.setup_components()

# Train
results = pipeline.train("path/to/data.txt", num_epochs=10)
```

### Diffusion Model Training
```python
from advanced_diffusion_system import DiffusionConfig, DiffusionTrainer

# Create diffusion configuration
config = DiffusionConfig(
    model_type="unet",
    image_size=64,
    batch_size=4,
    gradient_accumulation_steps=8,
    effective_batch_size=32,
    num_timesteps=1000,
    learning_rate=1e-4
)

# Create model and trainer
model = DiffusionModel(config)
trainer = DiffusionTrainer(model, config)

# Train
results = trainer.train(dataloader, num_epochs=100)
```

## Contributing

To contribute to the gradient accumulation functionality:

1. **Add New Features**: Implement additional optimization strategies
2. **Improve Documentation**: Add more examples and best practices
3. **Performance Optimization**: Optimize memory usage and training speed
4. **Testing**: Add comprehensive tests for different configurations

## License

This module is part of the advanced image processing system and follows the same license terms.

---

**Note**: This gradient accumulation system is designed to work seamlessly with the existing advanced training and diffusion model systems. For best results, ensure all dependencies are properly installed and GPU drivers are up to date.
