"""
Enhanced API Schemas
===================

Comprehensive Pydantic models with advanced validation, 
following FastAPI best practices and RORO pattern.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator, EmailStr, HttpUrl
import re


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
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
            UUID: lambda v: str(v)
        }


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MetadataMixin(BaseModel):
    """Mixin for metadata fields."""
    
    tags: List[str] = Field(default_factory=list, description="Content tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


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


class ContentGenerationRequest(EnhancedBaseModel, MetadataMixin):
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
    
    @validator('topic', 'description')
    def validate_text_fields(cls, v: str) -> str:
        """Validate text fields for harmful content."""
        if not v or not v.strip():
            raise ValueError("Text field cannot be empty")
        
        # Basic content filtering
        harmful_patterns = ['script>', 'javascript:', 'data:']
        v_lower = v.lower()
        for pattern in harmful_patterns:
            if pattern in v_lower:
                raise ValueError(f"Potentially harmful content detected: {pattern}")
        
        return v.strip()


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
    
    @validator('requests')
    def validate_unique_topics(cls, v: List[ContentGenerationRequest]) -> List[ContentGenerationRequest]:
        """Ensure topics are unique in batch."""
        topics = [req.topic.lower() for req in v]
        if len(topics) != len(set(topics)):
            raise ValueError("Duplicate topics found in batch request")
        return v


class SearchRequest(EnhancedBaseModel):
    """Enhanced search request."""
    
    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field("desc", regex="^(asc|desc)$", description="Sort order")
    
    @validator('query')
    def validate_query(cls, v: str) -> str:
        """Validate search query."""
        if not v or not v.strip():
            raise ValueError("Search query cannot be empty")
        
        # Remove special characters that could cause issues
        v = re.sub(r'[<>"\'\\\x00-\x1f]', '', v)
        return v.strip()


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
    
    @root_validator
    def validate_pagination(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pagination data."""
        pagination = values.get('pagination', {})
        required_fields = ['page', 'size', 'total', 'pages']
        
        for field in required_fields:
            if field not in pagination:
                raise ValueError(f"Missing required pagination field: {field}")
        
        return values


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
    
    @validator('content')
    def validate_content_length(cls, v: str) -> str:
        """Validate content length."""
        if len(v) < 10:
            raise ValueError("Generated content too short")
        if len(v) > 50000:
            raise ValueError("Generated content too long")
        return v


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
    
    @validator('metrics')
    def validate_metrics(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metrics data."""
        required_metrics = ['requests_total', 'response_time_avg', 'error_rate']
        for metric in required_metrics:
            if metric not in v:
                raise ValueError(f"Missing required metric: {metric}")
        return v


# =============================================================================
# ADVANCED VALIDATION MODELS
# =============================================================================

class ContactInfo(EnhancedBaseModel):
    """Contact information with validation."""
    
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    website: Optional[HttpUrl] = Field(None, description="Website URL")
    
    @validator('phone')
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is None:
            return v
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', v)
        
        # Check if it's a valid length (7-15 digits)
        if len(digits_only) < 7 or len(digits_only) > 15:
            raise ValueError("Phone number must be 7-15 digits")
        
        return v


class GeolocationData(EnhancedBaseModel):
    """Geolocation data with validation."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    accuracy: Optional[float] = Field(None, ge=0, description="Accuracy in meters")
    country: Optional[str] = Field(None, max_length=2, description="Country code (ISO 3166-1)")
    
    @validator('country')
    def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate country code format."""
        if v is None:
            return v
        
        if not v.isalpha() or len(v) != 2:
            raise ValueError("Country code must be 2 letters")
        
        return v.upper()


# =============================================================================
# EXPORT ALL MODELS
# =============================================================================

__all__ = [
    # Enums
    "ContentType", "ContentTone", "ContentLanguage",
    
    # Base models
    "EnhancedBaseModel", "TimestampMixin", "MetadataMixin",
    
    # Request models
    "PaginationParams", "ContentGenerationRequest", "BulkContentRequest", "SearchRequest",
    
    # Response models
    "BaseResponse", "DataResponse", "PaginatedResponse", "ErrorResponse",
    "ContentGenerationResponse", "HealthCheckResponse", "MetricsResponse",
    
    # Advanced models
    "ContactInfo", "GeolocationData"
] 