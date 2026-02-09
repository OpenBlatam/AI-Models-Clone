#!/usr/bin/env python3
"""
Centralized Configuration Manager
Environment-aware configuration management with type-safe validation
"""

import os
import json
import yaml
import toml
import logging
from typing import Dict, List, Any, Optional, Union, Type, TypeVar
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import asyncio
import threading
import time
from functools import lru_cache
from pydantic import BaseModel, Field, ValidationError
import redis
import aioredis

logger = logging.getLogger(__name__)

T = TypeVar('T')

class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class ConfigSource(Enum):
    """Configuration sources."""
    ENV_VARS = "env_vars"
    FILE = "file"
    DATABASE = "database"
    REMOTE = "remote"

@dataclass
class ConfigValue:
    """Configuration value with metadata."""
    value: Any
    source: ConfigSource
    timestamp: float
    environment: Environment
    validated: bool = False
    encrypted: bool = False

class ConfigSection(BaseModel):
    """Base configuration section."""
    class Config:
        extra = "forbid"

class DatabaseConfig(ConfigSection):
    """Database configuration."""
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    max_connections: int = Field(default=20, description="Maximum connections")
    min_connections: int = Field(default=5, description="Minimum connections")
    connection_timeout: int = Field(default=30, description="Connection timeout")
    pool_timeout: int = Field(default=30, description="Pool timeout")
    ssl_mode: str = Field(default="prefer", description="SSL mode")

class RedisConfig(ConfigSection):
    """Redis configuration."""
    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    database: int = Field(default=0, description="Redis database")
    password: Optional[str] = Field(default=None, description="Redis password")
    max_connections: int = Field(default=20, description="Maximum connections")
    connection_timeout: int = Field(default=30, description="Connection timeout")
    decode_responses: bool = Field(default=True, description="Decode responses")

class APIConfig(ConfigSection):
    """API configuration."""
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    workers: int = Field(default=4, description="Number of workers")
    reload: bool = Field(default=False, description="Auto reload")
    log_level: str = Field(default="info", description="Log level")
    cors_origins: List[str] = Field(default=["*"], description="CORS origins")
    rate_limit: int = Field(default=1000, description="Rate limit per minute")

class SecurityConfig(ConfigSection):
    """Security configuration."""
    secret_key: str = Field(..., description="Secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiry")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiry")
    bcrypt_rounds: int = Field(default=12, description="BCrypt rounds")

class LoggingConfig(ConfigSection):
    """Logging configuration."""
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    file_path: Optional[str] = Field(default=None, description="Log file path")
    max_size: int = Field(default=10485760, description="Max log file size")
    backup_count: int = Field(default=5, description="Number of backup files")

class PerformanceConfig(ConfigSection):
    """Performance configuration."""
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    max_memory_usage: int = Field(default=1073741824, description="Max memory usage in bytes")
    gc_threshold: float = Field(default=0.8, description="Garbage collection threshold")
    connection_pool_size: int = Field(default=100, description="Connection pool size")
    batch_size: int = Field(default=1000, description="Default batch size")

