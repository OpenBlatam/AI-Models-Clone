# Data Splitting and Validation for Blaze AI

A comprehensive implementation of proper train/validation/test splits and cross-validation strategies for deep learning workflows, integrated with enhanced PyTorch DataLoader utilities.

## 🚀 Quick Start

### Installation

```bash
# Install required dependencies
pip install torch numpy pandas scikit-learn matplotlib seaborn

# For GPU optimization
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Basic Usage

```python
from deployment.scripts.python.data_splitting_and_validation import DataSplitter, DataSplitConfig
from deployment.scripts.python.enhanced_dataloader import EnhancedDataset, EnhancedDataLoaderFactory

# Configure data splitting
config = DataSplitConfig(
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    stratify=True,
    random_state=42
)

# Create enhanced dataset
dataset = EnhancedDataset(X, y, split_config=config)

# Create data splits
split_datasets = dataset.create_splits()

# Configure DataLoader
dataloader_config = DataLoaderConfig(
    batch_size=32,
    num_workers=4,
    pin_memory=True
)

# Create DataLoaders for all splits
factory = EnhancedDataLoaderFactory(dataloader_config)
split_dataloaders = factory.create_split_dataloaders(dataset)
```

## 📚 Components Overview

### 1. Data Splitting and Validation (`data_splitting_and_validation.py`)

Comprehensive data splitting strategies with validation:

#### **DataSplitConfig**
Configuration class for data splitting strategies:
- **Split ratios**: Configurable train/validation/test proportions
- **Cross-validation**: Number of folds, shuffle settings
- **Stratification**: Maintain class distribution across splits
- **Group-based splitting**: Ensure groups don't overlap between splits
- **Time series splitting**: Maintain temporal order
- **Validation**: Automatic split validation and error checking

#### **DataSplitter**
Handles data splitting for deep learning workflows:

- **Random Split**: Basic random splitting without stratification
- **Stratified Split**: Maintains class distribution across splits
- **Group Split**: Ensures groups don't overlap between splits
- **Time Series Split**: Maintains temporal order for sequential data
- **Split Validation**: Automatic validation of split integrity
- **Split Persistence**: Save and load split configurations

#### **CrossValidator**
Implements various cross-validation strategies:

- **K-Fold**: Standard k-fold cross-validation
- **Stratified K-Fold**: Maintains class distribution in each fold
- **Group K-Fold**: Ensures groups don't overlap between folds
- **Time Series Split**: Temporal cross-validation
- **Fold Management**: Access individual fold data and metrics

#### **DataSplitVisualizer**
Visualization tools for data splits and cross-validation:

- **Split Distribution**: Bar charts showing sample counts and label distribution
- **Cross-Validation Results**: Fold-by-fold analysis with summary statistics
- **Export Options**: Save plots as high-resolution images

### 2. Enhanced DataLoader (`enhanced_dataloader.py`)

Optimized PyTorch DataLoader with built-in splitting support:

#### **DataLoaderConfig**
Comprehensive configuration for DataLoader creation:

- **Basic Settings**: Batch size, shuffle, workers, pin memory
- **Advanced Settings**: Prefetch factor, timeout, worker initialization
- **Memory Optimization**: Pin memory device, memory format
- **Distributed Training**: Multi-GPU and multi-node support
- **Data Augmentation**: Per-split augmentation control
- **Sampling Strategies**: Weighted sampling for imbalanced data

#### **EnhancedDataset**
Enhanced PyTorch Dataset with built-in splitting:

- **Automatic Splitting**: Create train/validation/test splits
- **Cross-Validation**: Generate cross-validation folds
- **Data Validation**: Ensure data consistency and integrity
- **Transform Support**: Built-in data and target transformations
- **Split Management**: Access individual split datasets

#### **EnhancedDataLoaderFactory**
Factory for creating optimized DataLoaders:

- **Split DataLoaders**: Create DataLoaders for all splits
- **Cross-Validation DataLoaders**: Generate fold-specific DataLoaders
- **Weighted Sampling**: Handle imbalanced datasets
- **Distributed Support**: Multi-GPU training support
- **Performance Optimization**: Automatic GPU optimization

#### **DataLoaderOptimizer**
Performance optimization utilities:

- **GPU Optimization**: Automatic batch size and worker optimization
- **Memory Management**: Pin memory and persistent worker optimization
- **Performance Profiling**: Measure throughput and batch timing
- **Resource Allocation**: Optimal resource utilization

### 3. Integration Example (`dataloader_integration_example.py`)

Complete integration example showing how to use all utilities together:

#### **IntegratedTrainer**
Trainer that integrates enhanced DataLoader with training:

- **Split-based Training**: Train with proper train/validation/test splits
- **Cross-Validation Training**: Train with k-fold cross-validation
- **Early Stopping**: Prevent overfitting with validation monitoring
- **Model Checkpointing**: Save best models during training
- **Training Visualization**: Plot training and validation curves

#### **Advanced Features**
Demonstration of advanced capabilities:

- **Group-based Splitting**: Handle grouped data (e.g., patient data)
- **Time Series Splitting**: Maintain temporal order for sequential data
- **Weighted Sampling**: Handle class imbalance with weighted sampling
- **Performance Profiling**: Measure DataLoader performance

## 🎯 Key Features

### 1. Proper Data Splitting

```python
# Stratified splitting maintains class distribution
config = DataSplitConfig(
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    stratify=True,  # Maintain class balance
    random_state=42
)

