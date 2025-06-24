import logging
import uuid
import asyncio
import re
import html
from typing import Callable, Any, Optional, Dict

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS: int = 120  # TTL global para cache de generación

ERRORS_I18N = {
    "es": {
        "short_text": "Texto demasiado corto.",
        "long_text": "Texto demasiado largo.",
        "short_prompt": "Prompt demasiado corto.",
        "long_prompt": "Prompt demasiado largo.",
        "llm_error": "Error al generar contenido: respuesta vacía o error de LLM.",
        "cancelled": "La generación fue cancelada por el usuario o el sistema.",
        "timeout": "La operación excedió el tiempo límite.",
        "invalid_input": "Entrada inválida proporcionada.",
        "sanitization_error": "Error al sanitizar la entrada.",
    },
    "en": {
        "short_text": "Text too short.",
        "long_text": "Text too long.",
        "short_prompt": "Prompt too short.",
        "long_prompt": "Prompt too long.",
        "llm_error": "Error generating content: empty response or LLM error.",
        "cancelled": "Generation was cancelled by user or system.",
        "timeout": "Operation exceeded time limit.",
        "invalid_input": "Invalid input provided.",
        "sanitization_error": "Error sanitizing input.",
    }
}

def get_error_msg(key: str, lang: str = "es") -> str:
    """
    Devuelve el mensaje de error localizado para la clave y el idioma dados.
    """
    return ERRORS_I18N.get(lang, ERRORS_I18N["es"]).get(key, key)

# --- Input Sanitization and Validation ---
def sanitize_text(text: str) -> str:
    """
    Sanitize input text by removing potentially harmful content and normalizing whitespace.
    
    Args:
        text: Raw input text
        
    Returns:
        Sanitized text
        
    Raises:
        ValueError: If text is None or empty after sanitization
    """
    if not text:
        raise ValueError("Text cannot be None or empty")
    
    # Convert to string if not already
    text = str(text)
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove potentially harmful characters and scripts
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<iframe[^>]*>.*?</iframe>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<object[^>]*>.*?</object>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<embed[^>]*>.*?</embed>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove HTML tags but keep content
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    if not text:
        raise ValueError("Text is empty after sanitization")
    
    return text

def validate_input_lengths(
    text: str, 
    min_length: int = 10, 
    max_length: int = 2000, 
    lang: str = "es",
    field_name: str = "text"
) -> None:
    """
    Validate input text length with localized error messages.
    
    Args:
        text: Text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        lang: Language for error messages
        field_name: Name of the field for error messages
        
    Raises:
        ValueError: If text length is invalid
    """
    if not isinstance(text, str):
        raise ValueError(f"{field_name} must be a string")
    
    text_length = len(text)
    
    if text_length < min_length:
        error_key = "short_text" if field_name == "text" else "short_prompt"
        raise ValueError(get_error_msg(error_key, lang))
    
    if text_length > max_length:
        error_key = "long_text" if field_name == "text" else "long_prompt"
        raise ValueError(get_error_msg(error_key, lang))

def validate_url(url: str) -> str:
    """
    Validate and sanitize URL input.
    
    Args:
        url: URL to validate
        
    Returns:
        Sanitized URL
        
    Raises:
        ValueError: If URL is invalid
    """
    if not url:
        raise ValueError("URL cannot be empty")
    
    url = str(url).strip()
    
    # Basic URL validation
    if not re.match(r'^https?://', url):
        raise ValueError("URL must start with http:// or https://")
    
    # Remove potentially harmful characters
    url = re.sub(r'[^\w\-._~:/?#[\]@!$&\'()*+,;=%]', '', url)
    
    return url

# --- Enhanced Cache Key Builders ---
def ads_cache_key(func: Callable, text: str, lang: str = "es", **kwargs) -> str:
    """
    Generate cache key for ads generation.
    
    Args:
        func: Function being cached
        text: Input text
        lang: Language
        **kwargs: Additional parameters
        
    Returns:
        Cache key string
    """
    # Sanitize text for consistent cache keys
    sanitized_text = sanitize_text(text)[:100]  # Limit length for cache key
    return f"ads:{hash(sanitized_text)}:{lang}"

def brandkit_cache_key(func: Callable, text: str, lang: str = "es", **kwargs) -> str:
    """
    Generate cache key for brand kit generation.
    
    Args:
        func: Function being cached
        text: Input text
        lang: Language
        **kwargs: Additional parameters
        
    Returns:
        Cache key string
    """
    sanitized_text = sanitize_text(text)[:100]
    return f"brandkit:{hash(sanitized_text)}:{lang}"

def custom_content_cache_key(func: Callable, prompt: str, text: str, lang: str = "es", **kwargs) -> str:
    """
    Generate cache key for custom content generation.
    
    Args:
        func: Function being cached
        prompt: Custom prompt
        text: Input text
        lang: Language
        **kwargs: Additional parameters
        
    Returns:
        Cache key string
    """
    sanitized_prompt = sanitize_text(prompt)[:50]
    sanitized_text = sanitize_text(text)[:100]
    return f"custom_content:{hash(sanitized_prompt)}:{hash(sanitized_text)}:{lang}"

