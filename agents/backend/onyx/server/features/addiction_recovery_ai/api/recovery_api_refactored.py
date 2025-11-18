"""
API endpoints refactorizados - Ejemplo de integración de nuevas rutas
Este archivo muestra cómo integrar las nuevas rutas modulares
"""

from fastapi import APIRouter

try:
    from api.routes import (
        assessment_router,
        progress_router,
        relapse_router,
        support_router,
        analytics_router,
        notifications_router,
        users_router,
        gamification_router,
        emergency_router
    )
except ImportError:
    from .routes import (
        assessment_router,
        progress_router,
        relapse_router,
        support_router,
        analytics_router,
        notifications_router,
        users_router,
        gamification_router,
        emergency_router
    )

# Crear router principal
router = APIRouter()

# Incluir routers modulares
router.include_router(assessment_router)
router.include_router(progress_router)
router.include_router(relapse_router)
router.include_router(support_router)
router.include_router(analytics_router)
router.include_router(notifications_router)
router.include_router(users_router)
router.include_router(gamification_router)
router.include_router(emergency_router)

# Nota: Este router puede incluirse en main.py junto con recovery_api.py
# para una migración gradual. Una vez que todos los endpoints estén migrados,
# se puede reemplazar recovery_api.py completamente.

