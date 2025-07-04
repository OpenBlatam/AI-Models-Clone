"""
🚀 ULTRA-EXTREME V5 - HEALTH ROUTES
===================================

Ultra-extreme health monitoring routes with:
- Comprehensive health checks
- Service status monitoring
- Performance metrics
- System diagnostics
- Real-time monitoring
- Health alerts
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import psutil
import platform

from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import structlog

from ..config.settings import get_settings

# Initialize router
health_router = APIRouter(prefix="/health", tags=["health"])
logger = structlog.get_logger(__name__)
settings = get_settings()


# Pydantic models
class HealthStatus(BaseModel):
    """Health status model"""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    uptime: float = Field(..., description="Service uptime in seconds")


class ServiceHealth(BaseModel):
    """Service health model"""
    service_name: str
    status: str
    response_time: float
    last_check: datetime
    error_count: int
    success_rate: float
    dependencies: List[str]


class SystemMetrics(BaseModel):
    """System metrics model"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_usage: Dict[str, float]
    load_average: List[float]
    process_count: int
    uptime: float


class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    request_count: int
    average_response_time: float
    error_rate: float
    throughput: float
    active_connections: int
    cache_hit_rate: float
    database_connections: int


class HealthReport(BaseModel):
    """Comprehensive health report model"""
    overall_status: str
    timestamp: datetime
    services: List[ServiceHealth]
    system_metrics: SystemMetrics
    performance_metrics: PerformanceMetrics
    alerts: List[Dict[str, Any]]
    recommendations: List[str]


# Route handlers
@health_router.get("/", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """Basic health check endpoint"""
    try:
        logger.info("Performing basic health check")
        
        # Calculate uptime
        uptime = time.time() - psutil.boot_time()
        
        health_status = HealthStatus(
            status="healthy",
            timestamp=datetime.utcnow(),
            service="ultra-extreme-v5-gateway",
            version="5.0.0",
            uptime=uptime
        )
        
        logger.info("Health check completed", status=health_status.status)
        return health_status
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


@health_router.get("/detailed", response_model=HealthReport)
async def detailed_health_check() -> HealthReport:
    """Detailed health check with comprehensive metrics"""
    try:
        logger.info("Performing detailed health check")
        
        # Get system metrics
        system_metrics = await get_system_metrics()
        
        # Get service health
        services_health = await get_services_health()
        
        # Get performance metrics
        performance_metrics = await get_performance_metrics()
        
        # Determine overall status
        overall_status = determine_overall_status(services_health, system_metrics, performance_metrics)
        
        # Generate alerts and recommendations
        alerts = generate_alerts(services_health, system_metrics, performance_metrics)
        recommendations = generate_recommendations(services_health, system_metrics, performance_metrics)
        
        health_report = HealthReport(
            overall_status=overall_status,
            timestamp=datetime.utcnow(),
            services=services_health,
            system_metrics=system_metrics,
            performance_metrics=performance_metrics,
            alerts=alerts,
            recommendations=recommendations
        )
        
        logger.info("Detailed health check completed", overall_status=overall_status)
        return health_report
        
    except Exception as e:
        logger.error("Detailed health check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform detailed health check"
        )


@health_router.get("/services", response_model=List[ServiceHealth])
async def get_services_health_status() -> List[ServiceHealth]:
    """Get health status of all services"""
    try:
        logger.info("Getting services health status")
        
        services_health = await get_services_health()
        
        return services_health
        
    except Exception as e:
        logger.error("Failed to get services health status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get services health status"
        )


@health_router.get("/system", response_model=SystemMetrics)
async def get_system_metrics_endpoint() -> SystemMetrics:
    """Get system metrics"""
    try:
        logger.info("Getting system metrics")
        
        system_metrics = await get_system_metrics()
        
        return system_metrics
        
    except Exception as e:
        logger.error("Failed to get system metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system metrics"
        )


@health_router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics_endpoint() -> PerformanceMetrics:
    """Get performance metrics"""
    try:
        logger.info("Getting performance metrics")
        
        performance_metrics = await get_performance_metrics()
        
        return performance_metrics
        
    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance metrics"
        )


@health_router.get("/service/{service_name}")
async def get_service_health(service_name: str) -> ServiceHealth:
    """Get health status of a specific service"""
    try:
        logger.info("Getting service health", service_name=service_name)
        
        # Simulate service health check
        service_health = ServiceHealth(
            service_name=service_name,
            status="healthy",
            response_time=0.15,
            last_check=datetime.utcnow(),
            error_count=0,
            success_rate=99.8,
            dependencies=["database", "redis", "ai_service"]
        )
        
        return service_health
        
    except Exception as e:
        logger.error("Failed to get service health", service_name=service_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )


