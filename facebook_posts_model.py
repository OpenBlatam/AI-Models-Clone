"""
🎯 Facebook Posts - Onyx Features Model (REFACTORED)
====================================================

Modelo completamente refactorizado siguiendo Clean Architecture y patrones Onyx.
Ubicado en: /features/facebook_posts/
"""

from typing import List, Optional, Dict, Any, Protocol
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid
import hashlib
import re
from pydantic import BaseModel, Field, validator

__version__ = "2.0.0"
__author__ = "Onyx Features Team"

# ===== DOMAIN ENUMS =====

class PostType(str, Enum):
    """Tipos de posts para Facebook."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    LINK = "link"
    CAROUSEL = "carousel"
    POLL = "poll"
    STORY = "story"

class ContentTone(str, Enum):
    """Tonos de comunicación."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    INSPIRING = "inspiring"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    CONVERSATIONAL = "conversational"

class TargetAudience(str, Enum):
    """Audiencias objetivo."""
    GENERAL = "general"
    PROFESSIONALS = "professionals"
    ENTREPRENEURS = "entrepreneurs"
    STUDENTS = "students"
    MILLENNIALS = "millennials"
    PARENTS = "parents"
    TECH_ENTHUSIASTS = "tech_enthusiasts"

class EngagementTier(str, Enum):
    """Niveles de engagement objetivo."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXCEPTIONAL = "exceptional"
    VIRAL = "viral"

class ContentStatus(str, Enum):
    """Estados del contenido en el workflow."""
    DRAFT = "draft"
    ANALYZING = "analyzing"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# ===== VALUE OBJECTS =====

@dataclass(frozen=True)
class ContentIdentifier:
    """Identificador único inmutable."""
    content_id: str
    content_hash: str
    created_at: datetime
    version: str = "2.0"
    
    @classmethod
    def generate(cls, content: str) -> 'ContentIdentifier':
        """Generar identificador único."""
        return cls(
            content_id=str(uuid.uuid4()),
            content_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
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
    max_length: int = 280
    target_engagement: EngagementTier = EngagementTier.HIGH
    brand_voice: Optional[str] = None
    campaign_context: Optional[str] = None
    
    def __post_init__(self):
        if not self.topic or len(self.topic.strip()) < 3:
            raise ValueError("Topic must be at least 3 characters")

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
    keyword_density: float
    
    @property
    def engagement_potential(self) -> float:
        """Calcular potencial de engagement."""
        length_score = 1.0 if 100 <= self.character_count <= 300 else 0.7
        hashtag_score = min(1.0, self.hashtag_count / 5)
        emoji_score = 1.0 if self.emoji_count > 0 else 0.8
        
        return (length_score + hashtag_score + emoji_score + 
                self.readability_score + abs(self.sentiment_score)) / 5

@dataclass(frozen=True)
class EngagementPrediction:
    """Predicción de engagement."""
    predicted_likes: int
    predicted_shares: int
    predicted_comments: int
    predicted_reach: int
    predicted_saves: int
    engagement_rate: float
    virality_score: float
    optimal_posting_time: Optional[datetime]
    confidence: float
    
    @property
    def total_interactions(self) -> int:
        return (self.predicted_likes + self.predicted_shares + 
                self.predicted_comments + self.predicted_saves)

# ===== ENTITIES =====

class PostContent(BaseModel):
    """Contenido del post con validaciones avanzadas."""
    
    text: str = Field(..., min_length=10, max_length=2000)
    hashtags: List[str] = Field(default_factory=list, max_items=10)
    mentions: List[str] = Field(default_factory=list, max_items=5)
    media_urls: List[str] = Field(default_factory=list)
    link_url: Optional[str] = None
    call_to_action: Optional[str] = None
    
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
                if re.match(r'^[a-zA-Z0-9_]+$', clean_tag):
                    validated.append(clean_tag)
        return validated[:10]
    
    @validator('mentions')
    def validate_mentions(cls, v):
        validated = []
        for mention in v:
            clean_mention = mention.strip().replace('@', '')
            if clean_mention and re.match(r'^[a-zA-Z0-9._]+$', clean_mention):
                validated.append(clean_mention)
        return validated
    
    def get_display_text(self) -> str:
        """Generar texto completo para display."""
        text = self.text
        
        if self.call_to_action:
            text += f"\n\n{self.call_to_action}"
        
        if self.hashtags:
            hashtag_text = " ".join(f"#{tag}" for tag in self.hashtags)
            text += f"\n\n{hashtag_text}"
        
        return text
    
    def calculate_metrics(self, keywords: List[str] = None) -> ContentMetrics:
        """Calcular métricas avanzadas del contenido."""
        text = self.text
        words = text.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Advanced emoji detection
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs  
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "]+", flags=re.UNICODE
        )
        emojis = emoji_pattern.findall(text)
        
        # Enhanced readability
        avg_sentence_length = len(words) / max(len(sentences), 1)
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        readability = max(0, min(1, 1.2 - (0.05 * avg_sentence_length + 0.1 * avg_word_length)))
        
        # Advanced sentiment analysis
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
        sentiment = (positive_count - negative_count) / max(len(words), 1) * 2
        sentiment = max(-1, min(1, sentiment))
        
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
            hashtag_count=len(self.hashtags),
            mention_count=len(self.mentions),
            emoji_count=len(emojis),
            link_count=len(self.media_urls) + (1 if self.link_url else 0),
            readability_score=readability,
            sentiment_score=sentiment,
            keyword_density=keyword_density
        )

class PostAnalysis(BaseModel):
    """Análisis comprehensivo del post."""
    
    content_metrics: ContentMetrics
    engagement_prediction: EngagementPrediction
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    analysis_version: str = "2.0"
    confidence_level: float = Field(ge=0.0, le=1.0, default=0.85)
    processing_time_ms: float = Field(default=0.0)
    
    # Onyx integration
    onyx_model_used: Optional[str] = None
    langchain_chain_id: Optional[str] = None
    
    def get_overall_score(self) -> float:
        """Score general ponderado optimizado."""
        weights = {
            'engagement_potential': 0.30,
            'engagement_rate': 0.25,
            'virality': 0.20,
            'readability': 0.15,
            'confidence': 0.10
        }
        
        return (
            self.content_metrics.engagement_potential * weights['engagement_potential'] +
            self.engagement_prediction.engagement_rate * weights['engagement_rate'] +
            self.engagement_prediction.virality_score * weights['virality'] +
            self.content_metrics.readability_score * weights['readability'] +
            self.confidence_level * weights['confidence']
        )
    
    def get_quality_tier(self) -> str:
        """Determinar tier de calidad."""
        score = self.get_overall_score()
        if score >= 0.9:
            return "Exceptional"
        elif score >= 0.8:
            return "Excellent"
        elif score >= 0.7:
            return "Good"
        elif score >= 0.6:
            return "Fair"
        else:
            return "Poor"
    
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
        
        if self.engagement_prediction.engagement_rate < 0.6:
            recommendations.append({
                "category": "Engagement",
                "priority": "high",
                "action": "Include a strong call-to-action",
                "impact": "Higher interaction rate",
                "effort": "medium",
                "icon": "📢"
            })
        
        if metrics.readability_score < 0.7:
            recommendations.append({
                "category": "Readability",
                "priority": "medium",
                "action": "Simplify language and shorten sentences",
                "impact": "Better comprehension",
                "effort": "medium",
                "icon": "📖"
            })
        
        return recommendations

class FacebookPost(BaseModel):
    """Entidad principal del post (Aggregate Root)."""
    
    # Core identity and data
    identifier: ContentIdentifier
    specification: PostSpecification
    content: PostContent
    
    # State management
    status: ContentStatus = ContentStatus.DRAFT
    analysis: Optional[PostAnalysis] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    
    # Versioning and relationships
    version: int = 1
    parent_id: Optional[str] = None  # For variations/versions
    child_ids: List[str] = Field(default_factory=list)
    
    # Metadata and tags
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    
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
        json_encoders = {datetime: lambda v: v.isoformat()}
    
    # ===== BUSINESS METHODS =====
    
    def update_content(self, new_content: PostContent) -> None:
        """Actualizar contenido invalidando análisis."""
        self.content = new_content
        self.analysis = None  # Invalidate analysis
        self.status = ContentStatus.DRAFT  # Reset status
        self.updated_at = datetime.now()
        self.version += 1
    
    def set_analysis(self, analysis: PostAnalysis) -> None:
        """Establecer análisis con trazabilidad."""
        self.analysis = analysis
        self.updated_at = datetime.now()
        
        self.add_langchain_trace("analysis_completed", {
            "overall_score": analysis.get_overall_score(),
            "quality_tier": analysis.get_quality_tier(),
            "confidence": analysis.confidence_level,
            "processing_time_ms": analysis.processing_time_ms
        })
        
        # Auto-update status based on analysis
        if analysis.get_overall_score() >= 0.8:
            self.status = ContentStatus.APPROVED
        elif analysis.get_overall_score() >= 0.6:
            self.status = ContentStatus.UNDER_REVIEW
    
    def update_status(self, new_status: ContentStatus, user_id: Optional[str] = None) -> None:
        """Actualizar estado con validación."""
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
        self.actual_metrics = {
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
        accuracy = {}
        
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
            return self.analysis.get_quality_tier()
        return "Unassessed"
    
    def needs_review(self) -> bool:
        """Determinar si necesita revisión manual."""
        if not self.analysis:
            return True
        
        return (
            self.analysis.get_overall_score() < 0.7 or
            self.analysis.confidence_level < 0.8 or
            len(self.analysis.get_actionable_recommendations()) > 3 or
            self.status == ContentStatus.UNDER_REVIEW
        )
    
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
            
            if self.analysis.confidence_level < 0.6:
                errors.append("Analysis confidence is too low for safe publication")
        else:
            errors.append("Content must be analyzed before publication")
        
        # Status validation
        if self.status not in [ContentStatus.APPROVED, ContentStatus.SCHEDULED]:
            errors.append("Content must be approved or scheduled for publication")
        
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
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Resumen de performance completo."""
        summary = {
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
                "virality_score": self.analysis.engagement_prediction.virality_score,
                "recommendations_count": len(self.analysis.get_actionable_recommendations())
            })
        
        if self.actual_metrics:
            summary.update({
                "actual_performance": self.actual_metrics,
                "prediction_accuracy": self.actual_metrics.get("prediction_accuracy", {})
            })
        
        return summary

