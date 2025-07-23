"""
Guard Clauses

Comprehensive guard clause utilities for error and edge-case checking.
"""

import asyncio
import inspect
from typing import Any, Optional, Union, List, Dict, Callable, Type, TypeVar
from functools import wraps
from enum import Enum
import re
import ipaddress
from datetime import datetime, timedelta

from .error_handling import (
    SecurityToolkitError, ValidationError, ConfigurationError,
    NetworkError, CryptoError, TimeoutError, ConnectionError
)

# ============================================================================
# GUARD CLAUSE TYPES
# ============================================================================

class GuardType(str, Enum):
    """Types of guard clauses."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RESOURCE = "resource"
    STATE = "state"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    CRYPTO = "crypto"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"

class GuardSeverity(str, Enum):
    """Guard clause severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# ============================================================================
# GUARD CLAUSE DECORATORS
# ============================================================================

def guard_against_none(param_name: str, error_message: Optional[str] = None):
    """Guard against None values."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Check if parameter is None
            if param_name in kwargs and kwargs[param_name] is None:
                msg = error_message or f"Parameter '{param_name}' cannot be None"
                raise ValidationError(msg, field=param_name)
            
            # Check positional arguments
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            if param_name in param_names:
                param_index = param_names.index(param_name)
                if param_index < len(args) and args[param_index] is None:
                    msg = error_message or f"Parameter '{param_name}' cannot be None"
                    raise ValidationError(msg, field=param_name)
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Check if parameter is None
            if param_name in kwargs and kwargs[param_name] is None:
                msg = error_message or f"Parameter '{param_name}' cannot be None"
                raise ValidationError(msg, field=param_name)
            
            # Check positional arguments
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            if param_name in param_names:
                param_index = param_names.index(param_name)
                if param_index < len(args) and args[param_index] is None:
                    msg = error_message or f"Parameter '{param_name}' cannot be None"
                    raise ValidationError(msg, field=param_name)
            
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def guard_against_empty(param_name: str, error_message: Optional[str] = None):
    """Guard against empty values (None, empty string, empty list, empty dict)."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Check if parameter is empty
            if param_name in kwargs:
                value = kwargs[param_name]
                if _is_empty(value):
                    msg = error_message or f"Parameter '{param_name}' cannot be empty"
                    raise ValidationError(msg, field=param_name)
            
            # Check positional arguments
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            if param_name in param_names:
                param_index = param_names.index(param_name)
                if param_index < len(args):
                    value = args[param_index]
                    if _is_empty(value):
                        msg = error_message or f"Parameter '{param_name}' cannot be empty"
                        raise ValidationError(msg, field=param_name)
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Check if parameter is empty
            if param_name in kwargs:
                value = kwargs[param_name]
                if _is_empty(value):
                    msg = error_message or f"Parameter '{param_name}' cannot be empty"
                    raise ValidationError(msg, field=param_name)
            
            # Check positional arguments
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            if param_name in param_names:
                param_index = param_names.index(param_name)
                if param_index < len(args):
                    value = args[param_index]
                    if _is_empty(value):
                        msg = error_message or f"Parameter '{param_name}' cannot be empty"
                        raise ValidationError(msg, field=param_name)
            
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def guard_against_invalid_type(param_name: str, expected_type: Type, error_message: Optional[str] = None):
    """Guard against invalid parameter types."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Check parameter type
            if param_name in kwargs:
                value = kwargs[param_name]
                if not isinstance(value, expected_type):
                    msg = error_message or f"Parameter '{param_name}' must be of type {expected_type.__name__}"
                    raise ValidationError(msg, field=param_name, value=value)
            
            # Check positional arguments
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            if param_name in param_names:
                param_index = param_names.index(param_name)
                if param_index < len(args):
                    value = args[param_index]
                    if not isinstance(value, expected_type):
                        msg = error_message or f"Parameter '{param_name}' must be of type {expected_type.__name__}"
                        raise ValidationError(msg, field=param_name, value=value)
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Check parameter type
            if param_name in kwargs:
                value = kwargs[param_name]
                if not isinstance(value, expected_type):
                    msg = error_message or f"Parameter '{param_name}' must be of type {expected_type.__name__}"
                    raise ValidationError(msg, field=param_name, value=value)
            
            # Check positional arguments
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            if param_name in param_names:
                param_index = param_names.index(param_name)
                if param_index < len(args):
                    value = args[param_index]
                    if not isinstance(value, expected_type):
                        msg = error_message or f"Parameter '{param_name}' must be of type {expected_type.__name__}"
                        raise ValidationError(msg, field=param_name, value=value)
            
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def guard_against_invalid_range(param_name: str, min_value: Optional[Union[int, float]] = None, 
                               max_value: Optional[Union[int, float]] = None, 
                               error_message: Optional[str] = None):
    """Guard against values outside specified range."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Check parameter range
            if param_name in kwargs:
                value = kwargs[param_name]
                if not _is_in_range(value, min_value, max_value):
                    msg = error_message or f"Parameter '{param_name}' must be between {min_value} and {max_value}"
                    raise ValidationError(msg, field=param_name, value=value)
            
            # Check positional arguments
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            if param_name in param_names:
                param_index = param_names.index(param_name)
                if param_index < len(args):
                    value = args[param_index]
                    if not _is_in_range(value, min_value, max_value):
                        msg = error_message or f"Parameter '{param_name}' must be between {min_value} and {max_value}"
                        raise ValidationError(msg, field=param_name, value=value)
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Check parameter range
            if param_name in kwargs:
                value = kwargs[param_name]
                if not _is_in_range(value, min_value, max_value):
                    msg = error_message or f"Parameter '{param_name}' must be between {min_value} and {max_value}"
                    raise ValidationError(msg, field=param_name, value=value)
            
            # Check positional arguments
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            if param_name in param_names:
                param_index = param_names.index(param_name)
                if param_index < len(args):
                    value = args[param_index]
                    if not _is_in_range(value, min_value, max_value):
                        msg = error_message or f"Parameter '{param_name}' must be between {min_value} and {max_value}"
                        raise ValidationError(msg, field=param_name, value=value)
            
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def guard_against_invalid_format(param_name: str, pattern: str, error_message: Optional[str] = None):
    """Guard against invalid format using regex pattern."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Check parameter format
            if param_name in kwargs:
                value = kwargs[param_name]
                if not re.match(pattern, str(value)):
                    msg = error_message or f"Parameter '{param_name}' has invalid format"
                    raise ValidationError(msg, field=param_name, value=value)
            
            # Check positional arguments
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            if param_name in param_names:
                param_index = param_names.index(param_name)
                if param_index < len(args):
                    value = args[param_index]
                    if not re.match(pattern, str(value)):
                        msg = error_message or f"Parameter '{param_name}' has invalid format"
                        raise ValidationError(msg, field=param_name, value=value)
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Check parameter format
            if param_name in kwargs:
                value = kwargs[param_name]
                if not re.match(pattern, str(value)):
                    msg = error_message or f"Parameter '{param_name}' has invalid format"
                    raise ValidationError(msg, field=param_name, value=value)
            
            # Check positional arguments
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            if param_name in param_names:
                param_index = param_names.index(param_name)
                if param_index < len(args):
                    value = args[param_index]
                    if not re.match(pattern, str(value)):
                        msg = error_message or f"Parameter '{param_name}' has invalid format"
                        raise ValidationError(msg, field=param_name, value=value)
            
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def guard_against_timeout(timeout_param: str = "timeout", default_timeout: float = 30.0):
    """Guard against timeout issues."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get timeout value
            timeout = kwargs.get(timeout_param, default_timeout)
            
            # Validate timeout
            if timeout <= 0:
                raise ValidationError(f"Timeout must be positive, got {timeout}", field=timeout_param)
            
            # Execute with timeout
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Operation timed out after {timeout} seconds", timeout)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get timeout value
            timeout = kwargs.get(timeout_param, default_timeout)
            
            # Validate timeout
            if timeout <= 0:
                raise ValidationError(f"Timeout must be positive, got {timeout}", field=timeout_param)
            
            # For sync functions, we can't easily implement timeout without threading
            # Just validate the timeout parameter
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def guard_against_rate_limit(max_calls: int, time_window: float = 60.0):
    """Guard against rate limiting."""
    def decorator(func):
        call_history = []
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Clean old calls
            call_history[:] = [call_time for call_time in call_history 
                             if current_time - call_time < time_window]
            
            # Check rate limit
            if len(call_history) >= max_calls:
                raise SecurityToolkitError(
                    f"Rate limit exceeded: {max_calls} calls per {time_window} seconds",
                    error_code="RATE_LIMIT_ERROR"
                )
            
            # Record call
            call_history.append(current_time)
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Clean old calls
            call_history[:] = [call_time for call_time in call_history 
                             if current_time - call_time < time_window]
            
            # Check rate limit
            if len(call_history) >= max_calls:
                raise SecurityToolkitError(
                    f"Rate limit exceeded: {max_calls} calls per {time_window} seconds",
                    error_code="RATE_LIMIT_ERROR"
                )
            
            # Record call
            call_history.append(current_time)
            
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

