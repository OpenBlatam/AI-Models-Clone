"""
AI Video System - Core Module

Production-ready core utilities and components for the AI Video system.
Provides a comprehensive set of tools for building robust, scalable,
and maintainable AI video generation applications.
"""

# Core utilities
from .exceptions import (
    AIVideoError,
    PluginError,
    ConfigurationError,
    ValidationError,
    WorkflowError,
    SecurityError,
    PerformanceError
)

from .constants import (
    # System constants
    SYSTEM_NAME,
    VERSION,
    DEFAULT_CONFIG_PATH,
    DEFAULT_LOG_LEVEL,
    
    # Plugin constants
    PLUGIN_TYPES,
    PLUGIN_CATEGORIES,
    PLUGIN_STATUSES,
    
    # Workflow constants
    WORKFLOW_STAGES,
    WORKFLOW_STATUSES,
    WORKFLOW_PRIORITIES,
    
    # Security constants
    SECURITY_LEVELS,
    ENCRYPTION_ALGORITHMS,
    HASH_ALGORITHMS,
    
    # Performance constants
    PERFORMANCE_THRESHOLDS,
    CACHE_TTL_DEFAULTS,
    RATE_LIMIT_DEFAULTS,
    
    # Monitoring constants
    METRIC_TYPES,
    ALERT_SEVERITIES,
    HEALTH_STATUSES
)

from .utils import (
    # File utilities
    ensure_directory,
    safe_filename,
    get_file_extension,
    get_file_size,
    is_valid_file_path,
    
    # Data utilities
    deep_merge,
    flatten_dict,
    unflatten_dict,
    sanitize_data,
    validate_data_types,
    
    # Time utilities
    format_duration,
    parse_duration,
    get_timestamp,
    is_expired,
    
    # Network utilities
    is_valid_url,
    get_domain,
    validate_ip_address,
    check_connectivity,
    
    # System utilities
    get_system_info,
    get_memory_usage,
    get_cpu_usage,
    get_disk_usage,
    
    # Validation utilities
    validate_email,
    validate_phone,
    validate_json,
    validate_uuid,
    
    # Security utilities
    generate_secure_token,
    hash_password,
    verify_password,
    encrypt_data,
    decrypt_data,
    
    # Performance utilities
    measure_time,
    cache_result,
    retry_operation,
    rate_limit,
    
    # Monitoring utilities
    record_metric,
    log_event,
    create_alert,
    check_health
)

# Performance optimization
from .performance import (
    # Performance monitoring
    PerformanceMonitor,
    PerformanceMetrics,
    
    # Caching
    LRUCache,
    get_cache,
    clear_all_caches,
    
    # Connection pooling
    ConnectionPool,
    
    # Rate limiting
    AsyncRateLimiter,
    
    # Performance decorators
    measure_performance,
    cache_result,
    rate_limit,
    
    # Global instances
    monitor as performance_monitor
)

# Security
from .security import (
    # Security configuration
    SecurityConfig,
    
    # Input validation
    InputValidator,
    
    # Encryption
    EncryptionManager,
    
    # Session management
    SessionManager,
    
    # Security auditing
    SecurityAuditor,
    
    # Security decorators
    require_authentication,
    validate_input,
    log_security_event,
    
    # Security utilities
    sanitize_filename,
    validate_ip_address,
    is_suspicious_request,
    
    # Global instances
    security_config,
    input_validator,
    encryption_manager,
    session_manager,
    security_auditor
)

# Async utilities
from .async_utils import (
    # Task management
    AsyncTaskManager,
    AsyncTask,
    
    # Rate limiting
    AsyncRateLimiter,
    
    # Retry mechanism
    AsyncRetry,
    RetryConfig,
    
    # Batch processing
    AsyncBatchProcessor,
    
    # Async cache
    AsyncCache,
    
    # Async context managers
    timeout_context,
    retry_context,
    
    # Async decorators
    async_retry,
    async_timeout,
    async_rate_limit,
    
    # Async utilities
    gather_with_concurrency_limit,
    wait_for_first,
    run_in_executor,
    
    # Global instances
    task_manager,
    default_cache
)

# Monitoring
from .monitoring import (
    # Metrics collection
    MetricsCollector,
    MetricPoint,
    
    # Health checking
    HealthChecker,
    HealthCheck,
    
    # Alert management
    AlertManager,
    Alert,
    
    # Monitoring dashboard
    MonitoringDashboard,
    
    # Built-in health checks
    check_system_resources,
    check_database_connection,
    
    # Monitoring decorators
    monitor_operation,
    alert_on_error,
    
    # Global instances
    metrics_collector,
    health_checker,
    alert_manager,
    monitoring_dashboard
)

# Validation
from .validation import (
    # Schema validation
    SchemaValidator,
    FieldSchema,
    DataType,
    
    # Data validation
    DataValidator,
    
    # Validation results
    ValidationResult,
    ValidationError,
    
    # Validation decorators
    validate_schema,
    validate_input,
    
    # Validation utilities
    validate_email,
    validate_url,
    validate_phone,
    validate_filename,
    sanitize_filename,
    
    # Global instances
    schema_validator,
    data_validator
)

# Logging
from .logging_config import (
    # Logging configuration
    LogConfig,
    LogManager,
    
    # Structured logging
    StructuredFormatter,
    
    # Performance logging
    PerformanceLogger,
    
    # Security logging
    SecurityLogger,
    
    # Logging decorators
    log_function_call,
    log_security_event,
    
    # Logging utilities
    setup_logging,
    get_logger,
    get_performance_logger,
    get_security_logger,
    
    # Global instances
    log_config,
    log_manager,
    main_logger,
    performance_logger,
    security_logger
)

