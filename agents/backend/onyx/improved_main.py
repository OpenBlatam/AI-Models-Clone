"""
🚀 IMPROVED ENTERPRISE MAIN
==========================

Enhanced version of main.py with advanced microservices patterns:
- Circuit breakers & retries
- Multi-tier caching (Memory + Redis)
- Advanced rate limiting
- Prometheus metrics
- Distributed tracing
- Health checks & monitoring
- Serverless optimization
- Security best practices
"""

import asyncio
import logging
import sys
import time
import uuid
import weakref
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

# FastAPI & core dependencies
from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Import existing onyx components
from onyx import __version__
from onyx.configs.app_configs import (
    APP_API_PREFIX, APP_HOST, APP_PORT, CORS_ALLOWED_ORIGIN
)
from onyx.utils.logger import setup_logger

# Optional advanced dependencies
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    import orjson as json
    JSON_AVAILABLE = True
except ImportError:
    import json
    JSON_AVAILABLE = False

# Setup logger
logger = setup_logger()

# === ENTERPRISE CACHE MANAGER ===

class EnterpriseCache:
    """Multi-tier cache with Redis and memory layers"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.memory_cache = weakref.WeakValueDictionary()
        self.access_times = {}
        self.max_memory_items = 10000
        
        # Metrics
        self.hit_count = 0
        self.miss_count = 0
        self.redis_hits = 0
        self.memory_hits = 0
    
    async def init_redis(self):
        """Initialize Redis connection with retry logic"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available - using memory cache only")
            return
        
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                max_connections=20,
                retry_on_timeout=True,
                health_check_interval=30
            )
            await self.redis_client.ping()
            logger.info("✅ Redis cache initialized")
        except Exception as e:
            logger.error(f"❌ Redis init failed: {e}")
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache with L1 (memory) -> L2 (Redis) fallback"""
        # L1: Memory cache
        if key in self.memory_cache:
            self.access_times[key] = time.time()
            self.hit_count += 1
            self.memory_hits += 1
            return self.memory_cache[key]
        
        # L2: Redis cache
        if self.redis_client:
            try:
                data = await self.redis_client.get(f"enterprise:{key}")
                if data:
                    if JSON_AVAILABLE:
                        value = orjson.loads(data)
                    else:
                        value = json.loads(data)
                    
                    # Store in memory for faster access
                    await self._store_in_memory(key, value)
                    self.hit_count += 1
                    self.redis_hits += 1
                    return value
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        self.miss_count += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set in cache with intelligent storage"""
        try:
            # Store in memory
            await self._store_in_memory(key, value)
            
            # Store in Redis asynchronously
            if self.redis_client:
                asyncio.create_task(self._store_in_redis(key, value, ttl))
            
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def _store_in_memory(self, key: str, value: Any):
        """Store in memory with LRU eviction"""
        if len(self.memory_cache) >= self.max_memory_items:
            # LRU eviction
            if self.access_times:
                oldest_key = min(self.access_times.keys(), 
                               key=lambda k: self.access_times[k])
                self.memory_cache.pop(oldest_key, None)
                self.access_times.pop(oldest_key, None)
        
        self.memory_cache[key] = value
        self.access_times[key] = time.time()
    
    async def _store_in_redis(self, key: str, value: Any, ttl: int):
        """Store in Redis with error handling"""
        try:
            if JSON_AVAILABLE:
                data = orjson.dumps(value)
            else:
                data = json.dumps(value).encode()
            await self.redis_client.setex(f"enterprise:{key}", ttl, data)
        except Exception as e:
            logger.warning(f"Redis store error: {e}")
    
    @property
    def hit_ratio(self) -> float:
        """Calculate cache hit ratio"""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "memory_hits": self.memory_hits,
            "redis_hits": self.redis_hits,
            "hit_ratio": self.hit_ratio,
            "memory_cache_size": len(self.memory_cache),
            "redis_available": self.redis_client is not None
        }

# === CIRCUIT BREAKER ===

