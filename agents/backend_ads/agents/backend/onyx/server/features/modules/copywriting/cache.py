"""
Copywriting Cache Module.

High-performance caching system for AI-powered copywriting with compression,
TTL management, and intelligent cache strategies.
"""

import asyncio
import time
import json
import hashlib
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
import structlog

from .config import CopywritingConfig
from .exceptions import CacheError
from .models import ContentRequest, GeneratedContent

logger = structlog.get_logger(__name__)

# Optional imports for enhanced caching
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False

try:
    import orjson
    ORJSON_AVAILABLE = True
except ImportError:
    ORJSON_AVAILABLE = False


class CacheEntry:
    """Cache entry with metadata and expiration."""
    
    def __init__(
        self,
        key: str,
        data: Any,
        ttl: int = 3600,
        compression: bool = True
    ):
        self.key = key
        self.data = data
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = self.created_at
        self.compressed = compression and self._should_compress()
        
        if self.compressed:
            self._compress_data()
    
    def _should_compress(self) -> bool:
        """Determine if data should be compressed."""
        if not LZ4_AVAILABLE:
            return False
        
        # Compress if data is large enough
        serialized_size = len(self._serialize(self.data))
        return serialized_size > 1024  # 1KB threshold
    
    def _compress_data(self):
        """Compress the data using LZ4."""
        try:
            serialized = self._serialize(self.data)
            self.data = lz4.frame.compress(serialized)
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            self.compressed = False
    
    def _decompress_data(self) -> Any:
        """Decompress and deserialize the data."""
        if not self.compressed:
            return self.data
        
        try:
            decompressed = lz4.frame.decompress(self.data)
            return self._deserialize(decompressed)
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            raise CacheError(f"Failed to decompress cache entry: {e}")
    
    def _serialize(self, data: Any) -> bytes:
        """Serialize data to bytes."""
        if ORJSON_AVAILABLE:
            return orjson.dumps(data, default=str)
        else:
            return json.dumps(data, default=str).encode('utf-8')
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to data."""
        if ORJSON_AVAILABLE:
            return orjson.loads(data)
        else:
            return json.loads(data.decode('utf-8'))
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.created_at > self.ttl
    
    def get_data(self) -> Any:
        """Get data with access tracking."""
        self.access_count += 1
        self.last_accessed = time.time()
        
        if self.compressed:
            return self._decompress_data()
        return self.data
    
    def get_age(self) -> float:
        """Get age of cache entry in seconds."""
        return time.time() - self.created_at
    
    def get_ttl_remaining(self) -> float:
        """Get remaining TTL in seconds."""
        return max(0, self.ttl - self.get_age())


class MemoryCache:
    """In-memory cache with LRU eviction and compression."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # Check expiration
            if entry.is_expired():
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return None
            
            # Update access order for LRU
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            return entry.get_data()
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        compression: bool = True
    ) -> bool:
        """Set value in cache."""
        async with self._lock:
            ttl = ttl or self.default_ttl
            
            # Create cache entry
            entry = CacheEntry(key, value, ttl, compression)
            
            # Remove old entry if exists
            if key in self._cache:
                if key in self._access_order:
                    self._access_order.remove(key)
            
            # Add new entry
            self._cache[key] = entry
            self._access_order.append(key)
            
            # Evict if necessary
            await self._evict_if_needed()
            
            return True
    
    async def delete(self, key: str) -> bool:
        """Remove key from cache."""
        async with self._lock:
            if key not in self._cache:
                return False
            
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            
            return True
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
            return True
    
    async def _evict_if_needed(self):
        """Evict least recently used entries if cache is full."""
        while len(self._cache) > self.max_size:
            if not self._access_order:
                break
            
            # Remove LRU entry
            lru_key = self._access_order.pop(0)
            if lru_key in self._cache:
                del self._cache[lru_key]
    
    async def cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        async with self._lock:
            expired_keys = []
            
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        compressed_entries = sum(1 for entry in self._cache.values() if entry.compressed)
        
        if total_entries > 0:
            avg_age = sum(entry.get_age() for entry in self._cache.values()) / total_entries
            avg_access_count = sum(entry.access_count for entry in self._cache.values()) / total_entries
        else:
            avg_age = 0
            avg_access_count = 0
        
        return {
            "total_entries": total_entries,
            "max_size": self.max_size,
            "compressed_entries": compressed_entries,
            "compression_ratio": compressed_entries / total_entries if total_entries > 0 else 0,
            "avg_age_seconds": avg_age,
            "avg_access_count": avg_access_count
        }


