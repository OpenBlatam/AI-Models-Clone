# RORO (Receive an Object, Return an Object) Pattern Implementation

## Overview

This document explains how the framework has been refactored to use the **RORO (Receive an Object, Return an Object)** pattern, a modern JavaScript/TypeScript pattern that improves function signatures, maintainability, and code organization.

## What is RORO Pattern?

The **RORO pattern** is a function signature pattern where:
- **Receive an Object**: Functions receive a single object parameter containing all inputs
- **Return an Object**: Functions return a single object containing all outputs and status information

### Benefits of RORO Pattern

1. **Improved Function Signatures**: Single object parameter instead of multiple parameters
2. **Better Maintainability**: Easy to add/remove parameters without breaking existing code
3. **Consistent Error Handling**: All functions return objects with success/error status
4. **Self-Documenting**: Parameter names are explicit in the object
5. **Extensible**: Easy to add new parameters without changing function signatures
6. **Type Safety**: Better TypeScript/type hinting support

## RORO Pattern Examples

### 1. **Core Utilities with RORO Pattern**

```python
# roro_pattern_utils.py

def safe_execute_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Safely execute function and return result object."""
    func = params.get('func')
    args = params.get('args', [])
    kwargs = params.get('kwargs', {})
    
    try:
        result = func(*args, **kwargs)
        return {
            'is_successful': True,
            'result': result,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def compose_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Compose multiple functions using RORO pattern."""
    functions = params.get('functions', [])
    
    if not functions:
        return {
            'is_successful': False,
            'result': None,
            'error': 'No functions provided'
        }
    
    try:
        composed = reduce(lambda f, g: lambda x: f(g(x)), functions)
        return {
            'is_successful': True,
            'result': composed,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def pipe_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Pipe value through multiple functions using RORO pattern."""
    value = params.get('value')
    functions = params.get('functions', [])
    
    if not functions:
        return {
            'is_successful': False,
            'result': None,
            'error': 'No functions provided'
        }
    
    try:
        result = reduce(lambda acc, f: f(acc), functions, value)
        return {
            'is_successful': True,
            'result': result,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def retry_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Retry function with exponential backoff using RORO pattern."""
    func = params.get('func')
    args = params.get('args', [])
    kwargs = params.get('kwargs', {})
    max_attempts = params.get('max_attempts', 3)
    delay = params.get('delay', 1.0)
    
    if not func:
        return {
            'is_successful': False,
            'result': None,
            'error': 'No function provided'
        }
    
    last_exception = None
    for attempt in range(max_attempts):
        try:
            result = func(*args, **kwargs)
            return {
                'is_successful': True,
                'result': result,
                'error': None,
                'attempts': attempt + 1
            }
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
    
    return {
        'is_successful': False,
        'result': None,
        'error': str(last_exception),
        'attempts': max_attempts
    }
```

### 2. **Configuration Management with RORO Pattern**

