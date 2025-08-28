#!/usr/bin/env python3
"""
Advanced Configuration Management - Infrastructure Layer
====================================================

Advanced configuration management with environment-based configuration,
validation, feature flags, and enterprise-grade features.
"""

import asyncio
import json
import logging
import os
import secrets
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union
from contextlib import asynccontextmanager
import yaml
from pydantic import BaseModel, ValidationError, validator

T = TypeVar('T')


class Environment(Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ConfigSource(Enum):
    """Configuration sources."""
    ENVIRONMENT = "environment"
    FILE = "file"
    DATABASE = "database"
    REMOTE = "remote"
    SECRETS = "secrets"


@dataclass
class ConfigValue:
    """Configuration value with metadata."""
    
    key: str
    value: Any
    source: ConfigSource
    environment: Environment
    encrypted: bool = False
    last_updated: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if the configuration value is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'key': self.key,
            'value': self.value,
            'source': self.source.value,
            'environment': self.environment.value,
            'encrypted': self.encrypted,
            'last_updated': self.last_updated.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'metadata': self.metadata
        }


@dataclass
class FeatureFlag:
    """Feature flag configuration."""
    
    name: str
    enabled: bool
    environment: Environment
    rollout_percentage: float = 100.0
    user_groups: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def is_active(self, user_id: Optional[str] = None, user_groups: Optional[List[str]] = None) -> bool:
        """Check if feature flag is active for given context."""
        if not self.enabled:
            return False
        
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        
        # Check user groups
        if self.user_groups and user_groups:
            if not any(group in self.user_groups for group in user_groups):
                return False
        
        # Check rollout percentage
        if self.rollout_percentage < 100.0:
            # Simple hash-based rollout
            if user_id:
                hash_value = hash(user_id) % 100
                if hash_value >= self.rollout_percentage:
                    return False
        
        return True


class DatabaseConfig(BaseModel):
    """Database configuration model."""
    
    host: str
    port: int = 5432
    database: str
    username: str
    password: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    @validator('host')
    def validate_host(cls, v):
        if not v:
            raise ValueError('Database host cannot be empty')
        return v
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Database port must be between 1 and 65535')
        return v


class RedisConfig(BaseModel):
    """Redis configuration model."""
    
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    pool_size: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Redis port must be between 1 and 65535')
        return v


class SecurityConfig(BaseModel):
    """Security configuration model."""
    
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    bcrypt_rounds: int = 12
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters long')
        return v


class LoggingConfig(BaseModel):
    """Logging configuration model."""
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size_mb: int = 100
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = False
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()


class ApplicationConfig(BaseModel):
    """Main application configuration model."""
    
    # Basic settings
    app_name: str = "Ultra Library Optimization V7"
    version: str = "7.0.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Database configuration
    database: DatabaseConfig
    
    # Redis configuration
    redis: RedisConfig
    
    # Security configuration
    security: SecurityConfig
    
    # Logging configuration
    logging: LoggingConfig = LoggingConfig()
    
    # Feature flags
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    
    # Performance settings
    max_connections: int = 1000
    request_timeout: int = 30
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # Monitoring settings
    enable_metrics: bool = True
    enable_health_checks: bool = True
    metrics_port: int = 9090
    
    # Cache settings
    cache_ttl_seconds: int = 300
    cache_max_size: int = 1000
    
    # Event bus settings
    event_bus_workers: int = 10
    event_bus_queue_size: int = 1000
    
    # Command bus settings
    command_bus_workers: int = 5
    command_bus_queue_size: int = 500
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('workers')
    def validate_workers(cls, v):
        if v < 1:
            raise ValueError('Workers must be at least 1')
        return v