class RedisCache:
    """Redis-based cache with async support."""
    
    def __init__(
        self,
        redis_url: str,
        default_ttl: int = 3600,
        key_prefix: str = "copywriting:"
    ):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self._redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        if not REDIS_AVAILABLE:
            raise CacheError("Redis not available")
        
        try:
            self._redis = redis.from_url(self.redis_url)
            await self._redis.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            raise CacheError(f"Failed to connect to Redis: {e}")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._redis:
            await self._redis.close()
    
    def _make_key(self, key: str) -> str:
        """Create full Redis key with prefix."""
        return f"{self.key_prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self._redis:
            raise CacheError("Redis not connected")
        
        try:
            full_key = self._make_key(key)
            data = await self._redis.get(full_key)
            
            if data is None:
                return None
            
            # Deserialize data
            if ORJSON_AVAILABLE:
                return orjson.loads(data)
            else:
                return json.loads(data.decode('utf-8'))
        
        except Exception as e:
            logger.error(f"Redis get failed: {e}")
            raise CacheError(f"Failed to get from Redis: {e}")
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in Redis cache."""
        if not self._redis:
            raise CacheError("Redis not connected")
        
        try:
            full_key = self._make_key(key)
            ttl = ttl or self.default_ttl
            
            # Serialize data
            if ORJSON_AVAILABLE:
                data = orjson.dumps(value, default=str)
            else:
                data = json.dumps(value, default=str).encode('utf-8')
            
            await self._redis.setex(full_key, ttl, data)
            return True
        
        except Exception as e:
            logger.error(f"Redis set failed: {e}")
            raise CacheError(f"Failed to set in Redis: {e}")
    
    async def delete(self, key: str) -> bool:
        """Remove key from Redis cache."""
        if not self._redis:
            raise CacheError("Redis not connected")
        
        try:
            full_key = self._make_key(key)
            result = await self._redis.delete(full_key)
            return result > 0
        
        except Exception as e:
            logger.error(f"Redis delete failed: {e}")
            raise CacheError(f"Failed to delete from Redis: {e}")
    
    async def clear(self) -> bool:
        """Clear all cache entries with prefix."""
        if not self._redis:
            raise CacheError("Redis not connected")
        
        try:
            pattern = f"{self.key_prefix}*"
            keys = await self._redis.keys(pattern)
            
            if keys:
                await self._redis.delete(*keys)
            
            return True
        
        except Exception as e:
            logger.error(f"Redis clear failed: {e}")
            raise CacheError(f"Failed to clear Redis: {e}")


class CopywritingCache:
    """High-level cache manager for copywriting operations."""
    
    def __init__(self, config: CopywritingConfig):
        self.config = config
        self.memory_cache = MemoryCache(
            max_size=config.max_cache_size,
            default_ttl=config.cache_ttl
        )
        self.redis_cache: Optional[RedisCache] = None
        
        # Initialize Redis if URL provided
        if hasattr(config, 'redis_url') and config.redis_url:
            self.redis_cache = RedisCache(
                redis_url=config.redis_url,
                default_ttl=config.cache_ttl
            )
    
    async def initialize(self):
        """Initialize cache connections."""
        if self.redis_cache:
            try:
                await self.redis_cache.connect()
            except Exception as e:
                logger.warning(f"Redis cache initialization failed: {e}")
                self.redis_cache = None
    
    async def cleanup(self):
        """Cleanup cache connections."""
        if self.redis_cache:
            await self.redis_cache.disconnect()
    
    def _generate_cache_key(self, request: ContentRequest) -> str:
        """Generate deterministic cache key for content request."""
        # Create hash of request parameters
        request_dict = request.dict(exclude={'id'})
        request_json = json.dumps(request_dict, sort_keys=True)
        key_hash = hashlib.sha256(request_json.encode()).hexdigest()[:16]
        
        return f"content:{request.content_type}:{key_hash}"
    
    async def get_content(self, request: ContentRequest) -> Optional[GeneratedContent]:
        """Get cached generated content."""
        if not self.config.enable_caching:
            return None
        
        key = self._generate_cache_key(request)
        
        try:
            # Try Redis first if available
            if self.redis_cache:
                data = await self.redis_cache.get(key)
                if data:
                    return GeneratedContent(**data)
            
            # Fall back to memory cache
            data = await self.memory_cache.get(key)
            if data:
                return GeneratedContent(**data)
        
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        return None
    
    async def set_content(
        self,
        request: ContentRequest,
        content: GeneratedContent,
        ttl: Optional[int] = None
    ) -> bool:
        """Cache generated content."""
        if not self.config.enable_caching:
            return False
        
        key = self._generate_cache_key(request)
        data = content.dict()
        
        try:
            # Set in both caches
            if self.redis_cache:
                await self.redis_cache.set(key, data, ttl)
            
            await self.memory_cache.set(
                key, 
                data, 
                ttl, 
                compression=self.config.cache_compression
            )
            
            return True
        
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    async def invalidate_content(self, request: ContentRequest) -> bool:
        """Invalidate cached content for request."""
        key = self._generate_cache_key(request)
        
        try:
            if self.redis_cache:
                await self.redis_cache.delete(key)
            
            await self.memory_cache.delete(key)
            return True
        
        except Exception as e:
            logger.warning(f"Cache invalidation failed: {e}")
            return False
    
    async def clear_all(self) -> bool:
        """Clear all cached content."""
        try:
            if self.redis_cache:
                await self.redis_cache.clear()
            
            await self.memory_cache.clear()
            return True
        
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "memory_cache": self.memory_cache.get_stats(),
            "redis_cache": {"available": self.redis_cache is not None}
        }
        
        # Add Redis stats if available
        if self.redis_cache and self.redis_cache._redis:
            try:
                info = await self.redis_cache._redis.info()
                stats["redis_cache"]["info"] = {
                    "used_memory": info.get("used_memory", 0),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0)
                }
            except Exception as e:
                logger.warning(f"Failed to get Redis stats: {e}")
        
        return stats
    
    async def cleanup_expired(self) -> Dict[str, int]:
        """Cleanup expired entries from all caches."""
        memory_cleaned = await self.memory_cache.cleanup_expired()
        
        return {
            "memory_cache_cleaned": memory_cleaned,
            "redis_cache_cleaned": 0  # Redis handles expiration automatically
        }


# Export main components
__all__ = [
    "CopywritingCache",
    "MemoryCache",
    "RedisCache",
    "CacheEntry"
] 