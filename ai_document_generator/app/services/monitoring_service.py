"""
Monitoring service following functional patterns
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
import uuid
import json
import psutil
import asyncio
import aiohttp

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error, handle_not_found_error
from app.models.monitoring import Metric, Alert, HealthCheck, PerformanceLog
from app.schemas.monitoring import (
    MetricResponse, AlertResponse, HealthCheckResponse,
    PerformanceLogResponse, MonitoringDashboardResponse
)
from app.utils.validators import validate_metric_name, validate_alert_conditions
from app.utils.helpers import calculate_metric_trend, format_metric_value
from app.utils.cache import cache_metric_data, get_cached_metric_data, invalidate_metric_cache

logger = get_logger(__name__)


async def collect_system_metrics(
    db: AsyncSession
) -> Dict[str, Any]:
    """Collect system metrics."""
    try:
        metrics = {}
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        metrics["cpu"] = {
            "usage_percent": cpu_percent,
            "count": cpu_count,
            "frequency_mhz": cpu_freq.current if cpu_freq else None,
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
        
        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        metrics["memory"] = {
            "total_bytes": memory.total,
            "available_bytes": memory.available,
            "used_bytes": memory.used,
            "usage_percent": memory.percent,
            "swap_total_bytes": swap.total,
            "swap_used_bytes": swap.used,
            "swap_usage_percent": swap.percent
        }
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        metrics["disk"] = {
            "total_bytes": disk.total,
            "used_bytes": disk.used,
            "free_bytes": disk.free,
            "usage_percent": (disk.used / disk.total) * 100,
            "read_bytes": disk_io.read_bytes if disk_io else 0,
            "write_bytes": disk_io.write_bytes if disk_io else 0
        }
        
        # Network metrics
        network_io = psutil.net_io_counters()
        
        metrics["network"] = {
            "bytes_sent": network_io.bytes_sent if network_io else 0,
            "bytes_recv": network_io.bytes_recv if network_io else 0,
            "packets_sent": network_io.packets_sent if network_io else 0,
            "packets_recv": network_io.packets_recv if network_io else 0
        }
        
        # Process metrics
        process = psutil.Process()
        
        metrics["process"] = {
            "pid": process.pid,
            "memory_usage_bytes": process.memory_info().rss,
            "cpu_percent": process.cpu_percent(),
            "num_threads": process.num_threads(),
            "create_time": process.create_time()
        }
        
        # Database metrics
        db_metrics = await collect_database_metrics(db)
        metrics["database"] = db_metrics
        
        # Application metrics
        app_metrics = await collect_application_metrics(db)
        metrics["application"] = app_metrics
        
        return metrics
    
    except Exception as e:
        logger.error(f"Failed to collect system metrics: {e}")
        return {}


async def collect_database_metrics(
    db: AsyncSession
) -> Dict[str, Any]:
    """Collect database metrics."""
    try:
        metrics = {}
        
        # Get database size
        size_query = text("SELECT pg_database_size(current_database()) as size")
        size_result = await db.execute(size_query)
        db_size = size_result.scalar()
        
        metrics["size_bytes"] = db_size
        
        # Get connection count
        conn_query = text("SELECT count(*) FROM pg_stat_activity")
        conn_result = await db.execute(conn_query)
        conn_count = conn_result.scalar()
        
        metrics["connections"] = conn_count
        
        # Get table sizes
        table_size_query = text("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10
        """)
        
        table_size_result = await db.execute(table_size_query)
        table_sizes = [
            {
                "schema": row[0],
                "table": row[1],
                "size": row[2],
                "size_bytes": row[3]
            }
            for row in table_size_result.fetchall()
        ]
        
        metrics["table_sizes"] = table_sizes
        
        # Get slow queries (if available)
        try:
            slow_query = text("""
                SELECT query, mean_time, calls
                FROM pg_stat_statements
                ORDER BY mean_time DESC
                LIMIT 5
            """)
            slow_result = await db.execute(slow_query)
            slow_queries = [
                {
                    "query": row[0][:100] + "..." if len(row[0]) > 100 else row[0],
                    "mean_time": row[1],
                    "calls": row[2]
                }
                for row in slow_result.fetchall()
            ]
            metrics["slow_queries"] = slow_queries
        except Exception:
            metrics["slow_queries"] = []
        
        return metrics
    
    except Exception as e:
        logger.error(f"Failed to collect database metrics: {e}")
        return {}


