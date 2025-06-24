import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from agents.backend_ads.generation_service import (
    generate_ads,
    generate_brand_kit,
    generate_custom_content,
    batch_generate_ads,
    batch_generate_brand_kits,
    batch_generate_custom_content,
    batch_generate_with_semaphore,
    GenerationResult,
    BatchResult,
    GenerationError,
    ValidationError,
    LLMError,
    TimeoutError,
    get_generation_stats,
    reset_metrics
)
from agents.backend_ads.utils_generation import (
    sanitize_text,
    validate_input_lengths,
    validate_url,
    generate_trace_id,
    format_processing_time,
    validate_batch_size,
    RateLimiter
)
from aiocache import caches
import agents.backend_ads.generation_service as gen_service

# --- Test Fixtures ---
@pytest.fixture
def sample_text():
    return "This is a sample text for testing purposes. It contains enough content to pass validation."

@pytest.fixture
def sample_prompt():
    return "Generate a creative advertisement"

@pytest.fixture
def trace_id():
    return "test-trace-123"

@pytest.fixture
def mock_llm_response():
    return ["Ad 1", "Ad 2", "Ad 3"]

@pytest.fixture(autouse=True)
def clear_cache_and_disable_ttl(monkeypatch):
    # Set cache TTL to 0 for all tests
    monkeypatch.setattr(gen_service, 'CACHE_TTL_SECONDS', 0)
    
    # Completely disable caching by patching the cached decorator
    def no_cache_decorator(*args, **kwargs):
        def decorator(func):
            return func  # Return the original function without caching
        return decorator
    
    monkeypatch.setattr(gen_service, 'cached', no_cache_decorator)

    async def clear_all():
        for cache in caches._caches.values():
            await cache.clear()
    asyncio.get_event_loop().run_until_complete(clear_all())
    yield
    asyncio.get_event_loop().run_until_complete(clear_all())

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

