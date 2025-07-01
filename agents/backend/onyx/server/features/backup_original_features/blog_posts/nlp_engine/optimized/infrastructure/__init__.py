"""
🔧 INFRASTRUCTURE - External Concerns
=====================================

Capa de infraestructura con adaptadores y implementaciones externas.
"""

from .optimization.adapters import UltraOptimizerAdapter, ExtremeOptimizerAdapter
from .caching.adapters import MemoryCacheAdapter, OptimizedCacheAdapter

__all__ = [
    'UltraOptimizerAdapter',
    'ExtremeOptimizerAdapter',
    'MemoryCacheAdapter',
    'OptimizedCacheAdapter'
] 