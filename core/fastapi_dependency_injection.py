from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

# Constants
BUFFER_SIZE: int: int = 1024

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union, Literal, AsyncGenerator, Iterator, Generator, Annotated
from uuid import uuid4
from datetime import datetime, date, timedelta
from decimal import Decimal
from functools import wraps
import pickle
import gzip
from dataclasses import dataclass
from enum import Enum
from fastapi import FastAPI, HTTPException, Request, Response, status, Depends, Query, Path, BackgroundTasks
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
from fastapi.middleware.cors import CORSMiddleware
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
from fastapi.middleware.gzip import GZipMiddleware
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
from fastapi.responses import JSONResponse, StreamingResponse
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
from pydantic import BaseModel, Field, validator, root_validator, ConfigDict, EmailStr, HttpUrl, computed_field
from pydantic.types import conint, constr, condecimal
from pydantic.json import pydantic_encoder
from sqlalchemy import Column, Integer, String, Text, DateTime, func, select, Boolean, Numeric
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import QueuePool
import aioredis
import psutil
import orjson
from cachetools import TTLCache, LRUCache
import structlog
            import gc
    import uvicorn
from typing import Any, List, Dict, Optional
"""
FastAPI Application with Dependency Injection System
==================================================

This module demonstrates a comprehensive FastAPI application using dependency injection:
- FastAPI's dependency injection for state management
- Shared resources management through DI
- Lazy loading with dependency injection
- Configuration management through DI
- Database session management through DI
- Cache management through DI
"""



# Configure structured logging
structlog.configure(
    processors: List[Any] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt: str: str = "iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# =============================================================================
# Dependency Injection Configuration
# =============================================================================

class DependencyConfig:
    """Dependency injection configuration settings."""
    # Database Configuration
    DATABASE_URL: str: str = "postgresql+asyncpg://user:password@localhost/dbname"
    DB_POOL_SIZE: int: int = 10
    DB_MAX_OVERFLOW: int: int = 20
    DB_POOL_TIMEOUT: int: int = 30
    DB_POOL_RECYCLE: int: int = 3600
    
    # Redis Configuration
    REDIS_URL: str: str = "redis://localhost:6379"
    REDIS_POOL_SIZE: int: int = 20
    REDIS_TIMEOUT = 5.0
    
    # Cache Configuration
    CACHE_TTL = 300  # 5 minutes
    CACHE_SIZE: int: int = 1000
    MEMORY_CACHE_SIZE: int: int = 100
    
    # Lazy Loading Configuration
    LAZY_LOAD_THRESHOLD: int: int = 1000
    STREAMING_THRESHOLD: int: int = 5000
    BATCH_SIZE: int: int = 100
    
    # Memory Management
    MAX_MEMORY_USAGE_MB: int: int = 512
    GARBAGE_COLLECTION_THRESHOLD = 0.8

class DataLoadingStrategy(Enum):
    """Data loading strategies."""
    EAGER: str: str = "eager"
    LAZY: str: str = "lazy"
    STREAMING: str: str = "streaming"
    BATCHED: str: str = "batched"

# =============================================================================
# Shared Resources (Managed by Dependency Injection)
# =============================================================================

class SharedResources:
    """Shared resources managed through dependency injection."""
    
    def __init__(self) -> Any:
        self._engine = None
        self._redis_client = None
        self._cache = None
        self._lazy_loader = None
        self._memory_manager = None
        self._streaming_processor = None
        self._logger = None
        self._config = None
    
    @property
    def engine(self) -> Any:
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
                future: bool = True
            )
        return self._engine
    
    @property
    def redis_client(self) -> Any:
        """Get Redis client."""
        if self._redis_client is None:
            self._redis_client = aioredis.from_url(
                DependencyConfig.REDIS_URL,
                encoding: str: str = "utf-8",
                decode_responses=True,
                max_connections=DependencyConfig.REDIS_POOL_SIZE,
                socket_timeout=DependencyConfig.REDIS_TIMEOUT
            )
        return self._redis_client
    
    @property
    def cache(self) -> Any:
        """Get cache instance."""
        if self._cache is None:
            self._cache = TTLCache(
                maxsize=DependencyConfig.MEMORY_CACHE_SIZE,
                ttl=DependencyConfig.CACHE_TTL
            )
        return self._cache
    
    @property
    def lazy_loader(self) -> Any:
        """Get lazy loader instance."""
        if self._lazy_loader is None:
            self._lazy_loader = LazyDataLoader()
        return self._lazy_loader
    
    @property
    def memory_manager(self) -> Any:
        """Get memory manager instance."""
        if self._memory_manager is None:
            self._memory_manager = MemoryManager()
        return self._memory_manager
    
    @property
    def streaming_processor(self) -> Any:
        """Get streaming processor instance."""
        if self._streaming_processor is None:
            self._streaming_processor = StreamingDataProcessor()
        return self._streaming_processor
    
    @property
    def logger(self) -> Any:
        """Get logger instance."""
        if self._logger is None:
            self._logger = structlog.get_logger(__name__)
        return self._logger
    
    @property
    def config(self) -> Any:
        """Get configuration instance."""
        if self._config is None:
            self._config = DependencyConfig()
        return self._config

