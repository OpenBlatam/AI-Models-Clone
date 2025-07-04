"""
🚀 ULTRA-EXTREME CONTENT ENTITY V4
==================================

Ultra-extreme content entity with:
- Rich domain logic
- Validation rules
- Business methods
- Event generation
- Performance optimization
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json


class ContentType(Enum):
    """Content types"""
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    ADVERTISEMENT = "advertisement"
    PRODUCT_DESCRIPTION = "product_description"
    LANDING_PAGE = "landing_page"
    NEWS = "news"
    REVIEW = "review"
    TUTORIAL = "tutorial"
    WHITEPAPER = "whitepaper"
    CASE_STUDY = "case_study"


class ContentStatus(Enum):
    """Content status"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ContentPriority(Enum):
    """Content priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"


@dataclass
class ContentMetadata:
    """Content metadata"""
    title: str
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    author: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    reading_time: Optional[int] = None
    word_count: Optional[int] = None
    seo_score: Optional[float] = None
    engagement_score: Optional[float] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContentAnalytics:
    """Content analytics"""
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    clicks: int = 0
    conversions: int = 0
    bounce_rate: float = 0.0
    time_on_page: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContentOptimization:
    """Content optimization data"""
    seo_optimized: bool = False
    readability_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    keyword_density: Dict[str, float] = field(default_factory=dict)
    content_score: Optional[float] = None
    optimization_suggestions: List[str] = field(default_factory=list)
    last_optimized: Optional[datetime] = None


class UltraContent:
    """Ultra-extreme content entity"""
    
    def __init__(
        self,
        content_id: Optional[str] = None,
        content_type: ContentType = ContentType.ARTICLE,
        title: str = "",
        content: str = "",
        language: Language = Language.ENGLISH,
        status: ContentStatus = ContentStatus.DRAFT,
        priority: ContentPriority = ContentPriority.MEDIUM,
        metadata: Optional[ContentMetadata] = None,
        analytics: Optional[ContentAnalytics] = None,
        optimization: Optional[ContentOptimization] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        version: int = 1
    ):
        self.content_id = content_id or str(uuid.uuid4())
        self.content_type = content_type
        self.title = title
        self.content = content
        self.language = language
        self.status = status
        self.priority = priority
        self.metadata = metadata or ContentMetadata(title=title)
        self.analytics = analytics or ContentAnalytics()
        self.optimization = optimization or ContentOptimization()
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self.version = version
        
        # Validation
        self._validate()
    
    def _validate(self):
        """Validate content entity"""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        if not self.content or len(self.content.strip()) == 0:
            raise ValueError("Content cannot be empty")
        
        if len(self.title) > 500:
            raise ValueError("Title too long (max 500 characters)")
        
        if len(self.content) > 100000:
            raise ValueError("Content too long (max 100,000 characters)")
    
    # ============================================================================
    # BUSINESS METHODS
    # ============================================================================
    
    def update_content(self, new_content: str, new_title: Optional[str] = None) -> None:
        """Update content with validation"""
        if new_title:
            self.title = new_title
            self.metadata.title = new_title
        
        self.content = new_content
        self.updated_at = datetime.now(timezone.utc)
        self.version += 1
        
        # Recalculate metadata
        self._recalculate_metadata()
        
        # Reset optimization
        self.optimization.seo_optimized = False
        self.optimization.last_optimized = None
    
    def publish(self) -> None:
        """Publish content"""
        if self.status == ContentStatus.DRAFT:
            self.status = ContentStatus.PUBLISHED
            self.updated_at = datetime.now(timezone.utc)
        else:
            raise ValueError(f"Cannot publish content with status: {self.status}")
    
    def archive(self) -> None:
        """Archive content"""
        if self.status == ContentStatus.PUBLISHED:
            self.status = ContentStatus.ARCHIVED
            self.updated_at = datetime.now(timezone.utc)
        else:
            raise ValueError(f"Cannot archive content with status: {self.status}")
    
    def delete(self) -> None:
        """Delete content"""
        self.status = ContentStatus.DELETED
        self.updated_at = datetime.now(timezone.utc)
    
    def add_keyword(self, keyword: str) -> None:
        """Add keyword to metadata"""
        if keyword not in self.metadata.keywords:
            self.metadata.keywords.append(keyword)
            self.metadata.updated_at = datetime.now(timezone.utc)
    
    def remove_keyword(self, keyword: str) -> None:
        """Remove keyword from metadata"""
        if keyword in self.metadata.keywords:
            self.metadata.keywords.remove(keyword)
            self.metadata.updated_at = datetime.now(timezone.utc)
    
    def add_tag(self, tag: str) -> None:
        """Add tag to metadata"""
        if tag not in self.metadata.tags:
            self.metadata.tags.append(tag)
            self.metadata.updated_at = datetime.now(timezone.utc)
    
    def remove_tag(self, tag: str) -> None:
        """Remove tag from metadata"""
        if tag in self.metadata.tags:
            self.metadata.tags.remove(tag)
            self.metadata.updated_at = datetime.now(timezone.utc)
    
    def increment_views(self) -> None:
        """Increment view count"""
        self.analytics.views += 1
        self.analytics.last_updated = datetime.now(timezone.utc)
    
    def increment_likes(self) -> None:
        """Increment like count"""
        self.analytics.likes += 1
        self.analytics.last_updated = datetime.now(timezone.utc)
    
    def increment_shares(self) -> None:
        """Increment share count"""
        self.analytics.shares += 1
        self.analytics.last_updated = datetime.now(timezone.utc)
    
    def increment_comments(self) -> None:
        """Increment comment count"""
        self.analytics.comments += 1
        self.analytics.last_updated = datetime.now(timezone.utc)
    
    def increment_clicks(self) -> None:
        """Increment click count"""
        self.analytics.clicks += 1
        self.analytics.last_updated = datetime.now(timezone.utc)
    
    def increment_conversions(self) -> None:
        """Increment conversion count"""
        self.analytics.conversions += 1
        self.analytics.last_updated = datetime.now(timezone.utc)
    
    def update_bounce_rate(self, bounce_rate: float) -> None:
        """Update bounce rate"""
        self.analytics.bounce_rate = bounce_rate
        self.analytics.last_updated = datetime.now(timezone.utc)
    
    def update_time_on_page(self, time_on_page: float) -> None:
        """Update time on page"""
        self.analytics.time_on_page = time_on_page
        self.analytics.last_updated = datetime.now(timezone.utc)
    
    # ============================================================================
    # OPTIMIZATION METHODS
    # ============================================================================
    
    def optimize_for_seo(self, keywords: List[str]) -> str:
        """Optimize content for SEO"""
        # Simple SEO optimization
        optimized_content = self.content
        
        # Add keywords to title if not present
        title_keywords = [kw.lower() for kw in keywords]
        if not any(kw in self.title.lower() for kw in title_keywords):
            # Add primary keyword to title
            if keywords:
                optimized_title = f"{self.title} - {keywords[0]}"
                self.title = optimized_title
                self.metadata.title = optimized_title
        
        # Add keywords to content if not present
        for keyword in keywords:
            if keyword.lower() not in self.content.lower():
                # Add keyword naturally to content
                optimized_content += f"\n\n{keyword} is an important aspect to consider."
        
        self.content = optimized_content
        self.optimization.seo_optimized = True
        self.optimization.last_optimized = datetime.now(timezone.utc)
        
        return optimized_content
    
    def calculate_readability_score(self) -> float:
        """Calculate readability score (Flesch Reading Ease)"""
        # Simple implementation
        sentences = len(self.content.split('.'))
        words = len(self.content.split())
        syllables = self._count_syllables(self.content)
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Flesch Reading Ease formula
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0.0, min(100.0, score))
    
    def calculate_sentiment_score(self) -> float:
        """Calculate sentiment score (-1 to 1)"""
        # Simple sentiment analysis
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome'}
        negative_words = {'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'terrible', 'worst'}
        
        words = self.content.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_words = len(words)
        if total_words == 0:
            return 0.0
        
        score = (positive_count - negative_count) / total_words
        return max(-1.0, min(1.0, score))
    
    def calculate_keyword_density(self, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density"""
        words = self.content.lower().split()
        total_words = len(words)
        
        if total_words == 0:
            return {}
        
        density = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_count = sum(1 for word in words if keyword_lower in word)
            density[keyword] = (keyword_count / total_words) * 100
        
        self.optimization.keyword_density = density
        return density
    
    def calculate_content_score(self) -> float:
        """Calculate overall content score"""
        # Calculate various metrics
        readability = self.calculate_readability_score()
        sentiment = abs(self.calculate_sentiment_score())  # Use absolute value
        
        # Word count score (optimal range: 300-2000 words)
        word_count = len(self.content.split())
        if 300 <= word_count <= 2000:
            word_count_score = 1.0
        else:
            word_count_score = max(0.0, 1.0 - abs(word_count - 1150) / 1150)
        
        # Title length score (optimal: 50-60 characters)
        title_length = len(self.title)
        if 50 <= title_length <= 60:
            title_score = 1.0
        else:
            title_score = max(0.0, 1.0 - abs(title_length - 55) / 55)
        
        # Calculate weighted average
        score = (
            readability * 0.3 +
            sentiment * 0.2 +
            word_count_score * 0.25 +
            title_score * 0.25
        )
        
        self.optimization.content_score = score
        return score
    
    def generate_optimization_suggestions(self) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        # Check title length
        if len(self.title) < 30:
            suggestions.append("Title is too short. Aim for 50-60 characters.")
        elif len(self.title) > 60:
            suggestions.append("Title is too long. Aim for 50-60 characters.")
        
        # Check content length
        word_count = len(self.content.split())
        if word_count < 300:
            suggestions.append("Content is too short. Aim for at least 300 words.")
        elif word_count > 2000:
            suggestions.append("Content is too long. Consider breaking it into sections.")
        
        # Check readability
        readability = self.calculate_readability_score()
        if readability < 60:
            suggestions.append("Content is difficult to read. Consider simplifying language.")
        
        # Check keyword usage
        if not self.metadata.keywords:
            suggestions.append("Add relevant keywords to improve SEO.")
        
        self.optimization.optimization_suggestions = suggestions
        return suggestions
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _recalculate_metadata(self) -> None:
        """Recalculate metadata"""
        # Update word count
        self.metadata.word_count = len(self.content.split())
        
        # Calculate reading time (average 200 words per minute)
        if self.metadata.word_count:
            self.metadata.reading_time = max(1, self.metadata.word_count // 200)
        
        # Update timestamps
        self.metadata.updated_at = datetime.now(timezone.utc)
    
    def _count_syllables(self, text: str) -> int:
        """Count syllables in text (simplified)"""
        # Simple syllable counting
        vowels = 'aeiouy'
        count = 0
        text = text.lower()
        
        for char in text:
            if char in vowels:
                count += 1
        
        return count
    
    def generate_embeddings(self) -> List[float]:
        """Generate content embeddings (placeholder)"""
        # This would typically use a language model
        # For now, return a simple hash-based embedding
        content_hash = hashlib.md5(self.content.encode()).hexdigest()
        return [float(int(content_hash[i:i+2], 16)) / 255.0 for i in range(0, 32, 2)]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content_id": self.content_id,
            "content_type": self.content_type.value,
            "title": self.title,
            "content": self.content,
            "language": self.language.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "metadata": {
                "title": self.metadata.title,
                "description": self.metadata.description,
                "keywords": self.metadata.keywords,
                "author": self.metadata.author,
                "category": self.metadata.category,
                "tags": self.metadata.tags,
                "reading_time": self.metadata.reading_time,
                "word_count": self.metadata.word_count,
                "seo_score": self.metadata.seo_score,
                "engagement_score": self.metadata.engagement_score,
                "created_at": self.metadata.created_at.isoformat(),
                "updated_at": self.metadata.updated_at.isoformat(),
            },
            "analytics": {
                "views": self.analytics.views,
                "likes": self.analytics.likes,
                "shares": self.analytics.shares,
                "comments": self.analytics.comments,
                "clicks": self.analytics.clicks,
                "conversions": self.analytics.conversions,
                "bounce_rate": self.analytics.bounce_rate,
                "time_on_page": self.analytics.time_on_page,
                "last_updated": self.analytics.last_updated.isoformat(),
            },
            "optimization": {
                "seo_optimized": self.optimization.seo_optimized,
                "readability_score": self.optimization.readability_score,
                "sentiment_score": self.optimization.sentiment_score,
                "keyword_density": self.optimization.keyword_density,
                "content_score": self.optimization.content_score,
                "optimization_suggestions": self.optimization.optimization_suggestions,
                "last_optimized": self.optimization.last_optimized.isoformat() if self.optimization.last_optimized else None,
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UltraContent':
        """Create from dictionary"""
        return cls(
            content_id=data.get("content_id"),
            content_type=ContentType(data.get("content_type", "article")),
            title=data.get("title", ""),
            content=data.get("content", ""),
            language=Language(data.get("language", "en")),
            status=ContentStatus(data.get("status", "draft")),
            priority=ContentPriority(data.get("priority", "medium")),
            metadata=ContentMetadata(**data.get("metadata", {})),
            analytics=ContentAnalytics(**data.get("analytics", {})),
            optimization=ContentOptimization(**data.get("optimization", {})),
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data.get("updated_at")) if data.get("updated_at") else None,
            version=data.get("version", 1)
        )
    
    def __str__(self) -> str:
        """String representation"""
        return f"UltraContent(id={self.content_id}, title='{self.title}', type={self.content_type.value})"
    
    def __repr__(self) -> str:
        """Representation"""
        return self.__str__() 