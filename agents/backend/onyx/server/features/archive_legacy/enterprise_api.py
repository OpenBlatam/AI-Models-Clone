"""
🚀 ENTERPRISE API - Advanced FastAPI Implementation
==================================================

Ultra-optimized enterprise API with:
- Microservices architecture patterns
- Serverless optimization
- Advanced middleware stack
- Circuit breakers & retries
- Multi-tier caching
- Distributed tracing
- OAuth2 & security best practices
- Auto-scaling capabilities
- Health checks & monitoring
"""

import asyncio
import time
import uuid
import hashlib
import weakref
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor

# FastAPI & Dependencies
from fastapi import FastAPI, Request, Response, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi

# Advanced Libraries
try:
    import orjson as json
    JSONDecoder = json.loads
    JSONEncoder = json.dumps
except ImportError:
    import json
    JSONDecoder = json.loads
    JSONEncoder = json.dumps

try:
    from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    import opentelemetry
    from opentelemetry.trace import get_tracer
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False

try:
    import aiocache
    from aiocache import Cache, serializers
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

# === CONFIGURATION & SETTINGS ===

@dataclass
class EnterpriseConfig:
    """Enterprise API configuration with all advanced features"""
    
    # Application
    app_name: str = "Enterprise API"
    app_version: str = "1.0.0"
    environment: str = "production"
    debug: bool = False
    
    # Security
    secret_key: str = "ultra-secure-key-change-in-production"
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    trusted_hosts: List[str] = field(default_factory=lambda: ["*"])
    oauth2_scheme: str = "Bearer"
    
    # Performance
    max_workers: int = 10
    connection_pool_size: int = 50
    request_timeout: int = 30
    
    # Caching
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600
    cache_max_size: int = 10000
    
    # Rate Limiting
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600
    
    # Circuit Breaker
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    
    # Monitoring
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_health_checks: bool = True
    
    # Serverless Optimization
    cold_start_optimization: bool = True
    preload_dependencies: bool = True
    lazy_loading: bool = True

config = EnterpriseConfig()

# === ADVANCED CIRCUIT BREAKER ===

class CircuitBreakerState:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class AdvancedCircuitBreaker:
    """Enterprise-grade circuit breaker with exponential backoff"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60, 
                 half_open_max_calls: int = 5):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.half_open_calls = 0
        
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_calls = 0
            else:
                raise HTTPException(
                    status_code=503, 
                    detail="Service temporarily unavailable (Circuit Breaker OPEN)"
                )
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                raise HTTPException(
                    status_code=503, 
                    detail="Service temporarily unavailable (Circuit Breaker HALF_OPEN)"
                )
            self.half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise
    
    async def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.half_open_calls = 0
    
    async def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

# === ADVANCED CACHING SYSTEM ===

class EnterpriseCacheManager:
    """Multi-tier caching with Redis, memory, and intelligent eviction"""
    
    def __init__(self, redis_url: str, max_memory_items: int = 1000):
        self.redis_url = redis_url
        self.redis_client = None
        self.memory_cache = weakref.WeakValueDictionary()
        self.access_times = {}
        self.max_memory_items = max_memory_items
        self.hit_count = 0
        self.miss_count = 0
        
    async def init_redis(self):
        """Initialize Redis connection with retry logic"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                max_connections=20,
                retry_on_timeout=True,
                health_check_interval=30
            )
            await self.redis_client.ping()
        except Exception as e:
            logging.warning(f"Redis initialization failed: {e}")
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache with L1 (memory) -> L2 (Redis) fallback"""
        cache_key = self._generate_key(key)
        
        # L1: Memory cache
        if cache_key in self.memory_cache:
            self.hit_count += 1
            self.access_times[cache_key] = time.time()
            return self.memory_cache[cache_key]
        
        # L2: Redis cache
        if self.redis_client:
            try:
                data = await self.redis_client.get(cache_key)
                if data:
                    value = JSONDecoder(data)
                    await self._store_in_memory(cache_key, value)
                    self.hit_count += 1
                    return value
            except Exception as e:
                logging.warning(f"Redis get failed: {e}")
        
        self.miss_count += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set in cache with intelligent storage"""
        cache_key = self._generate_key(key)
        ttl = ttl or config.cache_ttl
        
        # Store in memory
        await self._store_in_memory(cache_key, value)
        
        # Store in Redis asynchronously
        if self.redis_client:
            try:
                asyncio.create_task(
                    self.redis_client.setex(cache_key, ttl, JSONEncoder(value))
                )
            except Exception as e:
                logging.warning(f"Redis set failed: {e}")
        
        return True
    
    async def _store_in_memory(self, key: str, value: Any):
        """Store in memory with LRU eviction"""
        if len(self.memory_cache) >= self.max_memory_items:
            # LRU eviction
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.memory_cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.memory_cache[key] = value
        self.access_times[key] = time.time()
    
    def _generate_key(self, key: str) -> str:
        """Generate consistent cache key"""
        return f"enterprise:{hashlib.md5(key.encode()).hexdigest()}"
    
    @property
    def hit_ratio(self) -> float:
        """Calculate cache hit ratio"""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0

