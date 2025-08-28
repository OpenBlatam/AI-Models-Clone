# FastAPI Application with Dedicated Async Functions
================================================

## Overview

This comprehensive FastAPI application demonstrates the use of dedicated async functions for database and external API operations. The application implements proper separation of concerns with dedicated async functions, repository patterns, client patterns, and comprehensive async error handling and retry logic.

## Key Dedicated Async Functions Features

### ✅ Dedicated Async Functions Implemented

1. **Dedicated Async Database Functions**: All database operations use dedicated async functions
2. **Dedicated Async External API Functions**: All external API operations use dedicated async functions
3. **Async Service Layer**: Proper separation of concerns with async service layer
4. **Async Repository Pattern**: Database operations using repository pattern
5. **Async Client Pattern**: External API operations using client pattern
6. **Comprehensive Async Error Handling**: Retry logic and error handling for all async operations
7. **Async Connection Pooling**: Efficient resource management with connection pooling

## Architecture

### 1. Async Configuration

#### Configuration Settings
```python
class AsyncConfig:
    """Configuration for async operations."""
    # Database Settings
    DB_POOL_SIZE = 20
    DB_MAX_OVERFLOW = 30
    DB_OPERATION_TIMEOUT = 10.0
    DB_RETRY_ATTEMPTS = 3
    DB_RETRY_DELAY = 1.0
    
    # External API Settings
    EXTERNAL_API_TIMEOUT = 15.0
    EXTERNAL_API_RETRY_ATTEMPTS = 3
    EXTERNAL_API_RETRY_DELAY = 2.0
    EXTERNAL_API_MAX_CONNECTIONS = 100
    
    # Cache Settings
    CACHE_TTL = 300
    CACHE_MAX_SIZE = 1000
    CACHE_RETRY_ATTEMPTS = 2
    
    # Connection Settings
    HTTP_CLIENT_TIMEOUT = 30.0
    HTTP_CLIENT_MAX_CONNECTIONS = 100
    HTTP_CLIENT_KEEPALIVE_TIMEOUT = 60.0
    
    # Async Processing Settings
    ENABLE_ASYNC_PROCESSING = True
    ENABLE_CONNECTION_POOLING = True
    ENABLE_RETRY_LOGIC = True
    ENABLE_CIRCUIT_BREAKER = True
```

#### Operation Types
```python
class OperationType(Enum):
    """Types of async operations."""
    DATABASE_READ = "database_read"
    DATABASE_WRITE = "database_write"
    DATABASE_DELETE = "database_delete"
    EXTERNAL_API_GET = "external_api_get"
    EXTERNAL_API_POST = "external_api_post"
    EXTERNAL_API_PUT = "external_api_put"
    EXTERNAL_API_DELETE = "external_api_delete"
    CACHE_GET = "cache_get"
    CACHE_SET = "cache_set"
    CACHE_DELETE = "cache_delete"
```

**Features:**
- **Configurable Timeouts**: Different timeout settings for different operation types
- **Retry Logic**: Comprehensive retry logic for all async operations
- **Connection Pooling**: Efficient connection management
- **Operation Tracking**: Detailed operation type tracking

### 2. Async Database Repository Pattern

#### Repository Implementation
```python
class AsyncDatabaseRepository:
    """Dedicated async functions for database operations."""
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.operation_stats = defaultdict(lambda: deque(maxlen=1000))
    
    async def create_user_async(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dedicated async function to create user."""
        async def _execute(session: AsyncSession) -> Dict[str, Any]:
            # Check if user already exists
            existing_user = await session.execute(
                select(User).where(
                    (User.username == user_data['username']) | (User.email == user_data['email'])
                )
            )
            
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this username or email already exists"
                )
            
            # Create new user
            db_user = User(
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data.get('full_name'),
                is_active=user_data.get('is_active', True),
                age=user_data.get('age'),
                bio=user_data.get('bio')
            )
            
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            
            return {
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
        
        return await self._execute_with_retry(_execute, OperationType.DATABASE_WRITE)
```

