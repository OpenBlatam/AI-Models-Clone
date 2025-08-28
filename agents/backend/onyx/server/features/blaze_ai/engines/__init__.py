"""
Modular Engine System for Blaze AI.

This module provides a clean, modular architecture for engine management,
circuit breakers, factories, orchestration, and plugin systems.
"""

from __future__ import annotations

# =============================================================================
# Core Engine Infrastructure
# =============================================================================

from .base import (
    Engine,
    EngineStatus,
    EngineType,
    EnginePriority,
    EngineMetadata,
    EngineCapabilities,
    Executable,
    HealthCheckable,
    Configurable,
    MetricsProvider
)

# =============================================================================
# Circuit Breaker Pattern
# =============================================================================

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerConfig,
    CircuitBreakerMetrics,
    circuit_breaker_context,
    create_circuit_breaker,
    create_resilient_circuit_breaker,
    create_stable_circuit_breaker
)

# =============================================================================
# Engine Factory System
# =============================================================================

from .factory import (
    EngineFactory,
    EngineFactoryConfig,
    EngineTemplate,
    create_engine_factory,
    create_standard_engine_factory,
    create_minimal_engine_factory,
    get_engine_factory,
    set_engine_factory
)

# =============================================================================
# Engine Manager & Orchestration
# =============================================================================

from .manager import (
    EngineManager,
    EngineManagerConfig,
    EngineInstance,
    get_engine_manager,
    shutdown_engine_manager
)

# =============================================================================
# Plugin System
# =============================================================================

from .plugins import (
    PluginManager,
    PluginLoader,
    PluginConfig,
    PluginMetadata,
    PluginInfo,
    create_plugin_manager,
    create_standard_plugin_manager,
    get_plugin_manager
)

# =============================================================================
# Legacy Compatibility (for backward compatibility)
# =============================================================================

# Re-export the main classes for backward compatibility
__all__ = [
    # Core Engine Infrastructure
    "Engine",
    "EngineStatus", 
    "EngineType",
    "EnginePriority",
    "EngineMetadata",
    "EngineCapabilities",
    "Executable",
    "HealthCheckable",
    "Configurable",
    "MetricsProvider",
    
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerState",
    "CircuitBreakerConfig",
    "CircuitBreakerMetrics",
    "circuit_breaker_context",
    "create_circuit_breaker",
    "create_resilient_circuit_breaker",
    "create_stable_circuit_breaker",
    
    # Factory System
    "EngineFactory",
    "EngineFactoryConfig",
    "EngineTemplate",
    "create_engine_factory",
    "create_standard_engine_factory",
    "create_minimal_engine_factory",
    "get_engine_factory",
    "set_engine_factory",
    
    # Manager & Orchestration
    "EngineManager",
    "EngineManagerConfig",
    "EngineInstance",
    "get_engine_manager",
    "shutdown_engine_manager",
    
    # Plugin System
    "PluginManager",
    "PluginLoader",
    "PluginConfig",
    "PluginMetadata",
    "PluginInfo",
    "create_plugin_manager",
    "create_standard_plugin_manager",
    "get_plugin_manager",
]

# =============================================================================
# Version Information
# =============================================================================

__version__ = "2.0.0"
__author__ = "Blaze AI Team"
__description__ = "Modular Engine System for Blaze AI"

# =============================================================================
# Quick Access Functions
# =============================================================================

def get_default_engine_manager():
    """Get the default engine manager instance."""
    return get_engine_manager()

def get_default_engine_factory():
    """Get the default engine factory instance."""
    return get_engine_factory()

def get_default_plugin_manager():
    """Get the default plugin manager instance."""
    return get_plugin_manager()

def create_engine(template_name: str, config: dict = None, instance_name: str = None):
    """Quick function to create an engine using the default factory."""
    factory = get_default_engine_factory()
    return factory.create_engine(template_name, config, instance_name)

def list_available_engines():
    """Quick function to list all available engine templates."""
    factory = get_default_engine_factory()
    return factory.get_available_templates()

def get_engine_info(template_name: str):
    """Quick function to get information about an engine template."""
    factory = get_default_engine_factory()
    return factory.get_template_info(template_name)

def list_plugins():
    """Quick function to list all available plugins."""
    plugin_manager = get_default_plugin_manager()
    return plugin_manager.loader.list_plugins()

def get_plugin_info(plugin_name: str):
    """Quick function to get information about a plugin."""
    plugin_manager = get_default_plugin_manager()
    return plugin_manager.loader.get_plugin_info(plugin_name)

def install_plugin(plugin_path: str):
    """Quick function to install a plugin."""
    plugin_manager = get_default_plugin_manager()
    return plugin_manager.install_plugin(plugin_path)

def remove_plugin(plugin_name: str):
    """Quick function to remove a plugin."""
    plugin_manager = get_default_plugin_manager()
    return plugin_manager.remove_plugin(plugin_name)

# =============================================================================
# System Status Functions
# =============================================================================

def get_system_status():
    """Get comprehensive system status including engines and plugins."""
    engine_manager = get_default_engine_manager()
    plugin_manager = get_default_plugin_manager()
    
    return {
        "engines": {
            "status": engine_manager.get_engine_status(),
            "metrics": engine_manager.get_system_metrics(),
            "total_engines": len(engine_manager.engines),
            "healthy_engines": len([e for e in engine_manager.engines.values() if e.engine.is_healthy()])
        },
        "plugins": {
            "metrics": plugin_manager.loader.get_plugin_metrics(),
            "total_plugins": len(plugin_manager.loader.plugins),
            "total_plugin_engines": len(plugin_manager.get_all_engine_templates())
        },
        "factory": {
            "available_templates": engine_manager.factory.get_available_templates(),
            "total_templates": len(engine_manager.factory.engine_templates)
        }
    }

def get_engine_health_summary():
    """Get a summary of engine health status."""
    engine_manager = get_default_engine_manager()
    status = engine_manager.get_engine_status()
    
    summary = {
        "total_engines": len(status),
        "healthy": 0,
        "unhealthy": 0,
        "by_type": {},
        "by_status": {}
    }
    
    for engine_name, engine_status in status.items():
        engine_type = engine_status.get("template", "unknown")
        engine_health = engine_status.get("status", "unknown")
        
        # Count by health
        if engine_health in ["idle", "busy"]:
            summary["healthy"] += 1
        else:
            summary["unhealthy"] += 1
        
        # Count by type
        if engine_type not in summary["by_type"]:
            summary["by_type"][engine_type] = 0
        summary["by_type"][engine_type] += 1
        
        # Count by status
        if engine_health not in summary["by_status"]:
            summary["by_status"][engine_health] = 0
        summary["by_status"][engine_health] += 1
    
    return summary


