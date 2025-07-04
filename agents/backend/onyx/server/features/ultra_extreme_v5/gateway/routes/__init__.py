"""
🚀 ULTRA-EXTREME V5 - ROUTES PACKAGE
====================================

Ultra-extreme API routes package with:
- Content management routes
- AI optimization routes
- Health monitoring routes
- Service discovery routes
- Performance monitoring routes
"""

from .content_routes import content_router
from .optimization_routes import optimization_router
from .ai_routes import ai_router
from .health_routes import health_router

__all__ = [
    "content_router",
    "optimization_router", 
    "ai_router",
    "health_router"
] 