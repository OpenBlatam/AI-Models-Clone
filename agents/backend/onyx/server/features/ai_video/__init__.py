"""
🚀 ULTRA VIDEO AI SYSTEM - MODULAR ARCHITECTURE
===============================================

Sistema modular ultra-optimizado para procesamiento de video AI.

Módulos disponibles:
- core: Modelos y clases principales
- api: APIs y servicios web
- optimization: Optimizaciones de rendimiento
- production: Configuración de producción
- benchmarking: Testing y benchmarking
- config: Configuración del sistema
- utils: Utilidades y helpers
- docs: Documentación
- deployment: Deployment y containerización
- monitoring: Monitoreo y métricas
"""

__version__ = "2.0.0"
__title__ = "Ultra Video AI System"
__description__ = "Sistema modular ultra-optimizado para procesamiento de video AI"

# Importaciones principales
from pathlib import Path

# Metadata
SYSTEM_PATH = Path(__file__).parent
MODULES = [
    "core",
    "api", 
    "optimization",
    "production",
    "benchmarking",
    "config",
    "utils",
    "docs",
    "deployment",
    "monitoring"
]

def get_system_info():
    """Obtener información del sistema."""
    return {
        "title": __title__,
        "version": __version__,
        "description": __description__,
        "modules": MODULES,
        "path": str(SYSTEM_PATH)
    }

def list_modules():
    """Listar módulos disponibles."""
    available_modules = []
    for module_name in MODULES:
        module_path = SYSTEM_PATH / module_name
        if module_path.exists() and module_path.is_dir():
            # Contar archivos Python en el módulo
            python_files = len([f for f in module_path.glob("*.py") if f.name != "__init__.py"])
            available_modules.append({
                "name": module_name,
                "path": str(module_path),
                "files": python_files,
                "has_init": (module_path / "__init__.py").exists()
            })
    return available_modules

def get_module_structure():
    """Obtener estructura completa del sistema."""
    structure = {}
    for module_info in list_modules():
        module_name = module_info["name"]
        module_path = Path(module_info["path"])
        
        files = []
        for py_file in module_path.glob("*.py"):
            if py_file.name != "__init__.py":
                files.append(py_file.name)
        
        structure[module_name] = {
            "description": _get_module_description(module_name),
            "files": files,
            "file_count": len(files)
        }
    
    return structure

def _get_module_description(module_name):
    """Obtener descripción de un módulo."""
    descriptions = {
        "core": "Modelos y clases principales del sistema de Video AI",
        "api": "APIs, servicios web y endpoints",
        "optimization": "Optimizaciones de rendimiento y algoritmos avanzados",
        "production": "Configuración y archivos específicos de producción",
        "benchmarking": "Sistemas de testing, benchmarking y validación",
        "config": "Archivos de configuración del sistema",
        "utils": "Utilidades, helpers y funciones auxiliares",
        "docs": "Documentación del sistema",
        "deployment": "Archivos de deployment y containerización",
        "monitoring": "Monitoreo, métricas y observabilidad"
    }
    return descriptions.get(module_name, "Módulo del sistema")

def verify_system_integrity():
    """Verificar integridad del sistema modular."""
    issues = []
    
    # Verificar que todos los módulos esperados existen
    for module_name in MODULES:
        module_path = SYSTEM_PATH / module_name
        if not module_path.exists():
            issues.append(f"Módulo faltante: {module_name}")
        elif not (module_path / "__init__.py").exists():
            issues.append(f"__init__.py faltante en: {module_name}")
    
    # Verificar backup
    backup_path = SYSTEM_PATH / "backup_original"
    if not backup_path.exists():
        issues.append("Directorio de backup no encontrado")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "modules_found": len(list_modules()),
        "expected_modules": len(MODULES)
    }

# Importaciones de módulos principales (con manejo de errores)
try:
    from . import core
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo core: {e}")

try:
    from . import api
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo api: {e}")

try:
    from . import optimization
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo optimization: {e}")

try:
    from . import production
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo production: {e}")

# Async I/O Optimization System
try:
    from .async_io_optimization import (
        AsyncIOOptimizationSystem,
        AsyncDatabaseManager,
        AsyncRedisManager,
        AsyncHTTPClient,
        AsyncFileManager,
        ConcurrentOperationManager,
        BlockingOperationDetector,
        AsyncConverter,
        async_io_optimized,
        non_blocking
    )
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo async_io_optimization: {e}")

