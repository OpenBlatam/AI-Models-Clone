# FastAPI Lifespan Migration Guide

## Overview

This guide explains how to migrate from the deprecated `@app.on_event("startup")` and `@app.on_event("shutdown")` decorators to modern lifespan context managers in FastAPI applications.

## Why Migrate to Lifespan Context Managers?

### Benefits of Lifespan Context Managers

1. **Better Resource Management**: Context managers ensure proper cleanup even when exceptions occur
2. **Cleaner Code**: Single function handles both startup and shutdown logic
3. **Better Error Handling**: Exceptions in startup don't prevent shutdown cleanup
4. **Async Support**: Native support for async operations
5. **Future-Proof**: Part of FastAPI's modern API design
6. **Testing**: Easier to test lifecycle events in isolation

### Problems with `app.on_event()`

1. **No Guaranteed Cleanup**: If startup fails, shutdown events might not run
2. **Scattered Logic**: Startup and shutdown logic in separate functions
3. **Limited Error Handling**: Difficult to handle startup failures gracefully
4. **Deprecated**: Marked for removal in future FastAPI versions

## Migration Patterns

### Pattern 1: Basic Migration

**Before (app.on_event):**
```python
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up")
    # Initialize resources

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
    # Cleanup resources

app = FastAPI()
```

**After (Lifespan Context Manager):**
```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Application starting up")
    try:
        # Initialize resources here
        yield
    finally:
        # Shutdown (runs even if startup fails)
        logger.info("Application shutting down")
        # Cleanup resources here

app = FastAPI(lifespan=lifespan)
```

### Pattern 2: Database Connection Management

**Before:**
```python
engine = None
AsyncSessionLocal = None

@app.on_event("startup")
async def connect_database():
    global engine, AsyncSessionLocal
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)

@app.on_event("shutdown")
async def disconnect_database():
    global engine
    if engine:
        await engine.dispose()
```

**After:**
```python
from ..utils.lifespan_manager import LifespanManager

# Create lifespan manager
lifespan_manager = LifespanManager()
lifespan_manager.add_database_connection(
    connect_database,
    disconnect_database,
    name="postgres",
    timeout=30.0
)

app = FastAPI(lifespan=lifespan_manager.create_lifespan())
```

### Pattern 3: Multiple Services

**Before:**
```python
@app.on_event("startup")
async def startup_event():
    await connect_database()
    await connect_redis()
    await start_background_service()
    await load_models()

@app.on_event("shutdown")
async def shutdown_event():
    await stop_background_service()
    await disconnect_redis()
    await disconnect_database()
```

**After:**
```python
from ..utils.lifespan_manager import LifespanManager, EventPriority

lifespan_manager = LifespanManager()

# Add services with priorities
lifespan_manager.add_database_connection(
    connect_database, disconnect_database,
    name="database", timeout=30.0
)
lifespan_manager.add_cache_connection(
    connect_redis, disconnect_redis,
    name="redis", timeout=10.0
)
lifespan_manager.add_background_task(
    start_func=start_background_service, stop_func=stop_background_service,
    name="background_service", timeout=10.0
)
lifespan_manager.add_startup_event(
    load_models,
    name="model_loading",
    priority=EventPriority.NORMAL,
    timeout=60.0,
    retry_count=2
)

app = FastAPI(lifespan=lifespan_manager.create_lifespan())
```

## Using the LifespanManager Utility

The `LifespanManager` class provides a powerful way to manage complex application lifecycles.

### Basic Usage

```python
from ..utils.lifespan_manager import LifespanManager, EventPriority

# Create manager
manager = LifespanManager()

# Add startup events
manager.add_startup_event(
    handler=initialize_database,
    name="database_init",
    priority=EventPriority.CRITICAL,
    timeout=30.0,
    retry_count=3
)

# Add shutdown events
manager.add_shutdown_event(
    handler=cleanup_database,
    name="database_cleanup",
    priority=EventPriority.CRITICAL,
    timeout=10.0
)

# Create FastAPI app
app = FastAPI(lifespan=manager.create_lifespan())
```

### Event Priorities

```python
class EventPriority(Enum):
    CRITICAL = 0    # Database connections, core services
    HIGH = 1        # Cache connections, external APIs
    NORMAL = 2      # Background tasks, model loading
    LOW = 3         # Logging, monitoring
    OPTIONAL = 4    # Non-critical services
```

### Convenience Functions

