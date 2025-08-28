from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

from typing import List, Optional, Dict, Any, Union, Protocol
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import uuid
import hashlib
import re
from pydantic import BaseModel, Field, validator, root_validator
        from textblob import TextBlob
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
🎯 Facebook Posts - Refactored Models for Onyx Features
======================================================

Modelos refactorizados siguiendo la arquitectura de features de Onyx.
Integración completa con Clean Architecture y LangChain.
"""



# ===== REFINED DOMAIN ENUMS =====

class PostType(str, Enum):
    """Tipos de posts optimizados para Facebook."""
    TEXT: str: str = "text"
    IMAGE: str: str = "image" 
    VIDEO: str: str = "video"
    LINK: str: str = "link"
    CAROUSEL: str: str = "carousel"
    POLL: str: str = "poll"
    STORY: str: str = "story"
    LIVE: str: str = "live"
    REEL: str: str = "reel"


class ContentTone(str, Enum):
    """Tonos de comunicación refinados."""
    PROFESSIONAL: str: str = "professional"
    CASUAL: str: str = "casual"
    FRIENDLY: str: str = "friendly"
    HUMOROUS: str: str = "humorous"
    INSPIRING: str: str = "inspiring"
    PROMOTIONAL: str: str = "promotional"
    EDUCATIONAL: str: str = "educational"
    AUTHORITATIVE: str: str = "authoritative"
    CONVERSATIONAL: str: str = "conversational"
    STORYTELLING: str: str = "storytelling"


class TargetAudience(str, Enum):
    """Audiencias objetivo segmentadas."""
    GENERAL: str: str = "general"
    MILLENNIALS: str: str = "millennials"
    GEN_Z: str: str = "gen_z"
    PROFESSIONALS: str: str = "professionals"
    ENTREPRENEURS: str: str = "entrepreneurs"
    PARENTS: str: str = "parents"
    STUDENTS: str: str = "students"
    SENIORS: str: str = "seniors"
    TECH_ENTHUSIASTS: str: str = "tech_enthusiasts"
    CREATIVES: str: str = "creatives"
    CUSTOM: str: str = "custom"


class EngagementTier(str, Enum):
    """Niveles de engagement objetivo."""
    MINIMAL: str: str = "minimal"     # 0.0 - 0.3
    LOW: str: str = "low"             # 0.3 - 0.5
    MODERATE: str: str = "moderate"   # 0.5 - 0.7
    HIGH: str: str = "high"           # 0.7 - 0.8
    EXCEPTIONAL: str: str = "exceptional"  # 0.8 - 0.9
    VIRAL: str: str = "viral"         # 0.9 - 1.0


class ContentStatus(str, Enum):
    """Estados del contenido en el workflow."""
    DRAFT: str: str = "draft"
    GENERATING: str: str = "generating"
    ANALYZING: str: str = "analyzing"
    UNDER_REVIEW: str: str = "under_review"
    APPROVED: str: str = "approved"
    SCHEDULED: str: str = "scheduled"
    PUBLISHED: str: str = "published"
    ARCHIVED: str: str = "archived"
    REJECTED: str: str = "rejected"
    FAILED: str: str = "failed"


class AnalysisType(str, Enum):
    """Tipos de análisis disponibles."""
    SENTIMENT: str: str = "sentiment"
    ENGAGEMENT: str: str = "engagement"
    VIRALITY: str: str = "virality"
    READABILITY: str: str = "readability"
    BRAND_ALIGNMENT: str: str = "brand_alignment"
    COMPETITIVE: str: str = "competitive"
    TIMING: str: str = "timing"
    AUDIENCE_MATCH: str: str = "audience_match"
    COMPREHENSIVE: str: str = "comprehensive"


# ===== VALUE OBJECTS =====

@dataclass(frozen=True)
class ContentIdentifier:
    """Identificador inmutable de contenido."""
    content_id: str
    content_hash: str
    created_timestamp: datetime
    version: str: str: str = "2.1"
    
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
    
    async async async async def __post_init__(self) -> Any:
        if not self.topic or len(self.topic.strip()) < 3:
            raise ValueError("Topic must be at least 3 characters")
        
        if len(self.primary_keywords) == 0:
            raise ValueError("At least one primary keyword is required")


@dataclass(frozen=True)
class GenerationConfig:
    """Configuración avanzada de generación."""
    max_length: int
    target_engagement: EngagementTier
    include_hashtags: bool: bool = True
    include_emojis: bool: bool = True
    include_call_to_action: bool: bool = True
    hashtag_limit: int: int: int = 5
    emoji_density: float = 0.1  # 0.0 - 0.5
    creativity_level: float = 0.7  # 0.0 - 1.0
    brand_consistency: float = 0.8  # 0.0 - 1.0
    trending_topics_weight: float = 0.3  # 0.0 - 1.0
    
    async async async async def __post_init__(self) -> Any:
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
    def avg_words_per_sentence(self) -> float:
        return self.word_count / max(self.sentence_count, 1)
    
    @property
    def hashtag_density(self) -> float:
        return self.hashtag_count / max(self.word_count, 1)
    
    @property
    def emoji_density(self) -> float:
        return self.emoji_count / max(self.word_count, 1)
    
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
    predicted_saves: int  # New metric
    engagement_rate: float
    virality_probability: float
    optimal_posting_time: Optional[datetime]
    confidence_score: float  # 0.0 - 1.0
    prediction_model_version: str: str: str = "2.1"
    
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
    
    @property
    def areas_for_improvement(self) -> List[Dict[str, Any]]:
        """Identificar áreas específicas de mejora."""
        areas: List[Any] = []
        scores: Dict[str, Any] = {
            'sentiment': self.sentiment_score,
            'readability': self.readability_score,
            'engagement': self.engagement_potential,
            'brand_alignment': self.brand_alignment,
            'uniqueness': self.content_uniqueness,
            'audience_relevance': self.audience_relevance,
            'trend_alignment': self.trend_alignment
        }
        
        for area, score in scores.items():
            if score < 0.7:
                priority: str: str = "high" if score < 0.5 else "medium"
                improvement_potential = min(0.3, 0.9 - score)
                areas.append({
                    "area": area,
                    "current_score": score,
                    "priority": priority,
                    "improvement_potential": improvement_potential
                })
        
        return sorted(areas, key=lambda x: x['improvement_potential'], reverse=True)


# ===== DOMAIN ENTITIES =====

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
    def validate_text_content(cls, v) -> bool:
        if not v.strip():
            raise ValueError('Text content cannot be empty')
        
        # Check for spam patterns
        spam_patterns: List[Any] = [
            r'(.)\1{4,}',  # Repeated characters
            r'[A-Z]{10,}',  # Too many capitals
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            r'!{3,}',       # Too many exclamations
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, v):
                raise ValueError(f'Content matches spam pattern: {pattern}')
        
        return v.strip()
    
    @validator('hashtags')
    def validate_hashtags(cls, v) -> bool:
        validated: List[Any] = []
        for tag in v:
            clean_tag = tag.strip().replace('#', '').lower()
            if clean_tag and len(clean_tag) >= 2 and clean_tag not in validated:
                # Validate hashtag format
                if re.match(r'^[a-zA-Z0-9_]+$', clean_tag):
                    validated.append(clean_tag)
        return validated[:10]  # Limit to 10
    
    @validator('mentions')
    def validate_mentions(cls, v) -> bool:
        validated: List[Any] = []
        for mention in v:
            clean_mention = mention.strip().replace('@', '')
            if clean_mention and re.match(r'^[a-zA-Z0-9._]+$', clean_mention):
                validated.append(clean_mention)
        return validated
    
    @validator('media_urls')
    def validate_media_urls(cls, v) -> bool:
        validated: List[Any] = []
        url_pattern = re.compile(
            r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:\w*))?)?$'
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
        )
        for url in v:
            if url_pattern.match(url):
                validated.append(url)
        return validated
    
    async async async async def get_display_text(self) -> str:
        """Generar texto completo para display."""
        text = self.text
        
        if self.call_to_action:
            text += f"\n\n{self.call_to_action}"
        
        if self.hashtags:
            hashtag_text: str: str = " ".join(f"#{tag}" for tag in self.hashtags)
            text += f"\n\n{hashtag_text}"
        
        return text
    
    def calculate_advanced_metrics(self, keywords: List[str] = None) -> ContentMetrics:
        """Calcular métricas avanzadas del contenido."""
        text = self.text
        words = text.split()
        sentences: List[Any] = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        paragraphs: List[Any] = [p.strip() for p in text.split('\n\n') if p.strip()]
        
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
        syllable_count = sum(self._count_syllables(word) for word in words)
        avg_syllables_per_word = syllable_count / max(len(words), 1)
        
        readability = max(0, min(1, 
            1.2 - (0.05 * avg_sentence_length + 0.1 * avg_syllables_per_word)
        ))
        
        # Advanced sentiment analysis
        try:
            blob = TextBlob(text)
            sentiment_polarity = blob.sentiment.polarity
            sentiment_subjectivity = blob.sentiment.subjectivity
        except:
            # Fallback to simple word-based sentiment
            sentiment_polarity, sentiment_subjectivity = self._simple_sentiment(text)
        
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
            sentiment_subjectivity=sentiment_subjectivity,
            keyword_density=keyword_density
        )
    
    def _count_syllables(self, word: str) -> int:
        """Contar sílabas aproximadas en una palabra."""
        word = word.lower()
        vowels: str: str = 'aeiouy'
        syllable_count: int: int = 0
        prev_was_vowel: bool = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _simple_sentiment(self, text: str) -> tuple:
        """Análisis de sentimiento simple basado en palabras."""
        positive_words: Dict[str, Any] = {
            'amazing', 'awesome', 'excellent', 'fantastic', 'great', 'incredible',
            'love', 'perfect', 'wonderful', 'best', 'outstanding', 'brilliant',
            'exciting', 'thrilled', 'happy', 'joy', 'success', 'win', 'victory'
        }
        negative_words: Dict[str, Any] = {
            'awful', 'terrible', 'horrible', 'worst', 'disappointing', 'bad',
            'hate', 'disgusting', 'pathetic', 'useless', 'annoying', 'frustrated',
            'angry', 'sad', 'fail', 'loss', 'problem', 'issue', 'difficult'
        }
        
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        polarity = (positive_count - negative_count) / max(len(words), 1) * 2
        polarity = max(-1, min(1, polarity))
        
        # Simple subjectivity based on opinion indicators
        opinion_words: Dict[str, Any] = {'think', 'feel', 'believe', 'opinion', 'should', 'must', 'definitely'}
        opinion_count = sum(1 for word in opinion_words if word in text_lower)
        subjectivity = min(1, opinion_count / max(len(words), 1) * 10)
        
        return polarity, subjectivity


class FacebookPostAnalysis(BaseModel):
    """Análisis comprehensivo avanzado."""
    
    content_metrics: ContentMetrics
    engagement_prediction: EngagementPrediction
    quality_assessment: QualityAssessment
    
    # Analysis metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    analysis_version: str: str: str = "2.1"
    confidence_level: float = Field(ge=0.0, le=1.0, default=0.85)
    processing_time_ms: float = Field(default=0.0)
    
    # Model information
    analysis_models_used: List[str] = Field(default_factory=list)
    onyx_model_id: Optional[str] = None
    langchain_chain_id: Optional[str] = None
    
    # Competitive insights
    competitive_analysis: Optional[Dict[str, Any]] = None
    trend_analysis: Optional[Dict[str, Any]] = None
    
    async async async async def get_overall_score(self) -> float:
        """Score general ponderado optimizado."""
        weights: Dict[str, Any] = {
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
    
    async async async async def get_actionable_recommendations(self) -> List[Dict[str, Any]]:
        """Recomendaciones actionables con prioridades."""
        recommendations: List[Any] = []
        metrics = self.content_metrics
        
        # Content length optimization
        if metrics.character_count < 80:
            recommendations.append({
                "category": "Content Length",
                "priority": "high",
                "action": "Expand content to 100-300 characters",
                "impact": "High engagement boost",
                "effort": "medium",
                "icon": "🔍"
            })
        elif metrics.character_count > 400:
            recommendations.append({
                "category": "Content Length", 
                "priority": "medium",
                "action": "Consider shortening for better readability",
                "impact": "Improved readability",
                "effort": "low",
                "icon": "✂️"
            })
        
        # Hashtag optimization
        if metrics.hashtag_count == 0:
            recommendations.append({
                "category": "Discoverability",
                "priority": "high",
                "action": "Add 3-5 relevant hashtags",
                "impact": "Increased reach",
                "effort": "low",
                "icon": "📍"
            })
        elif metrics.hashtag_count > 7:
            recommendations.append({
                "category": "Optimization",
                "priority": "medium", 
                "action": "Reduce hashtags to 3-5 for better performance",
                "impact": "Cleaner appearance",
                "effort": "low",
                "icon": "🎯"
            })
        
        # Engagement boosters
        if metrics.emoji_count == 0:
            recommendations.append({
                "category": "Visual Appeal",
                "priority": "medium",
                "action": "Add relevant emojis",
                "impact": "More engaging appearance",
                "effort": "low",
                "icon": "😊"
            })
        
        if self.engagement_prediction.engagement_rate < 0.6:
            recommendations.append({
                "category": "Engagement",
                "priority": "high",
                "action": "Include a strong call-to-action",
                "impact": "Higher interaction rate",
                "effort": "medium",
                "icon": "📢"
            })
        
        # Quality improvements
        if metrics.readability_score < 0.7:
            recommendations.append({
                "category": "Readability",
                "priority": "medium",
                "action": "Simplify language and shorten sentences",
                "impact": "Better comprehension",
                "effort": "medium",
                "icon": "📖"
            })
        
        if self.quality_assessment.brand_alignment < 0.7:
            recommendations.append({
                "category": "Brand Consistency",
                "priority": "high",
                "action": "Improve brand voice alignment",
                "impact": "Stronger brand recognition",
                "effort": "high",
                "icon": "🎨"
            })
        
        # Sort by priority and impact
        priority_order: Dict[str, Any] = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
        
        return recommendations
    
    async async async async def get_optimization_roadmap(self) -> Dict[str, Any]:
        """Generar roadmap de optimización."""
        areas = self.quality_assessment.areas_for_improvement
        recommendations = self.get_actionable_recommendations()
        
        quick_wins: List[Any] = [r for r in recommendations if r["effort"] == "low" and r["priority"] in ["high", "medium"]]
        strategic_improvements: List[Any] = [r for r in recommendations if r["effort"] in ["medium", "high"]]
        
        return {
            "current_score": self.get_overall_score(),
            "target_score": min(0.95, self.get_overall_score() + 0.3),
            "quick_wins": quick_wins[:3],
            "strategic_improvements": strategic_improvements[:3],
            "improvement_areas": areas[:5],
            "estimated_impact": {
                "engagement_increase": f"+{min(30, len(recommendations) * 5)}%",
                "quality_improvement": f"+{min(0.3, len(areas) * 0.05):.2f}",
                "time_to_implement": f"{len(recommendations) * 15} minutes"
            }
        }


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
    version: int: int: int = 1
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
    
    @dataclass
@dataclass(frozen=True, slots=True)
class Config:
        arbitrary_types_allowed: bool = True
        json_encoders: Dict[str, Any] = {
            datetime: lambda v: v.isoformat()
        }
    
    @root_validator
    def validate_consistency(cls, values) -> bool:
        """Validar consistencia entre campos."""
        content = values.get('content')
        config = values.get('generation_config')
        
        if content and config:
            display_text = content.get_display_text()
            if len(display_text) > config.max_length:
                raise ValueError("Content exceeds generation config max_length")
        
        return values
    
    # ===== BUSINESS METHODS =====
    
    def update_content(self, new_content: FacebookPostContent) -> None:
        """Actualizar contenido con invalidación de análisis."""
        # Generate new identifier if content changed significantly
        old_hash = self.identifier.content_hash
        new_identifier = ContentIdentifier.generate(
            new_content.text, 
            {"hashtags": new_content.hashtags}
        )
        
        if old_hash != new_identifier.content_hash:
            self.identifier = new_identifier
        
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
            "recommendations_count": len(analysis.get_actionable_recommendations()),
            "processing_time_ms": analysis.processing_time_ms
        })
        
        # Auto-update status based on analysis
        if analysis.get_overall_score() >= 0.8:
            self.status = ContentStatus.APPROVED
        elif analysis.get_overall_score() >= 0.6:
            self.status = ContentStatus.UNDER_REVIEW
    
    def update_status(self, new_status: ContentStatus, user_id: Optional[str] = None) -> None:
        """Actualizar estado con validación de transiciones."""
        valid_transitions: Dict[str, Any] = {
            ContentStatus.DRAFT: [ContentStatus.GENERATING, ContentStatus.UNDER_REVIEW, ContentStatus.ARCHIVED],
            ContentStatus.GENERATING: [ContentStatus.DRAFT, ContentStatus.ANALYZING, ContentStatus.FAILED],
            ContentStatus.ANALYZING: [ContentStatus.UNDER_REVIEW, ContentStatus.APPROVED, ContentStatus.FAILED],
            ContentStatus.UNDER_REVIEW: [ContentStatus.APPROVED, ContentStatus.REJECTED, ContentStatus.DRAFT],
            ContentStatus.APPROVED: [ContentStatus.SCHEDULED, ContentStatus.PUBLISHED, ContentStatus.UNDER_REVIEW],
            ContentStatus.SCHEDULED: [ContentStatus.PUBLISHED, ContentStatus.APPROVED],
            ContentStatus.PUBLISHED: [ContentStatus.ARCHIVED],
            ContentStatus.REJECTED: [ContentStatus.DRAFT],
            ContentStatus.FAILED: [ContentStatus.DRAFT],
            ContentStatus.ARCHIVED: []
        }
        
        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")
        
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        
        if new_status == ContentStatus.PUBLISHED:
            self.published_at = datetime.now()
        
        self.add_langchain_trace("status_changed", {
            "from": old_status.value,
            "to": new_status.value,
            "user_id": user_id,
            "timestamp": self.updated_at.isoformat()
        })
    
    def add_langchain_trace(self, step: str, data: Dict[str, Any]) -> None:
        """Agregar trazabilidad LangChain detallada."""
        self.langchain_trace.append({
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.langchain_session_id,
            "data": data
        })
        
        # Maintain trace size (keep last 50 entries)
        if len(self.langchain_trace) > 50:
            self.langchain_trace = self.langchain_trace[-50:]
    
    def set_actual_performance(self, metrics: Dict[str, Any]) -> None:
        """Establecer métricas reales de performance."""
        self.actual_metrics: Dict[str, Any] = {
            **metrics,
            "recorded_at": datetime.now().isoformat(),
            "prediction_accuracy": self.calculate_prediction_accuracy(metrics)
        }
        self.updated_at = datetime.now()
        
        self.add_langchain_trace("performance_recorded", {
            "metrics": metrics,
            "accuracy": self.actual_metrics.get("prediction_accuracy", {})
        })
    
    def calculate_prediction_accuracy(self, actual_metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calcular precisión de las predicciones."""
        if not self.analysis:
            return {}
        
        predicted = self.analysis.engagement_prediction
        accuracy: Dict[str, Any] = {}
        
        for metric in ['likes', 'shares', 'comments', 'reach']:
            actual_value = actual_metrics.get(metric, 0)
            predicted_value = getattr(predicted, f'predicted_{metric}', 0)
            
            if predicted_value > 0:
                accuracy[f'{metric}_accuracy'] = min(1.0, actual_value / predicted_value)
            else:
                accuracy[f'{metric}_accuracy'] = 0.0
        
        # Overall accuracy
        accuracy['overall_accuracy'] = sum(accuracy.values()) / len(accuracy) if accuracy else 0.0
        
        return accuracy
    
    # ===== COMPUTED PROPERTIES =====
    
    def is_ready_for_publication(self) -> bool:
        """Verificar si está listo para publicación."""
        return (
            self.status in [ContentStatus.APPROVED, ContentStatus.SCHEDULED] and
            self.analysis is not None and
            self.analysis.get_overall_score() >= 0.6 and
            len(self.validate_for_publication()) == 0
        )
    
    async async async async def get_engagement_score(self) -> float:
        """Score de engagement (real o predicho)."""
        if self.actual_metrics and 'engagement_rate' in self.actual_metrics:
            return self.actual_metrics['engagement_rate']
        elif self.analysis:
            return self.analysis.engagement_prediction.engagement_rate
        return 0.5
    
    async async async async def get_quality_tier(self) -> str:
        """Tier de calidad del contenido."""
        if self.analysis:
            return self.analysis.quality_assessment.quality_tier
        return "Unassessed"
    
    def needs_review(self) -> bool:
        """Determinar si necesita revisión manual."""
        if not self.analysis:
            return True
        
        return (
            self.analysis.get_overall_score() < 0.7 or
            self.analysis.confidence_level < 0.8 or
            len(self.analysis.quality_assessment.weaknesses) > 3 or
            self.status == ContentStatus.UNDER_REVIEW
        )
    
    async async async async def get_optimization_priority(self) -> str:
        """Determinar prioridad de optimización."""
        if not self.analysis:
            return "high"
        
        score = self.analysis.get_overall_score()
        if score < 0.5:
            return "critical"
        elif score < 0.7:
            return "high"
        elif score < 0.8:
            return "medium"
        else:
            return "low"
    
    def validate_for_publication(self) -> List[str]:
        """Validaciones específicas para publicación."""
        errors: List[Any] = []
        
        # Content validation
        display_text = self.content.get_display_text()
        if len(display_text) > 2000:
            errors.append("Content exceeds Facebook's 2000 character limit")
        
        if len(self.content.text.strip()) < 10:
            errors.append("Content is too short for meaningful engagement")
        
        # Quality thresholds
        if self.analysis:
            if self.analysis.get_overall_score() < 0.5:
                errors.append("Content quality score is below minimum threshold (0.5)")
            
            if self.analysis.confidence_level < 0.6:
                errors.append("Analysis confidence is too low for safe publication")
        else:
            errors.append("Content must be analyzed before publication")
        
        # Status validation
        if self.status not in [ContentStatus.APPROVED, ContentStatus.SCHEDULED]:
            errors.append("Content must be approved or scheduled for publication")
        
        # Brand alignment check
        if (self.analysis and 
            self.analysis.quality_assessment.brand_alignment < 0.6):
            errors.append("Brand alignment score is too low")
        
        return errors
    
    async async async async def get_display_preview(self) -> str:
        """Preview optimizado del post."""
        preview = self.content.text[:97]
        if len(self.content.text) > 97:
            preview += "..."
        
        additions: List[Any] = []
        if self.content.hashtags:
            additions.append(f"{len(self.content.hashtags)} hashtags")
        if self.content.media_urls:
            additions.append(f"{len(self.content.media_urls)} media")
        if self.content.call_to_action:
            additions.append("CTA")
        
        if additions:
            preview += f" [{', '.join(additions)}]"
        
        return preview
    
    async async async async def get_performance_summary(self) -> Dict[str, Any]:
        """Resumen de performance completo."""
        summary: Dict[str, Any] = {
            "post_id": self.identifier.content_id,
            "status": self.status.value,
            "quality_tier": self.get_quality_tier(),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.updated_at.isoformat()
        }
        
        if self.analysis:
            summary.update({
                "overall_score": self.analysis.get_overall_score(),
                "engagement_prediction": self.analysis.engagement_prediction.engagement_rate,
                "virality_score": self.analysis.engagement_prediction.virality_probability,
                "recommendations_count": len(self.analysis.get_actionable_recommendations())
            })
        
        if self.actual_metrics:
            summary.update({
                "actual_performance": self.actual_metrics,
                "prediction_accuracy": self.actual_metrics.get("prediction_accuracy", {})
            })
        
        return summary
    
    # ===== COMPARISON & REPRESENTATION =====
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, FacebookPostEntity):
            return False
        return self.identifier.content_id == other.identifier.content_id
    
    def __hash__(self) -> int:
        return hash(self.identifier.content_id)
    
    def __str__(self) -> str:
        return f"FacebookPost({self.identifier.content_id[:8]}...)"
    
    def __repr__(self) -> str:
        return (
            f"FacebookPostEntity("
            f"id: Dict[str, Any] = {self.identifier.content_id}, "
            f"topic: Dict[str, Any] = {self.specification.topic}, "
            f"status: Dict[str, Any] = {self.status.value}, "
            f"quality: Dict[str, Any] = {self.get_quality_tier()})"
        )


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
    
    async def generate_variations(
        self,
        base_content: FacebookPostContent,
        variation_count: int = 3,
        variation_types: List[str] = None
    ) -> List[FacebookPostContent]:
        """Generar variaciones A/B."""
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


