from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
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
from typing import Any, Dict, List, Optional, Union, Literal, TypeVar, Generic
from uuid import uuid4
from datetime import datetime, date, timedelta
from decimal import Decimal
from functools import wraps
import pickle
import gzip
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
from fastapi.responses import JSONResponse
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
    import uvicorn
from typing import Any, List, Dict, Optional
"""
FastAPI Application with Async Operations, Caching, and Optimized Pydantic Serialization
=======================================================================================

This module demonstrates a comprehensive FastAPI application with:
- Asynchronous operations for all I/O operations
- Multi-level caching (Redis + in-memory)
- Optimized Pydantic serialization/deserialization
- Performance monitoring and optimization
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
# Configuration
# =============================================================================

class CacheConfig:
    """Cache configuration settings."""
    # Redis Configuration
    REDIS_URL: str: str = "redis://localhost:6379"
    REDIS_DB: int: int = 0
    REDIS_PASSWORD = None
    REDIS_MAX_CONNECTIONS: int: int = 20
    
    # In-Memory Cache Configuration
    MEMORY_CACHE_SIZE: int: int = 1000
    MEMORY_CACHE_TTL = 300  # 5 minutes
    
    # Cache Keys
    USER_CACHE_PREFIX: str: str = "user:"
    POST_CACHE_PREFIX: str: str = "post:"
    STATS_CACHE_PREFIX: str: str = "stats:"
    
    # Cache TTLs
    USER_CACHE_TTL = 3600  # 1 hour
    POST_CACHE_TTL = 1800  # 30 minutes
    STATS_CACHE_TTL = 300  # 5 minutes

class AsyncConfig:
    """Async operation configuration."""
    MAX_CONCURRENT_DB_OPERATIONS: int: int = 50
    MAX_CONCURRENT_API_CALLS: int: int = 20
    DB_OPERATION_TIMEOUT = 10.0
    API_CALL_TIMEOUT = 30.0
    BATCH_SIZE: int: int = 100

class SerializationConfig:
    """Pydantic serialization configuration."""
    USE_ORJSON: bool = True
    COMPRESS_LARGE_OBJECTS: bool = True
    COMPRESSION_THRESHOLD = 1024  # bytes
    CACHE_SERIALIZED_OBJECTS: bool = True
    OPTIMIZE_FOR_READS: bool = True

# =============================================================================
# Optimized Pydantic Models with Serialization
# =============================================================================

class OptimizedBaseModel(BaseModel):
    """Base model with optimized serialization settings."""
    model_config = ConfigDict(
        # Use orjson for faster JSON serialization
        json_encoders: Dict[str, Any] = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        },
        # Optimize for performance
        validate_assignment=True,
        extra: str: str = 'forbid',
        # Use orjson if available
        json_schema_extra: Dict[str, Any] = {
            "example": {}
        }
    )

class UserCreateRequest(OptimizedBaseModel):
    """User creation request with optimized validation."""
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
    
    @validator('username')
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v.lower()
    
    @validator('email')
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        return v.lower()

class UserResponse(OptimizedBaseModel):
    """User response with optimized serialization."""
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
    
    @computed_field
    @property
    def is_verified(self) -> bool:
        """Computed field for verification status."""
        return self.post_count > 0 and self.is_active

class PostCreateRequest(OptimizedBaseModel):
    """Post creation request with optimized validation."""
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
    """Post response with optimized serialization."""
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
    
    @computed_field
    @property
    def is_popular(self) -> bool:
        """Computed field for popularity status."""
        return self.view_count > 100 or self.like_count > 10

class CacheStats(OptimizedBaseModel):
    """Cache statistics model."""
    total_hits: int = Field(0, description="Total cache hits")
    total_misses: int = Field(0, description="Total cache misses")
    hit_rate: float = Field(0.0, description="Cache hit rate")
    memory_usage_mb: float = Field(0.0, description="Memory cache usage in MB")
    redis_connected: bool = Field(False, description="Redis connection status")
    cache_size: int = Field(0, description="Current cache size")

# =============================================================================
# Multi-Level Caching System
# =============================================================================

class MultiLevelCache:
    """Multi-level caching system with Redis and in-memory cache."""
    
    def __init__(self) -> Any:
        self.redis_client: Optional[aioredis.Redis] = None
        self.memory_cache = TTLCache(
            maxsize=CacheConfig.MEMORY_CACHE_SIZE,
            ttl=CacheConfig.MEMORY_CACHE_TTL
        )
        self.stats: Dict[str, Any] = {
            'memory_hits': 0,
            'memory_misses': 0,
            'redis_hits': 0,
            'redis_misses': 0,
            'total_operations': 0
        }
    
    async def initialize_redis(self) -> Any:
        """Initialize Redis connection."""
        try:
            self.redis_client = aioredis.from_url(
                CacheConfig.REDIS_URL,
                db=CacheConfig.REDIS_DB,
                password=CacheConfig.REDIS_PASSWORD,
                max_connections=CacheConfig.REDIS_MAX_CONNECTIONS,
                decode_responses: bool = True
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async async async async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with multi-level fallback."""
        self.stats['total_operations'] += 1
        
        # Try memory cache first
        if key in self.memory_cache:
            self.stats['memory_hits'] += 1
            logger.debug(f"Memory cache hit for key: {key}")
            return self.memory_cache[key]
        
        self.stats['memory_misses'] += 1
        
        # Try Redis cache
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    self.stats['redis_hits'] += 1
                    # Deserialize and store in memory cache
                    deserialized_value = self._deserialize_value(value)
                    self.memory_cache[key] = deserialized_value
                    logger.debug(f"Redis cache hit for key: {key}")
                    return deserialized_value
                else:
                    self.stats['redis_misses'] += 1
                    logger.debug(f"Redis cache miss for key: {key}")
            except Exception as e:
                logger.error(f"Redis operation failed: {e}")
                self.stats['redis_misses'] += 1
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with multi-level storage."""
        try:
            # Serialize value
            serialized_value = self._serialize_value(value)
            
            # Store in memory cache
            self.memory_cache[key] = value
            
            # Store in Redis if available
            if self.redis_client:
                try:
                    await self.redis_client.set(key, serialized_value, ex=ttl)
                    logger.debug(f"Value cached in Redis for key: {key}")
                except Exception as e:
                    logger.error(f"Failed to cache in Redis: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to cache value: {e}")
            return False
    
    async async async async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            # Remove from memory cache
            self.memory_cache.pop(key, None)
            
            # Remove from Redis if available
            if self.redis_client:
                try:
                    await self.redis_client.delete(key)
                    logger.debug(f"Value deleted from Redis for key: {key}")
                except Exception as e:
                    logger.error(f"Failed to delete from Redis: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete cache value: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern."""
        deleted_count: int: int = 0
        
        # Clear memory cache entries
        keys_to_delete: List[Any] = [k for k in self.memory_cache.keys() if pattern in k]
        for key in keys_to_delete:
            self.memory_cache.pop(key, None)
            deleted_count += 1
        
        # Clear Redis cache entries
        if self.redis_client:
            try:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    deleted_count += len(keys)
                    logger.debug(f"Deleted {len(keys)} keys from Redis matching pattern: {pattern}")
            except Exception as e:
                logger.error(f"Failed to clear Redis pattern: {e}")
        
        return deleted_count
    
    async async async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        total_hits = self.stats['memory_hits'] + self.stats['redis_hits']
        total_misses = self.stats['memory_misses'] + self.stats['redis_misses']
        total_operations = total_hits + total_misses
        
        hit_rate = (total_hits / total_operations * 100) if total_operations > 0 else 0.0
        
        return CacheStats(
            total_hits=total_hits,
            total_misses=total_misses,
            hit_rate=hit_rate,
            memory_usage_mb=len(self.memory_cache) * 0.001,  # Rough estimate
            redis_connected=self.redis_client is not None,
            cache_size=len(self.memory_cache)
        )
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for caching."""
        if SerializationConfig.USE_ORJSON:
            # Use orjson for faster serialization
            serialized = orjson.dumps(value, default=pydantic_encoder)
            if SerializationConfig.COMPRESS_LARGE_OBJECTS and len(serialized) > SerializationConfig.COMPRESSION_THRESHOLD:
                compressed = gzip.compress(serialized)
                return f"gzip:{compressed.hex()}"
            return serialized.decode('utf-8')
        else:
            # Fallback to standard JSON
            serialized = json.dumps(value, default=pydantic_encoder)
            if SerializationConfig.COMPRESS_LARGE_OBJECTS and len(serialized) > SerializationConfig.COMPRESSION_THRESHOLD:
                compressed = gzip.compress(serialized.encode('utf-8'))
                return f"gzip:{compressed.hex()}"
            return serialized
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from cache."""
        if value.startswith("gzip:"):
            # Decompress gzipped data
            compressed_data = bytes.fromhex(value[5:])
            decompressed = gzip.decompress(compressed_data)
            if SerializationConfig.USE_ORJSON:
                return orjson.loads(decompressed)
            else:
                return json.loads(decompressed.decode('utf-8'))
        else:
            if SerializationConfig.USE_ORJSON:
                return orjson.loads(value.encode('utf-8'))
            else:
                return json.loads(value)

