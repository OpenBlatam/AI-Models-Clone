"""
Rate limiting utilities following functional patterns
"""
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import asyncio
from functools import wraps
from collections import defaultdict, deque

from app.core.errors import handle_rate_limit_error


class RateLimiter:
    """Simple rate limiter implementation."""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def _clean_old_requests(self, key: str) -> None:
        """Remove old requests outside the time window."""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.time_window)
        
        while self.requests[key] and self.requests[key][0] < cutoff:
            self.requests[key].popleft()
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed."""
        now = datetime.utcnow()
        self._clean_old_requests(key)
        
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        self.requests[key].append(now)
        return True
    
    def get_remaining_requests(self, key: str) -> int:
        """Get remaining requests in current window."""
        self._clean_old_requests(key)
        return max(0, self.max_requests - len(self.requests[key]))
    
    def get_reset_time(self, key: str) -> Optional[datetime]:
        """Get time when rate limit resets."""
        if not self.requests[key]:
            return None
        
        oldest_request = self.requests[key][0]
        return oldest_request + timedelta(seconds=self.time_window)


# Global rate limiters
_rate_limiters: Dict[str, RateLimiter] = {}


def create_rate_limiter(name: str, max_requests: int, time_window: int) -> RateLimiter:
    """Create a named rate limiter."""
    limiter = RateLimiter(max_requests, time_window)
    _rate_limiters[name] = limiter
    return limiter


def get_rate_limiter(name: str) -> Optional[RateLimiter]:
    """Get a named rate limiter."""
    return _rate_limiters.get(name)


def rate_limit(
    limiter_name: str,
    key_func: Optional[Callable] = None,
    error_message: str = "Rate limit exceeded"
):
    """Decorator for rate limiting."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            limiter = get_rate_limiter(limiter_name)
            if not limiter:
                raise ValueError(f"Rate limiter '{limiter_name}' not found")
            
            # Generate rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Default to using first argument as key
                key = str(args[0]) if args else "default"
            
            # Check rate limit
            if not limiter.is_allowed(key):
                remaining = limiter.get_remaining_requests(key)
                reset_time = limiter.get_reset_time(key)
                
                raise handle_rate_limit_error(
                    f"{error_message}. Try again in {reset_time}."
                )
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            limiter = get_rate_limiter(limiter_name)
            if not limiter:
                raise ValueError(f"Rate limiter '{limiter_name}' not found")
            
            # Generate rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Default to using first argument as key
                key = str(args[0]) if args else "default"
            
            # Check rate limit
            if not limiter.is_allowed(key):
                remaining = limiter.get_remaining_requests(key)
                reset_time = limiter.get_reset_time(key)
                
                raise handle_rate_limit_error(
                    f"{error_message}. Try again in {reset_time}."
                )
            
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Predefined rate limiters
def setup_default_rate_limiters() -> None:
    """Setup default rate limiters."""
    # API rate limiter: 100 requests per minute
    create_rate_limiter("api", 100, 60)
    
    # AI generation rate limiter: 10 requests per minute
    create_rate_limiter("ai_generation", 10, 60)
    
    # AI analysis rate limiter: 20 requests per minute
    create_rate_limiter("ai_analysis", 20, 60)
    
    # AI translation rate limiter: 15 requests per minute
    create_rate_limiter("ai_translation", 15, 60)
    
    # AI summarization rate limiter: 10 requests per minute
    create_rate_limiter("ai_summarization", 10, 60)
    
    # AI improvement rate limiter: 10 requests per minute
    create_rate_limiter("ai_improvement", 10, 60)
    
    # Document creation rate limiter: 5 requests per minute
    create_rate_limiter("document_creation", 5, 60)
    
    # Document update rate limiter: 20 requests per minute
    create_rate_limiter("document_update", 20, 60)
    
    # Collaboration rate limiter: 50 requests per minute
    create_rate_limiter("collaboration", 50, 60)
    
    # Chat message rate limiter: 30 requests per minute
    create_rate_limiter("chat_messages", 30, 60)
    
    # Search rate limiter: 20 requests per minute
    create_rate_limiter("search", 20, 60)
    
    # File upload rate limiter: 5 requests per minute
    create_rate_limiter("file_upload", 5, 60)
    
    # Authentication rate limiter: 5 requests per minute
    create_rate_limiter("auth", 5, 60)
    
    # Password reset rate limiter: 3 requests per hour
    create_rate_limiter("password_reset", 3, 3600)
    
    # Email verification rate limiter: 5 requests per hour
    create_rate_limiter("email_verification", 5, 3600)


# Rate limiting utilities for specific use cases
def rate_limit_by_user_id(user_id: str, limiter_name: str) -> bool:
    """Rate limit by user ID."""
    limiter = get_rate_limiter(limiter_name)
    if not limiter:
        return True
    
    return limiter.is_allowed(f"user:{user_id}")


