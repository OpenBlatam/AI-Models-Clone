"""
Webhook service following functional patterns
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
import uuid
import json
import hashlib
import hmac
import httpx
import asyncio

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error, handle_not_found_error
from app.models.webhook import Webhook, WebhookEvent, WebhookDelivery
from app.schemas.webhook import (
    WebhookCreate, WebhookUpdate, WebhookResponse,
    WebhookEventResponse, WebhookDeliveryResponse
)
from app.utils.validators import validate_webhook_url, validate_webhook_secret
from app.utils.helpers import generate_webhook_secret, create_webhook_signature
from app.utils.cache import cache_webhook_data, get_cached_webhook_data, invalidate_webhook_cache

logger = get_logger(__name__)


async def create_webhook(
    webhook_data: WebhookCreate,
    user_id: str,
    db: AsyncSession
) -> WebhookResponse:
    """Create a new webhook."""
    try:
        # Validate webhook URL
        url_validation = validate_webhook_url(webhook_data.url)
        if not url_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid webhook URL: {', '.join(url_validation['errors'])}")
            )
        
        # Validate webhook secret if provided
        if webhook_data.secret:
            secret_validation = validate_webhook_secret(webhook_data.secret)
            if not secret_validation["is_valid"]:
                raise handle_validation_error(
                    ValueError(f"Invalid webhook secret: {', '.join(secret_validation['errors'])}")
                )
        
        # Generate webhook secret if not provided
        webhook_secret = webhook_data.secret or generate_webhook_secret()
        
        # Create webhook
        webhook = Webhook(
            name=webhook_data.name,
            url=webhook_data.url,
            secret=webhook_secret,
            events=webhook_data.events,
            is_active=webhook_data.is_active,
            retry_count=webhook_data.retry_count,
            timeout=webhook_data.timeout,
            headers=webhook_data.headers or {},
            metadata=webhook_data.metadata or {},
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        db.add(webhook)
        await db.commit()
        await db.refresh(webhook)
        
        # Cache webhook data
        cache_webhook_data(str(webhook.id), webhook)
        
        logger.info(f"Webhook created: {webhook.id} by user {user_id}")
        
        return WebhookResponse.from_orm(webhook)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create webhook: {e}")
        raise handle_internal_error(f"Failed to create webhook: {str(e)}")


async def get_webhook(
    webhook_id: str,
    user_id: str,
    db: AsyncSession
) -> WebhookResponse:
    """Get webhook by ID."""
    try:
        # Check cache first
        cached_webhook = get_cached_webhook_data(webhook_id)
        if cached_webhook:
            return WebhookResponse.from_orm(cached_webhook)
        
        # Get from database
        query = select(Webhook).where(Webhook.id == webhook_id)
        result = await db.execute(query)
        webhook = result.scalar_one_or_none()
        
        if not webhook:
            raise handle_not_found_error("Webhook", webhook_id)
        
        # Check access permissions
        has_access = await check_webhook_access(webhook, user_id, db)
        if not has_access:
            raise handle_forbidden_error("Access denied to webhook")
        
        # Cache webhook data
        cache_webhook_data(webhook_id, webhook)
        
        return WebhookResponse.from_orm(webhook)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get webhook: {e}")
        raise handle_internal_error(f"Failed to get webhook: {str(e)}")


async def update_webhook(
    webhook_id: str,
    update_data: WebhookUpdate,
    user_id: str,
    db: AsyncSession
) -> WebhookResponse:
    """Update webhook."""
    try:
        # Get webhook
        query = select(Webhook).where(Webhook.id == webhook_id)
        result = await db.execute(query)
        webhook = result.scalar_one_or_none()
        
        if not webhook:
            raise handle_not_found_error("Webhook", webhook_id)
        
        # Check edit permissions
        can_edit = await check_webhook_edit_permission(webhook, user_id, db)
        if not can_edit:
            raise handle_forbidden_error("No edit permission for webhook")
        
        # Update fields
        if update_data.name is not None:
            webhook.name = update_data.name
        
        if update_data.url is not None:
            url_validation = validate_webhook_url(update_data.url)
            if not url_validation["is_valid"]:
                raise ValueError(f"Invalid webhook URL: {', '.join(url_validation['errors'])}")
            webhook.url = update_data.url
        
        if update_data.secret is not None:
            secret_validation = validate_webhook_secret(update_data.secret)
            if not secret_validation["is_valid"]:
                raise ValueError(f"Invalid webhook secret: {', '.join(secret_validation['errors'])}")
            webhook.secret = update_data.secret
        
        if update_data.events is not None:
            webhook.events = update_data.events
        
        if update_data.is_active is not None:
            webhook.is_active = update_data.is_active
        
        if update_data.retry_count is not None:
            webhook.retry_count = update_data.retry_count
        
        if update_data.timeout is not None:
            webhook.timeout = update_data.timeout
        
        if update_data.headers is not None:
            webhook.headers = update_data.headers
        
        if update_data.metadata is not None:
            webhook.metadata = update_data.metadata
        
        webhook.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(webhook)
        
        # Invalidate cache
        invalidate_webhook_cache(webhook_id)
        
        logger.info(f"Webhook updated: {webhook_id} by user {user_id}")
        
        return WebhookResponse.from_orm(webhook)
    
    except HTTPException:
        raise
    except ValueError as e:
        raise handle_validation_error(e)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update webhook: {e}")
        raise handle_internal_error(f"Failed to update webhook: {str(e)}")


async def delete_webhook(
    webhook_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Delete webhook."""
    try:
        # Get webhook
        query = select(Webhook).where(Webhook.id == webhook_id)
        result = await db.execute(query)
        webhook = result.scalar_one_or_none()
        
        if not webhook:
            raise handle_not_found_error("Webhook", webhook_id)
        
        # Check delete permissions (only creator can delete)
        if webhook.created_by != user_id:
            raise handle_forbidden_error("Only webhook creator can delete")
        
        # Soft delete
        webhook.is_deleted = True
        webhook.deleted_at = datetime.utcnow()
        webhook.deleted_by = user_id
        
        await db.commit()
        
        # Invalidate cache
        invalidate_webhook_cache(webhook_id)
        
        logger.info(f"Webhook deleted: {webhook_id} by user {user_id}")
        
        return {"message": "Webhook deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete webhook: {e}")
        raise handle_internal_error(f"Failed to delete webhook: {str(e)}")


