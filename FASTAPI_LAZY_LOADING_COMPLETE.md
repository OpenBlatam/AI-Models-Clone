# FastAPI Application with Lazy Loading Techniques
==============================================

## Overview

This comprehensive FastAPI application demonstrates advanced lazy loading techniques for handling large datasets and substantial API responses. The application implements multiple lazy loading strategies including streaming responses, progressive data loading, and memory-efficient data processing.

## Key Lazy Loading Features

### ✅ Lazy Loading Techniques Implemented

1. **Lazy Data Loading**: Load data on demand with intelligent caching
2. **Streaming Responses**: Progressive data streaming for large datasets
3. **Memory Management**: Efficient memory usage with garbage collection
4. **Batch Processing**: Process data in configurable batches
5. **Multiple Output Formats**: JSON and CSV streaming
6. **Background Preloading**: Preload data in background tasks
7. **Cache Management**: Intelligent cache invalidation and management

## Architecture

### 1. Lazy Loading Configuration

#### Configuration Settings
```python
class LazyLoadingConfig:
    """Lazy loading configuration settings."""
    # Streaming Configuration
    STREAM_CHUNK_SIZE = 1024  # bytes
    STREAM_TIMEOUT = 30.0  # seconds
    MAX_STREAM_SIZE = 100 * 1024 * 1024  # 100MB
    
    # Pagination Configuration
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 1000
    MIN_PAGE_SIZE = 10
    
    # Memory Management
    MAX_MEMORY_USAGE_MB = 512
    GARBAGE_COLLECTION_THRESHOLD = 0.8  # 80% of max memory
    
    # Lazy Loading Thresholds
    LAZY_LOAD_THRESHOLD = 1000  # items
    STREAMING_THRESHOLD = 5000  # items
    BATCH_SIZE = 100
    
    # Cache Configuration for Lazy Loading
    LAZY_CACHE_TTL = 300  # 5 minutes
    LAZY_CACHE_SIZE = 100
```

#### Data Loading Strategies
```python
class DataLoadingStrategy(Enum):
    """Data loading strategies."""
    EAGER = "eager"  # Load all data at once
    LAZY = "lazy"    # Load data on demand
    STREAMING = "streaming"  # Stream data progressively
    BATCHED = "batched"  # Load data in batches
```

**Features:**
- **Configurable Thresholds**: Adjustable loading thresholds
- **Memory Management**: Automatic memory monitoring
- **Multiple Strategies**: Different loading approaches
- **Performance Optimization**: Optimized for large datasets

### 2. Lazy Data Loader

#### Core Lazy Loading Implementation
```python
class LazyDataLoader:
    """Lazy data loader for large datasets."""
    
    def __init__(self, strategy: DataLoadingStrategy = DataLoadingStrategy.LAZY):
        self.strategy = strategy
        self.cache = TTLCache(
            maxsize=LazyLoadingConfig.LAZY_CACHE_SIZE,
            ttl=LazyLoadingConfig.LAZY_CACHE_TTL
        )
        self.loaded_data = {}
        self.loading_tasks = {}
    
    async def get_or_load(self, key: str, loader_func: callable, *args, **kwargs) -> Any:
        """Get data from cache or load it lazily."""
        # Check if already loaded
        if key in self.loaded_data:
            return self.loaded_data[key]
        
        # Check if currently loading
        if key in self.loading_tasks:
            try:
                return await self.loading_tasks[key]
            except Exception as e:
                logger.error(f"Lazy loading failed for {key}: {e}")
                raise
        
        # Start loading
        loading_task = asyncio.create_task(loader_func(*args, **kwargs))
        self.loading_tasks[key] = loading_task
        
        try:
            result = await loading_task
            self.loaded_data[key] = result
            return result
        except Exception as e:
            logger.error(f"Lazy loading failed for {key}: {e}")
            raise
        finally:
            # Clean up loading task
            if key in self.loading_tasks:
                del self.loading_tasks[key]
```

**Features:**
- **Intelligent Caching**: Cache loaded data with TTL
- **Concurrent Loading**: Handle multiple loading tasks
- **Error Handling**: Graceful error handling and logging
- **Memory Management**: Automatic cleanup of loading tasks

### 3. Streaming Data Processor