@health_router.post("/service/{service_name}/test")
async def test_service(service_name: str) -> Dict[str, Any]:
    """Test a specific service"""
    try:
        logger.info("Testing service", service_name=service_name)
        
        # Simulate service test
        test_result = {
            "service_name": service_name,
            "test_status": "passed",
            "response_time": 0.12,
            "tested_at": datetime.utcnow().isoformat(),
            "details": {
                "connectivity": "ok",
                "authentication": "ok",
                "functionality": "ok",
                "performance": "ok"
            }
        }
        
        return test_result
        
    except Exception as e:
        logger.error("Service test failed", service_name=service_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service test failed"
        )


@health_router.get("/alerts")
async def get_health_alerts() -> List[Dict[str, Any]]:
    """Get current health alerts"""
    try:
        logger.info("Getting health alerts")
        
        # Simulate alerts
        alerts = [
            {
                "id": "alert_001",
                "severity": "warning",
                "message": "High CPU usage detected",
                "service": "system",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "cpu_usage": 85.2,
                    "threshold": 80.0
                }
            },
            {
                "id": "alert_002",
                "severity": "info",
                "message": "Service restart recommended",
                "service": "ai_service",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "uptime": 86400,
                    "recommended_restart": 7200
                }
            }
        ]
        
        return alerts
        
    except Exception as e:
        logger.error("Failed to get health alerts", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get health alerts"
        )


@health_router.get("/metrics/history")
async def get_metrics_history(
    metric_type: str = Query(..., description="Type of metric (system, performance, service)"),
    duration: int = Query(3600, description="Duration in seconds", ge=60, le=86400)
) -> Dict[str, Any]:
    """Get historical metrics data"""
    try:
        logger.info("Getting metrics history", metric_type=metric_type, duration=duration)
        
        # Simulate historical data
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=duration)
        
        # Generate sample data points
        data_points = []
        interval = duration // 60  # 60 data points
        
        for i in range(60):
            timestamp = start_time + timedelta(seconds=i * interval)
            
            if metric_type == "system":
                data_point = {
                    "timestamp": timestamp.isoformat(),
                    "cpu_usage": 50 + (i % 30),
                    "memory_usage": 60 + (i % 20),
                    "disk_usage": 45 + (i % 15)
                }
            elif metric_type == "performance":
                data_point = {
                    "timestamp": timestamp.isoformat(),
                    "request_count": 100 + (i % 50),
                    "response_time": 0.1 + (i % 20) / 100,
                    "error_rate": 0.01 + (i % 5) / 1000
                }
            else:  # service
                data_point = {
                    "timestamp": timestamp.isoformat(),
                    "status": "healthy" if i % 10 != 0 else "warning",
                    "response_time": 0.15 + (i % 10) / 100,
                    "success_rate": 99.5 + (i % 10) / 10
                }
            
            data_points.append(data_point)
        
        history_data = {
            "metric_type": metric_type,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": duration,
            "data_points": data_points,
            "summary": {
                "min_value": min(dp.get("cpu_usage", 0) for dp in data_points),
                "max_value": max(dp.get("cpu_usage", 0) for dp in data_points),
                "average_value": sum(dp.get("cpu_usage", 0) for dp in data_points) / len(data_points)
            }
        }
        
        return history_data
        
    except Exception as e:
        logger.error("Failed to get metrics history", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metrics history"
        )