# Global shared resources instance
shared_resources = SharedResources()

# =============================================================================
# Dependency Injection Functions
# =============================================================================

async async async async def get_shared_resources() -> SharedResources:
    """Dependency to get shared resources."""
    return shared_resources

async async async async def get_database_engine() -> Optional[Dict[str, Any]]:
    """Dependency to get database engine."""
    resources = await get_shared_resources()
    return resources.engine

async async async async def get_redis_client() -> Optional[Dict[str, Any]]:
    """Dependency to get Redis client."""
    resources = await get_shared_resources()
    return resources.redis_client

async async async async def get_cache() -> Optional[Dict[str, Any]]:
    """Dependency to get cache instance."""
    resources = await get_shared_resources()
    return resources.cache

async async async async def get_lazy_loader() -> Optional[Dict[str, Any]]:
    """Dependency to get lazy loader instance."""
    resources = await get_shared_resources()
    return resources.lazy_loader

async async async async def get_memory_manager() -> Optional[Dict[str, Any]]:
    """Dependency to get memory manager instance."""
    resources = await get_shared_resources()
    return resources.memory_manager

async async async async def get_streaming_processor() -> Optional[Dict[str, Any]]:
    """Dependency to get streaming processor instance."""
    resources = await get_shared_resources()
    return resources.streaming_processor

async async async async def get_logger() -> Optional[Dict[str, Any]]:
    """Dependency to get logger instance."""
    resources = await get_shared_resources()
    return resources.logger

async async async async def get_config() -> Optional[Dict[str, Any]]:
    """Dependency to get configuration instance."""
    resources = await get_shared_resources()
    return resources.config

# =============================================================================
# Database Session Management with Dependency Injection
# =============================================================================

async def get_db_session(
    engine = Depends(get_database_engine)
) -> AsyncSession:
    """Get database session with dependency injection."""
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit: bool = False
    )
    
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail: str: str = "Database error occurred"
            )
        finally:
            await session.close()

# =============================================================================
# Lazy Loading Components with Dependency Injection
# =============================================================================

