# Named Exports for Routes and Utility Functions

## Overview

This document explains how the framework has been refactored to **favor named exports for routes and utility functions**, following modern JavaScript/TypeScript best practices and improving code organization, maintainability, and reusability.

## Key Principles

### 1. **Named Exports Over Default Exports**
- Use named exports for all functions and classes
- Avoid default exports to prevent naming conflicts
- Enable better tree-shaking and code splitting
- Improve IDE autocomplete and refactoring support

### 2. **Explicit `__all__` Declarations**
- Define `__all__` list to control what gets imported
- Make imports explicit and intentional
- Prevent accidental imports of internal functions
- Improve code documentation and discoverability

### 3. **Route Handler Factory Pattern**
- Create factory functions that return route handlers
- Enable dependency injection and configuration
- Support middleware and validation layers
- Allow for easy testing and mocking

## Named Exports Examples

### 1. **Core Utilities with Named Exports**

```python
# functional_utils_exports.py
from typing import Dict, Any, List, Callable, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')
U = TypeVar('U')

@dataclass
class Result(Generic[T]):
    """Immutable result container for functional error handling."""
    value: Optional[T] = None
    error: Optional[str] = None
    is_successful: bool = True

# Named exports for core utilities
def safe_execute(func: Callable[..., T], *args, **kwargs) -> Result[T]:
    """Safely execute function and return Result."""
    try:
        result = func(*args, **kwargs)
        return Result.success(result)
    except Exception as e:
        return Result.failure(str(e))

def compose(*functions: Callable) -> Callable:
    """Compose multiple functions from right to left."""
    return reduce(lambda f, g: lambda x: f(g(x)), functions)

def pipe(value: T, *functions: Callable) -> T:
    """Pipe value through multiple functions."""
    return reduce(lambda acc, f: f(acc), functions, value)

def batch_process(items: List[T], processor: Callable[[T], U], 
                  batch_size: int = 32) -> List[U]:
    """Process items in batches to avoid memory issues."""
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = [processor(item) for item in batch]
        results.extend(batch_results)
    return results

# Export all named functions and classes
__all__ = [
    'Result',
    'safe_execute',
    'compose',
    'pipe',
    'batch_process',
    'retry',
    'memoize',
    'create_logger',
    'validate_inputs',
    'create_device_manager',
    'create_metric_tracker',
    'create_config_validator',
    'create_model_factory',
    'create_optimizer_factory',
    'create_data_processor',
    'create_metrics_calculator',
    'create_checkpoint_manager',
    'create_experiment_tracker',
    'is_valid_learning_rate',
    'is_valid_batch_size',
    'is_valid_model_type',
    'should_normalize_data',
    'can_use_mixed_precision',
    'validate_config_inputs',
    'validate_model_inputs',
    'validate_data_inputs',
    'create_health_check_route',
    'create_model_info_route',
    'create_training_status_route'
]
```

### 2. **Configuration Management with Named Exports**

