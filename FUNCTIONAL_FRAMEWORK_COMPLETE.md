# Functional Deep Learning Framework

## Overview

This framework implements a **functional, declarative programming approach** for deep learning tasks, avoiding classes where possible and using pure functions, dataclasses, and functional composition patterns.

## Core Principles

### 1. **Functional Programming**
- Pure functions with no side effects
- Immutable data structures using dataclasses
- Function composition over inheritance
- Declarative configuration over imperative code

### 2. **Modular Design**
- Separate concerns: config, models, training, data
- Composable functions that can be combined
- Clear input/output contracts
- Minimal dependencies between modules

### 3. **Type Safety**
- Comprehensive type hints
- Dataclasses for structured data
- Validation functions for configuration
- Error handling with functional patterns

## Architecture

```
functional_framework.py      # Main integration
├── functional_config.py     # Configuration management
├── functional_models.py     # Model creation
├── functional_training.py   # Training functions
└── functional_data.py       # Data processing
```

## Key Components

### 1. Configuration Management (`functional_config.py`)

**Pure Functions:**
```python
def create_default_config() -> Dict[str, Any]
def load_config_from_yaml(file_path: str) -> Dict[str, Any]
def merge_configs(base: Dict, override: Dict) -> Dict[str, Any]
def get_config_value(config: Dict, path: str, default: Any) -> Any
```

**Dataclasses:**
```python
@dataclass
class ModelConfig:
    model_type: str
    hidden_size: int = 768
    num_layers: int = 12

@dataclass
class TrainingConfig:
    batch_size: int = 32
    learning_rate: float = 1e-4
    epochs: int = 100
```

### 2. Model Creation (`functional_models.py`)

**Factory Functions:**
```python
def create_linear_layer(input_size: int, output_size: int) -> nn.Linear
def create_conv_layer(in_channels: int, out_channels: int) -> nn.Conv2d
def create_transformer_block(hidden_size: int, num_heads: int) -> nn.Module
def create_simple_classifier(input_size: int, num_classes: int) -> nn.Module
def create_model_by_type(model_type: str, config: Dict) -> nn.Module
```

**Composition Pattern:**
```python
# Build complex models through function composition
model = nn.Sequential(
    create_linear_layer(784, 512),
    nn.ReLU(),
    create_linear_layer(512, 10)
)
```

### 3. Training Functions (`functional_training.py`)

**Pure Training Functions:**
```python
def train_step(model, optimizer, criterion, data, target) -> Dict[str, float]
def validate_step(model, criterion, data, target) -> Dict[str, float]
def train_epoch(model, train_loader, optimizer, criterion) -> Dict[str, float]
def train_model(model, train_loader, val_loader, config) -> List[TrainingState]
```

**Immutable State:**
```python
@dataclass
class TrainingState:
    epoch: int
    step: int
    loss: float
    accuracy: float
    learning_rate: float
```

### 4. Data Processing (`functional_data.py`)

**Data Pipeline Functions:**
```python
def create_tensor_dataset(data: np.ndarray, labels: np.ndarray) -> TensorDataset
def create_data_loader(dataset: Dataset, batch_size: int) -> DataLoader
def split_dataset(dataset: Dataset, train_ratio: float) -> Tuple[Dataset, Dataset, Dataset]
def preprocess_data(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict]
```

## Usage Examples

### 1. Basic Training Pipeline

```python
from functional_framework import run_training_experiment
import numpy as np

# Create data
X = np.random.randn(1000, 784)
y = np.random.randint(0, 10, 1000)

# Run experiment
results = run_training_experiment(X=X, y=y)
print(f"Test accuracy: {results['test_metrics']['test_accuracy']:.4f}")
```

### 2. Model Comparison

```python
from functional_framework import create_model_comparison

models_config = [
    {'model_type': 'classifier', 'name': 'simple_classifier'},
    {'model_type': 'cnn', 'name': 'cnn_classifier'},
    {'model_type': 'transformer', 'name': 'transformer_classifier'}
]

comparison_results = create_model_comparison(models_config, X, y)
```

### 3. Hyperparameter Search

```python
from functional_framework import create_hyperparameter_search

param_grid = {
    'learning_rate': [1e-3, 1e-4],
    'batch_size': [16, 32],
    'optimizer': ['adam', 'adamw']
}

hp_results = create_hyperparameter_search(param_grid, X, y)
print(f"Best parameters: {hp_results['best_params']}")
```

### 4. Custom Configuration

```python
from functional_config import create_default_config, save_config

# Create custom config
config = create_default_config()
config['training']['learning_rate'] = 1e-4
config['training']['batch_size'] = 64
config['model']['hidden_size'] = 1024

# Save configuration
save_config(config, "custom_config.yaml")
```

## Key Benefits

