#!/usr/bin/env python3
"""
Advanced Configuration System
============================

Advanced configuration management with environment-based settings,
validation, and multiple deployment profiles.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
from pydantic import BaseSettings, validator, Field


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseType(str, Enum):
    """Database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MOCK = "mock"


class CacheType(str, Enum):
    """Cache types."""
    REDIS = "redis"
    MEMORY = "memory"
    NONE = "none"


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    
    type: DatabaseType = DatabaseType.POSTGRESQL
    host: str = "localhost"
    port: int = 5432
    database: str = "ultra_library_v7"
    username: str = "user"
    password: str = "password"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    
    @property
    def connection_string(self) -> str:
        """Get database connection string."""
        if self.type == DatabaseType.POSTGRESQL:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == DatabaseType.MYSQL:
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == DatabaseType.SQLITE:
            return f"sqlite:///{self.database}.db"
        else:
            return "mock://"


@dataclass
class CacheConfig:
    """Cache configuration."""
    
    type: CacheType = CacheType.REDIS
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    max_connections: int = 10
    ttl: int = 3600  # seconds
    key_prefix: str = "ultra_library_v7:"
    
    @property
    def connection_string(self) -> str:
        """Get cache connection string."""
        if self.type == CacheType.REDIS:
            auth = f":{self.password}@" if self.password else ""
            return f"redis://{auth}{self.host}:{self.port}/{self.database}"
        else:
            return "memory://"


@dataclass
class APIConfig:
    """API configuration."""
    
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False
    log_level: LogLevel = LogLevel.INFO
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_per_minute: int = 60
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    timeout: int = 30
    enable_docs: bool = True
    enable_metrics: bool = True


@dataclass
class SecurityConfig:
    """Security configuration."""
    
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    bcrypt_rounds: int = 12
    enable_rate_limiting: bool = True
    enable_cors: bool = True
    allowed_hosts: List[str] = field(default_factory=lambda: ["*"])
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    
    enable_prometheus: bool = True
    prometheus_port: int = 9090
    enable_health_checks: bool = True
    health_check_interval: int = 30
    enable_logging: bool = True
    log_file: Optional[str] = None
    log_rotation: str = "1 day"
    log_retention: str = "30 days"
    enable_tracing: bool = False
    tracing_endpoint: Optional[str] = None


@dataclass
class OptimizationConfig:
    """Optimization configuration."""
    
    default_strategy: str = "default"
    enable_quantum: bool = True
    enable_neuromorphic: bool = True
    enable_federated: bool = True
    enable_ai_healing: bool = True
    max_concurrent_requests: int = 100
    request_timeout: int = 60
    enable_caching: bool = True
    cache_ttl: int = 3600
    enable_compression: bool = True
    compression_level: int = 6


@dataclass
class SystemConfig:
    """System configuration."""
    
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    app_name: str = "Ultra Library Optimization V7"
    app_version: str = "7.0.0"
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = field(default_factory=lambda: Path("data"))
    temp_dir: Path = field(default_factory=lambda: Path("temp"))
    backup_dir: Path = field(default_factory=lambda: Path("backups"))
    
    def __post_init__(self):
        """Create directories if they don't exist."""
        self.data_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)


