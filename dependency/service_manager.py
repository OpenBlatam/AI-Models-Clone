"""
Service Manager for Instagram Captions API v10.0
Service lifecycle management and dependency orchestration.
"""
import asyncio
import time
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
import logging
from .service_container import ServiceContainer, ServiceLifetime

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Service status enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class ServiceInfo:
    """Information about a managed service."""
    
    def __init__(self, name: str, service_type: type, lifetime: ServiceLifetime):
        self.name = name
        self.service_type = service_type
        self.lifetime = lifetime
        self.status = ServiceStatus.STOPPED
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
        self.error_message: Optional[str] = None
        self.health_check_count = 0
        self.last_health_check: Optional[float] = None
        self.dependencies: List[str] = []
        self.startup_order: Optional[int] = None

class ServiceManager:
    """Manages service lifecycle and dependencies."""
    
    def __init__(self, container: ServiceContainer):
        self.container = container
        self.services: Dict[str, ServiceInfo] = {}
        self.startup_order: List[str] = []
        self.shutdown_order: List[str] = []
        self.health_check_interval = 30  # seconds
        self.health_check_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    def register_service(self, name: str, service_type: type, 
                        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
                        dependencies: Optional[List[str]] = None):
        """Register a service for lifecycle management."""
        if name in self.services:
            logger.warning(f"Service {name} already registered, updating configuration")
        
        service_info = ServiceInfo(name, service_type, lifetime)
        if dependencies:
            service_info.dependencies = dependencies
        
        self.services[name] = service_info
        logger.info(f"Registered service: {name} ({lifetime.value})")
    
    def set_startup_order(self, service_names: List[str]):
        """Set the order in which services should be started."""
        self.startup_order = service_names.copy()
        
        # Update startup order in service info
        for i, name in enumerate(service_names):
            if name in self.services:
                self.services[name].startup_order = i
        
        logger.info(f"Set startup order: {service_names}")
    
    def set_shutdown_order(self, service_names: List[str]):
        """Set the order in which services should be stopped."""
        self.shutdown_order = service_names.copy()
        logger.info(f"Set shutdown order: {service_names}")
    
    async def start_all_services(self):
        """Start all registered services in the correct order."""
        if self.is_running:
            logger.warning("Services are already running")
            return
        
        logger.info("Starting all services...")
        self.is_running = True
        
        try:
            # Determine startup order
            startup_sequence = self._determine_startup_sequence()
            
            # Start services in order
            for service_name in startup_sequence:
                await self._start_service(service_name)
            
            # Start health monitoring
            await self._start_health_monitoring()
            
            logger.info("All services started successfully")
            
        except Exception as e:
            logger.error(f"Error starting services: {e}")
            await self.stop_all_services()
            raise
    
    async def stop_all_services(self):
        """Stop all services in the correct order."""
        if not self.is_running:
            logger.warning("Services are not running")
            return
        
        logger.info("Stopping all services...")
        self.is_running = False
        
        try:
            # Stop health monitoring
            await self._stop_health_monitoring()
            
            # Determine shutdown order
            shutdown_sequence = self._determine_shutdown_sequence()
            
            # Stop services in order
            for service_name in shutdown_sequence:
                await self._stop_service(service_name)
            
            logger.info("All services stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping services: {e}")
            raise
    
    def _determine_startup_sequence(self) -> List[str]:
        """Determine the order in which services should be started."""
        if self.startup_order:
            return self.startup_order
        
        # Use dependency-based ordering
        return self._topological_sort()
    
    def _determine_shutdown_sequence(self) -> List[str]:
        """Determine the order in which services should be stopped."""
        if self.shutdown_order:
            return list(reversed(self.shutdown_order))
        
        # Reverse of startup order
        startup_sequence = self._determine_startup_sequence()
        return list(reversed(startup_sequence))
    
    def _topological_sort(self) -> List[str]:
        """Topological sort based on dependencies."""
        # Create dependency graph
        graph = {}
        in_degree = {}
        
        for name in self.services:
            graph[name] = []
            in_degree[name] = 0
        
        for name, service_info in self.services.items():
            for dep in service_info.dependencies:
                if dep in self.services:
                    graph[dep].append(name)
                    in_degree[name] += 1
        
        # Topological sort using Kahn's algorithm
        result = []
        queue = [name for name, degree in in_degree.items() if degree == 0]
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self.services):
            logger.warning("Circular dependency detected, using registration order")
            return list(self.services.keys())
        
        return result
    
    async def _start_service(self, service_name: str):
        """Start a specific service."""
        if service_name not in self.services:
            logger.warning(f"Service {service_name} not found")
            return
        
        service_info = self.services[service_name]
        
        try:
            logger.info(f"Starting service: {service_name}")
            service_info.status = ServiceStatus.STARTING
            
            # Check dependencies
            for dep_name in service_info.dependencies:
                if dep_name not in self.services:
                    raise RuntimeError(f"Dependency {dep_name} not found for service {service_name}")
                
                dep_info = self.services[dep_name]
                if dep_info.status != ServiceStatus.RUNNING:
                    raise RuntimeError(f"Dependency {dep_name} is not running for service {service_name}")
            
            # Resolve service instance (this will create it if needed)
            service_instance = self.container.resolve(service_info.service_type)
            
            # Call start method if it exists
            if hasattr(service_instance, 'start') and callable(getattr(service_instance, 'start')):
                if asyncio.iscoroutinefunction(getattr(service_instance, 'start')):
                    await service_instance.start()
                else:
                    service_instance.start()
            
            service_info.status = ServiceStatus.RUNNING
            service_info.start_time = time.time()
            service_info.error_message = None
            
            logger.info(f"Service {service_name} started successfully")
            
        except Exception as e:
            service_info.status = ServiceStatus.ERROR
            service_info.error_message = str(e)
            logger.error(f"Failed to start service {service_name}: {e}")
            raise
    
    async def _stop_service(self, service_name: str):
        """Stop a specific service."""
        if service_name not in self.services:
            logger.warning(f"Service {service_name} not found")
            return
        
        service_info = self.services[service_name]
        
        if service_info.status == ServiceStatus.STOPPED:
            return
        
        try:
            logger.info(f"Stopping service: {service_name}")
            service_info.status = ServiceStatus.STOPPING
            
            # Resolve service instance
            try:
                service_instance = self.container.resolve(service_info.service_type)
                
                # Call stop method if it exists
                if hasattr(service_instance, 'stop') and callable(getattr(service_instance, 'stop')):
                    if asyncio.iscoroutinefunction(getattr(service_instance, 'stop')):
                        await service_instance.stop()
                    else:
                        service_instance.stop()
                        
            except Exception as e:
                logger.warning(f"Error stopping service {service_name}: {e}")
            
            service_info.status = ServiceStatus.STOPPED
            service_info.stop_time = time.time()
            
            logger.info(f"Service {service_name} stopped successfully")
            
        except Exception as e:
            service_info.status = ServiceStatus.ERROR
            service_info.error_message = str(e)
            logger.error(f"Failed to stop service {service_name}: {e}")
    
    async def _start_health_monitoring(self):
        """Start the health monitoring task."""
        if self.health_check_task and not self.health_check_task.done():
            return
        
        self.health_check_task = asyncio.create_task(self._health_monitoring_loop())
        logger.info("Health monitoring started")
    
    async def _stop_health_monitoring(self):
        """Stop the health monitoring task."""
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            logger.info("Health monitoring stopped")
    
    async def _health_monitoring_loop(self):
        """Health monitoring loop."""
        while self.is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _perform_health_checks(self):
        """Perform health checks on all services."""
        for service_name, service_info in self.services.items():
            if service_info.status == ServiceStatus.RUNNING:
                try:
                    await self._check_service_health(service_name, service_info)
                except Exception as e:
                    logger.error(f"Health check failed for {service_name}: {e}")
    
    async def _check_service_health(self, service_name: str, service_info: ServiceInfo):
        """Check the health of a specific service."""
        try:
            service_instance = self.container.resolve(service_info.service_type)
            
            # Call health check method if it exists
            if hasattr(service_instance, 'health_check') and callable(getattr(service_instance, 'health_check')):
                if asyncio.iscoroutinefunction(getattr(service_instance, 'health_check')):
                    is_healthy = await service_instance.health_check()
                else:
                    is_healthy = service_instance.health_check()
                
                if is_healthy:
                    service_info.status = ServiceStatus.HEALTHY
                else:
                    service_info.status = ServiceStatus.UNHEALTHY
                    logger.warning(f"Service {service_name} is unhealthy")
            else:
                # Default health check: service is healthy if it's running
                service_info.status = ServiceStatus.HEALTHY
            
            service_info.health_check_count += 1
            service_info.last_health_check = time.time()
            
        except Exception as e:
            service_info.status = ServiceStatus.UNHEALTHY
            service_info.error_message = str(e)
            logger.error(f"Health check error for {service_name}: {e}")
    
    def get_service_status(self, service_name: str) -> Optional[ServiceInfo]:
        """Get the status of a specific service."""
        return self.services.get(service_name)
    
    def get_all_service_status(self) -> Dict[str, ServiceInfo]:
        """Get the status of all services."""
        return self.services.copy()
    
    def get_healthy_services(self) -> List[str]:
        """Get list of healthy services."""
        return [name for name, info in self.services.items() 
                if info.status == ServiceStatus.HEALTHY]
    
    def get_unhealthy_services(self) -> List[str]:
        """Get list of unhealthy services."""
        return [name for name, info in self.services.items() 
                if info.status in [ServiceStatus.UNHEALTHY, ServiceStatus.ERROR]]
    
    def get_service_summary(self) -> Dict[str, Any]:
        """Get a summary of all services."""
        total_services = len(self.services)
        running_services = len([s for s in self.services.values() if s.status == ServiceStatus.RUNNING])
        healthy_services = len([s for s in self.services.values() if s.status == ServiceStatus.HEALTHY])
        error_services = len([s for s in self.services.values() if s.status == ServiceStatus.ERROR])
        
        return {
            'total_services': total_services,
            'running_services': running_services,
            'healthy_services': healthy_services,
            'error_services': error_services,
            'is_running': self.is_running,
            'services': {
                name: {
                    'status': info.status.value,
                    'lifetime': info.lifetime.value,
                    'start_time': info.start_time,
                    'last_health_check': info.last_health_check,
                    'error_message': info.error_message,
                    'dependencies': info.dependencies
                }
                for name, info in self.services.items()
            }
        }






