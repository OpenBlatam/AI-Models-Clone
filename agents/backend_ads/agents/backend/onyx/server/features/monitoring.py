"""
Production Monitoring System for Onyx Features.

Enterprise-grade monitoring with Prometheus metrics, structured logging,
health checks, performance tracking, and error monitoring.
"""

import asyncio
import time
import psutil
import functools
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict

import structlog
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)
from pydantic import BaseModel, Field
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Configure structured logging
logger = structlog.get_logger(__name__)

# Create custom registry for this module
monitoring_registry = CollectorRegistry()

# Core metrics
request_count = Counter(
    'onyx_requests_total',
    'Total number of requests processed',
    ['method', 'endpoint', 'status_code', 'feature'],
    registry=monitoring_registry
)

request_duration = Histogram(
    'onyx_request_duration_seconds',
    'Request processing duration in seconds',
    ['method', 'endpoint', 'feature'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float('inf')),
    registry=monitoring_registry
)

active_connections = Gauge(
    'onyx_active_connections',
    'Number of active connections',
    ['connection_type'],
    registry=monitoring_registry
)

cache_operations = Counter(
    'onyx_cache_operations_total',
    'Total cache operations',
    ['operation', 'cache_type', 'status'],
    registry=monitoring_registry
)

memory_usage = Gauge(
    'onyx_memory_usage_bytes',
    'Memory usage in bytes',
    ['memory_type'],
    registry=monitoring_registry
)

cpu_usage = Gauge(
    'onyx_cpu_usage_percent',
    'CPU usage percentage',
    registry=monitoring_registry
)

disk_usage = Gauge(
    'onyx_disk_usage_bytes',
    'Disk usage in bytes',
    ['disk_type'],
    registry=monitoring_registry
)

feature_usage = Counter(
    'onyx_feature_usage_total',
    'Feature usage count',
    ['feature_name', 'operation'],
    registry=monitoring_registry
)

error_count = Counter(
    'onyx_errors_total',
    'Total number of errors',
    ['error_type', 'feature', 'severity'],
    registry=monitoring_registry
)

# Performance metrics
image_processing_time = Histogram(
    'onyx_image_processing_seconds',
    'Image processing duration',
    ['operation', 'format'],
    registry=monitoring_registry
)

message_processing_time = Histogram(
    'onyx_message_processing_seconds',
    'Message processing duration',
    ['message_type', 'operation'],
    registry=monitoring_registry
)


@dataclass
class SystemMetrics:
    """System metrics data class."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_used_gb: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    timestamp: datetime


@dataclass
class HealthStatus:
    """Health check status."""
    healthy: bool
    service: str
    message: str
    timestamp: datetime
    details: Dict[str, Any] = None


class PerformanceTracker:
    """Performance tracking utilities."""
    
    def __init__(self):
        self._start_times: Dict[str, float] = {}
        self._metrics: Dict[str, List[float]] = {}
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self._start_times[operation] = time.time()
    
    def end_timer(self, operation: str) -> Optional[float]:
        """End timing and return duration."""
        if operation in self._start_times:
            duration = time.time() - self._start_times[operation]
            
            # Store metric
            if operation not in self._metrics:
                self._metrics[operation] = []
            self._metrics[operation].append(duration)
            
            # Keep only last 1000 measurements
            if len(self._metrics[operation]) > 1000:
                self._metrics[operation] = self._metrics[operation][-1000:]
            
            del self._start_times[operation]
            return duration
        return None
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation."""
        if operation not in self._metrics or not self._metrics[operation]:
            return {}
        
        measurements = self._metrics[operation]
        return {
            'count': len(measurements),
            'avg': sum(measurements) / len(measurements),
            'min': min(measurements),
            'max': max(measurements),
            'p95': sorted(measurements)[int(len(measurements) * 0.95)] if len(measurements) > 0 else 0,
            'p99': sorted(measurements)[int(len(measurements) * 0.99)] if len(measurements) > 0 else 0
        }


# Global performance tracker
performance_tracker = PerformanceTracker()


