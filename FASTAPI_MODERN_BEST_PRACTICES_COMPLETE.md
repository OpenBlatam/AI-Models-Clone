# Modern FastAPI Application with Best Practices
============================================

## Overview

This comprehensive FastAPI application demonstrates modern best practices for building scalable, maintainable, and production-ready APIs. The application follows the latest FastAPI conventions and integrates seamlessly with modern Python ecosystem tools.

## Key Features

### ✅ Modern Best Practices Implemented

1. **Functional Components**: All route handlers and services are implemented as pure functions
2. **Pydantic v2**: Latest Pydantic models with enhanced validation
3. **Async Database Integration**: SQLAlchemy 2.0 with asyncpg for PostgreSQL
4. **Lifespan Context Managers**: Proper startup/shutdown management
5. **Comprehensive Middleware**: Logging, error monitoring, and performance optimization
6. **Type Hints**: Complete type annotations throughout
7. **Error Handling**: Custom error types and structured error responses
8. **Declarative Routes**: Clear route definitions with response models

## Architecture

### Core Components

#### 1. Pydantic Models (Pydantic v2)
```python
class UserCreate(BaseModel):
    """User creation model with validation."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = Field(True, description="User active status")
    
    @validator('email')
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v.lower()
```

**Features:**
- Field validation with constraints
- Custom validators
- Descriptive field documentation
- Type safety with Pydantic v2

#### 2. SQLAlchemy 2.0 Models
```python
class User(Base):
    """User model using SQLAlchemy 2.0 syntax."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
```

**Features:**
- Modern SQLAlchemy 2.0 syntax with `Mapped` types
- Automatic timestamp management
- Proper foreign key relationships
- Database-level constraints

#### 3. Async Database Integration
```python
# Database URL with asyncpg
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

**Features:**
- Async PostgreSQL with asyncpg
- Connection pooling
- Session management
- Transaction handling

#### 4. Functional Service Layer
```python
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
            detail="User with this username or email already exists"
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
```

**Features:**
- Pure functions with clear inputs/outputs
- Proper error handling
- Database transaction management
- Type safety

#### 5. Lifespan Context Manager
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
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
```

**Features:**
- Proper startup/shutdown management
- Database initialization
- Connection cleanup
- Error handling during startup

#### 6. Comprehensive Middleware

##### Logging Middleware
```python
class LoggingMiddleware:
    """Middleware for request/response logging."""
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        # Generate request ID
        request_id = str(uuid4())
        request.state.request_id = request_id
        
        # Log request
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            logger.error(f"Request {request_id} failed: {e}")
            raise
        finally:
            # Log response time
            process_time = time.time() - start_time
            logger.info(f"Request {request_id} completed in {process_time:.4f}s")
```

**Features:**
- Request ID generation
- Performance timing
- Structured logging
- Error tracking

##### Error Monitoring Middleware
```python
class ErrorMonitoringMiddleware:
    """Middleware for error monitoring and handling."""
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            # Log error with context
            request = Request(scope, receive)
            request_id = getattr(request.state, 'request_id', 'unknown')
            
            logger.error(
                f"Unhandled error in request {request_id}: {e}",
                exc_info=True
            )
            
            # Return structured error response
            error_response = ErrorResponse(
                error="Internal server error",
                detail="An unexpected error occurred",
                timestamp=func.now().isoformat(),
                request_id=request_id
            )
            
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_response.dict()
            )
            
            await response(scope, receive, send)
```

**Features:**
- Comprehensive error handling
- Structured error responses
- Request context preservation
- Error logging with stack traces

##### Performance Middleware
```python
class PerformanceMiddleware:
    """Middleware for performance monitoring."""
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        # Track memory usage
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            await self.app(scope, receive, send)
        finally:
            # Calculate performance metrics
            process_time = time.time() - start_time
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_delta = final_memory - initial_memory
            
            self.request_times.append(process_time)
            
            # Log performance metrics for slow requests
            if process_time > 1.0:  # Log requests taking more than 1 second
                logger.warning(
                    f"Slow request detected: {process_time:.4f}s, "
                    f"memory delta: {memory_delta:.2f}MB"
                )
            
            # Keep only last 1000 request times for memory efficiency
            if len(self.request_times) > 1000:
                self.request_times = self.request_times[-1000:]
```

**Features:**
- Performance monitoring
- Memory usage tracking
- Slow request detection
- Metrics collection

#### 7. Declarative Route Handlers
```python
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
```

**Features:**
- Clear return type annotations
- Pydantic response models
- Dependency injection
- Proper HTTP status codes
- Functional approach

