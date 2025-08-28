# 🚀 Functional, Declarative Programming Approach

## Overview

This codebase has been refactored to use **functional, declarative programming** patterns instead of object-oriented classes. The approach emphasizes:

- **Pure functions** with no side effects
- **Data transformations** over mutable state
- **Composition** over inheritance
- **Immutable data structures**
- **Declarative configuration**

## Key Principles

### 1. Pure Functions
All functions are designed to be pure - they don't modify external state and always return the same output for the same input.

```python
# ✅ Pure function
def calculate_metrics(y_true, y_pred):
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'f1': f1_score(y_true, y_pred)
    }

# ❌ Impure function (modifies external state)
def calculate_metrics_impure(y_true, y_pred, metrics_store):
    metrics_store['accuracy'] = accuracy_score(y_true, y_pred)  # Side effect!
```

### 2. Immutable Data Structures
All data structures are immutable using `@dataclass(frozen=True)`:

```python
@dataclass(frozen=True)
class TrainingConfig:
    model_name: str
    batch_size: int
    learning_rate: float

# ✅ Immutable update
new_config = update_config(config, batch_size=32)

# ❌ Mutable modification
config.batch_size = 32  # This would fail!
```

### 3. Data Transformations
Instead of modifying objects, we transform data:

```python
# ✅ Data transformation
def update_experiment_state(current_state, **updates):
    return {**current_state, **updates}

# ❌ Mutable state modification
def update_experiment_state_mutable(state, **updates):
    state.update(updates)  # Modifies original state
```

### 4. Composition Over Inheritance
Functions are composed together instead of using class inheritance:

```python
# ✅ Function composition
def evaluate_model(y_true, y_pred, task_type):
    metrics = calculate_metrics(y_true, y_pred)
    result = create_evaluation_result(metrics, task_type)
    return export_results(result)

# ❌ Class inheritance
class BaseEvaluator:
    def evaluate(self): pass

class ClassificationEvaluator(BaseEvaluator):
    def evaluate(self): pass
```

## File Structure

### Core Functional Modules

```
functional_training.py          # Pure training functions
functional_fastapi_app.py       # Functional FastAPI endpoints
functional_config_loader.py     # Configuration management
functional_evaluation_metrics.py # Evaluation and metrics
```

### Key Functions

#### Training Pipeline
- `create_training_state()` - Creates immutable training state
- `train_model()` - Pure training function
- `evaluate_model()` - Pure evaluation function
- `update_config()` - Immutable config updates

#### Configuration Management
- `load_config_from_yaml()` - Pure config loading
- `validate_config()` - Pure validation
- `create_experiment_config()` - Immutable experiment configs
- `merge_configs()` - Pure config merging

#### Evaluation Metrics
- `calculate_classification_metrics()` - Pure metric calculation
- `compare_models()` - Pure model comparison
- `export_evaluation_results()` - Pure result export

#### FastAPI Integration
- `create_fastapi_app()` - Pure app creation
- `create_training_response()` - Pure response creation
- `handle_training_error()` - Pure error handling

## Usage Examples

### Quick Training

```python
# Functional approach
config = create_default_config("distilbert-base-uncased", "data/dataset.csv")
config = update_config(config, num_epochs=5)
results = await quick_train_transformer(config.model_name, config.dataset_path, config.num_epochs)
```

### Configuration Management

```python
# Load and validate config
config = load_config_from_yaml("config.yaml")
is_valid, errors = validate_config(config)

# Create experiment config
exp_config = create_experiment_config("exp_001", "My experiment", config)
```

### Model Evaluation

```python
# Evaluate model
result = evaluate_model(y_true, y_pred, y_prob, TaskType.CLASSIFICATION)

# Compare models
comparison = compare_models({
    'Model A': result_a,
    'Model B': result_b
}, metric_name='f1')
```

### FastAPI Endpoints

```python
@app.post("/train/quick")
async def quick_training(request: TrainingRequest):
    # Pure function calls
    experiment_id = create_experiment_id(request)
    state = create_experiment_state(experiment_id, request)
    response = create_training_response(experiment_id, "started", "Success")
    return response
```

## Benefits of Functional Approach

### 1. Predictability
- Functions always return the same output for the same input
- No hidden state or side effects
- Easier to reason about and debug

### 2. Testability
- Pure functions are easy to test
- No need to mock complex object state
- Isolated unit tests

### 3. Composability
- Functions can be easily combined
- Reusable building blocks
- Clear data flow

### 4. Immutability
- Prevents accidental state mutations
- Thread-safe by design
- Clear data ownership

### 5. Performance
- No object instantiation overhead
- Better memory usage
- Easier to optimize

## Migration from Classes

### Before (Class-based)
```python
class ModelTrainer:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.optimizer = None
    
    def train(self):
        self.setup_model()
        self.setup_optimizer()
        self.run_training()
    
    def setup_model(self):
        self.model = create_model(self.config)
```

### After (Functional)
```python
def create_training_state(config):
    model = create_model(config)
    optimizer = create_optimizer(model, config)
    return TrainingState(config=config, model=model, optimizer=optimizer)

def train_model(config):
    state = create_training_state(config)
    return run_training(state)
```

## Best Practices

### 1. Function Design
- Keep functions small and focused
- Use descriptive names
- Document input/output types
- Handle errors explicitly

### 2. Data Flow
- Pass data explicitly between functions
- Avoid global state
- Use immutable data structures
- Transform data, don't mutate

### 3. Error Handling
- Return error states explicitly
- Use Result types for complex operations
- Log errors at the boundary
- Provide meaningful error messages

### 4. Testing
- Test pure functions with various inputs
- Use property-based testing
- Test error conditions
- Mock external dependencies

## Performance Considerations

### 1. Memory Usage
- Immutable data structures may use more memory
- Use `copy()` sparingly
- Consider lazy evaluation for large datasets

### 2. Function Calls
- Function call overhead is minimal
- Compiler optimizations help
- Profile if performance is critical

### 3. Parallelization
- Pure functions are naturally parallelizable
- Use `concurrent.futures` for I/O operations
- Consider `multiprocessing` for CPU-intensive tasks

## Debugging

### 1. Function Tracing
```python
import logging

def traced_function(func):
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__} with {args}, {kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__} returned {result}")
        return result
    return wrapper
```

### 2. Data Inspection
```python
def inspect_data(data, label=""):
    print(f"{label}: {type(data)} - {data}")
    return data

# Use in pipeline
result = (data
    .pipe(lambda x: inspect_data(x, "After loading"))
    .pipe(transform_data)
    .pipe(lambda x: inspect_data(x, "After transform")))
```

## Future Enhancements

### 1. Type Safety
- Add comprehensive type hints
- Use `mypy` for static type checking
- Consider `pydantic` for runtime validation

### 2. Functional Libraries
- Consider `toolz` for advanced functional utilities
- Use `functools` for function composition
- Explore `more-itertools` for data processing

### 3. Async Support
- Use `asyncio` for I/O operations
- Consider `trio` for advanced async patterns
- Implement proper error handling for async functions

## Conclusion

The functional, declarative approach provides:

- **Better maintainability** through pure functions
- **Improved testability** with isolated functions
- **Enhanced reliability** with immutable data
- **Clearer code** with explicit data flow
- **Better performance** through optimization opportunities

This approach is particularly well-suited for ML/AI systems where data transformations are central to the application logic. 