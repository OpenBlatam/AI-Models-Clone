"""
Backward compatibility shim for TransformerOptimizer.
Deprecated: Import from optimizers.transformer instead.
"""

import warnings
from .transformer import TransformerOptimizer

# Emit deprecation warning on import
warnings.warn(
    "Importing TransformerOptimizer from 'optimizers' is deprecated. "
    "Please use 'from optimizers.transformer import TransformerOptimizer' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['TransformerOptimizer']
