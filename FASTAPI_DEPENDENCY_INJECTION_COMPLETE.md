# FastAPI Application with Dependency Injection System
==================================================

## Overview

This comprehensive FastAPI application demonstrates advanced dependency injection patterns for managing state and shared resources. The application implements FastAPI's dependency injection system to manage database connections, caching, lazy loading, memory management, and other shared resources efficiently.

## Key Dependency Injection Features

### ✅ Dependency Injection Patterns Implemented

1. **Shared Resources Management**: Centralized resource management through DI
2. **Database Session Management**: Dependency injection for database sessions
3. **Cache Management**: Redis and in-memory cache through DI
4. **Lazy Loading with DI**: Lazy loading components with dependency injection
5. **Memory Management**: Memory monitoring and cleanup through DI
6. **Configuration Management**: Centralized configuration through DI
7. **Statistics Collection**: Performance metrics through DI

## Architecture

### 1. Shared Resources Management

#### SharedResources Class
```python
class SharedResources:
    """Shared resources managed through dependency injection."""
    
    def __init__(self):
        self._engine = None
        self._redis_client = None
        self._cache = None
        self._lazy_loader = None
        self._memory_manager = None
        self._streaming_processor = None
        self._logger = None
        self._config = None
    
    @property
    def engine(self):
        """Get database engine."""
        if self._engine is None:
            self._engine = create_async_engine(
                DependencyConfig.DATABASE_URL,
                echo=False,
                poolclass=QueuePool,
                pool_size=DependencyConfig.DB_POOL_SIZE,
                max_overflow=DependencyConfig.DB_MAX_OVERFLOW,
                pool_timeout=DependencyConfig.DB_POOL_TIMEOUT,
                pool_recycle=DependencyConfig.DB_POOL_RECYCLE,
                future=True
            )
        return self._engine
    
    @property
    def redis_client(self):
        """Get Redis client."""
        if self._redis_client is None:
            self._redis_client = aioredis.from_url(
                DependencyConfig.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=DependencyConfig.REDIS_POOL_SIZE,
                socket_timeout=DependencyConfig.REDIS_TIMEOUT
            )
        return self._redis_client
```

**Features:**
- **Lazy Initialization**: Resources are created only when needed
- **Singleton Pattern**: Each resource is created only once
- **Centralized Management**: All shared resources in one place
- **Dependency Injection**: Resources injected into components

### 2. Dependency Injection Functions

#### Core Dependency Functions
```python
async def get_shared_resources() -> SharedResources:
    """Dependency to get shared resources."""
    return shared_resources

async def get_database_engine():
    """Dependency to get database engine."""
    resources = await get_shared_resources()
    return resources.engine

async def get_redis_client():
    """Dependency to get Redis client."""
    resources = await get_shared_resources()
    return resources.redis_client

async def get_cache():
    """Dependency to get cache instance."""
    resources = await get_shared_resources()
    return resources.cache

async def get_lazy_loader():
    """Dependency to get lazy loader instance."""
    resources = await get_shared_resources()
    return resources.lazy_loader

async def get_memory_manager():
    """Dependency to get memory manager instance."""
    resources = await get_shared_resources()
    return resources.memory_manager
```

**Benefits:**
- **Consistent Access**: All components access resources the same way
- **Testability**: Easy to mock dependencies for testing
- **Resource Management**: Automatic resource lifecycle management
- **Performance**: Shared resources reduce initialization overhead

### 3. Database Session Management with DI

#### Database Session Dependency
```python
async def get_db_session(
    engine = Depends(get_database_engine)
) -> AsyncSession:
    """Get database session with dependency injection."""
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
        finally:
            await session.close()
```

**Features:**
- **Automatic Cleanup**: Sessions are automatically closed
- **Error Handling**: Proper error handling and rollback
- **Connection Pooling**: Efficient connection management
- **Dependency Injection**: Engine injected from shared resources

### 4. Lazy Loading with Dependency Injection

