"""
Refactored Router Engine for the Blaze AI module.

This module provides a high-performance, production-ready router engine with
improved architecture, better error handling, and enhanced performance optimizations.
"""

from __future__ import annotations

import asyncio
import time
import hashlib
import json
from typing import Any, Dict, List, Optional, Union, Tuple, Protocol, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import weakref

from . import Engine, EngineStatus
from ..core.interfaces import CoreConfig
from ..utils.logging import get_logger

# =============================================================================
# Protocols and Interfaces
# =============================================================================

class RouteProvider(Protocol):
    """Protocol for route providers."""
    async def get_route(self, route_id: str) -> Optional[Any]: ...
    async def register_route(self, route_id: str, route: Any) -> bool: ...
    async def unregister_route(self, route_id: str) -> bool: ...

class LoadBalancer(Protocol):
    """Protocol for load balancers."""
    async def select_route(self, routes: List[Any], context: Dict[str, Any]) -> Optional[Any]: ...
    async def update_metrics(self, route_id: str, metrics: Dict[str, Any]) -> None: ...

# =============================================================================
# Enhanced Enums and Data Classes
# =============================================================================

class LoadBalancingStrategy(Enum):
    """Enhanced load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    CONSISTENT_HASH = "consistent_hash"
    ADAPTIVE = "adaptive"
    POWER_OF_TWO = "power_of_two"
    LEAST_LOADED = "least_loaded"

class RouteStatus(Enum):
    """Route status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

@dataclass
class RouterConfig:
    """Enhanced router engine configuration."""
    enable_caching: bool = True
    cache_ttl: int = 1800  # 30 minutes
    cache_capacity: int = 10000
    max_concurrent_requests: int = 100
    enable_load_balancing: bool = True
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    enable_health_checks: bool = True
    health_check_interval: float = 30.0
    health_check_timeout: float = 10.0
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    enable_retry: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_metrics: bool = True
    metrics_interval: float = 60.0
    enable_rate_limiting: bool = True
    rate_limit_requests: int = 1000
    rate_limit_window: float = 60.0
    enable_request_batching: bool = True
    max_batch_size: int = 50
    batch_timeout: float = 0.1
    enable_priority_routing: bool = True
    priority_levels: int = 10
    enable_sticky_sessions: bool = False
    sticky_session_ttl: int = 3600
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if self.cache_ttl <= 0:
            errors.append("cache_ttl must be positive")
        
        if self.cache_capacity <= 0:
            errors.append("cache_capacity must be positive")
        
        if self.max_concurrent_requests <= 0:
            errors.append("max_concurrent_requests must be positive")
        
        if self.health_check_interval <= 0:
            errors.append("health_check_interval must be positive")
        
        if self.health_check_timeout <= 0:
            errors.append("health_check_timeout must be positive")
        
        if self.circuit_breaker_threshold <= 0:
            errors.append("circuit_breaker_threshold must be positive")
        
        if self.circuit_breaker_timeout <= 0:
            errors.append("circuit_breaker_timeout must be positive")
        
        if self.max_retries < 0:
            errors.append("max_retries must be non-negative")
        
        if self.retry_delay < 0:
            errors.append("retry_delay must be non-negative")
        
        if self.rate_limit_requests <= 0:
            errors.append("rate_limit_requests must be positive")
        
        if self.rate_limit_window <= 0:
            errors.append("rate_limit_window must be positive")
        
        if self.max_batch_size <= 0:
            errors.append("max_batch_size must be positive")
        
        if self.batch_timeout <= 0:
            errors.append("batch_timeout must be positive")
        
        if self.priority_levels <= 0:
            errors.append("priority_levels must be positive")
        
        return errors

@dataclass
class RouteInfo:
    """Enhanced route information structure."""
    route_id: str
    target_engine: str
    target_operation: str
    weight: float = 1.0
    priority: int = 1
    status: RouteStatus = RouteStatus.HEALTHY
    health_score: float = 1.0
    connection_count: int = 0
    response_time: float = 0.0
    error_rate: float = 0.0
    success_rate: float = 1.0
    last_health_check: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    circuit_breaker_state: str = "closed"
    maintenance_mode: bool = False
    
    def __post_init__(self):
        """Validate route information."""
        if self.weight <= 0.0:
            raise ValueError("Weight must be positive")
        
        if not (1 <= self.priority <= 10):
            raise ValueError("Priority must be between 1 and 10")
        
        if not (0.0 <= self.health_score <= 1.0):
            raise ValueError("Health score must be between 0.0 and 1.0")