# Async Conversion Examples
try:
    from .async_conversion_examples import (
        DatabaseConversionExamples,
        HTTPConversionExamples,
        FileIOConversionExamples,
        CacheConversionExamples,
        ThirdPartyConversionExamples,
        AsyncConversionSystem
    )
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo async_conversion_examples: {e}")

# Enhanced Caching System
try:
    from .enhanced_caching_system import (
        EnhancedCachingSystem,
        CacheConfig,
        CacheType,
        EvictionPolicy,
        MemoryCache,
        RedisCache,
        PredictiveCache,
        StaticDataManager,
        FrequentDataManager,
        CacheWarmer,
        CacheInvalidator
    )
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo enhanced_caching_system: {e}")

# Pydantic Serialization Optimization System
try:
    from .pydantic_serialization_optimization import (
        OptimizedSerializer,
        SerializationCache,
        BatchSerializationOptimizer,
        SerializationPerformanceMonitor,
        SerializationConfig,
        SerializationFormat,
        CompressionType,
        CustomSerializers,
        CompressionUtils,
        SerializationStats,
        optimized_serialization,
        optimized_deserialization
    )
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo pydantic_serialization_optimization: {e}")

# Pydantic Serialization Examples
try:
    from .pydantic_serialization_examples import (
        OptimizedVideoModel,
        VideoProcessingResult,
        VideoBatchRequest,
        VideoStatus,
        VideoQuality,
        SerializationCache,
        OptimizedSerializer,
        BatchSerializationOptimizer,
        SerializationPerformanceMonitor
    )
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo pydantic_serialization_examples: {e}")

# Caching Integration Example
try:
    from .caching_integration_example import (
        AIVideoCacheIntegration
    )
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo caching_integration_example: {e}")

# Project Initialization System
try:
    from .project_init import (
        ProblemDefinition,
        DatasetInfo,
        DatasetAnalyzer,
        ProjectInitializer,
        create_project_from_template
    )
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo project_init: {e}")

# Configuración de logging para el sistema
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"🚀 {__title__} v{__version__} - Sistema modular inicializado")

# Verificar integridad al importar
integrity_check = verify_system_integrity()
if not integrity_check["is_valid"]:
    logger.warning(f"⚠️ Problemas de integridad encontrados: {integrity_check['issues']}")
else:
    logger.info(f"✅ Sistema modular verificado - {integrity_check['modules_found']} módulos disponibles")

"""
AI Video System - Gradio Integration

This module provides a comprehensive Gradio web interface for the AI Video system,
enabling users to generate, style, optimize, and monitor AI-powered videos through
an intuitive web interface with robust error handling and input validation.
"""

# Gradio Error Handling and Input Validation
from .gradio_error_handling import (
    GradioErrorHandler,
    GradioInputValidator,
    InputValidationRule,
    ErrorSeverity,
    ErrorCategory,
    GradioErrorInfo,
    gradio_error_handler,
    gradio_input_validator,
)

# Pydantic Validation System
from .pydantic_schemas import (
    # Enumerations
    VideoStatus,
    VideoFormat,
    QualityLevel,
    ProcessingPriority,
    ModelType,
    
    # Input Models
    VideoGenerationInput,
    BatchGenerationInput,
    VideoEditInput,
    
    # Response Models
    VideoMetadata,
    VideoGenerationResponse,
    BatchGenerationResponse,
    VideoEditResponse,
    
    # System Models
    SystemHealth,
    UserQuota,
    APIError,
    
    # Utilities
    ValidationUtils,
    create_video_id,
    create_batch_id,
    create_error_response,
    create_success_response
)

from .pydantic_validation import (
    ValidationConfig,
    PydanticValidationMiddleware,
    validate_request,
    validate_response,
    validate_input_output,
    ValidationUtils as ValidationUtilsMiddleware,
    ValidationPerformanceMonitor,
    create_validation_middleware,
    create_performance_monitor
)

# Gradio Application
from .gradio_app_example import (
    AIVideoGradioApp,
    create_gradio_app,
    create_simple_interface
)

# Version Control System
from .version_control import (
    GitManager,
    ConfigVersioning,
    ChangeTracker,
    VersionControlSystem,
    create_version_control_system,
    quick_version_config,
    start_experiment,
    finish_experiment
)

