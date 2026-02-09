# Comprehensive Middleware System

This middleware system provides centralized logging, metrics, exception handling, security, and performance monitoring for FastAPI applications using functional programming patterns and the RORO (Receive Object, Return Object) pattern.

## Features

- **Structured Logging**: JSON-formatted logs with context and correlation IDs
- **Metrics Collection**: Prometheus-compatible metrics with histograms, counters, and gauges
- **Exception Handling**: Centralized error handling with custom exception types
- **Security Middleware**: Authentication, authorization, rate limiting, and security headers
- **Performance Monitoring**: Caching, database profiling, and performance metrics
- **Decorators**: Easy-to-use decorators for common patterns
- **FastAPI Integration**: Seamless integration with FastAPI middleware stack

## Quick Start

### 1. Basic Setup

```python
from fastapi import FastAPI
from middleware.core import setup_structured_logging, setup_middleware_stack
from middleware.security import setup_security_middleware
from middleware.performance import setup_performance_middleware

# Initialize logging
logger = setup_structured_logging(log_level="INFO", log_format="json")

# Create FastAPI app
app = FastAPI()

# Setup all middleware
setup_middleware_stack(app)
setup_security_middleware(app)
setup_performance_middleware(app)
```

### 2. Using Decorators

```python
from middleware.core import with_logging, with_metrics, with_exception_handling
from middleware.security import require_authentication, rate_limit
from middleware.performance import with_caching, with_performance_monitoring

@with_logging("get_user_data", "users")
@with_metrics("get_user_data", "users")
@with_caching(ttl=300, key_prefix="user")
@require_authentication()
@rate_limit(limit=100, window=60)
async def get_user_data(user_id: str, request: Request):
    """Get user data with comprehensive middleware."""
    # Your business logic here
    return {"user_id": user_id, "data": "user_data"}
```

### 3. Manual Context Usage

```python
from middleware.core import create_log_context, log_operation, LogLevel
from middleware.core import create_metric_context, record_metric, MetricType

async def custom_operation(request_id: str, user_id: str):
    # Create logging context
    log_context = create_log_context(
        request_id=request_id,
        user_id=user_id,
        operation="custom_operation",
        component="business_logic"
    )
    
    # Log operation start
    log_operation(logger, log_context, "Starting custom operation")
    
    # Create metrics context
    metric_context = create_metric_context(
        "custom_operation", "business_logic"
    )
    
    try:
        # Your business logic here
        result = await perform_operation()
        
        # Record success metric
        record_metric(metric_context, MetricType.HISTOGRAM, time.time() - metric_context.start_time)
        
        return result
    except Exception as e:
        # Record error metric
        record_metric(metric_context, MetricType.COUNTER, 1, error="true")
        raise
```

## Core Middleware Components

### 1. Logging Middleware

**Features:**
- Structured JSON logging
- Request correlation IDs
- User context tracking
- Operation-level logging
- Configurable log levels and formats

**Usage:**
```python
from middleware.core import setup_structured_logging, create_log_context, log_operation

# Setup logging
logger = setup_structured_logging(log_level="INFO", log_format="json")

# Create context
context = create_log_context(
    request_id="req-123",
    user_id="user-456",
    operation="data_processing",
    component="api"
)

# Log with context
log_operation(logger, context, "Processing started", level=LogLevel.INFO)
```

### 2. Metrics Middleware

**Features:**
- Prometheus-compatible metrics
- Histograms for timing
- Counters for events
- Gauges for current values
- Automatic metric registration

**Usage:**
```python
from middleware.core import create_metric_context, record_metric, MetricType

# Create metric context
context = create_metric_context("api_request", "web", method="GET", path="/users")

# Record metrics
record_metric(context, MetricType.HISTOGRAM, 0.125)  # Duration
record_metric(context, MetricType.COUNTER, 1, status_code="200")  # Count
record_metric(context, MetricType.GAUGE, 42, metric="active_users")  # Current value
```

### 3. Exception Handling Middleware

**Features:**
- Custom exception types
- Structured error responses
- User-friendly error messages
- Stack trace handling
- Error severity levels

**Usage:**
```python
from middleware.core import create_exception_context, handle_exception
from middleware.security import SecurityException

try:
    # Your code here
    raise SecurityException("Access denied")
except Exception as e:
    context = create_exception_context(
        e, request_id="req-123", user_id="user-456"
    )
    error_response = handle_exception(logger, context)
    return error_response
```

## Security Middleware

### 1. Authentication

**Features:**
- JWT token validation
- Password hashing with PBKDF2
- Session management
- User context injection

**Usage:**
```python
from middleware.security import (
    validate_jwt_token, hash_password, verify_password,
    require_authentication
)

# Hash password
password_data = hash_password("secure_password")
# Returns: {"hash": "...", "salt": "..."}

# Verify password
is_valid = verify_password("secure_password", password_data["hash"], password_data["salt"])

# Protect endpoint
@require_authentication()
async def protected_endpoint(request: Request):
    user_id = request.state.user_id
    return {"message": f"Hello user {user_id}"}
```

