"""
Ultra-Optimized Multi-Level Cache
High-performance caching with compression and intelligent eviction
"""

import asyncio
import time
import hashlib
from typing import Any, Optional, Dict, List
from dataclasses import dataclass
from collections import OrderedDict
import orjson
import zstandard as zstd
from loguru import logger


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    size: int = 0
    compressed: bool = False
    compressed_data: Optional[bytes] = None
    
    def __post_init__(self):
        """Calculate size after initialization"""
        if not self.size:
            self.size = self._calculate_size()
    
    def _calculate_size(self) -> int:
        """Calculate entry size in bytes"""
        try:
            if self.compressed and self.compressed_data:
                return len(self.compressed_data)
            else:
                return len(orjson.dumps(self.value))
        except Exception:
            return 0
    
    def access(self):
        """Record access"""
        self.access_count += 1
    
    def compress(self, level: int = 3):
        """Compress entry data"""
        if not self.compressed:
            try:
                data = orjson.dumps(self.value)
                compressor = zstd.ZstdCompressor(level=level)
                self.compressed_data = compressor.compress(data)
                self.compressed = True
                self.size = len(self.compressed_data)
            except Exception as e:
                logger.warning(f"Failed to compress cache entry: {e}")
    
    def decompress(self) -> Any:
        """Decompress entry data"""
        if self.compressed and self.compressed_data:
            try:
                decompressor = zstd.ZstdDecompressor()
                data = decompressor.decompress(self.compressed_data)
                return orjson.loads(data)
            except Exception as e:
                logger.error(f"Failed to decompress cache entry: {e}")
                return self.value
        return self.value


