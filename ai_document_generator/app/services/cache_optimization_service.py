"""
Cache optimization service following functional patterns
"""
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
import uuid
import asyncio
import time
import json
import hashlib
import pickle
import weakref
from collections import defaultdict, deque, OrderedDict
import threading
import psutil

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error
from app.models.cache import CacheEntry, CacheStats, CachePolicy
from app.schemas.cache import (
    CacheEntryResponse, CacheStatsResponse, CachePolicyResponse,
    CacheOptimizationRequest, CacheOptimizationResponse,
    CacheAnalysisResponse, CachePerformanceResponse
)
from app.utils.validators import validate_cache_key, validate_cache_ttl
from app.utils.helpers import generate_cache_key, calculate_cache_hit_rate
from app.utils.cache import cache_data, get_cached_data, invalidate_cache

logger = get_logger(__name__)

# Global cache storage
_cache_storage: Dict[str, Any] = {}
_cache_metadata: Dict[str, Dict[str, Any]] = {}
_cache_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
    "hits": 0,
    "misses": 0,
    "sets": 0,
    "deletes": 0,
    "evictions": 0,
    "last_access": None
})

# Cache policies
_cache_policies: Dict[str, Dict[str, Any]] = {
    "default": {
        "max_size": 1000,
        "ttl_seconds": 300,
        "eviction_policy": "lru",
        "compression": False,
        "serialization": "json"
    },
    "high_performance": {
        "max_size": 5000,
        "ttl_seconds": 600,
        "eviction_policy": "lfu",
        "compression": True,
        "serialization": "pickle"
    },
    "memory_efficient": {
        "max_size": 500,
        "ttl_seconds": 180,
        "eviction_policy": "lru",
        "compression": True,
        "serialization": "json"
    }
}


class LRUCache:
    """LRU Cache implementation."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value
                return value
            return None
    
    def set(self, key: str, value: Any) -> None:
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # Remove least recently used
                self.cache.popitem(last=False)
            
            self.cache[key] = value
    
    def delete(self, key: str) -> bool:
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        with self.lock:
            return len(self.cache)


class LFUCache:
    """LFU Cache implementation."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
        self.freq = defaultdict(int)
        self.freq_groups = defaultdict(OrderedDict)
        self.min_freq = 0
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None
            
            # Update frequency
            old_freq = self.freq[key]
            self.freq[key] = old_freq + 1
            
            # Move to new frequency group
            del self.freq_groups[old_freq][key]
            if not self.freq_groups[old_freq] and old_freq == self.min_freq:
                self.min_freq += 1
            
            self.freq_groups[old_freq + 1][key] = self.cache[key]
            return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache[key] = value
                self.get(key)  # Update frequency
                return
            
            if len(self.cache) >= self.max_size:
                # Remove least frequently used
                lfu_key, _ = self.freq_groups[self.min_freq].popitem(last=False)
                del self.cache[lfu_key]
                del self.freq[lfu_key]
            
            # Add new entry
            self.cache[key] = value
            self.freq[key] = 1
            self.freq_groups[1][key] = value
            self.min_freq = 1
    
    def delete(self, key: str) -> bool:
        with self.lock:
            if key not in self.cache:
                return False
            
            freq = self.freq[key]
            del self.cache[key]
            del self.freq[key]
            del self.freq_groups[freq][key]
            
            if not self.freq_groups[freq] and freq == self.min_freq:
                self.min_freq += 1
            
            return True
    
    def clear(self) -> None:
        with self.lock:
            self.cache.clear()
            self.freq.clear()
            self.freq_groups.clear()
            self.min_freq = 0
    
    def size(self) -> int:
        with self.lock:
            return len(self.cache)


