"""
Pydantic schemas for multi-model API
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum


class ModelType(str, Enum):
    """Supported AI model types"""
    COMPOSER_1 = "composer_1"
    SONNET_45 = "sonnet_4.5"
    GPT_51_CODEX = "gpt_5.1_codex"
    GPT_51 = "gpt_5.1"
    GPT_51_CODEX_MINI = "gpt_5.1_codex_mini"
    HAIKU_45 = "haiku_4.5"
    GROK_CODE = "grok_code"


class ModelConfig(BaseModel):
    """Configuration for a single model"""
    model_type: ModelType = Field(..., description="Type of AI model")
    multiplier: int = Field(default=1, ge=1, le=5, description="Multiplier/weight for this model (1-5)")
    is_enabled: bool = Field(default=True, description="Whether this model is active")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Temperature setting")
    max_tokens: Optional[int] = Field(default=None, ge=1, le=100000, description="Max tokens for response")
    custom_params: Optional[Dict[str, Any]] = Field(default=None, description="Custom model parameters")


class MultiModelRequest(BaseModel):
    """Request for multi-model API"""
    prompt: str = Field(..., min_length=1, max_length=50000, description="Input prompt for models")
    models: List[ModelConfig] = Field(..., min_items=1, max_items=5, description="List of models to use (max 5)")
    strategy: Literal["parallel", "sequential", "consensus"] = Field(
        default="parallel",
        description="Execution strategy: parallel (all at once), sequential (one by one), consensus (vote)"
    )
    cache_enabled: bool = Field(default=True, description="Enable response caching")
    cache_ttl: Optional[int] = Field(default=3600, ge=0, le=86400, description="Cache TTL in seconds")
    
    @validator('models')
    def validate_models_count(cls, v):
        if len(v) > 5:
            raise ValueError("Maximum 5 models allowed")
        if not any(model.is_enabled for model in v):
            raise ValueError("At least one model must be enabled")
        return v
    
    @validator('models')
    def validate_unique_models(cls, v):
        model_types = [model.model_type for model in v if model.is_enabled]
        if len(model_types) != len(set(model_types)):
            raise ValueError("Duplicate model types are not allowed")
        return v


class ModelResponse(BaseModel):
    """Response from a single model"""
    model_type: ModelType
    response: str
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


class MultiModelResponse(BaseModel):
    """Response from multi-model API"""
    request_id: str
    prompt: str
    strategy: str
    responses: List[ModelResponse]
    aggregated_response: Optional[str] = None
    total_tokens: Optional[int] = None
    total_latency_ms: Optional[float] = None
    cache_hit: bool = False
    timestamp: str


class ModelStatus(BaseModel):
    """Status of a model"""
    model_type: ModelType
    is_available: bool
    is_enabled: bool
    multiplier: int
    last_used: Optional[str] = None
    success_rate: Optional[float] = None
    avg_latency_ms: Optional[float] = None


class ModelsListResponse(BaseModel):
    """List of available models"""
    models: List[ModelStatus]
    total_available: int
    total_enabled: int