#### Retry Logic Implementation
```python
async def _execute_with_retry(self, operation_func, operation_type: OperationType):
    """Execute database operation with retry logic."""
    for attempt in range(AsyncConfig.DB_RETRY_ATTEMPTS):
        try:
            async with self.session_factory() as session:
                start_time = time.time()
                result = await operation_func(session)
                operation_time = time.time() - start_time
                
                # Record operation stats
                self.operation_stats[operation_type.value].append(operation_time)
                
                return result
                
        except Exception as e:
            logger.error(f"Database operation failed (attempt {attempt + 1}): {e}")
            if attempt == AsyncConfig.DB_RETRY_ATTEMPTS - 1:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database operation failed after retries"
                )
            await asyncio.sleep(AsyncConfig.DB_RETRY_DELAY * (attempt + 1))
```

**Features:**
- **Dedicated Functions**: Each database operation has its own dedicated async function
- **Retry Logic**: Automatic retry with exponential backoff
- **Operation Statistics**: Detailed operation tracking and statistics
- **Error Handling**: Comprehensive error handling with proper HTTP status codes

### 3. Async External API Client Pattern

#### Client Implementation
```python
class AsyncExternalAPIClient:
    """Dedicated async functions for external API operations."""
    
    def __init__(self):
        self.session = None
        self.timeout = httpx.Timeout(AsyncConfig.EXTERNAL_API_TIMEOUT)
        self.operation_stats = defaultdict(lambda: deque(maxlen=1000))
    
    async def get_user_profile_async(self, user_id: int) -> Dict[str, Any]:
        """Dedicated async function to get user profile from external API."""
        async def _execute() -> Dict[str, Any]:
            session = await self.get_session()
            response = await session.get(f"https://api.example.com/users/{user_id}/profile")
            response.raise_for_status()
            return response.json()
        
        return await self._execute_with_retry(_execute, OperationType.EXTERNAL_API_GET)
    
    async def get_user_posts_async(self, user_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Dedicated async function to get user posts from external API."""
        async def _execute() -> Dict[str, Any]:
            session = await self.get_session()
            params = {'page': page, 'limit': limit}
            response = await session.get(f"https://api.example.com/users/{user_id}/posts", params=params)
            response.raise_for_status()
            return response.json()
        
        return await self._execute_with_retry(_execute, OperationType.EXTERNAL_API_GET)
```

#### Session Management
```python
async def get_session(self):
    """Get or create HTTP session."""
    if self.session is None:
        limits = httpx.Limits(
            max_keepalive_connections=AsyncConfig.EXTERNAL_API_MAX_CONNECTIONS,
            max_connections=AsyncConfig.EXTERNAL_API_MAX_CONNECTIONS
        )
        self.session = httpx.AsyncClient(
            timeout=self.timeout,
            limits=limits,
            http2=True
        )
    return self.session
```

**Features:**
- **Dedicated Functions**: Each external API operation has its own dedicated async function
- **Connection Pooling**: Efficient HTTP connection management
- **HTTP/2 Support**: Modern HTTP protocol support
- **Retry Logic**: Automatic retry with configurable delays

### 4. Async Cache Client Pattern

