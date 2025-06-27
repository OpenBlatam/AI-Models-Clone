"""
🧪 Facebook Posts Tests
======================

Tests básicos para el sistema de Facebook posts con LangChain.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# Import models
from ..models.facebook_models import (
    FacebookRequest, FacebookPost, FacebookAnalysis, FacebookFingerprint,
    FacebookTone, FacebookPostType, FacebookAudience, EngagementLevel
)
from ..core.facebook_engine import FacebookPostEngine
from ..services.langchain_service import FacebookLangChainService
from ..utils.facebook_utils import FacebookUtils
from ..config.langchain_config import FacebookLangChainConfig


class TestFacebookModels:
    """Tests para modelos de Facebook."""
    
    def test_facebook_fingerprint_creation(self):
        """Test creación de fingerprint."""
        content = "Test Facebook post content"
        fingerprint = FacebookFingerprint.create(content)
        
        assert fingerprint.post_id is not None
        assert fingerprint.content_hash is not None
        assert len(fingerprint.content_hash) == 32  # MD5 hash
        assert fingerprint.platform_version == "facebook_v1.0"
        assert isinstance(fingerprint.timestamp, datetime)
    
    def test_facebook_request_validation(self):
        """Test validación de FacebookRequest."""
        # Valid request
        request = FacebookRequest(
            content_topic="Test topic",
            post_type=FacebookPostType.TEXT,
            tone=FacebookTone.CASUAL,
            target_audience=FacebookAudience.GENERAL,
            max_length=280
        )
        
        assert request.content_topic == "Test topic"
        assert request.post_type == FacebookPostType.TEXT
        assert request.tone == FacebookTone.CASUAL
    
    def test_facebook_request_max_length_validation(self):
        """Test validación de longitud máxima."""
        with pytest.raises(ValueError):
            FacebookRequest(
                content_topic="Test",
                max_length=30  # Too short
            )
        
        with pytest.raises(ValueError):
            FacebookRequest(
                content_topic="Test",
                max_length=3000  # Too long
            )
    
    def test_facebook_post_creation(self):
        """Test creación de FacebookPost."""
        fingerprint = FacebookFingerprint.create("Test content")
        
        post = FacebookPost(
            fingerprint=fingerprint,
            post_type=FacebookPostType.TEXT,
            text_content="This is a test Facebook post",
            hashtags=["test", "facebook"],
            tone=FacebookTone.CASUAL,
            target_audience=FacebookAudience.GENERAL
        )
        
        assert post.fingerprint == fingerprint
        assert post.text_content == "This is a test Facebook post"
        assert len(post.hashtags) == 2
        assert post.is_within_limits()
    
    def test_facebook_analysis_score_calculation(self):
        """Test cálculo de score general."""
        analysis = FacebookAnalysis(
            engagement_prediction=0.8,
            virality_score=0.7,
            sentiment_score=0.9,
            readability_score=0.6,
            brand_alignment=0.5,
            predicted_likes=100,
            predicted_shares=20,
            predicted_comments=15,
            predicted_reach=1000
        )
        
        overall_score = analysis.overall_score()
        assert 0.0 <= overall_score <= 1.0
        assert overall_score > 0.6  # Should be decent with these scores


class TestFacebookUtils:
    """Tests para utilidades de Facebook."""
    
    def test_extract_hashtags(self):
        """Test extracción de hashtags."""
        content = "Check out this amazing #technology post about #AI and #MachineLearning!"
        hashtags = FacebookUtils.extract_hashtags(content)
        
        assert "technology" in hashtags
        assert "AI" in hashtags
        assert "MachineLearning" in hashtags
        assert len(hashtags) == 3
    
    def test_extract_mentions(self):
        """Test extracción de menciones."""
        content = "Thanks @john_doe and @tech_company for the inspiration!"
        mentions = FacebookUtils.extract_mentions(content)
        
        assert "john_doe" in mentions
        assert "tech_company" in mentions
        assert len(mentions) == 2
    
    def test_clean_content_for_display(self):
        """Test limpieza de contenido."""
        content = "Great post about AI! #technology #innovation #AI"
        cleaned = FacebookUtils.clean_content_for_display(content, separate_hashtags=True)
        
        assert cleaned == "Great post about AI!"
        assert "#technology" not in cleaned
    
    def test_validate_post_length(self):
        """Test validación de longitud."""
        short_content = "Short post"
        long_content = "x" * 2500
        
        is_valid_short, count_short = FacebookUtils.validate_post_length(short_content)
        is_valid_long, count_long = FacebookUtils.validate_post_length(long_content)
        
        assert is_valid_short is True
        assert count_short == len(short_content)
        assert is_valid_long is False
        assert count_long == 2500
    
    def test_analyze_post_structure(self):
        """Test análisis de estructura."""
        content = "What do you think about AI? 🤖 It's amazing! #AI #technology"
        analysis = FacebookUtils.analyze_post_structure(content)
        
        assert analysis['character_count'] > 0
        assert analysis['word_count'] > 0
        assert analysis['hashtag_count'] == 2
        assert analysis['emoji_count'] > 0
        assert analysis['has_question'] is True
        assert analysis['has_exclamation'] is True
    
    def test_calculate_readability_score(self):
        """Test cálculo de legibilidad."""
        easy_content = "This is easy to read. Short sentences. Clear message."
        hard_content = "This is an extraordinarily complicated sentence with unnecessarily complex vocabulary and excessively long constructions that make comprehension difficult."
        
        easy_score = FacebookUtils.calculate_readability_score(easy_content)
        hard_score = FacebookUtils.calculate_readability_score(hard_content)
        
        assert 0.0 <= easy_score <= 1.0
        assert 0.0 <= hard_score <= 1.0
        assert easy_score > hard_score  # Easy content should score higher
    
    def test_optimize_hashtags(self):
        """Test optimización de hashtags."""
        hashtags = ["AI", "technology", "AI", "innovation", "tech", "future", "ai", "trending"]
        optimized = FacebookUtils.optimize_hashtags(hashtags, max_hashtags=5)
        
        assert len(optimized) <= 5
        assert len(set(tag.lower() for tag in optimized)) == len(optimized)  # No duplicates
    
    def test_validate_facebook_compliance(self):
        """Test validación de cumplimiento."""
        good_content = "Sharing some insights about technology and innovation!"
        spam_content = "FREE MONEY NOW!!! CLICK HERE!!! GUARANTEED!!!"
        
        good_result = FacebookUtils.validate_facebook_compliance(good_content)
        spam_result = FacebookUtils.validate_facebook_compliance(spam_content)
        
        assert good_result['is_compliant'] is True
        assert good_result['compliance_score'] > 0.8
        assert spam_result['compliance_score'] < good_result['compliance_score']


class TestFacebookLangChainConfig:
    """Tests para configuración de LangChain."""
    
    def test_config_creation(self):
        """Test creación de configuración."""
        config = FacebookLangChainConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000
        )
        
        assert config.model_name == "gpt-3.5-turbo"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.use_onyx_llm is True  # Default
    
    def test_config_validation(self):
        """Test validación de configuración."""
        # Temperature validation
        with pytest.raises(ValueError):
            FacebookLangChainConfig(temperature=-0.1)
        
        with pytest.raises(ValueError):
            FacebookLangChainConfig(temperature=1.1)
        
        # Max tokens validation
        with pytest.raises(ValueError):
            FacebookLangChainConfig(max_tokens=50)  # Too low
        
        with pytest.raises(ValueError):
            FacebookLangChainConfig(max_tokens=5000)  # Too high


class TestFacebookEngineAsync:
    """Tests asíncronos para FacebookPostEngine."""
    
    @pytest.fixture
    def mock_langchain_service(self):
        """Mock LangChain service."""
        service = Mock(spec=FacebookLangChainService)
        service.generate_facebook_post = AsyncMock(return_value={
            'content': 'Generated Facebook post content',
            'metadata': {'tokens': 50, 'cost': 0.001},
            'metrics': {'total_tokens': 50}
        })
        service.analyze_facebook_post = AsyncMock(return_value={
            'engagement_prediction': 0.7,
            'virality_score': 0.5,
            'sentiment_score': 0.8,
            'readability_score': 0.6,
            'brand_alignment': 0.7,
            'predicted_likes': 150,
            'predicted_shares': 30,
            'predicted_comments': 20,
            'predicted_reach': 1500,
            'strengths': ['Good sentiment', 'Clear message'],
            'improvements': ['Add hashtags'],
            'hashtag_suggestions': ['#tech', '#innovation']
        })
        service.get_post_recommendations = AsyncMock(return_value={
            'recommendations': ['Add call-to-action', 'Include trending hashtags']
        })
        service.predict_optimal_timing = AsyncMock(return_value={
            'optimal_time': datetime.now()
        })
        
        return service
    
    @pytest.fixture
    def facebook_engine(self, mock_langchain_service):
        """Facebook engine con mock service."""
        return FacebookPostEngine(mock_langchain_service)
    
    @pytest.mark.asyncio
    async def test_generate_post_success(self, facebook_engine):
        """Test generación exitosa de post."""
        request = FacebookRequest(
            content_topic="Artificial Intelligence trends",
            post_type=FacebookPostType.TEXT,
            tone=FacebookTone.PROFESSIONAL,
            target_audience=FacebookAudience.PROFESSIONALS
        )
        
        result = await facebook_engine.generate_post(request)
        
        assert result.success is True
        assert result.post is not None
        assert result.analysis is not None
        assert result.processing_time_ms > 0
        assert len(result.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_post_success(self, facebook_engine):
        """Test análisis exitoso de post."""
        fingerprint = FacebookFingerprint.create("Test content")
        post = FacebookPost(
            fingerprint=fingerprint,
            post_type=FacebookPostType.TEXT,
            text_content="This is a test post about technology",
            tone=FacebookTone.CASUAL,
            target_audience=FacebookAudience.GENERAL
        )
        
        analysis = await facebook_engine.analyze_post(post)
        
        assert analysis is not None
        assert 0.0 <= analysis.engagement_prediction <= 1.0
        assert 0.0 <= analysis.virality_score <= 1.0
        assert analysis.predicted_likes > 0
        assert len(analysis.strengths) > 0
    
    def test_get_analytics(self, facebook_engine):
        """Test obtención de analytics."""
        analytics = facebook_engine.get_analytics()
        
        assert 'posts_generated' in analytics
        assert 'posts_analyzed' in analytics
        assert 'total_processing_time' in analytics
        assert 'cache_hits' in analytics
        assert 'cache_size' in analytics
    
    def test_cache_functionality(self, facebook_engine):
        """Test funcionalidad de cache."""
        # Clear cache first
        facebook_engine.clear_cache()
        
        request = FacebookRequest(content_topic="Cache test")
        cache_key = facebook_engine._get_cache_key(request)
        
        assert cache_key is not None
        assert len(cache_key) == 32  # MD5 hash length
        assert len(facebook_engine.cache) == 0


# Integration tests
class TestIntegration:
    """Tests de integración."""
    
    def test_end_to_end_flow(self):
        """Test flujo completo end-to-end."""
        # Create request
        request = FacebookRequest(
            content_topic="Social Media Marketing Tips",
            post_type=FacebookPostType.TEXT,
            tone=FacebookTone.EDUCATIONAL,
            target_audience=FacebookAudience.ENTREPRENEURS,
            include_hashtags=True,
            include_emoji=True,
            keywords=["marketing", "social media", "tips"]
        )
        
        # Validate request
        assert request.content_topic == "Social Media Marketing Tips"
        assert request.include_hashtags is True
        
        # Create mock post
        fingerprint = FacebookFingerprint.create(request.content_topic)
        post = FacebookPost(
            fingerprint=fingerprint,
            post_type=request.post_type,
            text_content="Here are 5 essential social media marketing tips! 📱✨",
            hashtags=["marketing", "socialmedia", "tips"],
            tone=request.tone,
            target_audience=request.target_audience
        )
        
        # Validate post
        assert post.is_within_limits()
        assert len(post.hashtags) == 3
        assert post.get_character_count() > 0
        
        # Analyze structure
        utils = FacebookUtils()
        structure = utils.analyze_post_structure(post.text_content)
        
        assert structure['emoji_count'] > 0
        assert structure['has_exclamation'] is True
        
        # Validate compliance
        compliance = utils.validate_facebook_compliance(post.text_content)
        assert compliance['is_compliant'] is True


# Performance tests
class TestPerformance:
    """Tests de performance."""
    
    def test_hashtag_extraction_performance(self):
        """Test performance de extracción de hashtags."""
        import time
        
        # Large content with many hashtags
        content = " ".join([f"#hashtag{i}" for i in range(100)])
        
        start_time = time.perf_counter()
        hashtags = FacebookUtils.extract_hashtags(content)
        processing_time = (time.perf_counter() - start_time) * 1000
        
        assert len(hashtags) == 100
        assert processing_time < 100  # Should be under 100ms
    
    def test_content_analysis_performance(self):
        """Test performance de análisis de contenido."""
        import time
        
        # Large content
        content = "This is a test post. " * 100  # 2000+ characters
        
        start_time = time.perf_counter()
        analysis = FacebookUtils.analyze_post_structure(content)
        processing_time = (time.perf_counter() - start_time) * 1000
        
        assert analysis['character_count'] > 2000
        assert processing_time < 50  # Should be under 50ms


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 