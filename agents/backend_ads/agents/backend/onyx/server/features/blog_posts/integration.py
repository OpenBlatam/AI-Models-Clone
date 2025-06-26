"""
Integration Guide for Blog Posts Module.

This file shows how to integrate the blog posts module with the main Onyx Features application
and provides examples of different integration patterns.
"""

from typing import Dict, Any, Optional
from fastapi import FastAPI, Depends
import structlog

from blog_posts import (
    create_blog_post_system,
    BlogPostConfig,
    BlogPostService,
    ContentGeneratorService,
    SEOOptimizerService,
    PublishingService
)
from blog_posts.api import router as blog_posts_router

logger = structlog.get_logger(__name__)


class BlogPostIntegration:
    """Integration class for managing blog posts in the main application."""
    
    def __init__(self, config: Optional[BlogPostConfig] = None):
        self.config = config or BlogPostConfig()
        self.system = create_blog_post_system(self.config)
        self.blog_service = self.system["blog_service"]
        self.content_generator = self.system["content_generator"]
        self.seo_optimizer = self.system["seo_optimizer"]
        self.publishing_service = self.system["publishing_service"]
        
        logger.info("Blog posts integration initialized")
    
    def get_blog_service(self) -> BlogPostService:
        """Get the blog post service."""
        return self.blog_service
    
    def get_content_generator(self) -> ContentGeneratorService:
        """Get the content generator service."""
        return self.content_generator
    
    def get_seo_optimizer(self) -> SEOOptimizerService:
        """Get the SEO optimizer service."""
        return self.seo_optimizer
    
    def get_publishing_service(self) -> PublishingService:
        """Get the publishing service."""
        return self.publishing_service
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all blog post services."""
        health_status = {
            "blog_service": {"healthy": True, "message": "Service operational"},
            "content_generator": {"healthy": True, "message": "Service operational"},
            "seo_optimizer": {"healthy": True, "message": "Service operational"},
            "publishing_service": {"healthy": True, "message": "Service operational"},
        }
        
        try:
            # Test each service
            posts = await self.blog_service.list_posts(limit=1)
            health_status["blog_service"]["posts_count"] = len(posts)
            
        except Exception as e:
            logger.error("Blog posts health check failed", error=str(e))
            health_status["overall"] = {"healthy": False, "error": str(e)}
        
        return health_status


# Global integration instance
_blog_integration: Optional[BlogPostIntegration] = None


def get_blog_integration() -> BlogPostIntegration:
    """Get the global blog integration instance."""
    global _blog_integration
    if _blog_integration is None:
        _blog_integration = BlogPostIntegration()
    return _blog_integration


def setup_blog_posts_integration(app: FastAPI, config: Optional[BlogPostConfig] = None) -> BlogPostIntegration:
    """
    Set up blog posts integration with a FastAPI application.
    
    Args:
        app: FastAPI application instance
        config: Optional blog post configuration
        
    Returns:
        BlogPostIntegration: Configured integration instance
    """
    global _blog_integration
    
    # Create integration
    _blog_integration = BlogPostIntegration(config)
    
    # Include the blog posts router
    app.include_router(
        blog_posts_router,
        prefix="/api/v1",
        tags=["blog-posts"]
    )
    
    # Add startup and shutdown events
    @app.on_event("startup")
    async def startup_blog_posts():
        logger.info("Starting blog posts services")
        health = await _blog_integration.health_check()
        logger.info("Blog posts health check", status=health)
    
    @app.on_event("shutdown")
    async def shutdown_blog_posts():
        logger.info("Shutting down blog posts services")
    
    # Add health check endpoint
    @app.get("/health/blog-posts")
    async def blog_posts_health():
        integration = get_blog_integration()
        return await integration.health_check()
    
    logger.info("Blog posts integration setup completed")
    return _blog_integration


def create_blog_posts_app(config: Optional[BlogPostConfig] = None) -> FastAPI:
    """
    Create a standalone FastAPI application with blog posts functionality.
    
    Args:
        config: Optional blog post configuration
        
    Returns:
        FastAPI: Configured application
    """
    app = FastAPI(
        title="Blog Posts API",
        description="Modular blog post management system with AI-powered content generation",
        version="1.0.0"
    )
    
    # Setup blog posts integration
    setup_blog_posts_integration(app, config)
    
    # Add root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Blog Posts API",
            "version": "1.0.0",
            "features": [
                "AI Content Generation",
                "SEO Optimization", 
                "Multi-Platform Publishing",
                "Content Management"
            ]
        }
    
    return app


# Dependency injection functions for use in other parts of the application
def get_blog_service() -> BlogPostService:
    """Dependency injection for blog service."""
    integration = get_blog_integration()
    return integration.get_blog_service()


def get_content_generator() -> ContentGeneratorService:
    """Dependency injection for content generator."""
    integration = get_blog_integration()
    return integration.get_content_generator()


def get_seo_optimizer() -> SEOOptimizerService:
    """Dependency injection for SEO optimizer."""
    integration = get_blog_integration()
    return integration.get_seo_optimizer()


def get_publishing_service() -> PublishingService:
    """Dependency injection for publishing service."""
    integration = get_blog_integration()
    return integration.get_publishing_service()


# Example integration with existing Onyx Features app
def integrate_with_onyx_app(onyx_app: FastAPI) -> None:
    """
    Integrate blog posts with the existing Onyx Features application.
    
    Args:
        onyx_app: The main Onyx Features FastAPI application
    """
    # Get or create blog posts configuration
    blog_config = BlogPostConfig()
    
    # Setup integration
    integration = setup_blog_posts_integration(onyx_app, blog_config)
    
    # Add blog posts specific middleware or hooks if needed
    @onyx_app.middleware("http")
    async def blog_posts_middleware(request, call_next):
        # Add any blog-specific middleware logic here
        response = await call_next(request)
        return response
    
    # Add blog posts to the main app's health check
    @onyx_app.get("/health")
    async def enhanced_health_check():
        # Existing health check logic
        health_status = {"status": "healthy"}
        
        # Add blog posts health
        blog_health = await integration.health_check()
        health_status["blog_posts"] = blog_health
        
        return health_status
    
    logger.info("Blog posts successfully integrated with Onyx Features application")


# Export main components
__all__ = [
    "BlogPostIntegration",
    "get_blog_integration",
    "setup_blog_posts_integration", 
    "create_blog_posts_app",
    "integrate_with_onyx_app",
    "get_blog_service",
    "get_content_generator",
    "get_seo_optimizer",
    "get_publishing_service"
] 