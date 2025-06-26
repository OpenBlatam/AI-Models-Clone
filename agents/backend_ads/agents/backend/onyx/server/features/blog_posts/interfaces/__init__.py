"""
Interfaces and Protocols for Blog Posts Module.

This module defines the contracts and interfaces for different components
of the blog post management system, promoting loose coupling and testability.
"""

from .content_interfaces import (
    IContentGenerator,
    IContentValidator,
    IContentProcessor
)
from .seo_interfaces import (
    ISEOOptimizer,
    ISEOAnalyzer,
    IKeywordExtractor
)
from .publishing_interfaces import (
    IPublisher,
    INotificationService,
    ISocialMediaService
)
from .repository_interfaces import (
    IBlogPostRepository,
    IAnalyticsRepository
)
from .service_interfaces import (
    IBlogPostService,
    IConfigurationService
)

__all__ = [
    # Content interfaces
    "IContentGenerator",
    "IContentValidator", 
    "IContentProcessor",
    # SEO interfaces
    "ISEOOptimizer",
    "ISEOAnalyzer",
    "IKeywordExtractor",
    # Publishing interfaces
    "IPublisher",
    "INotificationService",
    "ISocialMediaService",
    # Repository interfaces
    "IBlogPostRepository",
    "IAnalyticsRepository",
    # Service interfaces
    "IBlogPostService",
    "IConfigurationService"
] 