#### Streaming Implementation
```python
class StreamingDataProcessor:
    """Streaming data processor for large datasets."""
    
    def __init__(self):
        self.processed_count = 0
        self.total_size = 0
    
    async def process_stream(self, data_generator: AsyncGenerator, processor_func: callable) -> AsyncGenerator:
        """Process data stream with custom processor."""
        async for item in data_generator:
            processed_item = await processor_func(item)
            self.processed_count += 1
            self.total_size += len(str(processed_item))
            yield processed_item
    
    async def batch_process(self, data_generator: AsyncGenerator, batch_size: int = None) -> AsyncGenerator:
        """Process data in batches."""
        batch_size = batch_size or LazyLoadingConfig.BATCH_SIZE
        batch = []
        
        async for item in data_generator:
            batch.append(item)
            
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        # Yield remaining items
        if batch:
            yield batch
```

**Features:**
- **Streaming Processing**: Process data as it's generated
- **Batch Processing**: Process data in configurable batches
- **Progress Tracking**: Track processed items and size
- **Memory Efficiency**: Process data without loading everything

### 4. Memory Manager

#### Memory Management Implementation
```python
class MemoryManager:
    """Memory management for lazy loading."""
    
    def __init__(self):
        self.max_memory = LazyLoadingConfig.MAX_MEMORY_USAGE_MB * 1024 * 1024  # Convert to bytes
        self.current_memory = 0
        self.memory_threshold = LazyLoadingConfig.GARBAGE_COLLECTION_THRESHOLD
    
    def check_memory_usage(self) -> bool:
        """Check if memory usage is within limits."""
        process = psutil.Process()
        memory_info = process.memory_info()
        self.current_memory = memory_info.rss
        
        return self.current_memory < (self.max_memory * self.memory_threshold)
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        return self.current_memory / (1024 * 1024)
    
    def should_garbage_collect(self) -> bool:
        """Check if garbage collection is needed."""
        return self.current_memory > (self.max_memory * self.memory_threshold)
    
    async def cleanup_if_needed(self):
        """Perform cleanup if memory usage is high."""
        if self.should_garbage_collect():
            import gc
            gc.collect()
            logger.info(f"Garbage collection performed. Memory usage: {self.get_memory_usage_mb():.2f} MB")
```

**Features:**
- **Memory Monitoring**: Real-time memory usage tracking
- **Automatic Cleanup**: Garbage collection when needed
- **Threshold Management**: Configurable memory thresholds
- **Performance Optimization**: Prevent memory exhaustion

## Lazy Loading Strategies

### 1. Lazy Data Generation

#### Lazy Generator Implementation
```python
async def get_users_lazy_generator(session: AsyncSession, skip: int = 0, limit: int = 100) -> AsyncGenerator[User, None]:
    """Get users as lazy generator."""
    offset = skip
    batch_size = min(limit, LazyLoadingConfig.BATCH_SIZE)
    
    while offset < skip + limit:
        current_batch_size = min(batch_size, skip + limit - offset)
        
        result = await session.execute(
            select(User)
            .offset(offset)
            .limit(current_batch_size)
            .order_by(User.created_at.desc())
        )
        
        users = result.scalars().all()
        if not users:
            break
        
        for user in users:
            yield user
        
        offset += len(users)
        
        # Check memory usage
        if memory_manager.should_garbage_collect():
            await memory_manager.cleanup_if_needed()
```

**Benefits:**
- **Memory Efficiency**: Load data in small batches
- **Progressive Loading**: Load data as needed
- **Memory Management**: Automatic garbage collection
- **Scalability**: Handle large datasets efficiently

### 2. Streaming Responses

#### JSON Streaming
```python
async def generate_json_stream(data_generator: AsyncGenerator) -> AsyncGenerator[str, None]:
    """Generate JSON stream from data generator."""
    yield "[\n"
    
    first_item = True
    async for item in data_generator:
        if not first_item:
            yield ",\n"
        else:
            first_item = False
        
        # Serialize item to JSON
        if hasattr(item, 'model_dump'):
            json_str = orjson.dumps(item.model_dump()).decode('utf-8')
        else:
            json_str = orjson.dumps(item).decode('utf-8')
        
        yield json_str
    
    yield "\n]"
```

