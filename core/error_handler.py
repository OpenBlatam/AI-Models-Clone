"""
Error Handling and Retry Mechanism for HeyGen AI
================================================

Provides robust error handling, retry logic, and circuit breaker patterns
for enterprise-grade reliability and fault tolerance.
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union
import traceback

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for classification"""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    RESOURCE_NOT_FOUND = "resource_not_found"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    INTERNAL_ERROR = "internal_error"
    EXTERNAL_SERVICE = "external_service"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for error handling"""
    
    service_name: str
    operation: str
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_errors: List[Type[Exception]] = field(default_factory=list)
    non_retryable_errors: List[Type[Exception]] = field(default_factory=list)


@dataclass
class CircuitBreakerState:
    """Circuit breaker state information"""
    
    is_open: bool = False
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None
    success_count: int = 0
    total_requests: int = 0


class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance.
    
    Prevents cascading failures by temporarily stopping requests
    when a service is experiencing issues.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
        monitor_interval: float = 10.0
    ):
        """
        Initialize the circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
            expected_exception: Exception type to monitor
            monitor_interval: Interval for monitoring circuit state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.monitor_interval = monitor_interval
        
        self.state = CircuitBreakerState()
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Start monitoring
        self._start_monitoring()
    
    def _start_monitoring(self) -> None:
        """Start the monitoring task."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._monitor_task = asyncio.create_task(self._monitor_circuit())
        except RuntimeError:
            # No event loop running, skip monitoring
            pass
    
    async def _monitor_circuit(self) -> None:
        """Monitor circuit breaker state."""
        while True:
            try:
                await asyncio.sleep(self.monitor_interval)
                
                # Check if we should attempt recovery
                if (self.state.is_open and 
                    self.state.next_attempt_time and 
                    datetime.now() >= self.state.next_attempt_time):
                    self._attempt_recovery()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in circuit breaker monitoring: {e}")
    
    def _attempt_recovery(self) -> None:
        """Attempt to recover from open state."""
        self.state.is_open = False
        self.state.failure_count = 0
        self.state.next_attempt_time = None
        logger.info("Circuit breaker attempting recovery")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state.is_open:
            if (self.state.next_attempt_time and 
                datetime.now() >= self.state.next_attempt_time):
                self._attempt_recovery()
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute an async function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state.is_open:
            if (self.state.next_attempt_time and 
                datetime.now() >= self.state.next_attempt_time):
                self._attempt_recovery()
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self) -> None:
        """Handle successful function execution."""
        self.state.success_count += 1
        self.state.total_requests += 1
        
        # Reset failure count on success
        if self.state.failure_count > 0:
            self.state.failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle function execution failure."""
        self.state.failure_count += 1
        self.state.total_requests += 1
        self.state.last_failure_time = datetime.now()
        
        # Open circuit if threshold reached
        if self.state.failure_count >= self.failure_threshold:
            self.state.is_open = True
            self.state.next_attempt_time = datetime.now() + timedelta(seconds=self.recovery_timeout)
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "is_open": self.state.is_open,
            "failure_count": self.state.failure_count,
            "success_count": self.state.success_count,
            "total_requests": self.state.total_requests,
            "failure_rate": (self.state.failure_count / self.state.total_requests 
                           if self.state.total_requests > 0 else 0.0),
            "last_failure_time": self.state.last_failure_time.isoformat() if self.state.last_failure_time else None,
            "next_attempt_time": self.state.next_attempt_time.isoformat() if self.state.next_attempt_time else None
        }
    
    async def shutdown(self) -> None:
        """Shutdown the circuit breaker."""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass


class RetryHandler:
    """
    Retry handler with exponential backoff and jitter.
    
    Provides intelligent retry logic for transient failures.
    """
    
    def __init__(self, config: RetryConfig):
        """
        Initialize the retry handler.
        
        Args:
            config: Retry configuration
        """
        self.config = config
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # Check if error is retryable
                if not self._should_retry(e, attempt):
                    raise e
                
                # Don't sleep on last attempt
                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)
        
        # All attempts failed
        raise last_exception
    
    async def retry_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute an async function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return await func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # Check if error is retryable
                if not self._should_retry(e, attempt):
                    raise e
                
                # Don't sleep on last attempt
                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    await asyncio.sleep(delay)
        
        # All attempts failed
        raise last_exception
    
    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if an error should trigger a retry."""
        # Check if error is explicitly non-retryable
        if any(isinstance(error, error_type) for error_type in self.config.non_retryable_errors):
            return False
        
        # Check if error is explicitly retryable
        if self.config.retryable_errors and any(isinstance(error, error_type) for error_type in self.config.retryable_errors):
            return True
        
        # Default retryable errors
        retryable_types = (
            ConnectionError,
            TimeoutError,
            OSError,
            asyncio.TimeoutError
        )
        
        return isinstance(error, retryable_types)
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = min(
            self.config.base_delay * (self.config.exponential_base ** attempt),
            self.config.max_delay
        )
        
        if self.config.jitter:
            # Add jitter to prevent thundering herd
            jitter = random.uniform(0, 0.1 * delay)
            delay += jitter
        
        return delay


class ErrorClassifier:
    """
    Classifies errors for appropriate handling strategies.
    
    Provides intelligent error categorization and handling recommendations.
    """
    
    def __init__(self):
        """Initialize the error classifier."""
        self._error_patterns = self._build_error_patterns()
    
    def _build_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Build error classification patterns."""
        return {
            "network": {
                "patterns": ["connection", "timeout", "network", "dns", "ssl"],
                "severity": ErrorSeverity.MEDIUM,
                "retryable": True,
                "circuit_breaker": True
            },
            "authentication": {
                "patterns": ["auth", "login", "token", "expired", "invalid"],
                "severity": ErrorSeverity.HIGH,
                "retryable": False,
                "circuit_breaker": False
            },
            "authorization": {
                "patterns": ["permission", "access", "forbidden", "unauthorized"],
                "severity": ErrorSeverity.HIGH,
                "retryable": False,
                "circuit_breaker": False
            },
            "validation": {
                "patterns": ["validation", "invalid", "malformed", "schema"],
                "severity": ErrorSeverity.MEDIUM,
                "retryable": False,
                "circuit_breaker": False
            },
            "rate_limit": {
                "patterns": ["rate limit", "throttle", "quota", "too many"],
                "severity": ErrorSeverity.MEDIUM,
                "retryable": True,
                "circuit_breaker": True
            },
            "timeout": {
                "patterns": ["timeout", "deadline", "expired"],
                "severity": ErrorSeverity.MEDIUM,
                "retryable": True,
                "circuit_breaker": True
            },
            "resource_not_found": {
                "patterns": ["not found", "404", "missing", "doesn't exist"],
                "severity": ErrorSeverity.LOW,
                "retryable": False,
                "circuit_breaker": False
            }
        }
    
    def classify_error(self, error: Exception) -> Dict[str, Any]:
        """
        Classify an error for appropriate handling.
        
        Args:
            error: Exception to classify
            
        Returns:
            Dictionary with error classification
        """
        error_message = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Check patterns
        for category, info in self._error_patterns.items():
            for pattern in info["patterns"]:
                if pattern in error_message or pattern in error_type:
                    return {
                        "category": category,
                        "severity": info["severity"],
                        "retryable": info["retryable"],
                        "circuit_breaker": info["circuit_breaker"],
                        "error_type": type(error).__name__,
                        "error_message": str(error)
                    }
        
        # Default classification
        return {
            "category": ErrorCategory.UNKNOWN,
            "severity": ErrorSeverity.MEDIUM,
            "retryable": True,
            "circuit_breaker": True,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }


class ErrorHandler:
    """
    Main error handler for the HeyGen AI system.
    
    Orchestrates error handling, retry logic, and circuit breakers.
    """
    
    def __init__(self):
        """Initialize the error handler."""
        self.error_classifier = ErrorClassifier()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_handlers: Dict[str, RetryHandler] = {}
        self.error_history: List[Dict[str, Any]] = []
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create a circuit breaker for a service."""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
    
    def get_retry_handler(self, service_name: str, config: Optional[RetryConfig] = None) -> RetryHandler:
        """Get or create a retry handler for a service."""
        if service_name not in self.retry_handlers:
            config = config or RetryConfig()
            self.retry_handlers[service_name] = RetryHandler(config)
        return self.retry_handlers[service_name]
    
    def handle_error(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """
        Handle an error with appropriate strategy.
        
        Args:
            error: Exception that occurred
            context: Error context information
            
        Returns:
            Error handling result
        """
        # Classify the error
        classification = self.error_classifier.classify_error(error)
        
        # Create error record
        error_record = {
            "timestamp": context.timestamp.isoformat(),
            "service_name": context.service_name,
            "operation": context.operation,
            "error_type": classification["error_type"],
            "error_message": classification["error_message"],
            "category": classification["category"],
            "severity": classification["severity"],
            "retryable": classification["retryable"],
            "circuit_breaker": classification["circuit_breaker"],
            "user_id": context.user_id,
            "session_id": context.session_id,
            "request_id": context.request_id,
            "additional_context": context.additional_context,
            "stack_trace": traceback.format_exc()
        }
        
        # Add to history
        self.error_history.append(error_record)
        
        # Log the error
        log_level = logging.ERROR if classification["severity"] in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else logging.WARNING
        logger.log(log_level, f"Error in {context.service_name}.{context.operation}: {error}", extra=error_record)
        
        return error_record
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error handling statistics."""
        if not self.error_history:
            return {"total_errors": 0}
        
        total_errors = len(self.error_history)
        errors_by_category = {}
        errors_by_severity = {}
        errors_by_service = {}
        
        for error in self.error_history:
            # Category breakdown
            category = error["category"]
            errors_by_category[category] = errors_by_category.get(category, 0) + 1
            
            # Severity breakdown
            severity = error["severity"]
            errors_by_severity[severity] = errors_by_severity.get(severity, 0) + 1
            
            # Service breakdown
            service = error["service_name"]
            errors_by_service[service] = errors_by_service.get(service, 0) + 1
        
        return {
            "total_errors": total_errors,
            "errors_by_category": errors_by_category,
            "errors_by_severity": errors_by_severity,
            "errors_by_service": errors_by_service,
            "recent_errors": self.error_history[-10:] if len(self.error_history) > 10 else self.error_history
        }
    
    async def shutdown(self) -> None:
        """Shutdown all error handling components."""
        for circuit_breaker in self.circuit_breakers.values():
            await circuit_breaker.shutdown()


# Decorators for easy error handling
def with_error_handling(service_name: str, operation: str = None):
    """
    Decorator to add error handling to functions.
    
    Args:
        service_name: Name of the service
        operation: Name of the operation (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            error_handler = ErrorHandler()
            context = ErrorContext(
                service_name=service_name,
                operation=operation or func.__name__
            )
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_record = error_handler.handle_error(e, context)
                raise
        return wrapper
    return decorator


def with_retry(service_name: str, max_attempts: int = 3, base_delay: float = 1.0):
    """
    Decorator to add retry logic to functions.
    
    Args:
        service_name: Name of the service
        max_attempts: Maximum retry attempts
        base_delay: Base delay between retries
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            error_handler = ErrorHandler()
            retry_handler = error_handler.get_retry_handler(
                service_name, 
                RetryConfig(max_attempts=max_attempts, base_delay=base_delay)
            )
            
            return await retry_handler.retry_async(func, *args, **kwargs)
        return wrapper
    return decorator


def with_circuit_breaker(service_name: str, failure_threshold: int = 5):
    """
    Decorator to add circuit breaker protection to functions.
    
    Args:
        service_name: Name of the service
        failure_threshold: Failure threshold for circuit breaker
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            error_handler = ErrorHandler()
            circuit_breaker = error_handler.get_circuit_breaker(service_name)
            
            return await circuit_breaker.call_async(func, *args, **kwargs)
        return wrapper
    return decorator