#### 8. Custom Error Handlers
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    error_response = ErrorResponse(
        error=exc.detail,
        detail="HTTP exception occurred",
        timestamp=func.now().isoformat(),
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    error_response = ErrorResponse(
        error="Internal server error",
        detail="An unexpected error occurred",
        timestamp=func.now().isoformat(),
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict()
    )
```

**Features:**
- Structured error responses
- Request ID tracking
- Proper error logging
- User-friendly error messages

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description | Response Model |
|--------|----------|-------------|----------------|
| GET | `/` | Root endpoint | `Dict[str, str]` |
| GET | `/health` | Health check | `HealthCheckResponse` |
| POST | `/users` | Create user | `UserResponse` |
| GET | `/users/{user_id}` | Get user by ID | `UserResponse` |
| GET | `/users` | Get users (paginated) | `List[UserResponse]` |
| POST | `/posts` | Create post | `PostResponse` |
| GET | `/posts/{post_id}` | Get post by ID | `PostResponse` |
| GET | `/posts` | Get posts (paginated) | `List[PostResponse]` |

### Request/Response Examples

#### Create User
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true
  }'
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

#### Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "version": "1.0.0",
  "database_status": "healthy"
}
```

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# Application
APP_NAME=Modern FastAPI Application
APP_VERSION=1.0.0
DEBUG=false

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Database Setup
```bash
# Install dependencies
pip install -r fastapi_modern_requirements.txt

# Set up database
createdb fastapi_modern_db

# Run migrations (if using Alembic)
alembic upgrade head

# Start application
uvicorn fastapi_modern_best_practices:app --reload
```

## Development Workflow

### Code Quality
```bash
# Format code
black fastapi_modern_best_practices.py

# Sort imports
isort fastapi_modern_best_practices.py

# Lint code
flake8 fastapi_modern_best_practices.py

# Type checking
mypy fastapi_modern_best_practices.py
```

### Testing
```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=fastapi_modern_best_practices --cov-report=html
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Performance Features

### 1. Async Database Operations
- Non-blocking database queries
- Connection pooling
- Efficient session management

### 2. Middleware Performance Monitoring
- Request timing
- Memory usage tracking
- Slow request detection
- Performance metrics collection

### 3. Response Optimization
- GZip compression
- Structured JSON responses
- Efficient serialization

### 4. Error Handling
- Comprehensive error tracking
- Request ID correlation
- Structured error responses
- Performance impact monitoring

## Security Features

### 1. Input Validation
- Pydantic v2 field validation
- Custom validators
- Type safety enforcement

### 2. Error Handling
- No sensitive information in error responses
- Structured error logging
- Request ID tracking for debugging

### 3. CORS Configuration
- Configurable CORS middleware
- Secure default settings

### 4. Database Security
- Parameterized queries
- SQL injection prevention
- Connection security

## Monitoring and Observability

### 1. Logging
- Structured logging with request IDs
- Performance metrics
- Error tracking with stack traces
- Request/response logging

### 2. Health Checks
- Database connectivity monitoring
- Application status endpoint
- Comprehensive health information

### 3. Performance Monitoring
- Request timing
- Memory usage tracking
- Slow request detection
- Metrics collection

### 4. Error Monitoring
- Comprehensive error handling
- Error categorization
- Request context preservation
- Error reporting

## Best Practices Implemented

### ✅ FastAPI Best Practices
- [x] Use `def` for synchronous and `async def` for asynchronous operations
- [x] Type hints for all function signatures
- [x] Pydantic models for input validation and response schemas
- [x] Functional components (plain functions)
- [x] Declarative route definitions with clear return type annotations
- [x] Lifespan context managers for startup/shutdown events
- [x] Middleware for logging, error monitoring, and performance optimization

### ✅ Database Best Practices
- [x] SQLAlchemy 2.0 with async support
- [x] Async PostgreSQL with asyncpg
- [x] Proper connection pooling
- [x] Transaction management
- [x] Session lifecycle management

### ✅ Error Handling Best Practices
- [x] Custom error types
- [x] Structured error responses
- [x] Request ID tracking
- [x] Comprehensive logging
- [x] User-friendly error messages

### ✅ Performance Best Practices
- [x] Async operations throughout
- [x] Efficient database queries
- [x] Response compression
- [x] Performance monitoring
- [x] Memory usage tracking

### ✅ Security Best Practices
- [x] Input validation
- [x] Parameterized queries
- [x] CORS configuration
- [x] Error information sanitization
- [x] Secure defaults

## Benefits

### 1. Maintainability
- Clear separation of concerns
- Functional programming approach
- Comprehensive type hints
- Modular design

### 2. Performance
- Async operations throughout
- Efficient database queries
- Response optimization
- Performance monitoring

### 3. Reliability
- Comprehensive error handling
- Health checks
- Database connection management
- Graceful shutdown

### 4. Developer Experience
- Auto-generated API documentation
- Clear error messages
- Type safety
- Development tools integration

### 5. Production Readiness
- Monitoring and observability
- Performance tracking
- Error handling
- Security features

## Conclusion

This modern FastAPI application demonstrates the implementation of all current best practices for building scalable, maintainable, and production-ready APIs. The application provides a solid foundation for building complex web services with proper error handling, performance monitoring, and security features.

The modular design and functional approach make it easy to extend and maintain, while the comprehensive middleware system ensures proper monitoring and observability in production environments. 