# ===== SERVICES PROTOCOLS =====

class ContentGenerationService(Protocol):
    """Servicio de generación de contenido."""
    
    async def generate_content(
        self, 
        spec: PostSpecification
    ) -> PostContent:
        """Generar contenido base."""
        ...
    
    async def generate_variations(
        self,
        base_content: PostContent,
        variation_count: int = 3
    ) -> List[PostContent]:
        """Generar variaciones A/B."""
        ...

class ContentAnalysisService(Protocol):
    """Servicio de análisis de contenido."""
    
    async def analyze_content(
        self,
        post: FacebookPost
    ) -> PostAnalysis:
        """Analizar contenido comprehensivamente."""
        ...

class ContentOptimizationService(Protocol):
    """Servicio de optimización."""
    
    async def optimize_for_engagement(
        self,
        content: PostContent,
        target_engagement: EngagementTier
    ) -> PostContent:
        """Optimizar para engagement."""
        ...

class FacebookPostRepository(Protocol):
    """Repositorio de posts."""
    
    async def save(self, post: FacebookPost) -> bool:
        """Guardar post."""
        ...
    
    async def find_by_id(self, post_id: str) -> Optional[FacebookPost]:
        """Buscar por ID."""
        ...
    
    async def find_by_status(
        self, 
        status: ContentStatus,
        limit: int = 100
    ) -> List[FacebookPost]:
        """Buscar por estado."""
        ...

