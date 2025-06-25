"""
Key Messages Module - Production optimized implementation.

Provides enterprise-grade message handling capabilities with async support,
caching, batch processing, and comprehensive error handling.
"""

import logging
from typing import Optional, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Module version
__version__ = "1.0.0"

# Import core components
try:
    from .service import (
        KeyMessageService,
        KeyMessage,
        MessageBatch,
        KeyMessageConfig,
        MessageType,
        MessagePriority,
        KeyMessageServiceError,
        create_key_message_service,
        create_message_legacy
    )
    
    SERVICE_AVAILABLE = True
    
except ImportError as e:
    logger.error(f"Failed to import key message service components: {e}")
    SERVICE_AVAILABLE = False

# Export components
__all__ = [
    # Core service
    "KeyMessageService",
    "KeyMessage",
    "MessageBatch",
    "KeyMessageConfig",
    "MessageType",
    "MessagePriority",
    "KeyMessageServiceError",
    
    # Factory functions
    "create_key_message_service",
    "create_message_legacy",
    "create_default_service",
    "get_module_status",
    
    # Availability flag
    "SERVICE_AVAILABLE"
]


def create_default_service(
    enable_caching: bool = True,
    max_cache_size: int = 1000,
    **kwargs
) -> Optional["KeyMessageService"]:
    """
    Create a default key message service with optimized settings.
    
    Args:
        enable_caching: Whether to enable caching
        max_cache_size: Maximum cache size
        **kwargs: Additional configuration options
        
    Returns:
        KeyMessageService or None if not available
    """
    if not SERVICE_AVAILABLE:
        logger.error("Key message service not available")
        return None
    
    try:
        config = KeyMessageConfig(
            enable_compression=True,
            cache_ttl=3600,
            **kwargs
        )
        
        service = create_key_message_service(config)
        logger.info("Default key message service created successfully")
        return service
        
    except Exception as e:
        logger.error(f"Failed to create default service: {e}")
        return None


def get_module_status() -> Dict[str, Any]:
    """
    Get the status of key messages module.
    
    Returns:
        Dict: Module status information
    """
    return {
        "version": __version__,
        "service_available": SERVICE_AVAILABLE,
        "module_health": SERVICE_AVAILABLE,
        "features": {
            "async_support": SERVICE_AVAILABLE,
            "batch_processing": SERVICE_AVAILABLE,
            "caching": SERVICE_AVAILABLE,
            "error_handling": SERVICE_AVAILABLE
        }
    }


# Initialize module
logger.info(f"Key Messages Module v{__version__} initialized")
logger.info(f"Service Available: {'✓' if SERVICE_AVAILABLE else '✗'}") 