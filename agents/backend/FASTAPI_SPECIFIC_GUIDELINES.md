# FastAPI-Specific Guidelines
## Blatam Academy Backend

### 📊 Current FastAPI Usage Analysis

#### **FastAPI Implementation Overview**
- **Total FastAPI Applications**: 50+ across different modules
- **Application Factory Pattern**: Implemented in `core/app_factory.py`
- **Microservices Architecture**: Multiple specialized services
- **Production-Ready Features**: Rate limiting, monitoring, health checks

#### **Current Implementation Patterns**

##### **✅ Good Practices Found**
- Centralized app factory with configuration management
- Comprehensive middleware setup (CORS, compression, security headers)
- Rate limiting with slowapi integration
- Prometheus metrics with fastapi-instrumentator
- Structured logging with structlog
- Health check endpoints
- Error handling with custom exception handlers

##### **⚠️ Areas for Improvement**
- Inconsistent response models across services
- Mixed async/sync patterns in some endpoints
- Limited use of dependency injection
- Missing request/response validation in some endpoints
- Inconsistent error handling patterns

### 🚀 FastAPI Best Practices

#### **1. Application Structure**

##### **✅ Recommended Structure**
```
app/
├── main.py                 # Application entry point
├── core/
│   ├── config.py          # Configuration management
│   ├── dependencies.py    # Dependency injection
│   ├── exceptions.py      # Custom exceptions
│   └── middleware.py      # Custom middleware
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   ├── dependencies.py
│   │   └── router.py
│   └── deps.py
├── models/
│   ├── request.py
│   └── response.py
├── services/
│   └── business_logic.py
└── utils/
    └── helpers.py
```

##### **✅ Application Factory Pattern**
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await startup_event()
    yield
    # Shutdown
    await shutdown_event()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Blatam Academy API",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Setup routes
    setup_routes(app)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    return app
```

#### **2. Request/Response Models**

##### **✅ Pydantic v2 Models**
```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class BaseResponse(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        from_attributes=True,
        extra="forbid"
    )

class UserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    age: Optional[int] = Field(None, ge=0, le=150)

class UserResponse(BaseResponse):
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

class PaginatedResponse(BaseResponse, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
```

#### **3. Dependency Injection**

##### **✅ Service Dependencies**
```python
from fastapi import Depends
from typing import Annotated

# Database dependency
async def get_db() -> AsyncSession:
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

# Service dependency
async def get_user_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserService:
    return UserService(db)

# Authentication dependency
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    user = await user_service.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
```

#### **4. Error Handling**

##### **✅ Custom Exception Handlers**
```python
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "type": "validation_error",
                "message": "Validation failed",
                "details": exc.errors()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, 
    exc: HTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": "http_error",
                "message": exc.detail,
                "status_code": exc.status_code
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

#### **5. Middleware Configuration**

##### **✅ Comprehensive Middleware Setup**
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

def setup_middleware(app: FastAPI):
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Compression middleware
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000
    )
    
    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            "Incoming request",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host
        )
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=process_time
        )
        
        return response
```

#### **6. Rate Limiting**

##### **✅ Advanced Rate Limiting**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Custom rate limit key function
def get_user_rate_limit_key(request: Request) -> str:
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    return get_remote_address(request)

# Apply rate limiting
@app.get("/api/data")
@limiter.limit("100/minute")
async def get_data(
    request: Request,
    user: Annotated[User, Depends(get_current_user)]
):
    return {"data": "protected_data"}

# Different limits for different user types
@app.post("/api/upload")
@limiter.limit("10/minute", key_func=get_user_rate_limit_key)
async def upload_file(
    request: Request,
    user: Annotated[User, Depends(get_current_user)]
):
    return {"message": "File uploaded"}
```

#### **7. Background Tasks**

##### **✅ Efficient Background Processing**
```python
from fastapi import BackgroundTasks
from celery import Celery

# Celery configuration
celery_app = Celery("blatam_academy")
celery_app.config_from_object("celeryconfig")

@app.post("/api/process")
async def process_data(
    background_tasks: BackgroundTasks,
    data: ProcessRequest,
    user: Annotated[User, Depends(get_current_user)]
):
    # Immediate response
    task_id = str(uuid.uuid4())
    
    # Add to background tasks
    background_tasks.add_task(
        process_data_task,
        task_id=task_id,
        data=data.dict(),
        user_id=user.id
    )
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Task queued for processing"
    }

@celery_app.task
def process_data_task(task_id: str, data: dict, user_id: str):
    # Long-running task
    result = process_data_logic(data)
    
    # Update task status
    update_task_status(task_id, "completed", result)
```

#### **8. Caching Strategies**

##### **✅ Multi-Level Caching**
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# Setup cache
@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# Cache with TTL
@app.get("/api/users/{user_id}")
@cache(expire=300)  # 5 minutes
async def get_user(user_id: str):
    return await user_service.get_user(user_id)

# Cache with custom key
@app.get("/api/users/{user_id}/profile")
@cache(expire=600, key_builder=lambda func, **kwargs: f"profile:{kwargs['user_id']}")
async def get_user_profile(user_id: str):
    return await user_service.get_user_profile(user_id)

# Invalidate cache
@app.put("/api/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    user_service: Annotated[UserService, Depends(get_user_service)]
):
    updated_user = await user_service.update_user(user_id, user_data)
    
    # Invalidate related caches
    await FastAPICache.clear(namespace="users")
    
    return updated_user
```

#### **9. Monitoring and Metrics**

##### **✅ Comprehensive Monitoring**
```python
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge

# Custom metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"]
)

ACTIVE_USERS = Gauge(
    "active_users",
    "Number of active users"
)