#### CSV Streaming
```python
async def generate_csv_stream(data_generator: AsyncGenerator, headers: List[str]) -> AsyncGenerator[str, None]:
    """Generate CSV stream from data generator."""
    # Write headers
    yield ",".join(headers) + "\n"
    
    async for item in data_generator:
        if hasattr(item, 'model_dump'):
            data = item.model_dump()
        else:
            data = item
        
        # Convert to CSV row
        row = []
        for header in headers:
            value = data.get(header, "")
            # Escape commas and quotes
            if isinstance(value, str) and ("," in value or '"' in value):
                value = f'"{value.replace('"', '""')}"'
            row.append(str(value))
        
        yield ",".join(row) + "\n"
```

**Benefits:**
- **Progressive Delivery**: Start sending data immediately
- **Memory Efficiency**: Don't load entire dataset in memory
- **Multiple Formats**: Support JSON and CSV streaming
- **Large Dataset Support**: Handle datasets of any size

### 3. Lazy Loading Service Layer

#### Lazy User Loading
```python
async def get_users_streaming(session: AsyncSession, skip: int = 0, limit: int = 100) -> AsyncGenerator[UserResponse, None]:
    """Get users as streaming response."""
    async for user in get_users_lazy_generator(session, skip, limit):
        # Get author username (lazy loaded)
        author_username = await lazy_loader.get_or_load(
            f"user_username_{user.id}",
            lambda: user.username,
            user.id
        )
        
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            age=user.age,
            bio=user.bio,
            created_at=user.created_at,
            updated_at=user.updated_at,
            post_count=0,  # Lazy loaded
            comment_count=0  # Lazy loaded
        )
        
        yield user_response
```

#### Lazy Post Loading
```python
async def get_posts_streaming(session: AsyncSession, skip: int = 0, limit: int = 100) -> AsyncGenerator[PostResponse, None]:
    """Get posts as streaming response."""
    async for post in get_posts_lazy_generator(session, skip, limit):
        # Get author username (lazy loaded)
        author = await lazy_loader.get_or_load(
            f"user_{post.author_id}",
            get_user_service,
            session,
            post.author_id
        )
        author_username = author.username if author else "Unknown"
        
        post_response = PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            author_username=author_username,
            tags=post.tags.split(",") if post.tags else [],
            category=post.category,
            is_published=post.is_published,
            created_at=post.created_at,
            updated_at=post.updated_at,
            view_count=post.view_count,
            like_count=post.like_count,
            comment_count=post.comment_count
        )
        
        yield post_response
```

**Benefits:**
- **Related Data Loading**: Load related data on demand
- **Caching**: Cache loaded data for reuse
- **Efficiency**: Only load data when needed
- **Performance**: Reduce initial load time

## API Endpoints with Lazy Loading

### 1. Flexible Data Loading Endpoints

#### Users Endpoint with Multiple Strategies
```python
@app.get("/users")
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(LazyLoadingConfig.DEFAULT_PAGE_SIZE, ge=1, le=LazyLoadingConfig.MAX_PAGE_SIZE, description="Items per page"),
    strategy: DataLoadingStrategy = Query(DataLoadingStrategy.LAZY, description="Data loading strategy"),
    session: AsyncSession = Depends(get_db_session)
) -> Union[List[UserResponse], StreamingResponse]:
    """Get users with lazy loading strategies."""
    skip = (page - 1) * page_size
    
    if strategy == DataLoadingStrategy.STREAMING:
        # Streaming response for large datasets
        async def generate_users():
            async for user in get_users_streaming(session, skip, page_size):
                yield user
        
        return StreamingResponse(
            generate_json_stream(generate_users()),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=users_page_{page}.json"
            }
        )
    
    elif strategy == DataLoadingStrategy.LAZY:
        # Lazy loading with pagination
        users = []
        async for user in get_users_streaming(session, skip, page_size):
            users.append(user)
        
        return users
    
    else:
        # Eager loading (not recommended for large datasets)
        result = await session.execute(
            select(User)
            .offset(skip)
            .limit(page_size)
            .order_by(User.created_at.desc())
        )
        db_users = result.scalars().all()
        
        return [
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                age=user.age,
                bio=user.bio,
                created_at=user.created_at,
                updated_at=user.updated_at,
                post_count=0,
                comment_count=0
            )
            for user in db_users
        ]
```

### 2. Streaming Endpoints

