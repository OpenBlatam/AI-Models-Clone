"""
Main API router following functional patterns
"""
from fastapi import APIRouter

from app.api.v1.routes.ai_routes import router as ai_router
from app.api.v1.routes.collaboration_routes import router as collaboration_router
from app.api.v1.routes.document_routes import router as document_router
from app.api.v1.routes.auth_routes import router as auth_router
from app.api.v1.routes.search_routes import router as search_router
from app.api.v1.routes.analytics_routes import router as analytics_router
from app.api.v1.routes.file_routes import router as file_router
from app.api.v1.routes.workflow_routes import router as workflow_router

# Create main router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    ai_router,
    prefix="/ai",
    tags=["AI"]
)

api_router.include_router(
    document_router,
    prefix="/documents",
    tags=["Documents"]
)

api_router.include_router(
    collaboration_router,
    prefix="/collaboration",
    tags=["Collaboration"]
)

api_router.include_router(
    search_router,
    prefix="/search",
    tags=["Search"]
)

api_router.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["Analytics"]
)

api_router.include_router(
    file_router,
    prefix="/files",
    tags=["Files"]
)

api_router.include_router(
    workflow_router,
    prefix="/workflows",
    tags=["Workflows"]
)