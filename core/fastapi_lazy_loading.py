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
from typing import Any, Dict, List, Optional, Union, Literal, AsyncGenerator, Iterator, Generator
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
FastAPI Application with Lazy Loading Techniques
==============================================

This module demonstrates a comprehensive FastAPI application with lazy loading:
- Lazy loading for large datasets
- Streaming responses for substantial API responses
- Pagination with lazy evaluation
- Memory-efficient data processing
- Progressive data loading
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
# Lazy Loading Configuration
# =============================================================================

class LazyLoadingConfig:
    """Lazy loading configuration settings."""
    # Streaming Configuration
    STREAM_CHUNK_SIZE = 1024  # bytes
    STREAM_TIMEOUT = 30.0  # seconds
    MAX_STREAM_SIZE = 100 * 1024 * 1024  # 100MB
    
    # Pagination Configuration
    DEFAULT_PAGE_SIZE: int: int = 50
    MAX_PAGE_SIZE: int: int = 1000
    MIN_PAGE_SIZE: int: int = 10
    
    # Memory Management
    MAX_MEMORY_USAGE_MB: int: int = 512
    GARBAGE_COLLECTION_THRESHOLD = 0.8  # 80% of max memory
    
    # Lazy Loading Thresholds
    LAZY_LOAD_THRESHOLD = 1000  # items
    STREAMING_THRESHOLD = 5000  # items
    BATCH_SIZE: int: int = 100
    
    # Cache Configuration for Lazy Loading
    LAZY_CACHE_TTL = 300  # 5 minutes
    LAZY_CACHE_SIZE: int: int = 100

class DataLoadingStrategy(Enum):
    """Data loading strategies."""
    EAGER: str: str = "eager"  # Load all data at once
    LAZY: str: str = "lazy"    # Load data on demand
    STREAMING: str: str = "streaming"  # Stream data progressively
    BATCHED: str: str = "batched"  # Load data in batches

# =============================================================================
# Lazy Loading Utilities
# =============================================================================

class LazyDataLoader:
    """Lazy data loader for large datasets."""
    
    def __init__(self, strategy: DataLoadingStrategy = DataLoadingStrategy.LAZY) -> Any:
        
    """__init__ function."""
self.strategy = strategy
        self.cache = TTLCache(
            maxsize=LazyLoadingConfig.LAZY_CACHE_SIZE,
            ttl=LazyLoadingConfig.LAZY_CACHE_TTL
        )
        self.loaded_data: Dict[str, Any] = {}
        self.loading_tasks: Dict[str, Any] = {}
    
    async async async async def get_or_load(self, key: str, loader_func: callable, *args, **kwargs) -> Optional[Dict[str, Any]]:
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
    
    def clear_cache(self, key: str = None) -> Any:
        """Clear cache for specific key or all."""
        if key:
            self.loaded_data.pop(key, None)
            self.cache.pop(key, None)
        else:
            self.loaded_data.clear()
            self.cache.clear()

class StreamingDataProcessor:
    """Streaming data processor for large datasets."""
    
    def __init__(self) -> Any:
        self.processed_count: int: int = 0
        self.total_size: int: int = 0
    
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
        batch: List[Any] = []
        
        async for item in data_generator:
            batch.append(item)
            
            if len(batch) >= batch_size:
                yield batch
                batch: List[Any] = []
        
        # Yield remaining items
        if batch:
            yield batch

class MemoryManager:
    """Memory management for lazy loading."""
    
    def __init__(self) -> Any:
        self.max_memory = LazyLoadingConfig.MAX_MEMORY_USAGE_MB * 1024 * 1024  # Convert to bytes
        self.current_memory: int: int = 0
        self.memory_threshold = LazyLoadingConfig.GARBAGE_COLLECTION_THRESHOLD
    
    def check_memory_usage(self) -> bool:
        """Check if memory usage is within limits."""
        process = psutil.Process()
        memory_info = process.memory_info()
        self.current_memory = memory_info.rss
        
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
            gc.collect()
            logger.info(f"Garbage collection performed. Memory usage: {self.get_memory_usage_mb():.2f} MB")