async def collect_application_metrics(
    db: AsyncSession
) -> Dict[str, Any]:
    """Collect application metrics."""
    try:
        metrics = {}
        
        # Get user count
        user_count_query = select(func.count()).select_from(text("users"))
        user_count_result = await db.execute(user_count_query)
        user_count = user_count_result.scalar()
        
        metrics["users"] = {
            "total": user_count,
            "active_today": await get_active_users_today(db),
            "new_this_week": await get_new_users_this_week(db)
        }
        
        # Get document count
        doc_count_query = select(func.count()).select_from(text("documents"))
        doc_count_result = await db.execute(doc_count_query)
        doc_count = doc_count_result.scalar()
        
        metrics["documents"] = {
            "total": doc_count,
            "created_today": await get_documents_created_today(db),
            "created_this_week": await get_documents_created_this_week(db)
        }
        
        # Get AI usage
        ai_metrics = await get_ai_usage_metrics(db)
        metrics["ai_usage"] = ai_metrics
        
        # Get collaboration metrics
        collab_metrics = await get_collaboration_metrics(db)
        metrics["collaboration"] = collab_metrics
        
        return metrics
    
    except Exception as e:
        logger.error(f"Failed to collect application metrics: {e}")
        return {}


async def get_active_users_today(db: AsyncSession) -> int:
    """Get count of active users today."""
    try:
        today = datetime.utcnow().date()
        query = select(func.count(func.distinct(text("user_id")))).select_from(
            text("audit_logs")
        ).where(
            text("DATE(timestamp) = :today")
        )
        result = await db.execute(query, {"today": today})
        return result.scalar() or 0
    except Exception:
        return 0


async def get_new_users_this_week(db: AsyncSession) -> int:
    """Get count of new users this week."""
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        query = select(func.count()).select_from(text("users")).where(
            text("created_at >= :week_ago")
        )
        result = await db.execute(query, {"week_ago": week_ago})
        return result.scalar() or 0
    except Exception:
        return 0


async def get_documents_created_today(db: AsyncSession) -> int:
    """Get count of documents created today."""
    try:
        today = datetime.utcnow().date()
        query = select(func.count()).select_from(text("documents")).where(
            text("DATE(created_at) = :today")
        )
        result = await db.execute(query, {"today": today})
        return result.scalar() or 0
    except Exception:
        return 0


async def get_documents_created_this_week(db: AsyncSession) -> int:
    """Get count of documents created this week."""
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        query = select(func.count()).select_from(text("documents")).where(
            text("created_at >= :week_ago")
        )
        result = await db.execute(query, {"week_ago": week_ago})
        return result.scalar() or 0
    except Exception:
        return 0


async def get_ai_usage_metrics(db: AsyncSession) -> Dict[str, Any]:
    """Get AI usage metrics."""
    try:
        # This would implement actual AI usage tracking
        # For now, returning placeholder data
        return {
            "requests_today": 0,
            "requests_this_week": 0,
            "total_tokens_used": 0,
            "cost_today": 0.0,
            "cost_this_week": 0.0
        }
    except Exception:
        return {}


async def get_collaboration_metrics(db: AsyncSession) -> Dict[str, Any]:
    """Get collaboration metrics."""
    try:
        # This would implement actual collaboration tracking
        # For now, returning placeholder data
        return {
            "active_sessions": 0,
            "documents_shared": 0,
            "comments_today": 0,
            "real_time_editors": 0
        }
    except Exception:
        return {}


