"""
Audit service following functional patterns
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
import uuid
import json

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error, handle_not_found_error
from app.models.audit import AuditLog, AuditEvent, AuditTrail
from app.schemas.audit import (
    AuditLogResponse, AuditEventResponse, AuditTrailResponse,
    AuditSearchRequest, AuditStatsResponse
)
from app.utils.validators import validate_audit_search_params
from app.utils.helpers import generate_audit_id, sanitize_audit_data
from app.utils.cache import cache_audit_data, get_cached_audit_data, invalidate_audit_cache

logger = get_logger(__name__)


async def create_audit_log(
    event_type: str,
    user_id: str,
    resource_type: str,
    resource_id: str,
    action: str,
    details: Dict[str, Any],
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: AsyncSession = None
) -> AuditLogResponse:
    """Create an audit log entry."""
    try:
        # Sanitize audit data
        sanitized_details = sanitize_audit_data(details)
        
        # Create audit log
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=sanitized_details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        
        # Cache audit data
        cache_audit_data(str(audit_log.id), audit_log)
        
        logger.info(f"Audit log created: {audit_log.id} for {action} on {resource_type}")
        
        return AuditLogResponse.from_orm(audit_log)
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create audit log: {e}")
        raise handle_internal_error(f"Failed to create audit log: {str(e)}")


async def get_audit_log(
    audit_id: str,
    user_id: str,
    db: AsyncSession
) -> AuditLogResponse:
    """Get audit log by ID."""
    try:
        # Check cache first
        cached_audit = get_cached_audit_data(audit_id)
        if cached_audit:
            return AuditLogResponse.from_orm(cached_audit)
        
        # Get from database
        query = select(AuditLog).where(AuditLog.id == audit_id)
        result = await db.execute(query)
        audit_log = result.scalar_one_or_none()
        
        if not audit_log:
            raise handle_not_found_error("Audit log", audit_id)
        
        # Check access permissions
        has_access = await check_audit_access(audit_log, user_id, db)
        if not has_access:
            raise handle_forbidden_error("Access denied to audit log")
        
        # Cache audit data
        cache_audit_data(audit_id, audit_log)
        
        return AuditLogResponse.from_orm(audit_log)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get audit log: {e}")
        raise handle_internal_error(f"Failed to get audit log: {str(e)}")


async def search_audit_logs(
    search_params: AuditSearchRequest,
    user_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """Search audit logs with filtering and pagination."""
    try:
        # Validate search parameters
        validation = validate_audit_search_params(search_params)
        if not validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid search parameters: {', '.join(validation['errors'])}")
            )
        
        # Build query
        query = select(AuditLog)
        
        # Apply filters
        if search_params.event_type:
            query = query.where(AuditLog.event_type == search_params.event_type)
        
        if search_params.user_id:
            query = query.where(AuditLog.user_id == search_params.user_id)
        
        if search_params.resource_type:
            query = query.where(AuditLog.resource_type == search_params.resource_type)
        
        if search_params.resource_id:
            query = query.where(AuditLog.resource_id == search_params.resource_id)
        
        if search_params.action:
            query = query.where(AuditLog.action == search_params.action)
        
        if search_params.date_from:
            query = query.where(AuditLog.timestamp >= search_params.date_from)
        
        if search_params.date_to:
            query = query.where(AuditLog.timestamp <= search_params.date_to)
        
        if search_params.ip_address:
            query = query.where(AuditLog.ip_address == search_params.ip_address)
        
        if search_params.query:
            search_filter = or_(
                AuditLog.details.ilike(f"%{search_params.query}%"),
                AuditLog.action.ilike(f"%{search_params.query}%")
            )
            query = query.where(search_filter)
        
        # Apply access control
        access_filter = await get_audit_access_filter(user_id, db)
        query = query.where(access_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(AuditLog.timestamp)).offset(
            (search_params.page - 1) * search_params.size
        ).limit(search_params.size)
        
        # Execute query
        result = await db.execute(query)
        audit_logs = result.scalars().all()
        
        # Convert to response format
        audit_responses = [AuditLogResponse.from_orm(log) for log in audit_logs]
        
        return {
            "audit_logs": audit_responses,
            "total": total,
            "page": search_params.page,
            "size": search_params.size,
            "pages": (total + search_params.size - 1) // search_params.size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search audit logs: {e}")
        raise handle_internal_error(f"Failed to search audit logs: {str(e)}")


async def get_audit_trail(
    resource_type: str,
    resource_id: str,
    user_id: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get audit trail for a specific resource."""
    try:
        # Build query
        query = select(AuditLog).where(
            and_(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id
            )
        )
        
        # Apply access control
        access_filter = await get_audit_access_filter(user_id, db)
        query = query.where(access_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(AuditLog.timestamp)).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(query)
        audit_logs = result.scalars().all()
        
        # Convert to response format
        audit_responses = [AuditLogResponse.from_orm(log) for log in audit_logs]
        
        return {
            "audit_trail": audit_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except Exception as e:
        logger.error(f"Failed to get audit trail: {e}")
        raise handle_internal_error(f"Failed to get audit trail: {str(e)}")


async def get_audit_stats(
    user_id: str,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = None
) -> AuditStatsResponse:
    """Get audit statistics."""
    try:
        # Set default date range if not provided
        if not date_to:
            date_to = datetime.utcnow()
        if not date_from:
            date_from = date_to - timedelta(days=30)
        
        # Build base query
        base_query = select(AuditLog).where(
            and_(
                AuditLog.timestamp >= date_from,
                AuditLog.timestamp <= date_to
            )
        )
        
        # Apply access control
        access_filter = await get_audit_access_filter(user_id, db)
        base_query = base_query.where(access_filter)
        
        # Get total audit logs
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(total_query)
        total_logs = total_result.scalar()
        
        # Get audit logs by event type
        event_type_query = select(
            AuditLog.event_type,
            func.count(AuditLog.id).label('count')
        ).select_from(base_query.subquery()).group_by(AuditLog.event_type)
        
        event_type_result = await db.execute(event_type_query)
        event_type_stats = {row[0]: row[1] for row in event_type_result.fetchall()}
        
        # Get audit logs by action
        action_query = select(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).select_from(base_query.subquery()).group_by(AuditLog.action)
        
        action_result = await db.execute(action_query)
        action_stats = {row[0]: row[1] for row in action_result.fetchall()}
        
        # Get audit logs by resource type
        resource_type_query = select(
            AuditLog.resource_type,
            func.count(AuditLog.id).label('count')
        ).select_from(base_query.subquery()).group_by(AuditLog.resource_type)
        
        resource_type_result = await db.execute(resource_type_query)
        resource_type_stats = {row[0]: row[1] for row in resource_type_result.fetchall()}
        
        # Get audit logs by user
        user_query = select(
            AuditLog.user_id,
            func.count(AuditLog.id).label('count')
        ).select_from(base_query.subquery()).group_by(AuditLog.user_id)
        
        user_result = await db.execute(user_query)
        user_stats = {str(row[0]): row[1] for row in user_result.fetchall()}
        
        # Get audit logs by date
        date_query = select(
            func.date(AuditLog.timestamp).label('date'),
            func.count(AuditLog.id).label('count')
        ).select_from(base_query.subquery()).group_by(
            func.date(AuditLog.timestamp)
        ).order_by(func.date(AuditLog.timestamp))
        
        date_result = await db.execute(date_query)
        date_stats = {row[0].isoformat(): row[1] for row in date_result.fetchall()}
        
        # Get recent audit logs
        recent_query = base_query.order_by(desc(AuditLog.timestamp)).limit(10)
        recent_result = await db.execute(recent_query)
        recent_logs = [AuditLogResponse.from_orm(log) for log in recent_result.scalars().all()]
        
        return AuditStatsResponse(
            total_logs=total_logs,
            event_type_stats=event_type_stats,
            action_stats=action_stats,
            resource_type_stats=resource_type_stats,
            user_stats=user_stats,
            date_stats=date_stats,
            recent_logs=recent_logs,
            period_start=date_from,
            period_end=date_to
        )
    
    except Exception as e:
        logger.error(f"Failed to get audit stats: {e}")
        raise handle_internal_error(f"Failed to get audit stats: {str(e)}")


async def create_audit_event(
    event_type: str,
    user_id: str,
    event_data: Dict[str, Any],
    db: AsyncSession
) -> AuditEventResponse:
    """Create an audit event."""
    try:
        # Sanitize event data
        sanitized_data = sanitize_audit_data(event_data)
        
        # Create audit event
        audit_event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            event_data=sanitized_data,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_event)
        await db.commit()
        await db.refresh(audit_event)
        
        # Cache audit data
        cache_audit_data(str(audit_event.id), audit_event)
        
        logger.info(f"Audit event created: {audit_event.id} for {event_type}")
        
        return AuditEventResponse.from_orm(audit_event)
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create audit event: {e}")
        raise handle_internal_error(f"Failed to create audit event: {str(e)}")


