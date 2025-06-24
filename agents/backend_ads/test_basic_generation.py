import pytest
from unittest.mock import patch, AsyncMock
import asyncio
from datetime import datetime

# Test the utility functions first
from utils_generation import (
    sanitize_text,
    validate_input_lengths,
    validate_url,
    generate_trace_id,
    format_processing_time,
    validate_batch_size,
    RateLimiter,
    get_error_msg
)

# Test fixtures
@pytest.fixture
def sample_text():
    return "This is a sample text for testing purposes. It contains enough content to pass validation."

@pytest.fixture
def sample_prompt():
    return "Generate a creative advertisement"

@pytest.fixture
def trace_id():
    return "test-trace-123"

# --- Test Input Validation and Sanitization ---
class TestInputValidation:
    def test_sanitize_text_normal(self):
        """Test normal text sanitization"""
        text = "Hello <b>World</b>!"
        result = sanitize_text(text)
        assert result == "Hello World!"
    
    def test_sanitize_text_with_script(self):
        """Test sanitization removes scripts"""
        text = "Hello <script>alert('xss')</script> World!"
        result = sanitize_text(text)
        assert "script" not in result
        assert "alert" not in result
    
    def test_sanitize_text_empty(self):
        """Test sanitization with empty text"""
        with pytest.raises(ValueError, match="Text cannot be None or empty"):
            sanitize_text("")
    
    def test_sanitize_text_none(self):
        """Test sanitization with None"""
        with pytest.raises(ValueError, match="Text cannot be None or empty"):
            sanitize_text(None)
    
    def test_validate_input_lengths_valid(self, sample_text):
        """Test valid input length validation"""
        validate_input_lengths(sample_text, min_length=10, max_length=2000)
    
    def test_validate_input_lengths_too_short(self):
        """Test input length validation with too short text"""
        with pytest.raises(ValueError):
            validate_input_lengths("Short", min_length=10, max_length=2000)
    
    def test_validate_input_lengths_too_long(self):
        """Test input length validation with too long text"""
        long_text = "A" * 3000
        with pytest.raises(ValueError):
            validate_input_lengths(long_text, min_length=10, max_length=2000)
    
    def test_validate_url_valid(self):
        """Test valid URL validation"""
        url = "https://example.com"
        result = validate_url(url)
        assert result == url
    
    def test_validate_url_invalid(self):
        """Test invalid URL validation"""
        with pytest.raises(ValueError, match="URL must start with http:// or https://"):
            validate_url("invalid-url")
    
    def test_validate_batch_size_valid(self):
        """Test valid batch size validation"""
        items = ["item1", "item2", "item3"]
        validate_batch_size(items, max_size=10)
    
    def test_validate_batch_size_too_large(self):
        """Test batch size validation with too many items"""
        items = ["item"] * 60
        with pytest.raises(ValueError, match="Batch size 60 exceeds maximum limit of 50"):
            validate_batch_size(items, max_size=50)
    
    def test_validate_batch_size_empty(self):
        """Test batch size validation with empty list"""
        with pytest.raises(ValueError, match="Batch cannot be empty"):
            validate_batch_size([], max_size=50)

# --- Test Utility Functions ---
class TestUtilityFunctions:
    def test_generate_trace_id(self):
        """Test trace ID generation"""
        trace_id = generate_trace_id()
        assert isinstance(trace_id, str)
        assert len(trace_id) > 0
    
    def test_format_processing_time_ms(self):
        """Test processing time formatting for milliseconds"""
        result = format_processing_time(0.5)
        assert "ms" in result
    
    def test_format_processing_time_seconds(self):
        """Test processing time formatting for seconds"""
        result = format_processing_time(30.5)
        assert "s" in result
    
    def test_format_processing_time_minutes(self):
        """Test processing time formatting for minutes"""
        result = format_processing_time(90.5)
        assert "m" in result
    
    def test_get_error_msg(self):
        """Test error message internationalization"""
        # Test Spanish (default)
        es_msg = get_error_msg("short_text", "es")
        assert "corto" in es_msg.lower()
        
        # Test English
        en_msg = get_error_msg("short_text", "en")
        assert "short" in en_msg.lower()
        
        # Test fallback to Spanish
        fallback_msg = get_error_msg("short_text", "fr")
        assert "corto" in fallback_msg.lower()