async def list_webhooks(
    user_id: str,
    is_active: Optional[bool] = None,
    event: Optional[str] = None,
    search_query: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """List webhooks with filtering and pagination."""
    try:
        # Build query
        query = select(Webhook).where(Webhook.is_deleted == False)
        
        # Apply filters
        if is_active is not None:
            query = query.where(Webhook.is_active == is_active)
        
        if event:
            query = query.where(Webhook.events.contains([event]))
        
        if search_query:
            search_filter = or_(
                Webhook.name.ilike(f"%{search_query}%"),
                Webhook.url.ilike(f"%{search_query}%")
            )
            query = query.where(search_filter)
        
        # Apply access control
        access_filter = or_(
            Webhook.created_by == user_id
        )
        query = query.where(access_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(Webhook.updated_at)).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(query)
        webhooks = result.scalars().all()
        
        # Convert to response format
        webhook_responses = [WebhookResponse.from_orm(webhook) for webhook in webhooks]
        
        return {
            "webhooks": webhook_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except Exception as e:
        logger.error(f"Failed to list webhooks: {e}")
        raise handle_internal_error(f"Failed to list webhooks: {str(e)}")


async def trigger_webhook(
    webhook_id: str,
    event: str,
    payload: Dict[str, Any],
    user_id: str,
    db: AsyncSession
) -> WebhookDeliveryResponse:
    """Trigger a webhook delivery."""
    try:
        # Get webhook
        webhook = await get_webhook(webhook_id, user_id, db)
        
        if not webhook.is_active:
            raise handle_forbidden_error("Webhook is not active")
        
        if event not in webhook.events:
            raise handle_forbidden_error(f"Event '{event}' not allowed for this webhook")
        
        # Create delivery record
        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            event=event,
            payload=payload,
            status="pending",
            retry_count=0,
            created_at=datetime.utcnow()
        )
        
        db.add(delivery)
        await db.commit()
        await db.refresh(delivery)
        
        # Send webhook asynchronously
        asyncio.create_task(send_webhook_delivery(webhook, delivery, payload))
        
        logger.info(f"Webhook triggered: {webhook_id} for event {event}")
        
        return WebhookDeliveryResponse.from_orm(delivery)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to trigger webhook: {e}")
        raise handle_internal_error(f"Failed to trigger webhook: {str(e)}")


async def send_webhook_delivery(
    webhook: Webhook,
    delivery: WebhookDelivery,
    payload: Dict[str, Any]
) -> None:
    """Send webhook delivery."""
    try:
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AI-Document-Generator-Webhook/1.0",
            **webhook.headers
        }
        
        # Add signature if secret is provided
        if webhook.secret:
            signature = create_webhook_signature(webhook.secret, payload)
            headers["X-Webhook-Signature"] = signature
        
        # Send webhook
        async with httpx.AsyncClient(timeout=webhook.timeout) as client:
            response = await client.post(
                webhook.url,
                json=payload,
                headers=headers
            )
            
            # Update delivery status
            delivery.status = "delivered" if response.status_code < 400 else "failed"
            delivery.response_status = response.status_code
            delivery.response_body = response.text
            delivery.delivered_at = datetime.utcnow()
            
    except httpx.TimeoutException:
        delivery.status = "timeout"
        delivery.error_message = "Request timeout"
    except httpx.RequestError as e:
        delivery.status = "failed"
        delivery.error_message = str(e)
    except Exception as e:
        delivery.status = "failed"
        delivery.error_message = str(e)
        logger.error(f"Webhook delivery failed: {e}")
    
    # Update delivery record
    try:
        from app.core.database import get_db
        async with get_db() as db:
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to update delivery record: {e}")


