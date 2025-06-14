"""
Configuration settings for Onyx.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Onyx API"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./onyx.db")
    
    # LLM Configuration
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_URL: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL_NAME: str = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")
    
    # Onyx API Configuration
    ONYX_API_KEY: Optional[str] = os.getenv("ONYX_API_KEY")
    ONYX_API_URL: str = os.getenv("ONYX_API_URL", "https://api.onyx.ai/v1")
    
    # Storage Configuration
    STORAGE_BUCKET: str = os.getenv("STORAGE_BUCKET", "onyx-storage")
    STORAGE_REGION: str = os.getenv("STORAGE_REGION", "us-east-1")
    
    # Advanced Features Configuration
    ENABLE_AI_TRAINING: bool = os.getenv("ENABLE_AI_TRAINING", "true").lower() == "true"
    ENABLE_CONTENT_OPTIMIZATION: bool = os.getenv("ENABLE_CONTENT_OPTIMIZATION", "true").lower() == "true"
    ENABLE_AUDIENCE_ANALYSIS: bool = os.getenv("ENABLE_AUDIENCE_ANALYSIS", "true").lower() == "true"
    ENABLE_BRAND_VOICE_ANALYSIS: bool = os.getenv("ENABLE_BRAND_VOICE_ANALYSIS", "true").lower() == "true"
    ENABLE_CONTENT_PERFORMANCE: bool = os.getenv("ENABLE_CONTENT_PERFORMANCE", "true").lower() == "true"
    ENABLE_COMPETITOR_ANALYSIS: bool = os.getenv("ENABLE_COMPETITOR_ANALYSIS", "true").lower() == "true"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Caching
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 