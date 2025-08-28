# Efficient Data Loading System using PyTorch's DataLoader

## Overview

The Efficient Data Loading System is a comprehensive framework designed to optimize data loading for deep learning training, with special optimizations for diffusion models and general ML workloads. This system leverages PyTorch's DataLoader with advanced features for high-performance, memory-efficient, and scalable data loading.

## Features

### 🚀 **Core Data Loading**
- **Multi-process data loading** with configurable workers
- **Memory-efficient data handling** with intelligent caching strategies
- **Advanced prefetching** and persistent workers for optimal performance
- **GPU memory optimization** with pin_memory and device transfer utilities

### 🎯 **Specialized Datasets**
- **ImageTextDataset**: For image-text pairs commonly used in diffusion models
- **DiffusionDataset**: Specialized dataset for diffusion model training with automatic text loading
- **CachedDataset**: Intelligent caching wrapper with memory and disk caching
- **BaseDataset**: Abstract base class for custom dataset implementations

### ⚡ **Performance Optimization**
- **Automatic worker optimization** based on system resources
- **Performance monitoring** with real-time metrics collection
- **Memory usage tracking** for GPU and CPU operations
- **Profiling tools** for data loading performance analysis

### 🔧 **Advanced Features**
- **Distributed training support** with DistributedSampler
- **Custom samplers** for balanced training and special use cases
- **Flexible collate functions** for variable-length sequences
- **Batch size optimization** based on available GPU memory

### 📊 **Monitoring & Analytics**
- **Real-time performance metrics** collection
- **Memory usage tracking** and optimization suggestions
- **Batch processing statistics** and timing analysis
- **Comprehensive logging** and error handling

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Efficient Data Loading System            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   DataConfig    │  │  DataLoader     │  │  Monitoring │ │
│  │                 │  │   Factory       │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  ImageText      │  │   Diffusion     │  │   Cached    │ │
│  │   Dataset       │  │   Dataset       │  │   Dataset   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ EfficientData   │  │ DataLoader      │  │ Performance │ │
│  │   Loader        │  │   Monitor       │  │  Profiling  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Basic Usage

```python
from core.efficient_data_loading_system import (
    DataConfig, ImageTextDataset, DataLoaderFactory
)

# Create configuration
config = DataConfig(
    batch_size=32,
    num_workers=4,
    pin_memory=True,
    persistent_workers=True
)

# Create dataset
dataset = ImageTextDataset(
    image_paths=["path/to/image1.jpg", "path/to/image2.jpg"],
    texts=["Description 1", "Description 2"],
    image_size=(512, 512)
)

# Create optimized DataLoader
dataloader = DataLoaderFactory.create_dataloader(dataset, config)

# Use the loader
for batch in dataloader:
    images = batch['image']
    texts = batch['text']
    # Process your data...
```

### 2. Diffusion Model Training

```python
from core.efficient_data_loading_system import DiffusionDataset

# Create diffusion dataset from directory
diffusion_dataset = DiffusionDataset(
    data_dir="./training_data",
    image_size=(512, 512),
    cache_enabled=True
)

# Create loader with diffusion-optimized settings
config = DataConfig(
    batch_size=16,
    num_workers=6,
    pin_memory=True,
    persistent_workers=True,
    prefetch_factor=3
)

dataloader = DataLoaderFactory.create_diffusion_loader(
    data_dir="./training_data",
    config=config,
    image_size=(512, 512)
)
```

### 3. Performance Monitoring

```python
from core.efficient_data_loading_system import EfficientDataLoader, DataLoaderMonitor

# Create efficient loader
efficient_loader = EfficientDataLoader(dataset, config)

# Monitor performance
with DataLoaderMonitor(efficient_loader) as monitor:
    for batch in efficient_loader:
        # Monitor this batch
        monitored_batch = monitor.monitor_batch(batch)
        # Process batch...
    
    # Get statistics
    stats = monitor.get_stats()
    print(f"Average batch time: {stats['avg_batch_time']:.4f}s")
```

## Core Components

### DataConfig

Configuration class for data loading parameters with intelligent defaults.

```python
@dataclass
class DataConfig:
    batch_size: int = 32
    num_workers: int = 4
    pin_memory: bool = True
    persistent_workers: bool = True
    prefetch_factor: int = 2
    drop_last: bool = False
    shuffle: bool = True
    collate_fn: Optional[Callable] = None
    sampler: Optional[Sampler] = None
    timeout: int = 0
    multiprocessing_context: str = 'spawn'
    generator: Optional[torch.Generator] = None
```

**Key Parameters:**
- **batch_size**: Number of samples per batch
- **num_workers**: Number of worker processes for data loading
- **pin_memory**: Pin memory for faster GPU transfer
- **persistent_workers**: Keep workers alive between epochs
- **prefetch_factor**: Number of batches to prefetch per worker

### ImageTextDataset

Specialized dataset for image-text pairs with automatic image loading and resizing.

