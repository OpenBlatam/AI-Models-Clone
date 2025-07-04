"""
Core Copywriting System
=======================

This module contains the core components of the copywriting system:
- Engine: Main processing engine
- Models: Data models and schemas
- Services: Business logic services
- Utils: Utility functions
"""

from .engine import CopywritingEngine
from .models import CopywritingRequest, CopywritingResponse, CopywritingVariant
from .services import CopywritingService, OptimizationService, CacheService

__all__ = [
    'CopywritingEngine',
    'CopywritingRequest', 
    'CopywritingResponse',
    'CopywritingVariant',
    'CopywritingService',
    'OptimizationService',
    'CacheService'
] 