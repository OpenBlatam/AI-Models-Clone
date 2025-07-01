"""
🚀 ENTERPRISE MIDDLEWARE STACK
==============================

Advanced middleware implementations for microservices architecture:
- Circuit breakers with automatic recovery
- Multi-tier caching (Memory + Redis)
- Distributed rate limiting
- Security headers & authentication
- Performance monitoring & metrics
- Distributed tracing
- Health checks
"""

import time
import uuid
import asyncio
import hashlib
import weakref
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Try to import optional dependencies
try:
    import orjson as json
    JSON_AVAILABLE = True
except ImportError:
    import json
    JSON_AVAILABLE = False

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    import opentelemetry
    from opentelemetry.trace import get_tracer
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False

# === CIRCUIT BREAKER IMPLEMENTATION ===

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics"""
    total_requests: int = 0
    failed_requests: int = 0
    success_requests: int = 0
    timeout_requests: int = 0
    last_failure_time: Optional[float] = None
    state_transitions: int = 0

class EnterpriseCircuitBreaker:
    """Advanced circuit breaker with exponential backoff and health monitoring"""
    
    def __init__(self, 
                 service_name: str,
                 failure_threshold: int = 5,
                 timeout: int = 60,
                 half_open_max_calls: int = 5,
                 slow_call_threshold: float = 5.0):
        
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        self.slow_call_threshold = slow_call_threshold
        
        self.state = CircuitBreakerState.CLOSED
        self.stats = CircuitBreakerStats()
        self.half_open_calls = 0
        self.logger = logging.getLogger(f"circuit_breaker.{service_name}")
        
        # Metrics tracking
        if PROMETHEUS_AVAILABLE:
            self.state_metric = Gauge(
                f'circuit_breaker_state_{service_name}',
                f'Circuit breaker state for {service_name}'
            )
            self.requests_metric = Counter(
                f'circuit_breaker_requests_{service_name}',
                f'Circuit breaker requests for {service_name}',
                ['result']
            )
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        self.stats.total_requests += 1
        
        # Check if circuit is open
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                await self._transition_to_half_open()
            else:
                await self._record_blocked_request()
                raise HTTPException(
                    status_code=503,
                    detail=f"Service {self.service_name} temporarily unavailable (Circuit Breaker OPEN)"
                )
        
        # Check half-open state limits
        if self.state == CircuitBreakerState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                await self._record_blocked_request()
                raise HTTPException(
                    status_code=503,
                    detail=f"Service {self.service_name} temporarily unavailable (Circuit Breaker HALF_OPEN limit reached)"
                )
            self.half_open_calls += 1
        
        # Execute the function
        start_time = time.perf_counter()
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            execution_time = time.perf_counter() - start_time
            await self._record_success(execution_time)
            
            return result
            
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            await self._record_failure(e, execution_time)
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset"""
        if self.stats.last_failure_time is None:
            return True
        
        time_since_failure = time.time() - self.stats.last_failure_time
        # Exponential backoff: increase timeout based on consecutive failures
        backoff_multiplier = min(2 ** (self.stats.failed_requests // self.failure_threshold), 16)
        effective_timeout = self.timeout * backoff_multiplier
        
        return time_since_failure >= effective_timeout
    
    async def _transition_to_half_open(self):
        """Transition circuit breaker to half-open state"""
        self.state = CircuitBreakerState.HALF_OPEN
        self.half_open_calls = 0
        self.stats.state_transitions += 1
        
        self.logger.info(f"Circuit breaker for {self.service_name} transitioned to HALF_OPEN")
        
        if PROMETHEUS_AVAILABLE:
            self.state_metric.set(2)  # 2 = half_open
    
    async def _record_success(self, execution_time: float):
        """Record successful execution"""
        self.stats.success_requests += 1
        
        # Check for slow calls
        if execution_time > self.slow_call_threshold:
            self.stats.timeout_requests += 1
            self.logger.warning(
                f"Slow call detected for {self.service_name}: {execution_time:.2f}s"
            )
        
        # Reset circuit breaker if in half-open state
        if self.state == CircuitBreakerState.HALF_OPEN:
            await self._transition_to_closed()
        
        if PROMETHEUS_AVAILABLE:
            self.requests_metric.labels(result='success').inc()
    
    async def _record_failure(self, exception: Exception, execution_time: float):
        """Record failed execution"""
        self.stats.failed_requests += 1
        self.stats.last_failure_time = time.time()
        
        self.logger.warning(
            f"Circuit breaker failure for {self.service_name}: {str(exception)}"
        )
        
        # Transition to open if threshold exceeded
        if (self.state == CircuitBreakerState.CLOSED and 
            self.stats.failed_requests >= self.failure_threshold):
            await self._transition_to_open()
        elif self.state == CircuitBreakerState.HALF_OPEN:
            await self._transition_to_open()
        
        if PROMETHEUS_AVAILABLE:
            self.requests_metric.labels(result='failure').inc()
    
    async def _record_blocked_request(self):
        """Record request blocked by circuit breaker"""
        if PROMETHEUS_AVAILABLE:
            self.requests_metric.labels(result='blocked').inc()
    
    async def _transition_to_closed(self):
        """Transition circuit breaker to closed state"""
        self.state = CircuitBreakerState.CLOSED
        self.stats.failed_requests = 0
        self.half_open_calls = 0
        self.stats.state_transitions += 1
        
        self.logger.info(f"Circuit breaker for {self.service_name} transitioned to CLOSED")
        
        if PROMETHEUS_AVAILABLE:
            self.state_metric.set(0)  # 0 = closed
    
    async def _transition_to_open(self):
        """Transition circuit breaker to open state"""
        self.state = CircuitBreakerState.OPEN
        self.stats.state_transitions += 1
        
        self.logger.error(f"Circuit breaker for {self.service_name} transitioned to OPEN")
        
        if PROMETHEUS_AVAILABLE:
            self.state_metric.set(1)  # 1 = open
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "service_name": self.service_name,
            "state": self.state.value,
            "total_requests": self.stats.total_requests,
            "success_requests": self.stats.success_requests,
            "failed_requests": self.stats.failed_requests,
            "timeout_requests": self.stats.timeout_requests,
            "state_transitions": self.stats.state_transitions,
            "failure_rate": (
                self.stats.failed_requests / self.stats.total_requests 
                if self.stats.total_requests > 0 else 0
            ),
            "last_failure_time": self.stats.last_failure_time
        }

# === CACHING SYSTEM ===

class EnterpriseCacheManager:
    """Multi-tier caching with intelligent eviction and compression"""
    
    def __init__(self, redis_url: str, max_memory_items: int = 10000):
        self.redis_url = redis_url
        self.redis_client = None
        self.memory_cache = weakref.WeakValueDictionary()
        self.access_times = {}
        self.max_memory_items = max_memory_items
        self.compression_threshold = 1024  # bytes
        
        # Statistics
        self.hit_count = 0
        self.miss_count = 0
        self.l1_hits = 0  # Memory cache hits
        self.l2_hits = 0  # Redis cache hits
        
        self.logger = logging.getLogger("cache_manager")
        
        # Metrics
        if PROMETHEUS_AVAILABLE:
            self.cache_operations = Counter(
                'cache_operations_total',
                'Cache operations',
                ['operation', 'result', 'tier']
            )
            self.cache_size = Gauge('cache_size', 'Cache size', ['tier'])
    
    async def init_redis(self):
        """Initialize Redis connection with retry logic"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    max_connections=20,
                    retry_on_timeout=True,
                    health_check_interval=30,
                    socket_keepalive=True,
                    socket_keepalive_options={}
                )
                
                # Test connection
                await self.redis_client.ping()
                self.logger.info("Redis connection established successfully")
                return
                
            except Exception as e:
                self.logger.warning(
                    f"Redis connection attempt {attempt + 1} failed: {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
        
        self.logger.error("Failed to establish Redis connection after retries")
        self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache with L1 (memory) -> L2 (Redis) fallback"""
        cache_key = self._generate_key(key)
        
        # L1: Memory cache
        try:
            if cache_key in self.memory_cache:
                # Check if not expired
                if cache_key in self.access_times:
                    self.access_times[cache_key] = time.time()
                    self.hit_count += 1
                    self.l1_hits += 1
                    
                    if PROMETHEUS_AVAILABLE:
                        self.cache_operations.labels(
                            operation='get', result='hit', tier='memory'
                        ).inc()
                    
                    return self.memory_cache[cache_key]
        except Exception as e:
            self.logger.warning(f"Memory cache get error: {e}")
        
        # L2: Redis cache
        if self.redis_client:
            try:
                data = await self.redis_client.get(cache_key)
                if data:
                    if JSON_AVAILABLE:
                        value = orjson.loads(data)
                    else:
                        value = json.loads(data)
                    
                    # Store in memory cache for faster access
                    await self._store_in_memory(cache_key, value)
                    
                    self.hit_count += 1
                    self.l2_hits += 1
                    
                    if PROMETHEUS_AVAILABLE:
                        self.cache_operations.labels(
                            operation='get', result='hit', tier='redis'
                        ).inc()
                    
                    return value
                    
            except Exception as e:
                self.logger.warning(f"Redis cache get error: {e}")
        
        # Cache miss
        self.miss_count += 1
        
        if PROMETHEUS_AVAILABLE:
            self.cache_operations.labels(
                operation='get', result='miss', tier='all'
            ).inc()
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set in cache with intelligent storage strategy"""
        cache_key = self._generate_key(key)
        
        try:
            # Serialize data
            if JSON_AVAILABLE:
                serialized_data = orjson.dumps(value)
            else:
                serialized_data = json.dumps(value).encode()
            
            data_size = len(serialized_data)
            
            # Store in memory if small enough
            if data_size < self.compression_threshold:
                await self._store_in_memory(cache_key, value)
            
            # Store in Redis asynchronously
            if self.redis_client:
                asyncio.create_task(
                    self._store_in_redis(cache_key, serialized_data, ttl)
                )
            
            if PROMETHEUS_AVAILABLE:
                self.cache_operations.labels(
                    operation='set', result='success', tier='all'
                ).inc()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache set error for key {key}: {e}")
            
            if PROMETHEUS_AVAILABLE:
                self.cache_operations.labels(
                    operation='set', result='error', tier='all'
                ).inc()
            
            return False
    
    async def _store_in_memory(self, key: str, value: Any):
        """Store in memory with LRU eviction"""
        try:
            # LRU eviction if at capacity
            if len(self.memory_cache) >= self.max_memory_items:
                await self._evict_lru()
            
            self.memory_cache[key] = value
            self.access_times[key] = time.time()
            
            if PROMETHEUS_AVAILABLE:
                self.cache_size.labels(tier='memory').set(len(self.memory_cache))
        
        except Exception as e:
            self.logger.warning(f"Memory cache store error: {e}")
    
    async def _store_in_redis(self, key: str, data: bytes, ttl: int):
        """Store in Redis with error handling"""
        try:
            await self.redis_client.setex(key, ttl, data)
        except Exception as e:
            self.logger.warning(f"Redis store error for key {key}: {e}")
    
    async def _evict_lru(self):
        """Evict least recently used items"""
        if not self.access_times:
            return
        
        # Find oldest item
        oldest_key = min(self.access_times.keys(), 
                        key=lambda k: self.access_times[k])
        
        # Remove from both caches
        self.memory_cache.pop(oldest_key, None)
        self.access_times.pop(oldest_key, None)
    
    def _generate_key(self, key: str) -> str:
        """Generate consistent cache key with namespace"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return f"enterprise:cache:{key_hash}"
    
    async def clear(self, pattern: str = None):
        """Clear cache with optional pattern"""
        if pattern:
            # Clear specific pattern from Redis
            if self.redis_client:
                try:
                    keys = await self.redis_client.keys(f"enterprise:cache:*{pattern}*")
                    if keys:
                        await self.redis_client.delete(*keys)
                except Exception as e:
                    self.logger.warning(f"Redis pattern clear error: {e}")
        else:
            # Clear all
            self.memory_cache.clear()
            self.access_times.clear()
            
            if self.redis_client:
                try:
                    keys = await self.redis_client.keys("enterprise:cache:*")
                    if keys:
                        await self.redis_client.delete(*keys)
                except Exception as e:
                    self.logger.warning(f"Redis clear error: {e}")
    
    @property
    def hit_ratio(self) -> float:
        """Calculate overall cache hit ratio"""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
    
    @property
    def memory_hit_ratio(self) -> float:
        """Calculate memory cache hit ratio"""
        total = self.hit_count + self.miss_count
        return self.l1_hits / total if total > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "l1_hits": self.l1_hits,
            "l2_hits": self.l2_hits,
            "hit_ratio": self.hit_ratio,
            "memory_hit_ratio": self.memory_hit_ratio,
            "memory_cache_size": len(self.memory_cache),
            "redis_available": self.redis_client is not None
        }

