"""
Router principal para la API de canciones Suno Clone AI

Este módulo actúa como punto de entrada principal que importa y registra
todos los routers modulares especializados siguiendo el patrón de arquitectura
modular y separación de responsabilidades.

Estructura Modular:
===================

1. Generación y Procesamiento:
   - routes/generation.py - Generación de canciones desde prompts y chat
   - routes/audio_processing.py - Edición, mezcla y análisis de audio

2. Gestión de Contenido:
   - routes/songs.py - CRUD básico de canciones (optimizado con cache)
   - routes/tags.py - Sistema de tags y etiquetas
   - routes/comments.py - Sistema de comentarios
   - routes/favorites.py - Favoritos y sistema de ratings
   - routes/playlists.py - Gestión de playlists

3. Descubrimiento y Recomendaciones:
   - routes/search.py - Búsqueda avanzada con múltiples filtros
   - routes/recommendations.py - Sistema de recomendaciones inteligentes

4. Social y Compartición:
   - routes/sharing.py - Enlaces de compartición con expiración
   - routes/stats.py - Estadísticas avanzadas y rankings

5. Administración y Monitoreo:
   - routes/metrics.py - Métricas del sistema y rendimiento
   - routes/models.py - Gestión de modelos y caché
   - routes/export.py - Exportación de metadatos (JSON/XML/CSV)
   - routes/health.py - Health checks (liveness, readiness)

6. Comunicación:
   - routes/chat.py - Historial de conversaciones

Características Principales:
============================

- Arquitectura Modular: Cada funcionalidad en su propio módulo
- Optimización: Caching, lazy loading, async operations
- Validación Robusta: Validación de UUIDs, tipos y rangos
- Manejo de Errores: Errores específicos y mensajes claros
- Documentación: Docstrings completos con ejemplos
- Escalabilidad: Diseñado para crecer sin acoplamiento

Versión de API: v1.0.0
Última actualización: 2024
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter

from .routes import (
    generation,
    songs,
    audio_processing,
    tags,
    comments,
    recommendations,
    favorites,
    export,
    search,
    playlists,
    sharing,
    stats,
    metrics,
    models,
    chat,
    health,
    performance
)

logger = logging.getLogger(__name__)

# Router principal
router = APIRouter(
    prefix="/suno",
    tags=["suno"],
    responses={
        400: {"description": "Bad request - Parámetros inválidos"},
        401: {"description": "Unauthorized - Autenticación requerida"},
        403: {"description": "Forbidden - Sin permisos"},
        404: {"description": "Not found - Recurso no encontrado"},
        409: {"description": "Conflict - Conflicto de estado"},
        422: {"description": "Unprocessable entity - Validación fallida"},
        429: {"description": "Too many requests - Rate limit excedido"},
        500: {"description": "Internal server error - Error del servidor"},
        503: {"description": "Service unavailable - Servicio no disponible"},
        507: {"description": "Insufficient storage - Almacenamiento insuficiente"}
    }
)


# ============================================================================
# Endpoint de Información de la API
# ============================================================================

@router.get("", include_in_schema=True)
async def api_info() -> Dict[str, Any]:
    """
    Información general de la API Suno Clone AI.
    
    Proporciona información sobre versiones, endpoints disponibles,
    y estado del servicio.
    
    Returns:
        Diccionario con información de la API
    
    Example:
        ```
        GET /suno
        ```
    """
    try:
        from ..config.settings import settings
        
        return {
            "name": "Suno Clone AI API",
            "version": "1.0.0",
            "description": "API completa para generación y gestión de música con IA",
            "status": "active",
            "endpoints": {
                "generation": "/suno/generate",
                "songs": "/suno/songs",
                "search": "/suno/search",
                "health": "/suno/health",
                "metrics": "/suno/metrics",
                "models": "/suno/models",
                "performance": "/suno/performance"
            },
            "features": [
                "Generación de música con IA",
                "Procesamiento y edición de audio",
                "Sistema de búsqueda avanzada",
                "Recomendaciones inteligentes",
                "Gestión de playlists",
                "Sistema de ratings y favoritos",
                "Compartición segura",
                "Exportación de metadatos",
                "Estadísticas y métricas"
            ],
            "documentation": "/docs",
            "openapi_schema": "/openapi.json",
            "settings": {
                "default_model": settings.music_model,
                "max_audio_length": settings.max_audio_length,
                "default_duration": settings.default_duration
            }
        }
    except Exception as e:
        logger.error(f"Error getting API info: {e}", exc_info=True)
        return {
            "name": "Suno Clone AI API",
            "version": "1.0.0",
            "status": "error",
            "error": str(e)
        }


@router.get("/version")
async def get_api_version() -> Dict[str, Any]:
    """
    Obtiene la versión actual de la API.
    
    Returns:
        Información de versión
    
    Example:
        ```
        GET /suno/version
        ```
    """
    return {
        "version": "1.0.0",
        "api_version": "v1",
        "build_date": "2024",
        "compatibility": {
            "min_client_version": "1.0.0",
            "recommended_client_version": "1.0.0"
        }
    }


# ============================================================================
# Nota sobre Manejo de Errores
# ============================================================================
# Los exception handlers globales deben registrarse en la aplicación principal
# (app.py), no en el router. Este router proporciona respuestas estándar
# definidas en el parámetro 'responses' del APIRouter.
#
# Para manejo de errores personalizado, usar:
# - app.add_exception_handler() en el archivo principal de la aplicación
# - HTTPException en los endpoints individuales
# - Middleware personalizado para logging y transformación de errores


# ============================================================================
# Registrar todos los sub-routers
# ============================================================================

# Generación y procesamiento
router.include_router(generation.router)
router.include_router(audio_processing.router)

# Gestión de contenido
router.include_router(songs.router)
router.include_router(tags.router)
router.include_router(comments.router)
router.include_router(favorites.router)
router.include_router(playlists.router)

# Descubrimiento
router.include_router(search.router)
router.include_router(recommendations.router)

# Social y compartición
router.include_router(sharing.router)
router.include_router(stats.router)

# Administración
router.include_router(metrics.router)
router.include_router(models.router)
router.include_router(export.router)
router.include_router(chat.router)
router.include_router(health.router)
try:
    from .routes import (
        admin, backup, analytics, webhooks, feature_flags,
        search_advanced, recommendations, batch_processing, ab_testing,
        model_management, load_balancing, hyperparameter_tuning,
        transcription, sentiment, lyrics, distributed, scaling,
        streaming, audio_analysis, remix, karaoke,
        collaboration, marketplace, monetization, auto_dj, trends
    )
    router.include_router(admin.router)
    router.include_router(backup.router)
    router.include_router(analytics.router)
    router.include_router(webhooks.router)
    router.include_router(feature_flags.router)
    router.include_router(search_advanced.router)
    router.include_router(recommendations.router)
    router.include_router(batch_processing.router)
    router.include_router(ab_testing.router)
    router.include_router(model_management.router)
    router.include_router(load_balancing.router)
    router.include_router(hyperparameter_tuning.router)
    router.include_router(transcription.router)
    router.include_router(sentiment.router)
    router.include_router(lyrics.router)
    router.include_router(distributed.router)
    router.include_router(scaling.router)
    router.include_router(streaming.router)
    router.include_router(audio_analysis.router)
    router.include_router(remix.router)
    router.include_router(karaoke.router)
    router.include_router(collaboration.router)
    router.include_router(marketplace.router)
    router.include_router(monetization.router)
    router.include_router(auto_dj.router)
    router.include_router(trends.router)
except ImportError:
    pass

# Log de inicialización
logger.info("Suno Clone AI API router initialized with all sub-routers")

# Exportar el router principal
__all__ = ["router"]