splitter = DataSplitter(config)
splits = splitter.split_data(X, y)

# Verify no overlap between splits
assert len(set(splits['train_idx']) & set(splits['val_idx'])) == 0
assert len(set(splits['train_idx']) & set(splits['test_idx'])) == 0
assert len(set(splits['val_idx']) & set(splits['test_idx'])) == 0
```

### 2. Cross-Validation Support

```python
# Create cross-validation folds
cv_config = DataSplitConfig(n_splits=5)
cv_validator = CrossValidator(cv_config)

cv_results = cv_validator.cross_validate(X, y, cv_type="stratified")

# Access individual fold data
for fold_idx, fold_split in enumerate(cv_results['fold_splits']):
    train_data = fold_split['train_data']
    val_data = fold_split['val_data']
    print(f"Fold {fold_idx + 1}: Train={len(train_data)}, Val={len(val_data)}")
```

### 3. Enhanced DataLoader Creation

```python
# Create enhanced dataset with automatic splitting
dataset = EnhancedDataset(X, y, split_config=config)
split_datasets = dataset.create_splits()

# Configure optimized DataLoader
dataloader_config = DataLoaderConfig(
    batch_size=64,
    num_workers=4,
    pin_memory=True,
    persistent_workers=True
)

# Create DataLoaders for all splits
factory = EnhancedDataLoaderFactory(dataloader_config)
split_dataloaders = factory.create_split_dataloaders(dataset)

# Access individual split DataLoaders
train_loader = split_dataloaders['train']
val_loader = split_dataloaders['val']
test_loader = split_dataloaders['test']
```

### 4. Advanced Splitting Strategies

#### **Group-based Splitting**
```python
# Ensure groups don't overlap between splits
group_config = DataSplitConfig(
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    group_by='groups'
)

group_dataset = EnhancedDataset(X, y, split_config=group_config)
group_splits = group_dataset.create_splits(groups=group_ids)

