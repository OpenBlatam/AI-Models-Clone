# FastAPI Middleware Implementation Guide

## Overview

This guide explains how to implement comprehensive middleware for logging, error monitoring, and performance optimization in FastAPI applications. The middleware system provides a unified approach to observability, security, and performance monitoring.

## Why Use Middleware?

### Benefits of Middleware

1. **Centralized Logging**: Consistent request/response logging across all endpoints
2. **Performance Monitoring**: Real-time performance metrics and slow request detection
3. **Error Tracking**: Comprehensive error monitoring with sampling and retention
4. **Security**: Rate limiting, security headers, and access control
5. **Observability**: Prometheus metrics, health checks, and monitoring endpoints
6. **Consistency**: Standardized behavior across all applications

### Problems Solved

1. **Scattered Logging**: Inconsistent logging across different endpoints
2. **Performance Blind Spots**: No visibility into slow requests or bottlenecks
3. **Error Tracking**: Difficult to track and analyze application errors
4. **Security Gaps**: Missing rate limiting, security headers, or access controls
5. **Monitoring Complexity**: Manual setup of metrics and monitoring

## Middleware Components

### 1. LoggingMiddleware

Comprehensive request/response logging with configurable detail levels.

#### Features:
- **Request ID Generation**: Unique ID for each request
- **Structured Logging**: JSON-formatted logs with context
- **Header Sanitization**: Automatic masking of sensitive headers
- **Body Logging**: Optional request/response body logging
- **Performance Tracking**: Request duration and size metrics

#### Configuration:
```python
config = MiddlewareConfig(
    logging_enabled=True,
    log_request_body=False,  # Enable for debugging
    log_response_body=False,  # Enable for debugging
    log_headers=False,  # Enable for debugging
    sensitive_headers=["authorization", "cookie", "x-api-key"]
)
```

#### Example Output:
```json
{
    "event": "Incoming request",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "method": "POST",
    "url": "/api/v1/users",
    "client_ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "request_size": 1024
}
```

### 2. PerformanceMonitoringMiddleware

Real-time performance monitoring with Prometheus metrics.

#### Features:
- **Request Duration**: Histogram of request processing times
- **Response Size**: Tracking of response payload sizes
- **Active Requests**: Gauge of currently processing requests
- **Slow Request Detection**: Automatic detection and logging of slow requests
- **Prometheus Integration**: Standard metrics for monitoring systems

#### Metrics Collected:
- `http_requests_total`: Total request count by method/endpoint/status
- `http_request_duration_seconds`: Request duration histogram
- `http_response_size_bytes`: Response size histogram
- `http_errors_total`: Error count by type
- `http_active_requests`: Currently active requests
- `app_memory_usage_bytes`: Application memory usage
- `app_cpu_usage_percent`: Application CPU usage

#### Configuration:
```python
config = MiddlewareConfig(
    performance_monitoring_enabled=True,
    slow_request_threshold=1.0,  # 1 second
    performance_metrics_enabled=True
)
```

### 3. ErrorMonitoringMiddleware

Comprehensive error tracking with sampling and persistence.

#### Features:
- **Error Sampling**: Configurable sampling rate for high-volume applications
- **Error Categorization**: Automatic categorization by error type
- **Redis Integration**: Persistent error storage with TTL
- **Error Summaries**: Statistical summaries of error patterns
- **Traceback Capture**: Full stack traces for debugging

#### Configuration:
```python
config = MiddlewareConfig(
    error_monitoring_enabled=True,
    error_sampling_rate=0.1,  # Sample 10% of errors
    error_retention_days=30
)
```

### 4. RateLimitingMiddleware

Intelligent rate limiting with Redis and local fallback.

#### Features:
- **Redis Integration**: Distributed rate limiting across multiple instances
- **Local Fallback**: In-memory rate limiting when Redis is unavailable
- **Flexible Identification**: API key or IP-based client identification
- **Configurable Limits**: Customizable requests per time window
- **Rate Limit Headers**: Standard headers for client feedback

#### Configuration:
```python
config = MiddlewareConfig(
    rate_limiting_enabled=True,
    rate_limit_requests=100,  # 100 requests per minute
    rate_limit_window=60,  # 60 seconds
    redis_enabled=True
)
```

### 5. SecurityMiddleware

Security headers and basic protection mechanisms.

#### Features:
- **Security Headers**: Comprehensive security header injection
- **Content Security Policy**: XSS protection
- **HTTPS Enforcement**: HSTS headers
- **Frame Protection**: Clickjacking prevention
- **Content Type Protection**: MIME type sniffing prevention

#### Security Headers Added:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

## Configuration Patterns

### 1. Development Configuration

Optimized for debugging and development:

```python
from ..utils.middleware_system import create_development_middleware_config

config = create_development_middleware_config()
# Features:
# - Detailed logging (request/response bodies, headers)
# - Aggressive performance monitoring (500ms threshold)
# - Full error sampling
# - Disabled rate limiting
# - Permissive CORS
```

### 2. Production Configuration

Optimized for production performance and security:

```python
from ..utils.middleware_system import create_production_middleware_config

config = create_production_middleware_config()
# Features:
# - Minimal logging (no bodies, no headers)
# - Conservative performance monitoring (2s threshold)
# - Error sampling (10% of errors)
# - Strict rate limiting
# - Restrictive CORS
# - Trusted hosts
```

### 3. Custom Configuration

Tailored configuration for specific needs:

```python
from ..utils.middleware_system import MiddlewareConfig

config = MiddlewareConfig(
    # Logging
    logging_enabled=True,
    log_request_body=False,
    log_response_body=False,
    log_headers=True,
    sensitive_headers=["authorization", "x-api-key"],
    
    # Performance
    performance_monitoring_enabled=True,
    slow_request_threshold=1.5,
    performance_metrics_enabled=True,
    
    # Error monitoring
    error_monitoring_enabled=True,
    error_sampling_rate=0.2,
    error_retention_days=14,
    
    # Security
    security_enabled=True,
    rate_limiting_enabled=True,
    rate_limit_requests=200,
    rate_limit_window=60,
    
    # CORS
    cors_enabled=True,
    cors_origins=["https://app.example.com"],
    cors_credentials=True,
    
    # Redis
    redis_enabled=True,
    redis_url="redis://localhost:6379"
)
```

## Implementation Examples

### 1. Basic Setup

```python
from fastapi import FastAPI
from ..utils.middleware_system import MiddlewareManager, create_middleware_config

# Create configuration
config = create_middleware_config()

# Create middleware manager
middleware_manager = MiddlewareManager(config)

# Create FastAPI app
app = FastAPI(title="My API")

# Setup middleware
middleware_manager.setup_middleware(app)

# Add routes
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/metrics")
async def metrics():
    return middleware_manager.get_metrics()
```

### 2. Production Setup with Redis

```python
import redis.asyncio as redis
from ..utils.middleware_system import MiddlewareManager, create_production_middleware_config

async def create_production_app():
    # Create Redis client
    redis_client = redis.from_url("redis://localhost:6379")
    
    # Create production configuration
    config = create_production_middleware_config()
    
    # Create middleware manager
    middleware_manager = MiddlewareManager(config, redis_client)
    
    # Create FastAPI app
    app = FastAPI(title="Production API")
    
    # Setup middleware
    middleware_manager.setup_middleware(app)
    
    # Add monitoring endpoints
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    @app.get("/metrics")
    async def metrics():
        return middleware_manager.get_metrics()
    
    @app.get("/performance")
    async def performance():
        return middleware_manager.get_performance_summary()
    
    @app.get("/errors")
    async def errors():
        return middleware_manager.get_error_summary()
    
    return app
```

### 3. Development Setup with Detailed Logging

```python
from ..utils.middleware_system import MiddlewareManager, create_development_middleware_config

def create_development_app():
    # Create development configuration
    config = create_development_middleware_config()
    
    # Create middleware manager
    middleware_manager = MiddlewareManager(config)
    
    # Create FastAPI app
    app = FastAPI(title="Development API")
    
    # Setup middleware
    middleware_manager.setup_middleware(app)
    
    # Add debug endpoints
    @app.get("/debug/request-info")
    async def debug_request_info(request: Request):
        return {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_ip": request.client.host
        }
    
    @app.get("/debug/slow/{duration}")
    async def debug_slow_request(duration: float):
        await asyncio.sleep(duration)
        return {"message": f"Request took {duration} seconds"}
    
    return app
```

## Monitoring and Observability

### 1. Prometheus Metrics

The middleware automatically exposes Prometheus metrics:

```bash
# Get metrics
curl http://localhost:8000/metrics

# Example metrics output:
# http_requests_total{method="GET",endpoint="/api/users",status_code="200"} 150
# http_request_duration_seconds_bucket{method="POST",endpoint="/api/users",le="0.1"} 45
# http_errors_total{method="GET",endpoint="/api/users",error_type="HTTPException"} 3
```

### 2. Health Checks

Standard health check endpoints:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/health/ready")
async def readiness_check():
    # Add your readiness checks here
    return {"status": "ready"}

@app.get("/health/live")
async def liveness_check():
    return {"status": "alive"}
```

### 3. Performance Monitoring

Performance monitoring endpoints:

```python
@app.get("/api/v1/performance")
async def performance_summary():
    return middleware_manager.get_performance_summary()