# Setup monitoring
def setup_monitoring(app: FastAPI):
    # Prometheus metrics
    Instrumentator().instrument(app).expose(app)
    
    # Custom metrics middleware
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(time.time() - start_time)
        
        return response
```

#### **10. Security Best Practices**

##### **✅ Security Implementation**
```python
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# JWT token validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_token(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await get_user(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Role-based access control
def require_role(required_role: str):
    def role_checker(user: User = Depends(verify_token)):
        if required_role not in user.roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role {required_role} required"
            )
        return user
    return role_checker

@app.get("/admin/users")
async def get_users(
    user: Annotated[User, Depends(require_role("admin"))]
):
    return await user_service.get_all_users()
```

### 🔧 Performance Optimization

#### **1. Response Optimization**
```python
from fastapi.responses import ORJSONResponse
from fastapi import Response

# Use ORJSON for faster JSON serialization
app = FastAPI(default_response_class=ORJSONResponse)

# Streaming responses for large data
@app.get("/api/large-dataset")
async def get_large_dataset():
    async def generate():
        for i in range(10000):
            yield f"data:{i}\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

# File responses
@app.get("/api/download/{file_id}")
async def download_file(file_id: str):
    file_path = f"files/{file_id}"
    return FileResponse(
        file_path,
        filename=f"file_{file_id}.txt",
        media_type="application/octet-stream"
    )
```

#### **2. Database Optimization**
```python
# Connection pooling
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Optimized queries with eager loading
@app.get("/api/users/{user_id}")
async def get_user_with_posts(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    stmt = (
        select(User)
        .options(selectinload(User.posts))
        .where(User.id == user_id)
    )
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
```

#### **3. Async/Await Best Practices**
```python
# Proper async handling
@app.get("/api/data")
async def get_data():
    # Run multiple async operations concurrently
    user_data, post_data, comment_data = await asyncio.gather(
        get_user_data(),
        get_post_data(),
        get_comment_data()
    )
    
    return {
        "users": user_data,
        "posts": post_data,
        "comments": comment_data
    }

# Background task with proper error handling
@app.post("/api/process")
async def process_data(
    background_tasks: BackgroundTasks,
    data: ProcessRequest
):
    try:
        # Validate data
        validated_data = await validate_data(data)
        
        # Add to background tasks
        background_tasks.add_task(
            process_data_safely,
            validated_data
        )
        
        return {"status": "processing", "message": "Task queued"}
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

### 📊 Testing Guidelines

#### **1. Unit Testing**
```python
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Test client setup
@pytest.fixture
def client():
    app = create_test_app()
    return TestClient(app)

@pytest.fixture
async def async_client():
    app = create_test_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Test endpoint
def test_get_user(client):
    response = client.get("/api/users/123")
    assert response.status_code == 200
    assert "id" in response.json()

# Async test
@pytest.mark.asyncio
async def test_create_user(async_client):
    user_data = {"name": "Test User", "email": "test@example.com"}
    response = await async_client.post("/api/users", json=user_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test User"
```

#### **2. Integration Testing**
```python
# Database integration test
@pytest.mark.asyncio
async def test_user_crud_operations(async_client, test_db):
    # Create user
    user_data = {"name": "Test User", "email": "test@example.com"}
    create_response = await async_client.post("/api/users", json=user_data)
    assert create_response.status_code == 201
    
    user_id = create_response.json()["id"]
    
    # Get user
    get_response = await async_client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test User"
    
    # Update user
    update_data = {"name": "Updated User"}
    update_response = await async_client.put(f"/api/users/{user_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated User"
    
    # Delete user
    delete_response = await async_client.delete(f"/api/users/{user_id}")
    assert delete_response.status_code == 204
```

### 🚀 Deployment Guidelines

#### **1. Production Configuration**
```python
# Production settings
class ProductionConfig(BaseSettings):
    # Security
    SECRET_KEY: str
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    
    class Config:
        env_file = ".env.production"

# Production app factory
def create_production_app() -> FastAPI:
    config = ProductionConfig()
    
    app = FastAPI(
        title="Blatam Academy API",
        version="1.0.0",
        docs_url=None,  # Disable docs in production
        redoc_url=None
    )
    
    # Security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=config.ALLOWED_HOSTS
    )
    
    # Setup monitoring
    if config.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        
        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            integrations=[FastApiIntegration()]
        )
    
    return app
```

#### **2. Docker Configuration**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 📈 Performance Monitoring

#### **1. Key Metrics**
- Request latency (p50, p95, p99)
- Request rate (requests per second)
- Error rate (4xx, 5xx responses)
- Database query performance
- Memory usage
- CPU utilization

#### **2. Alerting Rules**
```yaml
# Prometheus alerting rules
groups:
  - name: fastapi_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
```

### 🎯 Implementation Checklist

#### **Immediate Actions**
- [ ] Standardize response models across all endpoints
- [ ] Implement consistent error handling
- [ ] Add request/response validation
- [ ] Setup comprehensive logging
- [ ] Implement rate limiting

#### **Short-term Goals**
- [ ] Optimize database queries
- [ ] Implement caching strategies
- [ ] Add comprehensive monitoring
- [ ] Setup automated testing
- [ ] Implement security best practices

#### **Long-term Goals**
- [ ] Performance optimization
- [ ] Advanced caching strategies
- [ ] Microservices architecture
- [ ] Advanced monitoring and alerting
- [ ] Automated deployment pipeline

### 📚 Resources

#### **Documentation**
- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/best-practices/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)

#### **Tools and Libraries**
- `fastapi-cache2`: Caching support
- `slowapi`: Rate limiting
- `prometheus-fastapi-instrumentator`: Metrics
- `structlog`: Structured logging
- `orjson`: Fast JSON serialization

This comprehensive guide provides the foundation for building high-performance, scalable, and maintainable FastAPI applications in your Blatam Academy backend. 