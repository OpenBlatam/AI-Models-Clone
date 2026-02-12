"""
Backward-compatibility shim for ai_extreme_optimizer.
Redirects to UnifiedTruthGPTOptimizer with SUPREME level.
"""

import warnings
from .core.base_truthgpt_optimizer import UnifiedTruthGPTOptimizer, OptimizationLevel

warnings.warn(
    "ai_extreme_optimizer is deprecated. Use UnifiedTruthGPTOptimizer with OptimizationLevel.SUPREME instead.",
    DeprecationWarning,
    stacklevel=2
)

class SupremeTruthGPTOptimizer(UnifiedTruthGPTOptimizer):
    """Supreme optimizer for extreme performance (Shim)."""
    def __init__(self, config=None):
        super().__init__(config=config, level=OptimizationLevel.SUPREME)

def create_extreme_optimizer(config=None):
    """Factory function for extreme optimizer (Shim)."""
    return SupremeTruthGPTOptimizer(config)

__all__ = ['SupremeTruthGPTOptimizer', 'create_extreme_optimizer']
