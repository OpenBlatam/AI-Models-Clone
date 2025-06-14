"""
Settings for the ads module.
"""
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class VectorStoreSettings(BaseModel):
    """Settings for vector store."""
    chunk_size: int = Field(default=1000, description="Size of text chunks")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")
    embedding_model: str = Field(default="text-embedding-3-small", description="Model for embeddings")
    vector_store_type: str = Field(default="faiss", description="Type of vector store")

class LLMSettings(BaseModel):
    """Settings for LLM."""
    model: str = Field(default="gpt-4-turbo-preview", description="Model to use")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    max_tokens: int = Field(default=2000, description="Maximum tokens for generation")
    top_p: float = Field(default=1.0, description="Top p for generation")
    frequency_penalty: float = Field(default=0.0, description="Frequency penalty")
    presence_penalty: float = Field(default=0.0, description="Presence penalty")

class AdsSettings(BaseModel):
    """Settings for ads generation."""
    max_ads_per_request: int = Field(default=5, description="Maximum ads per request")
    min_ad_length: int = Field(default=50, description="Minimum ad length")
    max_ad_length: int = Field(default=500, description="Maximum ad length")
    default_style: str = Field(default="professional", description="Default ad style")
    supported_platforms: list[str] = Field(
        default=["facebook", "instagram", "twitter", "linkedin"],
        description="Supported social media platforms"
    )

class MonitoringSettings(BaseModel):
    """Settings for monitoring."""
    enable_sentry: bool = Field(default=True, description="Enable Sentry monitoring")
    enable_prometheus: bool = Field(default=True, description="Enable Prometheus metrics")
    log_level: str = Field(default="INFO", description="Logging level")
    metrics_prefix: str = Field(default="ads_", description="Prefix for metrics")

class AdsModuleSettings(BaseSettings):
    """Settings for the ads module."""
    vector_store: VectorStoreSettings = Field(default_factory=VectorStoreSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    ads: AdsSettings = Field(default_factory=AdsSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    
    # Database settings
    database_url: str = Field(default="postgresql+asyncpg://user:pass@localhost/db")
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # API settings
    api_prefix: str = Field(default="/api/v1/ads")
    rate_limit: int = Field(default=100, description="Rate limit per minute")
    
    # Cache settings
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    enable_cache: bool = Field(default=True, description="Enable caching")
    
    class Config:
        env_prefix = "ADS_"
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = AdsModuleSettings() 