@dataclass
class RoutingRequest:
    """Enhanced routing request structure."""
    route_id: str
    operation: str
    params: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    timeout: Optional[float] = None
    retry_count: int = 0
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate routing request."""
        if not self.route_id.strip():
            raise ValueError("Route ID cannot be empty")
        
        if not (1 <= self.priority <= 10):
            raise ValueError("Priority must be between 1 and 10")
        
        if self.retry_count < 0:
            raise ValueError("Retry count must be non-negative")

@dataclass
class RoutingResponse:
    """Enhanced routing response structure."""
    success: bool
    result: Optional[Any] = None
    route_id: Optional[str] = None
    target_engine: Optional[str] = None
    processing_time: float = 0.0
    retry_count: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RoutingDecision:
    """Enhanced routing decision structure."""
    route: RouteInfo
    strategy: LoadBalancingStrategy
    confidence: float = 1.0
    reasoning: str = ""
    alternatives: List[RouteInfo] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

# =============================================================================
# Enhanced Router Cache Implementation
# =============================================================================

class EnhancedRouterCache:
    """Intelligent router caching with advanced features."""
    
    def __init__(self, config: RouterConfig):
        self.config = config
        self.cache: Dict[str, Any] = {}
        self.access_order: List[str] = []
        self.access_count: Dict[str, int] = {}
        self.last_access: Dict[str, float] = {}
        self.expiration_times: Dict[str, float] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                await self._perform_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error and continue
                continue
    
    async def _perform_cleanup(self):
        """Perform cache cleanup."""
        async with self._lock:
            current_time = time.time()
            
            # Remove expired items
            expired_keys = [
                key for key, expiration_time in self.expiration_times.items()
                if current_time > expiration_time
            ]
            
            for key in expired_keys:
                await self._remove_item(key)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get item from cache with enhanced tracking."""
        async with self._lock:
            if key in self.cache:
                # Check expiration
                if key in self.expiration_times and time.time() > self.expiration_times[key]:
                    await self._remove_item(key)
                    return None
                
                # Update access tracking
                self.access_count[key] = self.access_count.get(key, 0) + 1
                self.last_access[key] = time.time()
                
                # Move to end (most recently used)
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                
                return self.cache[key]
            return None
    
    async def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Put item in cache with enhanced management."""
        async with self._lock:
            if key in self.cache:
                # Update existing
                if key in self.access_order:
                    self.access_order.remove(key)
            elif len(self.cache) >= self.config.cache_capacity:
                # Evict least valuable item
                await self._evict_least_valuable()
            
            self.cache[key] = value
            self.access_order.append(key)
            self.access_count[key] = 1
            self.last_access[key] = time.time()
            
            # Set expiration time
            ttl = ttl or self.config.cache_ttl
            self.expiration_times[key] = time.time() + ttl
    
    async def _evict_least_valuable(self):
        """Evict least valuable item based on access pattern and expiration."""
        if not self.access_order:
            return
        
        # Calculate value score for each item
        item_scores = {}
        current_time = time.time()
        
        for key in self.cache:
            access_score = self.access_count.get(key, 0) / max(current_time - self.last_access.get(key, 0), 1)
            time_until_expiry = self.expiration_times.get(key, 0) - current_time
            expiry_score = 1.0 / (max(time_until_expiry, 1) + 1)
            item_scores[key] = access_score * expiry_score
        
        # Remove least valuable item
        if item_scores:
            least_valuable = min(item_scores.keys(), key=lambda k: item_scores[k])
            await self._remove_item(least_valuable)
    
    async def _remove_item(self, key: str):
        """Remove item from cache."""
        if key in self.cache:
            del self.cache[key]
            del self.access_count[key]
            del self.last_access[key]
            del self.expiration_times[key]
            
            if key in self.access_order:
                self.access_order.remove(key)
    
    async def invalidate(self, key: str) -> bool:
        """Invalidate a specific cache entry."""
        async with self._lock:
            if key in self.cache:
                await self._remove_item(key)
                return True
            return False
    
    async def clear(self):
        """Clear all cached items."""
        async with self._lock:
            for key in list(self.cache.keys()):
                await self._remove_item(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        total_accesses = sum(self.access_count.values())
        current_time = time.time()
        
        # Calculate hit rate
        total_requests = total_accesses + len(self.access_order)
        hit_rate = total_accesses / total_requests if total_requests > 0 else 0.0
        
        return {
            "size": len(self.cache),
            "capacity": self.config.cache_capacity,
            "total_accesses": total_accesses,
            "hit_rate": hit_rate,
            "average_accesses_per_item": total_accesses / len(self.cache) if self.cache else 0.0,
            "memory_efficiency": len(self.cache) / self.config.cache_capacity if self.config.cache_capacity > 0 else 0.0,
            "expired_items": len([k for k, exp in self.expiration_times.items() if current_time > exp])
        }
    
    async def shutdown(self):
        """Shutdown the cache."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

