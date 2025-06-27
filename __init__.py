"""
🎯 Facebook Posts - Onyx Features Module
========================================

Modelo completamente refactorizado con Clean Architecture.
Ubicado en: /features/facebook_posts/
"""

from .facebook_posts_model import (
    # Domain Enums
    PostType,
    ContentTone,
    TargetAudience,
    EngagementTier,
    ContentStatus,
    
    # Value Objects
    ContentIdentifier,
    PostSpecification,
    ContentMetrics,
    EngagementPrediction,
    
    # Entities
    PostContent,
    PostAnalysis,
    FacebookPost,
    
    # Services (Protocols)
    ContentGenerationService,
    ContentAnalysisService,
    ContentOptimizationService,
    FacebookPostRepository,
    
    # Factory
    FacebookPostFactory,
    
    # Demo functions
    create_demo_post,
    create_demo_analysis,
    demo_complete_workflow
)

__version__ = "2.0.0"
__author__ = "Onyx Features Team"

# Exports principales
__all__ = [
    # Enums
    "PostType",
    "ContentTone", 
    "TargetAudience",
    "EngagementTier",
    "ContentStatus",
    
    # Value Objects
    "ContentIdentifier",
    "PostSpecification",
    "ContentMetrics",
    "EngagementPrediction",
    
    # Entities
    "PostContent",
    "PostAnalysis",
    "FacebookPost",
    
    # Services
    "ContentGenerationService",
    "ContentAnalysisService",
    "ContentOptimizationService", 
    "FacebookPostRepository",
    
    # Factory
    "FacebookPostFactory",
    
    # Demo
    "create_demo_post",
    "create_demo_analysis",
    "demo_complete_workflow"
] 