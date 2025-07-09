#!/usr/bin/env python3
"""
Dependencies Management - AI Video System

Comprehensive dependencies management system for the AI Video system with:
- FastAPI integration with modern best practices
- Pydantic v2 models for validation and serialization
- SQLAlchemy 2.0 async ORM
- Async database libraries (asyncpg, aiomysql)
- Functional components and declarative routes
- Lifespan context managers for startup/shutdown
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any, Optional, List, Union
from functools import lru_cache

# FastAPI imports
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.requests import Request

# Pydantic v2 imports
from pydantic import BaseModel, Field, ConfigDict, ValidationError
from pydantic.json import pydantic_encoder

# SQLAlchemy 2.0 imports
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Text, Boolean
from sqlalchemy.sql import text

# Async database drivers
import asyncpg
import aiomysql

# Configuration and utilities
from .core.error_handler import ErrorContext, error_handler
from .core.exceptions import AIVideoError, ValidationError as AIVideoValidationError
from .optimization.performance_optimizer import PerformanceOptimizer, OptimizationConfig

# Setup logging
logger = logging.getLogger(__name__)


# Pydantic v2 Models
class VideoRequest(BaseModel):
    """Video generation request model."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    prompt: str = Field(..., min_length=1, max_length=1000, description="Video generation prompt")
    num_steps: int = Field(default=20, ge=1, le=100, description="Number of inference steps")
    quality: str = Field(default="medium", pattern="^(low|medium|high)$", description="Video quality")
    width: int = Field(default=512, ge=256, le=1024, description="Video width")
    height: int = Field(default=512, ge=256, le=1024, description="Video height")
    seed: Optional[int] = Field(default=None, ge=0, le=2**32-1, description="Random seed")
    
    def model_post_init(self, __context: Any) -> None:
        """Post-initialization validation."""
        if self.width % 8 != 0 or self.height % 8 != 0:
            raise ValueError("Width and height must be divisible by 8")


class VideoResponse(BaseModel):
    """Video generation response model."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    video_id: str = Field(..., description="Unique video identifier")
    status: str = Field(..., pattern="^(pending|processing|completed|failed)$", description="Processing status")
    video_url: Optional[str] = Field(default=None, description="Video download URL")
    thumbnail_url: Optional[str] = Field(default=None, description="Thumbnail URL")
    processing_time: Optional[float] = Field(default=None, ge=0, description="Processing time in seconds")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SystemStatus(BaseModel):
    """System status response model."""
    
    status: str = Field(..., description="System status")
    version: str = Field(..., description="System version")
    uptime: float = Field(..., ge=0, description="System uptime in seconds")
    active_requests: int = Field(..., ge=0, description="Number of active requests")
    gpu_utilization: Optional[float] = Field(default=None, ge=0, le=100, description="GPU utilization percentage")
    memory_usage: Optional[float] = Field(default=None, ge=0, le=100, description="Memory usage percentage")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: float = Field(..., description="Error timestamp")


# SQLAlchemy 2.0 Base and Models
class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base."""
    pass


class VideoRecord(Base):
    """Video record model."""
    
    __tablename__ = "videos"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    processing_time: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    video_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string


# Database Configuration
class DatabaseConfig(BaseModel):
    """Database configuration model."""
    
    url: str = Field(..., description="Database connection URL")
    pool_size: int = Field(default=10, ge=1, le=50, description="Connection pool size")
    max_overflow: int = Field(default=20, ge=0, le=100, description="Maximum overflow connections")
    echo: bool = Field(default=False, description="Enable SQL logging")
    pool_pre_ping: bool = Field(default=True, description="Enable connection health checks")


# Application State
class AppState:
    """Application state management."""
    
    def __init__(self):
        self.db_session_maker: Optional[async_sessionmaker[AsyncSession]] = None
        self.performance_optimizer: Optional[PerformanceOptimizer] = None
        self.active_requests: int = 0
        self.startup_time: Optional[float] = None
    
    def increment_requests(self) -> None:
        """Increment active request counter."""
        self.active_requests += 1
    
    def decrement_requests(self) -> None:
        """Decrement active request counter."""
        if self.active_requests > 0:
            self.active_requests -= 1
    
    def get_uptime(self) -> float:
        """Get system uptime."""
        if self.startup_time is None:
            return 0.0
        return asyncio.get_event_loop().time() - self.startup_time


