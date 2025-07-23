"""
Dependencies Module for Instagram Captions API v14.0

Centralized dependency injection system with clear organization:
- Authentication and authorization dependencies
- Database and API client dependencies
- Service layer dependencies
- Validation and error handling dependencies
- Performance monitoring dependencies
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

# Import core components
from core.shared_resources import get_shared_resources
from core.enhanced_async_operations import get_db_pool, get_api_client, get_io_monitor
from core.blocking_operations_limiter import blocking_limiter
from core.optimized_engine import engine
from core.smart_cache import get_cache_manager
from core.advanced_lazy_loader import get_lazy_loader

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)


# =============================================================================
# AUTHENTICATION DEPENDENCIES
# =============================================================================

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user
    
    Validates API key and extracts user information.
    Returns user data or raises authentication error.
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    api_key = credentials.credentials
    
    # Validate API key format
    if not api_key or len(api_key) < 10:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key format"
        )
    
    # Extract user identifier from API key
    user_id = api_key[:16]
    
    # Get user from database (simplified for demo)
    user_data = {
        "id": user_id,
        "api_key": api_key,
        "permissions": ["read", "write"],  # Default permissions
        "rate_limit": 1000  # Default rate limit
    }
    
    # Store user in request state for access in route handlers
    request.state.user = user_data
    
    return user_data


async def require_authentication(
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require authentication for protected endpoints
    
    Ensures user is authenticated before allowing access.
    """
    return user


async def require_permission(
    permission: str,
    user: Dict[str, Any] = Depends(require_authentication)
) -> Dict[str, Any]:
    """
    Require specific permission for endpoint access
    
    Checks if user has required permission.
    """
    if permission not in user.get("permissions", []):
        raise HTTPException(
            status_code=403,
            detail=f"Permission '{permission}' required"
        )
    
    return user


# =============================================================================
# DATABASE DEPENDENCIES
# =============================================================================

async def get_database_pool():
    """
    Get database connection pool
    
    Provides access to the enhanced database pool.
    """
    try:
        return await get_db_pool()
    except Exception as e:
        logger.error(f"Failed to get database pool: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )


async def get_api_client_pool():
    """
    Get API client pool
    
    Provides access to the enhanced API client.
    """
    try:
        return await get_api_client()
    except Exception as e:
        logger.error(f"Failed to get API client: {e}")
        raise HTTPException(
            status_code=503,
            detail="API service unavailable"
        )


# =============================================================================
# SERVICE DEPENDENCIES
# =============================================================================

async def get_optimized_engine():
    """
    Get optimized AI engine
    
    Provides access to the caption generation engine.
    """
    try:
        return engine
    except Exception as e:
        logger.error(f"Failed to get AI engine: {e}")
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable"
        )


async def get_cache_manager():
    """
    Get cache manager
    
    Provides access to the smart cache system.
    """
    try:
        return get_cache_manager()
    except Exception as e:
        logger.error(f"Failed to get cache manager: {e}")
        raise HTTPException(
            status_code=503,
            detail="Cache service unavailable"
        )


async def get_lazy_loader_manager():
    """
    Get lazy loader manager
    
    Provides access to the advanced lazy loading system.
    """
    try:
        return get_lazy_loader()
    except Exception as e:
        logger.error(f"Failed to get lazy loader: {e}")
        raise HTTPException(
            status_code=503,
            detail="Lazy loading service unavailable"
        )


# =============================================================================
# MONITORING DEPENDENCIES
# =============================================================================

async def get_io_monitor():
    """
    Get I/O monitor
    
    Provides access to performance monitoring.
    """
    try:
        return await get_io_monitor()
    except Exception as e:
        logger.error(f"Failed to get I/O monitor: {e}")
        # Don't fail the request if monitoring is unavailable
        return None


async def get_blocking_limiter():
    """
    Get blocking operations limiter
    
    Provides access to rate limiting and concurrency control.
    """
    try:
        return blocking_limiter
    except Exception as e:
        logger.error(f"Failed to get blocking limiter: {e}")
        # Don't fail the request if limiting is unavailable
        return None


# =============================================================================
# VALIDATION DEPENDENCIES
# =============================================================================

