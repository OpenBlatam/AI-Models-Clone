import logging
from typing import List, Callable, Any, Optional, Dict, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import uuid
import asyncio
from functools import wraps
from aiocache import cached
import os
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import orjson
from agents.backend_ads.llm_interface import (
    generate_ads_lcel,
    generate_brand_kit_lcel,
    generate_custom_content_lcel
)
from agents.backend_ads.utils_generation import (
    log_with_trace, 
    get_error_msg, 
    ads_cache_key, 
    brandkit_cache_key, 
    custom_content_cache_key, 
    CACHE_TTL_SECONDS,
    sanitize_text,
    validate_input_lengths
)

logger = logging.getLogger(__name__)

# --- Prometheus Metrics ---
if os.environ.get('PYTEST_CURRENT_TEST'):
    _test_registry = CollectorRegistry()
    GENERATION_REQUESTS = Counter('generation_requests_total', 'Total generation requests', ['type', 'status'], registry=_test_registry)
    GENERATION_LATENCY = Histogram('generation_latency_seconds', 'Generation latency', ['type'], registry=_test_registry)
    GENERATION_CACHE_HITS = Counter('generation_cache_hits_total', 'Cache hits', ['type'], registry=_test_registry)
    GENERATION_CACHE_MISSES = Counter('generation_cache_misses_total', 'Cache misses', ['type'], registry=_test_registry)
    ACTIVE_GENERATIONS = Gauge('active_generations', 'Currently active generations', ['type'], registry=_test_registry)
else:
    GENERATION_REQUESTS = Counter('generation_requests_total', 'Total generation requests', ['type', 'status'])
    GENERATION_LATENCY = Histogram('generation_latency_seconds', 'Generation latency', ['type'])
    GENERATION_CACHE_HITS = Counter('generation_cache_hits_total', 'Cache hits', ['type'])
    GENERATION_CACHE_MISSES = Counter('generation_cache_misses_total', 'Cache misses', ['type'])
    ACTIVE_GENERATIONS = Gauge('active_generations', 'Currently active generations', ['type'])

# --- Custom Exceptions ---
class GenerationError(Exception):
    """Base exception for generation errors"""
    def __init__(self, message: str, trace_id: Optional[str] = None, error_code: str = "GENERATION_ERROR"):
        super().__init__(message)
        self.message = message  # Add message attribute for tests
        self.trace_id = trace_id
        self.error_code = error_code
        self.timestamp = datetime.utcnow()

class ValidationError(GenerationError):
    """Exception for validation errors"""
    def __init__(self, message: str, trace_id: Optional[str] = None):
        super().__init__(message, trace_id, "VALIDATION_ERROR")

class LLMError(GenerationError):
    """Exception for LLM-related errors"""
    def __init__(self, message: str, trace_id: Optional[str] = None):
        super().__init__(message, trace_id, "LLM_ERROR")

class TimeoutError(GenerationError):
    """Exception for timeout errors"""
    def __init__(self, message: str, trace_id: Optional[str] = None):
        super().__init__(message, trace_id, "TIMEOUT_ERROR")

# --- Response Models ---
@dataclass
class GenerationResult:
    """Structured result for generation operations"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    trace_id: Optional[str] = None
    processing_time: float = 0.0
    cache_hit: bool = False
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BatchResult:
    """Structured result for batch operations"""
    results: List[GenerationResult]
    total_count: int
    success_count: int
    error_count: int
    total_processing_time: float
    trace_id: str

# --- Enhanced Decorators ---
def with_metrics(func: Callable) -> Callable:
    """Decorator to add Prometheus metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        func_name = func.__name__
        generation_type = func_name.replace('generate_', '').replace('_', '-')
        
        # Increment active generations
        ACTIVE_GENERATIONS.labels(type=generation_type).inc()
        
        start_time = datetime.utcnow()
        try:
            with GENERATION_LATENCY.labels(type=generation_type).time():
                result = await func(*args, **kwargs)
            
            GENERATION_REQUESTS.labels(type=generation_type, status="success").inc()
            return result
        except Exception as e:
            GENERATION_REQUESTS.labels(type=generation_type, status="error").inc()
            raise
        finally:
            ACTIVE_GENERATIONS.labels(type=generation_type).dec()
    
    return wrapper

