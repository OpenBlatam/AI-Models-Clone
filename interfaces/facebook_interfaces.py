"""
🎯 Facebook Posts - Domain Interfaces
=====================================

Interfaces y contratos del dominio para Facebook posts siguiendo arquitectura Onyx.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Protocol
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

# ===== ENUMS & VALUE OBJECTS =====

class PostType(str, Enum):
    """Tipos de posts de Facebook."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    LINK = "link"
    CAROUSEL = "carousel"
    POLL = "poll"
    EVENT = "event"
    STORY = "story"


class ContentTone(str, Enum):
    """Tonos de comunicación."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    HUMOROUS = "humorous"
    INSPIRING = "inspiring"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    CONTROVERSIAL = "controversial"


class TargetAudience(str, Enum):
    """Audiencias objetivo."""
    GENERAL = "general"
    YOUNG_ADULTS = "young_adults"
    PROFESSIONALS = "professionals"
    PARENTS = "parents"
    ENTREPRENEURS = "entrepreneurs"
    STUDENTS = "students"
    SENIORS = "seniors"
    CUSTOM = "custom"


class EngagementTier(str, Enum):
    """Niveles de engagement objetivo."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VIRAL = "viral"


class AnalysisStatus(str, Enum):
    """Estados de análisis."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentQuality(str, Enum):
    """Niveles de calidad de contenido."""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"
    OUTSTANDING = "outstanding"


# ===== VALUE OBJECTS =====

@dataclass(frozen=True)
class PostIdentifier:
    """Identificador único de post."""
    post_id: str
    content_hash: str
    created_at: datetime
    version: str = "1.0"


@dataclass(frozen=True)
class ContentMetrics:
    """Métricas de contenido."""
    character_count: int
    word_count: int
    hashtag_count: int
    mention_count: int
    emoji_count: int
    link_count: int


@dataclass(frozen=True)
class EngagementMetrics:
    """Métricas de engagement."""
    predicted_likes: int
    predicted_shares: int
    predicted_comments: int
    predicted_reach: int
    engagement_rate: float
    virality_score: float


@dataclass(frozen=True)
class QualityScores:
    """Scores de calidad."""
    sentiment_score: float  # 0.0 - 1.0
    readability_score: float  # 0.0 - 1.0
    brand_alignment_score: float  # 0.0 - 1.0
    engagement_prediction: float  # 0.0 - 1.0
    overall_quality: ContentQuality


@dataclass(frozen=True)
class GenerationConfig:
    """Configuración de generación."""
    max_length: int
    include_hashtags: bool
    include_emojis: bool
    include_call_to_action: bool
    target_engagement: EngagementTier
    brand_voice: Optional[str] = None
    campaign_context: Optional[str] = None


@dataclass(frozen=True)
class PostContent:
    """Contenido del post."""
    text: str
    hashtags: List[str]
    mentions: List[str]
    media_urls: List[str]
    link_url: Optional[str] = None


@dataclass(frozen=True)
class PostSpecification:
    """Especificación para generación de post."""
    topic: str
    post_type: PostType
    tone: ContentTone
    target_audience: TargetAudience
    keywords: List[str]
    config: GenerationConfig


@dataclass(frozen=True)
class AnalysisResult:
    """Resultado de análisis."""
    identifier: PostIdentifier
    content_metrics: ContentMetrics
    engagement_metrics: EngagementMetrics
    quality_scores: QualityScores
    recommendations: List[str]
    insights: List[str]
    status: AnalysisStatus
    processing_time_ms: float


# ===== DOMAIN ENTITIES =====

class FacebookPost:
    """Entidad principal - Facebook Post."""
    
    def __init__(
        self,
        identifier: PostIdentifier,
        specification: PostSpecification,
        content: PostContent,
        analysis: Optional[AnalysisResult] = None
    ):
        self._identifier = identifier
        self._specification = specification
        self._content = content
        self._analysis = analysis
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    @property
    def identifier(self) -> PostIdentifier:
        return self._identifier
    
    @property
    def specification(self) -> PostSpecification:
        return self._specification
    
    @property
    def content(self) -> PostContent:
        return self._content
    
    @property
    def analysis(self) -> Optional[AnalysisResult]:
        return self._analysis
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def update_content(self, new_content: PostContent) -> None:
        """Actualizar contenido del post."""
        self._content = new_content
        self._updated_at = datetime.now()
    
    def set_analysis(self, analysis: AnalysisResult) -> None:
        """Establecer resultado de análisis."""
        self._analysis = analysis
        self._updated_at = datetime.now()
    
    def get_display_text(self) -> str:
        """Obtener texto completo para mostrar."""
        text = self._content.text
        if self._content.hashtags:
            text += "\n\n" + " ".join(f"#{tag}" for tag in self._content.hashtags)
        return text
    
    def is_within_facebook_limits(self) -> bool:
        """Verificar si cumple límites de Facebook."""
        return len(self.get_display_text()) <= 2000
    
    def get_engagement_prediction(self) -> float:
        """Obtener predicción de engagement."""
        if self._analysis:
            return self._analysis.quality_scores.engagement_prediction
        return 0.5


# ===== REPOSITORIES =====

class FacebookPostRepository(ABC):
    """Repositorio para posts de Facebook."""
    
    @abstractmethod
    async def save(self, post: FacebookPost) -> bool:
        """Guardar post."""
        pass
    
    @abstractmethod
    async def find_by_id(self, post_id: str) -> Optional[FacebookPost]:
        """Buscar post por ID."""
        pass
    
    @abstractmethod
    async def find_by_hash(self, content_hash: str) -> Optional[FacebookPost]:
        """Buscar post por hash de contenido."""
        pass
    
    @abstractmethod
    async def find_all(self, limit: int = 100) -> List[FacebookPost]:
        """Obtener todos los posts."""
        pass
    
    @abstractmethod
    async def delete(self, post_id: str) -> bool:
        """Eliminar post."""
        pass


# ===== SERVICES =====

class ContentGenerator(ABC):
    """Servicio para generar contenido."""
    
    @abstractmethod
    async def generate_post(self, spec: PostSpecification) -> PostContent:
        """Generar contenido de post."""
        pass
    
    @abstractmethod
    async def generate_variations(
        self, 
        spec: PostSpecification, 
        count: int = 3
    ) -> List[PostContent]:
        """Generar variaciones del post."""
        pass


class ContentAnalyzer(ABC):
    """Servicio para analizar contenido."""
    
    @abstractmethod
    async def analyze_post(self, post: FacebookPost) -> AnalysisResult:
        """Analizar post completo."""
        pass
    
    @abstractmethod
    async def analyze_content(self, content: PostContent) -> QualityScores:
        """Analizar solo contenido."""
        pass
    
    @abstractmethod
    async def predict_engagement(self, content: PostContent) -> EngagementMetrics:
        """Predecir métricas de engagement."""
        pass


class ContentOptimizer(ABC):
    """Servicio para optimizar contenido."""
    
    @abstractmethod
    async def optimize_for_engagement(self, content: PostContent) -> PostContent:
        """Optimizar para engagement."""
        pass
    
    @abstractmethod
    async def suggest_improvements(self, post: FacebookPost) -> List[str]:
        """Sugerir mejoras."""
        pass
    
    @abstractmethod
    async def optimize_timing(self, spec: PostSpecification) -> datetime:
        """Optimizar tiempo de publicación."""
        pass


class HashtagResearcher(ABC):
    """Servicio para investigación de hashtags."""
    
    @abstractmethod
    async def research_trending_hashtags(self, topic: str) -> List[str]:
        """Investigar hashtags trending."""
        pass
    
    @abstractmethod
    async def suggest_hashtags(self, content: str) -> List[str]:
        """Sugerir hashtags para contenido."""
        pass
    
    @abstractmethod
    async def validate_hashtags(self, hashtags: List[str]) -> List[str]:
        """Validar y filtrar hashtags."""
        pass


# ===== EXTERNAL INTEGRATIONS =====

class LangChainProvider(Protocol):
    """Proveedor de LangChain."""
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generar texto usando LangChain."""
        ...
    
    async def analyze_sentiment(self, text: str) -> float:
        """Analizar sentimiento."""
        ...
    
    async def extract_keywords(self, text: str) -> List[str]:
        """Extraer keywords."""
        ...


