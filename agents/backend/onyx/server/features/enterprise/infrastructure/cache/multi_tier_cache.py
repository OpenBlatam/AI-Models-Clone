"""
Multi-Tier Cache Implementation
==============================

Concrete implementation of cache service with L1 (memory) and L2 (Redis) tiers.
"""

import time
import weakref
from typing import Any, Optional
import redis.asyncio as redis
from ...core.interfaces.cache_interface import ICacheService
from ...shared.utils import generate_cache_key, serialize_json, deserialize_json
import logging

logger = logging.getLogger(__name__)


class MultiTierCacheService(ICacheService):
    """Multi-tier cache with memory and Redis layers."""
    
    def __init__(self, redis_url: str, max_memory_items: int = 1000):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache = weakref.WeakValueDictionary()
        self.access_times = {}
        self.max_memory_items = max_memory_items
        self.hit_count = 0
        self.miss_count = 0
        
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                max_connections=20,
                retry_on_timeout=True,
                health_check_interval=30
            )
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with L1 -> L2 fallback."""
        cache_key = generate_cache_key(key)
        
        # L1: Memory cache
        if cache_key in self.memory_cache:
            self.hit_count += 1
            self.access_times[cache_key] = time.time()
            return self.memory_cache[cache_key]
        
        # L2: Redis cache
        if self.redis_client:
            try:
                data = await self.redis_client.get(cache_key)
                if data:
                    value = deserialize_json(data)
                    await self._store_in_memory(cache_key, value)
                    self.hit_count += 1
                    return value
            except Exception as e:
                logger.warning(f"Redis get failed for key {cache_key}: {e}")
        
        self.miss_count += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with intelligent storage."""
        cache_key = generate_cache_key(key)
        ttl = ttl or 3600
        
        # Store in memory
        await self._store_in_memory(cache_key, value)
        
        # Store in Redis asynchronously
        if self.redis_client:
            try:
                serialized_value = serialize_json(value)
                await self.redis_client.setex(cache_key, ttl, serialized_value)
                return True
            except Exception as e:
                logger.warning(f"Redis set failed for key {cache_key}: {e}")
        
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        cache_key = generate_cache_key(key)
        
        # Remove from memory
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        if cache_key in self.access_times:
            del self.access_times[cache_key]
        
        # Remove from Redis
        if self.redis_client:
            try:
                await self.redis_client.delete(cache_key)
            except Exception as e:
                logger.warning(f"Redis delete failed for key {cache_key}: {e}")
        
        return True
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        cache_key = generate_cache_key(key)
        
        # Check memory first
        if cache_key in self.memory_cache:
            return True
        
        # Check Redis
        if self.redis_client:
            try:
                return await self.redis_client.exists(cache_key) > 0
            except Exception as e:
                logger.warning(f"Redis exists check failed for key {cache_key}: {e}")
        
        return False
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        # Clear memory
        self.memory_cache.clear()
        self.access_times.clear()
        
        # Clear Redis (only enterprise keys)
        if self.redis_client:
            try:
                keys = await self.redis_client.keys("enterprise:*")
                if keys:
                    await self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis clear failed: {e}")
        
        return True
    
    def get_hit_ratio(self) -> float:
        """Calculate cache hit ratio."""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
    
    async def get_stats(self) -> dict:
        """Get cache statistics."""
        memory_keys = len(self.memory_cache)
        redis_keys = 0
        
        if self.redis_client:
            try:
                redis_keys = len(await self.redis_client.keys("enterprise:*"))
            except Exception as e:
                logger.warning(f"Failed to get Redis stats: {e}")
        
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_ratio": self.get_hit_ratio(),
            "memory_keys": memory_keys,
            "redis_keys": redis_keys,
            "max_memory_items": self.max_memory_items,
            "redis_available": self.redis_client is not None
        }
    
    async def _store_in_memory(self, key: str, value: Any):
        """Store value in memory with LRU eviction."""
        if len(self.memory_cache) >= self.max_memory_items:
            # LRU eviction
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            if oldest_key in self.memory_cache:
                del self.memory_cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.memory_cache[key] = value
        self.access_times[key] = time.time() 