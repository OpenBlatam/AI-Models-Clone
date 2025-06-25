"""
Routes Registration - Centralized Route Management.

Modular route registration system that organizes endpoints
by functionality and provides clean separation of concerns.
"""

from fastapi import FastAPI
import structlog

logger = structlog.get_logger(__name__)


def register_health_routes(app: FastAPI):
    """Register health and monitoring routes."""
    from ..api.health import router as health_router
    app.include_router(health_router, prefix="", tags=["health"])


def register_optimization_routes(app: FastAPI):
    """Register optimization API routes."""
    from ..api.optimization import router as optimization_router
    app.include_router(optimization_router, prefix="/api/v2/optimize", tags=["optimization"])


def register_network_routes(app: FastAPI):
    """Register network optimization routes."""
    try:
        from ..api.network import router as network_router
        app.include_router(network_router, prefix="/api/v2/network", tags=["network"])
    except ImportError:
        logger.warning("Network routes not available - optimizer not installed")


def register_ml_routes(app: FastAPI):
    """Register machine learning routes."""
    try:
        from ..api.ml import router as ml_router
        app.include_router(ml_router, prefix="/api/v2/ml", tags=["machine_learning"])
    except ImportError:
        logger.warning("ML routes not available - optimizer not installed")


def register_admin_routes(app: FastAPI):
    """Register administrative routes."""
    from ..api.admin import router as admin_router
    app.include_router(admin_router, prefix="/admin", tags=["admin"])


def register_all_routes(app: FastAPI):
    """Register all application routes."""
    routes_registered = []
    
    try:
        register_health_routes(app)
        routes_registered.append("health")
    except Exception as e:
        logger.error("Failed to register health routes", error=str(e))
    
    try:
        register_optimization_routes(app)
        routes_registered.append("optimization")
    except Exception as e:
        logger.error("Failed to register optimization routes", error=str(e))
    
    try:
        register_network_routes(app)
        routes_registered.append("network")
    except Exception as e:
        logger.warning("Network routes registration failed", error=str(e))
    
    try:
        register_ml_routes(app)
        routes_registered.append("ml")
    except Exception as e:
        logger.warning("ML routes registration failed", error=str(e))
    
    try:
        register_admin_routes(app)
        routes_registered.append("admin")
    except Exception as e:
        logger.error("Failed to register admin routes", error=str(e))
    
    logger.info("📍 Routes registered", 
               count=len(routes_registered),
               routes=routes_registered)


__all__ = ['register_all_routes'] 