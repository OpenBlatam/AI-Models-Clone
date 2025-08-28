# Efficient Data Loading System Guide

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Data Configuration](#data-configuration)
4. [Dataset Classes](#dataset-classes)
5. [Custom Samplers](#custom-samplers)
6. [Efficient Data Loader](#efficient-data-loader)
7. [Factory Pattern](#factory-pattern)
8. [Manager Class](#manager-class)
9. [Performance Optimization](#performance-optimization)
10. [Utility Functions](#utility-functions)
11. [Best Practices](#best-practices)
12. [Examples](#examples)
13. [Troubleshooting](#troubleshooting)

## System Overview

The Efficient Data Loading System provides high-performance data loading capabilities for deep learning training, with special optimizations for diffusion models and general ML workloads. It leverages PyTorch's DataLoader with advanced features like multi-process loading, caching, and custom samplers.

### Key Features

- **Multi-process data loading** with configurable workers
- **Memory-efficient data handling** with caching and prefetching
- **Custom samplers** for balanced training and infinite iteration
- **Data augmentation pipelines** using Albumentations
- **Distributed training support**
- **Performance monitoring** and profiling
- **Factory pattern** for easy loader creation
- **Manager class** for handling multiple loaders

## Core Components

### 1. DataConfig

Configuration class for data loading parameters:

```python
from efficient_data_loading_system import DataConfig

config = DataConfig(
    batch_size=32,
    num_workers=4,
    pin_memory=True,
    persistent_workers=True,
    prefetch_factor=2,
    drop_last=False,
    shuffle=True
)
```

**Parameters:**
- `batch_size`: Number of samples per batch
- `num_workers`: Number of subprocesses for data loading
- `pin_memory`: Whether to pin memory for faster GPU transfer
- `persistent_workers`: Keep workers alive between epochs
- `prefetch_factor`: Number of batches loaded in memory per worker
- `drop_last`: Drop the last incomplete batch
- `shuffle`: Shuffle the data at each epoch

### 2. BaseDataset

Abstract base class providing common functionality:

```python
class BaseDataset(Dataset, ABC):
    def __init__(self, transform: Optional[Callable] = None):
        self.transform = transform
        self._cached_data = {}
        self._cache_enabled = False
    
    def enable_cache(self, max_size: int = 1000):
        """Enable caching for frequently accessed samples."""
    
    def disable_cache(self):
        """Disable caching."""
```

## Dataset Classes

### 1. ImageDataset

Efficient image dataset with caching and augmentation:

```python
from efficient_data_loading_system import ImageDataset

dataset = ImageDataset(
    image_paths=['path/to/image1.jpg', 'path/to/image2.jpg'],
    labels=[0, 1],  # Optional
    target_size=(256, 256),
    cache_images=False,
    preload_images=False
)
```

**Features:**
- Automatic path validation
- Image resizing and normalization
- Optional label support
- Caching for frequently accessed images
- Preloading for small datasets

### 2. DiffusionDataset

Specialized dataset for diffusion model training:

```python
from efficient_data_loading_system import DiffusionDataset

augmentations = {
    'horizontal_flip': 0.5,
    'rotation': 10,
    'brightness_contrast': 0.1,
    'hue_saturation': 0.1
}

dataset = DiffusionDataset(
    image_paths=image_paths,
    target_size=(256, 256),
    normalize_range=(-1.0, 1.0),
    augmentations=augmentations,
    cache_enabled=True
)
```

**Features:**
- Built-in data augmentations using Albumentations
- Normalization to specified range (default: [-1, 1])
- Optimized for diffusion model training
- Automatic image format handling

## Custom Samplers

### 1. BalancedSampler

Handles imbalanced datasets by weighting samples inversely to class frequency:

```python
from efficient_data_loading_system import BalancedSampler

sampler = BalancedSampler(
    dataset=dataset,
    labels=labels,
    replacement=True,
    num_samples=None
)
```

### 2. InfiniteSampler

Provides infinite iteration for continuous training:

```python
from efficient_data_loading_system import InfiniteSampler

sampler = InfiniteSampler(
    dataset=dataset,
    shuffle=True
)
```

## Efficient Data Loader

The main data loader class with advanced features:

```python
from efficient_data_loading_system import EfficientDataLoader

loader = EfficientDataLoader(
    dataset=dataset,
    config=config,
    device=torch.device('cuda')
)
```

**Key Methods:**
- `__iter__()`: Iterate over batches
- `to_device(batch)`: Move batch to specified device
- `get_batch(batch_idx)`: Get specific batch by index
- `get_stats()`: Get loading statistics

## Factory Pattern

The DataLoaderFactory provides convenient methods for creating different types of loaders:

### 1. Image Loader

```python
from efficient_data_loading_system import DataLoaderFactory

loader = DataLoaderFactory.create_image_loader(
    image_paths=image_paths,
    labels=labels,
    config=config,
    target_size=(256, 256),
    augmentations=augmentations,
    device=device
)
```

### 2. Diffusion Loader

```python
loader = DataLoaderFactory.create_diffusion_loader(
    image_paths=image_paths,
    config=config,
    target_size=(256, 256),
    augmentations=augmentations,
    device=device
)
```

### 3. Balanced Loader

```python
loader = DataLoaderFactory.create_balanced_loader(
    dataset=dataset,
    labels=labels,
    config=config,
    device=device
)
```

### 4. Infinite Loader

```python
loader = DataLoaderFactory.create_infinite_loader(
    dataset=dataset,
    config=config,
    device=device
)
```

## Manager Class

DataLoaderManager handles multiple data loaders:

```python
from efficient_data_loading_system import DataLoaderManager

manager = DataLoaderManager()

# Add loaders
manager.add_loader('train', train_loader, 'training_dataset')
manager.add_loader('val', val_loader, 'validation_dataset')

# Get loader
train_loader = manager.get_loader('train')

# Get statistics
stats = manager.get_all_stats()

# Clean up
manager.close_all()
```

## Performance Optimization

### 1. Optimal Worker Configuration

The system automatically determines optimal number of workers:

```python
def _get_optimal_workers(self) -> int:
    cpu_count = mp.cpu_count()
    gpu_count = torch.cuda.device_count()
    
    optimal = min(
        self.config.num_workers,
        cpu_count,
        max(1, cpu_count // 2)
    )
    
    if gpu_count > 0:
        optimal = min(optimal, gpu_count * 2)
    
    return optimal
```

### 2. Caching Strategies

- **LRU Cache**: For frequently accessed samples
- **Preloading**: For small datasets that fit in memory
- **Persistent Workers**: Keep workers alive between epochs

### 3. Memory Management

- **Pin Memory**: Faster GPU transfer
- **Prefetch Factor**: Load multiple batches per worker
- **Batch Size Optimization**: Based on GPU memory

## Utility Functions

### 1. Custom Collate Function

```python
from efficient_data_loading_system import create_collate_fn

collate_fn = create_collate_fn(pad_value=0.0)
```

### 2. Optimal Batch Size Calculation

```python
from efficient_data_loading_system import get_optimal_batch_size

batch_size = get_optimal_batch_size(
    model_size_mb=100,
    gpu_memory_gb=8,
    safety_factor=0.8
)
```

### 3. Performance Profiling

```python
from efficient_data_loading_system import profile_data_loading

stats = profile_data_loading(
    loader=loader,
    num_batches=10
)

print(f"Samples per second: {stats['samples_per_second']:.2f}")
print(f"Average batch time: {stats['avg_batch_time']:.4f}s")
```

## Best Practices

### 1. Worker Configuration

```python
# For CPU-only training
config = DataConfig(
    num_workers=min(4, mp.cpu_count()),
    pin_memory=False
)

# For GPU training
config = DataConfig(
    num_workers=min(8, mp.cpu_count()),
    pin_memory=True,
    persistent_workers=True
)
```

### 2. Batch Size Optimization

```python
# Calculate optimal batch size
gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
batch_size = get_optimal_batch_size(
    model_size_mb=model_size,
    gpu_memory_gb=gpu_memory,
    safety_factor=0.8
)
```

### 3. Caching Strategy

```python
# For small datasets
dataset.enable_cache(max_size=len(dataset))

# For large datasets
dataset.enable_cache(max_size=1000)  # Cache frequently accessed samples

# For memory-constrained environments
dataset.disable_cache()
```

### 4. Data Augmentation

```python
# Conservative augmentations for classification
augmentations = {
    'horizontal_flip': 0.5,
    'rotation': 5,
    'brightness_contrast': 0.05
}

# Strong augmentations for diffusion models
augmentations = {
    'horizontal_flip': 0.5,
    'rotation': 15,
    'brightness_contrast': 0.2,
    'hue_saturation': 0.2,
    'gaussian_noise': 0.1
}
```

## Examples

### 1. Basic Image Classification

```python
import torch
from efficient_data_loading_system import DataLoaderFactory, DataConfig

# Setup
image_paths = ['path/to/image1.jpg', 'path/to/image2.jpg', ...]
labels = [0, 1, 0, 1, ...]

config = DataConfig(
    batch_size=32,
    num_workers=4,
    pin_memory=True
)

# Create loader
loader = DataLoaderFactory.create_image_loader(
    image_paths=image_paths,
    labels=labels,
    config=config,
    target_size=(224, 224)
)

# Training loop
for batch, batch_labels in loader:
    batch = loader.to_device(batch)
    batch_labels = torch.tensor(batch_labels).to(loader.device)
    
    # Forward pass, loss calculation, backward pass
    ...
```

### 2. Diffusion Model Training

```python
from efficient_data_loading_system import DataLoaderFactory, DataConfig

# Setup
image_paths = ['path/to/image1.jpg', 'path/to/image2.jpg', ...]

augmentations = {
    'horizontal_flip': 0.5,
    'rotation': 10,
    'brightness_contrast': 0.1
}

config = DataConfig(
    batch_size=16,
    num_workers=4,
    pin_memory=True
)

# Create loader
loader = DataLoaderFactory.create_diffusion_loader(
    image_paths=image_paths,
    config=config,
    target_size=(256, 256),
    augmentations=augmentations
)

# Training loop
for batch in loader:
    batch = loader.to_device(batch)
    
    # Diffusion training steps
    ...
```

### 3. Multi-Loader Management

```python
from efficient_data_loading_system import DataLoaderManager, DataLoaderFactory

manager = DataLoaderManager()

# Create train loader
train_loader = DataLoaderFactory.create_image_loader(
    image_paths=train_paths,
    labels=train_labels,
    config=DataConfig(batch_size=32)
)

# Create validation loader
val_loader = DataLoaderFactory.create_image_loader(
    image_paths=val_paths,
    labels=val_labels,
    config=DataConfig(batch_size=32, shuffle=False)
)

# Add to manager
manager.add_loader('train', train_loader, 'training_data')
manager.add_loader('val', val_loader, 'validation_data')

# Training loop
for epoch in range(num_epochs):
    # Training
    train_loader = manager.get_loader('train')
    for batch, labels in train_loader:
        ...
    
    # Validation
    val_loader = manager.get_loader('val')
    for batch, labels in val_loader:
        ...
```

### 4. Performance Profiling

```python
from efficient_data_loading_system import profile_data_loading

# Profile loader performance
stats = profile_data_loading(loader, num_batches=20)

print("Performance Statistics:")
print(f"Total time: {stats['total_time']:.2f}s")
print(f"Average batch time: {stats['avg_batch_time']:.4f}s")
print(f"Samples per second: {stats['samples_per_second']:.2f}")
print(f"Batches per second: {stats['batches_per_second']:.2f}")

# Optimize based on results
if stats['samples_per_second'] < 100:
    print("Consider increasing num_workers or batch_size")
```

## Troubleshooting

### Common Issues

1. **Out of Memory Errors**
   - Reduce batch size
   - Disable pin_memory
   - Reduce num_workers

2. **Slow Data Loading**
   - Increase num_workers
   - Enable persistent_workers
   - Use caching for small datasets
   - Check disk I/O performance

3. **Worker Process Errors**
   - Reduce num_workers
   - Check for memory leaks
   - Use 'spawn' multiprocessing context

4. **Inconsistent Results**
   - Set random seeds
   - Use deterministic samplers
   - Check data augmentation randomness

### Performance Tuning

1. **Monitor GPU Utilization**
   ```python
   # Check if GPU is waiting for data
   if torch.cuda.utilization() < 80:
       print("GPU underutilized - consider increasing batch_size or num_workers")
   ```

2. **Profile Data Loading**
   ```python
   stats = profile_data_loading(loader, num_batches=10)
   print(f"Data loading bottleneck: {stats['avg_batch_time']:.4f}s per batch")
   ```

3. **Memory Profiling**
   ```python
   import psutil
   
   process = psutil.Process()
   memory_info = process.memory_info()
   print(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
   ```

### Debugging Tips

1. **Test with Single Worker**
   ```python
   config = DataConfig(num_workers=0)  # Single-threaded for debugging
   ```

2. **Check Data Integrity**
   ```python
   for i, (batch, labels) in enumerate(loader):
       print(f"Batch {i}: shape={batch.shape}, labels={labels}")
       if i >= 2:  # Check first few batches
           break
   ```

3. **Validate Image Loading**
   ```python
   # Test individual image loading
   dataset = loader.dataset
   for i in range(min(5, len(dataset))):
       sample = dataset[i]
       print(f"Sample {i}: shape={sample.shape if hasattr(sample, 'shape') else type(sample)}")
   ```

This comprehensive guide covers all aspects of the Efficient Data Loading System, from basic usage to advanced optimization techniques. The system is designed to be flexible, performant, and easy to use for various deep learning applications. 