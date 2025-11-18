"""
Configuration sections for Settings

Each section is a separate mixin class for better organization.
"""

import os
from typing import List
from pydantic import BaseModel


class AppConfig(BaseModel):
    """Application configuration"""
    app_name: str = "Lovable Community API"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"


class DatabaseConfig(BaseModel):
    """Database configuration"""
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./lovable_community.db"
    )
    database_echo: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"


class ServerConfig(BaseModel):
    """Server configuration"""
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8007"))


class CORSConfig(BaseModel):
    """CORS configuration"""
    cors_origins: List[str] = os.getenv(
        "CORS_ORIGINS",
        "*"
    ).split(",") if os.getenv("CORS_ORIGINS") != "*" else ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]


class PaginationConfig(BaseModel):
    """Pagination configuration"""
    default_page_size: int = 20
    max_page_size: int = 100
    max_page: int = 1000


class SearchConfig(BaseModel):
    """Search configuration"""
    max_search_query_length: int = 200
    max_tags_per_chat: int = 10
    max_tag_length: int = 50


class ValidationConfig(BaseModel):
    """Validation configuration"""
    max_title_length: int = 200
    max_description_length: int = 1000
    max_chat_content_length: int = 50000


class RankingConfig(BaseModel):
    """Ranking configuration"""
    vote_weight: float = 2.0
    remix_weight: float = 3.0
    view_weight: float = 0.1


class CacheConfig(BaseModel):
    """Cache configuration"""
    cache_enabled: bool = os.getenv("CACHE_ENABLED", "False").lower() == "true"
    cache_ttl: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes default
    cache_backend: str = os.getenv("CACHE_BACKEND", "auto")  # auto, redis, memory
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class SecurityConfig(BaseModel):
    """Security configuration"""
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class LimitsConfig(BaseModel):
    """Limits configuration"""
    max_chats_per_user: int = int(os.getenv("MAX_CHATS_PER_USER", "1000"))
    max_remixes_per_chat: int = int(os.getenv("MAX_REMIXES_PER_CHAT", "100"))
    max_votes_per_user_per_day: int = int(os.getenv("MAX_VOTES_PER_USER_PER_DAY", "1000"))
    rate_limit_enabled: bool = os.getenv("RATE_LIMIT_ENABLED", "False").lower() == "true"
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))


class NotificationsConfig(BaseModel):
    """Notifications configuration"""
    notifications_enabled: bool = os.getenv("NOTIFICATIONS_ENABLED", "True").lower() == "true"
    email_notifications: bool = os.getenv("EMAIL_NOTIFICATIONS", "False").lower() == "true"


class AnalyticsConfig(BaseModel):
    """Analytics configuration"""
    analytics_enabled: bool = os.getenv("ANALYTICS_ENABLED", "True").lower() == "true"
    analytics_retention_days: int = int(os.getenv("ANALYTICS_RETENTION_DAYS", "90"))


class ExportConfig(BaseModel):
    """Export configuration"""
    max_export_items: int = 100
    export_formats: List[str] = ["json", "csv", "xml"]


class TrendingConfig(BaseModel):
    """Trending configuration"""
    trending_periods: List[str] = ["hour", "day", "week", "month"]
    trending_min_score: float = 1.0


class LoggingConfig(BaseModel):
    """Logging configuration"""
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    use_structlog: bool = os.getenv("USE_STRUCTLOG", "True").lower() == "true"
    json_logs: bool = os.getenv("JSON_LOGS", "False").lower() == "true"


class AIConfig(BaseModel):
    """AI and Deep Learning configuration"""
    # General AI
    ai_enabled: bool = os.getenv("AI_ENABLED", "True").lower() == "true"
    use_gpu: bool = os.getenv("USE_GPU", "True").lower() == "true"
    device: str = os.getenv("DEVICE", "cuda" if os.getenv("USE_GPU", "True").lower() == "true" else "cpu")
    
    # Embeddings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    embedding_dimension: int = 384
    batch_size_embeddings: int = int(os.getenv("BATCH_SIZE_EMBEDDINGS", "32"))
    
    # Sentiment Analysis
    sentiment_model: str = os.getenv("SENTIMENT_MODEL", "cardiffnlp/twitter-roberta-base-sentiment-latest")
    sentiment_enabled: bool = os.getenv("SENTIMENT_ENABLED", "True").lower() == "true"
    
    # Content Moderation
    moderation_model: str = os.getenv("MODERATION_MODEL", "unitary/toxic-bert")
    moderation_enabled: bool = os.getenv("MODERATION_ENABLED", "True").lower() == "true"
    moderation_threshold: float = float(os.getenv("MODERATION_THRESHOLD", "0.7"))
    
    # Text Generation
    text_generation_model: str = os.getenv("TEXT_GENERATION_MODEL", "gpt2")
    text_generation_enabled: bool = os.getenv("TEXT_GENERATION_ENABLED", "True").lower() == "true"
    max_generation_length: int = int(os.getenv("MAX_GENERATION_LENGTH", "200"))
    
    # Diffusion Models
    diffusion_model: str = os.getenv("DIFFUSION_MODEL", "runwayml/stable-diffusion-v1-5")
    diffusion_enabled: bool = os.getenv("DIFFUSION_ENABLED", "False").lower() == "true"
    
    # Training
    use_mixed_precision: bool = os.getenv("USE_MIXED_PRECISION", "True").lower() == "true"
    model_cache_dir: str = os.getenv("MODEL_CACHE_DIR", "./models_cache")








