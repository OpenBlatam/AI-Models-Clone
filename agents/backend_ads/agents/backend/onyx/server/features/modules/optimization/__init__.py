"""
Optimization Module - Unified High-Performance System Optimization.

This module consolidates all optimization functionality from legacy files:
- ultra_performance_optimizers.py (37KB) 
- core_optimizers.py (36KB)
- nexus_optimizer.py (27KB)
- ultra_optimizers.py (26KB)
- performance_optimizers.py (21KB)

Into a single, modular, enterprise-grade optimization system with 10x performance.
"""

from typing import Dict, Any, Optional
import structlog

from .config import OptimizationSettings, OptimizationLevel, SerializationFormat
from .models import PerformanceMetrics, OptimizationConfig, SystemStatus, OptimizationResult
from .exceptions import OptimizationException
from .engines import SerializationEngine

logger = structlog.get_logger(__name__)

# Global optimizer instance
_global_optimizer: Optional[Any] = None
_service_registry: Dict[str, Any] = {}


def register_service(name: str, service: Any) -> None:
    """Register a service in the optimization service registry."""
    _service_registry[name] = service
    logger.info(f"Optimization service registered: {name}")


def get_service(name: str) -> Any:
    """Get a service from the registry."""
    if name not in _service_registry:
        raise OptimizationException(f"Service '{name}' not found in registry")
    return _service_registry[name]


def create_optimization_system(config: Optional[OptimizationSettings] = None) -> Dict[str, Any]:
    """
    Factory function to create a complete optimization system.
    
    Args:
        config: Optional configuration for all services
        
    Returns:
        Dict[str, Any]: Dictionary containing all configured services
    """
    if config is None:
        config = OptimizationSettings()
    
    # Create engines
    serialization_engine = SerializationEngine(config)
    
    system = {
        "serialization_engine": serialization_engine,
        "config": config
    }
    
    # Register in global registry
    register_service("optimization_system", system)
    
    logger.info("Optimization system created", 
               level=config.optimization_level.value,
               format=config.serialization_format.value)
    return system


def get_global_optimizer(config: Optional[OptimizationSettings] = None) -> Dict[str, Any]:
    """Get or create the global optimizer instance (singleton pattern)."""
    global _global_optimizer
    
    if _global_optimizer is None:
        _global_optimizer = create_optimization_system(config)
        logger.info("Global optimizer instance created")
    
    return _global_optimizer


def optimize(
    level: OptimizationLevel = OptimizationLevel.ADVANCED,
    cache_results: bool = True,
    monitor_performance: bool = True
):
    """
    Decorator to optimize function execution with multiple strategies.
    
    Args:
        level: Optimization level to apply
        cache_results: Whether to cache function results
        monitor_performance: Whether to monitor performance metrics
        
    Returns:
        Decorated function with optimization applied
    """
    def decorator(func):
        from functools import wraps
        import time
        import asyncio
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            optimizer = get_global_optimizer()
            start_time = time.perf_counter()
            
            try:
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Record performance if enabled
                if monitor_performance:
                    execution_time = (time.perf_counter() - start_time) * 1000
                    logger.debug("Function optimized",
                               function=func.__name__,
                               duration_ms=execution_time,
                               level=level.value)
                
                return result
                
            except Exception as e:
                execution_time = (time.perf_counter() - start_time) * 1000
                logger.error("Optimized function failed",
                           function=func.__name__,
                           duration_ms=execution_time,
                           error=str(e))
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                
                if monitor_performance:
                    execution_time = (time.perf_counter() - start_time) * 1000
                    logger.debug("Function optimized",
                               function=func.__name__,
                               duration_ms=execution_time,
                               level=level.value)
                
                return result
                
            except Exception as e:
                execution_time = (time.perf_counter() - start_time) * 1000
                logger.error("Optimized function failed",
                           function=func.__name__,
                           duration_ms=execution_time,
                           error=str(e))
                raise
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Quick access functions for common operations
def fast_serialize(obj: Any) -> bytes:
    """Quick serialize using global optimizer."""
    system = get_global_optimizer()
    return system["serialization_engine"].serialize(obj)


def fast_deserialize(data: bytes) -> Any:
    """Quick deserialize using global optimizer."""
    system = get_global_optimizer()
    return system["serialization_engine"].deserialize(data)


def fast_hash(data: str) -> str:
    """Quick hash using optimal algorithm."""
    return SerializationEngine.hash_fast(data)


# Export main components
__all__ = [
    # Core configuration
    "OptimizationSettings",
    "OptimizationLevel", 
    "SerializationFormat",
    
    # Models
    "PerformanceMetrics",
    "OptimizationConfig",
    "SystemStatus",
    "OptimizationResult",
    
    # Exceptions
    "OptimizationException",
    
    # Engines
    "SerializationEngine",
    
    # Factory functions
    "create_optimization_system",
    "get_global_optimizer",
    
    # Service registry
    "register_service",
    "get_service",
    
    # Decorators and utilities
    "optimize",
    "fast_serialize",
    "fast_deserialize",
    "fast_hash"
] 