class DistributedCache:
    """Distributed cache implementation."""
    
    def __init__(self, nodes: List[str], policy: str = "default"):
        self.nodes = nodes
        self.policy = _cache_policies.get(policy, _cache_policies["default"])
        self.local_cache = self._create_local_cache()
        self.node_hashes = [hashlib.md5(node.encode()).hexdigest() for node in nodes]
    
    def _create_local_cache(self):
        eviction_policy = self.policy["eviction_policy"]
        max_size = self.policy["max_size"]
        
        if eviction_policy == "lru":
            return LRUCache(max_size)
        elif eviction_policy == "lfu":
            return LFUCache(max_size)
        else:
            return LRUCache(max_size)
    
    def _get_node(self, key: str) -> str:
        """Get the node responsible for a key using consistent hashing."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        
        for i, node_hash in enumerate(self.node_hashes):
            if key_hash <= node_hash:
                return self.nodes[i]
        
        return self.nodes[0]  # Wrap around
    
    def get(self, key: str) -> Optional[Any]:
        # For now, use local cache only
        # In a real implementation, this would communicate with distributed nodes
        return self.local_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        # For now, use local cache only
        # In a real implementation, this would communicate with distributed nodes
        self.local_cache.set(key, value)
    
    def delete(self, key: str) -> bool:
        # For now, use local cache only
        # In a real implementation, this would communicate with distributed nodes
        return self.local_cache.delete(key)
    
    def clear(self) -> None:
        self.local_cache.clear()


# Global cache instances
_cache_instances: Dict[str, Union[LRUCache, LFUCache, DistributedCache]] = {}


def get_cache_instance(
    cache_name: str = "default",
    policy: str = "default"
) -> Union[LRUCache, LFUCache, DistributedCache]:
    """Get or create cache instance."""
    if cache_name not in _cache_instances:
        cache_policy = _cache_policies.get(policy, _cache_policies["default"])
        eviction_policy = cache_policy["eviction_policy"]
        max_size = cache_policy["max_size"]
        
        if eviction_policy == "lru":
            _cache_instances[cache_name] = LRUCache(max_size)
        elif eviction_policy == "lfu":
            _cache_instances[cache_name] = LFUCache(max_size)
        else:
            _cache_instances[cache_name] = LRUCache(max_size)
    
    return _cache_instances[cache_name]


def cache_optimized(
    cache_name: str = "default",
    ttl_seconds: int = 300,
    key_func: Optional[Callable] = None,
    policy: str = "default"
) -> Callable:
    """Optimized cache decorator."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Get cache instance
            cache = get_cache_instance(cache_name, policy)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                # Update stats
                _cache_stats[cache_name]["hits"] += 1
                _cache_stats[cache_name]["last_access"] = datetime.utcnow()
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Cache miss - execute function
            _cache_stats[cache_name]["misses"] += 1
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result)
            _cache_stats[cache_name]["sets"] += 1
            
            logger.debug(f"Cache miss: {cache_key}")
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Get cache instance
            cache = get_cache_instance(cache_name, policy)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                # Update stats
                _cache_stats[cache_name]["hits"] += 1
                _cache_stats[cache_name]["last_access"] = datetime.utcnow()
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Cache miss - execute function
            _cache_stats[cache_name]["misses"] += 1
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result)
            _cache_stats[cache_name]["sets"] += 1
            
            logger.debug(f"Cache miss: {cache_key}")
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


async def get_cache_stats(
    cache_name: Optional[str] = None
) -> Dict[str, CacheStatsResponse]:
    """Get cache statistics."""
    try:
        stats = {}
        
        if cache_name:
            cache_names = [cache_name]
        else:
            cache_names = list(_cache_stats.keys())
        
        for name in cache_names:
            if name in _cache_stats:
                cache_stats = _cache_stats[name]
                cache_instance = _cache_instances.get(name)
                
                hits = cache_stats["hits"]
                misses = cache_stats["misses"]
                total_requests = hits + misses
                hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0
                
                stats[name] = CacheStatsResponse(
                    cache_name=name,
                    hits=hits,
                    misses=misses,
                    hit_rate=round(hit_rate, 2),
                    sets=cache_stats["sets"],
                    deletes=cache_stats["deletes"],
                    evictions=cache_stats["evictions"],
                    size=cache_instance.size() if cache_instance else 0,
                    max_size=_cache_policies.get(name, _cache_policies["default"])["max_size"],
                    last_access=cache_stats["last_access"],
                    memory_usage_mb=0  # Would be calculated from actual memory usage
                )
        
        return stats
    
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {}