# Verify no group overlap
train_groups = set(groups[group_splits['train_idx']])
val_groups = set(groups[group_splits['val_idx']])
test_groups = set(groups[group_splits['test_idx'])

assert len(train_groups & val_groups) == 0
assert len(train_groups & test_groups) == 0
assert len(val_groups & test_groups) == 0
```

#### **Time Series Splitting**
```python
# Maintain temporal order for sequential data
time_config = DataSplitConfig(
    train_ratio=0.6,
    val_ratio=0.2,
    test_ratio=0.2,
    is_time_series=True
)

time_dataset = EnhancedDataset(X, y, split_config=time_config)
time_splits = time_dataset.create_splits()

# Verify temporal order
assert max(time_splits['train_idx']) < min(time_splits['val_idx'])
assert max(time_splits['val_idx']) < min(time_splits['test_idx'])
```

### 5. Weighted Sampling for Imbalanced Data

```python
# Calculate class weights for imbalanced data
unique_labels, counts = np.unique(y, return_counts=True)
total_samples = len(y)
class_weights = {
    label: total_samples / (len(unique_labels) * count) 
    for label, count in zip(unique_labels, counts)
}

# Configure DataLoader with weighted sampling
weighted_config = DataLoaderConfig(
    batch_size=32,
    use_weighted_sampling=True,
    class_weights=class_weights
)

weighted_factory = EnhancedDataLoaderFactory(weighted_config)
weighted_dataloaders = weighted_factory.create_split_dataloaders(dataset)
```

### 6. Performance Optimization

```python
# Optimize DataLoader for GPU training
if torch.cuda.is_available():
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    dataloader_config = DataLoaderOptimizer.optimize_for_gpu(
        dataloader_config, gpu_memory_gb=gpu_memory
    )

# Profile DataLoader performance
profile_results = DataLoaderOptimizer.profile_dataloader(
    train_loader, num_batches=10
)

print(f"Throughput: {profile_results['samples_per_second']:.1f} samples/sec")
print(f"Avg batch time: {profile_results['avg_batch_time']:.3f}s")
```

## 🔧 Integration with Existing Framework

### 1. Training with Proper Splits

```python
from deployment.scripts.python.dataloader_integration_example import IntegratedTrainer

# Create integrated trainer
trainer = IntegratedTrainer(
    model=your_model,
    dataloader_config=dataloader_config,
    learning_rate=0.001
)

# Train with proper splits
split_results = trainer.train_with_splits(
    enhanced_dataset=dataset,
    num_epochs=15,
    early_stopping_patience=5
)

# Access results
train_accuracies = split_results['train_accuracies']
val_accuracies = split_results['val_accuracies']
test_accuracy = split_results['test_accuracy']
```

### 2. Cross-Validation Training

```python
# Train with cross-validation
cv_results = trainer.train_with_cross_validation(
    enhanced_dataset=dataset,
    n_folds=5,
    cv_type="stratified",
    num_epochs=10
)

# Access cross-validation summary
cv_summary = cv_results['cv_summary']
print(f"Mean CV Accuracy: {cv_summary['mean_cv_accuracy']:.4f} ± {cv_summary['std_cv_accuracy']:.4f}")
```

### 3. Visualization and Analysis

```python
# Plot training curves
trainer.plot_training_curves(save_path="./training_curves.png")

# Visualize data splits
from deployment.scripts.python.data_splitting_and_validation import DataSplitVisualizer

DataSplitVisualizer.plot_split_distribution(
    dataset.splits, y, 
    save_path="./split_distribution.png"
)

# Visualize cross-validation results
DataSplitVisualizer.plot_cv_results(
    cv_results, 
    save_path="./cv_results.png"
)
```

## 📊 Best Practices

### 1. Data Splitting Strategy Selection

- **Random Split**: Use for independent, identically distributed data
- **Stratified Split**: Use for classification tasks with imbalanced classes
- **Group Split**: Use when data has natural groupings (e.g., patient data, time series)
- **Time Series Split**: Use for sequential data where order matters

### 2. Cross-Validation Guidelines

- **K-Fold**: Standard choice for most datasets (k=5 or k=10)
- **Stratified K-Fold**: Essential for imbalanced classification tasks
- **Group K-Fold**: Use when data has natural groupings
- **Time Series Split**: Use for temporal data to prevent data leakage

### 3. DataLoader Optimization

- **Batch Size**: Start with 32-64, optimize based on GPU memory
- **Workers**: Use 2-4x number of CPU cores, but not more than 8
- **Pin Memory**: Enable for GPU training, disable for CPU
- **Persistent Workers**: Enable for faster epoch transitions
- **Prefetch Factor**: Use 2-4 for optimal memory usage

### 4. Validation Strategy

- **Early Stopping**: Monitor validation loss to prevent overfitting
- **Model Checkpointing**: Save best models based on validation performance
- **Final Evaluation**: Use test set only for final model evaluation
- **Cross-Validation**: Use for hyperparameter tuning and model selection

## 🚨 Common Issues and Solutions

### 1. Memory Issues

```python
# Reduce batch size and workers
dataloader_config = DataLoaderConfig(
    batch_size=16,  # Reduce from 64
    num_workers=2,  # Reduce from 4
    pin_memory=False  # Disable if memory is limited
)

# Use gradient accumulation for effective larger batch sizes
# (implement in training loop)
```

### 2. Slow Data Loading

```python
# Increase workers and enable persistent workers
dataloader_config = DataLoaderConfig(
    num_workers=8,  # Increase workers
    persistent_workers=True,  # Keep workers alive between epochs
    prefetch_factor=4  # Increase prefetch factor
)

# Profile DataLoader performance
profile_results = DataLoaderOptimizer.profile_dataloader(train_loader)
```

### 3. Imbalanced Data

```python
# Use stratified splitting and weighted sampling
config = DataSplitConfig(stratify=True)
dataset = EnhancedDataset(X, y, split_config=config)

# Calculate and use class weights
class_weights = calculate_class_weights(y)
weighted_config = DataLoaderConfig(
    use_weighted_sampling=True,
    class_weights=class_weights
)
```

### 4. Group Data Handling

```python
# Ensure groups don't overlap between splits
group_config = DataSplitConfig(
    group_by='groups',
    stratify=False  # Stratification may not be compatible with grouping
)

# Verify group separation
group_dataset = EnhancedDataset(X, y, split_config=group_config)
group_splits = group_dataset.create_splits(groups=group_ids)
```

## 📁 File Structure

```
deployment/scripts/python/
├── data_splitting_and_validation.py      # Core splitting and validation utilities
├── enhanced_dataloader.py                # Enhanced DataLoader with splitting support
├── dataloader_integration_example.py     # Complete integration example
└── README-data-splitting-and-validation.md  # This file
```

## 🔗 Integration with Other Components

### 1. GPU Optimization
```python
from deployment.scripts.python.gpu_optimization_and_mixed_precision import GPUOptimizedTrainer

# Use GPU-optimized trainer with enhanced DataLoader
trainer = GPUOptimizedTrainer(
    model=model,
    dataloader_config=dataloader_config
)
```

### 2. Memory Management
```python
from deployment.scripts.python.pytorch_utilities import PyTorchMemoryUtils

# Monitor memory usage during training
memory_utils = PyTorchMemoryUtils()
memory_info = memory_utils.get_gpu_memory_info()
```

### 3. Diffusion Models
```python
from deployment.scripts.python.diffusion_training_evaluation import DiffusionTrainer

# Use enhanced DataLoader with diffusion training
diffusion_trainer = DiffusionTrainer(
    model=diffusion_model,
    train_dataloader=split_dataloaders['train'],
    val_dataloader=split_dataloaders['val']
)
```

## 🤝 Contributing

When contributing to the data splitting and validation implementation:

1. **Follow PEP 8** style guidelines
2. **Use descriptive variable names** that reflect their purpose
3. **Add comprehensive docstrings** for all functions and classes
4. **Include error handling** for edge cases
5. **Add unit tests** for new functionality
6. **Update this README** for new features
7. **Ensure backward compatibility** with existing code

## 📄 License

This implementation is part of the Blaze AI project and follows the same licensing terms.

---

**Happy Data Splitting and Validation! 🎯✨**
