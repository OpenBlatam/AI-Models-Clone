"""
ONYX BLOG POST - Models Module
=============================

Modelos de datos para el sistema de blog posts integrado con Onyx.
Compatible con OpenRouter y LangChain.
"""

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum

class BlogPostType(Enum):
    """Tipos de blog posts soportados"""
    TECHNICAL = "technical"
    TUTORIAL = "tutorial" 
    NEWS = "news"
    OPINION = "opinion"
    REVIEW = "review"
    GUIDE = "guide"
    CASE_STUDY = "case_study"
    ANNOUNCEMENT = "announcement"

class BlogPostTone(Enum):
    """Tonos para blog posts"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"
    EDUCATIONAL = "educational"
    INSPIRATIONAL = "inspirational"

class BlogPostLength(Enum):
    """Longitudes de blog posts"""
    SHORT = ("short", 300, 600)      # 300-600 words
    MEDIUM = ("medium", 600, 1200)   # 600-1200 words  
    LONG = ("long", 1200, 2500)      # 1200-2500 words
    EXTENDED = ("extended", 2500, 5000)  # 2500-5000 words
    
    def __init__(self, name: str, min_words: int, max_words: int):
        self.display_name = name
        self.min_words = min_words
        self.max_words = max_words

class OpenRouterModel(Enum):
    """Modelos disponibles en OpenRouter"""
    GPT_4_TURBO = "openai/gpt-4-turbo"
    GPT_4O = "openai/gpt-4o"
    CLAUDE_3_SONNET = "anthropic/claude-3-sonnet"
    CLAUDE_3_HAIKU = "anthropic/claude-3-haiku"
    GEMINI_PRO = "google/gemini-pro"
    MISTRAL_LARGE = "mistralai/mistral-large"
    LLAMA_3_70B = "meta-llama/llama-3-70b-instruct"
    COHERE_COMMAND_R = "cohere/command-r"

class BlogPostStatus(Enum):
    """Estados del blog post"""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    PUBLISHED = "published"
    FAILED = "failed"

@dataclass
class SEOMetadata:
    """Metadata SEO para blog posts"""
    meta_title: str = ""
    meta_description: str = ""
    keywords: List[str] = field(default_factory=list)
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""
    canonical_url: str = ""
    schema_markup: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "keywords": self.keywords,
            "og_title": self.og_title,
            "og_description": self.og_description,
            "og_image": self.og_image,
            "canonical_url": self.canonical_url,
            "schema_markup": self.schema_markup
        }

@dataclass
class BlogPostStructure:
    """Estructura del blog post"""
    title: str = ""
    introduction: str = ""
    main_sections: List[Dict[str, str]] = field(default_factory=list)  # [{"title": "", "content": ""}]
    conclusion: str = ""
    call_to_action: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "introduction": self.introduction,
            "main_sections": self.main_sections,
            "conclusion": self.conclusion,
            "call_to_action": self.call_to_action
        }
    
    def get_word_count(self) -> int:
        """Calcular total de palabras"""
        total_words = 0
        total_words += len(self.title.split())
        total_words += len(self.introduction.split())
        total_words += len(self.conclusion.split())
        total_words += len(self.call_to_action.split())
        
        for section in self.main_sections:
            total_words += len(section.get("title", "").split())
            total_words += len(section.get("content", "").split())
        
        return total_words

@dataclass
class BlogPostRequest:
    """Request para generar blog post"""
    topic: str
    blog_type: BlogPostType = BlogPostType.TECHNICAL
    tone: BlogPostTone = BlogPostTone.PROFESSIONAL
    length: BlogPostLength = BlogPostLength.MEDIUM
    target_audience: str = "general"
    keywords: List[str] = field(default_factory=list)
    outline: List[str] = field(default_factory=list)  # Estructura opcional
    context: str = ""  # Contexto adicional
    include_seo: bool = True
    include_images: bool = False
    language: str = "es"
    model: OpenRouterModel = OpenRouterModel.GPT_4_TURBO
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Validación y sanitización automática"""
        if not self.topic:
            raise ValueError("Topic es requerido para generar blog post")
        
        # Limpiar topic
        self.topic = self.topic.strip()
        
        # Validar longitud del topic
        if len(self.topic) < 5:
            raise ValueError("Topic debe tener al menos 5 caracteres")
        
        # Limpiar keywords
        self.keywords = [kw.strip().lower() for kw in self.keywords if kw.strip()]
        
        # Limitar keywords
        if len(self.keywords) > 20:
            self.keywords = self.keywords[:20]
        
        # Limpiar outline
        self.outline = [item.strip() for item in self.outline if item.strip()]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            "topic": self.topic,
            "blog_type": self.blog_type.value,
            "tone": self.tone.value,
            "length": {
                "name": self.length.display_name,
                "min_words": self.length.min_words,
                "max_words": self.length.max_words
            },
            "target_audience": self.target_audience,
            "keywords": self.keywords,
            "outline": self.outline,
            "context": self.context,
            "include_seo": self.include_seo,
            "include_images": self.include_images,
            "language": self.language,
            "model": self.model.value,
            "request_id": self.request_id,
            "timestamp": self.timestamp
        }

