"""
Blog Posts Data Models.

Pydantic models for blog post management with comprehensive validation.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from uuid import uuid4, UUID

from pydantic import BaseModel, Field, validator, root_validator
from .config import ContentLanguage, ContentTone, BlogPostStatus, SEOLevel


class BlogPostMetadata(BaseModel):
    """Metadata for blog posts."""
    author: str
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    featured_image: Optional[str] = None
    excerpt: Optional[str] = None
    read_time_minutes: Optional[int] = None
    word_count: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "author": "John Doe",
                "tags": ["technology", "AI", "blogging"],
                "category": "Tech",
                "featured_image": "https://example.com/image.jpg",
                "excerpt": "A brief excerpt of the blog post...",
                "read_time_minutes": 5,
                "word_count": 1200
            }
        }


class SEOData(BaseModel):
    """SEO optimization data."""
    title: str = Field(..., max_length=60)
    meta_description: str = Field(..., max_length=160)
    keywords: List[str] = Field(default_factory=list)
    keyword_density: Optional[float] = None
    readability_score: Optional[float] = None
    schema_markup: Optional[Dict[str, Any]] = None
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("SEO title must be at least 10 characters")
        return v.strip()
    
    @validator('meta_description')
    def validate_meta_description(cls, v):
        if len(v.strip()) < 50:
            raise ValueError("Meta description must be at least 50 characters")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "title": "The Ultimate Guide to AI-Powered Content Creation",
                "meta_description": "Discover how artificial intelligence is revolutionizing content creation with practical tips and real-world examples.",
                "keywords": ["AI", "content creation", "artificial intelligence"],
                "keyword_density": 1.5,
                "readability_score": 75.2
            }
        }


class ContentRequest(BaseModel):
    """Request model for content generation."""
    topic: str = Field(..., min_length=5, max_length=200)
    target_audience: str = Field(..., min_length=5, max_length=100)
    content_type: str = Field(default="blog_post")
    language: ContentLanguage = Field(default=ContentLanguage.ENGLISH)
    tone: ContentTone = Field(default=ContentTone.PROFESSIONAL)
    keywords: List[str] = Field(default_factory=list)
    length_words: Optional[int] = Field(default=1000, ge=300, le=5000)
    include_outline: bool = Field(default=True)
    include_seo: bool = Field(default=True)
    custom_instructions: Optional[str] = None
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if len(v) > 10:
            raise ValueError("Maximum 10 keywords allowed")
        return [kw.strip().lower() for kw in v if kw.strip()]
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "Benefits of AI in Modern Marketing",
                "target_audience": "Marketing professionals and business owners",
                "content_type": "blog_post",
                "language": "en",
                "tone": "professional",
                "keywords": ["AI marketing", "automation", "personalization"],
                "length_words": 1500,
                "include_outline": True,
                "include_seo": True
            }
        }


class BlogPost(BaseModel):
    """Main blog post model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=10, max_length=200)
    content: str = Field(..., min_length=100)
    status: BlogPostStatus = Field(default=BlogPostStatus.DRAFT)
    language: ContentLanguage = Field(default=ContentLanguage.ENGLISH)
    tone: ContentTone = Field(default=ContentTone.PROFESSIONAL)
    
    # Metadata
    metadata: BlogPostMetadata
    seo: Optional[SEOData] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    # Content structure
    outline: Optional[List[str]] = None
    html_content: Optional[str] = None
    
    # Analytics
    view_count: int = Field(default=0, ge=0)
    like_count: int = Field(default=0, ge=0)
    share_count: int = Field(default=0, ge=0)
    
    # Publishing
    slug: Optional[str] = None
    featured: bool = Field(default=False)
    
    @validator('title')
    def validate_title(cls, v):
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        if len(v.split()) < 50:
            raise ValueError("Content must have at least 50 words")
        return v.strip()
    
    @validator('slug')
    def validate_slug(cls, v):
        if v:
            import re
            if not re.match(r'^[a-z0-9-]+$', v):
                raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        return v
    
    @root_validator
    def validate_published_status(cls, values):
        status = values.get('status')
        published_at = values.get('published_at')
        
        if status == BlogPostStatus.PUBLISHED and not published_at:
            values['published_at'] = datetime.now(timezone.utc)
        elif status != BlogPostStatus.PUBLISHED and published_at:
            values['published_at'] = None
            
        return values
    
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)
    
    def publish(self):
        """Publish the blog post."""
        self.status = BlogPostStatus.PUBLISHED
        self.published_at = datetime.now(timezone.utc)
        self.update_timestamp()
    
    def unpublish(self):
        """Unpublish the blog post."""
        self.status = BlogPostStatus.DRAFT
        self.published_at = None
        self.update_timestamp()
    
    class Config:
        schema_extra = {
            "example": {
                "title": "The Future of AI in Content Marketing",
                "content": "Artificial intelligence is transforming the way we create and distribute content...",
                "status": "draft",
                "language": "en",
                "tone": "professional",
                "metadata": {
                    "author": "Jane Smith",
                    "tags": ["AI", "marketing", "content"],
                    "category": "Technology"
                }
            }
        }


