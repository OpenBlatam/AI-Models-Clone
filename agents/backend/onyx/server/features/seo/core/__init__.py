"""
Core module for ultra-optimized SEO service.
Contains the fundamental components and interfaces.
"""

from .interfaces import HTMLParser, HTTPClient, CacheManager, SEOAnalyzer
from .parsers import SelectolaxUltraParser, LXMLFallbackParser
from .http_client import UltraFastHTTPClient
from .cache_manager import UltraOptimizedCacheManager
from .analyzer import UltraFastSEOAnalyzer
from .metrics import SEOMetrics, PerformanceTracker

__all__ = [
    'HTMLParser',
    'HTTPClient', 
    'CacheManager',
    'SEOAnalyzer',
    'SelectolaxUltraParser',
    'LXMLFallbackParser',
    'UltraFastHTTPClient',
    'UltraOptimizedCacheManager',
    'UltraFastSEOAnalyzer',
    'SEOMetrics',
    'PerformanceTracker'
] 