```python
# config_management_exports.py
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Callable

@dataclass
class ModelConfig:
    """Model configuration using dataclass."""
    model_type: str
    hidden_size: int = 768
    num_layers: int = 12
    num_heads: int = 12
    dropout: float = 0.1
    activation: str = "gelu"
    is_transformer: bool = True
    has_attention: bool = True

@dataclass
class TrainingConfig:
    """Training configuration using dataclass."""
    batch_size: int = 32
    learning_rate: float = 1e-4
    epochs: int = 100
    optimizer: str = "adamw"
    scheduler: str = "cosine"
    gradient_clip: float = 1.0
    is_mixed_precision: bool = True
    should_use_early_stopping: bool = True
    has_gradient_accumulation: bool = False

# Named exports for configuration creation
def create_default_config() -> Dict[str, Any]:
    """Create default configuration dictionary."""
    return {
        "model": ModelConfig("transformer"),
        "training": TrainingConfig(),
        "data": DataConfig(),
        "logging": {"level": "INFO", "save_dir": "logs"},
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "is_debug_mode": False,
        "should_save_checkpoints": True,
        "has_experiment_tracking": True
    }

def create_training_config(learning_rate: float = 1e-4, 
                          batch_size: int = 32,
                          epochs: int = 100,
                          is_mixed_precision: bool = True,
                          should_use_early_stopping: bool = True) -> TrainingConfig:
    """Create training config with common defaults."""
    return TrainingConfig(
        learning_rate=learning_rate,
        batch_size=batch_size,
        epochs=epochs,
        is_mixed_precision=is_mixed_precision,
        should_use_early_stopping=should_use_early_stopping
    )

def create_model_config(model_type: str = "transformer",
                       hidden_size: int = 768,
                       num_layers: int = 12,
                       is_transformer: bool = True,
                       has_attention: bool = True) -> ModelConfig:
    """Create model config with common defaults."""
    return ModelConfig(
        model_type=model_type,
        hidden_size=hidden_size,
        num_layers=num_layers,
        is_transformer=is_transformer,
        has_attention=has_attention
    )

# Named exports for configuration loading and saving
def load_config_from_yaml(file_path: str) -> Result[Dict[str, Any]]:
    """Load configuration from YAML file with error handling."""
    def _load_yaml(path: str) -> Dict[str, Any]:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    return safe_execute(_load_yaml, file_path).flat_map(
        lambda config_dict: safe_execute(merge_configs, create_default_config(), config_dict)
    )

def load_config_from_json(file_path: str) -> Result[Dict[str, Any]]:
    """Load configuration from JSON file with error handling."""
    def _load_json(path: str) -> Dict[str, Any]:
        with open(path, 'r') as f:
            return json.load(f)
    
    return safe_execute(_load_json, file_path).flat_map(
        lambda config_dict: safe_execute(merge_configs, create_default_config(), config_dict)
    )

def save_config_to_yaml(config: Dict[str, Any], file_path: str) -> Result[None]:
    """Save configuration to YAML file with error handling."""
    def _save_yaml() -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    return safe_execute(_save_yaml)

def save_config_to_json(config: Dict[str, Any], file_path: str) -> Result[None]:
    """Save configuration to JSON file with error handling."""
    def _save_json() -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
    
    return safe_execute(_save_json)

# Named exports for configuration manipulation
def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two configuration dictionaries recursively."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result

@memoize
def get_config_value(config: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get configuration value using dot notation path with memoization."""
    keys = path.split('.')
    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def set_config_value(config: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
    """Set configuration value using dot notation path."""
    keys = path.split('.')
    result = config.copy()
    current = result
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return result

def update_config_section(config: Dict[str, Any], section: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update a specific configuration section."""
    result = config.copy()
    if section not in result:
        result[section] = {}
    result[section].update(updates)
    return result

# Named exports for configuration validation
def validate_config(config: Dict[str, Any]) -> Result[List[str]]:
    """Validate configuration and return Result with errors."""
    config_validator = create_config_validator()
    errors = config_validator(config)
    
    # Additional custom validations with descriptive names
    model_config = config.get("model", {})
    if not isinstance(model_config.get("hidden_size"), int):
        errors.append("hidden_size must be an integer")
    
    training_config = config.get("training", {})
    if training_config.get("learning_rate", 0) <= 0:
        errors.append("learning_rate must be positive")
    
    # Check if required paths exist
    data_config = config.get("data", {})
    if data_config.get("train_path") and not Path(data_config["train_path"]).exists():
        errors.append("train_path does not exist")
    
    if errors:
        return Result.failure(f"Configuration validation failed: {errors}")
    return Result.success(errors)

def validate_training_config(config: Dict[str, Any]) -> Result[List[str]]:
    """Validate training configuration specifically."""
    errors = []
    training = config.get("training", {})
    
    if not is_valid_learning_rate(training.get("learning_rate", 0)):
        errors.append("Learning rate must be between 0 and 1")
    
    if not is_valid_batch_size(training.get("batch_size", 0)):
        errors.append("Batch size must be positive and even")
    
    if training.get("epochs", 0) <= 0:
        errors.append("Epochs must be positive")
    
    if errors:
        return Result.failure(f"Training configuration validation failed: {errors}")
    return Result.success(errors)

def validate_model_config(config: Dict[str, Any]) -> Result[List[str]]:
    """Validate model configuration specifically."""
    errors = []
    model = config.get("model", {})
    
    if not is_valid_model_type(model.get("model_type", "")):
        errors.append("Invalid model type")
    
    if model.get("hidden_size", 0) <= 0:
        errors.append("Hidden size must be positive")
    
    if model.get("num_layers", 0) <= 0:
        errors.append("Number of layers must be positive")
    
    if errors:
        return Result.failure(f"Model configuration validation failed: {errors}")
    return Result.success(errors)

# Named exports for configuration validation helpers
def is_valid_learning_rate(learning_rate: float) -> bool:
    """Check if learning rate is valid."""
    return 0 < learning_rate < 1

def is_valid_batch_size(batch_size: int) -> bool:
    """Check if batch size is valid."""
    return batch_size > 0 and batch_size % 2 == 0

def is_valid_model_type(model_type: str) -> bool:
    """Check if model type is valid."""
    valid_types = ["transformer", "cnn", "rnn", "mlp"]
    return model_type in valid_types

def is_valid_device(device: str) -> bool:
    """Check if device is valid."""
    valid_devices = ["cpu", "cuda", "auto"]
    return device in valid_devices

# Named exports for configuration pipelines
def create_config_pipeline() -> Callable[[Optional[str]], Result[Dict[str, Any]]]:
    """Create a config pipeline that handles loading, validation, and merging."""
    def load_and_validate_config(config_path: Optional[str] = None) -> Result[Dict[str, Any]]:
        # Load config
        if config_path and Path(config_path).exists():
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config_result = load_config_from_yaml(config_path)
            elif config_path.endswith('.json'):
                config_result = load_config_from_json(config_path)
            else:
                config_result = load_config_from_yaml(config_path)
        else:
            config_result = Result.success(create_default_config())
        
        # Validate config
        return config_result.flat_map(
            lambda config: validate_config(config).map(lambda _: config)
        )
    
    return load_and_validate_config

def create_config_updater() -> Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]:
    """Create a config updater that safely merges new values."""
    def update_config(config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        return merge_configs(config, updates)
    
    return update_config

def create_config_serializer() -> Callable[[Dict[str, Any], str], Result[str]]:
    """Create a config serializer that handles different formats."""
    def serialize_config(config: Dict[str, Any], format_type: str) -> Result[str]:
        def _serialize() -> str:
            if format_type == "yaml":
                return yaml.dump(config, default_flow_style=False)
            elif format_type == "json":
                return json.dumps(config, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
        
        return safe_execute(_serialize)
    
    return serialize_config

# Named exports for configuration routes (if this were a web framework)
def create_config_info_route() -> Callable:
    """Create config info route handler."""
    def config_info(config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "model_type": config.get("model", {}).get("model_type", "unknown"),
            "learning_rate": config.get("training", {}).get("learning_rate", 0.0),
            "batch_size": config.get("training", {}).get("batch_size", 0),
            "epochs": config.get("training", {}).get("epochs", 0),
            "device": config.get("device", "cpu"),
            "is_debug_mode": config.get("is_debug_mode", False),
            "should_save_checkpoints": config.get("should_save_checkpoints", True)
        }
    return config_info

def create_config_validation_route() -> Callable:
    """Create config validation route handler."""
    def validate_config_route(config: Dict[str, Any]) -> Dict[str, Any]:
        validation_result = validate_config(config)
        return {
            "is_valid": validation_result.is_successful,
            "errors": validation_result.error if not validation_result.is_successful else []
        }
    return validate_config_route

def create_config_update_route() -> Callable:
    """Create config update route handler."""
    def update_config_route(config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        updated_config = merge_configs(config, updates)
        validation_result = validate_config(updated_config)
        
        return {
            "is_valid": validation_result.is_successful,
            "config": updated_config if validation_result.is_successful else config,
            "errors": validation_result.error if not validation_result.is_successful else []
        }
    return update_config_route

# Export all named functions and classes
__all__ = [
    # Configuration classes
    'ModelConfig',
    'TrainingConfig', 
    'DataConfig',
    
    # Configuration creation
    'create_default_config',
    'create_training_config',
    'create_model_config',
    'create_data_config',
    'create_debug_config',
    'create_production_config',
    
    # Configuration loading and saving
    'load_config_from_yaml',
    'load_config_from_json',
    'save_config_to_yaml',
    'save_config_to_json',
    
    # Configuration manipulation
    'merge_configs',
    'get_config_value',
    'set_config_value',
    'update_config_section',
    
    # Configuration validation
    'validate_config',
    'validate_training_config',
    'validate_model_config',
    
    # Validation helpers
    'is_valid_learning_rate',
    'is_valid_batch_size',
    'is_valid_model_type',
    'is_valid_device',
    
    # Configuration pipelines
    'create_config_pipeline',
    'create_config_updater',
    'create_config_serializer',
    
    # Configuration routes
    'create_config_info_route',
    'create_config_validation_route',
    'create_config_update_route'
]
```