class ContentGenerationResult(BaseModel):
    """Result of content generation."""
    success: bool
    content: Optional[str] = None
    title: Optional[str] = None
    outline: Optional[List[str]] = None
    seo_data: Optional[SEOData] = None
    metadata: Optional[Dict[str, Any]] = None
    generation_time_ms: Optional[int] = None
    word_count: Optional[int] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "content": "Generated blog post content...",
                "title": "AI-Powered Marketing Strategies",
                "outline": ["Introduction", "Benefits", "Implementation", "Conclusion"],
                "generation_time_ms": 2500,
                "word_count": 1200
            }
        }


class PublishingConfig(BaseModel):
    """Configuration for publishing blog posts."""
    auto_publish: bool = Field(default=False)
    schedule_publish: Optional[datetime] = None
    platforms: List[str] = Field(default_factory=list)
    social_media_posts: bool = Field(default=True)
    send_notifications: bool = Field(default=True)
    seo_optimizations: bool = Field(default=True)
    
    class Config:
        schema_extra = {
            "example": {
                "auto_publish": False,
                "schedule_publish": "2024-01-15T10:00:00Z",
                "platforms": ["wordpress", "medium"],
                "social_media_posts": True,
                "send_notifications": True,
                "seo_optimizations": True
            }
        }


class SEOConfig(BaseModel):
    """Configuration for SEO optimization."""
    level: SEOLevel = Field(default=SEOLevel.ADVANCED)
    target_keywords: List[str] = Field(default_factory=list)
    keyword_density_target: float = Field(default=1.5, ge=0.5, le=5.0)
    readability_target: float = Field(default=70.0, ge=0.0, le=100.0)
    include_schema_markup: bool = Field(default=True)
    optimize_images: bool = Field(default=True)
    generate_meta_tags: bool = Field(default=True)
    
    class Config:
        schema_extra = {
            "example": {
                "level": "advanced",
                "target_keywords": ["AI marketing", "content strategy"],
                "keyword_density_target": 1.5,
                "readability_target": 75.0,
                "include_schema_markup": True
            }
        }


class BlogPostBatch(BaseModel):
    """Batch processing for multiple blog posts."""
    batch_id: str = Field(default_factory=lambda: str(uuid4()))
    posts: List[BlogPost]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = Field(default="processing")
    total_count: int = Field(default=0)
    completed_count: int = Field(default=0)
    failed_count: int = Field(default=0)
    
    @validator('total_count', always=True)
    def set_total_count(cls, v, values):
        posts = values.get('posts', [])
        return len(posts)
    
    def update_progress(self, completed: int, failed: int):
        """Update batch processing progress."""
        self.completed_count = completed
        self.failed_count = failed
        
        if completed + failed >= self.total_count:
            self.status = "completed"
        elif failed > 0:
            self.status = "partial_failure"


# Export all models
__all__ = [
    "BlogPost",
    "BlogPostMetadata", 
    "SEOData",
    "ContentRequest",
    "ContentGenerationResult",
    "PublishingConfig",
    "SEOConfig",
    "BlogPostBatch"
] 