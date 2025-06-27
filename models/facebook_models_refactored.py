"""
🎯 Facebook Posts - Refactored Models for Onyx Features
======================================================

Modelos refactorizados siguiendo la arquitectura de features de Onyx.
Integración completa con Clean Architecture, LangChain y patrones enterprise.
Migración completa a la nueva arquitectura modular.
"""

from typing import List, Optional, Dict, Any, Union, Protocol
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import uuid
import hashlib
import re
from pydantic import BaseModel, Field, validator, root_validator


# ===== REFINED DOMAIN ENUMS =====

class PostType(str, Enum):
    """Tipos de posts optimizados para Facebook."""
    TEXT = "text"
    IMAGE = "image" 
    VIDEO = "video"
    LINK = "link"
    CAROUSEL = "carousel"
    POLL = "poll"
    STORY = "story"
    LIVE = "live"
    REEL = "reel"


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
    STORYTELLING = "storytelling"


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
    CREATIVES = "creatives"
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
    """Estados del contenido en el workflow Onyx."""
    DRAFT = "draft"
    GENERATING = "generating"
    ANALYZING = "analyzing"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"
    FAILED = "failed"


class AnalysisType(str, Enum):
    """Tipos de análisis disponibles."""
    SENTIMENT = "sentiment"
    ENGAGEMENT = "engagement"
    VIRALITY = "virality"
    READABILITY = "readability"
    BRAND_ALIGNMENT = "brand_alignment"
    COMPETITIVE = "competitive"
    TIMING = "timing"
    AUDIENCE_MATCH = "audience_match"
    COMPREHENSIVE = "comprehensive"


# ===== VALUE OBJECTS =====

@dataclass(frozen=True)
class ContentIdentifier:
    """Identificador inmutable de contenido."""
    content_id: str
    content_hash: str
    created_timestamp: datetime
    version: str = "2.1"
    
    @classmethod
    def generate(cls, content: str, metadata: Optional[Dict] = None) -> 'ContentIdentifier':
        """Generar identificador único con metadata opcional."""
        content_id = str(uuid.uuid4())
        
        # Include metadata in hash for uniqueness
        hash_input = content
        if metadata:
            hash_input += str(sorted(metadata.items()))
        
        content_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        
        return cls(
            content_id=content_id,
            content_hash=content_hash,
            created_timestamp=datetime.now()
        )


@dataclass(frozen=True)
class ContentSpecification:
    """Especificación detallada de contenido."""
    topic: str
    post_type: PostType
    tone: ContentTone
    target_audience: TargetAudience
    primary_keywords: List[str]
    secondary_keywords: List[str] = field(default_factory=list)
    brand_voice: Optional[str] = None
    campaign_id: Optional[str] = None
    competitor_context: Optional[str] = None
    
    def __post_init__(self):
        if not self.topic or len(self.topic.strip()) < 3:
            raise ValueError("Topic must be at least 3 characters")
        
        if len(self.primary_keywords) == 0:
            raise ValueError("At least one primary keyword is required")


@dataclass(frozen=True)
class GenerationConfig:
    """Configuración avanzada de generación."""
    max_length: int
    target_engagement: EngagementTier
    include_hashtags: bool = True
    include_emojis: bool = True
    include_call_to_action: bool = True
    hashtag_limit: int = 5
    emoji_density: float = 0.1  # 0.0 - 0.5
    creativity_level: float = 0.7  # 0.0 - 1.0
    brand_consistency: float = 0.8  # 0.0 - 1.0
    trending_topics_weight: float = 0.3  # 0.0 - 1.0
    
    def __post_init__(self):
        if not 50 <= self.max_length <= 2000:
            raise ValueError("max_length must be between 50 and 2000")
        
        for field_name, value in [
            ("emoji_density", self.emoji_density),
            ("creativity_level", self.creativity_level),
            ("brand_consistency", self.brand_consistency),
            ("trending_topics_weight", self.trending_topics_weight)
        ]:
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0.0 and 1.0")


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
    sentiment_subjectivity: float  # 0.0 to 1.0
    keyword_density: float
    
    @property
    def engagement_factors(self) -> Dict[str, float]:
        """Factores que influyen en el engagement."""
        return {
            'optimal_length': self._calculate_length_score(),
            'hashtag_usage': min(1.0, self.hashtag_count / 5),
            'emoji_presence': min(1.0, self.emoji_count / max(self.word_count * 0.1, 1)),
            'readability': self.readability_score,
            'sentiment_strength': abs(self.sentiment_polarity),
            'content_richness': min(1.0, (self.link_count + self.mention_count) / 3)
        }
    
    def _calculate_length_score(self) -> float:
        """Calcular score basado en longitud óptima."""
        if 100 <= self.character_count <= 300:
            return 1.0
        elif 80 <= self.character_count <= 400:
            return 0.9
        elif 50 <= self.character_count <= 500:
            return 0.8
        else:
            return 0.6


