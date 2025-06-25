"""
Production Cache System for Onyx Features.

Multi-level caching with Redis, TTL, LRU, and async support.
Optimized with high-performance serialization and hashing libraries.
"""

import asyncio
import time
from typing import Any, Dict, Optional, Union, Callable, TypeVar
from datetime import datetime, timedelta
from functools import wraps

import aioredis
from cachetools import TTLCache, LRUCache
import structlog
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

# Import optimized serialization and hashing
from .optimization import FastSerializer, FastHasher, MemoryOptimizer, ProfilerOptimizer

# Configure logging
logger = structlog.get_logger(__name__)

T = TypeVar('T')

# Cache configurations
DEFAULT_TTL = 3600  # 1 hour
DEFAULT_MAX_SIZE = 1000
REDIS_KEY_PREFIX = "onyx:cache:"


class CacheConfig(BaseModel):
    """Cache configuration."""
    redis_url: str = Field(default="redis://localhost:6379/0")
    default_ttl: int = Field(default=DEFAULT_TTL, ge=60, le=86400)
    max_size: int = Field(default=DEFAULT_MAX_SIZE, ge=10, le=10000)
    enable_redis: bool = Field(default=True)
    enable_memory: bool = Field(default=True)
    compression: bool = Field(default=True)


class CacheStats(BaseModel):
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    size: int = 0
    memory_usage: int = 0


