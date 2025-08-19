# FastAPI Dependency Injection Implementation Summary

## Overview

This implementation provides **comprehensive dependency injection patterns** for FastAPI applications, demonstrating how to effectively manage state, shared resources, and application lifecycle using FastAPI's built-in dependency injection system. It covers database connections, caching, authentication, external services, and background tasks.

## Key Features

### 1. Settings Management
- **Singleton pattern** with `@lru_cache()`
- **Type-safe configuration** with Pydantic models
- **Environment-specific settings** management
- **Centralized configuration** access

### 2. Resource Management
- **Database connection pooling** with SQLAlchemy
- **Redis cache management** with connection pooling
- **HTTP client management** with connection reuse
- **Automatic resource cleanup** on application shutdown

### 3. Authentication Dependencies
- **JWT token management** with creation and validation
- **User authentication flow** with dependency chains
- **Role-based access control** implementation
- **Secure token handling** with expiration

### 4. Custom Dependencies
- **Request context dependencies** (ID, timestamp, user agent)
- **Business logic dependencies** (services, repositories)
- **Utility dependencies** (logging, metrics)
- **Dependency factory functions** for complex objects

### 5. Background Task Management
- **Task queue management** with lifecycle tracking
- **Async task execution** with dependency injection
- **Error handling and retry** mechanisms
- **Task completion monitoring**

## Implementation Components

### Settings Management

#### Settings Class
```python
class Settings:
    """Application settings with dependency injection support."""
    
    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_POOL_SIZE: int = 10
    
    # External API settings
    EXTERNAL_API_BASE_URL: str = "https://api.external.com"
    EXTERNAL_API_TIMEOUT: int = 30
    
    # Authentication settings
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
```

#### Settings Dependency
```python
@lru_cache()
def get_settings() -> Settings:
    """Get application settings (singleton)."""
    return Settings()
```

### Database Management

#### Database Manager
```python
class DatabaseManager:
    """Database connection manager with dependency injection."""
    
    def __init__(self, database_url: str, pool_size: int, max_overflow: int):
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize database connection pool."""
        if self.engine is None:
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                future=True,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False
            )
    
    async def get_session(self) -> AsyncSession:
        """Get database session."""
        if self.session_factory is None:
            await self.initialize()
        
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
```

#### Database Dependency
```python
async def get_db_session(
    db_manager: DatabaseManager = Depends(get_database_manager)
) -> AsyncSession:
    """Get database session dependency."""
    async for session in db_manager.get_session():
        yield session
```

### Cache Management

#### Cache Manager
```python
class CacheManager:
    """Redis cache manager with dependency injection."""
    
    def __init__(self, redis_url: str, pool_size: int):
        self.redis_url = redis_url
        self.pool_size = pool_size
        self.redis_pool = None
    
    async def initialize(self):
        """Initialize Redis connection pool."""
        if self.redis_pool is None:
            self.redis_pool = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=self.pool_size
            )
    
    async def get_redis(self) -> redis.Redis:
        """Get Redis connection."""
        if self.redis_pool is None:
            await self.initialize()
        return self.redis_pool
```

#### Cache Dependency
```python
async def get_cache(
    cache_manager: CacheManager = Depends(get_cache_manager)
) -> redis.Redis:
    """Get cache dependency."""
    return await cache_manager.get_redis()
```

### HTTP Client Management

#### HTTP Client Manager
```python
class HTTPClientManager:
    """HTTP client manager with dependency injection."""
    
    def __init__(self, base_url: str, timeout: int):
        self.base_url = base_url
        self.timeout = timeout
        self.client = None
    
    async def get_client(self) -> httpx.AsyncClient:
        """Get HTTP client with connection pooling."""
        if self.client is None:
            limits = httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0
            )
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                limits=limits,
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True
            )
        return self.client
```

#### HTTP Client Dependency
```python
async def get_http_client(
    client_manager: HTTPClientManager = Depends(get_http_client_manager)
) -> httpx.AsyncClient:
    """Get HTTP client dependency."""
    return await client_manager.get_client()
```

### Authentication Management

#### Auth Manager
```python
class AuthManager:
    """Authentication manager with dependency injection."""
    
    def __init__(self, secret_key: str, algorithm: str, access_token_expire_minutes: int):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token."""
        import jwt
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token."""
        import jwt
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
```

#### Authentication Dependencies
```python
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_manager: AuthManager = Depends(get_auth_manager)
) -> Dict[str, Any]:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = auth_manager.verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return {"user_id": user_id, "payload": payload}

async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current active user."""
    return current_user
```

### Custom Dependencies

