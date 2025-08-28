#!/usr/bin/env python3
"""
Modular Configuration System

Advanced configuration management with:
- Builder pattern for configuration construction
- Validation system for configuration parameters
- Dynamic configuration loading and saving
"""

import json
import yaml
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class BaseConfig:
    """Base configuration class."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save(self, path: str):
        """Save configuration to file."""
        file_path = Path(path)
        if file_path.suffix == '.json':
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
        elif file_path.suffix in ['.yml', '.yaml']:
            with open(file_path, 'w') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        logger.info(f"Configuration saved to {path}")

@dataclass
class MemoryConfig(BaseConfig):
    """Memory configuration."""
    threshold_gpu: float = 0.8
    threshold_cpu: float = 0.9
    optimization_interval: int = 10
    enable_auto_cleanup: bool = True
    enable_advanced_profiling: bool = True

@dataclass
class PerformanceConfig(BaseConfig):
    """Performance configuration."""
    enable_mixed_precision: bool = True
    enable_gradient_clipping: bool = True
    gradient_clip_norm: float = 1.0
    enable_adaptive_accumulation: bool = True
    enable_noise_injection: bool = False
    noise_scale: float = 1e-5

@dataclass
class TrainingConfig(BaseConfig):
    """Training configuration."""
    batch_size: int = 32
    effective_batch_size: int = 128
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    max_epochs: int = 100
    log_every: int = 10
    save_every: int = 100

class ConfigBuilder:
    """Builder pattern for configuration construction."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset builder to initial state."""
        self._memory_config = MemoryConfig()
        self._performance_config = PerformanceConfig()
        self._training_config = TrainingConfig()
        return self
    
    def with_memory_config(self, **kwargs):
        """Set memory configuration."""
        for key, value in kwargs.items():
            if hasattr(self._memory_config, key):
                setattr(self._memory_config, key, value)
        return self
    
    def with_performance_config(self, **kwargs):
        """Set performance configuration."""
        for key, value in kwargs.items():
            if hasattr(self._performance_config, key):
                setattr(self._performance_config, key, value)
        return self
    
    def with_training_config(self, **kwargs):
        """Set training configuration."""
        for key, value in kwargs.items():
            if hasattr(self._training_config, key):
                setattr(self._training_config, key, value)
        return self
    
    def build(self):
        """Build the complete configuration."""
        return {
            'memory': self._memory_config,
            'performance': self._performance_config,
            'training': self._training_config
        }

class ConfigValidator:
    """Configuration validation system."""
    
    @staticmethod
    def validate_memory_config(config: MemoryConfig) -> List[str]:
        """Validate memory configuration."""
        errors = []
        
        if not 0.0 <= config.threshold_gpu <= 1.0:
            errors.append("GPU threshold must be between 0.0 and 1.0")
        
        if not 0.0 <= config.threshold_cpu <= 1.0:
            errors.append("CPU threshold must be between 0.0 and 1.0")
        
        if config.optimization_interval < 1:
            errors.append("Optimization interval must be at least 1")
        
        return errors
    
    @staticmethod
    def validate_performance_config(config: PerformanceConfig) -> List[str]:
        """Validate performance configuration."""
        errors = []
        
        if config.gradient_clip_norm <= 0:
            errors.append("Gradient clip norm must be positive")
        
        if config.noise_scale < 0:
            errors.append("Noise scale must be non-negative")
        
        return errors
    
    @staticmethod
    def validate_training_config(config: TrainingConfig) -> List[str]:
        """Validate training configuration."""
        errors = []
        
        if config.batch_size <= 0:
            errors.append("Batch size must be positive")
        
        if config.effective_batch_size <= 0:
            errors.append("Effective batch size must be positive")
        
        if config.effective_batch_size % config.batch_size != 0:
            errors.append("Effective batch size must be divisible by batch size")
        
        if config.learning_rate <= 0:
            errors.append("Learning rate must be positive")
        
        if config.weight_decay < 0:
            errors.append("Weight decay must be non-negative")
        
        return errors
    
    @staticmethod
    def validate_all(configs: Dict[str, BaseConfig]) -> Dict[str, List[str]]:
        """Validate all configurations."""
        validation_results = {}
        
        if 'memory' in configs:
            validation_results['memory'] = ConfigValidator.validate_memory_config(configs['memory'])
        
        if 'performance' in configs:
            validation_results['performance'] = ConfigValidator.validate_performance_config(configs['performance'])
        
        if 'training' in configs:
            validation_results['training'] = ConfigValidator.validate_training_config(configs['training'])
        
        return validation_results

class ConfigManager:
    """Configuration manager for loading, saving, and managing configurations."""
    
    def __init__(self):
        self.configs = {}
        self.validator = ConfigValidator()
    
    def load_from_file(self, path: str) -> Dict[str, BaseConfig]:
        """Load configuration from file."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        if file_path.suffix == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
        elif file_path.suffix in ['.yml', '.yaml']:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Convert to configuration objects
        configs = {}
        if 'memory' in data:
            configs['memory'] = MemoryConfig(**data['memory'])
        if 'performance' in data:
            configs['performance'] = PerformanceConfig(**data['performance'])
        if 'training' in data:
            configs['training'] = TrainingConfig(**data['training'])
        
        # Validate configurations
        validation_results = self.validator.validate_all(configs)
        errors = []
        for config_name, config_errors in validation_results.items():
            errors.extend([f"{config_name}: {error}" for error in config_errors])
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(errors))
        
        self.configs = configs
        logger.info(f"Configuration loaded from {path}")
        return configs
    
    def save_to_file(self, path: str):
        """Save current configuration to file."""
        if not self.configs:
            raise ValueError("No configuration to save")
        
        # Convert to dictionary
        data = {}
        for name, config in self.configs.items():
            data[name] = config.to_dict()
        
        # Save to file
        file_path = Path(path)
        if file_path.suffix == '.json':
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif file_path.suffix in ['.yml', '.yaml']:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        logger.info(f"Configuration saved to {path}")
    
    def get_config(self, name: str) -> Optional[BaseConfig]:
        """Get configuration by name."""
        return self.configs.get(name)
    
    def update_config(self, name: str, **kwargs):
        """Update configuration parameters."""
        if name not in self.configs:
            raise ValueError(f"Configuration '{name}' not found")
        
        config = self.configs[name]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                logger.warning(f"Unknown parameter '{key}' for configuration '{name}'")
        
        # Validate updated configuration
        if name == 'memory':
            errors = self.validator.validate_memory_config(config)
        elif name == 'performance':
            errors = self.validator.validate_performance_config(config)
        elif name == 'training':
            errors = self.validator.validate_training_config(config)
        else:
            errors = []
        
        if errors:
            logger.warning(f"Configuration validation warnings for '{name}': {errors}")

# Example usage
if __name__ == "__main__":
    # Create configuration using builder pattern
    builder = ConfigBuilder()
    configs = builder.with_memory_config(threshold_gpu=0.75, threshold_cpu=0.85)\
                     .with_performance_config(enable_noise_injection=True, noise_scale=1e-4)\
                     .with_training_config(batch_size=16, effective_batch_size=128)\
                     .build()
    
    # Create configuration manager
    manager = ConfigManager()
    manager.configs = configs
    
    # Save configuration
    manager.save_to_file('config.json')
    
    # Load configuration
    loaded_configs = manager.load_from_file('config.json')
    
    print("Configuration loaded successfully!")
    print(f"Memory config: {loaded_configs['memory']}")
    print(f"Performance config: {loaded_configs['performance']}")
    print(f"Training config: {loaded_configs['training']}")
