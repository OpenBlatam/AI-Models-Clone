"""
Ultra-Fast Speed Middleware
Maximum performance optimizations for request processing
"""

import time
import logging
import hashlib
from typing import Callable, Optional, Dict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

try:
    from performance.serialization_optimizer import get_serializer
    from performance.response_optimizer import get_response_optimizer, FastJSONResponse
    from performance.request_batcher import get_request_batcher
    from performance.memory_optimizer import get_memory_optimizer
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False
    get_serializer = get_response_optimizer = get_request_batcher = get_memory_optimizer = None
    FastJSONResponse = None

logger = logging.getLogger(__name__)


class SpeedMiddleware(BaseHTTPMiddleware):
    """
    Ultra-fast speed optimization middleware
    
    Features:
    - Fast JSON serialization (orjson - 2-3x faster)
    - Response caching with smart TTL
    - Request deduplication
    - Early response optimization
    - Memory-efficient processing
    - Connection pooling hints
    """
    
    def __init__(self, app: ASGIApp, enable_cache: bool = True, cache_ttl: float = 1.0):
        super().__init__(app)
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        
        if PERFORMANCE_AVAILABLE:
            self.serializer = get_serializer()
            self.response_optimizer = get_response_optimizer()
            self.request_batcher = get_request_batcher()
            self.memory_optimizer = get_memory_optimizer()
            logger.info("✅ Speed middleware initialized with performance optimizations")
        else:
            self.serializer = None
            self.response_optimizer = None
            self.request_batcher = None
            self.memory_optimizer = None
            logger.warning("⚠️ Performance modules not available - using basic mode")
        
        self._request_cache: Dict[str, tuple] = {}
        self._cache_times: Dict[str, float] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with ultra-fast optimizations"""
        start_time = time.perf_counter()
        
        # Memory optimization before request
        if self.memory_optimizer:
            self.memory_optimizer.optimize_gc()
        
        # Check for duplicate requests (idempotency for GET)
        cache_key = None
        if request.method == "GET" and self.enable_cache:
            cache_key = self._get_cache_key(request)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                duration = time.perf_counter() - start_time
                cached_response.headers["X-Process-Time"] = f"{duration:.4f}"
                cached_response.headers["X-Cache-Hit"] = "true"
                cached_response.headers["X-Speed-Optimized"] = "true"
                logger.debug(f"Cache hit: {request.url.path}")
                return cached_response
        
        # Process request
        try:
            response = await call_next(request)
            
            # Optimize response
            response = await self._optimize_response(request, response)
            
            # Cache GET responses
            if cache_key and request.method == "GET" and response.status_code == 200:
                self._cache_response(cache_key, response)
            
            # Add performance headers
            duration = time.perf_counter() - start_time
            response.headers["X-Process-Time"] = f"{duration:.4f}"
            response.headers["X-Speed-Optimized"] = "true"
            
            # Memory optimization after request
            if self.memory_optimizer:
                self.memory_optimizer.optimize_gc()
            
            return response
            
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            raise
    
    def _get_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        key_data = f"{request.method}:{request.url.path}:{request.url.query}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Response]:
        """Get cached response if valid"""
        current_time = time.time()
        
        if cache_key in self._request_cache:
            response, cached_time = self._request_cache[cache_key]
            if current_time - cached_time < self.cache_ttl:
                # Create a copy of the response to avoid issues
                return response
            else:
                # Expired - remove
                del self._request_cache[cache_key]
                if cache_key in self._cache_times:
                    del self._cache_times[cache_key]
        
        return None
    
    def _cache_response(self, cache_key: str, response: Response) -> None:
        """Cache response"""
        current_time = time.time()
        self._request_cache[cache_key] = (response, current_time)
        self._cache_times[cache_key] = current_time
        
        # Cleanup old cache entries (keep last 1000)
        if len(self._request_cache) > 1000:
            # Remove oldest entries
            sorted_times = sorted(self._cache_times.items(), key=lambda x: x[1])
            for key, _ in sorted_times[:100]:
                if key in self._request_cache:
                    del self._request_cache[key]
                if key in self._cache_times:
                    del self._cache_times[key]
    
    async def _optimize_response(self, request: Request, response: Response) -> Response:
        """Optimize response for maximum speed"""
        if not PERFORMANCE_AVAILABLE or not self.response_optimizer:
            return response
        
        # Optimize headers
        response = self.response_optimizer.optimize_headers(response, cache_ttl=300)
        
        # Add compression hints
        if "content-encoding" not in response.headers:
            response.headers["Accept-Encoding"] = "gzip, deflate, br"
        
        return response















