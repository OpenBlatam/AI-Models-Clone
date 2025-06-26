"""
Configuration Management for Modular NLP System.

This module provides centralized configuration management for the NLP system,
supporting environment variables, config files, and runtime configuration.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum

from .interfaces import IConfiguration, AnalysisConfig, AnalysisType, Priority
from .exceptions import ConfigurationException, InvalidConfigurationException, MissingConfigurationException

class ConfigSource(Enum):
    """Configuration sources in order of priority (highest first)."""
    RUNTIME = "runtime"          # Set at runtime
    ENVIRONMENT = "environment"  # Environment variables
    CONFIG_FILE = "config_file" # Configuration files
    DEFAULT = "default"         # Default values

@dataclass
class CacheConfig:
    """Configuration for caching system."""
    enabled: bool = True
    type: str = "memory"  # memory, redis, file
    ttl_seconds: int = 3600
    max_size: int = 1000
    connection_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5

@dataclass
class PerformanceConfig:
    """Configuration for performance settings."""
    max_parallel_analyzers: int = 4
    default_timeout_ms: int = 5000
    enable_async: bool = True
    thread_pool_size: int = 8

@dataclass
class QualityConfig:
    """Configuration for quality scoring."""
    weights: Dict[str, float] = field(default_factory=lambda: {
        "readability": 0.25,
        "sentiment": 0.20,
        "seo": 0.25,
        "semantic": 0.15,
        "structure": 0.15
    })
    min_score_threshold: float = 70.0
    excellent_score_threshold: float = 90.0

@dataclass
class NLPSystemConfig:
    """Main configuration for the NLP system."""
    # System settings
    enable_plugins: bool = True
    enable_caching: bool = True
    enable_monitoring: bool = True
    debug_mode: bool = False
    
    # Component configurations
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    
    # Analyzer configurations
    analyzer_configs: Dict[str, AnalysisConfig] = field(default_factory=dict)
    
    # Plugin configurations
    plugin_directories: list = field(default_factory=lambda: ["plugins"])
    auto_load_plugins: bool = True
    
    def __post_init__(self):
        """Initialize default analyzer configurations."""
        if not self.analyzer_configs:
            self.analyzer_configs = self._get_default_analyzer_configs()
    
    def _get_default_analyzer_configs(self) -> Dict[str, AnalysisConfig]:
        """Get default configurations for all analyzers."""
        return {
            "readability": AnalysisConfig(
                enabled=True,
                priority=Priority.HIGH,
                timeout_ms=2000,
                parameters={
                    "metrics": ["flesch", "gunning_fog", "coleman_liau"],
                    "target_grade_level": 8
                }
            ),
            "sentiment": AnalysisConfig(
                enabled=True,
                priority=Priority.MEDIUM,
                timeout_ms=3000,
                parameters={
                    "engines": ["textblob", "vader"],
                    "combine_results": True
                }
            ),
            "seo": AnalysisConfig(
                enabled=True,
                priority=Priority.HIGH,
                timeout_ms=1500,
                parameters={
                    "optimal_keyword_density": 2.0,
                    "max_keyword_density": 4.0,
                    "check_title_keywords": True
                }
            ),
            "semantic": AnalysisConfig(
                enabled=True,
                priority=Priority.MEDIUM,
                timeout_ms=4000,
                parameters={
                    "model": "all-MiniLM-L6-v2",
                    "coherence_threshold": 0.7
                }
            ),
            "language": AnalysisConfig(
                enabled=True,
                priority=Priority.LOW,
                timeout_ms=1000,
                parameters={
                    "confidence_threshold": 0.8
                }
            ),
            "entity": AnalysisConfig(
                enabled=False,  # Disabled by default for performance
                priority=Priority.LOW,
                timeout_ms=3000,
                parameters={
                    "models": ["en_core_web_sm"],
                    "entity_types": ["PERSON", "ORG", "GPE"]
                }
            )
        }

class ConfigurationManager(IConfiguration):
    """Centralized configuration manager for the NLP system."""
    
    def __init__(self, config_file: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (JSON or YAML)
            config_dict: Configuration dictionary for testing/runtime
        """
        self._config_sources: Dict[ConfigSource, Dict[str, Any]] = {
            ConfigSource.RUNTIME: {},
            ConfigSource.ENVIRONMENT: {},
            ConfigSource.CONFIG_FILE: {},
            ConfigSource.DEFAULT: {}
        }
        
        # Load default configuration
        self._load_default_config()
        
        # Load from file if provided
        if config_file:
            self._load_config_file(config_file)
        
        # Load from dict if provided (for testing)
        if config_dict:
            self._config_sources[ConfigSource.RUNTIME].update(config_dict)
        
        # Load environment variables
        self._load_environment_config()
        
        # Build final merged configuration
        self._merged_config = self._merge_configurations()
        
        # Create system config object
        self.system_config = self._create_system_config()
    
    def _load_default_config(self):
        """Load default configuration."""
        default_config = NLPSystemConfig()
        self._config_sources[ConfigSource.DEFAULT] = asdict(default_config)
    
    def _load_config_file(self, config_file: str):
        """Load configuration from file."""
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise MissingConfigurationException(f"Config file not found: {config_file}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    config_data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    raise InvalidConfigurationException(
                        "config_file", 
                        f"Unsupported file format: {config_path.suffix}"
                    )
            
            self._config_sources[ConfigSource.CONFIG_FILE] = config_data
            
        except Exception as e:
            raise InvalidConfigurationException("config_file", str(e))
    
    def _load_environment_config(self):
        """Load configuration from environment variables."""
        env_config = {}
        
        # System-level environment variables
        env_mappings = {
            'NLP_DEBUG_MODE': ('debug_mode', bool),
            'NLP_ENABLE_CACHING': ('enable_caching', bool),
            'NLP_ENABLE_PLUGINS': ('enable_plugins', bool),
            'NLP_CACHE_TTL': ('cache.ttl_seconds', int),
            'NLP_CACHE_TYPE': ('cache.type', str),
            'NLP_LOG_LEVEL': ('logging.level', str),
            'NLP_MAX_PARALLEL': ('performance.max_parallel_analyzers', int),
            'NLP_DEFAULT_TIMEOUT': ('performance.default_timeout_ms', int),
        }
        
        for env_var, (config_path, value_type) in env_mappings.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Convert value to appropriate type
                if value_type == bool:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                elif value_type == int:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                
                # Set nested configuration
                self._set_nested_config(env_config, config_path, value)
        
        self._config_sources[ConfigSource.ENVIRONMENT] = env_config
    
    def _set_nested_config(self, config: Dict[str, Any], path: str, value: Any):
        """Set nested configuration value using dot notation."""
        keys = path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _merge_configurations(self) -> Dict[str, Any]:
        """Merge configurations from all sources in priority order."""
        merged = {}
        
        # Merge in reverse priority order (lowest to highest)
        for source in reversed(list(ConfigSource)):
            source_config = self._config_sources[source]
            merged = self._deep_merge(merged, source_config)
        
        return merged
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _create_system_config(self) -> NLPSystemConfig:
        """Create system configuration object from merged config."""
        try:
            # Convert dict back to dataclass
            return self._dict_to_dataclass(self._merged_config, NLPSystemConfig)
        except Exception as e:
            raise InvalidConfigurationException("system_config", str(e))
    
    def _dict_to_dataclass(self, data: Dict[str, Any], dataclass_type):
        """Convert dictionary to dataclass recursively."""
        if not isinstance(data, dict):
            return data
        
        # Get dataclass fields
        field_types = {f.name: f.type for f in dataclass_type.__dataclass_fields__.values()}
        
        kwargs = {}
        for field_name, field_type in field_types.items():
            if field_name in data:
                value = data[field_name]
                
                # Handle nested dataclasses
                if hasattr(field_type, '__dataclass_fields__'):
                    value = self._dict_to_dataclass(value, field_type)
                
                kwargs[field_name] = value
        
        return dataclass_type(**kwargs)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        current = self._merged_config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value at runtime."""
        self._set_nested_config(self._config_sources[ConfigSource.RUNTIME], key, value)
        self._merged_config = self._merge_configurations()
        self.system_config = self._create_system_config()
    
    def get_analyzer_config(self, analyzer_name: str) -> AnalysisConfig:
        """Get configuration for specific analyzer."""
        if analyzer_name in self.system_config.analyzer_configs:
            return self.system_config.analyzer_configs[analyzer_name]
        
        # Return default config if not found
        return AnalysisConfig()
    
    def update_analyzer_config(self, analyzer_name: str, config: AnalysisConfig):
        """Update configuration for specific analyzer."""
        self.system_config.analyzer_configs[analyzer_name] = config
    
    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration."""
        return self.system_config.cache
    
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration."""
        return self.system_config.performance
    
    def get_quality_config(self) -> QualityConfig:
        """Get quality configuration."""
        return self.system_config.quality
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.system_config.debug_mode
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self.system_config)
    
    def save_to_file(self, file_path: str, format: str = "yaml"):
        """Save current configuration to file."""
        config_dict = self.to_dict()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if format.lower() == "yaml":
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            elif format.lower() == "json":
                json.dump(config_dict, f, indent=2)
            else:
                raise InvalidConfigurationException("format", f"Unsupported format: {format}")

# Global configuration instance
_config_manager: Optional[ConfigurationManager] = None

def get_config() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager

def initialize_config(config_file: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None):
    """Initialize the global configuration manager."""
    global _config_manager
    _config_manager = ConfigurationManager(config_file, config_dict)

def reset_config():
    """Reset the global configuration manager."""
    global _config_manager
    _config_manager = None 