# Global application state
app_state = AppState()


# Database Dependencies
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    if app_state.db_session_maker is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialized"
        )
    
    async with app_state.db_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()


# Performance Optimizer Dependencies
async def get_performance_optimizer() -> PerformanceOptimizer:
    """Get performance optimizer dependency."""
    if app_state.performance_optimizer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Performance optimizer not initialized"
        )
    return app_state.performance_optimizer


# Error Handling Dependencies
def get_error_context(request: Request) -> ErrorContext:
    """Get error context from request."""
    return ErrorContext(
        operation=request.url.path,
        user_id=request.headers.get("X-User-ID"),
        request_id=request.headers.get("X-Request-ID")
    )


# Functional Components (Plain Functions)
def validate_video_request(request: VideoRequest) -> VideoRequest:
    """Validate video request with business logic."""
    # Early return for invalid quality/step combinations
    if request.quality == "high" and request.num_steps < 50:
        raise ValueError("High quality requires at least 50 steps")
    
    if request.quality == "low" and request.num_steps > 30:
        raise ValueError("Low quality should use 30 steps or fewer")
    
    # Validate aspect ratio
    aspect_ratio = request.width / request.height
    if aspect_ratio < 0.5 or aspect_ratio > 2.0:
        raise ValueError("Aspect ratio must be between 0.5 and 2.0")
    
    return request


def generate_video_id() -> str:
    """Generate unique video ID."""
    import uuid
    return str(uuid.uuid4())


