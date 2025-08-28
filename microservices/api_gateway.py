"""
API Gateway Microservice
========================

This module provides API Gateway capabilities for the microservices architecture.
It handles routing, rate limiting, authentication, caching, and request/response transformation.

Author: AI Assistant
Version: 10.1
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import logging
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import redis.asyncio as redis
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"

@dataclass
class RouteConfig:
    """Route configuration data class."""
    path: str
    service_name: str
    service_version: Optional[str] = None
    methods: List[str] = None
    rate_limit: Optional[int] = None
    rate_limit_window: int = 60  # seconds
    rate_limit_strategy: RateLimitStrategy = RateLimitStrategy.FIXED_WINDOW
    cache_ttl: Optional[int] = None
    auth_required: bool = False
    transform_request: bool = False
    transform_response: bool = False
    timeout: int = 30  # seconds
    retry_count: int = 3
    circuit_breaker: bool = True

class APIGateway:
    """
    API Gateway implementation for microservices architecture.
    
    Provides centralized routing, rate limiting, authentication, caching,
    and request/response transformation capabilities.
    """
    
    def __init__(self, 
                 service_discovery_url: str = "http://localhost:8080",
                 redis_url: str = "redis://localhost:6379",
                 gateway_host: str = "0.0.0.0",
                 gateway_port: int = 8000):
        """
        Initialize the API Gateway.
        
        Args:
            service_discovery_url: Service discovery registry URL
            redis_url: Redis connection URL for caching
            gateway_host: Gateway host
            gateway_port: Gateway port
        """
        self.service_discovery_url = service_discovery_url
        self.redis_url = redis_url
        self.gateway_host = gateway_host
        self.gateway_port = gateway_port
        
        # Initialize components
        self.app = FastAPI(title="API Gateway", version="10.1.0")
        self.redis_client: Optional[redis.Redis] = None
        self.routes: Dict[str, RouteConfig] = {}
        self.rate_limiters: Dict[str, Dict] = {}
        self.circuit_breakers: Dict[str, Dict] = {}
        
        # Setup middleware
        self._setup_middleware()
        
    def _setup_middleware(self):
        """Setup FastAPI middleware."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]
        )
        
        # Custom middleware for rate limiting and authentication
        self.app.middleware("http")(self._gateway_middleware)
    
    async def _gateway_middleware(self, request: Request, call_next):
        """Custom gateway middleware for rate limiting and authentication."""
        start_time = time.time()
        
        # Extract route info
        route_path = request.url.path
        route_config = self._get_route_config(route_path, request.method)
        
        if not route_config:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Rate limiting check
        if route_config.rate_limit:
            if not await self._check_rate_limit(request, route_config):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Authentication check
        if route_config.auth_required:
            if not await self._authenticate_request(request):
                raise HTTPException(status_code=401, detail="Authentication required")
        
        # Circuit breaker check
        if route_config.circuit_breaker:
            if not await self._check_circuit_breaker(route_config.service_name):
                raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Add gateway headers
            response.headers["X-Gateway-Processing-Time"] = str(time.time() - start_time)
            response.headers["X-Gateway-Version"] = "10.1.0"
            
            return response
            
        except Exception as e:
            logger.error(f"Gateway error: {e}")
            raise HTTPException(status_code=500, detail="Internal gateway error")
    
    def add_route(self, route_config: RouteConfig):
        """
        Add a route configuration to the gateway.
        
        Args:
            route_config: Route configuration
        """
        route_key = f"{route_config.methods[0]}:{route_config.path}"
        self.routes[route_key] = route_config
        
        # Initialize rate limiter
        if route_config.rate_limit:
            self.rate_limiters[route_key] = {
                "tokens": route_config.rate_limit,
                "last_reset": time.time(),
                "window": route_config.rate_limit_window,
                "strategy": route_config.rate_limit_strategy
            }
        
        # Initialize circuit breaker
        if route_config.circuit_breaker:
            self.circuit_breakers[route_config.service_name] = {
                "failures": 0,
                "last_failure": 0,
                "threshold": 5,
                "timeout": 60,
                "state": "CLOSED"  # CLOSED, OPEN, HALF_OPEN
            }
        
        logger.info(f"Added route: {route_key} -> {route_config.service_name}")
    
    async def route_request(self, request: Request) -> Response:
        """
        Route a request to the appropriate service.
        
        Args:
            request: Incoming request
            
        Returns:
            Service response
        """
        route_path = request.url.path
        route_config = self._get_route_config(route_path, request.method)
        
        if not route_config:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Check cache for GET requests
        if request.method == "GET" and route_config.cache_ttl:
            cached_response = await self._get_cached_response(request)
            if cached_response:
                return cached_response
        
        # Discover service
        service_info = await self._discover_service(route_config)
        if not service_info:
            raise HTTPException(status_code=503, detail="Service not available")
        
        # Transform request if needed
        transformed_request = await self._transform_request(request, route_config)
        
        # Forward request to service
        service_response = await self._forward_request(
            service_info, 
            transformed_request, 
            route_config
        )
        
        # Transform response if needed
        transformed_response = await self._transform_response(service_response, route_config)
        
        # Cache response for GET requests
        if request.method == "GET" and route_config.cache_ttl:
            await self._cache_response(request, transformed_response, route_config.cache_ttl)
        
        return transformed_response
    
    def _get_route_config(self, path: str, method: str) -> Optional[RouteConfig]:
        """Get route configuration for path and method."""
        route_key = f"{method}:{path}"
        return self.routes.get(route_key)
    
    async def _check_rate_limit(self, request: Request, route_config: RouteConfig) -> bool:
        """Check if request is within rate limits."""
        route_key = f"{route_config.methods[0]}:{route_config.path}"
        rate_limiter = self.rate_limiters.get(route_key)
        
        if not rate_limiter:
            return True
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit based on strategy
        if rate_limiter["strategy"] == RateLimitStrategy.FIXED_WINDOW:
            return await self._check_fixed_window_rate_limit(client_id, rate_limiter)
        elif rate_limiter["strategy"] == RateLimitStrategy.SLIDING_WINDOW:
            return await self._check_sliding_window_rate_limit(client_id, rate_limiter)
        else:
            return True  # Default to allow
    
    async def _check_fixed_window_rate_limit(self, client_id: str, rate_limiter: Dict) -> bool:
        """Check fixed window rate limit."""
        current_time = time.time()
        window_start = current_time - (current_time % rate_limiter["window"])
        
        # Use Redis for distributed rate limiting
        if self.redis_client:
            key = f"rate_limit:{client_id}:{window_start}"
            current_count = await self.redis_client.get(key)
            
            if current_count and int(current_count) >= rate_limiter["tokens"]:
                return False
            
            await self.redis_client.incr(key)
            await self.redis_client.expire(key, rate_limiter["window"])
            return True
        
        return True
    
    async def _check_sliding_window_rate_limit(self, client_id: str, rate_limiter: Dict) -> bool:
        """Check sliding window rate limit."""
        current_time = time.time()
        
        if self.redis_client:
            key = f"rate_limit:{client_id}"
            
            # Remove old entries
            await self.redis_client.zremrangebyscore(key, 0, current_time - rate_limiter["window"])
            
            # Count current requests
            current_count = await self.redis_client.zcard(key)
            
            if current_count >= rate_limiter["tokens"]:
                return False
            
            # Add current request
            await self.redis_client.zadd(key, {str(current_time): current_time})
            await self.redis_client.expire(key, rate_limiter["window"])
            return True
        
        return True
    
    async def _authenticate_request(self, request: Request) -> bool:
        """Authenticate the request."""
        # Extract token from headers
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return False
        
        token = auth_header.split(" ")[1]
        
        # Validate token (implement your authentication logic here)
        # For now, we'll use a simple check
        return len(token) > 10
    
    async def _check_circuit_breaker(self, service_name: str) -> bool:
        """Check circuit breaker status."""
        circuit_breaker = self.circuit_breakers.get(service_name)
        if not circuit_breaker:
            return True
        
        current_time = time.time()
        
        if circuit_breaker["state"] == "OPEN":
            if current_time - circuit_breaker["last_failure"] > circuit_breaker["timeout"]:
                circuit_breaker["state"] = "HALF_OPEN"
                return True
            return False
        
        return True
    
    async def _discover_service(self, route_config: RouteConfig) -> Optional[Dict]:
        """Discover service using service discovery."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.service_discovery_url}/services/{route_config.service_name}"
                if route_config.service_version:
                    url += f"?version={route_config.service_version}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        services = await response.json()
                        if services:
                            # Return the first healthy service
                            return services[0]
                    return None
                    
        except Exception as e:
            logger.error(f"Service discovery error: {e}")
            return None
    
    async def _transform_request(self, request: Request, route_config: RouteConfig) -> Request:
        """Transform request if needed."""
        if not route_config.transform_request:
            return request
        
        # Implement request transformation logic here
        # For now, return the original request
        return request
    
    async def _transform_response(self, response: Response, route_config: RouteConfig) -> Response:
        """Transform response if needed."""
        if not route_config.transform_response:
            return response
        
        # Implement response transformation logic here
        # For now, return the original response
        return response
    
    async def _forward_request(self, service_info: Dict, request: Request, route_config: RouteConfig) -> Response:
        """Forward request to the target service."""
        try:
            service_url = f"http://{service_info['host']}:{service_info['port']}{request.url.path}"
            
            # Prepare request data
            headers = dict(request.headers)
            headers.pop("host", None)  # Remove host header
            
            # Forward the request
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=request.method,
                    url=service_url,
                    headers=headers,
                    params=dict(request.query_params),
                    data=await request.body(),
                    timeout=aiohttp.ClientTimeout(total=route_config.timeout)
                ) as response:
                    
                    # Read response content
                    content = await response.read()
                    
                    # Create FastAPI response
                    fastapi_response = Response(
                        content=content,
                        status_code=response.status,
                        headers=dict(response.headers)
                    )
                    
                    return fastapi_response
                    
        except Exception as e:
            logger.error(f"Service forwarding error: {e}")
            
            # Update circuit breaker
            await self._update_circuit_breaker(route_config.service_name, failed=True)
            
            raise HTTPException(status_code=503, detail="Service unavailable")
    
    async def _get_cached_response(self, request: Request) -> Optional[Response]:
        """Get cached response if available."""
        if not self.redis_client:
            return None
        
        cache_key = self._generate_cache_key(request)
        cached_data = await self.redis_client.get(cache_key)
        
        if cached_data:
            data = json.loads(cached_data)
            return Response(
                content=data["content"],
                status_code=data["status_code"],
                headers=data["headers"]
            )
        
        return None
    
    async def _cache_response(self, request: Request, response: Response, ttl: int):
        """Cache response."""
        if not self.redis_client:
            return
        
        cache_key = self._generate_cache_key(request)
        cache_data = {
            "content": response.body.decode(),
            "status_code": response.status_code,
            "headers": dict(response.headers)
        }
        
        await self.redis_client.setex(cache_key, ttl, json.dumps(cache_data))
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request."""
        key_data = f"{request.method}:{request.url.path}:{request.url.query}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Use IP address as client ID
        return request.client.host if request.client else "unknown"
    
    async def _update_circuit_breaker(self, service_name: str, failed: bool = False):
        """Update circuit breaker state."""
        circuit_breaker = self.circuit_breakers.get(service_name)
        if not circuit_breaker:
            return
        
        if failed:
            circuit_breaker["failures"] += 1
            circuit_breaker["last_failure"] = time.time()
            
            if circuit_breaker["failures"] >= circuit_breaker["threshold"]:
                circuit_breaker["state"] = "OPEN"
        else:
            circuit_breaker["failures"] = 0
            circuit_breaker["state"] = "CLOSED"
    
    async def start(self):
        """Start the API Gateway."""
        # Connect to Redis
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
        
        # Add dynamic route handler
        self.app.add_api_route("/{path:path}", self.route_request, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        
        logger.info(f"API Gateway started on {self.gateway_host}:{self.gateway_port}")
    
    async def stop(self):
        """Stop the API Gateway."""
        if self.redis_client:
            await self.redis_client.close()
        logger.info("API Gateway stopped")
    
    def get_route_stats(self) -> Dict[str, Any]:
        """Get gateway statistics."""
        return {
            "total_routes": len(self.routes),
            "rate_limited_routes": len(self.rate_limiters),
            "circuit_breakers": len(self.circuit_breakers),
            "redis_connected": self.redis_client is not None
        }


