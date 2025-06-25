"""
Production Configuration Management for Onyx Features.

Centralized configuration using pydantic, decouple, and structured logging.
"""

import os
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from enum import Enum

from pydantic import BaseSettings, Field, validator, root_validator
from decouple import config, Csv
import structlog
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class RedisConfig(BaseSettings):
    """Redis configuration for caching and sessions."""
    host: str = Field(default=config("REDIS_HOST", default="localhost"))
    port: int = Field(default=config("REDIS_PORT", default=6379, cast=int))
    db: int = Field(default=config("REDIS_DB", default=0, cast=int))
    password: Optional[str] = Field(default=config("REDIS_PASSWORD", default=None))
    ssl: bool = Field(default=config("REDIS_SSL", default=False, cast=bool))
    max_connections: int = Field(default=config("REDIS_MAX_CONNECTIONS", default=20, cast=int))
    socket_timeout: float = Field(default=config("REDIS_SOCKET_TIMEOUT", default=30.0, cast=float))
    
    class Config:
        env_prefix = "REDIS_"


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    url: str = Field(default=config("DATABASE_URL", default="sqlite:///./onyx.db"))
    pool_size: int = Field(default=config("DB_POOL_SIZE", default=20, cast=int))
    max_overflow: int = Field(default=config("DB_MAX_OVERFLOW", default=30, cast=int))
    pool_timeout: int = Field(default=config("DB_POOL_TIMEOUT", default=30, cast=int))
    pool_recycle: int = Field(default=config("DB_POOL_RECYCLE", default=3600, cast=int))
    echo: bool = Field(default=config("DB_ECHO", default=False, cast=bool))
    
    class Config:
        env_prefix = "DB_"


class ImageProcessingConfig(BaseSettings):
    """Image processing configuration."""
    max_file_size_mb: int = Field(default=config("IMG_MAX_FILE_SIZE_MB", default=100, cast=int))
    max_vision_file_size_mb: int = Field(default=config("IMG_MAX_VISION_SIZE_MB", default=20, cast=int))
    max_dimension: int = Field(default=config("IMG_MAX_DIMENSION", default=1024, cast=int))
    jpeg_quality: int = Field(default=config("IMG_JPEG_QUALITY", default=85, cast=int), ge=1, le=100)
    webp_quality: int = Field(default=config("IMG_WEBP_QUALITY", default=80, cast=int), ge=1, le=100)
    enable_optimization: bool = Field(default=config("IMG_ENABLE_OPTIMIZATION", default=True, cast=bool))
    strict_validation: bool = Field(default=config("IMG_STRICT_VALIDATION", default=True, cast=bool))
    use_magic_bytes: bool = Field(default=config("IMG_USE_MAGIC_BYTES", default=True, cast=bool))
    storage_timeout: int = Field(default=config("IMG_STORAGE_TIMEOUT", default=30, cast=int))
    
    @validator('jpeg_quality', 'webp_quality')
    def validate_quality(cls, v):
        if not 1 <= v <= 100:
            raise ValueError("Quality must be between 1 and 100")
        return v
    
    class Config:
        env_prefix = "IMG_"


class KeyMessagesConfig(BaseSettings):
    """Key messages configuration."""
    max_message_length: int = Field(default=config("MSG_MAX_LENGTH", default=10000, cast=int))
    max_messages_per_batch: int = Field(default=config("MSG_MAX_BATCH", default=100, cast=int))
    cache_ttl: int = Field(default=config("MSG_CACHE_TTL", default=3600, cast=int))
    default_timeout: int = Field(default=config("MSG_DEFAULT_TIMEOUT", default=30, cast=int))
    enable_compression: bool = Field(default=config("MSG_ENABLE_COMPRESSION", default=True, cast=bool))
    enable_encryption: bool = Field(default=config("MSG_ENABLE_ENCRYPTION", default=False, cast=bool))
    
    @validator('max_message_length')
    def validate_message_length(cls, v):
        if v > 50000:
            raise ValueError("Message length cannot exceed 50000")
        return v
    
    class Config:
        env_prefix = "MSG_"


class MonitoringConfig(BaseSettings):
    """Monitoring and metrics configuration."""
    enable_prometheus: bool = Field(default=config("MONITORING_PROMETHEUS", default=True, cast=bool))
    enable_sentry: bool = Field(default=config("MONITORING_SENTRY", default=False, cast=bool))
    sentry_dsn: Optional[str] = Field(default=config("SENTRY_DSN", default=None))
    metrics_port: int = Field(default=config("METRICS_PORT", default=8000, cast=int))
    health_check_interval: int = Field(default=config("HEALTH_CHECK_INTERVAL", default=60, cast=int))
    
    class Config:
        env_prefix = "MONITORING_"


