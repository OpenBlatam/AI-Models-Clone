"""
High-Level Service Interfaces.

Defines protocols for main application services and configuration management.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Protocol
from ..models import BlogPost, BlogPostMetadata, ContentRequest, SEOConfig, PublishingConfig
from ..config import BlogPostConfig


class IBlogPostService(Protocol):
    """Protocol for the main blog post service."""
    
    @abstractmethod
    async def create_post(
        self,
        title: str,
        content: str,
        metadata: BlogPostMetadata,
        seo_data: Optional[Dict[str, Any]] = None
    ) -> BlogPost:
        """Create a new blog post."""
        ...
    
    @abstractmethod
    async def get_post(self, post_id: str) -> Optional[BlogPost]:
        """Get a blog post by ID."""
        ...
    
    @abstractmethod
    async def update_post(self, post_id: str, **updates) -> Optional[BlogPost]:
        """Update a blog post."""
        ...
    
    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        """Delete a blog post."""
        ...
    
    @abstractmethod
    async def list_posts(
        self,
        status: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[BlogPost]:
        """List blog posts with filtering."""
        ...
    
    @abstractmethod
    async def publish_post(self, post_id: str) -> bool:
        """Publish a blog post."""
        ...
    
    @abstractmethod
    async def generate_content(self, request: ContentRequest) -> Dict[str, Any]:
        """Generate AI-powered content."""
        ...
    
    @abstractmethod
    async def optimize_seo(self, post_id: str, config: SEOConfig) -> BlogPost:
        """Optimize SEO for a post."""
        ...
    
    @abstractmethod
    async def publish_to_platforms(self, post_id: str, config: PublishingConfig) -> Dict[str, Any]:
        """Publish to external platforms."""
        ...


class IConfigurationService(Protocol):
    """Protocol for configuration management."""
    
    @abstractmethod
    def get_config(self) -> BlogPostConfig:
        """Get current configuration."""
        ...
    
    @abstractmethod
    def update_config(self, updates: Dict[str, Any]) -> BlogPostConfig:
        """Update configuration."""
        ...
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration."""
        ...
    
    @abstractmethod
    def reset_config(self) -> BlogPostConfig:
        """Reset configuration to defaults."""
        ...
    
    @abstractmethod
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags."""
        ...
    
    @abstractmethod
    def set_feature_flag(self, flag_name: str, enabled: bool) -> bool:
        """Set a feature flag."""
        ...


class IHealthCheckService(Protocol):
    """Protocol for health check and monitoring."""
    
    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        ...
    
    @abstractmethod
    async def check_dependencies(self) -> Dict[str, Any]:
        """Check external dependencies."""
        ...
    
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        ...
    
    @abstractmethod
    async def get_version_info(self) -> Dict[str, Any]:
        """Get version information."""
        ...


class IEventService(Protocol):
    """Protocol for event handling and pub/sub."""
    
    @abstractmethod
    async def publish_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Publish an event."""
        ...
    
    @abstractmethod
    async def subscribe_to_event(self, event_type: str, handler: callable) -> bool:
        """Subscribe to an event type."""
        ...
    
    @abstractmethod
    async def unsubscribe_from_event(self, event_type: str, handler: callable) -> bool:
        """Unsubscribe from an event type."""
        ...
    
    @abstractmethod
    async def get_event_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get event history."""
        ...


class ISecurityService(Protocol):
    """Protocol for security and access control."""
    
    @abstractmethod
    async def authenticate_user(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Authenticate a user."""
        ...
    
    @abstractmethod
    async def authorize_action(self, user_id: str, action: str, resource: str) -> bool:
        """Check if user is authorized for an action."""
        ...
    
    @abstractmethod
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions."""
        ...
    
    @abstractmethod
    async def audit_log(self, user_id: str, action: str, resource: str, result: str) -> bool:
        """Log an audit event."""
        ...


class IPerformanceService(Protocol):
    """Protocol for performance monitoring and optimization."""
    
    @abstractmethod
    async def track_operation(self, operation: str, duration: float, metadata: Dict[str, Any]) -> bool:
        """Track operation performance."""
        ...
    
    @abstractmethod
    async def get_performance_stats(self, time_range: str = "hour") -> Dict[str, Any]:
        """Get performance statistics."""
        ...
    
    @abstractmethod
    async def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks."""
        ...
    
    @abstractmethod
    async def optimize_performance(self, optimization_type: str) -> Dict[str, Any]:
        """Run performance optimizations."""
        ... 