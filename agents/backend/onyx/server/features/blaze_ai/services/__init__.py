"""
Service registry and management for the Blaze AI module.

This module provides a centralized service registry that handles:
- Service registration and discovery
- Dependency injection and lifecycle management
- Service health monitoring
- Service configuration management
- Service metrics and performance tracking
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Type
from abc import ABC, abstractmethod

from ..core.interfaces import CoreConfig, HealthStatus
from ..utils.logging import get_logger

class ServiceStatus(Enum):
    """Service operational status."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    DEGRADED = "degraded"

@dataclass
class ServiceInfo:
    """Information about a registered service."""
    name: str
    service_class: Type
    instance: Optional[Any] = None
    status: ServiceStatus = ServiceStatus.INITIALIZING
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    health_check: Optional[Callable] = None
    startup_time: Optional[float] = None
    last_health_check: Optional[float] = None
    error_count: int = 0
    total_requests: int = 0
    successful_requests: int = 0

class Service(ABC):
    """Base service class with common functionality."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = get_logger(f"service.{name}")
        self.status = ServiceStatus.INITIALIZING
        self.startup_time = None
        self.error_count = 0
        self.total_requests = 0
        self.successful_requests = 0
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the service."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the service."""
        return {
            "status": self.status.value,
            "uptime": time.time() - self.startup_time if self.startup_time else 0,
            "error_count": self.error_count,
            "total_requests": self.total_requests,
            "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 1.0
        }
    
    def record_request(self, success: bool = True):
        """Record a request for metrics."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.error_count += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        return {
            "name": self.name,
            "status": self.status.value,
            "uptime": time.time() - self.startup_time if self.startup_time else 0,
            "error_count": self.error_count,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 1.0
        }

class ServiceRegistry:
    """
    Centralized service registry for the Blaze AI module.
    
    Provides:
    - Service registration and discovery
    - Dependency injection
    - Service lifecycle management
    - Health monitoring
    - Configuration management
    """
    
    def __init__(self, config: Optional[CoreConfig] = None):
        self.config = config or CoreConfig()
        self.logger = get_logger("service_registry")
        self.services: Dict[str, ServiceInfo] = {}
        self.service_instances: Dict[str, Service] = {}
        self._initialization_lock = asyncio.Lock()
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Register default services
        self._register_default_services()
        
        # Start health monitoring
        self._start_health_monitoring()
    
    def _register_default_services(self):
        """Register default services."""
        try:
            from .seo import SEOService
            from .brand import BrandVoiceService
            from .generation import ContentGenerationService
            from .analytics import AnalyticsService
            from .planner import ContentPlannerService
            
            # Register SEO service
            seo_config = self.config.get_component_config("seo_service")
            self.register_service("seo", SEOService, seo_config)
            
            # Register brand voice service
            brand_config = self.config.get_component_config("brand_service")
            self.register_service("brand", BrandVoiceService, brand_config)
            
            # Register content generation service
            generation_config = self.config.get_component_config("generation_service")
            self.register_service("generation", ContentGenerationService, generation_config)
            
            # Register analytics service
            analytics_config = self.config.get_component_config("analytics_service")
            self.register_service("analytics", AnalyticsService, analytics_config)
            
            # Register planner service
            planner_config = self.config.get_component_config("planner_service")
            self.register_service("planner", ContentPlannerService, planner_config)
            
            self.logger.info("Default services registered successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to register default services: {e}")
            raise
    
    def register_service(self, name: str, service_class: Type[Service], 
                        config: Optional[Dict[str, Any]] = None,
                        dependencies: Optional[List[str]] = None,
                        health_check: Optional[Callable] = None) -> None:
        """
        Register a service with the registry.
        
        Args:
            name: Service name
            service_class: Service class to instantiate
            config: Service configuration
            dependencies: List of service dependencies
            health_check: Custom health check function
        """
        if name in self.services:
            self.logger.warning(f"Service '{name}' already registered, overwriting")
        
        self.services[name] = ServiceInfo(
            name=name,
            service_class=service_class,
            config=config or {},
            dependencies=dependencies or [],
            health_check=health_check
        )
        
        self.logger.info(f"Service '{name}' registered successfully")
    
    async def get_service(self, name: str) -> Service:
        """
        Get a service instance, initializing it if necessary.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service not found
            Exception: If service initialization fails
        """
        if name not in self.services:
            raise ValueError(f"Service '{name}' not found")
        
        # Return existing instance if available
        if name in self.service_instances:
            return self.service_instances[name]
        
        # Initialize service
        async with self._initialization_lock:
            # Double-check after acquiring lock
            if name in self.service_instances:
                return self.service_instances[name]
            
            return await self._initialize_service(name)
    
    async def _initialize_service(self, name: str) -> Service:
        """Initialize a service and its dependencies."""
        service_info = self.services[name]
        
        # Check dependencies first
        for dep_name in service_info.dependencies:
            if dep_name not in self.services:
                raise ValueError(f"Service '{name}' depends on '{dep_name}' which is not registered")
            
            # Ensure dependency is initialized
            await self.get_service(dep_name)
        
        try:
            # Create service instance
            service_instance = service_info.service_class(name, service_info.config)
            
            # Initialize the service
            await service_instance.initialize()
            
            # Update service info
            service_info.instance = service_instance
            service_info.status = ServiceStatus.RUNNING
            service_info.startup_time = time.time()
            
            # Store instance
            self.service_instances[name] = service_instance
            
            self.logger.info(f"Service '{name}' initialized successfully")
            return service_instance
            
        except Exception as e:
            service_info.status = ServiceStatus.ERROR
            self.logger.error(f"Failed to initialize service '{name}': {e}")
            raise
    
    def has_service(self, name: str) -> bool:
        """Check if a service is registered."""
        return name in self.services
    
    def list_services(self) -> List[str]:
        """List all registered service names."""
        return list(self.services.keys())
    
    def list_running_services(self) -> List[str]:
        """List all running service names."""
        return [name for name, info in self.services.items() 
                if info.status == ServiceStatus.RUNNING]
    
    async def shutdown_service(self, name: str) -> None:
        """Shutdown a specific service."""
        if name in self.service_instances:
            service = self.service_instances[name]
            try:
                await service.shutdown()
                self.services[name].status = ServiceStatus.STOPPED
                self.logger.info(f"Service '{name}' shutdown successfully")
            except Exception as e:
                self.logger.error(f"Failed to shutdown service '{name}': {e}")
                raise
    
    async def shutdown_all(self) -> None:
        """Shutdown all services."""
        self.logger.info("Shutting down all services")
        
        # Stop health monitoring
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Shutdown all services
        shutdown_tasks = []
        for name in self.service_instances:
            shutdown_tasks.append(asyncio.create_task(self.shutdown_service(name)))
        
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        self.logger.info("All services shutdown complete")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services."""
        status = {}
        for name, info in self.services.items():
            status[name] = {
                'status': info.status.value,
                'dependencies': info.dependencies,
                'startup_time': info.startup_time,
                'last_health_check': info.last_health_check,
                'error_count': info.error_count,
                'total_requests': info.total_requests,
                'successful_requests': info.successful_requests
            }
            
            # Add instance metrics if available
            if info.instance:
                status[name]['instance_metrics'] = info.instance.get_metrics()
        
        return status
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health checks on all services."""
        health_results = {}
        
        for name, info in self.services.items():
            try:
                if info.instance:
                    health_result = await info.instance.health_check()
                elif info.health_check:
                    health_result = await info.health_check()
                else:
                    health_result = {
                        "status": info.status.value,
                        "message": "No health check available"
                    }
                
                health_results[name] = health_result
                info.last_health_check = time.time()
                
            except Exception as e:
                health_results[name] = {
                    "status": "error",
                    "message": str(e)
                }
                info.error_count += 1
        
        return health_results
    
    def _start_health_monitoring(self):
        """Start the health monitoring task."""
        if self.config.monitoring.enable_metrics:
            self._health_check_task = asyncio.create_task(self._health_monitor_loop())
    
    async def _health_monitor_loop(self):
        """Health monitoring loop."""
        while True:
            try:
                await self.health_check_all()
                await asyncio.sleep(self.config.monitoring.health_check_interval)
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)  # Short delay on error

# Global service registry instance
_default_service_registry: Optional[ServiceRegistry] = None

def get_service_registry(config: Optional[CoreConfig] = None) -> ServiceRegistry:
    """Get the global service registry instance."""
    global _default_service_registry
    if _default_service_registry is None:
        _default_service_registry = ServiceRegistry(config)
    return _default_service_registry

# Legacy alias for backward compatibility
BlazeServiceRegistry = ServiceRegistry

# Export main components
__all__ = [
    "ServiceStatus",
    "ServiceInfo",
    "Service",
    "ServiceRegistry",
    "BlazeServiceRegistry",
    "get_service_registry"
]


