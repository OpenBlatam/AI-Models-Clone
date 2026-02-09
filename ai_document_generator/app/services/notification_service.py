"""
Notification service following functional patterns
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
import uuid

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error
from app.models.user import User
from app.models.document import Document
from app.models.organization import Organization
from app.schemas.notification import (
    NotificationCreate, NotificationResponse, NotificationUpdate,
    NotificationSettings, NotificationTemplate
)
from app.utils.validators import validate_pagination
from app.utils.helpers import format_timestamp, get_time_ago
from app.utils.cache import cache_user_data, get_cached_user_data

logger = get_logger(__name__)


async def create_notification(
    notification_data: NotificationCreate,
    db: AsyncSession
) -> NotificationResponse:
    """Create a new notification."""
    try:
        # Create notification
        notification = Notification(
            user_id=notification_data.user_id,
            title=notification_data.title,
            message=notification_data.message,
            notification_type=notification_data.notification_type,
            priority=notification_data.priority,
            metadata=notification_data.metadata or {},
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        # Send real-time notification if user is online
        await send_realtime_notification(notification)
        
        logger.info(f"Notification created: {notification.id} for user {notification_data.user_id}")
        
        return NotificationResponse.from_orm(notification)
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create notification: {e}")
        raise handle_internal_error(f"Failed to create notification: {str(e)}")


async def get_user_notifications(
    user_id: str,
    page: int = 1,
    size: int = 20,
    unread_only: bool = False,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get notifications for a user."""
    try:
        # Validate pagination
        pagination_validation = validate_pagination(page, size)
        if not pagination_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid pagination: {', '.join(pagination_validation['errors'])}")
            )
        
        # Build query
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply ordering and pagination
        query = query.order_by(desc(Notification.created_at)).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        # Convert to response format
        notification_responses = [NotificationResponse.from_orm(notif) for notif in notifications]
        
        return {
            "notifications": notification_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
            "unread_count": await get_unread_notification_count(user_id, db)
        }
    
    except Exception as e:
        logger.error(f"Failed to get user notifications: {e}")
        raise handle_internal_error(f"Failed to get user notifications: {str(e)}")


async def mark_notification_read(
    notification_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Mark a notification as read."""
    try:
        # Get notification
        query = select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        result = await db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise handle_not_found_error("Notification", notification_id)
        
        # Mark as read
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Notification marked as read: {notification_id}")
        
        return {"message": "Notification marked as read"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to mark notification as read: {e}")
        raise handle_internal_error(f"Failed to mark notification as read: {str(e)}")


async def mark_all_notifications_read(
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Mark all notifications as read for a user."""
    try:
        # Get unread notifications
        query = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        # Mark all as read
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"All notifications marked as read for user: {user_id}")
        
        return {"message": "All notifications marked as read"}
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to mark all notifications as read: {e}")
        raise handle_internal_error(f"Failed to mark all notifications as read: {str(e)}")


