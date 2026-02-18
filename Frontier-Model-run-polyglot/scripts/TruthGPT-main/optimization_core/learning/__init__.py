"""
Learning Module Compatibility Shim
==================================

Redirects imports to `optimization_core.modules.learning`.
PLEASE UPDATE IMPORTS TO USE `optimization_core.modules.learning` DIRECTLY.
"""

from optimization_core.modules.learning import *  # noqa: F403
from optimization_core.modules.learning import __all__

# Re-export for wildcard imports
__all__ = __all__
