"""
Backward-compatibility shim for advanced_optimization_registry_v2.
This module has been moved to optimization_core.optimizers.registries.advanced_optimization_registry_v2.
"""

import warnings
from .registries.advanced_optimization_registry_v2 import (
    AdvancedOptimizationConfig,
    ADVANCED_OPTIMIZATION_CONFIGS,
    get_advanced_optimization_config,
    apply_advanced_optimizations,
    get_advanced_optimization_report
)

warnings.warn(
    "optimization_core.optimizers.advanced_optimization_registry_v2 is deprecated. "
    "Please use optimization_core.optimizers.registries.advanced_optimization_registry_v2 instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    'AdvancedOptimizationConfig',
    'ADVANCED_OPTIMIZATION_CONFIGS',
    'get_advanced_optimization_config',
    'apply_advanced_optimizations',
    'get_advanced_optimization_report'
]
