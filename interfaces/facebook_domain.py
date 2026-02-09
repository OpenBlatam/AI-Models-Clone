from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import hashlib
from pydantic import BaseModel, Field, validator, root_validator
        import re
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
🎯 Facebook Posts - Refactored Domain Models
============================================

Modelos del dominio refactorizados siguiendo Clean Architecture y patrones de Onyx.
"""



# ===== DOMAIN ENUMS =====

class PostType(str, Enum):
    """Tipos de posts optimizados."""
    TEXT = "text"
    IMAGE = "image" 
    VIDEO = "video"
    LINK = "link"
    CAROUSEL = "carousel"
    POLL = "poll"
    STORY = "story"
    LIVE = "live"


class ContentTone(str, Enum):
    """Tonos de comunicación refinados."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    HUMOROUS = "humorous"
    INSPIRING = "inspiring"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"


class TargetAudience(str, Enum):
    """Audiencias objetivo segmentadas."""
    GENERAL = "general"
    MILLENNIALS = "millennials"
    GEN_Z = "gen_z"
    PROFESSIONALS = "professionals"
    ENTREPRENEURS = "entrepreneurs"
    PARENTS = "parents"
    STUDENTS = "students"
    SENIORS = "seniors"
    TECH_ENTHUSIASTS = "tech_enthusiasts"
    CUSTOM = "custom"


class EngagementTier(str, Enum):
    """Niveles de engagement objetivo."""
    MINIMAL = "minimal"     # 0.0 - 0.3
    LOW = "low"             # 0.3 - 0.5
    MODERATE = "moderate"   # 0.5 - 0.7
    HIGH = "high"           # 0.7 - 0.8
    EXCEPTIONAL = "exceptional"  # 0.8 - 0.9
    VIRAL = "viral"         # 0.9 - 1.0


class ContentStatus(str, Enum):
    """Estados del contenido."""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class AnalysisType(str, Enum):
    """Tipos de análisis disponibles."""
    SENTIMENT = "sentiment"
    ENGAGEMENT = "engagement"
    VIRALITY = "virality"
    READABILITY = "readability"
    BRAND_ALIGNMENT = "brand_alignment"
    COMPETITIVE = "competitive"
    TIMING = "timing"
    COMPREHENSIVE = "comprehensive"


# ===== VALUE OBJECTS =====

@dataclass(frozen=True)
class ContentIdentifier:
    """Identificador inmutable de contenido."""
    content_id: str
    content_hash: str
    created_timestamp: datetime
    version: str = "2.0"
    
    @classmethod
    def generate(cls, content: str) -> 'ContentIdentifier':
        """Generar identificador para contenido."""
        content_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return cls(
            content_id=content_id,
            content_hash=content_hash,
            created_timestamp=datetime.now()
        )


@dataclass(frozen=True)
class ContentSpecification:
    """Especificación de contenido."""
    topic: str
    post_type: PostType
    tone: ContentTone
    target_audience: TargetAudience
    primary_keywords: List[str]
    secondary_keywords: List[str] = field(default_factory=list)
    brand_voice: Optional[str] = None
    campaign_id: Optional[str] = None
    
    def __post_init__(self) -> Any:
        if not self.topic or len(self.topic.strip()) < 3:
            raise ValueError("Topic must be at least 3 characters")


@dataclass(frozen=True)
class GenerationParameters:
    """Parámetros de generación."""
    max_length: int
    target_engagement: EngagementTier
    include_hashtags: bool = True
    include_emojis: bool = True
    include_call_to_action: bool = True
    hashtag_limit: int = 5
    emoji_density: float = 0.1  # Percentage of words that should be emojis
    
    def __post_init__(self) -> Any:
        if not 50 <= self.max_length <= 2000:
            raise ValueError("max_length must be between 50 and 2000")
        if not 0 <= self.emoji_density <= 0.5:
            raise ValueError("emoji_density must be between 0 and 0.5")


@dataclass(frozen=True)
class ContentMetrics:
    """Métricas calculadas del contenido."""
    character_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    hashtag_count: int
    mention_count: int
    emoji_count: int
    link_count: int
    readability_score: float
    sentiment_polarity: float  # -1.0 to 1.0
    
    @property
    def avg_words_per_sentence(self) -> float:
        return self.word_count / max(self.sentence_count, 1)
    
    @property
    def hashtag_density(self) -> float:
        return self.hashtag_count / max(self.word_count, 1)


@dataclass(frozen=True)
class EngagementPrediction:
    """Predicción de engagement."""
    predicted_likes: int
    predicted_shares: int
    predicted_comments: int
    predicted_reach: int
    engagement_rate: float
    virality_probability: float
    optimal_posting_time: datetime
    confidence_score: float  # 0.0 - 1.0
    
    @property
    def total_interactions(self) -> int:
        return self.predicted_likes + self.predicted_shares + self.predicted_comments