class CircuitBreaker:
    """Simple but effective circuit breaker"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise HTTPException(503, "Service temporarily unavailable")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
            self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"Circuit breaker opened after {self.failure_count} failures")
            
            raise

# === RATE LIMITER ===

class RateLimiter:
    """Redis-based distributed rate limiter"""
    
    def __init__(self, redis_client, requests_per_minute: int = 1000):
        self.redis_client = redis_client
        self.requests_per_minute = requests_per_minute
    
    async def is_allowed(self, identifier: str) -> tuple[bool, Dict[str, Any]]:
        """Check if request is allowed"""
        if not self.redis_client:
            return True, {"rate_limit_active": False}
        
        key = f"rate_limit:{identifier}"
        current_time = time.time()
        window_start = current_time - 60  # 1-minute window
        
        try:
            # Remove old entries and count current requests
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcount(key, window_start, current_time)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, 60)
            
            results = await pipe.execute()
            current_count = results[1]
            
            allowed = current_count < self.requests_per_minute
            remaining = max(0, self.requests_per_minute - current_count)
            
            return allowed, {
                "rate_limit_active": True,
                "requests_remaining": remaining,
                "current_requests": current_count
            }
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True, {"rate_limit_active": False, "error": str(e)}

# === MIDDLEWARE ===

class EnterpriseMiddleware(BaseHTTPMiddleware):
    """Comprehensive enterprise middleware"""
    
    def __init__(self, app, cache_manager, rate_limiter, circuit_breaker):
        super().__init__(app)
        self.cache_manager = cache_manager
        self.rate_limiter = rate_limiter
        self.circuit_breaker = circuit_breaker
        
        # Prometheus metrics
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
            self.active_requests = Gauge('http_active_requests', 'Active requests')
    
    async def dispatch(self, request: Request, call_next):
        """Process request with all enterprise features"""
        start_time = time.perf_counter()
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        if PROMETHEUS_AVAILABLE:
            self.active_requests.inc()
        
        try:
            # Rate limiting
            if self.rate_limiter:
                client_ip = request.client.host
                allowed, info = await self.rate_limiter.is_allowed(client_ip)
                
                if not allowed:
                    return JSONResponse(
                        status_code=429,
                        content={"error": "Rate limit exceeded", "retry_after": 60},
                        headers={"Retry-After": "60"}
                    )
            
            # Circuit breaker protection for sensitive endpoints
            if request.url.path.startswith("/api/"):
                response = await self.circuit_breaker.call(call_next, request)
            else:
                response = await call_next(request)
            
            # Add headers
            duration = time.perf_counter() - start_time
            response.headers.update({
                "X-Request-ID": request_id,
                "X-Process-Time": f"{duration:.4f}",
                "X-Cache-Hit-Ratio": f"{self.cache_manager.hit_ratio:.3f}",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block"
            })
            
            # Record metrics
            if PROMETHEUS_AVAILABLE:
                self.request_count.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=response.status_code
                ).inc()
                
                self.request_duration.labels(
                    method=request.method,
                    endpoint=request.url.path
                ).observe(duration)
            
            return response
            
        except HTTPException as e:
            # Handle known HTTP exceptions
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.detail,
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            # Handle unexpected exceptions
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        finally:
            if PROMETHEUS_AVAILABLE:
                self.active_requests.dec()

# === GLOBAL INSTANCES ===

cache_manager = EnterpriseCache()
circuit_breaker = CircuitBreaker()
rate_limiter = None  # Will be initialized after Redis

# === APPLICATION LIFESPAN ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced application lifecycle management"""
    logger.info("🚀 Starting Enhanced Enterprise API...")
    
    # Initialize cache and Redis
    await cache_manager.init_redis()
    
    # Initialize rate limiter
    global rate_limiter
    if cache_manager.redis_client:
        rate_limiter = RateLimiter(cache_manager.redis_client)
        logger.info("✅ Rate limiter initialized")
    
    # Warm up cache for cold start optimization
    await cache_manager.set("warmup", {"status": "ready"}, ttl=60)
    
    logger.info("✅ Enhanced Enterprise API ready")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down Enhanced Enterprise API...")
    
    if cache_manager.redis_client:
        await cache_manager.redis_client.close()
    
    logger.info("✅ Shutdown complete")

# === ENHANCED APPLICATION FACTORY ===

