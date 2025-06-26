"""
Copywriting Data Models.

Pydantic models for copywriting with comprehensive validation and AI integration.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from uuid import uuid4, UUID

from pydantic import BaseModel, Field, validator, root_validator
from .config import ContentType, ContentTone, ContentLanguage


class ContentMetrics(BaseModel):
    """Metrics for evaluating content quality and performance."""
    readability_score: float = Field(default=0.0, ge=0.0, le=100.0)
    sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    engagement_prediction: float = Field(default=0.0, ge=0.0, le=1.0)
    word_count: int = Field(default=0, ge=0)
    character_count: int = Field(default=0, ge=0)
    reading_time_minutes: float = Field(default=0.0, ge=0.0)
    keyword_density: Dict[str, float] = Field(default_factory=dict)
    emotional_triggers: List[str] = Field(default_factory=list)
    call_to_action_strength: float = Field(default=0.0, ge=0.0, le=1.0)
    urgency_score: float = Field(default=0.0, ge=0.0, le=1.0)
    credibility_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    class Config:
        schema_extra = {
            "example": {
                "readability_score": 75.2,
                "sentiment_score": 0.8,
                "engagement_prediction": 0.85,
                "word_count": 150,
                "character_count": 800,
                "reading_time_minutes": 0.75,
                "keyword_density": {"marketing": 2.5, "AI": 1.8},
                "emotional_triggers": ["urgency", "social_proof"],
                "call_to_action_strength": 0.9,
                "urgency_score": 0.7,
                "credibility_score": 0.8
            }
        }


class ContentRequest(BaseModel):
    """Request for AI-powered content generation."""
    content_type: ContentType
    tone: ContentTone = ContentTone.PROFESSIONAL
    language: ContentLanguage = ContentLanguage.ENGLISH
    target_audience: str = Field(..., min_length=3, max_length=200, description="Description of target audience")
    key_message: str = Field(..., min_length=5, max_length=500, description="Main message to convey")
    keywords: List[str] = Field(default_factory=list, max_items=20)
    brand_voice: Optional[str] = Field(None, max_length=200)
    call_to_action: Optional[str] = Field(None, max_length=100)
    max_length: Optional[int] = Field(None, ge=10, le=5000)
    min_length: Optional[int] = Field(None, ge=5, le=2000)
    include_hashtags: bool = Field(default=False)
    include_emojis: bool = Field(default=False)
    urgency_level: int = Field(default=1, ge=1, le=5)
    creativity_level: float = Field(default=0.7, ge=0.0, le=1.0)
    
    # Advanced options
    context: Optional[str] = Field(None, max_length=1000, description="Additional context or background")
    competitors: List[str] = Field(default_factory=list, max_items=5, description="Competitor references")
    target_platforms: List[str] = Field(default_factory=list, max_items=10, description="Target platforms")
    campaign_goals: List[str] = Field(default_factory=list, max_items=5, description="Campaign objectives")
    
    @validator('keywords')
    def validate_keywords(cls, v):
        return [kw.strip().lower() for kw in v if kw.strip()]
    
    @validator('target_platforms')
    def validate_platforms(cls, v):
        valid_platforms = [
            "facebook", "instagram", "twitter", "linkedin", "youtube", 
            "tiktok", "email", "website", "blog", "ads"
        ]
        return [p.lower() for p in v if p.lower() in valid_platforms]
    
    @validator('min_length', 'max_length')
    def validate_length_constraints(cls, v, values):
        if 'min_length' in values and 'max_length' in values:
            min_len = values.get('min_length')
            max_len = values.get('max_length')
            if min_len and max_len and min_len >= max_len:
                raise ValueError("min_length must be less than max_length")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "content_type": "ad_copy",
                "tone": "professional",
                "language": "en",
                "target_audience": "Small business owners looking to grow their online presence",
                "key_message": "Our AI-powered marketing tools help you reach more customers",
                "keywords": ["AI marketing", "business growth", "automation"],
                "brand_voice": "Helpful and trustworthy technology partner",
                "call_to_action": "Start your free trial today",
                "max_length": 300,
                "include_hashtags": True,
                "urgency_level": 3,
                "creativity_level": 0.8,
                "target_platforms": ["facebook", "instagram"],
                "campaign_goals": ["increase_awareness", "generate_leads"]
            }
        }


class GeneratedContent(BaseModel):
    """Generated content with comprehensive metadata and analysis."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str = Field(..., min_length=1)
    content_type: ContentType
    tone: ContentTone
    language: ContentLanguage
    
    # Request context
    request_params: Dict[str, Any] = Field(default_factory=dict)
    
    # Analysis and metrics
    metrics: Optional[ContentMetrics] = None
    alternatives: List[str] = Field(default_factory=list, max_items=10)
    
    # Generation metadata
    generation_time_ms: float = Field(default=0.0, ge=0.0)
    model_used: str = Field(default="unknown")
    provider_used: str = Field(default="unknown")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Performance tracking
    view_count: int = Field(default=0, ge=0)
    click_count: int = Field(default=0, ge=0)
    conversion_count: int = Field(default=0, ge=0)
    
    # Version control
    version: int = Field(default=1, ge=1)
    parent_id: Optional[str] = None
    
    @validator('alternatives')
    def validate_alternatives(cls, v, values):
        # Remove duplicates and empty strings
        content = values.get('content', '')
        return [alt for alt in v if alt.strip() and alt != content]
    
    def calculate_engagement_rate(self) -> float:
        """Calculate engagement rate based on performance metrics."""
        if self.view_count == 0:
            return 0.0
        
        engagements = self.click_count + self.conversion_count
        return engagements / self.view_count
    
    def update_performance(self, views: int = 0, clicks: int = 0, conversions: int = 0):
        """Update performance metrics."""
        self.view_count += views
        self.click_count += clicks
        self.conversion_count += conversions
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "content": "Transform your business with AI-powered marketing tools that work 24/7 to grow your customer base. Start your free trial today! #AIMarketing #BusinessGrowth",
                "content_type": "ad_copy",
                "tone": "professional",
                "language": "en",
                "generation_time_ms": 1250.5,
                "model_used": "gpt-3.5-turbo",
                "provider_used": "openai",
                "confidence_score": 0.85,
                "alternatives": [
                    "Supercharge your marketing with AI tools that never sleep...",
                    "Discover how AI can revolutionize your customer acquisition..."
                ]
            }
        }


