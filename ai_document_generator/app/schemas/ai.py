"""
AI-related schemas for API validation and serialization
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
import uuid


class AIProvider(str, Enum):
    """AI provider enumeration."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    GOOGLE = "google"
    LOCAL = "local"


class AIModel(str, Enum):
    """AI model enumeration."""
    # OpenAI models
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    
    # Anthropic models
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    
    # DeepSeek models
    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_CODER = "deepseek-coder"
    
    # Google models
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"


class AIGenerationRequest(BaseModel):
    """Schema for AI generation request."""
    prompt: str = Field(..., min_length=1, max_length=10000)
    provider: AIProvider = AIProvider.OPENAI
    model: AIModel = AIModel.GPT_4
    max_tokens: Optional[int] = Field(None, ge=1, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    stop_sequences: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()


class AIGenerationResponse(BaseModel):
    """Schema for AI generation response."""
    id: uuid.UUID
    content: str
    provider: AIProvider
    model: AIModel
    usage: Dict[str, int]  # tokens_used, tokens_prompt, tokens_completion
    finish_reason: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AIDocumentGenerationRequest(BaseModel):
    """Schema for AI document generation request."""
    template_id: Optional[uuid.UUID] = None
    document_type: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
    ai_settings: AIGenerationRequest
    organization_id: uuid.UUID


class AIDocumentGenerationResponse(BaseModel):
    """Schema for AI document generation response."""
    document: "Document"
    generation: AIGenerationResponse
    processing_time: float
    quality_score: Optional[float] = None


class AIContentAnalysisRequest(BaseModel):
    """Schema for AI content analysis request."""
    content: str = Field(..., min_length=1)
    analysis_type: str = Field(..., regex="^(sentiment|quality|plagiarism|readability|summary)$")
    provider: AIProvider = AIProvider.OPENAI
    model: AIModel = AIModel.GPT_4
    options: Dict[str, Any] = Field(default_factory=dict)


class AIContentAnalysisResponse(BaseModel):
    """Schema for AI content analysis response."""
    id: uuid.UUID
    analysis_type: str
    results: Dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    provider: AIProvider
    model: AIModel
    created_at: datetime
    
    class Config:
        from_attributes = True


class AITranslationRequest(BaseModel):
    """Schema for AI translation request."""
    content: str = Field(..., min_length=1)
    source_language: str = Field(..., min_length=2, max_length=10)
    target_language: str = Field(..., min_length=2, max_length=10)
    provider: AIProvider = AIProvider.OPENAI
    model: AIModel = AIModel.GPT_4
    preserve_formatting: bool = True


class AITranslationResponse(BaseModel):
    """Schema for AI translation response."""
    id: uuid.UUID
    original_content: str
    translated_content: str
    source_language: str
    target_language: str
    confidence: float = Field(ge=0.0, le=1.0)
    provider: AIProvider
    model: AIModel
    created_at: datetime
    
    class Config:
        from_attributes = True


class AISummarizationRequest(BaseModel):
    """Schema for AI summarization request."""
    content: str = Field(..., min_length=1)
    summary_type: str = Field(default="extractive", regex="^(extractive|abstractive|bullet_points)$")
    max_length: int = Field(default=200, ge=50, le=1000)
    provider: AIProvider = AIProvider.OPENAI
    model: AIModel = AIModel.GPT_4


class AISummarizationResponse(BaseModel):
    """Schema for AI summarization response."""
    id: uuid.UUID
    original_content: str
    summary: str
    summary_type: str
    compression_ratio: float
    provider: AIProvider
    model: AIModel
    created_at: datetime
    
    class Config:
        from_attributes = True


class AIImprovementRequest(BaseModel):
    """Schema for AI content improvement request."""
    content: str = Field(..., min_length=1)
    improvement_type: str = Field(..., regex="^(grammar|style|clarity|tone|structure)$")
    target_audience: Optional[str] = None
    writing_style: Optional[str] = None
    provider: AIProvider = AIProvider.OPENAI
    model: AIModel = AIModel.GPT_4


class AIImprovementResponse(BaseModel):
    """Schema for AI content improvement response."""
    id: uuid.UUID
    original_content: str
    improved_content: str
    improvement_type: str
    changes: List[Dict[str, Any]]
    confidence: float = Field(ge=0.0, le=1.0)
    provider: AIProvider
    model: AIModel
    created_at: datetime
    
    class Config:
        from_attributes = True


class AIBatchRequest(BaseModel):
    """Schema for AI batch processing request."""
    requests: List[Union[
        AIGenerationRequest,
        AIContentAnalysisRequest,
        AITranslationRequest,
        AISummarizationRequest,
        AIImprovementRequest
    ]] = Field(..., min_items=1, max_items=10)
    provider: AIProvider = AIProvider.OPENAI
    model: AIModel = AIModel.GPT_4


class AIBatchResponse(BaseModel):
    """Schema for AI batch processing response."""
    id: uuid.UUID
    results: List[Dict[str, Any]]
    total_requests: int
    successful_requests: int
    failed_requests: int
    processing_time: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class AIUsageStats(BaseModel):
    """Schema for AI usage statistics."""
    provider: AIProvider
    model: AIModel
    total_requests: int
    total_tokens: int
    total_cost: float
    average_response_time: float
    success_rate: float
    period_start: datetime
    period_end: datetime


class AIProviderConfig(BaseModel):
    """Schema for AI provider configuration."""
    provider: AIProvider
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    rate_limit: int = Field(default=100, ge=1, le=10000)
    is_enabled: bool = True
    priority: int = Field(default=1, ge=1, le=10)


class AIProviderStatus(BaseModel):
    """Schema for AI provider status."""
    provider: AIProvider
    is_available: bool
    response_time: Optional[float] = None
    error_rate: float = Field(ge=0.0, le=1.0)
    last_check: datetime
    error_message: Optional[str] = None


# Update forward references
AIDocumentGenerationResponse.model_rebuild()




