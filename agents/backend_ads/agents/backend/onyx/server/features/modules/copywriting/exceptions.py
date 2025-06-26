"""
Copywriting Exceptions Module.

Custom exceptions for the AI-powered copywriting system with detailed error handling.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import traceback


class CopywritingException(Exception):
    """Base exception for all copywriting-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code or "COPYWRITING_ERROR"
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.utcnow()
        
        # Add traceback if available
        if cause:
            self.details["cause"] = str(cause)
            self.details["traceback"] = traceback.format_exc()
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class ContentGenerationError(CopywritingException):
    """Raised when content generation fails."""
    
    def __init__(
        self,
        message: str = "Content generation failed",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if provider:
            details["provider"] = provider
        if model:
            details["model"] = model
        
        super().__init__(
            message=message,
            error_code="CONTENT_GENERATION_FAILED",
            details=details,
            **kwargs
        )


class AIProviderError(CopywritingException):
    """Raised when AI provider operations fail."""
    
    def __init__(
        self,
        message: str = "AI provider error",
        provider: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if provider:
            details["provider"] = provider
        if status_code:
            details["status_code"] = status_code
        
        super().__init__(
            message=message,
            error_code="AI_PROVIDER_ERROR",
            details=details,
            **kwargs
        )


class ContentAnalysisError(CopywritingException):
    """Raised when content analysis fails."""
    
    def __init__(
        self,
        message: str = "Content analysis failed",
        analysis_type: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if analysis_type:
            details["analysis_type"] = analysis_type
        
        super().__init__(
            message=message,
            error_code="CONTENT_ANALYSIS_FAILED",
            details=details,
            **kwargs
        )


class TemplateError(CopywritingException):
    """Raised when template operations fail."""
    
    def __init__(
        self,
        message: str = "Template error",
        template_id: Optional[str] = None,
        template_name: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if template_id:
            details["template_id"] = template_id
        if template_name:
            details["template_name"] = template_name
        
        super().__init__(
            message=message,
            error_code="TEMPLATE_ERROR",
            details=details,
            **kwargs
        )


class CacheError(CopywritingException):
    """Raised when cache operations fail."""
    
    def __init__(
        self,
        message: str = "Cache operation failed",
        operation: Optional[str] = None,
        key: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if operation:
            details["operation"] = operation
        if key:
            details["cache_key"] = key
        
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details=details,
            **kwargs
        )


class ValidationError(CopywritingException):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            **kwargs
        )


class ConfigurationError(CopywritingException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if config_key:
            details["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
            **kwargs
        )


class RateLimitError(CopywritingException):
    """Raised when rate limits are exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        window: Optional[str] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if limit:
            details["limit"] = limit
        if window:
            details["window"] = window
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
            **kwargs
        )


class TimeoutError(CopywritingException):
    """Raised when operations timeout."""
    
    def __init__(
        self,
        message: str = "Operation timed out",
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        if operation:
            details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            details=details,
            **kwargs
        )


class ContentFilterError(CopywritingException):
    """Raised when content fails filtering checks."""
    
    def __init__(
        self,
        message: str = "Content failed filtering",
        filter_type: Optional[str] = None,
        content_snippet: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if filter_type:
            details["filter_type"] = filter_type
        if content_snippet:
            # Only include first 100 chars for privacy
            details["content_snippet"] = content_snippet[:100] + "..." if len(content_snippet) > 100 else content_snippet
        
        super().__init__(
            message=message,
            error_code="CONTENT_FILTER_FAILED",
            details=details,
            **kwargs
        )


class ABTestError(CopywritingException):
    """Raised when A/B testing operations fail."""
    
    def __init__(
        self,
        message: str = "A/B test error",
        test_id: Optional[str] = None,
        variant_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if test_id:
            details["test_id"] = test_id
        if variant_id:
            details["variant_id"] = variant_id
        
        super().__init__(
            message=message,
            error_code="AB_TEST_ERROR",
            details=details,
            **kwargs
        )


class BatchProcessingError(CopywritingException):
    """Raised when batch processing fails."""
    
    def __init__(
        self,
        message: str = "Batch processing failed",
        batch_id: Optional[str] = None,
        failed_count: Optional[int] = None,
        total_count: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if batch_id:
            details["batch_id"] = batch_id
        if failed_count is not None:
            details["failed_count"] = failed_count
        if total_count is not None:
            details["total_count"] = total_count
        
        super().__init__(
            message=message,
            error_code="BATCH_PROCESSING_FAILED",
            details=details,
            **kwargs
        )


# Utility functions for exception handling

def handle_ai_provider_error(error: Exception, provider: str) -> AIProviderError:
    """Convert generic AI provider error to structured exception."""
    if hasattr(error, 'status_code'):
        status_code = error.status_code
    elif hasattr(error, 'response') and hasattr(error.response, 'status_code'):
        status_code = error.response.status_code
    else:
        status_code = None
    
    return AIProviderError(
        message=f"AI provider '{provider}' failed: {str(error)}",
        provider=provider,
        status_code=status_code,
        cause=error
    )


def handle_timeout_error(error: Exception, operation: str, timeout: float) -> TimeoutError:
    """Convert generic timeout error to structured exception."""
    return TimeoutError(
        message=f"Operation '{operation}' timed out after {timeout} seconds",
        timeout_seconds=timeout,
        operation=operation,
        cause=error
    )


def handle_validation_error(error: Exception, field: str = None) -> ValidationError:
    """Convert generic validation error to structured exception."""
    return ValidationError(
        message=f"Validation failed: {str(error)}",
        field=field,
        cause=error
    )


# Export all exceptions
__all__ = [
    # Base exception
    "CopywritingException",
    
    # Specific exceptions
    "ContentGenerationError",
    "AIProviderError",
    "ContentAnalysisError",
    "TemplateError",
    "CacheError",
    "ValidationError",
    "ConfigurationError",
    "RateLimitError",
    "TimeoutError",
    "ContentFilterError",
    "ABTestError",
    "BatchProcessingError",
    
    # Utility functions
    "handle_ai_provider_error",
    "handle_timeout_error",
    "handle_validation_error"
] 