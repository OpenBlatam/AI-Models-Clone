"""
API package for Enhanced Blaze AI.

This package contains the API routes and middleware components.
"""

from .routes import create_api_router
from .middleware import create_middleware_stack

__all__ = ["create_api_router", "create_middleware_stack"]