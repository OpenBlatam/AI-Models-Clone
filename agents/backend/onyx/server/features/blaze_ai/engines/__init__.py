"""
Engine management system for the Blaze AI module.

This module provides centralized engine management, dispatching,
and monitoring for all AI engines in the system.
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Awaitable

from ..core.interfaces import CoreConfig, SystemHealth, HealthStatus
from ..utils.logging import get_logger

# =============================================================================
# Enums and Data Classes
# =============================================================================

class EngineStatus(Enum):
    """Engine status enumeration."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class EngineMetrics:
    """Engine performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    average_response_time: float = 0.0
    last_request_time: float = 0.0
    error_count: int = 0
    circuit_breaker_state: CircuitBreakerState = CircuitBreakerState.CLOSED

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: type = Exception

# =============================================================================
# Circuit Breaker Implementation
# =============================================================================

class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.config.expected_exception as e:
                self._on_failure()
                raise e
    
    def _on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN

# =============================================================================
# Base Engine Class
# =============================================================================

class Engine(ABC):
    """Abstract base class for all engines."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = get_logger(f"engine.{name}")
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
        self.metrics = EngineMetrics()
        self.status = EngineStatus.IDLE
    
    async def execute(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute an operation with circuit breaker protection."""
        async def _execute():
            self.status = EngineStatus.BUSY
            start_time = time.time()
            
            try:
                result = await self._execute_operation(operation, params)
                self.metrics.successful_requests += 1
                return result
            except Exception as e:
                self.metrics.failed_requests += 1
                self.metrics.error_count += 1
                self.status = EngineStatus.ERROR
                raise e
            finally:
                self.metrics.total_requests += 1
                self.metrics.total_response_time += time.time() - start_time
                self.metrics.average_response_time = (
                    self.metrics.total_response_time / self.metrics.total_requests
                )
                self.metrics.last_request_time = time.time()
                self.status = EngineStatus.IDLE
        
        return await self.circuit_breaker.call(_execute)
    
    @abstractmethod
    async def _execute_operation(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute specific operation - to be implemented by subclasses."""
        pass
    
    def get_health_status(self) -> HealthStatus:
        """Get engine health status."""
        return HealthStatus(
            component=self.name,
            status=self.status.value,
            message=f"Engine {self.name} is {self.status.value}",
            timestamp=time.time(),
            details={
                "metrics": {
                    "total_requests": self.metrics.total_requests,
                    "successful_requests": self.metrics.successful_requests,
                    "failed_requests": self.metrics.failed_requests,
                    "average_response_time": self.metrics.average_response_time,
                    "error_count": self.metrics.error_count
                },
                "circuit_breaker_state": self.circuit_breaker.state.value
            }
        )
    
    async def shutdown(self):
        """Shutdown the engine."""
        self.logger.info(f"Shutting down engine {self.name}")

# =============================================================================
# Engine Manager
# =============================================================================

class EngineManager:
    """Centralized engine manager for the Blaze AI module."""
    
    def __init__(self, config: Optional[CoreConfig] = None):
        self.config = config or CoreConfig()
        self.logger = get_logger("engine_manager")
        self.engines: Dict[str, Engine] = {}
        self.engine_metrics: Dict[str, EngineMetrics] = defaultdict(EngineMetrics)
        self.system_health = SystemHealth()
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        self._monitoring_task: Optional[asyncio.Task] = None
        
        self._register_default_engines()
        self._start_monitoring()
    
    def _register_default_engines(self):
        """Register default engines."""
        try:
            # Register LLM engine
            from .llm import LLMEngine
            self.register_engine("llm", LLMEngine("llm", {
                "model_name": "gpt2",
                "cache_capacity": 1000,
                "device": "auto",
                "precision": "float16",
                "enable_amp": True
            }))
            
            # Register Diffusion engine
            from .diffusion import DiffusionEngine
            self.register_engine("diffusion", DiffusionEngine("diffusion", {
                "model_id": "runwayml/stable-diffusion-v1-5",
                "cache_capacity": 100,
                "device": "auto",
                "precision": "float16",
                "enable_xformers": True
            }))
            
            # Register Router engine
            from .router import RouterEngine
            self.register_engine("router", RouterEngine("router", {
                "enable_caching": True,
                "cache_ttl": 1800,
                "max_concurrent_requests": 50,
                "load_balancing_strategy": "round_robin"
            }))
            
            self.logger.info("Default engines registered successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to register some engines: {e}")
    
    def register_engine(self, name: str, engine: Engine):
        """Register an engine."""
        self.engines[name] = engine
        self.logger.info(f"Registered engine: {name}")
    
    async def dispatch(self, engine_name: str, operation: str, params: Dict[str, Any]) -> Any:
        """Dispatch request to specific engine."""
        if engine_name not in self.engines:
            raise ValueError(f"Engine '{engine_name}' not found")
        
        async with self._semaphore:
            engine = self.engines[engine_name]
            return await engine.execute(operation, params)
    
    async def dispatch_batch(self, requests: List[Dict[str, Any]]) -> List[Any]:
        """Dispatch multiple requests in batch."""
        tasks = []
        for request in requests:
            engine_name = request.get("engine")
            operation = request.get("operation")
            params = request.get("params", {})
            
            if engine_name and operation:
                task = self.dispatch(engine_name, operation, params)
                tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get status of all engines."""
        status = {}
        for name, engine in self.engines.items():
            status[name] = {
                "status": engine.status.value,
                "metrics": {
                    "total_requests": engine.metrics.total_requests,
                    "successful_requests": engine.metrics.successful_requests,
                    "failed_requests": engine.metrics.failed_requests,
                    "average_response_time": engine.metrics.average_response_time,
                    "error_count": engine.metrics.error_count
                },
                "circuit_breaker_state": engine.circuit_breaker.state.value
            }
        return status
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics."""
        total_requests = sum(engine.metrics.total_requests for engine in self.engines.values())
        total_successful = sum(engine.metrics.successful_requests for engine in self.engines.values())
        total_failed = sum(engine.metrics.failed_requests for engine in self.engines.values())
        
        return {
            "total_requests": total_requests,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "success_rate": total_successful / total_requests if total_requests > 0 else 0.0,
            "active_engines": len([e for e in self.engines.values() if e.status != EngineStatus.OFFLINE])
        }
    
    def _start_monitoring(self):
        """Start background monitoring."""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitor_engines())
    
    async def _monitor_engines(self):
        """Background engine monitoring."""
        while True:
            try:
                for name, engine in self.engines.items():
                    health_status = engine.get_health_status()
                    await self.system_health.update_component(
                        name,
                        health_status.status,
                        health_status.message,
                        health_status.details
                    )
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Engine monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def shutdown(self):
        """Shutdown all engines."""
        self.logger.info("Shutting down engine manager...")
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        for name, engine in self.engines.items():
            try:
                await engine.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down engine {name}: {e}")
        
        self.logger.info("Engine manager shutdown complete")

# =============================================================================
# Global Instance Management
# =============================================================================

_default_engine_manager: Optional[EngineManager] = None

def get_engine_manager(config: Optional[CoreConfig] = None) -> EngineManager:
    """Get the global engine manager instance."""
    global _default_engine_manager
    if _default_engine_manager is None:
        _default_engine_manager = EngineManager(config)
    return _default_engine_manager

# Export main classes
__all__ = [
    "Engine",
    "EngineManager",
    "EngineStatus",
    "CircuitBreaker",
    "CircuitBreakerState",
    "EngineMetrics",
    "get_engine_manager"
]


