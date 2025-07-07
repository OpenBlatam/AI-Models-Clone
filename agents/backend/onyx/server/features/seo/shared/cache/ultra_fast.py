"""
Ultra-Fast Cache System
Maximum performance caching with advanced optimizations
"""

import asyncio
import time
import hashlib
from typing import Any, Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from collections import OrderedDict
import orjson
import zstandard as zstd
import lz4.frame
from loguru import logger
import mmap
import os


@dataclass
class CacheEntry:
    """Ultra-optimized cache entry"""
    
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    size: int = 0
    compressed: bool = False
    compressed_data: Optional[bytes] = None
    compression_ratio: float = 1.0
    hash_value: str = ""
    
    def __post_init__(self):
        """Initialize entry with optimizations"""
        if not self.hash_value:
            self.hash_value = hashlib.blake2b(self.key.encode(), digest_size=16).hexdigest()
        
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
        """Record access with timestamp"""
        self.access_count += 1
    
    def compress(self, algorithm: str = "zstd", level: int = 3):
        """Compress entry data with multiple algorithms"""
        if not self.compressed:
            try:
                data = orjson.dumps(self.value)
                
                if algorithm == "zstd":
                    compressor = zstd.ZstdCompressor(level=level)
                    self.compressed_data = compressor.compress(data)
                elif algorithm == "lz4":
                    self.compressed_data = lz4.frame.compress(data, compression_level=level)
                else:
                    return
                
                self.compressed = True
                self.size = len(self.compressed_data)
                self.compression_ratio = len(data) / self.size if self.size > 0 else 1.0
                
            except Exception as e:
                logger.warning(f"Failed to compress cache entry: {e}")
    
    def decompress(self) -> Any:
        """Decompress entry data"""
        if self.compressed and self.compressed_data:
            try:
                # Try zstd first
                try:
                    decompressor = zstd.ZstdDecompressor()
                    data = decompressor.decompress(self.compressed_data)
                    return orjson.loads(data)
                except:
                    # Try LZ4
                    data = lz4.frame.decompress(self.compressed_data)
                    return orjson.loads(data)
            except Exception as e:
                logger.error(f"Failed to decompress cache entry: {e}")
                return self.value
        return self.value


