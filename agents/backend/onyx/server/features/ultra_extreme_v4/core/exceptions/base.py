"""
🚀 ULTRA-EXTREME EXCEPTIONS V4
==============================

Ultra-extreme exception classes with:
- Hierarchical exception structure
- Detailed error information
- Error codes and messages
- Context preservation
- Logging integration
"""

import traceback
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    AI = "ai"
    OPTIMIZATION = "optimization"
    MONITORING = "monitoring"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Error context information"""
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_data: Dict[str, Any] = field(default_factory=dict)


class UltraExtremeException(Exception):
    """Base exception for ultra-extreme system"""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
        retryable: bool = False,
        **kwargs
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.context = context or ErrorContext()
        self.cause = cause
        self.retryable = retryable
        self.timestamp = datetime.utcnow()
        self.traceback = traceback.format_exc()
        
        # Additional error data
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Log the exception
        self._log_exception()
    
    def _log_exception(self):
        """Log the exception with appropriate level"""
        logger = logging.getLogger(__name__)
        
        log_data = {
            "error_code": self.error_code,
            "category": self.category.value,
            "severity": self.severity.value,
            "retryable": self.retryable,
            "timestamp": self.timestamp.isoformat(),
            "context": {
                "user_id": self.context.user_id,
                "request_id": self.context.request_id,
                "session_id": self.context.session_id,
                "endpoint": self.context.endpoint,
                "method": self.context.method,
                "ip_address": self.context.ip_address,
                "user_agent": self.context.user_agent,
                "additional_data": self.context.additional_data,
            },
        }
        
        if self.cause:
            log_data["cause"] = str(self.cause)
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"{self.message} - {log_data}")
        elif self.severity == ErrorSeverity.HIGH:
            logger.error(f"{self.message} - {log_data}")
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"{self.message} - {log_data}")
        else:
            logger.info(f"{self.message} - {log_data}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "retryable": self.retryable,
            "timestamp": self.timestamp.isoformat(),
            "context": {
                "user_id": self.context.user_id,
                "request_id": self.context.request_id,
                "session_id": self.context.session_id,
                "endpoint": self.context.endpoint,
                "method": self.context.method,
                "ip_address": self.context.ip_address,
                "user_agent": self.context.user_agent,
                "additional_data": self.context.additional_data,
            },
            "cause": str(self.cause) if self.cause else None,
            "traceback": self.traceback,
        }
    
    def __str__(self) -> str:
        """String representation of the exception"""
        return f"{self.error_code}: {self.message}"


class ValidationException(UltraExtremeException):
    """Validation error exception"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )
        self.field = field
        self.value = value


class AuthenticationException(UltraExtremeException):
    """Authentication error exception"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class AuthorizationException(UltraExtremeException):
    """Authorization error exception"""
    
    def __init__(self, message: str = "Authorization failed", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class NotFoundException(UltraExtremeException):
    """Not found error exception"""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            category=ErrorCategory.NOT_FOUND,
            severity=ErrorSeverity.LOW,
            **kwargs
        )


class ConflictException(UltraExtremeException):
    """Conflict error exception"""
    
    def __init__(self, message: str = "Resource conflict", **kwargs):
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            category=ErrorCategory.CONFLICT,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class RateLimitException(UltraExtremeException):
    """Rate limit error exception"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            retryable=True,
            **kwargs
        )
        self.retry_after = retry_after


class TimeoutException(UltraExtremeException):
    """Timeout error exception"""
    
    def __init__(self, message: str = "Operation timed out", **kwargs):
        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            retryable=True,
            **kwargs
        )


class NetworkException(UltraExtremeException):
    """Network error exception"""
    
    def __init__(self, message: str = "Network error occurred", **kwargs):
        super().__init__(
            message=message,
            error_code="NETWORK_ERROR",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            retryable=True,
            **kwargs
        )


class DatabaseException(UltraExtremeException):
    """Database error exception"""
    
    def __init__(self, message: str = "Database error occurred", **kwargs):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            retryable=True,
            **kwargs
        )


