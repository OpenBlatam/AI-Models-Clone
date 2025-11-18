"""
Multi-Model API Feature
Optimized multi-model API with enhanced caching, circuit breakers, and health monitoring
"""

__version__ = "2.0.0"

from .api import router
from .core import (
    ModelRegistry,
    get_registry,
    EnhancedCache,
    get_cache,
    HealthMonitor,
    get_health_monitor
)

__all__ = [
    "router",
    "ModelRegistry",
    "get_registry",
    "EnhancedCache",
    "get_cache",
    "HealthMonitor",
    "get_health_monitor"
]

