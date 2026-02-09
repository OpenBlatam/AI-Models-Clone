"""
Custom exceptions for the application
"""
from typing import Any, Dict, Optional


class DocumentGeneratorException(Exception):
    """Base exception for the application."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "GENERAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(DocumentGeneratorException):
    """Validation error exception."""
    
    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )


class AuthenticationError(DocumentGeneratorException):
    """Authentication error exception."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationError(DocumentGeneratorException):
    """Authorization error exception."""
    
    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details
        )


class NotFoundError(DocumentGeneratorException):
    """Resource not found exception."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details
        )


class ConflictError(DocumentGeneratorException):
    """Resource conflict exception."""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=details
        )


class RateLimitError(DocumentGeneratorException):
    """Rate limit exceeded exception."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details
        )


class AIProviderError(DocumentGeneratorException):
    """AI provider error exception."""
    
    def __init__(
        self,
        message: str = "AI provider error",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="AI_PROVIDER_ERROR",
            status_code=502,
            details=details
        )


class CollaborationError(DocumentGeneratorException):
    """Collaboration error exception."""
    
    def __init__(
        self,
        message: str = "Collaboration error",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="COLLABORATION_ERROR",
            status_code=400,
            details=details
        )