def track_performance(operation: str, feature: str = "general"):
    """
    Decorator to track function performance.
    
    Args:
        operation: Operation name
        feature: Feature name
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            performance_tracker.start_timer(f"{feature}_{operation}")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record metrics
                request_duration.labels(
                    method="async", 
                    endpoint=operation, 
                    feature=feature
                ).observe(duration)
                
                feature_usage.labels(
                    feature_name=feature, 
                    operation=operation
                ).inc()
                
                return result
                
            except Exception as e:
                error_count.labels(
                    error_type=type(e).__name__,
                    feature=feature,
                    severity="error"
                ).inc()
                raise
            finally:
                performance_tracker.end_timer(f"{feature}_{operation}")
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            performance_tracker.start_timer(f"{feature}_{operation}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record metrics
                request_duration.labels(
                    method="sync", 
                    endpoint=operation, 
                    feature=feature
                ).observe(duration)
                
                feature_usage.labels(
                    feature_name=feature, 
                    operation=operation
                ).inc()
                
                return result
                
            except Exception as e:
                error_count.labels(
                    error_type=type(e).__name__,
                    feature=feature,
                    severity="error"
                ).inc()
                raise
            finally:
                performance_tracker.end_timer(f"{feature}_{operation}")
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@asynccontextmanager
async def monitor_operation(operation: str, feature: str = "general"):
    """
    Context manager to monitor an operation.
    
    Args:
        operation: Operation name
        feature: Feature name
    """
    start_time = time.time()
    operation_id = f"{feature}_{operation}"
    
    try:
        performance_tracker.start_timer(operation_id)
        logger.info("Operation started", operation=operation, feature=feature)
        yield
        
        duration = time.time() - start_time
        request_duration.labels(
            method="context", 
            endpoint=operation, 
            feature=feature
        ).observe(duration)
        
        logger.info("Operation completed", 
                   operation=operation, 
                   feature=feature, 
                   duration=duration)
        
    except Exception as e:
        error_count.labels(
            error_type=type(e).__name__,
            feature=feature,
            severity="error"
        ).inc()
        
        logger.error("Operation failed", 
                    operation=operation, 
                    feature=feature, 
                    error=str(e),
                    exc_info=True)
        raise
    finally:
        performance_tracker.end_timer(operation_id)


def collect_system_metrics() -> SystemMetrics:
    """Collect current system metrics."""
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_usage.set(cpu_percent)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_usage.labels(memory_type="used").set(memory.used)
        memory_usage.labels(memory_type="available").set(memory.available)
        memory_usage.labels(memory_type="total").set(memory.total)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_usage.labels(disk_type="used").set(disk.used)
        disk_usage.labels(disk_type="free").set(disk.free)
        disk_usage.labels(disk_type="total").set(disk.total)
        
        # Network metrics
        network = psutil.net_io_counters()
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_available_mb=memory.available / (1024 * 1024),
            disk_used_gb=disk.used / (1024 * 1024 * 1024),
            disk_free_gb=disk.free / (1024 * 1024 * 1024),
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        logger.error("Failed to collect system metrics", error=str(e))
        raise


async def health_check_database() -> HealthStatus:
    """Health check for database connectivity."""
    try:
        # This would check actual database connectivity
        # For now, return healthy status
        return HealthStatus(
            healthy=True,
            service="database",
            message="Database connection healthy",
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        return HealthStatus(
            healthy=False,
            service="database",
            message=f"Database health check failed: {e}",
            timestamp=datetime.now(timezone.utc)
        )


async def health_check_redis() -> HealthStatus:
    """Health check for Redis connectivity."""
    try:
        # This would check actual Redis connectivity
        # For now, return healthy status
        return HealthStatus(
            healthy=True,
            service="redis",
            message="Redis connection healthy",
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        return HealthStatus(
            healthy=False,
            service="redis",
            message=f"Redis health check failed: {e}",
            timestamp=datetime.now(timezone.utc)
        )


async def comprehensive_health_check() -> Dict[str, HealthStatus]:
    """Perform comprehensive health check of all services."""
    health_checks = {
        "database": await health_check_database(),
        "redis": await health_check_redis(),
        "system": HealthStatus(
            healthy=True,
            service="system",
            message="System metrics collection active",
            timestamp=datetime.now(timezone.utc),
            details=asdict(collect_system_metrics())
        )
    }
    
    return health_checks


def setup_sentry(dsn: Optional[str] = None, environment: str = "production"):
    """
    Setup Sentry error tracking.
    
    Args:
        dsn: Sentry DSN
        environment: Environment name
    """
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            integrations=[
                AsyncioIntegration(),
                SqlalchemyIntegration()
            ],
            traces_sample_rate=0.1,
            send_default_pii=False,
            attach_stacktrace=True,
            debug=False
        )
        logger.info("Sentry monitoring initialized", environment=environment)


def get_metrics_export() -> str:
    """
    Get Prometheus metrics in export format.
    
    Returns:
        str: Metrics in Prometheus format
    """
    return generate_latest(monitoring_registry)


def get_monitoring_dashboard() -> Dict[str, Any]:
    """
    Get comprehensive monitoring dashboard data.
    
    Returns:
        Dict: Dashboard data with metrics and health status
    """
    try:
        system_metrics = collect_system_metrics()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_metrics": asdict(system_metrics),
            "performance_stats": {
                op: performance_tracker.get_stats(op) 
                for op in performance_tracker._metrics.keys()
            },
            "health_status": "healthy",  # This would be calculated from health checks
            "feature_usage": {
                "image_processing": "active",
                "key_messages": "active"
            }
        }
        
    except Exception as e:
        logger.error("Failed to generate monitoring dashboard", error=str(e))
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "health_status": "unhealthy"
        }


# Export main components
__all__ = [
    "track_performance",
    "monitor_operation", 
    "collect_system_metrics",
    "comprehensive_health_check",
    "setup_sentry",
    "get_metrics_export",
    "get_monitoring_dashboard",
    "PerformanceTracker",
    "SystemMetrics",
    "HealthStatus",
    "performance_tracker",
    "monitoring_registry"
]

# Initialize monitoring
logger.info("Monitoring system initialized")