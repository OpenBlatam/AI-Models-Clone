"""
Production Exceptions Module.

Comprehensive exception handling for production applications.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import ORJSONResponse
import structlog

logger = structlog.get_logger(__name__)


class ProductionException(Exception):
    """Base exception for production systems."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "PRODUCTION_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "status_code": self.status_code
        }


class DeploymentError(ProductionException):
    """Deployment-related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code="DEPLOYMENT_ERROR",
            status_code=503,
            **kwargs
        )


class ConfigurationError(ProductionException):
    """Configuration-related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=500,
            **kwargs
        )


class PerformanceError(ProductionException):
    """Performance-related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code="PERFORMANCE_ERROR",
            status_code=503,
            **kwargs
        )


def setup_exception_handlers(app: FastAPI):
    """Setup comprehensive exception handlers."""
    
    @app.exception_handler(ProductionException)
    async def production_exception_handler(request: Request, exc: ProductionException):
        """Handle production exceptions."""
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        logger.error("Production exception occurred",
                    error_code=exc.error_code,
                    message=exc.message,
                    details=exc.details,
                    correlation_id=correlation_id,
                    path=request.url.path,
                    method=request.method)
        
        response_data = exc.to_dict()
        response_data["correlation_id"] = correlation_id
        
        return ORJSONResponse(
            status_code=exc.status_code,
            content=response_data
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        return ORJSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code,
                "correlation_id": correlation_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        logger.error("Unhandled exception occurred",
                    error=str(exc),
                    error_type=type(exc).__name__,
                    correlation_id=correlation_id,
                    path=request.url.path,
                    method=request.method)
        
        return ORJSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "correlation_id": correlation_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# Export main components
__all__ = [
    "ProductionException",
    "DeploymentError", 
    "ConfigurationError",
    "PerformanceError",
    "setup_exception_handlers"
] 