class CacheManager:
    """Advanced multi-level cache manager."""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.stats = CacheStats()
        
        # Memory caches
        self.ttl_cache = TTLCache(
            maxsize=self.config.max_size,
            ttl=self.config.default_ttl
        )
        self.lru_cache = LRUCache(maxsize=self.config.max_size)
        
        # Redis connection
        self.redis: Optional[aioredis.Redis] = None
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize Redis connection."""
        if self.config.enable_redis:
            try:
                self.redis = aioredis.from_url(
                    self.config.redis_url,
                    encoding="utf-8",
                    decode_responses=False,
                    max_connections=20,
                    retry_on_timeout=True
                )
                await self.redis.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}")
                self.redis = None
    
    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """Generate cache key with namespace using fast hashing."""
        # Use fast hashing for better performance and collision resistance
        key_hash = FastHasher.hash_fast(f"{namespace}:{key}")
        return f"{REDIS_KEY_PREFIX}{key_hash}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage using optimized serialization."""
        try:
            # Try MessagePack for better performance and smaller size
            return FastSerializer.serialize_msgpack(value)
        except Exception:
            try:
                # Fallback to optimized JSON
                return FastSerializer.serialize_json(value)
            except Exception as e:
                logger.error(f"Serialization failed: {e}")
                # Final fallback to pickle with compression
                if self.config.compression:
                    import gzip, pickle
                    return gzip.compress(pickle.dumps(value))
                else:
                    import pickle
                    return pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage using optimized deserialization."""
        try:
            # Try MessagePack first
            return FastSerializer.deserialize_msgpack(data)
        except Exception:
            try:
                # Fallback to optimized JSON
                return FastSerializer.deserialize_json(data)
            except Exception:
                try:
                    # Final fallback to pickle
                    if self.config.compression:
                        import gzip, pickle
                        return pickle.loads(gzip.decompress(data))
                    else:
                        import pickle
                        return pickle.loads(data)
                except Exception as e:
                    logger.error(f"Deserialization failed: {e}")
                    raise
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache with fallback strategy."""
        cache_key = self._generate_key(key, namespace)
        
        # Level 1: TTL Cache
        async with self._lock:
            if key in self.ttl_cache:
                self.stats.hits += 1
                logger.debug("Cache hit (TTL)", key=key)
                return self.ttl_cache[key]
        
        # Level 2: LRU Cache
        async with self._lock:
            if key in self.lru_cache:
                self.stats.hits += 1
                logger.debug("Cache hit (LRU)", key=key)
                value = self.lru_cache[key]
                # Promote to TTL cache
                self.ttl_cache[key] = value
                return value
        
        # Level 3: Redis Cache
        if self.redis:
            try:
                data = await self.redis.get(cache_key)
                if data:
                    value = self._deserialize_value(data)
                    # Promote to memory caches
                    async with self._lock:
                        self.ttl_cache[key] = value
                        self.lru_cache[key] = value
                    self.stats.hits += 1
                    logger.debug("Cache hit (Redis)", key=key)
                    return value
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        
        self.stats.misses += 1
        logger.debug("Cache miss", key=key)
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        namespace: str = "default"
    ) -> bool:
        """Set value in all cache levels."""
        cache_key = self._generate_key(key, namespace)
        ttl = ttl or self.config.default_ttl
        
        try:
            # Set in memory caches
            async with self._lock:
                self.ttl_cache[key] = value
                self.lru_cache[key] = value
            
            # Set in Redis
            if self.redis:
                try:
                    serialized = self._serialize_value(value)
                    await self.redis.setex(cache_key, ttl, serialized)
                except Exception as e:
                    logger.warning(f"Redis set failed: {e}")
            
            self.stats.sets += 1
            logger.debug("Cache set", key=key, ttl=ttl)
            return True
            
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return False
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from all cache levels."""
        cache_key = self._generate_key(key, namespace)
        
        try:
            # Delete from memory caches
            async with self._lock:
                self.ttl_cache.pop(key, None)
                self.lru_cache.pop(key, None)
            
            # Delete from Redis
            if self.redis:
                try:
                    await self.redis.delete(cache_key)
                except Exception as e:
                    logger.warning(f"Redis delete failed: {e}")
            
            self.stats.deletes += 1
            logger.debug("Cache delete", key=key)
            return True
            
        except Exception as e:
            logger.error(f"Cache delete failed: {e}")
            return False
    
    async def clear(self, namespace: str = "default") -> bool:
        """Clear cache for namespace."""
        try:
            # Clear memory caches
            async with self._lock:
                self.ttl_cache.clear()
                self.lru_cache.clear()
            
            # Clear Redis namespace
            if self.redis:
                try:
                    pattern = f"{REDIS_KEY_PREFIX}{namespace}:*"
                    keys = await self.redis.keys(pattern)
                    if keys:
                        await self.redis.delete(*keys)
                except Exception as e:
                    logger.warning(f"Redis clear failed: {e}")
            
            logger.info("Cache cleared", namespace=namespace)
            return True
            
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = self.stats.dict()
        
        # Add memory cache info
        async with self._lock:
            stats.update({
                "ttl_cache_size": len(self.ttl_cache),
                "lru_cache_size": len(self.lru_cache),
                "ttl_cache_info": getattr(self.ttl_cache, 'data', {}),
                "lru_cache_info": getattr(self.lru_cache, 'data', {})
            })
        
        # Add Redis info
        if self.redis:
            try:
                redis_info = await self.redis.info('memory')
                stats['redis_memory'] = redis_info.get('used_memory_human', 'unknown')
            except Exception:
                stats['redis_memory'] = 'unavailable'
        
        return stats


# Global cache manager
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get or create global cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
        await _cache_manager.initialize()
    return _cache_manager


# Decorator for caching function results
def cached(
    ttl: Optional[int] = None,
    namespace: str = "functions",
    key_func: Optional[Callable] = None
):
    """Decorator for caching function results."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            cache_manager = await get_cache_manager()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key, namespace)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Cache result
            await cache_manager.set(cache_key, result, ttl, namespace)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            return asyncio.create_task(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Utility functions
async def cache_get(key: str, namespace: str = "default") -> Optional[Any]:
    """Get value from cache."""
    cache_manager = await get_cache_manager()
    return await cache_manager.get(key, namespace)


async def cache_set(
    key: str, 
    value: Any, 
    ttl: Optional[int] = None, 
    namespace: str = "default"
) -> bool:
    """Set value in cache."""
    cache_manager = await get_cache_manager()
    return await cache_manager.set(key, value, ttl, namespace)


async def cache_delete(key: str, namespace: str = "default") -> bool:
    """Delete value from cache."""
    cache_manager = await get_cache_manager()
    return await cache_manager.delete(key, namespace)


async def cache_clear(namespace: str = "default") -> bool:
    """Clear cache namespace."""
    cache_manager = await get_cache_manager()
    return await cache_manager.clear(namespace)


async def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    cache_manager = await get_cache_manager()
    return await cache_manager.get_stats()


# Context manager for cache sessions
class CacheSession:
    """Context manager for cache operations."""
    
    def __init__(self, namespace: str = "session"):
        self.namespace = namespace
        self.cache_manager: Optional[CacheManager] = None
    
    async def __aenter__(self):
        self.cache_manager = await get_cache_manager()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        pass
    
    async def get(self, key: str) -> Optional[Any]:
        return await self.cache_manager.get(key, self.namespace)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        return await self.cache_manager.set(key, value, ttl, self.namespace)
    
    async def delete(self, key: str) -> bool:
        return await self.cache_manager.delete(key, self.namespace)


# Export main components
__all__ = [
    "CacheManager",
    "CacheConfig", 
    "CacheStats",
    "CacheSession",
    "get_cache_manager",
    "cached",
    "cache_get",
    "cache_set", 
    "cache_delete",
    "cache_clear",
    "cache_stats"
] 