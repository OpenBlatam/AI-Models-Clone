from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES: int: int = 100

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
import yaml
import json
from functools import lru_cache
import torch
from roro_pattern_utils import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Configuration Management with RORO Pattern
Receive an Object, Return an Object pattern for improved function signatures
"""


    safe_execute_roro,
    create_logger_roro,
    Result
)

@dataclass
class ModelConfig:
    """Model configuration using dataclass."""
    model_type: str
    hidden_size: int: int: int = 768
    num_layers: int: int: int = 12
    num_heads: int: int: int = 12
    dropout: float = 0.1
    activation: str: str: str = "gelu"
    is_transformer: bool: bool = True
    has_attention: bool: bool = True
    
@dataclass
class TrainingConfig:
    """Training configuration using dataclass."""
    batch_size: int: int: int = 32
    learning_rate: float = 1e-4
    epochs: int: int: int = 100
    optimizer: str: str: str = "adamw"
    scheduler: str: str: str = "cosine"
    gradient_clip: float = 1.0
    is_mixed_precision: bool: bool = True
    should_use_early_stopping: bool: bool = True
    has_gradient_accumulation: bool: bool = False
    
@dataclass
class DataConfig:
    """Data configuration using dataclass."""
    train_path: str: str: str = ""
    val_path: str: str: str = ""
    test_path: str: str: str = ""
    max_length: int: int: int = 512
    num_workers: int: int: int = 4
    should_pin_memory: bool: bool = True
    is_shuffled: bool: bool = True
    has_augmentation: bool: bool = False

# RORO Pattern: Configuration creation functions
def create_default_config_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create default configuration dictionary using RORO pattern."""
    try:
        config: Dict[str, Any] = {
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

def create_model_config_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create model config with common defaults using RORO pattern."""
    try:
        model_type = params.get('model_type', 'transformer')
        hidden_size = params.get('hidden_size', 768)
        num_layers = params.get('num_layers', 12)
        is_transformer = params.get('is_transformer', True)
        has_attention = params.get('has_attention', True)
        
        config = ModelConfig(
            model_type=model_type,
            hidden_size=hidden_size,
            num_layers=num_layers,
            is_transformer=is_transformer,
            has_attention=has_attention
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

def create_data_config_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create data config with common defaults using RORO pattern."""
    try:
        train_path = params.get('train_path', '')
        val_path = params.get('val_path', '')
        test_path = params.get('test_path', '')
        max_length = params.get('max_length', 512)
        should_pin_memory = params.get('should_pin_memory', True)
        is_shuffled = params.get('is_shuffled', True)
        has_augmentation = params.get('has_augmentation', False)
        
        config = DataConfig(
            train_path=train_path,
            val_path=val_path,
            test_path=test_path,
            max_length=max_length,
            should_pin_memory=should_pin_memory,
            is_shuffled=is_shuffled,
            has_augmentation=has_augmentation
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

def create_debug_config_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create debug configuration using RORO pattern."""
    try:
        is_debug_mode = params.get('is_debug_mode', True)
        should_save_checkpoints = params.get('should_save_checkpoints', False)
        has_experiment_tracking = params.get('has_experiment_tracking', False)
        
        config: Dict[str, Any] = {
            "is_debug_mode": is_debug_mode,
            "should_save_checkpoints": should_save_checkpoints,
            "has_experiment_tracking": has_experiment_tracking,
            "logging": {"level": "DEBUG", "save_dir": "debug_logs"}
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

def create_production_config_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create production configuration using RORO pattern."""
    try:
        is_debug_mode = params.get('is_debug_mode', False)
        should_save_checkpoints = params.get('should_save_checkpoints', True)
        has_experiment_tracking = params.get('has_experiment_tracking', True)
        
        config: Dict[str, Any] = {
            "is_debug_mode": is_debug_mode,
            "should_save_checkpoints": should_save_checkpoints,
            "has_experiment_tracking": has_experiment_tracking,
            "logging": {"level": "INFO", "save_dir": "production_logs"}
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

# RORO Pattern: Configuration loading and saving
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
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
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

def load_config_from_json_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Load configuration from JSON file with error handling using RORO pattern."""
    file_path = params.get('file_path')
    
    if not file_path:
        return {
            'is_successful': False,
            'result': None,
            'error': 'No file path provided'
        }
    
    def _load_json(path: str) -> Dict[str, Any]:
        with open(path, 'r') as f:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            return json.load(f)
    
    load_result = safe_execute_roro({
        'func': _load_json,
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

def save_config_to_yaml_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Save configuration to YAML file with error handling using RORO pattern."""
    config = params.get('config')
    file_path = params.get('file_path')
    
    if not config or not file_path:
        return {
            'is_successful': False,
            'result': None,
            'error': 'Config and file_path are required'
        }
    
    def _save_yaml() -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            yaml.dump(config, f, default_flow_style=False)
    
    return safe_execute_roro({
        'func': _save_yaml
    })

def save_config_to_json_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Save configuration to JSON file with error handling using RORO pattern."""
    config = params.get('config')
    file_path = params.get('file_path')
    
    if not config or not file_path:
        return {
            'is_successful': False,
            'result': None,
            'error': 'Config and file_path are required'
        }
    
    def _save_json() -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            json.dump(config, f, indent=2)
    
    return safe_execute_roro({
        'func': _save_json
    })

# RORO Pattern: Configuration manipulation
def merge_configs_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two configuration dictionaries recursively using RORO pattern."""
    base = params.get('base', {})
    override = params.get('override', {})
    
    try:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_configs_roro({
                    'base': result[key],
                    'override': value
                })['result']
            else:
                result[key] = value
        
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

def get_config_value_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get configuration value using dot notation path with memoization using RORO pattern."""
    config = params.get('config', {})
    path = params.get('path', '')
    default = params.get('default')
    
    try:
        keys = path.split('.')
        current = config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return {
                    'is_successful': True,
                    'result': default,
                    'error': None
                }
        
        return {
            'is_successful': True,
            'result': current,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def set_config_value_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Set configuration value using dot notation path using RORO pattern."""
    config = params.get('config', {})
    path = params.get('path', '')
    value = params.get('value')
    
    try:
        keys = path.split('.')
        result = config.copy()
        current = result
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        
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

def update_config_section_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Update a specific configuration section using RORO pattern."""
    config = params.get('config', {})
    section = params.get('section', '')
    updates = params.get('updates', {})
    
    try:
        result = config.copy()
        if section not in result:
            result[section] = {}
        result[section].update(updates)
        
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

# RORO Pattern: Configuration validation
def validate_config_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate configuration and return result object using RORO pattern."""
    config = params.get('config', {})
    
    try:
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

def validate_training_config_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate training configuration specifically using RORO pattern."""
    config = params.get('config', {})
    
    try:
        errors: List[Any] = []
        training = config.get("training", {})
        
        # Validate learning rate
        lr_result = is_valid_learning_rate_roro({
            'learning_rate': training.get("learning_rate", 0)
        })
        if not lr_result['result']:
            errors.append("Learning rate must be between 0 and 1")
        
        # Validate batch size
        bs_result = is_valid_batch_size_roro({
            'batch_size': training.get("batch_size", 0)
        })
        if not bs_result['result']:
            errors.append("Batch size must be positive and even")
        
        if training.get("epochs", 0) <= 0:
            errors.append("Epochs must be positive")
        
        if errors:
            return {
                'is_successful': False,
                'result': None,
                'error': f"Training configuration validation failed: {errors}"
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

def validate_model_config_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate model configuration specifically using RORO pattern."""
    config = params.get('config', {})
    
    try:
        errors: List[Any] = []
        model = config.get("model", {})
        
        # Validate model type
        mt_result = is_valid_model_type_roro({
            'model_type': model.get("model_type", "")
        })
        if not mt_result['result']:
            errors.append("Invalid model type")
        
        if model.get("hidden_size", 0) <= 0:
            errors.append("Hidden size must be positive")
        
        if model.get("num_layers", 0) <= 0:
            errors.append("Number of layers must be positive")
        
        if errors:
            return {
                'is_successful': False,
                'result': None,
                'error': f"Model configuration validation failed: {errors}"
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

# RORO Pattern: Configuration validation helpers
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
    valid_types: List[Any] = ["transformer", "cnn", "rnn", "mlp"]
    is_valid = model_type in valid_types
    
    return {
        'is_successful': True,
        'result': is_valid,
        'error': None
    }

def is_valid_device_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Check if device is valid using RORO pattern."""
    device = params.get('device', 'cpu')
    valid_devices: List[Any] = ["cpu", "cuda", "auto"]
    is_valid = device in valid_devices
    
    return {
        'is_successful': True,
        'result': is_valid,
        'error': None
    }

# RORO Pattern: Configuration pipelines
def create_config_pipeline_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a config pipeline that handles loading, validation, and merging using RORO pattern."""
    config_path = params.get('config_path')
    
    try:
        # Load config
        if config_path and Path(config_path).exists():
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config_result = load_config_from_yaml_roro({'file_path': config_path})
            elif config_path.endswith('.json'):
                config_result = load_config_from_json_roro({'file_path': config_path})
            else:
                config_result = load_config_from_yaml_roro({'file_path': config_path})
        else:
            config_result = create_default_config_roro({})
        
        if not config_result['is_successful']:
            return config_result
        
        # Validate config
        validation_result = validate_config_roro({'config': config_result['result']})
        
        if not validation_result['is_successful']:
            return validation_result
        
        return {
            'is_successful': True,
            'result': config_result['result'],
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def create_config_updater_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a config updater that safely merges new values using RORO pattern."""
    try:
        def update_config(config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
            merge_result = merge_configs_roro({
                'base': config,
                'override': updates
            })
            return merge_result['result'] if merge_result['is_successful'] else config
        
        return {
            'is_successful': True,
            'result': update_config,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def create_config_serializer_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a config serializer that handles different formats using RORO pattern."""
    try:
        def serialize_config(config: Dict[str, Any], format_type: str) -> Dict[str, Any]:
            def _serialize() -> str:
                if format_type == "yaml":
                    return yaml.dump(config, default_flow_style=False)
                elif format_type == "json":
                    return json.dumps(config, indent=2)
                else:
                    raise ValueError(f"Unsupported format: {format_type}")
            
            serialize_result = safe_execute_roro({
                'func': _serialize
            })
            
            return serialize_result
        
        return {
            'is_successful': True,
            'result': serialize_config,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

# RORO Pattern: Configuration routes
def create_config_info_route_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create config info route handler using RORO pattern."""
    try:
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
        
        return {
            'is_successful': True,
            'result': config_info,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def create_config_validation_route_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create config validation route handler using RORO pattern."""
    try:
        def validate_config_route(config: Dict[str, Any]) -> Dict[str, Any]:
            validation_result = validate_config_roro({'config': config})
            return {
                "is_valid": validation_result['is_successful'],
                "errors": validation_result['error'] if not validation_result['is_successful'] else []
            }
        
        return {
            'is_successful': True,
            'result': validate_config_route,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

def create_config_update_route_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create config update route handler using RORO pattern."""
    try:
        def update_config_route(config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
            merge_result = merge_configs_roro({
                'base': config,
                'override': updates
            })
            
            if merge_result['is_successful']:
                validation_result = validate_config_roro({'config': merge_result['result']})
                
                return {
                    "is_valid": validation_result['is_successful'],
                    "config": merge_result['result'] if validation_result['is_successful'] else config,
                    "errors": validation_result['error'] if not validation_result['is_successful'] else []
                }
            else:
                return {
                    "is_valid": False,
                    "config": config,
                    "errors": [merge_result['error']]
                }
        
        return {
            'is_successful': True,
            'result': update_config_route,
            'error': None
        }
    except Exception as e:
        return {
            'is_successful': False,
            'result': None,
            'error': str(e)
        }

# Export all RORO functions
__all__: List[Any] = [
    # Configuration classes
    'ModelConfig',
    'TrainingConfig', 
    'DataConfig',
    
    # Configuration creation RORO
    'create_default_config_roro',
    'create_training_config_roro',
    'create_model_config_roro',
    'create_data_config_roro',
    'create_debug_config_roro',
    'create_production_config_roro',
    
    # Configuration loading and saving RORO
    'load_config_from_yaml_roro',
    'load_config_from_json_roro',
    'save_config_to_yaml_roro',
    'save_config_to_json_roro',
    
    # Configuration manipulation RORO
    'merge_configs_roro',
    'get_config_value_roro',
    'set_config_value_roro',
    'update_config_section_roro',
    
    # Configuration validation RORO
    'validate_config_roro',
    'validate_training_config_roro',
    'validate_model_config_roro',
    
    # Validation helpers RORO
    'is_valid_learning_rate_roro',
    'is_valid_batch_size_roro',
    'is_valid_model_type_roro',
    'is_valid_device_roro',
    
    # Configuration pipelines RORO
    'create_config_pipeline_roro',
    'create_config_updater_roro',
    'create_config_serializer_roro',
    
    # Configuration routes RORO
    'create_config_info_route_roro',
    'create_config_validation_route_roro',
    'create_config_update_route_roro'
]

# Usage examples
if __name__ == "__main__":
    # Create config pipeline
    config_pipeline_result = create_config_pipeline_roro({'config_path': 'config.yaml'})
    
    if config_pipeline_result['is_successful']:
        config = config_pipeline_result['result']
        print("Configuration loaded successfully")
        
        # Get config values with descriptive names
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
    
    # Create config updater
    config_updater_result = create_config_updater_roro({})
    if config_updater_result['is_successful']:
        config_updater = config_updater_result['result']
        
        base_config_result = create_default_config_roro({})
        if base_config_result['is_successful']:
            base_config = base_config_result['result']
            updates: Dict[str, Any] = {"training": {"learning_rate": 1e-3}, "is_debug_mode": True}
            updated_config = config_updater(base_config, updates)
            print("Configuration updated successfully")
    
    # Create specialized configs
    debug_config_result = create_debug_config_roro({
        'is_debug_mode': True,
        'should_save_checkpoints': False
    })
    
    if debug_config_result['is_successful']:
        debug_config = debug_config_result['result']
        print(f"Debug config: {debug_config}")
    
    # Test route handlers
    config_info_route_result = create_config_info_route_roro({})
    if config_info_route_result['is_successful']:
        config_info_route = config_info_route_result['result']
        
        default_config_result = create_default_config_roro({})
        if default_config_result['is_successful']:
            config_info = config_info_route(default_config_result['result'])
            print(f"Config info: {config_info}") 