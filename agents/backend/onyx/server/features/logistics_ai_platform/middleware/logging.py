"""Logging middleware"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json

from utils.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response"""
        start_time = time.time()
        
        # Log request
        client_host = request.client.host if request.client else "unknown"
        request_id = getattr(request.state, "request_id", "unknown")
        
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "client_host": client_host,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": process_time,
                }
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time": process_time,
                },
                exc_info=True
            )
            raise