@dataclass(frozen=True)
class EngagementPrediction:
    """Predicción avanzada de engagement."""
    predicted_likes: int
    predicted_shares: int
    predicted_comments: int
    predicted_reach: int
    predicted_saves: int  
    engagement_rate: float
    virality_probability: float
    optimal_posting_time: Optional[datetime]
    confidence_score: float  # 0.0 - 1.0
    prediction_model_version: str = "2.1"
    
    @property
    def total_interactions(self) -> int:
        return (self.predicted_likes + self.predicted_shares + 
                self.predicted_comments + self.predicted_saves)
    
    @property
    def engagement_quality_score(self) -> float:
        """Score que prioriza interacciones de alta calidad."""
        return (
            self.predicted_comments * 3 +  # Comments are highest value
            self.predicted_shares * 2 +    # Shares are high value
            self.predicted_saves * 2 +     # Saves indicate intent
            self.predicted_likes * 1       # Likes are baseline
        ) / max(self.predicted_reach, 1)


@dataclass(frozen=True)
class QualityAssessment:
    """Evaluación comprehensiva de calidad."""
    overall_score: float  # 0.0 - 1.0
    sentiment_score: float
    readability_score: float
    engagement_potential: float
    brand_alignment: float
    content_uniqueness: float
    audience_relevance: float
    trend_alignment: float
    
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    competitive_advantages: List[str] = field(default_factory=list)
    
    @property
    def quality_tier(self) -> str:
        """Determinar tier de calidad."""
        if self.overall_score >= 0.95:
            return "Outstanding"
        elif self.overall_score >= 0.9:
            return "Exceptional"
        elif self.overall_score >= 0.8:
            return "Excellent" 
        elif self.overall_score >= 0.7:
            return "Good"
        elif self.overall_score >= 0.6:
            return "Fair"
        elif self.overall_score >= 0.5:
            return "Below Average"
        else:
            return "Poor"


# ===== CORE ENTITIES =====