```python
from ..utils.lifespan_manager import (
    create_database_lifespan,
    create_cache_lifespan,
    create_background_task_lifespan
)

# Database lifespan
db_manager = create_database_lifespan(
    connect_func=connect_database,
    disconnect_func=disconnect_database,
    name="postgres",
    timeout=30.0
)

# Cache lifespan
cache_manager = create_cache_lifespan(
    connect_func=connect_redis,
    disconnect_func=disconnect_redis,
    name="redis",
    timeout=10.0
)

# Background task lifespan
task_manager = create_background_task_lifespan(
    start_func=start_background_service,
    stop_func=stop_background_service,
    name="background_service",
    timeout=10.0
)
```

## Migration Examples

### Example 1: Video Processing API

**Before:**
```python
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Video Processing API starting up", version="3.0.0")
    
    # Initialize processors
    try:
        video_processor = get_video_processor()
        viral_processor = get_viral_processor()
        langchain_processor = get_langchain_processor()
        batch_processor = get_batch_processor()
        
        logger.info("All processors initialized successfully")
        
    except Exception as e:
        logger.error("Failed to initialize processors", error=str(e))
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Video Processing API shutting down")
```

**After:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    logger.info("Video Processing API starting up", version="3.0.0")
    
    try:
        # Initialize processors
        video_processor = get_video_processor()
        viral_processor = get_viral_processor()
        langchain_processor = get_langchain_processor()
        batch_processor = get_batch_processor()
        
        logger.info("All processors initialized successfully")
        yield
        
    except Exception as e:
        logger.error("Failed to initialize processors", error=str(e))
        raise
    finally:
        logger.info("Video Processing API shutting down")

app = FastAPI(lifespan=lifespan)
```

### Example 2: AI Service with Multiple Dependencies

**Before:**
```python
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("Starting AI system...")
    await service_manager.initialize()
    logger.info("System started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Shutting down AI system...")
    await service_manager.cleanup()
    logger.info("System shut down successfully")

@app.on_event("startup")
async def start_metrics_updater():
    """Start metrics updater"""
    async def update_metrics():
        while True:
            monitoring_service.update_system_metrics()
            await asyncio.sleep(30)
    
    asyncio.create_task(update_metrics())
```

**After:**
```python
from ..utils.lifespan_manager import LifespanManager, EventPriority

# Create lifespan manager
lifespan_manager = LifespanManager()

# Add core service initialization
lifespan_manager.add_startup_event(
    handler=service_manager.initialize,
    name="service_initialization",
    priority=EventPriority.CRITICAL,
    timeout=60.0
)

# Add metrics updater
lifespan_manager.add_background_task(
    start_func=start_metrics_updater,
    stop_func=stop_metrics_updater,
    name="metrics_updater",
    timeout=10.0
)

# Add cleanup
lifespan_manager.add_shutdown_event(
    handler=service_manager.cleanup,
    name="service_cleanup",
    priority=EventPriority.CRITICAL,
    timeout=30.0
)

app = FastAPI(lifespan=lifespan_manager.create_lifespan())
```

## Best Practices

### 1. Error Handling

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    startup_errors = []
    
    try:
        # Initialize critical services first
        await connect_database()
        await connect_redis()
        
        # Initialize optional services
        try:
            await load_models()
        except Exception as e:
            startup_errors.append(("models", str(e)))
        
        if startup_errors:
            logger.warning("Some services failed to start", errors=startup_errors)
        
        yield
        
    finally:
        # Always cleanup, even if startup failed
        await cleanup_resources()
```

### 2. Resource Management

```python
class ResourceManager:
    def __init__(self):
        self.resources = []
    
    async def add_resource(self, resource):
        self.resources.append(resource)
    
    async def cleanup_all(self):
        for resource in reversed(self.resources):
            try:
                await resource.cleanup()
            except Exception as e:
                logger.error(f"Failed to cleanup {resource}: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    resource_manager = ResourceManager()
    
    try:
        # Add resources as they're created
        db = await create_database()
        await resource_manager.add_resource(db)
        
        cache = await create_cache()
        await resource_manager.add_resource(cache)
        
        yield
        
    finally:
        await resource_manager.cleanup_all()
```

### 3. Testing

```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def test_app():
    @asynccontextmanager
    async def test_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        # Setup test resources
        yield
        # Cleanup test resources
    
    app = FastAPI(lifespan=test_lifespan)
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

def test_application_lifecycle(client):
    # Test that the app starts and stops correctly
    response = client.get("/health")
    assert response.status_code == 200
```

