"""
🚀 LANDING PAGE MODELS - REFACTORED VERSION
==========================================

Modelos Pydantic refactorizados para el sistema ultra-avanzado de landing pages.
Diseñados para máxima performance y flexibilidad.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from enum import Enum


class PageStatus(str, Enum):
    """Estados posibles de una landing page."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class OptimizationLevel(str, Enum):
    """Niveles de optimización."""
    BASIC = "basic"
    ADVANCED = "advanced"
    ULTRA = "ultra"


class SEOModel(BaseModel):
    """Modelo para configuración SEO ultra-optimizada."""
    
    title: str = Field(..., min_length=30, max_length=60, description="Título SEO optimizado")
    meta_description: str = Field(..., min_length=120, max_length=160, description="Meta descripción")
    keywords: List[str] = Field(default_factory=list, description="Keywords principales")
    schema_markup: Dict[str, Any] = Field(default_factory=dict, description="Schema.org markup")
    canonical_url: Optional[str] = Field(None, description="URL canónica")
    open_graph: Dict[str, str] = Field(default_factory=dict, description="Open Graph meta tags")
    twitter_card: Dict[str, str] = Field(default_factory=dict, description="Twitter Card meta tags")
    
    # Métricas SEO
    seo_score: float = Field(default=0.0, ge=0, le=100, description="Score SEO 0-100")
    keyword_density: float = Field(default=0.0, ge=0, le=100, description="Densidad de keywords %")
    readability_score: float = Field(default=0.0, ge=0, le=100, description="Score de legibilidad")
    
    @validator('title')
    def validate_title_optimization(cls, v):
        """Valida que el título esté optimizado para conversiones."""
        power_words = ['ultimate', 'proven', 'revolutionary', 'exclusive', 'guaranteed']
        if not any(word in v.lower() for word in power_words):
            raise ValueError('Title should include power words for better conversion')
        return v


class ContentModel(BaseModel):
    """Modelo para el contenido de la landing page."""
    
    # Elementos principales
    headline: str = Field(..., min_length=10, max_length=100, description="Headline principal")
    subheadline: str = Field(..., max_length=200, description="Subheadline de apoyo")
    value_proposition: str = Field(..., max_length=500, description="Propuesta de valor")
    
    # Elementos de conversión
    primary_cta: str = Field(..., max_length=50, description="CTA principal")
    secondary_cta: Optional[str] = Field(None, max_length=50, description="CTA secundario")
    urgency_element: Optional[str] = Field(None, description="Elemento de urgencia")
    
    # Contenido de apoyo
    features: List[Dict[str, str]] = Field(default_factory=list, description="Lista de características")
    benefits: List[Dict[str, str]] = Field(default_factory=list, description="Lista de beneficios")
    testimonials: List[Dict[str, Any]] = Field(default_factory=list, description="Testimonios de clientes")
    
    # Elementos de confianza
    social_proof: Dict[str, Any] = Field(default_factory=dict, description="Prueba social")
    guarantees: List[str] = Field(default_factory=list, description="Garantías ofrecidas")
    trust_signals: List[str] = Field(default_factory=list, description="Señales de confianza")
    
    # Configuración de diseño
    color_scheme: Dict[str, str] = Field(default_factory=dict, description="Esquema de colores")
    layout_type: str = Field(default="modern", description="Tipo de layout")
    mobile_optimized: bool = Field(default=True, description="Optimizado para móvil")
    
    # Métricas de contenido
    content_quality_score: float = Field(default=0.0, ge=0, le=100, description="Score de calidad")
    conversion_optimization_score: float = Field(default=0.0, ge=0, le=100, description="Score de optimización")
    engagement_score: float = Field(default=0.0, ge=0, le=100, description="Score de engagement")
    
    @validator('primary_cta')
    def validate_cta_effectiveness(cls, v):
        """Valida que el CTA sea efectivo."""
        action_words = ['get', 'start', 'try', 'claim', 'download', 'access', 'join']
        if not any(word in v.lower() for word in action_words):
            raise ValueError('CTA should start with action word for better conversion')
        return v


