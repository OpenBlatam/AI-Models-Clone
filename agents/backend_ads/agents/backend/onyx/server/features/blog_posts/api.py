"""
FastAPI Router for Blog Posts Module.

Defines API endpoints for blog post management with proper error handling and validation.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
import structlog

from .core import (
    BlogPostService, ContentGeneratorService, 
    SEOOptimizerService, PublishingService
)
from .models import (
    BlogPost, ContentRequest, ContentGenerationResult,
    SEOConfig, PublishingConfig, BlogPostMetadata, SEOData
)
from .config import BlogPostConfig, BlogPostStatus, ContentLanguage, ContentTone
from .exceptions import BlogPostException
from . import (
    create_blog_post_service, create_content_generator,
    create_seo_optimizer, create_publishing_service
)

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/blog-posts", tags=["blog-posts"])

# Global services (in a real app, these would use dependency injection)
_services = {}


def get_blog_service() -> BlogPostService:
    """Dependency to get blog post service."""
    if "blog_service" not in _services:
        _services["blog_service"] = create_blog_post_service()
    return _services["blog_service"]


def get_content_generator() -> ContentGeneratorService:
    """Dependency to get content generator service."""
    if "content_generator" not in _services:
        _services["content_generator"] = create_content_generator()
    return _services["content_generator"]


def get_seo_optimizer() -> SEOOptimizerService:
    """Dependency to get SEO optimizer service."""
    if "seo_optimizer" not in _services:
        _services["seo_optimizer"] = create_seo_optimizer()
    return _services["seo_optimizer"]


def get_publishing_service() -> PublishingService:
    """Dependency to get publishing service."""
    if "publishing_service" not in _services:
        _services["publishing_service"] = create_publishing_service()
    return _services["publishing_service"]


@router.post("/", response_model=Dict[str, Any])
async def create_blog_post(
    title: str,
    content: str,
    author: str,
    tags: List[str] = [],
    category: Optional[str] = None,
    featured_image: Optional[str] = None,
    excerpt: Optional[str] = None,
    blog_service: BlogPostService = Depends(get_blog_service)
):
    """Create a new blog post."""
    try:
        metadata = BlogPostMetadata(
            author=author,
            tags=tags,
            category=category,
            featured_image=featured_image,
            excerpt=excerpt
        )
        
        post = await blog_service.create_post(
            title=title,
            content=content,
            metadata=metadata
        )
        
        return {
            "success": True,
            "message": "Blog post created successfully",
            "data": {
                "id": post.id,
                "title": post.title,
                "status": post.status,
                "slug": post.slug,
                "created_at": post.created_at.isoformat(),
                "metadata": {
                    "author": post.metadata.author,
                    "tags": post.metadata.tags,
                    "word_count": post.metadata.word_count,
                    "read_time_minutes": post.metadata.read_time_minutes
                }
            }
        }
        
    except BlogPostException as e:
        logger.error("Failed to create blog post", error=str(e))
        raise HTTPException(status_code=400, detail=e.to_dict())
    except Exception as e:
        logger.error("Unexpected error creating blog post", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{post_id}", response_model=Dict[str, Any])
async def get_blog_post(
    post_id: str,
    blog_service: BlogPostService = Depends(get_blog_service)
):
    """Get a blog post by ID."""
    try:
        post = await blog_service.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        return {
            "success": True,
            "data": {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "status": post.status,
                "language": post.language,
                "tone": post.tone,
                "slug": post.slug,
                "featured": post.featured,
                "created_at": post.created_at.isoformat(),
                "updated_at": post.updated_at.isoformat() if post.updated_at else None,
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "metadata": {
                    "author": post.metadata.author,
                    "tags": post.metadata.tags,
                    "category": post.metadata.category,
                    "word_count": post.metadata.word_count,
                    "read_time_minutes": post.metadata.read_time_minutes,
                    "excerpt": post.metadata.excerpt
                },
                "seo": {
                    "title": post.seo.title,
                    "meta_description": post.seo.meta_description,
                    "keywords": post.seo.keywords,
                    "keyword_density": post.seo.keyword_density,
                    "readability_score": post.seo.readability_score
                } if post.seo else None,
                "analytics": {
                    "views": post.view_count,
                    "likes": post.like_count,
                    "shares": post.share_count
                }
            }
        }
        
    except Exception as e:
        logger.error("Failed to get blog post", post_id=post_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=Dict[str, Any])
async def list_blog_posts(
    status: Optional[BlogPostStatus] = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    blog_service: BlogPostService = Depends(get_blog_service)
):
    """List blog posts with optional filtering."""
    try:
        posts = await blog_service.list_posts(status=status, limit=limit, offset=offset)
        
        return {
            "success": True,
            "data": {
                "posts": [
                    {
                        "id": post.id,
                        "title": post.title,
                        "status": post.status,
                        "slug": post.slug,
                        "featured": post.featured,
                        "created_at": post.created_at.isoformat(),
                        "published_at": post.published_at.isoformat() if post.published_at else None,
                        "metadata": {
                            "author": post.metadata.author,
                            "tags": post.metadata.tags,
                            "category": post.metadata.category,
                            "excerpt": post.metadata.excerpt,
                            "read_time_minutes": post.metadata.read_time_minutes
                        },
                        "analytics": {
                            "views": post.view_count,
                            "likes": post.like_count,
                            "shares": post.share_count
                        }
                    }
                    for post in posts
                ],
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total_returned": len(posts)
                }
            }
        }
        
    except Exception as e:
        logger.error("Failed to list blog posts", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{post_id}", response_model=Dict[str, Any])
async def update_blog_post(
    post_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    status: Optional[BlogPostStatus] = None,
    tags: Optional[List[str]] = None,
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    blog_service: BlogPostService = Depends(get_blog_service)
):
    """Update a blog post."""
    try:
        updates = {}
        if title is not None:
            updates["title"] = title
        if content is not None:
            updates["content"] = content
        if status is not None:
            updates["status"] = status
        if featured is not None:
            updates["featured"] = featured
        
        # Handle metadata updates
        if tags is not None or category is not None:
            post = await blog_service.get_post(post_id)
            if not post:
                raise HTTPException(status_code=404, detail="Blog post not found")
            
            if tags is not None:
                post.metadata.tags = tags
            if category is not None:
                post.metadata.category = category
            
            updates["metadata"] = post.metadata
        
        post = await blog_service.update_post(post_id, **updates)
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        return {
            "success": True,
            "message": "Blog post updated successfully",
            "data": {
                "id": post.id,
                "title": post.title,
                "status": post.status,
                "updated_at": post.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update blog post", post_id=post_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{post_id}", response_model=Dict[str, Any])
async def delete_blog_post(
    post_id: str,
    blog_service: BlogPostService = Depends(get_blog_service)
):
    """Delete a blog post."""
    try:
        success = await blog_service.delete_post(post_id)
        if not success:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        return {
            "success": True,
            "message": "Blog post deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete blog post", post_id=post_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{post_id}/publish", response_model=Dict[str, Any])
async def publish_blog_post(
    post_id: str,
    platforms: List[str] = [],
    social_media_posts: bool = True,
    send_notifications: bool = True,
    blog_service: BlogPostService = Depends(get_blog_service),
    publishing_service: PublishingService = Depends(get_publishing_service)
):
    """Publish a blog post."""
    try:
        # First publish in the blog service
        success = await blog_service.publish_post(post_id)
        if not success:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        # Get the post for publishing
        post = await blog_service.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        # Publish to external platforms if specified
        results = {}
        if platforms:
            publishing_config = PublishingConfig(
                platforms=platforms,
                social_media_posts=social_media_posts,
                send_notifications=send_notifications
            )
            
            results = await publishing_service.publish_post(post, publishing_config)
        
        return {
            "success": True,
            "message": "Blog post published successfully",
            "data": {
                "id": post.id,
                "status": post.status,
                "published_at": post.published_at.isoformat(),
                "publishing_results": results
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to publish blog post", post_id=post_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/generate", response_model=Dict[str, Any])
async def generate_blog_content(
    request: ContentRequest,
    content_generator: ContentGeneratorService = Depends(get_content_generator)
):
    """Generate AI-powered blog content."""
    try:
        result = await content_generator.generate_content(request)
        
        return {
            "success": result.success,
            "data": {
                "content": result.content,
                "title": result.title,
                "outline": result.outline,
                "seo_data": {
                    "title": result.seo_data.title,
                    "meta_description": result.seo_data.meta_description,
                    "keywords": result.seo_data.keywords,
                    "keyword_density": result.seo_data.keyword_density,
                    "readability_score": result.seo_data.readability_score
                } if result.seo_data else None,
                "metadata": {
                    "generation_time_ms": result.generation_time_ms,
                    "word_count": result.word_count
                }
            },
            "errors": result.errors,
            "warnings": result.warnings
        }
        
    except Exception as e:
        logger.error("Failed to generate content", error=str(e))
        raise HTTPException(status_code=500, detail="Content generation failed")


@router.post("/generate/batch", response_model=Dict[str, Any])
async def generate_batch_content(
    requests: List[ContentRequest],
    background_tasks: BackgroundTasks,
    content_generator: ContentGeneratorService = Depends(get_content_generator)
):
    """Generate multiple blog contents in batch."""
    try:
        if len(requests) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 requests allowed per batch")
        
        # Process in background for large batches
        if len(requests) > 3:
            background_tasks.add_task(
                _process_batch_generation,
                content_generator,
                requests
            )
            
            return {
                "success": True,
                "message": "Batch generation started in background",
                "data": {
                    "batch_size": len(requests),
                    "status": "processing"
                }
            }
        
        # Process immediately for small batches
        results = await content_generator.generate_batch(requests)
        
        return {
            "success": True,
            "data": {
                "results": [
                    {
                        "success": result.success,
                        "content": result.content,
                        "title": result.title,
                        "word_count": result.word_count,
                        "generation_time_ms": result.generation_time_ms,
                        "errors": result.errors
                    }
                    for result in results
                ],
                "summary": {
                    "total": len(results),
                    "successful": len([r for r in results if r.success]),
                    "failed": len([r for r in results if not r.success])
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate batch content", error=str(e))
        raise HTTPException(status_code=500, detail="Batch content generation failed")


@router.post("/{post_id}/optimize-seo", response_model=Dict[str, Any])
async def optimize_seo(
    post_id: str,
    seo_config: SEOConfig,
    blog_service: BlogPostService = Depends(get_blog_service),
    seo_optimizer: SEOOptimizerService = Depends(get_seo_optimizer)
):
    """Optimize SEO for a blog post."""
    try:
        post = await blog_service.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        optimized_post = await seo_optimizer.optimize_post(post, seo_config)
        
        # Update the post in the service
        await blog_service.update_post(post_id, seo=optimized_post.seo)
        
        return {
            "success": True,
            "message": "SEO optimization completed",
            "data": {
                "id": optimized_post.id,
                "seo": {
                    "title": optimized_post.seo.title,
                    "meta_description": optimized_post.seo.meta_description,
                    "keywords": optimized_post.seo.keywords,
                    "keyword_density": optimized_post.seo.keyword_density,
                    "readability_score": optimized_post.seo.readability_score,
                    "schema_markup": optimized_post.seo.schema_markup
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to optimize SEO", post_id=post_id, error=str(e))
        raise HTTPException(status_code=500, detail="SEO optimization failed")


async def _process_batch_generation(
    content_generator: ContentGeneratorService,
    requests: List[ContentRequest]
):
    """Background task to process batch content generation."""
    try:
        results = await content_generator.generate_batch(requests)
        logger.info("Batch generation completed", 
                   total=len(results),
                   successful=len([r for r in results if r.success]))
    except Exception as e:
        logger.error("Batch generation failed", error=str(e))


# Export the router
__all__ = ["router"] 