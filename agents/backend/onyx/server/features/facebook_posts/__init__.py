"""
🎯 Facebook Posts Feature for Onyx
==================================

Sistema avanzado de análisis y generación de Facebook posts integrado con LangChain.

Funcionalidades principales:
- Generación inteligente de contenido con LangChain
- Análisis de engagement y viralidad
- Optimización automática para Facebook
- Integración completa con Onyx backend
- Support para multimedia y scheduling
"""

__version__ = "1.0.0"
__author__ = "Onyx Facebook Posts Team"

from .core.facebook_engine import FacebookPostEngine
from .models.facebook_models import FacebookPost, FacebookAnalysis, FacebookRequest
from .services.langchain_service import FacebookLangChainService
from .api.facebook_api import router as facebook_router

__all__ = [
    "FacebookPostEngine",
    "FacebookPost", 
    "FacebookAnalysis",
    "FacebookRequest",
    "FacebookLangChainService",
    "facebook_router"
] 