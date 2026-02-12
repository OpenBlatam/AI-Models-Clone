"""
Backward-compatibility shim for enhanced_parameter_optimizer.
Redirects to the new UnifiedOptimizer architecture.
"""

import warnings
from .core.unified_optimizer import UnifiedOptimizer
from .core.base_truthgpt_optimizer import OptimizationLevel

warnings.warn(
    "enhanced_parameter_optimizer is deprecated. Use UnifiedOptimizer instead.",
    DeprecationWarning,
    stacklevel=2
)

class EnhancedParameterOptimizer(UnifiedOptimizer):
    """Enhanced parameter optimizer (Shim)."""
    def __init__(self, level=OptimizationLevel.ADVANCED, config=None):
        super().__init__(level=level, config=config)

def create_enhanced_parameter_optimizer(config=None):
    """Factory function (Shim)."""
    return EnhancedParameterOptimizer(config=config)

__all__ = ['EnhancedParameterOptimizer', 'create_enhanced_parameter_optimizer']
