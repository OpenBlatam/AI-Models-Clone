#!/usr/bin/env python3
"""
🚀 Unified Error Handler - Standardized Error Handling System
============================================================

Provides consistent error handling across the entire codebase,
eliminating inconsistencies and improving error reporting.
"""

import asyncio
import functools
import inspect
import logging
import sys
import traceback
from typing import Dict, List, Any, Optional, Union, Callable, Type, TypeVar, Generic, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime
import structlog

logger = structlog.get_logger()

# =============================================================================
# Error Types and Categories
# =============================================================================

class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    INTERNAL = "internal"
    EXTERNAL = "external"
    UNKNOWN = "unknown"

class ErrorContext(Enum):
    """Error context for better understanding."""
    API_REQUEST = "api_request"
    DATABASE_OPERATION = "database_operation"
    FILE_OPERATION = "file_operation"
    NETWORK_REQUEST = "network_request"
    BACKGROUND_TASK = "background_task"
    SCHEDULED_JOB = "scheduled_job"
    USER_ACTION = "user_action"
    SYSTEM_OPERATION = "system_operation"

# =============================================================================
# Error Information
# =============================================================================

@dataclass
class ErrorInfo:
    """Detailed error information."""
    error_type: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    context: ErrorContext
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    source_file: Optional[str] = None
    source_line: Optional[int] = None
    source_function: Optional[str] = None

@dataclass
class ErrorResponse:
    """Standardized error response."""
    success: bool = False
    error: ErrorInfo
    request_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    suggestions: List[str] = field(default_factory=list)
    help_url: Optional[str] = None

# =============================================================================
# Custom Exception Classes
# =============================================================================

class BaseAppException(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, 
                 message: str,
                 category: ErrorCategory = ErrorCategory.INTERNAL,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 context: ErrorContext = ErrorContext.SYSTEM_OPERATION,
                 user_id: Optional[str] = None,
                 request_id: Optional[str] = None,
                 additional_data: Optional[Dict[str, Any]] = None):
        
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context
        self.user_id = user_id
        self.request_id = request_id
        self.additional_data = additional_data or {}
        self.timestamp = datetime.now()
        
        # Capture stack trace
        self.stack_trace = traceback.format_exc()
        
        # Capture source information
        frame = inspect.currentframe().f_back
        if frame:
            self.source_file = frame.f_code.co_filename
            self.source_line = frame.f_lineno
            self.source_function = frame.f_code.co_name
    
    def to_error_info(self) -> ErrorInfo:
        """Convert exception to ErrorInfo."""
        return ErrorInfo(
            error_type=self.__class__.__name__,
            message=self.message,
            category=self.category,
            severity=self.severity,
            context=self.context,
            timestamp=self.timestamp,
            user_id=self.user_id,
            request_id=self.request_id,
            additional_data=self.additional_data,
            stack_trace=self.stack_trace,
            source_file=self.source_file,
            source_line=self.source_line,
            source_function=self.source_function
        )
    
    def to_error_response(self, request_id: Optional[str] = None) -> ErrorResponse:
        """Convert exception to ErrorResponse."""
        return ErrorResponse(
            error=self.to_error_info(),
            request_id=request_id or self.request_id,
            timestamp=self.timestamp
        )

class ValidationError(BaseAppException):
    """Validation error."""
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(message, ErrorCategory.VALIDATION, **kwargs)
        self.field = field

class AuthenticationError(BaseAppException):
    """Authentication error."""
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, ErrorCategory.AUTHENTICATION, ErrorSeverity.HIGH, **kwargs)

class AuthorizationError(BaseAppException):
    """Authorization error."""
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, ErrorCategory.AUTHORIZATION, ErrorSeverity.HIGH, **kwargs)

class DatabaseError(BaseAppException):
    """Database operation error."""
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(message, ErrorCategory.DATABASE, **kwargs)
        self.operation = operation

class NetworkError(BaseAppException):
    """Network operation error."""
    def __init__(self, message: str, endpoint: Optional[str] = None, **kwargs):
        super().__init__(message, ErrorCategory.NETWORK, **kwargs)
        self.endpoint = endpoint

class ConfigurationError(BaseAppException):
    """Configuration error."""
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(message, ErrorCategory.CONFIGURATION, **kwargs)
        self.config_key = config_key

class ResourceError(BaseAppException):
    """Resource error (file, memory, etc.)."""
    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs):
        super().__init__(message, ErrorCategory.RESOURCE, **kwargs)
        self.resource_type = resource_type

