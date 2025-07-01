"""
Refactored Copywriting Module
============================

A high-performance, modular copywriting service with intelligent optimization,
multi-language support, and seamless Onyx integration.

Features:
- Multi-language copywriting (19+ languages)
- Multiple tones and use cases (20+ tones, 25+ use cases)
- Intelligent optimization with graceful fallbacks
- Advanced caching and performance monitoring
- LangChain + OpenRouter integration
- Production-ready with comprehensive error handling
"""

from .config import CopywritingConfig
from .models import CopywritingRequest, CopywritingResponse, GenerationMetrics
from .service import CopywritingService
from .optimization import OptimizationManager
from .cache import CacheManager
from .monitoring import MetricsCollector
from .api import create_app

__version__ = "2.0.0"
__author__ = "Blatam Academy"

__all__ = [
    "CopywritingConfig",
    "CopywritingRequest", 
    "CopywritingResponse",
    "GenerationMetrics",
    "CopywritingService",
    "OptimizationManager",
    "CacheManager",
    "MetricsCollector",
    "create_app"
] 