# ===== FACTORY =====

class FacebookPostFactory:
    """Factory para crear posts optimizados."""
    
    @staticmethod
    def create_from_specification(
        specification: PostSpecification,
        content_text: str,
        hashtags: Optional[List[str]] = None,
        **kwargs
    ) -> FacebookPost:
        """Crear post completo desde especificación."""
        
        # Generate identifier
        identifier = ContentIdentifier.generate(content_text)
        
        # Create content
        content = PostContent(
            text=content_text,
            hashtags=hashtags or [],
            mentions=kwargs.get('mentions', []),
            media_urls=kwargs.get('media_urls', []),
            link_url=kwargs.get('link_url'),
            call_to_action=kwargs.get('call_to_action')
        )
        
        return FacebookPost(
            identifier=identifier,
            specification=specification,
            content=content,
            onyx_workspace_id=kwargs.get('workspace_id'),
            onyx_user_id=kwargs.get('user_id'),
            onyx_project_id=kwargs.get('project_id')
        )
    
    @staticmethod
    def create_high_performance_post(
        topic: str,
        audience: TargetAudience = TargetAudience.GENERAL,
        engagement_tier: EngagementTier = EngagementTier.HIGH,
        **kwargs
    ) -> FacebookPost:
        """Crear post con template de alta performance."""
        
        # High-performance configuration
        spec = PostSpecification(
            topic=topic,
            post_type=PostType.TEXT,
            tone=ContentTone.INSPIRING,
            target_audience=audience,
            keywords=[topic.lower()],
            target_engagement=engagement_tier
        )
        
        # Template-based content
        content_text = f"✨ Discover amazing {topic} insights! Transform your approach today. What's your experience?"
        
        return FacebookPostFactory.create_from_specification(
            specification=spec,
            content_text=content_text,
            hashtags=[topic.lower().replace(' ', ''), 'success', 'growth'],
            call_to_action="Share your thoughts below! 👇",
            **kwargs
        )