# Global cache instance
cache = MultiLevelCache()

# =============================================================================
# Async Database Operations
# =============================================================================

class AsyncDatabaseManager:
    """Manages async database operations with connection pooling."""
    
    def __init__(self) -> Any:
        self.semaphore = asyncio.Semaphore(AsyncConfig.MAX_CONCURRENT_DB_OPERATIONS)
        self.active_operations: int: int = 0
    
    async def execute_with_timeout(self, coro, timeout: float = None) -> Any:
        """Execute database operation with timeout and concurrency control."""
        timeout = timeout or AsyncConfig.DB_OPERATION_TIMEOUT
        
        async with self.semaphore:
            self.active_operations += 1
            try:
                return await asyncio.wait_for(coro, timeout=timeout)
            except asyncio.TimeoutError:
                logger.error(f"Database operation timeout after {timeout} seconds")
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail: str: str = "Database operation timed out"
                )
            finally:
                self.active_operations -= 1
    
    async def batch_operations(self, operations: List[Any], batch_size: int = None) -> List[Any]:
        """Execute database operations in batches."""
        batch_size = batch_size or AsyncConfig.BATCH_SIZE
        results: List[Any] = []
        
        for i in range(0, len(operations), batch_size):
            batch = operations[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
        
        return results

# Global database manager
db_manager = AsyncDatabaseManager()

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
# Database Configuration
# =============================================================================

DATABASE_URL: str: str = "postgresql+asyncpg://user:password@localhost/dbname"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    future: bool = True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit: bool = False
)

