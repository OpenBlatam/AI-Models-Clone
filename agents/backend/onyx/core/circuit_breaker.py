"""
🔄 ENTERPRISE CIRCUIT BREAKER
============================

Advanced circuit breaker implementation for microservices with:
- Exponential backoff
- Health monitoring
- Prometheus metrics
- Automatic recovery
- Per-service configuration
"""

import time
import asyncio
import logging
from typing import Any, Dict, Callable, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from fastapi import HTTPException

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics tracking"""
    total_requests: int = 0
    failed_requests: int = 0
    success_requests: int = 0
    timeout_requests: int = 0
    last_failure_time: Optional[float] = None
    state_transitions: int = 0

class EnterpriseCircuitBreaker:
    """
    Advanced circuit breaker with exponential backoff and health monitoring
    
    Features:
    - Multiple failure thresholds
    - Slow call detection
    - Exponential backoff
    - Prometheus metrics
    - Health monitoring
    """
    
    def __init__(self, 
                 service_name: str,
                 failure_threshold: int = 5,
                 timeout: int = 60,
                 half_open_max_calls: int = 5,
                 slow_call_threshold: float = 5.0,
                 max_backoff_multiplier: int = 16):
        
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        self.slow_call_threshold = slow_call_threshold
        self.max_backoff_multiplier = max_backoff_multiplier
        
        self.state = CircuitBreakerState.CLOSED
        self.stats = CircuitBreakerStats()
        self.half_open_calls = 0
        self.consecutive_failures = 0
        
        self.logger = logging.getLogger(f"circuit_breaker.{service_name}")
        
        # Initialize Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self._init_metrics()
    
    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        self.state_metric = Gauge(
            f'circuit_breaker_state',
            f'Circuit breaker state (0=closed, 1=open, 2=half_open)',
            ['service']
        )
        
        self.requests_metric = Counter(
            f'circuit_breaker_requests_total',
            f'Circuit breaker requests',
            ['service', 'result']
        )
        
        self.response_time_metric = Histogram(
            f'circuit_breaker_response_time_seconds',
            f'Circuit breaker response time',
            ['service']
        )
        
        # Set initial state
        self.state_metric.labels(service=self.service_name).set(0)
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            HTTPException: If circuit breaker is open or service unavailable
        """
        self.stats.total_requests += 1
        
        # Check circuit breaker state
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
        
        # Execute the function with timing
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
        """
        Check if circuit breaker should attempt to reset based on exponential backoff
        
        Returns:
            bool: True if should attempt reset
        """
        if self.stats.last_failure_time is None:
            return True
        
        time_since_failure = time.time() - self.stats.last_failure_time
        
        # Exponential backoff: increase timeout based on consecutive failures
        backoff_multiplier = min(
            2 ** (self.consecutive_failures // self.failure_threshold), 
            self.max_backoff_multiplier
        )
        effective_timeout = self.timeout * backoff_multiplier
        
        return time_since_failure >= effective_timeout
    
    async def _transition_to_half_open(self):
        """Transition circuit breaker to half-open state"""
        self.state = CircuitBreakerState.HALF_OPEN
        self.half_open_calls = 0
        self.stats.state_transitions += 1
        
        self.logger.info(f"Circuit breaker for {self.service_name} transitioned to HALF_OPEN")
        
        if PROMETHEUS_AVAILABLE:
            self.state_metric.labels(service=self.service_name).set(2)
    
    async def _record_success(self, execution_time: float):
        """Record successful execution"""
        self.stats.success_requests += 1
        self.consecutive_failures = 0  # Reset consecutive failures
        
        # Record response time
        if PROMETHEUS_AVAILABLE:
            self.response_time_metric.labels(service=self.service_name).observe(execution_time)
            self.requests_metric.labels(service=self.service_name, result='success').inc()
        
        # Check for slow calls
        if execution_time > self.slow_call_threshold:
            self.stats.timeout_requests += 1
            self.logger.warning(
                f"Slow call detected for {self.service_name}: {execution_time:.2f}s"
            )
        
        # Reset circuit breaker if in half-open state
        if self.state == CircuitBreakerState.HALF_OPEN:
            await self._transition_to_closed()
    
    async def _record_failure(self, exception: Exception, execution_time: float):
        """Record failed execution"""
        self.stats.failed_requests += 1
        self.consecutive_failures += 1
        self.stats.last_failure_time = time.time()
        
        if PROMETHEUS_AVAILABLE:
            self.response_time_metric.labels(service=self.service_name).observe(execution_time)
            self.requests_metric.labels(service=self.service_name, result='failure').inc()
        
        self.logger.warning(
            f"Circuit breaker failure for {self.service_name}: {type(exception).__name__}: {str(exception)}"
        )
        
        # Transition to open if threshold exceeded
        if (self.state == CircuitBreakerState.CLOSED and 
            self.consecutive_failures >= self.failure_threshold):
            await self._transition_to_open()
        elif self.state == CircuitBreakerState.HALF_OPEN:
            await self._transition_to_open()
    
    async def _record_blocked_request(self):
        """Record request blocked by circuit breaker"""
        if PROMETHEUS_AVAILABLE:
            self.requests_metric.labels(service=self.service_name, result='blocked').inc()
    
    async def _transition_to_closed(self):
        """Transition circuit breaker to closed state"""
        self.state = CircuitBreakerState.CLOSED
        self.consecutive_failures = 0
        self.half_open_calls = 0
        self.stats.state_transitions += 1
        
        self.logger.info(f"Circuit breaker for {self.service_name} transitioned to CLOSED")
        
        if PROMETHEUS_AVAILABLE:
            self.state_metric.labels(service=self.service_name).set(0)
    
    async def _transition_to_open(self):
        """Transition circuit breaker to open state"""
        self.state = CircuitBreakerState.OPEN
        self.stats.state_transitions += 1
        
        self.logger.error(f"Circuit breaker for {self.service_name} transitioned to OPEN")
        
        if PROMETHEUS_AVAILABLE:
            self.state_metric.labels(service=self.service_name).set(1)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive circuit breaker statistics
        
        Returns:
            Dict containing all statistics
        """
        return {
            "service_name": self.service_name,
            "state": self.state.value,
            "total_requests": self.stats.total_requests,
            "success_requests": self.stats.success_requests,
            "failed_requests": self.stats.failed_requests,
            "timeout_requests": self.stats.timeout_requests,
            "consecutive_failures": self.consecutive_failures,
            "state_transitions": self.stats.state_transitions,
            "failure_rate": (
                self.stats.failed_requests / self.stats.total_requests 
                if self.stats.total_requests > 0 else 0
            ),
            "success_rate": (
                self.stats.success_requests / self.stats.total_requests 
                if self.stats.total_requests > 0 else 0
            ),
            "last_failure_time": self.stats.last_failure_time,
            "configuration": {
                "failure_threshold": self.failure_threshold,
                "timeout": self.timeout,
                "half_open_max_calls": self.half_open_max_calls,
                "slow_call_threshold": self.slow_call_threshold
            }
        }
    
    async def reset(self):
        """Manually reset circuit breaker to closed state"""
        self.state = CircuitBreakerState.CLOSED
        self.consecutive_failures = 0
        self.half_open_calls = 0
        self.stats = CircuitBreakerStats()
        
        if PROMETHEUS_AVAILABLE:
            self.state_metric.labels(service=self.service_name).set(0)
        
        self.logger.info(f"Circuit breaker for {self.service_name} manually reset")

class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers with different configurations
    """
    
    def __init__(self):
        self.circuit_breakers: Dict[str, EnterpriseCircuitBreaker] = {}
        self.logger = logging.getLogger("circuit_breaker_manager")
    
    def register_service(self, 
                        service_name: str,
                        failure_threshold: int = 5,
                        timeout: int = 60,
                        half_open_max_calls: int = 5,
                        slow_call_threshold: float = 5.0) -> EnterpriseCircuitBreaker:
        """
        Register a new service with circuit breaker protection
        
        Args:
            service_name: Name of the service
            failure_threshold: Number of failures before opening
            timeout: Timeout before attempting reset
            half_open_max_calls: Max calls in half-open state
            slow_call_threshold: Threshold for slow call detection
            
        Returns:
            EnterpriseCircuitBreaker instance
        """
        circuit_breaker = EnterpriseCircuitBreaker(
            service_name=service_name,
            failure_threshold=failure_threshold,
            timeout=timeout,
            half_open_max_calls=half_open_max_calls,
            slow_call_threshold=slow_call_threshold
        )
        
        self.circuit_breakers[service_name] = circuit_breaker
        self.logger.info(f"Registered circuit breaker for service: {service_name}")
        
        return circuit_breaker
    
    def get_circuit_breaker(self, service_name: str) -> Optional[EnterpriseCircuitBreaker]:
        """Get circuit breaker for service"""
        return self.circuit_breakers.get(service_name)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all registered circuit breakers"""
        return {
            service_name: cb.get_stats() 
            for service_name, cb in self.circuit_breakers.items()
        }
    
    async def reset_all(self):
        """Reset all circuit breakers"""
        for circuit_breaker in self.circuit_breakers.values():
            await circuit_breaker.reset()
        
        self.logger.info("All circuit breakers reset")
    
    def get_service_health(self) -> Dict[str, str]:
        """Get health status of all services"""
        return {
            service_name: cb.state.value
            for service_name, cb in self.circuit_breakers.items()
        }

# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager() 