class FacebookPostContent(BaseModel):
    """Contenido del post con validaciones avanzadas."""
    
    text: str = Field(..., min_length=10, max_length=2000)
    hashtags: List[str] = Field(default_factory=list, max_items=10)
    mentions: List[str] = Field(default_factory=list, max_items=5)
    media_urls: List[str] = Field(default_factory=list)
    link_url: Optional[str] = None
    call_to_action: Optional[str] = None
    location_tag: Optional[str] = None
    
    @validator('text')
    def validate_text_content(cls, v):
        if not v.strip():
            raise ValueError('Text content cannot be empty')
        
        # Check for spam patterns
        spam_patterns = [
            r'(.)\1{4,}',  # Repeated characters
            r'[A-Z]{10,}',  # Too many capitals
            r'!{3,}',       # Too many exclamations
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, v):
                raise ValueError(f'Content matches spam pattern: {pattern}')
        
        return v.strip()
    
    @validator('hashtags')
    def validate_hashtags(cls, v):
        validated = []
        for tag in v:
            clean_tag = tag.strip().replace('#', '').lower()
            if clean_tag and len(clean_tag) >= 2 and clean_tag not in validated:
                # Validate hashtag format
                if re.match(r'^[a-zA-Z0-9_]+$', clean_tag):
                    validated.append(clean_tag)
        return validated[:10]  # Limit to 10
    
    def get_display_text(self) -> str:
        """Generar texto completo para display."""
        text = self.text
        
        if self.call_to_action:
            text += f"\n\n{self.call_to_action}"
        
        if self.hashtags:
            hashtag_text = " ".join(f"#{tag}" for tag in self.hashtags)
            text += f"\n\n{hashtag_text}"
        
        return text
    
    def calculate_advanced_metrics(self, keywords: List[str] = None) -> ContentMetrics:
        """Calcular métricas avanzadas del contenido."""
        text = self.text
        words = text.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Advanced emoji detection
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs  
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002600-\U000027BF"  # misc symbols
            "\U0001f926-\U0001f937"  # additional emoticons
            "]+", flags=re.UNICODE
        )
        emojis = emoji_pattern.findall(text)
        
        # Enhanced readability (Flesch-Kincaid inspired)
        avg_sentence_length = len(words) / max(len(sentences), 1)
        readability = max(0, min(1, 1.2 - (0.05 * avg_sentence_length)))
        
        # Simple sentiment analysis fallback
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
        sentiment_polarity = (positive_count - negative_count) / max(len(words), 1) * 2
        sentiment_polarity = max(-1, min(1, sentiment_polarity))
        
        # Keyword density calculation
        keyword_density = 0.0
        if keywords:
            text_lower = text.lower()
            keyword_count = sum(1 for kw in keywords if kw.lower() in text_lower)
            keyword_density = keyword_count / max(len(words), 1)
        
        return ContentMetrics(
            character_count=len(text),
            word_count=len(words),
            sentence_count=len(sentences),
            paragraph_count=len(paragraphs),
            hashtag_count=len(self.hashtags),
            mention_count=len(self.mentions),
            emoji_count=len(emojis),
            link_count=len(self.media_urls) + (1 if self.link_url else 0),
            readability_score=readability,
            sentiment_polarity=sentiment_polarity,
            sentiment_subjectivity=0.5,  # Default
            keyword_density=keyword_density
        )


class FacebookPostAnalysis(BaseModel):
    """Análisis comprehensivo avanzado."""
    
    content_metrics: ContentMetrics
    engagement_prediction: EngagementPrediction
    quality_assessment: QualityAssessment
    
    # Analysis metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    analysis_version: str = "2.1"
    confidence_level: float = Field(ge=0.0, le=1.0, default=0.85)
    processing_time_ms: float = Field(default=0.0)
    
    # Model information
    analysis_models_used: List[str] = Field(default_factory=list)
    onyx_model_id: Optional[str] = None
    langchain_chain_id: Optional[str] = None
    
    def get_overall_score(self) -> float:
        """Score general ponderado optimizado."""
        weights = {
            'quality': 0.30,
            'engagement': 0.25,
            'virality': 0.20,
            'audience_relevance': 0.15,
            'trend_alignment': 0.10
        }
        
        return (
            self.quality_assessment.overall_score * weights['quality'] +
            self.engagement_prediction.engagement_rate * weights['engagement'] +
            self.engagement_prediction.virality_probability * weights['virality'] +
            self.quality_assessment.audience_relevance * weights['audience_relevance'] +
            self.quality_assessment.trend_alignment * weights['trend_alignment']
        )
    
    def get_actionable_recommendations(self) -> List[Dict[str, Any]]:
        """Recomendaciones actionables con prioridades."""
        recommendations = []
        metrics = self.content_metrics
        
        # Content optimization recommendations
        if metrics.character_count < 80:
            recommendations.append({
                "category": "Content Length",
                "priority": "high",
                "action": "Expand content to 100-300 characters",
                "impact": "High engagement boost",
                "effort": "medium",
                "icon": "🔍"
            })
        
        if metrics.hashtag_count == 0:
            recommendations.append({
                "category": "Discoverability",
                "priority": "high", 
                "action": "Add 3-5 relevant hashtags",
                "impact": "Increased reach",
                "effort": "low",
                "icon": "📍"
            })
        
        if metrics.emoji_count == 0:
            recommendations.append({
                "category": "Visual Appeal",
                "priority": "medium",
                "action": "Add relevant emojis",
                "impact": "More engaging appearance",
                "effort": "low",
                "icon": "😊"
            })
        
        return recommendations