#### Request Context Dependencies
```python
async def get_request_id() -> str:
    """Generate unique request ID for tracing."""
    return str(uuid.uuid4())

async def get_request_timestamp() -> datetime:
    """Get request timestamp."""
    return datetime.utcnow()

async def get_user_agent(request: Request) -> str:
    """Get user agent from request."""
    return request.headers.get("user-agent", "Unknown")

async def get_client_ip(request: Request) -> str:
    """Get client IP address."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "Unknown"
```

### Service Layer with Dependencies

#### User Service
```python
class UserService:
    """User service with dependency injection."""
    
    def __init__(
        self,
        db_session: AsyncSession,
        cache: redis.Redis,
        auth_manager: AuthManager,
        logger: logging.Logger
    ):
        self.db_session = db_session
        self.cache = cache
        self.auth_manager = auth_manager
        self.logger = logger
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        try:
            # Check if user already exists
            cache_key = f"user:email:{user_data.email}"
            existing_user = await self.cache.get(cache_key)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists"
                )
            
            # Simulate database insert
            user_dict = user_data.model_dump()
            user_dict.update({
                "id": 999,  # Mock ID
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # Cache user data
            await self.cache.setex(
                cache_key,
                300,  # 5 minutes TTL
                str(user_dict)
            )
            
            self.logger.info(f"User created: {user_data.email}")
            return UserResponse(**user_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to create user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
```

#### Service Factory
```python
def create_user_service(
    db_session: AsyncSession = Depends(get_db_session),
    cache: redis.Redis = Depends(get_cache),
    auth_manager: AuthManager = Depends(get_auth_manager)
) -> UserService:
    """Create user service with dependencies."""
    logger = logging.getLogger("user_service")
    return UserService(db_session, cache, auth_manager, logger)
```

### Application Lifecycle Management

#### Lifespan Manager
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger = logging.getLogger("app")
    logger.info("Application starting up...")
    
    # Initialize shared resources
    settings = get_settings()
    
    # Initialize database manager
    db_manager = DatabaseManager(
        database_url=settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW
    )
    await db_manager.initialize()
    
    # Initialize cache manager
    cache_manager = CacheManager(
        redis_url=settings.REDIS_URL,
        pool_size=settings.REDIS_POOL_SIZE
    )
    await cache_manager.initialize()
    
    # Store managers in app state
    app.state.db_manager = db_manager
    app.state.cache_manager = cache_manager
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")
    
    # Close connections
    await db_manager.close()
    await cache_manager.close()
```

#### FastAPI Application
```python
def create_app() -> FastAPI:
    """Create FastAPI application with dependency injection."""
    
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app
```

## API Routes with Dependencies

### Login Endpoint
```python
@app.post("/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    user_service: UserService = Depends(create_user_service),
    auth_manager: AuthManager = Depends(get_auth_manager),
    request_id: str = Depends(get_request_id),
    timestamp: datetime = Depends(get_request_timestamp)
):
    """User login with dependency injection."""
    
    # Authenticate user
    user = await user_service.authenticate_user(
        login_data.username,
        login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token = auth_manager.create_access_token(
        data={"sub": str(user.id)}
    )
    
    return LoginResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )
```

### Create User Endpoint
```python
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(create_user_service),
    background_tasks: BackgroundTasks,
    task_manager: BackgroundTaskManager = Depends(get_background_task_manager),
    request_id: str = Depends(get_request_id),
    user_agent: str = Depends(get_user_agent),
    client_ip: str = Depends(get_client_ip)
):
    """Create user with comprehensive dependency injection."""
    
    # Add background task
    async def send_welcome_email(user_email: str):
        await asyncio.sleep(1)  # Simulate email sending
        logging.getLogger("background_task").info(f"Welcome email sent to {user_email}")
    
    background_tasks.add_task(send_welcome_email, user_data.email)
    
    # Create user
    user = await user_service.create_user(user_data)
    
    # Log request details
    logging.getLogger("request_log").info(
        f"User created - Request ID: {request_id}, "
        f"User Agent: {user_agent}, Client IP: {client_ip}"
    )
    
    return user