## Route Handler Factory Pattern

### 1. **Health Check Route**

```python
def create_health_check_route() -> Callable:
    """Create health check route handler."""
    def health_check() -> Dict[str, Any]:
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0"
        }
    return health_check
```

### 2. **Model Info Route**

```python
def create_model_info_route() -> Callable:
    """Create model info route handler."""
    def model_info(model: nn.Module) -> Dict[str, Any]:
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        return {
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "model_type": type(model).__name__,
            "device": next(model.parameters()).device
        }
    return model_info
```

### 3. **Training Status Route**

```python
def create_training_status_route() -> Callable:
    """Create training status route handler."""
    def training_status(history: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not history:
            return {"status": "not_started"}
        
        latest = history[-1]
        return {
            "status": "training",
            "current_epoch": latest.get("epoch", 0),
            "current_loss": latest.get("loss", 0.0),
            "current_accuracy": latest.get("accuracy", 0.0),
            "total_epochs": len(history)
        }
    return training_status
```

## Usage Examples

### 1. **Importing Named Exports**

```python
# Import specific functions
from functional_utils_exports import (
    safe_execute,
    compose,
    pipe,
    create_logger,
    create_device_manager,
    create_metric_tracker
)

# Import configuration functions
from config_management_exports import (
    create_default_config,
    load_config_from_yaml,
    validate_config,
    get_config_value,
    create_config_pipeline
)

# Import route handlers
from functional_utils_exports import (
    create_health_check_route,
    create_model_info_route,
    create_training_status_route
)
```

