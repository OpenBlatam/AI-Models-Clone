"""
API Package
==========

FastAPI application and API endpoints for the copywriting system.
"""

from .app import create_app, get_app
from .routes import router as api_router

__all__ = [
    "create_app",
    "get_app", 
    "api_router"
] 