@app.get("/api/v1/errors")
async def error_summary():
    return middleware_manager.get_error_summary()
```

## Best Practices

### 1. Configuration Management

```python
# Use environment variables for configuration
import os

config = MiddlewareConfig(
    logging_enabled=os.getenv("LOGGING_ENABLED", "true").lower() == "true",
    performance_monitoring_enabled=os.getenv("PERFORMANCE_MONITORING", "true").lower() == "true",
    rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379")
)
```

### 2. Error Handling

```python
# Custom error handling with middleware
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Middleware will automatically log this error
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Middleware will automatically log this error
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

### 3. Performance Optimization

```python
# Use middleware to identify slow endpoints
@app.get("/api/v1/slow-endpoint")
async def slow_endpoint():
    # This will be automatically detected as slow if > threshold
    await asyncio.sleep(2.0)
    return {"message": "Slow response"}

# Use middleware metrics for optimization
@app.get("/api/v1/optimization-data")
async def optimization_data():
    # Check performance metrics to identify bottlenecks
    performance_data = middleware_manager.get_performance_summary()
    return performance_data
```

### 4. Security Considerations

```python
# Use middleware for security headers
config = MiddlewareConfig(
    security_enabled=True,
    cors_enabled=True,
    cors_origins=["https://yourdomain.com"],
    trusted_hosts_enabled=True,
    trusted_hosts=["yourdomain.com", "*.yourdomain.com"]
)

# Use rate limiting for API protection
config = MiddlewareConfig(
    rate_limiting_enabled=True,
    rate_limit_requests=100,
    rate_limit_window=60
)
```

## Testing Middleware

### 1. Unit Testing

```python
import pytest
from fastapi.testclient import TestClient
from ..utils.middleware_system import MiddlewareManager, create_test_middleware_config

@pytest.fixture
def test_app():
    config = create_test_middleware_config()
    middleware_manager = MiddlewareManager(config)
    
    app = FastAPI()
    middleware_manager.setup_middleware(app)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

def test_middleware_logging(client):
    response = client.get("/test")
    assert response.status_code == 200
    # Check that request was logged (implementation specific)

def test_middleware_rate_limiting(client):
    # Make multiple requests to test rate limiting
    for _ in range(10):
        response = client.get("/test")
    
    # The 11th request should be rate limited
    response = client.get("/test")
    assert response.status_code == 429
```

### 2. Integration Testing

```python
async def test_middleware_integration():
    # Test full middleware stack
    app = create_test_app()
    client = TestClient(app)
    
    # Test normal request
    response = client.get("/test")
    assert response.status_code == 200
    
    # Test error handling
    response = client.get("/error")
    assert response.status_code == 500
    
    # Test metrics endpoint
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
```

## Deployment Considerations

### 1. Environment-Specific Configuration

```python
# config.py
import os

def get_middleware_config():
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        return create_production_middleware_config()
    elif environment == "staging":
        return create_staging_middleware_config()
    else:
        return create_development_middleware_config()
```

### 2. Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install Redis for rate limiting
RUN apt-get update && apt-get install -y redis-server

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose ports
EXPOSE 8000 6379

# Start Redis and application
CMD ["sh", "-c", "redis-server --daemonize yes && uvicorn main:app --host 0.0.0.0 --port 8000"]
```

### 3. Kubernetes Configuration

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: app
        image: fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
```

## Troubleshooting

### 1. Common Issues

**Middleware not working:**
- Check that middleware is added in correct order
- Verify configuration parameters
- Check logs for middleware initialization errors

**Performance impact:**
- Disable detailed logging in production
- Use sampling for error monitoring
- Optimize Redis connection pooling

**Rate limiting issues:**
- Check Redis connectivity
- Verify rate limit configuration
- Monitor rate limit headers in responses

### 2. Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check middleware configuration
print(config.dict())

# Test Redis connection
if config.redis_enabled:
    try:
        await redis_client.ping()
        print("Redis connection successful")
    except Exception as e:
        print(f"Redis connection failed: {e}")
```

## Conclusion

The middleware system provides a comprehensive solution for logging, error monitoring, and performance optimization in FastAPI applications. By following the patterns and best practices outlined in this guide, you can build robust, observable, and secure applications with minimal configuration overhead.

The system is designed to be:
- **Flexible**: Configurable for different environments and use cases
- **Performant**: Minimal overhead with intelligent sampling
- **Observable**: Rich metrics and logging for monitoring
- **Secure**: Built-in security features and rate limiting
- **Maintainable**: Clean separation of concerns and easy testing

Start with the basic setup and gradually add more features as your application grows and requirements evolve. 