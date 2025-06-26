"""
Blog Posts Configuration Module.

Centralized configuration for blog post management with environment-based settings.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pathlib import Path

from pydantic import BaseSettings, Field, validator
from decouple import config


class ContentLanguage(str, Enum):
    """Supported languages for content generation."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"


class ContentTone(str, Enum):
    """Content tone options."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    CREATIVE = "creative"
    TECHNICAL = "technical"


class BlogPostStatus(str, Enum):
    """Blog post status options."""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class SEOLevel(str, Enum):
    """SEO optimization levels."""
    BASIC = "basic"
    ADVANCED = "advanced"
    EXPERT = "expert"


class BlogPostConfig(BaseSettings):
    """Configuration for blog post management system."""
    
    # Content Generation Settings
    ai_model: str = Field(default=config("BLOG_AI_MODEL", default="gpt-3.5-turbo"))
    max_content_length: int = Field(default=config("BLOG_MAX_LENGTH", default=5000, cast=int))
    min_content_length: int = Field(default=config("BLOG_MIN_LENGTH", default=300, cast=int))
    default_language: ContentLanguage = Field(default=ContentLanguage.ENGLISH)
    default_tone: ContentTone = Field(default=ContentTone.PROFESSIONAL)
    
    # SEO Settings
    seo_level: SEOLevel = Field(default=SEOLevel.ADVANCED)
    max_title_length: int = Field(default=config("BLOG_MAX_TITLE_LENGTH", default=60, cast=int))
    max_description_length: int = Field(default=config("BLOG_MAX_DESCRIPTION_LENGTH", default=160, cast=int))
    target_keyword_density: float = Field(default=config("BLOG_KEYWORD_DENSITY", default=1.5, cast=float))
    enable_schema_markup: bool = Field(default=config("BLOG_ENABLE_SCHEMA", default=True, cast=bool))
    
    # Content Processing
    enable_html_sanitization: bool = Field(default=config("BLOG_ENABLE_SANITIZATION", default=True, cast=bool))
    enable_auto_formatting: bool = Field(default=config("BLOG_ENABLE_AUTO_FORMAT", default=True, cast=bool))
    enable_readability_check: bool = Field(default=config("BLOG_ENABLE_READABILITY", default=True, cast=bool))
    min_readability_score: float = Field(default=config("BLOG_MIN_READABILITY", default=60.0, cast=float))
    
    # Publishing Settings
    auto_publish: bool = Field(default=config("BLOG_AUTO_PUBLISH", default=False, cast=bool))
    enable_social_sharing: bool = Field(default=config("BLOG_ENABLE_SOCIAL", default=True, cast=bool))
    default_status: BlogPostStatus = Field(default=BlogPostStatus.DRAFT)
    
    # Storage Settings
    content_storage_path: str = Field(default=config("BLOG_STORAGE_PATH", default="./blog_content"))
    image_storage_path: str = Field(default=config("BLOG_IMAGE_PATH", default="./blog_images"))
    backup_enabled: bool = Field(default=config("BLOG_BACKUP_ENABLED", default=True, cast=bool))
    backup_retention_days: int = Field(default=config("BLOG_BACKUP_RETENTION", default=30, cast=int))
    
    # Cache Settings
    enable_caching: bool = Field(default=config("BLOG_ENABLE_CACHE", default=True, cast=bool))
    cache_ttl: int = Field(default=config("BLOG_CACHE_TTL", default=3600, cast=int))
    max_cache_size: int = Field(default=config("BLOG_MAX_CACHE_SIZE", default=1000, cast=int))
    
    # Performance Settings
    max_concurrent_generations: int = Field(default=config("BLOG_MAX_CONCURRENT", default=10, cast=int))
    generation_timeout: int = Field(default=config("BLOG_GENERATION_TIMEOUT", default=300, cast=int))
    enable_batch_processing: bool = Field(default=config("BLOG_ENABLE_BATCH", default=True, cast=bool))
    batch_size: int = Field(default=config("BLOG_BATCH_SIZE", default=5, cast=int))
    
    # API Settings
    enable_api_rate_limiting: bool = Field(default=config("BLOG_ENABLE_RATE_LIMIT", default=True, cast=bool))
    api_rate_limit_per_minute: int = Field(default=config("BLOG_RATE_LIMIT", default=100, cast=int))
    api_timeout: int = Field(default=config("BLOG_API_TIMEOUT", default=30, cast=int))
    
    # Monitoring Settings
    enable_performance_tracking: bool = Field(default=config("BLOG_ENABLE_TRACKING", default=True, cast=bool))
    enable_error_reporting: bool = Field(default=config("BLOG_ENABLE_ERROR_REPORTING", default=True, cast=bool))
    log_level: str = Field(default=config("BLOG_LOG_LEVEL", default="INFO"))
    
    # AI Provider Settings
    openai_api_key: Optional[str] = Field(default=config("OPENAI_API_KEY", default=None))
    anthropic_api_key: Optional[str] = Field(default=config("ANTHROPIC_API_KEY", default=None))
    ai_temperature: float = Field(default=config("BLOG_AI_TEMPERATURE", default=0.7, cast=float))
    ai_max_tokens: int = Field(default=config("BLOG_AI_MAX_TOKENS", default=2048, cast=int))
    
    # Content Templates
    enable_templates: bool = Field(default=config("BLOG_ENABLE_TEMPLATES", default=True, cast=bool))
    template_path: str = Field(default=config("BLOG_TEMPLATE_PATH", default="./templates"))
    
    # Image Processing
    enable_image_processing: bool = Field(default=config("BLOG_ENABLE_IMAGE_PROCESSING", default=True, cast=bool))
    max_image_size_mb: int = Field(default=config("BLOG_MAX_IMAGE_SIZE", default=10, cast=int))
    image_quality: int = Field(default=config("BLOG_IMAGE_QUALITY", default=85, cast=int))
    
    @validator('target_keyword_density')
    def validate_keyword_density(cls, v):
        if not 0.5 <= v <= 5.0:
            raise ValueError("Keyword density must be between 0.5% and 5.0%")
        return v
    
    @validator('min_readability_score')
    def validate_readability_score(cls, v):
        if not 0.0 <= v <= 100.0:
            raise ValueError("Readability score must be between 0.0 and 100.0")
        return v
    
    @validator('ai_temperature')
    def validate_ai_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("AI temperature must be between 0.0 and 2.0")
        return v
    
    @validator('image_quality')
    def validate_image_quality(cls, v):
        if not 1 <= v <= 100:
            raise ValueError("Image quality must be between 1 and 100")
        return v
    
    class Config:
        env_prefix = "BLOG_"
        env_file = ".env"
        case_sensitive = False


class AIProviderConfig(BaseSettings):
    """Configuration for AI providers."""
    
    openai_api_key: Optional[str] = Field(default=config("OPENAI_API_KEY", default=None))
    openai_org_id: Optional[str] = Field(default=config("OPENAI_ORG_ID", default=None))
    anthropic_api_key: Optional[str] = Field(default=config("ANTHROPIC_API_KEY", default=None))
    
    # Model preferences
    primary_model: str = Field(default=config("AI_PRIMARY_MODEL", default="gpt-3.5-turbo"))
    fallback_model: str = Field(default=config("AI_FALLBACK_MODEL", default="gpt-3.5-turbo"))
    
    # Performance settings
    max_retries: int = Field(default=config("AI_MAX_RETRIES", default=3, cast=int))
    retry_delay: float = Field(default=config("AI_RETRY_DELAY", default=1.0, cast=float))
    request_timeout: int = Field(default=config("AI_REQUEST_TIMEOUT", default=120, cast=int))
    
    class Config:
        env_prefix = "AI_"


class DatabaseConfig(BaseSettings):
    """Database configuration for blog posts."""
    
    url: str = Field(default=config("DATABASE_URL", default="sqlite:///blog_posts.db"))
    echo: bool = Field(default=config("DB_ECHO", default=False, cast=bool))
    pool_size: int = Field(default=config("DB_POOL_SIZE", default=10, cast=int))
    max_overflow: int = Field(default=config("DB_MAX_OVERFLOW", default=20, cast=int))
    
    class Config:
        env_prefix = "DB_"


# Global configuration instance
_config: Optional[BlogPostConfig] = None
_ai_config: Optional[AIProviderConfig] = None
_db_config: Optional[DatabaseConfig] = None


def get_blog_config() -> BlogPostConfig:
    """Get the global blog configuration instance."""
    global _config
    if _config is None:
        _config = BlogPostConfig()
    return _config


def get_ai_config() -> AIProviderConfig:
    """Get the global AI configuration instance."""
    global _ai_config
    if _ai_config is None:
        _ai_config = AIProviderConfig()
    return _ai_config


def get_db_config() -> DatabaseConfig:
    """Get the global database configuration instance."""
    global _db_config
    if _db_config is None:
        _db_config = DatabaseConfig()
    return _db_config


def reload_config() -> BlogPostConfig:
    """Reload the configuration from environment variables."""
    global _config, _ai_config, _db_config
    _config = BlogPostConfig()
    _ai_config = AIProviderConfig()
    _db_config = DatabaseConfig()
    return _config


# Export main components
__all__ = [
    "BlogPostConfig",
    "AIProviderConfig", 
    "DatabaseConfig",
    "ContentLanguage",
    "ContentTone",
    "BlogPostStatus",
    "SEOLevel",
    "get_blog_config",
    "get_ai_config",
    "get_db_config",
    "reload_config"
] 