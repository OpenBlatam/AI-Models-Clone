"""
Base Service Interface for HeyGen AI
====================================

Provides common functionality for all services:
- Health checking
- Configuration management
- Error handling
- Logging
- Metrics collection
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json
import traceback

logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    STOPPED = "stopped"


class ServiceType(str, Enum):
    """Service type enumeration"""
    CORE = "core"
    PHASE2 = "phase2"
    PHASE3 = "phase3"
    PHASE4 = "phase4"
    LIBRARY = "library"
    UTILITY = "utility"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    
    status: ServiceStatus
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    
    request_count: int = 0
    error_count: int = 0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0


class BaseService(ABC):
    """
    Base class for all HeyGen AI services.
    
    Provides common functionality and enforces interface compliance.
    """
    
    def __init__(self, service_name: str, service_type: ServiceType, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base service.
        
        Args:
            service_name: Human-readable name of the service
            service_type: Type of service (core, phase2, etc.)
            config: Service configuration dictionary
        """
        self.service_name = service_name
        self.service_type = service_type
        self.config = config or {}
        
        # Service state
        self.status = ServiceStatus.STARTING
        self.start_time = datetime.now()
        self.is_initialized = False
        self.initialization_error: Optional[str] = None
        
        # Metrics
        self.metrics = ServiceMetrics()
        
        # Dependencies
        self.dependencies: List[str] = []
        
        # Initialize the service
        self._initialize_service()
    
    @abstractmethod
    async def _initialize_service_impl(self) -> None:
        """
        Abstract method for service-specific initialization.
        
        Must be implemented by all subclasses.
        """
        pass
    
    def _initialize_service(self) -> None:
        """Initialize the service and handle errors."""
        try:
            logger.info(f"Initializing {self.service_name} service...")
            
            # Run the async initialization
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a task
                task = asyncio.create_task(self._initialize_service_impl())
                # For now, we'll wait for it to complete
                # In a real implementation, you might want to handle this differently
                try:
                    loop.run_until_complete(task)
                except RuntimeError:
                    # If we can't run_until_complete, we'll assume it's already running
                    pass
            else:
                loop.run_until_complete(self._initialize_service_impl())
            
            self.is_initialized = True
            self.status = ServiceStatus.HEALTHY
            logger.info(f"{self.service_name} service initialized successfully")
            
        except Exception as e:
            self.initialization_error = str(e)
            self.status = ServiceStatus.UNHEALTHY
            logger.error(f"Failed to initialize {self.service_name} service: {e}")
            logger.error(traceback.format_exc())
    
    @abstractmethod
    async def health_check(self) -> HealthCheckResult:
        """
        Abstract method for service-specific health checking.
        
        Must be implemented by all subclasses.
        
        Returns:
            HealthCheckResult with service status and details
        """
        pass
    
    async def get_service_info(self) -> Dict[str, Any]:
        """
        Get general service information.
        
        Returns:
            Dictionary with service details
        """
        return {
            "service_name": self.service_name,
            "service_type": self.service_type.value,
            "status": self.status.value,
            "is_initialized": self.is_initialized,
            "initialization_error": self.initialization_error,
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "dependencies": self.dependencies,
            "config_keys": list(self.config.keys()) if self.config else []
        }
    
    async def get_metrics(self) -> ServiceMetrics:
        """
        Get service performance metrics.
        
        Returns:
            ServiceMetrics object with current performance data
        """
        # Update uptime
        self.metrics.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        
        # Try to get system metrics if available
        try:
            import psutil
            process = psutil.Process()
            self.metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            self.metrics.cpu_usage_percent = process.cpu_percent()
        except ImportError:
            # psutil not available, skip system metrics
            pass
        
        return self.metrics
    
    def update_metrics(self, request_success: bool = True, response_time: Optional[float] = None) -> None:
        """
        Update service metrics.
        
        Args:
            request_success: Whether the request was successful
            response_time: Response time in seconds
        """
        self.metrics.request_count += 1
        if not request_success:
            self.metrics.error_count += 1
        
        if response_time is not None:
            # Simple moving average for response time
            if self.metrics.average_response_time == 0.0:
                self.metrics.average_response_time = response_time
            else:
                self.metrics.average_response_time = (
                    self.metrics.average_response_time * 0.9 + response_time * 0.1
                )
        
        self.metrics.last_request_time = datetime.now()
    
    async def shutdown(self) -> None:
        """
        Gracefully shutdown the service.
        
        This method can be overridden by subclasses for custom shutdown logic.
        """
        logger.info(f"Shutting down {self.service_name} service...")
        self.status = ServiceStatus.STOPPING
        
        try:
            # Call the abstract shutdown method if implemented
            if hasattr(self, '_shutdown_impl'):
                await self._shutdown_impl()
            
            self.status = ServiceStatus.STOPPED
            logger.info(f"{self.service_name} service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during {self.service_name} service shutdown: {e}")
            self.status = ServiceStatus.UNHEALTHY
    
    def _validate_config(self, required_keys: List[str]) -> bool:
        """
        Validate that required configuration keys are present.
        
        Args:
            required_keys: List of required configuration keys
            
        Returns:
            True if all required keys are present, False otherwise
        """
        if not self.config:
            logger.error(f"{self.service_name}: No configuration provided")
            return False
        
        missing_keys = [key for key in required_keys if key not in self.config]
        if missing_keys:
            logger.error(f"{self.service_name}: Missing required configuration keys: {missing_keys}")
            return False
        
        return True
    
    def _get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with a default fallback.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def _log_operation(self, operation: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an operation for debugging and monitoring.
        
        Args:
            operation: Name of the operation
            details: Additional details about the operation
        """
        log_data = {
            "service": self.service_name,
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "status": self.status.value
        }
        
        if details:
            log_data.update(details)
        
        logger.info(f"Operation: {operation}", extra=log_data)
    
    def _handle_error(self, error: Exception, context: str = "operation") -> None:
        """
        Handle and log errors consistently.
        
        Args:
            error: The exception that occurred
            context: Context where the error occurred
        """
        error_data = {
            "service": self.service_name,
            "context": context,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.error(f"Error in {context}: {error}", extra=error_data)
        
        # Update metrics
        self.update_metrics(request_success=False)
        
        # Update status if this is a critical error
        if self.status == ServiceStatus.HEALTHY:
            self.status = ServiceStatus.DEGRADED


class ServiceFactory:
    """
    Factory for creating and managing services.
    
    Provides centralized service creation and dependency management.
    """
    
    def __init__(self):
        """Initialize the service factory."""
        self.services: Dict[str, BaseService] = {}
        self.service_configs: Dict[str, Dict[str, Any]] = {}
    
    def register_service(self, service_name: str, service_class: type, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a service class with the factory.
        
        Args:
            service_name: Name for the service
            service_class: Service class to register
            config: Configuration for the service
        """
        self.service_configs[service_name] = config or {}
        logger.info(f"Registered service: {service_name}")
    
    def create_service(self, service_name: str, service_class: type, **kwargs) -> BaseService:
        """
        Create a service instance.
        
        Args:
            service_name: Name of the service
            service_class: Service class to instantiate
            **kwargs: Additional arguments for the service constructor
            
        Returns:
            Service instance
        """
        config = self.service_configs.get(service_name, {})
        config.update(kwargs)
        
        service = service_class(service_name=service_name, **config)
        self.services[service_name] = service
        
        logger.info(f"Created service: {service_name}")
        return service
    
    def get_service(self, service_name: str) -> Optional[BaseService]:
        """
        Get a service by name.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service instance or None if not found
        """
        return self.services.get(service_name)
    
    async def health_check_all(self) -> Dict[str, HealthCheckResult]:
        """
        Perform health check on all registered services.
        
        Returns:
            Dictionary mapping service names to health check results
        """
        results = {}
        
        for service_name, service in self.services.items():
            try:
                results[service_name] = await service.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                results[service_name] = HealthCheckResult(
                    status=ServiceStatus.UNHEALTHY,
                    error_message=str(e)
                )
        
        return results
    
    async def shutdown_all(self) -> None:
        """Shutdown all registered services."""
        logger.info("Shutting down all services...")
        
        for service_name, service in self.services.items():
            try:
                await service.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down {service_name}: {e}")
        
        logger.info("All services shutdown complete")
