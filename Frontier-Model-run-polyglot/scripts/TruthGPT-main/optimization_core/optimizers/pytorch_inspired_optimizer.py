"""
Backward-compatibility shim for pytorch_inspired_optimizer.
Redirects to the new UnifiedOptimizer architecture.
"""

import warnings
from .core.unified_optimizer import UnifiedOptimizer
from .core.base_truthgpt_optimizer import OptimizationLevel

warnings.warn(
    "pytorch_inspired_optimizer is deprecated. Use UnifiedOptimizer instead.",
    DeprecationWarning,
    stacklevel=2
)

class PyTorchInspiredOptimizer(UnifiedOptimizer):
    """PyTorch-inspired optimizer (Shim)."""
    def __init__(self, level=OptimizationLevel.ADVANCED, config=None):
        super().__init__(level=level, config=config)

def create_pytorch_optimizer(config=None):
    """Factory function (Shim)."""
    return PyTorchInspiredOptimizer(config=config)

__all__ = ['PyTorchInspiredOptimizer', 'create_pytorch_optimizer']