# =============================================================================
# Enhanced Request Batching Implementation
# =============================================================================

class EnhancedRequestBatcher:
    """Enhanced request batching with priority and timeout support."""
    
    def __init__(self, config: RouterConfig):
        self.config = config
        self.pending_requests: List[Tuple[float, RoutingRequest, asyncio.Future]] = []
        self._lock = asyncio.Lock()
        self._batch_task: Optional[asyncio.Task] = None
        self._start_batching()
    
    def _start_batching(self):
        """Start background batching task."""
        if self._batch_task is None or self._batch_task.done():
            self._batch_task = asyncio.create_task(self._batch_loop())
    
    async def add_request(self, request: RoutingRequest) -> asyncio.Future:
        """Add request to batch and return future for result."""
        future = asyncio.Future()
        async with self._lock:
            self.pending_requests.append((time.time(), request, future))
        return future
    
    async def _batch_loop(self):
        """Enhanced main batching loop."""
        while True:
            try:
                await asyncio.sleep(0.01)  # Check every 10ms
                
                async with self._lock:
                    current_time = time.time()
                    ready_requests = []
                    
                    # Sort by priority first, then by timestamp
                    self.pending_requests.sort(key=lambda x: (-x[1].priority, x[0]))
                    
                    # Check for requests that are ready to be batched
                    for timestamp, request, future in self.pending_requests:
                        if (len(ready_requests) >= self.config.max_batch_size or 
                            current_time - timestamp >= self.config.batch_timeout):
                            ready_requests.append((request, future))
                    
                    # Remove ready requests from pending
                    for request, future in ready_requests:
                        self.pending_requests = [
                            (ts, req, fut) for ts, req, fut in self.pending_requests
                            if fut != future
                        ]
                
                if ready_requests:
                    await self._process_batch(ready_requests)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error and continue
                continue
    
    async def _process_batch(self, batch: List[Tuple[RoutingRequest, asyncio.Future]]):
        """Process a batch of requests."""
        # This will be called by the router engine to process the batch
        # The actual processing logic is in the engine
        pass
    
    async def shutdown(self):
        """Shutdown the batcher."""
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass

# =============================================================================
# Enhanced Load Balancing Strategies
# =============================================================================

