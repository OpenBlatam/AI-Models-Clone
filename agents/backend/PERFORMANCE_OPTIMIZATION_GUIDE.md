# 🚀 Performance Optimization Guide

## Overview

This guide provides comprehensive strategies for optimizing performance in the Blatam Academy backend using async functions for I/O-bound tasks, advanced caching strategies, and intelligent lazy loading.

## Table of Contents

1. [Async Functions for I/O-bound Tasks](#async-functions-for-io-bound-tasks)
2. [Caching Strategies](#caching-strategies)
3. [Lazy Loading](#lazy-loading)
4. [Performance Monitoring](#performance-monitoring)
5. [Best Practices](#best-practices)
6. [Implementation Examples](#implementation-examples)

## Async Functions for I/O-bound Tasks

### When to Use Async Functions

- **Database operations** (queries, transactions)
- **HTTP requests** (API calls, web scraping)
- **File I/O operations** (reading/writing files)
- **External service calls** (Redis, message queues)
- **Network operations** (sockets, streaming)

### Implementation Patterns

#### 1. Basic Async Function

```python
async def fetch_user_data(user_id: str) -> Dict[str, Any]:
    """Fetch user data from database"""
    async with get_db_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return user.to_dict() if user else None
```

#### 2. Async Function with Error Handling

```python
async def fetch_user_data_with_retry(user_id: str, max_retries: int = 3) -> Dict[str, Any]:
    """Fetch user data with retry logic"""
    for attempt in range(max_retries):
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                return user.to_dict() if user else None
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

#### 3. Parallel Execution

```python
async def fetch_multiple_users(user_ids: List[str]) -> List[Dict[str, Any]]:
    """Fetch multiple users in parallel"""
    tasks = [fetch_user_data(user_id) for user_id in user_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions
    return [result for result in results if not isinstance(result, Exception)]
```

#### 4. Async Context Manager

```python
@asynccontextmanager
async def async_resource_manager(resource_name: str, loader_func: Callable):
    """Context manager for async resources"""
    resource = None
    try:
        if asyncio.iscoroutinefunction(loader_func):
            resource = await loader_func()
        else:
            loop = asyncio.get_event_loop()
            resource = await loop.run_in_executor(None, loader_func)
        yield resource
    finally:
        if resource and hasattr(resource, 'close'):
            await resource.close()

# Usage
async with async_resource_manager("database", create_db_connection) as db:
    result = await db.execute("SELECT * FROM users")
```

### Performance Optimizations

#### 1. Connection Pooling

```python
class DatabasePool:
    def __init__(self, max_connections: int = 20):
        self.pool = None
        self.max_connections = max_connections
    
    async def initialize(self):
        self.pool = await asyncpg.create_pool(
            DATABASE_URL,
            max_size=self.max_connections,
            min_size=5
        )
    
    async def get_connection(self):
        return await self.pool.acquire()
    
    async def release_connection(self, conn):
        await self.pool.release(conn)
```

#### 2. Batch Processing

```python
async def process_batch(items: List[Any], batch_size: int = 100):
    """Process items in batches"""
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        tasks = [process_item(item) for item in batch]
        await asyncio.gather(*tasks)
```

## Caching Strategies

### Multi-Level Caching

#### 1. L1 Cache (Memory)

```python
from cachetools import TTLCache, LRUCache

class L1Cache:
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.cache = TTLCache(maxsize=max_size, ttl=ttl)
        self.lru_cache = LRUCache(maxsize=max_size)
    
    def get(self, key: str) -> Optional[Any]:
        # Try TTL cache first
        if key in self.cache:
            return self.cache[key]
        
        # Try LRU cache
        if key in self.lru_cache:
            return self.lru_cache[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        self.cache[key] = value
        self.lru_cache[key] = value
```

#### 2. L2 Cache (Redis)

```python
import redis.asyncio as redis

class L2Cache:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            value = await self.redis_client.get(key)
            return orjson.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        try:
            serialized = orjson.dumps(value)
            await self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
```

#### 3. Predictive Caching

```python
class PredictiveCache:
    def __init__(self):
        self.access_patterns = defaultdict(int)
        self.prediction_threshold = 0.3
    
    async def get(self, key: str) -> Optional[Any]:
        # Record access pattern
        self._record_access(key)
        
        # Get value from cache
        value = await self._get_from_cache(key)
        
        # Predict and preload likely next keys
        if value is not None:
            asyncio.create_task(self._predict_and_preload(key))
        
        return value
    
    def _record_access(self, key: str):
        """Record access pattern for prediction"""
        # Implementation for pattern tracking
        pass
    
    async def _predict_and_preload(self, current_key: str):
        """Predict and preload likely next keys"""
        likely_keys = self._predict_next_keys(current_key)
        for key, confidence in likely_keys:
            if confidence > self.prediction_threshold:
                await self._preload_key(key)
```

### Cache Decorators

#### 1. Simple Cache Decorator

```python
def async_cache(ttl: int = 3600):
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = hashlib.md5(
                f"{func.__name__}:{args}:{sorted(kwargs.items())}".encode()
            ).hexdigest()
            
            # Check cache
            if key in cache:
                return cache[key]
            
            # Execute function
            result = await func(*args, **kwargs)
            cache[key] = result
            return result
        
        return wrapper
    return decorator

# Usage
@async_cache(ttl=300)
async def get_user_profile(user_id: str) -> Dict[str, Any]:
    # Expensive operation
    return await fetch_user_data(user_id)
```

#### 2. Advanced Cache Decorator

```python
def smart_cache(cache_key_generator: Callable = None, ttl: int = 3600):
    def decorator(func: Callable) -> Callable:
        cache = TTLCache(maxsize=1000, ttl=ttl)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_generator:
                key = cache_key_generator(*args, **kwargs)
            else:
                key = f"{func.__name__}:{hash(args)}:{hash(tuple(sorted(kwargs.items())))}"
            
            # Check cache
            if key in cache:
                return cache[key]
            
            # Execute function
            result = await func(*args, **kwargs)
            cache[key] = result
            return result
        
        # Add cache management methods
        wrapper.clear_cache = cache.clear
        wrapper.get_cache_stats = lambda: {"size": len(cache)}
        
        return wrapper
    return decorator
```

## Lazy Loading

### Basic Lazy Loading

```python
class LazyLoader:
    def __init__(self):
        self._loaded_modules = {}
        self._loading_futures = {}
    
    async def load(self, module_name: str, loader_func: Callable) -> Any:
        # Return if already loaded
        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]
        
        # Wait if already loading
        if module_name in self._loading_futures:
            return await self._loading_futures[module_name]
        
        # Start loading
        self._loading_futures[module_name] = asyncio.create_task(
            self._load_module(module_name, loader_func)
        )
        
        try:
            result = await self._loading_futures[module_name]
            return result
        finally:
            self._loading_futures.pop(module_name, None)
    
    async def _load_module(self, module_name: str, loader_func: Callable) -> Any:
        try:
            if asyncio.iscoroutinefunction(loader_func):
                module = await loader_func()
            else:
                loop = asyncio.get_event_loop()
                module = await loop.run_in_executor(None, loader_func)
            
            self._loaded_modules[module_name] = module
            return module
        except Exception as e:
            logger.error(f"Failed to load module {module_name}: {e}")
            raise
```

### Dependency-Aware Lazy Loading

```python
class DependencyAwareLazyLoader:
    def __init__(self):
        self.dependency_graph = {}
        self.loaded_modules = {}
        self.loading_futures = {}
    
    def register_module(self, name: str, loader_func: Callable, 
                       dependencies: List[str] = None):
        """Register a module with its dependencies"""
        self.dependency_graph[name] = {
            'loader': loader_func,
            'dependencies': dependencies or []
        }
    
    async def load(self, module_name: str) -> Any:
        """Load module with dependency resolution"""
        # Check if already loaded
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
        
        # Check if already loading
        if module_name in self.loading_futures:
            return await self.loading_futures[module_name]
        
        # Load dependencies first
        dependencies = self.dependency_graph.get(module_name, {}).get('dependencies', [])
        for dep in dependencies:
            await self.load(dep)
        
        # Load the module
        return await self._load_module(module_name)
    
    async def _load_module(self, module_name: str) -> Any:
        """Actually load the module"""
        loader_func = self.dependency_graph[module_name]['loader']
        
        # Create loading future
        future = asyncio.Future()
        self.loading_futures[module_name] = future
        
        try:
            if asyncio.iscoroutinefunction(loader_func):
                module = await loader_func()
            else:
                loop = asyncio.get_event_loop()
                module = await loop.run_in_executor(None, loader_func)
            
            self.loaded_modules[module_name] = module
            future.set_result(module)
            return module
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            self.loading_futures.pop(module_name, None)
```

### Lazy Loading Decorators

```python
def lazy_load(module_name: str, loader_func: Callable):
    """Decorator for lazy loading modules"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Load module lazily
            loader = LazyLoader()
            await loader.load(module_name, loader_func)
            
            # Execute function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Usage
@lazy_load("ml_model", load_ml_model)
async def predict_sentiment(text: str) -> float:
    # ML model is loaded only when this function is called
    return model.predict(text)
```

## Performance Monitoring

### Metrics Collection

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_times = {}
    
    def start_timer(self, name: str):
        """Start timing an operation"""
        self.start_times[name] = time.time()
    
    def end_timer(self, name: str):
        """End timing an operation"""
        if name in self.start_times:
            duration = time.time() - self.start_times[name]
            self.metrics[name].append(duration)
            del self.start_times[name]
    
    @asynccontextmanager
    async def timer(self, name: str):
        """Context manager for timing async operations"""
        self.start_timer(name)
        try:
            yield
        finally:
            self.end_timer(name)
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        values = self.metrics.get(name, [])
        if not values:
            return {}
        
        return {
            'count': len(values),
            'average': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'total': sum(values)
        }

# Usage
monitor = PerformanceMonitor()

async with monitor.timer("database_query"):
    result = await db.execute("SELECT * FROM users")

stats = monitor.get_stats("database_query")
print(f"Average query time: {stats['average']:.3f}s")
```

### Performance Alerts

```python
class PerformanceAlert:
    def __init__(self, threshold: float, severity: str = "warning"):
        self.threshold = threshold
        self.severity = severity
    
    def check(self, value: float) -> Optional[str]:
        """Check if value exceeds threshold"""
        if value > self.threshold:
            return f"Performance alert: {value} exceeds threshold {self.threshold}"
        return None

# Usage
response_time_alert = PerformanceAlert(1000, "error")  # 1 second

async def monitored_function():
    start_time = time.time()
    result = await expensive_operation()
    duration = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    alert = response_time_alert.check(duration)
    if alert:
        logger.error(alert)
    
    return result
```

## Best Practices

### 1. Async Function Best Practices

- **Use `async def` for I/O-bound operations**
- **Use `def` for CPU-bound operations**
- **Always handle exceptions in async functions**
- **Use connection pooling for database operations**
- **Implement retry logic for external service calls**
- **Use `asyncio.gather()` for parallel execution**
- **Avoid blocking operations in async functions**

### 2. Caching Best Practices

- **Cache frequently accessed data**
- **Use appropriate TTL values**
- **Implement cache invalidation strategies**
- **Monitor cache hit rates**
- **Use multi-level caching for better performance**
- **Compress large cached data**
- **Implement cache warming for critical data**

### 3. Lazy Loading Best Practices

- **Load resources only when needed**
- **Manage dependencies properly**
- **Handle circular dependencies**
- **Implement resource cleanup**
- **Monitor memory usage**
- **Use connection pooling for lazy-loaded resources**

### 4. Performance Monitoring Best Practices

- **Collect metrics for all critical operations**
- **Set up alerts for performance thresholds**
- **Monitor resource usage (CPU, memory, disk, network)**
- **Track response times and throughput**
- **Implement distributed tracing**
- **Use APM tools for production monitoring**

## Implementation Examples

### Complete Example: Optimized User Service

```python
from typing import List, Dict, Any, Optional
import asyncio
import time
from functools import wraps

class OptimizedUserService:
    def __init__(self):
        self.cache = TTLCache(maxsize=1000, ttl=300)
        self.monitor = PerformanceMonitor()
        self.lazy_loader = LazyLoader()
    
    @async_cache(ttl=300)
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user with caching"""
        async with self.monitor.timer("get_user"):
            # Try cache first
            cache_key = f"user:{user_id}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Fetch from database
            user = await self._fetch_user_from_db(user_id)
            if user:
                self.cache[cache_key] = user
            
            return user
    
    async def get_users_batch(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        """Get multiple users with parallel execution"""
        async with self.monitor.timer("get_users_batch"):
            # Check cache first
            cached_users = {}
            uncached_ids = []
            
            for user_id in user_ids:
                cache_key = f"user:{user_id}"
                if cache_key in self.cache:
                    cached_users[user_id] = self.cache[cache_key]
                else:
                    uncached_ids.append(user_id)
            
            # Fetch uncached users in parallel
            if uncached_ids:
                tasks = [self._fetch_user_from_db(user_id) for user_id in uncached_ids]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Cache results and combine with cached users
                for user_id, result in zip(uncached_ids, results):
                    if not isinstance(result, Exception) and result:
                        cache_key = f"user:{user_id}"
                        self.cache[cache_key] = result
                        cached_users[user_id] = result
            
            return [cached_users.get(user_id) for user_id in user_ids]
    
    async def _fetch_user_from_db(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch user from database"""
        # Simulate database query
        await asyncio.sleep(0.1)
        return {"id": user_id, "name": f"User {user_id}"}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            "cache_stats": {
                "size": len(self.cache),
                "hit_rate": self._calculate_cache_hit_rate()
            },
            "monitor_stats": {
                "get_user": self.monitor.get_stats("get_user"),
                "get_users_batch": self.monitor.get_stats("get_users_batch")
            }
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        # Implementation for cache hit rate calculation
        return 0.85  # Placeholder
```

### Example: FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from typing import List

app = FastAPI()
user_service = OptimizedUserService()

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get user endpoint with performance optimization"""
    try:
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/batch")
async def get_users_batch(user_ids: List[str]):
    """Get multiple users endpoint with batch optimization"""
    try:
        users = await user_service.get_users_batch(user_ids)
        return {"users": users}
    except Exception as e:
        logger.error(f"Error getting users batch: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/performance/stats")
async def get_performance_stats():
    """Get performance statistics endpoint"""
    return user_service.get_performance_stats()
```

## Conclusion

This guide provides a comprehensive approach to performance optimization using async functions, caching strategies, and lazy loading. By implementing these patterns, you can significantly improve the performance and scalability of your applications.

Remember to:

1. **Profile your application** to identify bottlenecks
2. **Monitor performance metrics** continuously
3. **Test optimizations** thoroughly before deploying
4. **Document performance improvements** for team knowledge
5. **Iterate and improve** based on real-world usage patterns

For more advanced optimization techniques, refer to the specific utility modules in the `onyx/server/features/utils/` directory. 