@dataclass
class BlogPostResponse:
    """Response del blog post generado"""
    request_id: str
    blog_post: BlogPostStructure
    seo_metadata: Optional[SEOMetadata] = None
    word_count: int = 0
    character_count: int = 0
    reading_time_minutes: int = 0
    status: BlogPostStatus = BlogPostStatus.COMPLETED
    model_used: str = ""
    generation_time_ms: float = 0.0
    tokens_used: int = 0
    cost_usd: float = 0.0
    quality_score: float = 0.0
    onyx_metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Cálculos automáticos"""
        if self.blog_post and self.word_count == 0:
            self.word_count = self.blog_post.get_word_count()
        
        if self.word_count > 0 and self.reading_time_minutes == 0:
            # Promedio 200 palabras por minuto
            self.reading_time_minutes = max(1, round(self.word_count / 200))
        
        # Calcular character count si no está presente
        if self.character_count == 0 and self.blog_post:
            full_text = f"{self.blog_post.title} {self.blog_post.introduction} {self.blog_post.conclusion}"
            for section in self.blog_post.main_sections:
                full_text += f" {section.get('title', '')} {section.get('content', '')}"
            self.character_count = len(full_text)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            "request_id": self.request_id,
            "blog_post": self.blog_post.to_dict() if self.blog_post else None,
            "seo_metadata": self.seo_metadata.to_dict() if self.seo_metadata else None,
            "word_count": self.word_count,
            "character_count": self.character_count,
            "reading_time_minutes": self.reading_time_minutes,
            "status": self.status.value,
            "model_used": self.model_used,
            "generation_time_ms": self.generation_time_ms,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "quality_score": self.quality_score,
            "onyx_metadata": self.onyx_metadata,
            "timestamp": self.timestamp
        }

@dataclass
class LangChainPrompt:
    """Prompt estructurado para LangChain"""
    system_prompt: str
    user_prompt: str
    variables: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, str]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    
    def format_prompt(self, **kwargs) -> str:
        """Formatear prompt con variables"""
        formatted_user = self.user_prompt.format(**self.variables, **kwargs)
        
        if self.examples:
            examples_text = "\n\nEjemplos:\n"
            for i, example in enumerate(self.examples, 1):
                examples_text += f"{i}. Input: {example.get('input', '')}\n"
                examples_text += f"   Output: {example.get('output', '')}\n"
            formatted_user += examples_text
        
        if self.constraints:
            constraints_text = "\n\nRestricciones:\n"
            for constraint in self.constraints:
                constraints_text += f"- {constraint}\n"
            formatted_user += constraints_text
        
        return formatted_user

@dataclass
class OpenRouterRequest:
    """Request específico para OpenRouter"""
    model: str
    messages: List[Dict[str, str]]
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stream: bool = False
    stop: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a formato API"""
        data = {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stream": self.stream
        }
        
        if self.max_tokens is not None:
            data["max_tokens"] = self.max_tokens
        
        if self.stop is not None:
            data["stop"] = self.stop
        
        return data

@dataclass
class OpenRouterResponse:
    """Response de OpenRouter"""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    
    def get_content(self) -> str:
        """Extraer contenido de la respuesta"""
        if self.choices and len(self.choices) > 0:
            message = self.choices[0].get("message", {})
            return message.get("content", "")
        return ""
    
    def get_tokens_used(self) -> int:
        """Obtener tokens utilizados"""
        return self.usage.get("total_tokens", 0)

@dataclass
class OnyxIntegration:
    """Datos de integración con Onyx"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    workspace_id: Optional[str] = None
    document_set_id: Optional[str] = None
    persona_id: Optional[str] = None
    onyx_request_id: Optional[str] = None
    priority: int = 1
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "workspace_id": self.workspace_id,
            "document_set_id": self.document_set_id,
            "persona_id": self.persona_id,
            "onyx_request_id": self.onyx_request_id,
            "priority": self.priority,
            "tags": self.tags,
            "metadata": self.metadata
        }

@dataclass
class BlogPostMetrics:
    """Métricas del sistema de blog posts"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_generation_time: float = 0.0
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    posts_by_type: Dict[str, int] = field(default_factory=dict)
    posts_by_model: Dict[str, int] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    
    def update_metrics(self, response: BlogPostResponse):
        """Actualizar métricas con nueva respuesta"""
        self.total_requests += 1
        
        if response.status == BlogPostStatus.COMPLETED:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        self.total_generation_time += response.generation_time_ms
        self.total_tokens_used += response.tokens_used
        self.total_cost_usd += response.cost_usd
        
        # Actualizar por modelo
        if response.model_used:
            self.posts_by_model[response.model_used] = self.posts_by_model.get(response.model_used, 0) + 1
    
    def get_success_rate(self) -> float:
        """Calcular tasa de éxito"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100.0
    
    def get_average_generation_time(self) -> float:
        """Calcular tiempo promedio de generación"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_generation_time / self.successful_requests
    
    def get_average_cost(self) -> float:
        """Calcular costo promedio por post"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_cost_usd / self.successful_requests

# Type aliases para claridad
BlogPostID = str
UserID = str
SessionID = str
WorkspaceID = str

__all__ = [
    # Enums
    'BlogPostType',
    'BlogPostTone', 
    'BlogPostLength',
    'OpenRouterModel',
    'BlogPostStatus',
    
    # Data classes
    'SEOMetadata',
    'BlogPostStructure',
    'BlogPostRequest',
    'BlogPostResponse',
    'LangChainPrompt',
    'OpenRouterRequest',
    'OpenRouterResponse',
    'OnyxIntegration',
    'BlogPostMetrics',
    
    # Type aliases
    'BlogPostID',
    'UserID',
    'SessionID', 
    'WorkspaceID',
] 