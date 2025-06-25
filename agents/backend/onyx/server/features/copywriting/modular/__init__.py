"""
Modular Copywriting Service Package.

Clean, modular architecture for production copywriting service:
- Separated concerns (config, service, cache, models)
- Easy to test and maintain
- Optimized for performance
- Production-ready
"""

from .config import ModularConfig, get_config
from .service import ModularCopywritingService, get_service
from .cache import CacheManager, get_cache_manager
from .optimization import OptimizationDetector, get_optimization_level
from .api import create_api_router

__version__ = "1.0.0"
__all__ = [
    "ModularConfig",
    "ModularCopywritingService", 
    "CacheManager",
    "OptimizationDetector",
    "get_config",
    "get_service",
    "get_cache_manager",
    "get_optimization_level",
    "create_api_router"
] 