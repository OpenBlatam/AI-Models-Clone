"""
🎯 Facebook LangChain Configuration
==================================

Configuración para el servicio LangChain de Facebook posts integrado con Onyx.
"""

import os
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class FacebookLangChainConfig(BaseModel):
    """Configuración para Facebook LangChain Service."""
    
    # Basic LLM Configuration
    openai_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY"),
        description="OpenAI API key"
    )
    model_name: str = Field("gpt-3.5-turbo-instruct", description="LLM model name")
    chat_model_name: str = Field("gpt-3.5-turbo", description="Chat model name")
    temperature: float = Field(0.7, description="Model temperature", ge=0.0, le=1.0)
    max_tokens: int = Field(1000, description="Maximum tokens", ge=100, le=4000)
    
    # Onyx Integration
    use_onyx_llm: bool = Field(True, description="Use Onyx LLM provider when available")
    onyx_fallback: bool = Field(True, description="Fallback to Onyx when OpenAI fails")
    
    # Memory Configuration
    use_memory: bool = Field(True, description="Enable conversation memory")
    memory_max_tokens: int = Field(2000, description="Maximum tokens for memory")
    
    # Tools Configuration
    enable_tools: bool = Field(True, description="Enable LangChain tools")
    enable_web_search: bool = Field(False, description="Enable web search tool")
    google_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY"),
        description="Google API key for search"
    )
    google_cse_id: Optional[str] = Field(
        default_factory=lambda: os.getenv("GOOGLE_CSE_ID"),
        description="Google Custom Search Engine ID"
    )
    
    # Agents Configuration
    enable_agents: bool = Field(False, description="Enable LangChain agents")
    agent_max_iterations: int = Field(3, description="Maximum agent iterations")
    
    # Vector Store Configuration
    enable_vector_store: bool = Field(False, description="Enable vector store")
    vector_store_path: str = Field("./facebook_vector_store", description="Vector store path")
    
    # Performance Configuration
    verbose: bool = Field(False, description="Enable verbose logging")
    cache_enabled: bool = Field(True, description="Enable response caching")
    async_mode: bool = Field(True, description="Enable async processing")
    
    # Facebook-specific Configuration
    facebook_api_version: str = Field("v18.0", description="Facebook API version")
    default_post_length: int = Field(280, description="Default post length limit")
    max_hashtags: int = Field(5, description="Maximum hashtags per post")
    enable_emoji: bool = Field(True, description="Enable emoji in posts")
    
    # Content Generation Configuration
    generation_retries: int = Field(2, description="Number of generation retries")
    variation_count: int = Field(2, description="Number of variations to generate")
    enable_a_b_testing: bool = Field(True, description="Enable A/B testing")
    
    # Analysis Configuration
    enable_sentiment_analysis: bool = Field(True, description="Enable sentiment analysis")
    enable_engagement_prediction: bool = Field(True, description="Enable engagement prediction")
    enable_virality_scoring: bool = Field(True, description="Enable virality scoring")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Default configurations for different environments
class DevelopmentConfig(FacebookLangChainConfig):
    """Development configuration."""
    verbose: bool = True
    enable_agents: bool = False
    enable_vector_store: bool = False
    generation_retries: int = 1


class ProductionConfig(FacebookLangChainConfig):
    """Production configuration."""
    verbose: bool = False
    enable_agents: bool = True
    enable_vector_store: bool = True
    cache_enabled: bool = True
    async_mode: bool = True


class TestingConfig(FacebookLangChainConfig):
    """Testing configuration."""
    model_name: str = "gpt-3.5-turbo-instruct"
    max_tokens: int = 500
    enable_tools: bool = False
    enable_agents: bool = False
    enable_vector_store: bool = False
    verbose: bool = True


# Configuration factory
def get_facebook_langchain_config(environment: str = "development") -> FacebookLangChainConfig:
    """Get configuration based on environment."""
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    
    config_class = configs.get(environment, DevelopmentConfig)
    return config_class()


# Onyx Integration Configuration
class OnyxIntegrationConfig(BaseModel):
    """Configuration for Onyx integration."""
    
    # Database Configuration
    use_onyx_db: bool = Field(True, description="Use Onyx database")
    db_table_prefix: str = Field("facebook_posts_", description="Database table prefix")
    
    # Authentication Configuration
    use_onyx_auth: bool = Field(True, description="Use Onyx authentication")
    require_auth: bool = Field(True, description="Require authentication for API calls")
    
    # Caching Configuration
    use_onyx_cache: bool = Field(True, description="Use Onyx caching system")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")
    
    # Monitoring Configuration
    use_onyx_monitoring: bool = Field(True, description="Use Onyx monitoring")
    log_all_requests: bool = Field(True, description="Log all API requests")
    
    # Feature Flags
    enable_facebook_api: bool = Field(False, description="Enable Facebook API integration")
    enable_scheduling: bool = Field(True, description="Enable post scheduling")
    enable_analytics: bool = Field(True, description="Enable analytics tracking")


# Prompt Templates Configuration
FACEBOOK_PROMPT_TEMPLATES = {
    "casual_post": """
    Create a casual Facebook post about {topic}.
    Tone: Friendly and approachable
    Target audience: {audience}
    Include relevant hashtags and emojis.
    Keep it under {max_length} characters.
    """,
    
    "professional_post": """
    Create a professional Facebook post about {topic}.
    Tone: Professional and informative
    Target audience: {audience}
    Focus on value and expertise.
    Keep it under {max_length} characters.
    """,
    
    "promotional_post": """
    Create a promotional Facebook post about {topic}.
    Tone: Exciting and persuasive
    Target audience: {audience}
    Include a clear call-to-action.
    Keep it under {max_length} characters.
    """,
    
    "educational_post": """
    Create an educational Facebook post about {topic}.
    Tone: Informative and helpful
    Target audience: {audience}
    Provide valuable insights or tips.
    Keep it under {max_length} characters.
    """
}


# Tool Configurations
FACEBOOK_TOOLS_CONFIG = {
    "web_search": {
        "enabled": False,
        "max_results": 5,
        "timeout": 10
    },
    "trend_analysis": {
        "enabled": True,
        "sources": ["facebook", "twitter", "google_trends"],
        "update_frequency": 3600  # 1 hour
    },
    "hashtag_research": {
        "enabled": True,
        "max_hashtags": 10,
        "popularity_threshold": 0.1
    },
    "engagement_prediction": {
        "enabled": True,
        "model": "facebook_engagement_v1",
        "confidence_threshold": 0.7
    }
} 