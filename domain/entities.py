from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
from pydantic import BaseModel, Field, validator
import re
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
🎯 Facebook Posts - Domain Entities (Onyx Compatible)
====================================================

Entidades del dominio refactorizadas siguiendo arquitectura de features Onyx.
Compatible con Clean Architecture y patterns establecidos.
"""



# ===== DOMAIN ENUMS =====

class PostType(str, Enum):
    TEXT = "text"
    IMAGE = "image" 
    VIDEO = "video"
    LINK = "link"
    CAROUSEL = "carousel"
    POLL = "poll"
    STORY = "story"
    LIVE = "live"


class ContentTone(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual" 
    FRIENDLY = "friendly"
    HUMOROUS = "humorous"
    INSPIRING = "inspiring"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    AUTHORITATIVE = "authoritative"


class TargetAudience(str, Enum):
    GENERAL = "general"
    MILLENNIALS = "millennials"
    GEN_Z = "gen_z"
    PROFESSIONALS = "professionals"
    ENTREPRENEURS = "entrepreneurs"
    PARENTS = "parents"
    STUDENTS = "students"
    SENIORS = "seniors"
    CUSTOM = "custom"


class EngagementTier(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXCEPTIONAL = "exceptional"
    VIRAL = "viral"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# ===== VALUE OBJECTS =====

@dataclass(frozen=True)
class PostIdentifier:
    """Identificador inmutable siguiendo patterns Onyx."""
    post_id: str
    content_hash: str
    created_at: datetime
    version: str = "2.0"
    
    @classmethod
    def generate(cls, content: str) -> 'PostIdentifier':
        """Generar identificador único."""
        post_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return cls(
            post_id=post_id,
            content_hash=content_hash,
            created_at=datetime.now()
        )


@dataclass(frozen=True)
class ContentMetrics:
    """Métricas calculadas del contenido."""
    character_count: int
    word_count: int
    sentence_count: int
    hashtag_count: int
    mention_count: int
    emoji_count: int
    link_count: int
    readability_score: float
    sentiment_score: float
    
    @property
    def engagement_factors(self) -> Dict[str, float]:
        """Factores de engagement optimizados."""
        return {
            'optimal_length': 1.0 if 100 <= self.character_count <= 300 else 0.7,
            'hashtag_usage': min(1.0, self.hashtag_count / 5),
            'emoji_presence': 1.0 if self.emoji_count > 0 else 0.8,
            'readability': self.readability_score,
            'sentiment': abs(self.sentiment_score)
        }


@dataclass(frozen=True)
class EngagementPrediction:
    """Predicción de engagement usando ML."""
    predicted_likes: int
    predicted_shares: int
    predicted_comments: int
    predicted_reach: int
    engagement_rate: float
    virality_score: float
    confidence: float
    optimal_time: Optional[datetime] = None
    
    @property
    def total_interactions(self) -> int:
        return self.predicted_likes + self.predicted_shares + self.predicted_comments


@dataclass(frozen=True)
class QualityAssessment:
    """Evaluación de calidad avanzada."""
    overall_score: float
    brand_alignment: float
    content_uniqueness: float
    audience_match: float
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    
    @property
    def quality_tier(self) -> str:
        if self.overall_score >= 0.9:
            return "Exceptional"
        elif self.overall_score >= 0.8:
            return "Excellent"
        elif self.overall_score >= 0.7:
            return "Good"
        elif self.overall_score >= 0.6:
            return "Fair"
        else:
            return "Poor"


# ===== CORE ENTITIES =====

class PostContent(BaseModel):
    """Contenido del post con validaciones Onyx."""
    
    text: str = Field(..., min_length=10, max_length=2000)
    hashtags: List[str] = Field(default_factory=list, max_items=10)
    mentions: List[str] = Field(default_factory=list)
    media_urls: List[str] = Field(default_factory=list)
    link_url: Optional[str] = None
    
    @validator('text')
    def validate_text(cls, v) -> bool:
        return v.strip()
    
    @validator('hashtags')
    def validate_hashtags(cls, v) -> bool:
        return [tag.strip().replace('#', '').lower() for tag in v if tag.strip()]
    
    def get_display_text(self) -> str:
        """Texto completo con hashtags."""
        text = self.text
        if self.hashtags:
            text += "\n\n" + " ".join(f"#{tag}" for tag in self.hashtags)
        return text
    
    def calculate_metrics(self) -> ContentMetrics:
        """Calcular métricas usando NLP optimizado."""
        
        text = self.text
        words = text.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Emoji detection optimizada
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "]+", flags=re.UNICODE
        )
        emojis = emoji_pattern.findall(text)
        
        # Readability optimizada (Flesch-inspired)
        avg_sentence_length = len(words) / max(len(sentences), 1)
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        readability = max(0, min(1, 1.2 - (avg_sentence_length / 20 + avg_word_length / 6)))
        
        # Sentiment analysis mejorada
        positive_words = {
            'amazing', 'awesome', 'excellent', 'fantastic', 'great', 'incredible',
            'love', 'perfect', 'wonderful', 'best', 'outstanding', 'brilliant'
        }
        negative_words = {
            'awful', 'terrible', 'horrible', 'worst', 'disappointing', 'bad',
            'hate', 'disgusting', 'pathetic', 'useless', 'annoying'
        }
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        sentiment = (positive_count - negative_count) / max(len(words), 1) * 5
        sentiment = max(-1, min(1, sentiment))
        
        return ContentMetrics(
            character_count=len(text),
            word_count=len(words),
            sentence_count=len(sentences),
            hashtag_count=len(self.hashtags),
            mention_count=len(self.mentions),
            emoji_count=len(emojis),
            link_count=len(self.media_urls) + (1 if self.link_url else 0),
            readability_score=readability,
            sentiment_score=sentiment
        )


class PostSpecification(BaseModel):
    """Especificación detallada del post."""
    
    topic: str = Field(..., min_length=3, max_length=200)
    post_type: PostType = PostType.TEXT
    tone: ContentTone = ContentTone.CASUAL
    target_audience: TargetAudience = TargetAudience.GENERAL
    keywords: List[str] = Field(default_factory=list, max_items=20)
    max_length: int = Field(280, ge=50, le=2000)
    target_engagement: EngagementTier = EngagementTier.HIGH
    
    # Advanced options
    brand_voice: Optional[str] = Field(None, max_length=500)
    campaign_context: Optional[str] = Field(None, max_length=1000)
    competitor_analysis: bool = Field(False)
    include_trending_topics: bool = Field(True)
    
    @validator('keywords')
    def validate_keywords(cls, v) -> bool:
        return [kw.strip().lower() for kw in v if kw.strip()]


class PostAnalysis(BaseModel):
    """Análisis comprehensivo optimizado para Onyx."""
    
    content_metrics: ContentMetrics
    engagement_prediction: EngagementPrediction
    quality_assessment: QualityAssessment
    
    # Analysis metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    analysis_version: str = "2.1"
    confidence_level: float = Field(ge=0.0, le=1.0, default=0.85)
    processing_time_ms: float = Field(default=0.0)
    
    # Onyx specific
    onyx_model_used: Optional[str] = None
    langchain_chain_id: Optional[str] = None
    
    def get_overall_score(self) -> float:
        """Score general ponderado optimizado."""
        return (
            self.quality_assessment.overall_score * 0.35 +
            self.engagement_prediction.engagement_rate * 0.30 +
            self.engagement_prediction.virality_score * 0.20 +
            self.quality_assessment.audience_match * 0.10 +
            self.confidence_level * 0.05
        )
    
    def get_recommendations(self) -> List[str]:
        """Recomendaciones inteligentes."""
        recommendations = []
        metrics = self.content_metrics
        
        # Length optimization
        if metrics.character_count < 80:
            recommendations.append("🔍 Expand content to 100-300 characters for optimal engagement")
        elif metrics.character_count > 400:
            recommendations.append("✂️ Consider shortening content for better readability")
        
        # Hashtag optimization
        if metrics.hashtag_count == 0:
            recommendations.append("📍 Add 3-5 relevant hashtags to improve discoverability")
        elif metrics.hashtag_count > 7:
            recommendations.append("🎯 Reduce hashtags to 3-5 for optimal performance")
        
        # Engagement boosters
        if metrics.emoji_count == 0:
            recommendations.append("😊 Add emojis to make content more engaging")
        
        if self.engagement_prediction.engagement_rate < 0.6:
            recommendations.append("📢 Include a strong call-to-action")
        
        # Quality improvements
        if metrics.readability_score < 0.7:
            recommendations.append("📖 Simplify language for better readability")
        
        if self.quality_assessment.brand_alignment < 0.7:
            recommendations.append("🎨 Improve brand voice consistency")
        
        # Virality potential
        if self.engagement_prediction.virality_score < 0.4:
            recommendations.append("🚀 Consider adding trending topics or current events")
        
        return recommendations
    
    def get_optimization_priorities(self) -> List[Dict[str, Any]]:
        """Prioridades de optimización."""
        priorities = []
        
        scores = {
            'engagement': self.engagement_prediction.engagement_rate,
            'quality': self.quality_assessment.overall_score,
            'virality': self.engagement_prediction.virality_score,
            'brand_alignment': self.quality_assessment.brand_alignment
        }
        
        for area, score in scores.items():
            if score < 0.7:
                priority = "high" if score < 0.5 else "medium"
                priorities.append({
                    "area": area,
                    "current_score": score,
                    "priority": priority,
                    "potential_improvement": min(0.3, 0.9 - score)
                })
        
        return sorted(priorities, key=lambda x: x['potential_improvement'], reverse=True)


class FacebookPostEntity(BaseModel):
    """Entidad principal refactorizada para Onyx."""
    
    # Core identity
    identifier: PostIdentifier
    specification: PostSpecification
    content: PostContent
    
    # State management
    status: ContentStatus = ContentStatus.DRAFT
    analysis: Optional[PostAnalysis] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    
    # Versioning
    version: int = 1
    parent_id: Optional[str] = None  # For variations
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    
    # Onyx integration
    onyx_workspace_id: Optional[str] = None
    onyx_user_id: Optional[str] = None
    langchain_trace: List[Dict[str, Any]] = Field(default_factory=list)
    generation_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance tracking
    actual_metrics: Optional[Dict[str, int]] = None  # Real performance data
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    # ===== BUSINESS METHODS =====
    
    def update_content(self, new_content: PostContent) -> None:
        """Actualizar contenido invalidando análisis."""
        old_hash = self.identifier.content_hash
        new_hash = hashlib.sha256(new_content.text.encode()).hexdigest()[:16]
        
        # Update identifier if content changed significantly
        if old_hash != new_hash:
            self.identifier = PostIdentifier(
                post_id=self.identifier.post_id,
                content_hash=new_hash,
                created_at=self.identifier.created_at,
                version=self.identifier.version
            )
        
        self.content = new_content
        self.analysis = None  # Invalidate analysis
        self.updated_at = datetime.now()
        self.version += 1
    
    def set_analysis(self, analysis: PostAnalysis) -> None:
        """Establecer análisis con trazabilidad."""
        self.analysis = analysis
        self.updated_at = datetime.now()
        
        # Add to trace
        self.add_langchain_trace("analysis_completed", {
            "overall_score": analysis.get_overall_score(),
            "confidence": analysis.confidence_level,
            "recommendations_count": len(analysis.get_recommendations())
        })
    
    def update_status(self, new_status: ContentStatus, user_id: Optional[str] = None) -> None:
        """Actualizar estado con auditoría."""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        
        if new_status == ContentStatus.PUBLISHED:
            self.published_at = datetime.now()
        
        # Add to trace
        self.add_langchain_trace("status_changed", {
            "from": old_status,
            "to": new_status,
            "user_id": user_id,
            "published_at": self.published_at.isoformat() if self.published_at else None
        })
    
    def add_langchain_trace(self, step: str, data: Dict[str, Any]) -> None:
        """Agregar trazabilidad LangChain."""
        self.langchain_trace.append({
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    
    def set_actual_metrics(self, likes: int, shares: int, comments: int, reach: int) -> None:
        """Establecer métricas reales de performance."""
        self.actual_metrics = {
            "likes": likes,
            "shares": shares,
            "comments": comments,
            "reach": reach,
            "total_interactions": likes + shares + comments,
            "engagement_rate": (likes + shares + comments) / max(reach, 1),
            "recorded_at": datetime.now().isoformat()
        }
        self.updated_at = datetime.now()
    
    # ===== COMPUTED PROPERTIES =====
    
    def is_ready_for_publication(self) -> bool:
        """Verificar si está listo para publicación."""
        return (
            self.status == ContentStatus.APPROVED and
            self.analysis is not None and
            self.analysis.get_overall_score() >= 0.6 and
            len(self.validate_for_publication()) == 0
        )
    
    def get_engagement_score(self) -> float:
        """Score de engagement predicho o real."""
        if self.actual_metrics:
            return self.actual_metrics.get("engagement_rate", 0.0)
        elif self.analysis:
            return self.analysis.engagement_prediction.engagement_rate
        return 0.5
    
    def get_quality_tier(self) -> str:
        """Tier de calidad."""
        if self.analysis:
            return self.analysis.quality_assessment.quality_tier
        return "Unassessed"
    
    def needs_review(self) -> bool:
        """Determinar si necesita revisión."""
        if not self.analysis:
            return True
        
        return (
            self.analysis.get_overall_score() < 0.7 or
            self.analysis.confidence_level < 0.8 or
            len(self.analysis.quality_assessment.improvements) > 3
        )
    
    def get_performance_comparison(self) -> Optional[Dict[str, float]]:
        """Comparar predicción vs performance real."""
        if not self.actual_metrics or not self.analysis:
            return None
        
        predicted = self.analysis.engagement_prediction
        actual = self.actual_metrics
        
        return {
            "likes_accuracy": min(1.0, actual["likes"] / max(predicted.predicted_likes, 1)),
            "shares_accuracy": min(1.0, actual["shares"] / max(predicted.predicted_shares, 1)),
            "comments_accuracy": min(1.0, actual["comments"] / max(predicted.predicted_comments, 1)),
            "reach_accuracy": min(1.0, actual["reach"] / max(predicted.predicted_reach, 1)),
            "overall_accuracy": min(1.0, actual["engagement_rate"] / max(predicted.engagement_rate, 0.01))
        }
    
    def validate_for_publication(self) -> List[str]:
        """Validaciones específicas para publicación."""
        errors = []
        
        # Content validation
        if len(self.content.get_display_text()) > 2000:
            errors.append("Content exceeds Facebook's 2000 character limit")
        
        if len(self.content.text.strip()) < 10:
            errors.append("Content is too short for meaningful engagement")
        
        # Quality thresholds
        if self.analysis:
            if self.analysis.get_overall_score() < 0.5:
                errors.append("Content quality score is below publication threshold")
            
            if self.analysis.confidence_level < 0.6:
                errors.append("Analysis confidence is too low for publication")
        
        # Status validation
        if self.status not in [ContentStatus.APPROVED, ContentStatus.SCHEDULED]:
            errors.append("Content must be approved before publication")
        
        return errors
    
    def get_display_preview(self) -> str:
        """Preview optimizado del post."""
        preview = self.content.text[:97]
        if len(self.content.text) > 97:
            preview += "..."
        
        if self.content.hashtags:
            preview += f" [{len(self.content.hashtags)} hashtags]"
        
        return preview
    
    # ===== COMPARISON & HASHING =====
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, FacebookPostEntity):
            return False
        return self.identifier.post_id == other.identifier.post_id
    
    def __hash__(self) -> int:
        return hash(self.identifier.post_id)
    
    def __str__(self) -> str:
        return f"FacebookPost({self.identifier.post_id[:8]}...)"
    
    def __repr__(self) -> str:
        return (
            f"FacebookPostEntity("
            f"id={self.identifier.post_id}, "
            f"topic={self.specification.topic}, "
            f"status={self.status}, "
            f"quality={self.get_quality_tier()})"
        ) 