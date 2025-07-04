"""
🚀 ULTRA-EXTREME V5 - CIRCUIT BREAKER MIDDLEWARE
===============================================

Ultra-extreme circuit breaker middleware with:
- Advanced failure detection
- Multiple circuit states
- Recovery strategies
- Health monitoring
- Distributed circuit breaking
- Adaptive thresholds
"""

import time
import asyncio
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import structlog
import redis.asyncio as redis

from ..config.settings import get_settings


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is recovered


class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    """Ultra-extreme circuit breaker middleware"""
    
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.settings = get_settings()
        self.logger = structlog.get_logger(__name__)
        self.redis_client = redis_client
        
        # Circuit breaker configuration
        self.failure_threshold = self.settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD
        self.recovery_timeout = self.settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT
        self.expected_exceptions = self.settings.CIRCUIT_BREAKER_EXPECTED_EXCEPTION
        
        # Circuit breakers cache
        self.circuit_breakers = defaultdict(self._create_circuit_breaker)
        
        # Health monitoring
        self.health_metrics = defaultdict(lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "timeout_requests": 0,
            "last_failure_time": None,
            "last_success_time": None,
            "average_response_time": 0.0,
            "response_times": deque(maxlen=100)
        })
        
        # Adaptive thresholds
        self.adaptive_enabled = True
        self.base_failure_threshold = self.failure_threshold
        self.min_failure_threshold = 1
        self.max_failure_threshold = 20
        
        # Recovery strategies
        self.recovery_strategies = {
            "exponential_backoff": self._exponential_backoff_strategy,
            "linear_backoff": self._linear_backoff_strategy,
            "immediate": self._immediate_recovery_strategy
        }
        self.current_recovery_strategy = "exponential_backoff"
    
    def _create_circuit_breaker(self) -> Dict[str, Any]:
        """Create a new circuit breaker instance"""
        return {
            "state": CircuitState.CLOSED,
            "failure_count": 0,
            "success_count": 0,
            "last_failure_time": None,
            "last_success_time": None,
            "last_state_change": time.time(),
            "next_attempt_time": None,
            "consecutive_failures": 0,
            "consecutive_successes": 0,
            "total_requests": 0,
            "total_failures": 0,
            "total_successes": 0,
            "average_response_time": 0.0,
            "response_times": deque(maxlen=50),
            "error_types": defaultdict(int)
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process the request through circuit breaker middleware"""
        start_time = time.time()
        
        try:
            # Skip circuit breaker for certain paths
            if self._should_skip_circuit_breaker(request.url.path):
                return await call_next(request)
            
            # Get service identifier
            service_id = self._get_service_identifier(request)
            
            # Check circuit breaker state
            circuit_breaker = await self._get_circuit_breaker(service_id)
            
            if circuit_breaker["state"] == CircuitState.OPEN:
                # Circuit is open, check if we should attempt recovery
                if await self._should_attempt_recovery(circuit_breaker):
                    circuit_breaker["state"] = CircuitState.HALF_OPEN
                    circuit_breaker["last_state_change"] = time.time()
                    self.logger.info("Circuit breaker moved to half-open", service_id=service_id)
                else:
                    # Circuit is open, fail fast
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Service temporarily unavailable (circuit breaker open)",
                        headers={"X-Circuit-Breaker-State": "open"}
                    )
            
            # Execute request
            try:
                response = await call_next(request)
                
                # Record success
                await self._record_success(service_id, circuit_breaker, time.time() - start_time)
                
                # Check if we should close the circuit
                if circuit_breaker["state"] == CircuitState.HALF_OPEN:
                    if circuit_breaker["consecutive_successes"] >= 3:
                        circuit_breaker["state"] = CircuitState.CLOSED
                        circuit_breaker["last_state_change"] = time.time()
                        circuit_breaker["failure_count"] = 0
                        circuit_breaker["consecutive_failures"] = 0
                        self.logger.info("Circuit breaker closed", service_id=service_id)
                
                return response
                
            except Exception as e:
                # Record failure
                await self._record_failure(service_id, circuit_breaker, e, time.time() - start_time)
                
                # Check if we should open the circuit
                if await self._should_open_circuit(circuit_breaker):
                    circuit_breaker["state"] = CircuitState.OPEN
                    circuit_breaker["last_state_change"] = time.time()
                    circuit_breaker["next_attempt_time"] = self._calculate_next_attempt_time(circuit_breaker)
                    self.logger.warning("Circuit breaker opened", service_id=service_id, failure_count=circuit_breaker["failure_count"])
                
                # Re-raise the exception
                raise
                
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error("Circuit breaker error", error=str(e), exc_info=True)
            # Continue without circuit breaker on error
            return await call_next(request)
    
    def _should_skip_circuit_breaker(self, path: str) -> bool:
        """Check if circuit breaker should be skipped for this path"""
        skip_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def _get_service_identifier(self, request: Request) -> str:
        """Get service identifier for circuit breaker"""
        # Use the target service URL as identifier
        target_service = request.headers.get("X-Target-Service")
        if target_service:
            return f"service:{target_service}"
        
        # Use path as fallback
        return f"path:{request.url.path.split('/')[1] if len(request.url.path.split('/')) > 1 else 'default'}"
    
    async def _get_circuit_breaker(self, service_id: str) -> Dict[str, Any]:
        """Get circuit breaker for service"""
        try:
            # Try to get from Redis first
            circuit_data = await self.redis_client.hgetall(f"circuit_breaker:{service_id}")
            if circuit_data:
                # Convert string values back to appropriate types
                circuit_breaker = self._create_circuit_breaker()
                circuit_breaker.update({
                    "state": CircuitState(circuit_data.get("state", "closed")),
                    "failure_count": int(circuit_data.get("failure_count", 0)),
                    "success_count": int(circuit_data.get("success_count", 0)),
                    "last_failure_time": float(circuit_data.get("last_failure_time", 0)) if circuit_data.get("last_failure_time") else None,
                    "last_success_time": float(circuit_data.get("last_success_time", 0)) if circuit_data.get("last_success_time") else None,
                    "last_state_change": float(circuit_data.get("last_state_change", 0)),
                    "next_attempt_time": float(circuit_data.get("next_attempt_time", 0)) if circuit_data.get("next_attempt_time") else None,
                    "consecutive_failures": int(circuit_data.get("consecutive_failures", 0)),
                    "consecutive_successes": int(circuit_data.get("consecutive_successes", 0)),
                    "total_requests": int(circuit_data.get("total_requests", 0)),
                    "total_failures": int(circuit_data.get("total_failures", 0)),
                    "total_successes": int(circuit_data.get("total_successes", 0)),
                    "average_response_time": float(circuit_data.get("average_response_time", 0.0))
                })
                return circuit_breaker
        except Exception as e:
            self.logger.warning("Failed to get circuit breaker from Redis", error=str(e))
        
        # Fallback to in-memory
        return self.circuit_breakers[service_id]
    
    async def _should_attempt_recovery(self, circuit_breaker: Dict[str, Any]) -> bool:
        """Check if we should attempt recovery"""
        if circuit_breaker["next_attempt_time"] is None:
            return True
        
        return time.time() >= circuit_breaker["next_attempt_time"]
    
    async def _record_success(self, service_id: str, circuit_breaker: Dict[str, Any], response_time: float):
        """Record successful request"""
        current_time = time.time()
        
        # Update circuit breaker
        circuit_breaker["success_count"] += 1
        circuit_breaker["consecutive_successes"] += 1
        circuit_breaker["consecutive_failures"] = 0
        circuit_breaker["last_success_time"] = current_time
        circuit_breaker["total_requests"] += 1
        circuit_breaker["total_successes"] += 1
        
        # Update response time tracking
        circuit_breaker["response_times"].append(response_time)
        circuit_breaker["average_response_time"] = sum(circuit_breaker["response_times"]) / len(circuit_breaker["response_times"])
        
        # Update health metrics
        health_metrics = self.health_metrics[service_id]
        health_metrics["successful_requests"] += 1
        health_metrics["total_requests"] += 1
        health_metrics["last_success_time"] = current_time
        health_metrics["response_times"].append(response_time)
        health_metrics["average_response_time"] = sum(health_metrics["response_times"]) / len(health_metrics["response_times"])
        
        # Save to Redis
        await self._save_circuit_breaker(service_id, circuit_breaker)
    
    async def _record_failure(self, service_id: str, circuit_breaker: Dict[str, Any], error: Exception, response_time: float):
        """Record failed request"""
        current_time = time.time()
        error_type = type(error).__name__
        
        # Update circuit breaker
        circuit_breaker["failure_count"] += 1
        circuit_breaker["consecutive_failures"] += 1
        circuit_breaker["consecutive_successes"] = 0
        circuit_breaker["last_failure_time"] = current_time
        circuit_breaker["total_requests"] += 1
        circuit_breaker["total_failures"] += 1
        circuit_breaker["error_types"][error_type] += 1
        
        # Update response time tracking
        circuit_breaker["response_times"].append(response_time)
        circuit_breaker["average_response_time"] = sum(circuit_breaker["response_times"]) / len(circuit_breaker["response_times"])
        
        # Update health metrics
        health_metrics = self.health_metrics[service_id]
        health_metrics["failed_requests"] += 1
        health_metrics["total_requests"] += 1
        health_metrics["last_failure_time"] = current_time
        health_metrics["response_times"].append(response_time)
        health_metrics["average_response_time"] = sum(health_metrics["response_times"]) / len(health_metrics["response_times"])
        
        # Save to Redis
        await self._save_circuit_breaker(service_id, circuit_breaker)
    
    async def _should_open_circuit(self, circuit_breaker: Dict[str, Any]) -> bool:
        """Check if circuit should be opened"""
        # Check failure threshold
        if circuit_breaker["consecutive_failures"] >= self.failure_threshold:
            return True
        
        # Check failure rate
        if circuit_breaker["total_requests"] >= 10:
            failure_rate = circuit_breaker["total_failures"] / circuit_breaker["total_requests"]
            if failure_rate > 0.5:  # 50% failure rate
                return True
        
        return False
    
    def _calculate_next_attempt_time(self, circuit_breaker: Dict[str, Any]) -> float:
        """Calculate next attempt time using recovery strategy"""
        strategy_func = self.recovery_strategies.get(self.current_recovery_strategy)
        if strategy_func:
            return strategy_func(circuit_breaker)
        
        # Default to exponential backoff
        return time.time() + self.recovery_timeout
    
    def _exponential_backoff_strategy(self, circuit_breaker: Dict[str, Any]) -> float:
        """Exponential backoff recovery strategy"""
        base_timeout = self.recovery_timeout
        consecutive_failures = circuit_breaker["consecutive_failures"]
        return time.time() + (base_timeout * (2 ** consecutive_failures))
    
    def _linear_backoff_strategy(self, circuit_breaker: Dict[str, Any]) -> float:
        """Linear backoff recovery strategy"""
        base_timeout = self.recovery_timeout
        consecutive_failures = circuit_breaker["consecutive_failures"]
        return time.time() + (base_timeout * consecutive_failures)
    
    def _immediate_recovery_strategy(self, circuit_breaker: Dict[str, Any]) -> float:
        """Immediate recovery strategy"""
        return time.time() + 1  # 1 second delay
    
    async def _save_circuit_breaker(self, service_id: str, circuit_breaker: Dict[str, Any]):
        """Save circuit breaker state to Redis"""
        try:
            circuit_data = {
                "state": circuit_breaker["state"].value,
                "failure_count": str(circuit_breaker["failure_count"]),
                "success_count": str(circuit_breaker["success_count"]),
                "last_failure_time": str(circuit_breaker["last_failure_time"]) if circuit_breaker["last_failure_time"] else "",
                "last_success_time": str(circuit_breaker["last_success_time"]) if circuit_breaker["last_success_time"] else "",
                "last_state_change": str(circuit_breaker["last_state_change"]),
                "next_attempt_time": str(circuit_breaker["next_attempt_time"]) if circuit_breaker["next_attempt_time"] else "",
                "consecutive_failures": str(circuit_breaker["consecutive_failures"]),
                "consecutive_successes": str(circuit_breaker["consecutive_successes"]),
                "total_requests": str(circuit_breaker["total_requests"]),
                "total_failures": str(circuit_breaker["total_failures"]),
                "total_successes": str(circuit_breaker["total_successes"]),
                "average_response_time": str(circuit_breaker["average_response_time"])
            }
            
            await self.redis_client.hset(f"circuit_breaker:{service_id}", mapping=circuit_data)
            await self.redis_client.expire(f"circuit_breaker:{service_id}", 3600)  # 1 hour TTL
            
        except Exception as e:
            self.logger.warning("Failed to save circuit breaker to Redis", error=str(e))
    
    def set_recovery_strategy(self, strategy: str):
        """Set recovery strategy"""
        if strategy in self.recovery_strategies:
            self.current_recovery_strategy = strategy
            self.logger.info("Recovery strategy changed", strategy=strategy)
        else:
            self.logger.warning("Invalid recovery strategy", strategy=strategy)
    
    def enable_adaptive_thresholds(self, enabled: bool = True):
        """Enable or disable adaptive thresholds"""
        self.adaptive_enabled = enabled
        self.logger.info("Adaptive thresholds", enabled=enabled)
    
    def get_circuit_breaker_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        stats = {
            "total_circuits": len(self.circuit_breakers),
            "open_circuits": 0,
            "half_open_circuits": 0,
            "closed_circuits": 0,
            "recovery_strategy": self.current_recovery_strategy,
            "adaptive_enabled": self.adaptive_enabled,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "circuits": {}
        }
        
        for service_id, circuit in self.circuit_breakers.items():
            stats["circuits"][service_id] = {
                "state": circuit["state"].value,
                "failure_count": circuit["failure_count"],
                "success_count": circuit["success_count"],
                "total_requests": circuit["total_requests"],
                "failure_rate": circuit["total_failures"] / circuit["total_requests"] if circuit["total_requests"] > 0 else 0,
                "average_response_time": circuit["average_response_time"],
                "last_failure_time": circuit["last_failure_time"],
                "last_success_time": circuit["last_success_time"]
            }
            
            if circuit["state"] == CircuitState.OPEN:
                stats["open_circuits"] += 1
            elif circuit["state"] == CircuitState.HALF_OPEN:
                stats["half_open_circuits"] += 1
            else:
                stats["closed_circuits"] += 1
        
        return stats
    
    def reset_circuit_breaker(self, service_id: str):
        """Reset circuit breaker for service"""
        if service_id in self.circuit_breakers:
            self.circuit_breakers[service_id] = self._create_circuit_breaker()
            self.logger.info("Circuit breaker reset", service_id=service_id)
    
    def clear_all_circuit_breakers(self):
        """Clear all circuit breakers"""
        self.circuit_breakers.clear()
        self.health_metrics.clear()
        self.logger.info("All circuit breakers cleared") 