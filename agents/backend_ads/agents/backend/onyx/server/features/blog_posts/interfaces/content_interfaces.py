"""
Content Management Interfaces.

Defines protocols for content generation, validation, and processing.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Protocol
from ..models import ContentRequest, ContentGenerationResult, BlogPost


class IContentGenerator(Protocol):
    """Protocol for content generation services."""
    
    @abstractmethod
    async def generate_content(self, request: ContentRequest) -> ContentGenerationResult:
        """Generate content based on request."""
        ...
    
    @abstractmethod
    async def generate_batch(self, requests: List[ContentRequest]) -> List[ContentGenerationResult]:
        """Generate multiple contents in batch."""
        ...
    
    @abstractmethod
    async def generate_title(self, request: ContentRequest) -> str:
        """Generate an optimized title."""
        ...
    
    @abstractmethod
    async def generate_outline(self, request: ContentRequest) -> List[str]:
        """Generate content outline."""
        ...


class IContentValidator(Protocol):
    """Protocol for content validation services."""
    
    @abstractmethod
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate content structure and quality."""
        ...
    
    @abstractmethod
    def validate_title(self, title: str) -> Dict[str, Any]:
        """Validate title format and length."""
        ...
    
    @abstractmethod
    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate blog post metadata."""
        ...


class IContentProcessor(Protocol):
    """Protocol for content processing services."""
    
    @abstractmethod
    def sanitize_html(self, content: str) -> str:
        """Sanitize HTML content."""
        ...
    
    @abstractmethod
    def format_content(self, content: str) -> str:
        """Auto-format content for better readability."""
        ...
    
    @abstractmethod
    def generate_excerpt(self, content: str, max_length: int = 200) -> str:
        """Generate excerpt from content."""
        ...
    
    @abstractmethod
    def calculate_reading_time(self, content: str) -> int:
        """Calculate estimated reading time."""
        ...
    
    @abstractmethod
    def calculate_readability_score(self, content: str) -> float:
        """Calculate readability score."""
        ...


class IContentTemplateEngine(Protocol):
    """Protocol for content template management."""
    
    @abstractmethod
    async def load_template(self, template_name: str) -> str:
        """Load a content template."""
        ...
    
    @abstractmethod
    async def render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template with variables."""
        ...
    
    @abstractmethod
    async def list_templates(self) -> List[str]:
        """List available templates."""
        ...


class IContentEnrichmentService(Protocol):
    """Protocol for content enrichment services."""
    
    @abstractmethod
    async def add_related_links(self, content: str, topic: str) -> str:
        """Add related links to content."""
        ...
    
    @abstractmethod
    async def add_images(self, content: str, topic: str) -> str:
        """Add relevant images to content."""
        ...
    
    @abstractmethod
    async def add_citations(self, content: str, sources: List[str]) -> str:
        """Add citations to content."""
        ... 