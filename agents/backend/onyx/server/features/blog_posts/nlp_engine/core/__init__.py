"""
🎯 CORE MODULE - Domain Logic
============================

Contiene la lógica de dominio pura:
- Entities: Objetos del dominio
- Value Objects: Objetos inmutables
- Enums: Tipos y constantes
- Domain Services: Lógica de dominio
"""

from .entities import AnalysisResult, TextFingerprint, AnalysisScore, ProcessingMetrics
from .enums import AnalysisType, ProcessingTier, CacheStrategy
from .domain_services import ScoreValidator, TextProcessor

__all__ = [
    'AnalysisResult',
    'TextFingerprint',
    'AnalysisScore', 
    'ProcessingMetrics',
    'AnalysisType',
    'ProcessingTier',
    'CacheStrategy',
    'ScoreValidator',
    'TextProcessor'
] 