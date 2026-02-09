"""
Search service following functional patterns
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
import uuid

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error
from app.models.document import Document
from app.models.user import User
from app.models.organization import Organization
from app.schemas.document import DocumentResponse
from app.schemas.user import UserResponse
from app.utils.validators import validate_search_query, validate_pagination
from app.utils.helpers import sanitize_input, extract_mentions, extract_hashtags
from app.utils.cache import cache_search_results, get_cached_search_results
from app.utils.helpers import create_slug

logger = get_logger(__name__)


async def search_documents(
    query: str,
    user_id: str,
    filters: Optional[Dict[str, Any]] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Search documents with full-text search."""
    try:
        # Validate search query
        query_validation = validate_search_query(query)
        if not query_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid search query: {', '.join(query_validation['errors'])}")
            )
        
        # Validate pagination
        pagination_validation = validate_pagination(page, size)
        if not pagination_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid pagination: {', '.join(pagination_validation['errors'])}")
            )
        
        # Sanitize query
        sanitized_query = query_validation["sanitized_query"]
        
        # Generate cache key
        cache_key = f"doc_search:{hash(sanitized_query + str(filters) + str(page) + str(size))}"
        
        # Check cache
        cached_results = get_cached_search_results(cache_key)
        if cached_results:
            return cached_results
        
        # Build search query
        search_filter = or_(
            Document.title.ilike(f"%{sanitized_query}%"),
            Document.description.ilike(f"%{sanitized_query}%"),
            Document.content.ilike(f"%{sanitized_query}%"),
            Document.tags.contains([sanitized_query])
        )
        
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
        
        # Build base query
        base_query = select(Document).where(
            and_(
                search_filter,
                access_filter,
                Document.is_deleted == False
            )
        )
        
        # Apply filters
        if filters:
            if filters.get("document_type"):
                base_query = base_query.where(Document.document_type == filters["document_type"])
            
            if filters.get("status"):
                base_query = base_query.where(Document.status == filters["status"])
            
            if filters.get("organization_id"):
                base_query = base_query.where(Document.organization_id == filters["organization_id"])
            
            if filters.get("date_from"):
                base_query = base_query.where(Document.created_at >= filters["date_from"])
            
            if filters.get("date_to"):
                base_query = base_query.where(Document.created_at <= filters["date_to"])
            
            if filters.get("tags"):
                for tag in filters["tags"]:
                    base_query = base_query.where(Document.tags.contains([tag]))
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply ordering and pagination
        base_query = base_query.order_by(
            desc(Document.updated_at)
        ).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(base_query)
        documents = result.scalars().all()
        
        # Convert to response format
        document_responses = [DocumentResponse.from_orm(doc) for doc in documents]
        
        # Prepare results
        results = {
            "documents": document_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
            "query": sanitized_query,
            "filters": filters or {}
        }
        
        # Cache results
        cache_search_results(cache_key, results)
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search documents: {e}")
        raise handle_internal_error(f"Failed to search documents: {str(e)}")


async def search_users(
    query: str,
    user_id: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Search users by name, username, or email."""
    try:
        # Validate search query
        query_validation = validate_search_query(query)
        if not query_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid search query: {', '.join(query_validation['errors'])}")
            )
        
        # Validate pagination
        pagination_validation = validate_pagination(page, size)
        if not pagination_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid pagination: {', '.join(pagination_validation['errors'])}")
            )
        
        # Sanitize query
        sanitized_query = query_validation["sanitized_query"]
        
        # Generate cache key
        cache_key = f"user_search:{hash(sanitized_query + str(page) + str(size))}"
        
        # Check cache
        cached_results = get_cached_search_results(cache_key)
        if cached_results:
            return cached_results
        
        # Build search query
        search_filter = or_(
            User.full_name.ilike(f"%{sanitized_query}%"),
            User.username.ilike(f"%{sanitized_query}%"),
            User.email.ilike(f"%{sanitized_query}%")
        )
        
        # Build base query
        base_query = select(User).where(
            and_(
                search_filter,
                User.is_active == True,
                User.is_verified == True,
                User.id != user_id  # Exclude current user
            )
        )
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply ordering and pagination
        base_query = base_query.order_by(
            User.full_name
        ).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(base_query)
        users = result.scalars().all()
        
        # Convert to response format
        user_responses = [UserResponse.from_orm(user) for user in users]
        
        # Prepare results
        results = {
            "users": user_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
            "query": sanitized_query
        }
        
        # Cache results
        cache_search_results(cache_key, results)
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search users: {e}")
        raise handle_internal_error(f"Failed to search users: {str(e)}")


async def search_organizations(
    query: str,
    user_id: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Search organizations by name or description."""
    try:
        # Validate search query
        query_validation = validate_search_query(query)
        if not query_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid search query: {', '.join(query_validation['errors'])}")
            )
        
        # Validate pagination
        pagination_validation = validate_pagination(page, size)
        if not pagination_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid pagination: {', '.join(pagination_validation['errors'])}")
            )
        
        # Sanitize query
        sanitized_query = query_validation["sanitized_query"]
        
        # Generate cache key
        cache_key = f"org_search:{hash(sanitized_query + str(page) + str(size))}"
        
        # Check cache
        cached_results = get_cached_search_results(cache_key)
        if cached_results:
            return cached_results
        
        # Build search query
        search_filter = or_(
            Organization.name.ilike(f"%{sanitized_query}%"),
            Organization.description.ilike(f"%{sanitized_query}%")
        )
        
        # Build base query
        base_query = select(Organization).where(
            and_(
                search_filter,
                Organization.is_active == True,
                Organization.is_verified == True
            )
        )
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply ordering and pagination
        base_query = base_query.order_by(
            Organization.name
        ).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(base_query)
        organizations = result.scalars().all()
        
        # Convert to response format
        org_responses = [OrganizationResponse.from_orm(org) for org in organizations]
        
        # Prepare results
        results = {
            "organizations": org_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
            "query": sanitized_query
        }
        
        # Cache results
        cache_search_results(cache_key, results)
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search organizations: {e}")
        raise handle_internal_error(f"Failed to search organizations: {str(e)}")


