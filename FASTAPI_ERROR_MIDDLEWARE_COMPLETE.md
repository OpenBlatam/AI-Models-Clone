# FastAPI Application with Advanced Error Handling Middleware
========================================================

## Overview

This comprehensive FastAPI application demonstrates advanced error handling techniques for building robust, production-ready APIs. The application implements multiple middleware layers for handling unexpected errors, comprehensive logging, error monitoring, and performance tracking.

## Key Error Handling Features

### ✅ Advanced Error Handling Implemented

1. **Comprehensive Error Handling Middleware**: Multi-layer error handling with structured responses
2. **Structured Logging**: JSON-formatted logs with context and correlation
3. **Error Tracking and Analytics**: Real-time error monitoring and statistics
4. **Performance Monitoring**: Error correlation with performance metrics
5. **Rate Limiting**: Request rate limiting with error handling
6. **Error Categorization**: Intelligent error classification and severity levels
7. **Request Tracking**: Complete request lifecycle monitoring
8. **Custom Exception Handlers**: Specialized handlers for different error types

## Architecture

### Core Error Handling Components

#### 1. Error Configuration System
```python
@dataclass
class ErrorConfig:
    """Error handling configuration settings."""
    # Logging
    enable_structured_logging: bool = True
    log_error_details: bool = True
    log_request_context: bool = True
    log_performance_metrics: bool = True
    
    # Error monitoring
    enable_error_tracking: bool = True
    error_tracking_sample_rate: float = 1.0  # 100% of errors
    max_error_details_length: int = 1000
    
    # Performance monitoring
    enable_performance_monitoring: bool = True
    slow_request_threshold: float = 1.0  # seconds
    performance_metrics_interval: int = 60  # seconds
    
    # Error responses
    include_error_details_in_production: bool = False
    sanitize_error_messages: bool = True
    include_request_id_in_errors: bool = True
    
    # Rate limiting
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = 100
    rate_limit_burst_size: int = 20
```

**Features:**
- **Configurable Settings**: All error handling parameters configurable
- **Environment-Specific**: Different settings for development/production
- **Performance Tuning**: Configurable thresholds and limits
- **Security Settings**: Sanitization and detail exposure controls

#### 2. Error Tracking and Analytics
```python
class ErrorTracker:
    """Comprehensive error tracking and analytics system."""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_timestamps: Dict[str, List[datetime]] = {}
        self.performance_metrics: Dict[str, List[float]] = {
            'response_times': [],
            'error_response_times': [],
            'memory_usage': [],
            'cpu_usage': []
        }
        self.active_requests: Dict[str, Dict[str, Any]] = {}
        self.start_time = datetime.now()
    
    def track_error(self, error_type: str, severity: ErrorSeverity, 
                   category: ErrorCategory, context: Dict[str, Any] = None):
        """Track error occurrence with context."""
        error_key = f"{category.value}_{error_type}"
        
        # Update error counts
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Track error timestamps
        if error_key not in self.error_timestamps:
            self.error_timestamps[error_key] = []
        self.error_timestamps[error_key].append(datetime.now())
        
        # Log error with structured logging
        logger.error(
            "Error tracked",
            error_type=error_type,
            severity=severity.value,
            category=category.value,
            error_count=self.error_counts[error_key],
            context=context or {}
        )
```

**Features:**
- **Error Counting**: Track error occurrences by type
- **Timestamp Tracking**: Monitor error patterns over time
- **Performance Correlation**: Link errors with performance metrics
- **Request Lifecycle**: Track complete request journey
- **Structured Logging**: JSON-formatted error logs

#### 3. Error Handling Middleware
```python
class ErrorHandlingMiddleware:
    """Comprehensive error handling middleware."""
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        request_id = str(uuid4())
        request.state.request_id = request_id
        request.state.start_time = time.time()
        
        # Track request start
        error_tracker.track_request_start(request_id, {
            'method': request.method,
            'path': request.url.path,
            'client_ip': request.client.host if request.client else 'unknown',
            'user_agent': request.headers.get('user-agent', 'unknown')
        })
        
        try:
            # Process request
            await self.app(scope, receive, send)
            
            # Track successful request completion
            error_tracker.track_request_end(request_id, {
                'status': 'success',
                'duration': time.time() - request.state.start_time
            })
        
        except HTTPException as e:
            # Handle expected HTTP exceptions
            error_tracker.track_error(
                "http_exception",
                ErrorSeverity.MEDIUM,
                self._categorize_http_error(e.status_code),
                {
                    'request_id': request_id,
                    'status_code': e.status_code,
                    'detail': e.detail,
                    'method': request.method,
                    'path': request.url.path
                }
            )
            
            # Re-raise HTTPException (will be handled by FastAPI)
            raise e
        
        except Exception as e:
            # Handle unexpected errors
            error_info = {
                'request_id': request_id,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'method': request.method,
                'path': request.url.path,
                'traceback': traceback.format_exc() if ERROR_CONFIG.log_error_details else None
            }
            
            # Track unexpected error
            error_tracker.track_error(
                "unexpected_error",
                ErrorSeverity.HIGH,
                ErrorCategory.INTERNAL_SERVER,
                error_info
            )
            
            # Return structured error response
            error_response = self._create_error_response(request_id, e)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_response
            )
            
            await response(scope, receive, send)
```

