"""
Health Monitoring for Enhanced Blaze AI.

This module provides comprehensive health checking capabilities.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class ServiceStatus(Enum):
    """Service status enumeration."""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    OUTAGE = "outage"
    MAINTENANCE = "maintenance"

@dataclass
class ServiceHealth:
    """Individual service health information."""
    name: str
    status: ServiceStatus
    response_time: Optional[float] = None
    last_check: Optional[datetime] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class SystemHealth:
    """Complete system health information."""
    overall_status: HealthStatus
    timestamp: datetime
    uptime: float
    services: List[ServiceHealth]
    system_metrics: Dict[str, Any]
    version: str = "2.1.0"

class HealthChecker:
    """Health checker for system components."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the health checker."""
        self.config = config or {}
        self.services = {}
        self.last_check = None
        self.check_interval = self.config.get('check_interval', 30)
        
    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """Check health of a specific service."""
        try:
            start_time = time.time()
            
            if service_name == "database":
                health = await self._check_database_health()
            elif service_name == "cache":
                health = await self._check_cache_health()
            elif service_name == "api":
                health = await self._check_api_health()
            else:
                health = ServiceHealth(
                    name=service_name,
                    status=ServiceStatus.UNKNOWN,
                    error_message="Unknown service"
                )
            
            health.response_time = time.time() - start_time
            health.last_check = datetime.now()
            
            return health
            
        except Exception as e:
            logger.error(f"Error checking {service_name} health: {e}")
            return ServiceHealth(
                name=service_name,
                status=ServiceStatus.OUTAGE,
                error_message=str(e),
                last_check=datetime.now()
            )
    
    async def _check_database_health(self) -> ServiceHealth:
        """Check database health."""
        # Simulate database health check
        await asyncio.sleep(0.1)
        return ServiceHealth(
            name="database",
            status=ServiceStatus.OPERATIONAL,
            details={"connections": 5, "active_queries": 2}
        )
    
    async def _check_cache_health(self) -> ServiceHealth:
        """Check cache health."""
        try:
            # Try to connect to Redis if available
            redis_client = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=1)
            redis_client.ping()
            redis_client.close()
            
            return ServiceHealth(
                name="cache",
                status=ServiceStatus.OPERATIONAL,
                details={"type": "redis", "connected": True}
            )
        except Exception as e:
            return ServiceHealth(
                name="cache",
                status=ServiceStatus.DEGRADED,
                error_message=f"Cache connection failed: {e}",
                details={"type": "redis", "connected": False}
            )
    
    async def _check_api_health(self) -> ServiceHealth:
        """Check API health."""
        # Simulate API health check
        await asyncio.sleep(0.05)
        return ServiceHealth(
            name="api",
            status=ServiceStatus.OPERATIONAL,
            details={"endpoints": 8, "active_requests": 3}
        )
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "connections": len(psutil.net_connections()),
                    "interfaces": list(psutil.net_if_addrs().keys())
                }
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e)}
    
    def get_uptime(self) -> float:
        """Get system uptime."""
        try:
            return time.time() - psutil.boot_time()
        except Exception as e:
            logger.error(f"Error getting uptime: {e}")
            return 0.0
    
    def determine_overall_status(self, services: List[ServiceHealth]) -> HealthStatus:
        """Determine overall system health status."""
        if not services:
            return HealthStatus.UNKNOWN
        
        status_counts = {
            ServiceStatus.OPERATIONAL: 0,
            ServiceStatus.DEGRADED: 0,
            ServiceStatus.OUTAGE: 0,
            ServiceStatus.MAINTENANCE: 0
        }
        
        for service in services:
            status_counts[service.status] += 1
        
        if status_counts[ServiceStatus.OUTAGE] > 0:
            return HealthStatus.UNHEALTHY
        elif status_counts[ServiceStatus.DEGRADED] > 0:
            return HealthStatus.DEGRADED
        elif status_counts[ServiceStatus.OPERATIONAL] == len(services):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.DEGRADED

class SystemHealth:
    """System health monitoring and reporting."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize system health monitoring."""
        self.health_checker = HealthChecker(config)
        self.services_to_check = ["database", "cache", "api"]
        
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information."""
        try:
            # Check all services
            service_healths = []
            for service_name in self.services_to_check:
                health = await self.health_checker.check_service_health(service_name)
                service_healths.append(health)
            
            # Get system metrics
            system_metrics = self.health_checker.get_system_metrics()
            uptime = self.health_checker.get_uptime()
            
            # Determine overall status
            overall_status = self.health_checker.determine_overall_status(service_healths)
            
            # Create system health object
            health_info = SystemHealth(
                overall_status=overall_status,
                timestamp=datetime.now(),
                uptime=uptime,
                services=service_healths,
                system_metrics=system_metrics
            )
            
            return asdict(health_info)
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "overall_status": HealthStatus.UNKNOWN.value,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health of a specific service."""
        try:
            health = await self.health_checker.check_service_health(service_name)
            return asdict(health)
        except Exception as e:
            logger.error(f"Error getting {service_name} health: {e}")
            return {
                "name": service_name,
                "status": ServiceStatus.OUTAGE.value,
                "error": str(e)
            }
    
    async def start_health_monitoring(self, interval: int = 30):
        """Start continuous health monitoring."""
        logger.info(f"Starting health monitoring with {interval}s interval")
        
        while True:
            try:
                await self.get_system_health()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def stop_health_monitoring(self):
        """Stop health monitoring."""
        logger.info("Stopping health monitoring")
        # Implementation would depend on how monitoring is implemented
