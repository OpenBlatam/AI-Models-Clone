"""
🎯 API MODULE - Presentation Layer
=================================

Capa de presentación para el motor NLP modular.
Incluye endpoints REST, middleware y serialización.
"""

from .routes import router, create_app
from .middleware import setup_middleware
from .serializers import AnalysisRequestSerializer, AnalysisResponseSerializer

__all__ = [
    'router',
    'create_app', 
    'setup_middleware',
    'AnalysisRequestSerializer',
    'AnalysisResponseSerializer'
] 