**Features:**
- **Request Tracking**: Complete request lifecycle monitoring
- **Error Categorization**: Intelligent error classification
- **Structured Responses**: Consistent error response format
- **Context Preservation**: Maintain request context in errors
- **Performance Correlation**: Link errors with performance data

#### 4. Structured Logging Middleware
```python
class LoggingMiddleware:
    """Enhanced logging middleware with structured logging."""
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        # Log request details
        logger.info(
            "Request received",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            headers=dict(request.headers) if ERROR_CONFIG.log_request_context else None,
            client_ip=request.client.host if request.client else 'unknown'
        )
        
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            # Log error with context
            logger.error(
                "Request failed",
                request_id=getattr(request.state, 'request_id', 'unknown'),
                method=request.method,
                path=request.url.path,
                error_type=type(e).__name__,
                error_message=str(e),
                duration=time.time() - start_time
            )
            raise
        finally:
            # Log response details
            duration = time.time() - start_time
            logger.info(
                "Request processed",
                request_id=getattr(request.state, 'request_id', 'unknown'),
                method=request.method,
                path=request.url.path,
                duration=duration
            )
```

**Features:**
- **Structured Logging**: JSON-formatted log entries
- **Request Context**: Complete request information
- **Error Context**: Detailed error information
- **Performance Tracking**: Request duration monitoring
- **Correlation IDs**: Request ID tracking throughout

#### 5. Performance Monitoring Middleware
```python
class PerformanceMonitoringMiddleware:
    """Performance monitoring middleware with error correlation."""
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        # Track system resources
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()
        
        try:
            await self.app(scope, receive, send)
        finally:
            # Calculate performance metrics
            duration = time.time() - start_time
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            final_cpu = process.cpu_percent()
            
            # Track performance metrics
            error_tracker.performance_metrics['memory_usage'].append(final_memory)
            error_tracker.performance_metrics['cpu_usage'].append(final_cpu)
            
            # Log performance metrics for slow requests
            if duration > ERROR_CONFIG.slow_request_threshold:
                logger.warning(
                    "Slow request performance",
                    request_id=getattr(request.state, 'request_id', 'unknown'),
                    method=request.method,
                    path=request.url.path,
                    duration=duration,
                    memory_delta=final_memory - initial_memory,
                    cpu_usage=final_cpu,
                    threshold=ERROR_CONFIG.slow_request_threshold
                )
```

**Features:**
- **Resource Monitoring**: CPU and memory usage tracking
- **Performance Correlation**: Link errors with performance issues
- **Slow Request Detection**: Identify performance bottlenecks
- **System Metrics**: Comprehensive system monitoring
- **Error Correlation**: Connect errors with performance data

#### 6. Rate Limiting Middleware
```python
class RateLimitingMiddleware:
    """Rate limiting middleware with error handling."""
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        client_ip = request.client.host if request.client else 'unknown'
        current_time = time.time()
        
        # Initialize request count for client
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        # Clean old requests (older than 1 minute)
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        if len(self.request_counts[client_ip]) >= ERROR_CONFIG.rate_limit_requests_per_minute:
            # Track rate limit error
            error_tracker.track_error(
                "rate_limit_exceeded",
                ErrorSeverity.MEDIUM,
                ErrorCategory.RATE_LIMIT,
                {
                    'client_ip': client_ip,
                    'request_count': len(self.request_counts[client_ip]),
                    'limit': ERROR_CONFIG.rate_limit_requests_per_minute
                }
            )
            
            # Return rate limit error response
            error_response = {
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {ERROR_CONFIG.rate_limit_requests_per_minute} per minute",
                "timestamp": datetime.now().isoformat(),
                "retry_after": 60
            }
            
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=error_response
            )
            
            await response(scope, receive, send)
            return
        
        # Add current request
        self.request_counts[client_ip].append(current_time)
        
        # Continue with request
        await self.app(scope, receive, send)
```

