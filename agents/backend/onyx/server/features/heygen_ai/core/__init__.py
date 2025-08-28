"""
HeyGen AI Core Module
Main entry point for the HeyGen AI equivalent system.
"""

import logging
import asyncio

__version__ = "1.0.0"
__author__ = "Blatam Academy"

# Only import modules that don't have relative import issues
try:
    from .external_api_integration import (
        ExternalAPIManager, ServiceConfig, ServiceType, 
        ElevenLabsService, SocialMediaService, CloudStorageService, AnalyticsService
    )
    EXTERNAL_API_AVAILABLE = True
except ImportError:
    EXTERNAL_API_AVAILABLE = False
    logging.warning("External API integration not available")

try:
    from .performance_optimizer import (
        PerformanceOptimizer, MultiLevelCache, MemoryCache, RedisCache,
        LoadBalancer, PerformanceMonitor, BackgroundTaskProcessor
    )
    PERFORMANCE_OPTIMIZER_AVAILABLE = True
except ImportError:
    PERFORMANCE_OPTIMIZER_AVAILABLE = False
    logging.warning("Performance optimizer not available")

try:
    from .langchain_manager import LangChainManager
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain manager not available")

__all__ = [
    "ExternalAPIManager",
    "ServiceConfig", 
    "ServiceType",
    "ElevenLabsService",
    "SocialMediaService",
    "CloudStorageService",
    "AnalyticsService",
    "PerformanceOptimizer",
    "MultiLevelCache",
    "MemoryCache",
    "RedisCache",
    "LoadBalancer",
    "PerformanceMonitor",
    "BackgroundTaskProcessor",
    "LangChainManager"
] 