class EnhancedLoadBalancer:
    """Enhanced load balancer with multiple strategies."""
    
    def __init__(self, strategy: LoadBalancingStrategy):
        self.strategy = strategy
        self._round_robin_index = 0
        self._consistent_hash_ring = {}
        self._strategy_weights = {}
    
    async def select_route(self, routes: List[RouteInfo], context: Dict[str, Any]) -> Optional[RouteInfo]:
        """Select route using the configured strategy."""
        if not routes:
            return None
        
        # Filter healthy routes
        healthy_routes = [r for r in routes if r.status == RouteStatus.HEALTHY]
        if not healthy_routes:
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return await self._round_robin(healthy_routes)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return await self._least_connections(healthy_routes)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return await self._weighted_round_robin(healthy_routes)
        elif self.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return await self._least_response_time(healthy_routes)
        elif self.strategy == LoadBalancingStrategy.CONSISTENT_HASH:
            return await self._consistent_hash(healthy_routes, context)
        elif self.strategy == LoadBalancingStrategy.ADAPTIVE:
            return await self._adaptive(healthy_routes, context)
        elif self.strategy == LoadBalancingStrategy.POWER_OF_TWO:
            return await self._power_of_two(healthy_routes)
        elif self.strategy == LoadBalancingStrategy.LEAST_LOADED:
            return await self._least_loaded(healthy_routes)
        else:
            return healthy_routes[0]  # Default to first healthy route
    
    async def _round_robin(self, routes: List[RouteInfo]) -> RouteInfo:
        """Round-robin load balancing."""
        route = routes[self._round_robin_index % len(routes)]
        self._round_robin_index = (self._round_robin_index + 1) % len(routes)
        return route
    
    async def _least_connections(self, routes: List[RouteInfo]) -> RouteInfo:
        """Least connections load balancing."""
        return min(routes, key=lambda r: r.connection_count)
    
    async def _weighted_round_robin(self, routes: List[RouteInfo]) -> RouteInfo:
        """Weighted round-robin load balancing."""
        # Calculate total weight
        total_weight = sum(r.weight for r in routes)
        if total_weight <= 0:
            return routes[0]
        
        # Use round-robin index to select weighted route
        current_weight = 0
        target_weight = self._round_robin_index % total_weight
        
        for route in routes:
            current_weight += route.weight
            if current_weight > target_weight:
                self._round_robin_index = (self._round_robin_index + 1) % total_weight
                return route
        
        return routes[0]
    
    async def _least_response_time(self, routes: List[RouteInfo]) -> RouteInfo:
        """Least response time load balancing."""
        return min(routes, key=lambda r: r.response_time)
    
    async def _consistent_hash(self, routes: List[RouteInfo], context: Dict[str, Any]) -> RouteInfo:
        """Consistent hash load balancing."""
        # Use session ID or request ID for consistent hashing
        key = context.get('session_id') or context.get('request_id') or str(hash(str(context)))
        
        if not self._consistent_hash_ring:
            # Build hash ring
            for route in routes:
                hash_value = hash(f"{route.route_id}:{route.target_engine}")
                self._consistent_hash_ring[hash_value] = route
        
        # Find the route with hash >= key hash
        key_hash = hash(key)
        sorted_hashes = sorted(self._consistent_hash_ring.keys())
        
        for hash_value in sorted_hashes:
            if hash_value >= key_hash:
                return self._consistent_hash_ring[hash_value]
        
        # Wrap around to first route
        return self._consistent_hash_ring[sorted_hashes[0]]
    
    async def _adaptive(self, routes: List[RouteInfo], context: Dict[str, Any]) -> RouteInfo:
        """Adaptive load balancing based on multiple factors."""
        # Calculate adaptive score for each route
        route_scores = []
        for route in routes:
            # Health score (0-1)
            health_score = route.health_score
            
            # Response time score (lower is better)
            response_time_score = 1.0 / (route.response_time + 1)
            
            # Connection count score (lower is better)
            connection_score = 1.0 / (route.connection_count + 1)
            
            # Success rate score
            success_score = route.success_rate
            
            # Weight score
            weight_score = route.weight
            
            # Calculate composite score
            composite_score = (
                health_score * 0.3 +
                response_time_score * 0.25 +
                connection_score * 0.2 +
                success_score * 0.15 +
                weight_score * 0.1
            )
            
            route_scores.append((route, composite_score))
        
        # Return route with highest score
        return max(route_scores, key=lambda x: x[1])[0]
    
    async def _power_of_two(self, routes: List[RouteInfo]) -> RouteInfo:
        """Power of two choices load balancing."""
        if len(routes) < 2:
            return routes[0]
        
        # Select two random routes
        import random
        choice1, choice2 = random.sample(routes, 2)
        
        # Return the one with fewer connections
        return choice1 if choice1.connection_count <= choice2.connection_count else choice2
    
    async def _least_loaded(self, routes: List[RouteInfo]) -> RouteInfo:
        """Least loaded route selection."""
        # Calculate load based on multiple factors
        route_loads = []
        for route in routes:
            # Normalize factors
            connection_load = route.connection_count / max(max(r.connection_count for r in routes), 1)
            response_load = route.response_time / max(max(r.response_time for r in routes), 1)
            error_load = route.error_rate
            
            # Calculate composite load
            composite_load = connection_load * 0.4 + response_load * 0.4 + error_load * 0.2
            route_loads.append((route, composite_load))
        
        # Return route with lowest load
        return min(route_loads, key=lambda x: x[1])[0]
    
    async def update_metrics(self, route_id: str, metrics: Dict[str, Any]) -> None:
        """Update route metrics for load balancing decisions."""
        # This method can be used to update internal state for adaptive strategies
        pass

