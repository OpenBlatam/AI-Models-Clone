"""
SEO Management Interfaces.

Defines protocols for SEO optimization, analysis, and keyword management.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Protocol
from ..models import BlogPost, SEOData, SEOConfig


class ISEOOptimizer(Protocol):
    """Protocol for SEO optimization services."""
    
    @abstractmethod
    async def optimize_post(self, post: BlogPost, config: SEOConfig) -> BlogPost:
        """Optimize a blog post for SEO."""
        ...
    
    @abstractmethod
    async def generate_meta_tags(self, post: BlogPost) -> Dict[str, str]:
        """Generate meta tags for a post."""
        ...
    
    @abstractmethod
    async def generate_schema_markup(self, post: BlogPost) -> Dict[str, Any]:
        """Generate schema.org markup."""
        ...
    
    @abstractmethod
    async def optimize_title(self, title: str, keywords: List[str]) -> str:
        """Optimize title for SEO."""
        ...
    
    @abstractmethod
    async def optimize_description(self, content: str, max_length: int = 160) -> str:
        """Generate optimized meta description."""
        ...


class ISEOAnalyzer(Protocol):
    """Protocol for SEO analysis services."""
    
    @abstractmethod
    async def analyze_content(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze content for SEO metrics."""
        ...
    
    @abstractmethod
    def calculate_keyword_density(self, content: str, keywords: List[str]) -> float:
        """Calculate keyword density."""
        ...
    
    @abstractmethod
    def calculate_readability_score(self, content: str) -> float:
        """Calculate readability score."""
        ...
    
    @abstractmethod
    def analyze_heading_structure(self, content: str) -> Dict[str, Any]:
        """Analyze heading structure."""
        ...
    
    @abstractmethod
    def check_internal_links(self, content: str) -> Dict[str, Any]:
        """Check internal linking structure."""
        ...
    
    @abstractmethod
    def validate_seo_requirements(self, post: BlogPost, config: SEOConfig) -> Dict[str, Any]:
        """Validate SEO requirements."""
        ...


class IKeywordExtractor(Protocol):
    """Protocol for keyword extraction services."""
    
    @abstractmethod
    def extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from content."""
        ...
    
    @abstractmethod
    async def suggest_keywords(self, topic: str, audience: str) -> List[str]:
        """Suggest relevant keywords for a topic."""
        ...
    
    @abstractmethod
    def analyze_keyword_competition(self, keywords: List[str]) -> Dict[str, float]:
        """Analyze keyword competition scores."""
        ...
    
    @abstractmethod
    def find_long_tail_keywords(self, seed_keyword: str) -> List[str]:
        """Find long-tail keyword variations."""
        ...
    
    @abstractmethod
    def calculate_keyword_relevance(self, keyword: str, content: str) -> float:
        """Calculate keyword relevance score."""
        ...


class ISEOReporter(Protocol):
    """Protocol for SEO reporting services."""
    
    @abstractmethod
    async def generate_seo_report(self, post: BlogPost) -> Dict[str, Any]:
        """Generate comprehensive SEO report."""
        ...
    
    @abstractmethod
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate SEO improvement recommendations."""
        ...
    
    @abstractmethod
    async def track_seo_metrics(self, post_id: str, metrics: Dict[str, Any]) -> bool:
        """Track SEO metrics over time."""
        ...
    
    @abstractmethod
    async def compare_seo_performance(self, post_ids: List[str]) -> Dict[str, Any]:
        """Compare SEO performance across posts."""
        ...


class ISEOConfigManager(Protocol):
    """Protocol for SEO configuration management."""
    
    @abstractmethod
    def get_seo_config(self, level: str = "advanced") -> SEOConfig:
        """Get SEO configuration by level."""
        ...
    
    @abstractmethod
    def validate_seo_config(self, config: SEOConfig) -> Dict[str, Any]:
        """Validate SEO configuration."""
        ...
    
    @abstractmethod
    async def update_seo_rules(self, rules: Dict[str, Any]) -> bool:
        """Update SEO optimization rules."""
        ...
    
    @abstractmethod
    def get_keyword_limits(self) -> Dict[str, int]:
        """Get keyword usage limits."""
        ... 