### 2. Authorization

**Features:**
- Role-based access control
- Permission-based access control
- Declarative authorization decorators

**Usage:**
```python
from middleware.security import require_permission, require_role

@require_permission("read:users")
async def get_users():
    return {"users": [...]}

@require_role(["admin", "manager"])
async def admin_only():
    return {"admin_data": "..."}
```

### 3. Rate Limiting

**Features:**
- Sliding window rate limiting
- IP-based and user-based limits
- Configurable limits and windows
- Rate limit headers

**Usage:**
```python
from middleware.security import rate_limit

@rate_limit(limit=100, window=60)  # 100 requests per minute
async def rate_limited_endpoint():
    return {"data": "..."}

# Custom key function
def user_based_key(request: Request):
    return f"user:{request.state.user_id}"

@rate_limit(limit=10, window=60, key_func=user_based_key)
async def user_rate_limited():
    return {"data": "..."}
```

### 4. Security Headers

**Features:**
- Automatic security headers
- XSS protection
- CSRF protection
- Content security policy
- HSTS headers

**Usage:**
```python
# Automatically applied by security middleware
# Headers added:
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY
# - X-XSS-Protection: 1; mode=block
# - Strict-Transport-Security: max-age=31536000; includeSubDomains
# - Content-Security-Policy: default-src 'self'
```

## Performance Middleware

### 1. Caching

**Features:**
- Redis-based caching
- Automatic cache key generation
- TTL support
- Cache hit/miss metrics

**Usage:**
```python
from middleware.performance import with_caching, CacheManager

# Initialize cache
cache_manager = CacheManager("redis://localhost:6379")
await cache_manager.connect()

# Use caching decorator
@with_caching(ttl=300, key_prefix="users")
async def get_user(user_id: str):
    # Expensive database query
    return await database.get_user(user_id)

# Manual cache operations
await cache_manager.set("key", {"data": "value"}, ttl=3600)
cached_data = await cache_manager.get("key")
```

### 2. Database Profiling

**Features:**
- Query performance tracking
- Slow query detection
- Query statistics
- Optimization suggestions

**Usage:**
```python
from middleware.performance import with_database_profiling, DatabaseProfiler

@with_database_profiling()
async def database_operation():
    # Database queries are automatically profiled
    return await db.execute("SELECT * FROM users")

# Get profiling statistics
db_profiler = DatabaseProfiler()
stats = db_profiler.get_query_statistics()
slow_queries = db_profiler.get_slow_queries(threshold=1.0)
```

### 3. Performance Monitoring

**Features:**
- Memory usage tracking
- CPU usage monitoring
- Operation timing
- Performance alerts

**Usage:**
```python
from middleware.performance import with_performance_monitoring

@with_performance_monitoring("data_processing", "analytics")
async def process_data():
    # Performance is automatically monitored
    return await heavy_computation()
```

## Decorators Reference

### Core Decorators

| Decorator | Purpose | Example |
|-----------|---------|---------|
| `@with_logging` | Automatic operation logging | `@with_logging("get_user", "users")` |
| `@with_metrics` | Automatic metrics collection | `@with_metrics("api_call", "web")` |
| `@with_exception_handling` | Centralized error handling | `@with_exception_handling()` |

### Security Decorators

| Decorator | Purpose | Example |
|-----------|---------|---------|
| `@require_authentication` | Require valid JWT token | `@require_authentication()` |
| `@require_permission` | Require specific permission | `@require_permission("read:users")` |
| `@require_role` | Require specific role | `@require_role(["admin"])` |
| `@rate_limit` | Apply rate limiting | `@rate_limit(100, 60)` |

### Performance Decorators

| Decorator | Purpose | Example |
|-----------|---------|---------|
| `@with_caching` | Cache function results | `@with_caching(ttl=300)` |
| `@with_database_profiling` | Profile database queries | `@with_database_profiling()` |
| `@with_performance_monitoring` | Monitor performance | `@with_performance_monitoring("op", "comp")` |

## Configuration

### Environment Variables

```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_INCLUDE_TIMESTAMP=true

# Redis Cache
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRES_IN=3600

# Rate Limiting
RATE_LIMIT_DEFAULT=100
RATE_LIMIT_WINDOW=60
```

### Application Configuration

```python
# middleware_config.py
from dataclasses import dataclass

@dataclass
class MiddlewareConfig:
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    include_timestamp: bool = True
    
    # Cache
    redis_url: str = "redis://localhost:6379"
    cache_default_ttl: int = 3600
    
    # Security
    jwt_secret_key: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expires_in: int = 3600
    
    # Rate Limiting
    default_rate_limit: int = 100
    default_rate_window: int = 60
    
    # Performance
    slow_query_threshold: float = 1.0
    enable_performance_monitoring: bool = True
```

