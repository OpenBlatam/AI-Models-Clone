"""
🚀 ULTRA-EXTREME V6 - CONTENT SERVICE DOMAIN ENTITIES
Clean architecture domain entities for content management
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from enum import Enum
import uuid
import json

class ContentType(Enum):
    """Content type enumeration"""
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    ADVERTISEMENT = "advertisement"
    PRODUCT_DESCRIPTION = "product_description"
    LANDING_PAGE = "landing_page"
    VIDEO_SCRIPT = "video_script"
    PODCAST_SCRIPT = "podcast_script"

class ContentStatus(Enum):
    """Content status enumeration"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"

class ContentPriority(Enum):
    """Content priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class ContentMetadata:
    """Content metadata for SEO and analytics"""
    title: str
    description: str
    keywords: List[str] = field(default_factory=list)
    author: str = ""
    category: str = ""
    tags: List[str] = field(default_factory=list)
    language: str = "en"
    target_audience: List[str] = field(default_factory=list)
    seo_score: float = 0.0
    readability_score: float = 0.0
    sentiment_score: float = 0.0

@dataclass
class ContentOptimization:
    """Content optimization data"""
    ai_optimized: bool = False
    optimization_score: float = 0.0
    suggested_improvements: List[str] = field(default_factory=list)
    keyword_density: Dict[str, float] = field(default_factory=dict)
    readability_level: str = "intermediate"
    word_count: int = 0
    reading_time: int = 0
    engagement_score: float = 0.0

@dataclass
class ContentAnalytics:
    """Content analytics and performance metrics"""
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    click_through_rate: float = 0.0
    bounce_rate: float = 0.0
    time_on_page: float = 0.0
    conversion_rate: float = 0.0
    revenue_generated: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ContentVersion:
    """Content version for version control"""
    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    metadata: ContentMetadata = field(default_factory=ContentMetadata)
    optimization: ContentOptimization = field(default_factory=ContentOptimization)
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    change_description: str = ""
    is_current: bool = False

@dataclass
class ContentCollaboration:
    """Content collaboration and workflow data"""
    assigned_to: str = ""
    reviewers: List[str] = field(default_factory=list)
    approvers: List[str] = field(default_factory=list)
    workflow_stage: str = "draft"
    review_comments: List[Dict[str, Any]] = field(default_factory=list)
    approval_status: str = "pending"
    collaboration_score: float = 0.0
    team_efficiency: float = 0.0

@dataclass
class ContentEntity:
    """
    🎯 CONTENT ENTITY - DOMAIN CORE
    
    This is the central domain entity for content management,
    encapsulating all content-related business logic and rules.
    """
    
    # Core identifiers
    content_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    external_id: Optional[str] = None
    
    # Content properties
    content_type: ContentType = ContentType.BLOG_POST
    title: str = ""
    content: str = ""
    status: ContentStatus = ContentStatus.DRAFT
    priority: ContentPriority = ContentPriority.MEDIUM
    
    # Rich data
    metadata: ContentMetadata = field(default_factory=ContentMetadata)
    optimization: ContentOptimization = field(default_factory=ContentOptimization)
    analytics: ContentAnalytics = field(default_factory=ContentAnalytics)
    collaboration: ContentCollaboration = field(default_factory=ContentCollaboration)
    
    # Version control
    versions: List[ContentVersion] = field(default_factory=list)
    current_version: Optional[ContentVersion] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
    # Business rules
    is_active: bool = True
    is_featured: bool = False
    is_premium: bool = False
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        self._validate_content()
        self._setup_current_version()
        self._calculate_metrics()
    
    def _validate_content(self):
        """Validate content according to business rules"""
        if not self.title.strip():
            raise ValueError("Content title cannot be empty")
        
        if not self.content.strip():
            raise ValueError("Content body cannot be empty")
        
        if len(self.title) > 200:
            raise ValueError("Content title cannot exceed 200 characters")
        
        if len(self.content) > 50000:
            raise ValueError("Content body cannot exceed 50,000 characters")
    
    def _setup_current_version(self):
        """Setup current version if not exists"""
        if not self.current_version:
            self.current_version = ContentVersion(
                content=self.content,
                metadata=self.metadata,
                optimization=self.optimization,
                is_current=True
            )
            self.versions.append(self.current_version)
    
    def _calculate_metrics(self):
        """Calculate content metrics"""
        # Calculate word count
        self.optimization.word_count = len(self.content.split())
        
        # Calculate reading time (average 200 words per minute)
        self.optimization.reading_time = max(1, self.optimization.word_count // 200)
        
        # Calculate engagement score
        self._calculate_engagement_score()
    
    def _calculate_engagement_score(self):
        """Calculate content engagement score"""
        # Base score from content quality
        base_score = 0.5
        
        # Title quality bonus
        if len(self.title) > 10 and len(self.title) < 60:
            base_score += 0.1
        
        # Content length bonus
        if 500 <= self.optimization.word_count <= 2000:
            base_score += 0.1
        elif self.optimization.word_count > 2000:
            base_score += 0.05
        
        # SEO score bonus
        base_score += self.metadata.seo_score * 0.2
        
        # Readability bonus
        base_score += self.optimization.readability_score * 0.1
        
        # Sentiment bonus
        base_score += abs(self.metadata.sentiment_score) * 0.05
        
        self.optimization.engagement_score = min(1.0, base_score)
    
    def update_content(self, new_content: str, user_id: str, change_description: str = "") -> ContentVersion:
        """Update content and create new version"""
        # Create new version
        new_version = ContentVersion(
            content=new_content,
            metadata=self.metadata,
            optimization=self.optimization,
            created_by=user_id,
            change_description=change_description,
            is_current=True
        )
        
        # Update current version
        if self.current_version:
            self.current_version.is_current = False
        
        self.current_version = new_version
        self.versions.append(new_version)
        
        # Update content
        self.content = new_content
        self.updated_at = datetime.utcnow()
        
        # Recalculate metrics
        self._calculate_metrics()
        
        return new_version
    
    def update_metadata(self, new_metadata: ContentMetadata, user_id: str) -> None:
        """Update content metadata"""
        self.metadata = new_metadata
        self.updated_at = datetime.utcnow()
        
        # Update current version metadata
        if self.current_version:
            self.current_version.metadata = new_metadata
        
        # Recalculate metrics
        self._calculate_metrics()
    
    def update_optimization(self, new_optimization: ContentOptimization) -> None:
        """Update content optimization data"""
        self.optimization = new_optimization
        self.updated_at = datetime.utcnow()
        
        # Update current version optimization
        if self.current_version:
            self.current_version.optimization = new_optimization
        
        # Recalculate metrics
        self._calculate_metrics()
    
    def change_status(self, new_status: ContentStatus, user_id: str) -> None:
        """Change content status"""
        # Validate status transition
        self._validate_status_transition(new_status)
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        # Set published date if publishing
        if new_status == ContentStatus.PUBLISHED and not self.published_at:
            self.published_at = datetime.utcnow()
    
    def _validate_status_transition(self, new_status: ContentStatus) -> None:
        """Validate status transition according to business rules"""
        valid_transitions = {
            ContentStatus.DRAFT: [ContentStatus.IN_REVIEW, ContentStatus.ARCHIVED],
            ContentStatus.IN_REVIEW: [ContentStatus.DRAFT, ContentStatus.APPROVED, ContentStatus.REJECTED],
            ContentStatus.APPROVED: [ContentStatus.PUBLISHED, ContentStatus.DRAFT],
            ContentStatus.PUBLISHED: [ContentStatus.ARCHIVED],
            ContentStatus.ARCHIVED: [ContentStatus.DRAFT],
            ContentStatus.REJECTED: [ContentStatus.DRAFT, ContentStatus.ARCHIVED]
        }
        
        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")
    
    def assign_reviewer(self, reviewer_id: str) -> None:
        """Assign a reviewer to the content"""
        if reviewer_id not in self.collaboration.reviewers:
            self.collaboration.reviewers.append(reviewer_id)
            self.updated_at = datetime.utcnow()
    
    def add_review_comment(self, reviewer_id: str, comment: str, section: str = "") -> None:
        """Add a review comment"""
        review_comment = {
            "reviewer_id": reviewer_id,
            "comment": comment,
            "section": section,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.collaboration.review_comments.append(review_comment)
        self.updated_at = datetime.utcnow()
    
    def update_analytics(self, analytics_data: Dict[str, Any]) -> None:
        """Update content analytics"""
        for key, value in analytics_data.items():
            if hasattr(self.analytics, key):
                setattr(self.analytics, key, value)
        
        self.analytics.last_updated = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def is_ready_for_publishing(self) -> bool:
        """Check if content is ready for publishing"""
        return (
            self.status == ContentStatus.APPROVED and
            self.metadata.seo_score >= 0.7 and
            self.optimization.readability_score >= 0.6 and
            len(self.collaboration.reviewers) > 0
        )
    
    def get_content_summary(self) -> Dict[str, Any]:
        """Get content summary for quick overview"""
        return {
            "content_id": self.content_id,
            "title": self.title,
            "content_type": self.content_type.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "word_count": self.optimization.word_count,
            "reading_time": self.optimization.reading_time,
            "engagement_score": self.optimization.engagement_score,
            "seo_score": self.metadata.seo_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "content_id": self.content_id,
            "external_id": self.external_id,
            "content_type": self.content_type.value,
            "title": self.title,
            "content": self.content,
            "status": self.status.value,
            "priority": self.priority.value,
            "metadata": {
                "title": self.metadata.title,
                "description": self.metadata.description,
                "keywords": self.metadata.keywords,
                "author": self.metadata.author,
                "category": self.metadata.category,
                "tags": self.metadata.tags,
                "language": self.metadata.language,
                "target_audience": self.metadata.target_audience,
                "seo_score": self.metadata.seo_score,
                "readability_score": self.metadata.readability_score,
                "sentiment_score": self.metadata.sentiment_score
            },
            "optimization": {
                "ai_optimized": self.optimization.ai_optimized,
                "optimization_score": self.optimization.optimization_score,
                "suggested_improvements": self.optimization.suggested_improvements,
                "keyword_density": self.optimization.keyword_density,
                "readability_level": self.optimization.readability_level,
                "word_count": self.optimization.word_count,
                "reading_time": self.optimization.reading_time,
                "engagement_score": self.optimization.engagement_score
            },
            "analytics": {
                "views": self.analytics.views,
                "likes": self.analytics.likes,
                "shares": self.analytics.shares,
                "comments": self.analytics.comments,
                "click_through_rate": self.analytics.click_through_rate,
                "bounce_rate": self.analytics.bounce_rate,
                "time_on_page": self.analytics.time_on_page,
                "conversion_rate": self.analytics.conversion_rate,
                "revenue_generated": self.analytics.revenue_generated,
                "last_updated": self.analytics.last_updated.isoformat()
            },
            "collaboration": {
                "assigned_to": self.collaboration.assigned_to,
                "reviewers": self.collaboration.reviewers,
                "approvers": self.collaboration.approvers,
                "workflow_stage": self.collaboration.workflow_stage,
                "review_comments": self.collaboration.review_comments,
                "approval_status": self.collaboration.approval_status,
                "collaboration_score": self.collaboration.collaboration_score,
                "team_efficiency": self.collaboration.team_efficiency
            },
            "versions": [
                {
                    "version_id": version.version_id,
                    "content": version.content,
                    "created_at": version.created_at.isoformat(),
                    "created_by": version.created_by,
                    "change_description": version.change_description,
                    "is_current": version.is_current
                }
                for version in self.versions
            ],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "is_active": self.is_active,
            "is_featured": self.is_featured,
            "is_premium": self.is_premium
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentEntity':
        """Create entity from dictionary"""
        # Convert enums
        content_type = ContentType(data.get('content_type', 'blog_post'))
        status = ContentStatus(data.get('status', 'draft'))
        priority = ContentPriority(data.get('priority', 'medium'))
        
        # Create metadata
        metadata_data = data.get('metadata', {})
        metadata = ContentMetadata(
            title=metadata_data.get('title', ''),
            description=metadata_data.get('description', ''),
            keywords=metadata_data.get('keywords', []),
            author=metadata_data.get('author', ''),
            category=metadata_data.get('category', ''),
            tags=metadata_data.get('tags', []),
            language=metadata_data.get('language', 'en'),
            target_audience=metadata_data.get('target_audience', []),
            seo_score=metadata_data.get('seo_score', 0.0),
            readability_score=metadata_data.get('readability_score', 0.0),
            sentiment_score=metadata_data.get('sentiment_score', 0.0)
        )
        
        # Create optimization
        optimization_data = data.get('optimization', {})
        optimization = ContentOptimization(
            ai_optimized=optimization_data.get('ai_optimized', False),
            optimization_score=optimization_data.get('optimization_score', 0.0),
            suggested_improvements=optimization_data.get('suggested_improvements', []),
            keyword_density=optimization_data.get('keyword_density', {}),
            readability_level=optimization_data.get('readability_level', 'intermediate'),
            word_count=optimization_data.get('word_count', 0),
            reading_time=optimization_data.get('reading_time', 0),
            engagement_score=optimization_data.get('engagement_score', 0.0)
        )
        
        # Create analytics
        analytics_data = data.get('analytics', {})
        analytics = ContentAnalytics(
            views=analytics_data.get('views', 0),
            likes=analytics_data.get('likes', 0),
            shares=analytics_data.get('shares', 0),
            comments=analytics_data.get('comments', 0),
            click_through_rate=analytics_data.get('click_through_rate', 0.0),
            bounce_rate=analytics_data.get('bounce_rate', 0.0),
            time_on_page=analytics_data.get('time_on_page', 0.0),
            conversion_rate=analytics_data.get('conversion_rate', 0.0),
            revenue_generated=analytics_data.get('revenue_generated', 0.0),
            last_updated=datetime.fromisoformat(analytics_data.get('last_updated', datetime.utcnow().isoformat()))
        )
        
        # Create collaboration
        collaboration_data = data.get('collaboration', {})
        collaboration = ContentCollaboration(
            assigned_to=collaboration_data.get('assigned_to', ''),
            reviewers=collaboration_data.get('reviewers', []),
            approvers=collaboration_data.get('approvers', []),
            workflow_stage=collaboration_data.get('workflow_stage', 'draft'),
            review_comments=collaboration_data.get('review_comments', []),
            approval_status=collaboration_data.get('approval_status', 'pending'),
            collaboration_score=collaboration_data.get('collaboration_score', 0.0),
            team_efficiency=collaboration_data.get('team_efficiency', 0.0)
        )
        
        # Create versions
        versions = []
        for version_data in data.get('versions', []):
            version = ContentVersion(
                version_id=version_data.get('version_id', str(uuid.uuid4())),
                content=version_data.get('content', ''),
                created_at=datetime.fromisoformat(version_data.get('created_at', datetime.utcnow().isoformat())),
                created_by=version_data.get('created_by', ''),
                change_description=version_data.get('change_description', ''),
                is_current=version_data.get('is_current', False)
            )
            versions.append(version)
        
        # Parse timestamps
        created_at = datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat()))
        updated_at = datetime.fromisoformat(data.get('updated_at', datetime.utcnow().isoformat()))
        published_at = None
        if data.get('published_at'):
            published_at = datetime.fromisoformat(data['published_at'])
        
        return cls(
            content_id=data.get('content_id', str(uuid.uuid4())),
            external_id=data.get('external_id'),
            content_type=content_type,
            title=data.get('title', ''),
            content=data.get('content', ''),
            status=status,
            priority=priority,
            metadata=metadata,
            optimization=optimization,
            analytics=analytics,
            collaboration=collaboration,
            versions=versions,
            created_at=created_at,
            updated_at=updated_at,
            published_at=published_at,
            is_active=data.get('is_active', True),
            is_featured=data.get('is_featured', False),
            is_premium=data.get('is_premium', False)
        )

# Example usage
if __name__ == "__main__":
    # Create a sample content entity
    content = ContentEntity(
        title="Ultra-Extreme V6: Next-Generation Content Management",
        content="This is a comprehensive guide to the Ultra-Extreme V6 content management system...",
        content_type=ContentType.BLOG_POST,
        priority=ContentPriority.HIGH
    )
    
    # Update metadata
    metadata = ContentMetadata(
        title="Ultra-Extreme V6 Content Management",
        description="Comprehensive guide to next-generation content management",
        keywords=["content management", "AI", "optimization", "performance"],
        author="AI Assistant",
        category="Technology",
        tags=["AI", "Content", "Management"],
        seo_score=0.85,
        readability_score=0.78,
        sentiment_score=0.2
    )
    
    content.update_metadata(metadata, "user_123")
    
    # Print content summary
    print("🎯 CONTENT ENTITY SUMMARY:")
    summary = content.get_content_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Convert to dictionary
    content_dict = content.to_dict()
    print(f"\n📊 Content converted to dictionary with {len(content_dict)} fields")
    
    # Recreate from dictionary
    recreated_content = ContentEntity.from_dict(content_dict)
    print(f"✅ Content recreated successfully: {recreated_content.title}") 