# Error Handling and Edge Case Management
try:
    from .error_handling import (
        AIVideoError, ErrorCategory, ErrorSeverity, ErrorContext,
        SystemError, MemoryError, DiskError, NetworkError,
        ModelLoadingError, ModelInferenceError, ModelTrainingError, ModelMemoryError,
        DataLoadingError, DataValidationError, DataTransformationError,
        VideoProcessingError, VideoEncodingError, VideoFormatError,
        APIError, RateLimitError, ConfigurationError, DependencyError,
        ConcurrencyError, DeadlockError, SecurityError, ValidationError,
        RecoveryStrategy, RecoveryManager, ErrorMonitor, GlobalErrorHandler,
        handle_errors, retry_on_error, error_context, async_error_context,
        safe_execute, safe_execute_async, get_error_handler, setup_error_handling
    )
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo error_handling: {e}")

try:
    from .edge_case_handler import (
        EdgeCaseType, ResourceType, ResourceLimits, ResourceUsage,
        ResourceMonitor, BoundaryConditionHandler, RaceConditionHandler,
        MemoryLeakDetector, TimeoutHandler, DataValidator,
        SystemOverloadProtector, EdgeCaseHandler,
        create_edge_case_handler, with_edge_case_protection,
        validate_system_requirements, get_edge_handler, setup_edge_case_handling
    )
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo edge_case_handler: {e}")

# Guard Clauses and Early Validation
try:
    from .guard_clauses import (
        GuardType, GuardSeverity, GuardResult,
        guard_validation, guard_resources, guard_state,
        ValidationGuards, ResourceGuards, StateGuards,
        BoundaryGuards, SanityGuards, GuardClauseManager,
        fail_fast, require_not_none, require_not_empty,
        require_file_exists, require_valid_range,
        guard_context, resource_guard_context,
        get_guard_manager, setup_guard_clauses
    )
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo guard_clauses: {e}")

try:
    from .early_validation import (
        ValidationType, ValidationLevel, ValidationRule, ValidationResult,
        early_validate, ValidationSchema,
        TypeValidators, RangeValidators, FormatValidators,
        ExistenceValidators, SizeValidators, ContentValidators,
        RelationshipValidators,
        create_video_validation_schema, create_model_validation_schema,
        create_data_validation_schema, validate_all, validate_any,
        create_custom_validator, validate_function_signature,
        setup_early_validation
    )
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo early_validation: {e}")

# Early Returns System
try:
    from .early_returns import (
        ReturnType, EarlyReturnResult,
        early_return_on_error, early_return_on_condition,
        EarlyReturnConditions, EarlyReturnPatterns,
        return_if_none, return_if_empty, return_if_file_not_exists,
        return_if_invalid_batch_size, return_if_insufficient_memory,
        return_if_system_overloaded, return_if_invalid_quality,
        return_if_data_corrupted, early_return_context, validation_context,
        apply_early_returns, create_early_return_validator,
        setup_early_returns
    )
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo early_returns: {e}")

# Async/Sync Patterns
from .async_sync_patterns import (
    # Sync functions
    validate_input_data,
    calculate_processing_time,
    format_file_size,
    normalize_tensor_sync,
    save_config_sync,
    load_config_sync,
    validate_video_parameters,
    calculate_batch_size,
    
    # Async functions
    fetch_video_data,
    save_video_file_async,
    process_video_batch_async,
    generate_video_async,
    update_database_async,
    download_model_async,
    
    # Mixed patterns
    process_video_with_validation,
    batch_process_videos_async,
    
    # Utility functions
    run_sync_in_executor,
    run_sync_async,
    sync_to_async,
    async_to_sync,
    with_async_context,
    
    # Examples
    example_video_processing_pipeline,
    example_sync_utility_functions,
    example_async_operations
)

from .async_sync_examples import (
    # Video processing examples
    validate_video_request,
    calculate_estimated_time,
    format_video_metadata,
    save_video_record,
    save_video_file,
    process_video_request,
    
    # Batch processing examples
    validate_batch_requests,
    calculate_batch_resources,
    process_batch_requests,
    
    # Configuration examples
    validate_config,
    transform_config_for_model,
    load_config_async,
    save_config_async,
    
    # Error handling examples
    classify_error,
    format_error_message,
    handle_async_operation,
    
    # Usage examples
    example_usage
)

