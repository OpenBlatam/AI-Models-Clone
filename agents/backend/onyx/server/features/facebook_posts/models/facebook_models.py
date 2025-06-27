"""
🎯 Facebook Posts Models
========================

Modelos de datos para el sistema de Facebook posts integrado con Onyx.
Compatibles con LangChain y optimizados para performance.
"""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
from pydantic import BaseModel, Field, validator


class FacebookPostType(str, Enum):
    """Tipos de posts de Facebook."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    LINK = "link"
    CAROUSEL = "carousel"
    POLL = "poll"
    EVENT = "event"
    STORY = "story"


class FacebookTone(str, Enum):
    """Tonos de comunicación para Facebook."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    HUMOROUS = "humorous"
    INSPIRING = "inspiring"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    CONTROVERSIAL = "controversial"


class FacebookAudience(str, Enum):
    """Audiencias objetivo para Facebook."""
    GENERAL = "general"
    YOUNG_ADULTS = "young_adults"
    PROFESSIONALS = "professionals"
    PARENTS = "parents"
    ENTREPRENEURS = "entrepreneurs"
    STUDENTS = "students"
    SENIORS = "seniors"
    CUSTOM = "custom"


class EngagementLevel(str, Enum):
    """Niveles de engagement."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VIRAL = "viral"


@dataclass
class FacebookFingerprint:
    """Identificador único para posts de Facebook."""
    post_id: str
    content_hash: str
    timestamp: datetime
    platform_version: str = "facebook_v1.0"
    
    @classmethod
    def create(cls, content: str, post_type: FacebookPostType = FacebookPostType.TEXT) -> 'FacebookFingerprint':
        """Crear fingerprint para contenido."""
        import hashlib
        
        content_hash = hashlib.md5(content.encode()).hexdigest()
        post_id = str(uuid.uuid4())
        
        return cls(
            post_id=post_id,
            content_hash=content_hash,
            timestamp=datetime.now(),
            platform_version="facebook_v1.0"
        )


class FacebookRequest(BaseModel):
    """Request para generar Facebook post."""
    content_topic: str = Field(..., description="Tema principal del post")
    post_type: FacebookPostType = Field(FacebookPostType.TEXT, description="Tipo de post")
    tone: FacebookTone = Field(FacebookTone.CASUAL, description="Tono del post")
    target_audience: FacebookAudience = Field(FacebookAudience.GENERAL, description="Audiencia objetivo")
    
    # Configuración de contenido
    max_length: int = Field(280, description="Longitud máxima del texto")
    include_hashtags: bool = Field(True, description="Incluir hashtags")
    include_emoji: bool = Field(True, description="Incluir emojis")
    include_call_to_action: bool = Field(True, description="Incluir call to action")
    
    # Configuración avanzada
    keywords: List[str] = Field(default_factory=list, description="Keywords clave")
    brand_voice: Optional[str] = Field(None, description="Voz de marca específica")
    campaign_context: Optional[str] = Field(None, description="Contexto de campaña")
    target_engagement: EngagementLevel = Field(EngagementLevel.HIGH, description="Nivel de engagement objetivo")
    
    # Configuración multimedia
    include_image: bool = Field(False, description="Incluir imagen")
    image_description: Optional[str] = Field(None, description="Descripción de imagen deseada")
    include_video: bool = Field(False, description="Incluir video")
    video_concept: Optional[str] = Field(None, description="Concepto de video")
    
    @validator('max_length')
    def validate_max_length(cls, v):
        if v < 50:
            raise ValueError('max_length debe ser al menos 50 caracteres')
        if v > 2000:
            raise ValueError('max_length no puede exceder 2000 caracteres')
        return v


@dataclass
class FacebookAnalysis:
    """Análisis de un Facebook post."""
    engagement_prediction: float  # 0.0 - 1.0
    virality_score: float  # 0.0 - 1.0
    sentiment_score: float  # 0.0 - 1.0
    readability_score: float  # 0.0 - 1.0
    brand_alignment: float  # 0.0 - 1.0
    
    # Métricas detalladas
    predicted_likes: int
    predicted_shares: int
    predicted_comments: int
    predicted_reach: int
    optimal_posting_time: Optional[datetime] = None
    
    # Insights y recomendaciones
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    hashtag_suggestions: List[str] = field(default_factory=list)
    similar_successful_posts: List[str] = field(default_factory=list)
    
    def overall_score(self) -> float:
        """Calcular score general del post."""
        return (
            self.engagement_prediction * 0.3 +
            self.virality_score * 0.25 +
            self.sentiment_score * 0.2 +
            self.readability_score * 0.15 +
            self.brand_alignment * 0.1
        )


class FacebookPost(BaseModel):
    """Modelo principal de Facebook post."""
    
    # Identificación
    fingerprint: FacebookFingerprint = Field(..., description="Identificador único")
    post_type: FacebookPostType = Field(..., description="Tipo de post")
    
    # Contenido principal
    text_content: str = Field(..., description="Contenido de texto")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags del post")
    mentions: List[str] = Field(default_factory=list, description="Menciones (@)")
    
    # Multimedia
    image_urls: List[str] = Field(default_factory=list, description="URLs de imágenes")
    video_url: Optional[str] = Field(None, description="URL de video")
    link_url: Optional[str] = Field(None, description="URL de enlace")
    link_preview: Optional[Dict[str, Any]] = Field(None, description="Preview del enlace")
    
    # Metadatos
    tone: FacebookTone = Field(..., description="Tono del post")
    target_audience: FacebookAudience = Field(..., description="Audiencia objetivo")
    campaign_id: Optional[str] = Field(None, description="ID de campaña")
    
    # Análisis
    analysis: Optional[FacebookAnalysis] = Field(None, description="Análisis del post")
    
    # Configuración de publicación
    scheduled_time: Optional[datetime] = Field(None, description="Hora programada")
    auto_publish: bool = Field(False, description="Publicación automática")
    
    # Tracking
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = Field("1.0", description="Versión del post")
    
    # LangChain metadata
    langchain_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata de LangChain")
    generation_metrics: Dict[str, Any] = Field(default_factory=dict, description="Métricas de generación")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def get_display_text(self) -> str:
        """Obtener texto para mostrar (con hashtags)."""
        text = self.text_content
        if self.hashtags:
            text += "\n\n" + " ".join(f"#{tag}" for tag in self.hashtags)
        return text
    
    def get_character_count(self) -> int:
        """Obtener conteo de caracteres del post completo."""
        return len(self.get_display_text())
    
    def is_within_limits(self) -> bool:
        """Verificar si el post está dentro de los límites de Facebook."""
        return self.get_character_count() <= 2000
    
    def get_engagement_prediction(self) -> float:
        """Obtener predicción de engagement."""
        if self.analysis:
            return self.analysis.engagement_prediction
        return 0.5  # Default neutral


class FacebookPostVariation(BaseModel):
    """Variación de un Facebook post."""
    base_post_id: str = Field(..., description="ID del post base")
    variation_type: str = Field(..., description="Tipo de variación")
    post: FacebookPost = Field(..., description="Post variado")
    differences: List[str] = Field(default_factory=list, description="Diferencias con el original")
    a_b_test_metrics: Dict[str, Any] = Field(default_factory=dict, description="Métricas de A/B testing")


class FacebookCampaign(BaseModel):
    """Campaña de Facebook posts."""
    campaign_id: str = Field(..., description="ID de la campaña")
    name: str = Field(..., description="Nombre de la campaña")
    description: Optional[str] = Field(None, description="Descripción")
    
    posts: List[FacebookPost] = Field(default_factory=list, description="Posts de la campaña")
    variations: List[FacebookPostVariation] = Field(default_factory=list, description="Variaciones A/B")
    
    # Configuración
    start_date: datetime = Field(..., description="Fecha de inicio")
    end_date: Optional[datetime] = Field(None, description="Fecha de fin")
    budget: Optional[float] = Field(None, description="Presupuesto")
    
    # Métricas agregadas
    total_engagement: int = Field(0, description="Engagement total")
    total_reach: int = Field(0, description="Alcance total")
    conversion_rate: float = Field(0.0, description="Tasa de conversión")
    
    # LangChain workflow
    workflow_config: Dict[str, Any] = Field(default_factory=dict, description="Configuración de workflow")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Modelos de respuesta API
class FacebookPostResponse(BaseModel):
    """Respuesta de generación de Facebook post."""
    success: bool = Field(..., description="Éxito de la operación")
    post: Optional[FacebookPost] = Field(None, description="Post generado")
    variations: List[FacebookPost] = Field(default_factory=list, description="Variaciones del post")
    analysis: Optional[FacebookAnalysis] = Field(None, description="Análisis del post")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones")
    processing_time_ms: float = Field(..., description="Tiempo de procesamiento")
    error_message: Optional[str] = Field(None, description="Mensaje de error")


class FacebookAnalysisResponse(BaseModel):
    """Respuesta de análisis de Facebook post."""
    success: bool = Field(..., description="Éxito del análisis")
    analysis: Optional[FacebookAnalysis] = Field(None, description="Análisis completo")
    insights: List[str] = Field(default_factory=list, description="Insights clave")
    optimization_suggestions: List[str] = Field(default_factory=list, description="Sugerencias de optimización")
    competitive_analysis: Dict[str, Any] = Field(default_factory=dict, description="Análisis competitivo")
    processing_time_ms: float = Field(..., description="Tiempo de procesamiento")


# Modelos para LangChain
class LangChainPromptTemplate(BaseModel):
    """Template de prompt para LangChain."""
    template_name: str = Field(..., description="Nombre del template")
    template_content: str = Field(..., description="Contenido del template")
    variables: List[str] = Field(default_factory=list, description="Variables del template")
    post_type: FacebookPostType = Field(..., description="Tipo de post aplicable")
    tone: Optional[FacebookTone] = Field(None, description="Tono específico")


class LangChainChainConfig(BaseModel):
    """Configuración de cadena LangChain."""
    chain_type: str = Field(..., description="Tipo de cadena")
    model_name: str = Field("gpt-3.5-turbo", description="Modelo LLM")
    temperature: float = Field(0.7, description="Temperatura del modelo")
    max_tokens: int = Field(500, description="Máximo tokens")
    use_memory: bool = Field(True, description="Usar memoria conversacional")
    enable_tools: bool = Field(False, description="Habilitar herramientas")
    custom_prompts: List[LangChainPromptTemplate] = Field(default_factory=list, description="Prompts personalizados") 