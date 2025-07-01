"""
Utility functions for Instagram Captions API.

Pure functions and helpers for common operations, error handling, and performance optimization.
"""

import asyncio
import json
import hashlib
import time
from typing import Any, Dict, List, Optional, Callable, TypeVar, Union
from functools import wraps
from datetime import datetime, timezone
import logging

from fastapi import HTTPException
from pydantic import BaseModel

from .schemas import ErrorResponse

logger = logging.getLogger(__name__)

T = TypeVar('T')


def create_error_response(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create standardized error response."""
    return ErrorResponse(
        error_code=error_code,
        message=message,
        details=details or {},
        request_id=request_id
    )


def handle_api_errors(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for standardized API error handling with early returns."""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except ValueError as e:
            logger.warning(f"Validation error in {func.__name__}: {e}")
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    error_code="VALIDATION_ERROR",
                    message=str(e)
                ).model_dump()
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=create_error_response(
                    error_code="INTERNAL_ERROR",
                    message="An unexpected error occurred"
                ).model_dump()
            )
    
    return wrapper


def validate_non_empty_string(value: str, field_name: str) -> str:
    """Validate that string is not empty with early return."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value.strip()


def validate_list_not_empty(value: List[Any], field_name: str) -> List[Any]:
    """Validate that list is not empty with early return."""
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    return value


def validate_numeric_range(
    value: Union[int, float], 
    min_val: Union[int, float], 
    max_val: Union[int, float], 
    field_name: str
) -> Union[int, float]:
    """Validate numeric value is within range with early return."""
    if value < min_val or value > max_val:
        raise ValueError(f"{field_name} must be between {min_val} and {max_val}")
    return value


def generate_cache_key(*args, **kwargs) -> str:
    """Generate consistent cache key from arguments."""
    # Create a deterministic string from arguments
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def measure_execution_time(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure and log function execution time."""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.perf_counter() - start_time
            
            logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            logger.warning(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper


async def timeout_operation(
    operation: Callable[..., T],
    timeout_seconds: float,
    *args,
    **kwargs
) -> T:
    """Execute operation with timeout."""
    try:
        return await asyncio.wait_for(
            operation(*args, **kwargs),
            timeout=timeout_seconds
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail=create_error_response(
                error_code="OPERATION_TIMEOUT",
                message=f"Operation timed out after {timeout_seconds} seconds"
            ).model_dump()
        )


def serialize_for_cache(data: Any) -> str:
    """Serialize data for caching with proper handling of complex types."""
    if isinstance(data, BaseModel):
        return data.model_dump_json()
    
    try:
        return json.dumps(data, default=str, sort_keys=True)
    except TypeError as e:
        logger.warning(f"Failed to serialize data for cache: {e}")
        return json.dumps({"error": "serialization_failed"})


def deserialize_from_cache(data: str, model_class: Optional[type] = None) -> Any:
    """Deserialize data from cache with optional model validation."""
    try:
        parsed = json.loads(data)
        
        if model_class and issubclass(model_class, BaseModel):
            return model_class.model_validate(parsed)
        
        return parsed
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to deserialize cached data: {e}")
        return None


def normalize_timezone_string(timezone_str: str) -> str:
    """Normalize timezone string with validation."""
    if not timezone_str:
        return "UTC"
    
    # Basic validation
    normalized = timezone_str.strip().replace(" ", "_")
    
    # Common timezone mappings
    timezone_mappings = {
        "est": "US/Eastern",
        "pst": "US/Pacific",
        "cst": "US/Central",
        "mst": "US/Mountain",
        "utc": "UTC",
        "gmt": "UTC"
    }
    
    return timezone_mappings.get(normalized.lower(), normalized)


def extract_keywords_from_text(text: str, max_keywords: int = 10) -> List[str]:
    """Extract meaningful keywords from text with filtering."""
    if not text:
        return []
    
    # Simple keyword extraction
    import re
    
    # Remove special characters and split
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
    }
    
    # Get meaningful words
    keywords = [word for word in words if len(word) > 3 and word not in stop_words]
    
    # Remove duplicates while preserving order
    unique_keywords = []
    seen = set()
    for keyword in keywords:
        if keyword not in seen:
            unique_keywords.append(keyword)
            seen.add(keyword)
    
    return unique_keywords[:max_keywords]


