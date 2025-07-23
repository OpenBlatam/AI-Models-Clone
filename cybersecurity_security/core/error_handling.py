"""
Error Handling System

Comprehensive error handling for the cybersecurity toolkit.
"""

import asyncio
import traceback
import time
from typing import Dict, Any, List, Optional, Union, Callable, Type
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging
import functools
from contextlib import contextmanager

# ============================================================================
# BASE EXCEPTIONS
# ============================================================================

class SecurityToolkitError(Exception):
    """Base exception for all security toolkit errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "traceback": self.traceback
        }

class ValidationError(SecurityToolkitError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None, **kwargs):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field
        self.value = value

class ConfigurationError(SecurityToolkitError):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)
        self.config_key = config_key

class NetworkError(SecurityToolkitError):
    """Exception raised for network-related errors."""
    
    def __init__(self, message: str, target: Optional[str] = None, 
                 port: Optional[int] = None, **kwargs):
        super().__init__(message, error_code="NETWORK_ERROR", **kwargs)
        self.target = target
        self.port = port

class CryptoError(SecurityToolkitError):
    """Exception raised for cryptographic operation errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None, 
                 algorithm: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="CRYPTO_ERROR", **kwargs)
        self.operation = operation
        self.algorithm = algorithm

class ScanError(SecurityToolkitError):
    """Exception raised for scanning operation errors."""
    
    def __init__(self, message: str, scan_type: Optional[str] = None, 
                 target: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="SCAN_ERROR", **kwargs)
        self.scan_type = scan_type
        self.target = target

class AttackError(SecurityToolkitError):
    """Exception raised for attack operation errors."""
    
    def __init__(self, message: str, attack_type: Optional[str] = None, 
                 target: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="ATTACK_ERROR", **kwargs)
        self.attack_type = attack_type
        self.target = target

class ReportError(SecurityToolkitError):
    """Exception raised for report generation errors."""
    
    def __init__(self, message: str, report_format: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="REPORT_ERROR", **kwargs)
        self.report_format = report_format

# ============================================================================
# SPECIFIC EXCEPTIONS
# ============================================================================

class TargetValidationError(ValidationError):
    """Exception raised for target validation errors."""
    
    def __init__(self, message: str, target: str, **kwargs):
        super().__init__(message, field="target", value=target, **kwargs)
        self.target = target

class PortValidationError(ValidationError):
    """Exception raised for port validation errors."""
    
    def __init__(self, message: str, port: int, **kwargs):
        super().__init__(message, field="port", value=port, **kwargs)
        self.port = port

class CredentialValidationError(ValidationError):
    """Exception raised for credential validation errors."""
    
    def __init__(self, message: str, username: Optional[str] = None, **kwargs):
        super().__init__(message, field="credentials", value=username, **kwargs)
        self.username = username

class PayloadValidationError(ValidationError):
    """Exception raised for payload validation errors."""
    
    def __init__(self, message: str, payload_type: Optional[str] = None, **kwargs):
        super().__init__(message, field="payload", value=payload_type, **kwargs)
        self.payload_type = payload_type

class TimeoutError(SecurityToolkitError):
    """Exception raised for timeout errors."""
    
    def __init__(self, message: str, timeout: float, operation: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="TIMEOUT_ERROR", **kwargs)
        self.timeout = timeout
        self.operation = operation

class ConnectionError(NetworkError):
    """Exception raised for connection errors."""
    
    def __init__(self, message: str, target: str, port: Optional[int] = None, **kwargs):
        super().__init__(message, target=target, port=port, error_code="CONNECTION_ERROR", **kwargs)

class AuthenticationError(SecurityToolkitError):
    """Exception raised for authentication errors."""
    
    def __init__(self, message: str, service: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="AUTH_ERROR", **kwargs)
        self.service = service

class AuthorizationError(SecurityToolkitError):
    """Exception raised for authorization errors."""
    
    def __init__(self, message: str, resource: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="AUTHZ_ERROR", **kwargs)
        self.resource = resource

class RateLimitError(SecurityToolkitError):
    """Exception raised for rate limiting errors."""
    
    def __init__(self, message: str, retry_after: Optional[float] = None, **kwargs):
        super().__init__(message, error_code="RATE_LIMIT_ERROR", **kwargs)
        self.retry_after = retry_after

