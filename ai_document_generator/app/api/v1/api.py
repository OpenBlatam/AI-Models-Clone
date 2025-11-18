"""
Main API router for v1 endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    organizations,
    documents,
    ai,
    collaboration,
    analytics
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(collaboration.router, prefix="/collaboration", tags=["collaboration"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])




