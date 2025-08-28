#!/usr/bin/env python3
"""
Advanced Configuration Manager - Infrastructure Layer
==================================================

Enterprise-grade configuration management with hot-reloading,
encryption, feature flags, and environment-specific configs.
"""

import asyncio
import json
import logging
import os
import re
import secrets
import yaml
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union
import threading
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import watchdog.observers
import watchdog.events


class Environment(Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ConfigScope(Enum):
    """Configuration scopes."""
    GLOBAL = "global"
    ENVIRONMENT = "environment"
    FEATURE = "feature"
    USER = "user"
    SESSION = "session"


@dataclass
class FeatureFlag:
    """Feature flag configuration."""
    
    name: str
    enabled: bool = False
    description: Optional[str] = None
    rollout_percentage: float = 0.0
    target_users: List[str] = field(default_factory=list)
    target_environments: List[Environment] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigValue:
    """Configuration value with metadata."""
    
    key: str
    value: Any
    scope: ConfigScope
    environment: Optional[Environment] = None
    encrypted: bool = False
    description: Optional[str] = None
    last_modified: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    tags: List[str] = field(default_factory=list)


class ConfigEncryption:
    """Configuration encryption utilities."""
    
    def __init__(self, secret_key: Optional[str] = None):
        if secret_key is None:
            secret_key = os.getenv('CONFIG_SECRET_KEY', secrets.token_urlsafe(32))
        
        # Generate encryption key from secret
        salt = b'config_salt_123'  # In production, use a secure salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, value: str) -> str:
        """Encrypt a configuration value."""
        return self.cipher.encrypt(value.encode()).decode()
    
    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt a configuration value."""
        return self.cipher.decrypt(encrypted_value.encode()).decode()


class ConfigValidator:
    """Configuration validation utilities."""
    
    @staticmethod
    def validate_database_config(config: Dict[str, Any]) -> bool:
        """Validate database configuration."""
        required_keys = ['host', 'port', 'database', 'username']
        return all(key in config for key in required_keys)
    
    @staticmethod
    def validate_redis_config(config: Dict[str, Any]) -> bool:
        """Validate Redis configuration."""
        required_keys = ['host', 'port']
        return all(key in config for key in required_keys)
    
    @staticmethod
    def validate_api_config(config: Dict[str, Any]) -> bool:
        """Validate API configuration."""
        required_keys = ['host', 'port', 'debug']
        return all(key in config for key in required_keys)
    
    @staticmethod
    def validate_security_config(config: Dict[str, Any]) -> bool:
        """Validate security configuration."""
        required_keys = ['secret_key', 'algorithm', 'access_token_expire_minutes']
        return all(key in config for key in required_keys)


class ConfigWatcher:
    """File system watcher for configuration changes."""
    
    def __init__(self, config_manager: 'AdvancedConfigManager'):
        self.config_manager = config_manager
        self.observer = watchdog.observers.Observer()
        self._logger = logging.getLogger(__name__)
        self._watching = False
    
    def start_watching(self, config_path: str) -> None:
        """Start watching configuration files for changes."""
        if self._watching:
            return
        
        class ConfigFileHandler(watchdog.events.FileSystemEventHandler):
            def __init__(self, manager):
                self.manager = manager
                self.logger = logging.getLogger(__name__)
            
            def on_modified(self, event):
                if not event.is_directory and event.src_path.endswith(('.yaml', '.yml', '.json')):
                    self.logger.info(f"Configuration file changed: {event.src_path}")
                    asyncio.create_task(self.manager.reload_config())
        
        self.observer.schedule(ConfigFileHandler(self.config_manager), config_path, recursive=False)
        self.observer.start()
        self._watching = True
        self._logger.info(f"Started watching configuration files in: {config_path}")
    
    def stop_watching(self) -> None:
        """Stop watching configuration files."""
        if self._watching:
            self.observer.stop()
            self.observer.join()
            self._watching = False
            self._logger.info("Stopped watching configuration files")


class AdvancedConfigManager:
    """
    Advanced configuration management system.
    
    Features:
    - Environment-specific configurations
    - Hot-reloading of configuration files
    - Encrypted configuration values
    - Feature flags management
    - Configuration validation
    - Configuration versioning
    - Backup and restore capabilities
    - Configuration change notifications
    """
    
    def __init__(self, config_path: str = "config", environment: Environment = Environment.DEVELOPMENT):
        self.config_path = Path(config_path)
        self.environment = environment
        self.encryption = ConfigEncryption()
        self.validator = ConfigValidator()
        self.watcher = ConfigWatcher(self)
        
        self._config: Dict[str, ConfigValue] = {}
        self._feature_flags: Dict[str, FeatureFlag] = {}
        self._config_history: List[Dict[str, Any]] = []
        self._change_listeners: List[callable] = []
        
        self._logger = logging.getLogger(__name__)
        self._lock = threading.RLock()
        
        # Load initial configuration
        self._load_configuration()
        
        # Start file watcher
        self.watcher.start_watching(str(self.config_path))
    
    def _load_configuration(self) -> None:
        """Load configuration from files."""
        try:
            # Load base configuration
            base_config = self._load_config_file("base.yaml")
            if base_config:
                self._merge_config(base_config, ConfigScope.GLOBAL)
            
            # Load environment-specific configuration
            env_config = self._load_config_file(f"{self.environment.value}.yaml")
            if env_config:
                self._merge_config(env_config, ConfigScope.ENVIRONMENT)
            
            # Load feature flags
            feature_config = self._load_config_file("features.yaml")
            if feature_config:
                self._load_feature_flags(feature_config)
            
            self._logger.info(f"Configuration loaded for environment: {self.environment.value}")
            
        except Exception as e:
            self._logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _load_config_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load configuration from a specific file."""
        file_path = self.config_path / filename
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    return yaml.safe_load(f)
                elif filename.endswith('.json'):
                    return json.load(f)
                else:
                    self._logger.warning(f"Unsupported config file format: {filename}")
                    return None
        except Exception as e:
            self._logger.error(f"Failed to load config file {filename}: {e}")
            return None
    
    def _merge_config(self, config: Dict[str, Any], scope: ConfigScope) -> None:
        """Merge configuration into the current config."""
        with self._lock:
            for key, value in config.items():
                if isinstance(value, dict):
                    # Handle nested configuration
                    for nested_key, nested_value in value.items():
                        full_key = f"{key}.{nested_key}"
                        self._set_config_value(full_key, nested_value, scope)
                else:
                    self._set_config_value(key, value, scope)
    
    def _set_config_value(self, key: str, value: Any, scope: ConfigScope) -> None:
        """Set a configuration value."""
        # Check if value is encrypted
        encrypted = False
        if isinstance(value, str) and value.startswith('ENC[') and value.endswith(']'):
            encrypted = True
            value = value[4:-1]  # Remove ENC[...] wrapper
        
        config_value = ConfigValue(
            key=key,
            value=value,
            scope=scope,
            environment=self.environment if scope == ConfigScope.ENVIRONMENT else None,
            encrypted=encrypted
        )
        
        self._config[key] = config_value
    
    def _load_feature_flags(self, config: Dict[str, Any]) -> None:
        """Load feature flags from configuration."""
        feature_flags = config.get('feature_flags', {})
        
        for flag_name, flag_config in feature_flags.items():
            flag = FeatureFlag(
                name=flag_name,
                enabled=flag_config.get('enabled', False),
                description=flag_config.get('description'),
                rollout_percentage=flag_config.get('rollout_percentage', 0.0),
                target_users=flag_config.get('target_users', []),
                target_environments=[
                    Environment(env) for env in flag_config.get('target_environments', [])
                ],
                expires_at=datetime.fromisoformat(flag_config['expires_at']) if flag_config.get('expires_at') else None,
                metadata=flag_config.get('metadata', {})
            )
            
            self._feature_flags[flag_name] = flag
    
    async def reload_config(self) -> None:
        """Reload configuration from files."""
        with self._lock:
            # Backup current configuration
            self._backup_config()
            
            # Clear current configuration
            self._config.clear()
            self._feature_flags.clear()
            
            # Reload configuration
            self._load_configuration()
            
            # Notify listeners
            await self._notify_change_listeners("configuration_reloaded")
            
            self._logger.info("Configuration reloaded successfully")
    
    def get(self, key: str, default: Any = None, decrypt: bool = True) -> Any:
        """Get a configuration value."""
        with self._lock:
            if key not in self._config:
                return default
            
            config_value = self._config[key]
            value = config_value.value
            
            # Decrypt if needed
            if decrypt and config_value.encrypted:
                try:
                    value = self.encryption.decrypt(value)
                except Exception as e:
                    self._logger.error(f"Failed to decrypt config value {key}: {e}")
                    return default
            
            return value
    
    def set(self, key: str, value: Any, scope: ConfigScope = ConfigScope.GLOBAL,
            encrypt: bool = False) -> None:
        """Set a configuration value."""
        with self._lock:
            # Encrypt if requested
            if encrypt and isinstance(value, str):
                value = f"ENC[{self.encryption.encrypt(value)}]"
            
            config_value = ConfigValue(
                key=key,
                value=value,
                scope=scope,
                environment=self.environment if scope == ConfigScope.ENVIRONMENT else None,
                encrypted=encrypt
            )
            
            self._config[key] = config_value
            
            # Notify listeners
            asyncio.create_task(self._notify_change_listeners("config_updated", key=key, value=value))
    
    def get_feature_flag(self, flag_name: str, user_id: Optional[str] = None) -> bool:
        """Check if a feature flag is enabled."""
        with self._lock:
            if flag_name not in self._feature_flags:
                return False
            
            flag = self._feature_flags[flag_name]
            
            # Check if flag is expired
            if flag.expires_at and datetime.utcnow() > flag.expires_at:
                return False
            
            # Check environment
            if flag.target_environments and self.environment not in flag.target_environments:
                return False
            
            # Check user targeting
            if flag.target_users and user_id and user_id not in flag.target_users:
                return False
            
            # Check rollout percentage
            if flag.rollout_percentage > 0 and user_id:
                # Simple hash-based rollout
                user_hash = hashlib.md5(f"{user_id}_{flag_name}".encode()).hexdigest()
                user_percentage = int(user_hash[:8], 16) / (16 ** 8)
                return user_percentage <= flag.rollout_percentage
            
            return flag.enabled
    
    def set_feature_flag(self, flag: FeatureFlag) -> None:
        """Set a feature flag."""
        with self._lock:
            self._feature_flags[flag.name] = flag
            
            # Notify listeners
            asyncio.create_task(self._notify_change_listeners("feature_flag_updated", flag_name=flag.name))
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        config = {
            'host': self.get('database.host', 'localhost'),
            'port': self.get('database.port', 5432),
            'database': self.get('database.name', 'ultra_library'),
            'username': self.get('database.username', 'postgres'),
            'password': self.get('database.password', ''),
            'pool_size': self.get('database.pool_size', 10),
            'max_overflow': self.get('database.max_overflow', 20)
        }
        
        if not self.validator.validate_database_config(config):
            raise ValueError("Invalid database configuration")
        
        return config
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration."""
        config = {
            'host': self.get('redis.host', 'localhost'),
            'port': self.get('redis.port', 6379),
            'password': self.get('redis.password'),
            'db': self.get('redis.db', 0),
            'max_connections': self.get('redis.max_connections', 10)
        }
        
        if not self.validator.validate_redis_config(config):
            raise ValueError("Invalid Redis configuration")
        
        return config
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        config = {
            'host': self.get('api.host', '0.0.0.0'),
            'port': self.get('api.port', 8000),
            'debug': self.get('api.debug', False),
            'workers': self.get('api.workers', 1),
            'cors_origins': self.get('api.cors_origins', ['*']),
            'rate_limit': self.get('api.rate_limit', 100)
        }
        
        if not self.validator.validate_api_config(config):
            raise ValueError("Invalid API configuration")
        
        return config
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        config = {
            'secret_key': self.get('security.secret_key', secrets.token_urlsafe(32)),
            'algorithm': self.get('security.algorithm', 'HS256'),
            'access_token_expire_minutes': self.get('security.access_token_expire_minutes', 30),
            'refresh_token_expire_days': self.get('security.refresh_token_expire_days', 7),
            'password_min_length': self.get('security.password_min_length', 8),
            'max_login_attempts': self.get('security.max_login_attempts', 5),
            'lockout_duration_minutes': self.get('security.lockout_duration_minutes', 30)
        }
        
        if not self.validator.validate_security_config(config):
            raise ValueError("Invalid security configuration")
        
        return config
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration values."""
        with self._lock:
            return {
                key: {
                    'value': config_value.value,
                    'scope': config_value.scope.value,
                    'environment': config_value.environment.value if config_value.environment else None,
                    'encrypted': config_value.encrypted,
                    'last_modified': config_value.last_modified.isoformat(),
                    'version': config_value.version
                }
                for key, config_value in self._config.items()
            }
    
    def get_feature_flags(self) -> Dict[str, Any]:
        """Get all feature flags."""
        with self._lock:
            return {
                name: {
                    'enabled': flag.enabled,
                    'description': flag.description,
                    'rollout_percentage': flag.rollout_percentage,
                    'target_users': flag.target_users,
                    'target_environments': [env.value for env in flag.target_environments],
                    'created_at': flag.created_at.isoformat(),
                    'expires_at': flag.expires_at.isoformat() if flag.expires_at else None,
                    'metadata': flag.metadata
                }
                for name, flag in self._feature_flags.items()
            }
    
    def add_change_listener(self, listener: callable) -> None:
        """Add a configuration change listener."""
        with self._lock:
            self._change_listeners.append(listener)
    
    def remove_change_listener(self, listener: callable) -> None:
        """Remove a configuration change listener."""
        with self._lock:
            if listener in self._change_listeners:
                self._change_listeners.remove(listener)
    
    async def _notify_change_listeners(self, event_type: str, **kwargs) -> None:
        """Notify all change listeners."""
        with self._lock:
            listeners = self._change_listeners.copy()
        
        for listener in listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(event_type, **kwargs)
                else:
                    listener(event_type, **kwargs)
            except Exception as e:
                self._logger.error(f"Error in config change listener: {e}")
    
    def _backup_config(self) -> None:
        """Backup current configuration."""
        backup = {
            'timestamp': datetime.utcnow().isoformat(),
            'environment': self.environment.value,
            'config': self.get_all_config(),
            'feature_flags': self.get_feature_flags()
        }
        
        self._config_history.append(backup)
        
        # Keep only last 10 backups
        if len(self._config_history) > 10:
            self._config_history.pop(0)
    
    def export_config(self, format: str = "json") -> str:
        """Export configuration in specified format."""
        data = {
            'environment': self.environment.value,
            'config': self.get_all_config(),
            'feature_flags': self.get_feature_flags(),
            'export_timestamp': datetime.utcnow().isoformat()
        }
        
        if format.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        elif format.lower() == "yaml":
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_config(self, config_data: str, format: str = "json") -> None:
        """Import configuration from string."""
        try:
            if format.lower() == "json":
                data = json.loads(config_data)
            elif format.lower() == "yaml":
                data = yaml.safe_load(config_data)
            else:
                raise ValueError(f"Unsupported import format: {format}")
            
            # Import configuration
            with self._lock:
                for key, config_info in data.get('config', {}).items():
                    config_value = ConfigValue(
                        key=key,
                        value=config_info['value'],
                        scope=ConfigScope(config_info['scope']),
                        environment=Environment(config_info['environment']) if config_info['environment'] else None,
                        encrypted=config_info['encrypted'],
                        last_modified=datetime.fromisoformat(config_info['last_modified']),
                        version=config_info['version']
                    )
                    self._config[key] = config_value
                
                # Import feature flags
                for name, flag_info in data.get('feature_flags', {}).items():
                    flag = FeatureFlag(
                        name=name,
                        enabled=flag_info['enabled'],
                        description=flag_info['description'],
                        rollout_percentage=flag_info['rollout_percentage'],
                        target_users=flag_info['target_users'],
                        target_environments=[Environment(env) for env in flag_info['target_environments']],
                        created_at=datetime.fromisoformat(flag_info['created_at']),
                        expires_at=datetime.fromisoformat(flag_info['expires_at']) if flag_info.get('expires_at') else None,
                        metadata=flag_info['metadata']
                    )
                    self._feature_flags[name] = flag
            
            self._logger.info("Configuration imported successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to import configuration: {e}")
            raise
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        self.watcher.stop_watching()


# Global configuration manager instance
config_manager = AdvancedConfigManager()


# Decorators for easy configuration access
def config_value(key: str, default: Any = None, decrypt: bool = True):
    """Decorator to inject configuration values."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            value = config_manager.get(key, default, decrypt)
            return func(value, *args, **kwargs)
        return wrapper
    return decorator


def feature_flag(flag_name: str, user_id_key: str = None):
    """Decorator to check feature flags."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_id = kwargs.get(user_id_key) if user_id_key else None
            if config_manager.get_feature_flag(flag_name, user_id):
                return func(*args, **kwargs)
            else:
                raise ValueError(f"Feature flag '{flag_name}' is not enabled")
        return wrapper
    return decorator 