```

### External API Call Endpoint
```python
@app.get("/external-api/{endpoint}")
async def call_external_api(
    endpoint: str,
    http_client: httpx.AsyncClient = Depends(get_http_client),
    cache: redis.Redis = Depends(get_cache),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Call external API with dependency injection."""
    
    # Check cache first
    cache_key = f"external_api:{endpoint}"
    cached_response = await cache.get(cache_key)
    if cached_response:
        return {"data": cached_response, "source": "cache"}
    
    try:
        # Make external API call
        response = await http_client.get(f"/{endpoint}")
        response.raise_for_status()
        
        # Cache response
        await cache.setex(cache_key, 300, response.text)
        
        return {"data": response.json(), "source": "api"}
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"External API error: {e.response.status_code}"
        )
```

## Usage Examples

### Basic Dependency Usage
```python
# Simple dependency injection
@app.get("/items/")
async def get_items(
    db: AsyncSession = Depends(get_db_session),
    cache: redis.Redis = Depends(get_cache)
):
    """Get items with database and cache dependencies."""
    
    # Check cache first
    cached_items = await cache.get("items")
    if cached_items:
        return {"items": cached_items, "source": "cache"}
    
    # Query database
    result = await db.execute(select(Item))
    items = result.scalars().all()
    
    # Cache results
    await cache.setex("items", 300, str(items))
    
    return {"items": items, "source": "database"}
```

### Complex Dependency Chain
```python
# Dependency chain example
@app.post("/orders/")
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db_session),
    cache: redis.Redis = Depends(get_cache),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    order_service: OrderService = Depends(create_order_service),
    notification_service: NotificationService = Depends(create_notification_service)
):
    """Create order with complex dependency chain."""
    
    # Create order
    order = await order_service.create_order(order_data, current_user["user_id"])
    
    # Send notification
    await notification_service.send_order_confirmation(order.id)
    
    return order
```

### Testing with Dependency Overrides
```python
# Test with dependency overrides
def test_create_user():
    """Test user creation with mocked dependencies."""
    
    # Mock dependencies
    mock_db = AsyncMock()
    mock_cache = AsyncMock()
    mock_auth_manager = Mock()
    
    # Override dependencies
    app.dependency_overrides[get_db_session] = lambda: mock_db
    app.dependency_overrides[get_cache] = lambda: mock_cache
    app.dependency_overrides[get_auth_manager] = lambda: mock_auth_manager
    
    # Test request
    response = client.post("/users/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 201
    
    # Clean up
    app.dependency_overrides.clear()
```

## Best Practices

### 1. Dependency Design
- **Single responsibility**: Each dependency should have one clear purpose
- **Interface segregation**: Use interfaces for complex dependencies
- **Dependency inversion**: Depend on abstractions, not concretions
- **Loose coupling**: Minimize dependencies between components

### 2. Resource Management
- **Connection pooling**: Use connection pools for database and cache
- **Resource cleanup**: Implement proper cleanup in lifespan managers
- **Error handling**: Handle resource failures gracefully
- **Monitoring**: Monitor resource usage and health

### 3. Performance Optimization
- **Dependency caching**: Use FastAPI's automatic dependency caching
- **Lazy loading**: Initialize expensive resources on demand
- **Connection reuse**: Reuse connections across requests
- **Async operations**: Use async dependencies for I/O operations

### 4. Security Considerations
- **Configuration security**: Secure sensitive configuration values
- **Authentication**: Implement proper authentication dependencies
- **Input validation**: Validate all inputs with Pydantic models
- **Error handling**: Don't expose sensitive information in errors

### 5. Testing Strategy
- **Dependency overrides**: Use dependency overrides for testing
- **Mock external services**: Mock database, cache, and external APIs
- **Integration testing**: Test with real dependencies when needed
- **Performance testing**: Test dependency performance under load

## Benefits

### 1. Code Quality
- **Loose coupling** between components
- **High cohesion** within components
- **Testability** with dependency overrides
- **Maintainability** with clear dependency relationships

### 2. Performance
- **Resource sharing** across requests
- **Connection pooling** for better performance
- **Dependency caching** for faster resolution
- **Async operations** for better concurrency

### 3. Scalability
- **Horizontal scaling** with stateless dependencies
- **Resource management** for better resource utilization
- **Load balancing** with shared resources
- **Monitoring** for performance optimization

### 4. Developer Experience
- **Clear dependency relationships** in code
- **Easy testing** with dependency overrides
- **Type safety** with proper type hints
- **Documentation** through dependency structure

## Conclusion

This dependency injection implementation provides a comprehensive foundation for building scalable, maintainable FastAPI applications. It demonstrates:

- **Effective resource management** with connection pooling and lifecycle management
- **Secure authentication** with JWT tokens and proper validation
- **Performance optimization** with caching and async operations
- **Testing strategies** with dependency overrides and mocking
- **Best practices** for dependency design and management

The implementation serves as a reference for implementing dependency injection patterns in FastAPI applications, ensuring proper resource management, security, and performance while maintaining code quality and testability.

Key benefits include:
- **Improved code organization** with clear dependency relationships
- **Better resource utilization** with connection pooling and caching
- **Enhanced security** with proper authentication and validation
- **Easier testing** with dependency overrides and mocking
- **Better performance** with async operations and resource sharing
- **Scalable architecture** with proper resource management

The patterns demonstrated here can be applied to any FastAPI application to ensure proper dependency management, resource utilization, and application scalability. 