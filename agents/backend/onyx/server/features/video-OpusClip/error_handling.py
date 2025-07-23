"""
Comprehensive Error Handling for Video-OpusClip

Centralized error handling with custom exceptions, error codes, and validation.
Enhanced with proper error logging and user-friendly error messages.
"""

from enum import Enum
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
import structlog
from fastapi import HTTPException
import traceback
import time
from datetime import datetime

# Import enhanced logging
try:
    from .logging_config import EnhancedLogger, ErrorMessages, log_error_with_context
    logger = EnhancedLogger("error_handling")
except ImportError:
    logger = structlog.get_logger()

# Import error factories
try:
    from .error_factories import (
        ErrorFactory, ErrorContextManager, ErrorContext,
        create_error_context, enrich_error_with_context, get_error_summary
    )
    error_factory = ErrorFactory()
    context_manager = ErrorContextManager()
except ImportError:
    error_factory = None
    context_manager = None

# =============================================================================
# ERROR CODES
# =============================================================================

class ErrorCode(Enum):
    """Standardized error codes for the video processing system.
    
    Priority levels:
    - CRITICAL (1000-1999): System-breaking errors that require immediate attention
    - HIGH (2000-3999): Processing failures that affect user experience
    - MEDIUM (4000-5999): Resource and configuration issues
    - LOW (6000-7999): Security and validation issues
    - UNKNOWN (9000-9999): Unexpected errors
    """
    
    # CRITICAL ERRORS - System-breaking (1000-1999)
    SYSTEM_CRASH = 1001
    DATABASE_CONNECTION_LOST = 1002
    REDIS_CONNECTION_LOST = 1003
    GPU_MEMORY_EXHAUSTED = 1004
    DISK_SPACE_CRITICAL = 1005
    MODEL_LOADING_FAILED = 1006
    PIPELINE_INITIALIZATION_FAILED = 1007
    CRITICAL_SERVICE_UNAVAILABLE = 1008
    
    # HIGH PRIORITY - Processing failures (2000-2999)
    VIDEO_PROCESSING_FAILED = 2001
    LANGCHAIN_PROCESSING_FAILED = 2002
    VIRAL_ANALYSIS_FAILED = 2003
    BATCH_PROCESSING_FAILED = 2004
    CACHE_OPERATION_FAILED = 2005
    PARALLEL_PROCESSING_FAILED = 2006
    MODEL_INFERENCE_FAILED = 2007
    VIDEO_ENCODING_FAILED = 2008
    AUDIO_EXTRACTION_FAILED = 2009
    FRAME_EXTRACTION_FAILED = 2010
    
    # EXTERNAL SERVICE ERRORS (3000-3999)
    YOUTUBE_API_ERROR = 3001
    LANGCHAIN_API_ERROR = 3002
    REDIS_CONNECTION_ERROR = 3003
    DATABASE_ERROR = 3004
    FILE_STORAGE_ERROR = 3005
    EXTERNAL_API_TIMEOUT = 3006
    EXTERNAL_API_RATE_LIMIT = 3007
    EXTERNAL_SERVICE_UNAVAILABLE = 3008
    
    # RESOURCE ERRORS (4000-4999)
    INSUFFICIENT_MEMORY = 4001
    GPU_NOT_AVAILABLE = 4002
    DISK_SPACE_FULL = 4003
    RATE_LIMIT_EXCEEDED = 4004
    TIMEOUT_ERROR = 4005
    CPU_OVERLOADED = 4006
    NETWORK_BANDWIDTH_LIMITED = 4007
    TEMPORARY_RESOURCE_UNAVAILABLE = 4008
    
    # CONFIGURATION ERRORS (5000-5999)
    MISSING_CONFIG = 5001
    INVALID_CONFIG = 5002
    ENVIRONMENT_ERROR = 5003
    MODEL_CONFIG_INVALID = 5004
    API_KEY_MISSING = 5005
    ENVIRONMENT_VARIABLE_MISSING = 5006
    
    # VALIDATION ERRORS (6000-6999)
    INVALID_YOUTUBE_URL = 6001
    INVALID_LANGUAGE_CODE = 6002
    INVALID_CLIP_LENGTH = 6003
    INVALID_VIRAL_SCORE = 6004
    INVALID_CAPTION = 6005
    INVALID_VARIANT_ID = 6006
    INVALID_AUDIENCE_PROFILE = 6007
    INVALID_BATCH_SIZE = 6008
    INVALID_FILE_FORMAT = 6009
    INVALID_VIDEO_DURATION = 6010
    
    # SECURITY ERRORS (7000-7999)
    UNAUTHORIZED_ACCESS = 7001
    INVALID_TOKEN = 7002
    RATE_LIMIT_VIOLATION = 7003
    MALICIOUS_INPUT_DETECTED = 7004
    INJECTION_ATTEMPT = 7005
    EXCESSIVE_REQUESTS = 7006
    
    # UNKNOWN ERRORS (9000-9999)
    UNKNOWN_ERROR = 9001
    INTERNAL_SERVER_ERROR = 9002
    UNEXPECTED_EXCEPTION = 9003

# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class VideoProcessingError(Exception):
    """Base exception for video processing errors."""
    
    def __init__(self, message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(VideoProcessingError):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: str, value: Any = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_YOUTUBE_URL,  # Will be overridden
            details={"field": field, "value": value}
        )

class ProcessingError(VideoProcessingError):
    """Exception for processing errors."""
    
    def __init__(self, message: str, operation: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VIDEO_PROCESSING_FAILED,  # Will be overridden
            details={"operation": operation, **(details or {})}
        )

class ExternalServiceError(VideoProcessingError):
    """Exception for external service errors."""
    
    def __init__(self, message: str, service: str, status_code: Optional[int] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.YOUTUBE_API_ERROR,  # Will be overridden
            details={"service": service, "status_code": status_code}
        )

class ResourceError(VideoProcessingError):
    """Exception for resource-related errors."""
    
    def __init__(self, message: str, resource: str, available: Optional[Any] = None, required: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_MEMORY,  # Will be overridden
            details={"resource": resource, "available": available, "required": required}
        )

class CriticalSystemError(VideoProcessingError):
    """Exception for critical system failures that require immediate attention."""
    
    def __init__(self, message: str, component: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.SYSTEM_CRASH,  # Will be overridden
            details={"component": component, **(details or {})}
        )

class SecurityError(VideoProcessingError):
    """Exception for security-related errors."""
    
    def __init__(self, message: str, threat_type: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.UNAUTHORIZED_ACCESS,  # Will be overridden
            details={"threat_type": threat_type, **(details or {})}
        )

class ConfigurationError(VideoProcessingError):
    """Exception for configuration-related errors."""
    
    def __init__(self, message: str, config_key: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.MISSING_CONFIG,  # Will be overridden
            details={"config_key": config_key, **(details or {})}
        )

# =============================================================================
# ERROR RESPONSE MODEL
# =============================================================================

@dataclass
class ErrorResponse:
    """Standardized error response format."""
    
    error_code: ErrorCode
    message: str
    details: Dict[str, Any]
    timestamp: float
    request_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "details": self.details,
                "timestamp": self.timestamp,
                "request_id": self.request_id
            }
        }

# =============================================================================
# ERROR HANDLER
# =============================================================================

