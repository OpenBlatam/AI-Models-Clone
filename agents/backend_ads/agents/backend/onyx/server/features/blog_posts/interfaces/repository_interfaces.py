"""
Repository Interfaces for Data Access Layer.

Defines protocols for data persistence and retrieval operations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Protocol
from datetime import datetime
from ..models import BlogPost, BlogPostMetadata, SEOData


class IBlogPostRepository(Protocol):
    """Protocol for blog post data access."""
    
    @abstractmethod
    async def create(self, post: BlogPost) -> BlogPost:
        """Create a new blog post."""
        ...
    
    @abstractmethod
    async def get_by_id(self, post_id: str) -> Optional[BlogPost]:
        """Get blog post by ID."""
        ...
    
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[BlogPost]:
        """Get blog post by slug."""
        ...
    
    @abstractmethod
    async def update(self, post_id: str, updates: Dict[str, Any]) -> Optional[BlogPost]:
        """Update a blog post."""
        ...
    
    @abstractmethod
    async def delete(self, post_id: str) -> bool:
        """Delete a blog post."""
        ...
    
    @abstractmethod
    async def list_posts(
        self,
        status: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> List[BlogPost]:
        """List blog posts with filtering and pagination."""
        ...
    
    @abstractmethod
    async def search_posts(self, query: str, limit: int = 10) -> List[BlogPost]:
        """Search blog posts by content."""
        ...
    
    @abstractmethod
    async def get_posts_by_author(self, author: str, limit: int = 10) -> List[BlogPost]:
        """Get posts by author."""
        ...
    
    @abstractmethod
    async def get_posts_by_tags(self, tags: List[str], limit: int = 10) -> List[BlogPost]:
        """Get posts by tags."""
        ...
    
    @abstractmethod
    async def get_posts_by_category(self, category: str, limit: int = 10) -> List[BlogPost]:
        """Get posts by category."""
        ...
    
    @abstractmethod
    async def get_featured_posts(self, limit: int = 5) -> List[BlogPost]:
        """Get featured posts."""
        ...
    
    @abstractmethod
    async def get_related_posts(self, post_id: str, limit: int = 5) -> List[BlogPost]:
        """Get related posts based on tags and category."""
        ...


class IAnalyticsRepository(Protocol):
    """Protocol for analytics data access."""
    
    @abstractmethod
    async def track_view(self, post_id: str, visitor_data: Dict[str, Any]) -> bool:
        """Track a post view."""
        ...
    
    @abstractmethod
    async def track_engagement(self, post_id: str, engagement_type: str, data: Dict[str, Any]) -> bool:
        """Track engagement events."""
        ...
    
    @abstractmethod
    async def get_post_analytics(self, post_id: str, time_range: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics for a specific post."""
        ...
    
    @abstractmethod
    async def get_author_analytics(self, author: str, time_range: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics for an author."""
        ...
    
    @abstractmethod
    async def get_category_analytics(self, category: str, time_range: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics for a category."""
        ...
    
    @abstractmethod
    async def get_popular_posts(self, time_range: str = "week", limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular posts by views/engagement."""
        ...
    
    @abstractmethod
    async def get_trending_topics(self, time_range: str = "week", limit: int = 10) -> List[str]:
        """Get trending topics/tags."""
        ...


class IContentRepository(Protocol):
    """Protocol for content-specific data access."""
    
    @abstractmethod
    async def save_draft(self, post_id: str, content: str) -> bool:
        """Save content as draft."""
        ...
    
    @abstractmethod
    async def get_draft(self, post_id: str) -> Optional[str]:
        """Get draft content."""
        ...
    
    @abstractmethod
    async def save_version(self, post_id: str, version: int, content: str) -> bool:
        """Save content version."""
        ...
    
    @abstractmethod
    async def get_version(self, post_id: str, version: int) -> Optional[str]:
        """Get specific content version."""
        ...
    
    @abstractmethod
    async def list_versions(self, post_id: str) -> List[Dict[str, Any]]:
        """List all versions of a post."""
        ...
    
    @abstractmethod
    async def restore_version(self, post_id: str, version: int) -> bool:
        """Restore content to a specific version."""
        ...


class IMediaRepository(Protocol):
    """Protocol for media/asset data access."""
    
    @abstractmethod
    async def upload_image(self, file_data: bytes, filename: str, metadata: Dict[str, Any]) -> str:
        """Upload and store an image."""
        ...
    
    @abstractmethod
    async def get_image(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get image metadata and URL."""
        ...
    
    @abstractmethod
    async def delete_image(self, image_id: str) -> bool:
        """Delete an image."""
        ...
    
    @abstractmethod
    async def list_images(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List uploaded images."""
        ...
    
    @abstractmethod
    async def optimize_image(self, image_id: str, optimization_params: Dict[str, Any]) -> str:
        """Optimize image and return new URL."""
        ...


class ICacheRepository(Protocol):
    """Protocol for caching operations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        ...
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        ...
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        ...
    
    @abstractmethod
    async def clear_pattern(self, pattern: str) -> bool:
        """Clear cache entries matching pattern."""
        ...
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        ...
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        ... 