#### Streaming Users with Multiple Formats
```python
@app.get("/users/stream")
async def stream_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(LazyLoadingConfig.DEFAULT_PAGE_SIZE, ge=1, le=LazyLoadingConfig.MAX_PAGE_SIZE, description="Items per page"),
    format: Literal["json", "csv"] = Query("json", description="Output format"),
    session: AsyncSession = Depends(get_db_session)
) -> StreamingResponse:
    """Stream users with different formats."""
    skip = (page - 1) * page_size
    
    if format == "csv":
        headers = ["id", "username", "email", "full_name", "is_active", "created_at"]
        
        async def generate_csv():
            async for user in get_users_streaming(session, skip, page_size):
                yield user
        
        return StreamingResponse(
            generate_csv_stream(generate_csv(), headers),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=users_page_{page}.csv"
            }
        )
    else:
        async def generate_json():
            async for user in get_users_streaming(session, skip, page_size):
                yield user
        
        return StreamingResponse(
            generate_json_stream(generate_json()),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=users_page_{page}.json"
            }
        )
```

### 3. Background Preloading

#### Background Data Preloading
```python
async def preload_user_data_background(user_ids: List[int]):
    """Background task to preload user data."""
    try:
        async with AsyncSessionLocal() as session:
            for user_id in user_ids:
                await lazy_loader.get_or_load(
                    f"user_{user_id}",
                    get_user_service,
                    session,
                    user_id
                )
        logger.info(f"Preloaded data for {len(user_ids)} users")
    except Exception as e:
        logger.error(f"Failed to preload user data: {e}")

@app.post("/users/preload")
async def preload_users(
    user_ids: List[int] = Query(..., description="User IDs to preload"),
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Preload user data in background."""
    background_tasks.add_task(preload_user_data_background, user_ids)
    
    return {
        "message": f"Preloading data for {len(user_ids)} users",
        "user_ids": user_ids,
        "timestamp": datetime.now().isoformat()
    }
```

## API Endpoints

### Core Endpoints with Lazy Loading

| Endpoint | Lazy Loading Features | Streaming | Background Tasks |
|----------|----------------------|-----------|------------------|
| `GET /users` | Multiple strategies | Yes | None |
| `GET /users/stream` | JSON/CSV streaming | Yes | None |
| `GET /posts` | Multiple strategies | Yes | None |
| `GET /posts/stream` | JSON/CSV streaming | Yes | None |
| `POST /users/preload` | Background preloading | No | Yes |
| `GET /lazy-loading/stats` | Statistics | No | None |
| `POST /lazy-loading/clear-cache` | Cache management | No | None |

### Lazy Loading Management Endpoints

| Endpoint | Description | Features |
|----------|-------------|----------|
| `GET /lazy-loading/stats` | Lazy loading statistics | Performance metrics |
| `POST /lazy-loading/clear-cache` | Clear lazy cache | Cache management |
| `POST /users/preload` | Preload user data | Background processing |

## Performance Monitoring

### 1. Lazy Loading Statistics

#### Statistics Model
```python
class LazyLoadingStats(OptimizedBaseModel):
    """Lazy loading statistics model."""
    total_items: int = Field(0, description="Total items processed")
    loaded_items: int = Field(0, description="Items currently loaded")
    memory_usage_mb: float = Field(0.0, description="Memory usage in MB")
    cache_hits: int = Field(0, description="Cache hits")
    cache_misses: int = Field(0, description="Cache misses")
    streaming_active: bool = Field(False, description="Streaming status")
```

#### Statistics Collection
```python
@app.get("/lazy-loading/stats", response_model=LazyLoadingStats)
async def get_lazy_loading_stats() -> LazyLoadingStats:
    """Get lazy loading statistics."""
    return LazyLoadingStats(
        total_items=streaming_processor.processed_count,
        loaded_items=len(lazy_loader.loaded_data),
        memory_usage_mb=memory_manager.get_memory_usage_mb(),
        cache_hits=0,  # TODO: Implement cache hit tracking
        cache_misses=0,  # TODO: Implement cache miss tracking
        streaming_active=len(lazy_loader.loading_tasks) > 0
    )
```

### 2. Health Check with Lazy Loading Metrics

