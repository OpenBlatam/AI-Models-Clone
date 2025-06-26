"""
Shared Cache Services

Provides centralized caching functionality for all modules including:
- Redis integration
- Multi-level caching
- Cache strategies (LRU, TTL, etc.)
- Cache warming and invalidation
- Performance monitoring
"""

import asyncio
import json
import hashlib
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
import threading

logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """Cache configuration"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    default_ttl: int = 3600  # 1 hour
    max_memory_cache_size: int = 1000
    key_prefix: str = "blatam:"
    compression_enabled: bool = True

@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    hit_rate: float = 0.0
    memory_usage: int = 0
    total_keys: int = 0

class MemoryCache:
    """In-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_order: List[str] = []
        self.stats = CacheStats()
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        with self._lock:
            if key not in self.cache:
                self.stats.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check TTL
            if entry.get('expires_at') and datetime.now() > entry['expires_at']:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
                self.stats.misses += 1
                return None
            
            # Update access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            self.stats.hits += 1
            return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache"""
        with self._lock:
            try:
                expires_at = None
                if ttl:
                    expires_at = datetime.now() + timedelta(seconds=ttl)
                
                self.cache[key] = {
                    'value': value,
                    'created_at': datetime.now(),
                    'expires_at': expires_at
                }
                
                # Update access order
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                
                # Evict if necessary
                self._evict_if_needed()
                
                self.stats.sets += 1
                return True
                
            except Exception as e:
                logger.error(f"Memory cache set error: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """Delete key from memory cache"""
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
                self.stats.deletes += 1
                return True
            return False
    
    def _evict_if_needed(self):
        """Evict least recently used items if cache is full"""
        while len(self.cache) > self.max_size:
            if self.access_order:
                lru_key = self.access_order.pop(0)
                if lru_key in self.cache:
                    del self.cache[lru_key]
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
            self.access_order.clear()
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        with self._lock:
            total_requests = self.stats.hits + self.stats.misses
            hit_rate = self.stats.hits / total_requests if total_requests > 0 else 0.0
            
            return CacheStats(
                hits=self.stats.hits,
                misses=self.stats.misses,
                sets=self.stats.sets,
                deletes=self.stats.deletes,
                hit_rate=hit_rate,
                total_keys=len(self.cache)
            )

class CacheService:
    """Unified cache service with multiple backends"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.memory_cache = MemoryCache(config.max_memory_cache_size)
        self.redis_client = None  # Would initialize Redis client here
        self._initialized = False
    
    async def initialize(self):
        """Initialize cache service"""
        try:
            # Initialize Redis connection if available
            # self.redis_client = await aioredis.from_url(...)
            self._initialized = True
            logger.info("Cache service initialized successfully")
        except Exception as e:
            logger.error(f"Cache initialization failed: {e}")
            # Fall back to memory cache only
            self._initialized = True
    
    async def get(self, key: str, use_memory: bool = True) -> Optional[Any]:
        """Get value from cache (memory first, then Redis)"""
        if not self._initialized:
            await self.initialize()
        
        # Try memory cache first
        if use_memory:
            value = self.memory_cache.get(key)
            if value is not None:
                return value
        
        # Try Redis if available
        if self.redis_client:
            try:
                redis_key = f"{self.config.key_prefix}{key}"
                value = await self.redis_client.get(redis_key)
                if value:
                    # Store in memory cache for faster access
                    if use_memory:
                        self.memory_cache.set(key, value)
                    return json.loads(value) if value else None
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                  use_memory: bool = True) -> bool:
        """Set value in cache"""
        if not self._initialized:
            await self.initialize()
        
        success = True
        ttl = ttl or self.config.default_ttl
        
        # Set in memory cache
        if use_memory:
            success &= self.memory_cache.set(key, value, ttl)
        
        # Set in Redis if available
        if self.redis_client:
            try:
                redis_key = f"{self.config.key_prefix}{key}"
                serialized_value = json.dumps(value)
                await self.redis_client.setex(redis_key, ttl, serialized_value)
            except Exception as e:
                logger.error(f"Redis set error: {e}")
                success = False
        
        return success
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._initialized:
            await self.initialize()
        
        success = True
        
        # Delete from memory cache
        success &= self.memory_cache.delete(key)
        
        # Delete from Redis if available
        if self.redis_client:
            try:
                redis_key = f"{self.config.key_prefix}{key}"
                await self.redis_client.delete(redis_key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
                success = False
        
        return success
    
    async def clear(self, pattern: Optional[str] = None):
        """Clear cache entries"""
        # Clear memory cache
        self.memory_cache.clear()
        
        # Clear Redis if available
        if self.redis_client and pattern:
            try:
                keys = await self.redis_client.keys(f"{self.config.key_prefix}{pattern}")
                if keys:
                    await self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis clear error: {e}")
    
    def cached(self, ttl: Optional[int] = None, key_func: Optional[Callable] = None,
               use_memory: bool = True):
        """Decorator for caching function results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cached_result = await self.get(cache_key, use_memory)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                await self.set(cache_key, result, ttl, use_memory)
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # For sync functions, we'll need to handle differently
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try memory cache only for sync functions
                cached_result = self.memory_cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                result = func(*args, **kwargs)
                self.memory_cache.set(cache_key, result, ttl)
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate unique cache key for function call"""
        key_data = f"{func_name}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def warm_cache(self, data: Dict[str, Any], ttl: Optional[int] = None):
        """Warm cache with initial data"""
        for key, value in data.items():
            await self.set(key, value, ttl)
        logger.info(f"Cache warmed with {len(data)} entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        memory_stats = self.memory_cache.get_stats()
        
        return {
            'memory_cache': {
                'hits': memory_stats.hits,
                'misses': memory_stats.misses,
                'hit_rate': memory_stats.hit_rate,
                'total_keys': memory_stats.total_keys
            },
            'redis_available': self.redis_client is not None,
            'initialized': self._initialized
        }

# Global cache instance
_cache_instance: Optional[CacheService] = None

def get_cache() -> CacheService:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        config = CacheConfig()
        _cache_instance = CacheService(config)
    return _cache_instance

async def cache_get(key: str) -> Optional[Any]:
    """Get value from global cache"""
    cache = get_cache()
    return await cache.get(key)

async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in global cache"""
    cache = get_cache()
    return await cache.set(key, value, ttl)

def cached(ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """Global caching decorator"""
    cache = get_cache()
    return cache.cached(ttl=ttl, key_func=key_func)

__all__ = [
    'CacheConfig',
    'CacheStats',
    'CacheService',
    'MemoryCache',
    'get_cache',
    'cache_get',
    'cache_set',
    'cached'
] 