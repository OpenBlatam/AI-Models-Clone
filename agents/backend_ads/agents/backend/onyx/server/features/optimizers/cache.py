"""
Cache Optimizer - Ultra-High Performance Caching System.

Advanced caching optimizer with multi-tier architecture, intelligent eviction,
compression, distributed caching, and memory optimization.
"""

import asyncio
import time
import hashlib
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass
from contextlib import asynccontextmanager
from enum import Enum
import logging

# High-performance serialization
try:
    import orjson
    JSON_AVAILABLE = True
except ImportError:
    import json as orjson
    JSON_AVAILABLE = False

# Redis for distributed caching
try:
    import aioredis
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Memory caching
try:
    from cachetools import TTLCache, LRUCache, LFUCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False

# Compression
try:
    import blosc2
    BLOSC2_AVAILABLE = True
except ImportError:
    BLOSC2_AVAILABLE = False

try:
    import xxhash
    XXHASH_AVAILABLE = True
except ImportError:
    XXHASH_AVAILABLE = False

# Disk caching
try:
    import diskcache
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache level hierarchy."""
    L1_MEMORY = "l1_memory"      # In-process memory cache
    L2_PROCESS = "l2_process"    # Shared memory cache
    L3_DISK = "l3_disk"          # Local disk cache
    L4_DISTRIBUTED = "l4_distributed"  # Distributed cache (Redis)


class EvictionPolicy(Enum):
    """Cache eviction policies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out


@dataclass
class CacheConfig:
    """Cache optimization configuration."""
    # Multi-tier settings
    enable_l1_cache: bool = True
    enable_l2_cache: bool = True
    enable_l3_cache: bool = DISKCACHE_AVAILABLE
    enable_l4_cache: bool = REDIS_AVAILABLE
    
    # Size limits (in MB)
    l1_size_mb: int = 256
    l2_size_mb: int = 512
    l3_size_mb: int = 2048
    l4_size_mb: int = 10240
    
    # TTL settings (in seconds)
    default_ttl: int = 3600
    l1_ttl: int = 300
    l2_ttl: int = 1800
    l3_ttl: int = 3600
    l4_ttl: int = 86400
    
    # Eviction policies
    l1_eviction: EvictionPolicy = EvictionPolicy.LRU
    l2_eviction: EvictionPolicy = EvictionPolicy.LFU
    l3_eviction: EvictionPolicy = EvictionPolicy.TTL
    
    # Compression settings
    enable_compression: bool = BLOSC2_AVAILABLE
    compression_threshold: int = 1024  # Compress data larger than 1KB
    compression_level: int = 3  # Fast compression
    
    # Performance settings
    enable_async_write: bool = True
    write_batch_size: int = 100
    enable_background_cleanup: bool = True
    cleanup_interval: int = 300
    
    # Redis settings (if available)
    redis_url: str = "redis://localhost:6379"
    redis_max_connections: int = 100
    redis_timeout: float = 5.0