class ResourceNotFoundError(SecurityToolkitError):
    """Exception raised for resource not found errors."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, 
                 resource_id: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="NOT_FOUND_ERROR", **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id

# ============================================================================
# ERROR CONTEXT AND SEVERITY
# ============================================================================

class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(str, Enum):
    """Error categories."""
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    CRYPTO = "crypto"
    SCAN = "scan"
    ATTACK = "attack"
    REPORT = "report"
    SYSTEM = "system"
    SECURITY = "security"

@dataclass
class ErrorContext:
    """Error context information."""
    operation: str
    module: str
    function: str
    line_number: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    target: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "operation": self.operation,
            "module": self.module,
            "function": self.function,
            "line_number": self.line_number,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "target": self.target,
            "metadata": self.metadata
        }

# ============================================================================
# ERROR HANDLER
# ============================================================================

class ErrorHandler:
    """Central error handler for the security toolkit."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts: Dict[str, int] = {}
        self.error_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
    
    def handle_error(self, error: Exception, context: Optional[ErrorContext] = None) -> None:
        """Handle an error with context."""
        error_info = self._create_error_info(error, context)
        
        # Log error
        self._log_error(error_info)
        
        # Update error counts
        error_type = error.__class__.__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Store in history
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)
        
        # Handle based on error type
        self._handle_specific_error(error, error_info)
    
    def _create_error_info(self, error: Exception, context: Optional[ErrorContext]) -> Dict[str, Any]:
        """Create error information dictionary."""
        error_info = {
            "error_type": error.__class__.__name__,
            "message": str(error),
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc()
        }
        
        if isinstance(error, SecurityToolkitError):
            error_info.update(error.to_dict())
        
        if context:
            error_info["context"] = context.to_dict()
        
        return error_info
    
    def _log_error(self, error_info: Dict[str, Any]) -> None:
        """Log error information."""
        level = self._get_log_level(error_info["error_type"])
        message = self._format_error_message(error_info)
        
        if level == logging.CRITICAL:
            self.logger.critical(message)
        elif level == logging.ERROR:
            self.logger.error(message)
        elif level == logging.WARNING:
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def _get_log_level(self, error_type: str) -> int:
        """Get appropriate log level for error type."""
        critical_errors = ["AuthenticationError", "AuthorizationError", "CryptoError"]
        warning_errors = ["ValidationError", "ConfigurationError"]
        
        if error_type in critical_errors:
            return logging.CRITICAL
        elif error_type in warning_errors:
            return logging.WARNING
        else:
            return logging.ERROR
    
    def _format_error_message(self, error_info: Dict[str, Any]) -> str:
        """Format error message for logging."""
        message = f"[{error_info['error_type']}] {error_info['message']}"
        
        if "context" in error_info:
            context = error_info["context"]
            message += f" | Operation: {context.get('operation', 'unknown')}"
            message += f" | Module: {context.get('module', 'unknown')}"
            message += f" | Function: {context.get('function', 'unknown')}"
        
        return message
    
    def _handle_specific_error(self, error: Exception, error_info: Dict[str, Any]) -> None:
        """Handle specific error types."""
        if isinstance(error, TimeoutError):
            self._handle_timeout_error(error)
        elif isinstance(error, RateLimitError):
            self._handle_rate_limit_error(error)
        elif isinstance(error, ConnectionError):
            self._handle_connection_error(error)
        elif isinstance(error, ValidationError):
            self._handle_validation_error(error)
    
    def _handle_timeout_error(self, error: TimeoutError) -> None:
        """Handle timeout errors."""
        self.logger.warning(f"Timeout occurred: {error.operation} after {error.timeout}s")
    
    def _handle_rate_limit_error(self, error: RateLimitError) -> None:
        """Handle rate limit errors."""
        if error.retry_after:
            self.logger.info(f"Rate limited, retry after {error.retry_after}s")
    
    def _handle_connection_error(self, error: ConnectionError) -> None:
        """Handle connection errors."""
        self.logger.error(f"Connection failed to {error.target}:{error.port}")
    
    def _handle_validation_error(self, error: ValidationError) -> None:
        """Handle validation errors."""
        self.logger.warning(f"Validation failed for {error.field}: {error.value}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "total_errors": len(self.error_history),
            "error_counts": self.error_counts,
            "recent_errors": self.error_history[-10:] if self.error_history else []
        }
    
    def clear_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()
        self.error_counts.clear()

# ============================================================================
# ERROR RECOVERY MECHANISMS
# ============================================================================