# =============================================================================
# Async Service Layer with Caching
# =============================================================================

async async async async def get_db_session() -> AsyncSession:
    """Get database session with async error handling."""
    async with AsyncSessionLocal() as session:
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

async def create_user_service(session: AsyncSession, user_data: UserCreateRequest) -> User:
    """Create user with async operations and caching."""
    async def _create_user() -> Any:
        
    """_create_user function."""
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
        
        return db_user
    
    return await db_manager.execute_with_timeout(_create_user())

async async async async def get_user_service(session: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID with async operations and caching."""
    cache_key = f"{CacheConfig.USER_CACHE_PREFIX}{user_id}"
    
    # Try cache first
    cached_user = await cache.get(cache_key)
    if cached_user:
        logger.debug(f"User cache hit for ID: {user_id}")
        return cached_user
    
    # Fetch from database
    async async async async def _get_user() -> Optional[Dict[str, Any]]:
        
    """_get_user function."""
result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    db_user = await db_manager.execute_with_timeout(_get_user())
    
    if db_user:
        # Cache the result
        user_response = UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            age=db_user.age,
            bio=db_user.bio,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            post_count=0,  # TODO: Calculate from database
            comment_count=0  # TODO: Calculate from database
        )
        await cache.set(cache_key, user_response.model_dump(), CacheConfig.USER_CACHE_TTL)
        logger.debug(f"User cached for ID: {user_id}")
    
    return db_user

async async async async def get_users_service(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Get users with async operations and caching."""
    cache_key = f"{CacheConfig.USER_CACHE_PREFIX}list:{skip}:{limit}"
    
    # Try cache first
    cached_users = await cache.get(cache_key)
    if cached_users:
        logger.debug(f"Users list cache hit for skip: {skip}, limit: {limit}")
        return cached_users
    
    # Fetch from database
    async async async async def _get_users() -> Optional[Dict[str, Any]]:
        
    """_get_users function."""
result = await session.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()
    
    db_users = await db_manager.execute_with_timeout(_get_users())
    
    if db_users:
        # Cache the result
        user_responses: List[Any] = [
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
            ).model_dump()
            for user in db_users
        ]
        await cache.set(cache_key, user_responses, CacheConfig.USER_CACHE_TTL)
        logger.debug(f"Users list cached for skip: {skip}, limit: {limit}")
    
    return db_users