def format_processing_time(seconds: float) -> str:
    """Format processing time for display."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


# Database Operations
async def create_video_record(
    session: AsyncSession,
    video_id: str,
    prompt: str,
    metadata: Dict[str, Any]
) -> VideoRecord:
    """Create video record in database."""
    from datetime import datetime
    
    video_record = VideoRecord(
        id=video_id,
        prompt=prompt,
        status="pending",
        created_at=datetime.utcnow(),
        metadata=str(metadata)
    )
    
    session.add(video_record)
    await session.commit()
    await session.refresh(video_record)
    
    return video_record


async def update_video_status(
    session: AsyncSession,
    video_id: str,
    status: str,
    video_path: Optional[str] = None,
    thumbnail_path: Optional[str] = None,
    error_message: Optional[str] = None,
    processing_time: Optional[float] = None
) -> VideoRecord:
    """Update video status in database."""
    from datetime import datetime
    
    result = await session.execute(
        text("""
            UPDATE videos 
            SET status = :status, 
                completed_at = :completed_at,
                video_path = :video_path,
                thumbnail_path = :thumbnail_path,
                error_message = :error_message,
                processing_time = :processing_time
            WHERE id = :video_id
        """),
        {
            "status": status,
            "completed_at": datetime.utcnow() if status in ["completed", "failed"] else None,
            "video_path": video_path,
            "thumbnail_path": thumbnail_path,
            "error_message": error_message,
            "processing_time": processing_time,
            "video_id": video_id
        }
    )
    
    await session.commit()
    
    # Fetch updated record
    result = await session.execute(
        text("SELECT * FROM videos WHERE id = :video_id"),
        {"video_id": video_id}
    )
    return result.fetchone()


async def get_video_record(session: AsyncSession, video_id: str) -> Optional[VideoRecord]:
    """Get video record by ID."""
    result = await session.execute(
        text("SELECT * FROM videos WHERE id = :video_id"),
        {"video_id": video_id}
    )
    return result.fetchone()


# Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting AI Video System...")
    app_state.startup_time = asyncio.get_event_loop().time()
    
    try:
        # Initialize database
        await initialize_database()
        
        # Initialize performance optimizer
        await initialize_performance_optimizer()
        
        logger.info("AI Video System started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down AI Video System...")
        await cleanup_resources()
        logger.info("AI Video System shutdown completed")


# Database Initialization
async def initialize_database() -> None:
    """Initialize database connection."""
    try:
        # Parse database URL
        db_url = "postgresql+asyncpg://user:password@localhost/ai_video_db"
        
        # Create async engine
        engine = create_async_engine(
            db_url,
            pool_size=10,
            max_overflow=20,
            echo=False,
            pool_pre_ping=True
        )
        
        # Create session maker
        app_state.db_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Test connection
        async with app_state.db_session_maker() as session:
            await session.execute(text("SELECT 1"))
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


# Performance Optimizer Initialization
async def initialize_performance_optimizer() -> None:
    """Initialize performance optimizer."""
    try:
        config = OptimizationConfig(
            use_gpu=True,
            mixed_precision=True,
            cache_enabled=True,
            enable_profiling=True,
            max_concurrent_tasks=4
        )
        
        app_state.performance_optimizer = await PerformanceOptimizer(config)
        await app_state.performance_optimizer.initialize()
        
        logger.info("Performance optimizer initialized successfully")
        
    except Exception as e:
        logger.error(f"Performance optimizer initialization failed: {e}")
        raise


# Resource Cleanup
async def cleanup_resources() -> None:
    """Cleanup application resources."""
    try:
        # Cleanup performance optimizer
        if app_state.performance_optimizer:
            await app_state.performance_optimizer.cleanup()
        
        # Close database connections
        if app_state.db_session_maker:
            await app_state.db_session_maker.close_all()
        
        logger.info("Resources cleaned up successfully")
        
    except Exception as e:
        logger.error(f"Resource cleanup failed: {e}")


# FastAPI Application Factory
def create_app() -> FastAPI:
    """Create FastAPI application with dependencies."""
    
    app = FastAPI(
        title="AI Video System API",
        description="Advanced AI video generation system with performance optimization",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]
    )
    
    # Add exception handlers
    app.add_exception_handler(AIVideoError, handle_ai_video_error)
    app.add_exception_handler(ValidationError, handle_validation_error)
    app.add_exception_handler(Exception, handle_generic_error)
    
    # Include routers
    from .api.routes import video_router, system_router
    app.include_router(video_router, prefix="/api/v1/videos", tags=["videos"])
    app.include_router(system_router, prefix="/api/v1/system", tags=["system"])
    
    return app


# Exception Handlers
def handle_ai_video_error(request: Request, exc: AIVideoError) -> JSONResponse:
    """Handle AI Video system errors."""
    error_response = ErrorResponse(
        error=exc.message,
        error_code=exc.error_code or "AI_VIDEO_ERROR",
        details=exc.details,
        timestamp=asyncio.get_event_loop().time()
    )
    
    logger.error(f"AI Video Error: {exc.message}", extra={"error_code": exc.error_code})
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.model_dump()
    )


def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    error_response = ErrorResponse(
        error="Validation error",
        error_code="VALIDATION_ERROR",
        details={"errors": exc.errors()},
        timestamp=asyncio.get_event_loop().time()
    )
    
    logger.error(f"Validation Error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )


def handle_generic_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic errors."""
    error_response = ErrorResponse(
        error="Internal server error",
        error_code="INTERNAL_ERROR",
        details={"type": type(exc).__name__},
        timestamp=asyncio.get_event_loop().time()
    )
    
    logger.error(f"Generic Error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


# Health Check
def health_check() -> Dict[str, Any]:
    """Health check function."""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "version": "1.0.0"
    }


# Export main components
__all__ = [
    "VideoRequest",
    "VideoResponse", 
    "SystemStatus",
    "ErrorResponse",
    "DatabaseConfig",
    "AppState",
    "app_state",
    "get_db_session",
    "get_performance_optimizer",
    "get_error_context",
    "validate_video_request",
    "generate_video_id",
    "format_processing_time",
    "create_video_record",
    "update_video_status",
    "get_video_record",
    "create_app",
    "health_check"
] 