"""
Production Utilities for Onyx Features.

Common utilities optimized for production use with async support,
caching, retry logic, and comprehensive error handling.
Enhanced with high-performance libraries for maximum efficiency.
"""

import asyncio
import uuid
import time
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from datetime import datetime, timezone, timedelta
from pathlib import Path
from functools import wraps
from contextlib import asynccontextmanager

import aiofiles
import aiohttp  # Faster than httpx for high concurrency
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from cachetools import TTLCache, LRUCache
import structlog
from rich.console import Console
from rich.progress import Progress, TaskID
from pydantic import BaseModel, Field, validator

# High-performance libraries
import orjson  # Ultra-fast JSON
import polars as pl  # Ultra-fast DataFrame processing
import numpy as np  # Numerical operations
import xxhash  # Fast hashing
import lz4.frame  # Fast compression
import psutil  # System monitoring
from asyncio_throttle import Throttler  # Rate limiting

# Import our optimization module
from .optimization import FastSerializer, FastHasher, VectorizedProcessor, MemoryOptimizer

# Configure logging
logger = structlog.get_logger(__name__)
console = Console()

# Type variables
T = TypeVar('T')
P = TypeVar('P')

# Global caches
memory_cache = TTLCache(maxsize=1000, ttl=3600)  # 1 hour TTL
lru_cache = LRUCache(maxsize=500)

# Constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
CHUNK_SIZE = 8192


class CacheConfig(BaseModel):
    """Cache configuration."""
    ttl_seconds: int = Field(default=3600, ge=60, le=86400)
    max_size: int = Field(default=1000, ge=10, le=10000)
    enable_compression: bool = Field(default=True)
    
    @validator('ttl_seconds')
    def validate_ttl(cls, v):
        if v < 60:
            raise ValueError("TTL must be at least 60 seconds")
        return v


class RetryConfig(BaseModel):
    """Retry configuration."""
    max_attempts: int = Field(default=MAX_RETRIES, ge=1, le=10)
    min_wait: float = Field(default=1.0, ge=0.1, le=10.0)
    max_wait: float = Field(default=60.0, ge=1.0, le=300.0)
    exponential_base: int = Field(default=2, ge=2, le=10)


class AsyncLimiter:
    """Async rate limiter for controlling concurrent operations."""
    
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_concurrent = max_concurrent
    
    async def __aenter__(self):
        await self.semaphore.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.semaphore.release()


class ProgressTracker:
    """Progress tracking for long-running operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.description = description
        self.current = 0
        self.start_time = time.time()
        self.progress = Progress()
        self.task_id: Optional[TaskID] = None
    
    def start(self):
        """Start progress tracking."""
        self.progress.start()
        self.task_id = self.progress.add_task(self.description, total=self.total)
        return self
    
    def update(self, advance: int = 1):
        """Update progress."""
        if self.task_id is not None:
            self.current += advance
            self.progress.update(self.task_id, advance=advance)
    
    def finish(self):
        """Finish progress tracking."""
        if self.task_id is not None:
            self.progress.stop()
            elapsed = time.time() - self.start_time
            logger.info("Operation completed", 
                       total=self.total, 
                       elapsed_seconds=elapsed,
                       items_per_second=self.total / elapsed if elapsed > 0 else 0)


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for request tracking."""
    return f"onyx_{uuid.uuid4().hex[:12]}_{int(time.time())}"


def hash_content(content: Union[str, bytes], algorithm: str = "xxhash") -> str:
    """
    Generate hash for content using ultra-fast algorithms.
    
    Args:
        content: Content to hash
        algorithm: Hash algorithm (xxhash, sha256, md5, sha1, sha512)
        
    Returns:
        str: Hex digest of hash
    """
    if algorithm == "xxhash":
        # Use ultra-fast xxHash for production
        return FastHasher.hash_fast(content)
    else:
        # Fallback to standard algorithms
        import hashlib
        if isinstance(content, str):
            content = content.encode('utf-8')
        hasher = hashlib.new(algorithm)
        hasher.update(content)
        return hasher.hexdigest()


def safe_json_serialize(obj: Any, use_orjson: bool = True) -> str:
    """
    Safely serialize object to JSON using ultra-fast serialization.
    
    Args:
        obj: Object to serialize
        use_orjson: Use orjson for faster serialization
        
    Returns:
        str: JSON string
    """
    try:
        if use_orjson:
            # Use ultra-fast orjson serialization
            result = FastSerializer.serialize_json(obj)
            return result.decode('utf-8') if isinstance(result, bytes) else result
        else:
            # Fallback to standard JSON
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, Path):
                    return str(obj)
                elif hasattr(obj, '__dict__'):
                    return obj.__dict__
                else:
                    return str(obj)
            
            import json
            return json.dumps(obj, default=json_serializer, ensure_ascii=False)
    except Exception as e:
        logger.warning("JSON serialization failed", error=str(e))
        import json
        return json.dumps({"error": "Serialization failed", "type": type(obj).__name__})


def safe_json_deserialize(json_str: Union[str, bytes], default: Any = None, use_orjson: bool = True) -> Any:
    """
    Safely deserialize JSON string using ultra-fast deserialization.
    
    Args:
        json_str: JSON string or bytes to deserialize
        default: Default value if deserialization fails
        use_orjson: Use orjson for faster deserialization
        
    Returns:
        Any: Deserialized object or default
    """
    try:
        if use_orjson:
            # Use ultra-fast orjson deserialization
            if isinstance(json_str, str):
                json_str = json_str.encode('utf-8')
            return FastSerializer.deserialize_json(json_str)
        else:
            # Fallback to standard JSON
            import json
            if isinstance(json_str, bytes):
                json_str = json_str.decode('utf-8')
            return json.loads(json_str)
    except Exception as e:
        logger.warning("JSON deserialization failed", error=str(e))
        return default


