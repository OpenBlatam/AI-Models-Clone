"""
Domain Exceptions
================

Custom exceptions for the enterprise API domain.
"""

from .api_exceptions import (
    EnterpriseAPIException,
    RateLimitExceededException, 
    CircuitBreakerOpenException,
    CacheException,
    HealthCheckException
)

__all__ = [
    "EnterpriseAPIException",
    "RateLimitExceededException",
    "CircuitBreakerOpenException", 
    "CacheException",
    "HealthCheckException",
] 