from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
TIMEOUT_SECONDS = 60

# Constants
BUFFER_SIZE = 1024

import asyncio
import functools
import time
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import hashlib
import redis.asyncio as redis
from fastapi import Request, Response
import structlog
from .core import (
            import psutil
            import psutil
    import psutil
from typing import Any, List, Dict, Optional
import logging
"""
Performance monitoring middleware for caching, database optimization, and metrics.
Uses functional programming patterns and RORO pattern.
"""



    LogContext, create_log_context, log_operation, LogLevel,
    MetricContext, create_metric_context, record_metric, MetricType,
    with_logging, with_metrics, with_exception_handling
)


@dataclass
class CacheContext:
    """Context for caching operations."""
    key: str
    ttl: int
    operation: str
    hit: bool = False
    miss: bool = False
    error: bool = False


@dataclass
class DatabaseContext:
    """Context for database operations."""
    query: str
    operation: str
    table: Optional[str] = None
    execution_time: float = 0.0
    rows_affected: int = 0
    error: bool = False


@dataclass
class PerformanceContext:
    """Context for performance monitoring."""
    operation: str
    component: str
    start_time: float
    end_time: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CacheManager:
    """Redis-based cache manager with async operations."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        
    """__init__ function."""
self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.logger = structlog.get_logger()
    
    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            log_operation(
                self.logger,
                create_log_context(operation="cache_connect", component="performance"),
                "Connected to Redis cache"
            )
        except Exception as e:
            log_operation(
                self.logger,
                create_log_context(operation="cache_connect", component="performance"),
                f"Failed to connect to Redis: {str(e)}",
                level=LogLevel.ERROR
            )
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
    
    def generate_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from function arguments."""
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            log_operation(
                self.logger,
                create_log_context(operation="cache_get", component="performance"),
                f"Cache get error: {str(e)}",
                level=LogLevel.ERROR
            )
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache."""
        if not self.redis_client:
            return False
        
        try:
            serialized_value = json.dumps(value)
            await self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            log_operation(
                self.logger,
                create_log_context(operation="cache_set", component="performance"),
                f"Cache set error: {str(e)}",
                level=LogLevel.ERROR
            )
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            log_operation(
                self.logger,
                create_log_context(operation="cache_delete", component="performance"),
                f"Cache delete error: {str(e)}",
                level=LogLevel.ERROR
            )
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern."""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
            return len(keys)
        except Exception as e:
            log_operation(
                self.logger,
                create_log_context(operation="cache_clear", component="performance"),
                f"Cache clear error: {str(e)}",
                level=LogLevel.ERROR
            )
            return 0


# Global cache manager instance
cache_manager = CacheManager()