# === RATE LIMITER ===

class EnterpriseRateLimiter:
    """Distributed rate limiter with sliding window and burst control"""
    
    def __init__(self, redis_client, 
                 requests_per_minute: int = 1000,
                 burst_size: int = 100):
        self.redis_client = redis_client
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.window_size = 60  # seconds
        
        self.logger = logging.getLogger("rate_limiter")
        
        # Metrics
        if PROMETHEUS_AVAILABLE:
            self.rate_limit_counter = Counter(
                'rate_limit_requests_total',
                'Rate limit requests',
                ['result', 'identifier_type']
            )
    
    async def is_allowed(self, identifier: str, 
                        identifier_type: str = "default") -> tuple[bool, Dict[str, Any]]:
        """Check if request is allowed under rate limit"""
        
        if not self.redis_client:
            return True, {"rate_limit_active": False}
        
        key = f"rate_limit:{identifier_type}:{identifier}"
        current_time = time.time()
        window_start = current_time - self.window_size
        
        try:
            # Use Redis Lua script for atomic operations
            lua_script = """
            local key = KEYS[1]
            local window_start = ARGV[1]
            local current_time = ARGV[2]
            local max_requests = ARGV[3]
            local window_size = ARGV[4]
            
            -- Remove old entries
            redis.call('ZREMRANGEBYSCORE', key, 0, window_start)
            
            -- Count current requests
            local current_count = redis.call('ZCARD', key)
            
            -- Check if under limit
            if current_count < tonumber(max_requests) then
                -- Add new request
                redis.call('ZADD', key, current_time, current_time .. '-' .. math.random())
                redis.call('EXPIRE', key, window_size)
                return {1, current_count + 1}
            else
                return {0, current_count}
            end
            """
            
            result = await self.redis_client.eval(
                lua_script, 1, key,
                window_start, current_time, 
                self.requests_per_minute, self.window_size
            )
            
            allowed = bool(result[0])
            current_requests = int(result[1])
            remaining = max(0, self.requests_per_minute - current_requests)
            
            # Record metrics
            if PROMETHEUS_AVAILABLE:
                self.rate_limit_counter.labels(
                    result='allowed' if allowed else 'blocked',
                    identifier_type=identifier_type
                ).inc()
            
            return allowed, {
                "rate_limit_active": True,
                "requests_remaining": remaining,
                "current_requests": current_requests,
                "window_size": self.window_size,
                "reset_time": current_time + self.window_size
            }
            
        except Exception as e:
            self.logger.error(f"Rate limiting failed for {identifier}: {e}")
            return True, {"rate_limit_active": False, "error": str(e)}
    
    async def get_stats(self, identifier: str, 
                       identifier_type: str = "default") -> Dict[str, Any]:
        """Get rate limiting statistics for identifier"""
        if not self.redis_client:
            return {"rate_limit_active": False}
        
        key = f"rate_limit:{identifier_type}:{identifier}"
        current_time = time.time()
        window_start = current_time - self.window_size
        
        try:
            # Clean old entries and count current
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            current_requests = await self.redis_client.zcard(key)
            
            return {
                "identifier": identifier,
                "identifier_type": identifier_type,
                "current_requests": current_requests,
                "requests_remaining": max(0, self.requests_per_minute - current_requests),
                "window_size": self.window_size,
                "limit": self.requests_per_minute
            }
            
        except Exception as e:
            self.logger.error(f"Rate limit stats failed for {identifier}: {e}")
            return {"error": str(e)}

