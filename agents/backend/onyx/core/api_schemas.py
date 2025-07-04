"""
Enhanced API Schemas
===================

Comprehensive Pydantic models with advanced validation, 
following FastAPI best practices and RORO pattern.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


# =============================================================================
# ENUMS
# =============================================================================

class ContentType(str, Enum):
    """Content type enumeration."""
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    PRODUCT_DESCRIPTION = "product_description"
    EMAIL_CAMPAIGN = "email_campaign"
    AD_COPY = "ad_copy"
    LANDING_PAGE = "landing_page"


class ContentTone(str, Enum):
    """Content tone enumeration."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"
    HUMOROUS = "humorous"


class ContentLanguage(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"


# =============================================================================
# BASE MODELS
# =============================================================================

class EnhancedBaseModel(BaseModel):
    """Enhanced base model with common configuration."""
    
    class Config:
        use_enum_values = True
        validate_assignment = True
        str_strip_whitespace = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# =============================================================================
# REQUEST MODELS
# =============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters with validation."""
    
    page: int = Field(1, ge=1, le=10000, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class ContentGenerationRequest(EnhancedBaseModel):
    """Enhanced content generation request."""
    
    content_type: ContentType = Field(..., description="Type of content to generate")
    topic: str = Field(..., min_length=3, max_length=200, description="Content topic")
    description: str = Field(..., min_length=10, max_length=2000, description="Content description")
    
    # Style parameters
    tone: ContentTone = Field(default=ContentTone.PROFESSIONAL, description="Content tone")
    language: ContentLanguage = Field(default=ContentLanguage.ENGLISH, description="Content language")
    
    # Content parameters
    target_audience: Optional[str] = Field(None, max_length=500, description="Target audience description")
    keywords: List[str] = Field(default_factory=list, description="SEO keywords")
    word_count: Optional[int] = Field(None, ge=50, le=10000, description="Target word count")
    
    # AI parameters
    creativity_level: float = Field(0.7, ge=0.0, le=1.0, description="AI creativity level (0-1)")
    include_cta: bool = Field(True, description="Include call-to-action")
    
    @validator('keywords')
    def validate_keywords(cls, v: List[str]) -> List[str]:
        """Validate and clean keywords."""
        return [keyword.strip().lower() for keyword in v if keyword.strip()]


class BulkContentRequest(EnhancedBaseModel):
    """Bulk content generation request."""
    
    requests: List[ContentGenerationRequest] = Field(
        ..., 
        min_items=1, 
        max_items=10, 
        description="List of content requests"
    )
    
    # Bulk parameters
    batch_id: Optional[str] = Field(None, description="Batch identifier")
    priority: int = Field(1, ge=1, le=5, description="Processing priority (1=highest)")


class SearchRequest(EnhancedBaseModel):
    """Enhanced search request."""
    
    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field("desc", regex="^(asc|desc)$", description="Sort order")


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class BaseResponse(EnhancedBaseModel):
    """Standardized base response."""
    
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: Optional[str] = Field(None, description="Request tracking ID")
    execution_time_ms: Optional[float] = Field(None, description="Execution time in milliseconds")


class DataResponse(BaseResponse):
    """Response with data payload."""
    
    data: Any = Field(..., description="Response data")
    meta: Optional[Dict[str, Any]] = Field(None, description="Response metadata")


class PaginatedResponse(BaseResponse):
    """Paginated response."""
    
    data: List[Any] = Field(..., description="Paginated data")
    pagination: Dict[str, Any] = Field(..., description="Pagination info")


class ErrorResponse(BaseResponse):
    """Standardized error response."""
    
    success: bool = Field(default=False)
    error_code: str = Field(..., description="Error code")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    retry_after: Optional[int] = Field(None, description="Retry after seconds")


class ContentGenerationResponse(BaseResponse):
    """Content generation response."""
    
    content: str = Field(..., description="Generated content")
    content_type: ContentType = Field(..., description="Content type")
    word_count: int = Field(..., description="Word count")
    
    # Quality metrics
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Content quality score")
    seo_score: float = Field(..., ge=0.0, le=1.0, description="SEO score")
    readability_score: float = Field(..., ge=0.0, le=1.0, description="Readability score")
    
    # Metadata
    keywords_used: List[str] = Field(default_factory=list, description="Keywords used")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class HealthCheckResponse(BaseResponse):
    """Health check response."""
    
    status: str = Field(..., description="Overall health status")
    checks: Dict[str, Any] = Field(..., description="Individual health checks")
    uptime: float = Field(..., description="Service uptime in seconds")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment")


class MetricsResponse(BaseResponse):
    """Metrics response."""
    
    metrics: Dict[str, Any] = Field(..., description="Performance metrics")
    period: str = Field(..., description="Metrics period") 