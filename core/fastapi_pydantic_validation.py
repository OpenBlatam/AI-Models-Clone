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
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union, Literal
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal
from fastapi import FastAPI, HTTPException, Request, Response, status, Depends, Query, Path
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
from pydantic import BaseModel, Field, validator, root_validator, ConfigDict, EmailStr, HttpUrl
from pydantic.types import conint, constr, condecimal
from sqlalchemy import Column, Integer, String, Text, DateTime, func, select, Boolean, Numeric
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import QueuePool
import psutil
    import uvicorn
from typing import Any, List, Dict, Optional
"""
FastAPI Application with Comprehensive Pydantic Validation
========================================================

This module demonstrates a comprehensive FastAPI application using Pydantic's BaseModel
for consistent input/output validation and response schemas throughout the application.
"""



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format: str: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# Pydantic Base Models for Input Validation
# =============================================================================

class UserCreateRequest(BaseModel):
    """User creation request model with comprehensive validation."""
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
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra: str: str = 'forbid',
        json_schema_extra: Dict[str, Any] = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "age": 30,
                "bio": "Software developer"
            }
        }
    )
    
    username: constr(min_length=3, max_length=50, strip_whitespace=True) = Field(
        ..., 
        description: str: str = "Username (3-50 characters)",
        pattern=r"^[a-zA-Z0-9_]+$"
    )
    email: EmailStr = Field(..., description="Valid email address")
    full_name: Optional[constr(max_length=100)] = Field(None, description="Full name")
    is_active: bool = Field(True, description="User active status")
    age: Optional[conint(ge=0, le=150)] = Field(None, description="User age (0-150)")
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
    
    @root_validator
    def validate_user_data(cls, values) -> bool:
        """Validate user data consistency."""
        username = values.get('username')
        email = values.get('email')
        
        if username and email:
            # Check if username and email are related
            if username.split('_')[0].lower() in email.lower():
                logger.info(f"Username and email are related for user: {username}")
        
        return values

class UserUpdateRequest(BaseModel):
    """User update request model with partial validation."""
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
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra: str: str = 'forbid'
    )
    
    username: Optional[constr(min_length=3, max_length=50)] = Field(None, description="Username")
    email: Optional[EmailStr] = Field(None, description: str: str = "Email address")
    full_name: Optional[constr(max_length=100)] = Field(None, description="Full name")
    is_active: Optional[bool] = Field(None, description: str: str = "User active status")
    age: Optional[conint(ge=0, le=150)] = Field(None, description="User age")
    bio: Optional[constr(max_length=500)] = Field(None, description="User biography")
    
    @validator('username')
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format."""
        if v is not None:
            if not v.isalnum() and '_' not in v:
                raise ValueError('Username must contain only letters, numbers, and underscores')
            return v.lower()
        return v

class PostCreateRequest(BaseModel):
    """Post creation request model with comprehensive validation."""
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
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra: str: str = 'forbid',
        json_schema_extra: Dict[str, Any] = {
            "example": {
                "title": "My First Post",
                "content": "This is the content of my first post.",
                "author_id": 1,
                "tags": ["technology", "programming"],
                "is_published": True,
                "category": "technology"
            }
        }
    )
    
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
    
    @validator('title')
    def validate_title(cls, v: str) -> str:
        """Validate title format."""
        if len(v.strip()) < 1:
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v: str) -> str:
        """Validate content format."""
        if len(v.strip()) < 10:
            raise ValueError('Content must be at least 10 characters long')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags."""
        # Remove duplicates and empty tags
        unique_tags = list(set(tag.strip().lower() for tag in v if tag.strip()))
        if len(unique_tags) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return unique_tags

class PostUpdateRequest(BaseModel):
    """Post update request model with partial validation."""
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
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra: str: str = 'forbid'
    )
    
    title: Optional[constr(min_length=1, max_length=200)] = Field(None, description="Post title")
    content: Optional[constr(min_length=1, max_length=10000)] = Field(None, description="Post content")
    tags: Optional[List[constr(max_length=50)]] = Field(None, description="Post tags")
    is_published: Optional[bool] = Field(None, description: str: str = "Post publication status")
    category: Optional[Literal["technology", "science", "business", "lifestyle", "other"]] = Field(
        None, 
        description: str: str = "Post category"
    )

class CommentCreateRequest(BaseModel):
    """Comment creation request model."""
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
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra: str: str = 'forbid'
    )
    
    content: constr(min_length=1, max_length=1000) = Field(
        ..., 
        description: str: str = "Comment content (1-1000 characters)"
    )
    post_id: conint(gt=0) = Field(..., description="Post ID")
    author_id: conint(gt=0) = Field(..., description="Author ID")
    parent_comment_id: Optional[conint(gt=0)] = Field(None, description="Parent comment ID for replies")