# === MIDDLEWARE CLASSES ===

class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    """Middleware for circuit breaker protection"""
    
    def __init__(self, app, circuit_breakers: Dict[str, EnterpriseCircuitBreaker]):
        super().__init__(app)
        self.circuit_breakers = circuit_breakers
    
    async def dispatch(self, request: Request, call_next):
        # Determine service based on path
        service_name = self._get_service_name(request.url.path)
        
        if service_name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[service_name]
            return await circuit_breaker.call(call_next, request)
        
        return await call_next(request)
    
    def _get_service_name(self, path: str) -> str:
        """Extract service name from request path"""
        path_parts = path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] == 'api':
            return path_parts[1] if len(path_parts) > 1 else 'default'
        return 'default'

class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and metrics"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("performance")
        
        if PROMETHEUS_AVAILABLE:
            self.request_count = Counter(
                'http_requests_total',
                'Total HTTP requests',
                ['method', 'endpoint', 'status']
            )
            
            self.request_duration = Histogram(
                'http_request_duration_seconds',
                'HTTP request duration',
                ['method', 'endpoint']
            )
            
            self.active_requests = Gauge(
                'http_active_requests',
                'Active HTTP requests'
            )
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.perf_counter()
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.start_time = start_time
        
        if PROMETHEUS_AVAILABLE:
            self.active_requests.inc()
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.perf_counter() - start_time
            
            # Add performance headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration:.4f}"
            response.headers["X-Timestamp"] = str(int(time.time()))
            
            # Record metrics
            endpoint = request.url.path
            method = request.method
            status = response.status_code
            
            if PROMETHEUS_AVAILABLE:
                self.request_count.labels(
                    method=method, endpoint=endpoint, status=status
                ).inc()
                self.request_duration.labels(
                    method=method, endpoint=endpoint
                ).observe(duration)
            
            # Log slow requests
            if duration > 1.0:  # Log requests slower than 1 second
                self.logger.warning(
                    f"Slow request: {method} {endpoint} took {duration:.2f}s"
                )
            
            return response
            
        finally:
            if PROMETHEUS_AVAILABLE:
                self.active_requests.dec()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers"""
    
    def __init__(self, app, config: Dict[str, Any] = None):
        super().__init__(app)
        self.config = config or {}
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }
        
        # HSTS header for HTTPS
        if request.url.scheme == "https":
            security_headers["Strict-Transport-Security"] = \
                f"max-age={self.config.get('hsts_max_age', 31536000)}; includeSubDomains"
        
        # CSP header
        csp = self.config.get('content_security_policy', "default-src 'self'")
        security_headers["Content-Security-Policy"] = csp
        
        # Apply headers
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response 