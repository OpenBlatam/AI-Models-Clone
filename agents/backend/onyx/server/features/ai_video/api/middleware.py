"""
Custom Middleware for FastAPI Application
========================================

Middleware components for logging, monitoring, and request processing.
"""

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import StreamingResponse
import time
import logging
import json
import uuid
from typing import Callable, Dict, Any
from datetime import datetime
import redis
import asyncio
from contextlib import asynccontextmanager

# Configure logging
logger = logging.getLogger(__name__)

# Redis for metrics
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request logging."""
    
    def __init__(self, app, log_requests: bool = True, log_responses: bool = True):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request start
        start_time = time.time()
        
        if self.log_requests:
            await self.log_request(request, request_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            if self.log_responses:
                await self.log_response(response, request_id, duration)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Processing-Time"] = str(duration)
            
            return response
            
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            await self.log_error(request, request_id, e, duration)
            raise
    
    async def log_request(self, request: Request, request_id: str):
        """Log incoming request details."""
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Request: {json.dumps(log_data, indent=2)}")
    
    async def log_response(self, response: Response, request_id: str, duration: float):
        """Log response details."""
        log_data = {
            "request_id": request_id,
            "status_code": response.status_code,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Response: {json.dumps(log_data, indent=2)}")
    
    async def log_error(self, request: Request, request_id: str, error: Exception, duration: float):
        """Log error details."""
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "error": str(error),
            "error_type": type(error).__name__,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.error(f"Error: {json.dumps(log_data, indent=2)}")

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting API metrics."""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Increment request counter
        await self.increment_metric("total_requests")
        
        # Track endpoint usage
        endpoint = f"{request.method}:{request.url.path}"
        await self.increment_metric(f"endpoint:{endpoint}")
        
        try:
            response = await call_next(request)
            
            # Track response status
            status_code = response.status_code
            await self.increment_metric(f"status:{status_code}")
            
            # Track successful requests
            if 200 <= status_code < 300:
                await self.increment_metric("successful_requests")
            elif 400 <= status_code < 500:
                await self.increment_metric("client_errors")
            elif 500 <= status_code < 600:
                await self.increment_metric("server_errors")
            
            return response
            
        except Exception as e:
            # Track errors
            await self.increment_metric("exceptions")
            await self.increment_metric(f"exception:{type(e).__name__}")
            raise
    
    async def increment_metric(self, metric_name: str, value: int = 1):
        """Increment metric in Redis."""
        try:
            key = f"metrics:{metric_name}"
            redis_client.incr(key, value)
            redis_client.expire(key, 86400)  # 24 hours TTL
        except Exception as e:
            logger.error(f"Error incrementing metric {metric_name}: {str(e)}")

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""
    
    def __init__(self, app, rate_limit: int = 100, window: int = 3600):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window = window
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Get client identifier
        client_id = self.get_client_id(request)
        
        # Check rate limit
        if not await self.check_rate_limit(client_id):
            return Response(
                content=json.dumps({"error": "Rate limit exceeded"}),
                status_code=429,
                media_type="application/json"
            )
        
        return await call_next(request)
    
    def get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Use IP address or user ID from token
        return request.client.host if request.client else "unknown"
    
    async def check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit."""
        key = f"rate_limit:{client_id}"
        current = redis_client.get(key)
        
        if current is None:
            redis_client.setex(key, self.window, 1)
            return True
        
        current_count = int(current)
        if current_count >= self.rate_limit:
            return False
        
        redis_client.incr(key)
        return True

class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for response caching."""
    
    def __init__(self, app, cache_ttl: int = 3600):
        super().__init__(app)
        self.cache_ttl = cache_ttl
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Generate cache key
        cache_key = self.generate_cache_key(request)
        
        # Check cache
        cached_response = await self.get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Process request
        response = await call_next(request)
        
        # Cache response if successful
        if response.status_code == 200:
            await self.cache_response(cache_key, response)
        
        return response
    
    def generate_cache_key(self, request: Request) -> str:
        """Generate cache key from request."""
        return f"cache:{request.method}:{request.url.path}:{hash(str(request.query_params))}"
    
    async def get_cached_response(self, cache_key: str) -> Response:
        """Get cached response."""
        try:
            cached = redis_client.get(cache_key)
            if cached:
                data = json.loads(cached)
                return Response(
                    content=data["content"],
                    status_code=data["status_code"],
                    headers=data["headers"],
                    media_type=data["media_type"]
                )
        except Exception as e:
            logger.error(f"Error getting cached response: {str(e)}")
        
        return None
    
    async def cache_response(self, cache_key: str, response: Response):
        """Cache response."""
        try:
            # Read response content
            if hasattr(response, 'body'):
                content = response.body.decode()
            else:
                content = ""
            
            cache_data = {
                "content": content,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "media_type": response.media_type
            }
            
            redis_client.setex(cache_key, self.cache_ttl, json.dumps(cache_data))
        except Exception as e:
            logger.error(f"Error caching response: {str(e)}")

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers."""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring."""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Track memory usage before request
        import psutil
        memory_before = psutil.virtual_memory().used
        
        try:
            response = await call_next(request)
            
            # Calculate metrics
            duration = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_delta = memory_after - memory_before
            
            # Store performance metrics
            await self.store_performance_metrics(request, duration, memory_delta)
            
            # Add performance headers
            response.headers["X-Processing-Time"] = str(duration)
            response.headers["X-Memory-Delta"] = str(memory_delta)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            await self.store_performance_metrics(request, duration, 0, error=True)
            raise
    
    async def store_performance_metrics(self, request: Request, duration: float, 
                                      memory_delta: int, error: bool = False):
        """Store performance metrics in Redis."""
        try:
            endpoint = f"{request.method}:{request.url.path}"
            metrics_key = f"performance:{endpoint}"
            
            metrics = {
                "duration": duration,
                "memory_delta": memory_delta,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in Redis with TTL
            redis_client.lpush(metrics_key, json.dumps(metrics))
            redis_client.ltrim(metrics_key, 0, 99)  # Keep last 100 entries
            redis_client.expire(metrics_key, 86400)  # 24 hours TTL
            
        except Exception as e:
            logger.error(f"Error storing performance metrics: {str(e)}")

# Middleware factory
def create_middleware_stack(app):
    """Create and configure middleware stack."""
    
    # Add custom middleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(CacheMiddleware)
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(PerformanceMiddleware)
    
    # Add standard middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure appropriately for production
    )
    
    return app 