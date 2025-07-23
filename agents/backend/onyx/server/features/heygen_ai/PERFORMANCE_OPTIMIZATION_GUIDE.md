# Performance Optimization Guide

A comprehensive guide for optimizing performance in the HeyGen AI FastAPI application.

## 🎯 Overview

This guide covers:
- **Caching Strategies**: Multi-level caching with Redis and memory
- **Database Optimization**: Connection pooling and query optimization
- **Async Processing**: Concurrent task execution and batch processing
- **Connection Pooling**: Efficient resource management
- **Monitoring**: Performance metrics and health checks
- **Best Practices**: Optimization patterns and recommendations

## 📋 Table of Contents

1. [Caching Strategies](#caching-strategies)
2. [Database Optimization](#database-optimization)
3. [Connection Pooling](#connection-pooling)
4. [Async Processing](#async-processing)
5. [Performance Monitoring](#performance-monitoring)
6. [Integration Examples](#integration-examples)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## 🗄️ Caching Strategies

### Overview

The caching system provides multiple levels of caching with different strategies for optimal performance.

### Cache Strategies

#### **Memory Cache (LRU)**
```python
from api.optimization.performance_optimizer import CacheManager, CacheStrategy

# Memory-only caching
cache_manager = CacheManager(
    memory_cache_size=1000,
    default_ttl=300
)

# Store data in memory
await cache_manager.set("user:123", user_data, ttl=600, strategy=CacheStrategy.MEMORY)

# Retrieve from memory
user_data = await cache_manager.get("user:123", strategy=CacheStrategy.MEMORY)
```

#### **Redis Cache**
```python
# Redis caching
cache_manager = CacheManager(
    redis_url="redis://localhost:6379",
    default_ttl=300
)

# Store data in Redis
await cache_manager.set("video:456", video_data, ttl=1800, strategy=CacheStrategy.REDIS)

# Retrieve from Redis
video_data = await cache_manager.get("video:456", strategy=CacheStrategy.REDIS)
```

#### **Hybrid Cache (Recommended)**
```python
# Hybrid caching (memory + Redis)
cache_manager = CacheManager(
    redis_url="redis://localhost:6379",
    memory_cache_size=1000,
    default_ttl=300
)

# Store data in both memory and Redis
await cache_manager.set("user:123", user_data, ttl=600, strategy=CacheStrategy.HYBRID)

# Retrieve (tries memory first, then Redis)
user_data = await cache_manager.get("user:123", strategy=CacheStrategy.HYBRID)
```

### Cache Decorators

#### **Function Result Caching**
```python
from api.optimization.performance_optimizer import cache_result

@cache_result(ttl=300, strategy=CacheStrategy.HYBRID)
async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user profile with caching."""
    # Expensive database query
    user = await user_service.get_user(user_id)
    return user.to_dict()

@cache_result(ttl=1800, strategy=CacheStrategy.REDIS)
async def get_video_analytics(video_id: str) -> Dict[str, Any]:
    """Get video analytics with Redis caching."""
    analytics = await analytics_service.get_video_analytics(video_id)
    return analytics
```

#### **Custom Cache Key Generation**
```python
def generate_user_cache_key(user_id: str, include_profile: bool = False) -> str:
    """Generate custom cache key for user data."""
    return f"user:{user_id}:profile:{include_profile}"

@cache_result(
    ttl=600,
    strategy=CacheStrategy.HYBRID,
    key_generator=generate_user_cache_key
)
async def get_user_data(user_id: str, include_profile: bool = False) -> Dict[str, Any]:
    """Get user data with custom cache key."""
    user_data = await user_service.get_user_data(user_id, include_profile)
    return user_data
```

### Cache Invalidation

#### **Manual Invalidation**
```python
# Invalidate specific keys
await cache_manager.delete("user:123", strategy=CacheStrategy.HYBRID)

# Invalidate pattern-based keys
async def invalidate_user_cache(user_id: str):
    """Invalidate all user-related cache entries."""
    patterns = [
        f"user:{user_id}",
        f"user:{user_id}:profile:*",
        f"user:{user_id}:analytics:*"
    ]
    
    for pattern in patterns:
        await cache_manager.delete(pattern, strategy=CacheStrategy.HYBRID)
```

#### **Automatic Invalidation**
```python
# Cache with automatic invalidation
@cache_result(ttl=300, strategy=CacheStrategy.HYBRID)
async def get_user_videos(user_id: str) -> List[Dict[str, Any]]:
    """Get user videos with automatic cache invalidation."""
    videos = await video_service.get_user_videos(user_id)
    return videos

# When user creates a new video, invalidate cache
async def create_video(user_id: str, video_data: Dict[str, Any]):
    """Create video and invalidate related cache."""
    video = await video_service.create_video(user_id, video_data)
    
    # Invalidate user videos cache
    await cache_manager.delete(f"user:{user_id}:videos", strategy=CacheStrategy.HYBRID)
    
    return video
```

## 🗃️ Database Optimization

### Overview

Database optimization includes connection pooling, query optimization, and efficient data access patterns.

### Connection Pooling

#### **Database Connection Pool**
```python
from api.optimization.connection_pooling import DatabaseConnectionPool, ConnectionConfig

# Configure database connection pool
db_config = ConnectionConfig(
    url="postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
    connection_timeout=30,
    read_timeout=30
)

db_pool = DatabaseConnectionPool(db_config)

# Use connection pool
async def get_user_data(user_id: str) -> Dict[str, Any]:
    """Get user data using connection pool."""
    async with db_pool.get_session() as session:
        result = await session.execute(
            text("SELECT * FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )
        return dict(result.fetchone()._mapping)
```

#### **Query Optimization**
```python
from api.optimization.performance_optimizer import QueryOptimizer

query_optimizer = QueryOptimizer(cache_manager)

# Execute optimized query with caching
async def get_user_videos(user_id: str) -> List[Dict[str, Any]]:
    """Get user videos with query optimization and caching."""
    query = """
        SELECT v.*, u.name as user_name 
        FROM videos v 
        JOIN users u ON v.user_id = u.id 
        WHERE v.user_id = :user_id 
        ORDER BY v.created_at DESC
    """
    
    return await query_optimizer.execute_cached_query(
        query=query,
        params={"user_id": user_id},
        ttl=300
    )
```

#### **Batch Operations**
```python
# Batch insert
async def create_multiple_videos(videos_data: List[Dict[str, Any]]) -> List[str]:
    """Create multiple videos efficiently."""
    queries = []
    params = []
    
    for video_data in videos_data:
        queries.append("""
            INSERT INTO videos (title, description, user_id, created_at)
            VALUES (:title, :description, :user_id, :created_at)
            RETURNING id
        """)
        params.append({
            "title": video_data["title"],
            "description": video_data["description"],
            "user_id": video_data["user_id"],
            "created_at": datetime.now(timezone.utc)
        })
    
    results = await db_pool.execute_batch(queries, params)
    return [result[0]["id"] for result in results]
```

### Query Optimization Techniques

#### **Index Optimization**
```python
# Add database indexes for common queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_created_at ON videos(created_at);
CREATE INDEX idx_videos_status ON videos(status);

# Composite indexes for complex queries
CREATE INDEX idx_videos_user_status ON videos(user_id, status);
CREATE INDEX idx_videos_user_created ON videos(user_id, created_at DESC);
```

#### **Query Hints**
```python
# Use query hints for better performance
async def get_user_videos_optimized(user_id: str) -> List[Dict[str, Any]]:
    """Get user videos with query hints."""
    query = """
        SELECT /*+ INDEX(videos idx_videos_user_id) */
            v.*, u.name as user_name
        FROM videos v
        JOIN users u ON v.user_id = u.id
        WHERE v.user_id = :user_id
        ORDER BY v.created_at DESC
        LIMIT 100
    """
    
    return await db_pool.execute_query(query, {"user_id": user_id})
```

#### **Pagination Optimization**
```python
# Efficient pagination with cursor-based approach
async def get_videos_paginated(
    cursor: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """Get videos with cursor-based pagination."""
    if cursor:
        query = """
            SELECT v.*, u.name as user_name
            FROM videos v
            JOIN users u ON v.user_id = u.id
            WHERE v.created_at < :cursor
            ORDER BY v.created_at DESC
            LIMIT :limit
        """
        params = {"cursor": cursor, "limit": limit}
    else:
        query = """
            SELECT v.*, u.name as user_name
            FROM videos v
            JOIN users u ON v.user_id = u.id
            ORDER BY v.created_at DESC
            LIMIT :limit
        """
        params = {"limit": limit}
    
    results = await db_pool.execute_query(query, params)
    
    # Generate next cursor
    next_cursor = None
    if results and len(results) == limit:
        next_cursor = results[-1]["created_at"].isoformat()
    
    return {
        "videos": results,
        "next_cursor": next_cursor,
        "has_more": len(results) == limit
    }
```

## 🔗 Connection Pooling

### Overview

Connection pooling manages database, Redis, HTTP, and MongoDB connections efficiently.

### Multi-Service Connection Pooling

#### **Connection Pool Manager**
```python
from api.optimization.connection_pooling import (
    ConnectionPoolManager, ConnectionType, ConnectionConfig
)

# Initialize connection pool manager
pool_manager = ConnectionPoolManager()

# Add database pool
db_config = ConnectionConfig(
    url="postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,
    max_overflow=30
)
await pool_manager.add_pool("database", ConnectionType.DATABASE, db_config)

# Add Redis pool
redis_config = ConnectionConfig(
    url="redis://localhost:6379",
    pool_size=10,
    max_overflow=20
)
await pool_manager.add_pool("redis", ConnectionType.REDIS, redis_config)

# Add HTTP pool
http_config = ConnectionConfig(
    url="https://api.heygen.com",
    pool_size=50,
    max_overflow=100,
    connection_timeout=30,
    read_timeout=30
)
await pool_manager.add_pool("heygen_api", ConnectionType.HTTP, http_config)
```

#### **Using Connection Pools**
```python
# Get database pool
db_pool = await pool_manager.get_pool("database")
async with db_pool.get_session() as session:
    result = await session.execute(text("SELECT * FROM users"))
    users = result.fetchall()

# Get Redis pool
redis_pool = await pool_manager.get_pool("redis")
client = await redis_pool.get_redis_client()
await client.set("key", "value")

# Get HTTP pool
http_pool = await pool_manager.get_pool("heygen_api")
response = await http_pool.get("/v1/videos")
data = await response.json()
```

### HTTP Client Optimization

#### **Optimized HTTP Client**
```python
from api.optimization.connection_pooling import HTTPConnectionPool, ConnectionConfig

# Configure HTTP client with optimization
http_config = ConnectionConfig(
    url="https://api.heygen.com",
    pool_size=50,
    max_overflow=100,
    connection_timeout=30,
    read_timeout=30,
    keepalive_timeout=60,
    compression=True,
    gzip=True,
    brotli=True,
    ssl_verify=True,
    max_retries=3,
    backoff_factor=0.3
)

http_pool = HTTPConnectionPool(http_config)

# Make optimized requests
async def create_video_with_heygen(video_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create video using HeyGen API with optimized HTTP client."""
    try:
        response = await http_pool.post(
            "/v1/videos",
            json=video_data,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status == 200:
            return await response.json()
        else:
            raise Exception(f"HeyGen API error: {response.status}")
            
    except Exception as e:
        logger.error(f"HeyGen API request failed: {e}")
        raise
```

#### **Batch HTTP Requests**
```python
async def process_multiple_videos(video_ids: List[str]) -> List[Dict[str, Any]]:
    """Process multiple videos concurrently."""
    tasks = []
    
    for video_id in video_ids:
        task = http_pool.get(f"/v1/videos/{video_id}")
        tasks.append(task)
    
    # Execute all requests concurrently
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    results = []
    for response in responses:
        if isinstance(response, Exception):
            logger.error(f"Request failed: {response}")
            results.append({"error": str(response)})
        else:
            data = await response.json()
            results.append(data)
    
    return results
```

## ⚡ Async Processing

### Overview

Async processing enables concurrent execution of tasks for improved performance.

### Async Optimizer

#### **Concurrent Task Execution**
```python
from api.optimization.connection_pooling import AsyncOptimizer

async_optimizer = AsyncOptimizer(max_concurrent_tasks=100)

# Run tasks concurrently
async def process_user_data(user_ids: List[str]) -> List[Dict[str, Any]]:
    """Process multiple users concurrently."""
    async def process_user(user_id: str) -> Dict[str, Any]:
        user_data = await user_service.get_user(user_id)
        user_videos = await video_service.get_user_videos(user_id)
        user_analytics = await analytics_service.get_user_analytics(user_id)
        
        return {
            "user": user_data,
            "videos": user_videos,
            "analytics": user_analytics
        }
    
    tasks = [process_user(user_id) for user_id in user_ids]
    return await async_optimizer.run_concurrent(tasks, max_concurrent=50)
```

#### **Batch Processing**
```python
async def process_video_batch(video_ids: List[str]) -> List[Dict[str, Any]]:
    """Process videos in batches."""
    async def process_video(video_id: str) -> Dict[str, Any]:
        # Process individual video
        video_data = await video_service.get_video(video_id)
        processed_data = await video_processor.process(video_data)
        return processed_data
    
    return await async_optimizer.run_batch(
        items=video_ids,
        processor=process_video,
        batch_size=100,
        max_concurrent=20
    )
```

### Background Tasks

#### **Async Background Processing**
```python
from fastapi import BackgroundTasks
from api.optimization.performance_optimizer import monitor_performance

@monitor_performance("background_video_processing")
async def process_video_background(video_id: str):
    """Process video in background."""
    try:
        # Get video data
        video_data = await video_service.get_video(video_id)
        
        # Process video
        processed_video = await video_processor.process(video_data)
        
        # Update database
        await video_service.update_video(video_id, processed_video)
        
        # Send notification
        await notification_service.send_video_ready_notification(video_id)
        
    except Exception as e:
        logger.error(f"Background video processing failed: {e}")
        await notification_service.send_error_notification(video_id, str(e))

# Use in endpoint
@router.post("/videos/{video_id}/process")
async def process_video(
    video_id: str,
    background_tasks: BackgroundTasks
):
    """Start video processing in background."""
    background_tasks.add_task(process_video_background, video_id)
    return {"message": "Video processing started", "video_id": video_id}
```

## 📊 Performance Monitoring

### Overview

Performance monitoring tracks metrics and provides insights for optimization.

### Performance Optimizer

#### **Main Performance Optimizer**
```python
from api.optimization.performance_optimizer import (
    PerformanceOptimizer, OptimizationLevel
)

# Initialize performance optimizer
optimizer = PerformanceOptimizer(
    redis_url="redis://localhost:6379",
    database_url="postgresql+asyncpg://user:pass@localhost/db",
    optimization_level=OptimizationLevel.STANDARD,
    memory_cache_size=1000,
    database_pool_size=20,
    max_metrics=10000
)

# Get performance report
report = optimizer.get_performance_report()
print(f"Cache hit rate: {report['cache_stats']['memory_hit_rate']:.2%}")
print(f"Database queries: {report['database_stats']['total_queries']}")
print(f"Average response time: {report['performance_stats']['average_duration_ms']:.2f}ms")
```

#### **Health Check**
```python
# Perform health check
health_status = await optimizer.health_check()
for component, status in health_status.items():
    print(f"{component}: {status}")

# Example output:
# cache_manager: healthy
# database_optimizer: healthy
# query_optimizer: healthy
# performance_monitor: healthy
```

### Metrics Collection

#### **Custom Metrics**
```python
from api.optimization.performance_optimizer import PerformanceMonitor

monitor = PerformanceMonitor(max_metrics=10000)

# Record custom metrics
monitor.record_operation(
    operation="video_processing",
    duration_ms=1500.0,
    cache_hits=2,
    cache_misses=1,
    database_queries=5,
    database_time_ms=800.0,
    memory_usage_mb=50.0
)

# Get operation statistics
stats = monitor.get_operation_stats("video_processing")
print(f"Average processing time: {stats['average_duration_ms']:.2f}ms")
print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")
```

#### **Endpoint Monitoring**
```python
from api.optimization.performance_optimizer import optimize_endpoint

@optimize_endpoint(cache_ttl=300, cache_strategy=CacheStrategy.HYBRID, monitor=True)
async def get_user_videos(
    request: Request,
    user_id: str,
    optimizer: PerformanceOptimizer = Depends(get_performance_optimizer)
):
    """Get user videos with performance optimization."""
    videos = await video_service.get_user_videos(user_id)
    return {"videos": videos, "count": len(videos)}
```

## 🔗 Integration Examples

### FastAPI Application Setup

#### **Main Application Configuration**
```python
from fastapi import FastAPI, Depends
from api.optimization.performance_optimizer import PerformanceOptimizer
from api.optimization.connection_pooling import ConnectionPoolManager

app = FastAPI(title="HeyGen AI API")

# Initialize performance optimizer
@app.on_event("startup")
async def startup_event():
    # Initialize connection pools
    pool_manager = ConnectionPoolManager()
    
    # Add database pool
    db_config = ConnectionConfig(
        url=os.getenv("DATABASE_URL"),
        pool_size=20,
        max_overflow=30
    )
    await pool_manager.add_pool("database", ConnectionType.DATABASE, db_config)
    
    # Add Redis pool
    redis_config = ConnectionConfig(
        url=os.getenv("REDIS_URL"),
        pool_size=10,
        max_overflow=20
    )
    await pool_manager.add_pool("redis", ConnectionType.REDIS, redis_config)
    
    # Store in app state
    app.state.pool_manager = pool_manager
    
    # Initialize performance optimizer
    optimizer = PerformanceOptimizer(
        redis_url=os.getenv("REDIS_URL"),
        database_url=os.getenv("DATABASE_URL"),
        optimization_level=OptimizationLevel.STANDARD
    )
    app.state.optimizer = optimizer

@app.on_event("shutdown")
async def shutdown_event():
    # Close all connection pools
    await app.state.pool_manager.close_all()
```

#### **Dependency Injection**
```python
def get_pool_manager() -> ConnectionPoolManager:
    """Get connection pool manager."""
    return app.state.pool_manager

def get_optimizer() -> PerformanceOptimizer:
    """Get performance optimizer."""
    return app.state.optimizer

# Use in endpoints
@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    pool_manager: ConnectionPoolManager = Depends(get_pool_manager),
    optimizer: PerformanceOptimizer = Depends(get_optimizer)
):
    """Get user with optimized performance."""
    # Get database pool
    db_pool = await pool_manager.get_pool("database")
    
    async with db_pool.get_session() as session:
        result = await session.execute(
            text("SELECT * FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )
        user = result.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return dict(user._mapping)
```

### Service Layer Integration

#### **Optimized User Service**
```python
class UserService:
    def __init__(self, pool_manager: ConnectionPoolManager, optimizer: PerformanceOptimizer):
        self.pool_manager = pool_manager
        self.optimizer = optimizer
    
    @cache_result(ttl=600, strategy=CacheStrategy.HYBRID)
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user with caching."""
        db_pool = await self.pool_manager.get_pool("database")
        
        async with db_pool.get_session() as session:
            result = await session.execute(
                text("SELECT * FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            )
            user = result.fetchone()
            
            if not user:
                raise ValueError("User not found")
            
            return dict(user._mapping)
    
    @monitor_performance("user_creation")
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user with performance monitoring."""
        db_pool = await self.pool_manager.get_pool("database")
        
        async with db_pool.get_session() as session:
            result = await session.execute(
                text("""
                    INSERT INTO users (email, first_name, last_name, created_at)
                    VALUES (:email, :first_name, :last_name, :created_at)
                    RETURNING *
                """),
                {
                    **user_data,
                    "created_at": datetime.now(timezone.utc)
                }
            )
            user = result.fetchone()
            await session.commit()
            
            # Invalidate cache
            await self.optimizer.cache_manager.delete(f"user:{user['id']}")
            
            return dict(user._mapping)
```

#### **Optimized Video Service**
```python
class VideoService:
    def __init__(self, pool_manager: ConnectionPoolManager, optimizer: PerformanceOptimizer):
        self.pool_manager = pool_manager
        self.optimizer = optimizer
    
    async def get_user_videos(
        self,
        user_id: str,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get user videos with pagination and caching."""
        cache_key = f"user:{user_id}:videos:{page}:{per_page}"
        
        # Try cache first
        cached_result = await self.optimizer.cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        # Query database
        db_pool = await self.pool_manager.get_pool("database")
        
        async with db_pool.get_session() as session:
            # Get total count
            count_result = await session.execute(
                text("SELECT COUNT(*) FROM videos WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            total = count_result.scalar()
            
            # Get videos
            offset = (page - 1) * per_page
            videos_result = await session.execute(
                text("""
                    SELECT v.*, u.name as user_name
                    FROM videos v
                    JOIN users u ON v.user_id = u.id
                    WHERE v.user_id = :user_id
                    ORDER BY v.created_at DESC
                    LIMIT :limit OFFSET :offset
                """),
                {"user_id": user_id, "limit": per_page, "offset": offset}
            )
            videos = [dict(row._mapping) for row in videos_result.fetchall()]
            
            result = {
                "videos": videos,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            }
            
            # Cache result
            await self.optimizer.cache_manager.set(cache_key, result, ttl=300)
            
            return result
```

## 🏆 Best Practices

### 1. Caching Strategy

#### **Cache Key Design**
```python
# ✅ Good: Descriptive cache keys
cache_keys = {
    "user_profile": f"user:{user_id}:profile",
    "user_videos": f"user:{user_id}:videos",
    "video_analytics": f"video:{video_id}:analytics",
    "search_results": f"search:{query_hash}:page:{page}"
}

# ❌ Bad: Generic cache keys
cache_keys = {
    "user_data": f"data:{user_id}",
    "video_data": f"data:{video_id}"
}
```

#### **Cache TTL Strategy**
```python
# Different TTL for different data types
CACHE_TTL = {
    "user_profile": 1800,      # 30 minutes
    "user_videos": 300,        # 5 minutes
    "video_analytics": 3600,   # 1 hour
    "search_results": 60,      # 1 minute
    "static_data": 86400       # 24 hours
}

@cache_result(ttl=CACHE_TTL["user_profile"])
async def get_user_profile(user_id: str):
    return await user_service.get_profile(user_id)
```

### 2. Database Optimization

#### **Query Optimization**
```python
# ✅ Good: Optimized queries with indexes
async def get_user_videos_optimized(user_id: str):
    query = """
        SELECT v.id, v.title, v.status, v.created_at
        FROM videos v
        WHERE v.user_id = :user_id AND v.status = 'completed'
        ORDER BY v.created_at DESC
        LIMIT 50
    """
    return await db_pool.execute_query(query, {"user_id": user_id})

# ❌ Bad: Inefficient queries
async def get_user_videos_inefficient(user_id: str):
    query = """
        SELECT * FROM videos
        WHERE user_id = :user_id
    """
    return await db_pool.execute_query(query, {"user_id": user_id})
```

#### **Connection Management**
```python
# ✅ Good: Proper connection management
async def get_user_data(user_id: str):
    async with db_pool.get_session() as session:
        result = await session.execute(
            text("SELECT * FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )
        return dict(result.fetchone()._mapping)

# ❌ Bad: Manual connection management
async def get_user_data_bad(user_id: str):
    session = db_pool.session_factory()
    try:
        result = await session.execute(
            text("SELECT * FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )
        return dict(result.fetchone()._mapping)
    finally:
        await session.close()
```

### 3. Async Processing

#### **Concurrent Execution**
```python
# ✅ Good: Controlled concurrency
async def process_multiple_users(user_ids: List[str]):
    async def process_user(user_id: str):
        return await user_service.process_user(user_id)
    
    return await async_optimizer.run_concurrent(
        [process_user(uid) for uid in user_ids],
        max_concurrent=50
    )

# ❌ Bad: Uncontrolled concurrency
async def process_multiple_users_bad(user_ids: List[str]):
    tasks = [user_service.process_user(uid) for uid in user_ids]
    return await asyncio.gather(*tasks)  # No concurrency limit
```

#### **Batch Processing**
```python
# ✅ Good: Efficient batch processing
async def process_videos_batch(video_ids: List[str]):
    return await async_optimizer.run_batch(
        items=video_ids,
        processor=video_service.process_video,
        batch_size=100,
        max_concurrent=20
    )

# ❌ Bad: Inefficient processing
async def process_videos_bad(video_ids: List[str]):
    results = []
    for video_id in video_ids:
        result = await video_service.process_video(video_id)
        results.append(result)
    return results
```

### 4. Error Handling

#### **Graceful Degradation**
```python
async def get_user_data_with_fallback(user_id: str):
    """Get user data with cache fallback."""
    try:
        # Try database first
        user_data = await user_service.get_user(user_id)
        return user_data
    except Exception as e:
        logger.warning(f"Database error, trying cache: {e}")
        
        try:
            # Fallback to cache
            cached_data = await cache_manager.get(f"user:{user_id}")
            if cached_data:
                return cached_data
        except Exception as cache_error:
            logger.error(f"Cache error: {cache_error}")
        
        # Return default data
        return {"id": user_id, "error": "Data unavailable"}
```

#### **Retry Logic**
```python
async def make_api_request_with_retry(url: str, max_retries: int = 3):
    """Make API request with retry logic."""
    for attempt in range(max_retries):
        try:
            response = await http_pool.get(url)
            return await response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff
            delay = 2 ** attempt
            await asyncio.sleep(delay)
```

## 🔧 Troubleshooting

### Common Issues

#### **High Memory Usage**
```python
# Monitor memory usage
import psutil
import gc

def check_memory_usage():
    """Check current memory usage."""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    logger.info(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
    
    if memory_info.rss > 1024 * 1024 * 1024:  # 1GB
        logger.warning("High memory usage detected")
        gc.collect()  # Force garbage collection

# Use in performance monitoring
@monitor_performance("memory_check")
async def check_system_health():
    check_memory_usage()
```

#### **Slow Database Queries**
```python
# Monitor slow queries
async def monitor_database_performance():
    """Monitor database performance."""
    db_pool = await pool_manager.get_pool("database")
    stats = db_pool.get_stats()
    
    if stats["average_time_ms"] > 1000:
        logger.warning(f"Slow database queries detected: {stats['average_time_ms']:.2f}ms")
    
    if stats["slow_queries"] > 10:
        logger.error(f"Too many slow queries: {stats['slow_queries']}")
```

#### **Cache Performance Issues**
```python
# Monitor cache performance
async def monitor_cache_performance():
    """Monitor cache performance."""
    cache_stats = optimizer.cache_manager.get_stats()
    
    if cache_stats["memory_hit_rate"] < 0.8:
        logger.warning(f"Low memory cache hit rate: {cache_stats['memory_hit_rate']:.2%}")
    
    if cache_stats["redis_hit_rate"] < 0.7:
        logger.warning(f"Low Redis cache hit rate: {cache_stats['redis_hit_rate']:.2%}")
```

### Performance Tuning

#### **Optimization Levels**
```python
# Adjust optimization level based on environment
if os.getenv("ENVIRONMENT") == "production":
    optimization_level = OptimizationLevel.AGGRESSIVE
elif os.getenv("ENVIRONMENT") == "development":
    optimization_level = OptimizationLevel.BASIC
else:
    optimization_level = OptimizationLevel.STANDARD

optimizer = PerformanceOptimizer(
    optimization_level=optimization_level,
    memory_cache_size=2000 if optimization_level == OptimizationLevel.AGGRESSIVE else 1000
)
```

#### **Connection Pool Tuning**
```python
# Tune connection pools based on load
if os.getenv("HIGH_LOAD") == "true":
    db_config = ConnectionConfig(
        url=os.getenv("DATABASE_URL"),
        pool_size=50,  # Increased for high load
        max_overflow=100,
        pool_timeout=60
    )
else:
    db_config = ConnectionConfig(
        url=os.getenv("DATABASE_URL"),
        pool_size=20,  # Standard size
        max_overflow=30,
        pool_timeout=30
    )
```

## 📈 Expected Performance Improvements

### 1. Response Time Reduction
- **Caching**: 70-90% reduction for frequently accessed data
- **Connection Pooling**: 50-80% reduction in connection overhead
- **Query Optimization**: 30-60% reduction in database query time
- **Async Processing**: 60-80% reduction for concurrent operations

### 2. Throughput Increase
- **Connection Pooling**: 3-5x increase in concurrent requests
- **Async Processing**: 2-4x increase in processing capacity
- **Caching**: 5-10x increase for cached endpoints

### 3. Resource Utilization
- **Memory Usage**: 20-40% reduction through efficient caching
- **Database Connections**: 50-70% reduction through pooling
- **CPU Usage**: 30-50% reduction through optimized queries

### 4. Scalability
- **Horizontal Scaling**: Better support for multiple instances
- **Load Distribution**: Improved handling of traffic spikes
- **Resource Efficiency**: More efficient use of available resources

This comprehensive performance optimization system provides your HeyGen AI API with:
- **Multi-level caching** for optimal data access
- **Efficient connection pooling** for all external services
- **Async processing** for concurrent operations
- **Comprehensive monitoring** for performance insights
- **Automatic optimization** based on usage patterns
- **Graceful degradation** for improved reliability

The system is designed to scale with your application while maintaining optimal performance across all components. 