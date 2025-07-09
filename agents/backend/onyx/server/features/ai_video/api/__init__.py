"""
APIS, SERVICIOS WEB Y ENDPOINTS
==============================

APIs, servicios web y endpoints

Estructura del módulo:
- fastapi_microservice.py: Microservicio FastAPI principal
- services.py: Servicios web y lógica de negocio
- utils_api.py: Utilidades para APIs
- utils_batch.py: Utilidades para procesamiento por lotes
- aws_lambda_handler.py: Handler para AWS Lambda
"""

# Importaciones automáticas
import os
from pathlib import Path

# Metadata del módulo
__module_name__ = "api"
__description__ = "APIs, servicios web y endpoints"
__version__ = "1.0.0"

# Path del módulo
MODULE_PATH = Path(__file__).parent

# Auto-discovery de archivos Python
__all__ = []
for file_path in MODULE_PATH.glob("*.py"):
    if file_path.name != "__init__.py":
        module_name = file_path.stem
        __all__.append(module_name)

def get_module_info():
    """Obtener información del módulo."""
    return {
        "name": __module_name__,
        "description": __description__,
        "version": __version__,
        "path": str(MODULE_PATH),
        "files": __all__
    }

def list_files():
    """Listar archivos en el módulo."""
    return [f.name for f in MODULE_PATH.glob("*.py")]

# Importaciones principales para facilitar el uso
try:
    from . import fastapi_microservice
    from . import services
    from . import utils_api
    from . import utils_batch
    from . import aws_lambda_handler
except ImportError as e:
    import logging
    logging.warning(f"No se pudieron importar algunos módulos de API: {e}")

"""
AI Video API Module
==================

FastAPI-based API for AI video generation with latest best practices.
"""

from .fastapi_app import app
from .models import (
    VideoGenerationRequest, VideoGenerationResponse, JobStatusResponse,
    BatchGenerationRequest, BatchGenerationResponse, HealthCheckResponse,
    MetricsResponse, UserQuota, ModelConfig, APIError, VideoMetadata,
    JobStatus, VideoFormat, QualityLevel
)
from .dependencies import (
    get_current_user, check_rate_limit, check_quota, increment_quota,
    get_cached_result, get_health_status, get_metrics, RateLimiter,
    QuotaManager, CacheManager, AuthManager
)
from .middleware import (
    RequestLoggingMiddleware, MetricsMiddleware, RateLimitMiddleware,
    CacheMiddleware, SecurityMiddleware, PerformanceMiddleware,
    create_middleware_stack
)
from .routes import (
    api_router, health_router, admin_router
)

# Quick start function
def create_app():
    """Create and configure FastAPI application."""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    # Create app
    app = FastAPI(
        title="AI Video Generation API",
        description="Scalable API for AI video generation using latest technologies",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add middleware
    app = create_middleware_stack(app)
    
    # Include routers
    app.include_router(api_router)
    app.include_router(health_router)
    app.include_router(admin_router)
    
    return app

# Example usage
def run_example():
    """Run example API server."""
    import uvicorn
    
    app = create_app()
    
    print("Starting AI Video API server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )

# Export main components
__all__ = [
    # Main app
    "app",
    "create_app",
    "run_example",
    
    # Models
    "VideoGenerationRequest",
    "VideoGenerationResponse", 
    "JobStatusResponse",
    "BatchGenerationRequest",
    "BatchGenerationResponse",
    "HealthCheckResponse",
    "MetricsResponse",
    "UserQuota",
    "ModelConfig",
    "APIError",
    "VideoMetadata",
    "JobStatus",
    "VideoFormat",
    "QualityLevel",
    
    # Dependencies
    "get_current_user",
    "check_rate_limit",
    "check_quota",
    "increment_quota",
    "get_cached_result",
    "get_health_status",
    "get_metrics",
    "RateLimiter",
    "QuotaManager",
    "CacheManager",
    "AuthManager",
    
    # Middleware
    "RequestLoggingMiddleware",
    "MetricsMiddleware",
    "RateLimitMiddleware",
    "CacheMiddleware",
    "SecurityMiddleware",
    "PerformanceMiddleware",
    "create_middleware_stack",
    
    # Routers
    "api_router",
    "health_router",
    "admin_router"
] 