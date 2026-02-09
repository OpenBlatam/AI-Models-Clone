"""
Service lifecycle management module.
Handles service startup, shutdown, and state transitions.
"""

import asyncio
import time
from typing import Optional, Callable, Any, Dict, List
from dataclasses import dataclass, field
from .dependency_structures import ServiceStatus, ServicePriority, ServiceInfo


@dataclass
class ServiceLifecycle:
    """Manages the lifecycle of a single service"""
    name: str
    service_type: str
    priority: ServicePriority = ServicePriority.NORMAL
    status: ServiceStatus = ServiceStatus.UNKNOWN
    start_time: Optional[float] = None
    stop_time: Optional[float] = None
    error_count: int = 0
    last_error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Callbacks
    _on_start: Optional[Callable] = None
    _on_stop: Optional[Callable] = None
    _on_error: Optional[Callable] = None
    
    def add_dependency(self, dependency: str) -> None:
        """Add a dependency to the service"""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)
    
    def remove_dependency(self, dependency: str) -> None:
        """Remove a dependency from the service"""
        if dependency in self.dependencies:
            self.dependencies.remove(dependency)
    
    def on_start(self, callback: Callable) -> None:
        """Register a callback for service start"""
        self._on_start = callback
    
    def on_stop(self, callback: Callable) -> None:
        """Register a callback for service stop"""
        self._on_stop = callback
    
    def on_error(self, callback: Callable) -> None:
        """Register a callback for service errors"""
        self._on_error = callback
    
    async def start(self) -> None:
        """Start the service"""
        try:
            self.status = ServiceStatus.STARTING
            self.start_time = time.time()
            
            if self._on_start:
                await self._on_start()
            
            self.status = ServiceStatus.RUNNING
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.error_count += 1
            self.last_error = str(e)
            
            if self._on_error:
                await self._on_error()
            
            raise
    
    async def stop(self) -> None:
        """Stop the service"""
        try:
            self.status = ServiceStatus.STOPPING
            
            if self._on_stop:
                await self._on_stop()
            
            self.status = ServiceStatus.STOPPED
            self.stop_time = time.time()
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.error_count += 1
            self.last_error = str(e)
            
            if self._on_error:
                await self._on_error()
            
            raise
    
    def to_info(self) -> ServiceInfo:
        """Convert to ServiceInfo"""
        return ServiceInfo(
            name=self.name,
            service_type=self.service_type,
            priority=self.priority,
            status=self.status,
            start_time=self.start_time,
            stop_time=self.stop_time,
            error_count=self.error_count,
            last_error=self.last_error,
            dependencies=self.dependencies.copy(),
            metadata=self.metadata.copy()
        )


class LifecycleManager:
    """Manages multiple service lifecycles"""
    
    def __init__(self):
        self.services: Dict[str, ServiceLifecycle] = {}
        self._startup_order: List[str] = []
    
    def register_service(
        self,
        name: str,
        service_type: str,
        priority: ServicePriority = ServicePriority.NORMAL,
        dependencies: Optional[List[str]] = None
    ) -> ServiceLifecycle:
        """Register a new service"""
        lifecycle = ServiceLifecycle(name, service_type, priority)
        
        if dependencies:
            for dep in dependencies:
                lifecycle.add_dependency(dep)
        
        self.services[name] = lifecycle
        return lifecycle
    
    def get_service(self, name: str) -> Optional[ServiceLifecycle]:
        """Get a service by name"""
        return self.services.get(name)
    
    def get_startup_order(self) -> List[str]:
        """Calculate the startup order based on dependencies"""
        if not self._startup_order:
            self._startup_order = self._calculate_startup_order()
        return self._startup_order.copy()
    
    def _calculate_startup_order(self) -> List[str]:
        """Calculate startup order using topological sort"""
        # Simple implementation - can be enhanced with proper topological sort
        services = list(self.services.keys())
        ordered = []
        
        # Add services with no dependencies first
        for service_name in services:
            if not self.services[service_name].dependencies:
                ordered.append(service_name)
        
        # Add remaining services
        for service_name in services:
            if service_name not in ordered:
                ordered.append(service_name)
        
        return ordered
    
    async def start_all_services(self) -> None:
        """Start all services in dependency order"""
        startup_order = self.get_startup_order()
        
        for service_name in startup_order:
            service = self.services[service_name]
            if service.status == ServiceStatus.STOPPED:
                await service.start()
    
    async def stop_all_services(self) -> None:
        """Stop all services in reverse dependency order"""
        startup_order = self.get_startup_order()
        
        for service_name in reversed(startup_order):
            service = self.services[service_name]
            if service.status == ServiceStatus.RUNNING:
                await service.stop()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary of all services"""
        total = len(self.services)
        running = sum(1 for s in self.services.values() if s.status == ServiceStatus.RUNNING)
        stopped = sum(1 for s in self.services.values() if s.status == ServiceStatus.STOPPED)
        error = sum(1 for s in self.services.values() if s.status == ServiceStatus.ERROR)
        
        health_percentage = (running / total * 100) if total > 0 else 0
        
        return {
            "total_services": total,
            "running_services": running,
            "stopped_services": stopped,
            "error_services": error,
            "health_percentage": health_percentage,
            "timestamp": time.time(),
            "services": [s.to_info() for s in self.services.values()]
        }