## Monitoring and Observability

### 1. Prometheus Metrics

Access metrics at `/metrics`:
```bash
curl http://localhost:8000/metrics
```

Available metrics:
- `http_request_duration_seconds` - Request duration histogram
- `http_request_total` - Request count
- `cache_hit_total` - Cache hit count
- `cache_miss_total` - Cache miss count
- `database_query_duration_seconds` - Database query duration

### 2. Structured Logging

Logs are in JSON format with correlation IDs:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "request_id": "req-123",
  "user_id": "user-456",
  "operation": "get_user",
  "component": "api",
  "message": "User retrieved successfully",
  "execution_time": 0.125
}
```

### 3. Performance Statistics

Get performance statistics:
```python
from middleware.performance import get_performance_statistics

stats = get_performance_statistics()
print(stats)
# {
#   "database": {
#     "total_queries": 150,
#     "avg_execution_time": 0.045,
#     "slow_queries": 3
#   },
#   "cache": {
#     "connected": true
#   }
# }
```

## Best Practices

### 1. Decorator Order

Apply decorators in this order:
```python
@with_logging("operation", "component")      # 1. Logging
@with_metrics("operation", "component")      # 2. Metrics
@with_caching(ttl=300)                      # 3. Caching
@require_authentication()                    # 4. Security
@rate_limit(100, 60)                        # 5. Rate limiting
async def your_function():
    pass
```

### 2. Error Handling

Use structured error handling:
```python
from middleware.core import with_exception_handling

@with_exception_handling()
async def safe_operation():
    try:
        return await risky_operation()
    except SpecificException as e:
        # Handle specific exceptions
        raise
    # Other exceptions are handled automatically
```

### 3. Context Management

Use context managers for complex operations:
```python
from middleware.core import operation_context

async def complex_operation():
    async with operation_context("complex_op", "business_logic"):
        # All operations within this context are logged and monitored
        step1_result = await step1()
        step2_result = await step2(step1_result)
        return step2_result
```

### 4. Security Validation

Always validate and sanitize inputs:
```python
from middleware.security import sanitize_input, validate_email

async def create_user(email: str, name: str):
    if not validate_email(email):
        raise HTTPException(status_code=400, detail="Invalid email")
    
    sanitized_name = sanitize_input(name)
    # Use sanitized_name in database operations
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```python
   # Check Redis is running
   redis-cli ping
   
   # Verify connection URL
   cache_manager = CacheManager("redis://localhost:6379")
   await cache_manager.connect()
   ```

2. **JWT Token Issues**
   ```python
   # Ensure consistent secret key
   token = generate_jwt_token(payload, "your-secret-key")
   payload = validate_jwt_token(token, "your-secret-key")
   ```

3. **Rate Limiting Too Aggressive**
   ```python
   # Adjust rate limits
   @rate_limit(limit=1000, window=60)  # 1000 requests per minute
   async def high_traffic_endpoint():
       pass
   ```

4. **Cache Not Working**
   ```python
   # Check cache key generation
   @with_caching(ttl=300, key_prefix="users")
   async def get_user(user_id: str):
       # Cache key will be: "users:hash_of_function_args"
       pass
   ```

### Debug Mode

Enable debug logging:
```python
logger = setup_structured_logging(log_level="DEBUG")
```

### Performance Tuning

1. **Cache TTL Optimization**
   ```python
   # Short TTL for frequently changing data
   @with_caching(ttl=60)  # 1 minute
   
   # Long TTL for static data
   @with_caching(ttl=3600)  # 1 hour
   ```

2. **Database Query Optimization**
   ```python
   # Monitor slow queries
   slow_queries = db_profiler.get_slow_queries(threshold=0.5)
   for query in slow_queries:
       print(f"Slow query: {query['query']} - {query['execution_time']}s")
   ```

3. **Memory Usage Monitoring**
   ```python
   @with_performance_monitoring("memory_intensive", "processing")
   async def memory_intensive_operation():
       # Memory usage is automatically tracked
       pass
   ```

## Integration Examples

### FastAPI Application

See `examples/middleware_usage.py` for a complete FastAPI application demonstrating all middleware features.

### Custom Middleware

```python
from middleware.core import create_log_context, log_operation

async def custom_middleware(request: Request, call_next):
    # Pre-processing
    context = create_log_context(
        request_id=request.headers.get("X-Request-ID"),
        operation=f"{request.method} {request.url.path}",
        component="custom"
    )
    
    log_operation(logger, context, "Custom middleware pre-processing")
    
    # Process request
    response = await call_next(request)
    
    # Post-processing
    log_operation(logger, context, "Custom middleware post-processing")
    
    return response

# Add to FastAPI app
app.middleware("http")(custom_middleware)
```

This middleware system provides a comprehensive foundation for building production-ready FastAPI applications with excellent observability, security, and performance characteristics. 