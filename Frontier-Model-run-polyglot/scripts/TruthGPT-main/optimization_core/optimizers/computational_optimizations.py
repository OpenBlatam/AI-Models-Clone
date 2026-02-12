"""
Backward-compatibility shim for computational_optimizations.
This module has been moved to optimization_core.optimizers.techniques.computational_optimizations.
"""

import warnings
from .techniques.computational_optimizations import (
    FusedAttention,
    BatchOptimizer,
    ComputationalOptimizer,
    create_computational_optimizer
)

warnings.warn(
    "optimization_core.optimizers.computational_optimizations is deprecated. "
    "Please use optimization_core.optimizers.techniques.computational_optimizations instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    'FusedAttention',
    'BatchOptimizer',
    'ComputationalOptimizer',
    'create_computational_optimizer',
]
