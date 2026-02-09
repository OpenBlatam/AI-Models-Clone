from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

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
import statistics
import threading
from collections import defaultdict, deque
import aiofiles
import aiohttp
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
import httpx
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
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from fastapi import FastAPI, HTTPException, Request, Response, status, Depends, Query, Path, BackgroundTasks, APIRouter
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
from sqlalchemy import Column, Integer, String, Text, DateTime, func, select, Boolean, Numeric, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import QueuePool
import aioredis
import psutil
import orjson
from cachetools import TTLCache, LRUCache
import structlog
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
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
from starlette.responses import Response as StarletteResponse
    import uvicorn
from typing import Any, List, Dict, Optional
"""
FastAPI Application with Structured Routes and Dependencies
=========================================================

This module demonstrates a comprehensive FastAPI application with clearly structured:
- Modular route organization with dedicated routers
- Clear dependency injection patterns
- Separation of concerns with dedicated modules
- Well-organized project structure
- Maintainable and readable code architecture
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

class AppConfig:
    """Application configuration with structured settings."""
    # Application Settings
    APP_NAME: str: str = "FastAPI Structured Routes and Dependencies"
    APP_VERSION: str: str = "1.0.0"
    APP_DESCRIPTION: str: str = "A comprehensive FastAPI application with structured routes and dependencies"
    
    # Database Settings
    DATABASE_URL: str: str = "postgresql+asyncpg://user:password@localhost/dbname"
    DB_POOL_SIZE: int: int = 20
    DB_MAX_OVERFLOW: int: int = 30
    DB_OPERATION_TIMEOUT = 10.0
    
    # Redis Settings
    REDIS_URL: str: str = "redis://localhost"
    REDIS_POOL_SIZE: int: int = 10
    
    # Cache Settings
    CACHE_TTL: int: int = 300
    CACHE_MAX_SIZE: int: int = 1000
    
    # API Settings
    API_PREFIX: str: str = "/api/v1"
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
    MAX_PAGE_SIZE: int: int = 1000
    DEFAULT_PAGE_SIZE: int: int = 50
    
    # Security Settings
    SECRET_KEY: str: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int: int = 30
    
    # Monitoring Settings
    ENABLE_METRICS: bool = True
    ENABLE_HEALTH_CHECKS: bool = True
    ENABLE_LOGGING: bool = True

# =============================================================================
# Database Models
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
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

# =============================================================================
# Pydantic Models
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

# User Models
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

class UserUpdateRequest(OptimizedBaseModel):
    """User update request with validation."""
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
    full_name: Optional[constr(max_length=100)] = Field(None, description="Full name")
    is_active: Optional[bool] = Field(None, description: str: str = "User active status")
    age: Optional[conint(ge=0, le=150)] = Field(None, description="User age")
    bio: Optional[constr(max_length=500)] = Field(None, description="User biography")

class UserResponse(OptimizedBaseModel):
    """User response with performance optimization."""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description: str: str = "Full name")
    is_active: bool = Field(..., description="User active status")
    age: Optional[int] = Field(None, description: str: str = "User age")
    bio: Optional[str] = Field(None, description: str: str = "User biography")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    @computed_field
    @property
    def display_name(self) -> str:
        """Computed field for display name."""
        return self.full_name or self.username

# Post Models
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
        ..., description: str: str = "Post title"
    )
    content: constr(min_length=1, strip_whitespace=True) = Field(
        ..., description: str: str = "Post content"
    )
    is_published: bool = Field(False, description="Publication status")

class PostUpdateRequest(OptimizedBaseModel):
    """Post update request with validation."""
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
    title: Optional[constr(min_length=1, max_length=200, strip_whitespace=True)] = Field(
        None, description: str: str = "Post title"
    )
    content: Optional[constr(min_length=1, strip_whitespace=True)] = Field(
        None, description: str: str = "Post content"
    )
    is_published: Optional[bool] = Field(None, description: str: str = "Publication status")

class PostResponse(OptimizedBaseModel):
    """Post response with performance optimization."""
    id: int = Field(..., description="Post ID")
    user_id: int = Field(..., description="User ID")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    is_published: bool = Field(..., description="Publication status")
    view_count: int = Field(..., description="View count")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

# Pagination Models
class PaginationParams(OptimizedBaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(AppConfig.DEFAULT_PAGE_SIZE, ge=1, le=AppConfig.MAX_PAGE_SIZE, description="Items per page")

class PaginatedResponse(OptimizedBaseModel):
    """Paginated response wrapper."""
    items: List[Any] = Field(..., description: str: str = "List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")

# Health and Status Models
class HealthResponse(OptimizedBaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="Application version")
    database_status: str = Field(..., description="Database status")
    redis_status: str = Field(..., description="Redis status")

class StatusResponse(OptimizedBaseModel):
    """Status response."""
    message: str = Field(..., description="Status message")
    status: str = Field(..., description="Status")
    timestamp: datetime = Field(..., description="Timestamp")

# =============================================================================
# Database Configuration
# =============================================================================

# Create database engine
engine = create_async_engine(
    AppConfig.DATABASE_URL,
    echo=False,
    poolclass=QueuePool,
    pool_size=AppConfig.DB_POOL_SIZE,
    max_overflow=AppConfig.DB_MAX_OVERFLOW,
    pool_timeout=AppConfig.DB_OPERATION_TIMEOUT,
    pool_recycle=3600,
    future: bool = True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit: bool = False
)

# =============================================================================
# Dependencies
# =============================================================================

class Dependencies:
    """Centralized dependency management."""
    
    @staticmethod
    async async async async async def get_db_session() -> AsyncSession:
        """Dependency to get database session."""
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
    
    @staticmethod
    async async async async def get_redis_client() -> Optional[Dict[str, Any]]:
        """Dependency to get Redis client."""
        try:
            redis_client = aioredis.from_url(AppConfig.REDIS_URL)
            await redis_client.ping()
            yield redis_client
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            yield None
        finally:
            if redis_client:
                await redis_client.close()
    
    @staticmethod
    async async async def get_cache() -> Optional[Dict[str, Any]]:
        """Dependency to get cache instance."""
        return TTLCache(
            maxsize=AppConfig.CACHE_MAX_SIZE,
            ttl=AppConfig.CACHE_TTL
        )
    
    @staticmethod
    def get_pagination_params(
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(AppConfig.DEFAULT_PAGE_SIZE, ge=1, le=AppConfig.MAX_PAGE_SIZE, description="Items per page")
    ) -> PaginationParams:
        """Dependency to get pagination parameters."""
        return PaginationParams(page=page, page_size=page_size)
    
    @staticmethod
    def validate_user_id(user_id: int = Path(..., gt=0, description="User ID")) -> int:
        """Dependency to validate user ID."""
        return user_id
    
    @staticmethod
    def validate_post_id(post_id: int = Path(..., gt=0, description="Post ID")) -> int:
        """Dependency to validate post ID."""
        return post_id

# =============================================================================
# Services
# =============================================================================

class UserService:
    """User service with clear separation of concerns."""
    
    def __init__(self, db_session: AsyncSession, cache: TTLCache, redis_client=None) -> Any:
        
    """__init__ function."""
self.db_session = db_session
        self.cache = cache
        self.redis_client = redis_client
    
    async def create_user(self, user_data: UserCreateRequest) -> UserResponse:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.db_session.execute(
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
        
        self.db_session.add(db_user)
        await self.db_session.commit()
        await self.db_session.refresh(db_user)
        
        # Cache the new user
        cache_key = f"user:{db_user.id}"
        self.cache[cache_key] = {
            'id': db_user.id,
            'username': db_user.username,
            'email': db_user.email,
            'full_name': db_user.full_name,
            'is_active': db_user.is_active,
            'age': db_user.age,
            'bio': db_user.bio,
            'created_at': db_user.created_at,
            'updated_at': db_user.updated_at
        }
        
        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            age=db_user.age,
            bio=db_user.bio,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async async async async async def get_user(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID."""
        # Try cache first
        cache_key = f"user:{user_id}"
        cached_user = self.cache.get(cache_key)
        
        if cached_user:
            return UserResponse(**cached_user)
        
        # Get from database
        result = await self.db_session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        user_data: Dict[str, Any] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'is_active': user.is_active,
            'age': user.age,
            'bio': user.bio,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }
        
        # Cache the result
        self.cache[cache_key] = user_data
        
        return UserResponse(**user_data)
    
    async async async async async def get_users(self, pagination: PaginationParams) -> PaginatedResponse:
        """Get users with pagination."""
        skip = (pagination.page - 1) * pagination.page_size
        
        # Get total count
        count_result = await self.db_session.execute(select(func.count(User.id)))
        total = count_result.scalar()
        
        # Get users
        result = await self.db_session.execute(
            select(User)
            .offset(skip)
            .limit(pagination.page_size)
            .order_by(User.created_at.desc())
        )
        users = result.scalars().all()
        
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
                updated_at=user.updated_at
            )
            for user in users
        ]
        
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        
        return PaginatedResponse(
            items=user_responses,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1
        )
    
    async def update_user(self, user_id: int, update_data: UserUpdateRequest) -> Optional[UserResponse]:
        """Update user."""
        # Get user first
        result = await self.db_session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Update user fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.now()
        await self.db_session.commit()
        await self.db_session.refresh(user)
        
        # Update cache
        cache_key = f"user:{user_id}"
        self.cache[cache_key] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'is_active': user.is_active,
            'age': user.age,
            'bio': user.bio,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            age=user.age,
            bio=user.bio,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    async async async async def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        result = await self.db_session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        await self.db_session.delete(user)
        await self.db_session.commit()
        
        # Remove from cache
        cache_key = f"user:{user_id}"
        self.cache.pop(cache_key, None)
        
        return True