class OnyxLLMProvider(Protocol):
    """Proveedor LLM de Onyx."""
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generar contenido."""
        ...
    
    async def analyze(self, content: str, **kwargs) -> Dict[str, Any]:
        """Analizar contenido."""
        ...


class CacheProvider(Protocol):
    """Proveedor de cache."""
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtener del cache."""
        ...
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Guardar en cache."""
        ...
    
    async def delete(self, key: str) -> bool:
        """Eliminar del cache."""
        ...


# ===== USE CASES =====

class GeneratePostUseCase(ABC):
    """Caso de uso: Generar post de Facebook."""
    
    @abstractmethod
    async def execute(self, spec: PostSpecification) -> FacebookPost:
        """Ejecutar generación de post."""
        pass


class AnalyzePostUseCase(ABC):
    """Caso de uso: Analizar post de Facebook."""
    
    @abstractmethod
    async def execute(self, post: FacebookPost) -> AnalysisResult:
        """Ejecutar análisis de post."""
        pass


class OptimizePostUseCase(ABC):
    """Caso de uso: Optimizar post de Facebook."""
    
    @abstractmethod
    async def execute(self, post: FacebookPost) -> FacebookPost:
        """Ejecutar optimización de post."""
        pass


class BatchGenerateUseCase(ABC):
    """Caso de uso: Generar posts en lote."""
    
    @abstractmethod
    async def execute(
        self, 
        specs: List[PostSpecification], 
        max_concurrency: int = 5
    ) -> List[FacebookPost]:
        """Ejecutar generación en lote."""
        pass


# ===== EVENTS =====

@dataclass(frozen=True)
class PostGeneratedEvent:
    """Evento: Post generado."""
    post_id: str
    specification: PostSpecification
    timestamp: datetime


@dataclass(frozen=True)
class PostAnalyzedEvent:
    """Evento: Post analizado."""
    post_id: str
    analysis_result: AnalysisResult
    timestamp: datetime


@dataclass(frozen=True)
class PostOptimizedEvent:
    """Evento: Post optimizado."""
    post_id: str
    original_content: PostContent
    optimized_content: PostContent
    timestamp: datetime


# ===== ERROR TYPES =====

class FacebookPostError(Exception):
    """Error base para posts de Facebook."""
    pass


class ContentGenerationError(FacebookPostError):
    """Error en generación de contenido."""
    pass


class ContentAnalysisError(FacebookPostError):
    """Error en análisis de contenido."""
    pass


class ContentOptimizationError(FacebookPostError):
    """Error en optimización de contenido."""
    pass


class RepositoryError(FacebookPostError):
    """Error en repositorio."""
    pass


class ValidationError(FacebookPostError):
    """Error de validación."""
    pass 