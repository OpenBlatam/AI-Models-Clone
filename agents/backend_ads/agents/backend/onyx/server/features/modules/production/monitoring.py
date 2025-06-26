"""
Production Monitoring Module.

Comprehensive monitoring and metrics collection for production systems.
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

import structlog

try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from .config import ProductionSettings

logger = structlog.get_logger(__name__)


@dataclass
class HealthStatus:
    """Health status for a service or component."""
    healthy: bool
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """Collect and manage production metrics."""
    
    def __init__(self, config: ProductionSettings):
        self.config = config
        self.metrics = {}
        
        if PROMETHEUS_AVAILABLE and config.prometheus_enabled:
            self._setup_prometheus_metrics()
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        self.request_count = Counter(
            'production_requests_total',
            'Total requests',
            ['method', 'endpoint', 'status']
        )
        self.request_duration = Histogram(
            'production_request_duration_seconds',
            'Request duration',
            ['method', 'endpoint']
        )
        self.memory_usage = Gauge(
            'production_memory_usage_bytes',
            'Memory usage'
        )
        self.cpu_usage = Gauge(
            'production_cpu_usage_percent',
            'CPU usage'
        )
    
    async def initialize(self):
        """Initialize metrics collection."""
        if PROMETHEUS_AVAILABLE and self.config.prometheus_enabled:
            try:
                start_http_server(self.config.metrics_port)
                logger.info("📊 Prometheus metrics server started", port=self.config.metrics_port)
            except Exception as e:
                logger.warning("Failed to start metrics server", error=str(e))
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record request metrics."""
        if PROMETHEUS_AVAILABLE and hasattr(self, 'request_count'):
            self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
            self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def update_system_metrics(self):
        """Update system metrics."""
        if PROMETHEUS_AVAILABLE and PSUTIL_AVAILABLE:
            try:
                if hasattr(self, 'memory_usage'):
                    self.memory_usage.set(psutil.virtual_memory().used)
                if hasattr(self, 'cpu_usage'):
                    self.cpu_usage.set(psutil.cpu_percent())
            except Exception as e:
                logger.warning("Failed to update system metrics", error=str(e))


class HealthChecker:
    """Comprehensive health checking system."""
    
    def __init__(self, config: ProductionSettings):
        self.config = config
        self.health_status = {}
    
    async def initialize(self):
        """Initialize health checker."""
        logger.info("🏥 Health checker initialized")
    
    async def check_system_health(self) -> HealthStatus:
        """Check overall system health."""
        try:
            if PSUTIL_AVAILABLE:
                memory = psutil.virtual_memory()
                cpu = psutil.cpu_percent()
                
                healthy = memory.percent < 90 and cpu < 90
                
                return HealthStatus(
                    healthy=healthy,
                    message="System healthy" if healthy else "System under stress",
                    details={
                        "memory_percent": memory.percent,
                        "cpu_percent": cpu,
                        "available_memory_gb": memory.available / (1024**3)
                    }
                )
            else:
                return HealthStatus(
                    healthy=True,
                    message="Basic health check passed",
                    details={"psutil_available": False}
                )
        except Exception as e:
            return HealthStatus(
                healthy=False,
                message=f"Health check failed: {e}",
                details={"error": str(e)}
            )
    
    async def check_database_health(self) -> HealthStatus:
        """Check database health."""
        # Placeholder - would implement actual database checks
        return HealthStatus(
            healthy=True,
            message="Database check not implemented",
            details={"database_url": bool(self.config.database_url)}
        )
    
    async def check_redis_health(self) -> HealthStatus:
        """Check Redis health."""
        # Placeholder - would implement actual Redis checks
        return HealthStatus(
            healthy=True,
            message="Redis check not implemented", 
            details={"redis_url": bool(self.config.redis_url)}
        )


class ProductionMonitor:
    """Main production monitoring system."""
    
    def __init__(self, config: ProductionSettings):
        self.config = config
        self.metrics_collector = MetricsCollector(config)
        self.health_checker = HealthChecker(config)
        self.operation_stats = {}
        self.start_time = time.time()
    
    async def initialize(self):
        """Initialize monitoring system."""
        await self.metrics_collector.initialize()
        await self.health_checker.initialize()
        logger.info("📊 Production monitoring initialized")
    
    def record_operation(self, operation: str, duration_ms: float, level: str, success: bool, error: str = None):
        """Record operation metrics."""
        if operation not in self.operation_stats:
            self.operation_stats[operation] = {
                "count": 0,
                "total_time": 0.0,
                "successes": 0,
                "failures": 0,
                "avg_time": 0.0
            }
        
        stats = self.operation_stats[operation]
        stats["count"] += 1
        stats["total_time"] += duration_ms
        stats["avg_time"] = stats["total_time"] / stats["count"]
        
        if success:
            stats["successes"] += 1
        else:
            stats["failures"] += 1
            if error:
                logger.warning("Operation failed", operation=operation, error=error)
    
    async def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        # Update system metrics
        self.metrics_collector.update_system_metrics()
        
        # Get health status
        system_health = await self.health_checker.check_system_health()
        db_health = await self.health_checker.check_database_health()
        redis_health = await self.health_checker.check_redis_health()
        
        return {
            "uptime_seconds": time.time() - self.start_time,
            "health": {
                "system": {
                    "healthy": system_health.healthy,
                    "message": system_health.message,
                    "details": system_health.details
                },
                "database": {
                    "healthy": db_health.healthy,
                    "message": db_health.message
                },
                "redis": {
                    "healthy": redis_health.healthy,
                    "message": redis_health.message
                }
            },
            "operations": self.operation_stats,
            "configuration": {
                "production_level": self.config.production_level.value,
                "environment": self.config.environment.value,
                "monitoring_enabled": self.config.enable_monitoring
            }
        }
    
    async def cleanup(self):
        """Cleanup monitoring resources."""
        logger.info("✅ Production monitoring cleaned up")


def setup_monitoring(app, config: ProductionSettings):
    """Setup monitoring for FastAPI application."""
    monitor = ProductionMonitor(config)
    app.state.monitor = monitor
    return monitor


# Export main components
__all__ = [
    "ProductionMonitor",
    "MetricsCollector", 
    "HealthChecker",
    "HealthStatus",
    "setup_monitoring"
] 