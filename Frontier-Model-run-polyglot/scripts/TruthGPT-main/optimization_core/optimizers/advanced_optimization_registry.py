"""
Backward-compatibility shim for advanced_optimization_registry.
This module has been moved to optimization_core.optimizers.registries.advanced_optimization_registry.
"""

import warnings
from .registries.advanced_optimization_registry import (
    AdvancedOptimizationConfig,
    get_advanced_optimizations,
    OPTIMIZATION_CONFIGS,
    get_advanced_optimization_config,
    apply_advanced_optimizations,
    get_advanced_optimization_report
)

warnings.warn(
    "optimization_core.optimizers.advanced_optimization_registry is deprecated. "
    "Please use optimization_core.optimizers.registries.advanced_optimization_registry instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    'AdvancedOptimizationConfig',
    'get_advanced_optimizations',
    'OPTIMIZATION_CONFIGS',
    'get_advanced_optimization_config',
    'apply_advanced_optimizations',
    'get_advanced_optimization_report'
]
