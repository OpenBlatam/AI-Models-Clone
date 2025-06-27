"""
🎯 Facebook Posts API
=====================

API endpoints para el sistema de Facebook posts integrado con Onyx y LangChain.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
import time

# Onyx imports
from ..models.facebook_models import (
    FacebookRequest, FacebookPost, FacebookPostResponse, 
    FacebookAnalysis, FacebookAnalysisResponse, FacebookTone, 
    FacebookPostType, FacebookAudience, EngagementLevel
)
from ..core.facebook_engine import FacebookPostEngine
from ..services.langchain_service import FacebookLangChainService
from ..config.langchain_config import get_facebook_langchain_config
from ..utils.facebook_utils import FacebookUtils

# Dependencies for Onyx integration
from ...auth.authentication import get_current_user
from ...db.database import get_database_session

logger = logging.getLogger(__name__)

# Router setup
router = APIRouter(
    prefix="/facebook_posts",
    tags=["Facebook Posts"],
    responses={404: {"description": "Not found"}}
)

# Service instances (will be initialized)
facebook_engine: Optional[FacebookPostEngine] = None
langchain_service: Optional[FacebookLangChainService] = None


async def get_facebook_engine() -> FacebookPostEngine:
    """Dependency para obtener Facebook engine."""
    global facebook_engine, langchain_service
    
    if not facebook_engine:
        try:
            # Initialize LangChain service
            config = get_facebook_langchain_config("production")
            langchain_service = FacebookLangChainService(config)
            
            # Initialize Facebook engine
            facebook_engine = FacebookPostEngine(langchain_service)
            
            logger.info("Facebook engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Facebook engine: {e}")
            raise HTTPException(
                status_code=500,
                detail="Facebook service unavailable"
            )
    
    return facebook_engine


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check del servicio Facebook posts."""
    try:
        engine = await get_facebook_engine()
        analytics = engine.get_analytics()
        
        return {
            "status": "healthy",
            "service": "Facebook Posts with LangChain",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "analytics": analytics,
            "langchain_available": langchain_service is not None,
            "features": {
                "post_generation": True,
                "post_analysis": True,
                "langchain_integration": True,
                "onyx_integration": True,
                "async_processing": True
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Generate Facebook post
@router.post("/generate", response_model=FacebookPostResponse)
async def generate_facebook_post(
    request: FacebookRequest,
    background_tasks: BackgroundTasks,
    engine: FacebookPostEngine = Depends(get_facebook_engine),
    # current_user = Depends(get_current_user),  # Onyx auth
    # db_session = Depends(get_database_session)  # Onyx DB
):
    """
    Generar Facebook post usando LangChain.
    
    Features:
    - Generación inteligente con LangChain
    - Análisis automático de engagement
    - Variaciones A/B automáticas
    - Recomendaciones de optimización
    - Integración completa con Onyx
    """
    try:
        logger.info(f"Generating Facebook post for topic: {request.content_topic}")
        
        # Validate request
        if not request.content_topic or len(request.content_topic.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Content topic must be at least 3 characters long"
            )
        
        # Generate post using engine
        result = await engine.generate_post(request)
        
        # Log analytics in background
        background_tasks.add_task(
            log_generation_analytics,
            request.content_topic,
            request.post_type.value,
            result.processing_time_ms
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating Facebook post: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Facebook post: {str(e)}"
        )


# Analyze existing Facebook post
@router.post("/analyze", response_model=FacebookAnalysisResponse)
async def analyze_facebook_post(
    content: str,
    post_type: FacebookPostType = FacebookPostType.TEXT,
    context: Optional[Dict[str, Any]] = None,
    engine: FacebookPostEngine = Depends(get_facebook_engine),
    # current_user = Depends(get_current_user)
):
    """
    Analizar Facebook post existente.
    
    Features:
    - Análisis de engagement con LangChain
    - Predicción de viralidad
    - Score de legibilidad
    - Recomendaciones de mejora
    - Análisis competitivo
    """
    try:
        start_time = time.perf_counter()
        
        # Validate content
        if not content or len(content.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Content must be at least 10 characters long"
            )
        
        # Create mock post for analysis
        from ..models.facebook_models import FacebookFingerprint
        fingerprint = FacebookFingerprint.create(content, post_type)
        
        mock_post = FacebookPost(
            fingerprint=fingerprint,
            post_type=post_type,
            text_content=content,
            tone=FacebookTone.CASUAL,
            target_audience=FacebookAudience.GENERAL
        )
        
        # Analyze post
        analysis = await engine.analyze_post(mock_post)
        
        # Get additional insights
        insights = await get_post_insights(content, analysis)
        
        # Get optimization suggestions
        optimization_suggestions = await get_optimization_suggestions(mock_post, analysis)
        
        # Competitive analysis (mock)
        competitive_analysis = await get_competitive_analysis(content)
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        return FacebookAnalysisResponse(
            success=True,
            analysis=analysis,
            insights=insights,
            optimization_suggestions=optimization_suggestions,
            competitive_analysis=competitive_analysis,
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing Facebook post: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze Facebook post: {str(e)}"
        )


# Get post variations
@router.post("/variations")
async def get_post_variations(
    base_request: FacebookRequest,
    variation_count: int = Query(3, ge=1, le=5),
    engine: FacebookPostEngine = Depends(get_facebook_engine)
):
    """
    Generar variaciones de un Facebook post para A/B testing.
    """
    try:
        variations = []
        
        # Generate multiple variations with different tones
        tones = [FacebookTone.CASUAL, FacebookTone.PROFESSIONAL, FacebookTone.FRIENDLY]
        
        for i, tone in enumerate(tones[:variation_count]):
            variation_request = FacebookRequest(
                content_topic=base_request.content_topic,
                post_type=base_request.post_type,
                tone=tone,
                target_audience=base_request.target_audience,
                max_length=base_request.max_length,
                include_hashtags=base_request.include_hashtags,
                include_emoji=base_request.include_emoji,
                keywords=base_request.keywords,
                brand_voice=base_request.brand_voice
            )
            
            result = await engine.generate_post(variation_request)
            if result.success and result.post:
                variations.append({
                    "variation_id": f"var_{i+1}",
                    "tone": tone.value,
                    "post": result.post,
                    "analysis": result.analysis
                })
        
        return {
            "success": True,
            "base_topic": base_request.content_topic,
            "variations": variations,
            "total_variations": len(variations)
        }
        
    except Exception as e:
        logger.error(f"Error generating variations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate variations: {str(e)}"
        )


# Optimize existing post
@router.post("/optimize")
async def optimize_facebook_post(
    content: str,
    target_engagement: EngagementLevel = EngagementLevel.HIGH,
    focus_areas: List[str] = Query(["engagement", "readability", "virality"]),
    engine: FacebookPostEngine = Depends(get_facebook_engine)
):
    """
    Optimizar Facebook post existente usando LangChain.
    """
    try:
        # Analyze current post
        utils = FacebookUtils()
        current_analysis = utils.analyze_post_structure(content)
        
        # Create optimization request using LangChain
        optimization_context = {
            "original_content": content,
            "target_engagement": target_engagement.value,
            "focus_areas": focus_areas,
            "current_metrics": current_analysis
        }
        
        # Use LangChain to generate optimized version
        optimized_result = await langchain_service.generate_facebook_post({
            "topic": f"Optimize this content for {target_engagement.value} engagement",
            "tone": "optimized",
            "audience": "general",
            "max_length": len(content) + 100,  # Allow slightly longer
            "include_hashtags": True,
            "include_emoji": True,
            "keywords": focus_areas,
            "optimization_context": optimization_context
        })
        
        # Create optimized post
        from ..models.facebook_models import FacebookFingerprint
        fingerprint = FacebookFingerprint.create(optimized_result['content'])
        
        optimized_post = FacebookPost(
            fingerprint=fingerprint,
            post_type=FacebookPostType.TEXT,
            text_content=optimized_result['content'],
            tone=FacebookTone.CASUAL,
            target_audience=FacebookAudience.GENERAL,
            langchain_metadata=optimized_result.get('metadata', {})
        )
        
        # Analyze optimized version
        optimized_analysis = await engine.analyze_post(optimized_post)
        
        # Calculate improvement metrics
        improvements = calculate_improvements(current_analysis, optimized_analysis)
        
        return {
            "success": True,
            "original_content": content,
            "optimized_post": optimized_post,
            "optimized_analysis": optimized_analysis,
            "improvements": improvements,
            "optimization_focus": focus_areas
        }
        
    except Exception as e:
        logger.error(f"Error optimizing post: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize post: {str(e)}"
        )


# Get trending topics for Facebook
@router.get("/trending")
async def get_trending_topics(
    audience: FacebookAudience = FacebookAudience.GENERAL,
    count: int = Query(10, ge=1, le=20)
):
    """
    Obtener temas trending para Facebook posts.
    """
    try:
        # In a real implementation, this would call social media APIs
        # For now, we'll return mock trending topics
        
        trending_topics = [
            {"topic": "Artificial Intelligence", "trend_score": 0.95, "hashtags": ["#AI", "#Tech", "#Innovation"]},
            {"topic": "Sustainable Living", "trend_score": 0.87, "hashtags": ["#Sustainability", "#EcoFriendly", "#GreenLiving"]},
            {"topic": "Remote Work", "trend_score": 0.82, "hashtags": ["#RemoteWork", "#DigitalNomad", "#WorkFromHome"]},
            {"topic": "Social Media Marketing", "trend_score": 0.78, "hashtags": ["#SocialMedia", "#Marketing", "#DigitalMarketing"]},
            {"topic": "Mental Health Awareness", "trend_score": 0.75, "hashtags": ["#MentalHealth", "#Wellness", "#SelfCare"]},
            {"topic": "Cryptocurrency", "trend_score": 0.73, "hashtags": ["#Crypto", "#Bitcoin", "#Blockchain"]},
            {"topic": "Fitness and Wellness", "trend_score": 0.70, "hashtags": ["#Fitness", "#Wellness", "#HealthyLifestyle"]},
            {"topic": "Online Learning", "trend_score": 0.68, "hashtags": ["#OnlineLearning", "#Education", "#SkillDevelopment"]},
            {"topic": "Food Photography", "trend_score": 0.65, "hashtags": ["#FoodPhotography", "#Foodie", "#DeliciousFood"]},
            {"topic": "Travel Planning", "trend_score": 0.62, "hashtags": ["#Travel", "#TravelPlanning", "#Wanderlust"]}
        ]
        
        # Filter and sort by relevance to audience
        filtered_topics = trending_topics[:count]
        
        return {
            "success": True,
            "audience": audience.value,
            "trending_topics": filtered_topics,
            "timestamp": datetime.now().isoformat(),
            "total_topics": len(filtered_topics)
        }
        
    except Exception as e:
        logger.error(f"Error getting trending topics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get trending topics: {str(e)}"
        )


# Get service analytics
@router.get("/analytics")
async def get_service_analytics(
    engine: FacebookPostEngine = Depends(get_facebook_engine)
):
    """
    Obtener analytics del servicio Facebook posts.
    """
    try:
        engine_analytics = engine.get_analytics()
        langchain_metrics = langchain_service.get_metrics() if langchain_service else {}
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "engine_analytics": engine_analytics,
            "langchain_metrics": langchain_metrics,
            "service_health": {
                "uptime": "N/A",  # Would track actual uptime
                "status": "operational",
                "langchain_available": langchain_service is not None,
                "onyx_integration": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics: {str(e)}"
        )


# Utility functions
async def get_post_insights(content: str, analysis: FacebookAnalysis) -> List[str]:
    """Obtener insights del post."""
    insights = []
    
    # Engagement insights
    if analysis.engagement_prediction > 0.7:
        insights.append("High engagement potential - content is likely to perform well")
    elif analysis.engagement_prediction < 0.4:
        insights.append("Low engagement predicted - consider adding more engaging elements")
    
    # Virality insights
    if analysis.virality_score > 0.6:
        insights.append("Content has strong viral potential")
    
    # Sentiment insights
    if analysis.sentiment_score > 0.7:
        insights.append("Positive sentiment detected - likely to generate good reactions")
    elif analysis.sentiment_score < 0.3:
        insights.append("Negative sentiment detected - may need tone adjustment")
    
    # Structure insights
    utils = FacebookUtils()
    structure = utils.analyze_post_structure(content)
    
    if structure.get('has_question', False):
        insights.append("Questions encourage engagement and comments")
    
    if structure.get('emoji_count', 0) > 0:
        insights.append("Emojis improve visual appeal and engagement")
    
    return insights


async def get_optimization_suggestions(post: FacebookPost, analysis: FacebookAnalysis) -> List[str]:
    """Obtener sugerencias de optimización."""
    suggestions = []
    
    # Engagement optimization
    if analysis.engagement_prediction < 0.5:
        suggestions.append("Add a question to encourage comments")
        suggestions.append("Include a call-to-action to drive engagement")
    
    # Hashtag optimization
    if len(post.hashtags) == 0:
        suggestions.append("Add 3-5 relevant hashtags to increase discoverability")
    elif len(post.hashtags) > 8:
        suggestions.append("Reduce hashtags to 3-5 for optimal performance")
    
    # Content length optimization
    char_count = post.get_character_count()
    if char_count < 50:
        suggestions.append("Consider adding more content for better engagement")
    elif char_count > 1000:
        suggestions.append("Consider shortening the post for better readability")
    
    # Visual optimization
    if not post.image_urls and not post.video_url:
        suggestions.append("Add visual content (image/video) to increase engagement")
    
    return suggestions


async def get_competitive_analysis(content: str) -> Dict[str, Any]:
    """Obtener análisis competitivo (mock)."""
    # In a real implementation, this would analyze similar content from competitors
    return {
        "similar_posts_found": 5,
        "avg_engagement_rate": 0.034,
        "top_performing_keywords": ["innovation", "technology", "future"],
        "recommended_timing": "2:00 PM - 4:00 PM",
        "audience_overlap": 0.45
    }


def calculate_improvements(original_analysis: Dict[str, Any], optimized_analysis: FacebookAnalysis) -> Dict[str, Any]:
    """Calcular métricas de mejora."""
    return {
        "engagement_improvement": "+15%",  # Mock calculation
        "readability_improvement": "+22%",
        "viral_potential_improvement": "+8%",
        "overall_score_improvement": "+18%"
    }


async def log_generation_analytics(topic: str, post_type: str, processing_time: float):
    """Log analytics en background."""
    try:
        logger.info(f"Analytics: Generated {post_type} post about '{topic}' in {processing_time:.0f}ms")
        # Here you would save to Onyx database
        
    except Exception as e:
        logger.error(f"Error logging analytics: {e}")


# Initialize service on startup
@router.on_event("startup")
async def startup_event():
    """Initialize Facebook service on startup."""
    try:
        await get_facebook_engine()
        logger.info("Facebook Posts API initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Facebook Posts API: {e}") 