### 4. Monitoring and Logging

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    start_time = time.time()
    
    try:
        logger.info("Application starting up")
        
        # Initialize services with timing
        for service_name, init_func in services.items():
            service_start = time.time()
            await init_func()
            service_time = time.time() - service_start
            logger.info(f"Service {service_name} initialized", duration=service_time)
        
        total_startup_time = time.time() - start_time
        logger.info("Application started successfully", startup_time=total_startup_time)
        yield
        
    finally:
        shutdown_start = time.time()
        logger.info("Application shutting down")
        
        # Cleanup services
        for service_name, cleanup_func in reversed(list(cleanup_services.items())):
            try:
                await cleanup_func()
                logger.info(f"Service {service_name} cleaned up")
            except Exception as e:
                logger.error(f"Failed to cleanup {service_name}", error=str(e))
        
        total_shutdown_time = time.time() - shutdown_start
        logger.info("Application shut down", shutdown_time=total_shutdown_time)
```

## Migration Script

Use the provided migration script to automatically convert existing code:

```bash
# Dry run to see what would be migrated
python scripts/migrate_lifespan.py --dry-run agents/backend/onyx/server/features

# Perform the migration
python scripts/migrate_lifespan.py agents/backend/onyx/server/features
```

The script will:
1. Find all Python files with `@app.on_event()` decorators
2. Convert them to lifespan context managers
3. Create backup files
4. Update FastAPI app creation to include lifespan parameter

## Common Migration Issues

### Issue 1: Global Variables

**Problem:** Startup/shutdown functions modify global variables
**Solution:** Use dependency injection or app state

```python
# Instead of global variables
global db_connection
db_connection = await create_connection()

# Use app state
app.state.db_connection = await create_connection()
```

### Issue 2: Multiple Event Handlers

**Problem:** Multiple `@app.on_event("startup")` handlers
**Solution:** Combine them in a single lifespan function

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Run all startup logic
    await setup_database()
    await setup_cache()
    await setup_background_tasks()
    
    yield
    
    # Run all shutdown logic
    await cleanup_background_tasks()
    await cleanup_cache()
    await cleanup_database()
```

### Issue 3: Conditional Initialization

**Problem:** Some services only initialize under certain conditions
**Solution:** Use conditional logic in lifespan

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        # Always initialize core services
        await setup_database()
        
        # Conditionally initialize optional services
        if app.state.config.enable_cache:
            await setup_cache()
        
        if app.state.config.enable_background_tasks:
            await setup_background_tasks()
        
        yield
        
    finally:
        # Cleanup in reverse order
        if hasattr(app.state, 'background_tasks'):
            await cleanup_background_tasks()
        
        if hasattr(app.state, 'cache'):
            await cleanup_cache()
        
        await cleanup_database()
```

## Performance Considerations

### 1. Parallel Initialization

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        # Initialize independent services in parallel
        db_task = asyncio.create_task(setup_database())
        cache_task = asyncio.create_task(setup_cache())
        
        # Wait for all to complete
        await asyncio.gather(db_task, cache_task)
        
        yield
        
    finally:
        # Cleanup in parallel
        cleanup_tasks = [
            cleanup_database(),
            cleanup_cache()
        ]
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
```

### 2. Lazy Initialization

```python
class LazyService:
    def __init__(self):
        self._initialized = False
        self._connection = None
    
    async def get_connection(self):
        if not self._initialized:
            self._connection = await create_connection()
            self._initialized = True
        return self._connection
    
    async def cleanup(self):
        if self._initialized and self._connection:
            await self._connection.close()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    lazy_service = LazyService()
    app.state.lazy_service = lazy_service
    
    yield
    
    await lazy_service.cleanup()
```

## Conclusion

Migrating from `@app.on_event()` to lifespan context managers provides:

1. **Better resource management** with guaranteed cleanup
2. **Cleaner, more maintainable code**
3. **Improved error handling** and recovery
4. **Future-proof architecture** aligned with FastAPI's direction
5. **Better testing capabilities**

The `LifespanManager` utility provides a powerful, flexible way to manage complex application lifecycles with features like:

- Event prioritization
- Retry logic
- Timeout handling
- Comprehensive logging
- Convenience functions for common patterns

Start migrating your applications today to take advantage of these improvements! 