```python
class ImageTextDataset(BaseDataset):
    def __init__(
        self,
        image_paths: List[str],
        texts: List[str],
        transform: Optional[Callable] = None,
        max_text_length: int = 77,
        image_size: Tuple[int, int] = (512, 512)
    )
```

**Features:**
- Automatic image loading and resizing
- Text description handling
- Built-in caching support
- Error handling with placeholder images
- Flexible transform pipeline

### DiffusionDataset

Specialized dataset for diffusion model training with automatic text file discovery.

```python
class DiffusionDataset(BaseDataset):
    def __init__(
        self,
        data_dir: str,
        transform: Optional[Callable] = None,
        image_size: Tuple[int, int] = (512, 512),
        max_text_length: int = 77,
        cache_enabled: bool = True
    )
```

**Features:**
- Automatic image discovery in directory
- Text file association (.txt files with same name)
- Fallback text generation for missing descriptions
- Built-in caching for performance
- Support for multiple image formats

### CachedDataset

Intelligent caching wrapper that provides both memory and disk caching.

```python
class CachedDataset(Dataset):
    def __init__(
        self,
        dataset: Dataset,
        cache_dir: str = "./cache",
        cache_size: int = 1000,
        cache_policy: str = "lru"
    )
```

**Features:**
- **Memory caching**: Fast access to frequently used items
- **Disk caching**: Persistent storage for large datasets
- **LRU/FIFO policies**: Configurable cache eviction strategies
- **Automatic cleanup**: Memory management for optimal performance

### DataLoaderFactory

Factory class for creating optimized DataLoaders with intelligent configuration.

```python
class DataLoaderFactory:
    @staticmethod
    def create_dataloader(
        dataset: Dataset,
        config: DataConfig,
        distributed: bool = False,
        rank: int = 0,
        world_size: int = 1
    ) -> DataLoader
```

**Features:**
- Automatic worker optimization based on system resources
- Distributed training support
- Intelligent sampler creation
- Performance-optimized defaults

### EfficientDataLoader

Enhanced DataLoader with performance monitoring and device management.

```python
class EfficientDataLoader:
    def __init__(
        self,
        dataset: Dataset,
        config: DataConfig,
        device: Optional[torch.device] = None
    )
```

**Features:**
- Performance monitoring and statistics
- Automatic device transfer utilities
- Memory usage tracking
- Batch processing optimization

### DataLoaderMonitor

Context manager for monitoring DataLoader performance in real-time.

```python
class DataLoaderMonitor:
    def __init__(self, data_loader: EfficientDataLoader)
    
    def monitor_batch(self, batch: Any) -> Any
    def get_stats(self) -> Dict[str, Any]
```

**Features:**
- Real-time batch timing
- Memory usage tracking
- Performance statistics collection
- Context manager interface

## Advanced Usage

### 1. Custom Collate Functions

```python
from core.efficient_data_loading_system import create_collate_fn

# Create custom collate function for variable-length sequences
collate_fn = create_collate_fn(pad_value=0.0)

# Use in DataLoader
dataloader = DataLoader(
    dataset,
    batch_size=32,
    collate_fn=collate_fn
)
```

### 2. Distributed Training

```python
# Create distributed DataLoader
dataloader = DataLoaderFactory.create_dataloader(
    dataset,
    config,
    distributed=True,
    rank=0,
    world_size=4
)
```

### 3. Performance Profiling

```python
from core.efficient_data_loading_system import profile_data_loading

# Profile data loading performance
stats = profile_data_loading(efficient_loader, num_batches=10)
print(f"Batches per second: {stats['batches_per_second']:.2f}")
```

### 4. GPU Memory Optimization

```python
from core.efficient_data_loading_system import get_optimal_batch_size

# Calculate optimal batch size based on GPU memory
optimal_batch_size = await get_optimal_batch_size(
    model_size_mb=500,  # Model size in MB
    gpu_memory_gb=8,    # Available GPU memory in GB
    safety_factor=0.8    # Safety margin
)
```

## Performance Optimization

### 1. Worker Optimization

The system automatically determines the optimal number of workers:

```python
def _get_optimal_workers(requested_workers: int) -> int:
    cpu_count = mp.cpu_count()
    gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
    
    # Conservative approach: don't use more than 75% of CPU cores
    max_workers = max(1, int(cpu_count * 0.75))
    
    # If GPU is available, ensure we have enough workers to keep it busy
    if gpu_count > 0:
        min_workers = min(2, max_workers)
    else:
        min_workers = 1
    
    optimal_workers = min(requested_workers, max_workers)
    optimal_workers = max(optimal_workers, min_workers)
    
    return optimal_workers
```

### 2. Memory Management

- **Pin Memory**: Automatically enabled for CUDA devices
- **Persistent Workers**: Keeps workers alive between epochs
- **Prefetch Factor**: Configurable batch prefetching
- **Cache Management**: Intelligent memory and disk caching

### 3. GPU Optimization