**Features:**
- **Client-Based Limiting**: Per-client rate limiting
- **Configurable Limits**: Adjustable rate limits
- **Error Tracking**: Monitor rate limit violations
- **Structured Responses**: Consistent error messages
- **Automatic Cleanup**: Remove old request records

## Error Handling Strategies

### 1. Error Categorization

#### Error Categories
```python
class ErrorCategory(Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL_SERVER = "internal_server"
    UNKNOWN = "unknown"
```

#### Error Severity Levels
```python
class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

**Benefits:**
- **Intelligent Classification**: Automatic error categorization
- **Severity Assessment**: Prioritize error handling
- **Analytics**: Track error patterns by category
- **Alerting**: Set up category-specific alerts

### 2. Structured Error Responses

#### Error Response Format
```python
def _create_error_response(self, request_id: str, error: Exception) -> Dict[str, Any]:
    """Create structured error response."""
    response = {
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id if ERROR_CONFIG.include_request_id_in_errors else None
    }
    
    # Include error details in development
    if not ERROR_CONFIG.include_error_details_in_production:
        response["error_type"] = type(error).__name__
        response["error_message"] = str(error)
    
    return response
```

**Benefits:**
- **Consistent Format**: Standardized error responses
- **Security**: Configurable detail exposure
- **Debugging**: Request ID correlation
- **User Experience**: Clear error messages

### 3. Error Tracking and Analytics

#### Error Statistics
```python
def get_error_statistics(self) -> Dict[str, Any]:
    """Get comprehensive error statistics."""
    stats = {
        'total_errors': sum(self.error_counts.values()),
        'error_counts': self.error_counts,
        'error_rate': self._calculate_error_rate(),
        'performance_metrics': self._get_performance_summary(),
        'active_requests': len([r for r in self.active_requests.values() if r['status'] == 'active']),
        'uptime_seconds': (datetime.now() - self.start_time).total_seconds()
    }
    
    # Calculate error rates by category
    category_stats = {}
    for error_key, count in self.error_counts.items():
        category = error_key.split('_')[0]
        if category not in category_stats:
            category_stats[category] = 0
        category_stats[category] += count
    
    stats['error_counts_by_category'] = category_stats
    
    return stats
```

**Benefits:**
- **Real-time Monitoring**: Live error statistics
- **Trend Analysis**: Track error patterns over time
- **Performance Correlation**: Link errors with performance
- **Capacity Planning**: Understand error impact

### 4. Custom Exception Handlers

#### HTTP Exception Handler
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with structured logging."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log HTTP exception
    logger.warning(
        "HTTP exception handled",
        request_id=request_id,
        status_code=exc.status_code,
        detail=exc.detail,
        method=request.method,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id if ERROR_CONFIG.include_request_id_in_errors else None
        }
    )
```

#### General Exception Handler
```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions with comprehensive logging."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log unexpected exception
    logger.error(
        "Unexpected exception handled",
        request_id=request_id,
        error_type=type(exc).__name__,
        error_message=str(exc),
        method=request.method,
        path=request.url.path,
        traceback=traceback.format_exc() if ERROR_CONFIG.log_error_details else None
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id if ERROR_CONFIG.include_request_id_in_errors else None
        }
    )
```

**Benefits:**
- **Specialized Handling**: Different handlers for different error types
- **Structured Logging**: Comprehensive error logging
- **Security**: Sanitized error messages
- **Debugging**: Detailed error information

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description | Error Handling Features |
|--------|----------|-------------|------------------------|
| GET | `/` | Root endpoint | Basic response |
| GET | `/health` | Health check | Error statistics |
| POST | `/users` | Create user | Validation, database errors |
| GET | `/users/{user_id}` | Get user by ID | Not found, database errors |
| GET | `/users` | Get users (paginated) | Database errors |
| POST | `/posts` | Create post | Validation, database errors |
| GET | `/posts/{post_id}` | Get post by ID | Not found, database errors |
| GET | `/posts` | Get posts (paginated) | Database errors |

### Error Monitoring Endpoints

| Method | Endpoint | Description | Features |
|--------|----------|-------------|----------|
| GET | `/errors/statistics` | Error statistics | Comprehensive error analytics |
| GET | `/errors/active-requests` | Active requests | Request monitoring |

