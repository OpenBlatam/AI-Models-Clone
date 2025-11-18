"""Performance monitoring middleware"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from utils.logger import logger


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring"""
    
    async def dispatch(self, request: Request, call_next):
        """Process request with performance tracking"""
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate metrics
        process_time = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")
        
        # Log slow requests
        if process_time > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} took {process_time:.4f}s",
                extra={
                    "method": request.method,
                    "path": str(request.url.path),
                    "process_time": process_time,
                    "status_code": response.status_code
                }
            )
        
        return response