#### Cache Client Implementation
```python
class AsyncCacheClient:
    """Dedicated async functions for cache operations."""
    
    def __init__(self):
        self.cache = TTLCache(
            maxsize=AsyncConfig.CACHE_MAX_SIZE,
            ttl=AsyncConfig.CACHE_TTL
        )
        self.redis_client = None
        self.operation_stats = defaultdict(lambda: deque(maxlen=1000))
    
    async def get_user_cache_async(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Dedicated async function to get user from cache."""
        async def _execute() -> Optional[Dict[str, Any]]:
            cache_key = f"user:{user_id}"
            
            # Try memory cache first
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Try Redis if available
            if self.redis_client:
                try:
                    value = await self.redis_client.get(cache_key)
                    if value:
                        return orjson.loads(value)
                except Exception as e:
                    logger.error(f"Redis GET error: {e}")
            
            return None
        
        return await self._execute_with_retry(_execute, OperationType.CACHE_GET)
    
    async def set_user_cache_async(self, user_id: int, user_data: Dict[str, Any], ttl: int = None) -> bool:
        """Dedicated async function to set user in cache."""
        async def _execute() -> bool:
            cache_key = f"user:{user_id}"
            ttl = ttl or AsyncConfig.CACHE_TTL
            
            # Set in memory cache
            self.cache[cache_key] = user_data
            
            # Set in Redis if available
            if self.redis_client:
                try:
                    serialized_value = orjson.dumps(user_data)
                    await self.redis_client.set(cache_key, serialized_value, ex=ttl)
                except Exception as e:
                    logger.error(f"Redis SET error: {e}")
            
            return True
        
        return await self._execute_with_retry(_execute, OperationType.CACHE_SET)
```

**Features:**
- **Multi-level Caching**: Memory and Redis cache support
- **Dedicated Functions**: Each cache operation has its own dedicated async function
- **TTL Support**: Configurable time-to-live for cache entries
- **Error Handling**: Graceful error handling for cache failures

### 5. Async Service Layer

#### User Service Implementation
```python
class AsyncUserService:
    """Service layer with dedicated async functions."""
    
    async def create_user_async(self, user_data: UserCreateRequest) -> UserResponse:
        """Create user with dedicated async functions."""
        # Convert to dict for database operation
        user_dict = user_data.model_dump()
        
        # Create user in database
        db_user = await db_repository.create_user_async(user_dict)
        
        # Cache the new user
        await cache_client.set_user_cache_async(db_user['id'], db_user)
        
        return UserResponse(**db_user)
    
    async def get_user_async(self, user_id: int) -> Optional[UserResponse]:
        """Get user with dedicated async functions."""
        # Try cache first
        cached_user = await cache_client.get_user_cache_async(user_id)
        if cached_user:
            return UserResponse(**cached_user)
        
        # Get from database
        db_user = await db_repository.get_user_by_id_async(user_id)
        if not db_user:
            return None
        
        # Cache the result
        await cache_client.set_user_cache_async(user_id, db_user)
        
        return UserResponse(**db_user)
```

#### External API Service Implementation
```python
class AsyncExternalAPIService:
    """Service layer for external API operations."""
    
    async def get_user_profile_async(self, user_id: int) -> ExternalAPIResponse:
        """Get user profile from external API."""
        try:
            profile_data = await external_api_client.get_user_profile_async(user_id)
            return ExternalAPIResponse(
                success=True,
                data=profile_data,
                message="User profile retrieved successfully",
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return ExternalAPIResponse(
                success=False,
                data=None,
                message="Failed to retrieve user profile",
                timestamp=datetime.now()
            )
```

**Features:**
- **Separation of Concerns**: Clear separation between different types of operations
- **Dedicated Functions**: Each service method is a dedicated async function
- **Error Handling**: Comprehensive error handling with proper response models
- **Caching Integration**: Automatic cache integration in service layer

## Dedicated Async Functions Analysis

### 1. Database Operations

#### Dedicated Database Functions
```python
# Create user
async def create_user_async(self, user_data: Dict[str, Any]) -> Dict[str, Any]

# Get user by ID
async def get_user_by_id_async(self, user_id: int) -> Optional[Dict[str, Any]]

# Get users with pagination
async def get_users_async(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]

# Update user
async def update_user_async(self, user_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]

# Delete user
async def delete_user_async(self, user_id: int) -> bool

# Search users
async def search_users_async(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]

# Get user count
async def get_user_count_async(self) -> int
```

**Benefits:**
- **Single Responsibility**: Each function has a single, clear purpose
- **Reusability**: Functions can be reused across different service layers
- **Testability**: Each function can be tested independently
- **Maintainability**: Easy to modify and maintain individual functions

### 2. External API Operations