# Lifespan Patterns
from .lifespan_patterns import (
    # Basic lifespan
    lifespan,
    create_app,
    
    # Advanced lifespan patterns
    lifespan_with_health_checks,
    lifespan_with_retry,
    
    # Helper classes
    PerformanceMonitor,
    BackgroundTaskManager,
    
    # Helper functions
    setup_signal_handlers,
    load_video_model,
    load_text_model,
    unload_video_model,
    unload_text_model,
    
    # Examples
    example_basic_lifespan,
    example_advanced_lifespan,
    example_retry_lifespan
)

from .lifespan_examples import (
    # Basic migration examples
    basic_lifespan,
    ai_model_lifespan,
    background_task_lifespan,
    comprehensive_lifespan,
    
    # Helper classes
    BackgroundTaskManager,
    PerformanceMonitor,
    
    # Model loading functions
    load_video_model,
    load_text_model,
    load_diffusion_pipeline,
    unload_model,
    
    # Background tasks
    monitor_system_resources,
    cleanup_old_files,
    collect_system_metrics,
    
    # Health checks and utilities
    run_health_checks,
    setup_signal_handlers,
    
    # FastAPI application examples
    create_basic_app,
    create_ai_model_app,
    create_comprehensive_app,
    
    # Migration utilities
    migrate_from_on_event_to_lifespan
)

# Middleware Patterns
from .middleware_patterns import (
    # Request logging middleware
    RequestLoggingMiddleware,
    
    # Error monitoring middleware
    ErrorMonitoringMiddleware,
    
    # Performance monitoring middleware
    PerformanceMiddleware,
    
    # Security middleware
    SecurityMiddleware,
    
    # Rate limiting middleware
    RateLimitMiddleware,
    
    # Caching middleware
    CacheMiddleware,
    
    # Middleware stack creation
    create_middleware_stack,
    
    # Examples
    example_basic_middleware,
    example_comprehensive_middleware
)

from .middleware_examples import (
    # AI Video specific middleware
    AIVideoLoggingMiddleware,
    PerformanceMonitoringMiddleware,
    ErrorMonitoringMiddleware,
    AIVideoCacheMiddleware,
    AIVideoRateLimitMiddleware,
    
    # Middleware stack creation
    create_ai_video_middleware_stack,
    create_ai_video_app,
    
    # Example applications
    example_basic_middleware,
    example_performance_middleware,
    example_error_monitoring
)

# HTTP exception system
from .http_exceptions import (
    AIVideoHTTPException,
    ErrorContext,
    ErrorCategory,
    ErrorSeverity,
    ValidationError,
    InvalidVideoRequestError,
    InvalidModelRequestError,
    AuthenticationError,
    InvalidTokenError,
    AuthorizationError,
    InsufficientPermissionsError,
    ResourceNotFoundError,
    VideoNotFoundError,
    ModelNotFoundError,
    ResourceConflictError,
    VideoAlreadyExistsError,
    ProcessingError,
    VideoGenerationError,
    VideoProcessingTimeoutError,
    ModelError,
    ModelLoadError,
    ModelInferenceError,
    DatabaseError,
    DatabaseConnectionError,
    DatabaseQueryError,
    CacheError,
    CacheConnectionError,
    ExternalServiceError,
    RateLimitError,
    SystemError,
    MemoryError,
    TimeoutError,
    HTTPExceptionHandler,
    ErrorMonitor,
    error_context,
    handle_errors,
    setup_error_handlers
)

from .http_exception_examples import (
    VideoProcessingAPI,
    ModelManagementAPI,
    DatabaseService,
    CacheService,
    ExternalVideoService,
    create_video_api
)

# Error middleware system
from .error_middleware import (
    ErrorType,
    ErrorAction,
    ErrorInfo,
    ErrorTracker,
    RequestLog,
    StructuredLoggingMiddleware,
    ErrorHandlingMiddleware,
    PerformanceMetrics,
    PerformanceMonitoringMiddleware,
    MiddlewareStack,
    create_app_with_middleware
)

from .error_middleware_examples import (
    CircuitBreakerExample,
    PerformanceMonitoringExample,
    ErrorRecoveryExample,
    AlertingExample,
    IntegratedErrorHandlingSystem,
    test_error_scenarios,
    run_error_middleware_examples
)

