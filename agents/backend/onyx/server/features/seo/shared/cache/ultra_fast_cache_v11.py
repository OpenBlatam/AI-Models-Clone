#!/usr/bin/env python3
"""
Ultra-Fast Cache v11
Maximum Performance with Latest Optimizations
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
    size: int = 0
    compression_ratio: float = 1.0


class UltraFastCacheV11:
    """Ultra-fast cache with maximum performance optimizations v11"""
    
    def __init__(
        self,
        maxsize: int = 50000,
        ttl: int = 3600,
        enable_compression: bool = True,
        compression_threshold: int = 512,
        redis_url: Optional[str] = None,
        enable_redis: bool = False,
        compression_level: int = 3,
        enable_stats: bool = True
    ):
        self.maxsize = maxsize
        self.default_ttl = ttl
        self.enable_compression = enable_compression
        self.compression_threshold = compression_threshold
        self.enable_redis = enable_redis
        self.compression_level = compression_level
        self.enable_stats = enable_stats
        
        # In-memory cache with maximum performance
        self.memory_cache = TTLCache(maxsize=maxsize, ttl=ttl)
        
        # Redis client for distributed caching
        self.redis_client = None
        if enable_redis and redis_url:
            self.redis_client = redis.Redis.from_url(
                redis_url, 
                decode_responses=False,
                socket_keepalive=True,
                socket_keepalive_options={},
                retry_on_timeout=True,
                health_check_interval=30
            )
        
        # Async Redis client
        self.aioredis_client = None
        
        # Performance metrics
        self.hit_count = 0
        self.miss_count = 0
        self.set_count = 0
        self.total_time = 0.0
        self.avg_operation_time = 0.0
        self.compression_savings = 0
        self.total_size = 0
        self.compressed_size = 0
        
        # Advanced features
        self._compression_stats = {}
        self._access_patterns = {}
    
    async def initialize(self):
        """Initialize async components with advanced configuration"""
        if self.enable_redis:
            try:
                self.aioredis_client = await aioredis.from_url(
                    "redis://localhost:6379",
                    encoding="utf-8",
                    decode_responses=False,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    retry_on_timeout=True,
                    health_check_interval=30,
                    max_connections=50,
                    max_connections_per_node=10
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
        key_bytes = orjson.dumps(key_data, sort_keys=True, option=orjson.OPT_SERIALIZE_NUMPY)
        return hashlib.sha256(key_bytes).hexdigest()
    
    def _compress_data(self, data: bytes, algorithm: str = "zstd") -> bytes:
        """Compress data with fastest algorithm and advanced options"""
        if algorithm == "zstd":
            compressor = zstd.ZstdCompressor(
                level=self.compression_level,
                threads=0,  # Use all available threads
                write_content_size=True,
                write_checksum=True
            )
            return compressor.compress(data)
        elif algorithm == "brotli":
            return brotli.compress(
                data, 
                quality=4, 
                lgwin=22,
                lgblock=24,
                mode=brotli.MODE_GENERIC
            )
        else:
            return data
    
    def _decompress_data(self, data: bytes, algorithm: str = "zstd") -> bytes:
        """Decompress data with error handling"""
        try:
            if algorithm == "zstd":
                decompressor = zstd.ZstdDecompressor()
                return decompressor.decompress(data)
            elif algorithm == "brotli":
                return brotli.decompress(data)
            else:
                return data
        except Exception as e:
            logger.error("Decompression failed", algorithm=algorithm, error=str(e))
            return data
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value with maximum performance"""
        return orjson.dumps(value, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NAIVE_UTC)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value with maximum performance"""
        return orjson.loads(data)
    
    def _should_compress(self, data: bytes) -> bool:
        """Determine if data should be compressed"""
        if not self.enable_compression:
            return False
        
        if len(data) < self.compression_threshold:
            return False
        
        # Check if data is already compressed
        if data.startswith(b'\x1f\x8b') or data.startswith(b'\x78\x9c') or data.startswith(b'\x28\xb5'):
            return False
        
        return True
    
    def _get_best_compression(self, data: bytes) -> tuple:
        """Get the best compression algorithm for the data"""
        if not self._should_compress(data):
            return data, "none", 1.0
        
        # Try different compression algorithms
        algorithms = [
            ("zstd", self._compress_data(data, "zstd")),
            ("brotli", self._compress_data(data, "brotli"))
        ]
        
        best_algorithm = "none"
        best_compressed = data
        best_ratio = 1.0
        
        for name, compressed in algorithms:
            ratio = len(compressed) / len(data)
            if ratio < best_ratio:
                best_ratio = ratio
                best_compressed = compressed
                best_algorithm = name
        
        return best_compressed, best_algorithm, best_ratio
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with maximum performance and advanced features"""
        start_time = time.time()
        
        try:
            # Try memory cache first (fastest)
            if key in self.memory_cache:
                self.hit_count += 1
                self._update_metrics(time.time() - start_time)
                self._track_access_pattern(key)
                logger.debug("Memory cache hit", key=key, hit_count=self.hit_count)
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
                        self._track_access_pattern(key)
                        logger.debug("Redis cache hit", key=key, hit_count=self.hit_count)
                        return value
                except Exception as e:
                    logger.warning("Redis get failed", key=key, error=str(e))
            
            # Cache miss
            self.miss_count += 1
            self._update_metrics(time.time() - start_time)
            logger.debug("Cache miss", key=key, miss_count=self.miss_count)
            return default
            
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with maximum performance and advanced compression"""
        start_time = time.time()
        
        try:
            # Serialize value
            serialized_value = self._serialize_value(value)
            original_size = len(serialized_value)
            
            # Compress if enabled and beneficial
            compressed_value, algorithm, ratio = self._get_best_compression(serialized_value)
            compressed_size = len(compressed_value)
            
            # Update compression statistics
            if self.enable_stats:
                self.compression_savings += (original_size - compressed_size)
                self.total_size += original_size
                self.compressed_size += compressed_size
                
                if algorithm not in self._compression_stats:
                    self._compression_stats[algorithm] = {"count": 0, "total_savings": 0}
                self._compression_stats[algorithm]["count"] += 1
                self._compression_stats[algorithm]["total_savings"] += (original_size - compressed_size)
            
            # Store in memory cache
            self.memory_cache[key] = value
            
            # Store in Redis if available
            if self.enable_redis and self.aioredis_client:
                try:
                    redis_ttl = ttl or self.default_ttl
                    await self.aioredis_client.setex(key, redis_ttl, compressed_value)
                except Exception as e:
                    logger.warning("Redis set failed", key=key, error=str(e))
            
            self.set_count += 1
            self._update_metrics(time.time() - start_time)
            logger.debug(
                "Cache set successful", 
                key=key, 
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=ratio,
                algorithm=algorithm
            )
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
            
            # Reset statistics
            if self.enable_stats:
                self.compression_savings = 0
                self.total_size = 0
                self.compressed_size = 0
                self._compression_stats.clear()
                self._access_patterns.clear()
            
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
                    self._track_access_pattern(key)
            
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
                                self._track_access_pattern(key)
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
                        compressed_value, _, _ = self._get_best_compression(serialized_value)
                        pipeline.setex(key, redis_ttl, compressed_value)
                    
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
    
    def _track_access_pattern(self, key: str):
        """Track access patterns for optimization"""
        if self.enable_stats:
            if key not in self._access_patterns:
                self._access_patterns[key] = 0
            self._access_patterns[key] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        compression_efficiency = (
            (self.compression_savings / self.total_size * 100) 
            if self.total_size > 0 else 0
        )
        
        # Get top accessed keys
        top_keys = sorted(
            self._access_patterns.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        stats = {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "set_count": self.set_count,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "avg_operation_time": self.avg_operation_time,
            "memory_cache_size": len(self.memory_cache),
            "redis_enabled": self.enable_redis,
            "compression_efficiency": compression_efficiency,
            "total_size": self.total_size,
            "compressed_size": self.compressed_size,
            "compression_savings": self.compression_savings,
            "compression_stats": self._compression_stats,
            "top_accessed_keys": top_keys
        }
        
        return stats
    
    def _update_metrics(self, elapsed: float):
        """Update performance metrics"""
        self.total_time += elapsed
        total_operations = self.hit_count + self.miss_count + self.set_count
        self.avg_operation_time = self.total_time / total_operations if total_operations > 0 else 0
    
    async def health_check(self) -> bool:
        """Health check for cache"""
        try:
            test_key = "__health_check__"
            test_value = {"timestamp": time.time(), "test": "data"}
            
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
    
    async def optimize(self) -> Dict[str, Any]:
        """Optimize cache performance"""
        logger.info("Starting cache optimization")
        
        optimization_results = {
            "memory_cache_size_before": len(self.memory_cache),
            "compression_efficiency_before": self.get_stats()["compression_efficiency"],
            "hit_rate_before": self.get_stats()["hit_rate"]
        }
        
        # Remove least accessed keys if cache is too full
        if len(self.memory_cache) > self.maxsize * 0.9:
            # Convert to LRU cache temporarily to remove least used items
            lru_cache = LRUCache(maxsize=self.maxsize * 0.8)
            for key, value in self.memory_cache.items():
                lru_cache[key] = value
            
            removed_count = len(self.memory_cache) - len(lru_cache)
            self.memory_cache.clear()
            self.memory_cache.update(lru_cache)
            
            optimization_results["removed_keys"] = removed_count
            logger.info(f"Removed {removed_count} least accessed keys")
        
        optimization_results.update({
            "memory_cache_size_after": len(self.memory_cache),
            "compression_efficiency_after": self.get_stats()["compression_efficiency"],
            "hit_rate_after": self.get_stats()["hit_rate"]
        })
        
        logger.info("Cache optimization completed", **optimization_results)
        return optimization_results


# Global cache instance for maximum performance
_global_cache: Optional[UltraFastCacheV11] = None


async def get_cache() -> UltraFastCacheV11:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = UltraFastCacheV11()
        await _global_cache.initialize()
    return _global_cache


async def cleanup_cache():
    """Cleanup global cache"""
    global _global_cache
    if _global_cache:
        await _global_cache.cleanup()
        _global_cache = None 