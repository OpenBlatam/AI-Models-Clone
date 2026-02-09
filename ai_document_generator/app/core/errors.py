"""
Enhanced error handling with comprehensive error types and responses
"""
from typing import Dict, Any, Optional, Union, List
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging
import traceback
from datetime import datetime
import uuid

from app.core.logging import get_logger

logger = get_logger(__name__)


class ErrorResponse(BaseModel):
    """Standardized error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")


class ValidationErrorResponse(ErrorResponse):
    """Validation error response model."""
    field_errors: Optional[List[Dict[str, Any]]] = Field(None, description="Field-specific validation errors")


class BusinessLogicError(Exception):
    """Custom exception for business logic errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "BUSINESS_LOGIC_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ResourceNotFoundError(BusinessLogicError):
    """Exception for resource not found errors."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found",
            error_code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class PermissionDeniedError(BusinessLogicError):
    """Exception for permission denied errors."""
    
    def __init__(self, action: str, resource: str):
        super().__init__(
            message=f"Permission denied for action '{action}' on resource '{resource}'",
            error_code="PERMISSION_DENIED",
            details={"action": action, "resource": resource}
        )


class ValidationError(BusinessLogicError):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field_errors: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field_errors": field_errors or []}
        )


class ExternalServiceError(BusinessLogicError):
    """Exception for external service errors."""
    
    def __init__(self, service_name: str, message: str, status_code: Optional[int] = None):
        super().__init__(
            message=f"External service '{service_name}' error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service_name": service_name, "status_code": status_code}
        )


class RateLimitError(BusinessLogicError):
    """Exception for rate limit errors."""
    
    def __init__(self, limit: int, window: int, retry_after: Optional[int] = None):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window} seconds",
            error_code="RATE_LIMIT_EXCEEDED",
            details={"limit": limit, "window": window, "retry_after": retry_after}
        )


class DatabaseError(BusinessLogicError):
    """Exception for database errors."""
    
    def __init__(self, operation: str, message: str):
        super().__init__(
            message=f"Database {operation} failed: {message}",
            error_code="DATABASE_ERROR",
            details={"operation": operation}
        )


class AuthenticationError(BusinessLogicError):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(BusinessLogicError):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR"
        )


# Error handler functions
def create_error_response(
    error: str,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Optional[Dict[str, Any]] = None,
    code: Optional[str] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create standardized error response."""
    error_response = ErrorResponse(
        error=error,
        message=message,
        details=details,
        code=code,
        request_id=request_id
    )
    
    return HTTPException(
        status_code=status_code,
        detail=error_response.model_dump()
    )