__all__ = [
    # Error Handling
    "GradioErrorHandler",
    "GradioInputValidator", 
    "InputValidationRule",
    "ErrorSeverity",
    "ErrorCategory",
    "GradioErrorInfo",
    "gradio_error_handler",
    "gradio_input_validator",
    "create_gradio_error_components",
    "update_error_display",
    "handle_gradio_error",
    "validate_gradio_inputs",
    
    # Applications
    "AIVideoGradioApp",
    "create_gradio_app",
    "create_simple_interface",
    
    # Version Control
    "GitManager",
    "ConfigVersioning", 
    "ChangeTracker",
    "VersionControlSystem",
    "create_version_control_system",
    "quick_version_config",
    "start_experiment",
    "finish_experiment",
    
    # Error Handling and Edge Case Management
    "AIVideoError",
    "ErrorContext",
    "SystemError",
    "MemoryError",
    "DiskError",
    "NetworkError",
    "ModelLoadingError",
    "ModelInferenceError",
    "ModelTrainingError",
    "ModelMemoryError",
    "DataLoadingError",
    "DataValidationError",
    "DataTransformationError",
    "VideoProcessingError",
    "VideoEncodingError",
    "VideoFormatError",
    "APIError",
    "RateLimitError",
    "ConfigurationError",
    "DependencyError",
    "ConcurrencyError",
    "DeadlockError",
    "SecurityError",
    "ValidationError",
    "RecoveryStrategy",
    "RecoveryManager",
    "ErrorMonitor",
    "GlobalErrorHandler",
    "handle_errors",
    "retry_on_error",
    "error_context",
    "async_error_context",
    "safe_execute",
    "safe_execute_async",
    "get_error_handler",
    "setup_error_handling",
    "EdgeCaseType",
    "ResourceType",
    "ResourceLimits",
    "ResourceUsage",
    "ResourceMonitor",
    "BoundaryConditionHandler",
    "RaceConditionHandler",
    "MemoryLeakDetector",
    "TimeoutHandler",
    "DataValidator",
    "SystemOverloadProtector",
    "EdgeCaseHandler",
    "create_edge_case_handler",
    "with_edge_case_protection",
    "validate_system_requirements",
    "get_edge_handler",
    "setup_edge_case_handling",
    # Guard Clauses and Early Validation
    "GuardType",
    "GuardSeverity",
    "GuardResult",
    "guard_validation",
    "guard_resources",
    "guard_state",
    "ValidationGuards",
    "ResourceGuards",
    "StateGuards",
    "BoundaryGuards",
    "SanityGuards",
    "GuardClauseManager",
    "fail_fast",
    "require_not_none",
    "require_not_empty",
    "require_file_exists",
    "require_valid_range",
    "guard_context",
    "resource_guard_context",
    "get_guard_manager",
    "setup_guard_clauses",
    "ValidationType",
    "ValidationLevel",
    "ValidationRule",
    "ValidationResult",
    "early_validate",
    "ValidationSchema",
    "TypeValidators",
    "RangeValidators",
    "FormatValidators",
    "ExistenceValidators",
    "SizeValidators",
    "ContentValidators",
    "RelationshipValidators",
    "create_video_validation_schema",
    "create_model_validation_schema",
    "create_data_validation_schema",
    "validate_all",
    "validate_any",
    "create_custom_validator",
    "validate_function_signature",
    "setup_early_validation",
    # Early Returns System
    "ReturnType",
    "EarlyReturnResult",
    "early_return_on_error",
    "early_return_on_condition",
    "EarlyReturnConditions",
    "EarlyReturnPatterns",
    "return_if_none",
    "return_if_empty",
    "return_if_file_not_exists",
    "return_if_invalid_batch_size",
    "return_if_insufficient_memory",
    "return_if_system_overloaded",
    "return_if_invalid_quality",
    "return_if_data_corrupted",
    "early_return_context",
    "validation_context",
    "apply_early_returns",
    "create_early_return_validator",
    "setup_early_returns",
    # Async/Sync Patterns
    "validate_input_data",
    "calculate_processing_time",
    "format_file_size",
    "normalize_tensor_sync",
    "save_config_sync",
    "load_config_sync",
    "validate_video_parameters",
    "calculate_batch_size",
    "fetch_video_data",
    "save_video_file_async",
    "process_video_batch_async",
    "generate_video_async",
    "update_database_async",
    "download_model_async",
    "process_video_with_validation",
    "batch_process_videos_async",
    "run_sync_in_executor",
    "run_sync_async",
    "sync_to_async",
    "async_to_sync",
    "with_async_context",
    "example_video_processing_pipeline",
    "example_sync_utility_functions",
    "example_async_operations",
    # Video processing examples
    "validate_video_request",
    "calculate_estimated_time",
    "format_video_metadata",
    "save_video_record",
    "save_video_file",
    "process_video_request",
    # Batch processing examples
    "validate_batch_requests",
    "calculate_batch_resources",
    "process_batch_requests",
    # Configuration examples
    "validate_config",
    "transform_config_for_model",
    "load_config_async",
    "save_config_async",
    # Error handling examples
    "classify_error",
    "format_error_message",
    "handle_async_operation",
    # Usage examples
    "example_usage",
    # Lifespan Patterns
    "lifespan",
    "create_app",
    "lifespan_with_health_checks",
    "lifespan_with_retry",
    "PerformanceMonitor",
    "BackgroundTaskManager",
    "setup_signal_handlers",
    "load_video_model",
    "load_text_model",
    "unload_video_model",
    "unload_text_model",
    "example_basic_lifespan",
    "example_advanced_lifespan",
    "example_retry_lifespan",
    "basic_lifespan",
    "ai_model_lifespan",
    "background_task_lifespan",
    "comprehensive_lifespan",
    "monitor_system_resources",
    "cleanup_old_files",
    "collect_system_metrics",
    "run_health_checks",
    "create_basic_app",
    "create_ai_model_app",
    "create_comprehensive_app",
    "migrate_from_on_event_to_lifespan",
    # Middleware Patterns
    "RequestLoggingMiddleware",
    "ErrorMonitoringMiddleware",
    "PerformanceMiddleware",
    "SecurityMiddleware",
    "RateLimitMiddleware",
    "CacheMiddleware",
    "create_middleware_stack",
    "example_basic_middleware",
    "example_comprehensive_middleware",
    # Middleware Examples
    "AIVideoLoggingMiddleware",
    "PerformanceMonitoringMiddleware",
    "ErrorMonitoringMiddleware",
    "AIVideoCacheMiddleware",
    "AIVideoRateLimitMiddleware",
    "create_ai_video_middleware_stack",
    "create_ai_video_app",
    "example_basic_middleware",
    "example_performance_middleware",
    "example_error_monitoring",
    # HTTP exception system
    "AIVideoHTTPException",
    "ErrorContext",
    "ErrorCategory", 
    "ErrorSeverity",
    "ValidationError",
    "InvalidVideoRequestError",
    "InvalidModelRequestError",
    "AuthenticationError",
    "InvalidTokenError",
    "AuthorizationError",
    "InsufficientPermissionsError",
    "ResourceNotFoundError",
    "VideoNotFoundError",
    "ModelNotFoundError",
    "ResourceConflictError",
    "VideoAlreadyExistsError",
    "ProcessingError",
    "VideoGenerationError",
    "VideoProcessingTimeoutError",
    "ModelError",
    "ModelLoadError",
    "ModelInferenceError",
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseQueryError",
    "CacheError",
    "CacheConnectionError",
    "ExternalServiceError",
    "RateLimitError",
    "SystemError",
    "MemoryError",
    "TimeoutError",
    "HTTPExceptionHandler",
    "ErrorMonitor",
    "error_context",
    "handle_errors",
    "setup_error_handlers",
    # HTTP exception examples
    "VideoProcessingAPI",
    "ModelManagementAPI",
    "DatabaseService",
    "CacheService",
    "ExternalVideoService",
    "create_video_api",
    # Error middleware system
    "ErrorType",
    "ErrorAction", 
    "ErrorInfo",
    "ErrorTracker",
    "RequestLog",
    "StructuredLoggingMiddleware",
    "ErrorHandlingMiddleware",
    "PerformanceMetrics",
    "PerformanceMonitoringMiddleware",
    "MiddlewareStack",
    "create_app_with_middleware",
    
    # Error middleware examples
    "CircuitBreakerExample",
    "PerformanceMonitoringExample",
    "ErrorRecoveryExample",
    "AlertingExample",
    "IntegratedErrorHandlingSystem",
    "test_error_scenarios",
    "run_error_middleware_examples"
]