```python
# config_management_roro.py

def create_default_config_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create default configuration dictionary using RORO pattern."""
    try:
        config = {
            "model": ModelConfig("transformer"),
            "training": TrainingConfig(),
            "data": DataConfig(),
            "logging": {"level": "INFO", "save_dir": "logs"},
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "is_debug_mode": False,
            "should_save_checkpoints": True,
            "has_experiment_tracking": True
        }
        
        return {
            'is_successful': True,
            'result': config,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def create_training_config_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create training config with common defaults using RORO pattern."""
    try:
        learning_rate = params.get('learning_rate', 1e-4)
        batch_size = params.get('batch_size', 32)
        epochs = params.get('epochs', 100)
        is_mixed_precision = params.get('is_mixed_precision', True)
        should_use_early_stopping = params.get('should_use_early_stopping', True)
        
        config = TrainingConfig(
            learning_rate=learning_rate,
            batch_size=batch_size,
            epochs=epochs,
            is_mixed_precision=is_mixed_precision,
            should_use_early_stopping=should_use_early_stopping
        )
        
        return {
            'is_successful': True,
            'result': config,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def load_config_from_yaml_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Load configuration from YAML file with error handling using RORO pattern."""
    file_path = params.get('file_path')
    
    if not file_path:
        return {
            'is_successful': False,
            'result': None,
            'error': 'No file path provided'
        }
    
    def _load_yaml(path: str) -> Dict[str, Any]:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    load_result = safe_execute_roro({
        'func': _load_yaml,
        'args': [file_path]
    })
    
    if not load_result['is_successful']:
        return load_result
    
    # Merge with default config
    default_result = create_default_config_roro({})
    if not default_result['is_successful']:
        return default_result
    
    merge_result = merge_configs_roro({
        'base': default_result['result'],
        'override': load_result['result']
    })
    
    return merge_result

def validate_config_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate configuration and return result object using RORO pattern."""
    config = params.get('config', {})
    
    try:
        errors = []
        
        # Validate required keys
        required_keys = ['model', 'training', 'data']
        for key in required_keys:
            if key not in config:
                errors.append(f"Missing required key: {key}")
        
        # Validate training config
        if 'training' in config:
            training = config['training']
            if training.get('learning_rate', 0) <= 0:
                errors.append("Learning rate must be positive")
            if training.get('batch_size', 0) <= 0:
                errors.append("Batch size must be positive")
        
        # Check if required paths exist
        data_config = config.get('data', {})
        if data_config.get('train_path') and not Path(data_config["train_path"]).exists():
            errors.append("train_path does not exist")
        
        if errors:
            return {
                'is_successful': False,
                'result': None,
                'error': f"Configuration validation failed: {errors}"
            }
        
        return {
            'is_successful': True,
            'result': errors,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }
```

### 3. **Factory Functions with RORO Pattern**

```python
def create_logger_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create standardized logger using RORO pattern."""
    name = params.get('name', 'default')
    level = params.get('level', logging.INFO)
    
    try:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return {
            'is_successful': True,
            'result': logger,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def create_device_manager_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create device manager using RORO pattern."""
    try:
        def get_device(device_name: str = "auto") -> torch.device:
            if device_name == "auto":
                return torch.device("cuda" if torch.cuda.is_available() else "cpu")
            return torch.device(device_name)
        
        return {
            'is_successful': True,
            'result': get_device,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def create_metric_tracker_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create metric tracker using RORO pattern."""
    try:
        metrics = {}
        
        def track_metric(name: str, value: float) -> None:
            if name not in metrics:
                metrics[name] = []
            metrics[name].append(value)
        
        track_metric.get_metrics = lambda: metrics.copy()
        track_metric.get_latest = lambda name: metrics.get(name, [])[-1] if metrics.get(name) else None
        
        return {
            'is_successful': True,
            'result': track_metric,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }
```

### 4. **Validation Functions with RORO Pattern**

```python
def is_valid_learning_rate_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Check if learning rate is valid using RORO pattern."""
    learning_rate = params.get('learning_rate', 0)
    is_valid = 0 < learning_rate < 1
    
    return {
        'is_successful': True,
        'result': is_valid,
        'error': None
    }

def is_valid_batch_size_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Check if batch size is valid using RORO pattern."""
    batch_size = params.get('batch_size', 0)
    is_valid = batch_size > 0 and batch_size % 2 == 0
    
    return {
        'is_successful': True,
        'result': is_valid,
        'error': None
    }

def is_valid_model_type_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Check if model type is valid using RORO pattern."""
    model_type = params.get('model_type', '')
    valid_types = ["transformer", "cnn", "rnn", "mlp"]
    is_valid = model_type in valid_types
    
    return {
        'is_successful': True,
        'result': is_valid,
        'error': None
    }
```

### 5. **Route Handlers with RORO Pattern**

```python
def create_health_check_route_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create health check route handler using RORO pattern."""
    try:
        def health_check() -> Dict[str, Any]:
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "version": "1.0.0"
            }
        
        return {
            'is_successful': True,
            'result': health_check,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def create_model_info_route_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create model info route handler using RORO pattern."""
    try:
        def model_info(model: nn.Module) -> Dict[str, Any]:
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            
            return {
                "total_parameters": total_params,
                "trainable_parameters": trainable_params,
                "model_type": type(model).__name__,
                "device": next(model.parameters()).device
            }
        
        return {
            'is_successful': True,
            'result': model_info,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }
```