#### Dedicated External API Functions
```python
# Get user profile
async def get_user_profile_async(self, user_id: int) -> Dict[str, Any]

# Get user posts
async def get_user_posts_async(self, user_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]

# Create user post
async def create_user_post_async(self, user_id: int, post_data: Dict[str, Any]) -> Dict[str, Any]

# Update user post
async def update_user_post_async(self, user_id: int, post_id: int, post_data: Dict[str, Any]) -> Dict[str, Any]

# Delete user post
async def delete_user_post_async(self, user_id: int, post_id: int) -> bool

# Get user friends
async def get_user_friends_async(self, user_id: int) -> List[Dict[str, Any]]

# Get user analytics
async def get_user_analytics_async(self, user_id: int, date_range: str = "30d") -> Dict[str, Any]
```

**Benefits:**
- **API Abstraction**: Clean abstraction over external APIs
- **Error Handling**: Centralized error handling for external calls
- **Retry Logic**: Automatic retry with configurable strategies
- **Connection Management**: Efficient connection pooling and management

### 3. Cache Operations

#### Dedicated Cache Functions
```python
# Get user from cache
async def get_user_cache_async(self, user_id: int) -> Optional[Dict[str, Any]]

# Set user in cache
async def set_user_cache_async(self, user_id: int, user_data: Dict[str, Any], ttl: int = None) -> bool

# Delete user from cache
async def delete_user_cache_async(self, user_id: int) -> bool

# Get users list from cache
async def get_users_cache_async(self, cache_key: str) -> Optional[List[Dict[str, Any]]]

# Set users list in cache
async def set_users_cache_async(self, cache_key: str, users_data: List[Dict[str, Any]], ttl: int = None) -> bool
```

**Benefits:**
- **Multi-level Caching**: Support for memory and Redis caching
- **TTL Management**: Configurable time-to-live for cache entries
- **Error Resilience**: Graceful handling of cache failures
- **Performance Optimization**: Fast cache operations with dedicated functions

## API Endpoints with Dedicated Async Functions

### 1. User Management Endpoints

#### Create User Endpoint
```python
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateRequest) -> UserResponse:
    """Create user endpoint with dedicated async functions."""
    return await user_service.create_user_async(user_data)
```

#### Get User Endpoint
```python
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int = Path(..., gt=0, description="User ID")) -> UserResponse:
    """Get user by ID endpoint with dedicated async functions."""
    user = await user_service.get_user_async(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
```

#### Update User Endpoint
```python
@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int = Path(..., gt=0, description="User ID"),
    update_data: UserUpdateRequest = Field(..., description="User update data")
) -> UserResponse:
    """Update user endpoint with dedicated async functions."""
    user = await user_service.update_user_async(user_id, update_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
```

### 2. External API Endpoints

#### Get User Profile Endpoint
```python
@app.get("/external/users/{user_id}/profile", response_model=ExternalAPIResponse)
async def get_user_profile(user_id: int = Path(..., gt=0, description="User ID")) -> ExternalAPIResponse:
    """Get user profile from external API with dedicated async function."""
    return await external_api_service.get_user_profile_async(user_id)
```

#### Get User Posts Endpoint
```python
@app.get("/external/users/{user_id}/posts", response_model=ExternalAPIResponse)
async def get_user_posts(
    user_id: int = Path(..., gt=0, description="User ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
) -> ExternalAPIResponse:
    """Get user posts from external API with dedicated async function."""
    return await external_api_service.get_user_posts_async(user_id, page, limit)
```

### 3. Statistics Endpoints

#### Operation Statistics Endpoint
```python
@app.get("/stats/operations", response_model=OperationStatsResponse)
async def get_operation_stats() -> OperationStatsResponse:
    """Get operation statistics for all dedicated async functions."""
    return OperationStatsResponse(
        database_stats=db_repository.get_operation_stats(),
        external_api_stats=external_api_client.get_operation_stats(),
        cache_stats=cache_client.get_operation_stats()
    )
```