def cached(ttl: int = 3600, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds
        key_func: Function to generate cache key
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache = TTLCache(maxsize=100, ttl=ttl)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = hash_content(f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}")
            
            # Check cache
            if cache_key in cache:
                logger.debug("Cache hit", function=func.__name__, key=cache_key)
                return cache[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = result
            logger.debug("Cache miss - result cached", function=func.__name__, key=cache_key)
            return result
        
        return wrapper
    return decorator


def async_cached(ttl: int = 3600, key_func: Optional[Callable] = None):
    """
    Decorator for caching async function results.
    
    Args:
        ttl: Time to live in seconds
        key_func: Function to generate cache key
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache = TTLCache(maxsize=100, ttl=ttl)
        
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = hash_content(f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}")
            
            # Check cache
            if cache_key in cache:
                logger.debug("Cache hit", function=func.__name__, key=cache_key)
                return cache[cache_key]
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = result
            logger.debug("Cache miss - result cached", function=func.__name__, key=cache_key)
            return result
        
        return wrapper
    return decorator


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        config: Retry configuration
        exceptions: Exceptions to retry on
    """
    if config is None:
        config = RetryConfig()
    
    return retry(
        stop=stop_after_attempt(config.max_attempts),
        wait=wait_exponential(
            multiplier=config.min_wait,
            max=config.max_wait,
            exp_base=config.exponential_base
        ),
        retry=retry_if_exception_type(exceptions),
        reraise=True
    )


async def async_file_read(file_path: Union[str, Path], chunk_size: int = CHUNK_SIZE) -> bytes:
    """
    Asynchronously read file contents.
    
    Args:
        file_path: Path to file
        chunk_size: Size of chunks to read
        
    Returns:
        bytes: File contents
    """
    try:
        async with aiofiles.open(file_path, 'rb') as file:
            content = await file.read()
            return content
    except Exception as e:
        logger.error("Failed to read file", file_path=str(file_path), error=str(e))
        raise


async def async_file_write(
    file_path: Union[str, Path], 
    content: Union[str, bytes],
    mode: str = 'w'
) -> bool:
    """
    Asynchronously write content to file.
    
    Args:
        file_path: Path to file
        content: Content to write
        mode: File open mode
        
    Returns:
        bool: True if successful
    """
    try:
        async with aiofiles.open(file_path, mode) as file:
            await file.write(content)
            return True
    except Exception as e:
        logger.error("Failed to write file", file_path=str(file_path), error=str(e))
        return False


async def async_http_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Any] = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = MAX_RETRIES
) -> Optional[httpx.Response]:
    """
    Make async HTTP request with retry logic.
    
    Args:
        url: Request URL
        method: HTTP method
        headers: Request headers
        data: Request data
        timeout: Request timeout
        retries: Number of retries
        
    Returns:
        httpx.Response or None if failed
    """
    @retry_with_backoff(
        config=RetryConfig(max_attempts=retries),
        exceptions=(httpx.RequestError, httpx.HTTPStatusError)
    )
    async def _make_request():
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=data if isinstance(data, dict) else None,
                data=data if not isinstance(data, dict) else None
            )
            response.raise_for_status()
            return response
    
    try:
        return await _make_request()
    except Exception as e:
        logger.error("HTTP request failed", url=url, method=method, error=str(e))
        return None


async def batch_process(
    items: List[T],
    processor: Callable[[T], Any],
    batch_size: int = 10,
    max_concurrent: int = 5,
    show_progress: bool = True
) -> List[Any]:
    """
    Process items in batches with concurrency control.
    
    Args:
        items: Items to process
        processor: Processing function
        batch_size: Size of each batch
        max_concurrent: Maximum concurrent operations
        show_progress: Whether to show progress
        
    Returns:
        List: Processing results
    """
    results = []
    limiter = AsyncLimiter(max_concurrent)
    
    # Setup progress tracking
    tracker = None
    if show_progress:
        tracker = ProgressTracker(len(items), "Processing items").start()
    
    try:
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_tasks = []
            
            for item in batch:
                async def process_item(item_to_process):
                    async with limiter:
                        if asyncio.iscoroutinefunction(processor):
                            return await processor(item_to_process)
                        else:
                            return processor(item_to_process)
                
                batch_tasks.append(process_item(item))
            
            # Process batch
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Update progress
            if tracker:
                tracker.update(len(batch))
        
        return results
        
    finally:
        if tracker:
            tracker.finish()


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if valid
    """
    try:
        import urllib.parse
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human readable string.
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        str: Formatted string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration into human readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


@asynccontextmanager
async def async_timer(operation: str = "operation"):
    """
    Context manager to time async operations.
    
    Args:
        operation: Operation name for logging
    """
    start_time = time.time()
    logger.info("Operation started", operation=operation)
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.info("Operation completed", 
                   operation=operation, 
                   duration=format_duration(duration))


# Export main components
__all__ = [
    "CacheConfig",
    "RetryConfig",
    "AsyncLimiter",
    "ProgressTracker",
    "generate_correlation_id",
    "hash_content",
    "safe_json_serialize",
    "safe_json_deserialize",
    "cached",
    "async_cached",
    "retry_with_backoff",
    "async_file_read",
    "async_file_write",
    "async_http_request",
    "batch_process",
    "validate_url",
    "format_bytes",
    "format_duration",
    "async_timer",
    "memory_cache",
    "lru_cache"
]

# Initialize utilities
logger.info("Production utilities initialized") 