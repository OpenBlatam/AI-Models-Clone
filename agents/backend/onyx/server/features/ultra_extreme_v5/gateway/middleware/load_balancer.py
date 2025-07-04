"""
🚀 ULTRA-EXTREME V5 - LOAD BALANCER MIDDLEWARE
=============================================

Ultra-extreme load balancer middleware with:
- Multiple load balancing strategies
- Health checking
- Intelligent routing
- Service discovery integration
- Performance monitoring
- Adaptive load balancing
"""

import time
import asyncio
import random
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from collections import defaultdict, deque
import statistics

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import structlog
import httpx

from ..config.settings import get_settings
from ..config.service_discovery import ServiceDiscovery


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    ADAPTIVE = "adaptive"


class LoadBalancerMiddleware(BaseHTTPMiddleware):
    """Ultra-extreme load balancer middleware"""
    
    def __init__(self, app, service_discovery: ServiceDiscovery):
        super().__init__(app)
        self.settings = get_settings()
        self.logger = structlog.get_logger(__name__)
        self.service_discovery = service_discovery
        
        # Load balancer configuration
        self.strategy = LoadBalancingStrategy(self.settings.LOAD_BALANCER_STRATEGY)
        self.health_check_enabled = self.settings.LOAD_BALANCER_HEALTH_CHECK_ENABLED
        
        # Service tracking
        self.service_instances = defaultdict(list)
        self.service_weights = defaultdict(lambda: 1.0)
        self.service_connections = defaultdict(int)
        self.service_response_times = defaultdict(lambda: deque(maxlen=100))
        self.service_health_status = defaultdict(lambda: {"healthy": True, "last_check": 0})
        
        # Round robin counters
        self.round_robin_counters = defaultdict(int)
        
        # Performance metrics
        self.performance_metrics = defaultdict(lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "min_response_time": float('inf'),
            "max_response_time": 0.0,
            "response_times": deque(maxlen=1000),
            "error_rates": deque(maxlen=100),
            "throughput": deque(maxlen=60)  # 1 minute window
        })
        
        # Adaptive load balancing
        self.adaptive_enabled = True
        self.adaptive_threshold = 0.8
        self.adaptive_weights = defaultdict(lambda: 1.0)
        
        # Health check configuration
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5  # seconds
        self.health_check_path = "/health"
        self.unhealthy_threshold = 3
        self.healthy_threshold = 2
        
        # Start health checking
        if self.health_check_enabled:
            asyncio.create_task(self._health_check_loop())
    
    async def dispatch(self, request: Request, call_next):
        """Process the request through load balancer middleware"""
        start_time = time.time()
        
        try:
            # Skip load balancing for certain paths
            if self._should_skip_load_balancing(request.url.path):
                return await call_next(request)
            
            # Get target service
            target_service = self._get_target_service(request)
            if not target_service:
                return await call_next(request)
            
            # Get available instances
            instances = await self._get_available_instances(target_service)
            if not instances:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"No available instances for service: {target_service}"
                )
            
            # Select instance using load balancing strategy
            selected_instance = await self._select_instance(target_service, instances, request)
            if not selected_instance:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No suitable instance available"
                )
            
            # Update connection count
            self.service_connections[selected_instance["id"]] += 1
            
            # Forward request to selected instance
            try:
                response = await self._forward_request(request, selected_instance)
                
                # Record success
                response_time = time.time() - start_time
                await self._record_success(target_service, selected_instance, response_time)
                
                return response
                
            except Exception as e:
                # Record failure
                response_time = time.time() - start_time
                await self._record_failure(target_service, selected_instance, e, response_time)
                raise
                
            finally:
                # Decrease connection count
                self.service_connections[selected_instance["id"]] = max(0, self.service_connections[selected_instance["id"]] - 1)
                
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error("Load balancer error", error=str(e), exc_info=True)
            # Continue without load balancing on error
            return await call_next(request)
    
    def _should_skip_load_balancing(self, path: str) -> bool:
        """Check if load balancing should be skipped for this path"""
        skip_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def _get_target_service(self, request: Request) -> Optional[str]:
        """Get target service from request"""
        # Check header first
        target_service = request.headers.get("X-Target-Service")
        if target_service:
            return target_service
        
        # Check path
        path_parts = request.url.path.split('/')
        if len(path_parts) > 1:
            return path_parts[1]
        
        return None
    
    async def _get_available_instances(self, service_name: str) -> List[Dict[str, Any]]:
        """Get available instances for service"""
        try:
            # Get instances from service discovery
            instances = await self.service_discovery.get_service_instances(service_name)
            
            # Filter healthy instances
            healthy_instances = []
            for instance in instances:
                instance_id = instance.get("id", f"{service_name}-{instance.get('host', 'unknown')}")
                health_status = self.service_health_status[instance_id]
                
                if health_status["healthy"]:
                    healthy_instances.append({
                        "id": instance_id,
                        "host": instance.get("host"),
                        "port": instance.get("port"),
                        "url": instance.get("url"),
                        "weight": self.service_weights[instance_id],
                        "connections": self.service_connections[instance_id],
                        "response_time": self._get_average_response_time(instance_id),
                        "metadata": instance.get("metadata", {})
                    })
            
            return healthy_instances
            
        except Exception as e:
            self.logger.error("Error getting service instances", error=str(e))
            return []
    
    async def _select_instance(self, service_name: str, instances: List[Dict[str, Any]], request: Request) -> Optional[Dict[str, Any]]:
        """Select instance using load balancing strategy"""
        if not instances:
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(service_name, instances)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(instances)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(service_name, instances)
        elif self.strategy == LoadBalancingStrategy.IP_HASH:
            return self._ip_hash_selection(instances, request)
        elif self.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time_selection(instances)
        elif self.strategy == LoadBalancingStrategy.ADAPTIVE:
            return self._adaptive_selection(service_name, instances)
        else:
            # Default to round robin
            return self._round_robin_selection(service_name, instances)
    
    def _round_robin_selection(self, service_name: str, instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Round robin selection"""
        counter = self.round_robin_counters[service_name]
        selected_instance = instances[counter % len(instances)]
        self.round_robin_counters[service_name] = counter + 1
        return selected_instance
    
    def _least_connections_selection(self, instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Least connections selection"""
        return min(instances, key=lambda x: x["connections"])
    
    def _weighted_round_robin_selection(self, service_name: str, instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Weighted round robin selection"""
        # Calculate total weight
        total_weight = sum(instance["weight"] for instance in instances)
        if total_weight == 0:
            return instances[0]
        
        # Get current counter
        counter = self.round_robin_counters[service_name]
        
        # Find instance based on weight
        current_weight = 0
        for instance in instances:
            current_weight += instance["weight"]
            if counter < current_weight:
                self.round_robin_counters[service_name] = counter + 1
                return instance
        
        # Fallback
        self.round_robin_counters[service_name] = counter + 1
        return instances[0]
    
    def _ip_hash_selection(self, instances: List[Dict[str, Any]], request: Request) -> Dict[str, Any]:
        """IP hash selection"""
        client_ip = self._get_client_ip(request)
        hash_value = hash(client_ip) % len(instances)
        return instances[hash_value]
    
    def _least_response_time_selection(self, instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Least response time selection"""
        return min(instances, key=lambda x: x["response_time"] or float('inf'))
    
    def _adaptive_selection(self, service_name: str, instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Adaptive selection based on performance"""
        if not self.adaptive_enabled:
            return self._round_robin_selection(service_name, instances)
        
        # Calculate adaptive weights based on performance
        adaptive_instances = []
        for instance in instances:
            instance_id = instance["id"]
            performance = self.performance_metrics[instance_id]
            
            # Calculate adaptive weight based on response time and error rate
            avg_response_time = performance["average_response_time"] or 1.0
            error_rate = performance["failed_requests"] / max(performance["total_requests"], 1)
            
            # Invert response time and error rate for weight calculation
            response_weight = 1.0 / max(avg_response_time, 0.1)
            error_weight = 1.0 - min(error_rate, 0.9)
            
            adaptive_weight = response_weight * error_weight
            adaptive_instances.append({
                **instance,
                "adaptive_weight": adaptive_weight
            })
        
        # Select instance with highest adaptive weight
        return max(adaptive_instances, key=lambda x: x["adaptive_weight"])
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    def _get_average_response_time(self, instance_id: str) -> float:
        """Get average response time for instance"""
        response_times = self.service_response_times[instance_id]
        if not response_times:
            return 0.0
        return sum(response_times) / len(response_times)
    
    async def _forward_request(self, request: Request, instance: Dict[str, Any]) -> Response:
        """Forward request to selected instance"""
        # Build target URL
        target_url = f"{instance['url']}{request.url.path}"
        if request.url.query:
            target_url += f"?{request.url.query}"
        
        # Prepare headers
        headers = dict(request.headers)
        headers.pop("host", None)  # Remove host header
        
        # Prepare request body
        body = await request.body()
        
        # Make request to target instance
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            
            # Create response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )
    
    async def _record_success(self, service_name: str, instance: Dict[str, Any], response_time: float):
        """Record successful request"""
        instance_id = instance["id"]
        
        # Update response times
        self.service_response_times[instance_id].append(response_time)
        
        # Update performance metrics
        metrics = self.performance_metrics[instance_id]
        metrics["total_requests"] += 1
        metrics["successful_requests"] += 1
        metrics["response_times"].append(response_time)
        metrics["average_response_time"] = sum(metrics["response_times"]) / len(metrics["response_times"])
        metrics["min_response_time"] = min(metrics["min_response_time"], response_time)
        metrics["max_response_time"] = max(metrics["max_response_time"], response_time)
        
        # Update error rate
        error_rate = metrics["failed_requests"] / metrics["total_requests"]
        metrics["error_rates"].append(error_rate)
        
        # Update throughput
        current_time = time.time()
        metrics["throughput"].append(current_time)
        
        # Clean old throughput data
        cutoff_time = current_time - 60  # 1 minute window
        metrics["throughput"] = deque(
            [t for t in metrics["throughput"] if t > cutoff_time],
            maxlen=60
        )
    
    async def _record_failure(self, service_name: str, instance: Dict[str, Any], error: Exception, response_time: float):
        """Record failed request"""
        instance_id = instance["id"]
        
        # Update response times
        self.service_response_times[instance_id].append(response_time)
        
        # Update performance metrics
        metrics = self.performance_metrics[instance_id]
        metrics["total_requests"] += 1
        metrics["failed_requests"] += 1
        metrics["response_times"].append(response_time)
        metrics["average_response_time"] = sum(metrics["response_times"]) / len(metrics["response_times"])
        metrics["min_response_time"] = min(metrics["min_response_time"], response_time)
        metrics["max_response_time"] = max(metrics["max_response_time"], response_time)
        
        # Update error rate
        error_rate = metrics["failed_requests"] / metrics["total_requests"]
        metrics["error_rates"].append(error_rate)
        
        self.logger.warning(
            "Request failed",
            service_name=service_name,
            instance_id=instance_id,
            error=str(error)
        )
    
    async def _health_check_loop(self):
        """Health check loop"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                self.logger.error("Health check error", error=str(e))
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _perform_health_checks(self):
        """Perform health checks on all instances"""
        for service_name in self.service_instances:
            instances = await self.service_discovery.get_service_instances(service_name)
            
            for instance in instances:
                instance_id = instance.get("id", f"{service_name}-{instance.get('host', 'unknown')}")
                await self._check_instance_health(instance_id, instance)
    
    async def _check_instance_health(self, instance_id: str, instance: Dict[str, Any]):
        """Check health of specific instance"""
        try:
            health_url = f"{instance['url']}{self.health_check_path}"
            
            async with httpx.AsyncClient(timeout=self.health_check_timeout) as client:
                response = await client.get(health_url)
                
                is_healthy = response.status_code == 200
                current_status = self.service_health_status[instance_id]
                
                if is_healthy:
                    if not current_status["healthy"]:
                        # Instance recovered
                        current_status["healthy"] = True
                        self.logger.info("Instance recovered", instance_id=instance_id)
                else:
                    if current_status["healthy"]:
                        # Instance became unhealthy
                        current_status["healthy"] = False
                        self.logger.warning("Instance became unhealthy", instance_id=instance_id)
                
                current_status["last_check"] = time.time()
                
        except Exception as e:
            # Instance is unhealthy
            current_status = self.service_health_status[instance_id]
            if current_status["healthy"]:
                current_status["healthy"] = False
                self.logger.warning("Instance health check failed", instance_id=instance_id, error=str(e))
            
            current_status["last_check"] = time.time()
    
    def set_strategy(self, strategy: LoadBalancingStrategy):
        """Set load balancing strategy"""
        self.strategy = strategy
        self.logger.info("Load balancing strategy changed", strategy=strategy.value)
    
    def enable_adaptive_balancing(self, enabled: bool = True):
        """Enable or disable adaptive load balancing"""
        self.adaptive_enabled = enabled
        self.logger.info("Adaptive load balancing", enabled=enabled)
    
    def set_instance_weight(self, instance_id: str, weight: float):
        """Set weight for instance"""
        self.service_weights[instance_id] = max(0.1, weight)
        self.logger.info("Instance weight set", instance_id=instance_id, weight=weight)
    
    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        stats = {
            "strategy": self.strategy.value,
            "adaptive_enabled": self.adaptive_enabled,
            "health_check_enabled": self.health_check_enabled,
            "total_instances": len(self.service_instances),
            "healthy_instances": sum(1 for status in self.service_health_status.values() if status["healthy"]),
            "unhealthy_instances": sum(1 for status in self.service_health_status.values() if not status["healthy"]),
            "instances": {}
        }
        
        for instance_id, metrics in self.performance_metrics.items():
            stats["instances"][instance_id] = {
                "total_requests": metrics["total_requests"],
                "successful_requests": metrics["successful_requests"],
                "failed_requests": metrics["failed_requests"],
                "success_rate": metrics["successful_requests"] / max(metrics["total_requests"], 1),
                "average_response_time": metrics["average_response_time"],
                "min_response_time": metrics["min_response_time"] if metrics["min_response_time"] != float('inf') else 0,
                "max_response_time": metrics["max_response_time"],
                "current_connections": self.service_connections[instance_id],
                "weight": self.service_weights[instance_id],
                "healthy": self.service_health_status[instance_id]["healthy"]
            }
        
        return stats
    
    def reset_stats(self):
        """Reset all statistics"""
        self.performance_metrics.clear()
        self.service_response_times.clear()
        self.round_robin_counters.clear()
        self.logger.info("Load balancer statistics reset") 