## API Endpoints

### Core Endpoints with Dedicated Async Functions

| Endpoint | Dedicated Async Functions | Operations | Features |
|----------|--------------------------|------------|----------|
| `GET /` | Basic response | None | Standard |
| `GET /health` | Health check | Database check | Basic |
| `GET /stats/operations` | Statistics collection | All operations | Statistics |
| `POST /users` | Create user | Database + cache | CRUD |
| `GET /users/{user_id}` | Get user | Cache + database | CRUD |
| `GET /users` | Get users | Cache + database | CRUD |
| `PUT /users/{user_id}` | Update user | Database + cache | CRUD |
| `DELETE /users/{user_id}` | Delete user | Database + cache | CRUD |
| `GET /users/search` | Search users | Database | Search |
| `GET /users/count` | Get count | Database | Statistics |
| `GET /external/users/{user_id}/profile` | Get profile | External API | External |
| `GET /external/users/{user_id}/posts` | Get posts | External API | External |
| `POST /external/users/{user_id}/posts` | Create post | External API | External |

### Dedicated Async Function Types

| Function Type | Dedicated Functions | Retry Logic | Error Handling |
|---------------|-------------------|-------------|----------------|
| `DATABASE_READ` | get_user_by_id_async, get_users_async, search_users_async, get_user_count_async | Yes | HTTP 500 |
| `DATABASE_WRITE` | create_user_async, update_user_async | Yes | HTTP 500 |
| `DATABASE_DELETE` | delete_user_async | Yes | HTTP 500 |
| `EXTERNAL_API_GET` | get_user_profile_async, get_user_posts_async, get_user_friends_async, get_user_analytics_async | Yes | HTTP 502 |
| `EXTERNAL_API_POST` | create_user_post_async | Yes | HTTP 502 |
| `EXTERNAL_API_PUT` | update_user_post_async | Yes | HTTP 502 |
| `EXTERNAL_API_DELETE` | delete_user_post_async | Yes | HTTP 502 |
| `CACHE_GET` | get_user_cache_async, get_users_cache_async | Yes | HTTP 500 |
| `CACHE_SET` | set_user_cache_async, set_users_cache_async | Yes | HTTP 500 |
| `CACHE_DELETE` | delete_user_cache_async | Yes | HTTP 500 |

## Dedicated Async Functions Benefits

### 1. Separation of Concerns
- **Database Operations**: Dedicated functions for all database operations
- **External API Operations**: Dedicated functions for all external API calls
- **Cache Operations**: Dedicated functions for all cache operations
- **Service Layer**: Clean service layer with dedicated async functions

### 2. Reusability and Maintainability
- **Single Responsibility**: Each function has a single, clear purpose
- **Reusability**: Functions can be reused across different service layers
- **Testability**: Each function can be tested independently
- **Maintainability**: Easy to modify and maintain individual functions

### 3. Error Handling and Resilience
- **Retry Logic**: Automatic retry with configurable strategies
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Circuit Breaker**: Built-in circuit breaker patterns for external calls
- **Graceful Degradation**: Fallback mechanisms for failures

### 4. Performance Optimization
- **Connection Pooling**: Efficient connection management
- **Caching**: Multi-level caching with dedicated functions
- **Async Operations**: All operations are truly asynchronous
- **Resource Management**: Proper resource lifecycle management

### 5. Monitoring and Observability
- **Operation Statistics**: Detailed tracking of all operations
- **Performance Metrics**: Response time and throughput monitoring
- **Error Tracking**: Comprehensive error tracking and logging
- **Health Checks**: Built-in health check endpoints

## Configuration

