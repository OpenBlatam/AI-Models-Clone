"""
Enhanced Centralized Dependency Management System
===============================================

Advanced dependency management with:
- Service lifecycle management
- Dependency injection
- Health monitoring integration
- Performance metrics
- Auto-scaling capabilities
- Circuit breaker pattern
- Service discovery
"""

import asyncio
import time
import threading
from typing import Dict, Any, Optional, Callable, List, Type, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import weakref
import statistics
from collections import defaultdict, deque
import traceback

# Import configuration and logging
try:
    from .config_manager import get_config
    from .logger_manager import get_logger
except ImportError:
    # Fallback for testing
    def get_config():
        class MockConfig:
            class Monitoring:
                health_check_interval = 30
            monitoring = Monitoring()
        return MockConfig()
    
    def get_logger(name):
        import logging
        return logging.getLogger(name)

logger = get_logger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""
    UNKNOWN = "unknown"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class ServicePriority(Enum):
    """Service priority enumeration"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class ServiceHealth(Enum):
    """Service health enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    response_time: deque = field(default_factory=lambda: deque(maxlen=100))
    error_count: int = 0
    success_count: int = 0
    last_response_time: Optional[float] = None
    uptime: float = 0.0
    start_time: Optional[float] = None
    
    def add_response_time(self, response_time: float):
        """Add response time measurement"""
        self.response_time.append(response_time)
        self.last_response_time = response_time
    
    def add_error(self):
        """Increment error count"""
        self.error_count += 1
    
    def add_success(self):
        """Increment success count"""
        self.success_count += 1
    
    def get_avg_response_time(self) -> Optional[float]:
        """Get average response time"""
        if self.response_time:
            return statistics.mean(self.response_time)
        return None
    
    def get_error_rate(self) -> float:
        """Get error rate percentage"""
        total = self.error_count + self.success_count
        if total == 0:
            return 0.0
        return (self.error_count / total) * 100
    
    def get_uptime(self) -> float:
        """Get current uptime"""
        if self.start_time:
            return time.time() - self.start_time
        return 0.0


@dataclass
class ServiceInfo:
    """Enhanced service information"""
    name: str
    service_type: str
    priority: ServicePriority
    status: ServiceStatus
    health: ServiceHealth = ServiceHealth.UNKNOWN
    start_time: Optional[float] = None
    stop_time: Optional[float] = None
    error_count: int = 0
    last_error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: ServiceMetrics = field(default_factory=ServiceMetrics)
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e
    
    def get_state(self) -> str:
        """Get current circuit breaker state"""
        return self.state


