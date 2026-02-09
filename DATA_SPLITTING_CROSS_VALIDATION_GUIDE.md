# Comprehensive Data Splitting and Cross-Validation Guide
## PyTorch Deep Learning Best Practices

This guide documents the comprehensive data splitting and cross-validation system implemented in the `ultra_optimized_deep_learning.py` module, providing best practices for proper train/validation/test splits and cross-validation strategies.

## Table of Contents

1. [Overview](#overview)
2. [Data Split Configuration](#data-split-configuration)
3. [Train/Validation/Test Splits](#trainvalidationtest-splits)
4. [Cross-Validation Strategies](#cross-validation-strategies)
5. [Specialized Splitting Techniques](#specialized-splitting-techniques)
6. [DataLoader Integration](#dataloader-integration)
7. [Factory Functions](#factory-functions)
8. [Best Practices](#best-practices)
9. [Use Cases and Applications](#use-cases-and-applications)
10. [Examples and Tutorials](#examples-and-tutorials)

## Overview

The data splitting and cross-validation system provides comprehensive tools for:

- **Proper Data Splitting**: Train/validation/test splits with configurable ratios
- **Stratified Splitting**: Maintaining class balance across splits
- **Cross-Validation**: Multiple strategies (K-Fold, Stratified, Group, Time Series)
- **Time Series Handling**: Temporal order preservation and gap-based validation
- **Group-Based Splitting**: Preventing data leakage in grouped scenarios
- **DataLoader Integration**: Seamless integration with PyTorch DataLoader
- **Performance Analysis**: Fold variance analysis and distribution validation

## Data Split Configuration

### `DataSplitConfig` Class

```python
@dataclass
class DataSplitConfig:
    """Configuration for comprehensive data splitting and cross-validation."""
    
    # Split ratios
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    
    # Cross-validation configuration
    use_cross_validation: bool = False
    cv_folds: int = 5
    cv_strategy: str = "stratified"  # "kfold", "stratified", "group", "time_series", "shuffle", "repeated"
    cv_repeats: int = 1
    
    # Stratification configuration
    stratify: bool = True
    stratify_labels: Optional[List] = None
    
    # Group-based splitting (for avoiding data leakage)
    group_split: bool = False
    group_labels: Optional[List] = None
    
    # Time series configuration
    time_series_split: bool = False
    time_column: Optional[str] = None
    gap: int = 0  # Gap between train and test in time series
    
    # Random state and shuffling
    random_state: int = 42
    shuffle: bool = True
    
    # Validation
    min_samples_per_split: int = 1
    ensure_minimum_samples: bool = True
```

**Key Configuration Options:**

- **Split Ratios**: Configurable train/validation/test ratios that must sum to 1.0
- **Cross-Validation**: Support for multiple CV strategies with configurable folds
- **Stratification**: Automatic class balance preservation
- **Group Handling**: Group-based splitting to prevent data leakage
- **Time Series**: Temporal order preservation with optional gaps
- **Reproducibility**: Random state control for consistent results

## Train/Validation/Test Splits

### `DataSplit` Class

```python
@dataclass
class DataSplit:
    """Container for data splits."""
    train_indices: List[int]
    val_indices: List[int]
    test_indices: List[int]
    
    # Metadata
    total_samples: int
    train_samples: int
    val_samples: int
    test_samples: int
    split_info: Dict[str, Any] = field(default_factory=dict)
    
    def get_datasets(self, base_dataset: Dataset) -> Tuple[Dataset, Dataset, Dataset]:
        """Create dataset splits from indices."""
        
    def get_dataloaders(
        self, 
        base_dataset: Dataset, 
        config: AdvancedDataLoaderConfig
    ) -> Tuple[AdvancedDataLoader, AdvancedDataLoader, AdvancedDataLoader]:
        """Create DataLoader splits."""
```

**Features:**

- **Index Management**: Stores indices for each split
- **Metadata Tracking**: Sample counts and split information
- **Dataset Creation**: Easy conversion to PyTorch Dataset objects
- **DataLoader Integration**: Direct creation of optimized DataLoaders
- **Split Information**: Detailed metadata about the splitting strategy

### Usage Example

```python
# Create train/validation/test split
data_split = create_train_val_test_split(
    dataset,
    labels=labels,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    stratify=True,
    random_state=42
)

# Get datasets
train_dataset, val_dataset, test_dataset = data_split.get_datasets(dataset)

# Or get DataLoaders directly
dataloader_config = AdvancedDataLoaderConfig(batch_size=32, num_workers=4)
train_loader, val_loader, test_loader = data_split.get_dataloaders(dataset, dataloader_config)
```

## Cross-Validation Strategies

### Supported Strategies

#### 1. K-Fold Cross-Validation
```python
cv_split = create_cross_validation_split(
    dataset,
    cv_folds=5,
    cv_strategy="kfold",
    random_state=42
)
```

#### 2. Stratified Cross-Validation
```python
cv_split = create_cross_validation_split(
    dataset,
    labels=labels,
    cv_folds=5,
    cv_strategy="stratified",
    random_state=42
)
```

#### 3. Group Cross-Validation
```python
config = DataSplitConfig(cv_folds=5, cv_strategy="group")
splitter = ComprehensiveDataSplitter(config)
cv_split = splitter.create_cross_validation_splits(dataset, labels, groups)
```

#### 4. Time Series Cross-Validation
```python
config = DataSplitConfig(cv_folds=5, cv_strategy="time_series", gap=5)
splitter = ComprehensiveDataSplitter(config)
cv_split = splitter.create_cross_validation_splits(dataset)
```

#### 5. Shuffle Split
```python
config = DataSplitConfig(cv_folds=5, cv_strategy="shuffle")
splitter = ComprehensiveDataSplitter(config)
cv_split = splitter.create_cross_validation_splits(dataset)
```

#### 6. Repeated Cross-Validation
```python
config = DataSplitConfig(cv_folds=5, cv_strategy="repeated", cv_repeats=3)
splitter = ComprehensiveDataSplitter(config)
cv_split = splitter.create_cross_validation_splits(dataset, labels)
```

### `CrossValidationSplit` Class

```python
@dataclass
class CrossValidationSplit:
    """Container for complete cross-validation splits."""
    folds: List[CrossValidationFold]
    cv_strategy: str
    total_samples: int
    cv_info: Dict[str, Any] = field(default_factory=dict)
    
    def get_fold_datasets(self, fold_index: int, base_dataset: Dataset) -> Tuple[Dataset, Dataset]:
        """Get datasets for a specific fold."""
        
    def get_fold_dataloaders(
        self, 
        fold_index: int, 
        base_dataset: Dataset, 
        config: AdvancedDataLoaderConfig
    ) -> Tuple[AdvancedDataLoader, AdvancedDataLoader]:
        """Get DataLoaders for a specific fold."""
```

### Cross-Validation Usage

```python
# Create stratified cross-validation
cv_split = create_cross_validation_split(
    dataset,
    labels=labels,
    cv_folds=5,
    cv_strategy="stratified"
)

# Iterate through folds
for fold_idx, fold in enumerate(cv_split):
    train_loader, val_loader = cv_split.get_fold_dataloaders(
        fold_idx, dataset, dataloader_config
    )
    
    # Train and validate on this fold
    model = train_model(model, train_loader, val_loader)
    fold_results = evaluate_model(model, val_loader)
```

## Specialized Splitting Techniques

### Time Series Splitting

```python
def create_time_series_split(
    dataset: Dataset,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    gap: int = 0
) -> DataSplit:
    """Create time series split preserving temporal order."""
```

**Features:**
- Preserves temporal order
- Configurable gaps between splits
- Prevents future data leakage
- Supports forward-chaining validation

### Group-Based Splitting

```python
# Configure group-based splitting
config = DataSplitConfig(
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    group_split=True
)

splitter = ComprehensiveDataSplitter(config)
group_split = splitter.split_dataset(dataset, labels=labels, groups=groups)
```

**Features:**
- Prevents data leakage between groups
- Maintains group integrity
- Configurable group-based ratios
- Useful for user-based, domain-based splits

### Stratified Splitting for Imbalanced Datasets

```python
class StratifiedDataSplitter:
    """Specialized data splitter for imbalanced datasets with stratification."""
    
    def stratified_split(self, dataset: Dataset, labels: List, config: DataSplitConfig) -> DataSplit:
        """Create stratified splits ensuring class balance."""
        
    def balanced_cross_validation(self, dataset: Dataset, labels: List, config: DataSplitConfig) -> CrossValidationSplit:
        """Create balanced cross-validation folds."""
```

**Usage:**
```python
stratified_splitter = StratifiedDataSplitter(min_samples_per_class=5)
balanced_split = stratified_splitter.stratified_split(dataset, labels, config)
```

## DataLoader Integration

### Seamless Integration

The splitting system integrates seamlessly with the existing DataLoader infrastructure:

```python
# From DataSplit
train_loader, val_loader, test_loader = data_split.get_dataloaders(dataset, config)

# From CrossValidationSplit
train_loader, val_loader = cv_split.get_fold_dataloaders(fold_idx, dataset, config)

# Custom configuration per split
train_config = AdvancedDataLoaderConfig(batch_size=32, shuffle=True)
val_config = AdvancedDataLoaderConfig(batch_size=64, shuffle=False)

train_loader = AdvancedDataLoader(train_dataset, train_config)
val_loader = AdvancedDataLoader(val_dataset, val_config)
```

### Advanced DataLoader Features

All split-generated DataLoaders support:
- Memory-efficient collate functions
- Balanced sampling
- Adaptive batching
- Performance monitoring
- Distributed training

## Factory Functions

### Quick Setup Functions

```python
# Standard train/val/test split
def create_train_val_test_split(
    dataset: Dataset,
    labels: Optional[List] = None,
    groups: Optional[List] = None,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    stratify: bool = True,
    random_state: int = 42
) -> DataSplit

# Cross-validation split
def create_cross_validation_split(
    dataset: Dataset,
    labels: Optional[List] = None,
    groups: Optional[List] = None,
    cv_folds: int = 5,
    cv_strategy: str = "stratified",
    random_state: int = 42
) -> CrossValidationSplit

# Time series split
def create_time_series_split(
    dataset: Dataset,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    gap: int = 0
) -> DataSplit
```

## Best Practices

### 1. Choose Appropriate Split Strategy

```python
# For balanced classification
data_split = create_train_val_test_split(dataset, labels, stratify=True)

# For imbalanced datasets
stratified_splitter = StratifiedDataSplitter()
data_split = stratified_splitter.stratified_split(dataset, labels, config)

# For time series
time_split = create_time_series_split(dataset, gap=24)  # 24-hour gap

# For grouped data (users, domains, etc.)
config = DataSplitConfig(group_split=True)
splitter = ComprehensiveDataSplitter(config)
group_split = splitter.split_dataset(dataset, labels, groups)
```

### 2. Cross-Validation Strategy Selection

```python
# Standard classification
cv_split = create_cross_validation_split(dataset, labels, cv_strategy="stratified")

# Time series forecasting
cv_config = DataSplitConfig(cv_strategy="time_series", gap=7)
cv_split = splitter.create_cross_validation_splits(dataset)

# Group-based validation
cv_config = DataSplitConfig(cv_strategy="group")
cv_split = splitter.create_cross_validation_splits(dataset, labels, groups)

# Robust estimation
cv_config = DataSplitConfig(cv_strategy="repeated", cv_repeats=5)
cv_split = splitter.create_cross_validation_splits(dataset, labels)
```

### 3. Validation and Monitoring

```python
# Validate split ratios
assert abs(config.train_ratio + config.val_ratio + config.test_ratio - 1.0) < 1e-6

# Check minimum samples
assert all(split.train_samples >= config.min_samples_per_split 
          for split in [data_split])

# Analyze class distribution
for split_name, indices in [("train", data_split.train_indices), 
                           ("val", data_split.val_indices),
                           ("test", data_split.test_indices)]:
    split_labels = [labels[i] for i in indices]
    distribution = np.bincount(split_labels)
    print(f"{split_name} distribution: {distribution}")
```

### 4. Reproducibility

```python
# Set random state for reproducible splits
config = DataSplitConfig(random_state=42, shuffle=True)

# Save split indices for later use
np.save("train_indices.npy", data_split.train_indices)
np.save("val_indices.npy", data_split.val_indices)
np.save("test_indices.npy", data_split.test_indices)

# Load and recreate splits
train_indices = np.load("train_indices.npy")
train_dataset = Subset(dataset, train_indices)
```

## Use Cases and Applications

### Standard Machine Learning

```python
# Classification with stratified splits
data_split = create_train_val_test_split(
    dataset, labels, stratify=True, random_state=42
)
train_loader, val_loader, test_loader = data_split.get_dataloaders(dataset, config)

# Cross-validation for model selection
cv_split = create_cross_validation_split(dataset, labels, cv_strategy="stratified")
cv_scores = []
for fold_idx in range(len(cv_split)):
    train_loader, val_loader = cv_split.get_fold_dataloaders(fold_idx, dataset, config)
    model = train_model(model, train_loader)
    score = evaluate_model(model, val_loader)
    cv_scores.append(score)
```

### Time Series Analysis

```python
# Time series with forward-chaining validation
time_split = create_time_series_split(dataset, gap=24)  # 24-step gap
train_loader, val_loader, test_loader = time_split.get_dataloaders(dataset, config)

# Time series cross-validation
cv_config = DataSplitConfig(cv_strategy="time_series", cv_folds=5, gap=12)
cv_splitter = ComprehensiveDataSplitter(cv_config)
cv_split = cv_splitter.create_cross_validation_splits(dataset)
```

### Group-Based Applications

```python
# User-based splitting (no user overlap)
user_groups = [user_id for user_id, _ in user_interactions]
group_config = DataSplitConfig(group_split=True, random_state=42)
splitter = ComprehensiveDataSplitter(group_config)
group_split = splitter.split_dataset(dataset, labels, user_groups)

# Domain adaptation
domain_groups = [sample.domain for sample in dataset]
domain_split = splitter.split_dataset(dataset, labels, domain_groups)
```

### Advanced Scenarios

```python
# Nested cross-validation for model selection and evaluation
outer_cv = create_cross_validation_split(dataset, labels, cv_folds=5)
inner_cv_scores = []

for outer_fold in range(len(outer_cv)):
    train_val_dataset, test_dataset = outer_cv.get_fold_datasets(outer_fold, dataset)
    
    # Inner cross-validation for hyperparameter tuning
    inner_cv = create_cross_validation_split(train_val_dataset, cv_folds=3)
    best_params = hyperparameter_search(inner_cv, train_val_dataset)
    
    # Train with best params and evaluate on outer test fold
    final_model = train_with_params(train_val_dataset, best_params)
    score = evaluate_model(final_model, test_dataset)
    inner_cv_scores.append(score)
```

## Examples and Tutorials

### Basic Usage

```python
from ultra_optimized_deep_learning import (
    create_train_val_test_split,
    create_cross_validation_split,
    AdvancedDataLoaderConfig
)

# Create dataset
dataset = MyDataset()
labels = dataset.get_labels()

# Split data
data_split = create_train_val_test_split(
    dataset, labels, 
    train_ratio=0.8, val_ratio=0.1, test_ratio=0.1
)

# Create DataLoaders
config = AdvancedDataLoaderConfig(batch_size=32)
train_loader, val_loader, test_loader = data_split.get_dataloaders(dataset, config)

# Train model
model = MyModel()
trained_model = train_model(model, train_loader, val_loader)

# Evaluate
test_score = evaluate_model(trained_model, test_loader)
```

### Cross-Validation Example

```python
# Create cross-validation splits
cv_split = create_cross_validation_split(
    dataset, labels, 
    cv_folds=5, cv_strategy="stratified"
)

# Perform cross-validation
cv_scores = []
for fold_idx in range(len(cv_split)):
    print(f"Training fold {fold_idx + 1}/{len(cv_split)}")
    
    # Get fold data
    train_loader, val_loader = cv_split.get_fold_dataloaders(
        fold_idx, dataset, config
    )
    
    # Train and evaluate
    model = MyModel()
    model = train_model(model, train_loader)
    score = evaluate_model(model, val_loader)
    cv_scores.append(score)
    
    print(f"Fold {fold_idx + 1} score: {score:.4f}")

print(f"Mean CV score: {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}")
```

### Advanced Configuration

```python
from ultra_optimized_deep_learning import DataSplitConfig, ComprehensiveDataSplitter

# Custom configuration
config = DataSplitConfig(
    train_ratio=0.7,
    val_ratio=0.15, 
    test_ratio=0.15,
    stratify=True,
    cv_folds=10,
    cv_strategy="repeated",
    cv_repeats=3,
    random_state=42,
    min_samples_per_split=5
)

# Create splitter
splitter = ComprehensiveDataSplitter(config)

# Create splits
data_split = splitter.split_dataset(dataset, labels)
cv_split = splitter.create_cross_validation_splits(dataset, labels)

# Analyze splits
print(f"Train: {data_split.train_samples} samples")
print(f"Val: {data_split.val_samples} samples") 
print(f"Test: {data_split.test_samples} samples")
print(f"CV folds: {len(cv_split)} with {config.cv_repeats} repeats")
```

## Integration with Training Pipeline

```python
def train_with_cross_validation(dataset, labels, model_class, config):
    """Complete training pipeline with cross-validation."""
    
    # Create train/test split
    data_split = create_train_val_test_split(dataset, labels, test_ratio=0.2)
    train_val_dataset, _, test_dataset = data_split.get_datasets(dataset)
    
    # Cross-validation on train/val data
    cv_split = create_cross_validation_split(
        train_val_dataset, cv_folds=5, cv_strategy="stratified"
    )
    
    # Train models with cross-validation
    cv_models = []
    cv_scores = []
    
    for fold_idx in range(len(cv_split)):
        model = model_class()
        train_loader, val_loader = cv_split.get_fold_dataloaders(
            fold_idx, train_val_dataset, config
        )
        
        trained_model = train_model(model, train_loader, val_loader)
        score = evaluate_model(trained_model, val_loader)
        
        cv_models.append(trained_model)
        cv_scores.append(score)
    
    # Select best model and evaluate on test set
    best_model = cv_models[np.argmax(cv_scores)]
    test_loader = AdvancedDataLoader(test_dataset, config)
    test_score = evaluate_model(best_model, test_loader)
    
    return {
        'best_model': best_model,
        'cv_scores': cv_scores,
        'test_score': test_score,
        'mean_cv_score': np.mean(cv_scores),
        'cv_std': np.std(cv_scores)
    }
```

## Conclusion

The comprehensive data splitting and cross-validation system provides:

- **Flexible Configuration**: Highly configurable splitting strategies
- **Best Practices**: Built-in validation and error checking
- **Multiple Strategies**: Support for various splitting and CV techniques
- **PyTorch Integration**: Seamless integration with DataLoader system
- **Production Ready**: Robust error handling and performance optimization
- **Reproducible Results**: Consistent random state management

This system ensures proper evaluation methodologies while maintaining compatibility with the existing PyTorch ecosystem and optimization features.

