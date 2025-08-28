from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
    import redis.asyncio as redis
    from prometheus_client import Counter, generate_latest
                    import json
                import json
from fastapi import Response
    import uvicorn
from typing import Any, List, Dict, Optional
import logging
"""
🚀 ENTERPRISE API DEMO
===================

Compact demonstration of advanced FastAPI patterns for microservices:
- Circuit breakers
- Multi-tier caching
- Rate limiting
- Metrics & monitoring
- Health checks
- Security headers
"""



# Optional dependencies
try:
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# === ENTERPRISE COMPONENTS ===

class SimpleCache:
    """Multi-tier cache with Redis and memory"""
    
    def __init__(self) -> Any:
        self.redis_client = None
        self.memory_cache = {}
        self.hit_count = 0
        self.miss_count = 0
    
    async def init_redis(self) -> Any:
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url("redis://localhost:6379")
                await self.redis_client.ping()
                print("✅ Redis cache initialized")
            except:
                print("❌ Redis unavailable, using memory only")
    
    async def get(self, key: str) -> Optional[Any]:
        # Try memory first
        if key in self.memory_cache:
            self.hit_count += 1
            return self.memory_cache[key]
        
        # Try Redis
        if self.redis_client:
            try:
                data = await self.redis_client.get(f"demo:{key}")
                if data:
                    value = json.loads(data)
                    self.memory_cache[key] = value
                    self.hit_count += 1
                    return value
            except:
                pass
        
        self.miss_count += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        
    """set function."""
self.memory_cache[key] = value
        if self.redis_client:
            try:
                await self.redis_client.setex(f"demo:{key}", ttl, json.dumps(value))
            except:
                pass
    
    @property
    def hit_ratio(self) -> float:
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0

class CircuitBreaker:
    """Simple circuit breaker"""
    
    def __init__(self, failure_threshold: int = 3):
        
    """__init__ function."""
self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure = None
    
    async def call(self, func, *args, **kwargs) -> Any:
        if self.state == "OPEN":
            if time.time() - self.last_failure > 30:  # 30 second timeout
                self.state = "CLOSED"
                self.failure_count = 0
            else:
                raise HTTPException(503, "Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise

class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self) -> Any:
        self.requests = {}
    
    async def is_allowed(self, identifier: str, limit: int = 100) -> bool:
        now = time.time()
        window = 60  # 1 minute
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] 
            if now - req_time < window
        ]
        
        if len(self.requests[identifier]) >= limit:
            return False
        
        self.requests[identifier].append(now)
        return True

# === GLOBAL INSTANCES ===

cache = SimpleCache()
circuit_breaker = CircuitBreaker()
rate_limiter = RateLimiter()

if PROMETHEUS_AVAILABLE:
    request_counter = Counter('demo_requests_total', 'Total requests', ['endpoint'])

# === APPLICATION LIFESPAN ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    """lifespan function."""
print("🚀 Starting Enterprise Demo API...")
    await cache.init_redis()
    print("✅ Startup complete")
    
    yield
    
    print("🛑 Shutting down...")
    if cache.redis_client:
        await cache.redis_client.close()
    print("✅ Shutdown complete")

# === APPLICATION FACTORY ===

def create_demo_app() -> FastAPI:
    app = FastAPI(
        title="Enterprise Demo API",
        description="Demonstration of advanced FastAPI patterns",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Custom middleware for enterprise features
    @app.middleware("http")
    async def enterprise_middleware(request: Request, call_next):
        
    """enterprise_middleware function."""
start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Rate limiting
        client_ip = request.client.host
        if not await rate_limiter.is_allowed(client_ip):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add enterprise headers
        response.headers.update({
            "X-Request-ID": request_id,
            "X-Process-Time": f"{time.time() - start_time:.4f}",
            "X-Cache-Hit-Ratio": f"{cache.hit_ratio:.3f}",
            "X-Circuit-Breaker": circuit_breaker.state,
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY"
        })
        
        # Record metrics
        if PROMETHEUS_AVAILABLE:
            request_counter.labels(endpoint=request.url.path).inc()
        
        return response
    
    # === ENDPOINTS ===
    
    @app.get("/")
    async def root():
        
    """root function."""
return {
            "service": "Enterprise Demo API",
            "version": "1.0.0",
            "status": "operational",
            "features": {
                "caching": {"hit_ratio": cache.hit_ratio, "redis": cache.redis_client is not None},
                "circuit_breaker": {"state": circuit_breaker.state, "failures": circuit_breaker.failure_count},
                "rate_limiting": True,
                "monitoring": PROMETHEUS_AVAILABLE
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/health")
    async def health_check():
        
    """health_check function."""
redis_ok = cache.redis_client is not None
        circuit_ok = circuit_breaker.state != "OPEN"
        
        return {
            "status": "healthy" if redis_ok and circuit_ok else "degraded",
            "checks": {
                "redis": "ok" if redis_ok else "unavailable",
                "circuit_breaker": circuit_breaker.state,
                "cache": f"hit_ratio={cache.hit_ratio:.3f}"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/api/cached")
    async def cached_endpoint():
        """Endpoint demonstrating caching"""
        cache_key = "demo_data"
        
        # Try cache first
        cached_data = await cache.get(cache_key)
        if cached_data:
            return {"data": cached_data, "cached": True}
        
        # Generate fresh data
        fresh_data = {
            "message": "Fresh data from API",
            "timestamp": datetime.utcnow().isoformat(),
            "random": time.time()
        }
        
        # Cache for 5 minutes
        await cache.set(cache_key, fresh_data, ttl=300)
        
        return {"data": fresh_data, "cached": False}
    
    @app.get("/api/protected")
    async def protected_endpoint():
        """Endpoint with circuit breaker protection"""
        
        async def business_logic():
            
    """business_logic function."""
# Simulate potential failures
            if time.time() % 10 < 2:  # 20% chance of failure
                raise Exception("Simulated service failure")
            
            return {
                "message": "Protected operation successful",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return await circuit_breaker.call(business_logic)
    
    @app.get("/stats")
    async def get_stats():
        """Get comprehensive statistics"""
        return {
            "cache": {
                "hit_count": cache.hit_count,
                "miss_count": cache.miss_count,
                "hit_ratio": cache.hit_ratio,
                "memory_items": len(cache.memory_cache),
                "redis_available": cache.redis_client is not None
            },
            "circuit_breaker": {
                "state": circuit_breaker.state,
                "failure_count": circuit_breaker.failure_count,
                "threshold": circuit_breaker.failure_threshold
            },
            "rate_limiter": {
                "tracked_ips": len(rate_limiter.requests)
            }
        }
    
    if PROMETHEUS_AVAILABLE:
        @app.get("/metrics")
        async def metrics():
            
    """metrics function."""
            return Response(content=generate_latest(), media_type="text/plain")
    
    return app

# === APPLICATION INSTANCE ===

app = create_demo_app()

if __name__ == "__main__":
    print("🚀 Starting Enterprise Demo API on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001) 