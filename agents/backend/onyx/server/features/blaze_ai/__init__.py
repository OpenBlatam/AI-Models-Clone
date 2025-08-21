"""
Blaze AI - Advanced AI Module for Content Generation and Analysis

A comprehensive, production-ready AI module providing:
- Text generation with state-of-the-art language models
- Image generation using diffusion models
- SEO optimization and content analysis
- Brand voice learning and application
- Interactive Gradio interfaces
- Robust API endpoints with FastAPI
- Advanced monitoring and logging
- Comprehensive training and evaluation tools

Key Features:
- Modular architecture with clear separation of concerns
- Production-ready error handling and monitoring
- Optimized performance with mixed precision and caching
- Comprehensive testing and documentation
- Easy integration and deployment
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# Version information
__version__ = "2.0.0"
__author__ = "Blaze AI Team"
__description__ = "Advanced AI Module for Content Generation and Analysis"

# Core imports
from .core import CoreConfig, ServiceContainer, SystemMode
from .engines import EngineManager
from .services import BlazeServiceRegistry
from .api.router import router as blaze_ai_router

# Main class
class ModularBlazeAI:
    """
    Main entry point for the Blaze AI module.
    
    Provides a unified interface for all AI capabilities including:
    - Text generation and analysis
    - Image generation
    - SEO optimization
    - Brand voice management
    - Content planning and scheduling
    """
    
    def __init__(self, config: Optional[CoreConfig] = None):
        """Initialize the Blaze AI module with optional configuration."""
        self.config = config or CoreConfig()
        self.logger = self._setup_logging()
        
        # Initialize core components
        self.service_container = ServiceContainer()
        self.engine_manager = EngineManager()
        self.service_registry = BlazeServiceRegistry()
        
        # Initialize services
        self._initialize_services()
        
        self.logger.info("Blaze AI module initialized successfully")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the module."""
        logger = logging.getLogger("blaze_ai")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_services(self):
        """Initialize all core services."""
        try:
            # Register core services
            self.service_registry.register_service("seo", "SEOService")
            self.service_registry.register_service("brand", "BrandVoiceService")
            self.service_registry.register_service("generation", "ContentGenerationService")
            self.service_registry.register_service("analytics", "AnalyticsService")
            self.service_registry.register_service("planner", "ContentPlannerService")
            
            self.logger.info("Core services initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {e}")
            raise
    
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using the LLM engine."""
        try:
            result = await self.engine_manager.dispatch(
                "llm", "generate", {"prompt": prompt, **kwargs}
            )
            return result
        except Exception as e:
            self.logger.error(f"Text generation failed: {e}")
            raise
    
    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate image using the diffusion engine."""
        try:
            result = await self.engine_manager.dispatch(
                "diffusion", "generate", {"prompt": prompt, **kwargs}
            )
            return result
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            raise
    
    async def analyze_seo(self, content: str, **kwargs) -> Dict[str, Any]:
        """Analyze content for SEO optimization."""
        try:
            result = await self.engine_manager.dispatch(
                "router", "seo_analysis", {"content": content, **kwargs}
            )
            return result
        except Exception as e:
            self.logger.error(f"SEO analysis failed: {e}")
            raise
    
    async def apply_brand_voice(self, content: str, brand_name: str, action: str = "apply", **kwargs) -> Dict[str, Any]:
        """Apply brand voice to content."""
        try:
            result = await self.engine_manager.dispatch(
                "router", "brand_voice", {"content": content, "brand_name": brand_name, "action": action, **kwargs}
            )
            return result
        except Exception as e:
            self.logger.error(f"Brand voice application failed: {e}")
            raise
    
    async def generate_content(self, content_type: str, topic: str, **kwargs) -> Dict[str, Any]:
        """Generate content of specified type."""
        try:
            result = await self.engine_manager.dispatch(
                "router", "content_generation", {"content_type": content_type, "topic": topic, **kwargs}
            )
            return result
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            raise
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get the health status of all components."""
        try:
            return {
                "overall_status": "healthy",
                "version": __version__,
                "services": self.service_registry.get_service_status(),
                "engines": self.engine_manager.get_engine_status(),
                "config": {
                    "system_mode": self.config.system_mode.value,
                    "log_level": self.config.log_level.value,
                    "enable_async": self.config.enable_async,
                    "max_concurrent_requests": self.config.max_concurrent_requests
                }
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "overall_status": "unhealthy",
                "error": str(e),
                "version": __version__
            }
    
    async def shutdown(self):
        """Gracefully shutdown the module."""
        try:
            await self.engine_manager.shutdown()
            self.logger.info("Blaze AI module shutdown successfully")
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")

# Factory function for easy instantiation
def create_modular_ai(config_path: Optional[str] = None, **kwargs) -> ModularBlazeAI:
    """
    Factory function to create a ModularBlazeAI instance.
    
    Args:
        config_path: Path to configuration file
        **kwargs: Additional configuration parameters
    
    Returns:
        Configured ModularBlazeAI instance
    """
    config = None
    
    if config_path:
        try:
            from .utils.config import load_config_from_file
            config_data = load_config_from_file(config_path)
            config = CoreConfig(**config_data)
        except Exception as e:
            logging.warning(f"Failed to load config from {config_path}: {e}")
    
    if not config:
        config = CoreConfig(**kwargs)
    
    return ModularBlazeAI(config)

# Convenience function to get logger
def get_logger(name: str = "blaze_ai") -> logging.Logger:
    """Get a logger instance for the module."""
    from .utils.logging import get_logger as _get_logger
    return _get_logger(name)

# Export main components
__all__ = [
    "ModularBlazeAI",
    "create_modular_ai",
    "get_logger",
    "blaze_ai_router",
    "CoreConfig",
    "ServiceContainer",
    "SystemMode",
    "EngineManager",
    "BlazeServiceRegistry",
    "__version__",
    "__author__",
    "__description__"
]