# Helper functions
async def get_system_metrics() -> SystemMetrics:
    """Get current system metrics"""
    try:
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        disk_usage = (disk.used / disk.total) * 100
        
        # Get network usage
        network = psutil.net_io_counters()
        network_usage = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }
        
        # Get load average
        load_average = psutil.getloadavg()
        
        # Get process count
        process_count = len(psutil.pids())
        
        # Get system uptime
        uptime = time.time() - psutil.boot_time()
        
        return SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_usage=network_usage,
            load_average=list(load_average),
            process_count=process_count,
            uptime=uptime
        )
        
    except Exception as e:
        logger.error("Failed to get system metrics", error=str(e))
        # Return default metrics on error
        return SystemMetrics(
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
            network_usage={"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0},
            load_average=[0.0, 0.0, 0.0],
            process_count=0,
            uptime=0.0
        )


async def get_services_health() -> List[ServiceHealth]:
    """Get health status of all services"""
    try:
        # Simulate service health checks
        services = [
            ServiceHealth(
                service_name="gateway",
                status="healthy",
                response_time=0.05,
                last_check=datetime.utcnow(),
                error_count=0,
                success_rate=99.9,
                dependencies=[]
            ),
            ServiceHealth(
                service_name="content_service",
                status="healthy",
                response_time=0.12,
                last_check=datetime.utcnow(),
                error_count=2,
                success_rate=99.8,
                dependencies=["database", "cache"]
            ),
            ServiceHealth(
                service_name="ai_service",
                status="healthy",
                response_time=0.25,
                last_check=datetime.utcnow(),
                error_count=1,
                success_rate=99.7,
                dependencies=["gpu", "model_cache"]
            ),
            ServiceHealth(
                service_name="optimization_service",
                status="warning",
                response_time=0.45,
                last_check=datetime.utcnow(),
                error_count=5,
                success_rate=98.5,
                dependencies=["ai_service", "database"]
            ),
            ServiceHealth(
                service_name="database",
                status="healthy",
                response_time=0.08,
                last_check=datetime.utcnow(),
                error_count=0,
                success_rate=99.9,
                dependencies=[]
            ),
            ServiceHealth(
                service_name="redis_cache",
                status="healthy",
                response_time=0.02,
                last_check=datetime.utcnow(),
                error_count=0,
                success_rate=99.9,
                dependencies=[]
            )
        ]
        
        return services
        
    except Exception as e:
        logger.error("Failed to get services health", error=str(e))
        return []


async def get_performance_metrics() -> PerformanceMetrics:
    """Get current performance metrics"""
    try:
        # Simulate performance metrics
        return PerformanceMetrics(
            request_count=15420,
            average_response_time=0.18,
            error_rate=0.015,
            throughput=125.5,
            active_connections=45,
            cache_hit_rate=94.2,
            database_connections=12
        )
        
    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e))
        return PerformanceMetrics(
            request_count=0,
            average_response_time=0.0,
            error_rate=0.0,
            throughput=0.0,
            active_connections=0,
            cache_hit_rate=0.0,
            database_connections=0
        )


def determine_overall_status(
    services: List[ServiceHealth],
    system_metrics: SystemMetrics,
    performance_metrics: PerformanceMetrics
) -> str:
    """Determine overall health status"""
    # Check if any service is unhealthy
    unhealthy_services = [s for s in services if s.status == "unhealthy"]
    if unhealthy_services:
        return "unhealthy"
    
    # Check if any service is warning
    warning_services = [s for s in services if s.status == "warning"]
    if warning_services:
        return "warning"
    
    # Check system metrics
    if system_metrics.cpu_usage > 90 or system_metrics.memory_usage > 90:
        return "warning"
    
    # Check performance metrics
    if performance_metrics.error_rate > 0.05:  # 5% error rate
        return "warning"
    
    return "healthy"


def generate_alerts(
    services: List[ServiceHealth],
    system_metrics: SystemMetrics,
    performance_metrics: PerformanceMetrics
) -> List[Dict[str, Any]]:
    """Generate health alerts"""
    alerts = []
    
    # System alerts
    if system_metrics.cpu_usage > 80:
        alerts.append({
            "severity": "warning",
            "message": f"High CPU usage: {system_metrics.cpu_usage:.1f}%",
            "service": "system"
        })
    
    if system_metrics.memory_usage > 85:
        alerts.append({
            "severity": "warning",
            "message": f"High memory usage: {system_metrics.memory_usage:.1f}%",
            "service": "system"
        })
    
    # Service alerts
    for service in services:
        if service.status == "unhealthy":
            alerts.append({
                "severity": "critical",
                "message": f"Service {service.service_name} is unhealthy",
                "service": service.service_name
            })
        elif service.status == "warning":
            alerts.append({
                "severity": "warning",
                "message": f"Service {service.service_name} has warnings",
                "service": service.service_name
            })
    
    # Performance alerts
    if performance_metrics.error_rate > 0.03:
        alerts.append({
            "severity": "warning",
            "message": f"High error rate: {performance_metrics.error_rate:.3f}",
            "service": "performance"
        })
    
    return alerts


def generate_recommendations(
    services: List[ServiceHealth],
    system_metrics: SystemMetrics,
    performance_metrics: PerformanceMetrics
) -> List[str]:
    """Generate health recommendations"""
    recommendations = []
    
    # System recommendations
    if system_metrics.cpu_usage > 70:
        recommendations.append("Consider scaling up CPU resources or optimizing workload distribution")
    
    if system_metrics.memory_usage > 80:
        recommendations.append("Consider increasing memory allocation or optimizing memory usage")
    
    # Service recommendations
    for service in services:
        if service.response_time > 0.5:
            recommendations.append(f"Optimize {service.service_name} response time")
        
        if service.success_rate < 99.0:
            recommendations.append(f"Investigate errors in {service.service_name}")
    
    # Performance recommendations
    if performance_metrics.cache_hit_rate < 90:
        recommendations.append("Optimize cache configuration to improve hit rate")
    
    if performance_metrics.error_rate > 0.02:
        recommendations.append("Investigate and fix error sources to improve reliability")
    
    return recommendations


# Import time module for uptime calculation
import time 