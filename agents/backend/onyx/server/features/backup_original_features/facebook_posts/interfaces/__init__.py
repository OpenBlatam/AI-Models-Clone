"""
🎯 Facebook Posts - Interfaces & Contracts
==========================================

Definición de interfaces, protocolos y contratos para Clean Architecture.
"""

from .repositories import (
    FacebookPostRepository,
    AnalysisRepository,
    CacheRepository
)

from .services import (
    ContentGeneratorInterface,
    ContentAnalyzerInterface,
    LangChainServiceInterface,
    NotificationServiceInterface
)

from .external import (
    FacebookAPIInterface,
    OnySIntegrationInterface,
    AIModelInterface
)

__all__ = [
    # Repository interfaces
    "FacebookPostRepository",
    "AnalysisRepository", 
    "CacheRepository",
    
    # Service interfaces
    "ContentGeneratorInterface",
    "ContentAnalyzerInterface",
    "LangChainServiceInterface",
    "NotificationServiceInterface",
    
    # External interfaces
    "FacebookAPIInterface",
    "OnySIntegrationInterface",
    "AIModelInterface"
] 