async def get_audit_events(
    user_id: str,
    event_type: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get audit events."""
    try:
        # Build query
        query = select(AuditEvent)
        
        # Apply filters
        if event_type:
            query = query.where(AuditEvent.event_type == event_type)
        
        # Apply access control
        access_filter = await get_audit_access_filter(user_id, db)
        query = query.where(access_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(AuditEvent.timestamp)).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(query)
        audit_events = result.scalars().all()
        
        # Convert to response format
        event_responses = [AuditEventResponse.from_orm(event) for event in audit_events]
        
        return {
            "audit_events": event_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except Exception as e:
        logger.error(f"Failed to get audit events: {e}")
        raise handle_internal_error(f"Failed to get audit events: {str(e)}")


async def export_audit_logs(
    user_id: str,
    export_format: str,
    search_params: AuditSearchRequest,
    db: AsyncSession
) -> Dict[str, Any]:
    """Export audit logs in specified format."""
    try:
        # Get audit logs
        search_result = await search_audit_logs(search_params, user_id, db)
        audit_logs = search_result["audit_logs"]
        
        # Convert to export format
        if export_format == "json":
            export_data = [log.dict() for log in audit_logs]
        elif export_format == "csv":
            export_data = convert_audit_logs_to_csv(audit_logs)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        # Generate export file
        export_filename = f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{export_format}"
        export_path = os.path.join("exports", export_filename)
        
        # Ensure export directory exists
        os.makedirs("exports", exist_ok=True)
        
        # Write export file
        if export_format == "json":
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        elif export_format == "csv":
            with open(export_path, 'w', newline='') as f:
                f.write(export_data)
        
        return {
            "export_filename": export_filename,
            "export_path": export_path,
            "total_records": len(audit_logs),
            "format": export_format
        }
    
    except Exception as e:
        logger.error(f"Failed to export audit logs: {e}")
        raise handle_internal_error(f"Failed to export audit logs: {str(e)}")


async def cleanup_old_audit_logs(
    days_old: int = 90,
    db: AsyncSession = None
) -> int:
    """Clean up old audit logs."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Delete old audit logs
        query = select(AuditLog).where(AuditLog.timestamp < cutoff_date)
        result = await db.execute(query)
        old_logs = result.scalars().all()
        
        deleted_count = 0
        for log in old_logs:
            await db.delete(log)
            deleted_count += 1
        
        await db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old audit logs")
        
        return deleted_count
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to cleanup old audit logs: {e}")
        return 0


# Helper functions
async def check_audit_access(
    audit_log: AuditLog,
    user_id: str,
    db: AsyncSession
) -> bool:
    """Check if user has access to audit log."""
    # User can access their own audit logs
    if audit_log.user_id == user_id:
        return True
    
    # Check if user is admin or has audit access
    from app.core.auth_utils import get_user_by_id
    user = await get_user_by_id(db, user_id)
    if user and user.is_superuser:
        return True
    
    return False


async def get_audit_access_filter(
    user_id: str,
    db: AsyncSession
) -> Any:
    """Get audit access filter for user."""
    # Check if user is admin
    from app.core.auth_utils import get_user_by_id
    user = await get_user_by_id(db, user_id)
    
    if user and user.is_superuser:
        # Admin can see all audit logs
        return True
    else:
        # Regular users can only see their own audit logs
        return AuditLog.user_id == user_id


def convert_audit_logs_to_csv(audit_logs: List[AuditLogResponse]) -> str:
    """Convert audit logs to CSV format."""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Event Type', 'User ID', 'Resource Type', 'Resource ID',
        'Action', 'IP Address', 'User Agent', 'Timestamp', 'Details'
    ])
    
    # Write data
    for log in audit_logs:
        writer.writerow([
            str(log.id),
            log.event_type,
            str(log.user_id),
            log.resource_type,
            log.resource_id,
            log.action,
            log.ip_address or '',
            log.user_agent or '',
            log.timestamp.isoformat(),
            json.dumps(log.details) if log.details else ''
        ])
    
    return output.getvalue()


async def log_user_action(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    details: Dict[str, Any],
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: AsyncSession = None
) -> None:
    """Log a user action."""
    try:
        await create_audit_log(
            event_type="user_action",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            db=db
        )
    except Exception as e:
        logger.error(f"Failed to log user action: {e}")


async def log_system_event(
    event_type: str,
    event_data: Dict[str, Any],
    db: AsyncSession
) -> None:
    """Log a system event."""
    try:
        await create_audit_event(
            event_type=event_type,
            user_id="system",
            event_data=event_data,
            db=db
        )
    except Exception as e:
        logger.error(f"Failed to log system event: {e}")


async def log_security_event(
    event_type: str,
    user_id: str,
    details: Dict[str, Any],
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: AsyncSession = None
) -> None:
    """Log a security event."""
    try:
        await create_audit_log(
            event_type="security",
            user_id=user_id,
            resource_type="security",
            resource_id=event_type,
            action=event_type,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            db=db
        )
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")




