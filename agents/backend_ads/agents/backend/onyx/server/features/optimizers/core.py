"""
Core Optimizer - Main Orchestrator for All Optimization Components.

This module provides the main UnifiedOptimizer class that coordinates
all individual optimization components for maximum performance.
"""

import asyncio
import time
import os
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
import structlog

# Import modular optimizers
from .config import OptimizationConfig, OptimizationLevel, FEATURES
from .serialization import SerializationOptimizer
from .hashing import HashingOptimizer

# Import remaining optimizers from existing modules (until they are modularized)
try:
    from ..core_optimizers import (
        MemoryOptimizer, ConcurrencyOptimizer, 
        PerformanceMetrics, ProfilerOptimizer
    )
    LEGACY_OPTIMIZERS_AVAILABLE = True
except ImportError:
    LEGACY_OPTIMIZERS_AVAILABLE = False

# Optional ultra-performance imports
try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

logger = structlog.get_logger(__name__)


class UnifiedOptimizer:
    """
    Main orchestrator for all optimization systems.
    
    Coordinates serialization, hashing, memory, concurrency, and other
    optimizations into a cohesive high-performance system.
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.initialized = False
        
        # Performance tracking
        self.metrics = PerformanceMetrics() if LEGACY_OPTIMIZERS_AVAILABLE else SimpleMetrics()
        self.start_time = time.perf_counter()
        
        # Initialize individual optimizers
        self._initialize_optimizers()
        
        logger.info("Unified optimizer created",
                   level=self.config.level.value,
                   features=self.config.get_feature_report())
    
    def _initialize_optimizers(self):
        """Initialize all individual optimizer components."""
        # Core modular optimizers
        self.serialization = SerializationOptimizer(self.config)
        self.hashing = HashingOptimizer(self.config)
        
        # Legacy optimizers (to be modularized)
        if LEGACY_OPTIMIZERS_AVAILABLE:
            self.memory = MemoryOptimizer(self.config)
            self.concurrency = ConcurrencyOptimizer(self.config)
            self.profiler = ProfilerOptimizer()
        else:
            # Simple fallbacks
            self.memory = SimpleMemoryManager()
            self.concurrency = SimpleConcurrencyManager()
            self.profiler = SimpleProfiler()
        
        # Convenient aliases for backward compatibility
        self.serializer = self.serialization
        self.hasher = self.hashing
        self.memory_optimizer = self.memory
        self.async_optimizer = self.concurrency
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize all optimizers and setup event loop optimizations."""
        start_time = time.perf_counter()
        initialization_results = {}
        
        # Setup event loop optimization
        if self.config.enable_uvloop and UVLOOP_AVAILABLE:
            try:
                uvloop.install()
                logger.info("UVLoop event loop installed")
                initialization_results["uvloop"] = "installed"
            except Exception as e:
                logger.warning("UVLoop installation failed", error=str(e))
                initialization_results["uvloop"] = f"failed: {e}"
        else:
            initialization_results["uvloop"] = "not available or disabled"
        
        # Initialize individual components
        try:
            # Modular optimizers
            initialization_results["serialization"] = "initialized"
            initialization_results["hashing"] = "initialized"
            
            # Legacy optimizers
            if LEGACY_OPTIMIZERS_AVAILABLE:
                initialization_results["memory"] = self.memory.initialize()
                initialization_results["concurrency"] = self.concurrency.initialize()
            else:
                initialization_results["memory"] = "simple fallback"
                initialization_results["concurrency"] = "simple fallback"
            
            initialization_results["profiler"] = "initialized"
            
        except Exception as e:
            logger.error("Failed to initialize some optimizers", error=str(e))
            initialization_results["error"] = str(e)
        
        # Warmup JIT compilation if available
        if self.config.enable_jit and FEATURES["NUMBA_AVAILABLE"]:
            try:
                import numpy as np
                from .hashing import hash_array_fast
                
                # Warmup array operations
                warmup_array = np.random.random(1000).astype(np.float64)
                hash_array_fast(warmup_array)
                
                initialization_results["jit_warmup"] = "completed"
                logger.info("JIT compilation warmed up")
            except Exception as e:
                logger.warning("JIT warmup failed", error=str(e))
                initialization_results["jit_warmup"] = f"failed: {e}"
        
        # Initial memory optimization
        try:
            memory_stats = self.memory.optimize_memory_usage() if hasattr(self.memory, 'optimize_memory_usage') else {}
            initialization_results["initial_memory_cleanup"] = memory_stats
        except Exception as e:
            logger.warning("Initial memory cleanup failed", error=str(e))
        
        init_time = (time.perf_counter() - start_time) * 1000
        self.initialized = True
        
        return {
            "initialization_time_ms": init_time,
            "components": initialization_results,
            "features": self.config.get_feature_report(),
            "ready": True
        }
    
    @asynccontextmanager
    async def performance_context(self, operation_name: str):
        """Context manager for comprehensive performance monitoring."""
        start_time = time.perf_counter()
        
        # Start profiling
        if hasattr(self.profiler, 'start_profiling'):
            self.profiler.start_profiling()
        
        # Memory monitoring
        memory_context = None
        if hasattr(self.memory, 'memory_monitor'):
            memory_context = self.memory.memory_monitor(operation_name)
            await memory_context.__aenter__()
        
        try:
            yield
        finally:
            # Stop profiling
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            if hasattr(self.profiler, 'stop_profiling'):
                self.profiler.stop_profiling(operation_name)
            
            if hasattr(self.metrics, 'record_operation'):
                self.metrics.record_operation(duration_ms)
            
            # Close memory monitoring
            if memory_context:
                await memory_context.__aexit__(None, None, None)
            
            # Log slow operations
            if duration_ms > self.config.max_response_time_ms:
                logger.warning("Slow operation detected",
                             operation=operation_name,
                             duration_ms=duration_ms)
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics from all optimizers."""
        metrics = {
            "uptime_seconds": time.perf_counter() - self.start_time,
            "config": self.config.get_feature_report(),
            "system": {
                "cpu_count": os.cpu_count(),
                "platform": os.name
            }
        }
        
        # Add component-specific metrics
        try:
            if hasattr(self.serialization, 'get_metrics'):
                metrics["serialization"] = self.serialization.get_metrics()
            
            if hasattr(self.hashing, 'get_metrics'):
                metrics["hashing"] = self.hashing.get_metrics()
            
            if hasattr(self.memory, 'get_memory_usage'):
                metrics["memory"] = self.memory.get_memory_usage()
            
            if hasattr(self.metrics, 'get_summary'):
                metrics["overall"] = self.metrics.get_summary()
            
        except Exception as e:
            logger.warning("Failed to collect some metrics", error=str(e))
            metrics["metrics_error"] = str(e)
        
        return metrics
    
    async def cleanup(self):
        """Cleanup all optimizer resources."""
        cleanup_results = {}
        
        try:
            # Cleanup individual components
            if hasattr(self.memory, 'cleanup'):
                self.memory.cleanup()
                cleanup_results["memory"] = "cleaned"
            
            if hasattr(self.concurrency, 'cleanup'):
                self.concurrency.cleanup()
                cleanup_results["concurrency"] = "cleaned"
            
            # Force final memory cleanup
            if hasattr(self.memory, 'optimize_memory_usage'):
                final_memory_stats = self.memory.optimize_memory_usage()
                cleanup_results["final_memory_cleanup"] = final_memory_stats
            
            logger.info("Unified optimizer cleaned up successfully", results=cleanup_results)
            
        except Exception as e:
            logger.warning("Cleanup encountered errors", error=str(e))


class SimpleMetrics:
    """Simple metrics fallback when legacy optimizers not available."""
    
    def __init__(self):
        self.operations_count = 0
        self.start_time = time.perf_counter()
    
    def record_operation(self, duration_ms: float, error: bool = False):
        """Record operation."""
        self.operations_count += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get basic summary."""
        return {
            "operations_count": self.operations_count,
            "uptime_seconds": time.perf_counter() - self.start_time
        }