# --- Enhanced Logging Decorator ---
def log_with_trace(func: Callable) -> Callable:
    """
    Enhanced decorator for structured logging, trace_id, i18n and metrics in async functions.
    Now includes input validation and better error handling.
    """
    async def wrapper(*args, trace_id: Optional[str] = None, lang: str = "es", extra_log: Optional[Dict] = None, metrics_cb: Optional[Callable] = None, timeout: Optional[float] = None, **kwargs):
        trace_id = trace_id or str(uuid.uuid4())
        
        # Prepare log data
        log_data = {
            "event": f"{func.__name__}_start", 
            "trace_id": trace_id, 
            "lang": lang,
            "function": func.__name__
        }
        
        if extra_log:
            log_data.update(extra_log)
        
        # Log start with input validation info
        logger.info(log_data)
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Execute function with timeout if specified
            coro = func(*args, trace_id=trace_id, lang=lang, **kwargs)
            if timeout:
                result = await asyncio.wait_for(coro, timeout=timeout)
            else:
                result = await coro
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Log success
            success_log = {
                "event": f"{func.__name__}_success",
                "trace_id": trace_id,
                "processing_time": processing_time
            }
            logger.info(success_log)
            
            # Call metrics callback if provided
            if metrics_cb:
                metrics_cb(func.__name__, success=True, processing_time=processing_time)
            
            return result
            
        except asyncio.TimeoutError:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.warning({
                "event": f"{func.__name__}_timeout",
                "trace_id": trace_id,
                "processing_time": processing_time,
                "timeout": timeout
            })
            if metrics_cb:
                metrics_cb(func.__name__, success=False, error="timeout", processing_time=processing_time)
            return {"error": get_error_msg("timeout", lang), "details": None, "trace_id": trace_id}
            
        except asyncio.CancelledError:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.warning({
                "event": f"{func.__name__}_cancelled",
                "trace_id": trace_id,
                "processing_time": processing_time
            })
            if metrics_cb:
                metrics_cb(func.__name__, success=False, error="cancelled", processing_time=processing_time)
            return {"error": get_error_msg("cancelled", lang), "details": None, "trace_id": trace_id}
            
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error({
                "event": f"{func.__name__}_error",
                "trace_id": trace_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "processing_time": processing_time
            })
            if metrics_cb:
                metrics_cb(func.__name__, success=False, error=str(e), processing_time=processing_time)
            return {"error": str(e), "details": None, "trace_id": trace_id}
    
    return wrapper

# --- Performance Monitoring ---
def measure_performance(func: Callable) -> Callable:
    """
    Decorator to measure function performance and log metrics.
    """
    async def wrapper(*args, **kwargs):
        start_time = asyncio.get_event_loop().time()
        try:
            result = await func(*args, **kwargs)
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Log performance metrics
            logger.info({
                "event": "performance_metric",
                "function": func.__name__,
                "processing_time": processing_time,
                "status": "success"
            })
            
            return result
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            
            logger.error({
                "event": "performance_metric",
                "function": func.__name__,
                "processing_time": processing_time,
                "status": "error",
                "error": str(e)
            })
            raise
    
    return wrapper

# --- Rate Limiting Utilities ---
class RateLimiter:
    """
    Simple in-memory rate limiter for API endpoints.
    """
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            key: Unique identifier for the requester
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = asyncio.get_event_loop().time()
        
        # Clean old entries
        self.requests = {
            k: v for k, v in self.requests.items() 
            if now - v['timestamp'] < self.window_seconds
        }
        
        # Check current requests for this key
        if key not in self.requests:
            self.requests[key] = {'count': 1, 'timestamp': now}
            return True
        
        if self.requests[key]['count'] >= self.max_requests:
            return False
        
        self.requests[key]['count'] += 1
        return True

# --- Global rate limiter instance ---
rate_limiter = RateLimiter()

# --- Utility Functions ---
def generate_trace_id() -> str:
    """
    Generate a unique trace ID for request tracking.
    
    Returns:
        Unique trace ID string
    """
    return str(uuid.uuid4())

def format_processing_time(seconds: float) -> str:
    """
    Format processing time in a human-readable format.
    
    Args:
        seconds: Processing time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.2f}s"

def validate_batch_size(items: list, max_size: int = 50) -> None:
    """
    Validate batch size to prevent abuse.
    
    Args:
        items: List of items to process
        max_size: Maximum allowed batch size
        
    Raises:
        ValueError: If batch size exceeds limit
    """
    if len(items) > max_size:
        raise ValueError(f"Batch size {len(items)} exceeds maximum limit of {max_size}")
    
    if len(items) == 0:
        raise ValueError("Batch cannot be empty") 