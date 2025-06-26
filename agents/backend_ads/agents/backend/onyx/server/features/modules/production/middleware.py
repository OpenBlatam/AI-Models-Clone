"""
Production Middleware Module.

High-performance middleware for production applications.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from .config import ProductionSettings

logger = structlog.get_logger(__name__)


class ProductionMiddleware(BaseHTTPMiddleware):
    """Enterprise-grade production middleware."""
    
    def __init__(self, app, config: ProductionSettings):
        super().__init__(app)
        self.config = config
        self.request_count = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with production optimizations."""
        self.request_count += 1
        start_time = time.perf_counter()
        
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())[:8]
        request.state.correlation_id = correlation_id
        request.state.start_time = start_time
        
        # Setup structured logging context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate metrics
            duration = time.perf_counter() - start_time
            
            # Add response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            response.headers["X-Server"] = self.config.app_name
            response.headers["X-Version"] = self.config.app_version
            response.headers["X-Environment"] = self.config.environment.value
            
            # Record metrics
            if hasattr(request.app.state, 'monitor'):
                monitor = request.app.state.monitor
                monitor.metrics_collector.record_request(
                    method=request.method,
                    endpoint=request.url.path,
                    status=response.status_code,
                    duration=duration
                )
            
            # Log slow requests
            if duration > 1.0:
                logger.warning("🐌 Slow request detected",
                             duration=f"{duration:.3f}s",
                             endpoint=request.url.path,
                             method=request.method,
                             status=response.status_code)
            
            return response
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.error("Request processing failed",
                        error=str(e),
                        duration=f"{duration:.3f}s",
                        endpoint=request.url.path,
                        method=request.method)
            raise


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Additional performance optimizations middleware."""
    
    def __init__(self, app, config: ProductionSettings):
        super().__init__(app)
        self.config = config
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply performance optimizations."""
        # Memory optimization check
        if self.config.enable_memory_optimization:
            import gc
            if self.request_count % self.config.gc_threshold == 0:
                gc.collect()
        
        response = await call_next(request)
        
        # Add performance headers
        if self.config.enable_compression:
            response.headers["X-Compression"] = "enabled"
        
        return response


# Export main components
__all__ = [
    "ProductionMiddleware",
    "PerformanceMiddleware"
] 