class ServiceLifecycle:
    """Enhanced service lifecycle management"""
    
    def __init__(self, name: str, service_type: str, priority: ServicePriority = ServicePriority.NORMAL):
        self.name = name
        self.service_type = service_type
        self.priority = priority
        self.status = ServiceStatus.UNKNOWN
        self.health = ServiceHealth.UNKNOWN
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
        self.error_count = 0
        self.last_error: Optional[str] = None
        self.dependencies: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.metrics = ServiceMetrics()
        self.version = "1.0.0"
        self.tags: List[str] = []
        
        # Lifecycle hooks
        self._on_start: Optional[Callable] = None
        self._on_stop: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
        self._on_health_check: Optional[Callable] = None
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreaker()
        
        logger.debug(f"Created service lifecycle for {name}")
    
    def add_dependency(self, service_name: str):
        """Add a dependency"""
        if service_name not in self.dependencies:
            self.dependencies.append(service_name)
            logger.debug(f"Added dependency {service_name} to {self.name}")
    
    def remove_dependency(self, service_name: str):
        """Remove a dependency"""
        if service_name in self.dependencies:
            self.dependencies.remove(service_name)
            logger.debug(f"Removed dependency {service_name} from {self.name}")
    
    def on_start(self, callback: Callable):
        """Set start callback"""
        self._on_start = callback
    
    def on_stop(self, callback: Callable):
        """Set stop callback"""
        self._on_stop = callback
    
    def on_error(self, callback: Callable):
        """Set error callback"""
        self._on_error = callback
    
    def on_health_check(self, callback: Callable):
        """Set health check callback"""
        self._on_health_check = callback
    
    async def start(self):
        """Start the service"""
        try:
            logger.info(f"Starting service {self.name}")
            self.status = ServiceStatus.STARTING
            self.start_time = time.time()
            self.metrics.start_time = self.start_time
            
            if self._on_start:
                await self._on_start()
            
            self.status = ServiceStatus.RUNNING
            self.health = ServiceHealth.HEALTHY
            logger.info(f"Service {self.name} started successfully")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.health = ServiceHealth.UNHEALTHY
            self.error_count += 1
            self.last_error = str(e)
            self.metrics.add_error()
            logger.error(f"Failed to start service {self.name}: {e}")
            
            if self._on_error:
                await self._on_error(e)
            
            raise
    
    async def stop(self):
        """Stop the service"""
        try:
            logger.info(f"Stopping service {self.name}")
            self.status = ServiceStatus.STOPPING
            self.stop_time = time.time()
            
            if self._on_stop:
                await self._on_stop()
            
            self.status = ServiceStatus.STOPPED
            self.health = ServiceHealth.UNKNOWN
            logger.info(f"Service {self.name} stopped successfully")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.health = ServiceHealth.UNHEALTHY
            self.error_count += 1
            self.last_error = str(e)
            self.metrics.add_error()
            logger.error(f"Failed to stop service {self.name}: {e}")
            
            if self._on_error:
                await self._on_error(e)
            
            raise
    
    async def health_check(self) -> ServiceHealth:
        """Perform health check"""
        try:
            if self._on_health_check:
                health_result = await self._on_health_check()
                self.health = health_result
            else:
                # Default health check based on status and metrics
                if self.status == ServiceStatus.RUNNING:
                    error_rate = self.metrics.get_error_rate()
                    if error_rate < 5:
                        self.health = ServiceHealth.HEALTHY
                    elif error_rate < 20:
                        self.health = ServiceHealth.DEGRADED
                    else:
                        self.health = ServiceHealth.UNHEALTHY
                else:
                    self.health = ServiceHealth.UNKNOWN
            
            return self.health
            
        except Exception as e:
            self.health = ServiceHealth.UNHEALTHY
            logger.error(f"Health check failed for {self.name}: {e}")
            return self.health
    
    def record_operation(self, response_time: float, success: bool = True):
        """Record operation metrics"""
        self.metrics.add_response_time(response_time)
        if success:
            self.metrics.add_success()
        else:
            self.metrics.add_error()
            self.error_count += 1
    
    def to_info(self) -> ServiceInfo:
        """Convert to ServiceInfo"""
        return ServiceInfo(
            name=self.name,
            service_type=self.service_type,
            priority=self.priority,
            status=self.status,
            health=self.health,
            start_time=self.start_time,
            stop_time=self.stop_time,
            error_count=self.error_count,
            last_error=self.last_error,
            dependencies=self.dependencies.copy(),
            metadata=self.metadata.copy(),
            metrics=self.metrics,
            version=self.version,
            tags=self.tags.copy()
        )