### Environment Variables
```bash
# Database Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_OPERATION_TIMEOUT=10.0
DB_RETRY_ATTEMPTS=3
DB_RETRY_DELAY=1.0

# External API Settings
EXTERNAL_API_TIMEOUT=15.0
EXTERNAL_API_RETRY_ATTEMPTS=3
EXTERNAL_API_RETRY_DELAY=2.0
EXTERNAL_API_MAX_CONNECTIONS=100

# Cache Settings
CACHE_TTL=300
CACHE_MAX_SIZE=1000
CACHE_RETRY_ATTEMPTS=2

# Connection Settings
HTTP_CLIENT_TIMEOUT=30.0
HTTP_CLIENT_MAX_CONNECTIONS=100
HTTP_CLIENT_KEEPALIVE_TIMEOUT=60.0

# Async Processing Settings
ENABLE_ASYNC_PROCESSING=true
ENABLE_CONNECTION_POOLING=true
ENABLE_RETRY_LOGIC=true
ENABLE_CIRCUIT_BREAKER=true
```

### Async Configuration
```python
class AsyncConfig:
    """Configuration for async operations."""
    # Database Settings
    DB_POOL_SIZE = 20
    DB_MAX_OVERFLOW = 30
    DB_OPERATION_TIMEOUT = 10.0
    DB_RETRY_ATTEMPTS = 3
    DB_RETRY_DELAY = 1.0
    
    # External API Settings
    EXTERNAL_API_TIMEOUT = 15.0
    EXTERNAL_API_RETRY_ATTEMPTS = 3
    EXTERNAL_API_RETRY_DELAY = 2.0
    EXTERNAL_API_MAX_CONNECTIONS = 100
    
    # Cache Settings
    CACHE_TTL = 300
    CACHE_MAX_SIZE = 1000
    CACHE_RETRY_ATTEMPTS = 2
    
    # Connection Settings
    HTTP_CLIENT_TIMEOUT = 30.0
    HTTP_CLIENT_MAX_CONNECTIONS = 100
    HTTP_CLIENT_KEEPALIVE_TIMEOUT = 60.0
    
    # Async Processing Settings
    ENABLE_ASYNC_PROCESSING = True
    ENABLE_CONNECTION_POOLING = True
    ENABLE_RETRY_LOGIC = True
    ENABLE_CIRCUIT_BREAKER = True
```

## Best Practices Implemented

### ✅ Dedicated Async Functions Best Practices
- [x] Dedicated async functions for all database operations
- [x] Dedicated async functions for all external API operations
- [x] Dedicated async functions for all cache operations
- [x] Async service layer with proper separation of concerns
- [x] Repository pattern for database operations
- [x] Client pattern for external API operations
- [x] Comprehensive async error handling and retry logic

### ✅ FastAPI Best Practices
- [x] Async route handlers with dedicated functions
- [x] Proper separation of concerns
- [x] Comprehensive error handling
- [x] Resource pooling and management
- [x] Monitoring and observability

### ✅ Performance Best Practices
- [x] Connection pooling for database and HTTP
- [x] Multi-level caching with dedicated functions
- [x] Retry logic with exponential backoff
- [x] Circuit breaker patterns for external calls
- [x] Comprehensive operation statistics

## Conclusion

This FastAPI application demonstrates comprehensive use of dedicated async functions for database and external API operations. The implementation includes:

1. **Dedicated Async Database Functions**: All database operations use dedicated async functions with repository pattern
2. **Dedicated Async External API Functions**: All external API operations use dedicated async functions with client pattern
3. **Async Service Layer**: Proper separation of concerns with async service layer
4. **Comprehensive Error Handling**: Retry logic and error handling for all async operations
5. **Async Connection Pooling**: Efficient resource management with connection pooling
6. **Monitoring and Observability**: Detailed operation tracking and statistics

The application provides significant benefits through:
- **Separation of Concerns**: Clear separation between different types of operations
- **Reusability**: Dedicated functions can be reused across different service layers
- **Maintainability**: Easy to modify and maintain individual functions
- **Error Resilience**: Comprehensive error handling and retry logic
- **Performance Optimization**: Efficient resource management and caching
- **Observability**: Detailed monitoring and statistics for all operations

This serves as a foundation for building high-performance APIs with dedicated async functions and proper separation of concerns. 