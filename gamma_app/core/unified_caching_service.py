"""
Unified Caching Service - Advanced caching functionality
Implements multi-level caching with Redis, Memcached, and in-memory caching
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
import json
import pickle
import hashlib
import time
from datetime import datetime, timedelta
import redis.asyncio as redis
import aiomcache
from collections import OrderedDict
import threading
import weakref

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Cache Levels"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_MEMCACHED = "l3_memcached"
    L4_DATABASE = "l4_database"

class CacheStrategy(Enum):
    """Cache Strategies"""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"

@dataclass
class CacheConfig:
    """Cache Configuration"""
    # L1 Memory Cache
    l1_max_size: int = 1000
    l1_ttl: int = 300  # 5 minutes
    
    # L2 Redis Cache
    l2_enabled: bool = True
    l2_redis_url: str = "redis://localhost:6379/0"
    l2_ttl: int = 3600  # 1 hour
    l2_max_connections: int = 20
    
    # L3 Memcached Cache
    l3_enabled: bool = False
    l3_memcached_host: str = "localhost"
    l3_memcached_port: int = 11211
    l3_ttl: int = 7200  # 2 hours
    
    # General settings
    default_ttl: int = 1800  # 30 minutes
    compression_enabled: bool = True
    serialization_method: str = "json"  # json, pickle, msgpack
    enable_statistics: bool = True

@dataclass
class CacheEntry:
    """Cache Entry"""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: datetime
    size_bytes: int = 0
    level: CacheLevel = CacheLevel.L1_MEMORY

@dataclass
class CacheStatistics:
    """Cache Statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    hit_rate: float = 0.0
    total_size_bytes: int = 0
    entries_count: int = 0
    last_reset: datetime = None

