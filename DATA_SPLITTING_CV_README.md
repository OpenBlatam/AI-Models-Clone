# Data Splitting and Cross-Validation System for Diffusion Models

A comprehensive system for proper train/validation/test splits and cross-validation strategies specifically designed for diffusion models. This system provides robust data splitting capabilities with various validation strategies to ensure reliable model evaluation and training.

## 🚀 Features

### Data Splitting Strategies
- **Train-Validation-Test Split**: Standard three-way split with configurable ratios
- **Train-Test Split**: Two-way split for simpler workflows
- **Cross-Validation Split**: K-fold and other CV strategies
- **Nested Cross-Validation**: For hyperparameter tuning
- **Time Series Split**: Temporal-aware splitting
- **Group-Based Split**: Maintains group integrity across splits

### Cross-Validation Methods
- **K-Fold Cross-Validation**: Standard k-fold splitting
- **Stratified K-Fold**: Maintains class distribution across folds
- **Group K-Fold**: Preserves group structure
- **Time Series Split**: Forward-chaining validation
- **Shuffle Split**: Random sampling-based validation
- **Stratified Shuffle Split**: Stratified random sampling
- **Leave-One-Out**: Exhaustive validation
- **Repeated K-Fold**: Multiple runs for stability

### Advanced Features
- **Stratification**: Maintains class balance across splits
- **Group Preservation**: Keeps related samples together
- **Time Awareness**: Respects temporal ordering
- **Data Distribution Analysis**: Comprehensive split analysis
- **Visualization**: Built-in plotting and analysis tools
- **Integration**: Seamless integration with training systems

## 📦 Installation

### Prerequisites
```bash
pip install torch numpy matplotlib scikit-learn pandas
```

### From Source
```bash
git clone <repository-url>
cd blatam-academy
pip install -e .
```

## 🎯 Quick Start

### Basic Data Splitting
```python
from core.data_splitting_cross_validation_system import (
    create_data_split_config, DataSplitter
)

# Create configuration
config = create_data_split_config(
    split_type=SplitType.TRAIN_VAL_TEST,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    random_state=42,
    shuffle=True
)

# Create splitter and split data
splitter = DataSplitter(config)
result = splitter.split_data(data, labels)

# Access splits
train_indices = result.train_indices
val_indices = result.val_indices
test_indices = result.test_indices
```

### Cross-Validation
```python
from core.data_splitting_cross_validation_system import (
    create_cross_validation_config, CrossValidator
)

# Create CV configuration
cv_config = create_cross_validation_config(
    cv_type=CrossValidationType.STRATIFIED_K_FOLD,
    n_folds=5,
    n_repeats=2,
    random_state=42
)

# Create validator and perform CV
validator = CrossValidator(cv_config)

def create_model():
    return YourModel()

cv_result = validator.cross_validate(
    model_fn=create_model,
    data=train_data,
    labels=train_labels
)

# Access results
summary = cv_result["summary"]
for metric_name, metric_stats in summary.items():
    print(f"{metric_name}: {metric_stats['mean']:.4f} ± {metric_stats['std']:.4f}")
```

## 🔧 Configuration

### DataSplitConfig
```python
@dataclass
class DataSplitConfig:
    split_type: SplitType = SplitType.TRAIN_VAL_TEST
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    
    # Cross-validation parameters
    cv_type: CrossValidationType = CrossValidationType.K_FOLD
    n_folds: int = 5
    n_repeats: int = 1
    
    # Advanced parameters
    random_state: Optional[int] = 42
    shuffle: bool = True
    stratify: Optional[str] = None
    group_by: Optional[str] = None
    time_column: Optional[str] = None
    
    # Validation parameters
    ensure_min_samples: int = 10
    ensure_class_balance: bool = True
    max_imbalance_ratio: float = 0.8
```

### CrossValidationConfig
```python
@dataclass
class CrossValidationConfig:
    cv_type: CrossValidationType = CrossValidationType.K_FOLD
    n_folds: int = 5
    n_repeats: int = 1
    random_state: Optional[int] = 42
    shuffle: bool = True
    stratify: Optional[str] = None
    group_by: Optional[str] = None
    time_column: Optional[str] = None
    
    # Nested CV parameters
    inner_cv_type: CrossValidationType = CrossValidationType.K_FOLD
    inner_n_folds: int = 3
    
    # Performance tracking
    track_metrics: List[str] = field(default_factory=lambda: ["loss", "accuracy"])
    save_predictions: bool = True
    save_models: bool = False
```

## 📊 Usage Examples

