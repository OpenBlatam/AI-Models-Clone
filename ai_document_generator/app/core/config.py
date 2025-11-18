"""
Enhanced configuration management with environment-specific settings
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseSettings, validator, Field
from pydantic.env_settings import SettingsSourceCallable
import os
import secrets
from pathlib import Path
from functools import lru_cache

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class Settings(BaseSettings):
    """Enhanced application settings with validation and environment-specific configurations."""
    
    # Application
    PROJECT_NAME: str = Field(default="AI Document Generator", env="PROJECT_NAME")
    VERSION: str = Field(default="2.0.0", env="VERSION")
    DESCRIPTION: str = Field(
        default="AI-powered document generation and collaboration platform with advanced features",
        env="DESCRIPTION"
    )
    ENVIRONMENT: str = Field(default=ENVIRONMENT, env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    API_V1_STR: str = Field(default="/api/v1", env="API_V1_STR")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    
    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    
    # CORS
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"] if ENVIRONMENT == "development" else ["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost/ai_document_generator",
        env="DATABASE_URL"
    )
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=30, env="DB_MAX_OVERFLOW")
    DB_POOL_RECYCLE: int = Field(default=3600, env="DB_POOL_RECYCLE")
    DB_ECHO: bool = Field(default=False, env="DB_ECHO")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_POOL_SIZE: int = Field(default=10, env="REDIS_POOL_SIZE")
    REDIS_MAX_CONNECTIONS: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    COHERE_API_KEY: Optional[str] = Field(default=None, env="COHERE_API_KEY")
    
    # File Storage
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["pdf", "docx", "txt", "md", "html", "json", "csv"],
        env="ALLOWED_FILE_TYPES"
    )
    
    # Performance
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # 1 minute
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Email
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")
    
    # Webhooks
    WEBHOOK_SECRET: Optional[str] = Field(default=None, env="WEBHOOK_SECRET")
    WEBHOOK_TIMEOUT: int = Field(default=30, env="WEBHOOK_TIMEOUT")
    
    # Advanced Features
    ENABLE_AI_IMPROVEMENT: bool = Field(default=True, env="ENABLE_AI_IMPROVEMENT")
    ENABLE_PREDICTIVE_OPTIMIZATION: bool = Field(default=True, env="ENABLE_PREDICTIVE_OPTIMIZATION")
    ENABLE_REAL_TIME_COLLABORATION: bool = Field(default=True, env="ENABLE_REAL_TIME_COLLABORATION")
    ENABLE_ADVANCED_ANALYTICS: bool = Field(default=True, env="ENABLE_ADVANCED_ANALYTICS")
    
    # Machine Learning
    ML_MODEL_CACHE_SIZE: int = Field(default=100, env="ML_MODEL_CACHE_SIZE")
    ML_PREDICTION_TIMEOUT: int = Field(default=30, env="ML_PREDICTION_TIMEOUT")
    ML_TRAINING_BATCH_SIZE: int = Field(default=32, env="ML_TRAINING_BATCH_SIZE")
    
    # Optimization
    OPTIMIZATION_INTERVAL: int = Field(default=1800, env="OPTIMIZATION_INTERVAL")  # 30 minutes
    PERFORMANCE_THRESHOLD: float = Field(default=0.8, env="PERFORMANCE_THRESHOLD")
    AUTO_SCALING_ENABLED: bool = Field(default=False, env="AUTO_SCALING_ENABLED")
    
    # Backup
    BACKUP_ENABLED: bool = Field(default=True, env="BACKUP_ENABLED")
    BACKUP_INTERVAL: int = Field(default=86400, env="BACKUP_INTERVAL")  # 24 hours
    BACKUP_RETENTION_DAYS: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    
    # Security Headers
    SECURITY_HEADERS: Dict[str, str] = Field(
        default={
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        },
        env="SECURITY_HEADERS"
    )
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(",")]
        return v
    
    @validator("SECURITY_HEADERS", pre=True)
    def parse_security_headers(cls, v):
        if isinstance(v, str):
            # Parse JSON string
            import json
            return json.loads(v)
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        allowed_environments = ["development", "staging", "production", "testing"]
        if v not in allowed_environments:
            raise ValueError(f"Environment must be one of {allowed_environments}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()
    
    @validator("DEBUG")
    def validate_debug(cls, v, values):
        # Disable debug in production
        if values.get("ENVIRONMENT") == "production" and v:
            return False
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql://", "postgresql+asyncpg://", "sqlite://")):
            raise ValueError("Database URL must be PostgreSQL or SQLite")
        return v
    
    @validator("REDIS_URL")
    def validate_redis_url(cls, v):
        if not v.startswith(("redis://", "rediss://")):
            raise ValueError("Redis URL must start with redis:// or rediss://")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )


class DevelopmentSettings(Settings):
    """Development environment settings."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DB_ECHO: bool = True
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Development-specific overrides
    CACHE_TTL: int = 60  # Shorter cache for development
    RATE_LIMIT_REQUESTS: int = 1000  # Higher rate limit for development