class ContentTemplate(BaseModel):
    """Template for generating structured content."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    content_type: ContentType
    tone: ContentTone
    language: ContentLanguage
    template: str = Field(..., min_length=10)
    variables: List[str] = Field(default_factory=list)
    
    # Metadata
    created_by: str = Field(default="system")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    usage_count: int = Field(default=0, ge=0)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    
    # Categories and tags
    category: str = Field(default="general")
    tags: List[str] = Field(default_factory=list)
    
    @validator('template')
    def validate_template(cls, v):
        """Ensure template has proper variable placeholders."""
        import re
        # Check for valid variable syntax {variable_name}
        variables = re.findall(r'\{([^}]+)\}', v)
        if not variables:
            raise ValueError("Template must contain at least one variable placeholder {variable_name}")
        return v
    
    @validator('variables', always=True)
    def extract_variables(cls, v, values):
        """Auto-extract variables from template."""
        import re
        template = values.get('template', '')
        if template:
            extracted = re.findall(r'\{([^}]+)\}', template)
            return list(set(extracted))  # Remove duplicates
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Social Media Product Launch",
                "description": "Template for announcing new product launches on social media",
                "content_type": "social_post",
                "tone": "exciting",
                "language": "en",
                "template": "🚀 Introducing {product_name}! {key_benefit} Perfect for {target_audience}. {call_to_action} #{hashtag1} #{hashtag2}",
                "category": "product_launch",
                "tags": ["social_media", "product", "announcement"]
            }
        }


class ContentBatch(BaseModel):
    """Batch content generation request and results."""
    batch_id: str = Field(default_factory=lambda: str(uuid4()))
    requests: List[ContentRequest] = Field(..., min_items=1, max_items=50)
    
    # Processing status
    status: str = Field(default="pending")  # pending, processing, completed, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    # Results
    results: List[GeneratedContent] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    
    # Statistics
    total_count: int = Field(default=0)
    completed_count: int = Field(default=0)
    failed_count: int = Field(default=0)
    
    @validator('total_count', always=True)
    def set_total_count(cls, v, values):
        requests = values.get('requests', [])
        return len(requests)
    
    def update_progress(self, completed: int, failed: int):
        """Update batch processing progress."""
        self.completed_count = completed
        self.failed_count = failed
        
        if completed + failed >= self.total_count:
            self.status = "completed"
            self.completed_at = datetime.now(timezone.utc)
        elif failed > 0:
            self.status = "partial_failure"
    
    class Config:
        schema_extra = {
            "example": {
                "requests": [
                    {
                        "content_type": "ad_copy",
                        "target_audience": "Young professionals",
                        "key_message": "Save time with our productivity app"
                    }
                ],
                "status": "completed",
                "total_count": 1,
                "completed_count": 1,
                "failed_count": 0
            }
        }


class ABTestVariant(BaseModel):
    """A/B testing variant for content optimization."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: GeneratedContent
    
    # Test configuration
    variant_name: str = Field(..., min_length=1, max_length=50)
    test_percentage: float = Field(default=50.0, ge=0.0, le=100.0)
    
    # Performance metrics
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    conversions: int = Field(default=0, ge=0)
    
    # Calculated metrics
    click_through_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    conversion_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_level: float = Field(default=0.0, ge=0.0, le=1.0)
    
    def update_metrics(self, impressions: int = 0, clicks: int = 0, conversions: int = 0):
        """Update performance metrics and calculate rates."""
        self.impressions += impressions
        self.clicks += clicks
        self.conversions += conversions
        
        # Calculate rates
        if self.impressions > 0:
            self.click_through_rate = self.clicks / self.impressions
        
        if self.clicks > 0:
            self.conversion_rate = self.conversions / self.clicks