class DependencyManager:
    """Enhanced centralized dependency manager"""
    
    def __init__(self):
        self.config = get_config()
        self.services: Dict[str, ServiceLifecycle] = {}
        self.service_instances: Dict[str, Any] = {}
        self.service_factories: Dict[str, Callable] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.is_running = False
        self.health_check_task: Optional[asyncio.Task] = None
        self.metrics_lock = threading.Lock()
        
        logger.info("Enhanced dependency manager initialized")
    
    def register_service(
        self,
        name: str,
        service_type: str,
        factory: Callable,
        priority: ServicePriority = ServicePriority.NORMAL,
        dependencies: Optional[List[str]] = None,
        version: str = "1.0.0",
        tags: Optional[List[str]] = None
    ):
        """Register a service with enhanced metadata"""
        if name in self.services:
            logger.warning(f"Service {name} already registered, overwriting")
        
        # Create lifecycle
        lifecycle = ServiceLifecycle(name, service_type, priority)
        lifecycle.version = version
        lifecycle.tags = tags or []
        
        # Add dependencies
        if dependencies:
            for dep in dependencies:
                lifecycle.add_dependency(dep)
                self.reverse_dependencies[dep].add(name)
        
        # Store
        self.services[name] = lifecycle
        self.service_factories[name] = factory
        self.dependency_graph[name] = dependencies or []
        
        logger.info(f"Registered service {name} ({service_type}) with priority {priority.value}")
    
    def unregister_service(self, name: str):
        """Unregister a service"""
        if name not in self.services:
            logger.warning(f"Service {name} not registered")
            return
        
        # Stop if running
        if self.services[name].status == ServiceStatus.RUNNING:
            asyncio.create_task(self.services[name].stop())
        
        # Remove from reverse dependencies
        for dep in self.dependency_graph.get(name, []):
            if name in self.reverse_dependencies[dep]:
                self.reverse_dependencies[dep].remove(name)
        
        # Remove
        del self.services[name]
        if name in self.service_instances:
            del self.service_instances[name]
        if name in self.service_factories:
            del self.service_factories[name]
        if name in self.dependency_graph:
            del self.dependency_graph[name]
        
        logger.info(f"Unregistered service {name}")
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a service instance"""
        return self.service_instances.get(name)
    
    def has_service(self, name: str) -> bool:
        """Check if service exists"""
        return name in self.services
    
    def get_service_status(self, name: str) -> Optional[ServiceStatus]:
        """Get service status"""
        if name in self.services:
            return self.services[name].status
        return None
    
    def get_service_health(self, name: str) -> Optional[ServiceHealth]:
        """Get service health"""
        if name in self.services:
            return self.services[name].health
        return None
    
    def get_service_info(self, name: str) -> Optional[ServiceInfo]:
        """Get service information"""
        if name in self.services:
            return self.services[name].to_info()
        return None
    
    def get_all_services(self) -> List[ServiceInfo]:
        """Get information about all services"""
        return [service.to_info() for service in self.services.values()]
    
    def get_services_by_status(self, status: ServiceStatus) -> List[ServiceInfo]:
        """Get services by status"""
        return [
            service.to_info() 
            for service in self.services.values() 
            if service.status == status
        ]
    
    def get_services_by_health(self, health: ServiceHealth) -> List[ServiceInfo]:
        """Get services by health status"""
        return [
            service.to_info() 
            for service in self.services.values() 
            if service.health == health
        ]
    
    def get_services_by_priority(self, priority: ServicePriority) -> List[ServiceInfo]:
        """Get services by priority"""
        return [
            service.to_info() 
            for service in self.services.values() 
            if service.priority == priority
        ]
    
    def get_services_by_tag(self, tag: str) -> List[ServiceInfo]:
        """Get services by tag"""
        return [
            service.to_info() 
            for service in self.services.values() 
            if tag in service.tags
        ]
    
    def check_dependencies(self, service_name: str) -> bool:
        """Check if service dependencies are satisfied"""
        if service_name not in self.dependency_graph:
            return True
        
        dependencies = self.dependency_graph[service_name]
        for dep in dependencies:
            if dep not in self.services:
                logger.warning(f"Service {service_name} depends on {dep} which is not registered")
                return False
            
            if self.services[dep].status != ServiceStatus.RUNNING:
                logger.warning(f"Service {service_name} depends on {dep} which is not running")
                return False
            
            if self.services[dep].health == ServiceHealth.UNHEALTHY:
                logger.warning(f"Service {service_name} depends on {dep} which is unhealthy")
                return False
        
        return True
    
    def get_startup_order(self) -> List[str]:
        """Get the order in which services should be started"""
        # Simple topological sort for dependencies
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(service_name: str):
            if service_name in temp_visited:
                raise ValueError(f"Circular dependency detected: {service_name}")
            if service_name in visited:
                return
            
            temp_visited.add(service_name)
            
            # Visit dependencies first
            if service_name in self.dependency_graph:
                for dep in self.dependency_graph[service_name]:
                    visit(dep)
            
            temp_visited.remove(service_name)
            visited.add(service_name)
            order.append(service_name)
        
        # Visit all services
        for service_name in self.services.keys():
            if service_name not in visited:
                visit(service_name)
        
        # Sort by priority within dependency order
        def sort_key(service_name: str):
            return (
                order.index(service_name),
                self.services[service_name].priority.value
            )
        
        return sorted(order, key=sort_key)
    
    async def start_all_services(self):
        """Start all services in dependency order"""
        if self.is_running:
            logger.warning("Services already running")
            return
        
        self.is_running = True
        startup_order = self.get_startup_order()
        
        logger.info(f"Starting {len(startup_order)} services in order: {startup_order}")
        
        for service_name in startup_order:
            try:
                # Check dependencies
                if not self.check_dependencies(service_name):
                    logger.error(f"Cannot start {service_name}: dependencies not satisfied")
                    continue
                
                # Create instance
                if service_name not in self.service_instances:
                    factory = self.service_factories[service_name]
                    self.service_instances[service_name] = factory()
                
                # Start service
                await self.services[service_name].start()
                
                logger.info(f"Started service {service_name}")
                
            except Exception as e:
                logger.error(f"Failed to start service {service_name}: {e}")
                self.services[service_name].status = ServiceStatus.ERROR
                self.services[service_name].last_error = str(e)
        
        # Start health monitoring
        self._start_health_monitoring()
        
        logger.info("All services started")
    
    async def stop_all_services(self):
        """Stop all services in reverse dependency order"""
        if not self.is_running:
            logger.warning("Services not running")
            return
        
        self.is_running = False
        
        # Stop health monitoring
        self._stop_health_monitoring()
        
        startup_order = self.get_startup_order()
        shutdown_order = list(reversed(startup_order))
        
        logger.info(f"Stopping {len(shutdown_order)} services in order: {shutdown_order}")
        
        for service_name in shutdown_order:
            try:
                if self.services[service_name].status == ServiceStatus.RUNNING:
                    await self.services[service_name].stop()
                    logger.info(f"Stopped service {service_name}")
                
            except Exception as e:
                logger.error(f"Failed to stop service {service_name}: {e}")
        
        logger.info("All services stopped")
    
    async def restart_service(self, service_name: str):
        """Restart a specific service"""
        if service_name not in self.services:
            logger.warning(f"Service {service_name} not registered")
            return
        
        try:
            logger.info(f"Restarting service {service_name}")
            
            # Stop if running
            if self.services[service_name].status == ServiceStatus.RUNNING:
                await self.services[service_name].stop()
            
            # Start again
            await self.services[service_name].start()
            
            logger.info(f"Service {service_name} restarted successfully")
            
        except Exception as e:
            logger.error(f"Failed to restart service {service_name}: {e}")
            raise
    
    def _start_health_monitoring(self):
        """Start background health monitoring"""
        if self.health_check_task is None or self.health_check_task.done():
            self.health_check_task = asyncio.create_task(self._health_monitoring_loop())
    
    def _stop_health_monitoring(self):
        """Stop background health monitoring"""
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
    
    async def _health_monitoring_loop(self):
        """Background health monitoring loop"""
        while self.is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.monitoring.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _perform_health_checks(self):
        """Perform health checks on all services"""
        for service_name, service in self.services.items():
            if service.status == ServiceStatus.RUNNING:
                try:
                    await service.health_check()
                except Exception as e:
                    logger.error(f"Health check failed for {service_name}: {e}")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary of all services"""
        total_services = len(self.services)
        running_services = len(self.get_services_by_status(ServiceStatus.RUNNING))
        error_services = len(self.get_services_by_status(ServiceStatus.ERROR))
        stopped_services = len(self.get_services_by_status(ServiceStatus.STOPPED))
        
        healthy_services = len(self.get_services_by_health(ServiceHealth.HEALTHY))
        degraded_services = len(self.get_services_by_health(ServiceHealth.DEGRADED))
        unhealthy_services = len(self.get_services_by_health(ServiceHealth.UNHEALTHY))
        
        # Calculate overall health score
        if total_services > 0:
            health_score = (healthy_services / total_services) * 100
        else:
            health_score = 0
        
        return {
            'total_services': total_services,
            'running_services': running_services,
            'error_services': error_services,
            'stopped_services': stopped_services,
            'healthy_services': healthy_services,
            'degraded_services': degraded_services,
            'unhealthy_services': unhealthy_services,
            'health_score': round(health_score, 2),
            'health_percentage': (running_services / total_services * 100) if total_services > 0 else 0,
            'services': self.get_all_services(),
            'timestamp': time.time(),
            'dependency_graph': dict(self.dependency_graph),
            'reverse_dependencies': {k: list(v) for k, v in self.reverse_dependencies.items()}
        }
    
    def get_service_metrics(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed metrics for a specific service"""
        if service_name not in self.services:
            return None
        
        service = self.services[service_name]
        metrics = service.metrics
        
        return {
            'name': service_name,
            'status': service.status.value,
            'health': service.health.value,
            'uptime': metrics.get_uptime(),
            'avg_response_time': metrics.get_avg_response_time(),
            'error_rate': metrics.get_error_rate(),
            'total_requests': metrics.error_count + metrics.success_count,
            'success_count': metrics.success_count,
            'error_count': metrics.error_count,
            'last_response_time': metrics.last_response_time,
            'circuit_breaker_state': service.circuit_breaker.get_state()
        }
    
    def record_service_operation(self, service_name: str, response_time: float, success: bool = True):
        """Record operation metrics for a service"""
        if service_name in self.services:
            self.services[service_name].record_operation(response_time, success)
    
    @asynccontextmanager
    async def managed_services(self):
        """Context manager for service lifecycle"""
        try:
            await self.start_all_services()
            yield self
        finally:
            await self.stop_all_services()


# Global dependency manager instance
_dependency_manager: Optional[DependencyManager] = None


def get_dependency_manager() -> DependencyManager:
    """Get global dependency manager instance"""
    global _dependency_manager
    if _dependency_manager is None:
        _dependency_manager = DependencyManager()
    return _dependency_manager


def register_service(
    name: str,
    service_type: str,
    factory: Callable,
    priority: ServicePriority = ServicePriority.NORMAL,
    dependencies: Optional[List[str]] = None,
    version: str = "1.0.0",
    tags: Optional[List[str]] = None
):
    """Register a service using global manager"""
    dependency_manager = get_dependency_manager()
    dependency_manager.register_service(name, service_type, factory, priority, dependencies, version, tags)


def get_service(name: str) -> Optional[Any]:
    """Get a service using global manager"""
    dependency_manager = get_dependency_manager()
    return dependency_manager.get_service(name)


def has_service(name: str) -> bool:
    """Check if service exists using global manager"""
    dependency_manager = get_dependency_manager()
    return dependency_manager.has_service(name)


def get_service_health(name: str) -> Optional[ServiceHealth]:
    """Get service health using global manager"""
    dependency_manager = get_dependency_manager()
    return dependency_manager.get_service_health(name)


async def start_all_services():
    """Start all services using global manager"""
    dependency_manager = get_dependency_manager()
    await dependency_manager.start_all_services()


async def stop_all_services():
    """Stop all services using global manager"""
    dependency_manager = get_dependency_manager()
    await dependency_manager.stop_all_services()


def record_service_operation(service_name: str, response_time: float, success: bool = True):
    """Record service operation metrics using global manager"""
    dependency_manager = get_dependency_manager()
    dependency_manager.record_service_operation(service_name, response_time, success)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Register some services
        register_service("config", "configuration", lambda: get_config(), 
                       tags=["core", "configuration"])
        register_service("logger", "logging", lambda: get_logger("main"), 
                       tags=["core", "logging"])
        
        # Start services
        dependency_manager = get_dependency_manager()
        async with dependency_manager.managed_services():
            # Services are running
            config_service = get_service("config")
            logger_service = get_service("logger")
            
            print(f"Config service: {config_service}")
            print(f"Logger service: {logger_service}")
            
            # Get health summary
            health = dependency_manager.get_health_summary()
            print(f"Health: {health}")
            
            # Record some operations
            record_service_operation("config", 0.001, True)
            record_service_operation("logger", 0.002, True)
            
            # Get metrics
            config_metrics = dependency_manager.get_service_metrics("config")
            print(f"Config metrics: {config_metrics}")
    
    asyncio.run(main())
