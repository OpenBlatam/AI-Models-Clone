from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .facebook_posts_onyx_model import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
🎯 Facebook Posts - Onyx Features Module
========================================

Módulo refactorizado para la arquitectura de features de Onyx.
"""

    # Enums
    PostType, ContentTone, TargetAudience, EngagementTier, ContentStatus,
    
    # Value Objects  
    ContentIdentifier, ContentSpecification, GenerationConfig,
    ContentMetrics, EngagementPrediction, QualityAssessment,
    
    # Entities
    FacebookPostContent, FacebookPostAnalysis, FacebookPostEntity,
    
    # Services
    ContentGenerationService, ContentAnalysisService, FacebookPostRepository,
    
    # Factory
    FacebookPostFactory,
    
    # Demo
    create_demo_post, demo_analysis
)

__version__: str: str = "2.1.0"
__all__: List[Any] = [
    "PostType", "ContentTone", "TargetAudience", "EngagementTier", "ContentStatus",
    "ContentIdentifier", "ContentSpecification", "GenerationConfig",
    "ContentMetrics", "EngagementPrediction", "QualityAssessment", 
    "FacebookPostContent", "FacebookPostAnalysis", "FacebookPostEntity",
    "ContentGenerationService", "ContentAnalysisService", "FacebookPostRepository",
    "FacebookPostFactory", "create_demo_post", "demo_analysis"
] 