class ABTestExperiment(BaseModel):
    """A/B testing experiment for content optimization."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    
    # Test configuration
    original_request: ContentRequest
    variants: List[ABTestVariant] = Field(..., min_items=2, max_items=10)
    
    # Test status
    status: str = Field(default="active")  # active, paused, completed
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: Optional[datetime] = None
    duration_hours: int = Field(default=24, ge=1, le=168)  # Max 1 week
    
    # Results
    winner_variant_id: Optional[str] = None
    statistical_significance: float = Field(default=0.0, ge=0.0, le=1.0)
    
    def get_winner(self) -> Optional[ABTestVariant]:
        """Determine the winning variant based on conversion rate."""
        if not self.variants:
            return None
        
        return max(self.variants, key=lambda v: v.conversion_rate)
    
    def calculate_significance(self) -> float:
        """Calculate statistical significance of results."""
        # Simplified significance calculation
        if len(self.variants) < 2:
            return 0.0
        
        # This would use proper statistical tests in production
        winner = self.get_winner()
        if not winner:
            return 0.0
        
        # Simple confidence based on sample size
        min_sample_size = 100
        if winner.impressions >= min_sample_size:
            return min(0.95, winner.impressions / 1000)
        
        return winner.impressions / min_sample_size


# Export all models
__all__ = [
    "ContentMetrics",
    "ContentRequest", 
    "GeneratedContent",
    "ContentTemplate",
    "ContentBatch",
    "ABTestVariant",
    "ABTestExperiment"
] 