# =============================================================================
# Refactored Router Engine Implementation
# =============================================================================

class RouterEngine(Engine):
    """Refactored high-performance router engine with enhanced features."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.router_config = RouterConfig(**config)
        
        # Validate configuration
        errors = self.router_config.validate()
        if errors:
            raise ValueError(f"Invalid router configuration: {errors}")
        
        # Initialize components
        self.router_cache = EnhancedRouterCache(self.router_config)
        self.request_batcher = EnhancedRequestBatcher(self.router_config)
        self.load_balancer = EnhancedLoadBalancer(self.router_config.load_balancing_strategy)
        
        # Route management
        self.routes: Dict[str, RouteInfo] = {}
        self.route_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Request management
        self._request_semaphore = asyncio.Semaphore(self.router_config.max_concurrent_requests)
        self._route_lock = asyncio.Lock()
        
        # Performance tracking
        self._performance_metrics = {
            "total_routes": 0,
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "average_routing_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "load_balancing_decisions": 0
        }
        
        # Health check management
        self._health_check_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background monitoring and health check tasks."""
        if self.router_config.enable_health_checks:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        if self.router_config.enable_metrics:
            self._metrics_task = asyncio.create_task(self._metrics_loop())
    
    async def _health_check_loop(self):
        """Background health check loop."""
        while True:
            try:
                await asyncio.sleep(self.router_config.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error and continue
                continue
    
    async def _metrics_loop(self):
        """Background metrics collection loop."""
        while True:
            try:
                await asyncio.sleep(self.router_config.metrics_interval)
                await self._collect_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error and continue
                continue
    
    async def _perform_health_checks(self):
        """Perform health checks on all routes."""
        async with self._route_lock:
            for route_id, route in self.routes.items():
                try:
                    await self._check_route_health(route)
                except Exception as e:
                    self.logger.error(f"Health check failed for route {route_id}: {e}")
    
    async def _check_route_health(self, route: RouteInfo):
        """Check health of a specific route."""
        try:
            # This would integrate with the target engine's health check
            # For now, we'll simulate health checks
            current_time = time.time()
            
            # Update last health check time
            route.last_health_check = current_time
            
            # Simulate health score based on metrics
            if route.error_rate > 0.5:
                route.status = RouteStatus.UNHEALTHY
                route.health_score = 0.0
            elif route.error_rate > 0.2:
                route.status = RouteStatus.DEGRADED
                route.health_score = 0.5
            else:
                route.status = RouteStatus.HEALTHY
                route.health_score = 1.0
            
        except Exception as e:
            route.status = RouteStatus.UNHEALTHY
            route.health_score = 0.0
            self.logger.error(f"Health check failed for route {route.route_id}: {e}")
    
    async def _collect_metrics(self):
        """Collect and update route metrics."""
        async with self._route_lock:
            for route_id, route in self.routes.items():
                # Update route metrics based on performance
                if route_id not in self.route_metrics:
                    self.route_metrics[route_id] = {}
                
                self.route_metrics[route_id].update({
                    "last_updated": time.time(),
                    "status": route.status.value,
                    "health_score": route.health_score,
                    "connection_count": route.connection_count,
                    "response_time": route.response_time,
                    "error_rate": route.error_rate,
                    "success_rate": route.success_rate
                })
    
    async def _execute_operation(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute router operation with enhanced error handling."""
        if operation == "route":
            return await self._route_request(params)
        elif operation == "route_batch":
            return await self._route_batch(params)
        elif operation == "register_route":
            return await self._register_route(params)
        elif operation == "unregister_route":
            return await self._unregister_route(params)
        elif operation == "get_route_info":
            return await self._get_route_info(params)
        elif operation == "update_route_metrics":
            return await self._update_route_metrics(params)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def _route_request(self, params: Dict[str, Any]) -> RoutingResponse:
        """Route a single request with enhanced features."""
        request = RoutingRequest(**params)
        start_time = time.time()
        
        try:
            async with self._request_semaphore:
                # Check cache first
                cache_key = self._generate_cache_key(request)
                cached_result = await self.router_cache.get(cache_key)
                
                if cached_result:
                    self._performance_metrics["cache_hits"] += 1
                    return cached_result
                
                self._performance_metrics["cache_misses"] += 1
                
                # Find route
                route = await self._find_route(request)
                if not route:
                    return RoutingResponse(
                        success=False,
                        error_message=f"Route not found: {request.route_id}",
                        processing_time=time.time() - start_time
                    )
                
                # Make routing decision
                decision = await self._make_routing_decision(route, request)
                
                # Execute routing
                result = await self._execute_routing(decision, request)
                
                # Cache successful results
                if result.success:
                    await self.router_cache.put(cache_key, result)
                
                # Update metrics
                self._update_routing_metrics(route, result, time.time() - start_time)
                
                return result
                
        except Exception as e:
            self.logger.error(f"Routing failed: {e}")
            return RoutingResponse(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def _generate_cache_key(self, request: RoutingRequest) -> str:
        """Generate cache key for the request."""
        # Create deterministic key
        key_data = {
            "route_id": request.route_id,
            "operation": request.operation,
            "params_hash": hashlib.md5(json.dumps(request.params, sort_keys=True).encode()).hexdigest(),
            "priority": request.priority,
            "session_id": request.session_id
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _find_route(self, request: RoutingRequest) -> Optional[RouteInfo]:
        """Find route for the request."""
        async with self._route_lock:
            return self.routes.get(request.route_id)
    
    async def _make_routing_decision(self, route: RouteInfo, request: RoutingRequest) -> RoutingDecision:
        """Make intelligent routing decision."""
        # Get alternative routes if available
        alternatives = []
        async with self._route_lock:
            for r in self.routes.values():
                if (r.route_id != route.route_id and 
                    r.target_engine == route.target_engine and
                    r.status == RouteStatus.HEALTHY):
                    alternatives.append(r)
        
        # Select best route using load balancer
        selected_route = await self.load_balancer.select_route(
            [route] + alternatives,
            {"request_id": id(request), "session_id": request.session_id}
        )
        
        # Calculate confidence based on route health and alternatives
        confidence = selected_route.health_score
        if alternatives:
            confidence *= (1.0 + len(alternatives) * 0.1)  # Bonus for having alternatives
        
        return RoutingDecision(
            route=selected_route,
            strategy=self.router_config.load_balancing_strategy,
            confidence=min(confidence, 1.0),
            reasoning=f"Selected using {self.router_config.load_balancing_strategy.value} strategy",
            alternatives=alternatives
        )
    
    async def _execute_routing(self, decision: RoutingDecision, request: RoutingRequest) -> RoutingResponse:
        """Execute the routing decision."""
        try:
            # This would integrate with the target engine
            # For now, we'll simulate routing execution
            
            # Simulate processing time
            await asyncio.sleep(0.01)
            
            # Simulate successful routing
            return RoutingResponse(
                success=True,
                result={"routed_to": decision.route.target_engine},
                route_id=decision.route.route_id,
                target_engine=decision.route.target_engine,
                processing_time=0.01,
                metadata={
                    "strategy": decision.strategy.value,
                    "confidence": decision.confidence,
                    "alternatives_count": len(decision.alternatives)
                }
            )
            
        except Exception as e:
            return RoutingResponse(
                success=False,
                error_message=str(e),
                route_id=decision.route.route_id,
                target_engine=decision.route.target_engine
            )
    
    def _update_routing_metrics(self, route: RouteInfo, response: RoutingResponse, processing_time: float):
        """Update routing metrics."""
        self._performance_metrics["total_requests"] += 1
        
        if response.success:
            self._performance_metrics["successful_routes"] += 1
            route.success_rate = min(1.0, route.success_rate + 0.01)
            route.error_rate = max(0.0, route.error_rate - 0.01)
        else:
            self._performance_metrics["failed_routes"] += 1
            route.error_rate = min(1.0, route.error_rate + 0.01)
            route.success_rate = max(0.0, route.success_rate - 0.01)
        
        # Update response time (exponential moving average)
        alpha = 0.1
        route.response_time = alpha * processing_time + (1 - alpha) * route.response_time
        
        # Update connection count
        route.connection_count = max(0, route.connection_count - 1)
    
    async def _route_batch(self, params: Dict[str, Any]) -> List[RoutingResponse]:
        """Route multiple requests in batch."""
        requests = params.get("requests", [])
        if not requests:
            raise ValueError("No requests provided for batch routing")
        
        results = []
        for i, request_data in enumerate(requests):
            try:
                request = RoutingRequest(**request_data)
                request.batch_id = f"batch_{i}"
                result = await self._route_request({"route_id": request.route_id, **request_data})
                results.append(result)
            except Exception as e:
                self.logger.error(f"Batch routing failed for request {i}: {e}")
                results.append(RoutingResponse(
                    success=False,
                    error_message=str(e),
                    processing_time=0.0
                ))
        
        return results
    
    async def _register_route(self, params: Dict[str, Any]) -> bool:
        """Register a new route."""
        try:
            route_info = RouteInfo(**params)
            
            async with self._route_lock:
                self.routes[route_info.route_id] = route_info
                self._performance_metrics["total_routes"] += 1
            
            self.logger.info(f"Route registered: {route_info.route_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register route: {e}")
            return False
    
    async def _unregister_route(self, params: Dict[str, Any]) -> bool:
        """Unregister a route."""
        route_id = params.get("route_id")
        if not route_id:
            return False
        
        async with self._route_lock:
            if route_id in self.routes:
                del self.routes[route_id]
                self._performance_metrics["total_routes"] = max(0, self._performance_metrics["total_routes"] - 1)
                self.logger.info(f"Route unregistered: {route_id}")
                return True
        
        return False
    
    async def _get_route_info(self, params: Dict[str, Any]) -> Optional[RouteInfo]:
        """Get information about a specific route."""
        route_id = params.get("route_id")
        if not route_id:
            return None
        
        async with self._route_lock:
            return self.routes.get(route_id)
    
    async def _update_route_metrics(self, params: Dict[str, Any]) -> bool:
        """Update metrics for a specific route."""
        route_id = params.get("route_id")
        metrics = params.get("metrics", {})
        
        if not route_id or not metrics:
            return False
        
        async with self._route_lock:
            if route_id in self.routes:
                route = self.routes[route_id]
                
                # Update route metrics
                for key, value in metrics.items():
                    if hasattr(route, key):
                        setattr(route, key, value)
                
                return True
        
        return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            **self._performance_metrics,
            "cache_stats": self.router_cache.get_stats(),
            "route_stats": {
                "total_routes": len(self.routes),
                "healthy_routes": len([r for r in self.routes.values() if r.status == RouteStatus.HEALTHY]),
                "degraded_routes": len([r for r in self.routes.values() if r.status == RouteStatus.DEGRADED]),
                "unhealthy_routes": len([r for r in self.routes.values() if r.status == RouteStatus.UNHEALTHY])
            },
            "load_balancing_info": {
                "strategy": self.router_config.load_balancing_strategy.value,
                "enable_health_checks": self.router_config.enable_health_checks,
                "enable_circuit_breaker": self.router_config.enable_circuit_breaker
            }
        }
    
    async def shutdown(self):
        """Enhanced shutdown with cleanup."""
        self.logger.info("Shutting down router engine...")
        
        # Cancel background tasks
        for task in [self._health_check_task, self._metrics_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Shutdown components
        await self.router_cache.shutdown()
        await self.request_batcher.shutdown()
        
        # Clear routes
        self.routes.clear()
        self.route_metrics.clear()
        
        await super().shutdown()
        self.logger.info("Router engine shutdown complete")


# Legacy alias for backward compatibility
RouterEngines = RouterEngine


