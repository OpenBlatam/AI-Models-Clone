"""
Blatam Academy Shared Library
==============================

Librería compartida con utilidades avanzadas para FastAPI, microservicios y serverless.

Incluye:
- Middleware avanzado (OpenTelemetry, logging, security)
- OAuth2 security
- Async workers (Celery, RQ)
- Message brokers (RabbitMQ, Kafka, Redis)
- API Gateway integrations (Kong, AWS)
- Service mesh support (Istio, Linkerd)
- Database adapters (DynamoDB, Cosmos DB)
- Search & Cache (Elasticsearch, Memcached)
- OWASP security
- Serverless optimizations
- Service discovery
- Inter-service communication
"""

__version__ = "1.0.0"
__author__ = "Blatam Academy"

# Core modules
from .middleware import (
    setup_advanced_middleware,
    StructuredLoggingMiddleware,
    SecurityHeadersMiddleware,
    PerformanceMonitoringMiddleware,
    OpenTelemetryMiddleware,
    RequestContextMiddleware
)

# Security (opcional - copiar desde 3d_prototype_ai/utils/oauth2_security.py)
try:
    from .security import (
        oauth2_security,
        get_current_active_user,
        require_scope,
        require_role,
        User,
        Token,
        UserCreate,
        OAuth2Security
    )
except ImportError:
    # Módulo no disponible aún
    oauth2_security = None
    get_current_active_user = None
    require_scope = None
    require_role = None
    User = None
    Token = None
    UserCreate = None
    OAuth2Security = None

# Workers (opcional - copiar desde 3d_prototype_ai/utils/async_workers.py)
try:
    from .workers import (
        WorkerManager,
        WorkerType,
        AsyncWorker,
        CeleryWorker,
        RQWorker,
        TaskStatus
    )
except ImportError:
    WorkerManager = None
    WorkerType = None
    AsyncWorker = None
    CeleryWorker = None
    RQWorker = None
    TaskStatus = None

# Messaging (opcional - copiar desde 3d_prototype_ai/utils/message_broker.py)
try:
    from .messaging import (
        MessageBrokerManager,
        BrokerType,
        RabbitMQBroker,
        KafkaBroker,
        RedisPubSubBroker,
        Message
    )
except ImportError:
    MessageBrokerManager = None
    BrokerType = None
    RabbitMQBroker = None
    KafkaBroker = None
    RedisPubSubBroker = None
    Message = None

# Gateway (opcional - copiar desde 3d_prototype_ai/utils/)
try:
    from .gateway import (
        KongGatewayManager,
        AWSAPIGatewayManager,
        KongAdminClient
    )
except ImportError:
    KongGatewayManager = None
    AWSAPIGatewayManager = None
    KongAdminClient = None

# Service Mesh (opcional)
try:
    from .service_mesh import (
        ServiceMeshManager,
        ServiceMeshType,
        IstioConfig,
        LinkerdConfig
    )
except ImportError:
    ServiceMeshManager = None
    ServiceMeshType = None
    IstioConfig = None
    LinkerdConfig = None

# Database (opcional)
try:
    from .database import (
        DatabaseManager,
        DatabaseAdapter,
        DynamoDBAdapter,
        CosmosDBAdapter
    )
except ImportError:
    DatabaseManager = None
    DatabaseAdapter = None
    DynamoDBAdapter = None
    CosmosDBAdapter = None

# Search (opcional)
try:
    from .search import (
        ElasticsearchClient,
        elasticsearch_client
    )
except ImportError:
    ElasticsearchClient = None
    elasticsearch_client = None

# Cache (opcional)
try:
    from .cache import (
        MemcachedClient,
        memcached_client
    )
except ImportError:
    MemcachedClient = None
    memcached_client = None

# OWASP Security (opcional)
try:
    from .security_owasp import (
        OWASPSecurityValidator,
        DDoSProtectionMiddleware,
        SecurityHeadersMiddleware as OWASPSecurityHeaders,
        owasp_validator,
        ddos_protection
    )
except ImportError:
    OWASPSecurityValidator = None
    DDoSProtectionMiddleware = None
    OWASPSecurityHeaders = None
    owasp_validator = None
    ddos_protection = None

# Serverless (opcional)
try:
    from .serverless import (
        ServerlessConfig,
        get_serverless_config,
        serverless_handler,
        ColdStartOptimizer,
        MemoryOptimizer,
        ConnectionPool
    )
except ImportError:
    ServerlessConfig = None
    get_serverless_config = None
    serverless_handler = None
    ColdStartOptimizer = None
    MemoryOptimizer = None
    ConnectionPool = None

# Logging (opcional)
try:
    from .logging import (
        CentralizedLogging,
        StructuredLogger,
        CloudWatchLogger,
        ELKLogger
    )
except ImportError:
    CentralizedLogging = None
    StructuredLogger = None
    CloudWatchLogger = None
    ELKLogger = None

# Discovery (opcional)
try:
    from .discovery import (
        ServiceDiscoveryManager,
        ServiceDiscoveryType,
        ConsulServiceDiscovery,
        KubernetesServiceDiscovery,
        DNSServiceDiscovery,
        service_discovery
    )
