"""
Configuration for Key Messages feature.
"""
from typing import Dict, Any, Optional
from pydantic import BaseSettings
import os

class KeyMessagesConfig(BaseSettings):
    """Configuration settings for Key Messages feature."""
    
    # Cache settings
    CACHE_TTL_HOURS: int = 24
    CACHE_MAX_SIZE: int = 1000
    
    # LLM settings
    LLM_PROVIDER: str = "deepseek"
    LLM_MODEL: str = "deepseek-chat"
    LLM_MAX_TOKENS: int = 2000
    LLM_TEMPERATURE: float = 0.7
    
    # Batch processing settings
    MAX_BATCH_SIZE: int = 50
    BATCH_TIMEOUT_SECONDS: int = 300
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_BURST_SIZE: int = 20
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Feature flags
    ENABLE_CACHING: bool = True
    ENABLE_BATCH_PROCESSING: bool = True
    ENABLE_ANALYSIS: bool = True
    ENABLE_LEGACY_ENDPOINTS: bool = True
    
    # Performance settings
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_prefix = "KEY_MESSAGES_"
        case_sensitive = False

# Global configuration instance
config = KeyMessagesConfig()

def get_config() -> KeyMessagesConfig:
    """Get the configuration instance."""
    return config

def update_config(updates: Dict[str, Any]) -> None:
    """Update configuration with new values."""
    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)

# Environment-specific configurations
def get_development_config() -> Dict[str, Any]:
    """Get development configuration."""
    return {
        "CACHE_TTL_HOURS": 1,
        "LOG_LEVEL": "DEBUG",
        "ENABLE_CACHING": True,
        "MAX_BATCH_SIZE": 10,
        "RATE_LIMIT_REQUESTS_PER_MINUTE": 1000
    }

def get_production_config() -> Dict[str, Any]:
    """Get production configuration."""
    return {
        "CACHE_TTL_HOURS": 24,
        "LOG_LEVEL": "INFO",
        "ENABLE_CACHING": True,
        "MAX_BATCH_SIZE": 50,
        "RATE_LIMIT_REQUESTS_PER_MINUTE": 100,
        "MAX_CONCURRENT_REQUESTS": 20
    }

def get_test_config() -> Dict[str, Any]:
    """Get test configuration."""
    return {
        "CACHE_TTL_HOURS": 0,
        "LOG_LEVEL": "WARNING",
        "ENABLE_CACHING": False,
        "MAX_BATCH_SIZE": 5,
        "RATE_LIMIT_REQUESTS_PER_MINUTE": 1000,
        "REQUEST_TIMEOUT_SECONDS": 5
    }

# Initialize configuration based on environment
def initialize_config(environment: str = "development") -> None:
    """Initialize configuration based on environment."""
    env_configs = {
        "development": get_development_config(),
        "production": get_production_config(),
        "test": get_test_config()
    }
    
    if environment in env_configs:
        update_config(env_configs[environment])
    
    # Override with environment variables
    for key in config.__fields__:
        env_value = os.getenv(f"KEY_MESSAGES_{key}")
        if env_value is not None:
            # Convert to appropriate type
            field_type = config.__fields__[key].type_
            if field_type == bool:
                setattr(config, key, env_value.lower() in ('true', '1', 'yes'))
            elif field_type == int:
                setattr(config, key, int(env_value))
            elif field_type == float:
                setattr(config, key, float(env_value))
            else:
                setattr(config, key, env_value) 