class LandingPageModel(BaseModel):
    """Modelo principal ultra-optimizado de landing page."""
    
    # Identificación
    id: str = Field(..., description="ID único de la landing page")
    name: str = Field(..., min_length=1, max_length=200, description="Nombre de la página")
    status: PageStatus = Field(default=PageStatus.DRAFT, description="Estado actual")
    
    # Configuración básica
    industry: str = Field(..., description="Industria objetivo")
    target_audience: str = Field(..., description="Audiencia objetivo")
    objectives: List[str] = Field(default_factory=list, description="Objetivos de conversión")
    
    # Contenido y SEO
    content: ContentModel = Field(..., description="Contenido de la página")
    seo: SEOModel = Field(..., description="Configuración SEO")
    
    # IA y Analytics
    ai_prediction: Optional[Dict[str, Any]] = Field(None, description="Predicción de IA")
    competitor_analysis: Optional[Dict[str, Any]] = Field(None, description="Análisis de competidores")
    personalization_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Reglas de personalización")
    
    # Configuración técnica
    domain: Optional[str] = Field(None, description="Dominio personalizado")
    tracking_codes: Dict[str, str] = Field(default_factory=dict, description="Códigos de tracking")
    integration_settings: Dict[str, Any] = Field(default_factory=dict, description="Configuraciones de integración")
    
    # Timestamps
    creation_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación")
    last_modified: datetime = Field(default_factory=datetime.utcnow, description="Última modificación")
    last_optimization: Optional[datetime] = Field(None, description="Última optimización")
    
    # Métricas y performance
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Métricas de performance")
    conversion_rate: float = Field(default=0.0, ge=0, le=100, description="Tasa de conversión actual")
    traffic_sources: Dict[str, int] = Field(default_factory=dict, description="Fuentes de tráfico")
    
    # Configuración avanzada
    optimization_level: OptimizationLevel = Field(default=OptimizationLevel.ULTRA, description="Nivel de optimización")
    auto_optimization_enabled: bool = Field(default=True, description="Optimización automática habilitada")
    ab_testing_active: bool = Field(default=False, description="A/B testing activo")
    
    class Config:
        """Configuración del modelo."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "lp_12345",
                "name": "SaaS Product Launch Page",
                "status": "active",
                "industry": "saas",
                "target_audience": "business owners",
                "objectives": ["lead_generation", "trial_signup"],
                "content": {
                    "headline": "Revolutionary Business Automation Software",
                    "subheadline": "Save 20+ Hours Weekly with AI-Powered Automation",
                    "value_proposition": "The only platform that combines AI with human expertise",
                    "primary_cta": "Start Free Trial",
                    "features": [
                        {"title": "AI Automation", "description": "Smart workflow automation"}
                    ]
                },
                "seo": {
                    "title": "Best Business Automation Software 2024 - Free Trial",
                    "meta_description": "Transform your business with our AI-powered automation platform. Trusted by 50,000+ companies. Start free trial today!",
                    "keywords": ["business automation", "workflow software", "ai platform"]
                }
            }
        }
    
    @validator('conversion_rate')
    def validate_conversion_rate(cls, v):
        """Valida que la tasa de conversión sea realista."""
        if v > 50:
            raise ValueError('Conversion rate above 50% is unrealistic')
        return v
    
    def update_last_modified(self):
        """Actualiza timestamp de última modificación."""
        self.last_modified = datetime.utcnow()
    
    def get_optimization_score(self) -> float:
        """Calcula score general de optimización."""
        scores = [
            self.seo.seo_score,
            self.content.content_quality_score,
            self.content.conversion_optimization_score,
            self.content.engagement_score
        ]
        return sum(scores) / len(scores)


class OptimizationResult(BaseModel):
    """Resultado de una optimización aplicada."""
    
    page_id: str = Field(..., description="ID de la página optimizada")
    optimization_type: str = Field(..., description="Tipo de optimización")
    optimizations_applied: List[Dict[str, Any]] = Field(..., description="Optimizaciones aplicadas")
    
    # Métricas de resultado
    expected_lift_percentage: float = Field(..., description="Mejora esperada en %")
    confidence_score: float = Field(default=0.0, ge=0, le=100, description="Confianza en la optimización")
    implementation_status: str = Field(..., description="Estado de implementación")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de la optimización")
    applied_by: str = Field(default="auto_system", description="Aplicado por")
    
    # Resultados de A/B testing
    ab_test_results: Optional[Dict[str, Any]] = Field(None, description="Resultados de A/B testing")
    statistical_significance: Optional[float] = Field(None, description="Significancia estadística")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PageAnalytics(BaseModel):
    """Modelo para analytics de página."""
    
    page_id: str = Field(..., description="ID de la página")
    
    # Métricas principales
    visitors_today: int = Field(default=0, description="Visitantes hoy")
    conversions_today: int = Field(default=0, description="Conversiones hoy")
    conversion_rate_today: float = Field(default=0.0, description="Tasa conversión hoy")
    
    # Métricas históricas
    visitors_7d: int = Field(default=0, description="Visitantes últimos 7 días")
    conversions_7d: int = Field(default=0, description="Conversiones últimos 7 días")
    conversion_rate_7d: float = Field(default=0.0, description="Tasa conversión 7 días")
    
    # Engagement
    bounce_rate: float = Field(default=0.0, description="Tasa de rebote")
    avg_session_duration: float = Field(default=0.0, description="Duración promedio sesión")
    pages_per_session: float = Field(default=0.0, description="Páginas por sesión")
    
    # Performance técnico
    page_load_speed: float = Field(default=0.0, description="Velocidad de carga en segundos")
    mobile_performance_score: float = Field(default=0.0, description="Score performance móvil")
    
    # Revenue
    revenue_today: float = Field(default=0.0, description="Revenue hoy")
    revenue_7d: float = Field(default=0.0, description="Revenue 7 días")
    average_order_value: float = Field(default=0.0, description="Valor promedio pedido")
    
    # Timestamps
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Última actualización")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 