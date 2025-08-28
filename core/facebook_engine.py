from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..models.facebook_models import (
from ..services.langchain_service import FacebookLangChainService
from ..utils.facebook_utils import FacebookUtils
        import hashlib
from typing import Any, List, Dict, Optional
"""
🎯 Facebook Post Engine
=======================

Motor principal para generación y análisis de Facebook posts.
Integrado con LangChain y optimizado para Onyx.
"""


# Onyx imports
    FacebookPost, FacebookRequest, FacebookAnalysis, FacebookPostResponse,
    FacebookFingerprint, FacebookTone, FacebookPostType, EngagementLevel
)

logger = logging.getLogger(__name__)


class FacebookPostEngine:
    """Motor principal para Facebook posts con LangChain."""
    
    def __init__(self, langchain_service: FacebookLangChainService):
        
    """__init__ function."""
self.langchain_service = langchain_service
        self.utils = FacebookUtils()
        self.cache = {}
        self.analytics = {
            'posts_generated': 0,
            'posts_analyzed': 0,
            'total_processing_time': 0.0,
            'cache_hits': 0,
            'langchain_calls': 0
        }
        self.logger = logger
    
    async def generate_post(self, request: FacebookRequest) -> FacebookPostResponse:
        """Generar Facebook post usando LangChain."""
        start_time = time.perf_counter()
        
        try:
            self.logger.info(f"Generating Facebook post for topic: {request.content_topic}")
            
            # Check cache first
            cache_key = self._get_cache_key(request)
            if cache_key in self.cache:
                self.analytics['cache_hits'] += 1
                cached_result = self.cache[cache_key]
                self.logger.info("Returning cached Facebook post")
                return cached_result
            
            # Generate post using LangChain
            generated_post = await self._generate_with_langchain(request)
            
            # Analyze the generated post
            analysis = await self.analyze_post(generated_post)
            generated_post.analysis = analysis
            
            # Generate variations
            variations = await self._generate_variations(generated_post, request)
            
            # Get recommendations
            recommendations = await self._get_recommendations(generated_post, analysis)
            
            processing_time = (time.perf_counter() - start_time) * 1000
            
            response = FacebookPostResponse(
                success=True,
                post=generated_post,
                variations=variations,
                analysis=analysis,
                recommendations=recommendations,
                processing_time_ms=processing_time
            )
            
            # Cache the response
            self.cache[cache_key] = response
            
            # Update analytics
            self.analytics['posts_generated'] += 1
            self.analytics['total_processing_time'] += processing_time
            
            self.logger.info(f"Facebook post generated successfully in {processing_time:.0f}ms")
            return response
            
        except Exception as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            error_msg = f"Error generating Facebook post: {str(e)}"
            self.logger.error(error_msg)
            
            return FacebookPostResponse(
                success=False,
                processing_time_ms=processing_time,
                error_message=error_msg
            )
    
    async def _generate_with_langchain(self, request: FacebookRequest) -> FacebookPost:
        """Generar post usando LangChain."""
        self.analytics['langchain_calls'] += 1
        
        # Prepare prompt context
        prompt_context = {
            'topic': request.content_topic,
            'tone': request.tone.value,
            'audience': request.target_audience.value,
            'post_type': request.post_type.value,
            'max_length': request.max_length,
            'include_hashtags': request.include_hashtags,
            'include_emoji': request.include_emoji,
            'include_call_to_action': request.include_call_to_action,
            'keywords': request.keywords,
            'brand_voice': request.brand_voice or "neutral",
            'campaign_context': request.campaign_context or "general",
            'target_engagement': request.target_engagement.value
        }
        
        # Generate content using LangChain
        generation_result = await self.langchain_service.generate_facebook_post(prompt_context)
        
        # Create fingerprint
        fingerprint = FacebookFingerprint.create(
            generation_result['content'], 
            request.post_type
        )
        
        # Extract hashtags and mentions
        hashtags = self.utils.extract_hashtags(generation_result['content'])
        mentions = self.utils.extract_mentions(generation_result['content'])
        
        # Clean content (remove hashtags if they'll be added separately)
        clean_content = self.utils.clean_content_for_display(
            generation_result['content'],
            separate_hashtags=request.include_hashtags
        )
        
        # Create Facebook post
        facebook_post = FacebookPost(
            fingerprint=fingerprint,
            post_type=request.post_type,
            text_content=clean_content,
            hashtags=hashtags if request.include_hashtags else [],
            mentions=mentions,
            tone=request.tone,
            target_audience=request.target_audience,
            langchain_metadata=generation_result.get('metadata', {}),
            generation_metrics=generation_result.get('metrics', {})
        )
        
        return facebook_post
    
    async def analyze_post(self, post: FacebookPost) -> FacebookAnalysis:
        """Analizar un Facebook post."""
        try:
            self.logger.info(f"Analyzing Facebook post: {post.fingerprint.post_id}")
            
            # Use LangChain for analysis
            analysis_result = await self.langchain_service.analyze_facebook_post(
                post.text_content,
                {
                    'post_type': post.post_type.value,
                    'tone': post.tone.value,
                    'audience': post.target_audience.value,
                    'hashtags': post.hashtags,
                    'has_media': bool(post.image_urls or post.video_url)
                }
            )
            
            # Create analysis object
            analysis = FacebookAnalysis(
                engagement_prediction=analysis_result.get('engagement_prediction', 0.5),
                virality_score=analysis_result.get('virality_score', 0.3),
                sentiment_score=analysis_result.get('sentiment_score', 0.5),
                readability_score=analysis_result.get('readability_score', 0.7),
                brand_alignment=analysis_result.get('brand_alignment', 0.6),
                predicted_likes=analysis_result.get('predicted_likes', 100),
                predicted_shares=analysis_result.get('predicted_shares', 20),
                predicted_comments=analysis_result.get('predicted_comments', 15),
                predicted_reach=analysis_result.get('predicted_reach', 1000),
                strengths=analysis_result.get('strengths', []),
                improvements=analysis_result.get('improvements', []),
                hashtag_suggestions=analysis_result.get('hashtag_suggestions', []),
                similar_successful_posts=analysis_result.get('similar_posts', [])
            )
            
            # Set optimal posting time
            analysis.optimal_posting_time = await self._calculate_optimal_time(post)
            
            self.analytics['posts_analyzed'] += 1
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing Facebook post: {e}")
            
            # Return default analysis
            return FacebookAnalysis(
                engagement_prediction=0.5,
                virality_score=0.3,
                sentiment_score=0.5,
                readability_score=0.7,
                brand_alignment=0.6,
                predicted_likes=100,
                predicted_shares=20,
                predicted_comments=15,
                predicted_reach=1000,
                strengths=["Post created successfully"],
                improvements=["Analysis unavailable - using defaults"]
            )
    
    async def _generate_variations(self, base_post: FacebookPost, request: FacebookRequest) -> List[FacebookPost]:
        """Generar variaciones del post base."""
        variations = []
        
        try:
            # Generate tone variations
            alternative_tones = self._get_alternative_tones(request.tone)
            
            for tone in alternative_tones[:2]:  # Limit to 2 variations
                variation_request = FacebookRequest(
                    content_topic=request.content_topic,
                    post_type=request.post_type,
                    tone=tone,
                    target_audience=request.target_audience,
                    max_length=request.max_length,
                    include_hashtags=request.include_hashtags,
                    include_emoji=request.include_emoji,
                    include_call_to_action=request.include_call_to_action,
                    keywords=request.keywords,
                    brand_voice=request.brand_voice,
                    campaign_context=request.campaign_context,
                    target_engagement=request.target_engagement
                )
                
                variation = await self._generate_with_langchain(variation_request)
                variations.append(variation)
                
        except Exception as e:
            self.logger.warning(f"Error generating variations: {e}")
        
        return variations
    
    async def _get_recommendations(self, post: FacebookPost, analysis: FacebookAnalysis) -> List[str]:
        """Obtener recomendaciones para el post."""
        recommendations = []
        
        try:
            # Use LangChain to generate recommendations
            rec_result = await self.langchain_service.get_post_recommendations(
                post.text_content,
                {
                    'analysis': {
                        'engagement_prediction': analysis.engagement_prediction,
                        'virality_score': analysis.virality_score,
                        'sentiment_score': analysis.sentiment_score,
                        'readability_score': analysis.readability_score
                    },
                    'post_type': post.post_type.value,
                    'character_count': post.get_character_count(),
                    'has_hashtags': bool(post.hashtags),
                    'has_mentions': bool(post.mentions)
                }
            )
            
            recommendations = rec_result.get('recommendations', [])
            
            # Add basic recommendations if none provided
            if not recommendations:
                recommendations = self._get_basic_recommendations(post, analysis)
                
        except Exception as e:
            self.logger.warning(f"Error getting recommendations: {e}")
            recommendations = self._get_basic_recommendations(post, analysis)
        
        return recommendations
    
    def _get_basic_recommendations(self, post: FacebookPost, analysis: FacebookAnalysis) -> List[str]:
        """Obtener recomendaciones básicas."""
        recommendations = []
        
        # Character count recommendations
        char_count = post.get_character_count()
        if char_count < 100:
            recommendations.append("Consider adding more content to increase engagement")
        elif char_count > 1500:
            recommendations.append("Consider shortening the post for better readability")
        
        # Hashtag recommendations
        if not post.hashtags:
            recommendations.append("Add relevant hashtags to increase discoverability")
        elif len(post.hashtags) > 10:
            recommendations.append("Reduce hashtags - Facebook performs better with 3-5 hashtags")
        
        # Engagement recommendations
        if analysis.engagement_prediction < 0.5:
            recommendations.append("Consider adding a call-to-action to improve engagement")
            recommendations.append("Try using more engaging language or questions")
        
        # Virality recommendations
        if analysis.virality_score < 0.4:
            recommendations.append("Add trending topics or current events to increase virality")
            recommendations.append("Consider including visual elements for better performance")
        
        return recommendations
    
    def _get_alternative_tones(self, current_tone: FacebookTone) -> List[FacebookTone]:
        """Obtener tonos alternativos para variaciones."""
        tone_alternatives = {
            FacebookTone.CASUAL: [FacebookTone.FRIENDLY, FacebookTone.HUMOROUS],
            FacebookTone.PROFESSIONAL: [FacebookTone.EDUCATIONAL, FacebookTone.INSPIRING],
            FacebookTone.FRIENDLY: [FacebookTone.CASUAL, FacebookTone.INSPIRING],
            FacebookTone.HUMOROUS: [FacebookTone.CASUAL, FacebookTone.FRIENDLY],
            FacebookTone.INSPIRING: [FacebookTone.PROFESSIONAL, FacebookTone.EDUCATIONAL],
            FacebookTone.PROMOTIONAL: [FacebookTone.PROFESSIONAL, FacebookTone.INSPIRING],
            FacebookTone.EDUCATIONAL: [FacebookTone.PROFESSIONAL, FacebookTone.FRIENDLY],
            FacebookTone.CONTROVERSIAL: [FacebookTone.PROFESSIONAL, FacebookTone.CASUAL]
        }
        
        return tone_alternatives.get(current_tone, [FacebookTone.CASUAL, FacebookTone.FRIENDLY])
    
    async def _calculate_optimal_time(self, post: FacebookPost) -> Optional[datetime]:
        """Calcular tiempo óptimo de publicación."""
        try:
            # Use LangChain to predict optimal timing
            timing_result = await self.langchain_service.predict_optimal_timing(
                {
                    'content': post.text_content,
                    'post_type': post.post_type.value,
                    'audience': post.target_audience.value,
                    'tone': post.tone.value
                }
            )
            
            return timing_result.get('optimal_time')
            
        except Exception as e:
            self.logger.warning(f"Error calculating optimal time: {e}")
            return None
    
    def _get_cache_key(self, request: FacebookRequest) -> str:
        """Generar clave de cache para el request."""
        
        key_data = f"{request.content_topic}_{request.post_type}_{request.tone}_{request.target_audience}_{request.max_length}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_analytics(self) -> Dict[str, Any]:
        """Obtener analytics del motor."""
        return {
            **self.analytics,
            'cache_size': len(self.cache),
            'avg_processing_time': (
                self.analytics['total_processing_time'] / max(self.analytics['posts_generated'], 1)
            ),
            'cache_hit_rate': (
                self.analytics['cache_hits'] / max(self.analytics['posts_generated'], 1)
            )
        }
    
    def clear_cache(self) -> Any:
        """Limpiar cache del motor."""
        self.cache.clear()
        self.logger.info("Facebook post engine cache cleared") 