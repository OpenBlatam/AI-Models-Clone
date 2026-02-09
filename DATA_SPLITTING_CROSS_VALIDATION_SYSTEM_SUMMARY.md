# Data Splitting and Cross-Validation System Summary

## Overview

The Data Splitting and Cross-Validation System provides comprehensive capabilities for properly splitting datasets and performing cross-validation in deep learning and machine learning workflows. It addresses the critical need for proper train/validation/test splits and cross-validation to ensure robust model evaluation.

## Core System Files

- **`data_splitting_cross_validation_system.py`** - Main implementation with all splitting and CV components
- **`test_data_splitting_cross_validation.py`** - Comprehensive test suite with performance benchmarks
- **`DATA_SPLITTING_CROSS_VALIDATION_SYSTEM_GUIDE.md`** - Complete documentation and usage guide
- **`DATA_SPLITTING_CROSS_VALIDATION_SYSTEM_SUMMARY.md`** - This summary file

## Key Components

### 1. Splitting Strategies
- **RandomSplit**: Simple random splitting for general use
- **StratifiedSplit**: Stratified splitting for classification tasks
- **TimeSeriesSplit**: Time series splitting for sequential data
- **GroupSplit**: Group-based splitting for dependent samples

### 2. Cross-Validation Types
- **K-Fold**: Standard K-fold cross-validation
- **Stratified K-Fold**: Preserves class distribution
- **Time Series CV**: Respects temporal order
- **Group K-Fold**: Keeps groups together
- **Leave-One-Group-Out**: Extreme group splitting
- **Repeated K-Fold**: Multiple K-fold repetitions
- **Repeated Stratified K-Fold**: Multiple stratified repetitions

### 3. Data Split Management
- **DataSplitManager**: Manages three-way splits (train/validation/test)
- **CrossValidationManager**: High-level cross-validation management
- **NestedCrossValidator**: For hyperparameter tuning with proper validation

### 4. Data Leakage Detection
- **DataLeakageDetector**: Detects duplicate samples and distribution shifts
- **Validation functions**: Check split sizes and imbalance

### 5. Visualization
- **SplitVisualizer**: Plot split distributions and CV results
- **Performance analysis**: Visualize cross-validation performance

### 6. Factory Pattern
- **DataSplitFactory**: Convenient factory methods for common scenarios

## Usage Examples

### 1. Three-Way Split
```python
from data_splitting_cross_validation_system import DataSplitFactory

# Create train/validation/test split
train_data, val_data, test_data = DataSplitFactory.create_three_way_split(
    data=X,
    labels=y,
    train_size=0.7,
    val_size=0.15,
    test_size=0.15,
    stratify=True,
    random_state=42
)
```

### 2. Cross-Validation
```python
# Create cross-validation splits
cv_results = DataSplitFactory.create_cv_splits(
    data=X,
    labels=y,
    cv_type='stratified',
    n_folds=5,
    random_state=42
)
```

### 3. Nested Cross-Validation
```python
# Create nested cross-validation for hyperparameter tuning
nested_results = DataSplitFactory.create_nested_cv(
    data=X,
    labels=y,
    outer_cv_type='stratified',
    inner_cv_type='stratified',
    outer_folds=5,
    inner_folds=3,
    random_state=42
)
```

### 4. Data Leakage Detection
```python
from data_splitting_cross_validation_system import DataLeakageDetector

detector = DataLeakageDetector()

# Check for duplicate samples
leakage_results = detector.check_duplicates(
    train_data, val_data, test_data
)

# Check for distribution shift
shift_results = detector.check_distribution_shift(
    train_labels, val_labels, test_labels
)
```

### 5. Visualization
```python
from data_splitting_cross_validation_system import SplitVisualizer

# Plot split distribution
SplitVisualizer.plot_split_distribution(
    train_labels, val_labels, test_labels,
    title="Dataset Split Distribution"
)

# Plot CV results
SplitVisualizer.plot_cv_results(
    cv_results, metric_name="Accuracy"
)
```

## Split Size Guidelines

### Standard Split (70/15/15)
- Good for large datasets (>10K samples)
- Balanced validation and test sets
- Most common choice