__version__ = "2.0.0"
__author__ = "AI Video System Team"
__description__ = "Gradio integration with comprehensive error handling and input validation"

# Core performance optimization modules
from .performance_optimization import (
    AsyncIOOptimizer,
    AsyncCache,
    CacheConfig,
    CacheStats,
    ModelCache,
    LazyLoader,
    LazyDict,
    QueryOptimizer,
    MemoryOptimizer,
    WeakRefCache,
    BackgroundTaskProcessor,
    PerformanceMetrics,
    PerformanceMonitor,
    PerformanceOptimizationSystem
)

# Performance examples and patterns
from .performance_examples import (
    AsyncVideoProcessor,
    AIVideoModelManager,
    VideoDatabaseOptimizer,
    ModelMemoryManager,
    VideoBackgroundProcessor,
    AIVideoPerformanceSystem
)

# Error handling and edge cases
from .error_handling import (
    AIVideoError,
    ValidationError,
    ProcessingError,
    ModelError,
    DatabaseError,
    CacheError,
    ErrorHandler,
    ErrorRecovery,
    ErrorMonitor
)

from .edge_case_handler import (
    EdgeCaseHandler,
    ResourceMonitor,
    RaceConditionHandler,
    MemoryLeakDetector,
    TimeoutHandler,
    DataValidator,
    DataSanitizer,
    SystemOverloadProtector
)