## Usage Examples

### 1. **Using RORO Pattern Functions**

```python
# Import RORO functions
from roro_pattern_utils import (
    safe_execute_roro,
    compose_roro,
    pipe_roro,
    retry_roro,
    create_logger_roro,
    create_device_manager_roro,
    create_metric_tracker_roro
)

from config_management_roro import (
    create_default_config_roro,
    load_config_from_yaml_roro,
    validate_config_roro,
    get_config_value_roro,
    create_config_pipeline_roro
)

# Create utilities using RORO pattern
logger_result = create_logger_roro({
    'name': 'my_app',
    'level': logging.INFO
})

if logger_result['is_successful']:
    logger = logger_result['result']
    logger.info("Logger created successfully")
else:
    print(f"Logger creation failed: {logger_result['error']}")

# Create device manager using RORO pattern
device_manager_result = create_device_manager_roro({})

if device_manager_result['is_successful']:
    device_manager = device_manager_result['result']
    device = device_manager('auto')
    print(f"Device: {device}")

# Use functional composition with RORO pattern
compose_result = compose_roro({
    'functions': [
        lambda x: x * 2,
        lambda x: x + 1,
        lambda x: x ** 2
    ]
})

if compose_result['is_successful']:
    process_pipeline = compose_result['result']
    result = process_pipeline(5)
    print(f"Pipeline result: {result}")

# Use pipe operator with RORO pattern
pipe_result = pipe_roro({
    'value': 5,
    'functions': [
        lambda x: x * 2,
        lambda x: x + 1,
        lambda x: x ** 2
    ]
})

if pipe_result['is_successful']:
    result = pipe_result['result']
    print(f"Pipe result: {result}")

# Use safe execute with RORO pattern
safe_result = safe_execute_roro({
    'func': lambda x: x / 0,
    'args': [10]
})

if not safe_result['is_successful']:
    print(f"Error: {safe_result['error']}")

# Use retry with RORO pattern
retry_result = retry_roro({
    'func': lambda: 1 / 0 if time.time() % 2 > 1 else "Success",
    'max_attempts': 3,
    'delay': 0.1
})

if retry_result['is_successful']:
    print(f"Retry result: {retry_result['result']}")
else:
    print(f"Retry failed after {retry_result['attempts']} attempts: {retry_result['error']}")
```

### 2. **Configuration Management with RORO Pattern**

```python
# Create config pipeline using RORO pattern
config_pipeline_result = create_config_pipeline_roro({
    'config_path': 'config.yaml'
})

if config_pipeline_result['is_successful']:
    config = config_pipeline_result['result']
    print("Configuration loaded successfully")
    
    # Get config values using RORO pattern
    lr_result = get_config_value_roro({
        'config': config,
        'path': 'training.learning_rate',
        'default': 1e-4
    })
    
    if lr_result['is_successful']:
        learning_rate = lr_result['result']
        print(f"Learning rate: {learning_rate}")
else:
    print(f"Configuration error: {config_pipeline_result['error']}")

# Create specialized configs using RORO pattern
debug_config_result = create_debug_config_roro({
    'is_debug_mode': True,
    'should_save_checkpoints': False,
    'has_experiment_tracking': False
})

if debug_config_result['is_successful']:
    debug_config = debug_config_result['result']
    print(f"Debug config: {debug_config}")

# Validate config using RORO pattern
validation_result = validate_config_roro({
    'config': config
})

if validation_result['is_successful']:
    print("Configuration is valid")
else:
    print(f"Configuration validation failed: {validation_result['error']}")
```

### 3. **Route Handler Usage with RORO Pattern**

```python
# Create route handlers using RORO pattern
health_check_route_result = create_health_check_route_roro({})

if health_check_route_result['is_successful']:
    health_check_route = health_check_route_result['result']
    health_status = health_check_route()
    print(f"Health status: {health_status}")

model_info_route_result = create_model_info_route_roro({})

if model_info_route_result['is_successful']:
    model_info_route = model_info_route_result['result']
    model_info = model_info_route(model)
    print(f"Model info: {model_info}")

training_status_route_result = create_training_status_route_roro({})

if training_status_route_result['is_successful']:
    training_status_route = training_status_route_result['result']
    training_status = training_status_route(history)
    print(f"Training status: {training_status}")
```

