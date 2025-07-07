"""
Base Classes and Interfaces for Clean Architecture

This module provides the foundational classes and interfaces that define
the contract between different layers of the application.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

# Type variables for generic classes
T = TypeVar('T')
ID = TypeVar('ID', bound=str)
EntityT = TypeVar('EntityT', bound='BaseEntity')


class BaseEntity(BaseModel):
    """Base class for all domain entities."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValueObject(BaseModel):
    """Base class for value objects."""
    
    class Config:
        frozen = True
        from_attributes = True


class Repository(Generic[T], ABC):
    """Base repository interface for data access."""
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all entities with pagination."""
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete an entity by ID."""
        pass
    
    @abstractmethod
    async def exists(self, id: str) -> bool:
        """Check if entity exists."""
        pass


class UseCase(Generic[T], ABC):
    """Base use case interface."""
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> T:
        """Execute the use case."""
        pass


class Service(ABC):
    """Base service interface."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the service."""
        pass


class Cache(Generic[T], ABC):
    """Base cache interface."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[T]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: T, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache."""
        pass


class EventBus(ABC):
    """Base event bus interface."""
    
    @abstractmethod
    async def publish(self, event: str, data: Dict[str, Any]) -> bool:
        """Publish an event."""
        pass
    
    @abstractmethod
    async def subscribe(self, event: str, handler: callable) -> bool:
        """Subscribe to an event."""
        pass


class Validator(ABC):
    """Base validator interface."""
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate data."""
        pass
    
    @abstractmethod
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        pass


class MetricsCollector(ABC):
    """Base metrics collector interface."""
    
    @abstractmethod
    def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        pass
    
    @abstractmethod
    def record_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a gauge metric."""
        pass
    
    @abstractmethod
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram metric."""
        pass


class Logger(ABC):
    """Base logger interface."""
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        pass
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        pass


class Result(Generic[T]):
    """Result wrapper for operations that can fail."""
    
    def __init__(self, success: bool, data: Optional[T] = None, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error
    
    @classmethod
    def success(cls, data: T) -> 'Result[T]':
        """Create a successful result."""
        return cls(success=True, data=data)
    
    @classmethod
    def failure(cls, error: str) -> 'Result[T]':
        """Create a failed result."""
        return cls(success=False, error=error)
    
    def is_success(self) -> bool:
        """Check if result is successful."""
        return self.success
    
    def is_failure(self) -> bool:
        """Check if result is a failure."""
        return not self.success
    
    def get_data(self) -> Optional[T]:
        """Get the data if successful."""
        return self.data if self.success else None
    
    def get_error(self) -> Optional[str]:
        """Get the error if failed."""
        return self.error if not self.success else None


class Pagination(BaseModel):
    """Pagination parameters."""
    
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        """Calculate offset from page and size."""
        return (self.page - 1) * self.size
    
    @property
    def limit(self) -> int:
        """Get limit (same as size)."""
        return self.size


class SortOrder(str):
    """Sort order enumeration."""
    ASC = "asc"
    DESC = "desc"


class SortField(BaseModel):
    """Sort field definition."""
    
    field: str
    order: SortOrder = SortOrder.ASC


class QueryFilters(BaseModel):
    """Query filters for searching."""
    
    search: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    sort: List[SortField] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination) 