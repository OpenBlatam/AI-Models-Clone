#!/usr/bin/env python3
"""
Ultra-Fast Cache v10
Maximum Performance with Fastest Libraries
"""

import asyncio
import time
import hashlib
from typing import Any, Optional, Dict, List, Union
from dataclasses import dataclass
from contextlib import asynccontextmanager

# Ultra-fast imports
import orjson
import zstandard as zstd
import brotli
from cachetools import TTLCache, LRUCache
import aioredis
import redis
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class CacheEntry:
    """Ultra-optimized cache entry"""
    key: str
    value: Any
    timestamp: float
    ttl: float
    compressed: bool = False
    algorithm: str = "none"


class UltraFastCache:
    """Ultra-fast cache with maximum performance optimizations"""
    
    def __init__(
        self,
        maxsize: int = 10000,
        ttl: int = 3600,
        enable_compression: bool = True,
        compression_threshold: int = 1024,
        redis_url: Optional[str] = None,
        enable_redis: bool = False
    ):
        self.maxsize = maxsize
        self.default_ttl = ttl
        self.enable_compression = enable_compression
        self.compression_threshold = compression_threshold
        self.enable_redis = enable_redis
        
        # In-memory cache with maximum performance
        self.memory_cache = TTLCache(maxsize=maxsize, ttl=ttl)
        
        # Redis client for distributed caching
        self.redis_client = None
        if enable_redis and redis_url:
            self.redis_client = redis.Redis.from_url(redis_url, decode_responses=False)
        
        # Async Redis client
        self.aioredis_client = None
        
        # Performance metrics
        self.hit_count = 0
        self.miss_count = 0
        self.set_count = 0
        self.total_time = 0.0
        self.avg_operation_time = 0.0
    
    async def initialize(self):
        """Initialize async components"""
        if self.enable_redis:
            try:
                self.aioredis_client = await aioredis.from_url(
                    "redis://localhost:6379",
                    encoding="utf-8",
                    decode_responses=False
                )
                logger.info("Redis client initialized successfully")
            except Exception as e:
                logger.warning("Failed to initialize Redis client", error=str(e))
                self.enable_redis = False
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.aioredis_client:
            await self.aioredis_client.close()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key with maximum performance"""
        # Use orjson for fast serialization
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key_bytes = orjson.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_bytes).hexdigest()
    
    def _compress_data(self, data: bytes, algorithm: str = "zstd") -> bytes:
        """Compress data with fastest algorithm"""
        if algorithm == "zstd":
            compressor = zstd.ZstdCompressor(level=3)
            return compressor.compress(data)
        elif algorithm == "brotli":
            return brotli.compress(data, quality=4)
        else:
            return data
    
    def _decompress_data(self, data: bytes, algorithm: str = "zstd") -> bytes:
        """Decompress data"""
        if algorithm == "zstd":
            decompressor = zstd.ZstdDecompressor()
            return decompressor.decompress(data)
        elif algorithm == "brotli":
            return brotli.decompress(data)
        else:
            return data
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value with maximum performance"""
        return orjson.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value with maximum performance"""
        return orjson.loads(data)
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with maximum performance"""
        start_time = time.time()
        
        try:
            # Try memory cache first (fastest)
            if key in self.memory_cache:
                self.hit_count += 1
                self._update_metrics(time.time() - start_time)
                logger.debug("Memory cache hit", key=key)
                return self.memory_cache[key]
            
            # Try Redis if available
            if self.enable_redis and self.aioredis_client:
                try:
                    redis_data = await self.aioredis_client.get(key)
                    if redis_data:
                        # Deserialize and decompress if needed
                        value = self._deserialize_value(redis_data)
                        
                        # Store in memory cache for faster access
                        self.memory_cache[key] = value
                        
                        self.hit_count += 1
                        self._update_metrics(time.time() - start_time)
                        logger.debug("Redis cache hit", key=key)
                        return value
                except Exception as e:
                    logger.warning("Redis get failed", key=key, error=str(e))
            
            # Cache miss
            self.miss_count += 1
            self._update_metrics(time.time() - start_time)
            logger.debug("Cache miss", key=key)
            return default
            
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with maximum performance"""
        start_time = time.time()
        
        try:
            # Serialize value
            serialized_value = self._serialize_value(value)
            
            # Compress if enabled and data is large enough
            if self.enable_compression and len(serialized_value) > self.compression_threshold:
                compressed_value = self._compress_data(serialized_value, "zstd")
                if len(compressed_value) < len(serialized_value):
                    serialized_value = compressed_value
            
            # Store in memory cache
            self.memory_cache[key] = value
            
            # Store in Redis if available
            if self.enable_redis and self.aioredis_client:
                try:
                    redis_ttl = ttl or self.default_ttl
                    await self.aioredis_client.setex(key, redis_ttl, serialized_value)
                except Exception as e:
                    logger.warning("Redis set failed", key=key, error=str(e))
            
            self.set_count += 1
            self._update_metrics(time.time() - start_time)
            logger.debug("Cache set successful", key=key)
            return True
            
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache with maximum performance"""
        try:
            # Remove from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # Remove from Redis if available
            if self.enable_redis and self.aioredis_client:
                try:
                    await self.aioredis_client.delete(key)
                except Exception as e:
                    logger.warning("Redis delete failed", key=key, error=str(e))
            
            logger.debug("Cache delete successful", key=key)
            return True
            
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            return False
    
    async def clear(self) -> bool:
        """Clear all cache with maximum performance"""
        try:
            # Clear memory cache
            self.memory_cache.clear()
            
            # Clear Redis if available
            if self.enable_redis and self.aioredis_client:
                try:
                    await self.aioredis_client.flushdb()
                except Exception as e:
                    logger.warning("Redis clear failed", error=str(e))
            
            logger.info("Cache cleared successfully")
            return True
            
        except Exception as e:
            logger.error("Cache clear error", error=str(e))
            return False
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values with maximum performance"""
        start_time = time.time()
        results = {}
        
        try:
            # Try memory cache first
            for key in keys:
                if key in self.memory_cache:
                    results[key] = self.memory_cache[key]
                    self.hit_count += 1
            
            # Try Redis for remaining keys
            if self.enable_redis and self.aioredis_client:
                remaining_keys = [k for k in keys if k not in results]
                if remaining_keys:
                    try:
                        redis_values = await self.aioredis_client.mget(remaining_keys)
                        for key, value in zip(remaining_keys, redis_values):
                            if value is not None:
                                deserialized_value = self._deserialize_value(value)
                                results[key] = deserialized_value
                                self.memory_cache[key] = deserialized_value
                                self.hit_count += 1
                    except Exception as e:
                        logger.warning("Redis mget failed", error=str(e))
            
            # Count misses
            self.miss_count += len(keys) - len(results)
            self._update_metrics(time.time() - start_time)
            
            return results
            
        except Exception as e:
            logger.error("Cache get_many error", error=str(e))
            return {}
    
    async def set_many(self, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values with maximum performance"""
        start_time = time.time()
        
        try:
            # Set in memory cache
            for key, value in data.items():
                self.memory_cache[key] = value
            
            # Set in Redis if available
            if self.enable_redis and self.aioredis_client:
                try:
                    pipeline = self.aioredis_client.pipeline()
                    redis_ttl = ttl or self.default_ttl
                    
                    for key, value in data.items():
                        serialized_value = self._serialize_value(value)
                        pipeline.setex(key, redis_ttl, serialized_value)
                    
                    pipeline.execute()
                except Exception as e:
                    logger.warning("Redis set_many failed", error=str(e))
            
            self.set_count += len(data)
            self._update_metrics(time.time() - start_time)
            logger.debug("Cache set_many successful", count=len(data))
            return True
            
        except Exception as e:
            logger.error("Cache set_many error", error=str(e))
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "set_count": self.set_count,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "avg_operation_time": self.avg_operation_time,
            "memory_cache_size": len(self.memory_cache),
            "redis_enabled": self.enable_redis
        }
    
    def _update_metrics(self, elapsed: float):
        """Update performance metrics"""
        self.total_time += elapsed
        total_operations = self.hit_count + self.miss_count + self.set_count
        self.avg_operation_time = self.total_time / total_operations if total_operations > 0 else 0
    
    async def health_check(self) -> bool:
        """Health check for cache"""
        try:
            test_key = "__health_check__"
            test_value = {"timestamp": time.time()}
            
            # Test set
            set_success = await self.set(test_key, test_value, ttl=10)
            if not set_success:
                return False
            
            # Test get
            retrieved_value = await self.get(test_key)
            if retrieved_value != test_value:
                return False
            
            # Test delete
            delete_success = await self.delete(test_key)
            if not delete_success:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Cache health check failed", error=str(e))
            return False


# Global cache instance for maximum performance
_global_cache: Optional[UltraFastCache] = None


async def get_cache() -> UltraFastCache:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = UltraFastCache()
        await _global_cache.initialize()
    return _global_cache


async def cleanup_cache():
    """Cleanup global cache"""
    global _global_cache
    if _global_cache:
        await _global_cache.cleanup()
        _global_cache = None 