class ErrorHandler:
    """Centralized error handler with logging and response formatting.
    
    Prioritizes critical errors and provides different handling strategies
    based on error severity and impact. Enhanced with error factories for
    consistent error handling.
    """
    
    def __init__(self):
        try:
            self.logger = EnhancedLogger("error_handler")
        except NameError:
            self.logger = structlog.get_logger()
        self.critical_error_count = 0
        self.error_thresholds = {
            'critical': 5,  # Alert after 5 critical errors
            'high': 20,     # Alert after 20 high priority errors
            'medium': 50    # Alert after 50 medium priority errors
        }
        
        # Initialize error factory and context manager
        self.error_factory = error_factory
        self.context_manager = context_manager
    
    def handle_validation_error(self, error: ValidationError, request_id: Optional[str] = None) -> ErrorResponse:
        """Handle validation errors with user-friendly messages."""
        # Get user-friendly message
        error_code_name = error.error_code.name.lower()
        user_message = ErrorMessages.get_user_message(error_code_name, **error.details)
        suggestion = ErrorMessages.get_suggestion(error_code_name)
        
        # Log with enhanced context
        self.logger.warning(
            user_message,
            details={
                "error_code": error.error_code.value,
                "field": error.details.get("field"),
                "value": error.details.get("value"),
                "suggestion": suggestion,
                "technical_message": error.message
            }
        )
        
        return ErrorResponse(
            error_code=error.error_code,
            message=user_message,
            details={
                **error.details,
                "suggestion": suggestion,
                "help_url": f"/docs/errors/{error_code_name}"
            },
            timestamp=self._get_timestamp(),
            request_id=request_id
        )
    
    def handle_processing_error(self, error: ProcessingError, request_id: Optional[str] = None) -> ErrorResponse:
        """Handle processing errors with user-friendly messages."""
        # Get user-friendly message
        error_code_name = error.error_code.name.lower()
        user_message = ErrorMessages.get_user_message(error_code_name, **error.details)
        suggestion = ErrorMessages.get_suggestion(error_code_name)
        
        # Log with enhanced context
        self.logger.error(
            user_message,
            error=error,
            details={
                "error_code": error.error_code.value,
                "operation": error.details.get("operation"),
                "suggestion": suggestion,
                "technical_message": error.message
            }
        )
        
        return ErrorResponse(
            error_code=error.error_code,
            message=user_message,
            details={
                **error.details,
                "suggestion": suggestion,
                "help_url": f"/docs/errors/{error_code_name}",
                "retry_after": 30  # Suggest retry after 30 seconds
            },
            timestamp=self._get_timestamp(),
            request_id=request_id
        )
    
    def handle_external_service_error(self, error: ExternalServiceError, request_id: Optional[str] = None) -> ErrorResponse:
        """Handle external service errors with user-friendly messages."""
        # Get user-friendly message
        error_code_name = error.error_code.name.lower()
        user_message = ErrorMessages.get_user_message(error_code_name, **error.details)
        suggestion = ErrorMessages.get_suggestion(error_code_name)
        
        # Log with enhanced context
        self.logger.error(
            user_message,
            error=error,
            details={
                "error_code": error.error_code.value,
                "service": error.details.get("service"),
                "status_code": error.details.get("status_code"),
                "suggestion": suggestion,
                "technical_message": error.message
            }
        )
        
        return ErrorResponse(
            error_code=error.error_code,
            message=user_message,
            details={
                **error.details,
                "suggestion": suggestion,
                "help_url": f"/docs/errors/{error_code_name}",
                "retry_after": 60  # Suggest retry after 1 minute for external services
            },
            timestamp=self._get_timestamp(),
            request_id=request_id
        )
    
    def handle_resource_error(self, error: ResourceError, request_id: Optional[str] = None) -> ErrorResponse:
        """Handle resource errors with user-friendly messages."""
        # Get user-friendly message
        error_code_name = error.error_code.name.lower()
        user_message = ErrorMessages.get_user_message(error_code_name, **error.details)
        suggestion = ErrorMessages.get_suggestion(error_code_name)
        
        # Log with enhanced context
        self.logger.warning(
            user_message,
            error=error,
            details={
                "error_code": error.error_code.value,
                "resource": error.details.get("resource"),
                "available": error.details.get("available"),
                "required": error.details.get("required"),
                "suggestion": suggestion,
                "technical_message": error.message
            }
        )
        
        return ErrorResponse(
            error_code=error.error_code,
            message=user_message,
            details={
                **error.details,
                "suggestion": suggestion,
                "help_url": f"/docs/errors/{error_code_name}",
                "retry_after": 120  # Suggest retry after 2 minutes for resource issues
            },
            timestamp=self._get_timestamp(),
            request_id=request_id
        )
    
    def handle_critical_system_error(self, error: CriticalSystemError, request_id: Optional[str] = None) -> ErrorResponse:
        """Handle critical system errors with immediate alerting and user-friendly messages."""
        self.critical_error_count += 1
        
        # Get user-friendly message
        error_code_name = error.error_code.name.lower()
        user_message = ErrorMessages.get_user_message(error_code_name, **error.details)
        suggestion = ErrorMessages.get_suggestion(error_code_name)
        
        # Log with highest priority
        self.logger.critical(
            user_message,
            error=error,
            details={
                "error_code": error.error_code.value,
                "component": error.details.get("component"),
                "suggestion": suggestion,
                "technical_message": error.message,
                "critical_error_count": self.critical_error_count
            }
        )
        
        # Alert if threshold exceeded
        if self.critical_error_count >= self.error_thresholds['critical']:
            self._send_critical_alert(error, request_id)
        
        return ErrorResponse(
            error_code=error.error_code,
            message=user_message,
            details={
                **error.details,
                "suggestion": suggestion,
                "help_url": f"/docs/errors/{error_code_name}",
                "contact_support": True,  # Indicate user should contact support
                "critical": True
            },
            timestamp=self._get_timestamp(),
            request_id=request_id
        )
    
    def handle_security_error(self, error: SecurityError, request_id: Optional[str] = None) -> ErrorResponse:
        """Handle security errors with threat detection and user-friendly messages."""
        # Get user-friendly message
        error_code_name = error.error_code.name.lower()
        user_message = ErrorMessages.get_user_message(error_code_name, **error.details)
        suggestion = ErrorMessages.get_suggestion(error_code_name)
        
        # Log with security context
        self.logger.warning(
            user_message,
            error=error,
            details={
                "error_code": error.error_code.value,
                "threat_type": error.details.get("threat_type"),
                "suggestion": suggestion,
                "technical_message": error.message,
                "security_incident": True
            }
        )
        
        # Block suspicious requests
        if error.details.get("threat_type") in ["injection", "malicious_input"]:
            self._block_suspicious_ip(request_id)
        
        return ErrorResponse(
            error_code=error.error_code,
            message=user_message,
            details={
                "threat_type": error.details.get("threat_type"),
                "suggestion": suggestion,
                "help_url": f"/docs/errors/{error_code_name}",
                "security_incident": True
            },
            timestamp=self._get_timestamp(),
            request_id=request_id
        )
    
    def handle_configuration_error(self, error: ConfigurationError, request_id: Optional[str] = None) -> ErrorResponse:
        """Handle configuration errors with fallback strategies and user-friendly messages."""
        # Get user-friendly message
        error_code_name = error.error_code.name.lower()
        user_message = ErrorMessages.get_user_message(error_code_name, **error.details)
        suggestion = ErrorMessages.get_suggestion(error_code_name)
        
        # Log with configuration context
        self.logger.error(
            user_message,
            error=error,
            details={
                "error_code": error.error_code.value,
                "config_key": error.details.get("config_key"),
                "suggestion": suggestion,
                "technical_message": error.message
            }
        )
        
        # Try to use default configuration
        fallback_config = self._get_fallback_config(error.details.get("config_key"))
        if fallback_config:
            self.logger.info("Using fallback configuration", config_key=error.details.get("config_key"))
        
        return ErrorResponse(
            error_code=error.error_code,
            message=user_message,
            details={
                **error.details,
                "suggestion": suggestion,
                "help_url": f"/docs/errors/{error_code_name}",
                "contact_support": True,  # Configuration issues often need support
                "fallback_used": fallback_config is not None
            },
            timestamp=self._get_timestamp(),
            request_id=request_id
        )
    
    def handle_unknown_error(self, error: Exception, request_id: Optional[str] = None) -> ErrorResponse:
        """Handle unknown errors with enhanced debugging and user-friendly messages."""
        # Get user-friendly message
        user_message = ErrorMessages.get_user_message("unknown_error")
        suggestion = ErrorMessages.get_suggestion("unknown_error")
        
        # Check for common patterns in unknown errors
        error_pattern = self._analyze_error_pattern(error)
        
        # Enrich error with context if available
        if self.context_manager:
            enrich_error_with_context(error, self.context_manager.get_context())
        
        # Get error summary
        error_summary = get_error_summary(error) if hasattr(error, 'context') else {}
        
        # Log with enhanced debugging
        self.logger.error(
            user_message,
            error=error,
            details={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "error_pattern": error_pattern,
                "suggestion": suggestion,
                "technical_message": "An unexpected error occurred during processing",
                "stack_trace": traceback.format_exc(),
                "error_summary": error_summary
            }
        )
        
        return ErrorResponse(
            error_code=ErrorCode.UNKNOWN_ERROR,
            message=user_message,
            details={
                "error_type": type(error).__name__, 
                "original_message": str(error),
                "error_pattern": error_pattern,
                "suggestion": suggestion,
                "help_url": "/docs/errors/unknown_error",
                "contact_support": True,  # Unknown errors should be reported
                "debug_info": {
                    "error_class": type(error).__name__,
                    "error_pattern": error_pattern,
                    "error_summary": error_summary
                }
            },
            timestamp=self._get_timestamp(),
            request_id=request_id
        )
    
    def _send_critical_alert(self, error: CriticalSystemError, request_id: Optional[str] = None):
        """Send critical alert to monitoring systems."""
        try:
            # This would integrate with your alerting system (PagerDuty, Slack, etc.)
            alert_data = {
                "severity": "critical",
                "error_code": error.error_code.value,
                "component": error.details.get("component"),
                "message": error.message,
                "request_id": request_id,
                "timestamp": self._get_timestamp()
            }
            self.logger.critical("CRITICAL ALERT SENT", alert_data=alert_data)
        except Exception as e:
            self.logger.error("Failed to send critical alert", error=str(e))
    
    def _block_suspicious_ip(self, request_id: Optional[str] = None):
        """Block suspicious IP addresses."""
        try:
            # This would integrate with your security system
            self.logger.warning("Blocking suspicious IP", request_id=request_id)
        except Exception as e:
            self.logger.error("Failed to block suspicious IP", error=str(e))
    
    def _get_fallback_config(self, config_key: str) -> Optional[Dict[str, Any]]:
        """Get fallback configuration for critical settings."""
        fallback_configs = {
            "model_path": "/default/models/",
            "api_key": "default_key",
            "max_workers": 1,
            "timeout": 30
        }
        return fallback_configs.get(config_key)
    
    def _analyze_error_pattern(self, error: Exception) -> str:
        """Analyze error patterns to help with debugging."""
        error_str = str(error).lower()
        
        if "memory" in error_str or "out of memory" in error_str:
            return "memory_related"
        
        if "timeout" in error_str or "timed out" in error_str:
            return "timeout_related"
        
        if "connection" in error_str or "network" in error_str:
            return "network_related"
        
        if "permission" in error_str or "access" in error_str:
            return "permission_related"
        
        return "unknown_pattern"
    
    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time
        return time.time()
    
    def create_error_with_context(self, error_type: str, message: str, 
                                 context: Optional[ErrorContext] = None, **kwargs) -> VideoProcessingError:
        """Create an error using the error factory with context."""
        if self.error_factory:
            return self.error_factory.create_error(error_type, message, context=context, **kwargs)
        else:
            # Fallback to basic error creation
            return create_processing_error(message, error_type, context)
    
    def set_request_context(self, request_id: str, user_id: Optional[str] = None,
                           session_id: Optional[str] = None):
        """Set request context for error tracking."""
        if self.context_manager:
            self.context_manager.set_request_context(request_id, user_id, session_id)
    
    def set_operation_context(self, operation: str, component: Optional[str] = None,
                             step: Optional[str] = None):
        """Set operation context for error tracking."""
        if self.context_manager:
            self.context_manager.set_operation_context(operation, component, step)
    
    def start_error_tracking(self):
        """Start error tracking for current operation."""
        if self.context_manager:
            self.context_manager.start_timing()
    
    def end_error_tracking(self):
        """End error tracking for current operation."""
        if self.context_manager:
            self.context_manager.end_timing()
    
    def get_error_context(self) -> Optional[ErrorContext]:
        """Get current error context."""
        if self.context_manager:
            return self.context_manager.get_context()
        return None
    
    def handle_custom_error(self, error: VideoProcessingError, request_id: Optional[str] = None) -> ErrorResponse:
        """Handle custom error types with enhanced context."""
        # Get user-friendly message based on error category
        error_category = getattr(error, 'category', None)
        if error_category:
            error_code_name = f"{error_category.value}_error"
        else:
            error_code_name = "unknown_error"
        
        user_message = ErrorMessages.get_user_message(error_code_name)
        suggestion = ErrorMessages.get_suggestion(error_code_name)
        
        # Log with enhanced context
        self.logger.error(
            user_message,
            error=error,
            details={
                "error_type": type(error).__name__,
                "error_category": error_category.value if error_category else None,
                "suggestion": suggestion,
                "technical_message": error.message,
                "context": error.context.to_dict() if hasattr(error, 'context') and error.context else None
            }
        )
        
        return ErrorResponse(
            error_code=getattr(error, 'error_code', ErrorCode.UNKNOWN_ERROR),
            message=user_message,
            details={
                **error.details,
                "suggestion": suggestion,
                "help_url": f"/docs/errors/{error_code_name}",
                "error_category": error_category.value if error_category else None,
                "context": error.context.to_dict() if hasattr(error, 'context') and error.context else None
            },
            timestamp=self._get_timestamp(),
            request_id=request_id
        )

