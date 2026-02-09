"""
Caching utilities following functional patterns
"""
from typing import Any, Optional, Dict, List, Callable
from datetime import datetime, timedelta
import asyncio
import json
import hashlib
from functools import wraps


class MemoryCache:
    """Simple in-memory cache implementation."""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
    
    def _is_expired(self, item: Dict[str, Any]) -> bool:
        """Check if cache item is expired."""
        if 'expires_at' not in item:
            return True
        return datetime.utcnow() > item['expires_at']
    
    def _clean_expired(self) -> None:
        """Remove expired items from cache."""
        expired_keys = [
            key for key, item in self._cache.items()
            if self._is_expired(item)
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        self._clean_expired()
        
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        if self._is_expired(item):
            del self._cache[key]
            return None
        
        return item['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ttl = ttl or self._default_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.utcnow()
        }
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()
    
    def keys(self) -> List[str]:
        """Get all cache keys."""
        self._clean_expired()
        return list(self._cache.keys())
    
    def size(self) -> int:
        """Get cache size."""
        self._clean_expired()
        return len(self._cache)


# Global cache instance
_cache = MemoryCache()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = _cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            _cache.set(key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = _cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache.set(key, result, ttl)
            
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def cache_invalidate(pattern: str) -> None:
    """Invalidate cache entries matching pattern."""
    keys_to_delete = [key for key in _cache.keys() if pattern in key]
    for key in keys_to_delete:
        _cache.delete(key)


def cache_clear() -> None:
    """Clear all cache."""
    _cache.clear()


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return {
        "size": _cache.size(),
        "keys": _cache.keys()
    }


# Cache utilities for specific use cases
def cache_user_data(user_id: str, data: Any, ttl: int = 600) -> None:
    """Cache user-specific data."""
    key = f"user:{user_id}"
    _cache.set(key, data, ttl)


def get_cached_user_data(user_id: str) -> Optional[Any]:
    """Get cached user data."""
    key = f"user:{user_id}"
    return _cache.get(key)


def cache_document_data(document_id: str, data: Any, ttl: int = 300) -> None:
    """Cache document-specific data."""
    key = f"document:{document_id}"
    _cache.set(key, data, ttl)


def get_cached_document_data(document_id: str) -> Optional[Any]:
    """Get cached document data."""
    key = f"document:{document_id}"
    return _cache.get(key)


def cache_ai_response(prompt_hash: str, response: Any, ttl: int = 3600) -> None:
    """Cache AI response."""
    key = f"ai:{prompt_hash}"
    _cache.set(key, response, ttl)


def get_cached_ai_response(prompt_hash: str) -> Optional[Any]:
    """Get cached AI response."""
    key = f"ai:{prompt_hash}"
    return _cache.get(key)


def cache_organization_data(org_id: str, data: Any, ttl: int = 1800) -> None:
    """Cache organization-specific data."""
    key = f"org:{org_id}"
    _cache.set(key, data, ttl)


def get_cached_organization_data(org_id: str) -> Optional[Any]:
    """Get cached organization data."""
    key = f"org:{org_id}"
    return _cache.get(key)


def cache_collaboration_data(document_id: str, data: Any, ttl: int = 60) -> None:
    """Cache collaboration data (short TTL for real-time updates)."""
    key = f"collab:{document_id}"
    _cache.set(key, data, ttl)


def get_cached_collaboration_data(document_id: str) -> Optional[Any]:
    """Get cached collaboration data."""
    key = f"collab:{document_id}"
    return _cache.get(key)


def cache_search_results(query_hash: str, results: Any, ttl: int = 300) -> None:
    """Cache search results."""
    key = f"search:{query_hash}"
    _cache.set(key, results, ttl)


def get_cached_search_results(query_hash: str) -> Optional[Any]:
    """Get cached search results."""
    key = f"search:{query_hash}"
    return _cache.get(key)


def cache_api_response(endpoint: str, params_hash: str, response: Any, ttl: int = 300) -> None:
    """Cache API response."""
    key = f"api:{endpoint}:{params_hash}"
    _cache.set(key, response, ttl)


def get_cached_api_response(endpoint: str, params_hash: str) -> Optional[Any]:
    """Get cached API response."""
    key = f"api:{endpoint}:{params_hash}"
    return _cache.get(key)


def invalidate_user_cache(user_id: str) -> None:
    """Invalidate all cache for a user."""
    cache_invalidate(f"user:{user_id}")


def invalidate_document_cache(document_id: str) -> None:
    """Invalidate all cache for a document."""
    cache_invalidate(f"document:{document_id}")
    cache_invalidate(f"collab:{document_id}")


def invalidate_organization_cache(org_id: str) -> None:
    """Invalidate all cache for an organization."""
    cache_invalidate(f"org:{org_id}")


def invalidate_ai_cache() -> None:
    """Invalidate all AI-related cache."""
    cache_invalidate("ai:")


def invalidate_search_cache() -> None:
    """Invalidate all search-related cache."""
    cache_invalidate("search:")


def invalidate_api_cache(endpoint: str) -> None:
    """Invalidate cache for specific API endpoint."""
    cache_invalidate(f"api:{endpoint}")


# Cache warming utilities
async def warm_user_cache(user_id: str, user_data: Any) -> None:
    """Warm user cache with data."""
    cache_user_data(user_id, user_data)


async def warm_document_cache(document_id: str, document_data: Any) -> None:
    """Warm document cache with data."""
    cache_document_data(document_id, document_data)


async def warm_organization_cache(org_id: str, org_data: Any) -> None:
    """Warm organization cache with data."""
    cache_organization_data(org_id, org_data)


# Cache monitoring
def get_cache_hit_rate() -> Dict[str, Any]:
    """Get cache hit rate statistics."""
    # This would need to be implemented with proper tracking
    return {
        "hits": 0,
        "misses": 0,
        "hit_rate": 0.0
    }


def reset_cache_stats() -> None:
    """Reset cache statistics."""
    # This would need to be implemented with proper tracking
    pass




