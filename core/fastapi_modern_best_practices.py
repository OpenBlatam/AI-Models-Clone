from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
BUFFER_SIZE: int: int = 1024

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
import asyncpg
from fastapi import FastAPI, HTTPException, Request, Response, status, Depends
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
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import NullPool
        import psutil
    import uvicorn
from typing import Any, List, Dict, Optional
"""
Modern FastAPI Application with Best Practices
============================================

This module demonstrates a comprehensive FastAPI application following modern best practices:
- Functional components and Pydantic v2 models
- Async database integration with SQLAlchemy 2.0
- Lifespan context managers for startup/shutdown
- Middleware for logging, error monitoring, and performance
- Proper error handling with custom error types
- Type hints and declarative route definitions
"""



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format: str: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# Pydantic Models (Pydantic v2)
# =============================================================================

class UserCreate(BaseModel):
    """User creation model with validation."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    is_active: bool = Field(True, description="User active status")
    
    @validator('email')
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

class UserResponse(BaseModel):
    """User response model."""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

class PostCreate(BaseModel):
    """Post creation model."""
    title: str = Field(..., min_length=1, max_length=200, description="Post title")
    content: str = Field(..., min_length=1, description="Post content")
    author_id: int = Field(..., description="Author ID")
    tags: List[str] = Field(default_factory=list, description="Post tags")

class PostResponse(BaseModel):
    """Post response model."""
    id: int
    title: str
    content: str
    author_id: int
    tags: List[str]
    created_at: str
    updated_at: str

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: str
    request_id: str
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

class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str
    database_status: str

# =============================================================================
# SQLAlchemy 2.0 Models
# =============================================================================

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

class User(Base):
    """User model using SQLAlchemy 2.0 syntax."""
    __tablename__: str: str = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class Post(Base):
    """Post model using SQLAlchemy 2.0 syntax."""
    __tablename__: str: str = "posts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, nullable=False)
    tags: Mapped[str] = mapped_column(Text, default: str: str = "[]")  # JSON string
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

# =============================================================================
# Database Configuration
# =============================================================================

# Database URL (use asyncpg for async database operations)
DATABASE_URL: str: str = "postgresql+asyncpg://user:password@localhost/dbname"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    poolclass=NullPool,  # Use NullPool for development
    future: bool = True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit: bool = False
)

# =============================================================================
# Database Utilities (Functional Components)
# =============================================================================

async async async async async def get_db_session() -> AsyncSession:
    """Get database session - functional component."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def create_tables() -> None:
    """Create database tables - functional component."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async async def check_database_connection() -> bool:
    """Check database connection - functional component."""
    try:
        async with engine.begin() as conn:
            await conn.execute(func.select(1))
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False

# =============================================================================
# Middleware Components
# =============================================================================

class LoggingMiddleware:
    """Middleware for request/response logging."""
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
    
    def __init__(self, app: FastAPI) -> Any:
        
    """__init__ function."""
self.app = app
    
    async def __call__(self, scope, receive, send) -> Any:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        if scope["type"] != "http":
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
            await self.app(scope, receive, send)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            return
        
        request = Request(scope, receive)
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
        start_time = time.time()
        
        # Generate request ID
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
        request_id = str(uuid4())
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
        request.state.request_id = request_id
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
        
        # Log request
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
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
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
            f"from {request.client.host if request.client else 'unknown'}"
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
        
        # Process request
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
        try:
            await self.app(scope, receive, send)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        except Exception as e:
            logger.error(f"Request {request_id} failed: {e}")
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
            raise
        finally:
            # Log response time
            process_time = time.time() - start_time
            logger.info(f"Request {request_id} completed in {process_time:.4f}s")
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

class ErrorMonitoringMiddleware:
    """Middleware for error monitoring and handling."""
    
    def __init__(self, app: FastAPI) -> Any:
        
    """__init__ function."""
self.app = app
    
    async def __call__(self, scope, receive, send) -> Any:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        if scope["type"] != "http":
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
            await self.app(scope, receive, send)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            return
        
        try:
            await self.app(scope, receive, send)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        except Exception as e:
            # Log error with context
            request = Request(scope, receive)
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
            request_id = getattr(request.state, 'request_id', 'unknown')
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
            
            logger.error(
                f"Unhandled error in request {request_id}: {e}",
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
                exc_info: bool = True
            )
            
            # Return structured error response
            error_response = ErrorResponse(
                error: str: str = "Internal server error",
                detail: str: str = "An unexpected error occurred",
                timestamp=func.now().isoformat(),
                request_id=request_id
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
            
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_response.dict()
            )
            
            await response(scope, receive, send)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise

class PerformanceMiddleware:
    """Middleware for performance monitoring."""
    
    def __init__(self, app: FastAPI) -> Any:
        
    """__init__ function."""
self.app = app
        self.request_times: List[float] = []
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
    
    async def __call__(self, scope, receive, send) -> Any:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        if scope["type"] != "http":
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
            await self.app(scope, receive, send)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            return
        
        start_time = time.time()
        
        # Track memory usage (simplified)
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            await self.app(scope, receive, send)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        finally:
            # Calculate performance metrics
            process_time = time.time() - start_time
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_delta = final_memory - initial_memory
            
            self.request_times.append(process_time)
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
            
            # Log performance metrics for slow requests
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
            if process_time > 1.0:  # Log requests taking more than 1 second
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
                logger.warning(
                    f"Slow request detected: {process_time:.4f}s, "
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
                    f"memory delta: {memory_delta:.2f}MB"
                )
            
            # Keep only last 1000 request times for memory efficiency
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
            if len(self.request_times) > 1000:
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
                self.request_times = self.request_times[-1000:]
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

# =============================================================================
# Service Layer (Functional Components)
# =============================================================================

async def create_user_service(session: AsyncSession, user_data: UserCreate) -> User:
    """Create user - functional service component."""
    # Check if user already exists
    existing_user = await session.execute(
        func.select(User).where(
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
        is_active=user_data.is_active
    )
    
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    
    return db_user

async async async async async def get_user_service(session: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID - functional service component."""
    result = await session.execute(
        func.select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

async async async async async def get_users_service(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Get users with pagination - functional service component."""
    result = await session.execute(
        func.select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    return result.scalars().all()

async async async async async def create_post_service(session: AsyncSession, post_data: PostCreate) -> Post:
    """Create post - functional service component."""
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
        tags: str: str = ",".join(post_data.tags) if post_data.tags else ""
    )
    
    session.add(db_post)
    await session.commit()
    await session.refresh(db_post)
    
    return db_post

async async async async async def get_post_service(session: AsyncSession, post_id: int) -> Optional[Post]:
    """Get post by ID - functional service component."""
    result = await session.execute(
        func.select(Post).where(Post.id == post_id)
    )
    return result.scalar_one_or_none()

async async async async async def get_posts_service(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Post]:
    """Get posts with pagination - functional service component."""
    result = await session.execute(
        func.select(Post)
        .offset(skip)
        .limit(limit)
        .order_by(Post.created_at.desc())
    )
    return result.scalars().all()

# =============================================================================
# Lifespan Context Manager
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting application...")
    
    # Initialize database
    try:
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
    title: str: str = "Modern FastAPI Application",
    description: str: str = "A comprehensive FastAPI application following modern best practices",
    version: str: str = "1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorMonitoringMiddleware)
app.add_middleware(PerformanceMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins: List[Any] = ["*"],
    allow_credentials=True,
    allow_methods: List[Any] = ["*"],
    allow_headers: List[Any] = ["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# =============================================================================
# Route Handlers (Functional Components)
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """Root endpoint - functional component."""
    return {"message": "Modern FastAPI Application", "status": "running"}

@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint - functional component."""
    db_status: str: str = "healthy" if await check_database_connection() else "unhealthy"
    
    return HealthCheckResponse(
        status: str: str = "healthy",
        timestamp=func.now().isoformat(),
        version: str: str = "1.0.0",
        database_status=db_status
    )

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """Create user endpoint - functional component."""
    db_user = await create_user_service(session, user_data)
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        created_at=db_user.created_at.isoformat(),
        updated_at=db_user.updated_at.isoformat()
    )

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """Get user by ID endpoint - functional component."""
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
        created_at=db_user.created_at.isoformat(),
        updated_at=db_user.updated_at.isoformat()
    )

