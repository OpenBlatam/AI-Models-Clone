"""
🎯 Facebook Posts - Onyx Features Module
========================================

Módulo refactorizado para la arquitectura de features de Onyx.
"""

from .facebook_posts_onyx_model import (
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

__version__ = "2.1.0"
__all__ = [
    "PostType", "ContentTone", "TargetAudience", "EngagementTier", "ContentStatus",
    "ContentIdentifier", "ContentSpecification", "GenerationConfig",
    "ContentMetrics", "EngagementPrediction", "QualityAssessment", 
    "FacebookPostContent", "FacebookPostAnalysis", "FacebookPostEntity",
    "ContentGenerationService", "ContentAnalysisService", "FacebookPostRepository",
    "FacebookPostFactory", "create_demo_post", "demo_analysis"
] 