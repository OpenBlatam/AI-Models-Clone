#!/usr/bin/env python3
"""
Logging Integration for Video-OpusClip
Integrates structured logging with error handling and validation systems
"""

import asyncio
import functools
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, Type
from contextlib import contextmanager

from .structured_logging import (
    StructuredLogger, get_logger, log_function_call, log_errors,
    LogContext, LogParameters, ErrorDetails, PerformanceMetrics, StructuredLogEntry
)
from .custom_exceptions import VideoOpusClipException
from .error_handlers import handle_errors, error_context
from .validation import validate_input
from .guard_clauses import validate_scan_target_early, validate_scan_configuration_early
from .early_returns import validate_scan_inputs_early_return


# ============================================================================
# INTEGRATED LOGGING DECORATORS
# ============================================================================

def comprehensive_logging(
    logger: Optional[StructuredLogger] = None,
    log_parameters: bool = True,
    log_performance: bool = True,
    log_errors: bool = True,
    validate_inputs: bool = True,
    use_guard_clauses: bool = True,
    use_early_returns: bool = True
):
    """
    Comprehensive logging decorator that integrates all logging features
    
    Args:
        logger: Structured logger instance
        log_parameters: Whether to log function parameters
        log_performance: Whether to track performance
        log_errors: Whether to log errors
        validate_inputs: Whether to validate inputs
        use_guard_clauses: Whether to use guard clauses
        use_early_returns: Whether to use early returns
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get logger
            log_instance = logger or get_logger()
            
            # Log function entry with parameters
            if log_parameters:
                log_instance.info(
                    f"Function {func.__name__} called",
                    *args,
                    **kwargs,
                    tags=['function_call', 'entry', 'sync']
                )
            
            # Input validation
            if validate_inputs:
                try:
                    # Validate inputs based on function signature
                    validated_args, validated_kwargs = _validate_function_inputs(
                        func, args, kwargs, log_instance
                    )
                    args, kwargs = validated_args, validated_kwargs
                except Exception as e:
                    log_instance.error(
                        f"Input validation failed for {func.__name__}",
                        error=e,
                        *args,
                        **kwargs,
                        tags=['validation', 'error', 'input']
                    )
                    raise
            
            # Guard clauses
            if use_guard_clauses:
                try:
                    args, kwargs = _apply_guard_clauses(
                        func, args, kwargs, log_instance
                    )
                except Exception as e:
                    log_instance.error(
                        f"Guard clause validation failed for {func.__name__}",
                        error=e,
                        *args,
                        **kwargs,
                        tags=['guard_clauses', 'error']
                    )
                    raise
            
            # Early returns
            if use_early_returns:
                try:
                    early_result = _check_early_returns(
                        func, args, kwargs, log_instance
                    )
                    if early_result is not None:
                        log_instance.info(
                            f"Early return from {func.__name__}",
                            result=early_result,
                            tags=['early_return', 'success']
                        )
                        return early_result
                except Exception as e:
                    log_instance.error(
                        f"Early return check failed for {func.__name__}",
                        error=e,
                        *args,
                        **kwargs,
                        tags=['early_returns', 'error']
                    )
                    raise
            
            # Performance tracking
            if log_performance:
                with log_instance.performance_tracking(func.__name__):
                    try:
                        result = func(*args, **kwargs)
                        
                        # Log successful completion
                        log_instance.info(
                            f"Function {func.__name__} completed successfully",
                            result=result,
                            tags=['function_call', 'success', 'sync']
                        )
                        
                        return result
                        
                    except Exception as e:
                        # Log error
                        if log_errors:
                            log_instance.error(
                                f"Function {func.__name__} failed",
                                error=e,
                                *args,
                                **kwargs,
                                tags=['function_call', 'error', 'sync']
                            )
                        raise
            else:
                try:
                    result = func(*args, **kwargs)
                    
                    # Log successful completion
                    log_instance.info(
                        f"Function {func.__name__} completed successfully",
                        result=result,
                        tags=['function_call', 'success', 'sync']
                    )
                    
                    return result
                    
                except Exception as e:
                    # Log error
                    if log_errors:
                        log_instance.error(
                            f"Function {func.__name__} failed",
                            error=e,
                            *args,
                            **kwargs,
                            tags=['function_call', 'error', 'sync']
                        )
                    raise
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get logger
            log_instance = logger or get_logger()
            
            # Log function entry with parameters
            if log_parameters:
                log_instance.info(
                    f"Async function {func.__name__} called",
                    *args,
                    **kwargs,
                    tags=['function_call', 'entry', 'async']
                )
            
            # Input validation
            if validate_inputs:
                try:
                    # Validate inputs based on function signature
                    validated_args, validated_kwargs = _validate_function_inputs(
                        func, args, kwargs, log_instance
                    )
                    args, kwargs = validated_args, validated_kwargs
                except Exception as e:
                    log_instance.error(
                        f"Input validation failed for {func.__name__}",
                        error=e,
                        *args,
                        **kwargs,
                        tags=['validation', 'error', 'input']
                    )
                    raise
            
            # Guard clauses
            if use_guard_clauses:
                try:
                    args, kwargs = _apply_guard_clauses(
                        func, args, kwargs, log_instance
                    )
                except Exception as e:
                    log_instance.error(
                        f"Guard clause validation failed for {func.__name__}",
                        error=e,
                        *args,
                        **kwargs,
                        tags=['guard_clauses', 'error']
                    )
                    raise
            
            # Early returns
            if use_early_returns:
                try:
                    early_result = await _check_async_early_returns(
                        func, args, kwargs, log_instance
                    )
                    if early_result is not None:
                        log_instance.info(
                            f"Early return from {func.__name__}",
                            result=early_result,
                            tags=['early_return', 'success', 'async']
                        )
                        return early_result
                except Exception as e:
                    log_instance.error(
                        f"Early return check failed for {func.__name__}",
                        error=e,
                        *args,
                        **kwargs,
                        tags=['early_returns', 'error', 'async']
                    )
                    raise
            
            # Performance tracking
            if log_performance:
                with log_instance.performance_tracking(func.__name__):
                    try:
                        result = await func(*args, **kwargs)
                        
                        # Log successful completion
                        log_instance.info(
                            f"Async function {func.__name__} completed successfully",
                            result=result,
                            tags=['function_call', 'success', 'async']
                        )
                        
                        return result
                        
                    except Exception as e:
                        # Log error
                        if log_errors:
                            log_instance.error(
                                f"Async function {func.__name__} failed",
                                error=e,
                                *args,
                                **kwargs,
                                tags=['function_call', 'error', 'async']
                            )
                        raise
            else:
                try:
                    result = await func(*args, **kwargs)
                    
                    # Log successful completion
                    log_instance.info(
                        f"Async function {func.__name__} completed successfully",
                        result=result,
                        tags=['function_call', 'success', 'async']
                    )
                    
                    return result
                    
                except Exception as e:
                    # Log error
                    if log_errors:
                        log_instance.error(
                            f"Async function {func.__name__} failed",
                            error=e,
                            *args,
                            **kwargs,
                            tags=['function_call', 'error', 'async']
                        )
                    raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def _validate_function_inputs(
    func: Callable,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    logger: StructuredLogger
) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
    """Validate function inputs based on function signature"""
    import inspect
    
    # Get function signature
    sig = inspect.signature(func)
    parameters = sig.parameters
    
    # Create validation rules based on type hints
    validation_rules = {}
    
    for name, param in parameters.items():
        if param.annotation != inspect.Parameter.empty:
            # Convert type hints to validation rules
            if param.annotation == str:
                validation_rules[name] = {'type': 'string', 'required': True}
            elif param.annotation == int:
                validation_rules[name] = {'type': 'integer', 'required': True}
            elif param.annotation == float:
                validation_rules[name] = {'type': 'float', 'required': True}
            elif param.annotation == bool:
                validation_rules[name] = {'type': 'boolean', 'required': True}
            elif hasattr(param.annotation, '__origin__') and param.annotation.__origin__ == list:
                validation_rules[name] = {'type': 'list', 'required': True}
            elif hasattr(param.annotation, '__origin__') and param.annotation.__origin__ == dict:
                validation_rules[name] = {'type': 'dict', 'required': True}
    
    # Validate inputs
    validated_data = {}
    
    # Validate positional arguments
    for i, (name, param) in enumerate(parameters.items()):
        if i < len(args):
            validated_data[name] = args[i]
        elif name in kwargs:
            validated_data[name] = kwargs[name]
        elif param.default != inspect.Parameter.empty:
            validated_data[name] = param.default
        elif param.kind == inspect.Parameter.VAR_POSITIONAL:
            # Handle *args
            validated_data[name] = args[i:]
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            # Handle **kwargs
            validated_data[name] = kwargs
    
    # Apply validation
    if validation_rules:
        try:
            validated_data = validate_input(validated_data, validation_rules)
        except Exception as e:
            logger.warning(
                f"Input validation warning for {func.__name__}",
                error=str(e),
                validation_rules=validation_rules,
                tags=['validation', 'warning']
            )
    
    # Reconstruct args and kwargs
    new_args = []
    new_kwargs = {}
    
    for name, param in parameters.items():
        if name in validated_data:
            if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                new_args.append(validated_data[name])
            elif param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                if len(new_args) < param.default if param.default != inspect.Parameter.empty else 0:
                    new_args.append(validated_data[name])
                else:
                    new_kwargs[name] = validated_data[name]
            elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                new_kwargs[name] = validated_data[name]
            elif param.kind == inspect.Parameter.VAR_POSITIONAL:
                new_args.extend(validated_data[name])
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                new_kwargs.update(validated_data[name])
    
    return tuple(new_args), new_kwargs


def _apply_guard_clauses(
    func: Callable,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    logger: StructuredLogger
) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
    """Apply guard clauses based on function name and parameters"""
    func_name = func.__name__.lower()
    
    # Apply domain-specific guard clauses
    if 'scan' in func_name:
        if args and isinstance(args[0], dict):
            # Apply scan target guard clauses
            validated_target = validate_scan_target_early(args[0])
            if validated_target is None:
                logger.warning(
                    f"Guard clause failed for scan target in {func.__name__}",
                    target=args[0],
                    tags=['guard_clauses', 'scan', 'warning']
                )
                raise ValueError("Invalid scan target")
            args = (validated_target,) + args[1:]
        
        if len(args) > 1 and isinstance(args[1], dict):
            # Apply scan configuration guard clauses
            validated_config = validate_scan_configuration_early(args[1])
            if validated_config is None:
                logger.warning(
                    f"Guard clause failed for scan configuration in {func.__name__}",
                    config=args[1],
                    tags=['guard_clauses', 'scan', 'warning']
                )
                raise ValueError("Invalid scan configuration")
            args = args[:1] + (validated_config,) + args[2:]
    
    elif 'enum' in func_name:
        # Apply enumeration guard clauses
        if args and isinstance(args[0], str):
            logger.debug(
                f"Applying enumeration guard clauses for {func.__name__}",
                target=args[0],
                tags=['guard_clauses', 'enumeration', 'debug']
            )
    
    elif 'attack' in func_name:
        # Apply attack guard clauses
        if args and isinstance(args[0], str):
            logger.debug(
                f"Applying attack guard clauses for {func.__name__}",
                target=args[0],
                tags=['guard_clauses', 'attack', 'debug']
            )
    
    return args, kwargs


def _check_early_returns(
    func: Callable,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    logger: StructuredLogger
) -> Optional[Any]:
    """Check for early returns based on function name and parameters"""
    func_name = func.__name__.lower()
    
    # Apply domain-specific early returns
    if 'scan' in func_name:
        if args and isinstance(args[0], dict):
            try:
                # Apply scan input validation with early returns
                validated_config = validate_scan_inputs_early_return(
                    args[0], 
                    args[1] if len(args) > 1 else 'port_scan'
                )
                logger.debug(
                    f"Early return validation passed for {func.__name__}",
                    config=validated_config,
                    tags=['early_returns', 'scan', 'debug']
                )
            except Exception as e:
                logger.warning(
                    f"Early return validation failed for {func.__name__}",
                    error=str(e),
                    tags=['early_returns', 'scan', 'warning']
                )
                return {
                    "success": False,
                    "error": str(e),
                    "function": func.__name__
                }
    
    return None


async def _check_async_early_returns(
    func: Callable,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    logger: StructuredLogger
) -> Optional[Any]:
    """Check for early returns in async functions"""
    func_name = func.__name__.lower()
    
    # Apply domain-specific early returns for async functions
    if 'scan' in func_name:
        if args and isinstance(args[0], dict):
            try:
                # Simulate async early return check
                await asyncio.sleep(0.001)  # Minimal delay for async context
                
                # Check if target is unreachable
                target = args[0].get('host', '')
                if target == 'unreachable.example.com':
                    logger.warning(
                        f"Early return: Target is unreachable in {func.__name__}",
                        target=target,
                        tags=['early_returns', 'scan', 'async', 'warning']
                    )
                    return {
                        "success": False,
                        "error": "Target is unreachable",
                        "target": target,
                        "function": func.__name__
                    }
                
                logger.debug(
                    f"Async early return validation passed for {func.__name__}",
                    target=target,
                    tags=['early_returns', 'scan', 'async', 'debug']
                )
                
            except Exception as e:
                logger.warning(
                    f"Async early return validation failed for {func.__name__}",
                    error=str(e),
                    tags=['early_returns', 'scan', 'async', 'warning']
                )
                return {
                    "success": False,
                    "error": str(e),
                    "function": func.__name__
                }
    
    return None


# ============================================================================
# DOMAIN-SPECIFIC LOGGING INTEGRATIONS
# ============================================================================

class ScanningLogger:
    """Specialized logger for scanning operations"""
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        self.logger = logger or get_logger(name="scanning")
    
    @comprehensive_logging()
    def log_scan_start(self, target: Dict[str, Any], scan_type: str) -> None:
        """Log scan start with comprehensive context"""
        self.logger.info(
            f"Starting {scan_type} scan",
            target=target,
            scan_type=scan_type,
            tags=['scanning', 'start']
        )
    
    @comprehensive_logging()
    def log_scan_progress(self, target: str, progress: float, current_port: Optional[int] = None) -> None:
        """Log scan progress"""
        self.logger.info(
            f"Scan progress: {progress:.1f}%",
            target=target,
            progress=progress,
            current_port=current_port,
            tags=['scanning', 'progress']
        )
    
    @comprehensive_logging()
    def log_scan_result(self, target: str, results: Dict[str, Any], scan_type: str) -> None:
        """Log scan results"""
        self.logger.info(
            f"Scan completed for {target}",
            target=target,
            results=results,
            scan_type=scan_type,
            tags=['scanning', 'complete', 'success']
        )
    
    @comprehensive_logging()
    def log_scan_error(self, target: str, error: Exception, scan_type: str) -> None:
        """Log scan error"""
        self.logger.error(
            f"Scan failed for {target}",
            error=error,
            target=target,
            scan_type=scan_type,
            tags=['scanning', 'error']
        )


class EnumerationLogger:
    """Specialized logger for enumeration operations"""
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        self.logger = logger or get_logger(name="enumeration")
    
    @comprehensive_logging()
    def log_enumeration_start(self, target: str, enum_type: str) -> None:
        """Log enumeration start"""
        self.logger.info(
            f"Starting {enum_type} enumeration",
            target=target,
            enum_type=enum_type,
            tags=['enumeration', 'start']
        )
    
    @comprehensive_logging()
    def log_enumeration_result(self, target: str, results: Dict[str, Any], enum_type: str) -> None:
        """Log enumeration results"""
        self.logger.info(
            f"Enumeration completed for {target}",
            target=target,
            results=results,
            enum_type=enum_type,
            tags=['enumeration', 'complete', 'success']
        )
    
    @comprehensive_logging()
    def log_enumeration_error(self, target: str, error: Exception, enum_type: str) -> None:
        """Log enumeration error"""
        self.logger.error(
            f"Enumeration failed for {target}",
            error=error,
            target=target,
            enum_type=enum_type,
            tags=['enumeration', 'error']
        )


class AttackLogger:
    """Specialized logger for attack operations"""
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        self.logger = logger or get_logger(name="attack")
    
    @comprehensive_logging()
    def log_attack_start(self, target: str, attack_type: str) -> None:
        """Log attack start"""
        self.logger.info(
            f"Starting {attack_type} attack",
            target=target,
            attack_type=attack_type,
            tags=['attack', 'start']
        )
    
    @comprehensive_logging()
    def log_attack_progress(self, target: str, progress: float, attempts: int) -> None:
        """Log attack progress"""
        self.logger.info(
            f"Attack progress: {progress:.1f}%",
            target=target,
            progress=progress,
            attempts=attempts,
            tags=['attack', 'progress']
        )
    
    @comprehensive_logging()
    def log_attack_success(self, target: str, credentials: Dict[str, str], attack_type: str) -> None:
        """Log successful attack"""
        self.logger.info(
            f"Attack successful for {target}",
            target=target,
            credentials=credentials,
            attack_type=attack_type,
            tags=['attack', 'success']
        )
    
    @comprehensive_logging()
    def log_attack_failure(self, target: str, error: Exception, attack_type: str) -> None:
        """Log failed attack"""
        self.logger.error(
            f"Attack failed for {target}",
            error=error,
            target=target,
            attack_type=attack_type,
            tags=['attack', 'failure']
        )


class SecurityLogger:
    """Specialized logger for security operations"""
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        self.logger = logger or get_logger(name="security")
    
    @comprehensive_logging()
    def log_authentication_attempt(self, username: str, success: bool, method: str = "password") -> None:
        """Log authentication attempt"""
        level = "info" if success else "warning"
        message = f"Authentication {'successful' if success else 'failed'}"
        
        getattr(self.logger, level)(
            message,
            username=username,
            success=success,
            method=method,
            tags=['security', 'authentication', 'success' if success else 'failure']
        )
    
    @comprehensive_logging()
    def log_authorization_check(self, user_id: str, resource: str, action: str, authorized: bool) -> None:
        """Log authorization check"""
        level = "info" if authorized else "warning"
        message = f"Authorization {'granted' if authorized else 'denied'}"
        
        getattr(self.logger, level)(
            message,
            user_id=user_id,
            resource=resource,
            action=action,
            authorized=authorized,
            tags=['security', 'authorization', 'granted' if authorized else 'denied']
        )
    
    @comprehensive_logging()
    def log_security_violation(self, violation_type: str, details: Dict[str, Any]) -> None:
        """Log security violation"""
        self.logger.warning(
            f"Security violation detected: {violation_type}",
            violation_type=violation_type,
            details=details,
            tags=['security', 'violation', 'detected']
        )


# ============================================================================
# CONTEXT MANAGERS
# ============================================================================

@contextmanager
def logging_context(
    logger: StructuredLogger,
    operation: str,
    **context_data
):
    """Context manager for logging operations with context"""
    # Set context
    with logger.context(**context_data):
        logger.info(
            f"Starting {operation}",
            operation=operation,
            **context_data,
            tags=['context', 'start']
        )
        
        try:
            yield logger
        except Exception as e:
            logger.error(
                f"Error in {operation}",
                error=e,
                operation=operation,
                **context_data,
                tags=['context', 'error']
            )
            raise
        finally:
            logger.info(
                f"Completed {operation}",
                operation=operation,
                **context_data,
                tags=['context', 'complete']
            )


@contextmanager
def performance_logging_context(
    logger: StructuredLogger,
    operation: str,
    **context_data
):
    """Context manager for performance logging with context"""
    with logger.context(**context_data):
        with logger.performance_tracking(operation):
            logger.info(
                f"Starting performance tracking for {operation}",
                operation=operation,
                **context_data,
                tags=['performance', 'start']
            )
            
            try:
                yield logger
            except Exception as e:
                logger.error(
                    f"Error in {operation}",
                    error=e,
                    operation=operation,
                    **context_data,
                    tags=['performance', 'error']
                )
                raise
            finally:
                logger.info(
                    f"Completed performance tracking for {operation}",
                    operation=operation,
                    **context_data,
                    tags=['performance', 'complete']
                )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example usage of integrated logging
    print("🔗 Integrated Logging Example")
    
    # Create logger
    logger = get_logger(
        name="video_opusclip_integrated",
        log_file="logs/integrated.log",
        error_file="logs/integrated_errors.log",
        performance_file="logs/integrated_performance.log"
    )
    
    # Set request context
    with logger.context(
        request_id="req_integrated_123",
        session_id="sess_integrated_456",
        user_id="user_integrated_789"
    ):
        # Example function with comprehensive logging
        @comprehensive_logging(
            logger=logger,
            log_parameters=True,
            log_performance=True,
            log_errors=True,
            validate_inputs=True,
            use_guard_clauses=True,
            use_early_returns=True
        )
        def example_scan_function(target: Dict[str, Any], scan_type: str) -> Dict[str, Any]:
            """Example scan function with integrated logging"""
            # Simulate scan operation
            import time
            time.sleep(0.1)
            
            # Simulate finding open ports
            open_ports = [80, 443, 22, 21]
            
            return {
                "target": target,
                "scan_type": scan_type,
                "open_ports": open_ports,
                "status": "completed"
            }
        
        # Example async function with comprehensive logging
        @comprehensive_logging(
            logger=logger,
            log_parameters=True,
            log_performance=True,
            log_errors=True,
            validate_inputs=True,
            use_guard_clauses=True,
            use_early_returns=True
        )
        async def example_async_enumeration(target: str, enum_type: str) -> Dict[str, Any]:
            """Example async enumeration function with integrated logging"""
            # Simulate async enumeration
            await asyncio.sleep(0.1)
            
            # Simulate enumeration results
            results = {
                "target": target,
                "enum_type": enum_type,
                "records": ["record1", "record2", "record3"],
                "status": "completed"
            }
            
            return results
        
        # Test functions
        try:
            # Test sync function
            scan_result = example_scan_function(
                target={"host": "192.168.1.100", "port": 80},
                scan_type="port_scan"
            )
            print(f"Scan result: {scan_result}")
            
            # Test async function
            async def test_async():
                enum_result = await example_async_enumeration(
                    target="example.com",
                    enum_type="dns"
                )
                print(f"Enumeration result: {enum_result}")
            
            asyncio.run(test_async())
            
            # Test with context managers
            with logging_context(logger, "test_operation", test_param="value"):
                print("Operation in context")
            
            with performance_logging_context(logger, "test_performance", perf_param="value"):
                import time
                time.sleep(0.05)
                print("Performance tracked operation")
            
            # Test specialized loggers
            scan_logger = ScanningLogger(logger)
            scan_logger.log_scan_start(
                target={"host": "192.168.1.100"},
                scan_type="port_scan"
            )
            scan_logger.log_scan_result(
                target="192.168.1.100",
                results={"open_ports": [80, 443]},
                scan_type="port_scan"
            )
            
            enum_logger = EnumerationLogger(logger)
            enum_logger.log_enumeration_start("example.com", "dns")
            enum_logger.log_enumeration_result(
                "example.com",
                {"records": ["A", "MX", "TXT"]},
                "dns"
            )
            
            attack_logger = AttackLogger(logger)
            attack_logger.log_attack_start("192.168.1.100", "brute_force")
            attack_logger.log_attack_success(
                "192.168.1.100",
                {"username": "admin", "password": "password"},
                "brute_force"
            )
            
            security_logger = SecurityLogger(logger)
            security_logger.log_authentication_attempt("user123", True, "password")
            security_logger.log_authorization_check("user123", "/admin", "read", False)
            security_logger.log_security_violation("brute_force", {"attempts": 100, "ip": "192.168.1.100"})
            
        except Exception as e:
            print(f"Error in example: {e}")
        
        # Get statistics
        stats = logger.get_statistics()
        print(f"\n📊 Integrated Logging Statistics:")
        print(f"Total logs: {stats['total_logs']}")
        print(f"Error logs: {stats['error_logs']}")
        print(f"Performance logs: {stats['performance_logs']}")
        
        if stats['error_analysis']['total_errors'] > 0:
            print(f"Total errors: {stats['error_analysis']['total_errors']}")
        
        if stats['performance_analysis']['total_operations'] > 0:
            perf = stats['performance_analysis']
            print(f"Average execution time: {perf['execution_time']['avg']:.3f}s") 