async def get_webhook_deliveries(
    webhook_id: str,
    user_id: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get webhook deliveries."""
    try:
        # Check webhook access
        webhook = await get_webhook(webhook_id, user_id, db)
        
        # Get deliveries
        query = select(WebhookDelivery).where(
            WebhookDelivery.webhook_id == webhook_id
        ).order_by(desc(WebhookDelivery.created_at))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination
        query = query.offset((page - 1) * size).limit(size)
        
        result = await db.execute(query)
        deliveries = result.scalars().all()
        
        delivery_responses = [WebhookDeliveryResponse.from_orm(delivery) for delivery in deliveries]
        
        return {
            "deliveries": delivery_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get webhook deliveries: {e}")
        raise handle_internal_error(f"Failed to get webhook deliveries: {str(e)}")


async def retry_webhook_delivery(
    delivery_id: str,
    user_id: str,
    db: AsyncSession
) -> WebhookDeliveryResponse:
    """Retry a failed webhook delivery."""
    try:
        # Get delivery
        query = select(WebhookDelivery).where(WebhookDelivery.id == delivery_id)
        result = await db.execute(query)
        delivery = result.scalar_one_or_none()
        
        if not delivery:
            raise handle_not_found_error("Webhook delivery", delivery_id)
        
        # Check webhook access
        webhook = await get_webhook(delivery.webhook_id, user_id, db)
        
        if delivery.retry_count >= webhook.retry_count:
            raise handle_forbidden_error("Maximum retry count reached")
        
        # Update delivery status
        delivery.status = "pending"
        delivery.retry_count += 1
        delivery.updated_at = datetime.utcnow()
        
        await db.commit()
        
        # Retry delivery
        asyncio.create_task(send_webhook_delivery(webhook, delivery, delivery.payload))
        
        logger.info(f"Webhook delivery retry: {delivery_id}")
        
        return WebhookDeliveryResponse.from_orm(delivery)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to retry webhook delivery: {e}")
        raise handle_internal_error(f"Failed to retry webhook delivery: {str(e)}")


async def get_webhook_stats(
    webhook_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """Get webhook statistics."""
    try:
        # Check webhook access
        webhook = await get_webhook(webhook_id, user_id, db)
        
        # Get delivery statistics
        deliveries_query = select(WebhookDelivery).where(
            WebhookDelivery.webhook_id == webhook_id
        )
        deliveries_result = await db.execute(deliveries_query)
        deliveries = deliveries_result.scalars().all()
        
        # Calculate stats
        total_deliveries = len(deliveries)
        successful_deliveries = len([d for d in deliveries if d.status == "delivered"])
        failed_deliveries = len([d for d in deliveries if d.status == "failed"])
        pending_deliveries = len([d for d in deliveries if d.status == "pending"])
        
        # Delivery by event
        delivery_by_event = {}
        for delivery in deliveries:
            event = delivery.event
            if event not in delivery_by_event:
                delivery_by_event[event] = {"total": 0, "successful": 0, "failed": 0}
            delivery_by_event[event]["total"] += 1
            if delivery.status == "delivered":
                delivery_by_event[event]["successful"] += 1
            elif delivery.status == "failed":
                delivery_by_event[event]["failed"] += 1
        
        # Delivery by date
        delivery_by_date = {}
        for delivery in deliveries:
            date = delivery.created_at.date()
            if date not in delivery_by_date:
                delivery_by_date[date] = {"total": 0, "successful": 0, "failed": 0}
            delivery_by_date[date]["total"] += 1
            if delivery.status == "delivered":
                delivery_by_date[date]["successful"] += 1
            elif delivery.status == "failed":
                delivery_by_date[date]["failed"] += 1
        
        # Average response time
        successful_deliveries_with_time = [
            d for d in deliveries 
            if d.status == "delivered" and d.delivered_at
        ]
        avg_response_time = 0
        if successful_deliveries_with_time:
            total_time = sum(
                (d.delivered_at - d.created_at).total_seconds()
                for d in successful_deliveries_with_time
            )
            avg_response_time = total_time / len(successful_deliveries_with_time)
        
        return {
            "webhook_id": webhook_id,
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "pending_deliveries": pending_deliveries,
            "success_rate": successful_deliveries / total_deliveries if total_deliveries > 0 else 0,
            "average_response_time": avg_response_time,
            "delivery_by_event": delivery_by_event,
            "delivery_by_date": delivery_by_date,
            "recent_deliveries": [
                {
                    "id": str(delivery.id),
                    "event": delivery.event,
                    "status": delivery.status,
                    "created_at": delivery.created_at.isoformat(),
                    "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else None,
                    "response_status": delivery.response_status,
                    "error_message": delivery.error_message
                }
                for delivery in deliveries[-10:]  # Last 10 deliveries
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get webhook stats: {e}")
        raise handle_internal_error(f"Failed to get webhook stats: {str(e)}")


async def test_webhook(
    webhook_id: str,
    user_id: str,
    test_payload: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """Test a webhook with sample payload."""
    try:
        # Get webhook
        webhook = await get_webhook(webhook_id, user_id, db)
        
        # Create test delivery
        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            event="test",
            payload=test_payload,
            status="pending",
            retry_count=0,
            created_at=datetime.utcnow()
        )
        
        db.add(delivery)
        await db.commit()
        await db.refresh(delivery)
        
        # Send test webhook
        await send_webhook_delivery(webhook, delivery, test_payload)
        
        return {
            "delivery_id": str(delivery.id),
            "status": delivery.status,
            "response_status": delivery.response_status,
            "response_body": delivery.response_body,
            "error_message": delivery.error_message,
            "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to test webhook: {e}")
        raise handle_internal_error(f"Failed to test webhook: {str(e)}")


# Helper functions
async def check_webhook_access(
    webhook: Webhook,
    user_id: str,
    db: AsyncSession
) -> bool:
    """Check if user has access to webhook."""
    # Creator has access
    if webhook.created_by == user_id:
        return True
    
    return False


async def check_webhook_edit_permission(
    webhook: Webhook,
    user_id: str,
    db: AsyncSession
) -> bool:
    """Check if user can edit webhook."""
    # Only creator can edit
    if webhook.created_by == user_id:
        return True
    
    return False


async def cleanup_old_deliveries(
    days_old: int = 30,
    db: AsyncSession = None
) -> int:
    """Clean up old webhook deliveries."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Delete old deliveries
        query = select(WebhookDelivery).where(
            WebhookDelivery.created_at < cutoff_date
        )
        result = await db.execute(query)
        old_deliveries = result.scalars().all()
        
        deleted_count = 0
        for delivery in old_deliveries:
            await db.delete(delivery)
            deleted_count += 1
        
        await db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old webhook deliveries")
        
        return deleted_count
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to cleanup old webhook deliveries: {e}")
        return 0