async def optimize_cache_performance(
    optimization_request: CacheOptimizationRequest,
    db: AsyncSession
) -> CacheOptimizationResponse:
    """Optimize cache performance."""
    try:
        optimizations = []
        
        # Analyze cache performance
        cache_analysis = await analyze_cache_performance()
        
        # Optimize cache policies
        if optimization_request.optimize_policies:
            policy_optimizations = await optimize_cache_policies(cache_analysis)
            optimizations.extend(policy_optimizations)
        
        # Optimize cache eviction
        if optimization_request.optimize_eviction:
            eviction_optimizations = await optimize_cache_eviction(cache_analysis)
            optimizations.extend(eviction_optimizations)
        
        # Optimize cache compression
        if optimization_request.optimize_compression:
            compression_optimizations = await optimize_cache_compression(cache_analysis)
            optimizations.extend(compression_optimizations)
        
        # Clean up unused caches
        if optimization_request.cleanup_unused:
            cleanup_optimizations = await cleanup_unused_caches()
            optimizations.extend(cleanup_optimizations)
        
        return CacheOptimizationResponse(
            optimizations=optimizations,
            total_optimizations=len(optimizations),
            cache_analysis=cache_analysis,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to optimize cache performance: {e}")
        raise handle_internal_error(f"Failed to optimize cache performance: {str(e)}")


async def analyze_cache_performance() -> CacheAnalysisResponse:
    """Analyze cache performance."""
    try:
        # Get cache statistics
        cache_stats = await get_cache_stats()
        
        # Calculate overall performance metrics
        total_hits = sum(stats.hits for stats in cache_stats.values())
        total_misses = sum(stats.misses for stats in cache_stats.values())
        total_requests = total_hits + total_misses
        overall_hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        # Analyze cache efficiency
        cache_efficiency = {}
        for cache_name, stats in cache_stats.items():
            efficiency_score = 0
            
            # Hit rate score (0-40 points)
            if stats.hit_rate >= 90:
                efficiency_score += 40
            elif stats.hit_rate >= 80:
                efficiency_score += 30
            elif stats.hit_rate >= 70:
                efficiency_score += 20
            elif stats.hit_rate >= 60:
                efficiency_score += 10
            
            # Size utilization score (0-30 points)
            size_utilization = (stats.size / stats.max_size * 100) if stats.max_size > 0 else 0
            if 70 <= size_utilization <= 90:
                efficiency_score += 30
            elif 50 <= size_utilization <= 95:
                efficiency_score += 20
            elif size_utilization >= 30:
                efficiency_score += 10
            
            # Memory efficiency score (0-30 points)
            if stats.memory_usage_mb < 100:
                efficiency_score += 30
            elif stats.memory_usage_mb < 500:
                efficiency_score += 20
            elif stats.memory_usage_mb < 1000:
                efficiency_score += 10
            
            cache_efficiency[cache_name] = {
                "score": efficiency_score,
                "hit_rate": stats.hit_rate,
                "size_utilization": size_utilization,
                "memory_usage_mb": stats.memory_usage_mb
            }
        
        # Identify performance issues
        performance_issues = []
        
        if overall_hit_rate < 70:
            performance_issues.append("Low overall cache hit rate")
        
        for cache_name, efficiency in cache_efficiency.items():
            if efficiency["score"] < 50:
                performance_issues.append(f"Poor efficiency in cache '{cache_name}'")
            
            if efficiency["hit_rate"] < 60:
                performance_issues.append(f"Low hit rate in cache '{cache_name}'")
            
            if efficiency["size_utilization"] > 95:
                performance_issues.append(f"Cache '{cache_name}' is nearly full")
        
        return CacheAnalysisResponse(
            overall_hit_rate=round(overall_hit_rate, 2),
            total_caches=len(cache_stats),
            total_requests=total_requests,
            cache_efficiency=cache_efficiency,
            performance_issues=performance_issues,
            analyzed_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to analyze cache performance: {e}")
        raise handle_internal_error(f"Failed to analyze cache performance: {str(e)}")


async def optimize_cache_policies(
    cache_analysis: CacheAnalysisResponse
) -> List[Dict[str, Any]]:
    """Optimize cache policies based on analysis."""
    try:
        optimizations = []
        
        for cache_name, efficiency in cache_analysis.cache_efficiency.items():
            if efficiency["score"] < 50:
                # Low efficiency - optimize policy
                current_policy = _cache_policies.get(cache_name, _cache_policies["default"])
                
                if efficiency["hit_rate"] < 60:
                    # Low hit rate - increase TTL and size
                    new_policy = current_policy.copy()
                    new_policy["ttl_seconds"] = min(current_policy["ttl_seconds"] * 2, 3600)
                    new_policy["max_size"] = min(current_policy["max_size"] * 2, 10000)
                    
                    _cache_policies[cache_name] = new_policy
                    
                    optimizations.append({
                        "type": "policy_optimization",
                        "cache_name": cache_name,
                        "changes": {
                            "ttl_seconds": new_policy["ttl_seconds"],
                            "max_size": new_policy["max_size"]
                        },
                        "reason": "Low hit rate detected"
                    })
                
                elif efficiency["size_utilization"] > 95:
                    # High utilization - increase size
                    new_policy = current_policy.copy()
                    new_policy["max_size"] = min(current_policy["max_size"] * 2, 10000)
                    
                    _cache_policies[cache_name] = new_policy
                    
                    optimizations.append({
                        "type": "policy_optimization",
                        "cache_name": cache_name,
                        "changes": {
                            "max_size": new_policy["max_size"]
                        },
                        "reason": "High size utilization detected"
                    })
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to optimize cache policies: {e}")
        return []


async def optimize_cache_eviction(
    cache_analysis: CacheAnalysisResponse
) -> List[Dict[str, Any]]:
    """Optimize cache eviction policies."""
    try:
        optimizations = []
        
        for cache_name, efficiency in cache_analysis.cache_efficiency.items():
            current_policy = _cache_policies.get(cache_name, _cache_policies["default"])
            current_eviction = current_policy["eviction_policy"]
            
            # Optimize eviction policy based on access patterns
            if efficiency["hit_rate"] < 70 and current_eviction == "lru":
                # Switch to LFU for better hit rate
                new_policy = current_policy.copy()
                new_policy["eviction_policy"] = "lfu"
                
                _cache_policies[cache_name] = new_policy
                
                # Recreate cache instance with new policy
                if cache_name in _cache_instances:
                    del _cache_instances[cache_name]
                
                optimizations.append({
                    "type": "eviction_optimization",
                    "cache_name": cache_name,
                    "changes": {
                        "eviction_policy": "lfu"
                    },
                    "reason": "Switched to LFU for better hit rate"
                })
            
            elif efficiency["hit_rate"] > 90 and current_eviction == "lfu":
                # Switch to LRU for better memory efficiency
                new_policy = current_policy.copy()
                new_policy["eviction_policy"] = "lru"
                
                _cache_policies[cache_name] = new_policy
                
                # Recreate cache instance with new policy
                if cache_name in _cache_instances:
                    del _cache_instances[cache_name]
                
                optimizations.append({
                    "type": "eviction_optimization",
                    "cache_name": cache_name,
                    "changes": {
                        "eviction_policy": "lru"
                    },
                    "reason": "Switched to LRU for better memory efficiency"
                })
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to optimize cache eviction: {e}")
        return []


async def optimize_cache_compression(
    cache_analysis: CacheAnalysisResponse
) -> List[Dict[str, Any]]:
    """Optimize cache compression."""
    try:
        optimizations = []
        
        for cache_name, efficiency in cache_analysis.cache_efficiency.items():
            current_policy = _cache_policies.get(cache_name, _cache_policies["default"])
            
            # Enable compression for large caches
            if efficiency["memory_usage_mb"] > 500 and not current_policy["compression"]:
                new_policy = current_policy.copy()
                new_policy["compression"] = True
                
                _cache_policies[cache_name] = new_policy
                
                optimizations.append({
                    "type": "compression_optimization",
                    "cache_name": cache_name,
                    "changes": {
                        "compression": True
                    },
                    "reason": "High memory usage detected"
                })
            
            # Disable compression for small caches
            elif efficiency["memory_usage_mb"] < 100 and current_policy["compression"]:
                new_policy = current_policy.copy()
                new_policy["compression"] = False
                
                _cache_policies[cache_name] = new_policy
                
                optimizations.append({
                    "type": "compression_optimization",
                    "cache_name": cache_name,
                    "changes": {
                        "compression": False
                    },
                    "reason": "Low memory usage - compression overhead not needed"
                })
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to optimize cache compression: {e}")
        return []


async def cleanup_unused_caches() -> List[Dict[str, Any]]:
    """Clean up unused caches."""
    try:
        optimizations = []
        
        # Find caches with no recent access
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        for cache_name, stats in _cache_stats.items():
            if stats["last_access"] and stats["last_access"] < cutoff_time:
                # Cache hasn't been accessed in 24 hours
                if cache_name in _cache_instances:
                    _cache_instances[cache_name].clear()
                    del _cache_instances[cache_name]
                
                # Reset stats
                _cache_stats[cache_name] = {
                    "hits": 0,
                    "misses": 0,
                    "sets": 0,
                    "deletes": 0,
                    "evictions": 0,
                    "last_access": None
                }
                
                optimizations.append({
                    "type": "cache_cleanup",
                    "cache_name": cache_name,
                    "changes": {
                        "cleared": True
                    },
                    "reason": "No recent access detected"
                })
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to cleanup unused caches: {e}")
        return []


async def create_cache_performance_report(
    db: AsyncSession
) -> CachePerformanceResponse:
    """Create comprehensive cache performance report."""
    try:
        # Get cache analysis
        cache_analysis = await analyze_cache_performance()
        
        # Get cache statistics
        cache_stats = await get_cache_stats()
        
        # Calculate performance metrics
        total_memory_usage = sum(stats.memory_usage_mb for stats in cache_stats.values())
        average_hit_rate = sum(stats.hit_rate for stats in cache_stats.values()) / len(cache_stats) if cache_stats else 0
        
        # Generate recommendations
        recommendations = []
        
        if cache_analysis.overall_hit_rate < 70:
            recommendations.append("Overall cache hit rate is low. Consider increasing TTL or cache sizes.")
        
        if total_memory_usage > 1000:
            recommendations.append("High memory usage detected. Consider enabling compression or reducing cache sizes.")
        
        if len(cache_analysis.performance_issues) > 0:
            recommendations.append(f"Found {len(cache_analysis.performance_issues)} performance issues that need attention.")
        
        # Calculate performance score
        performance_score = min(100, cache_analysis.overall_hit_rate + (100 - total_memory_usage / 10))
        
        return CachePerformanceResponse(
            performance_score=round(performance_score, 2),
            overall_hit_rate=cache_analysis.overall_hit_rate,
            total_caches=len(cache_stats),
            total_memory_usage_mb=round(total_memory_usage, 2),
            average_hit_rate=round(average_hit_rate, 2),
            cache_analysis=cache_analysis,
            cache_stats=cache_stats,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to create cache performance report: {e}")
        raise handle_internal_error(f"Failed to create cache performance report: {str(e)}")


async def warm_up_cache(
    cache_name: str,
    warm_up_data: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """Warm up cache with predefined data."""
    try:
        cache = get_cache_instance(cache_name)
        warmed_up_count = 0
        
        for key, value in warm_up_data.items():
            cache.set(key, value)
            warmed_up_count += 1
        
        # Update stats
        _cache_stats[cache_name]["sets"] += warmed_up_count
        _cache_stats[cache_name]["last_access"] = datetime.utcnow()
        
        return {
            "cache_name": cache_name,
            "warmed_up_count": warmed_up_count,
            "cache_size": cache.size(),
            "warmed_at": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to warm up cache: {e}")
        raise handle_internal_error(f"Failed to warm up cache: {str(e)}")


async def clear_cache(
    cache_name: Optional[str] = None
) -> Dict[str, Any]:
    """Clear cache data."""
    try:
        if cache_name:
            if cache_name in _cache_instances:
                _cache_instances[cache_name].clear()
                del _cache_instances[cache_name]
            
            # Reset stats
            _cache_stats[cache_name] = {
                "hits": 0,
                "misses": 0,
                "sets": 0,
                "deletes": 0,
                "evictions": 0,
                "last_access": None
            }
            
            return {"message": f"Cache '{cache_name}' cleared successfully"}
        else:
            # Clear all caches
            for cache_instance in _cache_instances.values():
                cache_instance.clear()
            
            _cache_instances.clear()
            _cache_stats.clear()
            
            return {"message": "All caches cleared successfully"}
    
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return {"error": str(e)}