#### LazyDataLoader with DI
```python
class LazyDataLoader:
    """Lazy data loader with dependency injection."""
    
    def __init__(self):
        self.loaded_data = {}
        self.loading_tasks = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'loads': 0
        }
    
    async def get_or_load(
        self, 
        key: str, 
        loader_func: callable, 
        cache = Depends(get_cache),
        *args, 
        **kwargs
    ) -> Any:
        """Get data from cache or load it lazily."""
        # Check if already loaded
        if key in self.loaded_data:
            self.cache_stats['hits'] += 1
            return self.loaded_data[key]
        
        # Check cache
        if cache and key in cache:
            self.cache_stats['hits'] += 1
            cached_data = cache[key]
            self.loaded_data[key] = cached_data
            return cached_data
        
        self.cache_stats['misses'] += 1
        
        # Check if currently loading
        if key in self.loading_tasks:
            try:
                result = await self.loading_tasks[key]
                return result
            except Exception as e:
                logger.error(f"Lazy loading failed for {key}: {e}")
                raise
        
        # Start loading
        loading_task = asyncio.create_task(loader_func(*args, **kwargs))
        self.loading_tasks[key] = loading_task
        
        try:
            result = await loading_task
            self.loaded_data[key] = result
            
            # Cache the result
            if cache:
                cache[key] = result
            
            self.cache_stats['loads'] += 1
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
- **Cache Integration**: Uses injected cache for storage
- **Statistics Tracking**: Tracks cache hits, misses, and loads
- **Concurrent Loading**: Handles multiple loading tasks
- **Error Handling**: Graceful error handling and logging

### 5. Memory Management with DI

#### MemoryManager with DI
```python
class MemoryManager:
    """Memory manager with dependency injection."""
    
    def __init__(self, config = Depends(get_config)):
        self.max_memory = config.MAX_MEMORY_USAGE_MB * 1024 * 1024
        self.current_memory = 0
        self.memory_threshold = config.GARBAGE_COLLECTION_THRESHOLD
        self.memory_stats = {
            'cleanups_performed': 0,
            'total_memory_freed': 0,
            'peak_memory_usage': 0
        }
    
    def check_memory_usage(self) -> bool:
        """Check if memory usage is within limits."""
        process = psutil.Process()
        memory_info = process.memory_info()
        self.current_memory = memory_info.rss
        
        # Update peak memory usage
        if self.current_memory > self.memory_stats['peak_memory_usage']:
            self.memory_stats['peak_memory_usage'] = self.current_memory
        
        return self.current_memory < (self.max_memory * self.memory_threshold)
    
    async def cleanup_if_needed(self):
        """Perform cleanup if memory usage is high."""
        if self.should_garbage_collect():
            import gc
            memory_before = self.current_memory
            gc.collect()
            memory_after = psutil.Process().memory_info().rss
            
            freed_memory = memory_before - memory_after
            self.memory_stats['cleanups_performed'] += 1
            self.memory_stats['total_memory_freed'] += freed_memory
            
            logger.info(f"Garbage collection performed. Memory usage: {self.get_memory_usage_mb():.2f} MB, Freed: {freed_memory / (1024 * 1024):.2f} MB")
```

**Features:**
- **Configuration Injection**: Uses injected configuration
- **Statistics Tracking**: Tracks memory usage and cleanup
- **Automatic Cleanup**: Performs garbage collection when needed
- **Performance Monitoring**: Monitors memory usage in real-time

### 6. Service Layer with Dependency Injection

#### Service Functions with DI
```python
async def create_user_service(
    session: AsyncSession,
    user_data: UserCreateRequest,
    lazy_loader = Depends(get_lazy_loader),
    cache = Depends(get_cache)
) -> User:
    """Create user with dependency injection."""
    # Check if user already exists
    existing_user = await session.execute(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    )
    
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists"
        )
    
    # Create new user
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        is_active=user_data.is_active,
        age=user_data.age,
        bio=user_data.bio
    )
    
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    
    # Cache the new user
    if cache:
        cache[f"user_{db_user.id}"] = db_user
    
    return db_user

async def get_user_service(
    session: AsyncSession,
    user_id: int,
    lazy_loader = Depends(get_lazy_loader),
    cache = Depends(get_cache)
) -> Optional[User]:
    """Get user by ID with dependency injection."""
    # Try cache first
    if cache and f"user_{user_id}" in cache:
        return cache[f"user_{user_id}"]
    
    # Load from database
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    # Cache the result
    if user and cache:
        cache[f"user_{user_id}"] = user
    
    return user