### Conservative Split (80/10/10)
- Good for medium datasets (1K-10K samples)
- More training data
- Smaller validation/test sets

### Aggressive Split (60/20/20)
- Good for small datasets (<1K samples)
- More validation/test data
- Better statistical significance

## Best Practices

### 1. Split Strategy Selection
- **Classification**: Always use stratified splitting
- **Regression**: Use random splitting
- **Time Series**: Use time series splitting
- **Dependent Data**: Use group splitting

### 2. Cross-Validation Guidelines
- **5-fold**: Good balance of bias and variance
- **10-fold**: Lower bias, higher variance
- **3-fold**: Higher bias, lower variance (small datasets)
- **Repeated CV**: Use for small datasets (5-10 repetitions)

### 3. Data Leakage Prevention
- Split data before preprocessing
- Avoid using future information in features
- Check for duplicate samples
- Validate split distributions

### 4. Imbalanced Dataset Handling
- Use stratified splitting
- Check imbalance with `check_imbalance()`
- Consider class weights or sampling techniques
- Monitor performance per class

## Utility Functions

### 1. Validation Functions
```python
from data_splitting_cross_validation_system import (
    validate_split_sizes, calculate_split_indices, check_imbalance
)

# Validate split sizes
is_valid = validate_split_sizes(0.7, 0.15, 0.15)

# Calculate indices
train_idx, val_idx, test_idx = calculate_split_indices(
    n_samples=1000,
    train_size=0.7,
    val_size=0.15,
    test_size=0.15,
    random_state=42
)

# Check imbalance
imbalance_results = check_imbalance(labels, threshold=0.1)
```

### 2. Save/Load Functions
```python
from data_splitting_cross_validation_system import save_splits, load_splits

# Save splits
save_splits(
    train_data, val_data, test_data,
    save_path="data_splits"
)

# Load splits
train_data, val_data, test_data = load_splits(
    save_path="data_splits",
    data_type="csv"
)
```

## System Benefits

- **Proper Data Splitting**: Ensures correct train/validation/test splits
- **Multiple Strategies**: Supports various data types and scenarios
- **Cross-Validation**: Comprehensive CV with multiple fold types
- **Data Leakage Prevention**: Built-in detection and prevention tools
- **Imbalanced Data Handling**: Stratified splitting and imbalance detection
- **Visualization**: Tools for analyzing splits and CV results
- **Reproducibility**: Save/load functionality for consistent splits
- **Factory Pattern**: Easy-to-use factory methods
- **Well-Tested**: Comprehensive test suite with performance benchmarks
- **Documented**: Complete guide with examples and troubleshooting

## Integration

The system integrates seamlessly with:
- PyTorch and TensorFlow workflows
- Scikit-learn pipelines
- HuggingFace datasets
- Custom model architectures
- Distributed training setups
- Hyperparameter tuning frameworks

## Common Use Cases

### 1. Classification Tasks
```python
# Always use stratified splitting for classification
train_data, val_data, test_data = DataSplitFactory.create_three_way_split(
    data=X, labels=y, stratify=True, random_state=42
)

cv_results = DataSplitFactory.create_cv_splits(
    data=X, labels=y, cv_type='stratified', n_folds=5
)
```

### 2. Time Series Forecasting
```python
# Use time series splitting
strategy = TimeSeriesSplit(n_splits=5)
splitter = DataSplitter(strategy)
splits = splitter.split_data(time_series_data)
```

### 3. Medical Data (Group-Based)
```python
# Use group splitting for patient data
strategy = GroupSplit(test_size=0.2, random_state=42)
splitter = DataSplitter(strategy)
train_data, test_data = splitter.split_data(data, groups=patient_ids)
```

### 4. Hyperparameter Tuning
```python
# Use nested cross-validation
nested_results = DataSplitFactory.create_nested_cv(
    data=X, labels=y,
    outer_cv_type='stratified', inner_cv_type='stratified',
    outer_folds=5, inner_folds=3
)
```

This comprehensive data splitting and cross-validation system ensures proper model evaluation and prevents data leakage in machine learning workflows. It provides the foundation for robust model development and evaluation across various data types and scenarios. 