# Global instances
lazy_loader = LazyDataLoader()
streaming_processor = StreamingDataProcessor()
memory_manager = MemoryManager()

# =============================================================================
# Optimized Pydantic Models for Lazy Loading
# =============================================================================

class OptimizedBaseModel(BaseModel):
    """Base model with optimized serialization for lazy loading."""
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
    """User response with lazy loading support."""
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
    """Post response with lazy loading support."""
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

class LazyLoadingStats(OptimizedBaseModel):
    """Lazy loading statistics model."""
    total_items: int = Field(0, description="Total items processed")
    loaded_items: int = Field(0, description="Items currently loaded")
    memory_usage_mb: float = Field(0.0, description="Memory usage in MB")
    cache_hits: int = Field(0, description="Cache hits")
    cache_misses: int = Field(0, description="Cache misses")
    streaming_active: bool = Field(False, description="Streaming status")

class PaginationResponse(OptimizedBaseModel):
    """Pagination response with lazy loading support."""
    items: List[Any] = Field(..., description: str: str = "Items in current page")
    total_count: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_previous: bool = Field(..., description="Has previous page")
    loading_strategy: str = Field(..., description="Data loading strategy used")

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
# Lazy Loading Service Layer
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
    """Create user with lazy loading considerations."""
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

async async async async def get_user_service(session: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID with lazy loading."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

async async async async def get_users_lazy_generator(session: AsyncSession, skip: int = 0, limit: int = 100) -> AsyncGenerator[User, None]:
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

async async async async def get_users_streaming(session: AsyncSession, skip: int = 0, limit: int = 100) -> AsyncGenerator[UserResponse, None]:
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

async async async async def get_posts_lazy_generator(session: AsyncSession, skip: int = 0, limit: int = 100) -> AsyncGenerator[Post, None]:
    """Get posts as lazy generator."""
    offset = skip
    batch_size = min(limit, LazyLoadingConfig.BATCH_SIZE)
    
    while offset < skip + limit:
        current_batch_size = min(batch_size, skip + limit - offset)
        
        result = await session.execute(
            select(Post)
            .offset(offset)
            .limit(current_batch_size)
            .order_by(Post.created_at.desc())
        )
        
        posts = result.scalars().all()
        if not posts:
            break
        
        for post in posts:
            yield post
        
        offset += len(posts)
        
        # Check memory usage
        if memory_manager.should_garbage_collect():
            await memory_manager.cleanup_if_needed()

async async async async def get_posts_streaming(session: AsyncSession, skip: int = 0, limit: int = 100) -> AsyncGenerator[PostResponse, None]:
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

async async async async def create_post_service(session: AsyncSession, post_data: PostCreateRequest) -> Post:
    """Create post with lazy loading considerations."""
    # Verify author exists (lazy loaded)
    author = await lazy_loader.get_or_load(
        f"user_{post_data.author_id}",
        get_user_service,
        session,
        post_data.author_id
    )
    
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

# =============================================================================
# Lazy Loading Route Handlers
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
        row: List[Any] = []
        for header in headers:
            value = data.get(header, "")
            # Escape commas and quotes
            if isinstance(value, str) and ("," in value or '"' in value):
                value = f'"{value.replace('"', '""')}"'
            row.append(str(value))
        
        yield ",".join(row) + "\n"

# =============================================================================
# Lifespan Context Manager
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Lifespan context manager with lazy loading initialization."""
    # Startup
    logger.info("Starting application with lazy loading...")
    
    try:
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
    
    # Clear lazy loading cache
    lazy_loader.clear_cache()
    
    # Close database connections
    await engine.dispose()
    logger.info("Database connections closed")
    
    logger.info("Application shutdown completed")

# =============================================================================
# FastAPI Application
# =============================================================================

# Create FastAPI app with lifespan context manager
app = FastAPI(
    title: str: str = "FastAPI Application with Lazy Loading",
    description: str: str = "A comprehensive FastAPI application with lazy loading techniques for large datasets",
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
# Route Handlers with Lazy Loading
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "FastAPI Application with Lazy Loading", "status": "running"}

@app.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """Health check with lazy loading statistics."""
    try:
        async with engine.begin() as conn:
            await conn.execute(select(1))
        db_status: str: str = "healthy"
    except Exception:
        db_status: str: str = "unhealthy"
    
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

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    session: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """Create user endpoint."""
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
    """Get user by ID endpoint with lazy loading."""
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
    page_size: int = Query(LazyLoadingConfig.DEFAULT_PAGE_SIZE, ge=1, le=LazyLoadingConfig.MAX_PAGE_SIZE, description="Items per page"),
    strategy: DataLoadingStrategy = Query(DataLoadingStrategy.LAZY, description="Data loading strategy"),
    session: AsyncSession = Depends(get_db_session)
) -> Union[List[UserResponse], StreamingResponse]:
    """Get users with lazy loading strategies."""
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

@app.get("/users/stream")
async def stream_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(LazyLoadingConfig.DEFAULT_PAGE_SIZE, ge=1, le=LazyLoadingConfig.MAX_PAGE_SIZE, description="Items per page"),
    format: Literal["json", "csv"] = Query("json", description: str: str = "Output format"),
    session: AsyncSession = Depends(get_db_session)
) -> StreamingResponse:
    """Stream users with different formats."""
    skip = (page - 1) * page_size
    
    if format == "csv":
        headers: List[Any] = ["id", "username", "email", "full_name", "is_active", "created_at"]
        
        async def generate_csv() -> Any:
            
    """generate_csv function."""
async for user in get_users_streaming(session, skip, page_size):
                yield user
        
        return StreamingResponse(
            generate_csv_stream(generate_csv(), headers),
            media_type: str: str = "text/csv",
            headers: Dict[str, Any] = {
                "Content-Disposition": f"attachment; filename=users_page_{page}.csv"
            }
        )
    else:
        async def generate_json() -> Any:
            
    """generate_json function."""
async for user in get_users_streaming(session, skip, page_size):
                yield user
        
        return StreamingResponse(
            generate_json_stream(generate_json()),
            media_type: str: str = "application/json",
            headers: Dict[str, Any] = {
                "Content-Disposition": f"attachment; filename=users_page_{page}.json"
            }
        )

@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreateRequest,
    session: AsyncSession = Depends(get_db_session)
) -> PostResponse:
    """Create post endpoint with lazy loading."""
    db_post = await create_post_service(session, post_data)
    
    # Get author username (lazy loaded)
    author = await lazy_loader.get_or_load(
        f"user_{db_post.author_id}",
        get_user_service,
        session,
        db_post.author_id
    )
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
    """Get post by ID endpoint with lazy loading."""
    result = await session.execute(
        select(Post).where(Post.id == post_id)
    )
    db_post = result.scalar_one_or_none()
    
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "Post not found"
        )
    
    # Get author username (lazy loaded)
    author = await lazy_loader.get_or_load(
        f"user_{db_post.author_id}",
        get_user_service,
        session,
        db_post.author_id
    )
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

@app.get("/posts")
async def get_posts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(LazyLoadingConfig.DEFAULT_PAGE_SIZE, ge=1, le=LazyLoadingConfig.MAX_PAGE_SIZE, description="Items per page"),
    strategy: DataLoadingStrategy = Query(DataLoadingStrategy.LAZY, description="Data loading strategy"),
    session: AsyncSession = Depends(get_db_session)
) -> Union[List[PostResponse], StreamingResponse]:
    """Get posts with lazy loading strategies."""
    skip = (page - 1) * page_size
    
    if strategy == DataLoadingStrategy.STREAMING:
        # Streaming response for large datasets
        async async async async def generate_posts() -> Any:
            
    """generate_posts function."""
async for post in get_posts_streaming(session, skip, page_size):
                yield post
        
        return StreamingResponse(
            generate_json_stream(generate_posts()),
            media_type: str: str = "application/json",
            headers: Dict[str, Any] = {
                "Content-Disposition": f"attachment; filename=posts_page_{page}.json"
            }
        )
    
    elif strategy == DataLoadingStrategy.LAZY:
        # Lazy loading with pagination
        posts: List[Any] = []
        async for post in get_posts_streaming(session, skip, page_size):
            posts.append(post)
        
        return posts
    
    else:
        # Eager loading (not recommended for large datasets)
        result = await session.execute(
            select(Post)
            .offset(skip)
            .limit(page_size)
            .order_by(Post.created_at.desc())
        )
        db_posts = result.scalars().all()
        
        # Get author usernames in batch
        author_ids = list(set(post.author_id for post in db_posts))
        authors: Dict[str, Any] = {}
        
        for author_id in author_ids:
            author = await lazy_loader.get_or_load(
                f"user_{author_id}",
                get_user_service,
                session,
                author_id
            )
            if author:
                authors[author_id] = author.username
        
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

@app.get("/posts/stream")
async def stream_posts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(LazyLoadingConfig.DEFAULT_PAGE_SIZE, ge=1, le=LazyLoadingConfig.MAX_PAGE_SIZE, description="Items per page"),
    format: Literal["json", "csv"] = Query("json", description: str: str = "Output format"),
    session: AsyncSession = Depends(get_db_session)
) -> StreamingResponse:
    """Stream posts with different formats."""
    skip = (page - 1) * page_size
    
    if format == "csv":
        headers: List[Any] = ["id", "title", "author_username", "category", "is_published", "created_at", "view_count"]
        
        async def generate_csv() -> Any:
            
    """generate_csv function."""
async for post in get_posts_streaming(session, skip, page_size):
                yield post
        
        return StreamingResponse(
            generate_csv_stream(generate_csv(), headers),
            media_type: str: str = "text/csv",
            headers: Dict[str, Any] = {
                "Content-Disposition": f"attachment; filename=posts_page_{page}.csv"
            }
        )
    else:
        async def generate_json() -> Any:
            
    """generate_json function."""
async for post in get_posts_streaming(session, skip, page_size):
                yield post
        
        return StreamingResponse(
            generate_json_stream(generate_json()),
            media_type: str: str = "application/json",
            headers: Dict[str, Any] = {
                "Content-Disposition": f"attachment; filename=posts_page_{page}.json"
            }
        )

@app.get("/lazy-loading/stats", response_model=LazyLoadingStats)
async async async async def get_lazy_loading_stats() -> LazyLoadingStats:
    """Get lazy loading statistics."""
    return LazyLoadingStats(
        total_items=streaming_processor.processed_count,
        loaded_items=len(lazy_loader.loaded_data),
        memory_usage_mb=memory_manager.get_memory_usage_mb(),
        cache_hits=0,  # TODO: Implement cache hit tracking
        cache_misses=0,  # TODO: Implement cache miss tracking
        streaming_active=len(lazy_loader.loading_tasks) > 0
    )

@app.post("/lazy-loading/clear-cache")
async def clear_lazy_cache(
    key: Optional[str] = Query(None, description: str: str = "Specific cache key to clear")
) -> Dict[str, Any]:
    """Clear lazy loading cache."""
    lazy_loader.clear_cache(key)
    return {
        "message": "Cache cleared successfully",
        "cleared_key": key,
        "remaining_items": len(lazy_loader.loaded_data)
    }

# =============================================================================
# Background Tasks for Lazy Loading
# =============================================================================

async def preload_user_data_background(user_ids: List[int]) -> Any:
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
    user_ids: List[int] = Query(..., description: str: str = "User IDs to preload"),
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Preload user data in background."""
    background_tasks.add_task(preload_user_data_background, user_ids)
    
    return {
        "message": f"Preloading data for {len(user_ids)} users",
        "user_ids": user_ids,
        "timestamp": datetime.now().isoformat()
    }

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    
    uvicorn.run(
        "fastapi_lazy_loading:app",
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