"""
Memory Cache - Modular caching component
Implements in-memory caching with configurable strategies
"""

import asyncio
import time
from collections import defaultdict, deque
from typing import Any, Dict, Optional

from ..core.interfaces import BaseCache
from ..core.component_registry import component_registry


class MemoryCache(BaseCache):
    """Modular in-memory cache with configurable strategies."""

    def __init__(self, name: str = "memory_cache", version: str = "2.0.0"):
        super().__init__(name, version)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_order: deque = deque()
        self._lock = asyncio.Lock()
        self._last_cleanup = time.time()

        # Configuration
        self._config = {
            "max_size": 1000,
            "ttl": 3600,  # 1 hour default
            "cleanup_interval": 300,  # 5 minutes
            "strategy": "lru",  # lru, lfu, ttl
            "enable_compression": False,
            "compression_threshold": 1024,
        }

    async def initialize(self) -> bool:
        """Initialize the memory cache."""
        try:
            # Register with component registry
            component_registry.register(self, "cache")

            # Start background cleanup task
            asyncio.create_task(self._background_cleanup())

            self._health_status = True
            return True

        except Exception as e:
            print(f"Failed to initialize memory cache: {e}")
            self._health_status = False
            return False

    async def shutdown(self) -> bool:
        """Shutdown the memory cache."""
        try:
            # Unregister from component registry
            component_registry.unregister(self.name)

            # Clear cache
            await self.clear()

            self._health_status = False
            return True

        except Exception as e:
            print(f"Failed to shutdown memory cache: {e}")
            return False

    async def health_check(self) -> bool:
        """Check cache health."""
        return self._health_status and self._enabled

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key not in self._cache:
                self._update_stats("misses")
                return None

            entry = self._cache[key]

            # Check TTL
            if entry.get("ttl") and time.time() > entry["timestamp"] + entry["ttl"]:
                await self.delete(key)
                self._update_stats("expired")
                return None

            # Update access order for LRU
            if self._config["strategy"] == "lru":
                self._access_order.remove(key)
                self._access_order.append(key)

            # Update access count for LFU
            if self._config["strategy"] == "lfu":
                entry["access_count"] = entry.get("access_count", 0) + 1

            self._update_stats("hits")
            return entry["value"]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        async with self._lock:
            # Remove existing entry
            if key in self._cache:
                self._access_order.remove(key)

            # Create entry
            entry = {"value": value, "timestamp": time.time(), "ttl": ttl or self._config["ttl"], "access_count": 0}

            # Apply compression if enabled
            if self._config["enable_compression"] and len(str(value)) > self._config["compression_threshold"]:
                entry["value"] = self._compress_value(value)
                entry["compressed"] = True

            self._cache[key] = entry
            self._access_order.append(key)

            # Update size stat
            self._cache_stats["size"] = len(self._cache)

            # Evict if necessary
            if len(self._cache) > self._config["max_size"]:
                await self._evict_oldest()

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)

                self._update_stats("deletes")
                self._cache_stats["size"] = len(self._cache)
                return True
            return False

    async def clear(self) -> None:
        """Clear all cached data."""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self._cache_stats["size"] = 0
            self._update_stats("clears")

    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        async with self._lock:
            stats = self.get_cache_stats().copy()

            # Add additional stats
            stats.update(
                {
                    "current_size": len(self._cache),
                    "max_size": self._config["max_size"],
                    "strategy": self._config["strategy"],
                    "ttl": self._config["ttl"],
                    "cleanup_interval": self._config["cleanup_interval"],
                }
            )

            # Calculate hit rate
            total_requests = stats["hits"] + stats["misses"]
            if total_requests > 0:
                stats["hit_rate"] = (stats["hits"] / total_requests) * 100
            else:
                stats["hit_rate"] = 0.0

            return stats

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the cache."""
        self._config.update(config)

    async def _evict_oldest(self) -> None:
        """Evict oldest entry based on strategy."""
        if not self._cache:
            return

        if self._config["strategy"] == "lru":
            # Remove least recently used
            oldest_key = self._access_order.popleft()
        elif self._config["strategy"] == "lfu":
            # Remove least frequently used
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].get("access_count", 0))
        else:
            # Default to LRU
            oldest_key = self._access_order.popleft()

        del self._cache[oldest_key]
        self._update_stats("evictions")
        self._cache_stats["size"] = len(self._cache)

    async def _background_cleanup(self) -> None:
        """Background task for cleaning up expired entries."""
        while self._health_status:
            try:
                await asyncio.sleep(self._config["cleanup_interval"])
                await self._cleanup_expired()
            except Exception as e:
                print(f"Background cleanup error: {e}")
                await asyncio.sleep(10)  # Wait before retrying

    async def _cleanup_expired(self) -> None:
        """Clean up expired cache entries."""
        async with self._lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, entry in self._cache.items()
                if entry.get("ttl") and current_time > entry["timestamp"] + entry["ttl"]
            ]

            for key in expired_keys:
                await self.delete(key)

    def _compress_value(self, value: Any) -> Any:
        """Compress value if compression is enabled."""
        # Simple compression implementation
        if isinstance(value, str):
            return value.encode("utf-8")
        return value

    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "type": "memory_cache",
            "configuration": self._config.copy(),
            "current_stats": self._cache_stats.copy(),
        }
