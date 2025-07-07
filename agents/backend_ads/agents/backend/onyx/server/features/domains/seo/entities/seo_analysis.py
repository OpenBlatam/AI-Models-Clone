"""
SEO Analysis Entity

This module contains the core SEO analysis entity that represents
the domain model for SEO analysis operations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

from ....core.base import BaseEntity, ValueObject


class SEOKeywords(ValueObject):
    """SEO keywords value object."""
    
    primary: List[str] = Field(default_factory=list)
    secondary: List[str] = Field(default_factory=list)
    long_tail: List[str] = Field(default_factory=list)
    
    @validator('primary', 'secondary', 'long_tail')
    def validate_keywords(cls, v):
        """Validate keywords are not empty strings."""
        return [kw.strip().lower() for kw in v if kw.strip()]


class SEOMetrics(ValueObject):
    """SEO metrics value object."""
    
    title_length: int = Field(ge=0, le=60)
    description_length: int = Field(ge=0, le=160)
    keyword_density: float = Field(ge=0.0, le=10.0)
    readability_score: float = Field(ge=0.0, le=100.0)
    word_count: int = Field(ge=0)
    heading_count: int = Field(ge=0)
    image_count: int = Field(ge=0)
    link_count: int = Field(ge=0)
    
    @property
    def title_optimization_score(self) -> float:
        """Calculate title optimization score."""
        if self.title_length == 0:
            return 0.0
        if 30 <= self.title_length <= 60:
            return 100.0
        elif 20 <= self.title_length < 30:
            return 80.0
        elif 60 < self.title_length <= 70:
            return 60.0
        else:
            return 20.0
    
    @property
    def description_optimization_score(self) -> float:
        """Calculate description optimization score."""
        if self.description_length == 0:
            return 0.0
        if 120 <= self.description_length <= 160:
            return 100.0
        elif 100 <= self.description_length < 120:
            return 80.0
        elif 160 < self.description_length <= 180:
            return 60.0
        else:
            return 20.0


class SEOIssues(ValueObject):
    """SEO issues value object."""
    
    critical: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    
    @property
    def total_issues(self) -> int:
        """Get total number of issues."""
        return len(self.critical) + len(self.warnings) + len(self.suggestions)
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if there are critical issues."""
        return len(self.critical) > 0


class SEOAnalysis(BaseEntity):
    """SEO Analysis entity."""
    
    url: str = Field(..., description="URL being analyzed")
    title: Optional[str] = None
    meta_description: Optional[str] = None
    content: Optional[str] = None
    
    # SEO Components
    keywords: SEOKeywords = Field(default_factory=SEOKeywords)
    metrics: SEOMetrics = Field(default_factory=SEOMetrics)
    issues: SEOIssues = Field(default_factory=SEOIssues)
    
    # Analysis metadata
    analysis_type: str = Field(default="comprehensive")
    analysis_depth: str = Field(default="standard")
    processing_time_ms: Optional[int] = None
    model_used: Optional[str] = None
    
    # Technical SEO
    technical_seo: Dict[str, Any] = Field(default_factory=dict)
    on_page_seo: Dict[str, Any] = Field(default_factory=dict)
    content_seo: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v
    
    @property
    def overall_score(self) -> float:
        """Calculate overall SEO score."""
        if not self.metrics:
            return 0.0
        
        scores = [
            self.metrics.title_optimization_score * 0.2,
            self.metrics.description_optimization_score * 0.2,
            min(self.metrics.readability_score, 100.0) * 0.3,
            max(0, 100 - (self.issues.total_issues * 5)) * 0.3
        ]
        
        return sum(scores)
    
    @property
    def grade(self) -> str:
        """Get SEO grade based on overall score."""
        score = self.overall_score
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def add_issue(self, issue_type: str, message: str) -> None:
        """Add an issue to the analysis."""
        if issue_type == "critical":
            self.issues.critical.append(message)
        elif issue_type == "warning":
            self.issues.warnings.append(message)
        elif issue_type == "suggestion":
            self.issues.suggestions.append(message)
    
    def update_metrics(self, **kwargs) -> None:
        """Update SEO metrics."""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "meta_description": self.meta_description,
            "overall_score": self.overall_score,
            "grade": self.grade,
            "total_issues": self.issues.total_issues,
            "has_critical_issues": self.issues.has_critical_issues,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 