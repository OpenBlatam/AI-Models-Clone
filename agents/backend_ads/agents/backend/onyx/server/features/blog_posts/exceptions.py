"""
Custom Exceptions for Blog Posts Module.

Defines specific exceptions for different types of errors in blog post management.
"""

from typing import Optional, Dict, Any


class BlogPostException(Exception):
    """Base exception for blog post related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class ContentGenerationError(BlogPostException):
    """Exception raised when content generation fails."""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.provider = provider
        if provider:
            self.details["provider"] = provider


class SEOOptimizationError(BlogPostException):
    """Exception raised when SEO optimization fails."""
    
    def __init__(self, message: str, seo_issue: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.seo_issue = seo_issue
        if seo_issue:
            self.details["seo_issue"] = seo_issue


class PublishingError(BlogPostException):
    """Exception raised when publishing fails."""
    
    def __init__(self, message: str, platform: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.platform = platform
        if platform:
            self.details["platform"] = platform


class ValidationError(BlogPostException):
    """Exception raised when validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field
        if field:
            self.details["field"] = field


class ConfigurationError(BlogPostException):
    """Exception raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        if config_key:
            self.details["config_key"] = config_key


class ServiceUnavailableError(BlogPostException):
    """Exception raised when a required service is unavailable."""
    
    def __init__(self, message: str, service: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.service = service
        if service:
            self.details["service"] = service


class RateLimitError(BlogPostException):
    """Exception raised when rate limits are exceeded."""
    
    def __init__(self, message: str, limit: Optional[int] = None, reset_time: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.limit = limit
        self.reset_time = reset_time
        if limit:
            self.details["limit"] = limit
        if reset_time:
            self.details["reset_time"] = reset_time


# Export all exceptions
__all__ = [
    "BlogPostException",
    "ContentGenerationError",
    "SEOOptimizationError", 
    "PublishingError",
    "ValidationError",
    "ConfigurationError",
    "ServiceUnavailableError",
    "RateLimitError"
] 