class CacheException(UltraExtremeException):
    """Cache error exception"""
    
    def __init__(self, message: str = "Cache error occurred", **kwargs):
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            category=ErrorCategory.CACHE,
            severity=ErrorSeverity.MEDIUM,
            retryable=True,
            **kwargs
        )


class AIException(UltraExtremeException):
    """AI service error exception"""
    
    def __init__(self, message: str = "AI service error occurred", **kwargs):
        super().__init__(
            message=message,
            error_code="AI_ERROR",
            category=ErrorCategory.AI,
            severity=ErrorSeverity.HIGH,
            retryable=True,
            **kwargs
        )


class OptimizationException(UltraExtremeException):
    """Optimization error exception"""
    
    def __init__(self, message: str = "Optimization error occurred", **kwargs):
        super().__init__(
            message=message,
            error_code="OPTIMIZATION_ERROR",
            category=ErrorCategory.OPTIMIZATION,
            severity=ErrorSeverity.MEDIUM,
            retryable=True,
            **kwargs
        )


class MonitoringException(UltraExtremeException):
    """Monitoring error exception"""
    
    def __init__(self, message: str = "Monitoring error occurred", **kwargs):
        super().__init__(
            message=message,
            error_code="MONITORING_ERROR",
            category=ErrorCategory.MONITORING,
            severity=ErrorSeverity.LOW,
            **kwargs
        )


class SystemException(UltraExtremeException):
    """System error exception"""
    
    def __init__(self, message: str = "System error occurred", **kwargs):
        super().__init__(
            message=message,
            error_code="SYSTEM_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            **kwargs
        )


class ConfigurationException(UltraExtremeException):
    """Configuration error exception"""
    
    def __init__(self, message: str = "Configuration error occurred", **kwargs):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            **kwargs
        )


class ServiceUnavailableException(UltraExtremeException):
    """Service unavailable error exception"""
    
    def __init__(self, message: str = "Service unavailable", **kwargs):
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            retryable=True,
            **kwargs
        )


# Exception mapping for easy lookup
EXCEPTION_MAPPING = {
    "validation": ValidationException,
    "authentication": AuthenticationException,
    "authorization": AuthorizationException,
    "not_found": NotFoundException,
    "conflict": ConflictException,
    "rate_limit": RateLimitException,
    "timeout": TimeoutException,
    "network": NetworkException,
    "database": DatabaseException,
    "cache": CacheException,
    "ai": AIException,
    "optimization": OptimizationException,
    "monitoring": MonitoringException,
    "system": SystemException,
    "configuration": ConfigurationException,
    "service_unavailable": ServiceUnavailableException,
}


def create_exception(
    category: str,
    message: str,
    error_code: Optional[str] = None,
    **kwargs
) -> UltraExtremeException:
    """Create exception by category"""
    exception_class = EXCEPTION_MAPPING.get(category.lower(), UltraExtremeException)
    
    if error_code is None:
        error_code = f"{category.upper()}_ERROR"
    
    return exception_class(message=message, error_code=error_code, **kwargs)


def handle_exception(
    exception: Exception,
    context: Optional[ErrorContext] = None
) -> UltraExtremeException:
    """Handle and convert any exception to UltraExtremeException"""
    if isinstance(exception, UltraExtremeException):
        if context:
            exception.context = context
        return exception
    
    # Convert to appropriate UltraExtremeException
    if isinstance(exception, ValueError):
        return ValidationException(
            message=str(exception),
            cause=exception,
            context=context
        )
    elif isinstance(exception, TimeoutError):
        return TimeoutException(
            message=str(exception),
            cause=exception,
            context=context
        )
    elif isinstance(exception, ConnectionError):
        return NetworkException(
            message=str(exception),
            cause=exception,
            context=context
        )
    else:
        return SystemException(
            message=str(exception),
            cause=exception,
            context=context
        ) 