class PostService:
    """Post service with clear separation of concerns."""
    
    def __init__(self, db_session: AsyncSession, cache: TTLCache, redis_client=None) -> Any:
        
    """__init__ function."""
self.db_session = db_session
        self.cache = cache
        self.redis_client = redis_client
    
    async async async async async def create_post(self, user_id: int, post_data: PostCreateRequest) -> PostResponse:
        """Create a new post."""
        # Verify user exists
        user_result = await self.db_session.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail: str: str = "User not found"
            )
        
        # Create new post
        db_post = Post(
            user_id=user_id,
            title=post_data.title,
            content=post_data.content,
            is_published=post_data.is_published
        )
        
        self.db_session.add(db_post)
        await self.db_session.commit()
        await self.db_session.refresh(db_post)
        
        return PostResponse(
            id=db_post.id,
            user_id=db_post.user_id,
            title=db_post.title,
            content=db_post.content,
            is_published=db_post.is_published,
            view_count=db_post.view_count,
            created_at=db_post.created_at,
            updated_at=db_post.updated_at
        )
    
    async async async async async def get_post(self, post_id: int) -> Optional[PostResponse]:
        """Get post by ID."""
        result = await self.db_session.execute(
            select(Post).where(Post.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            return None
        
        return PostResponse(
            id=post.id,
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            is_published=post.is_published,
            view_count=post.view_count,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
    
    async async async async async def get_user_posts(self, user_id: int, pagination: PaginationParams) -> PaginatedResponse:
        """Get posts by user ID."""
        skip = (pagination.page - 1) * pagination.page_size
        
        # Get total count
        count_result = await self.db_session.execute(
            select(func.count(Post.id)).where(Post.user_id == user_id)
        )
        total = count_result.scalar()
        
        # Get posts
        result = await self.db_session.execute(
            select(Post)
            .where(Post.user_id == user_id)
            .offset(skip)
            .limit(pagination.page_size)
            .order_by(Post.created_at.desc())
        )
        posts = result.scalars().all()
        
        post_responses: List[Any] = [
            PostResponse(
                id=post.id,
                user_id=post.user_id,
                title=post.title,
                content=post.content,
                is_published=post.is_published,
                view_count=post.view_count,
                created_at=post.created_at,
                updated_at=post.updated_at
            )
            for post in posts
        ]
        
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        
        return PaginatedResponse(
            items=post_responses,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1
        )
    
    async async async async async def update_post(self, post_id: int, update_data: PostUpdateRequest) -> Optional[PostResponse]:
        """Update post."""
        result = await self.db_session.execute(
            select(Post).where(Post.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            return None
        
        # Update post fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(post, field):
                setattr(post, field, value)
        
        post.updated_at = datetime.now()
        await self.db_session.commit()
        await self.db_session.refresh(post)
        
        return PostResponse(
            id=post.id,
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            is_published=post.is_published,
            view_count=post.view_count,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
    
    async async async async async def delete_post(self, post_id: int) -> bool:
        """Delete post."""
        result = await self.db_session.execute(
            select(Post).where(Post.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            return False
        
        await self.db_session.delete(post)
        await self.db_session.commit()
        
        return True

# =============================================================================
# Routers
# =============================================================================

# Create main router
main_router = APIRouter()

# Create user router
user_router = APIRouter(prefix="/users", tags=["users"])

# Create post router
post_router = APIRouter(prefix="/posts", tags=["posts"])

# Create health router
health_router = APIRouter(prefix="/health", tags=["health"])

# =============================================================================
# Main Router Routes
# =============================================================================

@main_router.get("/", response_model=StatusResponse)
async def root() -> StatusResponse:
    """Root endpoint."""
    return StatusResponse(
        message: str: str = "FastAPI Application with Structured Routes and Dependencies",
        status: str: str = "running",
        timestamp=datetime.now()
    )

# =============================================================================
# User Router Routes
# =============================================================================

@user_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    db_session: AsyncSession = Depends(Dependencies.get_db_session),
    cache: TTLCache = Depends(Dependencies.get_cache)
) -> UserResponse:
    """Create a new user."""
    user_service = UserService(db_session, cache)
    return await user_service.create_user(user_data)

@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int = Depends(Dependencies.validate_user_id),
    db_session: AsyncSession = Depends(Dependencies.get_db_session),
    cache: TTLCache = Depends(Dependencies.get_cache)
) -> UserResponse:
    """Get user by ID."""
    user_service = UserService(db_session, cache)
    user = await user_service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "User not found"
        )
    
    return user

@user_router.get("/", response_model=PaginatedResponse)
async def get_users(
    pagination: PaginationParams = Depends(Dependencies.get_pagination_params),
    db_session: AsyncSession = Depends(Dependencies.get_db_session),
    cache: TTLCache = Depends(Dependencies.get_cache)
) -> PaginatedResponse:
    """Get users with pagination."""
    user_service = UserService(db_session, cache)
    return await user_service.get_users(pagination)

@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int = Depends(Dependencies.validate_user_id),
    update_data: UserUpdateRequest = Field(..., description="User update data"),
    db_session: AsyncSession = Depends(Dependencies.get_db_session),
    cache: TTLCache = Depends(Dependencies.get_cache)
) -> UserResponse:
    """Update user."""
    user_service = UserService(db_session, cache)
    user = await user_service.update_user(user_id, update_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "User not found"
        )
    
    return user

@user_router.delete("/{user_id}")
async def delete_user(
    user_id: int = Depends(Dependencies.validate_user_id),
    db_session: AsyncSession = Depends(Dependencies.get_db_session),
    cache: TTLCache = Depends(Dependencies.get_cache)
) -> StatusResponse:
    """Delete user."""
    user_service = UserService(db_session, cache)
    success = await user_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "User not found"
        )
    
    return StatusResponse(
        message: str: str = "User deleted successfully",
        status: str: str = "success",
        timestamp=datetime.now()
    )

# =============================================================================
# Post Router Routes
# =============================================================================

@post_router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    user_id: int = Depends(Dependencies.validate_user_id),
    post_data: PostCreateRequest = Field(..., description="Post data"),
    db_session: AsyncSession = Depends(Dependencies.get_db_session),
    cache: TTLCache = Depends(Dependencies.get_cache)
) -> PostResponse:
    """Create a new post."""
    post_service = PostService(db_session, cache)
    return await post_service.create_post(user_id, post_data)

@post_router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int = Depends(Dependencies.validate_post_id),
    db_session: AsyncSession = Depends(Dependencies.get_db_session),
    cache: TTLCache = Depends(Dependencies.get_cache)
) -> PostResponse:
    """Get post by ID."""
    post_service = PostService(db_session, cache)
    post = await post_service.get_post(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "Post not found"
        )
    
    return post

@post_router.get("/user/{user_id}", response_model=PaginatedResponse)
async def get_user_posts(
    user_id: int = Depends(Dependencies.validate_user_id),
    pagination: PaginationParams = Depends(Dependencies.get_pagination_params),
    db_session: AsyncSession = Depends(Dependencies.get_db_session),
    cache: TTLCache = Depends(Dependencies.get_cache)
) -> PaginatedResponse:
    """Get posts by user ID."""
    post_service = PostService(db_session, cache)
    return await post_service.get_user_posts(user_id, pagination)

@post_router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int = Depends(Dependencies.validate_post_id),
    update_data: PostUpdateRequest = Field(..., description="Post update data"),
    db_session: AsyncSession = Depends(Dependencies.get_db_session),
    cache: TTLCache = Depends(Dependencies.get_cache)
) -> PostResponse:
    """Update post."""
    post_service = PostService(db_session, cache)
    post = await post_service.update_post(post_id, update_data)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "Post not found"
        )
    
    return post