- **Device Transfer**: Automatic batch movement to GPU
- **Memory Pinning**: Faster GPU memory transfers
- **Batch Size Optimization**: Based on available GPU memory

## Best Practices

### 1. Configuration Guidelines

```python
# For training (high performance)
config = DataConfig(
    batch_size=32,
    num_workers=6,
    pin_memory=True,
    persistent_workers=True,
    prefetch_factor=3
)

# For inference (memory efficient)
config = DataConfig(
    batch_size=16,
    num_workers=2,
    pin_memory=False,
    persistent_workers=False,
    prefetch_factor=2
)
```

### 2. Dataset Design

- Use appropriate image sizes for your model
- Enable caching for frequently accessed data
- Implement proper error handling for missing files
- Use transforms for data augmentation

### 3. Performance Monitoring

- Monitor batch loading times
- Track memory usage patterns
- Profile data loading bottlenecks
- Adjust worker count based on system resources

### 4. Caching Strategy

- Use memory caching for small, frequently accessed datasets
- Use disk caching for large datasets that don't fit in memory
- Implement LRU policy for optimal cache performance
- Monitor cache hit rates and adjust cache size accordingly

## Troubleshooting

### Common Issues

1. **Memory Errors**
   - Reduce batch size
   - Disable pin_memory
   - Reduce number of workers
   - Enable gradient checkpointing

2. **Slow Data Loading**
   - Increase number of workers
   - Enable persistent_workers
   - Increase prefetch_factor
   - Use SSD storage for data

3. **CUDA Out of Memory**
   - Reduce batch size
   - Use mixed precision training
   - Enable gradient accumulation
   - Monitor GPU memory usage

4. **Worker Process Issues**
   - Check multiprocessing context
   - Reduce number of workers
   - Check for memory leaks
   - Verify data integrity

### Performance Tuning

1. **Worker Count Optimization**
   ```python
   # Start with CPU count / 2
   num_workers = mp.cpu_count() // 2
   
   # Adjust based on memory and performance
   if gpu_memory_gb > 8:
       num_workers = min(num_workers, 8)
   ```

2. **Batch Size Tuning**
   ```python
   # Start with power of 2
   batch_size = 32
   
   # Adjust based on GPU memory
   if torch.cuda.is_available():
       gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
       batch_size = min(batch_size, int(gpu_memory * 0.1))
   ```

3. **Caching Strategy**
   ```python
   # For small datasets
   cache_size = min(1000, len(dataset))
   
   # For large datasets
   cache_size = min(100, len(dataset) // 100)
   ```

## Examples

### 1. Training Loop Integration

```python
# Setup
config = DataConfig(batch_size=32, num_workers=4, pin_memory=True)
dataset = ImageTextDataset(image_paths, texts, image_size=(512, 512))
dataloader = DataLoaderFactory.create_dataloader(dataset, config)

# Training loop
for epoch in range(num_epochs):
    for batch in dataloader:
        # Move to device
        batch = {k: v.to(device) for k, v in batch.items()}
        
        # Training step
        loss = model(batch['image'], batch['text'])
        loss.backward()
        optimizer.step()
```

### 2. Validation Loop

```python
# Validation setup
val_config = DataConfig(batch_size=64, num_workers=2, shuffle=False)
val_dataloader = DataLoaderFactory.create_dataloader(val_dataset, val_config)

# Validation loop
model.eval()
with torch.no_grad():
    for batch in val_dataloader:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(batch['image'], batch['text'])
        # Calculate metrics...
```

### 3. Custom Dataset

```python
class CustomDataset(BaseDataset):
    def __init__(self, data_path: str, transform=None):
        super().__init__(transform)
        self.data_path = data_path
        self.data = self._load_data()
    
    def _load_data(self):
        # Load your data here
        pass
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        if self.transform:
            item = self.transform(item)
        return item

# Usage
dataset = CustomDataset("./data", transform=my_transform)
dataloader = DataLoaderFactory.create_dataloader(dataset, config)
```

## Future Enhancements

### Planned Features

1. **Async Data Loading**
   - Asynchronous data loading for I/O bound operations
   - Background data preparation
   - Non-blocking data loading

2. **Advanced Caching**
   - Hierarchical caching (L1, L2, L3)
   - Predictive caching based on access patterns
   - Distributed caching for multi-node training

3. **Data Augmentation Pipeline**
   - Built-in augmentation strategies
   - Real-time augmentation
   - Augmentation scheduling

4. **Performance Analytics**
   - Detailed performance breakdowns
   - Bottleneck identification
   - Automatic optimization suggestions

5. **Cloud Integration**
   - Cloud storage support (S3, GCS, Azure)
   - Streaming datasets for large-scale data
   - Hybrid local/cloud caching

## Contributing

We welcome contributions to improve the Efficient Data Loading System! Please see our contributing guidelines for more information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on our GitHub repository or contact the development team.

---

**Note**: This system is designed to work with PyTorch 1.8+ and Python 3.7+. For optimal performance, we recommend using the latest stable versions of PyTorch and Python.