# =============================================================================
# VALIDATION DECORATORS
# =============================================================================

def validate_request(func):
    """Decorator to validate request parameters."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            error_handler = ErrorHandler()
            error_response = error_handler.handle_validation_error(e)
            raise HTTPException(status_code=400, detail=error_response.to_dict())
        except Exception as e:
            error_handler = ErrorHandler()
            error_response = error_handler.handle_unknown_error(e)
            raise HTTPException(status_code=500, detail=error_response.to_dict())
    return wrapper

def handle_processing_errors(func):
    """Decorator to handle processing errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ProcessingError as e:
            error_handler = ErrorHandler()
            error_response = error_handler.handle_processing_error(e)
            raise HTTPException(status_code=422, detail=error_response.to_dict())
        except ExternalServiceError as e:
            error_handler = ErrorHandler()
            error_response = error_handler.handle_external_service_error(e)
            raise HTTPException(status_code=503, detail=error_response.to_dict())
        except ResourceError as e:
            error_handler = ErrorHandler()
            error_response = error_handler.handle_resource_error(e)
            raise HTTPException(status_code=507, detail=error_response.to_dict())
        except Exception as e:
            error_handler = ErrorHandler()
            error_response = error_handler.handle_unknown_error(e)
            raise HTTPException(status_code=500, detail=error_response.to_dict())
    return wrapper

