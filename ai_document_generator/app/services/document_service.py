"""
Document service following functional patterns
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
import uuid

from app.core.logging import get_logger
from app.core.errors import handle_not_found_error, handle_conflict_error, handle_internal_error
from app.models.document import Document, DocumentVersion, DocumentComment, DocumentShare
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse,
    DocumentVersionResponse, DocumentCommentResponse,
    DocumentShareResponse
)
from app.utils.validators import validate_document_title, validate_document_content
from app.utils.helpers import create_slug, truncate_text, count_words
from app.utils.cache import cache_document_data, get_cached_document_data, invalidate_document_cache

logger = get_logger(__name__)


async def create_document(
    document_data: DocumentCreate,
    user_id: str,
    db: AsyncSession
) -> DocumentResponse:
    """Create a new document."""
    try:
        # Validate document data
        title_validation = validate_document_title(document_data.title)
        if not title_validation["is_valid"]:
            raise ValueError(f"Invalid title: {', '.join(title_validation['errors'])}")
        
        content_validation = validate_document_content(document_data.content or "")
        if not content_validation["is_valid"]:
            raise ValueError(f"Invalid content: {', '.join(content_validation['errors'])}")
        
        # Create document
        document = Document(
            title=document_data.title,
            description=document_data.description,
            content=document_data.content or "",
            document_type=document_data.document_type,
            status="draft",
            organization_id=document_data.organization_id,
            owner_id=user_id,
            is_public=document_data.is_public,
            allow_comments=document_data.allow_comments,
            allow_editing=document_data.allow_editing,
            allow_sharing=document_data.allow_sharing,
            tags=document_data.tags or [],
            metadata=document_data.metadata or {}
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        # Create initial version
        await create_document_version(
            document.id, user_id, "Initial version", document.content, db
        )
        
        # Cache document data
        cache_document_data(str(document.id), document)
        
        logger.info(f"Document created: {document.id} by user {user_id}")
        
        return DocumentResponse.from_orm(document)
    
    except ValueError as e:
        raise handle_validation_error(e)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create document: {e}")
        raise handle_internal_error(f"Failed to create document: {str(e)}")


async def get_document(
    document_id: str,
    user_id: str,
    db: AsyncSession
) -> DocumentResponse:
    """Get document by ID."""
    try:
        # Check cache first
        cached_document = get_cached_document_data(document_id)
        if cached_document:
            return DocumentResponse.from_orm(cached_document)
        
        # Get from database
        query = select(Document).where(Document.id == document_id)
        result = await db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise handle_not_found_error("Document", document_id)
        
        # Check access permissions
        has_access = await check_document_access(document, user_id, db)
        if not has_access:
            raise handle_forbidden_error("Access denied to document")
        
        # Cache document data
        cache_document_data(document_id, document)
        
        return DocumentResponse.from_orm(document)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document: {e}")
        raise handle_internal_error(f"Failed to get document: {str(e)}")


async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    user_id: str,
    db: AsyncSession
) -> DocumentResponse:
    """Update document."""
    try:
        # Get document
        query = select(Document).where(Document.id == document_id)
        result = await db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise handle_not_found_error("Document", document_id)
        
        # Check edit permissions
        can_edit = await check_document_edit_permission(document, user_id, db)
        if not can_edit:
            raise handle_forbidden_error("No edit permission for document")
        
        # Update fields
        if update_data.title is not None:
            title_validation = validate_document_title(update_data.title)
            if not title_validation["is_valid"]:
                raise ValueError(f"Invalid title: {', '.join(title_validation['errors'])}")
            document.title = update_data.title
        
        if update_data.description is not None:
            document.description = update_data.description
        
        if update_data.content is not None:
            content_validation = validate_document_content(update_data.content)
            if not content_validation["is_valid"]:
                raise ValueError(f"Invalid content: {', '.join(content_validation['errors'])}")
            
            # Create new version if content changed
            if document.content != update_data.content:
                await create_document_version(
                    document.id, user_id, "Content updated", update_data.content, db
                )
                document.content = update_data.content
                document.edit_count += 1
        
        if update_data.document_type is not None:
            document.document_type = update_data.document_type
        
        if update_data.status is not None:
            document.status = update_data.status
        
        if update_data.is_public is not None:
            document.is_public = update_data.is_public
        
        if update_data.allow_comments is not None:
            document.allow_comments = update_data.allow_comments
        
        if update_data.allow_editing is not None:
            document.allow_editing = update_data.allow_editing
        
        if update_data.allow_sharing is not None:
            document.allow_sharing = update_data.allow_sharing
        
        if update_data.tags is not None:
            document.tags = update_data.tags
        
        if update_data.metadata is not None:
            document.metadata = update_data.metadata
        
        document.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(document)
        
        # Invalidate cache
        invalidate_document_cache(document_id)
        
        logger.info(f"Document updated: {document_id} by user {user_id}")
        
        return DocumentResponse.from_orm(document)
    
    except HTTPException:
        raise
    except ValueError as e:
        raise handle_validation_error(e)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update document: {e}")
        raise handle_internal_error(f"Failed to update document: {str(e)}")


async def delete_document(
    document_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Delete document."""
    try:
        # Get document
        query = select(Document).where(Document.id == document_id)
        result = await db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise handle_not_found_error("Document", document_id)
        
        # Check delete permissions (only owner can delete)
        if document.owner_id != user_id:
            raise handle_forbidden_error("Only document owner can delete")
        
        # Soft delete
        document.is_deleted = True
        document.deleted_at = datetime.utcnow()
        document.deleted_by = user_id
        
        await db.commit()
        
        # Invalidate cache
        invalidate_document_cache(document_id)
        
        logger.info(f"Document deleted: {document_id} by user {user_id}")
        
        return {"message": "Document deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete document: {e}")
        raise handle_internal_error(f"Failed to delete document: {str(e)}")