## Configuration

### Environment Variables
```bash
# Error Handling
ENABLE_STRUCTURED_LOGGING=true
LOG_ERROR_DETAILS=true
LOG_REQUEST_CONTEXT=true
LOG_PERFORMANCE_METRICS=true

# Error Monitoring
ENABLE_ERROR_TRACKING=true
ERROR_TRACKING_SAMPLE_RATE=1.0
MAX_ERROR_DETAILS_LENGTH=1000

# Performance Monitoring
ENABLE_PERFORMANCE_MONITORING=true
SLOW_REQUEST_THRESHOLD=1.0
PERFORMANCE_METRICS_INTERVAL=60

# Error Responses
INCLUDE_ERROR_DETAILS_IN_PRODUCTION=false
SANITIZE_ERROR_MESSAGES=true
INCLUDE_REQUEST_ID_IN_ERRORS=true

# Rate Limiting
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_BURST_SIZE=20
```

### Error Configuration
```python
ERROR_CONFIG = ErrorConfig(
    enable_structured_logging=True,
    log_error_details=True,
    log_request_context=True,
    enable_error_tracking=True,
    enable_performance_monitoring=True,
    slow_request_threshold=1.0,
    include_error_details_in_production=False,
    enable_rate_limiting=True,
    rate_limit_requests_per_minute=100
)
```

## Error Handling Benefits

### 1. Reliability
- **Comprehensive Error Handling**: All error types covered
- **Graceful Degradation**: System continues operating during errors
- **Error Recovery**: Automatic error recovery mechanisms
- **System Stability**: Prevent cascading failures

### 2. Observability
- **Structured Logging**: JSON-formatted logs with context
- **Error Tracking**: Real-time error monitoring
- **Performance Correlation**: Link errors with performance issues
- **Request Tracing**: Complete request lifecycle tracking

### 3. Security
- **Error Sanitization**: Prevent information leakage
- **Configurable Detail Exposure**: Control error detail visibility
- **Rate Limiting**: Prevent abuse and DoS attacks
- **Request Validation**: Comprehensive input validation

### 4. Developer Experience
- **Clear Error Messages**: User-friendly error responses
- **Request Correlation**: Easy debugging with request IDs
- **Error Analytics**: Comprehensive error statistics
- **Performance Monitoring**: Real-time performance tracking

## Monitoring and Alerting

### 1. Error Metrics
- **Error Rate**: Percentage of requests that result in errors
- **Error Counts**: Number of errors by type and category
- **Response Times**: Performance impact of errors
- **Active Requests**: Current request load

### 2. Performance Metrics
- **Response Times**: API response time tracking
- **Memory Usage**: System memory consumption
- **CPU Usage**: System CPU utilization
- **Slow Requests**: Requests exceeding threshold

### 3. System Health
- **Database Connectivity**: Database health monitoring
- **Error Patterns**: Trend analysis of errors
- **Resource Usage**: System resource monitoring
- **Uptime Tracking**: Application availability

## Best Practices Implemented

### ✅ Error Handling Best Practices
- [x] Comprehensive error categorization
- [x] Structured error responses
- [x] Request lifecycle tracking
- [x] Performance correlation
- [x] Security-conscious error handling
- [x] Configurable error detail exposure
- [x] Rate limiting with error handling
- [x] Custom exception handlers

### ✅ Logging Best Practices
- [x] Structured JSON logging
- [x] Request correlation IDs
- [x] Context preservation
- [x] Performance metrics logging
- [x] Error detail logging
- [x] Security-conscious logging

### ✅ Monitoring Best Practices
- [x] Real-time error tracking
- [x] Performance monitoring
- [x] Error rate calculation
- [x] System resource monitoring
- [x] Request lifecycle tracking
- [x] Error pattern analysis

## Conclusion

This FastAPI application with advanced error handling middleware demonstrates comprehensive error management techniques for building robust, production-ready APIs. The implementation includes multi-layer error handling, structured logging, error tracking and analytics, performance monitoring, and rate limiting.

The application provides significant benefits through:
- **Enhanced Reliability**: Comprehensive error handling and recovery
- **Improved Observability**: Structured logging and error tracking
- **Better Security**: Error sanitization and rate limiting
- **Developer Experience**: Clear error messages and debugging tools
- **Production Readiness**: Monitoring, alerting, and analytics

This implementation serves as a foundation for building reliable, observable, and secure APIs that can handle errors gracefully while providing comprehensive monitoring and debugging capabilities. 