### 1. Standard Train-Validation-Test Split
```python
# Create configuration for standard split
config = create_data_split_config(
    split_type=SplitType.TRAIN_VAL_TEST,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    random_state=42,
    shuffle=True
)

# Split data
splitter = DataSplitter(config)
result = splitter.split_data(images, labels)

# Analyze results
sizes = result.get_split_sizes()
ratios = result.get_split_ratios()
print(f"Split sizes: {sizes}")
print(f"Split ratios: {ratios}")

# Access data distributions
if "label_distribution" in result.data_distribution["train"]:
    train_labels = result.data_distribution["train"]["label_distribution"]
    print(f"Train label distribution: {train_labels}")
```

### 2. Stratified Cross-Validation
```python
# Create stratified CV configuration
cv_config = create_cross_validation_config(
    cv_type=CrossValidationType.STRATIFIED_K_FOLD,
    n_folds=5,
    n_repeats=2,
    random_state=42,
    shuffle=True,
    track_metrics=["loss", "accuracy", "f1_score"]
)

# Perform cross-validation
validator = CrossValidator(cv_config)

def create_model():
    return DiffusionModel()

cv_result = validator.cross_validate(
    model_fn=create_model,
    data=training_data,
    labels=training_labels
)

# Analyze results
summary = cv_result["summary"]
for metric_name, metric_stats in summary.items():
    mean_val = metric_stats["mean"]
    std_val = metric_stats["std"]
    print(f"{metric_name}: {mean_val:.4f} ± {std_val:.4f}")
```

### 3. Group-Based Splitting
```python
# Create group-based configuration
config = create_data_split_config(
    split_type=SplitType.GROUP_BASED,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    group_by="patient_id",  # Keep patient data together
    random_state=42,
    shuffle=True
)

# Split data while preserving groups
splitter = DataSplitter(config)
result = splitter.split_data(
    data=medical_images,
    labels=diagnoses,
    groups=patient_ids
)

# Verify group integrity
train_groups = set(groups[result.train_indices])
val_groups = set(groups[result.val_indices])
test_groups = set(groups[result.test_indices])

# Groups should be disjoint
assert len(train_groups & val_groups) == 0
assert len(train_groups & test_groups) == 0
assert len(val_groups & test_groups) == 0
```

### 4. Time Series Splitting
```python
# Create time series configuration
config = create_data_split_config(
    split_type=SplitType.TIME_SERIES,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    time_column="timestamp",
    random_state=42,
    shuffle=False  # No shuffling for time series
)

# Split temporal data
splitter = DataSplitter(config)
result = splitter.split_data(
    data=time_series_data,
    labels=forecast_targets,
    timestamps=timestamps
)

# Verify temporal ordering
train_times = timestamps[result.train_indices]
val_times = timestamps[result.val_indices]
test_times = timestamps[result.test_indices]

assert train_times.max() <= val_times.min()
assert val_times.max() <= test_times.min()
```

### 5. Nested Cross-Validation
```python
# Create nested CV configuration
nested_config = create_nested_cv_config(
    outer_cv_type=CrossValidationType.K_FOLD,
    outer_n_folds=5,
    inner_cv_type=CrossValidationType.K_FOLD,
    inner_n_folds=3
)

# Perform nested cross-validation
validator = CrossValidator(nested_config)

def create_model():
    return DiffusionModel()

cv_result = validator.cross_validate(
    model_fn=create_model,
    data=training_data,
    labels=training_labels
)

# Access nested CV results
outer_folds = cv_result["folds"]
for fold in outer_folds:
    fold_idx = fold["fold"]
    metrics = fold["metrics"]
    print(f"Outer fold {fold_idx}: {metrics}")
```

## 🎨 Visualization and Analysis

### Plot Split Distribution
```python
# Plot the distribution of data across splits
splitter.plot_split_distribution()

# Save plot to file
splitter.plot_split_distribution(save_path="split_distribution.png")
```

### Plot Cross-Validation Results
```python
# Plot CV results
validator.plot_cv_results()

# Save plot to file
validator.plot_cv_results(save_path="cv_results.png")
```

### System-Wide Visualization
```python
# Plot all results from the system
system = DataSplittingCrossValidationSystem()
system.plot_all_results(save_dir="visualizations/")
```

## 🔄 Integration with Training Systems

### Complete Training Workflow
```python
# 1. Create data splitting configuration
split_config = create_data_split_config(
    split_type=SplitType.TRAIN_VAL_TEST,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    random_state=42,
    shuffle=True,
    stratify="labels"
)

# 2. Create cross-validation configuration
cv_config = create_cross_validation_config(
    cv_type=CrossValidationType.STRATIFIED_K_FOLD,
    n_folds=5,
    n_repeats=2,
    random_state=42,
    shuffle=True,
    track_metrics=["loss", "accuracy", "precision", "recall", "f1_score"]
)

# 3. Initialize system components
system = DataSplittingCrossValidationSystem()
splitter = system.create_data_splitter("training_splitter", split_config)
validator = system.create_cross_validator("training_validator", cv_config)

# 4. Split data
split_result = splitter.split_data(data, labels)
train_data = data[split_result.train_indices]
train_labels = labels[split_result.train_indices]

# 5. Perform cross-validation on training set
def create_model():
    return DiffusionModel()

cv_result = validator.cross_validate(
    model_fn=create_model,
    data=train_data,
    labels=train_labels
)

# 6. Use validation set for final evaluation
val_data = data[split_result.val_indices]
val_labels = labels[split_result.val_indices]

# 7. Use test set for final testing (only once!)
test_data = data[split_result.test_indices]
test_labels = labels[split_result.test_indices]
```