## Benefits of RORO Pattern

### 1. **Improved Function Signatures**
```python
# Before (Traditional)
def create_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    pass

# After (RORO Pattern)
def create_logger_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get('name', 'default')
    level = params.get('level', logging.INFO)
    # ... implementation
```

### 2. **Consistent Error Handling**
```python
# All RORO functions return the same structure
{
    'is_successful': True/False,
    'result': actual_result,
    'error': error_message_or_None
}
```

### 3. **Easy Parameter Addition**
```python
# Adding new parameters doesn't break existing code
def create_logger_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get('name', 'default')
    level = params.get('level', logging.INFO)
    # New parameter added without breaking existing calls
    format_string = params.get('format_string', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
```

### 4. **Self-Documenting Code**
```python
# Parameter names are explicit in the object
logger_result = create_logger_roro({
    'name': 'my_app',
    'level': logging.INFO,
    'format_string': '%(asctime)s - %(levelname)s - %(message)s'
})
```

### 5. **Better Type Safety**
```python
# Type hints are clearer
def function_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    # All inputs and outputs are clearly typed
    pass
```

## Migration Guide

### **Step 1: Convert Function Signatures**
```python
# Before
def create_config(learning_rate: float, batch_size: int, epochs: int) -> Dict[str, Any]:
    pass

# After
def create_config_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    learning_rate = params.get('learning_rate', 1e-4)
    batch_size = params.get('batch_size', 32)
    epochs = params.get('epochs', 100)
    # ... implementation
```

### **Step 2: Update Function Calls**
```python
# Before
config = create_config(1e-3, 64, 200)

# After
config_result = create_config_roro({
    'learning_rate': 1e-3,
    'batch_size': 64,
    'epochs': 200
})

if config_result['is_successful']:
    config = config_result['result']
```

### **Step 3: Add Error Handling**
```python
# All RORO functions return consistent error objects
result = some_roro_function(params)

if result['is_successful']:
    # Use result['result']
    pass
else:
    # Handle result['error']
    print(f"Error: {result['error']}")
```

### **Step 4: Update Imports**
```python
# Import RORO functions
from roro_pattern_utils import (
    safe_execute_roro,
    compose_roro,
    pipe_roro,
    retry_roro
)

from config_management_roro import (
    create_default_config_roro,
    load_config_from_yaml_roro,
    validate_config_roro
)
```

## Best Practices

### 1. **Consistent Return Structure**
```python
def roro_function(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Implementation
        return {
            'is_successful': True,
            'result': actual_result,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }
```

### 2. **Use Descriptive Parameter Names**
```python
# Good
logger_result = create_logger_roro({
    'name': 'my_app',
    'level': logging.INFO,
    'format_string': '%(asctime)s - %(levelname)s - %(message)s'
})

# Avoid
logger_result = create_logger_roro({
    'n': 'my_app',
    'l': logging.INFO
})
```

### 3. **Provide Sensible Defaults**
```python
def function_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    # Always provide sensible defaults
    param1 = params.get('param1', 'default_value')
    param2 = params.get('param2', 42)
    param3 = params.get('param3', True)
```

### 4. **Handle Errors Gracefully**
```python
def function_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Implementation
        return {
            'is_successful': True,
            'result': result,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }
```

### 5. **Use Type Hints**
```python
from typing import Dict, Any, Optional

def function_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    # Implementation
    pass
```

## Conclusion

The RORO pattern provides:

- **Better function signatures** with single object parameters
- **Consistent error handling** across all functions
- **Improved maintainability** with easy parameter addition/removal
- **Self-documenting code** with explicit parameter names
- **Better type safety** with clear input/output structures
- **Extensible design** that doesn't break existing code

This pattern follows modern JavaScript/TypeScript best practices and makes the codebase more professional, maintainable, and easier to understand for both current and future developers. 