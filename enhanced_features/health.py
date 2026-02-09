#!/usr/bin/env python3
"""
🏥 HEALTH CHECKING MODULE - Blaze AI System
Comprehensive system health monitoring and status checking
"""

import asyncio
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class ServiceStatus(Enum):
    """Service status enumeration."""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"

@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, float]
    timestamp: datetime

@dataclass
class ServiceHealth:
    """Individual service health information."""
    name: str
    status: ServiceStatus
    health_status: HealthStatus
    response_time: Optional[float]
    last_check: datetime
    error_message: Optional[str]
    metadata: Dict[str, Any]

@dataclass
class HealthCheckResult:
    """Complete health check result."""
    overall_status: HealthStatus
    system_health: HealthStatus
    services_health: Dict[str, ServiceHealth]
    system_metrics: SystemMetrics
    timestamp: datetime
    response_time: float
    recommendations: List[str]

class HealthChecker:
    """Main health checker class for the Blaze AI system."""
    
    def __init__(self):
        self.check_history: List[HealthCheckResult] = []
        self.max_history_size = 100
        self.health_thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 80.0,
            'memory_critical': 95.0,
            'disk_warning': 85.0,
            'disk_critical': 95.0,
            'response_time_warning': 1.0,
            'response_time_critical': 5.0
        }
    
    async def check_system_health(self) -> SystemMetrics:
        """Check overall system health metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_io=network_io,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                network_io={},
                timestamp=datetime.now()
            )
    
    def evaluate_system_health(self, metrics: SystemMetrics) -> HealthStatus:
        """Evaluate system health based on metrics and thresholds."""
        if (metrics.cpu_percent >= self.health_thresholds['cpu_critical'] or
            metrics.memory_percent >= self.health_thresholds['memory_critical'] or
            metrics.disk_percent >= self.health_thresholds['disk_critical']):
            return HealthStatus.CRITICAL
        elif (metrics.cpu_percent >= self.health_thresholds['cpu_warning'] or
              metrics.memory_percent >= self.health_thresholds['memory_warning'] or
              metrics.disk_percent >= self.health_thresholds['disk_warning']):
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """Check health of a specific service."""
        start_time = time.time()
        
        try:
            # Simulate service health check
            # In a real implementation, this would check actual services
            if service_name == "blaze_ai_api":
                # Simulate API health check
                await asyncio.sleep(0.1)  # Simulate API call
                status = ServiceStatus.RUNNING
                health_status = HealthStatus.HEALTHY
                error_message = None
            elif service_name == "database":
                # Simulate database health check
                await asyncio.sleep(0.05)  # Simulate DB check
                status = ServiceStatus.RUNNING
                health_status = HealthStatus.HEALTHY
                error_message = None
            elif service_name == "redis_cache":
                # Simulate Redis health check
                await asyncio.sleep(0.03)  # Simulate cache check
                status = ServiceStatus.RUNNING
                health_status = HealthStatus.HEALTHY
                error_message = None
            else:
                # Unknown service
                status = ServiceStatus.ERROR
                health_status = HealthStatus.UNKNOWN
                error_message = f"Unknown service: {service_name}"
            
            response_time = time.time() - start_time
            
            return ServiceHealth(
                name=service_name,
                status=status,
                health_status=health_status,
                response_time=response_time,
                last_check=datetime.now(),
                error_message=error_message,
                metadata={}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return ServiceHealth(
                name=service_name,
                status=ServiceStatus.ERROR,
                health_status=HealthStatus.CRITICAL,
                response_time=response_time,
                last_check=datetime.now(),
                error_message=str(e),
                metadata={}
            )
    
    async def run_comprehensive_health_check(self) -> HealthCheckResult:
        """Run a comprehensive health check of the entire system."""
        start_time = time.time()
        
        logger.info("🏥 Starting comprehensive health check...")
        
        # Check system health
        system_metrics = await self.check_system_health()
        system_health = self.evaluate_system_health(system_metrics)
        
        # Check services health
        services = ["blaze_ai_api", "database", "redis_cache"]
        services_health = {}
        
        for service in services:
            service_health = await self.check_service_health(service)
            services_health[service] = service_health
        
        # Determine overall health status
        overall_status = self._determine_overall_health(system_health, services_health)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(system_health, services_health, system_metrics)
        
        # Calculate total response time
        total_response_time = time.time() - start_time
        
        # Create health check result
        result = HealthCheckResult(
            overall_status=overall_status,
            system_health=system_health,
            services_health=services_health,
            system_metrics=system_metrics,
            timestamp=datetime.now(),
            response_time=total_response_time,
            recommendations=recommendations
        )
        
        # Store in history
        self._store_health_check(result)
        
        logger.info(f"🏥 Health check completed in {total_response_time:.3f}s - Status: {overall_status.value}")
        
        return result
    
    def _determine_overall_health(self, system_health: HealthStatus, services_health: Dict[str, ServiceHealth]) -> HealthStatus:
        """Determine overall health status based on system and services."""
        if system_health == HealthStatus.CRITICAL:
            return HealthStatus.CRITICAL
        
        # Check if any service is critical
        for service in services_health.values():
            if service.health_status == HealthStatus.CRITICAL:
                return HealthStatus.CRITICAL
        
        if system_health == HealthStatus.WARNING:
            return HealthStatus.WARNING
        
        # Check if any service is warning
        for service in services_health.values():
            if service.health_status == HealthStatus.WARNING:
                return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY
    
    def _generate_recommendations(self, system_health: HealthStatus, services_health: Dict[str, ServiceHealth], metrics: SystemMetrics) -> List[str]:
        """Generate health recommendations based on current status."""
        recommendations = []
        
        # System recommendations
        if metrics.cpu_percent >= self.health_thresholds['cpu_warning']:
            recommendations.append("Consider scaling CPU resources or optimizing CPU-intensive operations")
        
        if metrics.memory_percent >= self.health_thresholds['memory_warning']:
            recommendations.append("Monitor memory usage and consider increasing RAM or optimizing memory usage")
        
        if metrics.disk_percent >= self.health_thresholds['disk_warning']:
            recommendations.append("Disk space is running low, consider cleanup or expansion")
        
        # Service recommendations
        for service_name, service in services_health.items():
            if service.health_status == HealthStatus.CRITICAL:
                recommendations.append(f"Service {service_name} is critical - immediate attention required")
            elif service.health_status == HealthStatus.WARNING:
                recommendations.append(f"Service {service_name} needs monitoring")
        
        if not recommendations:
            recommendations.append("System is healthy - continue monitoring")
        
        return recommendations
    
    def _store_health_check(self, result: HealthCheckResult):
        """Store health check result in history."""
        self.check_history.append(result)
        
        # Maintain history size
        if len(self.check_history) > self.max_history_size:
            self.check_history.pop(0)
    
    def get_health_history(self, limit: Optional[int] = None) -> List[HealthCheckResult]:
        """Get health check history."""
        if limit is None:
            return self.check_history.copy()
        return self.check_history[-limit:]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of recent health checks."""
        if not self.check_history:
            return {"status": "No health checks performed yet"}
        
        recent_checks = self.check_history[-10:]  # Last 10 checks
        
        summary = {
            "total_checks": len(self.check_history),
            "recent_checks": len(recent_checks),
            "overall_status_counts": {},
            "average_response_time": 0.0,
            "last_check": None,
            "trend": "stable"
        }
        
        # Count statuses
        for check in recent_checks:
            status = check.overall_status.value
            summary["overall_status_counts"][status] = summary["overall_status_counts"].get(status, 0) + 1
        
        # Calculate average response time
        if recent_checks:
            avg_response = sum(check.response_time for check in recent_checks) / len(recent_checks)
            summary["average_response_time"] = round(avg_response, 3)
            summary["last_check"] = recent_checks[-1].timestamp.isoformat()
        
        # Determine trend
        if len(recent_checks) >= 2:
            first_status = recent_checks[0].overall_status
            last_status = recent_checks[-1].overall_status
            
            if first_status.value == "healthy" and last_status.value != "healthy":
                summary["trend"] = "degrading"
            elif first_status.value != "healthy" and last_status.value == "healthy":
                summary["trend"] = "improving"
            else:
                summary["trend"] = "stable"
        
        return summary
    
    def export_health_data(self, format: str = "json") -> str:
        """Export health data in specified format."""
        if format.lower() == "json":
            data = {
                "health_checker_info": {
                    "max_history_size": self.max_history_size,
                    "health_thresholds": self.health_thresholds
                },
                "health_history": [
                    {
                        "timestamp": check.timestamp.isoformat(),
                        "overall_status": check.overall_status.value,
                        "system_health": check.system_health.value,
                        "response_time": check.response_time,
                        "recommendations": check.recommendations
                    }
                    for check in self.check_history
                ],
                "summary": self.get_health_summary()
            }
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")

