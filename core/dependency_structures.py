"""
Core data structures for the dependency management system.
Modular architecture for better separation of concerns.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


class ServiceStatus(Enum):
    """Service status enumeration"""
    UNKNOWN = "unknown"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class ServicePriority(Enum):
    """Service priority enumeration"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class ServiceInfo:
    """Service information data structure"""
    name: str
    service_type: str
    priority: ServicePriority
    status: ServiceStatus
    start_time: Optional[float] = None
    stop_time: Optional[float] = None
    error_count: int = 0
    last_error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceHealth:
    """Service health information"""
    service_name: str
    status: ServiceStatus
    uptime: Optional[float] = None
    error_count: int = 0
    last_error: Optional[str] = None
    last_check: Optional[datetime] = None
    health_score: float = 100.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    service_name: str
    response_time: Optional[float] = None
    throughput: Optional[float] = None
    error_rate: float = 0.0
    availability: float = 100.0
    last_updated: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyInfo:
    """Dependency relationship information"""
    service_name: str
    dependency_name: str
    dependency_type: str = "required"
    is_healthy: bool = True
    last_check: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# Convenience functions for working with data structures
def create_service_info(
    name: str,
    service_type: str,
    priority: ServicePriority = ServicePriority.NORMAL,
    status: ServiceStatus = ServiceStatus.UNKNOWN,
    **kwargs
) -> ServiceInfo:
    """Create a ServiceInfo instance with default values"""
    return ServiceInfo(
        name=name,
        service_type=service_type,
        priority=priority,
        status=status,
        **kwargs
    )


def create_service_health(
    service_name: str,
    status: ServiceStatus,
    **kwargs
) -> ServiceHealth:
    """Create a ServiceHealth instance with default values"""
    return ServiceHealth(
        service_name=service_name,
        status=status,
        **kwargs
    )


def create_service_metrics(
    service_name: str,
    **kwargs
) -> ServiceMetrics:
    """Create a ServiceMetrics instance with default values"""
    return ServiceMetrics(
        service_name=service_name,
        **kwargs
    )


def create_dependency_info(
    service_name: str,
    dependency_name: str,
    **kwargs
) -> DependencyInfo:
    """Create a DependencyInfo instance with default values"""
    return DependencyInfo(
        service_name=service_name,
        dependency_name=dependency_name,
        **kwargs
    )
