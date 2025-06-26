"""
Blog Posts Module - Modular Architecture for Content Management.

This module provides a comprehensive, modular system for blog post management
with enterprise-grade features including AI-powered content generation,
SEO optimization, and performance monitoring.
"""

from typing import Dict, Any, Optional, List
import structlog

# Import core services
from .core import (
    BlogPostService,
    ContentGeneratorService,
    SEOOptimizerService,
    PublishingService
)

# Import data models
from .models import (
    BlogPost,
    BlogPostMetadata,
    ContentRequest,
    ContentGenerationResult,
    SEOConfig,
    SEOData,
    PublishingConfig,
    BlogPostBatch
)

# Import configuration
from .config import (
    BlogPostConfig,
    ContentLanguage,
    ContentTone,
    BlogPostStatus,
    SEOLevel
)

# Import exceptions
from .exceptions import (
    BlogPostException,
    ContentGenerationError,
    SEOOptimizationError,
    PublishingError,
    ValidationError
)

# Import utilities
from .utils import (
    validate_content,
    sanitize_html,
    calculate_reading_time,
    generate_slug,
    extract_keywords,
    calculate_keyword_density
)

logger = structlog.get_logger(__name__)

# Service registry for dependency injection
_service_registry: Dict[str, Any] = {}


def register_service(name: str, service: Any) -> None:
    """Register a service in the service registry."""
    _service_registry[name] = service
    logger.info(f"Service registered: {name}")


def get_service(name: str) -> Any:
    """Get a service from the registry."""
    if name not in _service_registry:
        raise BlogPostException(f"Service '{name}' not found in registry")
    return _service_registry[name]


def create_blog_post_service(config: Optional[BlogPostConfig] = None) -> BlogPostService:
    """
    Factory function to create a BlogPostService instance.
    
    Args:
        config: Optional configuration for the service
        
    Returns:
        BlogPostService: Configured service instance
    """
    if config is None:
        config = BlogPostConfig()
    
    service = BlogPostService(config)
    register_service("blog_post", service)
    return service


def create_content_generator(config: Optional[BlogPostConfig] = None) -> ContentGeneratorService:
    """
    Factory function to create a ContentGeneratorService instance.
    
    Args:
        config: Optional configuration for the service
        
    Returns:
        ContentGeneratorService: Configured service instance
    """
    if config is None:
        config = BlogPostConfig()
    
    service = ContentGeneratorService(config)
    register_service("content_generator", service)
    return service


def create_seo_optimizer(config: Optional[BlogPostConfig] = None) -> SEOOptimizerService:
    """
    Factory function to create a SEOOptimizerService instance.
    
    Args:
        config: Optional configuration for the service
        
    Returns:
        SEOOptimizerService: Configured service instance
    """
    if config is None:
        config = BlogPostConfig()
    
    service = SEOOptimizerService(config)
    register_service("seo_optimizer", service)
    return service


def create_publishing_service(config: Optional[BlogPostConfig] = None) -> PublishingService:
    """
    Factory function to create a PublishingService instance.
    
    Args:
        config: Optional configuration for the service
        
    Returns:
        PublishingService: Configured service instance
    """
    if config is None:
        config = BlogPostConfig()
    
    service = PublishingService(config)
    register_service("publishing", service)
    return service


def create_blog_post_system(config: Optional[BlogPostConfig] = None) -> Dict[str, Any]:
    """
    Factory function to create a complete blog post system with all services.
    
    Args:
        config: Optional configuration for all services
        
    Returns:
        Dict[str, Any]: Dictionary containing all configured services
    """
    if config is None:
        config = BlogPostConfig()
    
    # Create all services
    blog_service = create_blog_post_service(config)
    content_generator = create_content_generator(config)
    seo_optimizer = create_seo_optimizer(config)
    publishing_service = create_publishing_service(config)
    
    system = {
        "blog_service": blog_service,
        "content_generator": content_generator,
        "seo_optimizer": seo_optimizer,
        "publishing_service": publishing_service,
        "config": config
    }
    
    logger.info("Complete blog post system created")
    return system


# Export main components
__all__ = [
    # Core services
    "BlogPostService",
    "ContentGeneratorService", 
    "SEOOptimizerService",
    "PublishingService",
    # Models
    "BlogPost",
    "BlogPostMetadata",
    "ContentRequest",
    "ContentGenerationResult",
    "SEOConfig",
    "SEOData",
    "PublishingConfig",
    "BlogPostBatch",
    # Configuration
    "BlogPostConfig",
    "ContentLanguage",
    "ContentTone",
    "BlogPostStatus",
    "SEOLevel",
    # Exceptions
    "BlogPostException",
    "ContentGenerationError",
    "SEOOptimizationError",
    "PublishingError",
    "ValidationError",
    # Utilities
    "validate_content",
    "sanitize_html",
    "calculate_reading_time",
    "generate_slug",
    "extract_keywords",
    "calculate_keyword_density",
    # Factory functions
    "create_blog_post_service",
    "create_content_generator",
    "create_seo_optimizer",
    "create_publishing_service",
    "create_blog_post_system",
    # Service registry
    "register_service",
    "get_service"
] 