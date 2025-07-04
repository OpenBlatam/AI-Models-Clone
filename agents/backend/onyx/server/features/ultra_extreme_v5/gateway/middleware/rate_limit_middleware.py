"""
🚀 ULTRA-EXTREME V5 - RATE LIMITING MIDDLEWARE
==============================================

Ultra-extreme rate limiting middleware with:
- Sliding window rate limiting
- Burst handling
- Per-user and per-IP rate limiting
- Adaptive rate limiting
- Rate limit headers
- Redis-based distributed rate limiting
"""

import time
import asyncio
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import structlog
import redis.asyncio as redis

from ..config.settings import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Ultra-extreme rate limiting middleware"""
    
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.settings = get_settings()
        self.logger = structlog.get_logger(__name__)
        self.redis_client = redis_client
        
        # Rate limiting configuration
        self.requests_per_window = self.settings.RATE_LIMIT_REQUESTS
        self.window_size = self.settings.RATE_LIMIT_WINDOW
        self.burst_limit = self.settings.RATE_LIMIT_BURST
        
        # In-memory rate limit cache (fallback)
        self.rate_limit_cache = defaultdict(lambda: {
            "requests": deque(),
            "burst_requests": deque(),
            "last_reset": time.time()
        })
        
        # Rate limit strategies
        self.strategies = {
            "sliding_window": self._sliding_window_strategy,
            "fixed_window": self._fixed_window_strategy,
            "token_bucket": self._token_bucket_strategy,
            "leaky_bucket": self._leaky_bucket_strategy
        }
        
        # Current strategy
        self.current_strategy = "sliding_window"
        
        # Adaptive rate limiting
        self.adaptive_enabled = True
        self.system_load_threshold = 0.8
        self.current_system_load = 0.0
    
    async def dispatch(self, request: Request, call_next):
        """Process the request through rate limiting middleware"""
        start_time = time.time()
        
        try:
            # Skip rate limiting for certain paths
            if self._should_skip_rate_limit(request.url.path):
                return await call_next(request)
            
            # Get client identifier
            client_id = await self._get_client_identifier(request)
            
            # Check rate limit
            rate_limit_info = await self._check_rate_limit(client_id, request)
            
            # Add rate limit headers
            response = await call_next(request)
            self._add_rate_limit_headers(response, rate_limit_info)
            
            # Update rate limit tracking
            await self._update_rate_limit_tracking(client_id, rate_limit_info)
            
            # Adaptive rate limiting
            if self.adaptive_enabled:
                await self._update_adaptive_limits(response, start_time)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error("Rate limiting error", error=str(e), exc_info=True)
            # Continue without rate limiting on error
            return await call_next(request)
    
    def _should_skip_rate_limit(self, path: str) -> bool:
        """Check if rate limiting should be skipped for this path"""
        skip_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    async def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from request state (if authenticated)
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user.get('user_id', 'anonymous')}"
        
        # Try API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key[:8]}"
        
        # Use IP address as fallback
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    async def _check_rate_limit(self, client_id: str, request: Request) -> Dict[str, Any]:
        """Check rate limit for client"""
        current_time = time.time()
        
        try:
            # Try Redis-based rate limiting first
            rate_limit_info = await self._check_redis_rate_limit(client_id, current_time)
        except Exception as e:
            self.logger.warning("Redis rate limiting failed, falling back to memory", error=str(e))
            # Fallback to in-memory rate limiting
            rate_limit_info = await self._check_memory_rate_limit(client_id, current_time)
        
        # Check if rate limit exceeded
        if rate_limit_info["exceeded"]:
            self.logger.warning(
                "Rate limit exceeded",
                client_id=client_id,
                limit=rate_limit_info["limit"],
                remaining=rate_limit_info["remaining"]
            )
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(rate_limit_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_limit_info["remaining"]),
                    "X-RateLimit-Reset": str(int(rate_limit_info["reset_time"])),
                    "Retry-After": str(int(rate_limit_info["retry_after"]))
                }
            )
        
        return rate_limit_info
    
    async def _check_redis_rate_limit(self, client_id: str, current_time: float) -> Dict[str, Any]:
        """Check rate limit using Redis"""
        # Use sliding window with Redis
        window_start = current_time - self.window_size
        key = f"rate_limit:{client_id}"
        
        # Add current request to sorted set
        await self.redis_client.zadd(key, {str(current_time): current_time})
        
        # Remove old requests outside the window
        await self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Count requests in current window
        request_count = await self.redis_client.zcard(key)
        
        # Set expiration for the key
        await self.redis_client.expire(key, self.window_size + 60)
        
        # Calculate rate limit info
        limit = self._get_adaptive_limit()
        remaining = max(0, limit - request_count)
        exceeded = request_count > limit
        reset_time = current_time + self.window_size
        retry_after = max(1, int(reset_time - current_time))
        
        return {
            "limit": limit,
            "remaining": remaining,
            "reset_time": reset_time,
            "retry_after": retry_after,
            "exceeded": exceeded,
            "request_count": request_count,
            "window_start": window_start,
            "window_end": current_time
        }
    
    async def _check_memory_rate_limit(self, client_id: str, current_time: float) -> Dict[str, Any]:
        """Check rate limit using in-memory storage"""
        if client_id not in self.rate_limit_cache:
            self.rate_limit_cache[client_id] = {
                "requests": deque(),
                "burst_requests": deque(),
                "last_reset": current_time
            }
        
        client_data = self.rate_limit_cache[client_id]
        
        # Clean old requests
        window_start = current_time - self.window_size
        while client_data["requests"] and client_data["requests"][0] < window_start:
            client_data["requests"].popleft()
        
        # Check burst limit
        burst_window_start = current_time - 1  # 1 second burst window
        while client_data["burst_requests"] and client_data["burst_requests"][0] < burst_window_start:
            client_data["burst_requests"].popleft()
        
        # Check if burst limit exceeded
        if len(client_data["burst_requests"]) >= self.burst_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Burst rate limit exceeded",
                headers={"Retry-After": "1"}
            )
        
        # Add current request
        client_data["requests"].append(current_time)
        client_data["burst_requests"].append(current_time)
        
        # Calculate rate limit info
        limit = self._get_adaptive_limit()
        remaining = max(0, limit - len(client_data["requests"]))
        exceeded = len(client_data["requests"]) > limit
        reset_time = current_time + self.window_size
        retry_after = max(1, int(reset_time - current_time))
        
        return {
            "limit": limit,
            "remaining": remaining,
            "reset_time": reset_time,
            "retry_after": retry_after,
            "exceeded": exceeded,
            "request_count": len(client_data["requests"]),
            "window_start": window_start,
            "window_end": current_time
        }
    
    def _get_adaptive_limit(self) -> int:
        """Get adaptive rate limit based on system load"""
        if not self.adaptive_enabled:
            return self.requests_per_window
        
        # Reduce limit if system load is high
        if self.current_system_load > self.system_load_threshold:
            reduction_factor = 1 - (self.current_system_load - self.system_load_threshold)
            return max(1, int(self.requests_per_window * reduction_factor))
        
        return self.requests_per_window
    
    def _add_rate_limit_headers(self, response: Response, rate_limit_info: Dict[str, Any]):
        """Add rate limit headers to response"""
        response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(int(rate_limit_info["reset_time"]))
        response.headers["X-RateLimit-Strategy"] = self.current_strategy
    
    async def _update_rate_limit_tracking(self, client_id: str, rate_limit_info: Dict[str, Any]):
        """Update rate limit tracking"""
        # Log rate limit usage
        self.logger.debug(
            "Rate limit usage",
            client_id=client_id,
            limit=rate_limit_info["limit"],
            remaining=rate_limit_info["remaining"],
            request_count=rate_limit_info["request_count"]
        )
    
    async def _update_adaptive_limits(self, response: Response, start_time: float):
        """Update adaptive rate limiting based on response"""
        # Calculate response time
        response_time = time.time() - start_time
        
        # Update system load based on response time
        if response_time > 1.0:  # Slow response
            self.current_system_load = min(1.0, self.current_system_load + 0.1)
        elif response_time < 0.1:  # Fast response
            self.current_system_load = max(0.0, self.current_system_load - 0.05)
        
        # Gradually reduce load over time
        self.current_system_load = max(0.0, self.current_system_load - 0.01)
    
    async def _sliding_window_strategy(self, client_id: str, current_time: float) -> Dict[str, Any]:
        """Sliding window rate limiting strategy"""
        # This is implemented in _check_redis_rate_limit
        pass
    
    async def _fixed_window_strategy(self, client_id: str, current_time: float) -> Dict[str, Any]:
        """Fixed window rate limiting strategy"""
        # Implementation for fixed window
        pass
    
    async def _token_bucket_strategy(self, client_id: str, current_time: float) -> Dict[str, Any]:
        """Token bucket rate limiting strategy"""
        # Implementation for token bucket
        pass
    
    async def _leaky_bucket_strategy(self, client_id: str, current_time: float) -> Dict[str, Any]:
        """Leaky bucket rate limiting strategy"""
        # Implementation for leaky bucket
        pass
    
    def set_strategy(self, strategy: str):
        """Set rate limiting strategy"""
        if strategy in self.strategies:
            self.current_strategy = strategy
            self.logger.info("Rate limiting strategy changed", strategy=strategy)
        else:
            self.logger.warning("Invalid rate limiting strategy", strategy=strategy)
    
    def enable_adaptive_limiting(self, enabled: bool = True):
        """Enable or disable adaptive rate limiting"""
        self.adaptive_enabled = enabled
        self.logger.info("Adaptive rate limiting", enabled=enabled)
    
    def set_system_load_threshold(self, threshold: float):
        """Set system load threshold for adaptive limiting"""
        self.system_load_threshold = max(0.0, min(1.0, threshold))
        self.logger.info("System load threshold set", threshold=self.system_load_threshold)
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        return {
            "strategy": self.current_strategy,
            "adaptive_enabled": self.adaptive_enabled,
            "system_load": self.current_system_load,
            "system_load_threshold": self.system_load_threshold,
            "cache_size": len(self.rate_limit_cache),
            "requests_per_window": self.requests_per_window,
            "window_size": self.window_size,
            "burst_limit": self.burst_limit
        }
    
    def clear_rate_limit_cache(self):
        """Clear in-memory rate limit cache"""
        self.rate_limit_cache.clear()
        self.logger.info("Rate limit cache cleared") 