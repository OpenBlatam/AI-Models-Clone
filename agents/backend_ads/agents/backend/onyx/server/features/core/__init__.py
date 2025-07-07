"""
Core Module - Foundation for Clean Architecture

This module provides the core utilities, base classes, and interfaces
that form the foundation of the entire features system.
"""

from .config import Config, get_config
from .exceptions import (
    BaseException,
    ValidationError,
    BusinessLogicError,
    InfrastructureError,
    PresentationError
)
from .monitoring import (
    MetricsCollector,
    PerformanceTracker,
    HealthChecker,
    Logger
)
from .utils import (
    async_retry,
    cache_result,
    validate_input,
    sanitize_output,
    generate_id
)

__version__ = "2.0.0"
__author__ = "Onyx Features Team"

__all__ = [
    # Configuration
    "Config",
    "get_config",
    
    # Exceptions
    "BaseException",
    "ValidationError", 
    "BusinessLogicError",
    "InfrastructureError",
    "PresentationError",
    
    # Monitoring
    "MetricsCollector",
    "PerformanceTracker", 
    "HealthChecker",
    "Logger",
    
    # Utilities
    "async_retry",
    "cache_result",
    "validate_input",
    "sanitize_output",
    "generate_id"
] 