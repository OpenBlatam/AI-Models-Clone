#!/usr/bin/env python3
"""
🚀 ADVANCED CACHING MODULE - Blaze AI System
Distributed Redis caching with compression and intelligent invalidation
"""

import asyncio
import time
import json
import gzip
import hashlib
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aioredis
from functools import wraps

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache strategy enumeration."""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    ADAPTIVE = "adaptive"

class CompressionType(Enum):
    """Compression type enumeration."""
    NONE = "none"
    GZIP = "gzip"
    BROTLI = "brotli"

@dataclass
class CacheConfig:
    """Advanced cache configuration."""
    redis_url: str = "redis://localhost:6379"
    default_ttl: int = 3600  # 1 hour
    max_memory: str = "2gb"
    compression_threshold: int = 1024  # bytes
    compression_type: CompressionType = CompressionType.GZIP
    enable_clustering: bool = True
    cluster_nodes: List[str] = None
    retry_attempts: int = 3
    retry_delay: float = 0.1

@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    compression_ratio: float = 1.0
    avg_response_time: float = 0.0
    memory_usage: float = 0.0
    timestamp: float = 0.0

class AdvancedCache:
    """Advanced distributed caching system with compression."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_pool = None
        self.metrics = CacheMetrics()
        self.compression_stats = {
            'compressed': 0,
            'uncompressed': 0,
            'total_saved': 0
        }
        self._init_time = time.time()
    
    async def initialize(self):
        """Initialize Redis connection pool."""
        try:
            if self.config.enable_clustering and self.config.cluster_nodes:
                # Redis Cluster mode
                self.redis_pool = aioredis.RedisCluster.from_url(
                    self.config.redis_url,
                    startup_nodes=self.config.cluster_nodes,
                    decode_responses=True,
                    retry_on_timeout=True,
                    retry_on_error=[aioredis.ConnectionError],
                    max_connections=20
                )
            else:
                # Single Redis instance
                self.redis_pool = aioredis.from_url(
                    self.config.redis_url,
                    decode_responses=True,
                    max_connections=20,
                    retry_on_timeout=True
                )
            
            # Test connection
            await self.redis_pool.ping()
            logger.info("✅ Advanced cache initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize advanced cache: {e}")
            raise
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with automatic decompression."""
        start_time = time.time()
        
        try:
            if not self.redis_pool:
                return default
            
            # Get cached value
            cached_data = await self.redis_pool.get(key)
            
            if cached_data is None:
                self.metrics.misses += 1
                return default
            
            # Parse cached data
            try:
                data = json.loads(cached_data)
                if isinstance(data, dict) and 'compressed' in data:
                    if data['compressed']:
                        # Decompress data
                        decompressed = self._decompress_data(
                            data['data'], 
                            data['compression_type']
                        )
                        value = json.loads(decompressed)
                    else:
                        value = data['data']
                else:
                    value = data
                
                self.metrics.hits += 1
                response_time = time.time() - start_time
                self._update_avg_response_time(response_time)
                
                return value
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse cached data for key {key}: {e}")
                return default
                
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with intelligent compression."""
        start_time = time.time()
        
        try:
            if not self.redis_pool:
                return False
            
            # Determine if compression should be used
            value_str = json.dumps(value)
            should_compress = (
                len(value_str) > self.config.compression_threshold and
                self.config.compression_type != CompressionType.NONE
            )
            
            if should_compress:
                # Compress data
                compressed_data = self._compress_data(
                    value_str, 
                    self.config.compression_type
                )
                
                cache_data = {
                    'compressed': True,
                    'compression_type': self.config.compression_type.value,
                    'data': compressed_data,
                    'original_size': len(value_str),
                    'compressed_size': len(compressed_data)
                }
                
                self.compression_stats['compressed'] += 1
                self.compression_stats['total_saved'] += len(value_str) - len(compressed_data)
                
            else:
                cache_data = {
                    'compressed': False,
                    'data': value,
                    'compression_type': CompressionType.NONE.value
                }
                
                self.compression_stats['uncompressed'] += 1
            
            # Serialize and store
            serialized_data = json.dumps(cache_data)
            ttl = ttl or self.config.default_ttl
            
            await self.redis_pool.setex(key, ttl, serialized_data)
            
            self.metrics.sets += 1
            response_time = time.time() - start_time
            self._update_avg_response_time(response_time)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if not self.redis_pool:
                return False
            
            result = await self.redis_pool.delete(key)
            self.metrics.deletes += 1
            return result > 0
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def mget(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        try:
            if not self.redis_pool:
                return {}
            
            values = await self.redis_pool.mget(keys)
            result = {}
            
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        data = json.loads(value)
                        if isinstance(data, dict) and data.get('compressed'):
                            decompressed = self._decompress_data(
                                data['data'], 
                                data['compression_type']
                            )
                            result[key] = json.loads(decompressed)
                        else:
                            result[key] = data.get('data', data)
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            return result
            
        except Exception as e:
            logger.error(f"Error in mget: {e}")
            return {}
    
    async def mset(self, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache."""
        try:
            if not self.redis_pool:
                return False
            
            ttl = ttl or self.config.default_ttl
            pipeline = self.redis_pool.pipeline()
            
            for key, value in data.items():
                # Apply same compression logic as single set
                value_str = json.dumps(value)
                should_compress = (
                    len(value_str) > self.config.compression_threshold and
                    self.config.compression_type != CompressionType.NONE
                )
                
                if should_compress:
                    compressed_data = self._compress_data(
                        value_str, 
                        self.config.compression_type
                    )
                    
                    cache_data = {
                        'compressed': True,
                        'compression_type': self.config.compression_type.value,
                        'data': compressed_data,
                        'original_size': len(value_str),
                        'compressed_size': len(compressed_data)
                    }
                else:
                    cache_data = {
                        'compressed': False,
                        'data': value,
                        'compression_type': CompressionType.NONE.value
                    }
                
                serialized_data = json.dumps(cache_data)
                pipeline.setex(key, ttl, serialized_data)
            
            await pipeline.execute()
            self.metrics.sets += len(data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in mset: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern."""
        try:
            if not self.redis_pool:
                return 0
            
            keys = await self.redis_pool.keys(pattern)
            if keys:
                deleted = await self.redis_pool.delete(*keys)
                self.metrics.deletes += deleted
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"Error clearing pattern {pattern}: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        try:
            if not self.redis_pool:
                return {}
            
            # Get Redis info
            info = await self.redis_pool.info()
            
            # Calculate compression ratio
            total_compressed = self.compression_stats['compressed']
            total_uncompressed = self.compression_stats['uncompressed']
            
            if total_compressed > 0:
                compression_ratio = self.compression_stats['total_saved'] / (
                    self.compression_stats['total_saved'] + 
                    sum(len(str(v)) for v in self.compression_stats.values())
                )
            else:
                compression_ratio = 1.0
            
            # Update metrics
            self.metrics.compression_ratio = compression_ratio
            self.metrics.memory_usage = float(info.get('used_memory_human', '0').replace('M', ''))
            self.metrics.timestamp = time.time()
            
            return {
                'cache_metrics': asdict(self.metrics),
                'compression_stats': self.compression_stats,
                'redis_info': {
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory_human', '0'),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0)
                },
                'uptime': time.time() - self._init_time
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def _compress_data(self, data: str, compression_type: CompressionType) -> str:
        """Compress data using specified compression type."""
        try:
            if compression_type == CompressionType.GZIP:
                compressed = gzip.compress(data.encode('utf-8'))
                return compressed.hex()  # Convert to hex for JSON storage
            elif compression_type == CompressionType.BROTLI:
                # Note: brotli would need to be installed
                try:
                    import brotli
                    compressed = brotli.compress(data.encode('utf-8'))
                    return compressed.hex()
                except ImportError:
                    logger.warning("Brotli not available, falling back to gzip")
                    compressed = gzip.compress(data.encode('utf-8'))
                    return compressed.hex()
            else:
                return data
                
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return data
    
    def _decompress_data(self, compressed_data: str, compression_type: str) -> str:
        """Decompress data using specified compression type."""
        try:
            if compression_type == CompressionType.GZIP.value:
                # Convert from hex back to bytes
                compressed_bytes = bytes.fromhex(compressed_data)
                decompressed = gzip.decompress(compressed_bytes)
                return decompressed.decode('utf-8')
            elif compression_type == CompressionType.BROTLI.value:
                try:
                    import brotli
                    compressed_bytes = bytes.fromhex(compressed_data)
                    decompressed = brotli.decompress(compressed_bytes)
                    return decompressed.decode('utf-8')
                except ImportError:
                    logger.warning("Brotli not available, falling back to gzip")
                    compressed_bytes = bytes.fromhex(compressed_data)
                    decompressed = gzip.decompress(compressed_bytes)
                    return decompressed.decode('utf-8')
            else:
                return compressed_data
                
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            return compressed_data
    
    def _update_avg_response_time(self, response_time: float):
        """Update average response time."""
        total_requests = self.metrics.hits + self.metrics.misses + self.metrics.sets
        if total_requests > 0:
            self.metrics.avg_response_time = (
                (self.metrics.avg_response_time * (total_requests - 1) + response_time) / 
                total_requests
            )
    
    async def close(self):
        """Close Redis connection pool."""
        if self.redis_pool:
            await self.redis_pool.close()
            logger.info("Advanced cache connections closed")

# Cache decorator for easy use
def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator for automatic caching of function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cache_instance = getattr(wrapper, '_cache_instance', None)
            if cache_instance:
                cached_result = await cache_instance.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            if cache_instance:
                await cache_instance.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Utility functions
def create_advanced_cache(config: CacheConfig) -> AdvancedCache:
    """Create and configure an advanced cache instance."""
    return AdvancedCache(config)

async def initialize_advanced_cache(config: CacheConfig) -> AdvancedCache:
    """Create and initialize an advanced cache instance."""
    cache = create_advanced_cache(config)
    await cache.initialize()
    return cache

# Example usage
async def main():
    """Example usage of the advanced cache."""
    config = CacheConfig(
        redis_url="redis://localhost:6379",
        compression_type=CompressionType.GZIP,
        compression_threshold=100
    )
    
    cache = await initialize_advanced_cache(config)
    
    # Test caching
    await cache.set("test_key", {"message": "Hello World!", "timestamp": time.time()})
    result = await cache.get("test_key")
    
    print(f"Cached result: {result}")
    
    # Get stats
    stats = await cache.get_stats()
    print(f"Cache stats: {json.dumps(stats, indent=2)}")
    
    await cache.close()

if __name__ == "__main__":
    asyncio.run(main())