# --- Test Rate Limiter ---
class TestRateLimiter:
    def test_rate_limiter_initial(self):
        """Test rate limiter allows initial requests"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        assert limiter.is_allowed("user1") == True
    
    def test_rate_limiter_limit_reached(self):
        """Test rate limiter blocks when limit reached"""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == False
    
    def test_rate_limiter_different_users(self):
        """Test rate limiter handles different users separately"""
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user2") == True
        assert limiter.is_allowed("user1") == False

# --- Test Generation Service (with mocked dependencies) ---
class TestGenerationService:
    @pytest.mark.asyncio
    async def test_generate_ads_basic(self, sample_text, trace_id):
        """Test basic ads generation with mocked LLM"""
        mock_llm_response = ["Ad 1", "Ad 2", "Ad 3"]
        with patch('agents.backend_ads.llm_interface.generate_ads_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_llm_response
            from generation_service import generate_ads
            result = await generate_ads(
                text=sample_text,
                trace_id=trace_id,
                lang="en",
                llm_func=mock_llm
            )
            assert result.success == True
            assert result.data == mock_llm_response
    
    @pytest.mark.asyncio
    async def test_generate_ads_validation_error(self, trace_id):
        """Test ads generation with validation error"""
        from generation_service import generate_ads, ValidationError
        
        with pytest.raises(ValidationError):
            await generate_ads(
                text="Short",
                trace_id=trace_id,
                lang="en"
            )
    
    @pytest.mark.asyncio
    async def test_generate_brand_kit_basic(self, sample_text, trace_id):
        """Test basic brand kit generation with mocked LLM"""
        brand_kit_response = {"name": "Test Brand", "colors": ["red", "blue"]}
        with patch('agents.backend_ads.llm_interface.generate_brand_kit_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = brand_kit_response
            from generation_service import generate_brand_kit
            result = await generate_brand_kit(
                text=sample_text,
                trace_id=trace_id,
                lang="en",
                llm_func=mock_llm
            )
            assert result.success == True
            assert result.data == brand_kit_response
    
    @pytest.mark.asyncio
    async def test_generate_custom_content_basic(self, sample_text, sample_prompt, trace_id):
        """Test basic custom content generation with mocked LLM"""
        custom_response = "This is custom generated content"
        with patch('agents.backend_ads.llm_interface.generate_custom_content_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = custom_response
            from generation_service import generate_custom_content
            result = await generate_custom_content(
                prompt=sample_prompt,
                text=sample_text,
                trace_id=trace_id,
                lang="en",
                llm_func=mock_llm
            )
            assert result.success == True
            assert result.data == custom_response

# --- Test Batch Operations ---
class TestBatchOperations:
    @pytest.mark.asyncio
    async def test_batch_generate_ads_basic(self, trace_id):
        """Test basic batch ads generation"""
        texts = [
            "This is a valid text for testing batch 1.",
            "This is a valid text for testing batch 2.",
            "This is a valid text for testing batch 3."
        ]
        mock_responses = [["Ad 1"], ["Ad 2"], ["Ad 3"]]
        with patch('agents.backend_ads.llm_interface.generate_ads_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = mock_responses
            from generation_service import batch_generate_ads
            result = await batch_generate_ads(
                texts=texts,
                trace_id=trace_id,
                max_concurrency=2,
                **{"llm_func": mock_llm}
            )
            assert result.total_count == 3
            assert result.success_count == 3
    
    @pytest.mark.asyncio
    async def test_batch_generate_with_errors(self, trace_id):
        """Test batch generation with some errors"""
        texts = ["Valid text", "Short", "Another valid text"]
        
        with patch('generation_service.generate_ads_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = [["Ad 1"], Exception("LLM Error"), ["Ad 3"]]
            
            from generation_service import batch_generate_ads
            
            result = await batch_generate_ads(
                texts=texts,
                trace_id=trace_id,
                max_concurrency=2
            )
            
            assert result.total_count == 3
            assert result.success_count == 2
            assert result.error_count == 1

# --- Test Error Handling ---
class TestErrorHandling:
    def test_generation_error_creation(self):
        """Test GenerationError creation"""
        from generation_service import GenerationError
        
        error = GenerationError("Test error", "trace-123", "TEST_ERROR")
        assert error.message == "Test error"
        assert error.trace_id == "trace-123"
        assert error.error_code == "TEST_ERROR"
        assert isinstance(error.timestamp, datetime)
    
    def test_validation_error_creation(self):
        """Test ValidationError creation"""
        from generation_service import ValidationError
        
        error = ValidationError("Validation failed", "trace-123")
        assert error.message == "Validation failed"
        assert error.trace_id == "trace-123"
        assert error.error_code == "VALIDATION_ERROR"
    
    def test_llm_error_creation(self):
        """Test LLMError creation"""
        from generation_service import LLMError
        
        error = LLMError("LLM failed", "trace-123")
        assert error.message == "LLM failed"
        assert error.trace_id == "trace-123"
        assert error.error_code == "LLM_ERROR"
    
    def test_timeout_error_creation(self):
        """Test TimeoutError creation"""
        from generation_service import TimeoutError
        
        error = TimeoutError("Operation timed out", "trace-123")
        assert error.message == "Operation timed out"
        assert error.trace_id == "trace-123"
        assert error.error_code == "TIMEOUT_ERROR"

# --- Test Metrics ---
class TestMetrics:
    def test_get_generation_stats(self):
        """Test getting generation statistics"""
        from generation_service import get_generation_stats
        
        stats = get_generation_stats()
        
        assert isinstance(stats, dict)
        assert "active_generations" in stats
        assert "total_requests" in stats
        assert "cache_stats" in stats
    
    def test_reset_metrics(self):
        """Test resetting metrics"""
        from generation_service import reset_metrics, get_generation_stats
        
        # This should not raise an exception
        reset_metrics()
        
        # Verify metrics are reset
        stats = get_generation_stats()
        for metric_type in stats["total_requests"].values():
            assert metric_type == 0

# --- Integration Tests ---
class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_generation_workflow(self, sample_text, trace_id):
        """Test complete generation workflow"""
        with patch('agents.backend_ads.llm_interface.generate_ads_lcel', new_callable=AsyncMock) as mock_ads:
            mock_ads.return_value = ["Ad 1", "Ad 2"]
            from generation_service import generate_ads
            ads_result = await generate_ads(
                text=sample_text,
                trace_id=trace_id,
                lang="en",
                llm_func=mock_ads
            )
            assert ads_result.success == True
            assert len(ads_result.data) == 2
        with patch('agents.backend_ads.llm_interface.generate_brand_kit_lcel', new_callable=AsyncMock) as mock_brand:
            mock_brand.return_value = {"name": "Test Brand"}
            from generation_service import generate_brand_kit
            brand_result = await generate_brand_kit(
                text=sample_text,
                trace_id=trace_id,
                lang="en",
                llm_func=mock_brand
            )
            assert brand_result.success == True
            assert brand_result.data["name"] == "Test Brand"

# --- Performance Tests ---
class TestPerformance:
    @pytest.mark.asyncio
    async def test_concurrent_generation(self, trace_id):
        """Test concurrent generation performance"""
        texts = [
            f"This is a valid text for testing {i} with sufficient length to pass validation."
            for i in range(10)
        ]
        with patch('agents.backend_ads.llm_interface.generate_ads_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = ["Generated ad"]
            from generation_service import batch_generate_ads
            start_time = asyncio.get_event_loop().time()
            result = await batch_generate_ads(
                texts=texts,
                trace_id=trace_id,
                max_concurrency=5,
                **{"llm_func": mock_llm}
            )
            end_time = asyncio.get_event_loop().time()
            processing_time = end_time - start_time
            assert result.success_count == 10
            assert result.error_count == 0
            assert processing_time < 2.0  # Should complete quickly with mocked LLM

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 