# ============================================================================
# GUARD CLAUSE UTILITIES
# ============================================================================

def _is_empty(value: Any) -> bool:
    """Check if value is empty."""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, tuple, dict, set)) and len(value) == 0:
        return True
    return False

def _is_in_range(value: Any, min_value: Optional[Union[int, float]], 
                 max_value: Optional[Union[int, float]]) -> bool:
    """Check if value is within specified range."""
    if not isinstance(value, (int, float)):
        return False
    
    if min_value is not None and value < min_value:
        return False
    
    if max_value is not None and value > max_value:
        return False
    
    return True

def guard_target(target: str) -> None:
    """Guard against invalid target."""
    if target is None:
        raise ValidationError("Target cannot be None", field="target")
    
    if not isinstance(target, str):
        raise ValidationError("Target must be a string", field="target", value=target)
    
    if not target.strip():
        raise ValidationError("Target cannot be empty", field="target")
    
    # Check for valid IP, domain, or URL format
    if not _is_valid_target_format(target):
        raise ValidationError(f"Invalid target format: {target}", field="target", value=target)

def guard_port(port: int) -> None:
    """Guard against invalid port."""
    if port is None:
        raise ValidationError("Port cannot be None", field="port")
    
    if not isinstance(port, int):
        raise ValidationError("Port must be an integer", field="port", value=port)
    
    if not 1 <= port <= 65535:
        raise ValidationError(f"Port must be between 1 and 65535, got {port}", field="port", value=port)

