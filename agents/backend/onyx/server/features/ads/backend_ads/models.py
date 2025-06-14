"""
Ads Models - Onyx Integration
Enhanced models for ads with advanced features.
"""
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from pydantic import Field, validator, root_validator
from ...utils.base_model import OnyxBaseModel

class ModelConfig(OnyxBaseModel):
    """Enhanced model configuration for ads generation."""
    
    model_name: str = Field(..., description="Name of the model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
    stop_sequences: List[str] = Field(default_factory=list)
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Configure indexing
    index_fields = ["model_name"]
    search_fields = ["model_name", "custom_parameters"]
    
    @validator("temperature", "top_p", "frequency_penalty", "presence_penalty")
    def validate_float_range(cls, v: float, field: Field) -> float:
        """Validate float fields are within their ranges."""
        if field.name == "temperature" and not 0 <= v <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        if field.name == "top_p" and not 0 <= v <= 1:
            raise ValueError("Top P must be between 0 and 1")
        if field.name in ["frequency_penalty", "presence_penalty"] and not -2 <= v <= 2:
            raise ValueError(f"{field.name} must be between -2 and 2")
        return v
    
    @validator("max_tokens")
    def validate_max_tokens(cls, v: int) -> int:
        """Validate max tokens is positive."""
        if v <= 0:
            raise ValueError("Max tokens must be positive")
        return v
    
    def get_model_parameters(self) -> Dict[str, Any]:
        """Get model parameters for API calls."""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "max_tokens": self.max_tokens,
            "stop": self.stop_sequences,
            **self.custom_parameters
        }

