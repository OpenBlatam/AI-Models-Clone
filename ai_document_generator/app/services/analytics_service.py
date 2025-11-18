"""
Analytics service following functional patterns
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
import uuid

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error
from app.models.document import Document, DocumentVersion
from app.models.user import User
from app.models.organization import Organization
from app.models.collaboration import Collaboration, CollaborationEvent, ChatMessage
from app.utils.validators import validate_date_range, validate_pagination
from app.utils.helpers import format_timestamp, get_time_ago
from app.utils.cache import cache_user_data, get_cached_user_data

logger = get_logger(__name__)


async def get_document_analytics(
    document_id: str,
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get analytics for a specific document."""
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Validate date range
        date_validation = validate_date_range(start_date, end_date)
        if not date_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid date range: {', '.join(date_validation['errors'])}")
            )
        
        # Get document
        doc_query = select(Document).where(Document.id == document_id)
        doc_result = await db.execute(doc_query)
        document = doc_result.scalar_one_or_none()
        
        if not document:
            raise handle_not_found_error("Document", document_id)
        
        # Check access permissions
        has_access = await check_document_access(document, user_id, db)
        if not has_access:
            raise handle_forbidden_error("Access denied to document")
        
        # Get view count
        view_count = document.view_count or 0
        
        # Get edit count
        edit_count = document.edit_count or 0
        
        # Get share count
        share_count = document.share_count or 0
        
        # Get collaboration events
        collab_query = select(CollaborationEvent).where(
            and_(
                CollaborationEvent.document_id == document_id,
                CollaborationEvent.timestamp >= start_date,
                CollaborationEvent.timestamp <= end_date
            )
        )
        collab_result = await db.execute(collab_query)
        collaboration_events = collab_result.scalars().all()
        
        # Get chat messages
        chat_query = select(ChatMessage).where(
            and_(
                ChatMessage.document_id == document_id,
                ChatMessage.created_at >= start_date,
                ChatMessage.created_at <= end_date
            )
        )
        chat_result = await db.execute(chat_query)
        chat_messages = chat_result.scalars().all()
        
        # Get document versions
        version_query = select(DocumentVersion).where(
            and_(
                DocumentVersion.document_id == document_id,
                DocumentVersion.created_at >= start_date,
                DocumentVersion.created_at <= end_date
            )
        )
        version_result = await db.execute(version_query)
        versions = version_result.scalars().all()
        
        # Calculate metrics
        total_collaborators = len(set(event.user_id for event in collaboration_events))
        total_events = len(collaboration_events)
        total_messages = len(chat_messages)
        total_versions = len(versions)
        
        # Activity by day
        activity_by_day = {}
        for event in collaboration_events:
            day = event.timestamp.date()
            if day not in activity_by_day:
                activity_by_day[day] = {"events": 0, "messages": 0, "versions": 0}
            activity_by_day[day]["events"] += 1
        
        for message in chat_messages:
            day = message.created_at.date()
            if day not in activity_by_day:
                activity_by_day[day] = {"events": 0, "messages": 0, "versions": 0}
            activity_by_day[day]["messages"] += 1
        
        for version in versions:
            day = version.created_at.date()
            if day not in activity_by_day:
                activity_by_day[day] = {"events": 0, "messages": 0, "versions": 0}
            activity_by_day[day]["versions"] += 1
        
        # Convert to list format
        activity_timeline = [
            {
                "date": day.isoformat(),
                "events": data["events"],
                "messages": data["messages"],
                "versions": data["versions"]
            }
            for day, data in sorted(activity_by_day.items())
        ]
        
        return {
            "document_id": document_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "metrics": {
                "view_count": view_count,
                "edit_count": edit_count,
                "share_count": share_count,
                "total_collaborators": total_collaborators,
                "total_events": total_events,
                "total_messages": total_messages,
                "total_versions": total_versions
            },
            "activity_timeline": activity_timeline,
            "last_activity": document.updated_at.isoformat() if document.updated_at else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document analytics: {e}")
        raise handle_internal_error(f"Failed to get document analytics: {str(e)}")


async def get_user_analytics(
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get analytics for a specific user."""
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Validate date range
        date_validation = validate_date_range(start_date, end_date)
        if not date_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid date range: {', '.join(date_validation['errors'])}")
            )
        
        # Get user
        from app.core.auth_utils import get_user_by_id
        user = await get_user_by_id(db, user_id)
        if not user:
            raise handle_not_found_error("User", user_id)
        
        # Get documents created
        docs_query = select(Document).where(
            and_(
                Document.owner_id == user_id,
                Document.created_at >= start_date,
                Document.created_at <= end_date
            )
        )
        docs_result = await db.execute(docs_query)
        documents = docs_result.scalars().all()
        
        # Get collaboration events
        collab_query = select(CollaborationEvent).where(
            and_(
                CollaborationEvent.user_id == user_id,
                CollaborationEvent.timestamp >= start_date,
                CollaborationEvent.timestamp <= end_date
            )
        )
        collab_result = await db.execute(collab_query)
        collaboration_events = collab_result.scalars().all()
        
        # Get chat messages
        chat_query = select(ChatMessage).where(
            and_(
                ChatMessage.author_id == user_id,
                ChatMessage.created_at >= start_date,
                ChatMessage.created_at <= end_date
            )
        )
        chat_result = await db.execute(chat_query)
        chat_messages = chat_result.scalars().all()
        
        # Calculate metrics
        total_documents = len(documents)
        total_events = len(collaboration_events)
        total_messages = len(chat_messages)
        
        # Documents by type
        docs_by_type = {}
        for doc in documents:
            doc_type = doc.document_type
            if doc_type not in docs_by_type:
                docs_by_type[doc_type] = 0
            docs_by_type[doc_type] += 1
        
        # Activity by day
        activity_by_day = {}
        for event in collaboration_events:
            day = event.timestamp.date()
            if day not in activity_by_day:
                activity_by_day[day] = {"events": 0, "messages": 0, "documents": 0}
            activity_by_day[day]["events"] += 1
        
        for message in chat_messages:
            day = message.created_at.date()
            if day not in activity_by_day:
                activity_by_day[day] = {"events": 0, "messages": 0, "documents": 0}
            activity_by_day[day]["messages"] += 1
        
        for doc in documents:
            day = doc.created_at.date()
            if day not in activity_by_day:
                activity_by_day[day] = {"events": 0, "messages": 0, "documents": 0}
            activity_by_day[day]["documents"] += 1
        
        # Convert to list format
        activity_timeline = [
            {
                "date": day.isoformat(),
                "events": data["events"],
                "messages": data["messages"],
                "documents": data["documents"]
            }
            for day, data in sorted(activity_by_day.items())
        ]
        
        return {
            "user_id": user_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "metrics": {
                "total_documents": total_documents,
                "total_events": total_events,
                "total_messages": total_messages,
                "documents_by_type": docs_by_type
            },
            "activity_timeline": activity_timeline,
            "last_activity": user.updated_at.isoformat() if user.updated_at else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user analytics: {e}")
        raise handle_internal_error(f"Failed to get user analytics: {str(e)}")


async def get_organization_analytics(
    organization_id: str,
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get analytics for an organization."""
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Validate date range
        date_validation = validate_date_range(start_date, end_date)
        if not date_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid date range: {', '.join(date_validation['errors'])}")
            )
        
        # Check organization access
        from app.models.organization import OrganizationMember
        org_query = select(OrganizationMember).where(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
                OrganizationMember.is_active == True
            )
        )
        org_result = await db.execute(org_query)
        membership = org_result.scalar_one_or_none()
        
        if not membership:
            raise handle_forbidden_error("Access denied to organization")
        
        # Get organization
        org_query = select(Organization).where(Organization.id == organization_id)
        org_result = await db.execute(org_query)
        organization = org_result.scalar_one_or_none()
        
        if not organization:
            raise handle_not_found_error("Organization", organization_id)
        
        # Get documents
        docs_query = select(Document).where(
            and_(
                Document.organization_id == organization_id,
                Document.created_at >= start_date,
                Document.created_at <= end_date
            )
        )
        docs_result = await db.execute(docs_query)
        documents = docs_result.scalars().all()
        
        # Get members
        members_query = select(OrganizationMember).where(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.is_active == True
            )
        )
        members_result = await db.execute(members_query)
        members = members_result.scalars().all()
        
        # Get collaboration events
        collab_query = select(CollaborationEvent).where(
            and_(
                CollaborationEvent.document_id.in_([doc.id for doc in documents]),
                CollaborationEvent.timestamp >= start_date,
                CollaborationEvent.timestamp <= end_date
            )
        )
        collab_result = await db.execute(collab_query)
        collaboration_events = collab_result.scalars().all()
        
        # Calculate metrics
        total_documents = len(documents)
        total_members = len(members)
        total_events = len(collaboration_events)
        
        # Documents by type
        docs_by_type = {}
        for doc in documents:
            doc_type = doc.document_type
            if doc_type not in docs_by_type:
                docs_by_type[doc_type] = 0
            docs_by_type[doc_type] += 1
        
        # Activity by day
        activity_by_day = {}
        for event in collaboration_events:
            day = event.timestamp.date()
            if day not in activity_by_day:
                activity_by_day[day] = {"events": 0, "documents": 0}
            activity_by_day[day]["events"] += 1
        
        for doc in documents:
            day = doc.created_at.date()
            if day not in activity_by_day:
                activity_by_day[day] = {"events": 0, "documents": 0}
            activity_by_day[day]["documents"] += 1
        
        # Convert to list format
        activity_timeline = [
            {
                "date": day.isoformat(),
                "events": data["events"],
                "documents": data["documents"]
            }
            for day, data in sorted(activity_by_day.items())
        ]
        
        return {
            "organization_id": organization_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "metrics": {
                "total_documents": total_documents,
                "total_members": total_members,
                "total_events": total_events,
                "documents_by_type": docs_by_type
            },
            "activity_timeline": activity_timeline,
            "last_activity": organization.updated_at.isoformat() if organization.updated_at else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get organization analytics: {str(e)}")
        raise handle_internal_error(f"Failed to get organization analytics: {str(e)}")


async def get_system_analytics(
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get system-wide analytics (admin only)."""
    try:
        # Check if user is superuser
        from app.core.auth_utils import get_user_by_id
        user = await get_user_by_id(db, user_id)
        if not user or not user.is_superuser:
            raise handle_forbidden_error("Admin access required")
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Validate date range
        date_validation = validate_date_range(start_date, end_date)
        if not date_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid date range: {', '.join(date_validation['errors'])}")
            )
        
        # Get total users
        users_query = select(func.count(User.id)).where(
            and_(
                User.created_at >= start_date,
                User.created_at <= end_date
            )
        )
        users_result = await db.execute(users_query)
        total_users = users_result.scalar()
        
        # Get total documents
        docs_query = select(func.count(Document.id)).where(
            and_(
                Document.created_at >= start_date,
                Document.created_at <= end_date
            )
        )
        docs_result = await db.execute(docs_query)
        total_documents = docs_result.scalar()
        
        # Get total organizations
        orgs_query = select(func.count(Organization.id)).where(
            and_(
                Organization.created_at >= start_date,
                Organization.created_at <= end_date
            )
        )
        orgs_result = await db.execute(orgs_query)
        total_organizations = orgs_result.scalar()
        
        # Get total collaboration events
        events_query = select(func.count(CollaborationEvent.id)).where(
            and_(
                CollaborationEvent.timestamp >= start_date,
                CollaborationEvent.timestamp <= end_date
            )
        )
        events_result = await db.execute(events_query)
        total_events = events_result.scalar()
        
        # Get total chat messages
        messages_query = select(func.count(ChatMessage.id)).where(
            and_(
                ChatMessage.created_at >= start_date,
                ChatMessage.created_at <= end_date
            )
        )
        messages_result = await db.execute(messages_query)
        total_messages = messages_result.scalar()
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "metrics": {
                "total_users": total_users,
                "total_documents": total_documents,
                "total_organizations": total_organizations,
                "total_events": total_events,
                "total_messages": total_messages
            },
            "system_info": {
                "version": "1.0.0",
                "uptime": "99.9%",
                "last_backup": "2023-01-01T00:00:00Z"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get system analytics: {e}")
        raise handle_internal_error(f"Failed to get system analytics: {str(e)}")


async def get_ai_usage_analytics(
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get AI usage analytics for user."""
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Validate date range
        date_validation = validate_date_range(start_date, end_date)
        if not date_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid date range: {', '.join(date_validation['errors'])}")
            )
        
        # This would implement AI usage tracking logic
        # For now, returning placeholder data
        return {
            "user_id": user_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "metrics": {
                "total_requests": 150,
                "total_tokens": 5000,
                "total_cost": 10.50,
                "requests_by_provider": {
                    "openai": 100,
                    "anthropic": 30,
                    "deepseek": 20
                },
                "requests_by_type": {
                    "generation": 80,
                    "analysis": 40,
                    "translation": 20,
                    "summarization": 10
                }
            },
            "usage_timeline": [
                {
                    "date": "2023-01-01",
                    "requests": 5,
                    "tokens": 200,
                    "cost": 0.50
                }
            ]
        }
    
    except Exception as e:
        logger.error(f"Failed to get AI usage analytics: {e}")
        raise handle_internal_error(f"Failed to get AI usage analytics: {str(e)}")


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
    
    return False