### 2. **Using Named Exports**

```python
# Create utilities
logger = create_logger("my_app")
device_manager = create_device_manager()
metric_tracker = create_metric_tracker()

# Use functional composition
process_pipeline = compose(
    lambda x: x * 2,
    lambda x: x + 1,
    lambda x: x ** 2
)

result = process_pipeline(5)
print(f"Pipeline result: {result}")

# Use pipe operator
result = pipe(5, lambda x: x * 2, lambda x: x + 1, lambda x: x ** 2)
print(f"Pipe result: {result}")

# Use Result type for error handling
safe_result = safe_execute(lambda x: x / 0, 10)
if not safe_result.is_successful:
    print(f"Error: {safe_result.error}")
```

### 3. **Configuration Management**

```python
# Create config pipeline
config_pipeline = create_config_pipeline()

# Load and validate config
config_result = config_pipeline("config.yaml")

if config_result.is_successful:
    config = config_result.value
    print("Configuration loaded successfully")
    
    # Get config values with descriptive names
    learning_rate = get_config_value(config, "training.learning_rate", 1e-4)
    hidden_size = get_config_value(config, "model.hidden_size", 768)
    is_debug_mode = get_config_value(config, "is_debug_mode", False)
    should_save_checkpoints = get_config_value(config, "should_save_checkpoints", True)
    
    print(f"Learning rate: {learning_rate}")
    print(f"Hidden size: {hidden_size}")
    print(f"Is debug mode: {is_debug_mode}")
    print(f"Should save checkpoints: {should_save_checkpoints}")
else:
    print(f"Configuration error: {config_result.error}")
```

