"""
Optimized Copywriting Core Module.

High-performance copywriting service with advanced optimization libraries.
"""

from .config import OptimizedCopywritingConfig
from .service import OptimizedCopywritingService
from .cache import CacheManager
from .metrics import MetricsCollector
from .validators import FastValidator

__version__ = "2.0.0"
__all__ = [
    "OptimizedCopywritingConfig",
    "OptimizedCopywritingService", 
    "CacheManager",
    "MetricsCollector",
    "FastValidator"
] 