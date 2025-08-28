"""
Core module for the modular SEO system
Contains the main engine and core interfaces
"""

from .engine import SEOEngine
from .interfaces import TextProcessor, CacheProvider, MetricsProvider
from .plugin_system import PluginManager, plugin_manager, PluginProtocol, PluginInfo
from .event_system import EventBus, event_bus, Event, EventPriority, EventSubscription
from .middleware import MiddlewarePipeline, middleware_registry, BaseMiddleware, MiddlewarePriority, MiddlewareType
from .configuration import ConfigurationManager, config_manager, ConfigSchema, ConfigValidationLevel

__all__ = [
    "SEOEngine",
    "TextProcessor",
    "CacheProvider",
    "MetricsProvider",
    "PluginManager",
    "plugin_manager",
    "PluginProtocol",
    "PluginInfo",
    "EventBus",
    "event_bus",
    "Event",
    "EventPriority",
    "EventSubscription",
    "MiddlewarePipeline",
    "middleware_registry",
    "BaseMiddleware",
    "MiddlewarePriority",
    "MiddlewareType",
    "ConfigurationManager",
    "config_manager",
    "ConfigSchema",
    "ConfigValidationLevel",
]