async async async async def create_post_service(session: AsyncSession, post_data: PostCreateRequest) -> Post:
    """Create post with async operations and cache invalidation."""
    async async async async def _create_post() -> Any:
        
    """_create_post function."""
# Verify author exists
        author = await get_user_service(session, post_data.author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail: str: str = "Author not found"
            )
        
        # Create new post
        db_post = Post(
            title=post_data.title,
            content=post_data.content,
            author_id=post_data.author_id,
            tags: str: str = ",".join(post_data.tags) if post_data.tags else "",
            category=post_data.category,
            is_published=post_data.is_published
        )
        
        session.add(db_post)
        await session.commit()
        await session.refresh(db_post)
        
        return db_post
    
    db_post = await db_manager.execute_with_timeout(_create_post())
    
    # Invalidate related caches
    await cache.clear_pattern(f"{CacheConfig.USER_CACHE_PREFIX}{post_data.author_id}")
    await cache.clear_pattern(f"{CacheConfig.POST_CACHE_PREFIX}list:*")
    
    return db_post

async async async async def get_post_service(session: AsyncSession, post_id: int) -> Optional[Post]:
    """Get post by ID with async operations and caching."""
    cache_key = f"{CacheConfig.POST_CACHE_PREFIX}{post_id}"
    
    # Try cache first
    cached_post = await cache.get(cache_key)
    if cached_post:
        logger.debug(f"Post cache hit for ID: {post_id}")
        return cached_post
    
    # Fetch from database
    async async async async def _get_post() -> Optional[Dict[str, Any]]:
        
    """_get_post function."""
result = await session.execute(
            select(Post).where(Post.id == post_id)
        )
        return result.scalar_one_or_none()
    
    db_post = await db_manager.execute_with_timeout(_get_post())
    
    if db_post:
        # Get author username
        author = await get_user_service(session, db_post.author_id)
        author_username = author.username if author else "Unknown"
        
        # Cache the result
        post_response = PostResponse(
            id=db_post.id,
            title=db_post.title,
            content=db_post.content,
            author_id=db_post.author_id,
            author_username=author_username,
            tags=db_post.tags.split(",") if db_post.tags else [],
            category=db_post.category,
            is_published=db_post.is_published,
            created_at=db_post.created_at,
            updated_at=db_post.updated_at,
            view_count=db_post.view_count,
            like_count=db_post.like_count,
            comment_count=db_post.comment_count
        )
        await cache.set(cache_key, post_response.model_dump(), CacheConfig.POST_CACHE_TTL)
        logger.debug(f"Post cached for ID: {post_id}")
    
    return db_post

async async async async def get_posts_service(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Post]:
    """Get posts with async operations and caching."""
    cache_key = f"{CacheConfig.POST_CACHE_PREFIX}list:{skip}:{limit}"
    
    # Try cache first
    cached_posts = await cache.get(cache_key)
    if cached_posts:
        logger.debug(f"Posts list cache hit for skip: {skip}, limit: {limit}")
        return cached_posts
    
    # Fetch from database
    async async async async def _get_posts() -> Optional[Dict[str, Any]]:
        
    """_get_posts function."""
