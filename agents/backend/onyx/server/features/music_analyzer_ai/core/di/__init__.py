"""
Dependency Injection Submodule
Aggregates DI container components.
"""

from typing import Type, Callable, Optional, TypeVar, Any
from .container import DIContainer

T = TypeVar('T')

# Global container instance
_container = DIContainer()


def get_container() -> DIContainer:
    """
    Get global DI container.
    
    Returns:
        Global DIContainer instance.
    """
    return _container


def register_service(
    service_name: str,
    service_class: Type[T],
    singleton: bool = True,
    factory: Optional[Callable] = None
) -> None:
    """
    Register a service in global container.
    
    Args:
        service_name: Name of the service.
        service_class: Class to instantiate.
        singleton: Whether to use singleton pattern.
        factory: Optional factory function.
    """
    _container.register(service_name, service_class, singleton, factory)


def get_service(service_name: str, **kwargs) -> Any:
    """
    Get service from global container.
    
    Args:
        service_name: Name of the service.
        **kwargs: Additional arguments for instantiation.
    
    Returns:
        Service instance.
    """
    return _container.get(service_name, **kwargs)


__all__ = [
    "DIContainer",
    "get_container",
    "register_service",
    "get_service",
]