# Health check endpoints for FastAPI integration
class HealthEndpoints:
    """FastAPI endpoints for health checking."""
    
    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker
    
    async def health_check(self) -> Dict[str, Any]:
        """Basic health check endpoint."""
        try:
            result = await self.health_checker.run_comprehensive_health_check()
            return {
                "status": result.overall_status.value,
                "timestamp": result.timestamp.isoformat(),
                "response_time": result.response_time,
                "system_health": result.system_health.value,
                "services_count": len(result.services_health)
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def detailed_health_check(self) -> Dict[str, Any]:
        """Detailed health check endpoint."""
        try:
            result = await self.health_checker.run_comprehensive_health_check()
            return {
                "overall_status": result.overall_status.value,
                "timestamp": result.timestamp.isoformat(),
                "response_time": result.response_time,
                "system_health": result.system_health.value,
                "system_metrics": asdict(result.system_metrics),
                "services_health": {
                    name: {
                        "status": service.status.value,
                        "health_status": service.health_status.value,
                        "response_time": service.response_time,
                        "last_check": service.last_check.isoformat(),
                        "error_message": service.error_message
                    }
                    for name, service in result.services_health.items()
                },
                "recommendations": result.recommendations
            }
        except Exception as e:
            logger.error(f"Detailed health check failed: {e}")
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def health_summary(self) -> Dict[str, Any]:
        """Health summary endpoint."""
        try:
            return self.health_checker.get_health_summary()
        except Exception as e:
            logger.error(f"Health summary failed: {e}")
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

# Utility functions
def create_health_checker() -> HealthChecker:
    """Create and configure a health checker instance."""
    return HealthChecker()

def create_health_endpoints(health_checker: HealthChecker) -> HealthEndpoints:
    """Create health endpoints for FastAPI integration."""
    return HealthEndpoints(health_checker)

# Example usage
async def main():
    """Example usage of the health checker."""
    health_checker = create_health_checker()
    
    print("🏥 Blaze AI Health Checker")
    print("=" * 40)
    
    # Run health check
    result = await health_checker.run_comprehensive_health_check()
    
    print(f"Overall Status: {result.overall_status.value}")
    print(f"System Health: {result.system_health.value}")
    print(f"Response Time: {result.response_time:.3f}s")
    print(f"Services Checked: {len(result.services_health)}")
    
    print("\nSystem Metrics:")
    print(f"  CPU: {result.system_metrics.cpu_percent:.1f}%")
    print(f"  Memory: {result.system_metrics.memory_percent:.1f}%")
    print(f"  Disk: {result.system_metrics.disk_percent:.1f}%")
    
    print("\nRecommendations:")
    for rec in result.recommendations:
        print(f"  • {rec}")
    
    # Get summary
    summary = health_checker.get_health_summary()
    print(f"\nHealth Summary: {summary['trend']}")

if __name__ == "__main__":
    asyncio.run(main())
