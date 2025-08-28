# Data Splitting and Cross-Validation System Guide

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Splitting Strategies](#splitting-strategies)
4. [Cross-Validation](#cross-validation)
5. [Data Split Management](#data-split-management)
6. [Nested Cross-Validation](#nested-cross-validation)
7. [Data Leakage Detection](#data-leakage-detection)
8. [Visualization](#visualization)
9. [Factory Pattern](#factory-pattern)
10. [Utility Functions](#utility-functions)
11. [Best Practices](#best-practices)
12. [Examples](#examples)
13. [Troubleshooting](#troubleshooting)

## System Overview

The Data Splitting and Cross-Validation System provides comprehensive capabilities for properly splitting datasets and performing cross-validation in deep learning and machine learning workflows. It addresses the critical need for proper train/validation/test splits and cross-validation to ensure robust model evaluation.

### Key Features

- **Multiple splitting strategies** (random, stratified, time-based, group-based)
- **Cross-validation** with various fold types (K-fold, stratified, time series, group)
- **Nested cross-validation** for hyperparameter tuning
- **Data leakage detection** and prevention
- **Imbalanced dataset handling** with stratification
- **Visualization tools** for split analysis
- **Factory pattern** for easy split creation
- **Save/load functionality** for reproducible splits

## Core Components

### 1. SplitStrategy (Abstract Base Class)

Abstract base class for all splitting strategies:

```python
from data_splitting_cross_validation_system import SplitStrategy

class CustomSplit(SplitStrategy):
    def split(self, data: Any, **kwargs) -> Tuple[Any, Any]:
        # Custom splitting logic
        pass
    
    def get_name(self) -> str:
        return "Custom Split"
```

### 2. DataSplitter

Main class for applying splitting strategies:

```python
from data_splitting_cross_validation_system import DataSplitter, RandomSplit

strategy = RandomSplit(test_size=0.2, random_state=42)
splitter = DataSplitter(strategy)
train_data, test_data = splitter.split_data(data)
```

## Splitting Strategies

### 1. RandomSplit

Simple random splitting for general use:

```python
from data_splitting_cross_validation_system import RandomSplit

strategy = RandomSplit(test_size=0.2, random_state=42)
splitter = DataSplitter(strategy)
train_data, test_data = splitter.split_data(data)
```

**Use cases:**
- General machine learning tasks
- When data is already well-mixed
- Quick prototyping

### 2. StratifiedSplit

Stratified splitting for classification tasks:

```python
from data_splitting_cross_validation_system import StratifiedSplit

strategy = StratifiedSplit(test_size=0.2, random_state=42)
splitter = DataSplitter(strategy)
train_data, test_data = splitter.split_data(data, labels=labels)
```

**Use cases:**
- Classification tasks with imbalanced classes
- Ensuring representative class distribution
- Medical diagnosis, fraud detection

### 3. TimeSeriesSplit

Time series splitting for sequential data:

```python
from data_splitting_cross_validation_system import TimeSeriesSplit

strategy = TimeSeriesSplit(n_splits=5)
splitter = DataSplitter(strategy)
splits = splitter.split_data(data)  # Returns list of splits
```

**Use cases:**
- Time series forecasting
- Stock price prediction
- Weather forecasting
- Sensor data analysis

### 4. GroupSplit

Group-based splitting for dependent samples:

```python
from data_splitting_cross_validation_system import GroupSplit

strategy = GroupSplit(test_size=0.2, random_state=42)
splitter = DataSplitter(strategy)
train_data, test_data = splitter.split_data(data, groups=groups)
```

**Use cases:**
- Medical data with multiple samples per patient
- User behavior analysis
- Multi-view data
- Dependent observations

## Cross-Validation

### 1. CrossValidator

Base cross-validation class:

```python
from data_splitting_cross_validation_system import CrossValidator

cv = CrossValidator(
    fold_type='stratified',
    n_folds=5,
    n_repeats=1,
    random_state=42,
    shuffle=True
)
```

### 2. CrossValidationManager

High-level cross-validation management:

```python
from data_splitting_cross_validation_system import CrossValidationManager

cv_manager = CrossValidationManager(
    cv_type='stratified',
    n_folds=5,
    n_repeats=3,
    random_state=42
)

results = cv_manager.perform_cv(
    data=X,
    labels=y,
    model_fn=create_model,
    metric_fn=accuracy_score
)
```

### 3. Supported CV Types

#### K-Fold Cross-Validation
```python
cv_type='kfold'
```
- Standard K-fold splitting
- Good for balanced datasets
- Simple and effective

#### Stratified K-Fold
```python
cv_type='stratified'
```
- Preserves class distribution
- Essential for imbalanced datasets
- Most common for classification

#### Time Series Cross-Validation
```python
cv_type='timeseries'
```
- Respects temporal order
- No future data leakage
- For sequential data

#### Group K-Fold
```python
cv_type='group'
```
- Keeps groups together
- For dependent samples
- Medical, user data

#### Leave-One-Group-Out
```python
cv_type='leave_one_group'
```
- Extreme group splitting
- Small number of groups
- Maximum independence

#### Repeated K-Fold
```python
cv_type='repeated_kfold'
```
- Multiple K-fold repetitions
- More robust estimates
- Better confidence intervals

#### Repeated Stratified K-Fold
```python
cv_type='repeated_stratified'
```
- Multiple stratified repetitions
- Best for imbalanced data
- Most robust estimates

## Data Split Management

### 1. DataSplitManager

Manages three-way splits (train/validation/test):

```python
from data_splitting_cross_validation_system import DataSplitManager

manager = DataSplitManager(
    train_size=0.7,
    val_size=0.15,
    test_size=0.15,
    random_state=42
)

# Three-way split
train_data, val_data, test_data = manager.split_three_way(
    data=X,
    labels=y,
    stratify=True
)

# Train/validation split (for CV)
train_data, val_data = manager.split_with_validation(
    data=X,
    labels=y,
    stratify=True
)
```

### 2. Split Size Guidelines

#### Standard Split (70/15/15)
```python
train_size=0.7, val_size=0.15, test_size=0.15
```
- Good for large datasets (>10K samples)
- Balanced validation and test sets
- Most common choice

#### Conservative Split (80/10/10)
```python
train_size=0.8, val_size=0.1, test_size=0.1
```
- Good for medium datasets (1K-10K samples)
- More training data
- Smaller validation/test sets

#### Aggressive Split (60/20/20)
```python
train_size=0.6, val_size=0.2, test_size=0.2
```
- Good for small datasets (<1K samples)
- More validation/test data
- Better statistical significance

## Nested Cross-Validation

### 1. NestedCrossValidator

For hyperparameter tuning with proper validation:

```python
from data_splitting_cross_validation_system import NestedCrossValidator

outer_cv = CrossValidationManager('stratified', 5, random_state=42)
inner_cv = CrossValidationManager('stratified', 3, random_state=42)

nested_cv = NestedCrossValidator(outer_cv, inner_cv)

results = nested_cv.perform_nested_cv(
    data=X,
    labels=y,
    param_grid=param_grid,
    model_fn=create_model,
    metric_fn=accuracy_score
)
```

### 2. Nested CV Workflow

1. **Outer Loop**: Split data into K folds
2. **Inner Loop**: For each outer fold, perform CV on training data
3. **Hyperparameter Tuning**: Use inner CV to find best parameters
4. **Model Evaluation**: Train with best params on outer training fold
5. **Performance Estimation**: Evaluate on outer validation fold

## Data Leakage Detection

### 1. DataLeakageDetector

Detects common data leakage issues:

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

### 2. Common Leakage Issues

#### Duplicate Samples
- Same sample in train and test sets
- Data augmentation applied before splitting
- Multiple versions of same data

#### Distribution Shift
- Different class distributions
- Temporal drift
- Sampling bias

#### Feature Leakage
- Future information in features
- Target-derived features
- Data preprocessing before splitting

## Visualization

### 1. SplitVisualizer

Visualize splits and CV results:

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

### 2. Visualization Types

#### Split Distribution
- Bar charts of class distribution
- Train vs validation vs test
- Imbalance detection

#### CV Results
- Box plots of fold performance
- Line plots with confidence intervals
- Performance trends

## Factory Pattern

### 1. DataSplitFactory

Convenient factory methods for common scenarios:

```python
from data_splitting_cross_validation_system import DataSplitFactory

# Three-way split
train_data, val_data, test_data = DataSplitFactory.create_three_way_split(
    data=X,
    labels=y,
    train_size=0.7,
    val_size=0.15,
    test_size=0.15,
    stratify=True,
    random_state=42
)

# Cross-validation
cv_results = DataSplitFactory.create_cv_splits(
    data=X,
    labels=y,
    cv_type='stratified',
    n_folds=5,
    random_state=42
)

# Nested cross-validation
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

## Best Practices

### 1. Split Strategy Selection

#### For Classification Tasks
```python
# Always use stratified splitting
strategy = StratifiedSplit(test_size=0.2, random_state=42)
cv_type = 'stratified'
```

#### For Regression Tasks
```python
# Use random splitting
strategy = RandomSplit(test_size=0.2, random_state=42)
cv_type = 'kfold'
```

#### For Time Series
```python
# Use time series splitting
strategy = TimeSeriesSplit(n_splits=5)
cv_type = 'timeseries'
```

#### For Dependent Data
```python
# Use group splitting
strategy = GroupSplit(test_size=0.2, random_state=42)
cv_type = 'group'
```

### 2. Split Size Guidelines

#### Large Datasets (>10K samples)
```python
train_size=0.7, val_size=0.15, test_size=0.15
```

#### Medium Datasets (1K-10K samples)
```python
train_size=0.8, val_size=0.1, test_size=0.1
```

#### Small Datasets (<1K samples)
```python
train_size=0.6, val_size=0.2, test_size=0.2
# Consider using cross-validation instead
```

### 3. Cross-Validation Guidelines

#### Number of Folds
- **5-fold**: Good balance of bias and variance
- **10-fold**: Lower bias, higher variance
- **3-fold**: Higher bias, lower variance (small datasets)

#### Repeated CV
- Use repeated CV for small datasets
- 5-10 repetitions for robust estimates
- Helps with random seed sensitivity

### 4. Data Leakage Prevention

#### Preprocessing Order
```python
# WRONG: Preprocess before splitting
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
train_data, test_data = train_test_split(X_scaled, ...)

# CORRECT: Split first, then preprocess
train_data, test_data = train_test_split(X, ...)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(train_data)
X_test_scaled = scaler.transform(test_data)
```

#### Feature Engineering
```python
# WRONG: Use future information
df['future_price'] = df['price'].shift(-1)

# CORRECT: Only use past information
df['past_price'] = df['price'].shift(1)
```

## Examples

### 1. Basic Classification Workflow

```python
import numpy as np
from sklearn.datasets import make_classification
from data_splitting_cross_validation_system import DataSplitFactory

# Generate data
X, y = make_classification(n_samples=1000, n_classes=3, random_state=42)

# Create three-way split
train_data, val_data, test_data = DataSplitFactory.create_three_way_split(
    data=X,
    labels=y,
    train_size=0.7,
    val_size=0.15,
    test_size=0.15,
    stratify=True,
    random_state=42
)

print(f"Train: {len(train_data[0])}, Val: {len(val_data[0])}, Test: {len(test_data[0])}")

# Perform cross-validation
cv_results = DataSplitFactory.create_cv_splits(
    data=train_data[0],
    labels=train_data[1],
    cv_type='stratified',
    n_folds=5,
    random_state=42
)

print(f"Cross-validation created with {len(cv_results['fold_results'])} folds")
```

### 2. Imbalanced Dataset Handling

```python
from data_splitting_cross_validation_system import (
    DataSplitFactory, check_imbalance, SplitVisualizer
)

# Create imbalanced data
imbalanced_y = np.concatenate([
    np.zeros(800), np.ones(150), np.full(50, 2)
])

# Check imbalance
imbalance_results = check_imbalance(imbalanced_y)
print(f"Is imbalanced: {imbalance_results['is_imbalanced']}")
print(f"Imbalance score: {imbalance_results['imbalance_score']:.3f}")

# Create stratified split
train_data, val_data, test_data = DataSplitFactory.create_three_way_split(
    data=X,
    labels=imbalanced_y,
    stratify=True,
    random_state=42
)

# Visualize distribution
SplitVisualizer.plot_split_distribution(
    train_data[1], val_data[1], test_data[1],
    title="Imbalanced Dataset Split"
)
```

### 3. Time Series Data

```python
from data_splitting_cross_validation_system import (
    DataSplitFactory, TimeSeriesSplit, DataSplitter
)

# Create time series data
time_series_data = np.random.randn(1000, 10)

# Use time series splitting
strategy = TimeSeriesSplit(n_splits=5)
splitter = DataSplitter(strategy)
splits = splitter.split_data(time_series_data)

print(f"Created {len(splits)} time series splits")

# Each split respects temporal order
for i, (train_data, test_data) in enumerate(splits):
    print(f"Split {i+1}: Train={len(train_data)}, Test={len(test_data)}")
    # train_data contains only past data
    # test_data contains only future data
```

### 4. Group-Based Splitting

```python
from data_splitting_cross_validation_system import (
    DataSplitFactory, GroupSplit, DataSplitter
)

# Create data with groups (e.g., patients)
n_samples = 1000
groups = np.random.choice([0, 1, 2, 3, 4], size=n_samples)
X = np.random.randn(n_samples, 10)
y = np.random.choice([0, 1], size=n_samples)

# Use group splitting
strategy = GroupSplit(test_size=0.2, random_state=42)
splitter = DataSplitter(strategy)
train_data, test_data = splitter.split_data(X, groups=groups)

# Verify no group overlap
train_groups = set(groups[:len(train_data)])
test_groups = set(groups[len(train_data):])
print(f"Group overlap: {len(train_groups.intersection(test_groups))}")
```

### 5. Nested Cross-Validation

```python
from data_splitting_cross_validation_system import DataSplitFactory
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Define model creation function
def create_model(**params):
    return RandomForestClassifier(**params, random_state=42)

# Define parameter grid
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20]
}

# Perform nested CV
nested_results = DataSplitFactory.create_nested_cv(
    data=X,
    labels=y,
    outer_cv_type='stratified',
    inner_cv_type='stratified',
    outer_folds=5,
    inner_folds=3,
    random_state=42
)

print(f"Nested CV completed with {len(nested_results['nested_results'])} outer folds")
```

### 6. Data Leakage Detection

```python
from data_splitting_cross_validation_system import (
    DataSplitFactory, DataLeakageDetector
)

# Create splits
train_data, val_data, test_data = DataSplitFactory.create_three_way_split(
    data=X, labels=y, random_state=42
)

# Check for leakage
detector = DataLeakageDetector()

# Check duplicates
leakage_results = detector.check_duplicates(
    train_data[0], val_data[0], test_data[0]
)
print(f"Train-val overlap: {leakage_results['train_val_overlap']}")
print(f"Train-test overlap: {leakage_results['train_test_overlap']}")

# Check distribution shift
shift_results = detector.check_distribution_shift(
    train_data[1], val_data[1], test_data[1]
)
print(f"Distribution shift detected: {any(v > 0.1 for v in shift_results.values())}")
```

### 7. Save and Load Splits

```python
from data_splitting_cross_validation_system import (
    DataSplitFactory, save_splits, load_splits
)
import pandas as pd

# Create DataFrame
df = pd.DataFrame({
    'feature1': np.random.randn(1000),
    'feature2': np.random.randn(1000),
    'label': np.random.choice([0, 1], size=1000)
})

# Create splits
train_data, val_data, test_data = DataSplitFactory.create_three_way_split(
    data=df,
    labels=df['label'],
    stratify=True,
    random_state=42
)

# Save splits
save_splits(
    train_data[0], val_data[0], test_data[0],
    save_path="my_splits"
)

# Load splits later
loaded_train, loaded_val, loaded_test = load_splits(
    save_path="my_splits",
    data_type="csv"
)

# Verify data is preserved
pd.testing.assert_frame_equal(train_data[0], loaded_train)
```

## Troubleshooting

### Common Issues

1. **Split Sizes Don't Sum to 1.0**
   ```python
   # Error: ValueError: Split sizes must sum to 1.0
   # Solution: Ensure train_size + val_size + test_size = 1.0
   manager = DataSplitManager(train_size=0.7, val_size=0.15, test_size=0.15)
   ```

2. **Stratification Requires Labels**
   ```python
   # Error: Labels required for stratified cross-validation
   # Solution: Provide labels when using stratified methods
   cv_results = DataSplitFactory.create_cv_splits(X, labels=y, cv_type='stratified')
   ```

3. **Group Splitting Requires Groups**
   ```python
   # Error: Groups required for group cross-validation
   # Solution: Provide groups when using group methods
   cv_results = DataSplitFactory.create_cv_splits(X, labels=y, groups=groups, cv_type='group')
   ```

4. **Data Leakage Detected**
   ```python
   # Warning: Overlap detected between splits
   # Solution: Check preprocessing order and data sources
   # Ensure no duplicate samples or future information
   ```

### Performance Issues

1. **Slow Cross-Validation**
   ```python
   # Reduce number of folds
   cv_results = DataSplitFactory.create_cv_splits(X, y, n_folds=3)
   
   # Use simpler CV type
   cv_results = DataSplitFactory.create_cv_splits(X, y, cv_type='kfold')
   ```

2. **Memory Issues with Large Datasets**
   ```python
   # Use smaller validation/test sets
   train_data, val_data, test_data = DataSplitFactory.create_three_way_split(
       data=X, labels=y, train_size=0.8, val_size=0.1, test_size=0.1
   )
   ```

### Debugging Tips

1. **Check Split Sizes**
   ```python
   print(f"Train: {len(train_data[0])}")
   print(f"Val: {len(val_data[0])}")
   print(f"Test: {len(test_data[0])}")
   print(f"Total: {len(train_data[0]) + len(val_data[0]) + len(test_data[0])}")
   ```

2. **Verify Stratification**
   ```python
   from collections import Counter
   
   train_dist = Counter(train_data[1])
   val_dist = Counter(val_data[1])
   test_dist = Counter(test_data[1])
   
   print(f"Train distribution: {dict(train_dist)}")
   print(f"Val distribution: {dict(val_dist)}")
   print(f"Test distribution: {dict(test_dist)}")
   ```

3. **Check for Data Leakage**
   ```python
   from data_splitting_cross_validation_system import DataLeakageDetector
   
   detector = DataLeakageDetector()
   leakage_results = detector.check_duplicates(train_data[0], val_data[0], test_data[0])
   print(f"Leakage check: {leakage_results}")
   ```

This comprehensive guide covers all aspects of the Data Splitting and Cross-Validation System, from basic usage to advanced techniques. The system is designed to ensure proper data splitting and robust model evaluation in machine learning workflows. 