```

**Features:**
- **Multiple Dependencies**: Inject multiple dependencies
- **Cache Integration**: Automatic caching of results
- **Database Integration**: Proper database session management
- **Error Handling**: Comprehensive error handling

### 7. Lifespan Context Manager with DI

#### Lifespan Management
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager with dependency injection."""
    # Startup
    logger.info("Starting application with dependency injection...")
    
    try:
        # Initialize shared resources
        resources = await get_shared_resources()
        
        # Initialize database
        async with resources.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
        
        # Check database connection
        async with resources.engine.begin() as conn:
            await conn.execute(select(1))
        logger.info("Database connection verified")
        
        # Initialize Redis connection
        await resources.redis_client.ping()
        logger.info("Redis connection verified")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Clear lazy loading cache
    resources = await get_shared_resources()
    resources.lazy_loader.clear_cache()
    
    # Close database connections
    await resources.engine.dispose()
    logger.info("Database connections closed")
    
    # Close Redis connection
    await resources.redis_client.close()
    logger.info("Redis connection closed")
    
    logger.info("Application shutdown completed")
```

**Features:**
- **Resource Initialization**: Initialize all shared resources
- **Connection Verification**: Verify database and Redis connections
- **Graceful Shutdown**: Proper cleanup of resources
- **Error Handling**: Comprehensive error handling during startup/shutdown

## API Endpoints with Dependency Injection

### 1. Health Check with DI

#### Health Check Endpoint
```python
@app.get("/health", response_model=Dict[str, Any])
async def health_check(
    shared_resources = Depends(get_shared_resources),
    memory_manager = Depends(get_memory_manager)
) -> Dict[str, Any]:
    """Health check with dependency injection."""
    try:
        async with shared_resources.engine.begin() as conn:
            await conn.execute(select(1))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    try:
        await shared_resources.redis_client.ping()
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database_status": db_status,
        "redis_status": redis_status,
        "memory_usage_mb": memory_manager.get_memory_usage_mb(),
        "dependency_stats": {
            "loaded_items": len(shared_resources.lazy_loader.loaded_data),
            "loading_tasks": len(shared_resources.lazy_loader.loading_tasks),
            "cache_size": len(shared_resources.cache)
        }
    }
```

### 2. User Management with DI

#### User Endpoints with DI
```python
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    session: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """Create user endpoint with dependency injection."""
    db_user = await create_user_service(session, user_data)
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        age=db_user.age,
        bio=db_user.bio,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at,
        post_count=0,
        comment_count=0
    )

@app.get("/users")
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    strategy: DataLoadingStrategy = Query(DataLoadingStrategy.LAZY, description="Data loading strategy"),
    session: AsyncSession = Depends(get_db_session),
    lazy_loader = Depends(get_lazy_loader),
    memory_manager = Depends(get_memory_manager)
) -> Union[List[UserResponse], StreamingResponse]:
    """Get users with dependency injection."""
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

### 3. Dependency Statistics with DI

#### Statistics Endpoint
```python
@app.get("/dependency-injection/stats", response_model=DependencyStats)
async def get_dependency_stats(
    lazy_loader = Depends(get_lazy_loader),
    memory_manager = Depends(get_memory_manager),
    streaming_processor = Depends(get_streaming_processor),
    cache = Depends(get_cache)
) -> DependencyStats:
    """Get dependency injection statistics."""
    return DependencyStats(
        lazy_loader_stats=lazy_loader.cache_stats,
        memory_manager_stats=memory_manager.memory_stats,
        streaming_processor_stats=streaming_processor.processing_stats,
        cache_stats={
            'size': len(cache) if cache else 0,
            'max_size': cache.maxsize if cache else 0
        },
        memory_usage_mb=memory_manager.get_memory_usage_mb()
    )