def guard_credentials(credentials: Union[Dict[str, str], str]) -> None:
    """Guard against invalid credentials."""
    if credentials is None:
        raise ValidationError("Credentials cannot be None", field="credentials")
    
    if isinstance(credentials, dict):
        if "username" not in credentials:
            raise ValidationError("Credentials must contain 'username'", field="credentials")
        if "password" not in credentials:
            raise ValidationError("Credentials must contain 'password'", field="credentials")
        
        username = credentials["username"]
        password = credentials["password"]
        
        if not username or not isinstance(username, str):
            raise ValidationError("Username must be a non-empty string", field="username")
        if not password or not isinstance(password, str):
            raise ValidationError("Password must be a non-empty string", field="password")
    
    elif isinstance(credentials, str):
        if ":" not in credentials:
            raise ValidationError("Credential string must be in format 'username:password'", field="credentials")
        
        username, password = credentials.split(":", 1)
        if not username or not password:
            raise ValidationError("Username and password cannot be empty", field="credentials")
    
    else:
        raise ValidationError("Credentials must be a dictionary or string", field="credentials", value=credentials)

def guard_payload(payload: Union[Dict[str, Any], str]) -> None:
    """Guard against invalid payload."""
    if payload is None:
        raise ValidationError("Payload cannot be None", field="payload")
    
    if isinstance(payload, dict):
        if "content" not in payload:
            raise ValidationError("Payload must contain 'content'", field="payload")
        
        content = payload["content"]
        if not content or not isinstance(content, str):
            raise ValidationError("Payload content must be a non-empty string", field="content")
        
        # Check payload size
        content_size = len(content.encode('utf-8'))
        if content_size > 1048576:  # 1MB limit
            raise ValidationError(f"Payload content too large: {content_size} bytes", field="content")
    
    elif isinstance(payload, str):
        if not payload.strip():
            raise ValidationError("Payload cannot be empty", field="payload")
        
        # Check payload size
        payload_size = len(payload.encode('utf-8'))
        if payload_size > 1048576:  # 1MB limit
            raise ValidationError(f"Payload too large: {payload_size} bytes", field="payload")
    
    else:
        raise ValidationError("Payload must be a dictionary or string", field="payload", value=payload)