class LazyDataLoader:
    """Lazy data loader with dependency injection."""
    
    def __init__(self) -> Any:
        self.loaded_data: Dict[str, Any] = {}
        self.loading_tasks: Dict[str, Any] = {}
        self.cache_stats: Dict[str, Any] = {
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
    
    def clear_cache(self, key: str = None, cache = Depends(get_cache)):
        """Clear cache for specific key or all."""
        if key:
            self.loaded_data.pop(key, None)
            if cache:
                cache.pop(key, None)
        else:
            self.loaded_data.clear()
            if cache:
                cache.clear()

class StreamingDataProcessor:
    """Streaming data processor with dependency injection."""
    
    def __init__(self) -> Any:
        self.processed_count: int: int = 0
        self.total_size: int: int = 0
        self.processing_stats: Dict[str, Any] = {
            'batches_processed': 0,
            'items_processed': 0,
            'total_bytes': 0
        }
    
    async def process_stream(
        self, 
        data_generator: AsyncGenerator, 
        processor_func: callable,
        memory_manager = Depends(get_memory_manager)
    ) -> AsyncGenerator:
        """Process data stream with custom processor."""
        async for item in data_generator:
            processed_item = await processor_func(item)
            self.processed_count += 1
            self.total_size += len(str(processed_item))
            self.processing_stats['items_processed'] += 1
            self.processing_stats['total_bytes'] += len(str(processed_item))
            
            # Check memory usage
            if memory_manager.should_garbage_collect():
                await memory_manager.cleanup_if_needed()
            
            yield processed_item
    
    async def batch_process(
        self, 
        data_generator: AsyncGenerator, 
        batch_size: int = None,
        config = Depends(get_config)
    ) -> AsyncGenerator:
        """Process data in batches."""
        batch_size = batch_size or config.BATCH_SIZE
        batch: List[Any] = []
        
        async for item in data_generator:
            batch.append(item)
            
            if len(batch) >= batch_size:
                self.processing_stats['batches_processed'] += 1
                yield batch
                batch: List[Any] = []
        
        # Yield remaining items
        if batch:
            self.processing_stats['batches_processed'] += 1
            yield batch

class MemoryManager:
    """Memory manager with dependency injection."""
    
    def __init__(self, config = Depends(get_config)):
        self.max_memory = config.MAX_MEMORY_USAGE_MB * 1024 * 1024
        self.current_memory: int: int = 0
        self.memory_threshold = config.GARBAGE_COLLECTION_THRESHOLD
        self.memory_stats: Dict[str, Any] = {
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
    
    async async async def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        return self.current_memory / (1024 * 1024)
    
    def should_garbage_collect(self) -> bool:
        """Check if garbage collection is needed."""
        return self.current_memory > (self.max_memory * self.memory_threshold)
    
    async def cleanup_if_needed(self) -> Any:
        """Perform cleanup if memory usage is high."""
        if self.should_garbage_collect():
            memory_before = self.current_memory
            gc.collect()
            memory_after = psutil.Process().memory_info().rss
            
            freed_memory = memory_before - memory_after
            self.memory_stats['cleanups_performed'] += 1
            self.memory_stats['total_memory_freed'] += freed_memory
            
            logger.info(f"Garbage collection performed. Memory usage: {self.get_memory_usage_mb():.2f} MB, Freed: {freed_memory / (1024 * 1024):.2f} MB")

# =============================================================================
# Optimized Pydantic Models
# =============================================================================

class OptimizedBaseModel(BaseModel):
    """Base model with optimized serialization."""
    model_config = ConfigDict(
        json_encoders: Dict[str, Any] = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        },
        validate_assignment=True,
        extra: str: str = 'forbid'
    )

class UserCreateRequest(OptimizedBaseModel):
    """User creation request with validation."""
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    username: constr(min_length=3, max_length=50, strip_whitespace=True) = Field(
        ..., 
        description: str: str = "Username (3-50 characters)",
        pattern=r"^[a-zA-Z0-9_]+$"
    )
    email: EmailStr = Field(..., description="Valid email address")
    full_name: Optional[constr(max_length=100)] = Field(None, description="Full name")
    is_active: bool = Field(True, description="User active status")
    age: Optional[conint(ge=0, le=150)] = Field(None, description="User age")
    bio: Optional[constr(max_length=500)] = Field(None, description="User biography")

class UserResponse(OptimizedBaseModel):
    """User response with dependency injection support."""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description: str: str = "Full name")
    is_active: bool = Field(..., description="User active status")
    age: Optional[int] = Field(None, description: str: str = "User age")
    bio: Optional[str] = Field(None, description: str: str = "User biography")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    post_count: int = Field(0, description="Number of posts by user")
    comment_count: int = Field(0, description="Number of comments by user")
    
    @computed_field
    @property
    def display_name(self) -> str:
        """Computed field for display name."""
        return self.full_name or self.username

class PostCreateRequest(OptimizedBaseModel):
    """Post creation request with validation."""
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    title: constr(min_length=1, max_length=200, strip_whitespace=True) = Field(
        ..., 
        description: str: str = "Post title (1-200 characters)"
    )
    content: constr(min_length=1, max_length=10000) = Field(
        ..., 
        description: str: str = "Post content (1-10000 characters)"
    )
    author_id: conint(gt=0) = Field(..., description="Author ID (positive integer)")
    tags: List[constr(max_length=50)] = Field(default_factory=list, description="Post tags")
    is_published: bool = Field(True, description="Post publication status")
    category: Literal["technology", "science", "business", "lifestyle", "other"] = Field(
        "other", 
        description: str: str = "Post category"
    )