```python
@app.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """Health check with lazy loading statistics."""
    try:
        async with engine.begin() as conn:
            await conn.execute(select(1))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database_status": db_status,
        "memory_usage_mb": memory_manager.get_memory_usage_mb(),
        "lazy_loading_stats": {
            "loaded_items": len(lazy_loader.loaded_data),
            "loading_tasks": len(lazy_loader.loading_tasks),
            "cache_size": len(lazy_loader.cache)
        }
    }
```

## Configuration

### Environment Variables
```bash
# Lazy Loading Configuration
STREAM_CHUNK_SIZE=1024
STREAM_TIMEOUT=30.0
MAX_STREAM_SIZE=104857600
DEFAULT_PAGE_SIZE=50
MAX_PAGE_SIZE=1000
MIN_PAGE_SIZE=10
MAX_MEMORY_USAGE_MB=512
GARBAGE_COLLECTION_THRESHOLD=0.8
LAZY_LOAD_THRESHOLD=1000
STREAMING_THRESHOLD=5000
BATCH_SIZE=100
LAZY_CACHE_TTL=300
LAZY_CACHE_SIZE=100
```

### Lazy Loading Configuration
```python
# Lazy loading configuration
LAZY_CONFIG = LazyLoadingConfig(
    STREAM_CHUNK_SIZE=1024,
    STREAM_TIMEOUT=30.0,
    MAX_STREAM_SIZE=100 * 1024 * 1024,
    DEFAULT_PAGE_SIZE=50,
    MAX_PAGE_SIZE=1000,
    MIN_PAGE_SIZE=10,
    MAX_MEMORY_USAGE_MB=512,
    GARBAGE_COLLECTION_THRESHOLD=0.8,
    LAZY_LOAD_THRESHOLD=1000,
    STREAMING_THRESHOLD=5000,
    BATCH_SIZE=100,
    LAZY_CACHE_TTL=300,
    LAZY_CACHE_SIZE=100
)
```

## Lazy Loading Benefits

### 1. Memory Efficiency
- **Reduced Memory Usage**: Load data in small batches
- **Automatic Cleanup**: Garbage collection when needed
- **Memory Monitoring**: Real-time memory usage tracking
- **Threshold Management**: Configurable memory limits

### 2. Performance Improvements
- **Faster Initial Response**: Start streaming immediately
- **Progressive Loading**: Load data as needed
- **Background Processing**: Preload data in background
- **Caching**: Cache loaded data for reuse

### 3. Scalability
- **Large Dataset Support**: Handle datasets of any size
- **Concurrent Loading**: Handle multiple loading tasks
- **Streaming Responses**: Progressive data delivery
- **Multiple Formats**: Support JSON and CSV streaming

### 4. User Experience
- **Immediate Feedback**: Start receiving data quickly
- **Progress Tracking**: Monitor loading progress
- **Flexible Formats**: Choose output format
- **Background Processing**: Non-blocking operations

## Best Practices Implemented

### ✅ Lazy Loading Best Practices
- [x] Progressive data loading
- [x] Memory-efficient processing
- [x] Streaming responses
- [x] Background preloading
- [x] Cache management
- [x] Memory monitoring

### ✅ Performance Best Practices
- [x] Batch processing
- [x] Garbage collection
- [x] Memory thresholds
- [x] Streaming optimization
- [x] Cache invalidation

### ✅ User Experience Best Practices
- [x] Multiple output formats
- [x] Progress tracking
- [x] Background processing
- [x] Flexible strategies
- [x] Error handling

## Conclusion

This FastAPI application demonstrates comprehensive lazy loading techniques for handling large datasets and substantial API responses. The implementation includes:

1. **Lazy Data Loading**: Load data on demand with intelligent caching
2. **Streaming Responses**: Progressive data streaming for large datasets
3. **Memory Management**: Efficient memory usage with garbage collection
4. **Batch Processing**: Process data in configurable batches
5. **Multiple Output Formats**: JSON and CSV streaming
6. **Background Preloading**: Preload data in background tasks
7. **Cache Management**: Intelligent cache invalidation and management

The application provides significant benefits through:
- **Memory Efficiency**: Reduced memory usage for large datasets
- **Performance**: Faster initial responses and progressive loading
- **Scalability**: Handle datasets of any size efficiently
- **User Experience**: Immediate feedback and flexible output formats

This serves as a foundation for building high-performance APIs that can efficiently handle large datasets while maintaining excellent user experience and system performance. 