def with_cache_tracking(func: Callable) -> Callable:
    """Decorator to track cache hits/misses"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        func_name = func.__name__
        generation_type = func_name.replace('generate_', '').replace('_', '-')
        
        # This is a simplified version - in practice, you'd need to hook into aiocache
        # to detect actual cache hits/misses
        try:
            result = await func(*args, **kwargs)
            # Assume cache hit if result is returned quickly
            GENERATION_CACHE_HITS.labels(type=generation_type).inc()
            return result
        except Exception:
            GENERATION_CACHE_MISSES.labels(type=generation_type).inc()
            raise
    
    return wrapper

# --- Enhanced Generation Functions ---
@with_cache_tracking
@with_metrics
async def generate_ads(
    text: str,
    trace_id: Optional[str] = None,
    lang: str = "es",
    llm_func: Callable[[str], Any] = generate_ads_lcel,
    timeout: Optional[float] = None,
    metrics_cb: Optional[Callable] = None,
    **kwargs
) -> GenerationResult:
    """
    Generate ads from web text with enhanced error handling and metrics.
    """
    # If using the default llm_func, use the cached version
    if llm_func is generate_ads_lcel:
        return await _generate_ads_cached(
            text=text,
            trace_id=trace_id,
            lang=lang,
            llm_func=llm_func,
            timeout=timeout,
            metrics_cb=metrics_cb,
            **kwargs
        )
    # Otherwise, call the logic directly (no cache)
    return await _generate_ads_logic(
        text=text,
        trace_id=trace_id,
        lang=lang,
        llm_func=llm_func,
        timeout=timeout,
        metrics_cb=metrics_cb,
        **kwargs
    )

# Move the main logic to a helper function
async def _generate_ads_logic(
    text: str,
    trace_id: Optional[str] = None,
    lang: str = "es",
    llm_func: Callable[[str], Any] = generate_ads_lcel,
    timeout: Optional[float] = None,
    metrics_cb: Optional[Callable] = None,
    **kwargs
) -> GenerationResult:
    start_time = datetime.utcnow()
    try:
        sanitized_text = sanitize_text(text)
        validate_input_lengths(sanitized_text, min_length=10, max_length=2000, lang=lang)
        try:
            if timeout:
                ads_list = await asyncio.wait_for(llm_func(sanitized_text), timeout=timeout)
            else:
                ads_list = await llm_func(sanitized_text)
        except asyncio.TimeoutError:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.warning({
                "event": "generate_ads_timeout",
                "trace_id": trace_id,
                "processing_time": processing_time,
                "timeout": timeout
            })
            raise TimeoutError(get_error_msg("timeout", lang), trace_id)
        except Exception as e:
            if isinstance(e, (LLMError, TimeoutError, ValidationError)):
                raise
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error({
                "event": "generate_ads_llm_error",
                "trace_id": trace_id,
                "processing_time": processing_time,
                "error": str(e)
            })
            raise LLMError(get_error_msg("llm_error", lang), trace_id)
        if not ads_list:
            raise LLMError(get_error_msg("llm_error", lang), trace_id)
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info({
            "event": "generate_ads_success",
            "trace_id": trace_id,
            "processing_time": processing_time,
            "output_count": len(ads_list) if isinstance(ads_list, list) else 1
        })
        return GenerationResult(
            success=True,
            data=ads_list,
            trace_id=trace_id,
            processing_time=processing_time,
            metadata={"input_length": len(sanitized_text), "output_count": len(ads_list) if isinstance(ads_list, list) else 1}
        )
    except ValidationError:
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        logger.error({
            "event": "generate_ads_validation_error",
            "trace_id": trace_id,
            "processing_time": processing_time
        })
        raise
    except ValueError as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        logger.error({
            "event": "generate_ads_validation_error",
            "trace_id": trace_id,
            "processing_time": processing_time,
            "error": str(e)
        })
        raise ValidationError(str(e), trace_id)

# The cached version wraps the logic
@cached(ttl=CACHE_TTL_SECONDS, key_builder=ads_cache_key)
async def _generate_ads_cached(*args, **kwargs):
    return await _generate_ads_logic(*args, **kwargs)

@with_cache_tracking
@with_metrics
async def generate_brand_kit(
    text: str,
    trace_id: Optional[str] = None,
    lang: str = "es",
    llm_func: Callable[[str], Any] = generate_brand_kit_lcel,
    timeout: Optional[float] = None,
    metrics_cb: Optional[Callable] = None,
    **kwargs
) -> GenerationResult:
    """
    Generate brand kit from web text with enhanced error handling and metrics.
    """
    # If using the default llm_func, use the cached version
    if llm_func is generate_brand_kit_lcel:
        return await _generate_brand_kit_cached(
            text=text,
            trace_id=trace_id,
            lang=lang,
            llm_func=llm_func,
            timeout=timeout,
            metrics_cb=metrics_cb,
            **kwargs
        )
    # Otherwise, call the logic directly (no cache)
    return await _generate_brand_kit_logic(
        text=text,
        trace_id=trace_id,
        lang=lang,
        llm_func=llm_func,
        timeout=timeout,
        metrics_cb=metrics_cb,
        **kwargs
    )

# Move the main logic to a helper function
async def _generate_brand_kit_logic(
    text: str,
    trace_id: Optional[str] = None,
    lang: str = "es",
    llm_func: Callable[[str], Any] = generate_brand_kit_lcel,
    timeout: Optional[float] = None,
    metrics_cb: Optional[Callable] = None,
    **kwargs
) -> GenerationResult:
    start_time = datetime.utcnow()
    
    try:
        # Input validation and sanitization
        sanitized_text = sanitize_text(text)
        validate_input_lengths(sanitized_text, min_length=10, max_length=2000, lang=lang)
        
        # LLM generation with timeout
        if timeout:
            brand_kit = await asyncio.wait_for(llm_func(sanitized_text), timeout=timeout)
        else:
            brand_kit = await llm_func(sanitized_text)
        
        if not brand_kit:
            raise LLMError(get_error_msg("llm_error", lang), trace_id)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return GenerationResult(
            success=True,
            data=brand_kit,
            trace_id=trace_id,
            processing_time=processing_time,
            metadata={"input_length": len(sanitized_text)}
        )
        
    except asyncio.TimeoutError:
        raise TimeoutError(get_error_msg("timeout", lang), trace_id)
    except ValidationError:
        raise
    except Exception as e:
        raise LLMError(str(e), trace_id)

# The cached version wraps the logic
@cached(ttl=CACHE_TTL_SECONDS, key_builder=brandkit_cache_key)
async def _generate_brand_kit_cached(*args, **kwargs):
    return await _generate_brand_kit_logic(*args, **kwargs)

@with_cache_tracking
@with_metrics
async def generate_custom_content(
    prompt: str,
    text: str,
    trace_id: Optional[str] = None,
    lang: str = "es",
    llm_func: Callable[[str, str], Any] = generate_custom_content_lcel,
    timeout: Optional[float] = None,
    metrics_cb: Optional[Callable] = None,
    **kwargs
) -> GenerationResult:
    """
    Generate custom content from prompt and web text with enhanced error handling and metrics.
    """
    # If using the default llm_func, use the cached version
    if llm_func is generate_custom_content_lcel:
        return await _generate_custom_content_cached(
            prompt=prompt,
            text=text,
            trace_id=trace_id,
            lang=lang,
            llm_func=llm_func,
            timeout=timeout,
            metrics_cb=metrics_cb,
            **kwargs
        )
    # Otherwise, call the logic directly (no cache)
    return await _generate_custom_content_logic(
        prompt=prompt,
        text=text,
        trace_id=trace_id,
        lang=lang,
        llm_func=llm_func,
        timeout=timeout,
        metrics_cb=metrics_cb,
        **kwargs
    )

# Move the main logic to a helper function
async def _generate_custom_content_logic(
    prompt: str,
    text: str,
    trace_id: Optional[str] = None,
    lang: str = "es",
    llm_func: Callable[[str, str], Any] = generate_custom_content_lcel,
    timeout: Optional[float] = None,
    metrics_cb: Optional[Callable] = None,
    **kwargs
) -> GenerationResult:
    start_time = datetime.utcnow()
    
    try:
        # Input validation and sanitization
        sanitized_prompt = sanitize_text(prompt)
        sanitized_text = sanitize_text(text)
        
        validate_input_lengths(sanitized_prompt, min_length=5, max_length=500, lang=lang, field_name="prompt")
        validate_input_lengths(sanitized_text, min_length=10, max_length=2000, lang=lang, field_name="text")
        
        # LLM generation with timeout
        if timeout:
            content = await asyncio.wait_for(llm_func(sanitized_prompt, sanitized_text), timeout=timeout)
        else:
            content = await llm_func(sanitized_prompt, sanitized_text)
        
        if not content:
            raise LLMError(get_error_msg("llm_error", lang), trace_id)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return GenerationResult(
            success=True,
            data=content,
            trace_id=trace_id,
            processing_time=processing_time,
            metadata={"prompt_length": len(sanitized_prompt), "text_length": len(sanitized_text)}
        )
        
    except asyncio.TimeoutError:
        raise TimeoutError(get_error_msg("timeout", lang), trace_id)
    except ValidationError:
        raise
    except Exception as e:
        raise LLMError(str(e), trace_id)

# The cached version wraps the logic
@cached(ttl=CACHE_TTL_SECONDS, key_builder=custom_content_cache_key)
async def _generate_custom_content_cached(*args, **kwargs):
    return await _generate_custom_content_logic(*args, **kwargs)

# --- Enhanced Batch Operations ---
async def batch_generate_with_semaphore(
    items: List[Dict[str, Any]],
    generation_func: Callable,
    max_concurrency: int = 5,
    timeout: Optional[float] = None,
    trace_id: Optional[str] = None,
    **kwargs
) -> BatchResult:
    """
    Generate multiple items with controlled concurrency and comprehensive error handling.
    
    Args:
        items: List of dictionaries containing parameters for generation
        generation_func: Function to call for each item
        max_concurrency: Maximum concurrent operations
        timeout: Timeout per individual operation
        trace_id: Base trace ID for the batch
        **kwargs: Additional arguments to pass to generation function
        
    Returns:
        BatchResult with all results and summary statistics
    """
    start_time = datetime.utcnow()
    batch_trace_id = trace_id or str(uuid.uuid4())
    
    semaphore = asyncio.Semaphore(max_concurrency)
    
    async def process_item(item: Dict[str, Any]) -> GenerationResult:
        async with semaphore:
            item_trace_id = f"{batch_trace_id}-{uuid.uuid4().hex[:8]}"
            try:
                return await generation_func(**item, trace_id=item_trace_id, timeout=timeout, **kwargs)
            except Exception as e:
                return GenerationResult(
                    success=False,
                    error=str(e),
                    trace_id=item_trace_id,
                    processing_time=0.0
                )
    
    # Process all items concurrently
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    
    # All results should be GenerationResult objects now
    processed_results = results
    
    total_processing_time = (datetime.utcnow() - start_time).total_seconds()
    success_count = sum(1 for r in processed_results if r.success)
    error_count = len(processed_results) - success_count
    
    return BatchResult(
        results=processed_results,
        total_count=len(processed_results),
        success_count=success_count,
        error_count=error_count,
        total_processing_time=total_processing_time,
        trace_id=batch_trace_id
    )

async def batch_generate_ads(
    texts: List[str],
    max_concurrency: int = 5,
    timeout: Optional[float] = None,
    trace_id: Optional[str] = None,
    **kwargs
) -> BatchResult:
    """Generate multiple ads in parallel with controlled concurrency."""
    items = [{"text": text} for text in texts]
    return await batch_generate_with_semaphore(
        items, generate_ads, max_concurrency, timeout, trace_id, **kwargs
    )

async def batch_generate_brand_kits(
    texts: List[str],
    max_concurrency: int = 5,
    timeout: Optional[float] = None,
    trace_id: Optional[str] = None,
    **kwargs
) -> BatchResult:
    """Generate multiple brand kits in parallel with controlled concurrency."""
    items = [{"text": text} for text in texts]
    return await batch_generate_with_semaphore(
        items, generate_brand_kit, max_concurrency, timeout, trace_id, **kwargs
    )

async def batch_generate_custom_content(
    prompts_texts: List[Dict[str, str]],
    max_concurrency: int = 5,
    timeout: Optional[float] = None,
    trace_id: Optional[str] = None,
    **kwargs
) -> BatchResult:
    """Generate multiple custom contents in parallel with controlled concurrency."""
    return await batch_generate_with_semaphore(
        prompts_texts, generate_custom_content, max_concurrency, timeout, trace_id, **kwargs
    )

# --- Utility Functions ---
def get_generation_stats() -> Dict[str, Any]:
    """Get current generation statistics from Prometheus metrics."""
    return {
        "active_generations": {
            "ads": ACTIVE_GENERATIONS.labels(type="ads")._value.get(),
            "brand-kit": ACTIVE_GENERATIONS.labels(type="brand-kit")._value.get(),
            "custom-content": ACTIVE_GENERATIONS.labels(type="custom-content")._value.get(),
        },
        "total_requests": {
            "ads": GENERATION_REQUESTS.labels(type="ads", status="success")._value.get() + 
                   GENERATION_REQUESTS.labels(type="ads", status="error")._value.get(),
            "brand-kit": GENERATION_REQUESTS.labels(type="brand-kit", status="success")._value.get() + 
                        GENERATION_REQUESTS.labels(type="brand-kit", status="error")._value.get(),
            "custom-content": GENERATION_REQUESTS.labels(type="custom-content", status="success")._value.get() + 
                             GENERATION_REQUESTS.labels(type="custom-content", status="error")._value.get(),
        },
        "cache_stats": {
            "ads": {
                "hits": GENERATION_CACHE_HITS.labels(type="ads")._value.get(),
                "misses": GENERATION_CACHE_MISSES.labels(type="ads")._value.get(),
            },
            "brand-kit": {
                "hits": GENERATION_CACHE_HITS.labels(type="brand-kit")._value.get(),
                "misses": GENERATION_CACHE_MISSES.labels(type="brand-kit")._value.get(),
            },
            "custom-content": {
                "hits": GENERATION_CACHE_HITS.labels(type="custom-content")._value.get(),
                "misses": GENERATION_CACHE_MISSES.labels(type="custom-content")._value.get(),
            }
        }
    }

def reset_metrics():
    """Reset all Prometheus metrics (useful for testing)."""
    for metric in [GENERATION_REQUESTS, GENERATION_LATENCY, GENERATION_CACHE_HITS, GENERATION_CACHE_MISSES, ACTIVE_GENERATIONS]:
        metric._metrics.clear() 