class RetryStrategy:
    """Retry strategy for failed operations."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
    
    async def execute(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(operation):
                    return await operation(*args, **kwargs)
                else:
                    return operation(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    raise last_exception
                
                delay = min(self.base_delay * (self.backoff_factor ** attempt), self.max_delay)
                await asyncio.sleep(delay)
        
        raise last_exception

class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def execute(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with circuit breaker logic."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise SecurityToolkitError("Circuit breaker is OPEN")
        
        try:
            if asyncio.iscoroutinefunction(operation):
                result = await operation(*args, **kwargs)
            else:
                result = operation(*args, **kwargs)
            
            self._on_success()
            return result
        
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self) -> None:
        """Handle successful operation."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self) -> None:
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class FallbackHandler:
    """Fallback handler for failed operations."""
    
    def __init__(self, fallback_operation: Optional[Callable] = None):
        self.fallback_operation = fallback_operation
    
    async def execute(self, primary_operation: Callable, *args, **kwargs) -> Any:
        """Execute primary operation with fallback."""
        try:
            if asyncio.iscoroutinefunction(primary_operation):
                return await primary_operation(*args, **kwargs)
            else:
                return primary_operation(*args, **kwargs)
        
        except Exception as e:
            if self.fallback_operation:
                try:
                    if asyncio.iscoroutinefunction(self.fallback_operation):
                        return await self.fallback_operation(*args, **kwargs)
                    else:
                        return self.fallback_operation(*args, **kwargs)
                except Exception as fallback_error:
                    raise SecurityToolkitError(
                        f"Both primary and fallback operations failed: {e} -> {fallback_error}"
                    )
            else:
                raise e

class ErrorRecoveryManager:
    """Manages error recovery strategies."""
    
    def __init__(self):
        self.retry_strategies: Dict[str, RetryStrategy] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.fallback_handlers: Dict[str, FallbackHandler] = {}
    
    def add_retry_strategy(self, name: str, strategy: RetryStrategy) -> None:
        """Add a retry strategy."""
        self.retry_strategies[name] = strategy
    
    def add_circuit_breaker(self, name: str, circuit_breaker: CircuitBreaker) -> None:
        """Add a circuit breaker."""
        self.circuit_breakers[name] = circuit_breaker
    
    def add_fallback_handler(self, name: str, handler: FallbackHandler) -> None:
        """Add a fallback handler."""
        self.fallback_handlers[name] = handler
    
    async def execute_with_recovery(self, operation: Callable, strategy_name: str, 
                                  *args, **kwargs) -> Any:
        """Execute operation with specified recovery strategy."""
        if strategy_name in self.retry_strategies:
            return await self.retry_strategies[strategy_name].execute(operation, *args, **kwargs)
        elif strategy_name in self.circuit_breakers:
            return await self.circuit_breakers[strategy_name].execute(operation, *args, **kwargs)
        elif strategy_name in self.fallback_handlers:
            return await self.fallback_handlers[strategy_name].execute(operation, *args, **kwargs)
        else:
            raise ValueError(f"Unknown recovery strategy: {strategy_name}")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def handle_security_error(error: Exception, context: Optional[ErrorContext] = None) -> None:
    """Global error handler function."""
    handler = ErrorHandler()
    handler.handle_error(error, context)

def log_error(error: Exception, level: int = logging.ERROR, **kwargs) -> None:
    """Log an error with optional context."""
    logger = logging.getLogger(__name__)
    message = f"[{error.__class__.__name__}] {error}"
    
    if kwargs:
        message += f" | Context: {kwargs}"
    
    logger.log(level, message)

def format_error_message(error: Exception) -> str:
    """Format error message for display."""
    if isinstance(error, SecurityToolkitError):
        return f"[{error.error_code}] {error.message}"
    else:
        return f"[{error.__class__.__name__}] {error}"

def create_error_context(operation: str, module: str, function: str, **kwargs) -> ErrorContext:
    """Create error context with current information."""
    return ErrorContext(
        operation=operation,
        module=module,
        function=function,
        **kwargs
    )

# ============================================================================
# DECORATORS
# ============================================================================

def error_handler(error_types: Optional[List[Type[Exception]]] = None):
    """Decorator for automatic error handling."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if error_types is None or any(isinstance(e, t) for t in error_types):
                    context = create_error_context(
                        operation=func.__name__,
                        module=func.__module__,
                        function=func.__name__
                    )
                    handle_security_error(e, context)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_types is None or any(isinstance(e, t) for t in error_types):
                    context = create_error_context(
                        operation=func.__name__,
                        module=func.__module__,
                        function=func.__name__
                    )
                    handle_security_error(e, context)
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator for automatic retry on error."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            strategy = RetryStrategy(max_retries=max_retries, base_delay=delay)
            return await strategy.execute(func, *args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            strategy = RetryStrategy(max_retries=max_retries, base_delay=delay)
            return strategy.execute(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

@contextmanager
def error_context(operation: str, module: str, function: str, **kwargs):
    """Context manager for error handling."""
    context = create_error_context(operation, module, function, **kwargs)
    try:
        yield context
    except Exception as e:
        handle_security_error(e, context)
        raise 