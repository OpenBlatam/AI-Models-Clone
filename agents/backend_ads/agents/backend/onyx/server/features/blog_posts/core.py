"""
Core Services for Blog Post Management.

This module contains the main business logic services for blog post management,
including content generation, SEO optimization, and publishing.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
import structlog

from .models import (
    BlogPost, BlogPostMetadata, ContentRequest, ContentGenerationResult,
    SEOData, SEOConfig, PublishingConfig, BlogPostBatch
)
from .config import BlogPostConfig, ContentLanguage, ContentTone, BlogPostStatus
from .exceptions import BlogPostException, ContentGenerationError, SEOOptimizationError
from .utils import (
    validate_content, sanitize_html, calculate_reading_time,
    generate_slug, extract_keywords, calculate_keyword_density
)

logger = structlog.get_logger(__name__)


class BlogPostService:
    """Main service for blog post management."""
    
    def __init__(self, config: BlogPostConfig):
        self.config = config
        self.posts_cache: Dict[str, BlogPost] = {}
        self.logger = logger.bind(service="blog_post")
        
    async def create_post(
        self,
        title: str,
        content: str,
        metadata: BlogPostMetadata,
        seo_data: Optional[SEOData] = None
    ) -> BlogPost:
        """Create a new blog post."""
        try:
            # Validate content
            validation_result = validate_content(content)
            if not validation_result["is_valid"]:
                raise BlogPostException(f"Content validation failed: {validation_result['errors']}")
            
            # Sanitize content if enabled
            if self.config.enable_html_sanitization:
                content = sanitize_html(content)
            
            # Calculate metadata
            word_count = len(content.split())
            read_time = calculate_reading_time(content)
            
            # Update metadata
            metadata.word_count = word_count
            metadata.read_time_minutes = read_time
            
            # Create blog post
            post = BlogPost(
                title=title,
                content=content,
                metadata=metadata,
                seo=seo_data,
                slug=generate_slug(title)
            )
            
            # Cache the post
            self.posts_cache[post.id] = post
            
            self.logger.info("Blog post created", post_id=post.id, title=title)
            return post
            
        except Exception as e:
            self.logger.error("Failed to create blog post", error=str(e))
            raise BlogPostException(f"Failed to create blog post: {str(e)}")
    
    async def get_post(self, post_id: str) -> Optional[BlogPost]:
        """Retrieve a blog post by ID."""
        try:
            return self.posts_cache.get(post_id)
        except Exception as e:
            self.logger.error("Failed to retrieve blog post", post_id=post_id, error=str(e))
            return None
    
    async def update_post(self, post_id: str, **updates) -> Optional[BlogPost]:
        """Update a blog post."""
        try:
            post = self.posts_cache.get(post_id)
            if not post:
                return None
            
            # Update fields
            for field, value in updates.items():
                if hasattr(post, field):
                    setattr(post, field, value)
            
            # Update timestamp
            post.update_timestamp()
            
            # Re-cache
            self.posts_cache[post_id] = post
            
            self.logger.info("Blog post updated", post_id=post_id)
            return post
            
        except Exception as e:
            self.logger.error("Failed to update blog post", post_id=post_id, error=str(e))
            return None
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete a blog post."""
        try:
            if post_id in self.posts_cache:
                del self.posts_cache[post_id]
                self.logger.info("Blog post deleted", post_id=post_id)
                return True
            return False
        except Exception as e:
            self.logger.error("Failed to delete blog post", post_id=post_id, error=str(e))
            return False
    
    async def list_posts(
        self,
        status: Optional[BlogPostStatus] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[BlogPost]:
        """List blog posts with optional filtering."""
        try:
            posts = list(self.posts_cache.values())
            
            # Filter by status
            if status:
                posts = [p for p in posts if p.status == status]
            
            # Sort by creation date (newest first)
            posts.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            return posts[offset:offset + limit]
            
        except Exception as e:
            self.logger.error("Failed to list blog posts", error=str(e))
            return []
    
    async def publish_post(self, post_id: str) -> bool:
        """Publish a blog post."""
        try:
            post = self.posts_cache.get(post_id)
            if not post:
                return False
            
            post.publish()
            self.posts_cache[post_id] = post
            
            self.logger.info("Blog post published", post_id=post_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to publish blog post", post_id=post_id, error=str(e))
            return False


class ContentGeneratorService:
    """Service for AI-powered content generation."""
    
    def __init__(self, config: BlogPostConfig):
        self.config = config
        self.logger = logger.bind(service="content_generator")
        
    async def generate_content(self, request: ContentRequest) -> ContentGenerationResult:
        """Generate content based on request."""
        start_time = time.time()
        
        try:
            # Simulate AI content generation
            # In a real implementation, this would call OpenAI, Claude, etc.
            content = await self._generate_ai_content(request)
            title = await self._generate_title(request)
            outline = await self._generate_outline(request) if request.include_outline else None
            seo_data = await self._generate_seo_data(request) if request.include_seo else None
            
            generation_time = int((time.time() - start_time) * 1000)
            word_count = len(content.split()) if content else 0
            
            result = ContentGenerationResult(
                success=True,
                content=content,
                title=title,
                outline=outline,
                seo_data=seo_data,
                generation_time_ms=generation_time,
                word_count=word_count
            )
            
            self.logger.info(
                "Content generated successfully",
                topic=request.topic,
                word_count=word_count,
                generation_time_ms=generation_time
            )
            
            return result
            
        except Exception as e:
            self.logger.error("Content generation failed", error=str(e))
            return ContentGenerationResult(
                success=False,
                errors=[str(e)]
            )
    
    async def _generate_ai_content(self, request: ContentRequest) -> str:
        """Generate AI content (placeholder implementation)."""
        # This would integrate with actual AI providers
        await asyncio.sleep(0.5)  # Simulate API call
        
        return f"""
        # {request.topic}
        
        ## Introduction
        
        This article explores {request.topic.lower()} for {request.target_audience.lower()}. 
        The content is tailored to provide valuable insights and actionable information.
        
        ## Main Content
        
        {request.topic} is becoming increasingly important in today's digital landscape. 
        Here are the key points to consider:
        
        1. **Understanding the Basics**: Every professional should understand the fundamentals.
        2. **Implementation Strategies**: Practical approaches for real-world application.
        3. **Best Practices**: Proven methods that deliver results.
        4. **Future Trends**: What to expect in the coming years.
        
        ## Key Benefits
        
        - Improved efficiency and productivity
        - Better decision-making capabilities
        - Enhanced competitive advantage
        - Streamlined processes and workflows
        
        ## Conclusion
        
        Understanding and implementing {request.topic.lower()} is crucial for success in today's environment. 
        By following the strategies outlined in this article, {request.target_audience.lower()} can achieve 
        significant improvements in their operations and outcomes.
        
        ## Call to Action
        
        Ready to get started? Contact our team of experts to learn more about how we can help you 
        implement these strategies in your organization.
        """
    
    async def _generate_title(self, request: ContentRequest) -> str:
        """Generate an optimized title."""
        await asyncio.sleep(0.1)  # Simulate processing
        return f"The Complete Guide to {request.topic} for {request.target_audience}"
    
    async def _generate_outline(self, request: ContentRequest) -> List[str]:
        """Generate content outline."""
        await asyncio.sleep(0.1)  # Simulate processing
        return [
            "Introduction",
            f"Understanding {request.topic}",
            "Key Benefits and Advantages",
            "Implementation Strategies",
            "Best Practices and Tips",
            "Common Challenges and Solutions",
            "Future Trends and Predictions",
            "Conclusion and Next Steps"
        ]
    
    async def _generate_seo_data(self, request: ContentRequest) -> SEOData:
        """Generate SEO optimized data."""
        await asyncio.sleep(0.1)  # Simulate processing
        
        title = f"Complete {request.topic} Guide for {request.target_audience}"
        description = f"Discover everything you need to know about {request.topic.lower()}. " \
                     f"Expert insights and practical tips for {request.target_audience.lower()}."
        
        return SEOData(
            title=title[:60],  # Truncate if too long
            meta_description=description[:160],  # Truncate if too long
            keywords=request.keywords[:5],  # Limit keywords
            keyword_density=1.5,
            readability_score=75.0
        )
    
    async def generate_batch(self, requests: List[ContentRequest]) -> List[ContentGenerationResult]:
        """Generate content for multiple requests."""
        if not self.config.enable_batch_processing:
            # Process sequentially
            results = []
            for request in requests:
                result = await self.generate_content(request)
                results.append(result)
            return results
        
        # Process in batches
        batch_size = self.config.batch_size
        results = []
        
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.generate_content(req) for req in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append(ContentGenerationResult(
                        success=False,
                        errors=[str(result)]
                    ))
                else:
                    results.append(result)
        
        return results


class SEOOptimizerService:
    """Service for SEO optimization."""
    
    def __init__(self, config: BlogPostConfig):
        self.config = config
        self.logger = logger.bind(service="seo_optimizer")
    
    async def optimize_post(self, post: BlogPost, seo_config: SEOConfig) -> BlogPost:
        """Optimize a blog post for SEO."""
        try:
            # Analyze current content
            analysis = await self._analyze_content(post.content, seo_config.target_keywords)
            
            # Generate SEO data if not present
            if not post.seo:
                post.seo = await self._generate_seo_data(post, seo_config)
            
            # Update SEO data based on analysis
            post.seo.keyword_density = analysis["keyword_density"]
            post.seo.readability_score = analysis["readability_score"]
            
            # Generate schema markup if enabled
            if seo_config.include_schema_markup:
                post.seo.schema_markup = await self._generate_schema_markup(post)
            
            self.logger.info("SEO optimization completed", post_id=post.id)
            return post
            
        except Exception as e:
            self.logger.error("SEO optimization failed", post_id=post.id, error=str(e))
            raise SEOOptimizationError(f"SEO optimization failed: {str(e)}")
    
    async def _analyze_content(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze content for SEO metrics."""
        # Calculate keyword density
        keyword_density = calculate_keyword_density(content, keywords)
        
        # Calculate readability score (simplified)
        words = content.split()
        sentences = content.split('.')
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        readability_score = max(0, 100 - (avg_sentence_length * 1.5))
        
        return {
            "keyword_density": keyword_density,
            "readability_score": readability_score,
            "word_count": len(words),
            "sentence_count": len(sentences)
        }
    
    async def _generate_seo_data(self, post: BlogPost, config: SEOConfig) -> SEOData:
        """Generate SEO data for a post."""
        # Generate optimized title
        title = post.title
        if len(title) > self.config.max_title_length:
            title = title[:self.config.max_title_length-3] + "..."
        
        # Generate meta description
        description = post.metadata.excerpt or post.content[:200] + "..."
        if len(description) > self.config.max_description_length:
            description = description[:self.config.max_description_length-3] + "..."
        
        return SEOData(
            title=title,
            meta_description=description,
            keywords=config.target_keywords,
            keyword_density=config.keyword_density_target,
            readability_score=config.readability_target
        )
    
    async def _generate_schema_markup(self, post: BlogPost) -> Dict[str, Any]:
        """Generate schema.org markup for the post."""
        return {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post.title,
            "description": post.seo.meta_description if post.seo else "",
            "author": {
                "@type": "Person",
                "name": post.metadata.author
            },
            "datePublished": post.published_at.isoformat() if post.published_at else None,
            "dateModified": post.updated_at.isoformat() if post.updated_at else None,
            "wordCount": post.metadata.word_count,
            "keywords": post.seo.keywords if post.seo else []
        }


class PublishingService:
    """Service for publishing blog posts."""
    
    def __init__(self, config: BlogPostConfig):
        self.config = config
        self.logger = logger.bind(service="publishing")
    
    async def publish_post(
        self,
        post: BlogPost,
        publishing_config: PublishingConfig
    ) -> Dict[str, Any]:
        """Publish a blog post to configured platforms."""
        try:
            results = {}
            
            # Validate post is ready for publishing
            if not self._validate_for_publishing(post):
                raise BlogPostException("Post is not ready for publishing")
            
            # Publish to each platform
            for platform in publishing_config.platforms:
                try:
                    result = await self._publish_to_platform(post, platform)
                    results[platform] = {"success": True, "result": result}
                except Exception as e:
                    results[platform] = {"success": False, "error": str(e)}
            
            # Generate social media posts if enabled
            if publishing_config.social_media_posts:
                social_results = await self._generate_social_posts(post)
                results["social_media"] = social_results
            
            # Send notifications if enabled
            if publishing_config.send_notifications:
                await self._send_notifications(post)
                results["notifications"] = {"success": True}
            
            self.logger.info("Post published successfully", post_id=post.id, platforms=publishing_config.platforms)
            return results
            
        except Exception as e:
            self.logger.error("Publishing failed", post_id=post.id, error=str(e))
            raise BlogPostException(f"Publishing failed: {str(e)}")
    
    def _validate_for_publishing(self, post: BlogPost) -> bool:
        """Validate that a post is ready for publishing."""
        if not post.title or len(post.title.strip()) < 10:
            return False
        if not post.content or len(post.content.strip()) < 100:
            return False
        if not post.metadata.author:
            return False
        return True
    
    async def _publish_to_platform(self, post: BlogPost, platform: str) -> Dict[str, Any]:
        """Publish to a specific platform."""
        # This would integrate with actual publishing platforms
        await asyncio.sleep(0.5)  # Simulate API call
        
        return {
            "platform": platform,
            "post_id": post.id,
            "url": f"https://{platform}.com/posts/{post.slug}",
            "published_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _generate_social_posts(self, post: BlogPost) -> Dict[str, Any]:
        """Generate social media posts."""
        await asyncio.sleep(0.2)  # Simulate processing
        
        return {
            "twitter": f"New blog post: {post.title} - {post.seo.meta_description if post.seo else ''} #blog",
            "linkedin": f"I just published a new article: {post.title}. {post.seo.meta_description if post.seo else ''}",
            "facebook": f"Check out my latest blog post: {post.title}"
        }
    
    async def _send_notifications(self, post: BlogPost) -> None:
        """Send notifications about the published post."""
        await asyncio.sleep(0.1)  # Simulate sending
        self.logger.info("Notifications sent", post_id=post.id)


# Export all services
__all__ = [
    "BlogPostService",
    "ContentGeneratorService",
    "SEOOptimizerService",
    "PublishingService"
] 