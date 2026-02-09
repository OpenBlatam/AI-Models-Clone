# Multi-GPU Training System for Diffusion Models

## Overview

This system provides comprehensive multi-GPU training capabilities for diffusion models, supporting multiple parallelization strategies including DataParallel, DistributedDataParallel, Horovod, and DeepSpeed. It's designed to maximize training efficiency and scalability across multiple GPU devices.

## 🚀 Key Features

### Multi-GPU Training Modes
- **DataParallel**: Simple multi-GPU training with automatic data distribution
- **DistributedDataParallel**: Advanced distributed training with process groups
- **Horovod**: High-performance distributed training framework
- **DeepSpeed**: Microsoft's deep learning optimization library

### Performance Optimizations
- **Memory Management**: Gradient checkpointing, attention slicing, model offloading
- **Training Acceleration**: Mixed precision, XFormers attention, model compilation
- **CUDA Optimizations**: CUDNN benchmark, TF32, channels last memory format
- **Batch Size Scaling**: Automatic batch size optimization for multi-GPU setups

### Monitoring & Analytics
- **Performance Metrics**: Training time, memory usage, GPU utilization
- **Real-time Monitoring**: Live performance tracking during training
- **Memory Profiling**: Detailed memory usage analysis
- **Performance Reports**: Comprehensive optimization summaries

## 🏗️ Architecture

### Core Components

#### 1. MultiGPUConfig
Configuration class for multi-GPU training settings:
```python
@dataclass
class MultiGPUConfig:
    mode: MultiGPUMode = MultiGPUMode.NONE
    num_gpus: int = 1
    distributed_backend: str = "nccl"  # nccl for GPU, gloo for CPU
    distributed_init_method: str = "env://"
    distributed_world_size: int = 1
    distributed_rank: int = 0
    # ... additional configuration options
```

#### 2. DiffusionPerformanceOptimizer
Main optimization class with multi-GPU support:
```python
class DiffusionPerformanceOptimizer:
    def setup_multi_gpu_training(self, model, dataloader, rank=None, world_size=None):
        """Setup multi-GPU training with specified mode."""
        
    def get_multi_gpu_info(self):
        """Get information about multi-GPU setup."""
```

#### 3. Multi-GPU Training Methods
- `_setup_dataparallel_training()`: DataParallel configuration
- `_setup_distributed_training()`: DistributedDataParallel setup
- `_setup_horovod_training()`: Horovod integration
- `_setup_deepspeed_training()`: DeepSpeed configuration

## 📱 DataParallel Training

### Overview
DataParallel is the simplest form of multi-GPU training, automatically distributing data across available GPUs.

### Advantages
- **Easy Setup**: Minimal code changes required
- **Automatic Distribution**: Handles data splitting automatically
- **Backward Compatibility**: Works with existing single-GPU code

### Limitations
- **Single Process**: All GPUs share the same process
- **GIL Bottleneck**: Python Global Interpreter Lock can limit performance
- **Memory Replication**: Model parameters are replicated on each GPU

### Usage Example
```python
from core.diffusion_performance_optimizer import DiffusionPerformanceOptimizer, MultiGPUMode, MultiGPUConfig

# Configure DataParallel
config = PerformanceConfig(
    enable_multi_gpu=True,
    multi_gpu_config=MultiGPUConfig(
        mode=MultiGPUMode.DATAPARALLEL,
        num_gpus=torch.cuda.device_count()
    )
)

# Create optimizer
optimizer = DiffusionPerformanceOptimizer(config)

# Setup multi-GPU training
model, dataloader = optimizer.setup_multi_gpu_training(model, dataloader)

# Train normally - DataParallel handles the rest
for batch in dataloader:
    outputs = model(batch)
    loss = criterion(outputs, targets)
    loss.backward()
    optimizer.step()
```

## 🌐 DistributedDataParallel Training

### Overview
DistributedDataParallel (DDP) provides more efficient multi-GPU training using multiple processes and optimized communication.

### Advantages
- **Multi-Process**: Each GPU runs in its own process
- **Efficient Communication**: NCCL backend for optimal GPU communication
- **Memory Efficiency**: Better memory management than DataParallel
- **Scalability**: Can scale across multiple machines

### Setup Process
1. **Initialize Process Group**: Set up distributed environment
2. **Model Distribution**: Move model to appropriate GPU
3. **DDP Wrapper**: Wrap model with DistributedDataParallel
4. **Sampler Setup**: Configure distributed data sampling

### Usage Example
```python
# Configure DistributedDataParallel
config = PerformanceConfig(
    enable_multi_gpu=True,
    multi_gpu_config=MultiGPUConfig(
        mode=MultiGPUMode.DISTRIBUTED,
        distributed_backend="nccl",
        distributed_world_size=torch.cuda.device_count()
    )
)

# Create optimizer
optimizer = DiffusionPerformanceOptimizer(config)

# Setup distributed training
model, dataloader = optimizer.setup_multi_gpu_training(
    model, dataloader, rank=0, world_size=torch.cuda.device_count()
)

# Training loop remains the same
for batch in dataloader:
    outputs = model(batch)
    loss = criterion(outputs, targets)
    loss.backward()
    optimizer.step()
```