@dataclass(frozen=True)
class QualityAssessment:
    """Evaluación de calidad."""
    overall_score: float  # 0.0 - 1.0
    sentiment_score: float
    readability_score: float
    engagement_potential: float
    brand_alignment: float
    content_uniqueness: float
    
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    
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


# ===== DOMAIN ENTITIES =====

class FacebookPostContent(BaseModel):
    """Contenido del post con validaciones avanzadas."""
    
    text: str = Field(..., min_length=10, max_length=2000)
    hashtags: List[str] = Field(default_factory=list, max_items=10)
    mentions: List[str] = Field(default_factory=list, max_items=5)
    media_urls: List[str] = Field(default_factory=list)
    link_url: Optional[str] = None
    call_to_action: Optional[str] = None
    
    @validator('text')
    def validate_text_content(cls, v) -> bool:
        if not v.strip():
            raise ValueError('Text content cannot be empty')
        return v.strip()
    
    @validator('hashtags')
    def validate_hashtags(cls, v) -> bool:
        validated = []
        for tag in v:
            clean_tag = tag.strip().replace('#', '').lower()
            if clean_tag and len(clean_tag) >= 2:
                validated.append(clean_tag)
        return validated[:10]  # Limit to 10
    
    @validator('mentions')
    def validate_mentions(cls, v) -> bool:
        validated = []
        for mention in v:
            clean_mention = mention.strip().replace('@', '')
            if clean_mention:
                validated.append(clean_mention)
        return validated
    
    def get_display_text(self) -> str:
        """Generar texto completo para display."""
        text = self.text
        
        if self.hashtags:
            hashtag_text = " ".join(f"#{tag}" for tag in self.hashtags)
            text += f"\n\n{hashtag_text}"
        
        return text
    
    def calculate_metrics(self) -> ContentMetrics:
        """Calcular métricas del contenido."""
        
        text = self.text
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        
        # Count emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs  
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "]+", flags=re.UNICODE
        )
        emojis = emoji_pattern.findall(text)
        
        # Count URLs
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        urls = url_pattern.findall(text)
        
        # Simple readability (Flesch-like)
        avg_sentence_length = len(words) / max(len([s for s in sentences if s.strip()]), 1)
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        readability = max(0, min(1, 1 - (avg_sentence_length / 20 + avg_word_length / 6)))
        
        # Simple sentiment (basic word matching)
        positive_words = {'good', 'great', 'amazing', 'awesome', 'excellent', 'fantastic', 'wonderful', 'love', 'best'}
        negative_words = {'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'disappointing'}
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        sentiment = (positive_count - negative_count) / max(len(words), 1)
        sentiment = max(-1, min(1, sentiment))
        
        return ContentMetrics(
            character_count=len(text),
            word_count=len(words),
            sentence_count=len([s for s in sentences if s.strip()]),
            paragraph_count=len(paragraphs),
            hashtag_count=len(self.hashtags),
            mention_count=len(self.mentions),
            emoji_count=len(emojis),
            link_count=len(urls) + len(self.media_urls) + (1 if self.link_url else 0),
            readability_score=readability,
            sentiment_polarity=sentiment
        )


class FacebookPostAnalysis(BaseModel):
    """Análisis comprehensivo del post."""
    
    content_metrics: ContentMetrics
    engagement_prediction: EngagementPrediction
    quality_assessment: QualityAssessment
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    analysis_version: str = "2.0"
    confidence_level: float = Field(ge=0.0, le=1.0)
    
    def get_overall_score(self) -> float:
        """Calcular score general ponderado."""
        return (
            self.quality_assessment.overall_score * 0.4 +
            self.engagement_prediction.engagement_rate * 0.3 +
            self.engagement_prediction.virality_probability * 0.2 +
            self.confidence_level * 0.1
        )
    
    def get_recommendations(self) -> List[str]:
        """Generar recomendaciones automáticas."""
        recommendations = []
        
        # Based on metrics
        if self.content_metrics.character_count < 100:
            recommendations.append("Consider adding more content to increase engagement")
        
        if self.content_metrics.hashtag_count == 0:
            recommendations.append("Add relevant hashtags to improve discoverability")
        elif self.content_metrics.hashtag_count > 7:
            recommendations.append("Reduce hashtag count to 3-5 for optimal performance")
        
        if self.content_metrics.emoji_count == 0:
            recommendations.append("Add emojis to make the post more visually appealing")
        
        # Based on engagement prediction
        if self.engagement_prediction.engagement_rate < 0.5:
            recommendations.append("Add a call-to-action to improve engagement")
        
        if self.engagement_prediction.virality_probability < 0.3:
            recommendations.append("Include trending topics or current events")
        
        # Based on quality
        if self.quality_assessment.readability_score < 0.7:
            recommendations.append("Simplify language for better readability")
        
        return recommendations


class FacebookPostEntity(BaseModel):
    """Entidad principal del post refactorizada."""
    
    # Core identity
    identifier: ContentIdentifier
    specification: ContentSpecification
    generation_params: GenerationParameters
    
    # Content
    content: FacebookPostContent
    status: ContentStatus = ContentStatus.DRAFT
    
    # Analysis
    analysis: Optional[FacebookPostAnalysis] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # LangChain integration
    langchain_metadata: Dict[str, Any] = Field(default_factory=dict)
    generation_trace: List[Dict[str, Any]] = Field(default_factory=list)
    
    @dataclass
class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @root_validator
    def validate_consistency(cls, values) -> bool:
        """Validar consistencia entre campos."""
        content = values.get('content')
        params = values.get('generation_params')
        
        if content and params:
            if len(content.get_display_text()) > params.max_length:
                raise ValueError("Content exceeds specified max_length")
        
        return values
    
    # ===== BUSINESS METHODS =====
    
    def update_content(self, new_content: FacebookPostContent) -> None:
        """Actualizar contenido invalidando análisis."""
        self.content = new_content
        self.analysis = None  # Invalidate analysis
        self.updated_at = datetime.now()
        self.version += 1
    
    def set_analysis(self, analysis: FacebookPostAnalysis) -> None:
        """Establecer análisis."""
        self.analysis = analysis
        self.updated_at = datetime.now()
    
    def update_status(self, new_status: ContentStatus) -> None:
        """Actualizar estado con validación."""
        # Status transitions validation
        valid_transitions = {
            ContentStatus.DRAFT: [ContentStatus.UNDER_REVIEW, ContentStatus.ARCHIVED],
            ContentStatus.UNDER_REVIEW: [ContentStatus.APPROVED, ContentStatus.REJECTED, ContentStatus.DRAFT],
            ContentStatus.APPROVED: [ContentStatus.SCHEDULED, ContentStatus.PUBLISHED],
            ContentStatus.SCHEDULED: [ContentStatus.PUBLISHED, ContentStatus.APPROVED],
            ContentStatus.PUBLISHED: [ContentStatus.ARCHIVED],
            ContentStatus.REJECTED: [ContentStatus.DRAFT],
            ContentStatus.ARCHIVED: []
        }
        
        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")
        
        self.status = new_status
        self.updated_at = datetime.now()
    
    def add_generation_trace(self, step: str, data: Dict[str, Any]) -> None:
        """Agregar paso de trazabilidad de generación."""
        trace_entry = {
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.generation_trace.append(trace_entry)
    
    # ===== COMPUTED PROPERTIES =====
    
    def is_ready_for_publication(self) -> bool:
        """Verificar si está listo para publicación."""
        return (
            self.status == ContentStatus.APPROVED and
            self.analysis is not None and
            self.analysis.get_overall_score() >= 0.6 and
            len(self.content.get_display_text()) <= 2000
        )
    
    def get_engagement_score(self) -> float:
        """Obtener score de engagement predicho."""
        if self.analysis:
            return self.analysis.engagement_prediction.engagement_rate
        return 0.5
    
    def get_quality_tier(self) -> str:
        """Obtener tier de calidad."""
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
            len(self.analysis.quality_assessment.weaknesses) > 2
        )


# ===== DOMAIN SERVICES INTERFACES =====

class ContentGenerationService(ABC):
    """Servicio de generación de contenido."""
    
    @abstractmethod
    async def generate_content(
        self, 
        spec: ContentSpecification,
        params: GenerationParameters
    ) -> FacebookPostContent:
        """Generar contenido base."""
        pass
    
    @abstractmethod
    async def generate_variations(
        self,
        base_content: FacebookPostContent,
        variation_count: int = 3
    ) -> List[FacebookPostContent]:
        """Generar variaciones."""
        pass


class ContentAnalysisService(ABC):
    """Servicio de análisis de contenido."""
    
    @abstractmethod
    async def analyze_content(
        self,
        content: FacebookPostContent,
        analysis_types: List[AnalysisType]
    ) -> FacebookPostAnalysis:
        """Analizar contenido."""
        pass


class ContentOptimizationService(ABC):
    """Servicio de optimización."""
    
    @abstractmethod
    async def optimize_for_engagement(
        self,
        content: FacebookPostContent,
        target_engagement: EngagementTier
    ) -> FacebookPostContent:
        """Optimizar para engagement."""
        pass


# ===== REPOSITORY INTERFACE =====

class FacebookPostRepository(ABC):
    """Repositorio refactorizado."""
    
    @abstractmethod
    async def save(self, post: FacebookPostEntity) -> bool:
        pass
    
    @abstractmethod
    async def find_by_id(self, post_id: str) -> Optional[FacebookPostEntity]:
        pass
    
    @abstractmethod
    async def find_by_specification(
        self, 
        spec: ContentSpecification
    ) -> List[FacebookPostEntity]:
        pass
    
    @abstractmethod
    async def find_by_status(
        self, 
        status: ContentStatus
    ) -> List[FacebookPostEntity]:
        pass 