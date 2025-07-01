"""
Circuit Breaker Interface
=========================

Abstract interface for circuit breaker pattern implementation.
"""

from abc import ABC, abstractmethod
from typing import Callable, Any
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ICircuitBreaker(ABC):
    """Abstract interface for circuit breaker operations."""
    
    @abstractmethod
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        pass
    
    @abstractmethod
    def get_state(self) -> CircuitState:
        """Get current circuit breaker state."""
        pass
    
    @abstractmethod
    def get_failure_count(self) -> int:
        """Get current failure count."""
        pass
    
    @abstractmethod
    async def reset(self):
        """Manually reset circuit breaker."""
        pass
    
    @abstractmethod
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        pass 