## 🐎 Horovod Training

### Overview
Horovod is a distributed training framework that provides efficient all-reduce operations and excellent scalability.

### Features
- **Ring All-Reduce**: Efficient gradient synchronization
- **MPI Integration**: Works with existing MPI infrastructure
- **Framework Agnostic**: Supports multiple deep learning frameworks
- **High Performance**: Optimized for large-scale training

### Usage Example
```python
# Configure Horovod
config = PerformanceConfig(
    enable_multi_gpu=True,
    multi_gpu_config=MultiGPUConfig(
        mode=MultiGPUMode.HOROVOD
    )
)

# Create optimizer
optimizer = DiffusionPerformanceOptimizer(config)

# Setup Horovod training
model, dataloader = optimizer.setup_multi_gpu_training(model, dataloader)

# Horovod automatically handles gradient synchronization
for batch in dataloader:
    outputs = model(batch)
    loss = criterion(outputs, targets)
    loss.backward()
    optimizer.step()
```

## 🚀 DeepSpeed Training

### Overview
DeepSpeed provides advanced optimization techniques including ZeRO (Zero Redundancy Optimizer) for memory efficiency.

### Features
- **ZeRO Optimization**: Eliminates memory redundancy across GPUs
- **Mixed Precision**: Automatic FP16 training
- **Gradient Accumulation**: Efficient large batch training
- **Memory Offloading**: CPU and disk offloading for large models

### Usage Example
```python
# Configure DeepSpeed
config = PerformanceConfig(
    enable_multi_gpu=True,
    multi_gpu_config=MultiGPUConfig(
        mode=MultiGPUMode.DEEPSPEED
    )
)

# Create optimizer
optimizer = DiffusionPerformanceOptimizer(config)

# Setup DeepSpeed training
model, dataloader = optimizer.setup_multi_gpu_training(model, dataloader)

# DeepSpeed handles optimization automatically
for batch in dataloader:
    outputs = model(batch)
    loss = criterion(outputs, targets)
    loss.backward()
    optimizer.step()
```

## ⚙️ Configuration Options

### PerformanceConfig
```python
@dataclass
class PerformanceConfig:
    # Multi-GPU settings
    enable_multi_gpu: bool = False
    multi_gpu_sync_bn: bool = True
    multi_gpu_gradient_as_bucket_view: bool = True
    multi_gpu_broadcast_buffers: bool = True
    
    # Memory optimizations
    enable_gradient_checkpointing: bool = False
    enable_attention_slicing: bool = False
    enable_model_offloading: bool = False
    
    # Training accelerations
    enable_mixed_precision: bool = False
    enable_xformers_attention: bool = False
    enable_model_compilation: bool = False
```

### MultiGPUConfig
```python
@dataclass
class MultiGPUConfig:
    # Training mode
    mode: MultiGPUMode = MultiGPUMode.NONE
    
    # Distributed training settings
    distributed_backend: str = "nccl"
    distributed_init_method: str = "env://"
    distributed_world_size: int = 1
    distributed_rank: int = 0
    
    # DataParallel settings
    dataparallel_device_ids: Optional[List[int]] = None
    dataparallel_output_device: Optional[int] = None
    dataparallel_broadcast_buffers: bool = True
```

## 📊 Performance Monitoring

### Metrics Collection
The system automatically collects performance metrics during training:

```python
# Get performance summary
summary = optimizer.get_performance_summary()

# Save performance report
optimizer.save_performance_report("performance_report.json")

# Monitor performance during training
for step in range(num_steps):
    # Training code...
    optimizer.monitor_performance(step)
```

### Memory Monitoring
```python
# Memory usage tracking
memory_info = optimizer.metrics.memory_usage
gpu_info = optimizer.metrics.gpu_utilization

print(f"GPU Memory: {memory_info['gpu_0_allocated']:.2f} GB")
print(f"GPU Utilization: {gpu_info['gpu_0_load']:.1f}%")
```

## 🔧 Best Practices

### 1. Choose the Right Multi-GPU Mode
- **DataParallel**: Good for quick prototyping and small models
- **DistributedDataParallel**: Best for production training
- **Horovod**: Excellent for large-scale distributed training
- **DeepSpeed**: Ideal for very large models with memory constraints

### 2. Optimize Batch Size
```python
# Test different batch sizes to find optimal performance
batch_sizes = [16, 32, 64, 128, 256]
for batch_size in batch_sizes:
    try:
        # Test training with this batch size
        performance = benchmark_batch_size(model, batch_size)
        print(f"Batch {batch_size}: {performance['throughput']:.1f} samples/s")
    except RuntimeError as e:
        if "out of memory" in str(e):
            print(f"Batch {batch_size}: Out of memory")
            break
```

