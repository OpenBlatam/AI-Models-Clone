from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .error_handling import (
from .validation import (
from .logging import (
from .monitoring import (
from .guard_clauses import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Core Module

Provides core error handling, validation, logging, monitoring, and guard clauses for the cybersecurity toolkit.
"""

    # Base Exceptions
    SecurityToolkitError,
    ValidationError,
    ConfigurationError,
    NetworkError,
    CryptoError,
    ScanError,
    AttackError,
    ReportError,
    
    # Specific Exceptions
    TargetValidationError,
    PortValidationError,
    CredentialValidationError,
    PayloadValidationError,
    TimeoutError,
    ConnectionError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ResourceNotFoundError,
    
    # Error Handlers
    ErrorHandler,
    ErrorContext,
    ErrorSeverity,
    ErrorCategory,
    handle_security_error,
    log_error,
    format_error_message,
    create_error_context,
    
    # Error Recovery
    RetryStrategy,
    CircuitBreaker,
    FallbackHandler,
    ErrorRecoveryManager
)

    # Validators
    BaseValidator,
    TargetValidator,
    PortValidator,
    CredentialValidator,
    PayloadValidator,
    ConfigValidator,
    NetworkValidator,
    CryptoValidator,
    
    # Validation Rules
    ValidationRule,
    ValidationResult,
    ValidationContext,
    ValidationLevel,
    ValidationMode,
    
    # Validation Schemas
    ValidationSchema,
    FieldValidator,
    CustomValidator,
    CompositeValidator,
    
    # Validation Utilities
    validate_target,
    validate_port,
    validate_credentials,
    validate_payload,
    validate_config,
    validate_network_target,
    validate_crypto_params
)

    # Logging Components
    SecurityLogger,
    LogLevel,
    LogFormat,
    LogHandler,
    StructuredLogger,
    
    # Logging Configuration
    LogConfig,
    LogContext,
    LogMetadata,
    LogFilter,
    
    # Logging Utilities
    setup_logging,
    get_logger,
    log_operation,
    log_security_event,
    log_performance_metrics
)

    # Monitoring Components
    PerformanceMonitor,
    HealthChecker,
    MetricsCollector,
    AlertManager,
    
    # Monitoring Types
    MetricType,
    HealthStatus,
    AlertLevel,
    AlertChannel,
    
    # Monitoring Utilities
    track_performance,
    check_health,
    collect_metrics,
    send_alert,
    monitor_operation
)

    # Guard Clause Types
    GuardType,
    GuardSeverity,
    
    # Guard Clause Decorators
    guard_against_none,
    guard_against_empty,
    guard_against_invalid_type,
    guard_against_invalid_range,
    guard_against_invalid_format,
    guard_against_timeout,
    guard_against_rate_limit,
    
    # Guard Clause Utilities
    guard_target,
    guard_port,
    guard_credentials,
    guard_payload,
    guard_config,
    guard_network_params,
    guard_crypto_params,
    
    # Composite Guard Clauses
    guard_scan_parameters,
    guard_attack_parameters,
    guard_report_parameters,
    
    # Guard Clause Context
    GuardContext,
    
    # Guard Clause Utilities
    apply_guards,
    guard_function_signature
)

__all__ = [
    # Error Handling
    "SecurityToolkitError",
    "ValidationError",
    "ConfigurationError",
    "NetworkError",
    "CryptoError",
    "ScanError",
    "AttackError",
    "ReportError",
    "TargetValidationError",
    "PortValidationError",
    "CredentialValidationError",
    "PayloadValidationError",
    "TimeoutError",
    "ConnectionError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "ResourceNotFoundError",
    "ErrorHandler",
    "ErrorContext",
    "ErrorSeverity",
    "ErrorCategory",
    "handle_security_error",
    "log_error",
    "format_error_message",
    "create_error_context",
    "RetryStrategy",
    "CircuitBreaker",
    "FallbackHandler",
    "ErrorRecoveryManager",
    
    # Validation
    "BaseValidator",
    "TargetValidator",
    "PortValidator",
    "CredentialValidator",
    "PayloadValidator",
    "ConfigValidator",
    "NetworkValidator",
    "CryptoValidator",
    "ValidationRule",
    "ValidationResult",
    "ValidationContext",
    "ValidationLevel",
    "ValidationMode",
    "ValidationSchema",
    "FieldValidator",
    "CustomValidator",
    "CompositeValidator",
    "validate_target",
    "validate_port",
    "validate_credentials",
    "validate_payload",
    "validate_config",
    "validate_network_target",
    "validate_crypto_params",
    
    # Logging
    "SecurityLogger",
    "LogLevel",
    "LogFormat",
    "LogHandler",
    "StructuredLogger",
    "LogConfig",
    "LogContext",
    "LogMetadata",
    "LogFilter",
    "setup_logging",
    "get_logger",
    "log_operation",
    "log_security_event",
    "log_performance_metrics",
    
    # Monitoring
    "PerformanceMonitor",
    "HealthChecker",
    "MetricsCollector",
    "AlertManager",
    "MetricType",
    "HealthStatus",
    "AlertLevel",
    "AlertChannel",
    "track_performance",
    "check_health",
    "collect_metrics",
    "send_alert",
    "monitor_operation",
    
    # Guard Clauses
    "GuardType",
    "GuardSeverity",
    "guard_against_none",
    "guard_against_empty",
    "guard_against_invalid_type",
    "guard_against_invalid_range",
    "guard_against_invalid_format",
    "guard_against_timeout",
    "guard_against_rate_limit",
    "guard_target",
    "guard_port",
    "guard_credentials",
    "guard_payload",
    "guard_config",
    "guard_network_params",
    "guard_crypto_params",
    "guard_scan_parameters",
    "guard_attack_parameters",
    "guard_report_parameters",
    "GuardContext",
    "apply_guards",
    "guard_function_signature"
] 