class BrandVoice(OnyxBaseModel):
    """Enhanced brand voice configuration."""
    
    brand_name: str
    tone: str
    personality: Dict[str, float] = Field(
        default_factory=lambda: {
            "professional": 0.8,
            "friendly": 0.6,
            "creative": 0.7
        }
    )
    keywords: List[str] = Field(default_factory=list)
    style_guide: Dict[str, Any] = Field(default_factory=dict)
    examples: List[str] = Field(default_factory=list)
    
    # Configure indexing
    index_fields = ["brand_name"]
    search_fields = ["tone", "keywords"]
    
    @validator("personality")
    def validate_personality(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate personality scores are between 0 and 1."""
        for key, value in v.items():
            if not 0 <= value <= 1:
                raise ValueError(f"Personality score for {key} must be between 0 and 1")
        return v
    
    @validator("keywords")
    def validate_keywords(cls, v: List[str]) -> List[str]:
        """Validate keywords are non-empty."""
        return [k.strip() for k in v if k.strip()]
    
    def get_personality_vector(self) -> List[float]:
        """Get personality vector for similarity calculations."""
        return list(self.personality.values())
    
    def get_keyword_set(self) -> set:
        """Get set of keywords for matching."""
        return set(self.keywords)

class AudienceProfile(OnyxBaseModel):
    """Enhanced audience profile configuration."""
    
    name: str
    demographics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "age_range": [18, 65],
            "gender": "all",
            "location": "global",
            "interests": [],
            "behaviors": []
        }
    )
    preferences: Dict[str, Any] = Field(default_factory=dict)
    pain_points: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    
    # Configure indexing
    index_fields = ["name"]
    search_fields = ["demographics", "preferences", "pain_points", "goals"]
    
    @validator("demographics")
    def validate_demographics(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate demographics data."""
        required_fields = ["age_range", "gender", "location"]
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required demographics field: {field}")
        
        if not isinstance(v["age_range"], list) or len(v["age_range"]) != 2:
            raise ValueError("Age range must be a list of two numbers")
        
        if v["age_range"][0] > v["age_range"][1]:
            raise ValueError("Invalid age range")
        
        return v
    
    @validator("pain_points", "goals")
    def validate_lists(cls, v: List[str]) -> List[str]:
        """Validate list fields are non-empty."""
        return [item.strip() for item in v if item.strip()]
    
    def get_age_range(self) -> tuple:
        """Get age range as tuple."""
        return tuple(self.demographics["age_range"])
    
    def get_interests(self) -> set:
        """Get set of interests."""
        return set(self.demographics.get("interests", []))
    
    def get_behaviors(self) -> set:
        """Get set of behaviors."""
        return set(self.demographics.get("behaviors", []))

class AdContent(OnyxBaseModel):
    """Enhanced ad content model."""
    
    title: str
    description: str
    call_to_action: str
    media_urls: List[str] = Field(default_factory=list)
    target_audience: str
    platform: str
    metrics: Dict[str, float] = Field(default_factory=dict)
    status: str = Field(default="draft")
    
    # Configure indexing
    index_fields = ["id", "target_audience", "platform", "status"]
    search_fields = ["title", "description", "call_to_action"]
    
    @validator("status")
    def validate_status(cls, v: str) -> str:
        """Validate status is one of allowed values."""
        allowed_statuses = ["draft", "review", "approved", "rejected", "active", "paused"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v
    
    @validator("media_urls")
    def validate_media_urls(cls, v: List[str]) -> List[str]:
        """Validate media URLs."""
        return [url.strip() for url in v if url.strip()]
    
    def is_approved(self) -> bool:
        """Check if ad is approved."""
        return self.status == "approved"
    
    def is_active(self) -> bool:
        """Check if ad is active."""
        return self.status == "active"
    
    def get_metrics_summary(self) -> Dict[str, float]:
        """Get summary of ad metrics."""
        return {
            "impressions": self.metrics.get("impressions", 0),
            "clicks": self.metrics.get("clicks", 0),
            "ctr": self.metrics.get("ctr", 0),
            "conversions": self.metrics.get("conversions", 0)
        }

class AdCampaign(OnyxBaseModel):
    """Enhanced ad campaign model."""
    
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    budget: float
    target_audience: str
    platforms: List[str]
    ads: List[AdContent] = Field(default_factory=list)
    status: str = Field(default="draft")
    
    # Configure indexing
    index_fields = ["id", "name", "status"]
    search_fields = ["description", "target_audience", "platforms"]
    
    @validator("end_date")
    def validate_dates(cls, v: datetime, values: Dict[str, Any]) -> datetime:
        """Validate campaign dates."""
        if "start_date" in values and v <= values["start_date"]:
            raise ValueError("End date must be after start date")
        return v
    
    @validator("budget")
    def validate_budget(cls, v: float) -> float:
        """Validate budget is positive."""
        if v <= 0:
            raise ValueError("Budget must be positive")
        return v
    
    @validator("platforms")
    def validate_platforms(cls, v: List[str]) -> List[str]:
        """Validate platforms."""
        allowed_platforms = ["facebook", "instagram", "twitter", "linkedin", "google"]
        return [p.lower() for p in v if p.lower() in allowed_platforms]
    
    def is_active(self) -> bool:
        """Check if campaign is active."""
        now = datetime.utcnow()
        return (
            self.status == "active" and
            self.start_date <= now <= self.end_date
        )
    
    def get_budget_usage(self) -> float:
        """Calculate budget usage."""
        return sum(ad.metrics.get("spend", 0) for ad in self.ads)
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get campaign performance metrics."""
        total_impressions = sum(ad.metrics.get("impressions", 0) for ad in self.ads)
        total_clicks = sum(ad.metrics.get("clicks", 0) for ad in self.ads)
        total_conversions = sum(ad.metrics.get("conversions", 0) for ad in self.ads)
        
        return {
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "ctr": total_clicks / total_impressions if total_impressions > 0 else 0,
            "conversion_rate": total_conversions / total_clicks if total_clicks > 0 else 0
        }

# Example usage:
"""
# Create model configuration
model_config = ModelConfig(
    model_name="gpt-4",
    temperature=0.7,
    top_p=0.9,
    max_tokens=500
)

# Create brand voice
brand_voice = BrandVoice(
    brand_name="TechCorp",
    tone="professional",
    personality={
        "professional": 0.9,
        "friendly": 0.5,
        "creative": 0.7
    },
    keywords=["technology", "innovation", "solutions"]
)

# Create audience profile
audience = AudienceProfile(
    name="Tech Professionals",
    demographics={
        "age_range": [25, 45],
        "gender": "all",
        "location": "global",
        "interests": ["technology", "programming", "AI"]
    }
)

# Create ad content
ad = AdContent(
    title="Revolutionary AI Solution",
    description="Transform your business with our AI platform",
    call_to_action="Learn More",
    target_audience="Tech Professionals",
    platform="linkedin",
    status="approved"
)

# Create campaign
campaign = AdCampaign(
    name="Q2 Tech Campaign",
    description="Promoting our AI solutions",
    start_date=datetime.utcnow(),
    end_date=datetime.utcnow() + timedelta(days=30),
    budget=10000.0,
    target_audience="Tech Professionals",
    platforms=["linkedin", "twitter"],
    ads=[ad]
)

# Index models
redis_indexer = RedisIndexer()
model_config.index(redis_indexer)
brand_voice.index(redis_indexer)
audience.index(redis_indexer)
ad.index(redis_indexer)
campaign.index(redis_indexer)

# Get performance metrics
metrics = campaign.get_performance_metrics()
""" 