class CompressionManager:
    """Manage data compression for cache optimization."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.compression_stats = {
            "total_compressed": 0,
            "total_decompressed": 0,
            "compression_ratio": 0.0,
            "avg_compression_time": 0.0
        }
    
    def should_compress(self, data: bytes) -> bool:
        """Determine if data should be compressed."""
        return (
            self.config.enable_compression and 
            len(data) >= self.config.compression_threshold
        )
    
    def compress(self, data: bytes) -> Tuple[bytes, bool]:
        """Compress data if beneficial."""
        if not self.should_compress(data):
            return data, False
        
        start_time = time.time()
        
        try:
            if BLOSC2_AVAILABLE:
                compressed = blosc2.compress(
                    data, 
                    clevel=self.config.compression_level,
                    cname="lz4"
                )
            else:
                import gzip
                compressed = gzip.compress(data, compresslevel=self.config.compression_level)
            
            # Only use compression if it actually reduces size
            if len(compressed) < len(data) * 0.9:  # At least 10% reduction
                compression_time = time.time() - start_time
                self.compression_stats["total_compressed"] += 1
                self.compression_stats["avg_compression_time"] = (
                    self.compression_stats["avg_compression_time"] + compression_time
                ) / 2
                return compressed, True
            else:
                return data, False
                
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            return data, False
    
    def decompress(self, data: bytes, was_compressed: bool) -> bytes:
        """Decompress data if it was compressed."""
        if not was_compressed:
            return data
        
        try:
            if BLOSC2_AVAILABLE:
                return blosc2.decompress(data)
            else:
                import gzip
                return gzip.decompress(data)
                
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            raise


class KeyManager:
    """Manage cache keys with optimization and namespace support."""
    
    def __init__(self):
        self.key_stats = {
            "total_keys": 0,
            "key_collisions": 0,
            "namespace_usage": {}
        }
    
    def generate_key(self, key: str, namespace: str = "default") -> str:
        """Generate optimized cache key."""
        if XXHASH_AVAILABLE:
            # Use xxhash for fast, high-quality hashing
            full_key = f"{namespace}:{key}"
            key_hash = xxhash.xxh64(full_key.encode()).hexdigest()[:16]  # 16 chars = 64 bits
            cache_key = f"{namespace}:{key_hash}"
        else:
            # Fallback to MD5
            full_key = f"{namespace}:{key}"
            key_hash = hashlib.md5(full_key.encode()).hexdigest()[:16]
            cache_key = f"{namespace}:{key_hash}"
        
        self.key_stats["total_keys"] += 1
        if namespace not in self.key_stats["namespace_usage"]:
            self.key_stats["namespace_usage"][namespace] = 0
        self.key_stats["namespace_usage"][namespace] += 1
        
        return cache_key
    
    def extract_namespace(self, cache_key: str) -> str:
        """Extract namespace from cache key."""
        return cache_key.split(":", 1)[0] if ":" in cache_key else "default"


class L1MemoryCache:
    """L1 in-process memory cache."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.max_size = config.l1_size_mb * 1024 * 1024  # Convert to bytes
        
        if CACHETOOLS_AVAILABLE:
            if config.l1_eviction == EvictionPolicy.TTL:
                self.cache = TTLCache(maxsize=10000, ttl=config.l1_ttl)
            elif config.l1_eviction == EvictionPolicy.LFU:
                self.cache = LFUCache(maxsize=10000)
            else:  # LRU
                self.cache = LRUCache(maxsize=10000)
        else:
            # Simple dict fallback
            self.cache = {}
        
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
            "size_bytes": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from L1 cache."""
        try:
            if key in self.cache:
                self.stats["hits"] += 1
                return self.cache[key]
            else:
                self.stats["misses"] += 1
                return None
        except Exception as e:
            logger.warning(f"L1 cache get failed: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in L1 cache."""
        try:
            # Estimate size
            value_size = len(str(value).encode('utf-8'))
            
            # Check if we have space
            if self.stats["size_bytes"] + value_size > self.max_size:
                self._evict_to_make_space(value_size)
            
            self.cache[key] = value
            self.stats["sets"] += 1
            self.stats["size_bytes"] += value_size
            
            return True
            
        except Exception as e:
            logger.warning(f"L1 cache set failed: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from L1 cache."""
        try:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
        except Exception as e:
            logger.warning(f"L1 cache delete failed: {e}")
            return False
    
    def _evict_to_make_space(self, needed_space: int):
        """Evict items to make space."""
        if not CACHETOOLS_AVAILABLE:
            # Simple FIFO eviction for dict
            keys_to_remove = list(self.cache.keys())[:10]  # Remove 10 items
            for key in keys_to_remove:
                del self.cache[key]
            self.stats["evictions"] += len(keys_to_remove)


class L4DistributedCache:
    """L4 distributed cache using Redis."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_pool = None
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "connection_errors": 0
        }
    
    async def initialize(self) -> bool:
        """Initialize Redis connection pool."""
        if not REDIS_AVAILABLE:
            return False
        
        try:
            self.redis_pool = aioredis.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=self.config.redis_max_connections,
                socket_timeout=self.config.redis_timeout,
                socket_connect_timeout=self.config.redis_timeout
            )
            
            # Test connection
            redis_client = aioredis.Redis(connection_pool=self.redis_pool)
            await redis_client.ping()
            await redis_client.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            return False
    
    async def get(self, key: str) -> Optional[bytes]:
        """Get value from Redis."""
        if not self.redis_pool:
            return None
        
        try:
            redis_client = aioredis.Redis(connection_pool=self.redis_pool)
            value = await redis_client.get(key)
            await redis_client.close()
            
            if value:
                self.stats["hits"] += 1
                return value
            else:
                self.stats["misses"] += 1
                return None
                
        except Exception as e:
            self.stats["connection_errors"] += 1
            logger.warning(f"Redis get failed: {e}")
            return None
    
    async def set(self, key: str, value: bytes, ttl: Optional[int] = None) -> bool:
        """Set value in Redis."""
        if not self.redis_pool:
            return False
        
        try:
            redis_client = aioredis.Redis(connection_pool=self.redis_pool)
            
            if ttl:
                await redis_client.setex(key, ttl, value)
            else:
                await redis_client.set(key, value)
            
            await redis_client.close()
            self.stats["sets"] += 1
            return True
            
        except Exception as e:
            self.stats["connection_errors"] += 1
            logger.warning(f"Redis set failed: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis."""
        if not self.redis_pool:
            return False
        
        try:
            redis_client = aioredis.Redis(connection_pool=self.redis_pool)
            result = await redis_client.delete(key)
            await redis_client.close()
            return result > 0
            
        except Exception as e:
            logger.warning(f"Redis delete failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup Redis connections."""
        if self.redis_pool:
            await self.redis_pool.disconnect()


class CacheOptimizer:
    """Main cache optimizer with multi-tier architecture."""
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        
        # Initialize components
        self.compression_manager = CompressionManager(self.config)
        self.key_manager = KeyManager()
        
        # Initialize cache layers
        self.l1_cache = L1MemoryCache(self.config) if self.config.enable_l1_cache else None
        self.l4_cache = L4DistributedCache(self.config) if self.config.enable_l4_cache else None
        
        # Initialize disk cache
        self.l3_cache = None
        if self.config.enable_l3_cache and DISKCACHE_AVAILABLE:
            try:
                cache_dir = "/tmp/onyx_disk_cache"
                self.l3_cache = diskcache.Cache(
                    cache_dir,
                    size_limit=self.config.l3_size_mb * 1024 * 1024
                )
            except Exception as e:
                logger.warning(f"Disk cache initialization failed: {e}")
        
        # Global stats
        self.global_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "hit_ratio": 0.0,
            "layer_distribution": {
                "l1": 0, "l2": 0, "l3": 0, "l4": 0
            }
        }
    
    async def initialize(self) -> Dict[str, bool]:
        """Initialize cache optimizer."""
        results = {}
        
        # Initialize L4 (Redis) cache
        if self.l4_cache:
            results["l4_distributed"] = await self.l4_cache.initialize()
        else:
            results["l4_distributed"] = False
        
        # Other caches are initialized in constructor
        results["l1_memory"] = self.l1_cache is not None
        results["l3_disk"] = self.l3_cache is not None
        
        logger.info("Cache optimizer initialized", 
                   layers=sum(results.values()),
                   results=results)
        
        return results
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value with multi-tier lookup."""
        self.global_stats["total_requests"] += 1
        cache_key = self.key_manager.generate_key(key, namespace)
        
        # L1 Memory cache
        if self.l1_cache:
            value = self.l1_cache.get(cache_key)
            if value is not None:
                self.global_stats["cache_hits"] += 1
                self.global_stats["layer_distribution"]["l1"] += 1
                return value
        
        # L3 Disk cache
        if self.l3_cache:
            try:
                value = self.l3_cache.get(cache_key)
                if value is not None:
                    # Promote to L1
                    if self.l1_cache:
                        self.l1_cache.set(cache_key, value)
                    
                    self.global_stats["cache_hits"] += 1
                    self.global_stats["layer_distribution"]["l3"] += 1
                    return value
            except Exception as e:
                logger.warning(f"L3 cache get failed: {e}")
        
        # L4 Distributed cache
        if self.l4_cache:
            try:
                compressed_value = await self.l4_cache.get(cache_key)
                if compressed_value:
                    # Decompress and deserialize
                    metadata_key = f"{cache_key}:meta"
                    metadata_bytes = await self.l4_cache.get(metadata_key)
                    
                    if metadata_bytes:
                        metadata = orjson.loads(metadata_bytes)
                        data = self.compression_manager.decompress(
                            compressed_value, 
                            metadata.get("compressed", False)
                        )
                        value = orjson.loads(data)
                        
                        # Promote to higher caches
                        if self.l1_cache:
                            self.l1_cache.set(cache_key, value)
                        if self.l3_cache:
                            try:
                                self.l3_cache.set(cache_key, value)
                            except:
                                pass
                        
                        self.global_stats["cache_hits"] += 1
                        self.global_stats["layer_distribution"]["l4"] += 1
                        return value
            except Exception as e:
                logger.warning(f"L4 cache get failed: {e}")
        
        # Cache miss
        self.global_stats["cache_misses"] += 1
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        namespace: str = "default"
    ) -> Dict[str, bool]:
        """Set value in all appropriate cache layers."""
        cache_key = self.key_manager.generate_key(key, namespace)
        ttl = ttl or self.config.default_ttl
        results = {}
        
        # Serialize value
        try:
            serialized_data = orjson.dumps(value)
        except Exception as e:
            logger.error(f"Serialization failed: {e}")
            return {"serialization": False}
        
        # L1 Memory cache
        if self.l1_cache:
            results["l1"] = self.l1_cache.set(cache_key, value, ttl)
        
        # L3 Disk cache
        if self.l3_cache:
            try:
                self.l3_cache.set(cache_key, value, expire=ttl)
                results["l3"] = True
            except Exception as e:
                logger.warning(f"L3 cache set failed: {e}")
                results["l3"] = False
        
        # L4 Distributed cache
        if self.l4_cache:
            try:
                # Compress data
                compressed_data, was_compressed = self.compression_manager.compress(serialized_data)
                
                # Store data and metadata
                metadata = {
                    "compressed": was_compressed,
                    "timestamp": time.time(),
                    "size": len(serialized_data)
                }
                
                data_success = await self.l4_cache.set(cache_key, compressed_data, ttl)
                meta_success = await self.l4_cache.set(
                    f"{cache_key}:meta", 
                    orjson.dumps(metadata), 
                    ttl
                )
                
                results["l4"] = data_success and meta_success
            except Exception as e:
                logger.warning(f"L4 cache set failed: {e}")
                results["l4"] = False
        
        return results
    
    async def delete(self, key: str, namespace: str = "default") -> Dict[str, bool]:
        """Delete value from all cache layers."""
        cache_key = self.key_manager.generate_key(key, namespace)
        results = {}
        
        # L1 Memory cache
        if self.l1_cache:
            results["l1"] = self.l1_cache.delete(cache_key)
        
        # L3 Disk cache
        if self.l3_cache:
            try:
                results["l3"] = self.l3_cache.delete(cache_key)
            except Exception as e:
                logger.warning(f"L3 cache delete failed: {e}")
                results["l3"] = False
        
        # L4 Distributed cache
        if self.l4_cache:
            data_delete = await self.l4_cache.delete(cache_key)
            meta_delete = await self.l4_cache.delete(f"{cache_key}:meta")
            results["l4"] = data_delete or meta_delete
        
        return results
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cache performance metrics."""
        # Calculate hit ratio
        total_requests = self.global_stats["total_requests"]
        if total_requests > 0:
            self.global_stats["hit_ratio"] = (
                self.global_stats["cache_hits"] / total_requests
            )
        
        metrics = {
            "global_stats": self.global_stats,
            "compression_stats": self.compression_manager.compression_stats,
            "key_stats": self.key_manager.key_stats,
            "config": {
                "l1_enabled": self.config.enable_l1_cache,
                "l3_enabled": self.config.enable_l3_cache,
                "l4_enabled": self.config.enable_l4_cache,
                "compression_enabled": self.config.enable_compression
            }
        }
        
        # Add layer-specific metrics
        if self.l1_cache:
            metrics["l1_stats"] = self.l1_cache.stats
        
        if self.l4_cache:
            metrics["l4_stats"] = self.l4_cache.stats
        
        return metrics
    
    async def cleanup(self):
        """Cleanup cache resources."""
        if self.l4_cache:
            await self.l4_cache.cleanup()
        
        if self.l3_cache:
            try:
                self.l3_cache.close()
            except:
                pass
        
        logger.info("Cache optimizer cleanup completed")


__all__ = [
    'CacheOptimizer',
    'CacheConfig',
    'CacheLevel',
    'EvictionPolicy'
] 