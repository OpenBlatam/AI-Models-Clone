"""
API Middleware for Enhanced Blaze AI.

This module provides middleware components for request processing.
"""

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional
import logging
import time
import uuid

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request details."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request start
        start_time = time.time()
        logger.info(f"Request started: {request.method} {request.url.path} [ID: {request_id}]")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log request completion
            process_time = time.time() - start_time
            logger.info(f"Request completed: {request.method} {request.url.path} [ID: {request_id}] - {response.status_code} ({process_time:.3f}s)")
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log request error
            process_time = time.time() - start_time
            logger.error(f"Request failed: {request.method} {request.url.path} [ID: {request_id}] - Error: {e} ({process_time:.3f}s)")
            raise

def create_middleware_stack() -> list:
    """Create the middleware stack for the application."""
    return [
        RequestLoggingMiddleware
    ]
