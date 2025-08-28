"""
Service Container for Instagram Captions API v10.0
Dependency injection container with service registration and resolution.
"""
import inspect
from typing import Dict, Any, Optional, Callable, Type, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ServiceLifetime(Enum):
    """Service lifetime options."""
    TRANSIENT = "transient"      # New instance every time
    SINGLETON = "singleton"      # Single instance for lifetime
    SCOPED = "scoped"           # Single instance per scope

class ServiceRegistration:
    """Service registration information."""
    
    def __init__(self, service_type: Type, implementation: Union[Type, Callable], 
                 lifetime: ServiceLifetime, factory: Optional[Callable] = None):
        self.service_type = service_type
        self.implementation = implementation
        self.lifetime = lifetime
        self.factory = factory
        self.instance: Optional[Any] = None
        self.dependencies: Optional[list] = None

class ServiceContainer:
    """Dependency injection container."""
    
    def __init__(self):
        self._services: Dict[Type, ServiceRegistration] = {}
        self._scoped_services: Dict[str, Dict[Type, Any]] = {}
        self._current_scope: Optional[str] = None
    
    def register_singleton(self, service_type: Type, implementation: Optional[Type] = None):
        """Register a service as singleton."""
        if implementation is None:
            implementation = service_type
        
        self._services[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.SINGLETON
        )
        logger.debug(f"Registered singleton: {service_type.__name__} -> {implementation.__name__}")
    
    def register_transient(self, service_type: Type, implementation: Optional[Type] = None):
        """Register a service as transient."""
        if implementation is None:
            implementation = service_type
        
        self._services[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.TRANSIENT
        )
        logger.debug(f"Registered transient: {service_type.__name__} -> {implementation.__name__}")
    
    def register_scoped(self, service_type: Type, implementation: Optional[Type] = None):
        """Register a service as scoped."""
        if implementation is None:
            implementation = service_type
        
        self._services[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.SCOPED
        )
        logger.debug(f"Registered scoped: {service_type.__name__} -> {implementation.__name__}")
    
    def register_factory(self, service_type: Type, factory: Callable, lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT):
        """Register a service with a custom factory function."""
        self._services[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation=None,
            lifetime=lifetime,
            factory=factory
        )
        logger.debug(f"Registered factory: {service_type.__name__} with {lifetime.value} lifetime")
    
    def resolve(self, service_type: Type) -> Any:
        """Resolve a service instance."""
        if service_type not in self._services:
            raise ValueError(f"Service not registered: {service_type.__name__}")
        
        registration = self._services[service_type]
        
        # Handle different lifetimes
        if registration.lifetime == ServiceLifetime.SINGLETON:
            if registration.instance is None:
                registration.instance = self._create_instance(registration)
            return registration.instance
        
        elif registration.lifetime == ServiceLifetime.SCOPED:
            if self._current_scope is None:
                raise RuntimeError("Cannot resolve scoped service outside of scope")
            
            if self._current_scope not in self._scoped_services:
                self._scoped_services[self._current_scope] = {}
            
            if service_type not in self._scoped_services[self._current_scope]:
                self._scoped_services[self._current_scope][service_type] = self._create_instance(registration)
            
            return self._scoped_services[self._current_scope][service_type]
        
        else:  # TRANSIENT
            return self._create_instance(registration)
    
    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Create a new instance of a service."""
        try:
            if registration.factory:
                # Use custom factory
                return registration.factory()
            
            # Use constructor injection
            if registration.dependencies is None:
                registration.dependencies = self._get_constructor_dependencies(registration.implementation)
            
            # Resolve dependencies
            resolved_deps = []
            for dep_type in registration.dependencies:
                resolved_deps.append(self.resolve(dep_type))
            
            # Create instance
            if resolved_deps:
                return registration.implementation(*resolved_deps)
            else:
                return registration.implementation()
                
        except Exception as e:
            logger.error(f"Error creating instance of {registration.service_type.__name__}: {e}")
            raise
    
    def _get_constructor_dependencies(self, implementation: Type) -> list:
        """Get constructor dependencies using type hints."""
        try:
            # Get constructor signature
            if hasattr(implementation, '__init__'):
                sig = inspect.signature(implementation.__init__)
            else:
                sig = inspect.signature(implementation)
            
            dependencies = []
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                if param.annotation != inspect.Parameter.empty:
                    dependencies.append(param.annotation)
                else:
                    # Try to infer type from default value
                    if param.default != inspect.Parameter.empty:
                        dependencies.append(type(param.default))
                    else:
                        # Default to object if no type hint
                        dependencies.append(object)
            
            return dependencies
            
        except Exception as e:
            logger.warning(f"Could not determine dependencies for {implementation.__name__}: {e}")
            return []
    
    def create_scope(self, scope_name: str):
        """Create a new scope for scoped services."""
        if scope_name in self._scoped_services:
            logger.warning(f"Scope {scope_name} already exists, clearing previous services")
            del self._scoped_services[scope_name]
        
        self._scoped_services[scope_name] = {}
        logger.debug(f"Created scope: {scope_name}")
        return ServiceScope(self, scope_name)
    
    def enter_scope(self, scope_name: str):
        """Enter an existing scope."""
        if scope_name not in self._scoped_services:
            raise ValueError(f"Scope {scope_name} does not exist")
        
        self._current_scope = scope_name
        logger.debug(f"Entered scope: {scope_name}")
    
    def exit_scope(self):
        """Exit current scope."""
        if self._current_scope:
            logger.debug(f"Exited scope: {self._current_scope}")
            self._current_scope = None
    
    def clear_scope(self, scope_name: str):
        """Clear a specific scope."""
        if scope_name in self._scoped_services:
            del self._scoped_services[scope_name]
            logger.debug(f"Cleared scope: {scope_name}")
    
    def clear_all_scopes(self):
        """Clear all scoped services."""
        self._scoped_services.clear()
        self._current_scope = None
        logger.debug("Cleared all scoped services")
    
    def get_registered_services(self) -> Dict[str, list]:
        """Get all registered services grouped by lifetime."""
        services_by_lifetime = {
            'singleton': [],
            'transient': [],
            'scoped': [],
            'factory': []
        }
        
        for service_type, registration in self._services.items():
            if registration.factory:
                services_by_lifetime['factory'].append(service_type.__name__)
            else:
                services_by_lifetime[registration.lifetime.value].append(service_type.__name__)
        
        return services_by_lifetime
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if a service is registered."""
        return service_type in self._services
    
    def unregister(self, service_type: Type):
        """Unregister a service."""
        if service_type in self._services:
            del self._services[service_type]
            logger.debug(f"Unregistered service: {service_type.__name__}")

class ServiceScope:
    """Context manager for service scopes."""
    
    def __init__(self, container: ServiceContainer, scope_name: str):
        self.container = container
        self.scope_name = scope_name
    
    def __enter__(self):
        self.container.enter_scope(self.scope_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.container.exit_scope()
        if exc_type is not None:
            # Clear scope on exception
            self.container.clear_scope(self.scope_name)






