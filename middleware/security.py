from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import asyncio
import hashlib
import hmac
import json
import time
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import jwt
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
import structlog
from .core import (
    import re
from typing import Any, List, Dict, Optional
import logging
"""
Security middleware for authentication, authorization, rate limiting, and security headers.
Uses functional programming patterns and RORO pattern.
"""



    LogContext, create_log_context, log_operation, LogLevel,
    MetricContext, create_metric_context, record_metric, MetricType,
    ExceptionContext, create_exception_context, handle_exception,
    with_logging, with_metrics, with_exception_handling
)


@dataclass
class SecurityContext:
    """Context for security operations."""
    user_id: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    permissions: Set[str] = field(default_factory=set)
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_timestamp: float = field(default_factory=time.time)


@dataclass
class RateLimitContext:
    """Context for rate limiting."""
    key: str
    limit: int
    window: int
    current_count: int = 0
    reset_time: float = 0.0


class RateLimiter:
    """In-memory rate limiter with sliding window."""
    
    def __init__(self) -> Any:
        self.requests: Dict[str, List[float]] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
    
    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int
    ) -> bool:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Rate limit key (e.g., IP address, user ID)
            limit: Maximum requests allowed
            window: Time window in seconds
        
        Returns:
            True if request is allowed, False otherwise
        """
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()
        
        async with self.locks[key]:
            current_time = time.time()
            
            if key not in self.requests:
                self.requests[key] = []
            
            # Remove expired timestamps
            self.requests[key] = [
                ts for ts in self.requests[key]
                if current_time - ts < window
            ]
            
            # Check if limit exceeded
            if len(self.requests[key]) >= limit:
                return False
            
            # Add current request
            self.requests[key].append(current_time)
            return True
    
    async def get_remaining_requests(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests for a key."""
        current_time = time.time()
        
        if key not in self.requests:
            return limit
        
        valid_requests = [
            ts for ts in self.requests[key]
            if current_time - ts < window
        ]
        
        return max(0, limit - len(valid_requests))


# Global rate limiter instance
rate_limiter = RateLimiter()