class ConfigurationManager:
    """
    Advanced configuration manager with enterprise-grade features.
    
    Features:
    - Environment-based configuration
    - Configuration validation with Pydantic
    - Feature flags and dynamic configuration
    - Secrets management
    - Configuration hot-reloading
    - Configuration encryption
    - Configuration versioning
    - Configuration backup and restore
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self._config_path = config_path or "config"
        self._config: Dict[str, ConfigValue] = {}
        self._feature_flags: Dict[str, FeatureFlag] = {}
        self._secrets: Dict[str, str] = {}
        self._watchers: List[Callable] = []
        self._logger = logging.getLogger(__name__)
        self._environment = self._detect_environment()
        self._config_file = None
        self._last_modified = 0.0
        self._encryption_key = None
        
        # Load configuration
        self._load_configuration()
    
    @property
    def environment(self) -> Environment:
        """Get current environment."""
        return self._environment
    
    def get(self, key: str, default: Any = None, decrypt: bool = False) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            decrypt: Whether to decrypt the value
        
        Returns:
            Configuration value
        """
        if key not in self._config:
            return default
        
        config_value = self._config[key]
        
        # Check if expired
        if config_value.is_expired():
            self._logger.warning(f"Configuration key '{key}' has expired")
            return default
        
        value = config_value.value
        
        # Decrypt if requested
        if decrypt and config_value.encrypted:
            value = self._decrypt_value(value)
        
        return value
    
    def set(self, key: str, value: Any, source: ConfigSource = ConfigSource.FILE,
            encrypted: bool = False, expires_at: Optional[datetime] = None) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            source: Configuration source
            encrypted: Whether to encrypt the value
            expires_at: Expiration timestamp
        """
        # Encrypt if requested
        if encrypted:
            value = self._encrypt_value(value)
        
        config_value = ConfigValue(
            key=key,
            value=value,
            source=source,
            environment=self._environment,
            encrypted=encrypted,
            expires_at=expires_at
        )
        
        self._config[key] = config_value
        self._logger.info(f"Set configuration key '{key}' from {source.value}")
        
        # Notify watchers
        self._notify_watchers(key, value)
    
    def delete(self, key: str) -> None:
        """
        Delete configuration value.
        
        Args:
            key: Configuration key to delete
        """
        if key in self._config:
            del self._config[key]
            self._logger.info(f"Deleted configuration key '{key}'")
    
    def has(self, key: str) -> bool:
        """
        Check if configuration key exists.
        
        Args:
            key: Configuration key to check
        
        Returns:
            True if key exists and is not expired
        """
        if key not in self._config:
            return False
        
        return not self._config[key].is_expired()
    
    def get_all(self, prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Args:
            prefix: Optional prefix to filter keys
        
        Returns:
            Dictionary of configuration values
        """
        result = {}
        
        for key, config_value in self._config.items():
            if prefix and not key.startswith(prefix):
                continue
            
            if not config_value.is_expired():
                result[key] = config_value.value
        
        return result
    
    def reload(self) -> None:
        """Reload configuration from sources."""
        self._logger.info("Reloading configuration...")
        self._load_configuration()
        self._logger.info("Configuration reloaded")
    
    def watch(self, callback: Callable[[str, Any], None]) -> None:
        """
        Watch for configuration changes.
        
        Args:
            callback: Callback function to call when configuration changes
        """
        self._watchers.append(callback)
    
    def unwatch(self, callback: Callable[[str, Any], None]) -> None:
        """
        Stop watching for configuration changes.
        
        Args:
            callback: Callback function to remove
        """
        if callback in self._watchers:
            self._watchers.remove(callback)
    
    # Feature flags
    def set_feature_flag(self, name: str, enabled: bool, rollout_percentage: float = 100.0,
                        user_groups: Optional[List[str]] = None,
                        conditions: Optional[Dict[str, Any]] = None,
                        expires_at: Optional[datetime] = None) -> None:
        """
        Set a feature flag.
        
        Args:
            name: Feature flag name
            enabled: Whether the feature is enabled
            rollout_percentage: Percentage of users to enable for (0-100)
            user_groups: List of user groups to enable for
            conditions: Additional conditions
            expires_at: Expiration timestamp
        """
        feature_flag = FeatureFlag(
            name=name,
            enabled=enabled,
            environment=self._environment,
            rollout_percentage=rollout_percentage,
            user_groups=user_groups or [],
            conditions=conditions or {},
            expires_at=expires_at
        )
        
        self._feature_flags[name] = feature_flag
        self._logger.info(f"Set feature flag '{name}' to {enabled}")
    
    def is_feature_enabled(self, name: str, user_id: Optional[str] = None,
                          user_groups: Optional[List[str]] = None) -> bool:
        """
        Check if a feature flag is enabled.
        
        Args:
            name: Feature flag name
            user_id: User ID for rollout percentage
            user_groups: User groups for filtering
        
        Returns:
            True if feature is enabled
        """
        if name not in self._feature_flags:
            return False
        
        return self._feature_flags[name].is_active(user_id, user_groups)
    
    def get_feature_flags(self) -> Dict[str, FeatureFlag]:
        """Get all feature flags."""
        return self._feature_flags.copy()
    
    # Secrets management
    def set_secret(self, key: str, value: str) -> None:
        """
        Set a secret value.
        
        Args:
            key: Secret key
            value: Secret value
        """
        self._secrets[key] = value
        self._logger.info(f"Set secret '{key}'")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a secret value.
        
        Args:
            key: Secret key
            default: Default value if secret not found
        
        Returns:
            Secret value
        """
        return self._secrets.get(key, default)
    
    def delete_secret(self, key: str) -> None:
        """
        Delete a secret value.
        
        Args:
            key: Secret key to delete
        """
        if key in self._secrets:
            del self._secrets[key]
            self._logger.info(f"Deleted secret '{key}'")
    
    # Configuration validation
    def validate_config(self, config_class: Type[BaseModel]) -> BaseModel:
        """
        Validate configuration against a Pydantic model.
        
        Args:
            config_class: Pydantic model class
        
        Returns:
            Validated configuration instance
        
        Raises:
            ValidationError: If configuration is invalid
        """
        config_data = self.get_all()
        
        try:
            return config_class(**config_data)
        except ValidationError as e:
            self._logger.error(f"Configuration validation failed: {e}")
            raise
    
    # Configuration export/import
    def export_config(self, format: str = "json") -> str:
        """
        Export configuration.
        
        Args:
            format: Export format (json, yaml)
        
        Returns:
            Exported configuration string
        """
        config_data = {
            'environment': self._environment.value,
            'config': {k: v.to_dict() for k, v in self._config.items()},
            'feature_flags': {k: v.__dict__ for k, v in self._feature_flags.items()},
            'exported_at': datetime.utcnow().isoformat()
        }
        
        if format.lower() == "json":
            return json.dumps(config_data, indent=2, default=str)
        elif format.lower() == "yaml":
            return yaml.dump(config_data, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_config(self, config_data: str, format: str = "json") -> None:
        """
        Import configuration.
        
        Args:
            config_data: Configuration data string
            format: Import format (json, yaml)
        """
        if format.lower() == "json":
            data = json.loads(config_data)
        elif format.lower() == "yaml":
            data = yaml.safe_load(config_data)
        else:
            raise ValueError(f"Unsupported import format: {format}")
        
        # Import configuration values
        for key, config_dict in data.get('config', {}).items():
            config_value = ConfigValue(
                key=config_dict['key'],
                value=config_dict['value'],
                source=ConfigSource(config_dict['source']),
                environment=Environment(config_dict['environment']),
                encrypted=config_dict['encrypted'],
                last_updated=datetime.fromisoformat(config_dict['last_updated']),
                expires_at=datetime.fromisoformat(config_dict['expires_at']) if config_dict['expires_at'] else None,
                metadata=config_dict['metadata']
            )
            self._config[key] = config_value
        
        # Import feature flags
        for name, flag_dict in data.get('feature_flags', {}).items():
            feature_flag = FeatureFlag(
                name=flag_dict['name'],
                enabled=flag_dict['enabled'],
                environment=Environment(flag_dict['environment']),
                rollout_percentage=flag_dict['rollout_percentage'],
                user_groups=flag_dict['user_groups'],
                conditions=flag_dict['conditions'],
                created_at=datetime.fromisoformat(flag_dict['created_at']),
                updated_at=datetime.fromisoformat(flag_dict['updated_at']),
                expires_at=datetime.fromisoformat(flag_dict['expires_at']) if flag_dict['expires_at'] else None
            )
            self._feature_flags[name] = feature_flag
        
        self._logger.info("Configuration imported successfully")
    
    def _detect_environment(self) -> Environment:
        """Detect current environment."""
        env = os.getenv('ENVIRONMENT', 'development').lower()
        
        try:
            return Environment(env)
        except ValueError:
            self._logger.warning(f"Unknown environment '{env}', using development")
            return Environment.DEVELOPMENT
    
    def _load_configuration(self) -> None:
        """Load configuration from various sources."""
        # Load from environment variables
        self._load_from_environment()
        
        # Load from configuration files
        self._load_from_files()
        
        # Load from secrets
        self._load_from_secrets()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        for key, value in os.environ.items():
            if key.startswith('APP_'):
                config_key = key[4:].lower()
                self.set(config_key, value, ConfigSource.ENVIRONMENT)
    
    def _load_from_files(self) -> None:
        """Load configuration from files."""
        config_dir = Path(self._config_path)
        
        if not config_dir.exists():
            return
        
        # Load base configuration
        base_config_file = config_dir / "config.yaml"
        if base_config_file.exists():
            self._load_yaml_file(base_config_file)
        
        # Load environment-specific configuration
        env_config_file = config_dir / f"config.{self._environment.value}.yaml"
        if env_config_file.exists():
            self._load_yaml_file(env_config_file)
    
    def _load_yaml_file(self, file_path: Path) -> None:
        """Load configuration from YAML file."""
        try:
            with open(file_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            for key, value in config_data.items():
                self.set(key, value, ConfigSource.FILE)
            
            self._logger.info(f"Loaded configuration from {file_path}")
            
        except Exception as e:
            self._logger.error(f"Failed to load configuration from {file_path}: {e}")
    
    def _load_from_secrets(self) -> None:
        """Load configuration from secrets."""
        # This would typically load from a secrets management service
        # For now, we'll load from environment variables with SECRET_ prefix
        for key, value in os.environ.items():
            if key.startswith('SECRET_'):
                secret_key = key[7:].lower()
                self.set_secret(secret_key, value)
    
    def _encrypt_value(self, value: Any) -> str:
        """Encrypt a configuration value."""
        # This is a placeholder for encryption
        # In a real implementation, you would use proper encryption
        return f"encrypted:{value}"
    
    def _decrypt_value(self, value: str) -> Any:
        """Decrypt a configuration value."""
        # This is a placeholder for decryption
        # In a real implementation, you would use proper decryption
        if value.startswith("encrypted:"):
            return value[10:]
        return value
    
    def _notify_watchers(self, key: str, value: Any) -> None:
        """Notify configuration watchers."""
        for watcher in self._watchers:
            try:
                watcher(key, value)
            except Exception as e:
                self._logger.error(f"Error in configuration watcher: {e}")


# Global configuration manager instance
config_manager = ConfigurationManager()


# Decorators for easy configuration access
def config_value(key: str, default: Any = None, decrypt: bool = False):
    """Decorator to inject configuration value."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            value = config_manager.get(key, default, decrypt)
            return await func(value, *args, **kwargs)
        return wrapper
    return decorator


def feature_flag(name: str, user_id: Optional[str] = None, user_groups: Optional[List[str]] = None):
    """Decorator to check feature flag."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if config_manager.is_feature_enabled(name, user_id, user_groups):
                return await func(*args, **kwargs)
            else:
                raise Exception(f"Feature '{name}' is not enabled")
        return wrapper
    return decorator 