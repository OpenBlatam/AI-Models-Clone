from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator
from pydantic.config import ConfigDict
        import re
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
🚀 ULTRA LANDING PAGE MODELS - SEO & COPY OPTIMIZED
===================================================

Modelos avanzados para landing pages con el mejor SEO y copy,
integrados con LangChain y compatibles con Onyx BaseModel.
"""



# =============================================================================
# 🎯 ENUMS Y TIPOS
# =============================================================================

class LandingPageType(str, Enum):
    """Tipos de landing page optimizados."""
    SALES = "sales"
    LEAD_CAPTURE = "lead_capture" 
    PRODUCT_LAUNCH = "product_launch"
    WEBINAR = "webinar"
    EBOOK = "ebook"
    COURSE = "course"
    SAAS = "saas"
    ECOMMERCE = "ecommerce"  # Tienda online
    AGENCY = "agency"        # Servicios de agencia
    PERSONAL_BRAND = "personal_brand"  # Marca personal


class CopyTone(str, Enum):
    """Tonos de comunicación."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    URGENT = "urgent"
    LUXURY = "luxury"
    PERSUASIVE = "persuasive"


class SEODifficulty(str, Enum):
    """Dificultad SEO de las keywords."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA_HIGH = "ultra_high"


class ConversionGoal(str, Enum):
    """Objetivos de conversión."""
    PURCHASE = "purchase"
    SIGNUP = "signup"
    DOWNLOAD = "download"
    CONTACT = "contact"
    SUBSCRIBE = "subscribe"
    DEMO = "demo"
    CONSULTATION = "consultation"


# =============================================================================
# 🎨 MODELOS DE COMPONENTES
# =============================================================================

class SEOMetadata(BaseModel):
    """Metadatos SEO ultra-optimizados."""
    
    title: str = Field(..., min_length=30, max_length=60, description="Título SEO")
    meta_description: str = Field(..., min_length=120, max_length=160, description="Meta descripción")
    primary_keyword: str = Field(..., description="Keyword principal")
    secondary_keywords: List[str] = Field(default_factory=list, description="Keywords secundarias")
    canonical_url: Optional[str] = Field(None, description="URL canónica")
    schema_markup: Dict[str, Any] = Field(default_factory=dict, description="Schema.org")
    seo_score: float = Field(default=85.0, ge=0.0, le=100.0, description="Score SEO")
    
    @validator('title')
    def validate_title(cls, v: str) -> str:
        if len(v.strip()) < 30:
            raise ValueError("Título debe tener al menos 30 caracteres")
        return v.strip()


class CopySection(BaseModel):
    """Sección de copy optimizada."""
    
    section_id: str = Field(..., description="ID de la sección")
    headline: str = Field(..., min_length=10, max_length=100, description="Headline")
    subheadline: Optional[str] = Field(None, max_length=200, description="Subheadline")
    body_text: str = Field(..., min_length=50, description="Texto principal")
    cta_text: str = Field(..., min_length=3, max_length=50, description="CTA")
    cta_url: Optional[str] = Field(None, description="URL del CTA")
    copy_tone: CopyTone = Field(default=CopyTone.PROFESSIONAL, description="Tono")
    conversion_score: float = Field(default=75.0, ge=0.0, le=100.0, description="Score conversión")


class TestimonialModel(BaseModel):
    """Testimonio optimizado."""
    
    quote: str = Field(..., min_length=50, max_length=500, description="Testimonio")
    author_name: str = Field(..., min_length=2, max_length=100, description="Autor")
    author_title: Optional[str] = Field(None, max_length=100, description="Cargo")
    author_company: Optional[str] = Field(None, max_length=100, description="Empresa")
    credibility_score: float = Field(default=80.0, ge=0.0, le=100.0, description="Credibilidad")


class FeatureModel(BaseModel):
    """Feature optimizada para persuasión."""
    
    title: str = Field(..., min_length=5, max_length=80, description="Título")
    description: str = Field(..., min_length=50, max_length=300, description="Descripción")
    benefit: str = Field(..., min_length=20, max_length=150, description="Beneficio")
    icon_name: Optional[str] = Field(None, description="Icono")
    pain_point_solved: str = Field(..., description="Dolor que resuelve")
    importance_score: int = Field(default=8, ge=1, le=10, description="Importancia")


class PricingModel(BaseModel):
    """Modelo de precios optimizado para conversión."""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    # Información del plan
    plan_name: str = Field(..., min_length=3, max_length=50, description="Nombre del plan")
    price: Decimal = Field(..., ge=0, description="Precio")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="Moneda")
    billing_period: str = Field(default="monthly", description="Período de facturación")
    
    # Pricing psychology
    original_price: Optional[Decimal] = Field(None, ge=0, description="Precio original (para descuentos)")
    discount_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="% de descuento")
    urgency_text: Optional[str] = Field(None, description="Texto de urgencia")
    
    # Features incluidas
    features_included: List[str] = Field(default_factory=list, description="Features incluidas")
    features_highlighted: List[str] = Field(default_factory=list, description="Features destacadas")
    
    # Optimización de conversión
    is_most_popular: bool = Field(default=False, description="Plan más popular")
    conversion_optimized: bool = Field(default=True, description="Optimizado para conversión")
    psychological_price: bool = Field(default=False, description="Precio psicológico (99, 97, etc.)")
    
    @validator('discount_percentage', always=True)
    def calculate_discount(cls, v, values) -> Any:
        """Calcula el descuento automáticamente."""
        price = values.get('price')
        original_price = values.get('original_price')
        
        if original_price and price and original_price > price:
            discount = ((original_price - price) / original_price) * 100
            return round(discount, 1)
        return 0.0


# =============================================================================
# 🏠 MODELO PRINCIPAL
# =============================================================================

class UltraLandingPageModel(BaseModel):
    """Modelo principal de landing page ultra-optimizado."""
    
    # Identificación
    id: Optional[str] = Field(None, description="ID único")
    name: str = Field(..., min_length=5, max_length=100, description="Nombre")
    slug: str = Field(..., min_length=3, max_length=100, description="URL slug")
    
    # Configuración
    page_type: LandingPageType = Field(..., description="Tipo de página")
    conversion_goal: ConversionGoal = Field(..., description="Objetivo")
    target_audience: str = Field(..., min_length=10, description="Audiencia")
    
    # SEO y contenido
    seo_metadata: SEOMetadata = Field(..., description="SEO")
    hero_section: CopySection = Field(..., description="Hero")
    features: List[FeatureModel] = Field(default_factory=list, description="Features")
    testimonials: List[TestimonialModel] = Field(default_factory=list, description="Testimonios")
    
    # Optimización
    conversion_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Tasa conversión")
    performance_score: float = Field(default=85.0, ge=0.0, le=100.0, description="Performance")
    
    # LangChain integration
    ai_generated_content: Dict[str, Any] = Field(default_factory=dict, description="Contenido IA")
    langchain_prompts: Dict[str, str] = Field(default_factory=dict, description="Prompts")
    
    # Temporal
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creación")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Actualización")
    status: str = Field(default="draft", description="Estado")
    
    @validator('slug')
    def validate_slug(cls, v: str) -> str:
        slug = re.sub(r'[^a-z0-9\-]', '-', v.lower())
        slug = re.sub(r'-+', '-', slug).strip('-')
        if len(slug) < 3:
            raise ValueError("Slug debe tener al menos 3 caracteres")
        return slug
    
    def calculate_overall_score(self) -> float:
        """Calcula score general."""
        scores = [
            self.seo_metadata.seo_score,
            self.hero_section.conversion_score,
            self.performance_score
        ]
        
        if self.testimonials:
            avg_credibility = sum(t.credibility_score for t in self.testimonials) / len(self.testimonials)
            scores.append(avg_credibility)
        
        return round(sum(scores) / len(scores), 1)


# =============================================================================
# 📊 MODELOS API
# =============================================================================

class LandingPageCreateRequest(BaseModel):
    """Request para crear landing page."""
    
    name: str = Field(..., min_length=5, max_length=100, description="Nombre")
    page_type: LandingPageType = Field(..., description="Tipo")
    conversion_goal: ConversionGoal = Field(..., description="Objetivo")
    target_audience: str = Field(..., min_length=10, description="Audiencia")
    
    # SEO básico
    primary_keyword: str = Field(..., description="Keyword principal")
    title: str = Field(..., min_length=30, max_length=60, description="Título SEO")
    meta_description: str = Field(..., min_length=120, max_length=160, description="Meta descripción")
    
    # Hero básico
    hero_headline: str = Field(..., min_length=10, max_length=100, description="Headline")
    hero_body: str = Field(..., min_length=50, description="Texto hero")
    hero_cta: str = Field(..., min_length=3, max_length=50, description="CTA")
    
    # Opcionales
    copy_tone: CopyTone = Field(default=CopyTone.PROFESSIONAL, description="Tono")
    ai_enhance: bool = Field(default=True, description="Mejorar con IA")


class LandingPageResponse(BaseModel):
    """Response de landing page."""
    
    id: str
    name: str
    slug: str
    page_type: str
    status: str
    
    # URLs
    preview_url: str
    published_url: Optional[str] = None
    
    # Métricas
    overall_score: float
    seo_score: float
    conversion_score: float
    
    # Datos SEO
    primary_keyword: str
    title: str
    
    # Contadores
    features_count: int
    testimonials_count: int
    
    # Temporal
    created_at: datetime
    updated_at: datetime


# =============================================================================
# 🎯 MODELOS DE OPTIMIZACIÓN Y ANÁLISIS
# =============================================================================

class ConversionAnalysis(BaseModel):
    """Análisis de conversión de la landing page."""
    
    overall_conversion_score: float = Field(ge=0.0, le=100.0)
    
    # Análisis por secciones
    hero_effectiveness: float = Field(ge=0.0, le=100.0)
    features_persuasion: float = Field(ge=0.0, le=100.0)
    social_proof_strength: float = Field(ge=0.0, le=100.0)
    cta_optimization: float = Field(ge=0.0, le=100.0)
    
    # Recomendaciones
    optimization_suggestions: List[str] = Field(default_factory=list)
    priority_improvements: List[Dict[str, str]] = Field(default_factory=list)
    
    # Benchmarking
    industry_benchmark: float = Field(default=0.0)
    performance_vs_benchmark: str = Field(default="average")


class AIContentSuggestions(BaseModel):
    """Sugerencias de contenido generado por IA."""
    
    # Headlines alternativos
    alternative_headlines: List[str] = Field(default_factory=list, max_items=5)
    
    # Variaciones de copy
    hero_variations: List[str] = Field(default_factory=list, max_items=3)
    cta_variations: List[str] = Field(default_factory=list, max_items=5)
    
    # Mejoras SEO
    seo_improvements: List[str] = Field(default_factory=list)
    keyword_suggestions: List[str] = Field(default_factory=list)
    
    # Elementos de persuasión
    persuasion_elements: List[str] = Field(default_factory=list)
    urgency_phrases: List[str] = Field(default_factory=list)
    
    # Metadata de generación
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    ai_model_used: str = Field(default="gpt-4")
    confidence_score: float = Field(default=85.0, ge=0.0, le=100.0)


if __name__ == "__main__":
    print("🚀 ULTRA LANDING PAGE MODELS LOADED")
    print("✅ SEO-optimized")
    print("✅ Conversion-focused")
    print("✅ LangChain ready")
    print("🎯 Ready for ultra-converting pages!") 