"""
Copywriting Configuration Module.

Centralized configuration for AI-powered copywriting with environment-based settings.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pathlib import Path

from pydantic import BaseSettings, Field, validator
from decouple import config


class AIProvider(str, Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LANGCHAIN = "langchain"
    LOCAL = "local"
    MOCK = "mock"


class ContentType(str, Enum):
    """Types of content that can be generated."""
    AD_COPY = "ad_copy"
    SOCIAL_POST = "social_post"
    EMAIL_SUBJECT = "email_subject"
    EMAIL_BODY = "email_body"
    BLOG_TITLE = "blog_title"
    BLOG_CONTENT = "blog_content"
    PRODUCT_DESCRIPTION = "product_description"
    LANDING_PAGE = "landing_page"
    VIDEO_SCRIPT = "video_script"
    PRESS_RELEASE = "press_release"


class ContentTone(str, Enum):
    """Tone of voice for content."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    PLAYFUL = "playful"
    URGENT = "urgent"
    EMOTIONAL = "emotional"
    HUMOROUS = "humorous"


class ContentLanguage(str, Enum):
    """Supported languages for content generation."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    PORTUGUESE = "pt"
    ITALIAN = "it"
    CHINESE = "zh"
    JAPANESE = "ja"


class CopywritingConfig(BaseSettings):
    """Configuration for AI-powered copywriting system."""
    
    # AI Provider Settings
    primary_ai_provider: AIProvider = Field(default=AIProvider.OPENAI)
    fallback_ai_provider: AIProvider = Field(default=AIProvider.LANGCHAIN)
    openai_api_key: Optional[str] = Field(default=config("OPENAI_API_KEY", default=None))
    anthropic_api_key: Optional[str] = Field(default=config("ANTHROPIC_API_KEY", default=None))
    google_api_key: Optional[str] = Field(default=config("GOOGLE_API_KEY", default=None))
    
    # LangChain Settings
    enable_langchain: bool = Field(default=config("COPY_ENABLE_LANGCHAIN", default=True, cast=bool))
    langchain_verbose: bool = Field(default=config("LANGCHAIN_VERBOSE", default=False, cast=bool))
    langchain_cache: bool = Field(default=config("LANGCHAIN_CACHE", default=True, cast=bool))
    
    # Content Generation Settings
    default_language: ContentLanguage = Field(default=ContentLanguage.ENGLISH)
    default_tone: ContentTone = Field(default=ContentTone.PROFESSIONAL)
    max_content_length: int = Field(default=config("COPY_MAX_LENGTH", default=2000, cast=int))
    min_content_length: int = Field(default=config("COPY_MIN_LENGTH", default=50, cast=int))
    
    # AI Model Settings
    ai_model: str = Field(default=config("COPY_AI_MODEL", default="gpt-3.5-turbo"))
    ai_temperature: float = Field(default=config("COPY_AI_TEMPERATURE", default=0.7, cast=float))
    ai_max_tokens: int = Field(default=config("COPY_AI_MAX_TOKENS", default=1024, cast=int))
    ai_timeout: int = Field(default=config("COPY_AI_TIMEOUT", default=30, cast=int))
    
    # Content Analysis Settings
    enable_sentiment_analysis: bool = Field(default=config("COPY_ENABLE_SENTIMENT", default=True, cast=bool))
    enable_readability_analysis: bool = Field(default=config("COPY_ENABLE_READABILITY", default=True, cast=bool))
    enable_engagement_prediction: bool = Field(default=config("COPY_ENABLE_ENGAGEMENT", default=True, cast=bool))
    min_readability_score: float = Field(default=config("COPY_MIN_READABILITY", default=60.0, cast=float))
    
    # Template Settings
    enable_templates: bool = Field(default=config("COPY_ENABLE_TEMPLATES", default=True, cast=bool))
    template_path: str = Field(default=config("COPY_TEMPLATE_PATH", default="./templates"))
    custom_templates: Dict[str, str] = Field(default_factory=dict)
    
    # Cache Settings
    enable_caching: bool = Field(default=config("COPY_ENABLE_CACHE", default=True, cast=bool))
    cache_ttl: int = Field(default=config("COPY_CACHE_TTL", default=3600, cast=int))
    max_cache_size: int = Field(default=config("COPY_MAX_CACHE_SIZE", default=1000, cast=int))
    cache_compression: bool = Field(default=config("COPY_CACHE_COMPRESSION", default=True, cast=bool))
    
    # Performance Settings
    max_concurrent_generations: int = Field(default=config("COPY_MAX_CONCURRENT", default=10, cast=int))
    enable_batch_processing: bool = Field(default=config("COPY_ENABLE_BATCH", default=True, cast=bool))
    batch_size: int = Field(default=config("COPY_BATCH_SIZE", default=5, cast=int))
    request_timeout: int = Field(default=config("COPY_REQUEST_TIMEOUT", default=30, cast=int))
    
    # Quality Control Settings
    enable_content_filtering: bool = Field(default=config("COPY_ENABLE_FILTERING", default=True, cast=bool))
    profanity_filter: bool = Field(default=config("COPY_PROFANITY_FILTER", default=True, cast=bool))
    spam_detection: bool = Field(default=config("COPY_SPAM_DETECTION", default=True, cast=bool))
    duplicate_detection: bool = Field(default=config("COPY_DUPLICATE_DETECTION", default=True, cast=bool))
    
    # Monitoring Settings
    enable_performance_tracking: bool = Field(default=config("COPY_ENABLE_TRACKING", default=True, cast=bool))
    enable_usage_analytics: bool = Field(default=config("COPY_ENABLE_ANALYTICS", default=True, cast=bool))
    log_level: str = Field(default=config("COPY_LOG_LEVEL", default="INFO"))
    
    # API Settings
    enable_api_rate_limiting: bool = Field(default=config("COPY_ENABLE_RATE_LIMIT", default=True, cast=bool))
    api_rate_limit_per_minute: int = Field(default=config("COPY_RATE_LIMIT", default=100, cast=int))
    api_timeout: int = Field(default=config("COPY_API_TIMEOUT", default=30, cast=int))
    
    # A/B Testing Settings
    enable_ab_testing: bool = Field(default=config("COPY_ENABLE_AB_TEST", default=True, cast=bool))
    max_variants: int = Field(default=config("COPY_MAX_VARIANTS", default=5, cast=int))
    ab_test_duration_hours: int = Field(default=config("COPY_AB_TEST_DURATION", default=24, cast=int))
    
    # Content Optimization Settings
    enable_auto_optimization: bool = Field(default=config("COPY_ENABLE_AUTO_OPT", default=False, cast=bool))
    optimization_iterations: int = Field(default=config("COPY_OPT_ITERATIONS", default=3, cast=int))
    engagement_threshold: float = Field(default=config("COPY_ENGAGEMENT_THRESHOLD", default=0.7, cast=float))
    
    @validator('ai_temperature')
    def validate_ai_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("AI temperature must be between 0.0 and 2.0")
        return v
    
    @validator('min_readability_score')
    def validate_readability_score(cls, v):
        if not 0.0 <= v <= 100.0:
            raise ValueError("Readability score must be between 0.0 and 100.0")
        return v
    
    @validator('engagement_threshold')
    def validate_engagement_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Engagement threshold must be between 0.0 and 1.0")
        return v
    
    @validator('max_variants')
    def validate_max_variants(cls, v):
        if not 2 <= v <= 10:
            raise ValueError("Max variants must be between 2 and 10")
        return v
    
    class Config:
        env_prefix = "COPY_"
        env_file = ".env"
        case_sensitive = False


class AIProviderConfig(BaseSettings):
    """Configuration for specific AI providers."""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=config("OPENAI_API_KEY", default=None))
    openai_org_id: Optional[str] = Field(default=config("OPENAI_ORG_ID", default=None))
    openai_model: str = Field(default=config("OPENAI_MODEL", default="gpt-3.5-turbo"))
    openai_max_tokens: int = Field(default=config("OPENAI_MAX_TOKENS", default=1024, cast=int))
    openai_temperature: float = Field(default=config("OPENAI_TEMPERATURE", default=0.7, cast=float))
    
    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(default=config("ANTHROPIC_API_KEY", default=None))
    anthropic_model: str = Field(default=config("ANTHROPIC_MODEL", default="claude-3-sonnet-20240229"))
    anthropic_max_tokens: int = Field(default=config("ANTHROPIC_MAX_TOKENS", default=1024, cast=int))
    
    # Google Configuration
    google_api_key: Optional[str] = Field(default=config("GOOGLE_API_KEY", default=None))
    google_model: str = Field(default=config("GOOGLE_MODEL", default="gemini-pro"))
    
    # LangChain Configuration
    langchain_api_key: Optional[str] = Field(default=config("LANGCHAIN_API_KEY", default=None))
    langchain_llm_type: str = Field(default=config("LANGCHAIN_LLM_TYPE", default="openai"))
    langchain_model: str = Field(default=config("LANGCHAIN_MODEL", default="gpt-3.5-turbo"))
    langchain_temperature: float = Field(default=config("LANGCHAIN_TEMPERATURE", default=0.7, cast=float))
    langchain_max_tokens: int = Field(default=config("LANGCHAIN_MAX_TOKENS", default=1024, cast=int))
    langchain_chain_type: str = Field(default=config("LANGCHAIN_CHAIN_TYPE", default="llm"))
    langchain_memory_type: str = Field(default=config("LANGCHAIN_MEMORY_TYPE", default="buffer"))
    enable_langchain_agents: bool = Field(default=config("LANGCHAIN_ENABLE_AGENTS", default=True, cast=bool))
    enable_langchain_tools: bool = Field(default=config("LANGCHAIN_ENABLE_TOOLS", default=True, cast=bool))
    enable_vector_store: bool = Field(default=config("LANGCHAIN_ENABLE_VECTOR_STORE", default=True, cast=bool))
    vector_store_type: str = Field(default=config("LANGCHAIN_VECTOR_STORE", default="chroma"))
    
    # Local Model Configuration
    local_model_path: str = Field(default=config("LOCAL_MODEL_PATH", default="./models"))
    local_model_name: str = Field(default=config("LOCAL_MODEL_NAME", default="gpt2"))
    
    # Performance Configuration
    max_retries: int = Field(default=config("AI_MAX_RETRIES", default=3, cast=int))
    retry_delay: float = Field(default=config("AI_RETRY_DELAY", default=1.0, cast=float))
    request_timeout: int = Field(default=config("AI_REQUEST_TIMEOUT", default=30, cast=int))
    
    class Config:
        env_prefix = "AI_"


# Export main components
__all__ = [
    "CopywritingConfig",
    "AIProviderConfig",
    "AIProvider",
    "ContentType",
    "ContentTone", 
    "ContentLanguage"
] 