# --- Test Generation Functions ---
class TestGenerationFunctions:
    @pytest.mark.asyncio
    async def test_generate_ads_success(self, sample_text, trace_id, mock_llm_response):
        """Test successful ads generation"""
        with patch('agents.backend_ads.llm_interface.generate_ads_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_llm_response

            result = await generate_ads(
                text=sample_text,
                trace_id=trace_id,
                lang="en",
                llm_func=mock_llm
            )

            assert isinstance(result, GenerationResult)
            assert result.success == True
            assert result.data == mock_llm_response
            assert result.trace_id == trace_id
            assert result.processing_time > 0
            assert result.metadata is not None
    
    @pytest.mark.asyncio
    async def test_generate_ads_validation_error(self, trace_id):
        """Test ads generation with validation error"""
        with pytest.raises(ValidationError):
            await generate_ads(
                text="Short",
                trace_id=trace_id,
                lang="en"
            )
    
    @pytest.mark.asyncio
    async def test_generate_ads_llm_error(self, sample_text, trace_id):
        """Test LLM error handling"""
        with patch('agents.backend_ads.llm_interface.generate_ads_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = Exception("LLM API Error")

            with pytest.raises(LLMError) as exc_info:
                await generate_ads(
                    text=sample_text,
                    trace_id=trace_id,
                    lang="en",
                    llm_func=mock_llm
                )
            
            assert exc_info.value.message == "Error generating content: empty response or LLM error."
            assert exc_info.value.trace_id == trace_id
    
    @pytest.mark.asyncio
    async def test_generate_ads_timeout(self, sample_text, trace_id):
        """Test timeout handling"""
        with patch('agents.backend_ads.llm_interface.generate_ads_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = asyncio.TimeoutError()

            with pytest.raises(TimeoutError) as exc_info:
                await generate_ads(
                    text=sample_text,
                    trace_id=trace_id,
                    timeout=1.0,
                    lang="en",
                    llm_func=mock_llm
                )
            
            assert exc_info.value.message == "Operation exceeded time limit."
            assert exc_info.value.trace_id == trace_id
    
    @pytest.mark.asyncio
    async def test_generate_brand_kit_success(self, sample_text, trace_id):
        """Test successful brand kit generation"""
        mock_response = ["Brand Kit 1", "Brand Kit 2"]
        
        with patch('agents.backend_ads.llm_interface.generate_brand_kit_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response

            result = await generate_brand_kit(
                text=sample_text,
                trace_id=trace_id,
                lang="en",
                llm_func=mock_llm
            )

            assert isinstance(result, GenerationResult)
            assert result.success == True
            assert result.data == mock_response
    
    @pytest.mark.asyncio
    async def test_generate_custom_content_success(self, sample_text, trace_id):
        """Test successful custom content generation"""
        mock_response = ["Custom Content 1", "Custom Content 2"]
        
        with patch('agents.backend_ads.llm_interface.generate_custom_content_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response

            result = await generate_custom_content(
                prompt="Create a blog post",
                text=sample_text,
                trace_id=trace_id,
                lang="en",
                llm_func=mock_llm
            )

            assert isinstance(result, GenerationResult)
            assert result.success == True
            assert result.data == mock_response

# --- Test Batch Operations ---
class TestBatchOperations:
    @pytest.mark.asyncio
    async def test_batch_generate_ads_success(self, trace_id):
        """Test successful batch ads generation"""
        texts = ["This is a valid text for testing purposes.", "Another valid text with sufficient length.", "Third valid text that meets requirements."]
        mock_responses = [["Ad 1"], ["Ad 2"], ["Ad 3"]]

        with patch('agents.backend_ads.llm_interface.generate_ads_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = mock_responses

            result = await batch_generate_ads(
                texts=texts,
                trace_id=trace_id,
                max_concurrency=2,
                **{"llm_func": mock_llm}
            )

            assert isinstance(result, BatchResult)
            assert result.total_count == 3
            assert result.success_count == 3
            assert result.error_count == 0
            assert result.trace_id == trace_id
            assert len(result.results) == 3
    
    @pytest.mark.asyncio
    async def test_batch_generate_ads_with_errors(self, trace_id):
        """Test batch ads generation with some errors"""
        texts = ["Valid text for testing purposes.", "Short text", "Another valid text for testing."]
        with patch('agents.backend_ads.llm_interface.generate_ads_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = [["Ad 1"], Exception("LLM Error"), ["Ad 3"]]
            result = await batch_generate_ads(
                texts=texts,
                trace_id=trace_id,
                max_concurrency=2,
                **{"llm_func": mock_llm}
            )
            assert isinstance(result, BatchResult)
            assert result.total_count == 3
            assert result.success_count == 2
            assert result.error_count == 1
    
    @pytest.mark.asyncio
    async def test_batch_generate_with_semaphore(self, trace_id):
        """Test generic batch generation with semaphore"""
        items = [{"text": "Text 1"}, {"text": "Text 2"}]
        
        async def mock_generation_func(**kwargs):
            return GenerationResult(
                success=True,
                data=["Generated content"],
                trace_id=kwargs.get("trace_id")
            )
        
        result = await batch_generate_with_semaphore(
            items=items,
            generation_func=mock_generation_func,
            max_concurrency=1,
            trace_id=trace_id
        )
        
        assert isinstance(result, BatchResult)
        assert result.total_count == 2
        assert result.success_count == 2
        assert result.error_count == 0

# --- Test Metrics ---
class TestMetrics:
    def test_get_generation_stats(self):
        """Test getting generation statistics"""
        stats = get_generation_stats()
        
        assert isinstance(stats, dict)
        assert "active_generations" in stats
        assert "total_requests" in stats
        assert "cache_stats" in stats
    
    def test_reset_metrics(self):
        """Test resetting metrics"""
        # This should not raise an exception
        reset_metrics()
        
        # Verify metrics are reset
        stats = get_generation_stats()
        for metric_type in stats["total_requests"].values():
            assert metric_type == 0

# --- Test Error Handling ---
class TestErrorHandling:
    def test_generation_error_creation(self):
        """Test GenerationError creation"""
        error = GenerationError("Test error", "trace-123", "TEST_ERROR")
        assert error.message == "Test error"
        assert error.trace_id == "trace-123"
        assert error.error_code == "TEST_ERROR"
        assert isinstance(error.timestamp, datetime)
    
    def test_validation_error_creation(self):
        """Test ValidationError creation"""
        error = ValidationError("Validation failed", "trace-123")
        assert error.message == "Validation failed"
        assert error.trace_id == "trace-123"
        assert error.error_code == "VALIDATION_ERROR"
    
    def test_llm_error_creation(self):
        """Test LLMError creation"""
        error = LLMError("LLM failed", "trace-123")
        assert error.message == "LLM failed"
        assert error.trace_id == "trace-123"
        assert error.error_code == "LLM_ERROR"
    
    def test_timeout_error_creation(self):
        """Test TimeoutError creation"""
        error = TimeoutError("Operation timed out", "trace-123")
        assert error.message == "Operation timed out"
        assert error.trace_id == "trace-123"
        assert error.error_code == "TIMEOUT_ERROR"

# --- Integration Tests ---
class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_generation_workflow(self, sample_text, trace_id):
        """Test complete generation workflow"""
        # Test ads generation
        with patch('agents.backend_ads.llm_interface.generate_ads_lcel', new_callable=AsyncMock) as mock_ads:
            mock_ads.return_value = ["Ad 1", "Ad 2"]
            
            ads_result = await generate_ads(
                text=sample_text,
                trace_id=trace_id,
                lang="en",
                llm_func=mock_ads
            )
            
            assert ads_result.success == True
            assert len(ads_result.data) == 2
        
        # Test brand kit generation
        with patch('agents.backend_ads.llm_interface.generate_brand_kit_lcel', new_callable=AsyncMock) as mock_brand:
            mock_brand.return_value = {"name": "Test Brand"}

            brand_result = await generate_brand_kit(
                text=sample_text,
                trace_id=trace_id,
                lang="en",
                llm_func=mock_brand
            )

            assert brand_result.success == True
            assert brand_result.data["name"] == "Test Brand"
    
    @pytest.mark.asyncio
    async def test_batch_workflow_with_mixed_results(self, trace_id):
        """Test batch workflow with mixed success and error results"""
        texts = [
            "Valid text for generation",
            "Short text",  # This will fail validation
            "Another valid text for testing"
        ]
        with patch('agents.backend_ads.llm_interface.generate_ads_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = [
                ["Ad 1", "Ad 2"],  # Success
                Exception("Validation error"),  # Error
                ["Ad 3", "Ad 4"]   # Success
            ]
            result = await batch_generate_ads(
                texts=texts,
                trace_id=trace_id,
                max_concurrency=2,
                **{"llm_func": mock_llm}
            )
            assert result.total_count == 3
            assert result.success_count == 2
            assert result.error_count == 1
            # Check individual results
            assert result.results[0].success == True
            assert result.results[1].success == False
            assert result.results[2].success == True

# --- Performance Tests ---
class TestPerformance:
    @pytest.mark.asyncio
    async def test_concurrent_generation(self, trace_id):
        """Test concurrent generation performance"""
        texts = ["Valid text for testing " + str(i) + " with sufficient length to pass validation." for i in range(10)]

        with patch('agents.backend_ads.llm_interface.generate_ads_lcel', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = ["Generated ad"]

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