"""
Optimization Exceptions Module.

Custom exceptions for the high-performance optimization system.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import traceback


class OptimizationException(Exception):
    """Base exception for all optimization-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code or "OPTIMIZATION_ERROR"
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


class SerializationError(OptimizationException):
    """Raised when serialization operations fail."""
    
    def __init__(
        self,
        message: str = "Serialization failed",
        format_type: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if format_type:
            details["format_type"] = format_type
        
        super().__init__(
            message=message,
            error_code="SERIALIZATION_ERROR",
            details=details,
            **kwargs
        )


class CacheError(OptimizationException):
    """Raised when cache operations fail."""
    
    def __init__(
        self,
        message: str = "Cache operation failed",
        cache_level: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if cache_level:
            details["cache_level"] = cache_level
        if operation:
            details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details=details,
            **kwargs
        )


class DatabaseOptimizationError(OptimizationException):
    """Raised when database optimization fails."""
    
    def __init__(
        self,
        message: str = "Database optimization failed",
        connection_info: Optional[str] = None,
        query: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if connection_info:
            details["connection_info"] = connection_info
        if query:
            # Only include first 200 chars of query for security
            details["query_snippet"] = query[:200] + "..." if len(query) > 200 else query
        
        super().__init__(
            message=message,
            error_code="DATABASE_OPTIMIZATION_ERROR",
            details=details,
            **kwargs
        )


class NetworkOptimizationError(OptimizationException):
    """Raised when network optimization fails."""
    
    def __init__(
        self,
        message: str = "Network optimization failed",
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if url:
            details["url"] = url
        if status_code:
            details["status_code"] = status_code
        
        super().__init__(
            message=message,
            error_code="NETWORK_OPTIMIZATION_ERROR",
            details=details,
            **kwargs
        )


class MemoryOptimizationError(OptimizationException):
    """Raised when memory optimization fails."""
    
    def __init__(
        self,
        message: str = "Memory optimization failed",
        memory_usage_mb: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if memory_usage_mb:
            details["memory_usage_mb"] = memory_usage_mb
        if operation:
            details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="MEMORY_OPTIMIZATION_ERROR",
            details=details,
            **kwargs
        )


class CompressionError(OptimizationException):
    """Raised when compression operations fail."""
    
    def __init__(
        self,
        message: str = "Compression failed",
        algorithm: Optional[str] = None,
        data_size: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if algorithm:
            details["algorithm"] = algorithm
        if data_size:
            details["data_size"] = data_size
        
        super().__init__(
            message=message,
            error_code="COMPRESSION_ERROR",
            details=details,
            **kwargs
        )


class JITCompilationError(OptimizationException):
    """Raised when JIT compilation fails."""
    
    def __init__(
        self,
        message: str = "JIT compilation failed",
        function_name: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if function_name:
            details["function_name"] = function_name
        
        super().__init__(
            message=message,
            error_code="JIT_COMPILATION_ERROR",
            details=details,
            **kwargs
        )


class PerformanceThresholdExceeded(OptimizationException):
    """Raised when performance thresholds are exceeded."""
    
    def __init__(
        self,
        message: str = "Performance threshold exceeded",
        metric_name: Optional[str] = None,
        actual_value: Optional[float] = None,
        threshold_value: Optional[float] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if metric_name:
            details["metric_name"] = metric_name
        if actual_value is not None:
            details["actual_value"] = actual_value
        if threshold_value is not None:
            details["threshold_value"] = threshold_value
        
        super().__init__(
            message=message,
            error_code="PERFORMANCE_THRESHOLD_EXCEEDED",
            details=details,
            **kwargs
        )


class ConfigurationError(OptimizationException):
    """Raised when optimization configuration is invalid."""
    
    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if config_key:
            details["config_key"] = config_key
        if config_value is not None:
            details["config_value"] = str(config_value)
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
            **kwargs
        )


class ResourceExhaustionError(OptimizationException):
    """Raised when system resources are exhausted."""
    
    def __init__(
        self,
        message: str = "Resource exhaustion",
        resource_type: Optional[str] = None,
        usage_percent: Optional[float] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if resource_type:
            details["resource_type"] = resource_type
        if usage_percent is not None:
            details["usage_percent"] = usage_percent
        
        super().__init__(
            message=message,
            error_code="RESOURCE_EXHAUSTION_ERROR",
            details=details,
            **kwargs
        )


# Utility functions for exception handling

def handle_serialization_error(error: Exception, format_type: str) -> SerializationError:
    """Convert generic serialization error to structured exception."""
    return SerializationError(
        message=f"Serialization failed with format '{format_type}': {str(error)}",
        format_type=format_type,
        cause=error
    )


def handle_cache_error(error: Exception, cache_level: str, operation: str) -> CacheError:
    """Convert generic cache error to structured exception."""
    return CacheError(
        message=f"Cache {operation} failed at level {cache_level}: {str(error)}",
        cache_level=cache_level,
        operation=operation,
        cause=error
    )


def handle_performance_threshold_error(
    metric_name: str, 
    actual_value: float, 
    threshold_value: float
) -> PerformanceThresholdExceeded:
    """Create performance threshold exceeded exception."""
    return PerformanceThresholdExceeded(
        message=f"Performance threshold exceeded for {metric_name}: {actual_value} > {threshold_value}",
        metric_name=metric_name,
        actual_value=actual_value,
        threshold_value=threshold_value
    )


def handle_resource_exhaustion(
    resource_type: str, 
    usage_percent: float, 
    threshold: float = 90.0
) -> ResourceExhaustionError:
    """Create resource exhaustion exception."""
    return ResourceExhaustionError(
        message=f"Resource exhaustion: {resource_type} usage at {usage_percent:.1f}% (threshold: {threshold}%)",
        resource_type=resource_type,
        usage_percent=usage_percent
    )


# Export all exceptions
__all__ = [
    # Base exception
    "OptimizationException",
    
    # Specific exceptions
    "SerializationError",
    "CacheError",
    "DatabaseOptimizationError",
    "NetworkOptimizationError",
    "MemoryOptimizationError",
    "CompressionError",
    "JITCompilationError",
    "PerformanceThresholdExceeded",
    "ConfigurationError",
    "ResourceExhaustionError",
    
    # Utility functions
    "handle_serialization_error",
    "handle_cache_error",
    "handle_performance_threshold_error",
    "handle_resource_exhaustion"
] 