async def validate_request_id(request_id: str) -> str:
    """
    Validate request ID format
    
    Ensures request ID follows expected format.
    """
    if not request_id or len(request_id) < 8:
        raise HTTPException(
            status_code=400,
            detail="Invalid request ID format"
        )
    
    return request_id


async def validate_content_length(content: str, max_length: int = 10000) -> str:
    """
    Validate content length
    
    Ensures content doesn't exceed maximum length.
    """
    if len(content) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Content too long. Maximum {max_length} characters allowed."
        )
    
    return content


# =============================================================================
# COMBINED DEPENDENCIES
# =============================================================================

class ServiceDependencies:
    """Combined service dependencies for route handlers"""
    
    def __init__(
        self,
        user: Dict[str, Any] = Depends(require_authentication),
        db_pool = Depends(get_database_pool),
        api_client = Depends(get_api_client_pool),
        ai_engine = Depends(get_optimized_engine),
        cache_manager = Depends(get_cache_manager),
        lazy_loader = Depends(get_lazy_loader_manager),
        io_monitor = Depends(get_io_monitor),
        blocking_limiter = Depends(get_blocking_limiter)
    ):
        self.user = user
        self.db_pool = db_pool
        self.api_client = api_client
        self.ai_engine = ai_engine
        self.cache_manager = cache_manager
        self.lazy_loader = lazy_loader
        self.io_monitor = io_monitor
        self.blocking_limiter = blocking_limiter


class CoreDependencies:
    """Core dependencies for basic operations"""
    
    def __init__(
        self,
        user: Dict[str, Any] = Depends(require_authentication),
        ai_engine = Depends(get_optimized_engine),
        cache_manager = Depends(get_cache_manager)
    ):
        self.user = user
        self.ai_engine = ai_engine
        self.cache_manager = cache_manager


class AdvancedDependencies:
    """Advanced dependencies for complex operations"""
    
    def __init__(
        self,
        user: Dict[str, Any] = Depends(require_authentication),
        db_pool = Depends(get_database_pool),
        api_client = Depends(get_api_client_pool),
        ai_engine = Depends(get_optimized_engine),
        cache_manager = Depends(get_cache_manager),
        lazy_loader = Depends(get_lazy_loader_manager),
        io_monitor = Depends(get_io_monitor)
    ):
        self.user = user
        self.db_pool = db_pool
        self.api_client = api_client
        self.ai_engine = ai_engine
        self.cache_manager = cache_manager
        self.lazy_loader = lazy_loader
        self.io_monitor = io_monitor


# =============================================================================
# DEPENDENCY FACTORIES
# =============================================================================

def create_dependencies_for_route(route_type: str):
    """
    Create appropriate dependencies based on route type
    
    Returns the appropriate dependency class for the route.
    """
    if route_type == "core":
        return CoreDependencies
    elif route_type == "advanced":
        return AdvancedDependencies
    else:
        return ServiceDependencies


# =============================================================================
# UTILITY DEPENDENCIES
# =============================================================================

async def get_request_context(request: Request) -> Dict[str, Any]:
    """
    Get request context information
    
    Extracts useful information from the request.
    """
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "timestamp": request.state.get("start_time")
    }


async def get_shared_resources_manager():
    """
    Get shared resources manager
    
    Provides access to shared resources.
    """
    try:
        return get_shared_resources()
    except Exception as e:
        logger.error(f"Failed to get shared resources: {e}")
        raise HTTPException(
            status_code=503,
            detail="Shared resources unavailable"
        )


# Export all dependencies
__all__ = [
    # Authentication
    "get_current_user",
    "require_authentication", 
    "require_permission",
    
    # Database and API
    "get_database_pool",
    "get_api_client_pool",
    
    # Services
    "get_optimized_engine",
    "get_cache_manager",
    "get_lazy_loader_manager",
    
    # Monitoring
    "get_io_monitor",
    "get_blocking_limiter",
    
    # Validation
    "validate_request_id",
    "validate_content_length",
    
    # Combined dependencies
    "ServiceDependencies",
    "CoreDependencies", 
    "AdvancedDependencies",
    
    # Utilities
    "create_dependencies_for_route",
    "get_request_context",
    "get_shared_resources_manager"
] 