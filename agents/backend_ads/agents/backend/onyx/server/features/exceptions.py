"""
Production Exception Handling System for Onyx Features.

Comprehensive exception hierarchy with structured error reporting,
automatic error tracking, and production-ready error responses.
"""

import traceback
import uuid
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from enum import Enum

import structlog
import sentry_sdk
from pydantic import BaseModel, Field
from fastapi import HTTPException, status
from starlette.responses import JSONResponse

# Configure structured logging
logger = structlog.get_logger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    DATABASE = "database"
    NETWORK = "network"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class ErrorCode(str, Enum):
    """Standardized error codes."""
    # Validation errors (1000-1099)
    INVALID_INPUT = "E1001"
    MISSING_REQUIRED_FIELD = "E1002"
    INVALID_FORMAT = "E1003"
    VALUE_OUT_OF_RANGE = "E1004"
    
    # Authentication errors (1100-1199)
    INVALID_CREDENTIALS = "E1101"
    TOKEN_EXPIRED = "E1102"
    TOKEN_INVALID = "E1103"
    ACCOUNT_LOCKED = "E1104"
    
    # Authorization errors (1200-1299)
    INSUFFICIENT_PERMISSIONS = "E1201"
    ACCESS_DENIED = "E1202"
    QUOTA_EXCEEDED = "E1203"
    
    # Resource errors (1300-1399)
    RESOURCE_NOT_FOUND = "E1301"
    RESOURCE_ALREADY_EXISTS = "E1302"
    RESOURCE_LOCKED = "E1303"
    RESOURCE_CORRUPTED = "E1304"
    
    # Business logic errors (1400-1499)
    BUSINESS_RULE_VIOLATION = "E1401"
    OPERATION_NOT_ALLOWED = "E1402"
    WORKFLOW_ERROR = "E1403"
    
    # External service errors (1500-1599)
    SERVICE_UNAVAILABLE = "E1501"
    SERVICE_TIMEOUT = "E1502"
    SERVICE_ERROR = "E1503"
    RATE_LIMITED = "E1504"
    
    # Database errors (1600-1699)
    DATABASE_CONNECTION_FAILED = "E1601"
    DATABASE_QUERY_FAILED = "E1602"
    DATABASE_CONSTRAINT_VIOLATION = "E1603"
    DATABASE_TIMEOUT = "E1604"
    
    # System errors (1700-1799)
    INTERNAL_ERROR = "E1701"
    CONFIGURATION_ERROR = "E1702"
    MEMORY_ERROR = "E1703"
    DISK_SPACE_ERROR = "E1704"
    
    # Network errors (1800-1899)
    NETWORK_ERROR = "E1801"
    CONNECTION_TIMEOUT = "E1802"
    DNS_RESOLUTION_FAILED = "E1803"
    
    # File processing errors (1900-1999)
    FILE_NOT_FOUND = "E1901"
    FILE_TOO_LARGE = "E1902"
    FILE_FORMAT_UNSUPPORTED = "E1903"
    FILE_CORRUPTED = "E1904"


class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: ErrorCode
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None
    suggestion: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response format."""
    error_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_code: ErrorCode
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    details: List[ErrorDetail] = Field(default_factory=list)
    user_message: Optional[str] = None
    documentation_url: Optional[str] = None
    request_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BaseOnyxException(Exception):
    """Base exception class for all Onyx-specific exceptions."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[List[ErrorDetail]] = None,
        user_message: Optional[str] = None,
        original_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.details = details or []
        self.user_message = user_message
        self.original_error = original_error
        self.context = context or {}
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc)
        
        # Log the exception
        self._log_exception()
        
        # Report to Sentry if configured
        self._report_to_sentry()
    
    def _log_exception(self):
        """Log the exception with structured logging."""
        log_data = {
            "error_id": self.error_id,
            "error_code": self.error_code.value,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "context": self.context
        }
        
        if self.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            logger.error("Critical exception occurred", **log_data, exc_info=True)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning("Exception occurred", **log_data)
        else:
            logger.info("Low severity exception", **log_data)
    
    def _report_to_sentry(self):
        """Report exception to Sentry if configured."""
        try:
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("error_code", self.error_code.value)
                scope.set_tag("category", self.category.value)
                scope.set_tag("severity", self.severity.value)
                scope.set_context("error_details", {
                    "error_id": self.error_id,
                    "context": self.context,
                    "user_message": self.user_message
                })
                
                if self.original_error:
                    sentry_sdk.capture_exception(self.original_error)
                else:
                    sentry_sdk.capture_exception(self)
        except Exception:
            # Don't let Sentry reporting break the application
            pass
    
    def to_error_response(self) -> ErrorResponse:
        """Convert exception to standardized error response."""
        return ErrorResponse(
            error_id=self.error_id,
            timestamp=self.timestamp,
            error_code=self.error_code,
            message=self.message,
            category=self.category,
            severity=self.severity,
            details=self.details,
            user_message=self.user_message
        )
    
    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        status_code = self._get_http_status_code()
        return HTTPException(
            status_code=status_code,
            detail=self.to_error_response().dict()
        )
    
    def _get_http_status_code(self) -> int:
        """Get appropriate HTTP status code for the error."""
        status_map = {
            ErrorCategory.VALIDATION: status.HTTP_400_BAD_REQUEST,
            ErrorCategory.AUTHENTICATION: status.HTTP_401_UNAUTHORIZED,
            ErrorCategory.AUTHORIZATION: status.HTTP_403_FORBIDDEN,
            ErrorCategory.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            ErrorCategory.BUSINESS_LOGIC: status.HTTP_422_UNPROCESSABLE_ENTITY,
            ErrorCategory.EXTERNAL_SERVICE: status.HTTP_502_BAD_GATEWAY,
            ErrorCategory.DATABASE: status.HTTP_503_SERVICE_UNAVAILABLE,
            ErrorCategory.NETWORK: status.HTTP_503_SERVICE_UNAVAILABLE,
            ErrorCategory.SYSTEM: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        return status_map.get(self.category, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidationException(BaseOnyxException):
    """Exception for input validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_INPUT,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )
        if field:
            self.details.append(ErrorDetail(
                code=ErrorCode.INVALID_INPUT,
                message=message,
                field=field,
                value=value
            ))


class AuthenticationException(BaseOnyxException):
    """Exception for authentication failures."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_CREDENTIALS,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.MEDIUM,
            user_message="Please check your credentials and try again",
            **kwargs
        )


class AuthorizationException(BaseOnyxException):
    """Exception for authorization failures."""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.MEDIUM,
            user_message="You don't have permission to perform this action",
            **kwargs
        )


