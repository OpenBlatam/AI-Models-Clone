"""
Search routes following functional patterns and RORO
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.errors import handle_validation_error, handle_internal_error
from app.schemas.user import User
from app.services.search_service import (
    search_documents, search_users, search_organizations,
    global_search, get_search_suggestions, get_popular_searches,
    get_recent_searches
)
from app.utils.validators import validate_pagination
from app.utils.rate_limiter import rate_limit_search

router = APIRouter()


async def search_documents_endpoint(
    query: str,
    user: User,
    filters: Optional[Dict[str, Any]] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Search documents with full-text search."""
    return await search_documents(query, user.id, filters, page, size, db)


async def search_users_endpoint(
    query: str,
    user: User,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Search users by name, username, or email."""
    return await search_users(query, user.id, page, size, db)


async def search_organizations_endpoint(
    query: str,
    user: User,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Search organizations by name or description."""
    return await search_organizations(query, user.id, page, size, db)


async def global_search_endpoint(
    query: str,
    user: User,
    search_types: List[str] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Perform global search across all content types."""
    return await global_search(query, user.id, search_types, page, size, db)


async def get_search_suggestions_endpoint(
    query: str,
    user: User,
    limit: int = 10,
    db: AsyncSession = None
) -> List[str]:
    """Get search suggestions based on query."""
    return await get_search_suggestions(query, user.id, limit, db)


async def get_popular_searches_endpoint(
    user: User,
    limit: int = 10,
    db: AsyncSession = None
) -> List[str]:
    """Get popular search queries."""
    return await get_popular_searches(user.id, limit, db)


async def get_recent_searches_endpoint(
    user: User,
    limit: int = 10,
    db: AsyncSession = None
) -> List[str]:
    """Get recent search queries for user."""
    return await get_recent_searches(user.id, limit, db)


# Route definitions
@router.get("/documents", response_model=Dict[str, Any])
@rate_limit_search(key_func=lambda user, **kwargs: f"user:{user.id}")
async def search_documents_route(
    q: str = Query(..., description="Search query"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Search documents with full-text search."""
    # Build filters
    filters = {}
    if document_type:
        filters["document_type"] = document_type
    if status:
        filters["status"] = status
    if organization_id:
        filters["organization_id"] = organization_id
    if tags:
        filters["tags"] = [tag.strip() for tag in tags.split(",")]
    
    return await search_documents_endpoint(q, current_user, filters, page, size, db)


@router.get("/users", response_model=Dict[str, Any])
@rate_limit_search(key_func=lambda user, **kwargs: f"user:{user.id}")
async def search_users_route(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Search users by name, username, or email."""
    return await search_users_endpoint(q, current_user, page, size, db)


@router.get("/organizations", response_model=Dict[str, Any])
@rate_limit_search(key_func=lambda user, **kwargs: f"user:{user.id}")
async def search_organizations_route(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Search organizations by name or description."""
    return await search_organizations_endpoint(q, current_user, page, size, db)


@router.get("/global", response_model=Dict[str, Any])
@rate_limit_search(key_func=lambda user, **kwargs: f"user:{user.id}")
async def global_search_route(
    q: str = Query(..., description="Search query"),
    types: Optional[str] = Query(None, description="Search types (comma-separated): documents,users,organizations"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Perform global search across all content types."""
    search_types = None
    if types:
        search_types = [t.strip() for t in types.split(",")]
    
    return await global_search_endpoint(q, current_user, search_types, page, size, db)


@router.get("/suggestions", response_model=List[str])
async def get_search_suggestions_route(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[str]:
    """Get search suggestions based on query."""
    return await get_search_suggestions_endpoint(q, current_user, limit, db)


@router.get("/popular", response_model=List[str])
async def get_popular_searches_route(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of popular searches"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[str]:
    """Get popular search queries."""
    return await get_popular_searches_endpoint(current_user, limit, db)


@router.get("/recent", response_model=List[str])
async def get_recent_searches_route(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recent searches"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[str]:
    """Get recent search queries for user."""
    return await get_recent_searches_endpoint(current_user, limit, db)


@router.get("/analytics", response_model=Dict[str, Any])
async def get_search_analytics_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get search analytics for user."""
    # This would implement search analytics logic
    # For now, returning placeholder data
    return {
        "total_searches": 150,
        "searches_today": 5,
        "searches_this_week": 25,
        "searches_this_month": 100,
        "most_searched_terms": [
            {"term": "AI", "count": 25},
            {"term": "documentation", "count": 20},
            {"term": "collaboration", "count": 15}
        ],
        "search_success_rate": 0.85,
        "average_results_per_search": 12.5
    }


@router.post("/save")
async def save_search_query_route(
    query: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Save a search query for later reference."""
    # This would implement search query saving logic
    # For now, returning a placeholder response
    return {"message": "Search query saved successfully"}


@router.delete("/saved/{query_id}")
async def delete_saved_search_route(
    query_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Delete a saved search query."""
    # This would implement saved search deletion logic
    # For now, returning a placeholder response
    return {"message": "Saved search deleted successfully"}


@router.get("/saved", response_model=List[Dict[str, Any]])
async def get_saved_searches_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get user's saved search queries."""
    # This would implement saved searches retrieval logic
    # For now, returning placeholder data
    return [
        {
            "id": "saved-1",
            "query": "AI document generation",
            "created_at": "2023-01-01T12:00:00Z",
            "last_used": "2023-01-15T10:30:00Z"
        },
        {
            "id": "saved-2",
            "query": "collaboration tools",
            "created_at": "2023-01-05T14:20:00Z",
            "last_used": "2023-01-20T09:15:00Z"
        }
    ]