class TimeoutError(BaseAppException):
    """Timeout error."""
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, **kwargs):
        super().__init__(message, ErrorCategory.TIMEOUT, **kwargs)
        self.timeout_seconds = timeout_seconds

class RateLimitError(BaseAppException):
    """Rate limit error."""
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, ErrorCategory.RATE_LIMIT, **kwargs)
        self.retry_after = retry_after

# =============================================================================
# Error Handler
# =============================================================================

class UnifiedErrorHandler:
    """
    🚀 Unified Error Handler - Centralized error handling system.
    
    Provides consistent error handling, logging, and response formatting
    across the entire application.
    """
    
    def __init__(self):
        self.error_history: List[ErrorInfo] = []
        self.max_history_size = 1000
        self.error_counters: Dict[str, int] = {}
        self.severity_thresholds: Dict[ErrorSeverity, int] = {
            ErrorSeverity.LOW: 100,
            ErrorSeverity.MEDIUM: 50,
            ErrorSeverity.HIGH: 10,
            ErrorSeverity.CRITICAL: 1
        }
        self.alert_handlers: List[Callable[[ErrorInfo], None]] = []
        
        # Setup default alert handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default error alert handlers."""
        # Log all errors
        self.add_alert_handler(self._log_error)
        
        # Alert on critical errors
        self.add_alert_handler(self._alert_critical_errors)
        
        # Track error metrics
        self.add_alert_handler(self._track_error_metrics)
    
    def add_alert_handler(self, handler: Callable[[ErrorInfo], None]):
        """Add an error alert handler."""
        self.alert_handlers.append(handler)
    
    def handle_error(self, 
                    error: Exception,
                    context: ErrorContext = ErrorContext.SYSTEM_OPERATION,
                    user_id: Optional[str] = None,
                    request_id: Optional[str] = None,
                    additional_data: Optional[Dict[str, Any]] = None) -> ErrorResponse:
        """Handle an error and return standardized response."""
        
        # Convert to ErrorInfo
        if isinstance(error, BaseAppException):
            error_info = error.to_error_info()
            # Override context if provided
            if context != ErrorContext.SYSTEM_OPERATION:
                error_info.context = context
            if user_id:
                error_info.user_id = user_id
            if request_id:
                error_info.request_id = request_id
            if additional_data:
                error_info.additional_data.update(additional_data)
        else:
            # Convert standard exceptions
            error_info = self._convert_standard_exception(
                error, context, user_id, request_id, additional_data
            )
        
        # Store error
        self._store_error(error_info)
        
        # Trigger alert handlers
        self._trigger_alerts(error_info)
        
        # Create response
        response = ErrorResponse(
            error=error_info,
            request_id=request_id,
            timestamp=error_info.timestamp,
            suggestions=self._generate_suggestions(error_info),
            help_url=self._get_help_url(error_info)
        )
        
        return response
    
    def _convert_standard_exception(self,
                                  error: Exception,
                                  context: ErrorContext,
                                  user_id: Optional[str],
                                  request_id: Optional[str],
                                  additional_data: Optional[Dict[str, Any]]) -> ErrorInfo:
        """Convert standard exceptions to ErrorInfo."""
        
        # Determine category and severity
        category, severity = self._classify_exception(error)
        
        # Capture stack trace
        stack_trace = traceback.format_exc()
        
        # Capture source information
        frame = inspect.currentframe().f_back
        source_file = source_line = source_function = None
        if frame:
            source_file = frame.f_code.co_filename
            source_line = frame.f_lineno
            source_function = frame.f_code.co_name
        
        return ErrorInfo(
            error_type=error.__class__.__name__,
            message=str(error),
            category=category,
            severity=severity,
            context=context,
            timestamp=datetime.now(),
            user_id=user_id,
            request_id=request_id,
            additional_data=additional_data or {},
            stack_trace=stack_trace,
            source_file=source_file,
            source_line=source_line,
            source_function=source_function
        )
    
    def _classify_exception(self, error: Exception) -> Tuple[ErrorCategory, ErrorSeverity]:
        """Classify exception by type."""
        
        error_type = type(error).__name__
        
        # Database errors
        if any(db_error in error_type.lower() for db_error in ['database', 'sql', 'connection', 'timeout']):
            return ErrorCategory.DATABASE, ErrorSeverity.HIGH
        
        # Network errors
        if any(net_error in error_type.lower() for net_error in ['connection', 'timeout', 'http', 'request']):
            return ErrorCategory.NETWORK, ErrorSeverity.MEDIUM
        
        # Validation errors
        if any(val_error in error_type.lower() for val_error in ['validation', 'value', 'type']):
            return ErrorCategory.VALIDATION, ErrorSeverity.LOW
        
        # Resource errors
        if any(res_error in error_type.lower() for res_error in ['file', 'memory', 'disk', 'resource']):
            return ErrorCategory.RESOURCE, ErrorSeverity.MEDIUM
        
        # Default classification
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
    
    def _store_error(self, error_info: ErrorInfo):
        """Store error in history."""
        self.error_history.append(error_info)
        
        # Keep history size manageable
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
        
        # Update counters
        error_key = f"{error_info.category.value}_{error_info.severity.value}"
        self.error_counters[error_key] = self.error_counters.get(error_key, 0) + 1
    
    def _trigger_alerts(self, error_info: ErrorInfo):
        """Trigger all alert handlers."""
        for handler in self.alert_handlers:
            try:
                handler(error_info)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
    
    def _log_error(self, error_info: ErrorInfo):
        """Default error logging handler."""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error_info.severity, logging.ERROR)
        
        logger.log(
            log_level,
            f"Error: {error_info.error_type} - {error_info.message}",
            extra={
                "error_category": error_info.category.value,
                "error_severity": error_info.severity.value,
                "error_context": error_info.context.value,
                "user_id": error_info.user_id,
                "request_id": error_info.request_id,
                "source_file": error_info.source_file,
                "source_line": error_info.source_line,
                "source_function": error_info.source_function,
                "additional_data": error_info.additional_data
            }
        )
    
    def _alert_critical_errors(self, error_info: ErrorInfo):
        """Alert on critical errors."""
        if error_info.severity == ErrorSeverity.CRITICAL:
            # Send critical error alerts (email, Slack, etc.)
            logger.critical(f"🚨 CRITICAL ERROR ALERT: {error_info.message}")
            
            # You can implement actual alerting here
            # self._send_email_alert(error_info)
            # self._send_slack_alert(error_info)
    
    def _track_error_metrics(self, error_info: ErrorInfo):
        """Track error metrics for monitoring."""
        # Update metrics (could send to Prometheus, etc.)
        pass
    
    def _generate_suggestions(self, error_info: ErrorInfo) -> List[str]:
        """Generate helpful suggestions based on error type."""
        suggestions = []
        
        if error_info.category == ErrorCategory.VALIDATION:
            suggestions.extend([
                "Check the input data format",
                "Verify required fields are provided",
                "Ensure data types match expected format"
            ])
        
        elif error_info.category == ErrorCategory.DATABASE:
            suggestions.extend([
                "Verify database connection",
                "Check database permissions",
                "Review SQL query syntax"
            ])
        
        elif error_info.category == ErrorCategory.NETWORK:
            suggestions.extend([
                "Check network connectivity",
                "Verify endpoint URL",
                "Check firewall settings"
            ])
        
        elif error_info.category == ErrorCategory.AUTHENTICATION:
            suggestions.extend([
                "Verify credentials",
                "Check authentication token",
                "Ensure proper authentication flow"
            ])
        
        elif error_info.category == ErrorCategory.RATE_LIMIT:
            suggestions.extend([
                "Wait before retrying",
                "Reduce request frequency",
                "Check rate limit settings"
            ])
        
        # Add general suggestions
        suggestions.extend([
            "Check application logs for more details",
            "Verify system configuration",
            "Contact support if issue persists"
        ])
        
        return suggestions
    
    def _get_help_url(self, error_info: ErrorInfo) -> Optional[str]:
        """Get help URL for the error type."""
        # You can implement a mapping of error types to help URLs
        base_url = "https://docs.example.com/errors"
        
        help_urls = {
            ErrorCategory.VALIDATION: f"{base_url}/validation",
            ErrorCategory.DATABASE: f"{base_url}/database",
            ErrorCategory.NETWORK: f"{base_url}/network",
            ErrorCategory.AUTHENTICATION: f"{base_url}/authentication",
            ErrorCategory.AUTHORIZATION: f"{base_url}/authorization",
            ErrorCategory.CONFIGURATION: f"{base_url}/configuration",
            ErrorCategory.RESOURCE: f"{base_url}/resources",
            ErrorCategory.TIMEOUT: f"{base_url}/timeouts",
            ErrorCategory.RATE_LIMIT: f"{base_url}/rate-limits"
        }
        
        return help_urls.get(error_info.category)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error handling summary."""
        return {
            "total_errors": len(self.error_history),
            "error_counters": self.error_counters,
            "recent_errors": [
                {
                    "type": e.error_type,
                    "message": e.message,
                    "category": e.category.value,
                    "severity": e.severity.value,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in self.error_history[-10:]  # Last 10 errors
            ],
            "severity_distribution": {
                severity.value: len([e for e in self.error_history if e.severity == severity])
                for severity in ErrorSeverity
            },
            "category_distribution": {
                category.value: len([e for e in self.error_history if e.category == category])
                for category in ErrorCategory
            }
        }
    
    def clear_history(self):
        """Clear error history."""
        self.error_history.clear()
        self.error_counters.clear()

# =============================================================================
# Decorators and Context Managers
# =============================================================================

def handle_errors(context: ErrorContext = ErrorContext.SYSTEM_OPERATION,
                 user_id: Optional[str] = None,
                 request_id: Optional[str] = None):
    """Decorator for automatic error handling."""
    def decorator(func):
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = get_error_handler()
                return handler.handle_error(e, context, user_id, request_id)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                handler = get_error_handler()
                return handler.handle_error(e, context, user_id, request_id)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class ErrorContextManager:
    """Context manager for error handling."""
    
    def __init__(self, 
                 context: ErrorContext,
                 user_id: Optional[str] = None,
                 request_id: Optional[str] = None):
        self.context = context
        self.user_id = user_id
        self.request_id = request_id
        self.handler = get_error_handler()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.handler.handle_error(exc_val, self.context, self.user_id, self.request_id)
        return False  # Don't suppress the exception

# =============================================================================
# Global Instance and Utilities
# =============================================================================

# Global error handler instance
_error_handler: Optional[UnifiedErrorHandler] = None

def get_error_handler() -> UnifiedErrorHandler:
    """Get or create global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = UnifiedErrorHandler()
    return _error_handler