class ResourceNotFoundException(BaseOnyxException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource_type: str, resource_id: str, **kwargs):
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            category=ErrorCategory.NOT_FOUND,
            severity=ErrorSeverity.LOW,
            user_message=f"The requested {resource_type.lower()} was not found",
            context={"resource_type": resource_type, "resource_id": resource_id},
            **kwargs
        )


class BusinessLogicException(BaseOnyxException):
    """Exception for business logic violations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.BUSINESS_RULE_VIOLATION,
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class ExternalServiceException(BaseOnyxException):
    """Exception for external service errors."""
    
    def __init__(self, service_name: str, message: str = None, **kwargs):
        message = message or f"External service '{service_name}' is unavailable"
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.HIGH,
            user_message="A required service is currently unavailable. Please try again later",
            context={"service_name": service_name},
            **kwargs
        )


class DatabaseException(BaseOnyxException):
    """Exception for database-related errors."""
    
    def __init__(self, message: str, operation: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_QUERY_FAILED,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            user_message="A database error occurred. Please try again later",
            context={"operation": operation} if operation else {},
            **kwargs
        )


class FileProcessingException(BaseOnyxException):
    """Exception for file processing errors."""
    
    def __init__(self, message: str, filename: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.FILE_FORMAT_UNSUPPORTED,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            context={"filename": filename} if filename else {},
            **kwargs
        )


class RateLimitException(BaseOnyxException):
    """Exception for rate limiting."""
    
    def __init__(self, limit: int, window: str, **kwargs):
        message = f"Rate limit exceeded: {limit} requests per {window}"
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMITED,
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            user_message=f"Too many requests. Please wait before trying again",
            context={"limit": limit, "window": window},
            **kwargs
        )


def handle_unexpected_exception(exc: Exception, context: Dict[str, Any] = None) -> BaseOnyxException:
    """
    Convert unexpected exceptions to Onyx exceptions.
    
    Args:
        exc: The unexpected exception
        context: Additional context information
        
    Returns:
        BaseOnyxException: Wrapped exception
    """
    # Map common Python exceptions to appropriate Onyx exceptions
    if isinstance(exc, ValueError):
        return ValidationException(
            message=str(exc),
            original_error=exc,
            context=context
        )
    elif isinstance(exc, FileNotFoundError):
        return ResourceNotFoundException(
            resource_type="File",
            resource_id=str(exc.filename) if hasattr(exc, 'filename') else "unknown",
            original_error=exc,
            context=context
        )
    elif isinstance(exc, PermissionError):
        return AuthorizationException(
            message=str(exc),
            original_error=exc,
            context=context
        )
    elif isinstance(exc, ConnectionError):
        return ExternalServiceException(
            service_name="external_service",
            message=str(exc),
            original_error=exc,
            context=context
        )
    else:
        # For truly unexpected exceptions
        return BaseOnyxException(
            message=f"An unexpected error occurred: {str(exc)}",
            error_code=ErrorCode.INTERNAL_ERROR,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            user_message="An unexpected error occurred. Our team has been notified",
            original_error=exc,
            context=context
        )


async def create_error_response(exc: Exception, request_id: str = None) -> JSONResponse:
    """
    Create standardized error response for API endpoints.
    
    Args:
        exc: Exception to convert
        request_id: Request ID for tracking
        
    Returns:
        JSONResponse: Standardized error response
    """
    if isinstance(exc, BaseOnyxException):
        onyx_exc = exc
    else:
        onyx_exc = handle_unexpected_exception(exc)
    
    error_response = onyx_exc.to_error_response()
    if request_id:
        error_response.request_id = request_id
    
    return JSONResponse(
        status_code=onyx_exc._get_http_status_code(),
        content=error_response.dict()
    )


# Export main components
__all__ = [
    "BaseOnyxException",
    "ValidationException",
    "AuthenticationException", 
    "AuthorizationException",
    "ResourceNotFoundException",
    "BusinessLogicException",
    "ExternalServiceException",
    "DatabaseException",
    "FileProcessingException",
    "RateLimitException",
    "ErrorCode",
    "ErrorCategory",
    "ErrorSeverity",
    "ErrorDetail",
    "ErrorResponse",
    "handle_unexpected_exception",
    "create_error_response"
]

# Initialize exception handling
logger.info("Exception handling system initialized") 