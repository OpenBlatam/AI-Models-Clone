"""
Dependencies Package

This package contains all dependency injection functions for FastAPI.
Provides centralized dependency management for database, cache, monitoring, and other services.
"""

from .core import (
    get_current_user,
    get_db_session,
    get_cache_manager,
    get_performance_monitor,
    get_error_monitor,
    get_async_io_manager
)

from .auth import (
    get_authenticated_user,
    get_admin_user,
    get_user_permissions
)

from .validation import (
    validate_request_data,
    validate_response_data,
    get_pagination_params
)

from .monitoring import (
    get_request_tracker,
    get_performance_tracker,
    get_error_tracker
)

from .shared_resources import (
    # Configuration
    SharedResourceConfig,
    ResourceConfig,
    CryptoConfig,
    ResourceType,
    CryptoAlgorithm,
    NetworkProtocol,
    
    # Health and Metrics
    ResourceHealth,
    ResourceMetrics,
    
    # Managers
    BaseResourceManager,
    HTTPSessionManager,
    WebSocketSessionManager,
    CryptoBackendManager,
    DatabasePoolManager,
    RedisPoolManager,
    SharedResourcesContainer,
    
    # FastAPI Dependencies
    get_http_session,
    get_websocket_session,
    get_crypto_backend,
    get_database_pool,
    get_redis_pool,
    
    # Context Managers
    http_session_context,
    crypto_backend_context,
    
    # Lifecycle Management
    initialize_shared_resources,
    shutdown_shared_resources,
    
    # Health Monitoring
    get_resource_health,
    get_all_resource_health
)

# Export all dependencies
__all__ = [
    # Core dependencies
    "get_current_user",
    "get_db_session", 
    "get_cache_manager",
    "get_performance_monitor",
    "get_error_monitor",
    "get_async_io_manager",
    
    # Auth dependencies
    "get_authenticated_user",
    "get_admin_user", 
    "get_user_permissions",
    
    # Validation dependencies
    "validate_request_data",
    "validate_response_data",
    "get_pagination_params",
    
    # Monitoring dependencies
    "get_request_tracker",
    "get_performance_tracker",
    "get_error_tracker",
    
    # Shared Resources Configuration
    "SharedResourceConfig",
    "ResourceConfig",
    "CryptoConfig",
    "ResourceType",
    "CryptoAlgorithm",
    "NetworkProtocol",
    
    # Shared Resources Health and Metrics
    "ResourceHealth",
    "ResourceMetrics",
    
    # Shared Resources Managers
    "BaseResourceManager",
    "HTTPSessionManager",
    "WebSocketSessionManager",
    "CryptoBackendManager",
    "DatabasePoolManager",
    "RedisPoolManager",
    "SharedResourcesContainer",
    
    # Shared Resources FastAPI Dependencies
    "get_http_session",
    "get_websocket_session",
    "get_crypto_backend",
    "get_database_pool",
    "get_redis_pool",
    
    # Shared Resources Context Managers
    "http_session_context",
    "crypto_backend_context",
    
    # Shared Resources Lifecycle Management
    "initialize_shared_resources",
    "shutdown_shared_resources",
    
    # Shared Resources Health Monitoring
    "get_resource_health",
    "get_all_resource_health"
]

# Dependency registry for easy access
DEPENDENCY_REGISTRY = {
    "core": {
        "current_user": get_current_user,
        "db_session": get_db_session,
        "cache_manager": get_cache_manager,
        "performance_monitor": get_performance_monitor,
        "error_monitor": get_error_monitor,
        "async_io_manager": get_async_io_manager
    },
    "auth": {
        "authenticated_user": get_authenticated_user,
        "admin_user": get_admin_user,
        "user_permissions": get_user_permissions
    },
    "validation": {
        "request_data": validate_request_data,
        "response_data": validate_response_data,
        "pagination": get_pagination_params
    },
    "monitoring": {
        "request_tracker": get_request_tracker,
        "performance_tracker": get_performance_tracker,
        "error_tracker": get_error_tracker
    },
    "shared_resources": {
        "http_session": get_http_session,
        "websocket_session": get_websocket_session,
        "crypto_backend": get_crypto_backend,
        "database_pool": get_database_pool,
        "redis_pool": get_redis_pool
    }
}

def get_dependency(category: str, name: str):
    """Get a specific dependency by category and name."""
    return DEPENDENCY_REGISTRY.get(category, {}).get(name)

def get_dependencies_by_category(category: str):
    """Get all dependencies for a specific category."""
    return DEPENDENCY_REGISTRY.get(category, {}) 