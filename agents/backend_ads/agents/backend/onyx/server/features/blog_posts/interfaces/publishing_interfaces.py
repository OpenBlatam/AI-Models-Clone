"""
Publishing Management Interfaces.

Defines protocols for publishing, notifications, and social media integration.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Protocol
from datetime import datetime
from ..models import BlogPost, PublishingConfig


class IPublisher(Protocol):
    """Protocol for publishing services."""
    
    @abstractmethod
    async def publish_post(self, post: BlogPost, config: PublishingConfig) -> Dict[str, Any]:
        """Publish a blog post to configured platforms."""
        ...
    
    @abstractmethod
    async def publish_to_platform(self, post: BlogPost, platform: str) -> Dict[str, Any]:
        """Publish to a specific platform."""
        ...
    
    @abstractmethod
    async def schedule_publish(self, post: BlogPost, publish_time: datetime) -> bool:
        """Schedule a post for future publishing."""
        ...
    
    @abstractmethod
    async def unpublish_post(self, post_id: str, platform: str) -> bool:
        """Unpublish a post from a platform."""
        ...
    
    @abstractmethod
    async def get_publishing_status(self, post_id: str) -> Dict[str, Any]:
        """Get publishing status for a post."""
        ...
    
    @abstractmethod
    def validate_for_publishing(self, post: BlogPost) -> Dict[str, Any]:
        """Validate that a post is ready for publishing."""
        ...


class INotificationService(Protocol):
    """Protocol for notification services."""
    
    @abstractmethod
    async def send_publication_notification(self, post: BlogPost, recipients: List[str]) -> bool:
        """Send notification about post publication."""
        ...
    
    @abstractmethod
    async def send_email_notification(self, subject: str, body: str, recipients: List[str]) -> bool:
        """Send email notification."""
        ...
    
    @abstractmethod
    async def send_webhook_notification(self, webhook_url: str, data: Dict[str, Any]) -> bool:
        """Send webhook notification."""
        ...
    
    @abstractmethod
    async def send_slack_notification(self, channel: str, message: str) -> bool:
        """Send Slack notification."""
        ...
    
    @abstractmethod
    async def schedule_notification(self, notification_time: datetime, message: str, recipients: List[str]) -> bool:
        """Schedule a notification for future delivery."""
        ...


class ISocialMediaService(Protocol):
    """Protocol for social media integration services."""
    
    @abstractmethod
    async def generate_social_posts(self, post: BlogPost) -> Dict[str, str]:
        """Generate social media posts for different platforms."""
        ...
    
    @abstractmethod
    async def post_to_twitter(self, message: str, media: Optional[List[str]] = None) -> Dict[str, Any]:
        """Post to Twitter."""
        ...
    
    @abstractmethod
    async def post_to_linkedin(self, message: str, media: Optional[List[str]] = None) -> Dict[str, Any]:
        """Post to LinkedIn."""
        ...
    
    @abstractmethod
    async def post_to_facebook(self, message: str, media: Optional[List[str]] = None) -> Dict[str, Any]:
        """Post to Facebook."""
        ...
    
    @abstractmethod
    async def schedule_social_post(self, platform: str, message: str, publish_time: datetime) -> bool:
        """Schedule a social media post."""
        ...
    
    @abstractmethod
    async def get_social_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get social media analytics for a post."""
        ...


class IPlatformAdapter(Protocol):
    """Protocol for platform-specific adapters."""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with the platform."""
        ...
    
    @abstractmethod
    async def publish_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Publish content to the platform."""
        ...
    
    @abstractmethod
    async def update_content(self, content_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing content on the platform."""
        ...
    
    @abstractmethod
    async def delete_content(self, content_id: str) -> bool:
        """Delete content from the platform."""
        ...
    
    @abstractmethod
    async def get_content_status(self, content_id: str) -> Dict[str, Any]:
        """Get content status from the platform."""
        ...
    
    @abstractmethod
    def format_content_for_platform(self, post: BlogPost) -> Dict[str, Any]:
        """Format blog post content for the specific platform."""
        ...


class IScheduler(Protocol):
    """Protocol for scheduling services."""
    
    @abstractmethod
    async def schedule_task(self, task_name: str, execution_time: datetime, task_data: Dict[str, Any]) -> str:
        """Schedule a task for execution."""
        ...
    
    @abstractmethod
    async def cancel_scheduled_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        ...
    
    @abstractmethod
    async def get_scheduled_tasks(self, task_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of scheduled tasks."""
        ...
    
    @abstractmethod
    async def reschedule_task(self, task_id: str, new_time: datetime) -> bool:
        """Reschedule an existing task."""
        ...


class IAnalyticsCollector(Protocol):
    """Protocol for analytics collection services."""
    
    @abstractmethod
    async def track_publication(self, post_id: str, platform: str, metrics: Dict[str, Any]) -> bool:
        """Track publication metrics."""
        ...
    
    @abstractmethod
    async def track_engagement(self, post_id: str, engagement_data: Dict[str, Any]) -> bool:
        """Track engagement metrics."""
        ...
    
    @abstractmethod
    async def get_publication_analytics(self, post_id: str, time_range: Optional[str] = None) -> Dict[str, Any]:
        """Get publication analytics."""
        ...
    
    @abstractmethod
    async def get_platform_performance(self, platform: str, time_range: Optional[str] = None) -> Dict[str, Any]:
        """Get platform-specific performance metrics."""
        ... 