except ImportError:
    ServiceDiscoveryManager = None
    ServiceDiscoveryType = None
    ConsulServiceDiscovery = None
    KubernetesServiceDiscovery = None
    DNSServiceDiscovery = None
    service_discovery = None

# Inter-service (opcional)
try:
from .inter_service import (
    ServiceRegistry,
    ServiceClient,
    RESTClient,
    CommunicationPattern,
    service_registry
)
except ImportError:
    ServiceRegistry = None
    ServiceClient = None
    RESTClient = None
    CommunicationPattern = None
    service_registry = None

# AWS Integration (opcional)
try:
    from .aws import (
        create_lambda_handler,
        LambdaHandler,
        AWSAPIGatewayIntegration,
        DynamoDBManager,
        S3Manager,
        CloudWatchLogger,
        CloudWatchMetrics,
        ECSDeployment,
        ServerlessConfig,
        create_serverless_config,
        aws_api_gateway,
        dynamodb_manager,
        s3_manager,
        cloudwatch_logger,
        cloudwatch_metrics
    )
except ImportError:
    create_lambda_handler = None
    LambdaHandler = None
    AWSAPIGatewayIntegration = None
    DynamoDBManager = None
    S3Manager = None
    CloudWatchLogger = None
    CloudWatchMetrics = None
    ECSDeployment = None
    ServerlessConfig = None
    create_serverless_config = None
    aws_api_gateway = None
    dynamodb_manager = None
    s3_manager = None
    cloudwatch_logger = None
    cloudwatch_metrics = None

# Utils (siempre disponibles)
from .utils import (
    CircuitBreaker,
    CircuitBreakerState,
    retry,
    RetryConfig,
    ExponentialBackoff,
    RateLimiter,
    TokenBucket,
    SlidingWindow,
    HealthChecker,
    HealthStatus,
    GracefulShutdown,
    shutdown_handler,
    ConnectionPool,
    PoolConfig
)

__all__ = [
    # Version
    "__version__",
    "__author__",
    
    # Middleware
    "setup_advanced_middleware",
    "StructuredLoggingMiddleware",
    "SecurityHeadersMiddleware",
    "PerformanceMonitoringMiddleware",
    "OpenTelemetryMiddleware",
    "RequestContextMiddleware",
    
    # Security
    "oauth2_security",
    "get_current_active_user",
    "require_scope",
    "require_role",
    "User",
    "Token",
    "UserCreate",
    "OAuth2Security",
    
    # Workers
    "WorkerManager",
    "WorkerType",
    "AsyncWorker",
    "CeleryWorker",
    "RQWorker",
    "TaskStatus",
    
    # Messaging
    "MessageBrokerManager",
    "BrokerType",
    "RabbitMQBroker",
    "KafkaBroker",
    "RedisPubSubBroker",
    "Message",
    
    # Gateway
    "KongGatewayManager",
    "AWSAPIGatewayManager",
    "KongAdminClient",
    
    # Service Mesh
    "ServiceMeshManager",
    "ServiceMeshType",
    "IstioConfig",
    "LinkerdConfig",
    
    # Database
    "DatabaseManager",
    "DatabaseAdapter",
    "DynamoDBAdapter",
    "CosmosDBAdapter",
    
    # Search
    "ElasticsearchClient",
    "elasticsearch_client",
    
    # Cache
    "MemcachedClient",
    "memcached_client",
    
    # OWASP Security
    "OWASPSecurityValidator",
    "DDoSProtectionMiddleware",
    "OWASPSecurityHeaders",
    "owasp_validator",
    "ddos_protection",
    
    # Serverless
    "ServerlessConfig",
    "get_serverless_config",
    "serverless_handler",
    "ColdStartOptimizer",
    "MemoryOptimizer",
    "ConnectionPool",
    
    # Logging
    "CentralizedLogging",
    "StructuredLogger",
    "CloudWatchLogger",
    "ELKLogger",
    
    # Discovery
    "ServiceDiscoveryManager",
    "ServiceDiscoveryType",
    "ConsulServiceDiscovery",
    "KubernetesServiceDiscovery",
    "DNSServiceDiscovery",
    "service_discovery",
    
    # Inter-service
    "ServiceRegistry",
    "ServiceClient",
    "RESTClient",
    "CommunicationPattern",
    "service_registry",
    
    # AWS
    "create_lambda_handler",
    "LambdaHandler",
    "AWSAPIGatewayIntegration",
    "DynamoDBManager",
    "S3Manager",
    "CloudWatchLogger",
    "CloudWatchMetrics",
    "ECSDeployment",
    "ServerlessConfig",
    "create_serverless_config",
    "aws_api_gateway",
    "dynamodb_manager",
    "s3_manager",
    "cloudwatch_logger",
    "cloudwatch_metrics",
    
    # Utils
    "CircuitBreaker",
    "CircuitBreakerState",
    "retry",
    "RetryConfig",
    "ExponentialBackoff",
    "RateLimiter",
    "TokenBucket",
    "SlidingWindow",
    "HealthChecker",
    "HealthStatus",
    "GracefulShutdown",
    "shutdown_handler",
    "ConnectionPool",
    "PoolConfig",
]