result = await session.execute(
            select(Post)
            .offset(skip)
            .limit(limit)
            .order_by(Post.created_at.desc())
        )
        return result.scalars().all()
    
    db_posts = await db_manager.execute_with_timeout(_get_posts())
    
    if db_posts:
        # Get author usernames in batch
        author_ids = list(set(post.author_id for post in db_posts))
        authors: Dict[str, Any] = {}
        
        # Batch fetch authors
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
        async async async async def _get_author_batch() -> Optional[Dict[str, Any]]:
            
    """_get_author_batch function."""
author_tasks: List[Any] = [get_user_service(session, author_id) for author_id in author_ids]
            author_results = await asyncio.gather(*author_tasks, return_exceptions=True)
            for author_id, author_result in zip(author_ids, author_results):
                if isinstance(author_result, User):
                    authors[author_id] = author_result.username
        
        await _get_author_batch()
        
        # Cache the result
        post_responses: List[Any] = [
            PostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                author_id=post.author_id,
                author_username=authors.get(post.author_id, "Unknown"),
                tags=post.tags.split(",") if post.tags else [],
                category=post.category,
                is_published=post.is_published,
                created_at=post.created_at,
                updated_at=post.updated_at,
                view_count=post.view_count,
                like_count=post.like_count,
                comment_count=post.comment_count
            ).model_dump()
            for post in db_posts
        ]
        await cache.set(cache_key, post_responses, CacheConfig.POST_CACHE_TTL)
        logger.debug(f"Posts list cached for skip: {skip}, limit: {limit}")
    
    return db_posts

