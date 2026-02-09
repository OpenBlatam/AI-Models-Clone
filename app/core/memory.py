"""
Memory optimization for Enhanced Blog System v27.0.0 REFACTORED
"""

import gc
import threading
import weakref
from collections import deque
from typing import Any, Callable, Dict, Optional
from functools import lru_cache

from app.config import config


class ObjectPool:
    """Advanced object pooling system with optimization"""
    
    def __init__(self, pool_size: int = None):
        self.pool_size = pool_size or config.memory.object_pool_size
        self.pools = {}
        self.locks = {}
        self.stats = {
            'objects_created': 0,
            'objects_reused': 0,
            'objects_destroyed': 0,
            'pool_hits': 0,
            'pool_misses': 0
        }
        
        # Memory tracking
        self.memory_usage = deque(maxlen=1000)
        self.gc_stats = deque(maxlen=1000)
        
        # Start memory optimization
        self._start_memory_optimization()
    
    def _start_memory_optimization(self):
        """Start memory optimization background task"""
        def optimize_memory():
            while True:
                try:
                    # Track memory usage
                    import psutil
                    process = psutil.Process()
                    memory_info = process.memory_info()
                    self.memory_usage.append(memory_info.rss)
                    
                    # Track garbage collection stats
                    gc_stats = gc.get_stats()
                    self.gc_stats.append(gc_stats)
                    
                    # Trigger garbage collection if memory usage is high
                    if memory_info.rss > config.memory.memory_threshold_mb * 1024 * 1024:
                        self._optimize_memory()
                    
                    # Clean up unused pools
                    self._cleanup_unused_pools()
                    
                    import time
                    time.sleep(30)  # Run every 30 seconds
                except Exception as e:
                    print(f"Memory optimization error: {e}")
                    import time
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=optimize_memory, daemon=True)
        monitor_thread.start()
    
    def _optimize_memory(self):
        """Optimize memory usage"""
        # Force garbage collection
        collected = gc.collect()
        
        # Clear unused pools
        self._cleanup_unused_pools()
        
        print(f"Memory optimization: collected {collected} objects")
    
    def _cleanup_unused_pools(self):
        """Clean up unused object pools"""
        for object_type in list(self.pools.keys()):
            pool = self.pools[object_type]
            if len(pool) == 0:
                # Remove empty pools
                del self.pools[object_type]
                if object_type in self.locks:
                    del self.locks[object_type]
    
    def get_object(self, object_type: str, factory_func: Callable) -> Any:
        """Get object from pool or create new one with optimization"""
        if object_type not in self.pools:
            self.pools[object_type] = deque()
            self.locks[object_type] = threading.Lock()
        
        with self.locks[object_type]:
            if self.pools[object_type]:
                # Reuse existing object
                obj = self.pools[object_type].popleft()
                self.stats['objects_reused'] += 1
                self.stats['pool_hits'] += 1
                return obj
            else:
                # Create new object
                obj = factory_func()
                self.stats['objects_created'] += 1
                self.stats['pool_misses'] += 1
                return obj
    
    def return_object(self, object_type: str, obj: Any):
        """Return object to pool with optimization"""
        if object_type not in self.pools:
            return
        
        with self.locks[object_type]:
            if len(self.pools[object_type]) < self.pool_size:
                # Reset object state if it has a reset method
                if hasattr(obj, 'reset'):
                    obj.reset()
                
                self.pools[object_type].append(obj)
            else:
                # Pool is full, destroy object
                self.stats['objects_destroyed'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get object pool statistics"""
        total_objects = sum(len(pool) for pool in self.pools.values())
        
        return {
            **self.stats,
            'total_pools': len(self.pools),
            'total_objects_in_pools': total_objects,
            'pool_types': list(self.pools.keys()),
            'memory_usage_mb': self.memory_usage[-1] / 1024 / 1024 if self.memory_usage else 0,
            'gc_stats': self.gc_stats[-1] if self.gc_stats else {}
        }
    
    def clear_pool(self, object_type: str):
        """Clear specific object pool"""
        if object_type in self.pools:
            with self.locks[object_type]:
                self.pools[object_type].clear()
    
    def clear_all_pools(self):
        """Clear all object pools"""
        for object_type in list(self.pools.keys()):
            self.clear_pool(object_type)


class MemoryOptimizer:
    """Advanced memory optimization system"""
    
    def __init__(self):
        self.object_pool = ObjectPool()
        self.weak_refs = weakref.WeakSet()
        self.memory_threshold = config.memory.memory_threshold_mb * 1024 * 1024
        
    def optimize_memory_usage(self):
        """Optimize memory usage"""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        if memory_info.rss > self.memory_threshold:
            # Force garbage collection
            collected = gc.collect()
            
            # Clear object pools if memory is still high
            if memory_info.rss > self.memory_threshold * 1.2:
                self.object_pool.clear_all_pools()
            
            return {
                "memory_before": memory_info.rss,
                "memory_after": psutil.Process().memory_info().rss,
                "objects_collected": collected,
                "optimization_applied": True
            }
        
        return {
            "optimization_applied": False,
            "reason": "Memory usage below threshold"
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        import psutil
        
        process = psutil.Process()
        memory_info = process.memory_info()
        virtual_memory = psutil.virtual_memory()
        
        return {
            "process_memory": {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent()
            },
            "system_memory": {
                "total_mb": virtual_memory.total / 1024 / 1024,
                "available_mb": virtual_memory.available / 1024 / 1024,
                "percent": virtual_memory.percent
            },
            "object_pool": self.object_pool.get_stats(),
            "gc_stats": gc.get_stats(),
            "optimization_threshold_mb": config.memory.memory_threshold_mb
        }
    
    def create_weak_reference(self, obj: Any):
        """Create weak reference to object"""
        weak_ref = weakref.ref(obj)
        self.weak_refs.add(weak_ref)
        return weak_ref
    
    def cleanup_weak_references(self):
        """Clean up dead weak references"""
        dead_refs = set()
        for ref in self.weak_refs:
            if ref() is None:
                dead_refs.add(ref)
        
        for ref in dead_refs:
            self.weak_refs.discard(ref)
        
        return len(dead_refs)


# Global memory optimizer instance
memory_optimizer = MemoryOptimizer()


@lru_cache(maxsize=1000)
def cached_function(func_name: str, *args, **kwargs):
    """
    Cached function decorator with optimization.
    
    This function provides a caching mechanism for function calls.
    Note: This is a generic cache wrapper. For better performance,
    use @lru_cache directly on the function you want to cache.
    
    Args:
        func_name: Name of the function to cache (for logging/debugging)
        *args: Positional arguments to pass to the cached function
        **kwargs: Keyword arguments to pass to the cached function
    
    Returns:
        Cached result if available, otherwise None
    """
    # This is a generic cache wrapper
    # For actual caching, use @lru_cache directly on your functions
    # Example: @lru_cache(maxsize=1000)
    #          def my_function(arg1, arg2):
    #              return result
    
    # Return None as this is a placeholder for actual function caching
    # In production, this would call the actual function and cache results
    return None


def optimize_memory_decorator(func: Callable) -> Callable:
    """Decorator to optimize memory usage for functions"""
    def wrapper(*args, **kwargs):
        # Check memory usage before function execution
        before_stats = memory_optimizer.get_memory_stats()
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Check memory usage after function execution
        after_stats = memory_optimizer.get_memory_stats()
        
        # Optimize memory if usage increased significantly
        memory_increase = after_stats["process_memory"]["rss_mb"] - before_stats["process_memory"]["rss_mb"]
        if memory_increase > 10:  # 10MB threshold
            memory_optimizer.optimize_memory_usage()
        
        return result
    
    return wrapper 