class SecurityConfig(BaseSettings):
    """Security configuration."""
    secret_key: str = Field(default=config("SECRET_KEY", default="your-secret-key-change-in-production"))
    jwt_algorithm: str = Field(default=config("JWT_ALGORITHM", default="HS256"))
    jwt_expiration_hours: int = Field(default=config("JWT_EXPIRATION_HOURS", default=24, cast=int))
    encryption_key: Optional[str] = Field(default=config("ENCRYPTION_KEY", default=None))
    enable_cors: bool = Field(default=config("ENABLE_CORS", default=True, cast=bool))
    allowed_origins: List[str] = Field(default=config("ALLOWED_ORIGINS", default="*", cast=Csv()))
    
    class Config:
        env_prefix = "SECURITY_"


class OnyxConfig(BaseSettings):
    """Main configuration class combining all settings."""
    
    # Environment settings
    environment: Environment = Field(default=config("ENVIRONMENT", default=Environment.DEVELOPMENT))
    debug: bool = Field(default=config("DEBUG", default=False, cast=bool))
    log_level: LogLevel = Field(default=config("LOG_LEVEL", default=LogLevel.INFO))
    
    # Application settings
    app_name: str = Field(default=config("APP_NAME", default="Onyx Features"))
    app_version: str = Field(default=config("APP_VERSION", default="1.0.0"))
    api_prefix: str = Field(default=config("API_PREFIX", default="/api/v1"))
    
    # Component configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    image_processing: ImageProcessingConfig = Field(default_factory=ImageProcessingConfig)
    key_messages: KeyMessagesConfig = Field(default_factory=KeyMessagesConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    # Performance settings
    enable_async: bool = Field(default=config("ENABLE_ASYNC", default=True, cast=bool))
    max_workers: int = Field(default=config("MAX_WORKERS", default=4, cast=int))
    request_timeout: int = Field(default=config("REQUEST_TIMEOUT", default=30, cast=int))
    
    @root_validator
    def validate_production_settings(cls, values):
        """Validate production-specific settings."""
        env = values.get('environment')
        if env == Environment.PRODUCTION:
            # Ensure secure settings in production
            if values.get('debug', False):
                logger.warning("Debug mode should be disabled in production")
            
            security = values.get('security', {})
            if isinstance(security, SecurityConfig):
                if security.secret_key == "your-secret-key-change-in-production":
                    raise ValueError("Secret key must be changed in production")
        
        return values
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global configuration instance
_config: Optional[OnyxConfig] = None


def get_config() -> OnyxConfig:
    """
    Get the global configuration instance.
    
    Returns:
        OnyxConfig: Configuration instance
    """
    global _config
    if _config is None:
        _config = OnyxConfig()
        logger.info("Configuration loaded", environment=_config.environment.value)
    return _config


def reload_config() -> OnyxConfig:
    """
    Reload the configuration from environment variables.
    
    Returns:
        OnyxConfig: New configuration instance
    """
    global _config
    _config = OnyxConfig()
    logger.info("Configuration reloaded", environment=_config.environment.value)
    return _config


# Prometheus metrics setup
if get_config().monitoring.enable_prometheus:
    registry = CollectorRegistry()
    
    # Define metrics
    request_count = Counter(
        'onyx_requests_total',
        'Total number of requests',
        ['method', 'endpoint', 'status'],
        registry=registry
    )
    
    request_duration = Histogram(
        'onyx_request_duration_seconds',
        'Request duration in seconds',
        ['method', 'endpoint'],
        registry=registry
    )
    
    active_connections = Gauge(
        'onyx_active_connections',
        'Number of active connections',
        registry=registry
    )
    
    cache_hits = Counter(
        'onyx_cache_hits_total',
        'Total cache hits',
        ['cache_type'],
        registry=registry
    )
    
    cache_misses = Counter(
        'onyx_cache_misses_total',
        'Total cache misses',
        ['cache_type'],
        registry=registry
    )


# Export main components
__all__ = [
    "OnyxConfig",
    "Environment",
    "LogLevel",
    "DatabaseConfig",
    "RedisConfig",
    "ImageProcessingConfig",
    "KeyMessagesConfig",
    "MonitoringConfig",
    "SecurityConfig",
    "get_config",
    "reload_config",
    "logger"
]


# Initialize configuration
logger.info("Configuration module initialized", version=get_config().app_version) 