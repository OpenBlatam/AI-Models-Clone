"""
Backward-compatibility shim for triton_optimizations.
This module has been moved to optimization_core.optimizers.techniques.triton_optimizations.
"""

import warnings
from .techniques.triton_optimizations import (
    TritonOptimizations,
    TritonLayerNorm,
    TritonLayerNormModule,
    rotary_embed,
    block_copy
)

warnings.warn(
    "optimization_core.optimizers.triton_optimizations is deprecated. "
    "Please use optimization_core.optimizers.techniques.triton_optimizations instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    'TritonOptimizations',
    'TritonLayerNorm',
    'TritonLayerNormModule',
    'rotary_embed',
    'block_copy',
]
