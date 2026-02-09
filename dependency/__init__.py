"""
Dependency Injection Module for Instagram Captions API v10.0
Service registration, dependency resolution, and lifecycle management.
"""
from .service_container import ServiceContainer
from .service_manager import ServiceManager

__all__ = [
    'ServiceContainer',
    'ServiceManager'
]