def rate_limit_by_ip(ip_address: str, limiter_name: str) -> bool:
    """Rate limit by IP address."""
    limiter = get_rate_limiter(limiter_name)
    if not limiter:
        return True
    
    return limiter.is_allowed(f"ip:{ip_address}")


def rate_limit_by_organization(org_id: str, limiter_name: str) -> bool:
    """Rate limit by organization ID."""
    limiter = get_rate_limiter(limiter_name)
    if not limiter:
        return True
    
    return limiter.is_allowed(f"org:{org_id}")


def rate_limit_by_document(document_id: str, limiter_name: str) -> bool:
    """Rate limit by document ID."""
    limiter = get_rate_limiter(limiter_name)
    if not limiter:
        return True
    
    return limiter.is_allowed(f"doc:{document_id}")


def get_rate_limit_info(key: str, limiter_name: str) -> Dict[str, Any]:
    """Get rate limit information for a key."""
    limiter = get_rate_limiter(limiter_name)
    if not limiter:
        return {"error": "Rate limiter not found"}
    
    remaining = limiter.get_remaining_requests(key)
    reset_time = limiter.get_reset_time(key)
    
    return {
        "remaining": remaining,
        "reset_time": reset_time.isoformat() if reset_time else None,
        "max_requests": limiter.max_requests,
        "time_window": limiter.time_window
    }


def reset_rate_limit(key: str, limiter_name: str) -> bool:
    """Reset rate limit for a key."""
    limiter = get_rate_limiter(limiter_name)
    if not limiter:
        return False
    
    if key in limiter.requests:
        limiter.requests[key].clear()
        return True
    
    return False


def get_all_rate_limiters() -> Dict[str, Dict[str, Any]]:
    """Get information about all rate limiters."""
    return {
        name: {
            "max_requests": limiter.max_requests,
            "time_window": limiter.time_window,
            "active_keys": len(limiter.requests)
        }
        for name, limiter in _rate_limiters.items()
    }


def cleanup_expired_rate_limits() -> None:
    """Clean up expired rate limit entries."""
    for limiter in _rate_limiters.values():
        for key in list(limiter.requests.keys()):
            limiter._clean_old_requests(key)
            if not limiter.requests[key]:
                del limiter.requests[key]


# Rate limiting decorators for common use cases
def rate_limit_ai_generation(key_func: Optional[Callable] = None):
    """Rate limit AI generation requests."""
    return rate_limit("ai_generation", key_func, "AI generation rate limit exceeded")


def rate_limit_ai_analysis(key_func: Optional[Callable] = None):
    """Rate limit AI analysis requests."""
    return rate_limit("ai_analysis", key_func, "AI analysis rate limit exceeded")


def rate_limit_ai_translation(key_func: Optional[Callable] = None):
    """Rate limit AI translation requests."""
    return rate_limit("ai_translation", key_func, "AI translation rate limit exceeded")


def rate_limit_ai_summarization(key_func: Optional[Callable] = None):
    """Rate limit AI summarization requests."""
    return rate_limit("ai_summarization", key_func, "AI summarization rate limit exceeded")


def rate_limit_ai_improvement(key_func: Optional[Callable] = None):
    """Rate limit AI improvement requests."""
    return rate_limit("ai_improvement", key_func, "AI improvement rate limit exceeded")


def rate_limit_document_creation(key_func: Optional[Callable] = None):
    """Rate limit document creation requests."""
    return rate_limit("document_creation", key_func, "Document creation rate limit exceeded")


def rate_limit_document_update(key_func: Optional[Callable] = None):
    """Rate limit document update requests."""
    return rate_limit("document_update", key_func, "Document update rate limit exceeded")


def rate_limit_collaboration(key_func: Optional[Callable] = None):
    """Rate limit collaboration requests."""
    return rate_limit("collaboration", key_func, "Collaboration rate limit exceeded")


def rate_limit_chat_messages(key_func: Optional[Callable] = None):
    """Rate limit chat message requests."""
    return rate_limit("chat_messages", key_func, "Chat message rate limit exceeded")


def rate_limit_search(key_func: Optional[Callable] = None):
    """Rate limit search requests."""
    return rate_limit("search", key_func, "Search rate limit exceeded")


def rate_limit_file_upload(key_func: Optional[Callable] = None):
    """Rate limit file upload requests."""
    return rate_limit("file_upload", key_func, "File upload rate limit exceeded")


def rate_limit_auth(key_func: Optional[Callable] = None):
    """Rate limit authentication requests."""
    return rate_limit("auth", key_func, "Authentication rate limit exceeded")


def rate_limit_password_reset(key_func: Optional[Callable] = None):
    """Rate limit password reset requests."""
    return rate_limit("password_reset", key_func, "Password reset rate limit exceeded")


def rate_limit_email_verification(key_func: Optional[Callable] = None):
    """Rate limit email verification requests."""
    return rate_limit("email_verification", key_func, "Email verification rate limit exceeded")


# Initialize default rate limiters
setup_default_rate_limiters()