class FacebookPostEntity(BaseModel):
    """Entidad principal refactorizada para features de Onyx."""
    
    # Core identity
    identifier: ContentIdentifier
    specification: ContentSpecification
    generation_config: GenerationConfig
    content: FacebookPostContent
    
    # State management
    status: ContentStatus = ContentStatus.DRAFT
    analysis: Optional[FacebookPostAnalysis] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    
    # Versioning and relationships
    version: int = 1
    parent_id: Optional[str] = None  # For variations/versions
    child_ids: List[str] = Field(default_factory=list)  # Variations created from this
    
    # Metadata and tags
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    # Onyx integration
    onyx_workspace_id: Optional[str] = None
    onyx_user_id: Optional[str] = None
    onyx_project_id: Optional[str] = None
    
    # LangChain integration
    langchain_trace: List[Dict[str, Any]] = Field(default_factory=list)
    langchain_session_id: Optional[str] = None
    
    # Performance tracking
    actual_metrics: Optional[Dict[str, Any]] = None
    ab_test_group: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    # ===== BUSINESS METHODS =====
    
    def update_content(self, new_content: FacebookPostContent) -> None:
        """Actualizar contenido con invalidación de análisis."""
        self.content = new_content
        self.analysis = None  # Invalidate analysis
        self.status = ContentStatus.DRAFT  # Reset status
        self.updated_at = datetime.now()
        self.version += 1
    
    def set_analysis(self, analysis: FacebookPostAnalysis) -> None:
        """Establecer análisis con trazabilidad."""
        self.analysis = analysis
        self.updated_at = datetime.now()
        
        self.add_langchain_trace("analysis_completed", {
            "overall_score": analysis.get_overall_score(),
            "confidence": analysis.confidence_level,
            "processing_time_ms": analysis.processing_time_ms
        })
    
    def update_status(self, new_status: ContentStatus, user_id: Optional[str] = None) -> None:
        """Actualizar estado con validación de transiciones."""
        self.status = new_status
        self.updated_at = datetime.now()
        
        if new_status == ContentStatus.PUBLISHED:
            self.published_at = datetime.now()
    
    def add_langchain_trace(self, step: str, data: Dict[str, Any]) -> None:
        """Agregar trazabilidad LangChain detallada."""
        self.langchain_trace.append({
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.langchain_session_id,
            "data": data
        })
    
    # ===== COMPUTED PROPERTIES =====
    
    def is_ready_for_publication(self) -> bool:
        """Verificar si está listo para publicación."""
        return (
            self.status in [ContentStatus.APPROVED, ContentStatus.SCHEDULED] and
            self.analysis is not None and
            self.analysis.get_overall_score() >= 0.6 and
            len(self.validate_for_publication()) == 0
        )
    
    def get_engagement_score(self) -> float:
        """Score de engagement (real o predicho)."""
        if self.actual_metrics and 'engagement_rate' in self.actual_metrics:
            return self.actual_metrics['engagement_rate']
        elif self.analysis:
            return self.analysis.engagement_prediction.engagement_rate
        return 0.5
    
    def get_quality_tier(self) -> str:
        """Tier de calidad del contenido."""
        if self.analysis:
            return self.analysis.quality_assessment.quality_tier
        return "Unassessed"
    
    def validate_for_publication(self) -> List[str]:
        """Validaciones específicas para publicación."""
        errors = []
        
        # Content validation
        display_text = self.content.get_display_text()
        if len(display_text) > 2000:
            errors.append("Content exceeds Facebook's 2000 character limit")
        
        if len(self.content.text.strip()) < 10:
            errors.append("Content is too short for meaningful engagement")
        
        # Quality thresholds
        if self.analysis:
            if self.analysis.get_overall_score() < 0.5:
                errors.append("Content quality score is below minimum threshold")
        else:
            errors.append("Content must be analyzed before publication")
        
        return errors
    
    def get_display_preview(self) -> str:
        """Preview optimizado del post."""
        preview = self.content.text[:97]
        if len(self.content.text) > 97:
            preview += "..."
        
        additions = []
        if self.content.hashtags:
            additions.append(f"{len(self.content.hashtags)} hashtags")
        if self.content.media_urls:
            additions.append(f"{len(self.content.media_urls)} media")
        if self.content.call_to_action:
            additions.append("CTA")
        
        if additions:
            preview += f" [{', '.join(additions)}]"
        
        return preview