# Early returns and guard clauses
from .early_returns import (
    EarlyReturnHandler,
    GuardClauseDecorator,
    ValidationHelper,
    ErrorContextManager,
    EarlyReturnPatterns
)

from .guard_clauses import (
    GuardClauseHandler,
    InputValidator,
    StateChecker,
    ResourceValidator,
    SecurityValidator,
    GuardClausePatterns
)

from .early_validation import (
    EarlyValidationHandler,
    DataValidator,
    SchemaValidator,
    BusinessRuleValidator,
    SecurityValidator,
    ValidationPatterns
)

# Happy path last patterns
from .happy_path_last import (
    HappyPathHandler,
    GuardClausePatterns,
    ErrorFirstPatterns,
    ValidationFirstPatterns,
    HappyPathExamples
)

# Functional programming patterns
from .functional_pipeline import (
    Pipeline,
    PipelineStep,
    PipelineBuilder,
    FunctionalPipeline,
    PipelineExamples
)

from .functional_training import (
    TrainingPipeline,
    ModelTrainer,
    DataProcessor,
    Evaluator,
    FunctionalTraining
)

from .functional_api import (
    FunctionalAPI,
    RouteBuilder,
    MiddlewareBuilder,
    ErrorHandler,
    FunctionalAPIPatterns
)

from .functional_utils import (
    FunctionalUtils,
    PureFunctions,
    FunctionComposition,
    Currying,
    FunctionalPatterns
)

# Async/sync patterns
from .async_sync_patterns import (
    AsyncSyncHandler,
    AsyncPatterns,
    SyncPatterns,
    HybridPatterns,
    PatternExamples
)

from .async_sync_examples import (
    AsyncExamples,
    SyncExamples,
    HybridExamples,
    RealWorldExamples
)

# Lifespan patterns
from .lifespan_patterns import (
    LifespanHandler,
    StartupPhase,
    ShutdownPhase,
    ResourceManager,
    HealthChecker,
    LifespanPatterns
)

from .lifespan_examples import (
    LifespanExamples,
    StartupExamples,
    ShutdownExamples,
    ResourceExamples,
    HealthExamples
)

# Middleware patterns
from .middleware_patterns import (
    MiddlewareHandler,
    RequestLogger,
    ErrorMonitor,
    PerformanceTracker,
    SecurityHeaders,
    RateLimiter,
    CacheMiddleware,
    MiddlewareStack
)

from .middleware_examples import (
    MiddlewareExamples,
    LoggingExamples,
    ErrorExamples,
    PerformanceExamples,
    SecurityExamples
)

# Configuration and project management
from .config.config_manager import (
    ConfigManager,
    ConfigValidator,
    ConfigLoader,
    ConfigWatcher,
    ConfigExamples
)

from .project_init import (
    ProblemDefinition,
    DatasetAnalyzer,
    ProjectSetup,
    BaselineConfig,
    ExperimentTracker,
    ProjectInitializer
)

# Experiment tracking and version control
from .experiment_tracking.experiment_tracker import (
    ExperimentTracker,
    MetricsLogger,
    ArtifactManager,
    SampleLogger,
    VideoMetrics,
    PerformanceMonitor,
    ExperimentExamples
)

from .version_control.git_manager import (
    GitManager,
    CommitManager,
    BranchManager,
    ChangeTracker,
    GitExamples
)

from .version_control.config_versioning import (
    ConfigVersioning,
    DiffGenerator,
    RollbackManager,
    VersionTracker,
    ConfigExamples
)

