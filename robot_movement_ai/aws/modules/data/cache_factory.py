"""
Cache Factory
=============

Factory for creating cache adapters.
"""

import logging
import os
from typing import Optional
from aws.modules.ports.cache_port import CachePort
from aws.modules.adapters.cache_adapters import (
    RedisCacheAdapter,
    MemcachedCacheAdapter,
    InMemoryCacheAdapter
)

logger = logging.getLogger(__name__)


class CacheFactory:
    """Factory for creating cache adapters."""
    
    @staticmethod
    def create(
        adapter_type: str = "redis",
        redis_url: Optional[str] = None,
        memcached_servers: Optional[str] = None
    ) -> CachePort:
        """
        Create cache adapter.
        
        Args:
            adapter_type: Type of adapter (redis, memcached, memory)
            redis_url: Redis connection URL
            memcached_servers: Memcached servers
        
        Returns:
            Cache adapter instance
        """
        if adapter_type == "redis":
            url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
            return RedisCacheAdapter(redis_url=url)
        
        elif adapter_type == "memcached":
            servers = memcached_servers or os.getenv("MEMCACHED_SERVERS", "localhost:11211")
            return MemcachedCacheAdapter(servers=servers)
        
        elif adapter_type == "memory":
            return InMemoryCacheAdapter()
        
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}")
    
    @staticmethod
    def create_from_env() -> CachePort:
        """Create cache from environment variables."""
        adapter_type = os.getenv("CACHE_TYPE", "redis")
        
        redis_url = os.getenv("REDIS_URL")
        memcached_servers = os.getenv("MEMCACHED_SERVERS")
        
        return CacheFactory.create(
            adapter_type=adapter_type,
            redis_url=redis_url,
            memcached_servers=memcached_servers
        )