class SimpleMemoryManager:
    """Simple memory manager fallback."""
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Basic memory optimization."""
        import gc
        collected = gc.collect()
        return {"objects_collected": collected}
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Basic memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {"percent": memory.percent}
        except ImportError:
            return {"percent": 0}
    
    def cleanup(self):
        """Basic cleanup."""
        self.optimize_memory_usage()


class SimpleConcurrencyManager:
    """Simple concurrency manager fallback."""
    
    def initialize(self) -> bool:
        """Basic initialization."""
        return True
    
    def cleanup(self):
        """Basic cleanup."""
        pass


class SimpleProfiler:
    """Simple profiler fallback."""
    
    def start_profiling(self):
        """Basic profiling start."""
        pass
    
    def stop_profiling(self, operation_name: str):
        """Basic profiling stop."""
        pass


# Factory functions
def create_optimizer(
    level: OptimizationLevel = OptimizationLevel.ADVANCED,
    **kwargs
) -> UnifiedOptimizer:
    """Create a unified optimizer with specified level."""
    config = OptimizationConfig(level=level, **kwargs)
    return UnifiedOptimizer(config)


def create_production_optimizer(**kwargs) -> UnifiedOptimizer:
    """Create a production-optimized configuration."""
    config = OptimizationConfig.for_production()
    
    # Override with any provided kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return UnifiedOptimizer(config)


def create_development_optimizer(**kwargs) -> UnifiedOptimizer:
    """Create a development-friendly configuration."""
    config = OptimizationConfig.for_development()
    
    # Override with any provided kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return UnifiedOptimizer(config)


def create_testing_optimizer(**kwargs) -> UnifiedOptimizer:
    """Create a testing configuration with minimal overhead."""
    config = OptimizationConfig.for_testing()
    
    # Override with any provided kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return UnifiedOptimizer(config)


# Decorator for automatic optimization
def optimize(
    level: OptimizationLevel = OptimizationLevel.ADVANCED,
    cache_results: bool = True,
    monitor_performance: bool = True
):
    """Decorator for automatic optimization of functions."""
    def decorator(func):
        optimizer = create_optimizer(level)
        
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                if not optimizer.initialized:
                    await optimizer.initialize()
                
                operation_name = f"{func.__module__}.{func.__name__}"
                
                if monitor_performance:
                    async with optimizer.performance_context(operation_name):
                        return await func(*args, **kwargs)
                else:
                    return await func(*args, **kwargs)
            
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                # For sync functions, we can't easily use async context managers
                # So we do basic performance monitoring
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    
                    if hasattr(optimizer.metrics, 'record_operation'):
                        optimizer.metrics.record_operation(duration_ms)
                    
                    return result
                except Exception as e:
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    if hasattr(optimizer.metrics, 'record_operation'):
                        optimizer.metrics.record_operation(duration_ms, error=True)
                    raise
            
            return sync_wrapper
    
    return decorator


# Export main components
__all__ = [
    "UnifiedOptimizer",
    "create_optimizer",
    "create_production_optimizer",
    "create_development_optimizer", 
    "create_testing_optimizer",
    "optimize"
] 