# Core modules
from .core.video_processor import (
    VideoProcessor,
    VideoGenerator,
    VideoOptimizer,
    VideoValidator
)

from .core.model_manager import (
    ModelManager,
    ModelLoader,
    ModelCache,
    ModelOptimizer
)

from .core.data_pipeline import (
    DataPipeline,
    DataLoader,
    DataProcessor,
    DataValidator
)

# API and routing
from .api.video_routes import (
    VideoRoutes,
    VideoEndpoints,
    VideoMiddleware,
    VideoValidation
)

from .api.model_routes import (
    ModelRoutes,
    ModelEndpoints,
    ModelMiddleware,
    ModelValidation
)

# Utilities and helpers
from .utils.video_utils import (
    VideoUtils,
    VideoConverter,
    VideoAnalyzer,
    VideoOptimizer
)

from .utils.model_utils import (
    ModelUtils,
    ModelConverter,
    ModelAnalyzer,
    ModelOptimizer
)

# Testing and validation
from .tests.test_performance import (
    PerformanceTests,
    CacheTests,
    MemoryTests,
    AsyncTests
)

from .tests.test_integration import (
    IntegrationTests,
    EndToEndTests,
    LoadTests,
    StressTests
)

# Documentation and examples
from .docs.performance_guide import (
    PerformanceGuide,
    OptimizationTips,
    BestPractices,
    Examples
)

from .docs.api_reference import (
    APIReference,
    EndpointDocs,
    ModelDocs,
    ExampleDocs
)

# Main application entry points
from .main import (
    create_app,
    setup_middleware,
    setup_routes,
    setup_optimization,
    run_app
)

from .onyx_main import (
    OnyxVideoSystem,
    OnyxProcessor,
    OnyxOptimizer,
    OnyxManager
)

# Quick start and examples
from .quick_start import (
    quick_start_example,
    basic_usage,
    advanced_usage,
    optimization_example
)

from .performance_benchmark import (
    run_benchmarks,
    compare_performance,
    generate_report,
    benchmark_examples
)

# Installation and setup
from .install_latest import (
    install_dependencies,
    setup_environment,
    verify_installation,
    quick_setup
)

from .optimized_pipeline import (
    OptimizedPipeline,
    PipelineOptimizer,
    PipelineBenchmark,
    PipelineExamples
)

# Gradio integration
from .gradio_interface import (
    GradioInterface,
    VideoInterface,
    ModelInterface,
    GradioExamples
)

from .gradio_error_handling import (
    GradioErrorHandler,
    InputValidator,
    ErrorDisplay,
    RecoveryHandler,
    GradioErrorExamples
)

from .gradio_launcher import (
    GradioLauncher,
    InterfaceBuilder,
    LauncherConfig,
    LauncherExamples
)

# Dependencies and requirements
from .dependencies import (
    get_redis_client,
    get_database_session,
    get_model_cache,
    get_performance_monitor,
    get_background_processor
)

# Quick access to main components
def get_performance_system(redis_client=None):
    """Get the main performance optimization system."""
    return PerformanceOptimizationSystem(redis_client)

def get_ai_video_system(redis_client=None):
    """Get the main AI Video performance system."""
    return AIVideoPerformanceSystem(redis_client)

def create_optimized_app():
    """Create a FastAPI app with all optimizations enabled."""
    from .main import create_app
    return create_app()

# Performance optimization decorators
def async_optimized(func):
    """Decorator to add async optimization to functions."""
    from .performance_optimization import AsyncIOOptimizer
    optimizer = AsyncIOOptimizer()
    
    async def wrapper(*args, **kwargs):
        return await optimizer.process_with_timeout(func(*args, **kwargs))
    
    return wrapper

def cached_result(ttl=3600):
    """Decorator to cache function results."""
    from .performance_optimization import AsyncCache
    cache = AsyncCache()
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try cache first
            cached = await cache.get(cache_key)
            if cached:
                return cached
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

def lazy_loaded(loader_func):
    """Decorator to make a property lazy loaded."""
    from .performance_optimization import LazyLoader
    
    def decorator(func):
        lazy_loader = LazyLoader(loader_func)
        
        async def wrapper(*args, **kwargs):
            return await lazy_loader.get()
        
        return wrapper
    return decorator

# Export decorators
__all__.extend([
    "get_performance_system",
    "get_ai_video_system", 
    "create_optimized_app",
    "async_optimized",
    "cached_result",
    "lazy_loaded"
]) 