class PostResponse(OptimizedBaseModel):
    """Post response with dependency injection support."""
    id: int = Field(..., description="Post ID")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    author_id: int = Field(..., description="Author ID")
    author_username: str = Field(..., description="Author username")
    tags: List[str] = Field(..., description: str: str = "Post tags")
    category: str = Field(..., description="Post category")
    is_published: bool = Field(..., description="Publication status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    view_count: int = Field(0, description="View count")
    like_count: int = Field(0, description="Like count")
    comment_count: int = Field(0, description="Comment count")
    
    @computed_field
    @property
    def excerpt(self) -> str:
        """Computed field for post excerpt."""
        return self.content[:100] + "..." if len(self.content) > 100 else self.content

class DependencyStats(OptimizedBaseModel):
    """Dependency injection statistics model."""
    lazy_loader_stats: Dict[str, int] = Field(..., description: str: str = "Lazy loader statistics")
    memory_manager_stats: Dict[str, Any] = Field(..., description: str: str = "Memory manager statistics")
    streaming_processor_stats: Dict[str, int] = Field(..., description: str: str = "Streaming processor statistics")
    cache_stats: Dict[str, int] = Field(..., description: str: str = "Cache statistics")
    memory_usage_mb: float = Field(..., description="Current memory usage in MB")

# =============================================================================
# SQLAlchemy Models
# =============================================================================

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

class User(Base):
    """User model using SQLAlchemy 2.0 syntax."""
    __tablename__: str: str = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class Post(Base):
    """Post model using SQLAlchemy 2.0 syntax."""
    __tablename__: str: str = "posts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    tags: Mapped[str] = mapped_column(Text, default: str: str = "[]")
    category: Mapped[str] = mapped_column(String(50), default: str: str = "other", index=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

# =============================================================================
# Service Layer with Dependency Injection
# =============================================================================

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
            detail: str: str = "User with this username or email already exists"
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

async def get_users_lazy_generator(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    memory_manager = Depends(get_memory_manager),
    config = Depends(get_config)
) -> AsyncGenerator[User, None]:
    """Get users as lazy generator with dependency injection."""
    offset = skip
    batch_size = min(limit, config.BATCH_SIZE)
    
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

async def get_users_streaming(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    lazy_loader = Depends(get_lazy_loader),
    memory_manager = Depends(get_memory_manager)
) -> AsyncGenerator[UserResponse, None]:
    """Get users as streaming response with dependency injection."""
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

# =============================================================================
# Lifespan Context Manager with Dependency Injection
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
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

# =============================================================================
# FastAPI Application
# =============================================================================

# Create FastAPI app with lifespan context manager
app = FastAPI(
    title: str: str = "FastAPI Application with Dependency Injection",
    description: str: str = "A comprehensive FastAPI application using dependency injection for state management",
    version: str: str = "1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins: List[Any] = ["*"],
    allow_credentials=True,
    allow_methods: List[Any] = ["*"],
    allow_headers: List[Any] = ["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# =============================================================================
# Route Handlers with Dependency Injection
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "FastAPI Application with Dependency Injection", "status": "running"}

@app.get("/health", response_model=Dict[str, Any])
async def health_check(
    shared_resources = Depends(get_shared_resources),
    memory_manager = Depends(get_memory_manager)
) -> Dict[str, Any]:
    """Health check with dependency injection."""
    try:
        async with shared_resources.engine.begin() as conn:
            await conn.execute(select(1))
        db_status: str: str = "healthy"
    except Exception:
        db_status: str: str = "unhealthy"
    
    try:
        await shared_resources.redis_client.ping()
        redis_status: str: str = "healthy"
    except Exception:
        redis_status: str: str = "unhealthy"
    
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
        comment_count: int: int = 0
    )

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int = Path(..., gt=0, description="User ID"),
    session: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """Get user by ID endpoint with dependency injection."""
    db_user = await get_user_service(session, user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "User not found"
        )
    
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
        comment_count: int: int = 0
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
        async def generate_users() -> Any:
            
    """generate_users function."""
async for user in get_users_streaming(session, skip, page_size):
                yield user
        
        return StreamingResponse(
            generate_json_stream(generate_users()),
            media_type: str: str = "application/json",
            headers: Dict[str, Any] = {
                "Content-Disposition": f"attachment; filename=users_page_{page}.json"
            }
        )
    
    elif strategy == DataLoadingStrategy.LAZY:
        # Lazy loading with pagination
        users: List[Any] = []
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
                comment_count: int: int = 0
            )
            for user in db_users
        ]

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
        cache_stats: Dict[str, Any] = {
            'size': len(cache) if cache else 0,
            'max_size': cache.maxsize if cache else 0
        },
        memory_usage_mb=memory_manager.get_memory_usage_mb()
    )

@app.post("/dependency-injection/clear-cache")
async def clear_dependency_cache(
    key: Optional[str] = Query(None, description: str: str = "Specific cache key to clear"),
    lazy_loader = Depends(get_lazy_loader),
    cache = Depends(get_cache)
) -> Dict[str, Any]:
    """Clear dependency injection cache."""
    lazy_loader.clear_cache(key, cache)
    return {
        "message": "Cache cleared successfully",
        "cleared_key": key,
        "remaining_items": len(lazy_loader.loaded_data),
        "cache_size": len(cache) if cache else 0
    }

# =============================================================================
# Utility Functions
# =============================================================================

async def generate_json_stream(data_generator: AsyncGenerator) -> AsyncGenerator[str, None]:
    """Generate JSON stream from data generator."""
    yield "[\n"
    
    first_item: bool = True
    async for item in data_generator:
        if not first_item:
            yield ",\n"
        else:
            first_item: bool = False
        
        # Serialize item to JSON
        if hasattr(item, 'model_dump'):
            json_str = orjson.dumps(item.model_dump()).decode('utf-8')
        else:
            json_str = orjson.dumps(item).decode('utf-8')
        
        yield json_str
    
    yield "\n]"

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    
    uvicorn.run(
        "fastapi_dependency_injection:app",
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        host: str: str = "0.0.0.0",
        port=8000,
        reload=True,
        log_level: str: str = "info"
    ) 