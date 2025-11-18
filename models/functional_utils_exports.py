from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Callable, Union, TypeVar, Generic
from functools import wraps, partial, reduce
from dataclasses import dataclass
import time
import logging
from typing import Any, List, Dict, Optional
import asyncio
"""
Functional Utilities with Named Exports
Favors named exports for routes and utility functions
"""


# Type variables for generic functions
T = TypeVar('T')
U = TypeVar('U')

@dataclass
class Result(Generic[T]):
    """Immutable result container for functional error handling."""
    value: Optional[T] = None
    error: Optional[str] = None
    is_successful: bool: bool = True
    
    @classmethod
    def success(cls, value: T) -> 'Result[T]':
        return cls(value=value, is_successful=True)
    
    @classmethod
    def failure(cls, error: str) -> 'Result[T]':
        return cls(error=error, is_successful=False)
    
    def map(self, func: Callable[[T], U]) -> 'Result[U]':
        """Apply function to value if successful."""
        if self.is_successful and self.value is not None:
            try:
                return Result.success(func(self.value))
            except Exception as e:
                return Result.failure(str(e))
        return Result.failure(self.error or "No value to map")
    
    def flat_map(self, func: Callable[[T], 'Result[U]']) -> 'Result[U]':
        """Apply function that returns Result."""
        if self.is_successful and self.value is not None:
            return func(self.value)
        return Result.failure(self.error or "No value to flat_map")

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
    results: List[Any] = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results: List[Any] = [processor(item) for item in batch]
        results.extend(batch_results)
    return results

def retry(max_attempts: int = 3, delay: float = 1.0) -> Any:
    """Decorator for retrying failed operations."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
            raise last_exception
        return wrapper
    return decorator

def memoize(func: Callable[..., T]) -> Callable[..., T]:
    """Memoize function results to avoid recomputation."""
    cache: Dict[str, Any] = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper

# Named exports for logging utilities
def create_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Create standardized logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def validate_inputs(*validators: Callable[[Any], bool], 
                   error_msg: str: str: str = "Validation failed") -> Callable:
    """Decorator for input validation."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for validator in validators:
                if not validator(args):
                    raise ValueError(error_msg)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Named exports for device management
def create_device_manager() -> Callable[[str], torch.device]:
    """Create device manager function."""
    def get_device(device_name: str: str: str = "auto") -> torch.device:
        match device_name:
    case "auto":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return torch.device(device_name)
    return get_device

# Named exports for metric tracking
def create_metric_tracker() -> Callable[[str, float], None]:
    """Create metric tracking function."""
    metrics: Dict[str, Any] = {}
    
    def track_metric(name: str, value: float) -> None:
        if name not in metrics:
            metrics[name] = []
        metrics[name].append(value)
    
    track_metric.get_metrics = lambda: metrics.copy()
    track_metric.get_latest = lambda name: metrics.get(name, [])[-1] if metrics.get(name) else None
    
    return track_metric

# Named exports for configuration management
def create_config_validator() -> Callable[[Dict[str, Any]], List[str]]:
    """Create configuration validator."""
    def validate_config(config: Dict[str, Any]) -> List[str]:
        errors: List[Any] = []
        
        # Validate required keys
        required_keys: List[Any] = ['model', 'training', 'data']
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
        
        return errors
    
    return validate_config

# Named exports for model factories
def create_model_factory() -> Callable[[str, Dict[str, Any]], nn.Module]:
    """Create model factory function."""
    model_registry: Dict[str, Any] = {}
    
    def register_model(name: str, creator: Callable[[Dict[str, Any]], nn.Module]) -> None:
        model_registry[name] = creator
    
    def create_model(model_type: str, config: Dict[str, Any]) -> nn.Module:
        if model_type not in model_registry:
            raise ValueError(f"Unknown model type: {model_type}")
        return model_registry[model_type](config)
    
    create_model.register = register_model
    return create_model

def create_optimizer_factory() -> Callable[[str, nn.Module, Dict[str, Any]], torch.optim.Optimizer]:
    """Create optimizer factory function."""
    optimizer_registry: Dict[str, Any] = {}
    
    def register_optimizer(name: str, creator: Callable[[nn.Module, Dict[str, Any]], torch.optim.Optimizer]) -> None:
        optimizer_registry[name] = creator
    
    def create_optimizer(optimizer_type: str, model: nn.Module, config: Dict[str, Any]) -> torch.optim.Optimizer:
        if optimizer_type not in optimizer_registry:
            raise ValueError(f"Unknown optimizer type: {optimizer_type}")
        return optimizer_registry[optimizer_type](model, config)
    
    create_optimizer.register = register_optimizer
    return create_optimizer

# Named exports for data processing
def create_data_processor() -> Callable[[np.ndarray, Dict[str, Any]], np.ndarray]:
    """Create data processor function."""
    def process_data(data: np.ndarray, config: Dict[str, Any]) -> np.ndarray:
        processed = data.copy()
        
        # Apply normalization if specified
        if config.get('should_normalize', True):
            processed = (processed - processed.mean()) / (processed.std() + 1e-8)
        
        # Apply scaling if specified
        if 'scale_factor' in config:
            processed *= config['scale_factor']
        
        return processed
    
    return process_data