def create_validation_error_response(
    message: str,
    field_errors: Optional[List[Dict[str, Any]]] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create validation error response."""
    error_response = ValidationErrorResponse(
        error="ValidationError",
        message=message,
        field_errors=field_errors,
        code="VALIDATION_ERROR",
        request_id=request_id
    )
    
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=error_response.model_dump()
    )


# Specific error handlers
def handle_validation_error(
    error: Union[ValidationError, Exception],
    request_id: Optional[str] = None
) -> HTTPException:
    """Handle validation errors."""
    if isinstance(error, ValidationError):
        return create_validation_error_response(
            message=error.message,
            field_errors=error.details.get("field_errors"),
            request_id=request_id
        )
    
    return create_error_response(
        error="ValidationError",
        message=str(error),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        request_id=request_id
    )


def handle_not_found_error(
    resource_type: str,
    resource_id: str,
    request_id: Optional[str] = None
) -> HTTPException:
    """Handle resource not found errors."""
    return create_error_response(
        error="NotFoundError",
        message=f"{resource_type} with ID '{resource_id}' not found",
        status_code=status.HTTP_404_NOT_FOUND,
        details={"resource_type": resource_type, "resource_id": resource_id},
        code="RESOURCE_NOT_FOUND",
        request_id=request_id
    )


def handle_permission_denied_error(
    action: str,
    resource: str,
    request_id: Optional[str] = None
) -> HTTPException:
    """Handle permission denied errors."""
    return create_error_response(
        error="PermissionDeniedError",
        message=f"Permission denied for action '{action}' on resource '{resource}'",
        status_code=status.HTTP_403_FORBIDDEN,
        details={"action": action, "resource": resource},
        code="PERMISSION_DENIED",
        request_id=request_id
    )


def handle_authentication_error(
    message: str = "Authentication failed",
    request_id: Optional[str] = None
) -> HTTPException:
    """Handle authentication errors."""
    return create_error_response(
        error="AuthenticationError",
        message=message,
        status_code=status.HTTP_401_UNAUTHORIZED,
        code="AUTHENTICATION_ERROR",
        request_id=request_id
    )


def handle_authorization_error(
    message: str = "Authorization failed",
    request_id: Optional[str] = None
) -> HTTPException:
    """Handle authorization errors."""
    return create_error_response(
        error="AuthorizationError",
        message=message,
        status_code=status.HTTP_403_FORBIDDEN,
        code="AUTHORIZATION_ERROR",
        request_id=request_id
    )


def handle_rate_limit_error(
    limit: int,
    window: int,
    retry_after: Optional[int] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Handle rate limit errors."""
    return create_error_response(
        error="RateLimitError",
        message=f"Rate limit exceeded: {limit} requests per {window} seconds",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        details={"limit": limit, "window": window, "retry_after": retry_after},
        code="RATE_LIMIT_EXCEEDED",
        request_id=request_id
    )


def handle_external_service_error(
    service_name: str,
    message: str,
    status_code: Optional[int] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Handle external service errors."""
    return create_error_response(
        error="ExternalServiceError",
        message=f"External service '{service_name}' error: {message}",
        status_code=status.HTTP_502_BAD_GATEWAY,
        details={"service_name": service_name, "status_code": status_code},
        code="EXTERNAL_SERVICE_ERROR",
        request_id=request_id
    )


def handle_database_error(
    operation: str,
    message: str,
    request_id: Optional[str] = None
) -> HTTPException:
    """Handle database errors."""
    return create_error_response(
        error="DatabaseError",
        message=f"Database {operation} failed: {message}",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"operation": operation},
        code="DATABASE_ERROR",
        request_id=request_id
    )


def handle_internal_error(
    message: str,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Handle internal server errors."""
    return create_error_response(
        error="InternalServerError",
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=details,
        code="INTERNAL_SERVER_ERROR",
        request_id=request_id
    )


def handle_business_logic_error(
    error: BusinessLogicError,
    request_id: Optional[str] = None
) -> HTTPException:
    """Handle business logic errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    
    # Map specific error types to HTTP status codes
    if isinstance(error, ResourceNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(error, PermissionDeniedError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(error, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(error, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(error, RateLimitError):
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(error, ExternalServiceError):
        status_code = status.HTTP_502_BAD_GATEWAY
    elif isinstance(error, DatabaseError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return create_error_response(
        error=error.__class__.__name__,
        message=error.message,
        status_code=status_code,
        details=error.details,
        code=error.error_code,
        request_id=request_id
    )


# Error logging utilities
def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> None:
    """Log error with context information."""
    error_id = str(uuid.uuid4())
    
    log_data = {
        "error_id": error_id,
        "error_type": error.__class__.__name__,
        "error_message": str(error),
        "request_id": request_id,
        "context": context or {},
        "timestamp": datetime.utcnow().isoformat(),
        "traceback": traceback.format_exc()
    }
    
    if isinstance(error, BusinessLogicError):
        logger.warning(f"Business logic error: {error_id}", extra=log_data)
    else:
        logger.error(f"Unexpected error: {error_id}", extra=log_data)


def create_error_log_entry(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create structured error log entry."""
    return {
        "error_id": str(uuid.uuid4()),
        "error_type": error.__class__.__name__,
        "error_message": str(error),
        "request_id": request_id,
        "context": context or {},
        "timestamp": datetime.utcnow().isoformat(),
        "traceback": traceback.format_exc()
    }


# Error response utilities
def format_error_for_client(
    error: Exception,
    include_details: bool = False,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Format error for client response."""
    if isinstance(error, BusinessLogicError):
        return {
            "error": error.__class__.__name__,
            "message": error.message,
            "code": error.error_code,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": error.details if include_details else None
        }
    
    # For unexpected errors, return generic message
    return {
        "error": "InternalServerError",
        "message": "An unexpected error occurred",
        "code": "INTERNAL_SERVER_ERROR",
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "details": {"original_error": str(error)} if include_details else None
    }


# Error recovery utilities
def is_recoverable_error(error: Exception) -> bool:
    """Check if error is recoverable."""
    recoverable_errors = (
        ExternalServiceError,
        DatabaseError,
        RateLimitError
    )
    
    return isinstance(error, recoverable_errors)


def get_retry_delay(error: Exception, attempt: int) -> int:
    """Get retry delay for recoverable errors."""
    base_delay = 1  # seconds
    
    if isinstance(error, RateLimitError):
        return error.details.get("retry_after", 60)
    elif isinstance(error, ExternalServiceError):
        return base_delay * (2 ** attempt)  # Exponential backoff
    elif isinstance(error, DatabaseError):
        return base_delay * attempt  # Linear backoff
    
    return base_delay


# Error metrics
class ErrorMetrics:
    """Error metrics tracking."""
    
    def __init__(self):
        self.error_counts = {}
        self.error_timestamps = []
    
    def record_error(self, error: Exception) -> None:
        """Record error occurrence."""
        error_type = error.__class__.__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.error_timestamps.append(datetime.utcnow())
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "error_counts": self.error_counts,
            "total_errors": sum(self.error_counts.values()),
            "recent_errors": len([
                ts for ts in self.error_timestamps
                if (datetime.utcnow() - ts).total_seconds() < 3600
            ])
        }


# Global error metrics instance
error_metrics = ErrorMetrics()