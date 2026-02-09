"""
Modular dependency management system.
Integrates all components: structures, lifecycle, resolution, and health monitoring.
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from contextlib import asynccontextmanager

from .dependency_structures import ServiceStatus, ServicePriority, ServiceInfo
from .service_lifecycle import ServiceLifecycle, LifecycleManager
from .dependency_resolver import DependencyResolver
from .health_monitor import HealthMonitor


class DependencyManager:
    """Main dependency management system integrating all components"""
    
    def __init__(self):
        # Core components
        self.lifecycle_manager = LifecycleManager()
        self.dependency_resolver = DependencyResolver()
        self.health_monitor = HealthMonitor()
        
        # Service registry
        self.service_factories: Dict[str, Callable] = {}
        self.service_instances: Dict[str, Any] = {}
        self.is_running = False
        
        # Setup health monitoring callbacks
        self.health_monitor.on_health_change(self._on_service_health_change)
        self.health_monitor.on_alert(self._on_alert)
    
    def register_service(
        self,
        name: str,
        service_type: str,
        factory: Callable,
        priority: ServicePriority = ServicePriority.NORMAL,
        dependencies: Optional[List[str]] = None
    ) -> None:
        """Register a new service"""
        # Register with lifecycle manager
        lifecycle = self.lifecycle_manager.register_service(
            name, service_type, priority, dependencies
        )
        
        # Register with dependency resolver
        if dependencies:
            for dep in dependencies:
                self.dependency_resolver.add_dependency(name, dep)
        
        # Store factory
        self.service_factories[name] = factory
        
        # Initialize health monitoring
        self.health_monitor.update_service_status(name, ServiceStatus.UNKNOWN)
        
        print(f"Registered service {name} ({service_type}) with priority {priority}")
    
    def unregister_service(self, name: str) -> None:
        """Unregister a service"""
        # Remove from lifecycle manager
        if name in self.lifecycle_manager.services:
            del self.lifecycle_manager.services[name]
        
        # Remove from dependency resolver
        if name in self.dependency_resolver.dependency_graph:
            del self.dependency_resolver.dependency_graph[name]
        
        # Remove from reverse dependencies
        for deps in self.dependency_resolver.reverse_dependencies.values():
            deps.discard(name)
        
        # Remove factory and instance
        self.service_factories.pop(name, None)
        self.service_instances.pop(name, None)
        
        # Remove from health monitoring
        self.health_monitor.service_health.pop(name, None)
        self.health_monitor.service_metrics.pop(name, None)
    
    def get_service_status(self, name: str) -> Optional[ServiceStatus]:
        """Get the status of a service"""
        service = self.lifecycle_manager.get_service(name)
        return service.status if service else None
    
    def get_service_info(self, name: str) -> Optional[ServiceInfo]:
        """Get information about a service"""
        service = self.lifecycle_manager.get_service(name)
        return service.to_info() if service else None
    
    def get_all_services(self) -> List[ServiceInfo]:
        """Get information about all services"""
        return [
            service.to_info()
            for service in self.lifecycle_manager.services.values()
        ]
    
    def get_services_by_status(self, status: ServiceStatus) -> List[ServiceInfo]:
        """Get services with a specific status"""
        return [
            service.to_info()
            for service in self.lifecycle_manager.services.values()
            if service.status == status
        ]
    
    def check_dependencies(self, service_name: str) -> bool:
        """Check if all dependencies for a service are satisfied"""
        service = self.lifecycle_manager.get_service(service_name)
        if not service:
            return False
        
        for dep_name in service.dependencies:
            dep_service = self.lifecycle_manager.get_service(dep_name)
            if not dep_service or dep_service.status != ServiceStatus.RUNNING:
                return False
        
        return True
    
    def get_startup_order(self) -> List[str]:
        """Get the startup order for all services"""
        return self.dependency_resolver.get_topological_order()
    
    async def start_all_services(self) -> None:
        """Start all services in dependency order"""
        if self.is_running:
            return
        
        try:
            # Validate dependencies
            cycles = self.dependency_resolver.check_circular_dependencies()
            if cycles:
                raise ValueError(f"Circular dependencies detected: {cycles}")
            
            # Get startup order
            startup_order = self.get_startup_order()
            print(f"Starting {len(startup_order)} services in order: {startup_order}")
            
            # Start services in order
            for service_name in startup_order:
                if not self.check_dependencies(service_name):
                    print(f"Skipping {service_name} - dependencies not satisfied")
                    continue
                
                try:
                    # Create service instance
                    factory = self.service_factories[service_name]
                    instance = factory()
                    self.service_instances[service_name] = instance
                    
                    # Start service lifecycle
                    service = self.lifecycle_manager.get_service(service_name)
                    await service.start()
                    
                    # Update health status
                    self.health_monitor.update_service_status(service_name, ServiceStatus.RUNNING)
                    
                    print(f"Started service: {service_name}")
                    
                except Exception as e:
                    print(f"Failed to start service {service_name}: {e}")
                    self.health_monitor.update_service_status(service_name, ServiceStatus.ERROR)
                    raise
            
            self.is_running = True
            print("All services started")
            
        except Exception as e:
            print(f"Error starting services: {e}")
            raise
    
    async def stop_all_services(self) -> None:
        """Stop all services in reverse dependency order"""
        if not self.is_running:
            return
        
        try:
            # Stop services in reverse order
            startup_order = self.get_startup_order()
            for service_name in reversed(startup_order):
                service = self.lifecycle_manager.get_service(service_name)
                if service and service.status == ServiceStatus.RUNNING:
                    await service.stop()
                    self.health_monitor.update_service_status(service_name, ServiceStatus.STOPPED)
                    print(f"Stopped service: {service_name}")
            
            # Clear instances
            self.service_instances.clear()
            self.is_running = False
            print("All services stopped")
            
        except Exception as e:
            print(f"Error stopping services: {e}")
            raise
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a service instance by name"""
        return self.service_instances.get(name)
    
    def has_service(self, name: str) -> bool:
        """Check if a service exists"""
        return name in self.service_factories
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        lifecycle_summary = self.lifecycle_manager.get_health_summary()
        health_summary = self.health_monitor.get_health_summary()
        
        return {
            **lifecycle_summary,
            **health_summary,
            "dependency_health": {
                "circular_dependencies": len(self.dependency_resolver.check_circular_dependencies()),
                "missing_dependencies": len(self.dependency_resolver.validate_dependencies(
                    {name: service.to_info() for name, service in self.lifecycle_manager.services.items()}
                ))
            }
        }
    
    @asynccontextmanager
    async def managed_services(self):
        """Context manager for managing service lifecycle"""
        try:
            await self.start_all_services()
            yield self
        finally:
            await self.stop_all_services()
    
    def _on_service_health_change(self, service_name: str, status: ServiceStatus) -> None:
        """Handle service health changes"""
        print(f"Service {service_name} health changed to {status}")
    
    def _on_alert(self, alert) -> None:
        """Handle health monitoring alerts"""
        print(f"Alert: {alert.service_name} - {alert.message} ({alert.severity})")


# Global instance
dependency_manager = DependencyManager()


# Convenience functions
def get_dependency_manager() -> DependencyManager:
    """Get the global dependency manager instance"""
    return dependency_manager


def register_service(
    name: str,
    service_type: str,
    factory: Callable,
    priority: ServicePriority = ServicePriority.NORMAL,
    dependencies: Optional[List[str]] = None
) -> None:
    """Register a service with the global dependency manager"""
    dependency_manager.register_service(name, service_type, factory, priority, dependencies)


def get_service(name: str) -> Optional[Any]:
    """Get a service instance from the global dependency manager"""
    return dependency_manager.get_service(name)


def has_service(name: str) -> bool:
    """Check if a service exists in the global dependency manager"""
    return dependency_manager.has_service(name)


async def start_all_services() -> None:
    """Start all services in the global dependency manager"""
    await dependency_manager.start_all_services()


async def stop_all_services() -> None:
    """Stop all services in the global dependency manager"""
    await dependency_manager.stop_all_services()