def create_enhanced_application() -> FastAPI:
    """Create enhanced FastAPI application with enterprise features"""
    
    app = FastAPI(
        title="Enhanced Onyx Backend",
        description="""
        🚀 Enhanced enterprise backend with advanced microservices patterns:
        
        ## Features
        - ⚡ Multi-tier caching (Memory + Redis)
        - 🔄 Circuit breakers for resilience
        - 🛡️ Rate limiting & security headers
        - 📊 Prometheus metrics
        - 🏥 Health checks
        - ⚙️ Serverless optimization
        - 🔍 Request tracing
        """,
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # === MIDDLEWARE STACK ===
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if CORS_ALLOWED_ORIGIN == "*" else [CORS_ALLOWED_ORIGIN],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=86400
    )
    
    # Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Enterprise middleware
    app.add_middleware(
        EnterpriseMiddleware,
        cache_manager=cache_manager,
        rate_limiter=rate_limiter,
        circuit_breaker=circuit_breaker
    )
    
    # === ENHANCED ENDPOINTS ===
    
    @app.get("/")
    async def enhanced_root():
        """Enhanced root endpoint with comprehensive info"""
        return {
            "service": "Enhanced Onyx Backend",
            "version": __version__,
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "features": {
                "caching": {
                    "enabled": True,
                    "hit_ratio": cache_manager.hit_ratio,
                    "redis_available": cache_manager.redis_client is not None
                },
                "circuit_breaker": {
                    "enabled": True,
                    "state": circuit_breaker.state,
                    "failure_count": circuit_breaker.failure_count
                },
                "rate_limiting": rate_limiter is not None,
                "monitoring": PROMETHEUS_AVAILABLE,
                "security": True
            },
            "endpoints": {
                "health": "/health",
                "metrics": "/metrics" if PROMETHEUS_AVAILABLE else None,
                "cache_stats": "/cache/stats",
                "circuit_breaker": "/circuit-breaker/stats"
            }
        }
    
    @app.get("/health")
    async def enhanced_health():
        """Comprehensive health check"""
        redis_healthy = cache_manager.redis_client is not None
        if cache_manager.redis_client:
            try:
                await cache_manager.redis_client.ping()
                redis_healthy = True
            except:
                redis_healthy = False
        
        overall_health = redis_healthy and circuit_breaker.state != "OPEN"
        
        return {
            "status": "healthy" if overall_health else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "redis": "healthy" if redis_healthy else "unhealthy",
                "circuit_breaker": circuit_breaker.state,
                "cache": "healthy" if cache_manager.hit_ratio >= 0 else "unknown"
            },
            "metrics": {
                "cache_hit_ratio": cache_manager.hit_ratio,
                "circuit_breaker_failures": circuit_breaker.failure_count
            }
        }
    
    @app.get("/health/live")
    async def liveness_probe():
        """Kubernetes liveness probe"""
        return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
    
    @app.get("/health/ready")
    async def readiness_probe():
        """Kubernetes readiness probe"""
        ready = (cache_manager.redis_client is not None and 
                circuit_breaker.state != "OPEN")
        
        return {
            "status": "ready" if ready else "not_ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/cache/stats")
    async def cache_statistics():
        """Get cache statistics"""
        return cache_manager.get_stats()
    
    @app.get("/circuit-breaker/stats")
    async def circuit_breaker_stats():
        """Get circuit breaker statistics"""
        return {
            "state": circuit_breaker.state,
            "failure_count": circuit_breaker.failure_count,
            "failure_threshold": circuit_breaker.failure_threshold,
            "timeout": circuit_breaker.timeout,
            "last_failure_time": circuit_breaker.last_failure_time
        }
    
    if PROMETHEUS_AVAILABLE:
        @app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint"""
            return Response(content=generate_latest(), media_type="text/plain")
    
    @app.get("/api/v1/cached-example")
    async def cached_example_endpoint():
        """Example endpoint demonstrating caching"""
        cache_key = "example_data"
        
        # Try to get from cache
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            return {
                "data": cached_data,
                "cached": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Generate fresh data
        fresh_data = {
            "message": "This is fresh data",
            "generated_at": datetime.utcnow().isoformat(),
            "random_value": time.time()
        }
        
        # Cache for 5 minutes
        await cache_manager.set(cache_key, fresh_data, ttl=300)
        
        return {
            "data": fresh_data,
            "cached": False,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return app

# === MAIN APPLICATION ===

# Create enhanced application
enhanced_app = create_enhanced_application()

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting Enhanced Onyx Backend v{__version__}")
    logger.info(f"🌐 Server will run on http://{APP_HOST}:{APP_PORT}")
    logger.info("📊 Features: Caching, Circuit Breakers, Rate Limiting, Monitoring")
    
    # Run with optimal settings
    uvicorn.run(
        "improved_main:enhanced_app",
        host=APP_HOST,
        port=APP_PORT,
        reload=False,  # Disable in production
        workers=1,     # Use multiple workers in production
        loop="uvloop" if sys.platform != "win32" else "asyncio",
        access_log=True,
        log_level="info"
    ) 