# Re-export commonly used items
__all__ = [
    # Core exceptions
    'AIVideoError', 'PluginError', 'ConfigurationError', 'ValidationError',
    'WorkflowError', 'SecurityError', 'PerformanceError',
    
    # Core constants
    'SYSTEM_NAME', 'VERSION', 'DEFAULT_CONFIG_PATH', 'DEFAULT_LOG_LEVEL',
    'PLUGIN_TYPES', 'PLUGIN_CATEGORIES', 'PLUGIN_STATUSES',
    'WORKFLOW_STAGES', 'WORKFLOW_STATUSES', 'WORKFLOW_PRIORITIES',
    'SECURITY_LEVELS', 'ENCRYPTION_ALGORITHMS', 'HASH_ALGORITHMS',
    'PERFORMANCE_THRESHOLDS', 'CACHE_TTL_DEFAULTS', 'RATE_LIMIT_DEFAULTS',
    'METRIC_TYPES', 'ALERT_SEVERITIES', 'HEALTH_STATUSES',
    
    # Core utilities
    'ensure_directory', 'safe_filename', 'get_file_extension', 'get_file_size',
    'is_valid_file_path', 'deep_merge', 'flatten_dict', 'unflatten_dict',
    'sanitize_data', 'validate_data_types', 'format_duration', 'parse_duration',
    'get_timestamp', 'is_expired', 'is_valid_url', 'get_domain',
    'validate_ip_address', 'check_connectivity', 'get_system_info',
    'get_memory_usage', 'get_cpu_usage', 'get_disk_usage', 'validate_email',
    'validate_phone', 'validate_json', 'validate_uuid', 'generate_secure_token',
    'hash_password', 'verify_password', 'encrypt_data', 'decrypt_data',
    'measure_time', 'cache_result', 'retry_operation', 'rate_limit',
    'record_metric', 'log_event', 'create_alert', 'check_health',
    
    # Performance
    'PerformanceMonitor', 'PerformanceMetrics', 'LRUCache', 'get_cache',
    'clear_all_caches', 'ConnectionPool', 'AsyncRateLimiter', 'measure_performance',
    'cache_result', 'rate_limit', 'performance_monitor',
    
    # Security
    'SecurityConfig', 'InputValidator', 'EncryptionManager', 'SessionManager',
    'SecurityAuditor', 'require_authentication', 'validate_input',
    'log_security_event', 'sanitize_filename', 'validate_ip_address',
    'is_suspicious_request', 'security_config', 'input_validator',
    'encryption_manager', 'session_manager', 'security_auditor',
    
    # Async
    'AsyncTaskManager', 'AsyncTask', 'AsyncRetry', 'RetryConfig',
    'AsyncBatchProcessor', 'AsyncCache', 'timeout_context', 'retry_context',
    'async_retry', 'async_timeout', 'async_rate_limit',
    'gather_with_concurrency_limit', 'wait_for_first', 'run_in_executor',
    'task_manager', 'default_cache',
    
    # Monitoring
    'MetricsCollector', 'MetricPoint', 'HealthChecker', 'HealthCheck',
    'AlertManager', 'Alert', 'MonitoringDashboard', 'check_system_resources',
    'check_database_connection', 'monitor_operation', 'alert_on_error',
    'metrics_collector', 'health_checker', 'alert_manager', 'monitoring_dashboard',
    
    # Validation
    'SchemaValidator', 'FieldSchema', 'DataType', 'DataValidator',
    'ValidationResult', 'ValidationError', 'validate_schema', 'validate_input',
    'validate_email', 'validate_url', 'validate_phone', 'validate_filename',
    'sanitize_filename', 'schema_validator', 'data_validator',
    
    # Logging
    'LogConfig', 'LogManager', 'StructuredFormatter', 'PerformanceLogger',
    'SecurityLogger', 'log_function_call', 'log_security_event',
    'setup_logging', 'get_logger', 'get_performance_logger', 'get_security_logger',
    'log_config', 'log_manager', 'main_logger', 'performance_logger', 'security_logger'
]

# Version information
__version__ = VERSION

# Module initialization
def initialize_core():
    """Initialize core module components."""
    # Setup logging
    setup_logging()
    
    # Start monitoring
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create task for monitoring
            asyncio.create_task(start_monitoring())
        else:
            # Run monitoring in new event loop
            loop.run_until_complete(start_monitoring())
    except Exception as e:
        main_logger.error(f"Failed to start monitoring: {e}")
    
    main_logger.info("AI Video Core module initialized successfully")


def cleanup_core():
    """Cleanup core module resources."""
    import asyncio
    
    async def cleanup():
        # Cleanup all resources
        await cleanup_performance_resources()
        await cleanup_security_resources()
        await cleanup_async_resources()
        await cleanup_monitoring_resources()
        await cleanup_logging_resources()
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create task for cleanup
            asyncio.create_task(cleanup())
        else:
            # Run cleanup in new event loop
            loop.run_until_complete(cleanup())
    except Exception as e:
        main_logger.error(f"Failed to cleanup core resources: {e}")


# Auto-initialize when module is imported
initialize_core()

# Register cleanup on module unload
import atexit
atexit.register(cleanup_core) 