def guard_config(config: Dict[str, Any]) -> None:
    """Guard against invalid configuration."""
    if config is None:
        raise ValidationError("Configuration cannot be None", field="config")
    
    if not isinstance(config, dict):
        raise ValidationError("Configuration must be a dictionary", field="config", value=config)
    
    # Check for required fields
    required_fields = ["timeout", "retries"]
    for field_name in required_fields:
        if field_name not in config:
            raise ValidationError(f"Configuration missing required field: {field_name}", field=field_name)
    
    # Validate timeout
    timeout = config.get("timeout")
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ValidationError("Configuration timeout must be a positive number", field="timeout", value=timeout)
    
    # Validate retries
    retries = config.get("retries")
    if not isinstance(retries, int) or retries < 0:
        raise ValidationError("Configuration retries must be a non-negative integer", field="retries", value=retries)

def guard_network_params(target: str, port: Optional[int] = None, timeout: Optional[float] = None) -> None:
    """Guard against invalid network parameters."""
    guard_target(target)
    
    if port is not None:
        guard_port(port)
    
    if timeout is not None:
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValidationError("Timeout must be a positive number", field="timeout", value=timeout)

def guard_crypto_params(operation: str, algorithm: Optional[str] = None, data: Optional[str] = None) -> None:
    """Guard against invalid cryptographic parameters."""
    if operation is None:
        raise ValidationError("Operation cannot be None", field="operation")
    
    if not isinstance(operation, str):
        raise ValidationError("Operation must be a string", field="operation", value=operation)
    
    valid_operations = ["hash", "encrypt", "decrypt", "sign", "verify", "key_generation", "key_derivation"]
    if operation not in valid_operations:
        raise ValidationError(f"Invalid operation: {operation}", field="operation", value=operation)
    
    if algorithm is not None:
        if not isinstance(algorithm, str):
            raise ValidationError("Algorithm must be a string", field="algorithm", value=algorithm)
        
        valid_algorithms = [
            "md5", "sha1", "sha256", "sha512", "blake2b", "blake2s",
            "aes_256_gcm", "aes_256_cbc", "aes_128_gcm", "aes_128_cbc",
            "chacha20_poly1305", "rsa_2048", "rsa_4096"
        ]
        if algorithm not in valid_algorithms:
            raise ValidationError(f"Invalid algorithm: {algorithm}", field="algorithm", value=algorithm)
    
    if data is not None:
        if not isinstance(data, str):
            raise ValidationError("Data must be a string", field="data", value=data)
        
        if not data.strip():
            raise ValidationError("Data cannot be empty", field="data")

def _is_valid_target_format(target: str) -> bool:
    """Check if target has valid format."""
    # Check for IP address
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        pass
    
    # Check for domain name
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    if re.match(domain_pattern, target):
        return True
    
    # Check for URL
    url_pattern = r'^https?://[a-zA-Z0-9.-]+'
    if re.match(url_pattern, target):
        return True
    
    # Check for network range
    try:
        ipaddress.ip_network(target, strict=False)
        return True
    except ValueError:
        pass
    
    return False

# ============================================================================
# COMPOSITE GUARD CLAUSES
# ============================================================================

