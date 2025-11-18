"""
Aplicación principal FastAPI para la comunidad Lovable (modularizado)

Sistema de comunidad estilo Lovable donde los usuarios pueden:
- Publicar sus chats
- Remixar chats de otros usuarios
- Votar y rankear contenido
- Descubrir los mejores chats

Incluye optimizaciones, middleware, y mejor configuración.
Estructura modular para mejor mantenibilidad y escalabilidad.
"""

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from .core import lifespan
from .api.router import router
from .config import settings
from .middleware.error_handler import ErrorHandlerMiddleware
from .utils.logging_config import (
    setup_logging,
    StructuredLogger,
    PerformanceLogger
)

# Configurar logging estructurado
setup_logging(
    level=settings.log_level,
    use_structlog=settings.use_structlog,
    json_output=settings.json_logs
)

logger = StructuredLogger(__name__)
performance_logger = PerformanceLogger()


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para comunidad de chats estilo Lovable con sistema de ranking, remixes y votación",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=ORJSONResponse,  # Usar ORJSON para mejor rendimiento
    debug=settings.debug
)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Middleware de manejo de errores (debe ir después de CORS)
app.add_middleware(ErrorHandlerMiddleware)

# Middleware de logging de requests con métricas
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging estructurado de requests con métricas"""
    start_time = time.time()
    
    # Obtener user_id si está disponible
    user_id = request.headers.get("X-User-ID") or request.query_params.get("user_id")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log con structured logger
        performance_logger.log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=process_time,
            user_id=user_id,
            query_params=dict(request.query_params) if request.query_params else None
        )
        
        # Agregar headers de métricas
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "Request failed",
            method=request.method,
            path=request.url.path,
            duration=process_time,
            user_id=user_id,
            error=str(e)
        )
        raise

# Incluir router
app.include_router(router)

# Endpoints adicionales de utilidad
@app.get(
    "/",
    tags=["health"],
    summary="Root endpoint",
    description="Endpoint raíz que devuelve información básica de la API"
)
async def root():
    """
    Endpoint raíz de la API (optimizado).
    
    Returns:
        Diccionario con información básica de la API
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Verifica el estado de salud de la API y la base de datos"
)
async def health_check():
    """
    Health check endpoint (modularizado).
    
    Verifica:
    - Estado de la aplicación
    - Conexión a la base de datos
    - Versión de la API
    
    Returns:
        HealthCheckResponse con el estado del sistema
    """
    from .schemas import HealthCheckResponse
    from .core import get_database_manager
    
    db_manager = get_database_manager()
    health_result = db_manager.health_check()
    
    database_status = "connected" if health_result.get("connected") else "disconnected"
    app_status = health_result.get("status", "unhealthy")
    
    return HealthCheckResponse(
        status=app_status,
        version=settings.app_version,
        database=database_status
    )


@app.get(
    "/info",
    tags=["info"],
    summary="API Information",
    description="Obtiene información detallada sobre la API"
)
async def api_info():
    """
    Información detallada de la API (optimizado).
    
    Returns:
        Diccionario con información completa de la API
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "API para comunidad de chats estilo Lovable con sistema de ranking, remixes y votación",
        "features": [
            "Publicar chats",
            "Remixar chats",
            "Sistema de votación",
            "Ranking inteligente",
            "Búsqueda avanzada",
            "Analytics",
            "Perfiles de usuario",
            "Chats trending",
            "Operaciones en lote"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "info": "/info"
        },
        "database": {
            "type": "sqlite" if "sqlite" in settings.database_url else "other",
            "echo": settings.database_echo
        },
        "settings": {
            "debug": settings.debug,
            "cors_enabled": True,
            "rate_limit_enabled": settings.rate_limit_enabled
        }
    }

logger.info(
    "Application created successfully",
    app_name=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)


if __name__ == "__main__":
    import uvicorn
    
    # Configurar uvicorn con optimizaciones
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="debug" if settings.debug else "info",
        access_log=True,
        reload=settings.debug  # Auto-reload en modo debug
    )