class SearchRequest(BaseModel):
    """Search request model with pagination and filtering."""
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
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra: str: str = 'forbid'
    )
    
    query: Optional[constr(max_length=200)] = Field(None, description="Search query")
    category: Optional[Literal["technology", "science", "business", "lifestyle", "other"]] = Field(
        None, 
        description: str: str = "Filter by category"
    )
    author_id: Optional[conint(gt=0)] = Field(None, description="Filter by author")
    is_published: Optional[bool] = Field(None, description: str: str = "Filter by publication status")
    tags: Optional[List[constr(max_length=50)]] = Field(None, description="Filter by tags")
    date_from: Optional[date] = Field(None, description: str: str = "Filter by start date")
    date_to: Optional[date] = Field(None, description: str: str = "Filter by end date")
    page: conint(ge=1) = Field(1, description="Page number (1 or greater)")
    limit: conint(ge=1, le=100) = Field(20, description="Items per page (1-100)")
    sort_by: Literal["created_at", "updated_at", "title", "author"] = Field(
        "created_at", 
        description: str: str = "Sort field"
    )
    sort_order: Literal["asc", "desc"] = Field("desc", description: str: str = "Sort order")

# =============================================================================
# Pydantic Base Models for Response Schemas
# =============================================================================

class UserResponse(BaseModel):
    """User response model with comprehensive data."""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders: Dict[str, Any] = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
    )
    
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

class UserListResponse(BaseModel):
    """User list response model with pagination."""
    users: List[UserResponse] = Field(..., description: str: str = "List of users")
    total_count: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_previous: bool = Field(..., description="Has previous page")

class PostResponse(BaseModel):
    """Post response model with comprehensive data."""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders: Dict[str, Any] = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
    )
    
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

class PostListResponse(BaseModel):
    """Post list response model with pagination."""
    posts: List[PostResponse] = Field(..., description: str: str = "List of posts")
    total_count: int = Field(..., description="Total number of posts")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_previous: bool = Field(..., description="Has previous page")