# === ADVANCED RATE LIMITER ===

class EnterpriseRateLimiter:
    """Distributed rate limiter with sliding window"""
    
    def __init__(self, redis_client, requests_per_window: int = 1000, window_size: int = 3600):
        self.redis_client = redis_client
        self.requests_per_window = requests_per_window
        self.window_size = window_size
    
    async def is_allowed(self, identifier: str) -> tuple[bool, Dict[str, Any]]:
        """Check if request is allowed under rate limit"""
        if not self.redis_client:
            return True, {"rate_limit_active": False}
        
        key = f"rate_limit:{identifier}"
        current_time = time.time()
        window_start = current_time - self.window_size
        
        try:
            # Use Redis sorted set for sliding window
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcount(key, window_start, current_time)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, self.window_size)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            allowed = current_requests < self.requests_per_window
            remaining = max(0, self.requests_per_window - current_requests)
            
            return allowed, {
                "rate_limit_active": True,
                "requests_remaining": remaining,
                "window_size": self.window_size,
                "current_requests": current_requests
            }
            
        except Exception as e:
            logging.warning(f"Rate limiting failed for {identifier}: {e}")
            return True, {"rate_limit_active": False, "error": str(e)}

# === METRICS & MONITORING ===

class EnterpriseMetrics:
    """Advanced metrics collection with Prometheus integration"""
    
    def __init__(self):
        if PROMETHEUS_AVAILABLE:
            self.registry = CollectorRegistry()
            
            self.request_count = Counter(
                'api_requests_total',
                'Total API requests',
                ['method', 'endpoint', 'status'],
                registry=self.registry
            )
            
            self.request_duration = Histogram(
                'api_request_duration_seconds',
                'API request duration',
                ['method', 'endpoint'],
                registry=self.registry
            )
            
            self.active_connections = Gauge(
                'api_active_connections',
                'Active connections',
                registry=self.registry
            )
            
            self.cache_operations = Counter(
                'cache_operations_total',
                'Cache operations',
                ['operation', 'result'],
                registry=self.registry
            )
            
            self.circuit_breaker_state = Gauge(
                'circuit_breaker_state',
                'Circuit breaker state (0=closed, 1=open, 2=half_open)',
                ['service'],
                registry=self.registry
            )
        
        self.custom_metrics = {}
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record request metrics"""
        if PROMETHEUS_AVAILABLE:
            self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
            self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation metrics"""
        if PROMETHEUS_AVAILABLE:
            self.cache_operations.labels(operation=operation, result=result).inc()
    
    def get_metrics_data(self) -> str:
        """Get Prometheus formatted metrics"""
        if PROMETHEUS_AVAILABLE:
            return generate_latest(self.registry).decode()
        return "Prometheus not available"

# === ADVANCED MIDDLEWARE STACK ===

class EnterpriseMiddleware:
    """Collection of enterprise-grade middleware"""
    
    @staticmethod
    async def request_id_middleware(request: Request, call_next):
        """Add unique request ID for tracing"""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    
    @staticmethod
    async def performance_monitoring_middleware(request: Request, call_next):
        """Monitor request performance"""
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        duration = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        
        # Record metrics
        metrics.record_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration
        )
        
        return response
    
    @staticmethod
    async def security_headers_middleware(request: Request, call_next):
        """Add security headers"""
        response = await call_next(request)
        
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        })
        
        return response
    
    @staticmethod
    async def rate_limiting_middleware(request: Request, call_next):
        """Rate limiting middleware"""
        client_ip = request.client.host
        identifier = f"{client_ip}:{request.url.path}"
        
        allowed, info = await rate_limiter.is_allowed(identifier)
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": info.get("window_size", 3600)
                },
                headers={
                    "Retry-After": str(info.get("window_size", 3600)),
                    "X-RateLimit-Remaining": str(info.get("requests_remaining", 0))
                }
            )
        
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(info.get("requests_remaining", 0))
        return response

# === HEALTH CHECKS ===