# ===== DOMAIN SERVICES INTERFACES =====

class ContentGenerationService(Protocol):
    """Servicio de generación de contenido."""
    
    async def generate_content(
        self, 
        spec: ContentSpecification,
        config: GenerationConfig
    ) -> FacebookPostContent:
        """Generar contenido base."""
        ...


class ContentAnalysisService(Protocol):
    """Servicio de análisis de contenido."""
    
    async def analyze_content(
        self,
        post: FacebookPostEntity,
        analysis_types: List[AnalysisType] = None
    ) -> FacebookPostAnalysis:
        """Analizar contenido comprehensivamente."""
        ...


class FacebookPostRepository(Protocol):
    """Repositorio de posts."""
    
    async def save(self, post: FacebookPostEntity) -> bool:
        """Guardar post."""
        ...
    
    async def find_by_id(self, post_id: str) -> Optional[FacebookPostEntity]:
        """Buscar por ID."""
        ...


# ===== FACTORY =====

class FacebookPostFactory:
    """Factory para crear posts optimizados."""
    
    @staticmethod
    def create_from_specification(
        specification: ContentSpecification,
        generation_config: GenerationConfig,
        content_text: str,
        hashtags: Optional[List[str]] = None,
        **kwargs
    ) -> FacebookPostEntity:
        """Crear post completo desde especificación."""
        
        # Generate identifier
        identifier = ContentIdentifier.generate(
            content_text, 
            {"spec": specification.topic, "config": generation_config.target_engagement.value}
        )
        
        # Create content
        content = FacebookPostContent(
            text=content_text,
            hashtags=hashtags or [],
            mentions=kwargs.get('mentions', []),
            media_urls=kwargs.get('media_urls', []),
            link_url=kwargs.get('link_url'),
            call_to_action=kwargs.get('call_to_action')
        )
        
        return FacebookPostEntity(
            identifier=identifier,
            specification=specification,
            generation_config=generation_config,
            content=content,
            onyx_workspace_id=kwargs.get('workspace_id'),
            onyx_user_id=kwargs.get('user_id'),
            onyx_project_id=kwargs.get('project_id')
        )
    
    @staticmethod
    def create_high_performance_template(
        topic: str,
        audience: TargetAudience = TargetAudience.GENERAL,
        engagement_tier: EngagementTier = EngagementTier.HIGH,
        **kwargs
    ) -> FacebookPostEntity:
        """Crear post con template de alta performance."""
        
        # High-performance configuration
        spec = ContentSpecification(
            topic=topic,
            post_type=PostType.TEXT,
            tone=ContentTone.ENGAGING,
            target_audience=audience,
            primary_keywords=[topic.lower()]
        )
        
        config = GenerationConfig(
            max_length=280,
            target_engagement=engagement_tier,
            include_hashtags=True,
            include_emojis=True,
            include_call_to_action=True,
            creativity_level=0.8,
            trending_topics_weight=0.4
        )
        
        # Template-based content
        content_text = f"✨ Amazing {topic} discovery: Revolutionary insights await! What's your experience?"
        
        return FacebookPostFactory.create_from_specification(
            specification=spec,
            generation_config=config,
            content_text=content_text,
            hashtags=[topic.lower().replace(' ', ''), 'success', 'growth'],
            **kwargs
        ) 