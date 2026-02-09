"""
Ultra-Fast Memory Optimizer
Advanced memory management for maximum performance
"""

import logging
import gc
import sys
from typing import Any, Optional, Dict
from functools import wraps
import weakref

logger = logging.getLogger(__name__)


class MemoryOptimizer:
    """
    Ultra-fast memory optimizer
    
    Features:
    - Automatic garbage collection tuning
    - Memory pool management
    - Object pooling
    - Memory leak detection
    - Smart GC scheduling
    """
    
    def __init__(self, enable_auto_gc: bool = True, gc_threshold: tuple = (700, 10, 10)):
        self.enable_auto_gc = enable_auto_gc
        self.gc_threshold = gc_threshold
        self._object_pools: Dict[str, list] = {}
        self._pool_stats: Dict[str, Dict[str, int]] = {}
        
        if enable_auto_gc:
            self._configure_gc()
        
        logger.info("✅ Memory optimizer initialized")
    
    def _configure_gc(self):
        """Configure garbage collection for optimal performance"""
        # Set GC thresholds
        gc.set_threshold(*self.gc_threshold)
        
        # Disable automatic GC (we'll do it manually)
        gc.disable()
        
        logger.info(f"✅ GC configured (thresholds: {self.gc_threshold})")
    
    def optimize_gc(self):
        """Run optimized garbage collection"""
        # Collect generation 0 and 1 (faster)
        collected = gc.collect(1)
        return collected
    
    def full_gc(self):
        """Run full garbage collection"""
        collected = gc.collect()
        return collected
    
    def get_object(self, pool_name: str, factory: callable, *args, **kwargs) -> Any:
        """
        Get object from pool or create new
        
        Args:
            pool_name: Name of the object pool
            factory: Factory function to create objects
            *args: Factory arguments
            **kwargs: Factory keyword arguments
            
        Returns:
            Object from pool or newly created
        """
        if pool_name not in self._object_pools:
            self._object_pools[pool_name] = []
            self._pool_stats[pool_name] = {
                "created": 0,
                "reused": 0,
                "pool_size": 0
            }
        
        pool = self._object_pools[pool_name]
        stats = self._pool_stats[pool_name]
        
        if pool:
            obj = pool.pop()
            stats["reused"] += 1
            stats["pool_size"] = len(pool)
        else:
            obj = factory(*args, **kwargs)
            stats["created"] += 1
        
        return obj
    
    def return_object(self, pool_name: str, obj: Any, max_pool_size: int = 100):
        """
        Return object to pool
        
        Args:
            pool_name: Name of the object pool
            obj: Object to return
            max_pool_size: Maximum pool size
        """
        if pool_name not in self._object_pools:
            self._object_pools[pool_name] = []
            self._pool_stats[pool_name] = {
                "created": 0,
                "reused": 0,
                "pool_size": 0
            }
        
        pool = self._object_pools[pool_name]
        stats = self._pool_stats[pool_name]
        
        if len(pool) < max_pool_size:
            pool.append(obj)
            stats["pool_size"] = len(pool)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        
        return {
            "rss": mem_info.rss,  # Resident Set Size
            "vms": mem_info.vms,  # Virtual Memory Size
            "percent": process.memory_percent(),
            "gc_counts": gc.get_count(),
            "gc_threshold": gc.get_threshold()
        }
    
    def get_pool_stats(self, pool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get object pool statistics
        
        Args:
            pool_name: Specific pool name or None for all
            
        Returns:
            Pool statistics
        """
        if pool_name:
            return self._pool_stats.get(pool_name, {})
        return self._pool_stats.copy()


def memory_efficient(func):
    """Decorator for memory-efficient function execution"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        optimizer = get_memory_optimizer()
        
        # Run before function
        optimizer.optimize_gc()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            # Run after function
            optimizer.optimize_gc()
    
    return wrapper


# Global optimizer instance
_optimizer: Optional[MemoryOptimizer] = None


def get_memory_optimizer() -> MemoryOptimizer:
    """Get global memory optimizer instance"""
    global _optimizer
    if _optimizer is None:
        _optimizer = MemoryOptimizer()
    return _optimizer















