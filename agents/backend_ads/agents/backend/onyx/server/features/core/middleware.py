"""
Middleware - High-Performance Request Processing.

Modular middleware stack for performance monitoring, logging,
security, and optimization features.
"""

import time
from typing import Optional
import structlog

from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse

from ..monitoring import request_count, request_duration, performance_tracker
from ..utils import generate_correlation_id
from .config import AppConfig

logger = structlog.get_logger(__name__)


async def performance_middleware(request: Request, call_next):
    """Ultra-high performance request middleware."""
    start_time = time.perf_counter()
    request_size = int(request.headers.get("content-length", 0))
    
    # Import here to avoid circular imports
    from .app_factory import get_app_state
    app_state = get_app_state()
    
    # Generate correlation ID
    correlation_id = None
    if (app_state.master_optimizer and 
        hasattr(app_state.master_optimizer, 'hashing') and
        app_state.master_optimizer.hashing):
        try:
            correlation_id = app_state.master_optimizer.hashing.fast_hash(
                f"{request.url.path}_{start_time}_{id(request)}"
            )[:16]
        except:
            correlation_id = generate_correlation_id()[:16]
    else:
        correlation_id = generate_correlation_id()[:16]
    
    # Store in request state
    request.state.correlation_id = correlation_id
    request.state.start_time = start_time
    
    # Setup structured logging context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        correlation_id=correlation_id,
        method=request.method,
        path=request.url.path,
        user_agent=request.headers.get("user-agent", "")[:100]
    )
    
    # Memory tracking
    memory_before = None
    if (app_state.master_optimizer and 
        hasattr(app_state.master_optimizer, 'core') and
        app_state.master_optimizer.core and
        hasattr(app_state.master_optimizer.core, 'memory')):
        try:
            memory_before = app_state.master_optimizer.core.memory.get_memory_usage()
        except:
            pass
    
    # Process request
    response = None
    try:
        response = await call_next(request)
        
        # Add response headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Server"] = app_state.config.app_name if app_state.config else "Onyx"
        response.headers["X-Version"] = app_state.config.version if app_state.config else "2.0.0"
        
    except Exception as e:
        logger.error("Request processing failed", 
                    error=str(e),
                    path=request.url.path,
                    method=request.method)
        
        response = ORJSONResponse(
            status_code=500,
            content={
                "error": "Internal server error", 
                "correlation_id": correlation_id,
                "timestamp": time.time()
            }
        )
        response.headers["X-Correlation-ID"] = correlation_id
    
    # Calculate metrics
    duration = time.perf_counter() - start_time
    status_code = response.status_code if response else 500
    
    # Memory delta
    memory_delta = 0
    if memory_before and app_state.master_optimizer:
        try:
            memory_after = app_state.master_optimizer.core.memory.get_memory_usage()
            memory_delta = memory_after.get("percent", 0) - memory_before.get("percent", 0)
        except:
            pass
    
    # Record metrics
    try:
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=status_code,
            feature="api"
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path,
            feature="api"
        ).observe(duration)
    except Exception as e:
        logger.warning("Metrics recording failed", error=str(e))
    
    # Add performance headers
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    response.headers["X-Request-Size"] = str(request_size)
    response.headers["X-Memory-Delta"] = f"{memory_delta:.2f}%"
    
    # Log performance
    if duration > 1.0:  # Slow request
        logger.warning("🐌 Slow request detected", 
                      duration=f"{duration:.3f}s",
                      endpoint=request.url.path,
                      method=request.method,
                      status_code=status_code)
    elif app_state.config and app_state.config.debug:
        logger.info("✅ Request completed", 
                   duration=f"{duration:.3f}s",
                   status_code=status_code)
    
    return response


async def security_middleware(request: Request, call_next):
    """Security middleware for headers and basic protection."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Remove server header
    if "server" in response.headers:
        del response.headers["server"]
    
    return response


async def cache_middleware(request: Request, call_next):
    """Intelligent caching middleware."""
    # Check if request is cacheable
    if request.method == "GET" and not request.url.query:
        # Add cache headers for static content
        response = await call_next(request)
        
        if response.status_code == 200:
            # Cache static endpoints
            if any(path in str(request.url.path) for path in ["/health", "/metrics"]):
                response.headers["Cache-Control"] = "public, max-age=60"
            elif "/api/" in str(request.url.path):
                response.headers["Cache-Control"] = "private, max-age=300"
        
        return response
    
    return await call_next(request)


def setup_middleware(app: FastAPI, config: AppConfig):
    """Setup all middleware in correct order."""
    
    # Performance middleware (first - for timing everything)
    app.middleware("http")(performance_middleware)
    
    # Security middleware
    app.middleware("http")(security_middleware)
    
    # Cache middleware (if enabled)
    if config.performance.enable_caching:
        app.middleware("http")(cache_middleware)
    
    logger.info("🔧 Middleware configured",
               caching=config.performance.enable_caching,
               compression=config.performance.enable_compression)


__all__ = [
    'setup_middleware',
    'performance_middleware',
    'security_middleware', 
    'cache_middleware'
] 