class UnifiedCachingService:
    """
    Unified Caching Service - Advanced multi-level caching
    Implements L1 (memory), L2 (Redis), L3 (Memcached) caching with statistics
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        
        # L1 Memory Cache (LRU)
        self.l1_cache: OrderedDict = OrderedDict()
        self.l1_lock = threading.RLock()
        
        # L2 Redis Cache
        self.l2_redis: Optional[redis.Redis] = None
        self.l2_pool: Optional[redis.ConnectionPool] = None
        
        # L3 Memcached Cache
        self.l3_memcached: Optional[aiomcache.Client] = None
        
        # Statistics
        self.stats = CacheStatistics()
        self.stats.last_reset = datetime.now()
        
        # Serialization
        self.serializers = {
            "json": self._serialize_json,
            "pickle": self._serialize_pickle,
            "msgpack": self._serialize_msgpack
        }
        
        self.deserializers = {
            "json": self._deserialize_json,
            "pickle": self._deserialize_pickle,
            "msgpack": self._deserialize_msgpack
        }
        
        logger.info("UnifiedCachingService initialized")
    
    async def initialize(self):
        """Initialize caching service"""
        try:
            # Initialize L2 Redis
            if self.config.l2_enabled:
                await self._init_redis()
            
            # Initialize L3 Memcached
            if self.config.l3_enabled:
                await self._init_memcached()
            
            logger.info("Caching service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing caching service: {e}")
            raise
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self.l2_pool = redis.ConnectionPool.from_url(
                self.config.l2_redis_url,
                max_connections=self.config.l2_max_connections
            )
            self.l2_redis = redis.Redis(connection_pool=self.l2_pool)
            
            # Test connection
            await self.l2_redis.ping()
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.error(f"Error initializing Redis: {e}")
            self.config.l2_enabled = False
    
    async def _init_memcached(self):
        """Initialize Memcached connection"""
        try:
            self.l3_memcached = aiomcache.Client(
                self.config.l3_memcached_host,
                self.config.l3_memcached_port
            )
            
            # Test connection
            await self.l3_memcached.set(b"test", b"test", 1)
            await self.l3_memcached.delete(b"test")
            logger.info("Memcached connection established")
            
        except Exception as e:
            logger.error(f"Error initializing Memcached: {e}")
            self.config.l3_enabled = False
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        try:
            self.stats.total_requests += 1
            
            # Try L1 Memory Cache first
            value = await self._get_from_l1(key)
            if value is not None:
                self.stats.hits += 1
                self._update_hit_rate()
                return value
            
            # Try L2 Redis Cache
            if self.config.l2_enabled:
                value = await self._get_from_l2(key)
                if value is not None:
                    # Promote to L1
                    await self._set_to_l1(key, value, self.config.l1_ttl)
                    self.stats.hits += 1
                    self._update_hit_rate()
                    return value
            
            # Try L3 Memcached Cache
            if self.config.l3_enabled:
                value = await self._get_from_l3(key)
                if value is not None:
                    # Promote to L1 and L2
                    await self._set_to_l1(key, value, self.config.l1_ttl)
                    if self.config.l2_enabled:
                        await self._set_to_l2(key, value, self.config.l2_ttl)
                    self.stats.hits += 1
                    self._update_hit_rate()
                    return value
            
            # Cache miss
            self.stats.misses += 1
            self._update_hit_rate()
            return default
            
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            if ttl is None:
                ttl = self.config.default_ttl
            
            # Set in L1 Memory Cache
            await self._set_to_l1(key, value, ttl)
            
            # Set in L2 Redis Cache
            if self.config.l2_enabled:
                await self._set_to_l2(key, value, ttl)
            
            # Set in L3 Memcached Cache
            if self.config.l3_enabled:
                await self._set_to_l3(key, value, ttl)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            deleted = False
            
            # Delete from L1
            if await self._delete_from_l1(key):
                deleted = True
            
            # Delete from L2
            if self.config.l2_enabled and await self._delete_from_l2(key):
                deleted = True
            
            # Delete from L3
            if self.config.l3_enabled and await self._delete_from_l3(key):
                deleted = True
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def clear(self, level: Optional[CacheLevel] = None) -> bool:
        """Clear cache"""
        try:
            if level is None:
                # Clear all levels
                await self._clear_l1()
                if self.config.l2_enabled:
                    await self._clear_l2()
                if self.config.l3_enabled:
                    await self._clear_l3()
            else:
                if level == CacheLevel.L1_MEMORY:
                    await self._clear_l1()
                elif level == CacheLevel.L2_REDIS and self.config.l2_enabled:
                    await self._clear_l2()
                elif level == CacheLevel.L3_MEMCACHED and self.config.l3_enabled:
                    await self._clear_l3()
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def _get_from_l1(self, key: str) -> Any:
        """Get from L1 memory cache"""
        try:
            with self.l1_lock:
                if key in self.l1_cache:
                    entry = self.l1_cache[key]
                    
                    # Check expiration
                    if datetime.now() > entry.expires_at:
                        del self.l1_cache[key]
                        self.stats.evictions += 1
                        return None
                    
                    # Update access info
                    entry.access_count += 1
                    entry.last_accessed = datetime.now()
                    
                    # Move to end (LRU)
                    self.l1_cache.move_to_end(key)
                    
                    return entry.value
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting from L1 cache: {e}")
            return None
    
    async def _set_to_l1(self, key: str, value: Any, ttl: int):
        """Set to L1 memory cache"""
        try:
            with self.l1_lock:
                # Check if we need to evict
                if len(self.l1_cache) >= self.config.l1_max_size:
                    # Remove oldest entry (LRU)
                    oldest_key = next(iter(self.l1_cache))
                    del self.l1_cache[oldest_key]
                    self.stats.evictions += 1
                
                # Create cache entry
                now = datetime.now()
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=now,
                    expires_at=now + timedelta(seconds=ttl),
                    last_accessed=now,
                    size_bytes=len(str(value).encode('utf-8')),
                    level=CacheLevel.L1_MEMORY
                )
                
                self.l1_cache[key] = entry
                
        except Exception as e:
            logger.error(f"Error setting to L1 cache: {e}")
    
    async def _delete_from_l1(self, key: str) -> bool:
        """Delete from L1 memory cache"""
        try:
            with self.l1_lock:
                if key in self.l1_cache:
                    del self.l1_cache[key]
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error deleting from L1 cache: {e}")
            return False
    
    async def _clear_l1(self):
        """Clear L1 memory cache"""
        try:
            with self.l1_lock:
                self.l1_cache.clear()
                
        except Exception as e:
            logger.error(f"Error clearing L1 cache: {e}")
    
    async def _get_from_l2(self, key: str) -> Any:
        """Get from L2 Redis cache"""
        try:
            if not self.l2_redis:
                return None
            
            serialized_value = await self.l2_redis.get(key)
            if serialized_value:
                return self._deserialize(serialized_value)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting from L2 cache: {e}")
            return None
    
    async def _set_to_l2(self, key: str, value: Any, ttl: int):
        """Set to L2 Redis cache"""
        try:
            if not self.l2_redis:
                return
            
            serialized_value = self._serialize(value)
            await self.l2_redis.setex(key, ttl, serialized_value)
            
        except Exception as e:
            logger.error(f"Error setting to L2 cache: {e}")
    
    async def _delete_from_l2(self, key: str) -> bool:
        """Delete from L2 Redis cache"""
        try:
            if not self.l2_redis:
                return False
            
            result = await self.l2_redis.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Error deleting from L2 cache: {e}")
            return False
    
    async def _clear_l2(self):
        """Clear L2 Redis cache"""
        try:
            if self.l2_redis:
                await self.l2_redis.flushdb()
                
        except Exception as e:
            logger.error(f"Error clearing L2 cache: {e}")
    
    async def _get_from_l3(self, key: str) -> Any:
        """Get from L3 Memcached cache"""
        try:
            if not self.l3_memcached:
                return None
            
            serialized_value = await self.l3_memcached.get(key.encode())
            if serialized_value:
                return self._deserialize(serialized_value)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting from L3 cache: {e}")
            return None
    
    async def _set_to_l3(self, key: str, value: Any, ttl: int):
        """Set to L3 Memcached cache"""
        try:
            if not self.l3_memcached:
                return
            
            serialized_value = self._serialize(value)
            await self.l3_memcached.set(key.encode(), serialized_value, ttl)
            
        except Exception as e:
            logger.error(f"Error setting to L3 cache: {e}")
    
    async def _delete_from_l3(self, key: str) -> bool:
        """Delete from L3 Memcached cache"""
        try:
            if not self.l3_memcached:
                return False
            
            result = await self.l3_memcached.delete(key.encode())
            return result
            
        except Exception as e:
            logger.error(f"Error deleting from L3 cache: {e}")
            return False
    
    async def _clear_l3(self):
        """Clear L3 Memcached cache"""
        try:
            if self.l3_memcached:
                await self.l3_memcached.flush_all()
                
        except Exception as e:
            logger.error(f"Error clearing L3 cache: {e}")
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value"""
        try:
            serializer = self.serializers.get(self.config.serialization_method)
            if serializer:
                return serializer(value)
            else:
                return json.dumps(value).encode('utf-8')
                
        except Exception as e:
            logger.error(f"Error serializing value: {e}")
            return json.dumps(str(value)).encode('utf-8')
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value"""
        try:
            deserializer = self.deserializers.get(self.config.serialization_method)
            if deserializer:
                return deserializer(data)
            else:
                return json.loads(data.decode('utf-8'))
                
        except Exception as e:
            logger.error(f"Error deserializing value: {e}")
            return data.decode('utf-8')
    
    def _serialize_json(self, value: Any) -> bytes:
        """Serialize using JSON"""
        return json.dumps(value, default=str).encode('utf-8')
    
    def _deserialize_json(self, data: bytes) -> Any:
        """Deserialize using JSON"""
        return json.loads(data.decode('utf-8'))
    
    def _serialize_pickle(self, value: Any) -> bytes:
        """Serialize using Pickle"""
        return pickle.dumps(value)
    
    def _deserialize_pickle(self, data: bytes) -> Any:
        """Deserialize using Pickle"""
        return pickle.loads(data)
    
    def _serialize_msgpack(self, value: Any) -> bytes:
        """Serialize using MessagePack"""
        try:
            import msgpack
            return msgpack.packb(value)
        except ImportError:
            return self._serialize_json(value)
    
    def _deserialize_msgpack(self, data: bytes) -> Any:
        """Deserialize using MessagePack"""
        try:
            import msgpack
            return msgpack.unpackb(data, raw=False)
        except ImportError:
            return self._deserialize_json(data)
    
    def _update_hit_rate(self):
        """Update hit rate statistics"""
        if self.stats.total_requests > 0:
            self.stats.hit_rate = self.stats.hits / self.stats.total_requests
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            # Update L1 cache statistics
            with self.l1_lock:
                self.stats.entries_count = len(self.l1_cache)
                self.stats.total_size_bytes = sum(
                    entry.size_bytes for entry in self.l1_cache.values()
                )
            
            # Get L2 Redis statistics
            l2_stats = {}
            if self.config.l2_enabled and self.l2_redis:
                try:
                    info = await self.l2_redis.info()
                    l2_stats = {
                        "used_memory": info.get("used_memory", 0),
                        "connected_clients": info.get("connected_clients", 0),
                        "keyspace_hits": info.get("keyspace_hits", 0),
                        "keyspace_misses": info.get("keyspace_misses", 0)
                    }
                except:
                    pass
            
            return {
                "l1_memory": {
                    "entries": self.stats.entries_count,
                    "max_size": self.config.l1_max_size,
                    "size_bytes": self.stats.total_size_bytes,
                    "hit_rate": self.stats.hit_rate
                },
                "l2_redis": {
                    "enabled": self.config.l2_enabled,
                    "connected": self.l2_redis is not None,
                    "stats": l2_stats
                },
                "l3_memcached": {
                    "enabled": self.config.l3_enabled,
                    "connected": self.l3_memcached is not None
                },
                "overall": {
                    "hits": self.stats.hits,
                    "misses": self.stats.misses,
                    "total_requests": self.stats.total_requests,
                    "hit_rate": self.stats.hit_rate,
                    "evictions": self.stats.evictions
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {}
    
    async def reset_statistics(self):
        """Reset cache statistics"""
        try:
            self.stats = CacheStatistics()
            self.stats.last_reset = datetime.now()
            logger.info("Cache statistics reset")
            
        except Exception as e:
            logger.error(f"Error resetting cache statistics: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for caching service"""
        try:
            # Test L1 cache
            test_key = "health_check_test"
            test_value = "test_value"
            await self.set(test_key, test_value, 10)
            retrieved_value = await self.get(test_key)
            l1_healthy = retrieved_value == test_value
            await self.delete(test_key)
            
            # Test L2 Redis
            l2_healthy = False
            if self.config.l2_enabled and self.l2_redis:
                try:
                    await self.l2_redis.ping()
                    l2_healthy = True
                except:
                    pass
            
            # Test L3 Memcached
            l3_healthy = False
            if self.config.l3_enabled and self.l3_memcached:
                try:
                    await self.l3_memcached.set(b"health_check", b"test", 1)
                    await self.l3_memcached.delete(b"health_check")
                    l3_healthy = True
                except:
                    pass
            
            return {
                "status": "healthy" if l1_healthy else "unhealthy",
                "l1_memory": l1_healthy,
                "l2_redis": l2_healthy,
                "l3_memcached": l3_healthy,
                "statistics": await self.get_statistics()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def close(self):
        """Close caching service"""
        try:
            if self.l2_redis:
                await self.l2_redis.close()
            
            if self.l3_memcached:
                await self.l3_memcached.close()
            
            logger.info("Caching service closed")
            
        except Exception as e:
            logger.error(f"Error closing caching service: {e}")


