class Settings(BaseSettings):
    """Main settings class with Pydantic validation."""
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Database
    database_type: DatabaseType = DatabaseType.POSTGRESQL
    database_host: str = Field(default="localhost", description="Database host")
    database_port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    database_name: str = Field(default="ultra_library_v7", description="Database name")
    database_user: str = Field(default="user", description="Database user")
    database_password: str = Field(default="password", description="Database password")
    database_pool_size: int = Field(default=10, ge=1, le=100, description="Database pool size")
    
    # Cache
    cache_type: CacheType = CacheType.REDIS
    cache_host: str = Field(default="localhost", description="Cache host")
    cache_port: int = Field(default=6379, ge=1, le=65535, description="Cache port")
    cache_password: Optional[str] = Field(default=None, description="Cache password")
    cache_database: int = Field(default=0, ge=0, le=15, description="Cache database")
    
    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, ge=1, le=65535, description="API port")
    api_workers: int = Field(default=4, ge=1, le=32, description="API workers")
    api_rate_limit: int = Field(default=60, ge=1, le=10000, description="API rate limit per minute")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", description="Secret key")
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440, description="Access token expire minutes")
    
    # Monitoring
    enable_prometheus: bool = Field(default=True, description="Enable Prometheus metrics")
    prometheus_port: int = Field(default=9090, ge=1, le=65535, description="Prometheus port")
    
    # Optimization
    default_optimization_strategy: str = Field(default="default", description="Default optimization strategy")
    enable_quantum: bool = Field(default=True, description="Enable quantum optimization")
    enable_neuromorphic: bool = Field(default=True, description="Enable neuromorphic optimization")
    enable_federated: bool = Field(default=True, description="Enable federated learning")
    enable_ai_healing: bool = Field(default=True, description="Enable AI self-healing")
    
    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        """Validate secret key."""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @validator('default_optimization_strategy')
    def validate_optimization_strategy(cls, v):
        """Validate optimization strategy."""
        valid_strategies = [
            "default", "quantum", "neuromorphic", "federated", "hybrid",
            "quantum_internet", "neuromorphic_hardware", "federated_quantum",
            "quantum_safe", "ai_self_healing", "edge_iot", "multimodal",
            "collaborative", "analytics_dashboard"
        ]
        if v not in valid_strategies:
            raise ValueError(f"Invalid optimization strategy: {v}")
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class ConfigurationManager:
    """Advanced configuration manager."""
    
    def __init__(self, environment: Environment = None):
        self.environment = environment or Environment.DEVELOPMENT
        self.settings = Settings()
        self._config_cache: Dict[str, Any] = {}
        
        # Initialize configuration
        self._load_environment_config()
        self._validate_configuration()
        self._setup_logging()
    
    def _load_environment_config(self):
        """Load environment-specific configuration."""
        env_file = f"config/{self.environment.value}.yaml"
        if Path(env_file).exists():
            with open(env_file, 'r') as f:
                env_config = yaml.safe_load(f)
                self._config_cache.update(env_config)
    
    def _validate_configuration(self):
        """Validate configuration."""
        # Validate database configuration
        if self.settings.database_type == DatabaseType.POSTGRESQL:
            if not self.settings.database_host or not self.settings.database_name:
                raise ValueError("PostgreSQL requires host and database name")
        
        # Validate cache configuration
        if self.settings.cache_type == CacheType.REDIS:
            if not self.settings.cache_host:
                raise ValueError("Redis requires host")
        
        # Validate API configuration
        if self.settings.api_port < 1 or self.settings.api_port > 65535:
            raise ValueError("Invalid API port")
        
        # Validate security configuration
        if len(self.settings.secret_key) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
                'detailed': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.settings.log_level.upper(),
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['console'],
                    'level': self.settings.log_level.upper(),
                    'propagate': False
                }
            }
        }
        
        # Add file handler if log file is specified
        if self.settings.log_file:
            log_config['handlers']['file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': self.settings.log_level.upper(),
                'formatter': 'detailed',
                'filename': self.settings.log_file,
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 5
            }
            log_config['loggers']['']['handlers'].append('file')
        
        logging.config.dictConfig(log_config)
    
    @property
    def database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        return DatabaseConfig(
            type=self.settings.database_type,
            host=self.settings.database_host,
            port=self.settings.database_port,
            database=self.settings.database_name,
            username=self.settings.database_user,
            password=self.settings.database_password,
            pool_size=self.settings.database_pool_size
        )
    
    @property
    def cache_config(self) -> CacheConfig:
        """Get cache configuration."""
        return CacheConfig(
            type=self.settings.cache_type,
            host=self.settings.cache_host,
            port=self.settings.cache_port,
            password=self.settings.cache_password,
            database=self.settings.cache_database
        )
    
    @property
    def api_config(self) -> APIConfig:
        """Get API configuration."""
        return APIConfig(
            host=self.settings.api_host,
            port=self.settings.api_port,
            workers=self.settings.api_workers,
            rate_limit_per_minute=self.settings.api_rate_limit,
            reload=self.environment == Environment.DEVELOPMENT,
            log_level=self.settings.log_level
        )
    
    @property
    def security_config(self) -> SecurityConfig:
        """Get security configuration."""
        return SecurityConfig(
            secret_key=self.settings.secret_key,
            access_token_expire_minutes=self.settings.access_token_expire_minutes
        )
    
    @property
    def monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration."""
        return MonitoringConfig(
            enable_prometheus=self.settings.enable_prometheus,
            prometheus_port=self.settings.prometheus_port,
            log_file=self.settings.log_file
        )
    
    @property
    def optimization_config(self) -> OptimizationConfig:
        """Get optimization configuration."""
        return OptimizationConfig(
            default_strategy=self.settings.default_optimization_strategy,
            enable_quantum=self.settings.enable_quantum,
            enable_neuromorphic=self.settings.enable_neuromorphic,
            enable_federated=self.settings.enable_federated,
            enable_ai_healing=self.settings.enable_ai_healing
        )
    
    @property
    def system_config(self) -> SystemConfig:
        """Get system configuration."""
        return SystemConfig(
            environment=self.environment,
            debug=self.settings.debug
        )
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self._config_cache.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config_cache[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'environment': self.environment.value,
            'database': self.database_config.__dict__,
            'cache': self.cache_config.__dict__,
            'api': self.api_config.__dict__,
            'security': self.security_config.__dict__,
            'monitoring': self.monitoring_config.__dict__,
            'optimization': self.optimization_config.__dict__,
            'system': self.system_config.__dict__,
            'custom': self._config_cache
        }
    
    def to_json(self) -> str:
        """Convert configuration to JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    def to_yaml(self) -> str:
        """Convert configuration to YAML."""
        return yaml.dump(self.to_dict(), default_flow_style=False, indent=2)
    
    def save_config(self, file_path: str) -> None:
        """Save configuration to file."""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            with open(file_path, 'w') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def load_config(self, file_path: str) -> None:
        """Load configuration from file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r') as f:
                config_data = json.load(f)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            with open(file_path, 'r') as f:
                config_data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Update configuration
        self._config_cache.update(config_data.get('custom', {}))
        
        # Update settings if provided
        if 'environment' in config_data:
            self.environment = Environment(config_data['environment'])
        
        # Revalidate configuration
        self._validate_configuration()
    
    def validate_database_connection(self) -> bool:
        """Validate database connection."""
        try:
            # This would typically test the actual database connection
            # For now, we'll just validate the configuration
            db_config = self.database_config
            if db_config.type == DatabaseType.POSTGRESQL:
                return bool(db_config.host and db_config.database)
            return True
        except Exception as e:
            logging.error(f"Database connection validation failed: {e}")
            return False
    
    def validate_cache_connection(self) -> bool:
        """Validate cache connection."""
        try:
            # This would typically test the actual cache connection
            # For now, we'll just validate the configuration
            cache_config = self.cache_config
            if cache_config.type == CacheType.REDIS:
                return bool(cache_config.host)
            return True
        except Exception as e:
            logging.error(f"Cache connection validation failed: {e}")
            return False
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information."""
        return {
            'environment': self.environment.value,
            'debug': self.settings.debug,
            'app_name': self.system_config.app_name,
            'app_version': self.system_config.app_version,
            'database_connected': self.validate_database_connection(),
            'cache_connected': self.validate_cache_connection(),
            'features_enabled': {
                'quantum': self.settings.enable_quantum,
                'neuromorphic': self.settings.enable_neuromorphic,
                'federated': self.settings.enable_federated,
                'ai_healing': self.settings.enable_ai_healing,
                'prometheus': self.settings.enable_prometheus
            }
        }


# Global configuration instance
config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get global configuration manager instance."""
    global config_manager
    if config_manager is None:
        config_manager = ConfigurationManager()
    return config_manager


def init_config(environment: Environment = None) -> ConfigurationManager:
    """Initialize configuration manager."""
    global config_manager
    config_manager = ConfigurationManager(environment)
    return config_manager


if __name__ == "__main__":
    # Example usage
    config = init_config(Environment.DEVELOPMENT)
    
    print("Configuration loaded successfully!")
    print(f"Environment: {config.environment}")
    print(f"Database: {config.database_config.connection_string}")
    print(f"Cache: {config.cache_config.connection_string}")
    print(f"API: {config.api_config.host}:{config.api_config.port}")
    
    # Save configuration
    config.save_config("config/current_config.json")
    print("Configuration saved to config/current_config.json") 