def create_security_context(
    user_id: Optional[str] = None,
    roles: Optional[List[str]] = None,
    permissions: Optional[Set[str]] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> SecurityContext:
    """
    Create security context.
    
    Args:
        user_id: User identifier
        roles: User roles
        permissions: User permissions
        session_id: Session identifier
        ip_address: Client IP address
        user_agent: User agent string
    
    Returns:
        SecurityContext object
    """
    return SecurityContext(
        user_id=user_id,
        roles=roles or [],
        permissions=permissions or set(),
        session_id=session_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


def validate_jwt_token(
    token: str,
    secret_key: str,
    algorithms: List[str] = None
) -> Dict[str, Any]:
    """
    Validate JWT token.
    
    Args:
        token: JWT token string
        secret_key: Secret key for validation
        algorithms: Allowed algorithms
    
    Returns:
        Decoded token payload
    
    Raises:
        jwt.InvalidTokenError: If token is invalid
    """
    if algorithms is None:
        algorithms = ["HS256"]
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.InvalidTokenError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")


def hash_password(password: str, salt: Optional[str] = None) -> Dict[str, str]:
    """
    Hash password with salt.
    
    Args:
        password: Plain text password
        salt: Salt string (generated if not provided)
    
    Returns:
        Dictionary with hash and salt
    """
    if salt is None:
        salt = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
    
    # Use PBKDF2 for password hashing
    hash_obj = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # iterations
    )
    
    return {
        "hash": hash_obj.hex(),
        "salt": salt
    }


def verify_password(password: str, hash_value: str, salt: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        password: Plain text password
        hash_value: Stored hash
        salt: Stored salt
    
    Returns:
        True if password matches, False otherwise
    """
    computed_hash = hash_password(password, salt)
    return hmac.compare_digest(computed_hash["hash"], hash_value)


def check_permission(
    required_permission: str,
    user_permissions: Set[str]
) -> bool:
    """
    Check if user has required permission.
    
    Args:
        required_permission: Required permission
        user_permissions: User's permissions
    
    Returns:
        True if user has permission, False otherwise
    """
    return required_permission in user_permissions


def check_role(
    required_roles: List[str],
    user_roles: List[str]
) -> bool:
    """
    Check if user has required role.
    
    Args:
        required_roles: Required roles
        user_roles: User's roles
    
    Returns:
        True if user has required role, False otherwise
    """
    return any(role in user_roles for role in required_roles)


# =============================================================================
# SECURITY DECORATORS
# =============================================================================

def require_authentication():
    """Decorator to require authentication."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            request = kwargs.get("request")
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication header"
                )
            
            token = auth_header.split(" ")[1]
            try:
                # This would typically use a secret from configuration
                payload = validate_jwt_token(token, "your-secret-key")
                kwargs["user_id"] = payload.get("user_id")
                kwargs["user_roles"] = payload.get("roles", [])
                return await func(*args, **kwargs)
            except jwt.InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            request = kwargs.get("request")
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication header"
                )
            
            token = auth_header.split(" ")[1]
            try:
                payload = validate_jwt_token(token, "your-secret-key")
                kwargs["user_id"] = payload.get("user_id")
                kwargs["user_roles"] = payload.get("roles", [])
                return func(*args, **kwargs)
            except jwt.InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def require_permission(permission: str):
    """Decorator to require specific permission."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            user_permissions = kwargs.get("user_permissions", set())
            if not check_permission(permission, user_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            user_permissions = kwargs.get("user_permissions", set())
            if not check_permission(permission, user_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def require_role(roles: List[str]):
    """Decorator to require specific role."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            user_roles = kwargs.get("user_roles", [])
            if not check_role(roles, user_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"One of roles {roles} required"
                )
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            user_roles = kwargs.get("user_roles", [])
            if not check_role(roles, user_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"One of roles {roles} required"
                )
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def rate_limit(
    limit: int,
    window: int,
    key_func: Optional[Callable] = None
):
    """
    Decorator for rate limiting.
    
    Args:
        limit: Maximum requests allowed
        window: Time window in seconds
        key_func: Function to generate rate limit key
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            request = kwargs.get("request")
            if not request:
                return await func(*args, **kwargs)
            
            # Generate rate limit key
            if key_func:
                rate_limit_key = key_func(request)
            else:
                rate_limit_key = request.client.host if request.client else "unknown"
            
            # Check rate limit
            is_allowed = await rate_limiter.is_allowed(rate_limit_key, limit, window)
            if not is_allowed:
                remaining = rate_limiter.get_remaining_requests(rate_limit_key, limit, window)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again later.",
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": str(remaining),
                        "X-RateLimit-Reset": str(int(time.time() + window))
                    }
                )
            
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            request = kwargs.get("request")
            if not request:
                return func(*args, **kwargs)
            
            # Generate rate limit key
            if key_func:
                rate_limit_key = key_func(request)
            else:
                rate_limit_key = request.client.host if request.client else "unknown"
            
            # Check rate limit (synchronous version)
            current_time = time.time()
            if rate_limit_key not in rate_limiter.requests:
                rate_limiter.requests[rate_limit_key] = []
            
            # Remove expired timestamps
            rate_limiter.requests[rate_limit_key] = [
                ts for ts in rate_limiter.requests[rate_limit_key]
                if current_time - ts < window
            ]
            
            if len(rate_limiter.requests[rate_limit_key]) >= limit:
                remaining = max(0, limit - len(rate_limiter.requests[rate_limit_key]))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again later.",
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": str(remaining),
                        "X-RateLimit-Reset": str(int(current_time + window))
                    }
                )
            
            rate_limiter.requests[rate_limit_key].append(current_time)
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# =============================================================================
# SECURITY MIDDLEWARE
# =============================================================================

async def security_headers_middleware(request: Request, call_next):
    """Middleware to add security headers."""
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response


async def authentication_middleware(request: Request, call_next):
    """Middleware for authentication."""
    logger = structlog.get_logger()
    
    # Extract authentication information
    auth_header = request.headers.get("Authorization")
    user_id = None
    user_roles = []
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = validate_jwt_token(token, "your-secret-key")
            user_id = payload.get("user_id")
            user_roles = payload.get("roles", [])
            
            # Log successful authentication
            context = create_log_context(
                request_id=request.headers.get("X-Request-ID", "unknown"),
                user_id=user_id,
                operation="authentication",
                component="security"
            )
            log_operation(logger, context, "User authenticated successfully")
            
        except jwt.InvalidTokenError:
            # Log failed authentication
            context = create_log_context(
                request_id=request.headers.get("X-Request-ID", "unknown"),
                operation="authentication",
                component="security"
            )
            log_operation(logger, context, "Authentication failed", level=LogLevel.WARNING)
    
    # Add user information to request state
    request.state.user_id = user_id
    request.state.user_roles = user_roles
    
    response = await call_next(request)
    return response


async def authorization_middleware(request: Request, call_next):
    """Middleware for authorization."""
    logger = structlog.get_logger()
    
    # Check if endpoint requires authentication
    if hasattr(request.state, "requires_auth") and request.state.requires_auth:
        if not request.state.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
    
    # Check if endpoint requires specific roles
    if hasattr(request.state, "required_roles") and request.state.required_roles:
        user_roles = getattr(request.state, "user_roles", [])
        if not check_role(request.state.required_roles, user_roles):
            context = create_log_context(
                request_id=request.headers.get("X-Request-ID", "unknown"),
                user_id=getattr(request.state, "user_id"),
                operation="authorization",
                component="security"
            )
            log_operation(logger, context, "Access denied - insufficient roles", level=LogLevel.WARNING)
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    response = await call_next(request)
    return response


async def rate_limiting_middleware(request: Request, call_next):
    """Middleware for rate limiting."""
    logger = structlog.get_logger()
    
    # Generate rate limit key (IP-based by default)
    rate_limit_key = request.client.host if request.client else "unknown"
    
    # Apply rate limiting (100 requests per minute by default)
    is_allowed = await rate_limiter.is_allowed(rate_limit_key, 100, 60)
    
    if not is_allowed:
        context = create_log_context(
            request_id=request.headers.get("X-Request-ID", "unknown"),
            operation="rate_limiting",
            component="security",
            ip_address=rate_limit_key
        )
        log_operation(logger, context, "Rate limit exceeded", level=LogLevel.WARNING)
        
        remaining = rate_limiter.get_remaining_requests(rate_limit_key, 100, 60)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(time.time() + 60))
            }
        )
    
    response = await call_next(request)
    
    # Add rate limit headers to response
    remaining = rate_limiter.get_remaining_requests(rate_limit_key, 100, 60)
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
    
    return response


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def setup_security_middleware(app) -> None:
    """Setup security middleware stack."""
    app.middleware("http")(security_headers_middleware)
    app.middleware("http")(rate_limiting_middleware)
    app.middleware("http")(authentication_middleware)
    app.middleware("http")(authorization_middleware)


def generate_jwt_token(
    payload: Dict[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expires_in: int = 3600
) -> str:
    """
    Generate JWT token.
    
    Args:
        payload: Token payload
        secret_key: Secret key
        algorithm: JWT algorithm
        expires_in: Token expiration time in seconds
    
    Returns:
        JWT token string
    """
    payload["exp"] = datetime.utcnow() + timedelta(seconds=expires_in)
    payload["iat"] = datetime.utcnow()
    
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def sanitize_input(input_string: str) -> str:
    """
    Sanitize user input.
    
    Args:
        input_string: Input string to sanitize
    
    Returns:
        Sanitized string
    """
    # Basic XSS prevention
    dangerous_chars = {
        "<": "&lt;",
        ">": "&gt;",
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;"
    }
    
    sanitized = input_string
    for char, replacement in dangerous_chars.items():
        sanitized = sanitized.replace(char, replacement)
    
    return sanitized


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if email is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
    
    Returns:
        Dictionary with validation results
    """
    errors = []
    warnings = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        warnings.append("Password should contain at least one special character")
    
    if len(password) < 12:
        warnings.append("Consider using a longer password for better security")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "score": max(0, 10 - len(errors) * 2 - len(warnings))
    } 