def calculate_improvement_percentage(original_score: float, new_score: float) -> float:
    """Calculate improvement percentage with proper handling of edge cases."""
    if original_score <= 0:
        return 100.0 if new_score > 0 else 0.0
    
    improvement = ((new_score - original_score) / original_score) * 100
    return round(improvement, 2)


def validate_caption_length(caption: str, content_type: str = "post") -> bool:
    """Validate caption length based on content type."""
    length_limits = {
        "post": 2200,
        "story": 500,
        "reel": 1000,
        "carousel": 2200
    }
    
    max_length = length_limits.get(content_type.lower(), 2200)
    return len(caption) <= max_length


def sanitize_hashtags(hashtags: List[str]) -> List[str]:
    """Sanitize and validate hashtags."""
    sanitized = []
    
    for hashtag in hashtags:
        # Remove extra spaces and special characters
        clean_tag = re.sub(r'[^\w\-_]', '', hashtag.strip())
        
        # Ensure it starts with #
        if not clean_tag.startswith('#'):
            clean_tag = f"#{clean_tag}"
        
        # Remove # for length validation
        tag_content = clean_tag[1:]
        
        # Validate length and content
        if 1 <= len(tag_content) <= 30 and tag_content.replace('_', '').isalnum():
            sanitized.append(clean_tag.lower())
    
    # Remove duplicates while preserving order
    unique_hashtags = []
    seen = set()
    for tag in sanitized:
        if tag not in seen:
            unique_hashtags.append(tag)
            seen.add(tag)
    
    return unique_hashtags


def calculate_readability_score(text: str) -> float:
    """Calculate simple readability score for Instagram content."""
    if not text:
        return 0.0
    
    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?') + 1
    
    if not words or sentences == 0:
        return 0.0
    
    avg_words_per_sentence = len(words) / sentences
    avg_word_length = sum(len(word) for word in words) / len(words)
    
    # Optimal for Instagram: 10-20 words/sentence, 4-6 chars/word
    sentence_score = max(0, 1 - abs(avg_words_per_sentence - 15) / 20)
    word_score = max(0, 1 - abs(avg_word_length - 5) / 5)
    
    return round((sentence_score + word_score) / 2 * 100, 1)


def get_current_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def batch_process_with_concurrency(
    items: List[T],
    processor: Callable[[T], Any],
    max_concurrency: int = 5
) -> List[Any]:
    """Process items in batches with controlled concurrency."""
    async def process_batch(batch_items: List[T]) -> List[Any]:
        tasks = [processor(item) for item in batch_items]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    # Split items into batches
    batches = [
        items[i:i + max_concurrency] 
        for i in range(0, len(items), max_concurrency)
    ]
    
    # Process all batches
    all_results = []
    for batch in batches:
        batch_results = asyncio.run(process_batch(batch))
        all_results.extend(batch_results)
    
    return all_results


def format_duration_human_readable(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


class PerformanceMonitor:
    """Simple performance monitoring utility."""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, operation: str) -> float:
        """Start timing an operation."""
        start_time = time.perf_counter()
        self.metrics[operation] = {"start_time": start_time}
        return start_time
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration."""
        if operation not in self.metrics:
            return 0.0
        
        end_time = time.perf_counter()
        duration = end_time - self.metrics[operation]["start_time"]
        self.metrics[operation]["duration"] = duration
        self.metrics[operation]["end_time"] = end_time
        
        return duration
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return self.metrics.copy()
    
    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def log_performance_metrics(operation: str):
    """Decorator to automatically log performance metrics."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = performance_monitor.start_timer(operation)
            
            try:
                result = await func(*args, **kwargs)
                duration = performance_monitor.end_timer(operation)
                logger.info(f"Operation '{operation}' completed in {format_duration_human_readable(duration)}")
                return result
            except Exception as e:
                duration = performance_monitor.end_timer(operation)
                logger.warning(f"Operation '{operation}' failed after {format_duration_human_readable(duration)}: {e}")
                raise
        
        return wrapper
    return decorator 