"""
Middleware Module for Instagram Captions API v14.0

This module provides comprehensive middleware for:
- Request/response logging with structured data
- Performance monitoring and metrics collection
- Error tracking and monitoring
- Security validation and threat detection
- Response optimization and caching
- Error recovery and graceful degradation
"""

from .performance_middleware import (
    RequestLoggingMiddleware,
    PerformanceMonitoringMiddleware,
    SecurityMiddleware,
    ErrorHandlingMiddleware,
    CompressionMiddleware,
    CacheMiddleware,
    create_middleware_stack,
    middleware_performance_context
)

from .error_monitoring_middleware import (
    ErrorMonitoringMiddleware,
    ErrorRecoveryMiddleware,
    ErrorMonitor,
    ErrorCategory,
    ErrorPriority,
    ErrorRecord,
    get_error_monitor,
    log_error_with_context
)

__all__ = [
    # Performance middleware
    "RequestLoggingMiddleware",
    "PerformanceMonitoringMiddleware", 
    "SecurityMiddleware",
    "ErrorHandlingMiddleware",
    "CompressionMiddleware",
    "CacheMiddleware",
    "create_middleware_stack",
    "middleware_performance_context",
    
    # Error monitoring middleware
    "ErrorMonitoringMiddleware",
    "ErrorRecoveryMiddleware",
    "ErrorMonitor",
    "ErrorCategory",
    "ErrorPriority",
    "ErrorRecord",
    "get_error_monitor",
    "log_error_with_context"
] 