```

## Dependency Injection Benefits

### 1. Resource Management
- **Centralized Management**: All shared resources in one place
- **Lazy Initialization**: Resources created only when needed
- **Automatic Cleanup**: Proper resource lifecycle management
- **Connection Pooling**: Efficient connection management

### 2. Testability
- **Easy Mocking**: Dependencies can be easily mocked for testing
- **Isolated Testing**: Components can be tested in isolation
- **Dependency Override**: Easy to override dependencies for testing
- **Consistent Interface**: Same interface for real and mock dependencies

### 3. Performance
- **Shared Resources**: Reduce initialization overhead
- **Connection Reuse**: Reuse database and Redis connections
- **Caching**: Efficient caching with dependency injection
- **Memory Management**: Automatic memory monitoring and cleanup

### 4. Maintainability
- **Clear Dependencies**: Explicit dependency declarations
- **Modular Design**: Components are loosely coupled
- **Configuration Management**: Centralized configuration through DI
- **Error Handling**: Consistent error handling across components

## Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_POOL_SIZE=20
REDIS_TIMEOUT=5.0

# Cache Configuration
CACHE_TTL=300
CACHE_SIZE=1000
MEMORY_CACHE_SIZE=100

# Lazy Loading Configuration
LAZY_LOAD_THRESHOLD=1000
STREAMING_THRESHOLD=5000
BATCH_SIZE=100

# Memory Management
MAX_MEMORY_USAGE_MB=512
GARBAGE_COLLECTION_THRESHOLD=0.8
```

### Dependency Configuration
```python
class DependencyConfig:
    """Dependency injection configuration settings."""
    # Database Configuration
    DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
    DB_POOL_SIZE = 10
    DB_MAX_OVERFLOW = 20
    DB_POOL_TIMEOUT = 30
    DB_POOL_RECYCLE = 3600
    
    # Redis Configuration
    REDIS_URL = "redis://localhost:6379"
    REDIS_POOL_SIZE = 20
    REDIS_TIMEOUT = 5.0
    
    # Cache Configuration
    CACHE_TTL = 300  # 5 minutes
    CACHE_SIZE = 1000
    MEMORY_CACHE_SIZE = 100
    
    # Lazy Loading Configuration
    LAZY_LOAD_THRESHOLD = 1000
    STREAMING_THRESHOLD = 5000
    BATCH_SIZE = 100
    
    # Memory Management
    MAX_MEMORY_USAGE_MB = 512
    GARBAGE_COLLECTION_THRESHOLD = 0.8
```

## API Endpoints

### Core Endpoints with Dependency Injection

| Endpoint | Dependency Injection Features | Shared Resources | Statistics |
|----------|------------------------------|------------------|------------|
| `GET /` | Basic DI | None | None |
| `GET /health` | Multiple DIs | Database, Redis | Memory, Cache |
| `POST /users` | Service DI | Database, Cache | None |
| `GET /users/{user_id}` | Service DI | Database, Cache | None |
| `GET /users` | Multiple DIs | Database, Cache, Memory | Performance |
| `GET /dependency-injection/stats` | Multiple DIs | All Resources | Comprehensive |
| `POST /dependency-injection/clear-cache` | Cache DI | Cache | Cache Management |

### Dependency Injection Management Endpoints

| Endpoint | Description | Features |
|----------|-------------|----------|
| `GET /dependency-injection/stats` | DI statistics | Performance metrics |
| `POST /dependency-injection/clear-cache` | Clear DI cache | Cache management |

## Best Practices Implemented

### ✅ Dependency Injection Best Practices
- [x] Centralized resource management
- [x] Lazy initialization of resources
- [x] Proper dependency declaration
- [x] Resource lifecycle management
- [x] Error handling with DI

### ✅ FastAPI Best Practices
- [x] Use of `Depends()` for dependency injection
- [x] Proper session management
- [x] Lifespan context managers
- [x] Structured error handling
- [x] Performance monitoring

### ✅ Resource Management Best Practices
- [x] Connection pooling
- [x] Automatic cleanup
- [x] Memory monitoring
- [x] Cache management
- [x] Statistics collection

## Conclusion

This FastAPI application demonstrates comprehensive dependency injection patterns for managing state and shared resources. The implementation includes:

1. **Shared Resources Management**: Centralized resource management through DI
2. **Database Session Management**: Dependency injection for database sessions
3. **Cache Management**: Redis and in-memory cache through DI
4. **Lazy Loading with DI**: Lazy loading components with dependency injection
5. **Memory Management**: Memory monitoring and cleanup through DI
6. **Configuration Management**: Centralized configuration through DI
7. **Statistics Collection**: Performance metrics through DI

The application provides significant benefits through:
- **Resource Efficiency**: Shared resources reduce overhead
- **Testability**: Easy mocking and testing of dependencies
- **Performance**: Efficient resource management and caching
- **Maintainability**: Clear dependency structure and modular design

This serves as a foundation for building scalable FastAPI applications that properly manage state and shared resources through dependency injection. 