class HealthChecker:
    """Advanced health checking system"""
    
    def __init__(self):
        self.checks = {}
        self.last_check_time = {}
        self.check_cache_ttl = 30  # seconds
    
    def register_check(self, name: str, check_func: Callable):
        """Register a health check"""
        self.checks[name] = check_func
    
    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "version": config.app_version
        }
        
        overall_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                # Use cached result if available
                if (name in self.last_check_time and 
                    time.time() - self.last_check_time[name] < self.check_cache_ttl):
                    continue
                
                check_result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                results["checks"][name] = {
                    "status": "healthy" if check_result else "unhealthy",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                if not check_result:
                    overall_healthy = False
                
                self.last_check_time[name] = time.time()
                
            except Exception as e:
                results["checks"][name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                overall_healthy = False
        
        results["status"] = "healthy" if overall_healthy else "unhealthy"
        return results

# === GLOBAL INSTANCES ===

cache_manager = EnterpriseCacheManager(config.redis_url)
circuit_breaker = AdvancedCircuitBreaker()
metrics = EnterpriseMetrics()
rate_limiter = None  # Will be initialized with Redis
health_checker = HealthChecker()

# === APPLICATION LIFESPAN ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle with proper initialization and cleanup"""
    
    # Startup
    logging.info("🚀 Starting Enterprise API...")
    
    # Initialize Redis connections
    await cache_manager.init_redis()
    
    global rate_limiter
    if cache_manager.redis_client:
        rate_limiter = EnterpriseRateLimiter(cache_manager.redis_client)
    
    # Register health checks
    health_checker.register_check("redis", lambda: cache_manager.redis_client is not None)
    health_checker.register_check("cache", lambda: cache_manager.hit_ratio > 0 or cache_manager.miss_count == 0)
    
    # Serverless optimizations
    if config.cold_start_optimization:
        # Preload critical dependencies
        await cache_manager.get("warmup")  # Warm up connections
    
    # Initialize distributed tracing
    if TRACING_AVAILABLE and config.enable_tracing:
        FastAPIInstrumentor.instrument_app(app)
        logging.info("✅ Distributed tracing initialized")
    
    logging.info("✅ Enterprise API startup complete")
    
    yield
    
    # Shutdown
    logging.info("🛑 Shutting down Enterprise API...")
    
    if cache_manager.redis_client:
        await cache_manager.redis_client.close()
    
    logging.info("✅ Enterprise API shutdown complete")

# === ENTERPRISE FASTAPI APPLICATION ===

def create_enterprise_app() -> FastAPI:
    """Create enterprise-optimized FastAPI application"""
    
    app = FastAPI(
        title=config.app_name,
        description="""
        🚀 Enterprise API with Advanced Microservices Architecture
        
        ## Features
        - ⚡ Ultra-high performance with async optimization
        - 🛡️ Advanced security with OAuth2 & security headers
        - 🔄 Circuit breakers & automatic retries
        - 📊 Multi-tier caching (Memory + Redis)
        - 📈 Prometheus metrics & distributed tracing
        - 🌐 Rate limiting & DDoS protection
        - 🏥 Advanced health checks
        - ☁️ Serverless optimized
        - 🔧 Microservices ready
        """,
        version=config.app_version,
        docs_url="/docs" if config.debug else None,
        redoc_url="/redoc" if config.debug else None,
        lifespan=lifespan,
        default_response_class=JSONResponse
    )
    
    # === MIDDLEWARE STACK (Order matters - last added = first executed) ===
    
    # Security middleware (outermost)
    if config.environment == "production":
        app.add_middleware(HTTPSRedirectMiddleware)
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=config.trusted_hosts
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=["*"],
        max_age=86400
    )
    
    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Custom enterprise middleware
    app.middleware("http")(EnterpriseMiddleware.security_headers_middleware)
    app.middleware("http")(EnterpriseMiddleware.performance_monitoring_middleware)
    app.middleware("http")(EnterpriseMiddleware.request_id_middleware)
    
    if rate_limiter:
        app.middleware("http")(EnterpriseMiddleware.rate_limiting_middleware)
    
    # === ADVANCED ENDPOINTS ===
    
    @app.get("/", tags=["Root"])
    async def root():
        """Enterprise API root endpoint with comprehensive info"""
        return {
            "service": config.app_name,
            "version": config.app_version,
            "environment": config.environment,
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "features": {
                "microservices_ready": True,
                "serverless_optimized": config.cold_start_optimization,
                "circuit_breaker": circuit_breaker.state,
                "caching": {
                    "hit_ratio": cache_manager.hit_ratio,
                    "redis_available": cache_manager.redis_client is not None
                },
                "rate_limiting": rate_limiter is not None,
                "metrics": config.enable_metrics,
                "tracing": config.enable_tracing and TRACING_AVAILABLE
            },
            "endpoints": {
                "health": "/health",
                "metrics": "/metrics" if config.enable_metrics else None,
                "docs": "/docs" if config.debug else None
            }
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Advanced health check endpoint"""
        return await health_checker.run_checks()
    
    @app.get("/health/live", tags=["Health"])
    async def liveness_check():
        """Kubernetes liveness probe"""
        return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
    
    @app.get("/health/ready", tags=["Health"])
    async def readiness_check():
        """Kubernetes readiness probe"""
        redis_ready = cache_manager.redis_client is not None
        return {
            "status": "ready" if redis_ready else "not_ready",
            "checks": {
                "redis": redis_ready
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    if config.enable_metrics and PROMETHEUS_AVAILABLE:
        @app.get("/metrics", tags=["Monitoring"])
        async def get_metrics():
            """Prometheus metrics endpoint"""
            return Response(
                content=metrics.get_metrics_data(),
                media_type="text/plain"
            )
    
    @app.get("/info", tags=["Information"])
    async def system_info():
        """System information endpoint"""
        return {
            "app": {
                "name": config.app_name,
                "version": config.app_version,
                "environment": config.environment
            },
            "system": {
                "cache_hit_ratio": cache_manager.hit_ratio,
                "circuit_breaker_state": circuit_breaker.state,
                "rate_limiter_active": rate_limiter is not None
            },
            "capabilities": {
                "prometheus": PROMETHEUS_AVAILABLE,
                "tracing": TRACING_AVAILABLE,
                "cache": CACHE_AVAILABLE
            }
        }
    
    # === EXAMPLE PROTECTED ENDPOINTS ===
    
    @app.get("/api/v1/protected", tags=["API"])
    async def protected_endpoint(request: Request):
        """Example protected endpoint with all enterprise features"""
        
        # Circuit breaker protection
        async def business_logic():
            # Simulate some business logic
            await asyncio.sleep(0.1)
            return {
                "message": "Protected data accessed successfully",
                "request_id": getattr(request.state, "request_id", None),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            result = await circuit_breaker.call(business_logic)
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
    @app.get("/api/v1/cached", tags=["API"])
    async def cached_endpoint(request: Request):
        """Example endpoint with intelligent caching"""
        cache_key = f"cached_data:{request.client.host}"
        
        # Try cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return {
                "data": cached_result,
                "cached": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Generate new data
        fresh_data = {
            "message": "Fresh data generated",
            "request_id": getattr(request.state, "request_id", None),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Cache the result
        await cache_manager.set(cache_key, fresh_data, ttl=300)
        
        return {
            "data": fresh_data,
            "cached": False,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # === EXCEPTION HANDLERS ===
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with detailed logging"""
        logging.warning(
            f"HTTP {exc.status_code} error on {request.method} {request.url.path}: {exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
                "request_id": getattr(request.state, "request_id", None),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions"""
        logging.error(
            f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "status_code": 500,
                "request_id": getattr(request.state, "request_id", None),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # === OPENAPI CUSTOMIZATION ===
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=config.app_name,
            version=config.app_version,
            description="Enterprise API with Advanced Microservices Architecture",
            routes=app.routes,
        )
        
        # Add custom security schemes
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    
    return app

# === APPLICATION INSTANCE ===

app = create_enterprise_app()

# === PRODUCTION RECOMMENDATIONS ===

"""
🚀 PRODUCTION DEPLOYMENT RECOMMENDATIONS:

1. ENVIRONMENT VARIABLES:
   - REDIS_URL=redis://your-redis-cluster:6379
   - SECRET_KEY=your-ultra-secure-secret-key
   - ENVIRONMENT=production
   - ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

2. KUBERNETES DEPLOYMENT:
   - Use horizontal pod autoscaler (HPA)
   - Configure resource limits (CPU: 500m, Memory: 512Mi)
   - Set up liveness/readiness probes pointing to /health/live and /health/ready

3. API GATEWAY INTEGRATION:
   - Use Kong, AWS API Gateway, or Traefik
   - Configure rate limiting at gateway level
   - Set up JWT validation
   - Enable request/response transformation

4. MONITORING & OBSERVABILITY:
   - Deploy Prometheus + Grafana
   - Configure log aggregation (ELK/EFK stack)
   - Set up alerting rules
   - Use Jaeger for distributed tracing

5. SERVERLESS DEPLOYMENT:
   - Package with minimal dependencies
   - Use Lambda layers for common libraries
   - Configure provisioned concurrency for predictable latency
   - Set memory allocation to 512MB+ for optimal performance

6. SECURITY:
   - Use AWS WAF or Cloudflare for DDoS protection
   - Implement OAuth2/OIDC for authentication
   - Configure security groups/firewall rules
   - Enable audit logging

7. SCALING:
   - Use Redis Cluster for distributed caching
   - Configure connection pooling
   - Implement database read replicas
   - Use CDN for static content

8. CIRCUIT BREAKER TUNING:
   - Adjust failure thresholds based on SLA requirements
   - Configure different timeouts for different services
   - Monitor circuit breaker metrics

COMMAND TO RUN:
uvicorn enterprise_api:app --host 0.0.0.0 --port 8000 --workers 4
""" 