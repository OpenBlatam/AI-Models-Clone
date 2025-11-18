"""
Analizador de Documentos Inteligente
=====================================

Sistema avanzado de análisis de documentos con capacidades de fine-tuning
y aprendizaje adaptativo.
"""

__version__ = "1.0.0"
__author__ = "Blatam Academy"

from .core.document_analyzer import DocumentAnalyzer
from .core.fine_tuning_model import FineTuningModel
from .api.routes import router

__all__ = [
    "DocumentAnalyzer",
    "FineTuningModel",
    "router",
]
















