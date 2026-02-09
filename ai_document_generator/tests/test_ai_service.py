"""
Tests for AI service
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import uuid

from app.services.ai_service import AIService
from app.schemas.ai import (
    AIGenerationRequest, AIProvider, AIModel,
    AIContentAnalysisRequest, AITranslationRequest,
    AISummarizationRequest, AIImprovementRequest
)


@pytest.fixture
def ai_service():
    """Create AI service instance for testing."""
    return AIService()


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    client = AsyncMock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client."""
    client = AsyncMock()
    client.messages.create = AsyncMock()
    return client


class TestAIService:
    """Test cases for AI service."""
    
    @pytest.mark.asyncio
    async def test_generate_content_openai(self, ai_service, mock_openai_client):
        """Test content generation with OpenAI."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated content"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.total_tokens = 100
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 50
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Mock the client creation
        with patch.object(ai_service, '_get_client', return_value=mock_openai_client):
            request = AIGenerationRequest(
                prompt="Test prompt",
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4
            )
            
            response = await ai_service.generate_content(request)
            
            assert response.content == "Generated content"
            assert response.provider == AIProvider.OPENAI
            assert response.model == AIModel.GPT_4
            assert response.usage["tokens_used"] == 100
    
    @pytest.mark.asyncio
    async def test_generate_content_anthropic(self, ai_service, mock_anthropic_client):
        """Test content generation with Anthropic."""
        # Mock Anthropic response
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Generated content"
        mock_response.stop_reason = "end_turn"
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 50
        
        mock_anthropic_client.messages.create.return_value = mock_response
        
        # Mock the client creation
        with patch.object(ai_service, '_get_client', return_value=mock_anthropic_client):
            request = AIGenerationRequest(
                prompt="Test prompt",
                provider=AIProvider.ANTHROPIC,
                model=AIModel.CLAUDE_3_SONNET
            )
            
            response = await ai_service.generate_content(request)
            
            assert response.content == "Generated content"
            assert response.provider == AIProvider.ANTHROPIC
            assert response.model == AIModel.CLAUDE_3_SONNET
            assert response.usage["tokens_used"] == 100
    
    @pytest.mark.asyncio
    async def test_analyze_content_sentiment(self, ai_service):
        """Test content analysis for sentiment."""
        # Mock the generate_content method
        mock_response = MagicMock()
        mock_response.content = '{"sentiment": 0.8, "confidence": 0.9}'
        mock_response.provider = AIProvider.OPENAI
        mock_response.model = AIModel.GPT_4
        
        with patch.object(ai_service, 'generate_content', return_value=mock_response):
            request = AIContentAnalysisRequest(
                content="This is a positive text",
                analysis_type="sentiment",
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4
            )
            
            response = await ai_service.analyze_content(request)
            
            assert response.analysis_type == "sentiment"
            assert response.provider == AIProvider.OPENAI
            assert response.model == AIProvider.OPENAI
            assert response.confidence == 0.8
    
    @pytest.mark.asyncio
    async def test_translate_content(self, ai_service):
        """Test content translation."""
        # Mock the generate_content method
        mock_response = MagicMock()
        mock_response.content = "Translated content"
        mock_response.provider = AIProvider.OPENAI
        mock_response.model = AIModel.GPT_4
        
        with patch.object(ai_service, 'generate_content', return_value=mock_response):
            request = AITranslationRequest(
                content="Hello world",
                source_language="en",
                target_language="es",
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4
            )
            
            response = await ai_service.translate_content(request)
            
            assert response.original_content == "Hello world"
            assert response.translated_content == "Translated content"
            assert response.source_language == "en"
            assert response.target_language == "es"
            assert response.provider == AIProvider.OPENAI
    
    @pytest.mark.asyncio
    async def test_summarize_content(self, ai_service):
        """Test content summarization."""
        # Mock the generate_content method
        mock_response = MagicMock()
        mock_response.content = "Summary of the content"
        mock_response.provider = AIProvider.OPENAI
        mock_response.model = AIModel.GPT_4
        
        with patch.object(ai_service, 'generate_content', return_value=mock_response):
            request = AISummarizationRequest(
                content="Long content to summarize",
                summary_type="abstractive",
                max_length=100,
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4
            )
            
            response = await ai_service.summarize_content(request)
            
            assert response.original_content == "Long content to summarize"
            assert response.summary == "Summary of the content"
            assert response.summary_type == "abstractive"
            assert response.provider == AIProvider.OPENAI
    
    @pytest.mark.asyncio
    async def test_improve_content(self, ai_service):
        """Test content improvement."""
        # Mock the generate_content method
        mock_response = MagicMock()
        mock_response.content = "Improved content"
        mock_response.provider = AIProvider.OPENAI
        mock_response.model = AIModel.GPT_4
        
        with patch.object(ai_service, 'generate_content', return_value=mock_response):
            request = AIImprovementRequest(
                content="Content to improve",
                improvement_type="grammar",
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4
            )
            
            response = await ai_service.improve_content(request)
            
            assert response.original_content == "Content to improve"
            assert response.improved_content == "Improved content"
            assert response.improvement_type == "grammar"
            assert response.provider == AIProvider.OPENAI
    
    @pytest.mark.asyncio
    async def test_process_batch(self, ai_service):
        """Test batch processing."""
        # Mock individual methods
        mock_generation_response = MagicMock()
        mock_analysis_response = MagicMock()
        
        with patch.object(ai_service, 'generate_content', return_value=mock_generation_response), \
             patch.object(ai_service, 'analyze_content', return_value=mock_analysis_response):
            
            from app.schemas.ai import AIBatchRequest
            
            request = AIBatchRequest(
                requests=[
                    AIGenerationRequest(
                        prompt="Test prompt",
                        provider=AIProvider.OPENAI,
                        model=AIModel.GPT_4
                    ),
                    AIContentAnalysisRequest(
                        content="Test content",
                        analysis_type="sentiment",
                        provider=AIProvider.OPENAI,
                        model=AIModel.GPT_4
                    )
                ]
            )
            
            response = await ai_service.process_batch(request)
            
            assert response.total_requests == 2
            assert response.successful_requests == 2
            assert response.failed_requests == 0
            assert len(response.results) == 2
    
    @pytest.mark.asyncio
    async def test_get_provider_status_available(self, ai_service):
        """Test getting provider status when available."""
        # Mock successful test request
        mock_response = MagicMock()
        mock_response.content = "Test response"
        
        with patch.object(ai_service, 'generate_content', return_value=mock_response):
            status = await ai_service.get_provider_status(AIProvider.OPENAI)
            
            assert status.provider == AIProvider.OPENAI
            assert status.is_available == True
            assert status.error_rate == 0.0
            assert status.response_time is not None
    
    @pytest.mark.asyncio
    async def test_get_provider_status_unavailable(self, ai_service):
        """Test getting provider status when unavailable."""
        # Mock failed test request
        with patch.object(ai_service, 'generate_content', side_effect=Exception("API Error")):
            status = await ai_service.get_provider_status(AIProvider.OPENAI)
            
            assert status.provider == AIProvider.OPENAI
            assert status.is_available == False
            assert status.error_rate == 1.0
            assert status.error_message == "API Error"
    
    def test_create_analysis_prompt_sentiment(self, ai_service):
        """Test creating analysis prompt for sentiment."""
        request = AIContentAnalysisRequest(
            content="Test content",
            analysis_type="sentiment"
        )
        
        prompt = ai_service._create_analysis_prompt(request)
        
        assert "sentiment" in prompt.lower()
        assert "Test content" in prompt
        assert "score from -1" in prompt
    
    def test_create_analysis_prompt_quality(self, ai_service):
        """Test creating analysis prompt for quality."""
        request = AIContentAnalysisRequest(
            content="Test content",
            analysis_type="quality"
        )
        
        prompt = ai_service._create_analysis_prompt(request)
        
        assert "quality" in prompt.lower()
        assert "Test content" in prompt
        assert "grammar" in prompt
    
    def test_get_analysis_system_prompt(self, ai_service):
        """Test getting analysis system prompt."""
        prompt = ai_service._get_analysis_system_prompt("sentiment")
        assert "sentiment analysis" in prompt.lower()
        
        prompt = ai_service._get_analysis_system_prompt("quality")
        assert "quality assessor" in prompt.lower()
    
    def test_parse_analysis_results_valid_json(self, ai_service):
        """Test parsing analysis results with valid JSON."""
        content = '{"sentiment": 0.8, "confidence": 0.9}'
        results = ai_service._parse_analysis_results(content, "sentiment")
        
        assert results["sentiment"] == 0.8
        assert results["confidence"] == 0.9
    
    def test_parse_analysis_results_invalid_json(self, ai_service):
        """Test parsing analysis results with invalid JSON."""
        content = "Invalid JSON response"
        results = ai_service._parse_analysis_results(content, "sentiment")
        
        assert results["raw_response"] == content
        assert results["confidence"] == 0.8
    
    def test_create_improvement_prompt(self, ai_service):
        """Test creating improvement prompt."""
        request = AIImprovementRequest(
            content="Test content",
            improvement_type="grammar",
            target_audience="students",
            writing_style="formal"
        )
        
        prompt = ai_service._create_improvement_prompt(request)
        
        assert "grammar" in prompt.lower()
        assert "Test content" in prompt
        assert "students" in prompt
        assert "formal" in prompt
    
    def test_parse_improvements(self, ai_service):
        """Test parsing improvements."""
        content = "Improved content with changes"
        improvements = ai_service._parse_improvements(content)
        
        assert len(improvements) == 1
        assert improvements[0]["type"] == "improvement"
        assert improvements[0]["confidence"] == 0.8