async def delete_notification(
    notification_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Delete a notification."""
    try:
        # Get notification
        query = select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        result = await db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise handle_not_found_error("Notification", notification_id)
        
        # Delete notification
        await db.delete(notification)
        await db.commit()
        
        logger.info(f"Notification deleted: {notification_id}")
        
        return {"message": "Notification deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete notification: {e}")
        raise handle_internal_error(f"Failed to delete notification: {str(e)}")


async def get_unread_notification_count(
    user_id: str,
    db: AsyncSession
) -> int:
    """Get count of unread notifications for user."""
    try:
        query = select(func.count(Notification.id)).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        result = await db.execute(query)
        count = result.scalar()
        
        return count or 0
    
    except Exception as e:
        logger.error(f"Failed to get unread notification count: {e}")
        return 0


async def get_notification_settings(
    user_id: str,
    db: AsyncSession
) -> NotificationSettings:
    """Get notification settings for user."""
    try:
        # Get user
        from app.core.auth_utils import get_user_by_id
        user = await get_user_by_id(db, user_id)
        
        if not user:
            raise handle_not_found_error("User", user_id)
        
        # Return notification preferences from user model
        return NotificationSettings(
            user_id=user_id,
            email_notifications=user.notification_preferences.get("email", True),
            push_notifications=user.notification_preferences.get("push", True),
            document_notifications=user.notification_preferences.get("documents", True),
            collaboration_notifications=user.notification_preferences.get("collaboration", True),
            ai_notifications=user.notification_preferences.get("ai", True),
            system_notifications=user.notification_preferences.get("system", True)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get notification settings: {e}")
        raise handle_internal_error(f"Failed to get notification settings: {str(e)}")


async def update_notification_settings(
    user_id: str,
    settings: NotificationSettings,
    db: AsyncSession
) -> NotificationSettings:
    """Update notification settings for user."""
    try:
        # Get user
        from app.core.auth_utils import get_user_by_id
        user = await get_user_by_id(db, user_id)
        
        if not user:
            raise handle_not_found_error("User", user_id)
        
        # Update notification preferences
        user.notification_preferences = {
            "email": settings.email_notifications,
            "push": settings.push_notifications,
            "documents": settings.document_notifications,
            "collaboration": settings.collaboration_notifications,
            "ai": settings.ai_notifications,
            "system": settings.system_notifications
        }
        
        await db.commit()
        
        # Invalidate cache
        invalidate_user_cache(user_id)
        
        logger.info(f"Notification settings updated for user: {user_id}")
        
        return settings
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update notification settings: {e}")
        raise handle_internal_error(f"Failed to update notification settings: {str(e)}")


async def send_document_notification(
    document_id: str,
    notification_type: str,
    title: str,
    message: str,
    metadata: Dict[str, Any],
    db: AsyncSession
) -> None:
    """Send notification related to document activity."""
    try:
        # Get document
        doc_query = select(Document).where(Document.id == document_id)
        doc_result = await db.execute(doc_query)
        document = doc_result.scalar_one_or_none()
        
        if not document:
            return
        
        # Get users to notify
        users_to_notify = []
        
        # Add document owner
        users_to_notify.append(document.owner_id)
        
        # Add collaborators
        collab_query = select(Collaboration).where(
            and_(
                Collaboration.document_id == document_id,
                Collaboration.status == "active"
            )
        )
        collab_result = await db.execute(collab_query)
        collaborations = collab_result.scalars().all()
        
        for collab in collaborations:
            if collab.user_id not in users_to_notify:
                users_to_notify.append(collab.user_id)
        
        # Send notifications
        for user_id in users_to_notify:
            # Check if user wants this type of notification
            user_settings = await get_notification_settings(user_id, db)
            
            if notification_type == "document" and not user_settings.document_notifications:
                continue
            elif notification_type == "collaboration" and not user_settings.collaboration_notifications:
                continue
            
            # Create notification
            notification_data = NotificationCreate(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                priority="medium",
                metadata=metadata
            )
            
            await create_notification(notification_data, db)
    
    except Exception as e:
        logger.error(f"Failed to send document notification: {e}")


async def send_ai_notification(
    user_id: str,
    title: str,
    message: str,
    metadata: Dict[str, Any],
    db: AsyncSession
) -> None:
    """Send AI-related notification."""
    try:
        # Check if user wants AI notifications
        user_settings = await get_notification_settings(user_id, db)
        
        if not user_settings.ai_notifications:
            return
        
        # Create notification
        notification_data = NotificationCreate(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="ai",
            priority="low",
            metadata=metadata
        )
        
        await create_notification(notification_data, db)
    
    except Exception as e:
        logger.error(f"Failed to send AI notification: {e}")


async def send_system_notification(
    user_id: str,
    title: str,
    message: str,
    priority: str = "medium",
    metadata: Dict[str, Any] = None,
    db: AsyncSession = None
) -> None:
    """Send system notification."""
    try:
        # Check if user wants system notifications
        user_settings = await get_notification_settings(user_id, db)
        
        if not user_settings.system_notifications:
            return
        
        # Create notification
        notification_data = NotificationCreate(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="system",
            priority=priority,
            metadata=metadata or {}
        )
        
        await create_notification(notification_data, db)
    
    except Exception as e:
        logger.error(f"Failed to send system notification: {e}")


async def send_realtime_notification(
    notification: Notification
) -> None:
    """Send real-time notification via WebSocket."""
    try:
        # This would implement WebSocket notification sending
        # For now, just logging
        logger.info(f"Real-time notification sent: {notification.id}")
    
    except Exception as e:
        logger.error(f"Failed to send real-time notification: {e}")


async def cleanup_old_notifications(
    days_old: int = 30,
    db: AsyncSession = None
) -> int:
    """Clean up old notifications."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Delete old read notifications
        query = select(Notification).where(
            and_(
                Notification.created_at < cutoff_date,
                Notification.is_read == True
            )
        )
        result = await db.execute(query)
        old_notifications = result.scalars().all()
        
        deleted_count = 0
        for notification in old_notifications:
            await db.delete(notification)
            deleted_count += 1
        
        await db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old notifications")
        
        return deleted_count
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to cleanup old notifications: {e}")
        return 0