@post_router.delete("/{post_id}")
async def delete_post(
    post_id: int = Depends(Dependencies.validate_post_id),
    db_session: AsyncSession = Depends(Dependencies.get_db_session),
    cache: TTLCache = Depends(Dependencies.get_cache)
) -> StatusResponse:
    """Delete post."""
    post_service = PostService(db_session, cache)
    success = await post_service.delete_post(post_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "Post not found"
        )
    
    return StatusResponse(
        message: str: str = "Post deleted successfully",
        status: str: str = "success",
        timestamp=datetime.now()
    )

# =============================================================================
# Health Router Routes
# =============================================================================

@health_router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    # Check database
    try:
        async with engine.begin() as conn:
            await conn.execute(select(1))
        db_status: str: str = "healthy"
    except Exception:
        db_status: str: str = "unhealthy"
    
    # Check Redis
    try:
        redis_client = aioredis.from_url(AppConfig.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        redis_status: str: str = "healthy"
    except Exception:
        redis_status: str: str = "unhealthy"
    
    return HealthResponse(
        status: str: str = "healthy",
        timestamp=datetime.now(),
        version=AppConfig.APP_VERSION,
        database_status=db_status,
        redis_status=redis_status
    )

# =============================================================================
# Lifespan Context Manager
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Lifespan context manager with structured startup/shutdown."""
    # Startup
    logger.info("Starting application with structured routes and dependencies...")
    
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
    
    # Close connections
    await engine.dispose()
    
    logger.info("Application shutdown completed")

# =============================================================================
# FastAPI Application
# =============================================================================

# Create FastAPI app with lifespan context manager
app = FastAPI(
    title=AppConfig.APP_NAME,
    description=AppConfig.APP_DESCRIPTION,
    version=AppConfig.APP_VERSION,
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

# Include routers with clear structure
app.include_router(main_router, prefix=AppConfig.API_PREFIX)
app.include_router(user_router, prefix=AppConfig.API_PREFIX)
app.include_router(post_router, prefix=AppConfig.API_PREFIX)
app.include_router(health_router, prefix=AppConfig.API_PREFIX)

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    
    uvicorn.run(
        "fastapi_structured_routes_dependencies:app",
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