def handle_error(error: Exception,
                context: ErrorContext = ErrorContext.SYSTEM_OPERATION,
                user_id: Optional[str] = None,
                request_id: Optional[str] = None,
                additional_data: Optional[Dict[str, Any]] = None) -> ErrorResponse:
    """Handle error using global handler."""
    return get_error_handler().handle_error(error, context, user_id, request_id, additional_data)

def get_error_summary() -> Dict[str, Any]:
    """Get error summary from global handler."""
    return get_error_handler().get_error_summary()

# =============================================================================
# FastAPI Integration
# =============================================================================

def create_fastapi_error_handler():
    """Create FastAPI error handler."""
    from fastapi import Request
    from fastapi.responses import JSONResponse
    
    async def fastapi_error_handler(request: Request, exc: Exception):
        """FastAPI global error handler."""
        handler = get_error_handler()
        
        # Extract request information
        request_id = getattr(request.state, 'request_id', None)
        user_id = getattr(request.state, 'user_id', None)
        
        # Handle the error
        error_response = handler.handle_error(
            exc,
            context=ErrorContext.API_REQUEST,
            user_id=user_id,
            request_id=request_id,
            additional_data={
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client_ip": request.client.host if request.client else None
            }
        )
        
        # Convert to FastAPI response
        status_code = {
            ErrorSeverity.LOW: 400,
            ErrorSeverity.MEDIUM: 500,
            ErrorSeverity.HIGH: 500,
            ErrorSeverity.CRITICAL: 500
        }.get(error_response.error.severity, 500)
        
        return JSONResponse(
            status_code=status_code,
            content=error_response.__dict__
        )
    
    return fastapi_error_handler

# =============================================================================
# Example Usage
# =============================================================================

def example_usage():
    """Example of how to use the unified error handler."""
    
    # Get error handler
    handler = get_error_handler()
    
    # Example 1: Handle a standard exception
    try:
        result = 1 / 0
    except Exception as e:
        response = handler.handle_error(
            e,
            context=ErrorContext.API_REQUEST,
            user_id="user123",
            request_id="req456"
        )
        print(f"Error response: {response}")
    
    # Example 2: Use decorator
    @handle_errors(ErrorContext.DATABASE_OPERATION, user_id="user123")
    def risky_function():
        raise DatabaseError("Connection failed", operation="SELECT")
    
    try:
        risky_function()
    except Exception as e:
        print(f"Caught: {e}")
    
    # Example 3: Use context manager
    with ErrorContextManager(ErrorContext.FILE_OPERATION, user_id="user123"):
        # This will raise an error
        open("nonexistent_file.txt")
    
    # Get error summary
    summary = handler.get_error_summary()
    print(f"Error summary: {summary}")

if __name__ == "__main__":
    example_usage() 