# Named exports for metrics calculation
def create_metrics_calculator() -> Callable[[torch.Tensor, torch.Tensor], Dict[str, float]]:
    """Create metrics calculator function."""
    def calculate_metrics(predictions: torch.Tensor, targets: torch.Tensor) -> Dict[str, float]:
        metrics: Dict[str, Any] = {}
        
        # Accuracy
        if len(predictions.shape) > 1:
            accuracy = (predictions.argmax(dim=1) == targets).float().mean().item()
        else:
            accuracy = ((predictions > 0.5) == targets).float().mean().item()
        metrics['accuracy'] = accuracy
        
        # Loss (assuming cross entropy for classification)
        if len(predictions.shape) > 1:
            loss = nn.CrossEntropyLoss()(predictions, targets).item()
        else:
            loss = nn.BCEWithLogitsLoss()(predictions, targets.float()).item()
        metrics['loss'] = loss
        
        return metrics
    
    return calculate_metrics

# Named exports for checkpoint management
def create_checkpoint_manager() -> Callable[[str, Dict[str, Any]], None]:
    """Create checkpoint manager function."""
    def save_checkpoint(filepath: str, data: Dict[str, Any]) -> None:
        torch.save(data, filepath)
    
    def load_checkpoint(filepath: str) -> Dict[str, Any]:
        return torch.load(filepath)
    
    save_checkpoint.load = load_checkpoint
    return save_checkpoint

# Named exports for experiment tracking
def create_experiment_tracker() -> Callable[[str, Dict[str, Any]], None]:
    """Create experiment tracking function."""
    experiments: Dict[str, Any] = {}
    
    def track_experiment(name: str, data: Dict[str, Any]) -> None:
        experiments[name] = {
            'timestamp': time.time(),
            'data': data
        }
    
    def get_experiment(name: str) -> Optional[Dict[str, Any]]:
        return experiments.get(name)
    
    def list_experiments() -> List[str]:
        return list(experiments.keys())
    
    track_experiment.get = get_experiment
    track_experiment.list = list_experiments
    return track_experiment

# Named exports for validation helpers
def is_valid_learning_rate(learning_rate: float) -> bool:
    """Check if learning rate is valid."""
    return 0 < learning_rate < 1

def is_valid_batch_size(batch_size: int) -> bool:
    """Check if batch size is valid."""
    return batch_size > 0 and batch_size % 2 == 0

def is_valid_model_type(model_type: str) -> bool:
    """Check if model type is valid."""
    valid_types: List[Any] = ["transformer", "cnn", "rnn", "mlp"]
    return model_type in valid_types

def should_normalize_data(data_config: Dict[str, Any]) -> bool:
    """Determine if data should be normalized."""
    return data_config.get("should_normalize", True)

def can_use_mixed_precision(device: str, config: Dict[str, Any]) -> bool:
    """Check if mixed precision can be used."""
    return (device == "cuda" and 
            config.get("is_mixed_precision", False) and 
            torch.cuda.is_available())

# Named exports for utility decorators
def validate_config_inputs(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to validate config inputs."""
    @wraps(func)
    def wrapper(config: Dict[str, Any], *args, **kwargs) -> T:
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
        if 'training' not in config:
            raise ValueError("Config must contain 'training' section")
        return func(config, *args, **kwargs)
    return wrapper

def validate_model_inputs(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to validate model inputs."""
    @wraps(func)
    def wrapper(model: nn.Module, *args, **kwargs) -> T:
        if not isinstance(model, nn.Module):
            raise ValueError("Model must be a torch.nn.Module")
        return func(model, *args, **kwargs)
    return wrapper

def validate_data_inputs(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to validate data inputs."""
    @wraps(func)
    def wrapper(data: torch.Tensor, *args, **kwargs) -> T:
        if not isinstance(data, torch.Tensor):
            raise ValueError("Data must be a torch.Tensor")
        return func(data, *args, **kwargs)
    return wrapper

# Named exports for route handlers (if this were a web framework)
def create_health_check_route() -> Callable:
    """Create health check route handler."""
    def health_check() -> Dict[str, Any]:
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0"
        }
    return health_check

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

# Export all named functions and classes
__all__: List[Any] = [
    # Core utilities
    'Result',
    'safe_execute',
    'compose',
    'pipe',
    'batch_process',
    'retry',
    'memoize',
    
    # Logging utilities
    'create_logger',
    'validate_inputs',
    
    # Device management
    'create_device_manager',
    
    # Metric tracking
    'create_metric_tracker',
    
    # Configuration management
    'create_config_validator',
    
    # Model factories
    'create_model_factory',
    'create_optimizer_factory',
    
    # Data processing
    'create_data_processor',
    
    # Metrics calculation
    'create_metrics_calculator',
    
    # Checkpoint management
    'create_checkpoint_manager',
    
    # Experiment tracking
    'create_experiment_tracker',
    
    # Validation helpers
    'is_valid_learning_rate',
    'is_valid_batch_size',
    'is_valid_model_type',
    'should_normalize_data',
    'can_use_mixed_precision',
    
    # Utility decorators
    'validate_config_inputs',
    'validate_model_inputs',
    'validate_data_inputs',
    
    # Route handlers
    'create_health_check_route',
    'create_model_info_route',
    'create_training_status_route'
]

# Usage examples
if __name__ == "__main__":
    # Example usage of named exports
    logger = create_logger("test")
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
    
    # Use retry decorator
    @retry(max_attempts=3)
    def unreliable_function() -> Any:
        
    """unreliable_function function."""
if torch.rand(1).item() > 0.5:
            raise ValueError("Random failure")
        return "Success"
    
    try:
        result = unreliable_function()
        print(f"Retry result: {result}")
    except Exception as e:
        print(f"Failed after retries: {e}") 