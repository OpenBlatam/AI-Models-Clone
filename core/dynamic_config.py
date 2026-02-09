"""
Dynamic configuration system for the modular dependency management system.
Allows runtime configuration changes and hot-reloading of settings.
"""

import os
import json
import yaml
import asyncio
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .dependency_structures import ServiceStatus


@dataclass
class ConfigSection:
    """Configuration section with validation and callbacks"""
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    validators: Dict[str, Callable] = field(default_factory=dict)
    callbacks: Dict[str, List[Callable]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConfigValidator:
    """Configuration validation utilities"""
    
    @staticmethod
    def validate_string(value: Any, min_length: int = 0, max_length: Optional[int] = None) -> bool:
        """Validate string value"""
        if not isinstance(value, str):
            return False
        if len(value) < min_length:
            return False
        if max_length and len(value) > max_length:
            return False
        return True
    
    @staticmethod
    def validate_int(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None) -> bool:
        """Validate integer value"""
        if not isinstance(value, int):
            return False
        if min_value is not None and value < min_value:
            return False
        if max_value is not None and value > max_value:
            return False
        return True
    
    @staticmethod
    def validate_float(value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None) -> bool:
        """Validate float value"""
        if not isinstance(value, (int, float)):
            return False
        if min_value is not None and value < min_value:
            return False
        if max_value is not None and value > max_value:
            return False
        return True
    
    @staticmethod
    def validate_bool(value: Any) -> bool:
        """Validate boolean value"""
        return isinstance(value, bool)
    
    @staticmethod
    def validate_list(value: Any, min_length: int = 0, max_length: Optional[int] = None) -> bool:
        """Validate list value"""
        if not isinstance(value, list):
            return False
        if len(value) < min_length:
            return False
        if max_length and len(value) > max_length:
            return False
        return True
    
    @staticmethod
    def validate_dict(value: Any, required_keys: Optional[List[str]] = None) -> bool:
        """Validate dictionary value"""
        if not isinstance(value, dict):
            return False
        if required_keys:
            for key in required_keys:
                if key not in value:
                    return False
        return True


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for configuration files"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(('.json', '.yaml', '.yml')):
            self.logger.info(f"Configuration file modified: {event.src_path}")
            asyncio.create_task(self.config_manager.reload_config())


class DynamicConfigManager:
    """Dynamic configuration management system"""
    
    def __init__(self, config_path: str = "config", auto_reload: bool = True):
        self.config_path = Path(config_path)
        self.config_path.mkdir(exist_ok=True)
        
        self.sections: Dict[str, ConfigSection] = {}
        self.default_config: Dict[str, Any] = {}
        self.auto_reload = auto_reload
        self.observer: Optional[Observer] = None
        self.logger = logging.getLogger(__name__)
        
        # File handlers for different formats
        self.file_handlers = {
            '.json': self._load_json,
            '.yaml': self._load_yaml,
            '.yml': self._load_yaml
        }
        
        # Initialize default configuration
        self._init_default_config()
        
        # Start file watching if auto_reload is enabled
        if self.auto_reload:
            self._start_file_watcher()
    
    def _init_default_config(self):
        """Initialize default configuration sections"""
        self.default_config = {
            'system': {
                'debug_mode': False,
                'log_level': 'INFO',
                'max_workers': 4,
                'timeout': 30.0
            },
            'services': {
                'auto_start': True,
                'health_check_interval': 30.0,
                'max_retries': 3,
                'retry_delay': 5.0
            },
            'metrics': {
                'enabled': True,
                'collection_interval': 30.0,
                'retention_days': 7,
                'export_enabled': True
            },
            'plugins': {
                'auto_load': True,
                'plugin_dirs': ['plugins'],
                'enabled_plugins': []
            },
            'security': {
                'enabled': False,
                'auth_required': False,
                'ssl_enabled': False
            }
        }
        
        # Create sections from default config
        for section_name, section_data in self.default_config.items():
            self.add_section(section_name, section_data)
    
    def add_section(self, name: str, default_data: Dict[str, Any] = None) -> ConfigSection:
        """Add a new configuration section"""
        if name not in self.sections:
            self.sections[name] = ConfigSection(name, default_data or {})
        return self.sections[name]
    
    def get_section(self, name: str) -> Optional[ConfigSection]:
        """Get a configuration section"""
        return self.sections.get(name)
    
    def get(self, key: str, default: Any = None, section: str = 'system') -> Any:
        """Get a configuration value"""
        if section not in self.sections:
            return default
        
        # Handle nested keys (e.g., 'database.host')
        keys = key.split('.')
        value = self.sections[section].data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, section: str = 'system', validate: bool = True) -> bool:
        """Set a configuration value"""
        if section not in self.sections:
            self.add_section(section)
        
        # Validate the value if requested
        if validate:
            if not self._validate_value(key, value, section):
                self.logger.error(f"Validation failed for {section}.{key} = {value}")
                return False
        
        # Handle nested keys
        keys = key.split('.')
        data = self.sections[section].data
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        # Set the value
        data[keys[-1]] = value
        
        # Execute callbacks
        self._execute_callbacks(section, key, value)
        
        return True
    
    def _validate_value(self, key: str, value: Any, section: str) -> bool:
        """Validate a configuration value"""
        if section not in self.sections:
            return True
        
        validators = self.sections[section].validators
        if key in validators:
            return validators[key](value)
        
        return True
    
    def add_validator(self, key: str, validator: Callable, section: str = 'system'):
        """Add a validator for a configuration key"""
        if section not in self.sections:
            self.add_section(section)
        
        self.sections[section].validators[key] = validator
    
    def add_callback(self, key: str, callback: Callable, section: str = 'system'):
        """Add a callback for when a configuration key changes"""
        if section not in self.sections:
            self.add_section(section)
        
        if key not in self.sections[section].callbacks:
            self.sections[section].callbacks[key] = []
        
        self.sections[section].callbacks[key].append(callback)
    
    def _execute_callbacks(self, section: str, key: str, value: Any):
        """Execute callbacks for a configuration change"""
        if section not in self.sections:
            return
        
        callbacks = self.sections[section].callbacks.get(key, [])
        for callback in callbacks:
            try:
                callback(value)
            except Exception as e:
                self.logger.error(f"Error executing callback for {section}.{key}: {e}")
    
    def load_config_file(self, file_path: str) -> bool:
        """Load configuration from a file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.warning(f"Configuration file not found: {file_path}")
                return False
            
            extension = file_path.suffix.lower()
            if extension not in self.file_handlers:
                self.logger.error(f"Unsupported file format: {extension}")
                return False
            
            config_data = self.file_handlers[extension](file_path)
            
            # Merge configuration data
            for section_name, section_data in config_data.items():
                if section_name not in self.sections:
                    self.add_section(section_name)
                
                self.sections[section_name].data.update(section_data)
            
            self.logger.info(f"Configuration loaded from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading configuration from {file_path}: {e}")
            return False
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON configuration file"""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file"""
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    
    def save_config_file(self, file_path: str, format: str = 'json') -> bool:
        """Save current configuration to a file"""
        try:
            config_data = {}
            for section_name, section in self.sections.items():
                config_data[section_name] = section.data
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == 'json':
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
            elif format.lower() in ['yaml', 'yml']:
                with open(file_path, 'w') as f:
                    yaml.dump(config_data, f, default_flow_style=False)
            else:
                self.logger.error(f"Unsupported format: {format}")
                return False
            
            self.logger.info(f"Configuration saved to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration to {file_path}: {e}")
            return False
    
    def _start_file_watcher(self):
        """Start file system watcher for auto-reload"""
        try:
            self.observer = Observer()
            handler = ConfigFileHandler(self)
            self.observer.schedule(handler, str(self.config_path), recursive=True)
            self.observer.start()
            self.logger.info("Configuration file watcher started")
        except Exception as e:
            self.logger.error(f"Failed to start file watcher: {e}")
    
    def stop_file_watcher(self):
        """Stop file system watcher"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.logger.info("Configuration file watcher stopped")
    
    async def reload_config(self):
        """Reload configuration from files"""
        try:
            # Find all configuration files
            config_files = []
            for ext in ['.json', '.yaml', '.yml']:
                config_files.extend(self.config_path.glob(f"*{ext}"))
            
            # Load each file
            for config_file in config_files:
                self.load_config_file(str(config_file))
            
            self.logger.info("Configuration reloaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error reloading configuration: {e}")
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration data"""
        config_data = {}
        for section_name, section in self.sections.items():
            config_data[section_name] = section.data.copy()
        return config_data
    
    def reset_to_defaults(self, section: Optional[str] = None):
        """Reset configuration to defaults"""
        if section:
            if section in self.default_config:
                self.sections[section].data = self.default_config[section].copy()
        else:
            # Reset all sections
            for section_name, default_data in self.default_config.items():
                if section_name in self.sections:
                    self.sections[section_name].data = default_data.copy()
    
    def export_config(self, file_path: str, format: str = 'json') -> bool:
        """Export current configuration"""
        return self.save_config_file(file_path, format)
    
    def import_config(self, file_path: str) -> bool:
        """Import configuration from file"""
        return self.load_config_file(file_path)


# Global configuration manager instance
config_manager = DynamicConfigManager()


def get_config_manager() -> DynamicConfigManager:
    """Get the global configuration manager instance"""
    return config_manager


def get_config(key: str, default: Any = None, section: str = 'system') -> Any:
    """Get a configuration value using the global manager"""
    return config_manager.get(key, default, section)


def set_config(key: str, value: Any, section: str = 'system', validate: bool = True) -> bool:
    """Set a configuration value using the global manager"""
    return config_manager.set(key, value, section, validate)


def add_config_validator(key: str, validator: Callable, section: str = 'system'):
    """Add a configuration validator using the global manager"""
    config_manager.add_validator(key, validator, section)


def add_config_callback(key: str, callback: Callable, section: str = 'system'):
    """Add a configuration callback using the global manager"""
    config_manager.add_callback(key, callback, section)
