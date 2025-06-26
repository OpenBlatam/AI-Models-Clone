"""
Copywriting Module - Modular AI-Powered Content Generation System.

This module provides a comprehensive, modular system for AI-powered copywriting
with support for multiple providers, content analysis, and performance optimization.
"""

from typing import Dict, Any, Optional, List
import structlog

from .core import (
    CopywritingService,
    ContentGeneratorService,
    ContentAnalyzerService,
    TemplateService
)
from .models import (
    ContentRequest,
    GeneratedContent,
    ContentMetrics,
    ContentType,
    ContentTone,
    ContentLanguage
)
from .config import CopywritingConfig
from .exceptions import CopywritingException
from .cache import CopywritingCache
from .providers import AIProviderManager

logger = structlog.get_logger(__name__)

# Service registry for dependency injection
_service_registry: Dict[str, Any] = {}


def register_service(name: str, service: Any) -> None:
    """Register a service in the service registry."""
    _service_registry[name] = service
    logger.info(f"Copywriting service registered: {name}")


def get_service(name: str) -> Any:
    """Get a service from the registry."""
    if name not in _service_registry:
        raise CopywritingException(f"Service '{name}' not found in registry")
    return _service_registry[name]


def create_copywriting_service(config: Optional[CopywritingConfig] = None) -> CopywritingService:
    """
    Factory function to create a CopywritingService instance.
    
    Args:
        config: Optional configuration for the service
        
    Returns:
        CopywritingService: Configured service instance
    """
    if config is None:
        config = CopywritingConfig()
    
    service = CopywritingService(config)
    register_service("copywriting", service)
    return service


def create_content_generator(config: Optional[CopywritingConfig] = None) -> ContentGeneratorService:
    """
    Factory function to create a ContentGeneratorService instance.
    
    Args:
        config: Optional configuration for the service
        
    Returns:
        ContentGeneratorService: Configured service instance
    """
    if config is None:
        config = CopywritingConfig()
    
    service = ContentGeneratorService(config)
    register_service("content_generator", service)
    return service


def create_content_analyzer(config: Optional[CopywritingConfig] = None) -> ContentAnalyzerService:
    """
    Factory function to create a ContentAnalyzerService instance.
    
    Args:
        config: Optional configuration for the service
        
    Returns:
        ContentAnalyzerService: Configured service instance
    """
    if config is None:
        config = CopywritingConfig()
    
    service = ContentAnalyzerService(config)
    register_service("content_analyzer", service)
    return service


def create_template_service(config: Optional[CopywritingConfig] = None) -> TemplateService:
    """
    Factory function to create a TemplateService instance.
    
    Args:
        config: Optional configuration for the service
        
    Returns:
        TemplateService: Configured service instance
    """
    if config is None:
        config = CopywritingConfig()
    
    service = TemplateService(config)
    register_service("template_service", service)
    return service


def create_copywriting_system(config: Optional[CopywritingConfig] = None) -> Dict[str, Any]:
    """
    Factory function to create a complete copywriting system with all services.
    
    Args:
        config: Optional configuration for all services
        
    Returns:
        Dict[str, Any]: Dictionary containing all configured services
    """
    if config is None:
        config = CopywritingConfig()
    
    # Create all services
    copywriting_service = create_copywriting_service(config)
    content_generator = create_content_generator(config)
    content_analyzer = create_content_analyzer(config)
    template_service = create_template_service(config)
    
    # Create supporting components
    cache = CopywritingCache(config)
    ai_provider_manager = AIProviderManager(config)
    
    system = {
        "copywriting_service": copywriting_service,
        "content_generator": content_generator,
        "content_analyzer": content_analyzer,
        "template_service": template_service,
        "cache": cache,
        "ai_provider_manager": ai_provider_manager,
        "config": config
    }
    
    logger.info("Complete copywriting system created")
    return system


# Export main components
__all__ = [
    # Core services
    "CopywritingService",
    "ContentGeneratorService",
    "ContentAnalyzerService",
    "TemplateService",
    # Models
    "ContentRequest",
    "GeneratedContent",
    "ContentMetrics",
    "ContentType",
    "ContentTone",
    "ContentLanguage",
    # Configuration
    "CopywritingConfig",
    # Exceptions
    "CopywritingException",
    # Supporting components
    "CopywritingCache",
    "AIProviderManager",
    # Factory functions
    "create_copywriting_service",
    "create_content_generator",
    "create_content_analyzer",
    "create_template_service",
    "create_copywriting_system",
    # Service registry
    "register_service",
    "get_service"
] 