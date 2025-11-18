"""
Health check endpoint para la comunidad Lovable

Proporciona información sobre el estado de la aplicación.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..dependencies import get_db
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["health"]
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Verifica el estado de la aplicación y la base de datos"
)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint (optimizado).
    
    Verifica:
    - Estado de la aplicación
    - Conexión a la base de datos
    - Versión de la aplicación
    
    Returns:
        Diccionario con información de salud
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "app_name": settings.app_name,
        "checks": {
            "database": "unknown"
        }
    }
    
    # Verificar conexión a base de datos
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}", exc_info=True)
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = "disconnected"
        health_status["error"] = str(e)
    
    return health_status


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Verifica si la aplicación está lista para recibir tráfico"
)
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check endpoint.
    
    Verifica que todos los servicios estén listos.
    
    Returns:
        Diccionario con estado de readiness
    """
    ready = True
    checks = {}
    
    # Verificar base de datos
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ready"
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}", exc_info=True)
        checks["database"] = "not_ready"
        ready = False
    
    if not ready:
        return {
            "ready": False,
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }, status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "ready": True,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }

