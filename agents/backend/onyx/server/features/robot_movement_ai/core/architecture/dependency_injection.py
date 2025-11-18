"""
Dependency Injection
====================

Sistema de inyección de dependencias.
"""

import logging
from typing import Dict, Any, Optional, Type, TypeVar, Callable
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Container:
    """
    Contenedor de dependencias.
    """
    
    def __init__(self):
        """Inicializar contenedor."""
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
        self._singleton_flags: Dict[Type, bool] = {}
    
    def register(
        self,
        service_type: Type[T],
        implementation: Optional[T] = None,
        factory: Optional[Callable[[], T]] = None,
        singleton: bool = True
    ):
        """
        Registrar servicio.
        
        Args:
            service_type: Tipo del servicio
            implementation: Implementación concreta (opcional)
            factory: Factory function (opcional)
            singleton: Si es singleton
        """
        if implementation is not None:
            if singleton:
                self._singletons[service_type] = implementation
            else:
                self._services[service_type] = implementation
        elif factory is not None:
            self._factories[service_type] = factory
        else:
            raise ValueError("Debe proporcionar implementation o factory")
        
        self._singleton_flags[service_type] = singleton
        logger.debug(f"Servicio registrado: {service_type.__name__}")
    
    def register_instance(self, service_type: Type[T], instance: T):
        """
        Registrar instancia.
        
        Args:
            service_type: Tipo del servicio
            instance: Instancia
        """
        self._singletons[service_type] = instance
        self._singleton_flags[service_type] = True
    
    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolver servicio.
        
        Args:
            service_type: Tipo del servicio
            
        Returns:
            Instancia del servicio
        """
        # Verificar singleton
        if service_type in self._singletons:
            return self._singletons[service_type]
        
        # Verificar servicios normales
        if service_type in self._services:
            instance = self._services[service_type]
            if self._singleton_flags.get(service_type, False):
                self._singletons[service_type] = instance
            return instance
        
        # Verificar factories
        if service_type in self._factories:
            instance = self._factories[service_type]()
            if self._singleton_flags.get(service_type, False):
                self._singletons[service_type] = instance
            return instance
        
        raise ValueError(f"Servicio '{service_type.__name__}' no registrado")
    
    def is_registered(self, service_type: Type) -> bool:
        """
        Verificar si servicio está registrado.
        
        Args:
            service_type: Tipo del servicio
            
        Returns:
            True si está registrado
        """
        return (
            service_type in self._services or
            service_type in self._factories or
            service_type in self._singletons
        )
    
    def clear(self):
        """Limpiar todos los servicios."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._singleton_flags.clear()


class ServiceProvider:
    """
    Proveedor de servicios.
    """
    
    def __init__(self, container: Optional[Container] = None):
        """
        Inicializar proveedor.
        
        Args:
            container: Contenedor (opcional, crea uno nuevo si no se proporciona)
        """
        self.container = container or Container()
    
    def get_service(self, service_type: Type[T]) -> T:
        """
        Obtener servicio.
        
        Args:
            service_type: Tipo del servicio
            
        Returns:
            Instancia del servicio
        """
        return self.container.resolve(service_type)
    
    def register_service(
        self,
        service_type: Type[T],
        implementation: Optional[T] = None,
        factory: Optional[Callable[[], T]] = None,
        singleton: bool = True
    ):
        """
        Registrar servicio.
        
        Args:
            service_type: Tipo del servicio
            implementation: Implementación (opcional)
            factory: Factory (opcional)
            singleton: Si es singleton
        """
        self.container.register(
            service_type=service_type,
            implementation=implementation,
            factory=factory,
            singleton=singleton
        )


# Instancia global
_global_container = Container()
_global_provider = ServiceProvider(_global_container)


def register_service(
    service_type: Type[T],
    implementation: Optional[T] = None,
    factory: Optional[Callable[[], T]] = None,
    singleton: bool = True
):
    """
    Registrar servicio globalmente.
    
    Args:
        service_type: Tipo del servicio
        implementation: Implementación (opcional)
        factory: Factory (opcional)
        singleton: Si es singleton
    """
    _global_container.register(
        service_type=service_type,
        implementation=implementation,
        factory=factory,
        singleton=singleton
    )


def resolve_service(service_type: Type[T]) -> T:
    """
    Resolver servicio globalmente.
    
    Args:
        service_type: Tipo del servicio
        
    Returns:
        Instancia del servicio
    """
    return _global_container.resolve(service_type)


def inject(*dependencies):
    """
    Decorator para inyectar dependencias.
    
    Args:
        dependencies: Tipos de dependencias
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Resolver dependencias
            resolved = []
            for dep_type in dependencies:
                resolved.append(resolve_service(dep_type))
            
            # Llamar función con dependencias inyectadas
            return func(*args, *resolved, **kwargs)
        return wrapper
    return decorator

