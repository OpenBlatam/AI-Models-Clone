from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .landing_page_models import (
from .ai_models import (
from .analytics_models import (
from .nlp_models import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Models Module - Modelos de Datos y Esquemas
==========================================

Este módulo contiene todos los modelos Pydantic y esquemas de datos:
- LandingPageModel: Modelo principal de landing page
- AIModels: Modelos relacionados con IA
- AnalyticsModels: Modelos de analytics
- NLPModels: Modelos de procesamiento de lenguaje natural
"""

    LandingPageModel,
    OptimizationResult,
    ContentModel,
    SEOModel
)

    ConversionPrediction,
    CompetitorAnalysis,
    PersonalizationProfile
)

    RealTimeMetric,
    UserJourney,
    ConversionFunnel
)

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