class LRUCache:
    """Ultra-optimized LRU cache with size tracking"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.current_memory = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            entry.access()
            self.cache.move_to_end(key)
            self.hits += 1
            return entry.decompress()
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        # Check if key already exists
        if key in self.cache:
            old_entry = self.cache[key]
            self.current_memory -= old_entry.size
        
        # Create new entry
        entry = CacheEntry(
            key=key,
            value=value,
            timestamp=time.time()
        )
        
        # Check memory limits
        if entry.size > self.max_memory_bytes:
            logger.warning(f"Entry too large for cache: {entry.size} bytes")
            return False
        
        # Evict if necessary
        while (len(self.cache) >= self.max_size or 
               self.current_memory + entry.size > self.max_memory_bytes):
            self._evict_lru()
        
        # Add entry
        self.cache[key] = entry
        self.current_memory += entry.size
        self.cache.move_to_end(key)
        
        return True
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        # Remove oldest entry
        key, entry = self.cache.popitem(last=False)
        self.current_memory -= entry.size
        self.evictions += 1
        
        logger.debug(f"Evicted cache entry: {key}")
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        if key in self.cache:
            entry = self.cache[key]
            self.current_memory -= entry.size
            del self.cache[key]
            return True
        return False
    
    def clear(self):
        """Clear all entries"""
        self.cache.clear()
        self.current_memory = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'memory_used_mb': self.current_memory / (1024 * 1024),
            'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'evictions': self.evictions
        }


class MultiLevelCache:
    """Ultra-optimized multi-level cache system"""
    
    def __init__(
        self,
        l1_cache: Optional[LRUCache] = None,
        l2_cache: Optional[LRUCache] = None,
        compression: bool = True,
        compression_level: int = 3,
        compression_threshold: int = 1024  # Compress entries larger than 1KB
    ):
        # Level 1: Fast in-memory cache (small, fast access)
        self.l1_cache = l1_cache or LRUCache(max_size=1000, max_memory_mb=50)
        
        # Level 2: Larger in-memory cache (larger, slightly slower)
        self.l2_cache = l2_cache or LRUCache(max_size=10000, max_memory_mb=500)
        
        # Compression settings
        self.compression = compression
        self.compression_level = compression_level
        self.compression_threshold = compression_threshold
        
        # Statistics
        self.l1_hits = 0
        self.l2_hits = 0
        self.total_requests = 0
        self.compression_ratio = 1.0
        
        # Background tasks
        self._compression_queue = asyncio.Queue()
        self._compression_task = None
        
        # Start compression worker
        if self.compression:
            self._start_compression_worker()
    
    def _start_compression_worker(self):
        """Start background compression worker"""
        async def compression_worker():
            while True:
                try:
                    entry = await asyncio.wait_for(
                        self._compression_queue.get(), 
                        timeout=1.0
                    )
                    
                    if entry.size > self.compression_threshold:
                        entry.compress(self.compression_level)
                        
                        # Update compression ratio
                        if entry.size > 0:
                            original_size = len(orjson.dumps(entry.value))
                            self.compression_ratio = entry.size / original_size
                    
                    self._compression_queue.task_done()
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Compression worker error: {e}")
        
        self._compression_task = asyncio.create_task(compression_worker())
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache"""
        self.total_requests += 1
        
        # Try L1 cache first
        value = self.l1_cache.get(key)
        if value is not None:
            self.l1_hits += 1
            return value
        
        # Try L2 cache
        value = self.l2_cache.get(key)
        if value is not None:
            self.l2_hits += 1
            # Promote to L1 cache
            self.l1_cache.set(key, value)
            return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in multi-level cache"""
        # Set in L1 cache
        l1_success = self.l1_cache.set(key, value, ttl)
        
        # Set in L2 cache
        l2_success = self.l2_cache.set(key, value, ttl)
        
        # Schedule compression if enabled
        if self.compression and l2_success:
            entry = self.l2_cache.cache.get(key)
            if entry and entry.size > self.compression_threshold:
                await self._compression_queue.put(entry)
        
        return l1_success or l2_success
    
    async def delete(self, key: str) -> bool:
        """Delete value from both cache levels"""
        l1_deleted = self.l1_cache.delete(key)
        l2_deleted = self.l2_cache.delete(key)
        return l1_deleted or l2_deleted
    
    async def clear(self):
        """Clear both cache levels"""
        self.l1_cache.clear()
        self.l2_cache.clear()
        self.l1_hits = 0
        self.l2_hits = 0
        self.total_requests = 0
        self.compression_ratio = 1.0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        l1_stats = self.l1_cache.get_stats()
        l2_stats = self.l2_cache.get_stats()
        
        total_hits = self.l1_hits + self.l2_hits
        overall_hit_rate = total_hits / self.total_requests if self.total_requests > 0 else 0
        
        return {
            'overall': {
                'total_requests': self.total_requests,
                'total_hits': total_hits,
                'hit_rate': overall_hit_rate,
                'compression_ratio': self.compression_ratio
            },
            'l1_cache': {
                **l1_stats,
                'hits': self.l1_hits
            },
            'l2_cache': {
                **l2_stats,
                'hits': self.l2_hits
            },
            'compression': {
                'enabled': self.compression,
                'level': self.compression_level,
                'threshold_bytes': self.compression_threshold
            }
        }
    
    async def warm_up(self, data: Dict[str, Any]):
        """Warm up cache with data"""
        logger.info(f"Warming up cache with {len(data)} entries")
        
        for key, value in data.items():
            await self.set(key, value)
        
        logger.info("Cache warm-up complete")
    
    async def prefetch(self, keys: List[str], fetch_func):
        """Prefetch keys using provided fetch function"""
        logger.info(f"Prefetching {len(keys)} keys")
        
        # Filter out keys already in cache
        missing_keys = []
        for key in keys:
            if await self.get(key) is None:
                missing_keys.append(key)
        
        if not missing_keys:
            logger.info("All keys already in cache")
            return
        
        # Fetch missing keys
        try:
            results = await fetch_func(missing_keys)
            for key, value in results.items():
                await self.set(key, value)
            
            logger.info(f"Prefetched {len(results)} keys")
        except Exception as e:
            logger.error(f"Prefetch failed: {e}")
    
    async def cleanup(self):
        """Clean up expired entries and optimize cache"""
        # Clean up L1 cache
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.l1_cache.cache.items():
            if hasattr(entry, 'ttl') and entry.ttl:
                if current_time - entry.timestamp > entry.ttl:
                    expired_keys.append(key)
        
        for key in expired_keys:
            self.l1_cache.delete(key)
        
        # Clean up L2 cache
        expired_keys = []
        for key, entry in self.l2_cache.cache.items():
            if hasattr(entry, 'ttl') and entry.ttl:
                if current_time - entry.timestamp > entry.ttl:
                    expired_keys.append(key)
        
        for key in expired_keys:
            self.l2_cache.delete(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired entries")
    
    async def shutdown(self):
        """Shutdown cache and cleanup resources"""
        if self._compression_task:
            self._compression_task.cancel()
            try:
                await self._compression_task
            except asyncio.CancelledError:
                pass
        
        await self.clear()
        logger.info("Multi-level cache shutdown complete") 