### 3. Memory Optimization
```python
# Enable gradient checkpointing for memory efficiency
config.memory_optimizations.append(MemoryOptimization.GRADIENT_CHECKPOINTING)

# Use attention slicing for large models
config.memory_optimizations.append(MemoryOptimization.ATTENTION_SLICING)

# Enable mixed precision training
config.training_accelerations.append(TrainingAcceleration.MIXED_PRECISION)
```

### 4. Data Loading Optimization
```python
# Optimize data loader for multi-GPU training
dataloader = DataLoader(
    dataset,
    batch_size=32,
    num_workers=4,  # Adjust based on CPU cores
    pin_memory=True,  # Faster GPU transfer
    shuffle=True
)
```

## 🚀 Getting Started

### 1. Basic Setup
```python
from core.diffusion_performance_optimizer import (
    DiffusionPerformanceOptimizer, 
    PerformanceConfig, 
    MultiGPUConfig, 
    MultiGPUMode
)

# Create configuration
config = PerformanceConfig(
    enable_multi_gpu=True,
    multi_gpu_config=MultiGPUConfig(
        mode=MultiGPUMode.DATAPARALLEL
    )
)

# Initialize optimizer
optimizer = DiffusionPerformanceOptimizer(config)
```

### 2. Multi-GPU Training Setup
```python
# Setup multi-GPU training
model, dataloader = optimizer.setup_multi_gpu_training(model, dataloader)

# Train normally
for epoch in range(num_epochs):
    for batch in dataloader:
        # Training step
        outputs = model(batch)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        
        # Monitor performance
        optimizer.monitor_performance(step)
```

### 3. Performance Analysis
```python
# Get performance summary
summary = optimizer.get_performance_summary()

# Save detailed report
optimizer.save_performance_report("training_performance.json")

# Cleanup
optimizer.cleanup()
```

## 📈 Performance Benchmarks

### Expected Speedups
- **2 GPUs**: 1.5x - 1.8x speedup
- **4 GPUs**: 2.5x - 3.5x speedup
- **8 GPUs**: 4.0x - 6.0x speedup

### Factors Affecting Performance
- **Model Size**: Larger models benefit more from multi-GPU
- **Batch Size**: Optimal batch size varies with GPU memory
- **Data Transfer**: PCIe bandwidth can limit performance
- **Communication Overhead**: DDP has lower overhead than DataParallel

## 🐛 Troubleshooting

### Common Issues

#### 1. Out of Memory Errors
```python
# Reduce batch size
batch_size = batch_size // 2

# Enable gradient checkpointing
config.memory_optimizations.append(MemoryOptimization.GRADIENT_CHECKPOINTING)

# Use mixed precision
config.training_accelerations.append(TrainingAcceleration.MIXED_PRECISION)
```

#### 2. Communication Errors
```python
# Check distributed setup
if dist.is_initialized():
    print(f"World size: {dist.get_world_size()}")
    print(f"Rank: {dist.get_rank()}")

# Verify environment variables
print(f"MASTER_ADDR: {os.environ.get('MASTER_ADDR')}")
print(f"MASTER_PORT: {os.environ.get('MASTER_PORT')}")
```

#### 3. Performance Issues
```python
# Monitor GPU utilization
gpu_info = optimizer.get_multi_gpu_info()
print(f"GPU utilization: {gpu_info}")

# Check memory usage
memory_info = optimizer.metrics.memory_usage
print(f"Memory usage: {memory_info}")
```

## 🔮 Future Enhancements

### Planned Features
- **Automatic Mode Selection**: Choose optimal multi-GPU mode based on hardware
- **Dynamic Batch Size**: Automatic batch size adjustment during training
- **Advanced Profiling**: Detailed performance bottleneck analysis
- **Cloud Integration**: Support for cloud-based multi-GPU training
- **Federated Learning**: Multi-device training with privacy preservation

### Research Areas
- **Communication Optimization**: Novel approaches to reduce GPU communication overhead
- **Memory Management**: Advanced memory optimization techniques
- **Load Balancing**: Dynamic workload distribution across GPUs
- **Fault Tolerance**: Robust training with GPU failures

## 📚 Additional Resources

### Documentation
- [PyTorch Distributed Training](https://pytorch.org/tutorials/beginner/dist_overview.html)
- [Horovod Documentation](https://horovod.readthedocs.io/)
- [DeepSpeed Documentation](https://www.deepspeed.ai/)

### Research Papers
- "PyTorch Distributed: Experiences on Accelerating Data Parallel Training"
- "Horovod: fast and easy distributed deep learning in TensorFlow"
- "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models"

### Community
- [PyTorch Forums](https://discuss.pytorch.org/)
- [Horovod GitHub](https://github.com/horovod/horovod)
- [DeepSpeed GitHub](https://github.com/microsoft/DeepSpeed)

## 🤝 Contributing

We welcome contributions to improve the multi-GPU training system! Please see our contributing guidelines for more information.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This system is designed to work with PyTorch 1.8+ and requires CUDA support for GPU acceleration. Some features may require additional dependencies (Horovod, DeepSpeed) for full functionality.