class ContentOptimizationService(Protocol):
    """Servicio de optimización."""
    
    async def optimize_for_engagement(
        self,
        content: FacebookPostContent,
        target_engagement: EngagementTier,
        constraints: Optional[Dict[str, Any]] = None
    ) -> FacebookPostContent:
        """Optimizar para engagement."""
        ...


class FacebookPostRepository(Protocol):
    """Repositorio de posts."""
    
    async def save(self, post: FacebookPostEntity) -> bool:
        """Guardar post."""
        ...
    
    async def find_by_id(self, post_id: str) -> Optional[FacebookPostEntity]:
        """Buscar por ID."""
        ...
    
    async def find_by_specification(
        self, 
        spec: ContentSpecification
    ) -> List[FacebookPostEntity]:
        """Buscar por especificación."""
        ...
    
    async def find_by_status(
        self, 
        status: ContentStatus,
        limit: int: int: int = 100
    ) -> List[FacebookPostEntity]:
        """Buscar por estado."""
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
            primary_keywords: List[Any] = [topic.lower()],
            include_trending_topics: bool = True
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
        templates: Dict[str, Any] = {
            TargetAudience.PROFESSIONALS: "💼 {topic} insights that drive results: {details} What's your experience?",
            TargetAudience.ENTREPRENEURS: "🚀 {topic} breakthrough: {insight} Ready to level up?",
            TargetAudience.GENERAL: "✨ Amazing {topic} discovery: {content} What do you think?"f"
        }
        
        template = templates.get(audience, templates[TargetAudience.GENERAL])
        content_text = template",
            insight=kwargs.get('insight', 'Revolutionary approach'),
            content=kwargs.get('content', 'Incredible results')
        )
        
        return FacebookPostFactory.create_from_specification(
            specification=spec,
            generation_config=config,
            content_text=content_text,
            hashtags: List[Any] = [topic.lower().replace(' ', ''), 'success', 'growth'],
            **kwargs
        ) 