class DatabaseProfiler:
    """Database query profiler and optimizer."""
    
    def __init__(self) -> Any:
        self.queries: List[Dict[str, Any]] = []
        self.logger = structlog.get_logger()
    
    def record_query(
        self,
        query: str,
        execution_time: float,
        rows_affected: int = 0,
        error: bool = False
    ) -> None:
        """Record database query performance."""
        query_info = {
            "query": query,
            "execution_time": execution_time,
            "rows_affected": rows_affected,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.queries.append(query_info)
        
        # Log slow queries
        if execution_time > 1.0:  # More than 1 second
            context = create_log_context(
                operation="slow_query",
                component="database"
            )
            log_operation(
                self.logger,
                context,
                f"Slow query detected: {execution_time:.2f}s",
                level=LogLevel.WARNING,
                query=query,
                execution_time=execution_time
            )
    
    def get_slow_queries(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """Get queries slower than threshold."""
        return [
            q for q in self.queries
            if q["execution_time"] > threshold
        ]
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Get query performance statistics."""
        if not self.queries:
            return {}
        
        execution_times = [q["execution_time"] for q in self.queries]
        
        return {
            "total_queries": len(self.queries),
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "max_execution_time": max(execution_times),
            "min_execution_time": min(execution_times),
            "slow_queries": len(self.get_slow_queries()),
            "error_queries": len([q for q in self.queries if q["error"]])
        }


# Global database profiler instance
db_profiler = DatabaseProfiler()


# =============================================================================
# PERFORMANCE DECORATORS
# =============================================================================

def with_caching(
    ttl: int = 3600,
    key_prefix: str = "",
    cache_manager_instance: Optional[CacheManager] = None
):
    """
    Decorator for automatic caching of function results.
    
    Args:
        ttl: Cache TTL in seconds
        key_prefix: Prefix for cache keys
        cache_manager_instance: Cache manager instance
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            cache_mgr = cache_manager_instance or cache_manager
            
            # Generate cache key
            cache_key = cache_mgr.generate_cache_key(*args, **kwargs)
            if key_prefix:
                cache_key = f"{key_prefix}:{cache_key}"
            
            # Try to get from cache
            cached_result = await cache_mgr.get(cache_key)
            if cached_result is not None:
                # Cache hit
                context = create_log_context(
                    operation="cache_hit",
                    component="performance"
                )
                log_operation(
                    structlog.get_logger(),
                    context,
                    f"Cache hit for {func.__name__}"
                )
                
                metric_context = create_metric_context(
                    "cache_hit", "performance", operation=func.__name__
                )
                record_metric(metric_context, MetricType.COUNTER, 1)
                
                return cached_result
            
            # Cache miss - execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_mgr.set(cache_key, result, ttl)
            
            # Log cache miss
            context = create_log_context(
                operation="cache_miss",
                component="performance"
            )
            log_operation(
                structlog.get_logger(),
                context,
                f"Cache miss for {func.__name__}"
            )
            
            metric_context = create_metric_context(
                "cache_miss", "performance", operation=func.__name__
            )
            record_metric(metric_context, MetricType.COUNTER, 1)
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # For sync functions, we can't use async cache operations
            # This is a limitation - sync functions should be wrapped differently
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def with_database_profiling():
    """Decorator for database query profiling."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record query performance
                db_profiler.record_query(
                    query=str(func.__name__),
                    execution_time=execution_time,
                    rows_affected=getattr(result, 'rowcount', 0) if hasattr(result, 'rowcount') else 0
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                db_profiler.record_query(
                    query=str(func.__name__),
                    execution_time=execution_time,
                    error=True
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                db_profiler.record_query(
                    query=str(func.__name__),
                    execution_time=execution_time,
                    rows_affected=getattr(result, 'rowcount', 0) if hasattr(result, 'rowcount') else 0
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                db_profiler.record_query(
                    query=str(func.__name__),
                    execution_time=execution_time,
                    error=True
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def with_performance_monitoring(
    operation: str,
    component: str
):
    """
    Decorator for comprehensive performance monitoring.
    
    Args:
        operation: Operation name
        component: Component name
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            # Record memory usage before
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            try:
                result = await func(*args, **kwargs)
                end_time = time.time()
                
                # Record memory usage after
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_delta = memory_after - memory_before
                
                # Log performance metrics
                context = create_log_context(
                    operation=operation,
                    component=component
                )
                log_operation(
                    structlog.get_logger(),
                    context,
                    f"Operation completed in {end_time - start_time:.3f}s",
                    execution_time=end_time - start_time,
                    memory_delta=memory_delta
                )
                
                # Record metrics
                metric_context = create_metric_context(
                    operation, component
                )
                record_metric(metric_context, MetricType.HISTOGRAM, end_time - start_time)
                record_metric(metric_context, MetricType.GAUGE, memory_delta, metric="memory_mb")
                
                return result
            except Exception as e:
                end_time = time.time()
                
                context = create_log_context(
                    operation=operation,
                    component=component
                )
                log_operation(
                    structlog.get_logger(),
                    context,
                    f"Operation failed after {end_time - start_time:.3f}s",
                    level=LogLevel.ERROR,
                    execution_time=end_time - start_time,
                    error=str(e)
                )
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                
                memory_after = process.memory_info().rss / 1024 / 1024
                memory_delta = memory_after - memory_before
                
                context = create_log_context(
                    operation=operation,
                    component=component
                )
                log_operation(
                    structlog.get_logger(),
                    context,
                    f"Operation completed in {end_time - start_time:.3f}s",
                    execution_time=end_time - start_time,
                    memory_delta=memory_delta
                )
                
                metric_context = create_metric_context(operation, component)
                record_metric(metric_context, MetricType.HISTOGRAM, end_time - start_time)
                record_metric(metric_context, MetricType.GAUGE, memory_delta, metric="memory_mb")
                
                return result
            except Exception as e:
                end_time = time.time()
                
                context = create_log_context(
                    operation=operation,
                    component=component
                )
                log_operation(
                    structlog.get_logger(),
                    context,
                    f"Operation failed after {end_time - start_time:.3f}s",
                    level=LogLevel.ERROR,
                    execution_time=end_time - start_time,
                    error=str(e)
                )
                
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# =============================================================================
# PERFORMANCE MIDDLEWARE
# =============================================================================

async def performance_monitoring_middleware(request: Request, call_next):
    """Middleware for performance monitoring."""
    start_time = time.time()
    
    # Record request start
    context = create_log_context(
        request_id=request.headers.get("X-Request-ID", "unknown"),
        operation=f"{request.method} {request.url.path}",
        component="api"
    )
    
    # Monitor memory usage
    process = psutil.Process()
    memory_before = process.memory_info().rss / 1024 / 1024
    
    try:
        response = await call_next(request)
        end_time = time.time()
        
        # Calculate performance metrics
        execution_time = end_time - start_time
        memory_after = process.memory_info().rss / 1024 / 1024
        memory_delta = memory_after - memory_before
        
        # Log performance
        log_operation(
            structlog.get_logger(),
            context,
            f"Request completed in {execution_time:.3f}s",
            execution_time=execution_time,
            memory_delta=memory_delta,
            status_code=response.status_code
        )
        
        # Record metrics
        metric_context = create_metric_context(
            "http_request", "api",
            method=request.method,
            path=request.url.path,
            status_code=str(response.status_code)
        )
        record_metric(metric_context, MetricType.HISTOGRAM, execution_time)
        record_metric(metric_context, MetricType.GAUGE, memory_delta, metric="memory_mb")
        
        # Add performance headers
        response.headers["X-Execution-Time"] = f"{execution_time:.3f}"
        response.headers["X-Memory-Delta"] = f"{memory_delta:.2f}"
        
        return response
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        log_operation(
            structlog.get_logger(),
            context,
            f"Request failed after {execution_time:.3f}s",
            level=LogLevel.ERROR,
            execution_time=execution_time,
            error=str(e)
        )
        
        metric_context = create_metric_context(
            "http_request", "api",
            method=request.method,
            path=request.url.path,
            error="true"
        )
        record_metric(metric_context, MetricType.HISTOGRAM, execution_time)
        record_metric(metric_context, MetricType.COUNTER, 1, error="true")
        
        raise


async def caching_middleware(request: Request, call_next):
    """Middleware for response caching."""
    # Skip caching for non-GET requests
    if request.method != "GET":
        return await call_next(request)
    
    # Generate cache key
    cache_key = f"response:{request.url.path}:{request.query_params}"
    
    # Try to get from cache
    cached_response = await cache_manager.get(cache_key)
    if cached_response:
        # Return cached response
        context = create_log_context(
            request_id=request.headers.get("X-Request-ID", "unknown"),
            operation="response_cache_hit",
            component="performance"
        )
        log_operation(
            structlog.get_logger(),
            context,
            f"Cache hit for {request.url.path}"
        )
        
        return JSONResponse(
            content=cached_response,
            headers={"X-Cache": "HIT"}
        )
    
    # Cache miss - process request
    response = await call_next(request)
    
    # Cache successful responses
    if response.status_code == 200:
        try:
            response_body = await response.body()
            response_data = json.loads(response_body)
            
            # Cache for 5 minutes
            await cache_manager.set(cache_key, response_data, 300)
            
            # Add cache header
            response.headers["X-Cache"] = "MISS"
            
        except Exception as e:
            # Log cache error but don't fail the request
            context = create_log_context(
                request_id=request.headers.get("X-Request-ID", "unknown"),
                operation="response_cache_error",
                component="performance"
            )
            log_operation(
                structlog.get_logger(),
                context,
                f"Failed to cache response: {str(e)}",
                level=LogLevel.WARNING
            )
    
    return response


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def setup_performance_middleware(app) -> None:
    """Setup performance monitoring middleware stack."""
    app.middleware("http")(performance_monitoring_middleware)
    app.middleware("http")(caching_middleware)


async def initialize_cache() -> None:
    """Initialize cache connection."""
    await cache_manager.connect()


async def cleanup_cache() -> None:
    """Cleanup cache connection."""
    await cache_manager.disconnect()


def get_performance_statistics() -> Dict[str, Any]:
    """Get comprehensive performance statistics."""
    return {
        "database": db_profiler.get_query_statistics(),
        "cache": {
            "connected": cache_manager.redis_client is not None
        }
    }


def optimize_database_queries() -> List[str]:
    """Analyze and suggest database query optimizations."""
    suggestions = []
    
    # Analyze slow queries
    slow_queries = db_profiler.get_slow_queries()
    if slow_queries:
        suggestions.append(f"Found {len(slow_queries)} slow queries (>1s)")
        
        # Group by query pattern
        query_patterns = {}
        for query in slow_queries:
            pattern = query["query"][:50] + "..."  # Truncate for grouping
            if pattern not in query_patterns:
                query_patterns[pattern] = []
            query_patterns[pattern].append(query)
        
        for pattern, queries in query_patterns.items():
            avg_time = sum(q["execution_time"] for q in queries) / len(queries)
            suggestions.append(f"Consider optimizing: {pattern} (avg: {avg_time:.2f}s)")
    
    # Check for repeated queries
    query_counts = {}
    for query in db_profiler.queries:
        query_str = query["query"]
        query_counts[query_str] = query_counts.get(query_str, 0) + 1
    
    repeated_queries = [
        (query, count) for query, count in query_counts.items()
        if count > 5
    ]
    
    if repeated_queries:
        suggestions.append("Consider caching frequently repeated queries:")
        for query, count in repeated_queries[:5]:  # Top 5
            suggestions.append(f"  - {query[:50]}... (called {count} times)")
    
    return suggestions


def clear_cache_pattern(pattern: str) -> int:
    """Clear cache entries matching pattern."""
    return asyncio.run(cache_manager.clear_pattern(pattern))


def get_cache_statistics() -> Dict[str, Any]:
    """Get cache statistics."""
    if not cache_manager.redis_client:
        return {"status": "disconnected"}
    
    try:
        # This would require additional Redis commands to get statistics
        return {
            "status": "connected",
            "url": cache_manager.redis_url
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        } 