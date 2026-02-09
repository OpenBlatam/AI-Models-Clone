#!/usr/bin/env python3
"""
Deployment Circuit Breaker
Implements circuit breaker pattern to prevent cascading failures
"""

import time
import logging
from typing import Optional, Callable, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Open circuit after N failures
    success_threshold: int = 2  # Close circuit after N successes
    timeout_seconds: int = 60  # Time before attempting half-open
    failure_timeout: int = 300  # Time to wait before retry after failure


class CircuitBreaker:
    """Circuit breaker for deployment operations"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: datetime = datetime.now()
        self.opened_at: Optional[datetime] = None
    
    def call(self, func: Callable[[], Tuple[bool, Any]], operation_name: str = "operation") -> Tuple[bool, Any]:
        """
        Execute function with circuit breaker protection
        
        Returns:
            Tuple of (success: bool, result: Any)
        """
        # Check if circuit should transition
        self._check_state_transition()
        
        # If circuit is open, reject immediately
        if self.state == CircuitState.OPEN:
            logger.warning(f"Circuit breaker OPEN - rejecting {operation_name}")
            return False, "Circuit breaker is OPEN - too many recent failures"
        
        # Execute operation
        try:
            success, result = func()
            
            if success:
                self._on_success()
                return True, result
            else:
                self._on_failure()
                return False, result
                
        except Exception as e:
            self._on_failure()
            logger.error(f"Circuit breaker caught exception: {e}")
            return False, str(e)
    
    def _on_success(self) -> None:
        """Handle successful operation"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._close_circuit()
        else:
            # Reset failure count on success
            self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open state opens circuit
            self._open_circuit()
        elif self.failure_count >= self.config.failure_threshold:
            self._open_circuit()
    
    def _open_circuit(self) -> None:
        """Open the circuit breaker"""
        if self.state != CircuitState.OPEN:
            logger.error(f"Opening circuit breaker after {self.failure_count} failures")
            self.state = CircuitState.OPEN
            self.opened_at = datetime.now()
            self.last_state_change = datetime.now()
            self.failure_count = 0
            self.success_count = 0
    
    def _close_circuit(self) -> None:
        """Close the circuit breaker"""
        logger.info("Closing circuit breaker - service recovered")
        self.state = CircuitState.CLOSED
        self.last_state_change = datetime.now()
        self.failure_count = 0
        self.success_count = 0
        self.opened_at = None
    
    def _check_state_transition(self) -> None:
        """Check if circuit should transition states"""
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self.opened_at:
                elapsed = (datetime.now() - self.opened_at).total_seconds()
                if elapsed >= self.config.timeout_seconds:
                    logger.info("Transitioning to HALF_OPEN state")
                    self.state = CircuitState.HALF_OPEN
                    self.last_state_change = datetime.now()
                    self.success_count = 0
    
    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'last_state_change': self.last_state_change.isoformat()
        }
    
    def reset(self) -> None:
        """Manually reset circuit breaker"""
        logger.info("Manually resetting circuit breaker")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.opened_at = None
        self.last_state_change = datetime.now()
