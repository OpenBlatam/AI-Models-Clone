"""
Production Configuration
Environment-based configuration with security settings
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Production settings"""
    
    # Application settings
    APP_NAME: str = "Production API"
    DEBUG: bool = False  # Disable debug in production
    ENV: str = "production"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["https://yourdomain.com"]
    ALLOWED_HOSTS: List[str] = ["yourdomain.com", "api.yourdomain.com"]
    
    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost/production_db"
    
    # Security settings
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/production.log"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["https://yourdomain.com"]
    
    # Database connection pool
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_TIMEOUT: int = 30
    
    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Validate critical settings
if settings.ENV == "production":
    if settings.SECRET_KEY == "your-super-secret-key-change-in-production":
        raise ValueError("SECRET_KEY must be changed in production")
    
    if settings.DEBUG:
        raise ValueError("DEBUG must be False in production")
    
    if "localhost" in settings.DATABASE_URL:
        raise ValueError("DATABASE_URL must point to production database") 