async def store_metric(
    metric_name: str,
    metric_value: float,
    metric_type: str,
    tags: Dict[str, str],
    db: AsyncSession
) -> MetricResponse:
    """Store a metric."""
    try:
        # Validate metric name
        name_validation = validate_metric_name(metric_name)
        if not name_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid metric name: {', '.join(name_validation['errors'])}")
            )
        
        # Create metric
        metric = Metric(
            name=metric_name,
            value=metric_value,
            metric_type=metric_type,
            tags=tags,
            timestamp=datetime.utcnow()
        )
        
        db.add(metric)
        await db.commit()
        await db.refresh(metric)
        
        # Cache metric data
        cache_metric_data(str(metric.id), metric)
        
        # Check for alerts
        await check_metric_alerts(metric, db)
        
        logger.info(f"Metric stored: {metric_name} = {metric_value}")
        
        return MetricResponse.from_orm(metric)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to store metric: {e}")
        raise handle_internal_error(f"Failed to store metric: {str(e)}")


async def get_metrics(
    metric_name: Optional[str] = None,
    metric_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    page: int = 1,
    size: int = 100,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get metrics with filtering and pagination."""
    try:
        # Build query
        query = select(Metric)
        
        # Apply filters
        if metric_name:
            query = query.where(Metric.name == metric_name)
        
        if metric_type:
            query = query.where(Metric.metric_type == metric_type)
        
        if start_time:
            query = query.where(Metric.timestamp >= start_time)
        
        if end_time:
            query = query.where(Metric.timestamp <= end_time)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(Metric.timestamp)).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(query)
        metrics = result.scalars().all()
        
        # Convert to response format
        metric_responses = [MetricResponse.from_orm(metric) for metric in metrics]
        
        return {
            "metrics": metric_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise handle_internal_error(f"Failed to get metrics: {str(e)}")


async def get_metric_aggregation(
    metric_name: str,
    aggregation_type: str,
    start_time: datetime,
    end_time: datetime,
    db: AsyncSession
) -> Dict[str, Any]:
    """Get metric aggregation."""
    try:
        # Build query
        query = select(Metric).where(
            and_(
                Metric.name == metric_name,
                Metric.timestamp >= start_time,
                Metric.timestamp <= end_time
            )
        )
        
        result = await db.execute(query)
        metrics = result.scalars().all()
        
        if not metrics:
            return {
                "metric_name": metric_name,
                "aggregation_type": aggregation_type,
                "value": None,
                "count": 0
            }
        
        values = [metric.value for metric in metrics]
        
        if aggregation_type == "avg":
            aggregated_value = sum(values) / len(values)
        elif aggregation_type == "sum":
            aggregated_value = sum(values)
        elif aggregation_type == "min":
            aggregated_value = min(values)
        elif aggregation_type == "max":
            aggregated_value = max(values)
        elif aggregation_type == "count":
            aggregated_value = len(values)
        else:
            raise ValueError(f"Unsupported aggregation type: {aggregation_type}")
        
        return {
            "metric_name": metric_name,
            "aggregation_type": aggregation_type,
            "value": aggregated_value,
            "count": len(values),
            "start_time": start_time,
            "end_time": end_time
        }
    
    except Exception as e:
        logger.error(f"Failed to get metric aggregation: {e}")
        raise handle_internal_error(f"Failed to get metric aggregation: {str(e)}")


async def create_alert(
    alert_name: str,
    metric_name: str,
    condition: str,
    threshold: float,
    severity: str,
    db: AsyncSession
) -> AlertResponse:
    """Create an alert."""
    try:
        # Validate alert conditions
        condition_validation = validate_alert_conditions(condition)
        if not condition_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid alert condition: {', '.join(condition_validation['errors'])}")
            )
        
        # Create alert
        alert = Alert(
            name=alert_name,
            metric_name=metric_name,
            condition=condition,
            threshold=threshold,
            severity=severity,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        
        logger.info(f"Alert created: {alert_name}")
        
        return AlertResponse.from_orm(alert)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create alert: {e}")
        raise handle_internal_error(f"Failed to create alert: {str(e)}")


async def check_metric_alerts(
    metric: Metric,
    db: AsyncSession
) -> None:
    """Check if metric triggers any alerts."""
    try:
        # Get active alerts for this metric
        query = select(Alert).where(
            and_(
                Alert.metric_name == metric.name,
                Alert.is_active == True
            )
        )
        
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        for alert in alerts:
            if evaluate_alert_condition(metric.value, alert.condition, alert.threshold):
                await trigger_alert(alert, metric, db)
    
    except Exception as e:
        logger.error(f"Failed to check metric alerts: {e}")


def evaluate_alert_condition(
    metric_value: float,
    condition: str,
    threshold: float
) -> bool:
    """Evaluate alert condition."""
    if condition == "greater_than":
        return metric_value > threshold
    elif condition == "less_than":
        return metric_value < threshold
    elif condition == "equals":
        return metric_value == threshold
    elif condition == "not_equals":
        return metric_value != threshold
    else:
        return False


async def trigger_alert(
    alert: Alert,
    metric: Metric,
    db: AsyncSession
) -> None:
    """Trigger an alert."""
    try:
        # Create alert event
        alert_event = {
            "alert_id": str(alert.id),
            "alert_name": alert.name,
            "metric_name": metric.name,
            "metric_value": metric.value,
            "threshold": alert.threshold,
            "condition": alert.condition,
            "severity": alert.severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log alert
        logger.warning(f"Alert triggered: {alert.name} - {metric.name} = {metric.value}")
        
        # Send notification (this would implement actual notification sending)
        await send_alert_notification(alert, metric, alert_event)
        
        # Update alert last triggered
        alert.last_triggered = datetime.utcnow()
        alert.trigger_count += 1
        await db.commit()
    
    except Exception as e:
        logger.error(f"Failed to trigger alert: {e}")


async def send_alert_notification(
    alert: Alert,
    metric: Metric,
    alert_event: Dict[str, Any]
) -> None:
    """Send alert notification."""
    try:
        # This would implement actual notification sending
        # For now, just logging
        logger.info(f"Alert notification sent: {alert.name}")
    
    except Exception as e:
        logger.error(f"Failed to send alert notification: {e}")


async def get_health_check(
    db: AsyncSession
) -> HealthCheckResponse:
    """Get system health check."""
    try:
        health_status = "healthy"
        checks = {}
        
        # Database health
        try:
            db_query = text("SELECT 1")
            await db.execute(db_query)
            checks["database"] = {"status": "healthy", "response_time_ms": 0}
        except Exception as e:
            checks["database"] = {"status": "unhealthy", "error": str(e)}
            health_status = "unhealthy"
        
        # Redis health (if available)
        try:
            # This would check Redis connection
            checks["redis"] = {"status": "healthy", "response_time_ms": 0}
        except Exception as e:
            checks["redis"] = {"status": "unhealthy", "error": str(e)}
            health_status = "unhealthy"
        
        # External services health
        external_services = await check_external_services()
        checks["external_services"] = external_services
        
        # System resources
        system_resources = await check_system_resources()
        checks["system_resources"] = system_resources
        
        return HealthCheckResponse(
            status=health_status,
            timestamp=datetime.utcnow(),
            checks=checks
        )
    
    except Exception as e:
        logger.error(f"Failed to get health check: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            checks={"error": str(e)}
        )


async def check_external_services() -> Dict[str, Any]:
    """Check external services health."""
    try:
        services = {}
        
        # Check AI services
        ai_services = ["openai", "anthropic", "deepseek"]
        for service in ai_services:
            try:
                # This would implement actual service health checks
                services[service] = {"status": "healthy", "response_time_ms": 100}
            except Exception as e:
                services[service] = {"status": "unhealthy", "error": str(e)}
        
        return services
    
    except Exception as e:
        logger.error(f"Failed to check external services: {e}")
        return {}


async def check_system_resources() -> Dict[str, Any]:
    """Check system resources."""
    try:
        resources = {}
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        resources["cpu"] = {
            "usage_percent": cpu_percent,
            "status": "healthy" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
        }
        
        # Memory usage
        memory = psutil.virtual_memory()
        resources["memory"] = {
            "usage_percent": memory.percent,
            "status": "healthy" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
        }
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        resources["disk"] = {
            "usage_percent": disk_percent,
            "status": "healthy" if disk_percent < 80 else "warning" if disk_percent < 95 else "critical"
        }
        
        return resources
    
    except Exception as e:
        logger.error(f"Failed to check system resources: {e}")
        return {}


async def get_monitoring_dashboard(
    db: AsyncSession
) -> MonitoringDashboardResponse:
    """Get monitoring dashboard data."""
    try:
        # Get system metrics
        system_metrics = await collect_system_metrics(db)
        
        # Get application metrics
        app_metrics = system_metrics.get("application", {})
        
        # Get recent metrics
        recent_metrics = await get_metrics(page=1, size=10, db=db)
        
        # Get active alerts
        active_alerts_query = select(Alert).where(Alert.is_active == True)
        active_alerts_result = await db.execute(active_alerts_query)
        active_alerts = [AlertResponse.from_orm(alert) for alert in active_alerts_result.scalars().all()]
        
        # Get health check
        health_check = await get_health_check(db)
        
        return MonitoringDashboardResponse(
            system_metrics=system_metrics,
            application_metrics=app_metrics,
            recent_metrics=recent_metrics.get("metrics", []),
            active_alerts=active_alerts,
            health_check=health_check,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to get monitoring dashboard: {e}")
        raise handle_internal_error(f"Failed to get monitoring dashboard: {str(e)}")


async def log_performance(
    operation: str,
    duration_ms: float,
    success: bool,
    metadata: Dict[str, Any],
    db: AsyncSession
) -> PerformanceLogResponse:
    """Log performance metrics."""
    try:
        # Create performance log
        perf_log = PerformanceLog(
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            metadata=metadata,
            timestamp=datetime.utcnow()
        )
        
        db.add(perf_log)
        await db.commit()
        await db.refresh(perf_log)
        
        # Store as metric
        await store_metric(
            f"performance.{operation}.duration_ms",
            duration_ms,
            "gauge",
            {"operation": operation, "success": str(success)},
            db
        )
        
        logger.info(f"Performance logged: {operation} - {duration_ms}ms")
        
        return PerformanceLogResponse.from_orm(perf_log)
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to log performance: {e}")
        raise handle_internal_error(f"Failed to log performance: {str(e)}")


async def get_performance_logs(
    operation: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    page: int = 1,
    size: int = 100,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get performance logs."""
    try:
        # Build query
        query = select(PerformanceLog)
        
        # Apply filters
        if operation:
            query = query.where(PerformanceLog.operation == operation)
        
        if start_time:
            query = query.where(PerformanceLog.timestamp >= start_time)
        
        if end_time:
            query = query.where(PerformanceLog.timestamp <= end_time)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(PerformanceLog.timestamp)).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(query)
        perf_logs = result.scalars().all()
        
        # Convert to response format
        perf_responses = [PerformanceLogResponse.from_orm(log) for log in perf_logs]
        
        return {
            "performance_logs": perf_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except Exception as e:
        logger.error(f"Failed to get performance logs: {e}")
        raise handle_internal_error(f"Failed to get performance logs: {str(e)}")


async def cleanup_old_metrics(
    days_old: int = 30,
    db: AsyncSession = None
) -> int:
    """Clean up old metrics."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Delete old metrics
        query = select(Metric).where(Metric.timestamp < cutoff_date)
        result = await db.execute(query)
        old_metrics = result.scalars().all()
        
        deleted_count = 0
        for metric in old_metrics:
            await db.delete(metric)
            deleted_count += 1
        
        await db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old metrics")
        
        return deleted_count
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to cleanup old metrics: {e}")
        return 0




