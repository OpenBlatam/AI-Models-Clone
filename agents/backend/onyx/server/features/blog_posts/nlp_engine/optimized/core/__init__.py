"""
🎯 CORE - Domain Layer
======================

Capa de dominio con entidades e interfaces del sistema NLP.
"""

from .entities.models import (
    TextInput,
    AnalysisResult,
    BatchResult,
    AnalysisType,
    OptimizationTier,
    PerformanceMetrics
)

from .interfaces.contracts import (
    IOptimizer,
    ICache,
    INLPAnalyzer
)

__all__ = [
    # Entities
    'TextInput',
    'AnalysisResult', 
    'BatchResult',
    'AnalysisType',
    'OptimizationTier',
    'PerformanceMetrics',
    
    # Interfaces
    'IOptimizer',
    'ICache',
    'INLPAnalyzer'
] 