# =============================================================================
# Lifespan Context Manager
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Lifespan context manager with async initialization."""
    # Startup
    logger.info("Starting application with async operations and caching...")
    
    try:
        # Initialize Redis cache
        await cache.initialize_redis()
        
        # Initialize database
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
        
        # Check database connection
        async with engine.begin() as conn:
            await conn.execute(select(1))
        logger.info("Database connection verified")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Close database connections
    await engine.dispose()
    logger.info("Database connections closed")
    
    # Close Redis connection
    if cache.redis_client:
        await cache.redis_client.close()
        logger.info("Redis connection closed")
    
    logger.info("Application shutdown completed")

# =============================================================================
# FastAPI Application
# =============================================================================

# Create FastAPI app with lifespan context manager
app = FastAPI(
    title: str: str = "FastAPI Application with Async Operations and Caching",
    description: str: str = "A comprehensive FastAPI application with async operations, multi-level caching, and optimized serialization",
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
# Route Handlers with Async Operations and Caching
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "FastAPI Application with Async Operations and Caching", "status": "running"}

@app.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """Health check with cache statistics."""
    db_status: str: str = "healthy"
    try:
        async with engine.begin() as conn:
            await conn.execute(select(1))
    except Exception:
        db_status: str: str = "unhealthy"
    
    cache_stats = cache.get_stats()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database_status": db_status,
        "cache_stats": cache_stats.model_dump(),
        "active_db_operations": db_manager.active_operations
    }

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    session: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """Create user endpoint with async operations."""
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
    """Get user by ID endpoint with caching."""
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

@app.get("/users", response_model=List[UserResponse])
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_db_session)
) -> List[UserResponse]:
    """Get users with pagination and caching."""
    skip = (page - 1) * limit
    db_users = await get_users_service(session, skip, limit)
    
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

@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreateRequest,
    session: AsyncSession = Depends(get_db_session)
) -> PostResponse:
    """Create post endpoint with async operations and cache invalidation."""
    db_post = await create_post_service(session, post_data)
    
    # Get author username
    author = await get_user_service(session, db_post.author_id)
    author_username = author.username if author else "Unknown"
    
    return PostResponse(
        id=db_post.id,
        title=db_post.title,
        content=db_post.content,
        author_id=db_post.author_id,
        author_username=author_username,
        tags=db_post.tags.split(",") if db_post.tags else [],
        category=db_post.category,
        is_published=db_post.is_published,
        created_at=db_post.created_at,
        updated_at=db_post.updated_at,
        view_count=db_post.view_count,
        like_count=db_post.like_count,
        comment_count=db_post.comment_count
    )

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int = Path(..., gt=0, description="Post ID"),
    session: AsyncSession = Depends(get_db_session)
) -> PostResponse:
    """Get post by ID endpoint with caching."""
    db_post = await get_post_service(session, post_id)
    
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "Post not found"
        )
    
    # Get author username
    author = await get_user_service(session, db_post.author_id)
    author_username = author.username if author else "Unknown"
    
    return PostResponse(
        id=db_post.id,
        title=db_post.title,
        content=db_post.content,
        author_id=db_post.author_id,
        author_username=author_username,
        tags=db_post.tags.split(",") if db_post.tags else [],
        category=db_post.category,
        is_published=db_post.is_published,
        created_at=db_post.created_at,
        updated_at=db_post.updated_at,
        view_count=db_post.view_count,
        like_count=db_post.like_count,
        comment_count=db_post.comment_count
    )

@app.get("/posts", response_model=List[PostResponse])
async def get_posts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_db_session)
) -> List[PostResponse]:
    """Get posts with pagination and caching."""
    skip = (page - 1) * limit
    db_posts = await get_posts_service(session, skip, limit)
    
    # Get author usernames in batch
    author_ids = list(set(post.author_id for post in db_posts))
    authors: Dict[str, Any] = {}
    
    # Batch fetch authors
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
    author_tasks: List[Any] = [get_user_service(session, author_id) for author_id in author_ids]
    author_results = await asyncio.gather(*author_tasks, return_exceptions=True)
    for author_id, author_result in zip(author_ids, author_results):
        if isinstance(author_result, User):
            authors[author_id] = author_result.username
    
    return [
        PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            author_username=authors.get(post.author_id, "Unknown"),
            tags=post.tags.split(",") if post.tags else [],
            category=post.category,
            is_published=post.is_published,
            created_at=post.created_at,
            updated_at=post.updated_at,
            view_count=post.view_count,
            like_count=post.like_count,
            comment_count=post.comment_count
        )
        for post in db_posts
    ]

@app.get("/cache/stats", response_model=CacheStats)
async async async async def get_cache_stats() -> CacheStats:
    """Get cache statistics."""
    return cache.get_stats()

@app.post("/cache/clear")
async def clear_cache(
    pattern: str = Query(..., description="Cache pattern to clear")
) -> Dict[str, Any]:
    """Clear cache entries matching pattern."""
    deleted_count = await cache.clear_pattern(pattern)
    return {
        "message": f"Cleared {deleted_count} cache entries",
        "pattern": pattern,
        "deleted_count": deleted_count
    }

# =============================================================================
# Background Tasks
# =============================================================================

async async async async def update_post_stats_background(post_id: int) -> bool:
    """Background task to update post statistics."""
    try:
        async with AsyncSessionLocal() as session:
            # Update view count
            await session.execute(
                select(Post).where(Post.id == post_id)
            )
            # TODO: Implement actual statistics update
            logger.info(f"Updated statistics for post {post_id}")
    except Exception as e:
        logger.error(f"Failed to update post statistics: {e}")

@app.post("/posts/{post_id}/view")
async def increment_post_view(
    post_id: int = Path(..., gt=0, description="Post ID"),
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Increment post view count with background task."""
    # Add background task to update statistics
    background_tasks.add_task(update_post_stats_background, post_id)
    
    # Invalidate post cache
    await cache.delete(f"{CacheConfig.POST_CACHE_PREFIX}{post_id}")
    
    return {
        "message": "Post view recorded",
        "post_id": post_id,
        "timestamp": datetime.now().isoformat()
    }

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    
    uvicorn.run(
        "fastapi_async_caching_optimization:app",
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