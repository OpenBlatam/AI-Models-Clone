"""
Custom Exceptions for Modular NLP System.

This module defines custom exceptions used throughout the NLP analysis system
to provide better error handling and debugging capabilities.
"""

class NLPException(Exception):
    """Base exception for all NLP-related errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for logging/serialization."""
        return {
            'exception_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details
        }

class AnalyzerException(NLPException):
    """Base exception for analyzer-related errors."""
    pass

class AnalyzerNotAvailableException(AnalyzerException):
    """Raised when an analyzer is not available (missing dependencies, etc.)."""
    
    def __init__(self, analyzer_name: str, reason: str = None):
        message = f"Analyzer '{analyzer_name}' is not available"
        if reason:
            message += f": {reason}"
        super().__init__(message, "ANALYZER_NOT_AVAILABLE", {
            'analyzer_name': analyzer_name,
            'reason': reason
        })

class AnalyzerTimeoutException(AnalyzerException):
    """Raised when an analyzer times out during analysis."""
    
    def __init__(self, analyzer_name: str, timeout_ms: int):
        message = f"Analyzer '{analyzer_name}' timed out after {timeout_ms}ms"
        super().__init__(message, "ANALYZER_TIMEOUT", {
            'analyzer_name': analyzer_name,
            'timeout_ms': timeout_ms
        })

class InvalidInputException(AnalyzerException):
    """Raised when input text is invalid for analysis."""
    
    def __init__(self, analyzer_name: str, validation_error: str):
        message = f"Invalid input for analyzer '{analyzer_name}': {validation_error}"
        super().__init__(message, "INVALID_INPUT", {
            'analyzer_name': analyzer_name,
            'validation_error': validation_error
        })

class AnalysisFailedException(AnalyzerException):
    """Raised when analysis fails unexpectedly."""
    
    def __init__(self, analyzer_name: str, reason: str = None):
        message = f"Analysis failed for analyzer '{analyzer_name}'"
        if reason:
            message += f": {reason}"
        super().__init__(message, "ANALYSIS_FAILED", {
            'analyzer_name': analyzer_name,
            'reason': reason
        })

class ConfigurationException(NLPException):
    """Base exception for configuration-related errors."""
    pass

class InvalidConfigurationException(ConfigurationException):
    """Raised when configuration is invalid."""
    
    def __init__(self, config_key: str, reason: str):
        message = f"Invalid configuration for '{config_key}': {reason}"
        super().__init__(message, "INVALID_CONFIGURATION", {
            'config_key': config_key,
            'reason': reason
        })

class MissingConfigurationException(ConfigurationException):
    """Raised when required configuration is missing."""
    
    def __init__(self, config_key: str):
        message = f"Missing required configuration: '{config_key}'"
        super().__init__(message, "MISSING_CONFIGURATION", {
            'config_key': config_key
        })

class PluginException(NLPException):
    """Base exception for plugin-related errors."""
    pass

class PluginLoadException(PluginException):
    """Raised when a plugin fails to load."""
    
    def __init__(self, plugin_name: str, reason: str):
        message = f"Failed to load plugin '{plugin_name}': {reason}"
        super().__init__(message, "PLUGIN_LOAD_FAILED", {
            'plugin_name': plugin_name,
            'reason': reason
        })

class PluginInitializationException(PluginException):
    """Raised when a plugin fails to initialize."""
    
    def __init__(self, plugin_name: str, reason: str):
        message = f"Failed to initialize plugin '{plugin_name}': {reason}"
        super().__init__(message, "PLUGIN_INIT_FAILED", {
            'plugin_name': plugin_name,
            'reason': reason
        })

class PluginConflictException(PluginException):
    """Raised when there's a conflict between plugins."""
    
    def __init__(self, plugin1: str, plugin2: str, conflict_type: str):
        message = f"Conflict between plugins '{plugin1}' and '{plugin2}': {conflict_type}"
        super().__init__(message, "PLUGIN_CONFLICT", {
            'plugin1': plugin1,
            'plugin2': plugin2,
            'conflict_type': conflict_type
        })

class EnhancementException(NLPException):
    """Base exception for enhancement-related errors."""
    pass

class EnhancementFailedException(EnhancementException):
    """Raised when content enhancement fails."""
    
    def __init__(self, enhancer_name: str, reason: str = None):
        message = f"Enhancement failed for enhancer '{enhancer_name}'"
        if reason:
            message += f": {reason}"
        super().__init__(message, "ENHANCEMENT_FAILED", {
            'enhancer_name': enhancer_name,
            'reason': reason
        })

class UnsupportedEnhancementException(EnhancementException):
    """Raised when enhancement is not supported for the given analysis result."""
    
    def __init__(self, enhancer_name: str, analysis_type: str):
        message = f"Enhancer '{enhancer_name}' does not support analysis type '{analysis_type}'"
        super().__init__(message, "UNSUPPORTED_ENHANCEMENT", {
            'enhancer_name': enhancer_name,
            'analysis_type': analysis_type
        })

class CacheException(NLPException):
    """Base exception for cache-related errors."""
    pass

class CacheConnectionException(CacheException):
    """Raised when cache connection fails."""
    
    def __init__(self, cache_type: str, reason: str):
        message = f"Failed to connect to {cache_type} cache: {reason}"
        super().__init__(message, "CACHE_CONNECTION_FAILED", {
            'cache_type': cache_type,
            'reason': reason
        })

class CacheOperationException(CacheException):
    """Raised when a cache operation fails."""
    
    def __init__(self, operation: str, reason: str):
        message = f"Cache operation '{operation}' failed: {reason}"
        super().__init__(message, "CACHE_OPERATION_FAILED", {
            'operation': operation,
            'reason': reason
        })

class DependencyException(NLPException):
    """Raised when required dependencies are missing."""
    
    def __init__(self, dependency: str, required_version: str = None):
        message = f"Missing required dependency: {dependency}"
        if required_version:
            message += f" (version {required_version} or higher)"
        super().__init__(message, "MISSING_DEPENDENCY", {
            'dependency': dependency,
            'required_version': required_version
        })

class ResourceException(NLPException):
    """Raised when required resources are not available."""
    
    def __init__(self, resource_type: str, resource_name: str, reason: str = None):
        message = f"{resource_type} '{resource_name}' is not available"
        if reason:
            message += f": {reason}"
        super().__init__(message, "RESOURCE_NOT_AVAILABLE", {
            'resource_type': resource_type,
            'resource_name': resource_name,
            'reason': reason
        })

# Convenience function for dependency checking
def check_dependency(dependency_name: str, import_path: str = None) -> bool:
    """
    Check if a dependency is available.
    
    Args:
        dependency_name: Name of the dependency (for error messages)
        import_path: Import path to test (defaults to dependency_name)
        
    Returns:
        True if dependency is available
        
    Raises:
        DependencyException: If dependency is not available
    """
    import_path = import_path or dependency_name
    
    try:
        __import__(import_path)
        return True
    except ImportError as e:
        raise DependencyException(dependency_name, str(e))

# Convenience function for resource checking
def check_resource(resource_type: str, resource_name: str, check_function) -> bool:
    """
    Check if a resource is available.
    
    Args:
        resource_type: Type of resource (e.g., "model", "dataset")
        resource_name: Name of the resource
        check_function: Function that returns True if resource is available
        
    Returns:
        True if resource is available
        
    Raises:
        ResourceException: If resource is not available
    """
    try:
        if check_function():
            return True
        else:
            raise ResourceException(resource_type, resource_name, "Resource check failed")
    except Exception as e:
        raise ResourceException(resource_type, resource_name, str(e)) 