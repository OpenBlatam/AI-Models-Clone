"""
Core interfaces for the modular SEO system
Defines the contract that all components must implement
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from typing_extensions import Self

# ============================================================================
# CORE INTERFACES
# ============================================================================


@runtime_checkable
class TextProcessor(Protocol):
    """Protocol for text processing components."""

    async def process_text(self, text: str) -> Dict[str, Any]:
        """Process text asynchronously."""
        ...

    def process_text_sync(self, text: str) -> Dict[str, Any]:
        """Process text synchronously."""
        ...

    def get_capabilities(self) -> List[str]:
        """Get list of processing capabilities."""
        ...

    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        ...


@runtime_checkable
class CacheProvider(Protocol):
    """Protocol for cache implementations."""

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        ...

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ...

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        ...

    async def clear(self) -> None:
        """Clear all cached data."""
        ...

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        ...

    async def health_check(self) -> bool:
        """Check cache health."""
        ...


@runtime_checkable
class MetricsProvider(Protocol):
    """Protocol for metrics collection."""

    def record_timing(self, operation: str, duration: float) -> None:
        """Record timing metric."""
        ...

    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment counter metric."""
        ...

    def record_value(self, name: str, value: float) -> None:
        """Record value metric."""
        ...

    def record_gauge(self, name: str, value: float) -> None:
        """Record gauge metric."""
        ...

    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        ...

    async def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        ...


@runtime_checkable
class ModelProvider(Protocol):
    """Protocol for model management."""

    async def load_model(self, model_name: str) -> bool:
        """Load a model."""
        ...

    async def unload_model(self, model_name: str) -> bool:
        """Unload a model."""
        ...

    async def get_loaded_models(self) -> List[str]:
        """Get list of loaded models."""
        ...

    async def health_check(self) -> bool:
        """Check model health."""
        ...


@runtime_checkable
class StorageProvider(Protocol):
    """Protocol for data storage."""

    async def store(self, key: str, data: Any) -> bool:
        """Store data."""
        ...

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data."""
        ...

    async def delete(self, key: str) -> bool:
        """Delete data."""
        ...

    async def list_keys(self, pattern: str = "*") -> List[str]:
        """List keys matching pattern."""
        ...

    async def health_check(self) -> bool:
        """Check storage health."""
        ...


@runtime_checkable
class NotificationProvider(Protocol):
    """Protocol for notifications."""

    async def send_notification(self, message: str, level: str = "info") -> bool:
        """Send notification."""
        ...

    async def send_alert(self, message: str, severity: str = "medium") -> bool:
        """Send alert."""
        ...

    async def health_check(self) -> bool:
        """Check notification service health."""
        ...


# ============================================================================
# ABSTRACT BASE CLASSES
# ============================================================================


class BaseComponent(ABC):
    """Abstract base class for all system components."""

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self._enabled = True
        self._health_status = True

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the component."""
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the component."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check component health."""
        pass

    def enable(self) -> None:
        """Enable the component."""
        self._enabled = True

    def disable(self) -> None:
        """Disable the component."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if component is enabled."""
        return self._enabled

    def get_status(self) -> Dict[str, Any]:
        """Get component status."""
        return {"name": self.name, "version": self.version, "enabled": self._enabled, "healthy": self._health_status}


class BaseProcessor(BaseComponent):
    """Abstract base class for text processors."""

    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        self._processing_stats = {"total_processed": 0, "successful": 0, "failed": 0, "total_time": 0.0}

    @abstractmethod
    async def process(self, text: str) -> Dict[str, Any]:
        """Process text and return results."""
        pass

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self._processing_stats.copy()

    def _update_stats(self, success: bool, processing_time: float) -> None:
        """Update processing statistics."""
        self._processing_stats["total_processed"] += 1
        self._processing_stats["total_time"] += processing_time

        if success:
            self._processing_stats["successful"] += 1
        else:
            self._processing_stats["failed"] += 1


class BaseCache(BaseComponent):
    """Abstract base class for cache implementations."""

    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        self._cache_stats = {"hits": 0, "misses": 0, "evictions": 0, "size": 0}

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cached data."""
        pass

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self._cache_stats.copy()

    def _update_stats(self, stat_type: str, value: int = 1) -> None:
        """Update cache statistics."""
        if stat_type in self._cache_stats:
            self._cache_stats[stat_type] += value


# ============================================================================
# COMPONENT REGISTRY
# ============================================================================


class ComponentRegistry:
    """Registry for managing system components."""

    def __init__(self):
        self._components: Dict[str, BaseComponent] = {}
        self._component_types: Dict[str, List[str]] = {}

    def register(self, component: BaseComponent, component_type: str) -> None:
        """Register a component."""
        self._components[component.name] = component

        if component_type not in self._component_types:
            self._component_types[component_type] = []

        self._component_types[component_type].append(component.name)

    def unregister(self, component_name: str) -> bool:
        """Unregister a component."""
        if component_name in self._components:
            component = self._components[component_name]

            # Remove from type mapping
            for component_type, names in self._component_types.items():
                if component_name in names:
                    names.remove(component_name)

            # Remove from main registry
            del self._components[component_name]
            return True

        return False

    def get_component(self, name: str) -> Optional[BaseComponent]:
        """Get component by name."""
        return self._components.get(name)

    def get_components_by_type(self, component_type: str) -> List[BaseComponent]:
        """Get all components of a specific type."""
        if component_type not in self._component_types:
            return []

        return [self._components[name] for name in self._component_types[component_type] if name in self._components]

    def get_all_components(self) -> Dict[str, BaseComponent]:
        """Get all registered components."""
        return self._components.copy()

    def get_component_types(self) -> List[str]:
        """Get all component types."""
        return list(self._component_types.keys())

    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all components."""
        health_status = {}

        for name, component in self._components.items():
            try:
                health_status[name] = await component.health_check()
            except Exception:
                health_status[name] = False

        return health_status

    async def initialize_all(self) -> Dict[str, bool]:
        """Initialize all components."""
        init_status = {}

        for name, component in self._components.items():
            try:
                init_status[name] = await component.initialize()
            except Exception:
                init_status[name] = False

        return init_status

    async def shutdown_all(self) -> Dict[str, bool]:
        """Shutdown all components."""
        shutdown_status = {}

        for name, component in self._components.items():
            try:
                shutdown_status[name] = await component.shutdown()
            except Exception:
                shutdown_status[name] = False

        return shutdown_status


# Global component registry
component_registry = ComponentRegistry()