def guard_scan_parameters(target: str, ports: Optional[List[int]] = None, 
                         scan_type: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> None:
    """Guard against invalid scan parameters."""
    guard_target(target)
    
    if ports is not None:
        if not isinstance(ports, list):
            raise ValidationError("Ports must be a list", field="ports", value=ports)
        
        for port in ports:
            guard_port(port)
    
    if scan_type is not None:
        if not isinstance(scan_type, str):
            raise ValidationError("Scan type must be a string", field="scan_type", value=scan_type)
        
        valid_types = ["port_scan", "vulnerability_scan", "network_scan", "web_scan", "ssl_scan"]
        if scan_type not in valid_types:
            raise ValidationError(f"Invalid scan type: {scan_type}", field="scan_type", value=scan_type)
    
    if config is not None:
        guard_config(config)

def guard_attack_parameters(target: str, attack_type: Optional[str] = None,
                           payload: Optional[Union[Dict[str, Any], str]] = None,
                           credentials: Optional[Union[Dict[str, str], str]] = None) -> None:
    """Guard against invalid attack parameters."""
    guard_target(target)
    
    if attack_type is not None:
        if not isinstance(attack_type, str):
            raise ValidationError("Attack type must be a string", field="attack_type", value=attack_type)
        
        valid_types = ["brute_force", "exploit", "dos", "phishing", "sql_injection", "xss"]
        if attack_type not in valid_types:
            raise ValidationError(f"Invalid attack type: {attack_type}", field="attack_type", value=attack_type)
    
    if payload is not None:
        guard_payload(payload)
    
    if credentials is not None:
        guard_credentials(credentials)

def guard_report_parameters(report_format: str, report_level: Optional[str] = None,
                           sections: Optional[List[str]] = None) -> None:
    """Guard against invalid report parameters."""
    if report_format is None:
        raise ValidationError("Report format cannot be None", field="report_format")
    
    if not isinstance(report_format, str):
        raise ValidationError("Report format must be a string", field="report_format", value=report_format)
    
    valid_formats = ["json", "html", "pdf", "csv", "xml", "markdown"]
    if report_format not in valid_formats:
        raise ValidationError(f"Invalid report format: {report_format}", field="report_format", value=report_format)
    
    if report_level is not None:
        if not isinstance(report_level, str):
            raise ValidationError("Report level must be a string", field="report_level", value=report_level)
        
        valid_levels = ["summary", "detailed", "technical", "executive"]
        if report_level not in valid_levels:
            raise ValidationError(f"Invalid report level: {report_level}", field="report_level", value=report_level)
    
    if sections is not None:
        if not isinstance(sections, list):
            raise ValidationError("Sections must be a list", field="sections", value=sections)
        
        valid_sections = ["executive_summary", "methodology", "findings", "vulnerabilities", "recommendations"]
        for section in sections:
            if section not in valid_sections:
                raise ValidationError(f"Invalid section: {section}", field="sections", value=section)

# ============================================================================
# GUARD CLAUSE CONTEXT MANAGER
# ============================================================================

class GuardContext:
    """Context manager for guard clauses."""
    
    def __init__(self, operation: str, module: str, function: str):
        self.operation = operation
        self.module = module
        self.function = function
        self.guards_applied = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log guard failure
            print(f"Guard failure in {self.module}.{self.function}: {exc_val}")
        return False  # Don't suppress exceptions
    
    def apply_guard(self, guard_func: Callable, *args, **kwargs):
        """Apply a guard function."""
        try:
            guard_func(*args, **kwargs)
            self.guards_applied.append(guard_func.__name__)
        except Exception as e:
            # Add context to the error
            e.context = {
                "operation": self.operation,
                "module": self.module,
                "function": self.function,
                "guard": guard_func.__name__
            }
            raise

# ============================================================================
# GUARD CLAUSE UTILITY FUNCTIONS
# ============================================================================

def apply_guards(*guard_functions: Callable) -> Callable:
    """Decorator to apply multiple guard functions."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Apply all guard functions
            for guard_func in guard_functions:
                guard_func(*args, **kwargs)
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Apply all guard functions
            for guard_func in guard_functions:
                guard_func(*args, **kwargs)
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def guard_function_signature(func: Callable) -> Callable:
    """Decorator to guard function signature based on type hints."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Get function signature
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        # Check each parameter
        for param_name, param in sig.parameters.items():
            if param_name in bound_args.arguments:
                value = bound_args.arguments[param_name]
                
                # Check for None if not optional
                if param.annotation != Optional[param.annotation] and value is None:
                    raise ValidationError(f"Parameter '{param_name}' cannot be None", field=param_name)
                
                # Check type if annotation exists
                if param.annotation != inspect.Parameter.empty:
                    if not isinstance(value, param.annotation):
                        raise ValidationError(
                            f"Parameter '{param_name}' must be of type {param.annotation.__name__}",
                            field=param_name,
                            value=value
                        )
        
        return await func(*args, **kwargs)
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Get function signature
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        # Check each parameter
        for param_name, param in sig.parameters.items():
            if param_name in bound_args.arguments:
                value = bound_args.arguments[param_name]
                
                # Check for None if not optional
                if param.annotation != Optional[param.annotation] and value is None:
                    raise ValidationError(f"Parameter '{param_name}' cannot be None", field=param_name)
                
                # Check type if annotation exists
                if param.annotation != inspect.Parameter.empty:
                    if not isinstance(value, param.annotation):
                        raise ValidationError(
                            f"Parameter '{param_name}' must be of type {param.annotation.__name__}",
                            field=param_name,
                            value=value
                        )
        
        return func(*args, **kwargs)
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

# ============================================================================
# IMPORTS FOR TIME MODULE
# ============================================================================

import time 