## 📈 Best Practices

### 1. Data Splitting
- **Always use stratified splitting** when dealing with imbalanced classes
- **Preserve group integrity** for related samples (e.g., multiple images per patient)
- **Respect temporal ordering** for time series data
- **Use appropriate ratios**: 70/15/15 or 80/10/10 for train/val/test
- **Set random seeds** for reproducible results

### 2. Cross-Validation
- **Choose appropriate CV strategy** based on data characteristics
- **Use stratified CV** for classification tasks
- **Consider group CV** for dependent samples
- **Use nested CV** for hyperparameter tuning
- **Repeat CV multiple times** for stability

### 3. Validation Strategy
- **Never use test set** during training or validation
- **Use validation set** for model selection and early stopping
- **Perform final evaluation** only on test set
- **Monitor data leakage** between splits

### 4. Performance Tracking
- **Track multiple metrics** relevant to your task
- **Monitor split distributions** for consistency
- **Visualize results** for better understanding
- **Save intermediate results** for analysis

## 🚨 Common Pitfalls

### 1. Data Leakage
```python
# ❌ WRONG: Using test set for validation
test_data = data[test_indices]
model.fit(train_data, train_labels)
model.evaluate(test_data, test_labels)  # Data leakage!

# ✅ CORRECT: Use validation set for model selection
val_data = data[val_indices]
model.fit(train_data, train_labels)
val_score = model.evaluate(val_data, val_labels)

# Only use test set for final evaluation
test_score = model.evaluate(test_data, test_labels)
```

### 2. Improper Group Handling
```python
# ❌ WRONG: Random splitting with groups
random_split = train_test_split(data, labels, test_size=0.2)

# ✅ CORRECT: Group-aware splitting
group_splitter = DataSplitter(group_config)
result = group_splitter.split_data(data, labels, groups)
```

### 3. Ignoring Class Imbalance
```python
# ❌ WRONG: Random splitting with imbalanced classes
random_split = train_test_split(data, labels, test_size=0.2)

# ✅ CORRECT: Stratified splitting
stratified_config = create_data_split_config(
    stratify="labels",
    ensure_class_balance=True
)
stratified_splitter = DataSplitter(stratified_config)
result = stratified_splitter.split_data(data, labels)
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Install required dependencies
pip install scikit-learn pandas matplotlib

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 2. Memory Issues
```python
# Use smaller batch sizes for large datasets
config = create_data_split_config(
    ensure_min_samples=100,  # Increase minimum sample requirement
    max_imbalance_ratio=0.9  # Allow more imbalance
)
```

#### 3. Reproducibility Issues
```python
# Always set random state
config = create_data_split_config(
    random_state=42,  # Fixed seed
    shuffle=True
)

# Set global random seeds
import torch
import numpy as np
torch.manual_seed(42)
np.random.seed(42)
```

## 📚 API Reference

### Core Classes

#### DataSplitter
- `__init__(config: DataSplitConfig)`: Initialize splitter
- `split_data(data, labels=None, groups=None, **kwargs)`: Split data
- `plot_split_distribution(save_path=None)`: Visualize splits

#### CrossValidator
- `__init__(config: CrossValidationConfig)`: Initialize validator
- `cross_validate(model_fn, data, labels=None, groups=None, **kwargs)`: Perform CV
- `plot_cv_results(save_path=None)`: Visualize CV results
- `get_best_model(metric_name, criterion)`: Get best performing model

#### DataSplittingCrossValidationSystem
- `create_data_splitter(name, config)`: Create named splitter
- `create_cross_validator(name, config)`: Create named validator
- `plot_all_results(save_dir=None)`: Generate all visualizations

### Utility Functions
- `create_data_split_config(**kwargs)`: Create split configuration
- `create_cross_validation_config(**kwargs)`: Create CV configuration
- `create_nested_cv_config(**kwargs)`: Create nested CV configuration

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details on:
- Code style and standards
- Testing requirements
- Documentation updates
- Issue reporting

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built on top of scikit-learn for robust cross-validation
- Inspired by best practices in machine learning research
- Designed specifically for diffusion model workflows

---

For more information, examples, and advanced usage, please refer to the demo script `run_data_splitting_cv_demo.py` and the source code in `core/data_splitting_cross_validation_system.py`.