async def list_documents(
    user_id: str,
    organization_id: Optional[str] = None,
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    search_query: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """List documents with filtering and pagination."""
    try:
        # Build query
        query = select(Document).where(Document.is_deleted == False)
        
        # Apply filters
        if organization_id:
            query = query.where(Document.organization_id == organization_id)
        
        if status:
            query = query.where(Document.status == status)
        
        if document_type:
            query = query.where(Document.document_type == document_type)
        
        if search_query:
            search_filter = or_(
                Document.title.ilike(f"%{search_query}%"),
                Document.description.ilike(f"%{search_query}%"),
                Document.content.ilike(f"%{search_query}%")
            )
            query = query.where(search_filter)
        
        # Apply access control
        access_filter = or_(
            Document.owner_id == user_id,
            Document.is_public == True,
            Document.organization_id.in_(
                select(OrganizationMember.organization_id).where(
                    OrganizationMember.user_id == user_id,
                    OrganizationMember.is_active == True
                )
            )
        )
        query = query.where(access_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(Document.updated_at)).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(query)
        documents = result.scalars().all()
        
        # Convert to response format
        document_responses = [DocumentResponse.from_orm(doc) for doc in documents]
        
        return {
            "documents": document_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise handle_internal_error(f"Failed to list documents: {str(e)}")


async def create_document_version(
    document_id: str,
    user_id: str,
    version_note: str,
    content: str,
    db: AsyncSession
) -> DocumentVersionResponse:
    """Create a new document version."""
    try:
        # Get current version number
        version_query = select(func.max(DocumentVersion.version_number)).where(
            DocumentVersion.document_id == document_id
        )
        version_result = await db.execute(version_query)
        current_version = version_result.scalar() or 0
        
        # Create new version
        version = DocumentVersion(
            document_id=document_id,
            version_number=current_version + 1,
            content=content,
            version_note=version_note,
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        db.add(version)
        await db.commit()
        await db.refresh(version)
        
        return DocumentVersionResponse.from_orm(version)
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create document version: {e}")
        raise handle_internal_error(f"Failed to create document version: {str(e)}")


async def get_document_versions(
    document_id: str,
    user_id: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get document versions."""
    try:
        # Check document access
        doc_query = select(Document).where(Document.id == document_id)
        doc_result = await db.execute(doc_query)
        document = doc_result.scalar_one_or_none()
        
        if not document:
            raise handle_not_found_error("Document", document_id)
        
        has_access = await check_document_access(document, user_id, db)
        if not has_access:
            raise handle_forbidden_error("Access denied to document")
        
        # Get versions
        query = select(DocumentVersion).where(
            DocumentVersion.document_id == document_id
        ).order_by(desc(DocumentVersion.version_number))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination
        query = query.offset((page - 1) * size).limit(size)
        
        result = await db.execute(query)
        versions = result.scalars().all()
        
        version_responses = [DocumentVersionResponse.from_orm(version) for version in versions]
        
        return {
            "versions": version_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document versions: {e}")
        raise handle_internal_error(f"Failed to get document versions: {str(e)}")


async def add_document_comment(
    document_id: str,
    user_id: str,
    comment_data: Dict[str, Any],
    db: AsyncSession
) -> DocumentCommentResponse:
    """Add comment to document."""
    try:
        # Check document access
        doc_query = select(Document).where(Document.id == document_id)
        doc_result = await db.execute(doc_query)
        document = doc_result.scalar_one_or_none()
        
        if not document:
            raise handle_not_found_error("Document", document_id)
        
        if not document.allow_comments:
            raise handle_forbidden_error("Comments not allowed on this document")
        
        has_access = await check_document_access(document, user_id, db)
        if not has_access:
            raise handle_forbidden_error("Access denied to document")
        
        # Create comment
        comment = DocumentComment(
            document_id=document_id,
            author_id=user_id,
            content=comment_data["content"],
            parent_id=comment_data.get("parent_id"),
            position=comment_data.get("position"),
            created_at=datetime.utcnow()
        )
        
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        
        return DocumentCommentResponse.from_orm(comment)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to add document comment: {e}")
        raise handle_internal_error(f"Failed to add document comment: {str(e)}")


async def share_document(
    document_id: str,
    user_id: str,
    share_data: Dict[str, Any],
    db: AsyncSession
) -> DocumentShareResponse:
    """Share document with user or organization."""
    try:
        # Check document access and ownership
        doc_query = select(Document).where(Document.id == document_id)
        doc_result = await db.execute(doc_query)
        document = doc_result.scalar_one_or_none()
        
        if not document:
            raise handle_not_found_error("Document", document_id)
        
        if document.owner_id != user_id:
            raise handle_forbidden_error("Only document owner can share")
        
        if not document.allow_sharing:
            raise handle_forbidden_error("Sharing not allowed on this document")
        
        # Create share
        share = DocumentShare(
            document_id=document_id,
            shared_by=user_id,
            shared_with=share_data["shared_with"],
            permission=share_data["permission"],
            expires_at=share_data.get("expires_at"),
            created_at=datetime.utcnow()
        )
        
        db.add(share)
        await db.commit()
        await db.refresh(share)
        
        return DocumentShareResponse.from_orm(share)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to share document: {e}")
        raise handle_internal_error(f"Failed to share document: {str(e)}")


# Helper functions
async def check_document_access(
    document: Document,
    user_id: str,
    db: AsyncSession
) -> bool:
    """Check if user has access to document."""
    # Owner has access
    if document.owner_id == user_id:
        return True
    
    # Public documents
    if document.is_public:
        return True
    
    # Organization members
    if document.organization_id:
        from app.models.organization import OrganizationMember
        org_query = select(OrganizationMember).where(
            OrganizationMember.organization_id == document.organization_id,
            OrganizationMember.user_id == user_id,
            OrganizationMember.is_active == True
        )
        org_result = await db.execute(org_query)
        if org_result.scalar_one_or_none():
            return True
    
    # Shared documents
    share_query = select(DocumentShare).where(
        DocumentShare.document_id == document.id,
        DocumentShare.shared_with == user_id,
        DocumentShare.is_active == True
    )
    share_result = await db.execute(share_query)
    if share_result.scalar_one_or_none():
        return True
    
    return False


async def check_document_edit_permission(
    document: Document,
    user_id: str,
    db: AsyncSession
) -> bool:
    """Check if user can edit document."""
    if not document.allow_editing:
        return False
    
    # Owner can edit
    if document.owner_id == user_id:
        return True
    
    # Check for edit permission in shares
    share_query = select(DocumentShare).where(
        DocumentShare.document_id == document.id,
        DocumentShare.shared_with == user_id,
        DocumentShare.permission == "edit",
        DocumentShare.is_active == True
    )
    share_result = await db.execute(share_query)
    if share_result.scalar_one_or_none():
        return True
    
    return False