### 1. **Simplicity**
- No complex class hierarchies
- Clear function signatures
- Easy to understand and modify
- Minimal boilerplate code

### 2. **Composability**
- Functions can be easily combined
- Modular design allows reuse
- Clear separation of concerns
- Easy to test individual components

### 3. **Immutability**
- Dataclasses provide immutable state
- No unexpected side effects
- Thread-safe operations
- Predictable behavior

### 4. **Type Safety**
- Comprehensive type hints
- Better IDE support
- Catch errors at development time
- Self-documenting code

### 5. **Performance**
- No class instantiation overhead
- Efficient function calls
- Memory-efficient operations
- Optimized data pipelines

## Advanced Features

### 1. **Functional Composition**
```python
# Compose complex pipelines
pipeline = (
    create_data_loaders(X, y) >>
    setup_model_and_data(config) >>
    train_model(epochs=100) >>
    evaluate_model(test_loader)
)
```

### 2. **Immutable State Management**
```python
# Training state is immutable
state = TrainingState(epoch=1, step=100, loss=0.5, accuracy=0.8, lr=1e-3)
new_state = TrainingState(epoch=state.epoch + 1, ...)
```

### 3. **Pure Functions**
```python
# No side effects, same input always produces same output
def normalize_data(data: np.ndarray) -> np.ndarray:
    return (data - data.mean()) / data.std()
```

### 4. **Function Currying**
```python
from functools import partial

# Create specialized functions
create_adam_optimizer = partial(create_optimizer, optimizer_type="adam")
create_cosine_scheduler = partial(create_scheduler, scheduler_type="cosine")
```

## Error Handling

### 1. **Functional Error Handling**
```python
from typing import Union, Optional

def safe_divide(a: float, b: float) -> Union[float, None]:
    return a / b if b != 0 else None

def process_data(data: np.ndarray) -> Optional[np.ndarray]:
    try:
        return normalize_data(data)
    except Exception:
        return None
```

### 2. **Validation Functions**
```python
def validate_config(config: Dict[str, Any]) -> List[str]:
    errors = []
    if config.get('learning_rate', 0) <= 0:
        errors.append("Learning rate must be positive")
    return errors
```

## Performance Optimizations

### 1. **Lazy Evaluation**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_config_value(config: Dict[str, Any], path: str) -> Any:
    # Cached configuration access
    pass
```

### 2. **Memory Efficiency**
```python
def create_memory_efficient_loader(dataset: Dataset, batch_size: int) -> DataLoader:
    return DataLoader(
        dataset,
        batch_size=batch_size,
        pin_memory=False,  # Disable for memory efficiency
        persistent_workers=True
    )
```

### 3. **Batch Processing**
```python
def process_batch(batch: torch.Tensor, transform: Callable) -> torch.Tensor:
    return torch.stack([transform(item) for item in batch])
```

## Testing Strategy

### 1. **Unit Testing**
```python
def test_create_linear_layer():
    layer = create_linear_layer(10, 5)
    assert layer.in_features == 10
    assert layer.out_features == 5
    assert layer.weight.shape == (5, 10)
```

### 2. **Integration Testing**
```python
def test_training_pipeline():
    X = np.random.randn(100, 784)
    y = np.random.randint(0, 10, 100)
    
    results = run_training_experiment(X=X, y=y)
    assert 'test_metrics' in results
    assert 'training_history' in results
```

### 3. **Property-Based Testing**
```python
from hypothesis import given, strategies as st

@given(st.lists(st.floats(min_value=0, max_value=1)))
def test_normalize_data_properties(data):
    normalized = normalize_data(np.array(data))
    assert normalized.mean() == pytest.approx(0, abs=1e-10)
    assert normalized.std() == pytest.approx(1, abs=1e-10)
```

## Best Practices

### 1. **Function Design**
- Keep functions small and focused
- Use descriptive names
- Provide comprehensive type hints
- Document with docstrings

### 2. **Data Flow**
- Use immutable data structures
- Avoid global state
- Pass data explicitly between functions
- Use dataclasses for structured data

### 3. **Error Handling**
- Use Option/Result patterns
- Provide meaningful error messages
- Handle edge cases explicitly
- Use validation functions

### 4. **Performance**
- Use lazy evaluation where appropriate
- Cache expensive computations
- Optimize data pipelines
- Monitor memory usage

## Conclusion

This functional framework provides a clean, maintainable, and efficient approach to deep learning development. By avoiding classes and using pure functions, we achieve:

- **Better testability** through pure functions
- **Improved performance** through reduced overhead
- **Enhanced maintainability** through clear data flow
- **Greater flexibility** through function composition
- **Type safety** through comprehensive type hints

The framework demonstrates how functional programming principles can be effectively applied to deep learning workflows while maintaining performance and usability. 