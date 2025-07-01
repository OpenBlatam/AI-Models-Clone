"""
Configuration for AI providers.
"""
from typing import Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class ProviderConfig(BaseModel):
    """Base configuration for AI providers."""
    api_key: str = Field(..., description="API key for the provider")
    model: str = Field(default="gpt-4-turbo-preview", description="Model to use")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    max_tokens: int = Field(default=2000, description="Maximum tokens for generation")
    top_p: float = Field(default=1.0, description="Top p for generation")
    frequency_penalty: float = Field(default=0.0, description="Frequency penalty")
    presence_penalty: float = Field(default=0.0, description="Presence penalty")

class OpenAIProviderConfig(ProviderConfig):
    """Configuration for OpenAI provider."""
    model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model to use")
    organization: str = Field(default="", description="OpenAI organization ID")

class CohereProviderConfig(ProviderConfig):
    """Configuration for Cohere provider."""
    model: str = Field(default="command", description="Cohere model to use")
    client_name: str = Field(default="onyx", description="Client name for Cohere")

class ProvidersConfig(BaseSettings):
    """Configuration for all providers."""
    openai: OpenAIProviderConfig = Field(..., description="OpenAI provider configuration")
    cohere: CohereProviderConfig = Field(..., description="Cohere provider configuration")
    default_provider: str = Field(default="openai", description="Default provider to use")
    fallback_provider: str = Field(default="cohere", description="Fallback provider to use")

    class Config:
        env_prefix = "AI_PROVIDER_"
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global providers configuration
providers_config = ProvidersConfig(
    openai=OpenAIProviderConfig(
        api_key="your-openai-api-key",
        model="gpt-4-turbo-preview"
    ),
    cohere=CohereProviderConfig(
        api_key="your-cohere-api-key",
        model="command"
    )
) 