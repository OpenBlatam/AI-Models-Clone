"""
Models Module - Modelos de Datos y Esquemas
==========================================

Este módulo contiene todos los modelos Pydantic y esquemas de datos:
- LandingPageModel: Modelo principal de landing page
- AIModels: Modelos relacionados con IA
- AnalyticsModels: Modelos de analytics
- NLPModels: Modelos de procesamiento de lenguaje natural
"""

from .landing_page_models import (
    LandingPageModel,
    OptimizationResult,
    ContentModel,
    SEOModel
)

from .ai_models import (
    ConversionPrediction,
    CompetitorAnalysis,
    PersonalizationProfile
)

from .analytics_models import (
    RealTimeMetric,
    UserJourney,
    ConversionFunnel
)

from .nlp_models import (
    SentimentAnalysis,
    KeywordAnalysis,
    ContentOptimization
)

__all__ = [
    # Landing Page Models
    "LandingPageModel",
    "OptimizationResult", 
    "ContentModel",
    "SEOModel",
    
    # AI Models
    "ConversionPrediction",
    "CompetitorAnalysis",
    "PersonalizationProfile",
    
    # Analytics Models
    "RealTimeMetric",
    "UserJourney",
    "ConversionFunnel",
    
    # NLP Models
    "SentimentAnalysis",
    "KeywordAnalysis",
    "ContentOptimization"
] 