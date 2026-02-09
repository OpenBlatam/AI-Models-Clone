from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import List, Optional, Dict, Any, Union, Protocol
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import uuid
import hashlib
import re
from pydantic import BaseModel, Field, validator, root_validator
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
🎯 Facebook Posts - Refactored Models for Onyx Features
======================================================

Modelos refactorizados siguiendo la arquitectura de features de Onyx.
Integración completa con Clean Architecture, LangChain y patrones enterprise.
"""



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
    """Estados del contenido en el workflow."""
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
    def validate_max_length(cls, v) -> bool:
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
    
    @dataclass
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


class FacebookPostResponse(BaseModel):
    """Respuesta de generación de Facebook post."""
    success: bool = Field(..., description="Éxito de la operación")
    post: Optional[FacebookPost] = Field(None, description="Post generado")
    variations: List[FacebookPost] = Field(default_factory=list, description="Variaciones del post")
    analysis: Optional[FacebookAnalysis] = Field(None, description="Análisis del post")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones")
    processing_time_ms: float = Field(..., description="Tiempo de procesamiento")
    error_message: Optional[str] = Field(None, description="Mensaje de error") 