class UltraFastLRUCache:
    """Ultra-optimized LRU cache with advanced features"""
    
    def __init__(self, max_size: int = 10000, max_memory_mb: int = 500):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.current_memory = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.compression_savings = 0
        
        # Performance tracking
        self.access_times: List[float] = []
        self.eviction_times: List[float] = []
        
        # Background tasks
        self._compression_task = None
        self._cleanup_task = None
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with ultra-fast access"""
        start_time = time.perf_counter()
        
        if key in self.cache:
            entry = self.cache[key]
            entry.access()
            self.cache.move_to_end(key)
            self.hits += 1
            
            access_time = time.perf_counter() - start_time
            self.access_times.append(access_time)
            
            return entry.decompress()
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            compress: bool = True, compression_algorithm: str = "zstd") -> bool:
        """Set value in cache with compression"""
        start_time = time.perf_counter()
        
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
        
        # Compress if enabled and entry is large enough
        if compress and entry.size > 1024:  # Compress entries > 1KB
            entry.compress(compression_algorithm)
            self.compression_savings += entry.size * (1 - entry.compression_ratio)
        
        # Add entry
        self.cache[key] = entry
        self.current_memory += entry.size
        self.cache.move_to_end(key)
        
        return True
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        start_time = time.perf_counter()
        
        # Remove oldest entry
        key, entry = self.cache.popitem(last=False)
        self.current_memory -= entry.size
        self.evictions += 1
        
        eviction_time = time.perf_counter() - start_time
        self.eviction_times.append(eviction_time)
        
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
        self.compression_savings = 0
        self.access_times.clear()
        self.eviction_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        avg_access_time = sum(self.access_times) / len(self.access_times) if self.access_times else 0
        avg_eviction_time = sum(self.eviction_times) / len(self.eviction_times) if self.eviction_times else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'memory_used_mb': self.current_memory / (1024 * 1024),
            'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'evictions': self.evictions,
            'compression_savings_mb': self.compression_savings / (1024 * 1024),
            'avg_access_time_ms': avg_access_time * 1000,
            'avg_eviction_time_ms': avg_eviction_time * 1000,
            'memory_efficiency': self.current_memory / self.max_memory_bytes if self.max_memory_bytes > 0 else 0
        }


class MemoryMappedCache:
    """Memory-mapped cache for ultra-fast disk storage"""
    
    def __init__(self, file_path: str, max_size_mb: int = 1000):
        self.file_path = file_path
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.file = None
        self.mmap = None
        self.index: Dict[str, Tuple[int, int]] = {}  # key -> (offset, size)
        
        self._initialize_file()
    
    def _initialize_file(self):
        """Initialize memory-mapped file"""
        try:
            # Create file if it doesn't exist
            if not os.path.exists(self.file_path):
                with open(self.file_path, 'wb') as f:
                    f.write(b'\x00' * self.max_size_bytes)
            
            # Open file for read/write
            self.file = open(self.file_path, 'r+b')
            self.mmap = mmap.mmap(self.file.fileno(), self.max_size_bytes)
            
        except Exception as e:
            logger.error(f"Failed to initialize memory-mapped cache: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from memory-mapped cache"""
        if key not in self.index:
            return None
        
        try:
            offset, size = self.index[key]
            data = self.mmap[offset:offset + size]
            
            # Decompress and deserialize
            decompressed = lz4.frame.decompress(data)
            return orjson.loads(decompressed)
            
        except Exception as e:
            logger.error(f"Failed to read from memory-mapped cache: {e}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """Set value in memory-mapped cache"""
        try:
            # Serialize and compress
            data = orjson.dumps(value)
            compressed = lz4.frame.compress(data)
            
            # Find available space
            offset = self._find_space(len(compressed))
            if offset is None:
                return False
            
            # Write data
            self.mmap[offset:offset + len(compressed)] = compressed
            self.index[key] = (offset, len(compressed))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write to memory-mapped cache: {e}")
            return False
    
    def _find_space(self, size: int) -> Optional[int]:
        """Find available space in memory-mapped file"""
        # Simple first-fit allocation
        current_offset = 0
        
        for key, (offset, entry_size) in sorted(self.index.items(), key=lambda x: x[1][0]):
            if offset - current_offset >= size:
                return current_offset
            current_offset = offset + entry_size
        
        # Check if there's space at the end
        if self.max_size_bytes - current_offset >= size:
            return current_offset
        
        return None
    
    def close(self):
        """Close memory-mapped cache"""
        if self.mmap:
            self.mmap.close()
        if self.file:
            self.file.close()


class UltraFastMultiLevelCache:
    """Ultra-optimized multi-level cache system"""
    
    def __init__(
        self,
        l1_cache: Optional[UltraFastLRUCache] = None,
        l2_cache: Optional[UltraFastLRUCache] = None,
        mmap_cache: Optional[MemoryMappedCache] = None,
        compression: bool = True,
        compression_algorithm: str = "zstd",
        compression_threshold: int = 512,  # Compress entries larger than 512 bytes
        async_compression: bool = True
    ):
        # Level 1: Ultra-fast in-memory cache (small, fast access)
        self.l1_cache = l1_cache or UltraFastLRUCache(max_size=5000, max_memory_mb=100)
        
        # Level 2: Larger in-memory cache (larger, slightly slower)
        self.l2_cache = l2_cache or UltraFastLRUCache(max_size=50000, max_memory_mb=1000)
        
        # Level 3: Memory-mapped disk cache (largest, slower but persistent)
        self.mmap_cache = mmap_cache
        
        # Compression settings
        self.compression = compression
        self.compression_algorithm = compression_algorithm
        self.compression_threshold = compression_threshold
        self.async_compression = async_compression
        
        # Statistics
        self.l1_hits = 0
        self.l2_hits = 0
        self.mmap_hits = 0
        self.total_requests = 0
        self.compression_ratio = 1.0
        
        # Background tasks
        self._compression_queue = asyncio.Queue()
        self._compression_task = None
        
        # Start compression worker
        if self.async_compression:
            self._start_compression_worker()
    
    def _start_compression_worker(self):
        """Start background compression worker"""
        async def compression_worker():
            while True:
                try:
                    entry = await asyncio.wait_for(
                        self._compression_queue.get(), 
                        timeout=0.1
                    )
                    
                    if entry.size > self.compression_threshold:
                        entry.compress(self.compression_algorithm)
                        
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
        """Get value from multi-level cache with ultra-fast access"""
        self.total_requests += 1
        
        # Try L1 cache first (fastest)
        value = self.l1_cache.get(key)
        if value is not None:
            self.l1_hits += 1
            return value
        
        # Try L2 cache
        value = self.l2_cache.get(key)
        if value is not None:
            self.l2_hits += 1
            # Promote to L1 cache
            self.l1_cache.set(key, value, compress=False)
            return value
        
        # Try memory-mapped cache
        if self.mmap_cache:
            value = self.mmap_cache.get(key)
            if value is not None:
                self.mmap_hits += 1
                # Promote to L2 cache
                self.l2_cache.set(key, value, compress=False)
                return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in multi-level cache with intelligent placement"""
        # Set in L1 cache
        l1_success = self.l1_cache.set(key, value, compress=False)
        
        # Set in L2 cache with compression
        l2_success = self.l2_cache.set(
            key, value, 
            compress=self.compression,
            compression_algorithm=self.compression_algorithm
        )
        
        # Set in memory-mapped cache if available
        mmap_success = True
        if self.mmap_cache:
            mmap_success = self.mmap_cache.set(key, value)
        
        # Schedule async compression for L1 if enabled
        if self.async_compression and l1_success:
            entry = self.l1_cache.cache.get(key)
            if entry and entry.size > self.compression_threshold:
                await self._compression_queue.put(entry)
        
        return l1_success or l2_success or mmap_success
    
    async def delete(self, key: str) -> bool:
        """Delete value from all cache levels"""
        l1_deleted = self.l1_cache.delete(key)
        l2_deleted = self.l2_cache.delete(key)
        mmap_deleted = self.mmap_cache.delete(key) if self.mmap_cache else False
        
        return l1_deleted or l2_deleted or mmap_deleted
    
    async def clear(self):
        """Clear all cache levels"""
        self.l1_cache.clear()
        self.l2_cache.clear()
        if self.mmap_cache:
            # Clear memory-mapped cache by recreating file
            self.mmap_cache.close()
            os.remove(self.mmap_cache.file_path)
            self.mmap_cache = MemoryMappedCache(self.mmap_cache.file_path)
        
        self.l1_hits = 0
        self.l2_hits = 0
        self.mmap_hits = 0
        self.total_requests = 0
        self.compression_ratio = 1.0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive multi-level cache statistics"""
        l1_stats = self.l1_cache.get_stats()
        l2_stats = self.l2_cache.get_stats()
        
        total_hits = self.l1_hits + self.l2_hits + self.mmap_hits
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
            'mmap_cache': {
                'hits': self.mmap_hits,
                'enabled': self.mmap_cache is not None
            },
            'compression': {
                'enabled': self.compression,
                'algorithm': self.compression_algorithm,
                'threshold_bytes': self.compression_threshold,
                'async_enabled': self.async_compression
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
        
        if self.mmap_cache:
            self.mmap_cache.close()
        
        await self.clear()
        logger.info("Ultra-fast multi-level cache shutdown complete") 