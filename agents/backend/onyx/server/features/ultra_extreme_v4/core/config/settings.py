"""
🚀 ULTRA-EXTREME SETTINGS V4
============================

Ultra-extreme configuration settings with:
- Environment-based configuration
- Advanced performance settings
- AI service configurations
- Database and cache settings
- Monitoring and security settings
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, Field, validator
from pydantic.types import SecretStr
from functools import lru_cache


class UltraExtremeSettings(BaseSettings):
    """Ultra-extreme configuration settings"""
    
    # ============================================================================
    # APPLICATION SETTINGS
    # ============================================================================
    
    # Basic app settings
    APP_NAME: str = Field(default="Ultra-Extreme V4", description="Application name")
    APP_VERSION: str = Field(default="4.0.0", description="Application version")
    APP_DESCRIPTION: str = Field(default="Ultra-Extreme Refactor V4", description="Application description")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="production", description="Environment (development, staging, production)")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=16, description="Number of workers")
    MAX_CONNECTIONS: int = Field(default=200, description="Maximum connections")
    BATCH_SIZE: int = Field(default=100, description="Batch processing size")
    
    # ============================================================================
    # DATABASE SETTINGS
    # ============================================================================
    
    # PostgreSQL settings
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    DATABASE_POOL_SIZE: int = Field(default=20, description="Database pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, description="Database max overflow")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, description="Database pool timeout")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, description="Database pool recycle")
    
    # Redis settings
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis URL")
    REDIS_POOL_SIZE: int = Field(default=50, description="Redis pool size")
    REDIS_MAX_CONNECTIONS: int = Field(default=100, description="Redis max connections")
    REDIS_TIMEOUT: int = Field(default=5, description="Redis timeout")
    
    # MongoDB settings (optional)
    MONGODB_URL: Optional[str] = Field(default=None, description="MongoDB URL")
    MONGODB_DATABASE: str = Field(default="ultra_extreme", description="MongoDB database name")
    
    # ============================================================================
    # AI SERVICES SETTINGS
    # ============================================================================
    
    # OpenAI settings
    OPENAI_API_KEY: SecretStr = Field(..., description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", description="OpenAI model")
    OPENAI_MAX_TOKENS: int = Field(default=4000, description="OpenAI max tokens")
    OPENAI_TEMPERATURE: float = Field(default=0.7, description="OpenAI temperature")
    OPENAI_TIMEOUT: int = Field(default=60, description="OpenAI timeout")
    OPENAI_RETRY_ATTEMPTS: int = Field(default=3, description="OpenAI retry attempts")
    
    # Anthropic settings
    ANTHROPIC_API_KEY: Optional[SecretStr] = Field(default=None, description="Anthropic API key")
    ANTHROPIC_MODEL: str = Field(default="claude-3-sonnet-20240229", description="Anthropic model")
    ANTHROPIC_MAX_TOKENS: int = Field(default=4000, description="Anthropic max tokens")
    ANTHROPIC_TEMPERATURE: float = Field(default=0.7, description="Anthropic temperature")
    ANTHROPIC_TIMEOUT: int = Field(default=60, description="Anthropic timeout")
    
    # HuggingFace settings
    HUGGINGFACE_TOKEN: Optional[SecretStr] = Field(default=None, description="HuggingFace token")
    HUGGINGFACE_MODEL: str = Field(default="microsoft/DialoGPT-medium", description="HuggingFace model")
    HUGGINGFACE_CACHE_DIR: str = Field(default="./models", description="HuggingFace cache directory")
    HUGGINGFACE_TIMEOUT: int = Field(default=60, description="HuggingFace timeout")
    
    # Local AI settings
    LOCAL_AI_ENABLED: bool = Field(default=False, description="Enable local AI")
    LOCAL_AI_MODEL_PATH: Optional[str] = Field(default=None, description="Local AI model path")
    LOCAL_AI_DEVICE: str = Field(default="cuda", description="Local AI device (cuda/cpu)")
    LOCAL_AI_BATCH_SIZE: int = Field(default=8, description="Local AI batch size")
    
    # ============================================================================
    # CACHE SETTINGS
    # ============================================================================
    
    # Cache configuration
    CACHE_ENABLED: bool = Field(default=True, description="Enable caching")
    CACHE_TTL: int = Field(default=3600, description="Cache TTL in seconds")
    CACHE_MAX_SIZE: int = Field(default=10000, description="Cache max size")
    CACHE_PREDICTIVE_ENABLED: bool = Field(default=True, description="Enable predictive caching")
    CACHE_MULTI_LEVEL: bool = Field(default=True, description="Enable multi-level caching")
    
    # Memory cache settings
    MEMORY_CACHE_SIZE: int = Field(default=1000, description="Memory cache size")
    MEMORY_CACHE_TTL: int = Field(default=300, description="Memory cache TTL")
    
    # Disk cache settings
    DISK_CACHE_ENABLED: bool = Field(default=True, description="Enable disk cache")
    DISK_CACHE_DIR: str = Field(default="./cache", description="Disk cache directory")
    DISK_CACHE_SIZE: int = Field(default=1000000, description="Disk cache size in bytes")
    
    # ============================================================================
    # PERFORMANCE SETTINGS
    # ============================================================================
    
    # Performance optimization
    PERFORMANCE_MONITORING: bool = Field(default=True, description="Enable performance monitoring")
    PERFORMANCE_PROFILING: bool = Field(default=False, description="Enable performance profiling")
    PERFORMANCE_METRICS_INTERVAL: int = Field(default=30, description="Performance metrics interval")
    
    # GPU settings
    GPU_ENABLED: bool = Field(default=True, description="Enable GPU acceleration")
    GPU_MEMORY_FRACTION: float = Field(default=0.8, description="GPU memory fraction")
    GPU_VISIBLE_DEVICES: Optional[str] = Field(default=None, description="GPU visible devices")
    
    # Async settings
    ASYNC_ENABLED: bool = Field(default=True, description="Enable async processing")
    ASYNC_MAX_CONCURRENT: int = Field(default=100, description="Max concurrent async tasks")
    ASYNC_TIMEOUT: int = Field(default=300, description="Async timeout")
    
    # ============================================================================
    # MONITORING SETTINGS
    # ============================================================================
    
    # Prometheus settings
    PROMETHEUS_ENABLED: bool = Field(default=True, description="Enable Prometheus monitoring")
    PROMETHEUS_PORT: int = Field(default=9090, description="Prometheus port")
    PROMETHEUS_PATH: str = Field(default="/metrics", description="Prometheus metrics path")
    
    # Sentry settings
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN")
    SENTRY_ENVIRONMENT: str = Field(default="production", description="Sentry environment")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.1, description="Sentry traces sample rate")
    
    # OpenTelemetry settings
    OTEL_ENABLED: bool = Field(default=True, description="Enable OpenTelemetry")
    OTEL_ENDPOINT: str = Field(default="http://localhost:4317", description="OpenTelemetry endpoint")
    OTEL_SERVICE_NAME: str = Field(default="ultra-extreme-v4", description="OpenTelemetry service name")
    
    # Health check settings
    HEALTH_CHECK_ENABLED: bool = Field(default=True, description="Enable health checks")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, description="Health check interval")
    HEALTH_CHECK_TIMEOUT: int = Field(default=10, description="Health check timeout")
    
    # ============================================================================
    # SECURITY SETTINGS
    # ============================================================================
    
    # Authentication settings
    AUTH_ENABLED: bool = Field(default=True, description="Enable authentication")
    SECRET_KEY: SecretStr = Field(..., description="Secret key for JWT")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRATION: int = Field(default=3600, description="JWT expiration in seconds")
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per minute")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    
    # CORS settings
    CORS_ENABLED: bool = Field(default=True, description="Enable CORS")
    CORS_ORIGINS: List[str] = Field(default=["*"], description="CORS origins")
    CORS_METHODS: List[str] = Field(default=["GET", "POST", "PUT", "DELETE"], description="CORS methods")
    CORS_HEADERS: List[str] = Field(default=["*"], description="CORS headers")
    
    # ============================================================================
    # LOGGING SETTINGS
    # ============================================================================
    
    # Logging configuration
    LOG_LEVEL: str = Field(default="INFO", description="Log level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json/text)")
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path")
    LOG_MAX_SIZE: int = Field(default=100, description="Log max size in MB")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Log backup count")
    
    # Structured logging
    STRUCTURED_LOGGING: bool = Field(default=True, description="Enable structured logging")
    LOG_CORRELATION_ID: bool = Field(default=True, description="Enable correlation ID logging")
    
    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    
    # Feature flags
    FEATURE_AI_GENERATION: bool = Field(default=True, description="Enable AI content generation")
    FEATURE_AI_OPTIMIZATION: bool = Field(default=True, description="Enable AI optimization")
    FEATURE_BATCH_PROCESSING: bool = Field(default=True, description="Enable batch processing")
    FEATURE_PREDICTIVE_CACHING: bool = Field(default=True, description="Enable predictive caching")
    FEATURE_REAL_TIME_MONITORING: bool = Field(default=True, description="Enable real-time monitoring")
    FEATURE_AUTO_SCALING: bool = Field(default=True, description="Enable auto-scaling")
    
    # ============================================================================
    # VALIDATORS
    # ============================================================================
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment setting"""
        if v not in ["development", "staging", "production"]:
            raise ValueError("Environment must be development, staging, or production")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @validator("WORKERS")
    def validate_workers(cls, v):
        """Validate number of workers"""
        if v < 1 or v > 100:
            raise ValueError("Workers must be between 1 and 100")
        return v
    
    @validator("BATCH_SIZE")
    def validate_batch_size(cls, v):
        """Validate batch size"""
        if v < 1 or v > 10000:
            raise ValueError("Batch size must be between 1 and 10000")
        return v
    
    # ============================================================================
    # METHODS
    # ============================================================================
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "pool_timeout": self.DATABASE_POOL_TIMEOUT,
            "pool_recycle": self.DATABASE_POOL_RECYCLE,
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        return {
            "url": self.REDIS_URL,
            "pool_size": self.REDIS_POOL_SIZE,
            "max_connections": self.REDIS_MAX_CONNECTIONS,
            "timeout": self.REDIS_TIMEOUT,
        }
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration"""
        return {
            "api_key": self.OPENAI_API_KEY.get_secret_value(),
            "model": self.OPENAI_MODEL,
            "max_tokens": self.OPENAI_MAX_TOKENS,
            "temperature": self.OPENAI_TEMPERATURE,
            "timeout": self.OPENAI_TIMEOUT,
            "retry_attempts": self.OPENAI_RETRY_ATTEMPTS,
        }
    
    def get_anthropic_config(self) -> Dict[str, Any]:
        """Get Anthropic configuration"""
        if not self.ANTHROPIC_API_KEY:
            return {}
        return {
            "api_key": self.ANTHROPIC_API_KEY.get_secret_value(),
            "model": self.ANTHROPIC_MODEL,
            "max_tokens": self.ANTHROPIC_MAX_TOKENS,
            "temperature": self.ANTHROPIC_TEMPERATURE,
            "timeout": self.ANTHROPIC_TIMEOUT,
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration"""
        return {
            "enabled": self.CACHE_ENABLED,
            "ttl": self.CACHE_TTL,
            "max_size": self.CACHE_MAX_SIZE,
            "predictive_enabled": self.CACHE_PREDICTIVE_ENABLED,
            "multi_level": self.CACHE_MULTI_LEVEL,
            "memory": {
                "size": self.MEMORY_CACHE_SIZE,
                "ttl": self.MEMORY_CACHE_TTL,
            },
            "disk": {
                "enabled": self.DISK_CACHE_ENABLED,
                "directory": self.DISK_CACHE_DIR,
                "size": self.DISK_CACHE_SIZE,
            },
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return {
            "monitoring": self.PERFORMANCE_MONITORING,
            "profiling": self.PERFORMANCE_PROFILING,
            "metrics_interval": self.PERFORMANCE_METRICS_INTERVAL,
            "gpu": {
                "enabled": self.GPU_ENABLED,
                "memory_fraction": self.GPU_MEMORY_FRACTION,
                "visible_devices": self.GPU_VISIBLE_DEVICES,
            },
            "async": {
                "enabled": self.ASYNC_ENABLED,
                "max_concurrent": self.ASYNC_MAX_CONCURRENT,
                "timeout": self.ASYNC_TIMEOUT,
            },
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return {
            "prometheus": {
                "enabled": self.PROMETHEUS_ENABLED,
                "port": self.PROMETHEUS_PORT,
                "path": self.PROMETHEUS_PATH,
            },
            "sentry": {
                "dsn": self.SENTRY_DSN,
                "environment": self.SENTRY_ENVIRONMENT,
                "traces_sample_rate": self.SENTRY_TRACES_SAMPLE_RATE,
            },
            "otel": {
                "enabled": self.OTEL_ENABLED,
                "endpoint": self.OTEL_ENDPOINT,
                "service_name": self.OTEL_SERVICE_NAME,
            },
            "health_check": {
                "enabled": self.HEALTH_CHECK_ENABLED,
                "interval": self.HEALTH_CHECK_INTERVAL,
                "timeout": self.HEALTH_CHECK_TIMEOUT,
            },
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "auth": {
                "enabled": self.AUTH_ENABLED,
                "secret_key": self.SECRET_KEY.get_secret_value(),
                "jwt_algorithm": self.JWT_ALGORITHM,
                "jwt_expiration": self.JWT_EXPIRATION,
            },
            "rate_limit": {
                "enabled": self.RATE_LIMIT_ENABLED,
                "requests": self.RATE_LIMIT_REQUESTS,
                "window": self.RATE_LIMIT_WINDOW,
            },
            "cors": {
                "enabled": self.CORS_ENABLED,
                "origins": self.CORS_ORIGINS,
                "methods": self.CORS_METHODS,
                "headers": self.CORS_HEADERS,
            },
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "level": self.LOG_LEVEL,
            "format": self.LOG_FORMAT,
            "file": self.LOG_FILE,
            "max_size": self.LOG_MAX_SIZE,
            "backup_count": self.LOG_BACKUP_COUNT,
            "structured": self.STRUCTURED_LOGGING,
            "correlation_id": self.LOG_CORRELATION_ID,
        }
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags"""
        return {
            "ai_generation": self.FEATURE_AI_GENERATION,
            "ai_optimization": self.FEATURE_AI_OPTIMIZATION,
            "batch_processing": self.FEATURE_BATCH_PROCESSING,
            "predictive_caching": self.FEATURE_PREDICTIVE_CACHING,
            "real_time_monitoring": self.FEATURE_REAL_TIME_MONITORING,
            "auto_scaling": self.FEATURE_AUTO_SCALING,
        }
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True


@lru_cache()
def get_settings() -> UltraExtremeSettings:
    """Get cached settings instance"""
    return UltraExtremeSettings()


# Global settings instance
settings = get_settings() 