"""
Protocol Definitions for Onyx Features - Production Optimized.

This module defines protocols (interfaces) for better type safety,
code organization, and maintainability in production environments.
"""

from typing import Protocol, Any, Dict, List, Optional, Union, AsyncContextManager
from abc import ABC, abstractmethod
from datetime import datetime
import asyncio


class CacheProtocol(Protocol):
    """Protocol for cache implementations."""
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache."""
        ...
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, namespace: str = "default") -> bool:
        """Set value in cache."""
        ...
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache."""
        ...
    
    async def clear(self, namespace: str = "default") -> bool:
        """Clear cache namespace."""
        ...
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        ...


class MessageServiceProtocol(Protocol):
    """Protocol for message service implementations."""
    
    async def create_message(self, content: str, **kwargs) -> Any:
        """Create a new message."""
        ...
    
    async def get_message(self, message_id: str, **kwargs) -> Optional[Any]:
        """Retrieve a message by ID."""
        ...
    
    async def delete_message(self, message_id: str, **kwargs) -> bool:
        """Delete a message."""
        ...
    
    async def list_messages(self, **kwargs) -> List[Any]:
        """List messages with filtering."""
        ...


class ValidationProtocol(Protocol):
    """Protocol for validation implementations."""
    
    def validate(self, data: Any, **kwargs) -> Any:
        """Validate data and return result."""
        ...
    
    def is_valid(self, data: Any, **kwargs) -> bool:
        """Check if data is valid."""
        ...


class MonitoringProtocol(Protocol):
    """Protocol for monitoring implementations."""
    
    async def track_operation(self, name: str, duration: float, **kwargs) -> None:
        """Track operation metrics."""
        ...
    
    async def increment_counter(self, name: str, value: int = 1, **kwargs) -> None:
        """Increment counter metric."""
        ...
    
    async def record_gauge(self, name: str, value: float, **kwargs) -> None:
        """Record gauge metric."""
        ...


class ConnectionPoolProtocol(Protocol):
    """Protocol for connection pool implementations."""
    
    async def get_connection(self) -> AsyncContextManager[Any]:
        """Get connection from pool."""
        ...
    
    async def close_all(self) -> None:
        """Close all connections."""
        ...
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        ...


class ProcessorProtocol(Protocol):
    """Protocol for data processor implementations."""
    
    async def process(self, data: Any, **kwargs) -> Any:
        """Process data and return result."""
        ...
    
    async def process_batch(self, data_list: List[Any], **kwargs) -> List[Any]:
        """Process batch of data."""
        ...
    
    def can_process(self, data: Any) -> bool:
        """Check if processor can handle data."""
        ...


class SerializerProtocol(Protocol):
    """Protocol for serializer implementations."""
    
    def serialize(self, obj: Any) -> bytes:
        """Serialize object to bytes."""
        ...
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to object."""
        ...
    
    def get_content_type(self) -> str:
        """Get content type identifier."""
        ...


# Abstract base classes for common patterns

class BaseService(ABC):
    """Base service class with common patterns."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize service."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown service."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        pass
    
    async def ensure_initialized(self) -> None:
        """Ensure service is initialized."""
        if not self._initialized:
            await self.initialize()
            self._initialized = True


class BaseProcessor(ABC):
    """Base processor class with common patterns."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self._stats = {"processed": 0, "errors": 0, "start_time": datetime.now()}
    
    @abstractmethod
    async def process_single(self, data: Any, **kwargs) -> Any:
        """Process single item."""
        pass
    
    async def process_batch(self, data_list: List[Any], **kwargs) -> List[Any]:
        """Process batch of items with error handling."""
        results = []
        
        for item in data_list:
            try:
                result = await self.process_single(item, **kwargs)
                results.append(result)
                self._stats["processed"] += 1
            except Exception as e:
                self._stats["errors"] += 1
                results.append({"error": str(e), "item": item})
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        return self._stats.copy()


class BaseCache(ABC):
    """Base cache implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0}
    
    @abstractmethod
    async def _get_internal(self, key: str, namespace: str) -> Optional[Any]:
        """Internal get implementation."""
        pass
    
    @abstractmethod
    async def _set_internal(self, key: str, value: Any, ttl: Optional[int], namespace: str) -> bool:
        """Internal set implementation."""
        pass
    
    @abstractmethod
    async def _delete_internal(self, key: str, namespace: str) -> bool:
        """Internal delete implementation."""
        pass
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get with stats tracking."""
        result = await self._get_internal(key, namespace)
        if result is not None:
            self._stats["hits"] += 1
        else:
            self._stats["misses"] += 1
        return result
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, namespace: str = "default") -> bool:
        """Set with stats tracking."""
        result = await self._set_internal(key, value, ttl, namespace)
        if result:
            self._stats["sets"] += 1
        return result
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete with stats tracking."""
        result = await self._delete_internal(key, namespace)
        if result:
            self._stats["deletes"] += 1
        return result
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self._stats.copy()


# Factory protocols

class ServiceFactory(Protocol):
    """Protocol for service factories."""
    
    def create_service(self, service_type: str, config: Optional[Dict[str, Any]] = None) -> BaseService:
        """Create service instance."""
        ...
    
    def list_available_services(self) -> List[str]:
        """List available service types."""
        ...


class ProcessorFactory(Protocol):
    """Protocol for processor factories."""
    
    def create_processor(self, processor_type: str, config: Optional[Dict[str, Any]] = None) -> BaseProcessor:
        """Create processor instance."""
        ...
    
    def list_available_processors(self) -> List[str]:
        """List available processor types."""
        ...


# Export protocols
__all__ = [
    "CacheProtocol",
    "MessageServiceProtocol", 
    "ValidationProtocol",
    "MonitoringProtocol",
    "ConnectionPoolProtocol",
    "ProcessorProtocol",
    "SerializerProtocol",
    "BaseService",
    "BaseProcessor",
    "BaseCache",
    "ServiceFactory",
    "ProcessorFactory"
] 