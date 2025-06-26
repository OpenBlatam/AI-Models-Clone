"""
Caching Optimization Engine

Advanced caching strategies for optimal performance including:
- Multi-level caching
- Intelligent cache eviction
- Cache warming strategies
- Memory-aware caching
- Distributed caching support
"""

import asyncio
import time
import hashlib
import pickle
import threading
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
import logging
from collections import OrderedDict
import weakref
import gc

from ..config import OptimizationConfig
from ..models import CacheStrategy, CacheMetrics, OptimizationResult
from ..exceptions import OptimizationError, CacheError

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    created_at: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    ttl: Optional[int] = None
    size: int = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl)
    
    def access(self):
        """Mark entry as accessed"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()

class LRUCache:
    """LRU (Least Recently Used) Cache implementation"""
    
    def __init__(self, max_size: int = 1000, ttl: Optional[int] = None):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0
        }
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                del self.cache[key]
                self.stats['misses'] += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry.access()
            self.stats['hits'] += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        with self._lock:
            try:
                # Calculate size
                size = len(pickle.dumps(value)) if value else 0
                
                # Create entry
                entry = CacheEntry(
                    value=value,
                    created_at=datetime.utcnow(),
                    ttl=ttl or self.ttl,
                    size=size
                )
                
                # Remove existing if present
                if key in self.cache:
                    old_entry = self.cache[key]
                    self.stats['size'] -= old_entry.size
                
                # Add new entry
                self.cache[key] = entry
                self.cache.move_to_end(key)
                self.stats['size'] += size
                
                # Evict if necessary
                self._evict_if_needed()
                
                return True
                
            except Exception as e:
                logger.error(f"Cache set error: {e}")
                return False
    
    def _evict_if_needed(self):
        """Evict oldest entries if cache is full"""
        while len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            oldest_entry = self.cache[oldest_key]
            self.stats['size'] -= oldest_entry.size
            del self.cache[oldest_key]
            self.stats['evictions'] += 1
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                self.stats['size'] -= entry.size
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
            self.stats['size'] = 0
    
    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        with self._lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                entry = self.cache[key]
                self.stats['size'] -= entry.size
                del self.cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': hit_rate,
                'evictions': self.stats['evictions'],
                'size': len(self.cache),
                'max_size': self.max_size,
                'memory_usage_bytes': self.stats['size']
            }

class TimeBasedCache:
    """Time-based cache with automatic expiration"""
    
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.stats = {'hits': 0, 'misses': 0, 'expired': 0}
        self._lock = threading.RLock()
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            
            if entry.is_expired():
                del self.cache[key]
                self.stats['expired'] += 1
                self.stats['misses'] += 1
                return None
            
            entry.access()
            self.stats['hits'] += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        with self._lock:
            try:
                entry = CacheEntry(
                    value=value,
                    created_at=datetime.utcnow(),
                    ttl=ttl or self.default_ttl
                )
                self.cache[key] = entry
                return True
            except Exception as e:
                logger.error(f"Time-based cache set error: {e}")
                return False
    
    def _cleanup_loop(self):
        """Continuous cleanup of expired entries"""
        while True:
            try:
                time.sleep(60)  # Cleanup every minute
                self.cleanup_expired()
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        with self._lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
                self.stats['expired'] += 1
            
            return len(expired_keys)

class MultilevelCache:
    """Multi-level cache with L1 (memory) and L2 (persistent) levels"""
    
    def __init__(self, l1_size: int = 500, l2_size: int = 5000, ttl: int = 3600):
        self.l1_cache = LRUCache(max_size=l1_size, ttl=ttl)
        self.l2_cache = LRUCache(max_size=l2_size, ttl=ttl * 2)
        self.stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'misses': 0,
            'promotions': 0
        }
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache"""
        with self._lock:
            # Try L1 first
            value = self.l1_cache.get(key)
            if value is not None:
                self.stats['l1_hits'] += 1
                return value
            
            # Try L2
            value = self.l2_cache.get(key)
            if value is not None:
                self.stats['l2_hits'] += 1
                # Promote to L1
                self.l1_cache.set(key, value)
                self.stats['promotions'] += 1
                return value
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in multi-level cache"""
        with self._lock:
            # Store in both levels
            l1_success = self.l1_cache.set(key, value, ttl)
            l2_success = self.l2_cache.set(key, value, ttl)
            return l1_success and l2_success

class CacheOptimizer:
    """Advanced cache optimization engine"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.caches: Dict[str, Union[LRUCache, TimeBasedCache, MultilevelCache]] = {}
        self.default_cache = LRUCache(max_size=config.cache_size, ttl=config.cache_ttl)
        self.metrics_history: List[CacheMetrics] = []
        self._setup_monitoring()
    
    def _setup_monitoring(self):
        """Setup cache monitoring"""
        self._monitor_thread = threading.Thread(target=self._monitor_caches, daemon=True)
        self._monitor_thread.start()
    
    def _monitor_caches(self):
        """Monitor cache performance continuously"""
        while True:
            try:
                time.sleep(300)  # Monitor every 5 minutes
                self._collect_metrics()
                self._optimize_caches()
            except Exception as e:
                logger.error(f"Cache monitoring error: {e}")
    
    def _collect_metrics(self):
        """Collect cache metrics"""
        try:
            total_hits = 0
            total_misses = 0
            total_size = 0
            
            for name, cache in self.caches.items():
                if hasattr(cache, 'get_stats'):
                    stats = cache.get_stats()
                    total_hits += stats.get('hits', 0)
                    total_misses += stats.get('misses', 0)
                    total_size += stats.get('size', 0)
            
            # Add default cache stats
            default_stats = self.default_cache.get_stats()
            total_hits += default_stats['hits']
            total_misses += default_stats['misses']
            total_size += default_stats['size']
            
            total_requests = total_hits + total_misses
            hit_rate = total_hits / total_requests if total_requests > 0 else 0
            
            metrics = CacheMetrics(
                hit_rate=hit_rate,
                total_hits=total_hits,
                total_misses=total_misses,
                cache_size=total_size,
                memory_usage=self._calculate_memory_usage(),
                timestamp=datetime.utcnow()
            )
            
            self.metrics_history.append(metrics)
            
            # Keep only recent metrics
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-500:]
                
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
    
    def _calculate_memory_usage(self) -> int:
        """Calculate total memory usage of all caches"""
        total_memory = 0
        
        for cache in self.caches.values():
            if hasattr(cache, 'get_stats'):
                stats = cache.get_stats()
                total_memory += stats.get('memory_usage_bytes', 0)
        
        # Add default cache memory
        default_stats = self.default_cache.get_stats()
        total_memory += default_stats['memory_usage_bytes']
        
        return total_memory
    
    def _optimize_caches(self):
        """Optimize cache configurations based on metrics"""
        try:
            if len(self.metrics_history) < 5:
                return
            
            recent_metrics = self.metrics_history[-5:]
            avg_hit_rate = sum(m.hit_rate for m in recent_metrics) / len(recent_metrics)
            
            # If hit rate is low, consider increasing cache sizes
            if avg_hit_rate < 0.5:
                logger.info("Low cache hit rate detected, considering optimization")
                self._increase_cache_sizes()
            
            # Cleanup expired entries
            for cache in self.caches.values():
                if hasattr(cache, 'cleanup_expired'):
                    cache.cleanup_expired()
            
            self.default_cache.cleanup_expired()
            
        except Exception as e:
            logger.error(f"Cache optimization error: {e}")
    
    def _increase_cache_sizes(self):
        """Increase cache sizes if memory allows"""
        memory_usage = self._calculate_memory_usage()
        memory_limit = self.config.memory_threshold_mb * 1024 * 1024 * 0.3  # 30% of threshold
        
        if memory_usage < memory_limit:
            # Can increase cache sizes
            for cache in self.caches.values():
                if isinstance(cache, LRUCache) and cache.max_size < 2000:
                    cache.max_size = min(cache.max_size * 1.2, 2000)
    
    def create_cache(self, name: str, strategy: CacheStrategy) -> Union[LRUCache, TimeBasedCache, MultilevelCache]:
        """Create optimized cache with specific strategy"""
        try:
            if strategy.cache_type == "lru":
                cache = LRUCache(
                    max_size=strategy.max_size,
                    ttl=strategy.ttl
                )
            elif strategy.cache_type == "time_based":
                cache = TimeBasedCache(default_ttl=strategy.ttl)
            elif strategy.cache_type == "multilevel":
                cache = MultilevelCache(
                    l1_size=strategy.max_size // 4,
                    l2_size=strategy.max_size,
                    ttl=strategy.ttl
                )
            else:
                cache = LRUCache(max_size=strategy.max_size, ttl=strategy.ttl)
            
            self.caches[name] = cache
            logger.info(f"Created cache '{name}' with strategy: {strategy.cache_type}")
            return cache
            
        except Exception as e:
            logger.error(f"Cache creation error: {e}")
            raise CacheError(f"Failed to create cache '{name}': {e}")
    
    def get_cache(self, name: str = "default") -> Union[LRUCache, TimeBasedCache, MultilevelCache]:
        """Get cache by name or default cache"""
        if name == "default":
            return self.default_cache
        return self.caches.get(name, self.default_cache)
    
    def cached(self, cache_name: str = "default", ttl: Optional[int] = None, 
               key_func: Optional[Callable] = None):
        """Decorator for caching function results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cache = self.get_cache(cache_name)
                cached_result = cache.get(cache_key)
                
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate unique cache key for function call"""
        key_data = {
            'function': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        
        key_string = str(key_data)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def warm_cache(self, cache_name: str, data: Dict[str, Any]):
        """Warm up cache with initial data"""
        try:
            cache = self.get_cache(cache_name)
            
            for key, value in data.items():
                cache.set(key, value)
            
            logger.info(f"Warmed cache '{cache_name}' with {len(data)} entries")
            
        except Exception as e:
            logger.error(f"Cache warming error: {e}")
            raise CacheError(f"Failed to warm cache '{cache_name}': {e}")
    
    def get_cache_report(self) -> Dict[str, Any]:
        """Generate comprehensive cache performance report"""
        try:
            cache_stats = {}
            
            # Get stats for all named caches
            for name, cache in self.caches.items():
                if hasattr(cache, 'get_stats'):
                    cache_stats[name] = cache.get_stats()
            
            # Add default cache stats
            cache_stats['default'] = self.default_cache.get_stats()
            
            # Calculate overall statistics
            total_hits = sum(stats['hits'] for stats in cache_stats.values())
            total_misses = sum(stats['misses'] for stats in cache_stats.values())
            total_requests = total_hits + total_misses
            overall_hit_rate = total_hits / total_requests if total_requests > 0 else 0
            
            return {
                'overall_hit_rate': overall_hit_rate,
                'total_requests': total_requests,
                'total_hits': total_hits,
                'total_misses': total_misses,
                'cache_count': len(self.caches) + 1,  # +1 for default
                'total_memory_usage': self._calculate_memory_usage(),
                'individual_caches': cache_stats,
                'metrics_history_size': len(self.metrics_history)
            }
            
        except Exception as e:
            logger.error(f"Cache report error: {e}")
            return {"error": f"Failed to generate cache report: {e}"}

# Factory function
def create_cache_optimizer(config: OptimizationConfig) -> CacheOptimizer:
    """Create and configure cache optimizer"""
    return CacheOptimizer(config)

# Convenience decorators
def cache_result(ttl: int = 300, cache_name: str = "default"):
    """Simple result caching decorator"""
    config = OptimizationConfig()
    optimizer = create_cache_optimizer(config)
    return optimizer.cached(cache_name=cache_name, ttl=ttl) 