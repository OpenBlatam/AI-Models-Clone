"""
Document routes following functional patterns and RORO
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.errors import handle_validation_error, handle_not_found_error, handle_internal_error
from app.schemas.user import User
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse,
    DocumentVersionResponse, DocumentCommentResponse,
    DocumentShareResponse
)
from app.services.document_service import (
    create_document, get_document, update_document, delete_document,
    list_documents, get_document_versions, add_document_comment,
    share_document
)
from app.utils.validators import validate_pagination
from app.utils.rate_limiter import rate_limit_document_creation, rate_limit_document_update

router = APIRouter()


async def create_document_endpoint(
    document_data: DocumentCreate,
    user: User,
    db: AsyncSession
) -> DocumentResponse:
    """Create a new document."""
    return await create_document(document_data, user.id, db)


async def get_document_endpoint(
    document_id: str,
    user: User,
    db: AsyncSession
) -> DocumentResponse:
    """Get document by ID."""
    return await get_document(document_id, user.id, db)


async def update_document_endpoint(
    document_id: str,
    update_data: DocumentUpdate,
    user: User,
    db: AsyncSession
) -> DocumentResponse:
    """Update document."""
    return await update_document(document_id, update_data, user.id, db)


async def delete_document_endpoint(
    document_id: str,
    user: User,
    db: AsyncSession
) -> Dict[str, str]:
    """Delete document."""
    return await delete_document(document_id, user.id, db)


async def list_documents_endpoint(
    user: User,
    organization_id: Optional[str] = None,
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    search_query: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """List documents with filtering and pagination."""
    # Validate pagination
    pagination_validation = validate_pagination(page, size)
    if not pagination_validation["is_valid"]:
        raise handle_validation_error(
            ValueError(f"Invalid pagination: {', '.join(pagination_validation['errors'])}")
        )
    
    return await list_documents(
        user.id, organization_id, status, document_type,
        search_query, page, size, db
    )


async def get_document_versions_endpoint(
    document_id: str,
    user: User,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get document versions."""
    # Validate pagination
    pagination_validation = validate_pagination(page, size)
    if not pagination_validation["is_valid"]:
        raise handle_validation_error(
            ValueError(f"Invalid pagination: {', '.join(pagination_validation['errors'])}")
        )
    
    return await get_document_versions(document_id, user.id, page, size, db)


async def add_document_comment_endpoint(
    document_id: str,
    comment_data: Dict[str, Any],
    user: User,
    db: AsyncSession
) -> DocumentCommentResponse:
    """Add comment to document."""
    return await add_document_comment(document_id, user.id, comment_data, db)


async def share_document_endpoint(
    document_id: str,
    share_data: Dict[str, Any],
    user: User,
    db: AsyncSession
) -> DocumentShareResponse:
    """Share document with user or organization."""
    return await share_document(document_id, user.id, share_data, db)


# Route definitions
@router.post("/", response_model=DocumentResponse)
@rate_limit_document_creation(key_func=lambda user, **kwargs: f"user:{user.id}")
async def create_document_route(
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """Create a new document."""
    return await create_document_endpoint(document_data, current_user, db)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_route(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """Get document by ID."""
    return await get_document_endpoint(document_id, current_user, db)


@router.put("/{document_id}", response_model=DocumentResponse)
@rate_limit_document_update(key_func=lambda user, **kwargs: f"user:{user.id}")
async def update_document_route(
    document_id: str,
    update_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """Update document."""
    return await update_document_endpoint(document_id, update_data, current_user, db)


@router.delete("/{document_id}")
async def delete_document_route(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Delete document."""
    return await delete_document_endpoint(document_id, current_user, db)


@router.get("/", response_model=Dict[str, Any])
async def list_documents_route(
    organization_id: Optional[str] = Query(None, description="Filter by organization ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    search_query: Optional[str] = Query(None, description="Search in title, description, and content"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """List documents with filtering and pagination."""
    return await list_documents_endpoint(
        current_user, organization_id, status, document_type,
        search_query, page, size, db
    )


@router.get("/{document_id}/versions", response_model=Dict[str, Any])
async def get_document_versions_route(
    document_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get document versions."""
    return await get_document_versions_endpoint(document_id, current_user, page, size, db)


@router.post("/{document_id}/comments", response_model=DocumentCommentResponse)
async def add_document_comment_route(
    document_id: str,
    comment_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentCommentResponse:
    """Add comment to document."""
    return await add_document_comment_endpoint(document_id, comment_data, current_user, db)


@router.post("/{document_id}/share", response_model=DocumentShareResponse)
async def share_document_route(
    document_id: str,
    share_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentShareResponse:
    """Share document with user or organization."""
    return await share_document_endpoint(document_id, share_data, current_user, db)


@router.get("/{document_id}/comments", response_model=List[DocumentCommentResponse])
async def get_document_comments_route(
    document_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[DocumentCommentResponse]:
    """Get document comments."""
    # This would be implemented in document_service.py
    # For now, returning empty list
    return []


@router.get("/{document_id}/shares", response_model=List[DocumentShareResponse])
async def get_document_shares_route(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[DocumentShareResponse]:
    """Get document shares."""
    # This would be implemented in document_service.py
    # For now, returning empty list
    return []


@router.post("/{document_id}/duplicate", response_model=DocumentResponse)
async def duplicate_document_route(
    document_id: str,
    new_title: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """Duplicate a document."""
    # Get original document
    original_doc = await get_document_endpoint(document_id, current_user, db)
    
    # Create duplicate
    duplicate_data = DocumentCreate(
        title=new_title or f"Copy of {original_doc.title}",
        description=original_doc.description,
        content=original_doc.content,
        document_type=original_doc.document_type,
        organization_id=original_doc.organization_id,
        is_public=False,  # Duplicates are private by default
        allow_comments=original_doc.allow_comments,
        allow_editing=original_doc.allow_editing,
        allow_sharing=original_doc.allow_sharing,
        tags=original_doc.tags,
        metadata=original_doc.metadata
    )
    
    return await create_document_endpoint(duplicate_data, current_user, db)


@router.post("/{document_id}/export")
async def export_document_route(
    document_id: str,
    format: str = Query("pdf", description="Export format (pdf, docx, txt, md)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Export document in specified format."""
    # Get document
    document = await get_document_endpoint(document_id, current_user, db)
    
    # This would implement actual export logic
    # For now, returning a placeholder response
    return {
        "document_id": document_id,
        "format": format,
        "download_url": f"/api/v1/documents/{document_id}/download/{format}",
        "expires_at": "2023-12-31T23:59:59Z"
    }


@router.get("/{document_id}/analytics", response_model=Dict[str, Any])
async def get_document_analytics_route(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get document analytics."""
    # Get document
    document = await get_document_endpoint(document_id, current_user, db)
    
    # This would implement actual analytics logic
    # For now, returning placeholder data
    return {
        "document_id": document_id,
        "view_count": document.view_count,
        "edit_count": document.edit_count,
        "share_count": document.share_count,
        "last_viewed": document.updated_at.isoformat(),
        "collaborators": [],
        "activity_summary": {
            "views_today": 0,
            "edits_today": 0,
            "shares_today": 0
        }
    }