async def global_search(
    query: str,
    user_id: str,
    search_types: List[str] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Perform global search across all content types."""
    try:
        # Validate search query
        query_validation = validate_search_query(query)
        if not query_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid search query: {', '.join(query_validation['errors'])}")
            )
        
        # Validate pagination
        pagination_validation = validate_pagination(page, size)
        if not pagination_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid pagination: {', '.join(pagination_validation['errors'])}")
            )
        
        # Default search types
        if not search_types:
            search_types = ["documents", "users", "organizations"]
        
        # Sanitize query
        sanitized_query = query_validation["sanitized_query"]
        
        # Generate cache key
        cache_key = f"global_search:{hash(sanitized_query + str(search_types) + str(page) + str(size))}"
        
        # Check cache
        cached_results = get_cached_search_results(cache_key)
        if cached_results:
            return cached_results
        
        results = {
            "query": sanitized_query,
            "search_types": search_types,
            "page": page,
            "size": size,
            "results": {}
        }
        
        # Search documents
        if "documents" in search_types:
            doc_results = await search_documents(
                sanitized_query, user_id, None, page, size, db
            )
            results["results"]["documents"] = doc_results
        
        # Search users
        if "users" in search_types:
            user_results = await search_users(
                sanitized_query, user_id, page, size, db
            )
            results["results"]["users"] = user_results
        
        # Search organizations
        if "organizations" in search_types:
            org_results = await search_organizations(
                sanitized_query, user_id, page, size, db
            )
            results["results"]["organizations"] = org_results
        
        # Calculate total results
        total_results = sum(
            result.get("total", 0) for result in results["results"].values()
        )
        results["total_results"] = total_results
        
        # Cache results
        cache_search_results(cache_key, results)
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to perform global search: {e}")
        raise handle_internal_error(f"Failed to perform global search: {str(e)}")


async def get_search_suggestions(
    query: str,
    user_id: str,
    limit: int = 10,
    db: AsyncSession = None
) -> List[str]:
    """Get search suggestions based on query."""
    try:
        if not query or len(query) < 2:
            return []
        
        # Sanitize query
        sanitized_query = sanitize_input(query)
        
        suggestions = []
        
        # Get document title suggestions
        doc_query = select(Document.title).where(
            and_(
                Document.title.ilike(f"%{sanitized_query}%"),
                Document.is_deleted == False,
                or_(
                    Document.owner_id == user_id,
                    Document.is_public == True
                )
            )
        ).limit(limit)
        
        doc_result = await db.execute(doc_query)
        doc_titles = [row[0] for row in doc_result.fetchall()]
        suggestions.extend(doc_titles)
        
        # Get user name suggestions
        user_query = select(User.full_name).where(
            and_(
                User.full_name.ilike(f"%{sanitized_query}%"),
                User.is_active == True,
                User.id != user_id
            )
        ).limit(limit)
        
        user_result = await db.execute(user_query)
        user_names = [row[0] for row in user_result.fetchall()]
        suggestions.extend(user_names)
        
        # Get organization name suggestions
        org_query = select(Organization.name).where(
            and_(
                Organization.name.ilike(f"%{sanitized_query}%"),
                Organization.is_active == True
            )
        ).limit(limit)
        
        org_result = await db.execute(org_query)
        org_names = [row[0] for row in org_result.fetchall()]
        suggestions.extend(org_names)
        
        # Remove duplicates and limit results
        unique_suggestions = list(dict.fromkeys(suggestions))[:limit]
        
        return unique_suggestions
    
    except Exception as e:
        logger.error(f"Failed to get search suggestions: {e}")
        return []


async def get_popular_searches(
    user_id: str,
    limit: int = 10,
    db: AsyncSession = None
) -> List[str]:
    """Get popular search queries."""
    try:
        # This would implement popular searches logic
        # For now, returning placeholder data
        return [
            "AI document generation",
            "Collaboration tools",
            "Document templates",
            "Real-time editing",
            "Content analysis"
        ]
    
    except Exception as e:
        logger.error(f"Failed to get popular searches: {e}")
        return []


async def get_recent_searches(
    user_id: str,
    limit: int = 10,
    db: AsyncSession = None
) -> List[str]:
    """Get recent search queries for user."""
    try:
        # This would implement recent searches logic
        # For now, returning placeholder data
        return [
            "project documentation",
            "meeting notes",
            "technical specifications"
        ]
    
    except Exception as e:
        logger.error(f"Failed to get recent searches: {e}")
        return []




