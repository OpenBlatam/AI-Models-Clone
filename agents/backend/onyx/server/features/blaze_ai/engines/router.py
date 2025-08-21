"""
Router Engine for request routing and load balancing.

This module provides intelligent request routing, load balancing,
and request distribution across multiple engines.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, Optional, List
from collections import defaultdict

from . import Engine
from ..core.interfaces import HealthStatus
from ..utils.cache import LRUCache
from ..utils.logging import get_logger
from ..utils.metrics import Timer


class RouterEngine(Engine):
    """
    Router Engine for intelligent request routing and load balancing.
    
    Features:
    - Request routing based on content type and load
    - Load balancing across multiple engines
    - Request caching and optimization
    - Health-based routing decisions
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.logger = get_logger(f"engine.{name}")
        
        # Configuration
        self.enable_caching = config.get("enable_caching", True)
        self.cache_ttl = config.get("cache_ttl", 1800)
        self.max_concurrent_requests = config.get("max_concurrent_requests", 50)
        self.load_balancing_strategy = config.get("load_balancing_strategy", "round_robin")
        
        # Initialize components
        self._cache: Optional[LRUCache] = None
        self._engine_loads: Dict[str, int] = defaultdict(int)
        self._request_counts: Dict[str, int] = defaultdict(int)
        self._current_engine_index = 0
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_routing_time = 0.0
        
    async def _execute_operation(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute router operations."""
        if operation == "route":
            return await self._route_request(params)
        elif operation == "health_check":
            return await self._health_check()
        elif operation == "get_stats":
            return await self._get_stats()
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def _route_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate engine."""
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # Extract routing parameters
            request_type = params.get("request_type", "text")
            content = params.get("content", "")
            priority = params.get("priority", 0)
            
            # Check cache first
            if self.enable_caching and self._cache:
                cache_key = self._make_cache_key(request_type, content, priority)
                cached_result = self._cache.get(cache_key)
                if cached_result:
                    self.successful_requests += 1
                    return {
                        "success": True,
                        "result": cached_result,
                        "cached": True,
                        "routing_time": time.time() - start_time
                    }
            
            # Determine target engine
            target_engine = self._select_engine(request_type, priority)
            
            # Route request
            with Timer() as timer:
                result = await self._forward_to_engine(target_engine, params)
            
            routing_time = timer.elapsed
            self.total_routing_time += routing_time
            
            # Cache result if successful
            if result.get("success") and self.enable_caching and self._cache:
                cache_key = self._make_cache_key(request_type, content, priority)
                self._cache.set(cache_key, result, ttl=self.cache_ttl)
            
            # Update load statistics
            self._engine_loads[target_engine] += 1
            self._request_counts[target_engine] += 1
            
            self.successful_requests += 1
            return {
                "success": True,
                "result": result,
                "target_engine": target_engine,
                "routing_time": routing_time
            }
            
        except Exception as e:
            self.failed_requests += 1
            self.logger.error(f"Request routing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "routing_time": time.time() - start_time
            }
    
    def _select_engine(self, request_type: str, priority: int) -> str:
        """Select appropriate engine based on request type and load."""
        available_engines = self._get_available_engines(request_type)
        
        if not available_engines:
            raise ValueError(f"No available engines for request type: {request_type}")
        
        if self.load_balancing_strategy == "round_robin":
            return self._round_robin_select(available_engines)
        elif self.load_balancing_strategy == "least_loaded":
            return self._least_loaded_select(available_engines)
        elif self.load_balancing_strategy == "priority_based":
            return self._priority_based_select(available_engines, priority)
        else:
            return available_engines[0]  # Default to first available
    
    def _get_available_engines(self, request_type: str) -> List[str]:
        """Get list of available engines for request type."""
        # This would typically check engine health and availability
        # For now, return a simple mapping
        engine_mapping = {
            "text": ["llm_engine"],
            "image": ["diffusion_engine"],
            "seo": ["seo_service"],
            "brand": ["brand_service"],
            "content": ["generation_service"]
        }
        return engine_mapping.get(request_type, ["llm_engine"])
    
    def _round_robin_select(self, engines: List[str]) -> str:
        """Round-robin engine selection."""
        if not engines:
            raise ValueError("No engines available")
        
        engine = engines[self._current_engine_index % len(engines)]
        self._current_engine_index += 1
        return engine
    
    def _least_loaded_select(self, engines: List[str]) -> str:
        """Select engine with least load."""
        if not engines:
            raise ValueError("No engines available")
        
        return min(engines, key=lambda e: self._engine_loads.get(e, 0))
    
    def _priority_based_select(self, engines: List[str], priority: int) -> str:
        """Select engine based on priority and load."""
        if not engines:
            raise ValueError("No engines available")
        
        # For high priority requests, prefer less loaded engines
        if priority > 5:
            return self._least_loaded_select(engines)
        else:
            return self._round_robin_select(engines)
    
    async def _forward_to_engine(self, engine_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Forward request to specific engine."""
        # This would typically use the engine manager to dispatch
        # For now, return a mock response
        return {
            "success": True,
            "engine": engine_name,
            "processed": True
        }
    
    def _make_cache_key(self, request_type: str, content: str, priority: int) -> str:
        """Create cache key for request."""
        import hashlib
        key_data = f"{request_type}:{content}:{priority}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform health check on router engine."""
        try:
            # Calculate success rate
            success_rate = (self.successful_requests / self.total_requests) if self.total_requests > 0 else 1.0
            
            # Calculate average routing time
            avg_routing_time = (self.total_routing_time / self.successful_requests) if self.successful_requests > 0 else 0.0
            
            return {
                "status": "healthy" if success_rate > 0.8 else "degraded",
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": success_rate,
                "avg_routing_time": avg_routing_time,
                "engine_loads": dict(self._engine_loads),
                "cache_size": len(self._cache) if self._cache else 0
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def _get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        return {
            "load_balancing_strategy": self.load_balancing_strategy,
            "engine_loads": dict(self._engine_loads),
            "request_counts": dict(self._request_counts),
            "cache_stats": self._cache.get_stats() if self._cache else {}
        }
    
    def get_health_status(self) -> HealthStatus:
        """Get health status for the engine."""
        health_info = asyncio.run(self._health_check())
        
        return HealthStatus(
            component=self.name,
            status=health_info.get("status", "unknown"),
            message=f"Router Engine: {health_info.get('total_requests', 0)} requests routed",
            timestamp=time.time(),
            details=health_info
        )
    
    async def shutdown(self) -> None:
        """Shutdown the router engine."""
        self.logger.info("Shutting down router engine")
        
        # Clear cache
        if self._cache:
            self._cache.clear()
        
        # Reset statistics
        self._engine_loads.clear()
        self._request_counts.clear()
        self._current_engine_index = 0
        
        self.logger.info("Router engine shutdown complete")


# Legacy alias for backward compatibility
RouterEngines = RouterEngine