class CentralizedConfigManager:
    """
    Centralized configuration manager with environment-aware settings.
    """
    
    def __init__(self, environment: Environment = None):
        self.environment = environment or self._detect_environment()
        self.config_cache: Dict[str, ConfigValue] = {}
        self.config_sections: Dict[str, ConfigSection] = {}
        self.watchers: Dict[str, List[callable]] = {}
        self.config_file_paths: List[Path] = []
        self.redis_client: Optional[aioredis.Redis] = None
        self._lock = threading.Lock()
        self._load_configuration()
    
    def _detect_environment(self) -> Environment:
        """Detect current environment."""
        env_var = os.getenv("ENVIRONMENT", "").lower()
        
        if env_var in ["prod", "production"]:
            return Environment.PRODUCTION
        elif env_var in ["stage", "staging"]:
            return Environment.STAGING
        elif env_var in ["test", "testing"]:
            return Environment.TESTING
        else:
            return Environment.DEVELOPMENT
    
    def _load_configuration(self):
        """Load configuration from all sources."""
        logger.info(f"Loading configuration for environment: {self.environment.value}")
        
        # Load from environment variables
        self._load_from_env_vars()
        
        # Load from configuration files
        self._load_from_files()
        
        # Initialize configuration sections
        self._initialize_config_sections()
        
        # Start configuration monitoring
        self._start_config_monitoring()
    
    def _load_from_env_vars(self):
        """Load configuration from environment variables."""
        env_prefix = f"{self.environment.value.upper()}_"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                self.config_cache[config_key] = ConfigValue(
                    value=self._parse_value(value),
                    source=ConfigSource.ENV_VARS,
                    timestamp=time.time(),
                    environment=self.environment
                )
    
    def _load_from_files(self):
        """Load configuration from files."""
        config_paths = [
            Path("config.yaml"),
            Path("config.yml"),
            Path("config.json"),
            Path("config.toml"),
            Path(f"config.{self.environment.value}.yaml"),
            Path(f"config.{self.environment.value}.yml"),
            Path(f"config.{self.environment.value}.json"),
            Path(f"config.{self.environment.value}.toml"),
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                self._load_config_file(config_path)
                self.config_file_paths.append(config_path)
    
    def _load_config_file(self, file_path: Path):
        """Load configuration from a specific file."""
        try:
            if file_path.suffix in ['.yaml', '.yml']:
                with open(file_path, 'r') as f:
                    config_data = yaml.safe_load(f)
            elif file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    config_data = json.load(f)
            elif file_path.suffix == '.toml':
                with open(file_path, 'r') as f:
                    config_data = toml.load(f)
            else:
                return
            
            # Load environment-specific configuration
            env_config = config_data.get(self.environment.value, {})
            global_config = config_data.get('global', {})
            
            # Merge configurations (environment-specific overrides global)
            merged_config = {**global_config, **env_config}
            
            for key, value in merged_config.items():
                self.config_cache[key] = ConfigValue(
                    value=value,
                    source=ConfigSource.FILE,
                    timestamp=time.time(),
                    environment=self.environment
                )
            
            logger.info(f"Loaded configuration from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {e}")
    
    def _initialize_config_sections(self):
        """Initialize configuration sections."""
        # Database configuration
        db_config = DatabaseConfig(
            host=self.get("database.host", "localhost"),
            port=self.get("database.port", 5432),
            database=self.get("database.name", "blatam_academy"),
            username=self.get("database.username", "postgres"),
            password=self.get("database.password", ""),
            max_connections=self.get("database.max_connections", 20),
            min_connections=self.get("database.min_connections", 5),
            connection_timeout=self.get("database.connection_timeout", 30),
            pool_timeout=self.get("database.pool_timeout", 30),
            ssl_mode=self.get("database.ssl_mode", "prefer")
        )
        self.config_sections["database"] = db_config
        
        # Redis configuration
        redis_config = RedisConfig(
            host=self.get("redis.host", "localhost"),
            port=self.get("redis.port", 6379),
            database=self.get("redis.database", 0),
            password=self.get("redis.password"),
            max_connections=self.get("redis.max_connections", 20),
            connection_timeout=self.get("redis.connection_timeout", 30),
            decode_responses=self.get("redis.decode_responses", True)
        )
        self.config_sections["redis"] = redis_config
        
        # API configuration
        api_config = APIConfig(
            host=self.get("api.host", "0.0.0.0"),
            port=self.get("api.port", 8000),
            workers=self.get("api.workers", 4),
            reload=self.get("api.reload", self.environment == Environment.DEVELOPMENT),
            log_level=self.get("api.log_level", "info"),
            cors_origins=self.get("api.cors_origins", ["*"]),
            rate_limit=self.get("api.rate_limit", 1000)
        )
        self.config_sections["api"] = api_config
        
        # Security configuration
        security_config = SecurityConfig(
            secret_key=self.get("security.secret_key", "your-secret-key-change-this"),
            algorithm=self.get("security.algorithm", "HS256"),
            access_token_expire_minutes=self.get("security.access_token_expire_minutes", 30),
            refresh_token_expire_days=self.get("security.refresh_token_expire_days", 7),
            bcrypt_rounds=self.get("security.bcrypt_rounds", 12)
        )
        self.config_sections["security"] = security_config
        
        # Logging configuration
        logging_config = LoggingConfig(
            level=self.get("logging.level", "INFO"),
            format=self.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_path=self.get("logging.file_path"),
            max_size=self.get("logging.max_size", 10485760),
            backup_count=self.get("logging.backup_count", 5)
        )
        self.config_sections["logging"] = logging_config
        
        # Performance configuration
        performance_config = PerformanceConfig(
            cache_ttl=self.get("performance.cache_ttl", 3600),
            max_memory_usage=self.get("performance.max_memory_usage", 1073741824),
            gc_threshold=self.get("performance.gc_threshold", 0.8),
            connection_pool_size=self.get("performance.connection_pool_size", 100),
            batch_size=self.get("performance.batch_size", 1000)
        )
        self.config_sections["performance"] = performance_config
    
    def _start_config_monitoring(self):
        """Start monitoring configuration files for changes."""
        def monitor_config_files():
            while True:
                try:
                    for config_path in self.config_file_paths:
                        if config_path.exists():
                            current_mtime = config_path.stat().st_mtime
                            cached_mtime = getattr(config_path, '_last_mtime', 0)
                            
                            if current_mtime > cached_mtime:
                                logger.info(f"Configuration file {config_path} changed, reloading...")
                                self._load_config_file(config_path)
                                self._initialize_config_sections()
                                self._notify_watchers("file_change", config_path)
                                config_path._last_mtime = current_mtime
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    logger.error(f"Error monitoring configuration files: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=monitor_config_files, daemon=True)
        thread.start()
    
    def _parse_value(self, value: str) -> Any:
        """Parse string value to appropriate type."""
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        elif value.isdigit():
            return int(value)
        elif value.replace('.', '').isdigit():
            return float(value)
        elif value.startswith('[') and value.endswith(']'):
            try:
                return json.loads(value)
            except:
                return value
        elif value.startswith('{') and value.endswith('}'):
            try:
                return json.loads(value)
            except:
                return value
        else:
            return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        # Check cache first
        if key in self.config_cache:
            return self.config_cache[key].value
        
        # Check nested keys (e.g., "database.host")
        if '.' in key:
            section, subkey = key.split('.', 1)
            if section in self.config_sections:
                section_config = self.config_sections[section]
                if hasattr(section_config, subkey):
                    return getattr(section_config, subkey)
        
        return default
    
    def set(self, key: str, value: Any, source: ConfigSource = ConfigSource.ENV_VARS):
        """Set configuration value."""
        with self._lock:
            self.config_cache[key] = ConfigValue(
                value=value,
                source=source,
                timestamp=time.time(),
                environment=self.environment
            )
            self._notify_watchers("config_change", key, value)
    
    def get_section(self, section_name: str) -> Optional[ConfigSection]:
        """Get configuration section."""
        return self.config_sections.get(section_name)
    
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate all configuration sections."""
        errors = {}
        
        for section_name, section_config in self.config_sections.items():
            try:
                # Validate using Pydantic
                section_config.model_validate(section_config.dict())
            except ValidationError as e:
                errors[section_name] = [str(error) for error in e.errors()]
        
        return errors
    
    def export_config(self, format: str = "json") -> str:
        """Export configuration in specified format."""
        config_data = {}
        
        for section_name, section_config in self.config_sections.items():
            config_data[section_name] = section_config.dict()
        
        if format == "json":
            return json.dumps(config_data, indent=2)
        elif format == "yaml":
            return yaml.dump(config_data, default_flow_style=False)
        elif format == "toml":
            return toml.dumps(config_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def watch_config(self, key: str, callback: callable):
        """Watch for configuration changes."""
        if key not in self.watchers:
            self.watchers[key] = []
        self.watchers[key].append(callback)
    
    def _notify_watchers(self, event: str, *args):
        """Notify configuration watchers."""
        for key, callbacks in self.watchers.items():
            for callback in callbacks:
                try:
                    callback(event, *args)
                except Exception as e:
                    logger.error(f"Error in configuration watcher: {e}")
    
    @lru_cache(maxsize=128)
    def get_cached(self, key: str, default: Any = None) -> Any:
        """Get cached configuration value."""
        return self.get(key, default)
    
    async def load_from_redis(self, redis_key: str = "config"):
        """Load configuration from Redis."""
        if not self.redis_client:
            return
        
        try:
            config_data = await self.redis_client.get(redis_key)
            if config_data:
                config_dict = json.loads(config_data)
                for key, value in config_dict.items():
                    self.set(key, value, ConfigSource.DATABASE)
                logger.info("Configuration loaded from Redis")
        except Exception as e:
            logger.error(f"Error loading configuration from Redis: {e}")
    
    async def save_to_redis(self, redis_key: str = "config"):
        """Save configuration to Redis."""
        if not self.redis_client:
            return
        
        try:
            config_data = {}
            for key, config_value in self.config_cache.items():
                config_data[key] = config_value.value
            
            await self.redis_client.set(redis_key, json.dumps(config_data))
            logger.info("Configuration saved to Redis")
        except Exception as e:
            logger.error(f"Error saving configuration to Redis: {e}")

# Global configuration manager instance
config_manager = CentralizedConfigManager()

def get_config_manager() -> CentralizedConfigManager:
    """Get the global configuration manager instance."""
    return config_manager

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    return config_manager.get(key, default)

def set_config(key: str, value: Any):
    """Set configuration value."""
    config_manager.set(key, value)

def get_config_section(section_name: str) -> Optional[ConfigSection]:
    """Get configuration section."""
    return config_manager.get_section(section_name) 