class StagingSettings(Settings):
    """Staging environment settings."""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Staging-specific overrides
    CACHE_TTL: int = 300
    RATE_LIMIT_REQUESTS: int = 500


class ProductionSettings(Settings):
    """Production environment settings."""
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    
    # Production-specific overrides
    CACHE_TTL: int = 600  # Longer cache for production
    RATE_LIMIT_REQUESTS: int = 100  # Stricter rate limit for production
    DB_POOL_SIZE: int = 50  # Larger pool for production
    DB_MAX_OVERFLOW: int = 100
    
    # Security enhancements
    SECURITY_HEADERS: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'"
    }


class TestingSettings(Settings):
    """Testing environment settings."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/1"  # Use different Redis DB for testing
    
    # Testing-specific overrides
    CACHE_TTL: int = 1  # Very short cache for testing
    RATE_LIMIT_REQUESTS: int = 10000  # Very high rate limit for testing


def get_settings() -> Settings:
    """Get settings based on environment."""
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "development":
        return DevelopmentSettings()
    elif environment == "staging":
        return StagingSettings()
    elif environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return Settings()


@lru_cache()
def get_cached_settings() -> Settings:
    """Get cached settings instance."""
    return get_settings()


# Global settings instance
settings = get_cached_settings()


def get_database_config() -> Dict[str, Any]:
    """Get database configuration."""
    return {
        "url": settings.DATABASE_URL,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "echo": settings.DB_ECHO
    }


def get_redis_config() -> Dict[str, Any]:
    """Get Redis configuration."""
    return {
        "url": settings.REDIS_URL,
        "pool_size": settings.REDIS_POOL_SIZE,
        "max_connections": settings.REDIS_MAX_CONNECTIONS
    }


def get_ai_config() -> Dict[str, Any]:
    """Get AI services configuration."""
    return {
        "openai_api_key": settings.OPENAI_API_KEY,
        "anthropic_api_key": settings.ANTHROPIC_API_KEY,
        "deepseek_api_key": settings.DEEPSEEK_API_KEY,
        "cohere_api_key": settings.COHERE_API_KEY
    }


def get_security_config() -> Dict[str, Any]:
    """Get security configuration."""
    return {
        "secret_key": settings.SECRET_KEY,
        "algorithm": settings.ALGORITHM,
        "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "refresh_token_expire_days": settings.REFRESH_TOKEN_EXPIRE_DAYS,
        "security_headers": settings.SECURITY_HEADERS
    }


def get_performance_config() -> Dict[str, Any]:
    """Get performance configuration."""
    return {
        "cache_ttl": settings.CACHE_TTL,
        "rate_limit_requests": settings.RATE_LIMIT_REQUESTS,
        "rate_limit_window": settings.RATE_LIMIT_WINDOW,
        "enable_metrics": settings.ENABLE_METRICS,
        "metrics_port": settings.METRICS_PORT
    }


def get_feature_flags() -> Dict[str, bool]:
    """Get feature flags."""
    return {
        "ai_improvement": settings.ENABLE_AI_IMPROVEMENT,
        "predictive_optimization": settings.ENABLE_PREDICTIVE_OPTIMIZATION,
        "real_time_collaboration": settings.ENABLE_REAL_TIME_COLLABORATION,
        "advanced_analytics": settings.ENABLE_ADVANCED_ANALYTICS,
        "auto_scaling": settings.AUTO_SCALING_ENABLED,
        "backup": settings.BACKUP_ENABLED
    }


def is_development() -> bool:
    """Check if running in development environment."""
    return settings.ENVIRONMENT == "development"


def is_production() -> bool:
    """Check if running in production environment."""
    return settings.ENVIRONMENT == "production"


def is_testing() -> bool:
    """Check if running in testing environment."""
    return settings.ENVIRONMENT == "testing"


def get_upload_path() -> Path:
    """Get upload directory path."""
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def validate_configuration() -> Dict[str, Any]:
    """Validate configuration and return status."""
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check required settings
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        validation_results["errors"].append("SECRET_KEY must be at least 32 characters")
        validation_results["valid"] = False
    
    if not settings.DATABASE_URL:
        validation_results["errors"].append("DATABASE_URL is required")
        validation_results["valid"] = False
    
    # Check optional but recommended settings
    if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
        validation_results["warnings"].append("No AI API keys configured")
    
    if settings.ENVIRONMENT == "production" and settings.DEBUG:
        validation_results["warnings"].append("DEBUG should be False in production")
    
    return validation_results