class CommentResponse(BaseModel):
    """Comment response model."""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders: Dict[str, Any] = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
    )
    
    id: int = Field(..., description="Comment ID")
    content: str = Field(..., description="Comment content")
    post_id: int = Field(..., description="Post ID")
    author_id: int = Field(..., description="Author ID")
    author_username: str = Field(..., description="Author username")
    parent_comment_id: Optional[int] = Field(None, description: str: str = "Parent comment ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    like_count: int = Field(0, description="Like count")

class ErrorResponse(BaseModel):
    """Error response model with consistent structure."""
    model_config = ConfigDict(
        json_schema_extra: Dict[str, Any] = {
            "example": {
                "error": "Validation error",
                "message": "Invalid input data",
                "details": [
                    {
                        "field": "email",
                        "message": "Invalid email format"
                    }
                ],
                "timestamp": "2024-01-15T10:30:00",
                "request_id": "123e4567-e89b-12d3-a456-426614174000"
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
            }
        }
    )
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[List[Dict[str, Any]]] = Field(None, description: str: str = "Error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    request_id: Optional[str] = Field(None, description: str: str = "Request ID for tracking")
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

class SuccessResponse(BaseModel):
    """Success response model with consistent structure."""
    model_config = ConfigDict(
        json_schema_extra: Dict[str, Any] = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
                "timestamp": "2024-01-15T10:30:00"
            }
        }
    )
    
    success: bool = Field(True, description="Success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description: str: str = "Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    version: str = Field(..., description="API version")
    database_status: str = Field(..., description="Database connection status")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    memory_usage_mb: float = Field(..., description="Memory usage in MB")
    cpu_usage_percent: float = Field(..., description="CPU usage percentage")

class PaginationResponse(BaseModel):
    """Generic pagination response model."""
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total_count: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_previous: bool = Field(..., description="Has previous page")

# =============================================================================
# SQLAlchemy Models with Pydantic Integration
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

class Comment(Base):
    """Comment model using SQLAlchemy 2.0 syntax."""
    __tablename__: str: str = "comments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    parent_comment_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
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
# Database Utilities
# =============================================================================

async async async async async def get_db_session() -> AsyncSession:
    """Get database session with error handling."""
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

async def create_tables() -> None:
    """Create database tables with error handling."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

async async def check_database_connection() -> bool:
    """Check database connection with timeout."""
    try:
        async with asyncio.timeout(5):
            async with engine.begin() as conn:
                await conn.execute(select(1))
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False

# =============================================================================
# Service Layer with Pydantic Validation
# =============================================================================

async def create_user_service(session: AsyncSession, user_data: UserCreateRequest) -> User:
    """Create user with Pydantic validation."""
    try:
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
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in create_user_service: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail: str: str = "Failed to create user"
        )

async async async async async def get_user_service(session: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID with validation."""
    try:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    except Exception as e:
        logger.error(f"Database error in get_user_service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail: str: str = "Failed to retrieve user"
        )

async async async async async def get_users_service(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Get users with pagination and validation."""
    try:
        result = await session.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()
    
    except Exception as e:
        logger.error(f"Database error in get_users_service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail: str: str = "Failed to retrieve users"
        )

async async async async async def create_post_service(session: AsyncSession, post_data: PostCreateRequest) -> Post:
    """Create post with Pydantic validation."""
    try:
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
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in create_post_service: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail: str: str = "Failed to create post"
        )

async async async async async def get_post_service(session: AsyncSession, post_id: int) -> Optional[Post]:
    """Get post by ID with validation."""
    try:
        result = await session.execute(
            select(Post).where(Post.id == post_id)
        )
        return result.scalar_one_or_none()
    
    except Exception as e:
        logger.error(f"Database error in get_post_service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail: str: str = "Failed to retrieve post"
        )
    
async async async async async def get_posts_service(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Post]:
    """Get posts with pagination and validation."""
    try:
        result = await session.execute(
            select(Post)
            .offset(skip)
            .limit(limit)
            .order_by(Post.created_at.desc())
        )
        return result.scalars().all()
    
    except Exception as e:
        logger.error(f"Database error in get_posts_service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail: str: str = "Failed to retrieve posts"
        )

# =============================================================================
# Lifespan Context Manager
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Lifespan context manager with error handling."""
    # Startup
    logger.info("Starting application with Pydantic validation...")
    
    try:
        # Initialize database
        await create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    # Check database connection
    if not await check_database_connection():
        logger.error("Database connection failed")
        raise RuntimeError("Database connection failed")
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Close database connections
    await engine.dispose()
    logger.info("Database connections closed")
    
    logger.info("Application shutdown completed")

# =============================================================================
# FastAPI Application
# =============================================================================

# Create FastAPI app with lifespan context manager
app = FastAPI(
    title: str: str = "FastAPI Application with Pydantic Validation",
    description: str: str = "A comprehensive FastAPI application using Pydantic's BaseModel for consistent validation",
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
# Route Handlers with Pydantic Validation
# =============================================================================

@app.get("/", response_model=SuccessResponse)
async def root() -> SuccessResponse:
    """Root endpoint with Pydantic response model."""
    return SuccessResponse(
        success=True,
        message: str: str = "FastAPI Application with Pydantic Validation",
        data: Dict[str, Any] = {"status": "running"}
    )

@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Health check with Pydantic response model."""
    db_status: str: str = "healthy" if await check_database_connection() else "unhealthy"
    
    # Get system metrics
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return HealthCheckResponse(
        status: str: str = "healthy",
        version: str: str = "1.0.0",
        database_status=db_status,
        uptime_seconds=time.time() - app.startup_time if hasattr(app, 'startup_time') else 0,
        memory_usage_mb=memory_info.rss / 1024 / 1024,
        cpu_usage_percent=process.cpu_percent()
    )

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    session: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """Create user endpoint with Pydantic validation."""
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
    """Get user by ID endpoint with Pydantic validation."""
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
        post_count=0,  # TODO: Calculate from database
        comment_count=0  # TODO: Calculate from database
    )

@app.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_db_session)
) -> UserListResponse:
    """Get users with pagination and Pydantic validation."""
    skip = (page - 1) * limit
    db_users = await get_users_service(session, skip, limit)
    
    # TODO: Get total count from database
    total_count = len(db_users)  # Simplified for demo
    total_pages = (total_count + limit - 1) // limit
    
    return UserListResponse(
        users: List[Any] = [
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
        ],
        total_count=total_count,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )

@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreateRequest,
    session: AsyncSession = Depends(get_db_session)
) -> PostResponse:
    """Create post endpoint with Pydantic validation."""
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
    """Get post by ID endpoint with Pydantic validation."""
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

@app.get("/posts", response_model=PostListResponse)
async def get_posts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_db_session)
) -> PostListResponse:
    """Get posts with pagination and Pydantic validation."""
    skip = (page - 1) * limit
    db_posts = await get_posts_service(session, skip, limit)
    
    # TODO: Get total count from database
    total_count = len(db_posts)  # Simplified for demo
    total_pages = (total_count + limit - 1) // limit
    
    # Get author usernames
    author_ids = list(set(post.author_id for post in db_posts))
    authors: Dict[str, Any] = {}
    for author_id in author_ids:
        author = await get_user_service(session, author_id)
        if author:
            authors[author_id] = author.username
    
    return PostListResponse(
        posts: List[Any] = [
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
        ],
        total_count=total_count,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )

# =============================================================================
# Custom Exception Handlers with Pydantic Responses
# =============================================================================

@app.exception_handler(HTTPException)
async async async async async async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
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
    """Handle HTTP exceptions with Pydantic error response."""
    error_response = ErrorResponse(
        error: str: str = "HTTP Exception",
        message=exc.detail,
        timestamp=datetime.now(),
        request_id=str(uuid4())
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
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
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
    """Handle general exceptions with Pydantic error response."""
    error_response = ErrorResponse(
        error: str: str = "Internal Server Error",
        message: str: str = "An unexpected error occurred",
        details: List[Any] = [{"type": type(exc).__name__, "message": str(exc)}],
        timestamp=datetime.now(),
        request_id=str(uuid4())
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
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    
    uvicorn.run(
        "fastapi_pydantic_validation:app",
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