# =============================================================================
# GLOBAL ERROR HANDLER INSTANCE
# =============================================================================

error_handler = ErrorHandler()

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_validation_error(message: str, field: str, value: Any = None, error_code: ErrorCode = ErrorCode.INVALID_YOUTUBE_URL) -> ValidationError:
    """Create a validation error with proper error code mapping."""
    error = ValidationError(message, field, value)
    error.error_code = error_code
    return error

def create_processing_error(message: str, operation: str, error_code: ErrorCode = ErrorCode.VIDEO_PROCESSING_FAILED) -> ProcessingError:
    """Create a processing error with proper error code mapping."""
    error = ProcessingError(message, operation)
    error.error_code = error_code
    return error

def create_external_service_error(message: str, service: str, error_code: ErrorCode = ErrorCode.YOUTUBE_API_ERROR) -> ExternalServiceError:
    """Create an external service error with proper error code mapping."""
    error = ExternalServiceError(message, service)
    error.error_code = error_code
    return error

def create_resource_error(message: str, resource: str, error_code: ErrorCode = ErrorCode.INSUFFICIENT_MEMORY) -> ResourceError:
    """Create a resource error with proper error code mapping."""
    error = ResourceError(message, resource)
    error.error_code = error_code
    return error

def create_critical_system_error(message: str, component: str, error_code: ErrorCode = ErrorCode.SYSTEM_CRASH) -> CriticalSystemError:
    """Create a critical system error with proper error code mapping."""
    error = CriticalSystemError(message, component)
    error.error_code = error_code
    return error

def create_security_error(message: str, threat_type: str, error_code: ErrorCode = ErrorCode.UNAUTHORIZED_ACCESS) -> SecurityError:
    """Create a security error with proper error code mapping."""
    error = SecurityError(message, threat_type)
    error.error_code = error_code
    return error

def create_configuration_error(message: str, config_key: str, error_code: ErrorCode = ErrorCode.MISSING_CONFIG) -> ConfigurationError:
    """Create a configuration error with proper error code mapping."""
    error = ConfigurationError(message, config_key)
    error.error_code = error_code
    return error 