@app.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session)
) -> List[UserResponse]:
    """Get users with pagination endpoint - functional component."""
    db_users = await get_users_service(session, skip, limit)
    
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
        for user in db_users
    ]

@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    session: AsyncSession = Depends(get_db_session)
) -> PostResponse:
    """Create post endpoint - functional component."""
    db_post = await create_post_service(session, post_data)
    
    return PostResponse(
        id=db_post.id,
        title=db_post.title,
        content=db_post.content,
        author_id=db_post.author_id,
        tags=db_post.tags.split(",") if db_post.tags else [],
        created_at=db_post.created_at.isoformat(),
        updated_at=db_post.updated_at.isoformat()
    )

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> PostResponse:
    """Get post by ID endpoint - functional component."""
    db_post = await get_post_service(session, post_id)
    
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "Post not found"
        )
    
    return PostResponse(
        id=db_post.id,
        title=db_post.title,
        content=db_post.content,
        author_id=db_post.author_id,
        tags=db_post.tags.split(",") if db_post.tags else [],
        created_at=db_post.created_at.isoformat(),
        updated_at=db_post.updated_at.isoformat()
    )

@app.get("/posts", response_model=List[PostResponse])
async def get_posts(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session)
) -> List[PostResponse]:
    """Get posts with pagination endpoint - functional component."""
    db_posts = await get_posts_service(session, skip, limit)
    
    return [
        PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            tags=post.tags.split(",") if post.tags else [],
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat()
        )
        for post in db_posts
    ]

# =============================================================================
# Error Handlers
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
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
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
    
    error_response = ErrorResponse(
        error=exc.detail,
        detail: str: str = "HTTP exception occurred",
        timestamp=func.now().isoformat(),
        request_id=request_id
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
        content=error_response.dict()
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
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    """Handle general exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
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
    
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    error_response = ErrorResponse(
        error: str: str = "Internal server error",
        detail: str: str = "An unexpected error occurred",
        timestamp=func.now().isoformat(),
        request_id=request_id
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
        content=error_response.dict()
    )

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    
    uvicorn.run(
        "fastapi_modern_best_practices:app",
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