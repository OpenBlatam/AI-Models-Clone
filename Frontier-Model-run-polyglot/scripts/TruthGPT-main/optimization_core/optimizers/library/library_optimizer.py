"""
Backward-compatibility shim for library_optimizer.
Redirects to the new UnifiedOptimizer architecture.
"""

import warnings
from typing import Optional, Dict, Any

try:
    from ...core.unified_optimizer import UnifiedOptimizer
    from ...core.base_truthgpt_optimizer import OptimizationLevel
except (ImportError, ValueError):
    try:
        from core.unified_optimizer import UnifiedOptimizer
        from core.base_truthgpt_optimizer import OptimizationLevel
    except ImportError:
        # Fallback for absolute imports
        from optimization_core.optimizers.core.unified_optimizer import UnifiedOptimizer
        from optimization_core.optimizers.core.base_truthgpt_optimizer import OptimizationLevel

warnings.warn(
    "library_optimizer is deprecated. Use UnifiedOptimizer instead.",
    DeprecationWarning,
    stacklevel=2
)

class LibraryOptimizer(UnifiedOptimizer):
    """Library-centric optimizer (Shim)."""
    def __init__(
        self, 
        level: OptimizationLevel = OptimizationLevel.BASIC, 
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(level=level, config=config)

def create_library_optimizer(config: Optional[Dict[str, Any]] = None) -> LibraryOptimizer:
    """Factory function (Shim)."""
    return LibraryOptimizer(config=config)

__all__ = ['LibraryOptimizer', 'create_library_optimizer']
