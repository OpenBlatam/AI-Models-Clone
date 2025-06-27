"""
🎯 Facebook Posts - Onyx Features Refactored Model
================================================

Clean Architecture implementation ubicado en:
/agents/backend/onyx/server/features/facebook_posts/
"""

from typing import List, Optional, Dict, Any, Protocol
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid
import hashlib
from pydantic import BaseModel, Field, validator

__version__ = "2.0.0"

# ===== DOMAIN ENUMS =====

class PostType(str, Enum):
    TEXT = "text"
    IMAGE = "image" 
    VIDEO = "video"
    LINK = "link"
    CAROUSEL = "carousel"

class ContentTone(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    INSPIRING = "inspiring"

class TargetAudience(str, Enum):
    GENERAL = "general"
    PROFESSIONALS = "professionals"
    ENTREPRENEURS = "entrepreneurs"
    STUDENTS = "students"

class EngagementTier(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VIRAL = "viral"

class ContentStatus(str, Enum):
    DRAFT = "draft"
    ANALYZING = "analyzing"
    APPROVED = "approved"
    PUBLISHED = "published"

# ===== VALUE OBJECTS =====

@dataclass(frozen=True)
class ContentIdentifier:
    """Identificador único inmutable."""
    content_id: str
    content_hash: str
    created_at: datetime
    
    @classmethod
    def generate(cls, content: str) -> 'ContentIdentifier':
        return cls(
            content_id=str(uuid.uuid4()),
            content_hash=hashlib.sha256(content.encode()).hexdigest()[:12],
            created_at=datetime.now()
        )

@dataclass(frozen=True)
class PostSpecification:
    """Especificación del post."""
    topic: str
    post_type: PostType
    tone: ContentTone
    target_audience: TargetAudience
    keywords: List[str]

@dataclass(frozen=True)
class ContentMetrics:
    """Métricas calculadas."""
    character_count: int
    word_count: int
    hashtag_count: int
    readability_score: float
    sentiment_score: float
    
    @property
    def engagement_potential(self) -> float:
        return (self.readability_score + abs(self.sentiment_score)) / 2

# ===== ENTITIES =====

class PostContent(BaseModel):
    """Contenido del post."""
    text: str = Field(..., min_length=10, max_length=1000)
    hashtags: List[str] = Field(default_factory=list)
    call_to_action: Optional[str] = None
    
    @validator('text')
    def validate_text(cls, v):
        return v.strip()

class PostAnalysis(BaseModel):
    """Análisis del post."""
    content_metrics: ContentMetrics
    predicted_likes: int
    predicted_shares: int
    engagement_rate: float
    confidence: float
    
    def get_overall_score(self) -> float:
        return (self.content_metrics.engagement_potential + self.engagement_rate) / 2
    
    def get_quality_tier(self) -> str:
        score = self.get_overall_score()
        if score >= 0.8: return "Excellent"
        elif score >= 0.6: return "Good"
        else: return "Fair"

class FacebookPost(BaseModel):
    """Entidad principal."""
    
    identifier: ContentIdentifier
    specification: PostSpecification
    content: PostContent
    status: ContentStatus = ContentStatus.DRAFT
    analysis: Optional[PostAnalysis] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Onyx integration
    onyx_workspace_id: Optional[str] = None
    onyx_user_id: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def set_analysis(self, analysis: PostAnalysis) -> None:
        self.analysis = analysis
        if analysis.get_overall_score() >= 0.7:
            self.status = ContentStatus.APPROVED
    
    def is_ready(self) -> bool:
        return self.analysis is not None and self.analysis.get_overall_score() >= 0.6
    
    def get_quality_tier(self) -> str:
        return self.analysis.get_quality_tier() if self.analysis else "Unassessed"

# ===== SERVICES =====

class ContentGenerationService(Protocol):
    async def generate_content(self, spec: PostSpecification) -> PostContent: ...

class ContentAnalysisService(Protocol):
    async def analyze_content(self, post: FacebookPost) -> PostAnalysis: ...

# ===== FACTORY =====

class FacebookPostFactory:
    """Factory para crear posts."""
    
    @staticmethod
    def create_post(
        topic: str,
        content_text: str,
        audience: TargetAudience = TargetAudience.GENERAL,
        hashtags: List[str] = None
    ) -> FacebookPost:
        
        spec = PostSpecification(
            topic=topic,
            post_type=PostType.TEXT,
            tone=ContentTone.FRIENDLY,
            target_audience=audience,
            keywords=[topic.lower()]
        )
        
        content = PostContent(
            text=content_text,
            hashtags=hashtags or []
        )
        
        return FacebookPost(
            identifier=ContentIdentifier.generate(content_text),
            specification=spec,
            content=content
        )

# ===== DEMO =====

def demo():
    """Demo del modelo refactorizado."""
    print("🎯 Facebook Posts - Onyx Features (REFACTORED)")
    print("=" * 50)
    
    # Create post
    post = FacebookPostFactory.create_post(
        topic="AI Marketing",
        content_text="🚀 AI transforms marketing! Boost your ROI today.",
        audience=TargetAudience.ENTREPRENEURS,
        hashtags=["AI", "marketing", "growth"]
    )
    
    print(f"✅ Post created: {post.identifier.content_id[:8]}...")
    print(f"📝 Content: {post.content.text}")
    print(f"🎯 Audience: {post.specification.target_audience.value}")
    
    # Create analysis
    metrics = ContentMetrics(
        character_count=len(post.content.text),
        word_count=len(post.content.text.split()),
        hashtag_count=len(post.content.hashtags),
        readability_score=0.8,
        sentiment_score=0.7
    )
    
    analysis = PostAnalysis(
        content_metrics=metrics,
        predicted_likes=150,
        predicted_shares=25,
        engagement_rate=0.75,
        confidence=0.85
    )
    
    post.set_analysis(analysis)
    
    print(f"\n📈 Analysis:")
    print(f"   Score: {analysis.get_overall_score():.2f}")
    print(f"   Tier: {post.get_quality_tier()}")
    print(f"   Status: {post.status.value}")
    print(f"   Ready: {post.is_ready()}")
    
    print(f"\n📊 Model Stats:")
    print(f"   - Location: /features/facebook_posts/")
    print(f"   - Enums: 5")
    print(f"   - Value Objects: 3")
    print(f"   - Entities: 3")
    print(f"   - Services: 2")
    print(f"   - Factory: 1")
    
    print("\n✅ REFACTOR COMPLETADO!")
    print("🚀 Modelo migrado exitosamente a Onyx Features")
    
    return post

if __name__ == "__main__":
    demo() 