# ===== DEMO FUNCTIONS =====

def create_demo_post() -> FacebookPost:
    """Crear post de demostración."""
    spec = PostSpecification(
        topic="AI Marketing Revolution",
        post_type=PostType.TEXT,
        tone=ContentTone.INSPIRING,
        target_audience=TargetAudience.ENTREPRENEURS,
        keywords=["AI", "marketing", "automation", "business"]
    )
    
    return FacebookPostFactory.create_from_specification(
        specification=spec,
        content_text="🚀 AI is revolutionizing marketing! Discover automation strategies that boost ROI by 300%. Ready to transform your business?",
        hashtags=["AI", "marketing", "automation", "business", "growth"],
        call_to_action="Comment 'AI' if you want to learn more!"
    )

def create_demo_analysis() -> PostAnalysis:
    """Crear análisis de demostración."""
    metrics = ContentMetrics(
        character_count=135,
        word_count=22,
        sentence_count=3,
        hashtag_count=5,
        mention_count=0,
        emoji_count=1,
        link_count=0,
        readability_score=0.85,
        sentiment_score=0.8,
        keyword_density=0.18
    )
    
    prediction = EngagementPrediction(
        predicted_likes=280,
        predicted_shares=42,
        predicted_comments=55,
        predicted_reach=3500,
        predicted_saves=18,
        engagement_rate=0.82,
        virality_score=0.48,
        optimal_posting_time=datetime.now(),
        confidence=0.89
    )
    
    return PostAnalysis(
        content_metrics=metrics,
        engagement_prediction=prediction,
        confidence_level=0.89,
        processing_time_ms=195.5
    )

def demo_complete_workflow():
    """Demo del workflow completo refactorizado."""
    print("🎯 Facebook Posts - Onyx Features Model (REFACTORED)")
    print("=" * 60)
    
    # Create demo post
    post = create_demo_post()
    print(f"✅ Post created: {post.identifier.content_id[:8]}...")
    print(f"📝 Preview: {post.get_display_preview()}")
    print(f"🎯 Target: {post.specification.target_audience.value}")
    print(f"📊 Status: {post.status.value}")
    
    # Add analysis
    analysis = create_demo_analysis()
    post.set_analysis(analysis)
    
    print(f"\n📈 Analysis Results:")
    print(f"   Overall Score: {analysis.get_overall_score():.2f}")
    print(f"   Quality Tier: {post.get_quality_tier()}")
    print(f"   Engagement Rate: {post.get_engagement_score():.2f}")
    print(f"   Ready for Publication: {post.is_ready_for_publication()}")
    
    # Show recommendations
    recommendations = analysis.get_actionable_recommendations()
    if recommendations:
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec['icon']} {rec['action']} (Priority: {rec['priority']})")
    
    # Performance summary
    summary = post.get_performance_summary()
    print(f"\n📊 Performance Summary:")
    print(f"   Quality Tier: {summary['quality_tier']}")
    print(f"   Overall Score: {summary.get('overall_score', 'N/A')}")
    print(f"   Engagement Prediction: {summary.get('engagement_prediction', 'N/A')}")
    
    print(f"\n🔍 Technical Details:")
    print(f"   Trace Events: {len(post.langchain_trace)}")
    print(f"   Version: {post.version}")
    print(f"   Status: {post.status.value}")
    
    print(f"\n📈 Refactored Model Stats:")
    print(f"   - Location: /features/facebook_posts/")
    print(f"   - Enums: 5 domain types")
    print(f"   - Value Objects: 4 immutable")
    print(f"   - Entities: 3 with business logic")
    print(f"   - Services: 4 protocols")
    print(f"   - Factory: 1 with templates")
    print(f"   - Total Lines: ~600")
    
    print("\n✅ REFACTOR COMPLETADO EN DIRECTORIO CORRECTO!")
    print("🚀 Listo para integración Onyx en /features/facebook_posts/")
    
    return post

# Execute demo if run directly
if __name__ == "__main__":
    demo_complete_workflow() 