### 4. **Route Handler Usage**

```python
# Create route handlers
health_check_route = create_health_check_route()
model_info_route = create_model_info_route()
training_status_route = create_training_status_route()

# Use route handlers
health_status = health_check_route()
print(f"Health status: {health_status}")

model_info = model_info_route(model)
print(f"Model info: {model_info}")

training_status = training_status_route(history)
print(f"Training status: {training_status}")
```

## Benefits of Named Exports

### 1. **Better Tree Shaking**
- Only import what you need
- Reduce bundle size in web applications
- Improve performance

### 2. **Explicit Dependencies**
- Clear what functions are available
- Easy to see what's being imported
- Better code documentation

### 3. **Improved IDE Support**
- Better autocomplete
- Easier refactoring
- Clear function signatures

### 4. **Testing and Mocking**
- Easy to mock specific functions
- Better unit testing
- Clear test dependencies

### 5. **Code Organization**
- Logical grouping of functions
- Clear separation of concerns
- Better maintainability

## Best Practices

### 1. **Use Descriptive Names**
```python
# Good
def create_model_factory() -> Callable:
    pass

def validate_config_inputs() -> Callable:
    pass

# Avoid
def factory() -> Callable:
    pass

def validate() -> Callable:
    pass
```

### 2. **Group Related Functions**
```python
# Configuration functions
def create_default_config() -> Dict[str, Any]:
    pass

def load_config_from_yaml(file_path: str) -> Result[Dict[str, Any]]:
    pass

def save_config_to_yaml(config: Dict[str, Any], file_path: str) -> Result[None]:
    pass

# Validation functions
def validate_config(config: Dict[str, Any]) -> Result[List[str]]:
    pass

def validate_training_config(config: Dict[str, Any]) -> Result[List[str]]:
    pass

def validate_model_config(config: Dict[str, Any]) -> Result[List[str]]:
    pass
```

### 3. **Use Factory Pattern for Routes**
```python
def create_route_handler(dependencies: Dict[str, Any]) -> Callable:
    """Create route handler with dependencies."""
    def route_handler(request: Dict[str, Any]) -> Dict[str, Any]:
        # Use dependencies here
        return {"result": "success"}
    return route_handler
```

### 4. **Explicit `__all__` Declarations**
```python
__all__ = [
    # Core utilities
    'safe_execute',
    'compose',
    'pipe',
    
    # Configuration management
    'create_default_config',
    'load_config_from_yaml',
    'validate_config',
    
    # Route handlers
    'create_health_check_route',
    'create_model_info_route',
    'create_training_status_route'
]
```

## Migration Guide

### **Step 1: Convert Default Exports to Named Exports**
```python
# Before
def main_function():
    pass

# After
def create_main_function():
    pass

__all__ = ['create_main_function']
```

### **Step 2: Update Imports**
```python
# Before
from module import main_function

# After
from module import create_main_function
```

### **Step 3: Use Factory Pattern for Routes**
```python
# Before
def route_handler(request):
    pass

# After
def create_route_handler(dependencies):
    def route_handler(request):
        # Use dependencies
        pass
    return route_handler
```

### **Step 4: Add `__all__` Declarations**
```python
__all__ = [
    'create_main_function',
    'create_route_handler',
    'validate_inputs'
]
```

## Conclusion

The named exports approach provides:

- **Better code organization** through explicit exports
- **Improved maintainability** with clear function boundaries
- **Enhanced testing** with easy mocking and dependency injection
- **Better IDE support** with clear function signatures
- **Reduced bundle sizes** through tree shaking
- **Clearer dependencies** with explicit imports

This approach follows modern JavaScript/TypeScript best practices and makes the codebase more professional, maintainable, and easier to understand for both current and future developers. 