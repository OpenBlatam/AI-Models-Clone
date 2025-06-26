"""
Production Configuration Module.

Centralized configuration for enterprise-grade production deployment,
consolidating settings from all legacy production files.
"""

from typing import Optional, List, Dict, Any, Union
from enum import Enum
import os
import multiprocessing

from pydantic import BaseSettings, Field, validator
from decouple import config


class ProductionLevel(str, Enum):
    """Production optimization levels."""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ULTRA = "ultra"
    QUANTUM = "quantum"


class DeploymentEnvironment(str, Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseType(str, Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"


class LoadBalancerType(str, Enum):
    """Load balancer types."""
    NGINX = "nginx"
    HAPROXY = "haproxy"
    TRAEFIK = "traefik"
    CLOUDFLARE = "cloudflare"


class ProductionSettings(BaseSettings):
    """Comprehensive production settings consolidating all legacy configurations."""
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    
    # Basic app info
    app_name: str = Field(default="Onyx-Production-System")
    app_version: str = Field(default="3.0.0")
    app_description: str = Field(default="Enterprise-grade production system")
    
    # Environment
    environment: DeploymentEnvironment = Field(
        default=config("ENVIRONMENT", default=DeploymentEnvironment.PRODUCTION, cast=DeploymentEnvironment)
    )
    debug: bool = Field(default=config("DEBUG", default=False, cast=bool))
    
    # Production level
    production_level: ProductionLevel = Field(
        default=config("PRODUCTION_LEVEL", default=ProductionLevel.STANDARD, cast=ProductionLevel)
    )
    
    # =============================================================================
    # SERVER SETTINGS
    # =============================================================================
    
    # Network configuration
    host: str = Field(default=config("HOST", default="0.0.0.0"))
    port: int = Field(default=config("PORT", default=8000, cast=int))
    metrics_port: int = Field(default=config("METRICS_PORT", default=9090, cast=int))
    health_port: int = Field(default=config("HEALTH_PORT", default=8080, cast=int))
    
    # Worker configuration
    workers: int = Field(default=config("WORKERS", default=None, cast=int))
    worker_class: str = Field(default=config("WORKER_CLASS", default="uvicorn.workers.UvicornWorker"))
    worker_connections: int = Field(default=config("WORKER_CONNECTIONS", default=1000, cast=int))
    
    # Connection settings
    max_connections: int = Field(default=config("MAX_CONNECTIONS", default=10000, cast=int))
    max_connections_per_host: int = Field(default=config("MAX_CONNECTIONS_PER_HOST", default=100, cast=int))
    backlog: int = Field(default=config("BACKLOG", default=2048, cast=int))
    
    # Timeout settings
    keepalive_timeout: int = Field(default=config("KEEPALIVE_TIMEOUT", default=120, cast=int))
    request_timeout: int = Field(default=config("REQUEST_TIMEOUT", default=300, cast=int))
    graceful_shutdown_timeout: int = Field(default=config("GRACEFUL_SHUTDOWN_TIMEOUT", default=60, cast=int))
    
    # =============================================================================
    # PERFORMANCE SETTINGS
    # =============================================================================
    
    # Event loop optimization
    enable_uvloop: bool = Field(default=config("ENABLE_UVLOOP", default=True, cast=bool))
    
    # HTTP optimization
    enable_http2: bool = Field(default=config("ENABLE_HTTP2", default=True, cast=bool))
    enable_compression: bool = Field(default=config("ENABLE_COMPRESSION", default=True, cast=bool))
    compression_level: int = Field(default=config("COMPRESSION_LEVEL", default=6, cast=int))
    
    # Serialization
    default_json_encoder: str = Field(default=config("JSON_ENCODER", default="orjson"))
    enable_fast_serialization: bool = Field(default=config("ENABLE_FAST_SERIALIZATION", default=True, cast=bool))
    
    # Memory management
    max_memory_mb: int = Field(default=config("MAX_MEMORY_MB", default=None, cast=int))
    gc_threshold: int = Field(default=config("GC_THRESHOLD", default=500, cast=int))
    enable_memory_optimization: bool = Field(default=config("ENABLE_MEMORY_OPTIMIZATION", default=True, cast=bool))
    
    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    
    # Primary database
    database_url: Optional[str] = Field(default=config("DATABASE_URL", default=None))
    database_type: DatabaseType = Field(
        default=config("DATABASE_TYPE", default=DatabaseType.POSTGRESQL, cast=DatabaseType)
    )
    
    # Connection pooling
    db_pool_size: int = Field(default=config("DB_POOL_SIZE", default=20, cast=int))
    db_max_overflow: int = Field(default=config("DB_MAX_OVERFLOW", default=50, cast=int))
    db_pool_timeout: int = Field(default=config("DB_POOL_TIMEOUT", default=30, cast=int))
    db_pool_recycle: int = Field(default=config("DB_POOL_RECYCLE", default=3600, cast=int))
    
    # Read replicas
    database_replica_urls: List[str] = Field(default_factory=list)
    enable_read_replicas: bool = Field(default=config("ENABLE_READ_REPLICAS", default=False, cast=bool))
    
    # =============================================================================
    # CACHE CONFIGURATION
    # =============================================================================
    
    # Redis configuration
    redis_url: Optional[str] = Field(default=config("REDIS_URL", default=None))
    redis_cluster_urls: List[str] = Field(default_factory=list)
    redis_pool_size: int = Field(default=config("REDIS_POOL_SIZE", default=50, cast=int))
    
    # Cache settings
    enable_caching: bool = Field(default=config("ENABLE_CACHING", default=True, cast=bool))
    cache_ttl_default: int = Field(default=config("CACHE_TTL_DEFAULT", default=3600, cast=int))
    cache_prefix: str = Field(default=config("CACHE_PREFIX", default="onyx:prod:"))
    
    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================
    
    # Authentication
    secret_key: str = Field(default=config("SECRET_KEY", default="CHANGE-IN-PRODUCTION"))
    api_key: Optional[str] = Field(default=config("API_KEY", default=None))
    jwt_secret: Optional[str] = Field(default=config("JWT_SECRET", default=None))
    jwt_expiry_hours: int = Field(default=config("JWT_EXPIRY_HOURS", default=24, cast=int))
    
    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: config("CORS_ORIGINS", default="*").split(",")
    )
    cors_methods: List[str] = Field(
        default_factory=lambda: config("CORS_METHODS", default="GET,POST,PUT,DELETE,OPTIONS").split(",")
    )
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=config("RATE_LIMIT_PER_MINUTE", default=1000, cast=int))
    rate_limit_burst: int = Field(default=config("RATE_LIMIT_BURST", default=100, cast=int))
    
    # SSL/TLS
    enable_ssl: bool = Field(default=config("ENABLE_SSL", default=False, cast=bool))
    ssl_cert_path: Optional[str] = Field(default=config("SSL_CERT_PATH", default=None))
    ssl_key_path: Optional[str] = Field(default=config("SSL_KEY_PATH", default=None))
    
    # =============================================================================
    # MONITORING & OBSERVABILITY
    # =============================================================================
    
    # Monitoring
    enable_monitoring: bool = Field(default=config("ENABLE_MONITORING", default=True, cast=bool))
    enable_metrics: bool = Field(default=config("ENABLE_METRICS", default=True, cast=bool))
    enable_tracing: bool = Field(default=config("ENABLE_TRACING", default=True, cast=bool))
    enable_profiling: bool = Field(default=config("ENABLE_PROFILING", default=False, cast=bool))
    
    # External monitoring
    sentry_dsn: Optional[str] = Field(default=config("SENTRY_DSN", default=None))
    datadog_api_key: Optional[str] = Field(default=config("DATADOG_API_KEY", default=None))
    prometheus_enabled: bool = Field(default=config("PROMETHEUS_ENABLED", default=True, cast=bool))
    
    # Health checks
    health_check_interval: int = Field(default=config("HEALTH_CHECK_INTERVAL", default=30, cast=int))
    health_check_timeout: int = Field(default=config("HEALTH_CHECK_TIMEOUT", default=10, cast=int))
    
    # Logging
    log_level: str = Field(default=config("LOG_LEVEL", default="INFO"))
    log_format: str = Field(default=config("LOG_FORMAT", default="json"))
    enable_structured_logging: bool = Field(default=config("ENABLE_STRUCTURED_LOGGING", default=True, cast=bool))
    
    # =============================================================================
    # DEPLOYMENT SETTINGS
    # =============================================================================
    
    # Container settings
    container_registry: str = Field(default=config("CONTAINER_REGISTRY", default="docker.io"))
    image_name: str = Field(default=config("IMAGE_NAME", default="onyx-production"))
    image_tag: str = Field(default=config("IMAGE_TAG", default="latest"))
    
    # Kubernetes
    k8s_namespace: str = Field(default=config("K8S_NAMESPACE", default="default"))
    k8s_replicas: int = Field(default=config("K8S_REPLICAS", default=3, cast=int))
    k8s_cpu_request: str = Field(default=config("K8S_CPU_REQUEST", default="100m"))
    k8s_cpu_limit: str = Field(default=config("K8S_CPU_LIMIT", default="1000m"))
    k8s_memory_request: str = Field(default=config("K8S_MEMORY_REQUEST", default="256Mi"))
    k8s_memory_limit: str = Field(default=config("K8S_MEMORY_LIMIT", default="1Gi"))
    
    # Load balancing
    load_balancer_type: LoadBalancerType = Field(
        default=config("LOAD_BALANCER_TYPE", default=LoadBalancerType.NGINX, cast=LoadBalancerType)
    )
    enable_load_balancing: bool = Field(default=config("ENABLE_LOAD_BALANCING", default=True, cast=bool))
    
    # Auto-scaling
    enable_auto_scaling: bool = Field(default=config("ENABLE_AUTO_SCALING", default=True, cast=bool))
    min_replicas: int = Field(default=config("MIN_REPLICAS", default=2, cast=int))
    max_replicas: int = Field(default=config("MAX_REPLICAS", default=20, cast=int))
    target_cpu_percent: int = Field(default=config("TARGET_CPU_PERCENT", default=70, cast=int))
    target_memory_percent: int = Field(default=config("TARGET_MEMORY_PERCENT", default=80, cast=int))
    
    # =============================================================================
    # FEATURE FLAGS
    # =============================================================================
    
    # API features
    enable_api_docs: bool = Field(default=config("ENABLE_API_DOCS", default=False, cast=bool))
    enable_api_versioning: bool = Field(default=config("ENABLE_API_VERSIONING", default=True, cast=bool))
    enable_request_validation: bool = Field(default=config("ENABLE_REQUEST_VALIDATION", default=True, cast=bool))
    
    # Performance features
    enable_response_caching: bool = Field(default=config("ENABLE_RESPONSE_CACHING", default=True, cast=bool))
    enable_request_compression: bool = Field(default=config("ENABLE_REQUEST_COMPRESSION", default=True, cast=bool))
    enable_connection_pooling: bool = Field(default=config("ENABLE_CONNECTION_POOLING", default=True, cast=bool))
    
    # Advanced features
    enable_circuit_breakers: bool = Field(default=config("ENABLE_CIRCUIT_BREAKERS", default=True, cast=bool))
    enable_retry_logic: bool = Field(default=config("ENABLE_RETRY_LOGIC", default=True, cast=bool))
    enable_graceful_degradation: bool = Field(default=config("ENABLE_GRACEFUL_DEGRADATION", default=True, cast=bool))
    
    # =============================================================================
    # VALIDATORS
    # =============================================================================
    
    @validator('workers')
    def validate_workers(cls, v):
        if v is None:
            # Auto-calculate based on CPU cores and environment
            cpu_count = multiprocessing.cpu_count()
            if ProductionSettings().environment == DeploymentEnvironment.PRODUCTION:
                return min(32, max(2, cpu_count * 2))
            else:
                return min(8, max(1, cpu_count))
        
        if v < 1 or v > 128:
            raise ValueError("workers must be between 1 and 128")
        return v
    
    @validator('port')
    def validate_port(cls, v):
        if not 1024 <= v <= 65535:
            raise ValueError("port must be between 1024 and 65535")
        return v
    
    @validator('max_memory_mb')
    def validate_max_memory(cls, v):
        if v is None:
            # Auto-calculate based on available memory
            try:
                import psutil
                total_mb = psutil.virtual_memory().total / (1024 * 1024)
                return int(total_mb * 0.8)  # Use 80% of available memory
            except ImportError:
                return 4096  # Default 4GB
        
        if v < 512:
            raise ValueError("max_memory_mb must be at least 512MB")
        return v
    
    @validator('compression_level')
    def validate_compression_level(cls, v):
        if not 1 <= v <= 9:
            raise ValueError("compression_level must be between 1 and 9")
        return v
    
    @validator('db_pool_size')
    def validate_db_pool_size(cls, v):
        if v < 1 or v > 200:
            raise ValueError("db_pool_size must be between 1 and 200")
        return v
    
    def get_enabled_features(self) -> Dict[str, bool]:
        """Get all enabled features for this configuration."""
        return {
            "uvloop": self.enable_uvloop,
            "http2": self.enable_http2,
            "compression": self.enable_compression,
            "fast_serialization": self.enable_fast_serialization,
            "caching": self.enable_caching,
            "monitoring": self.enable_monitoring,
            "metrics": self.enable_metrics,
            "tracing": self.enable_tracing,
            "profiling": self.enable_profiling,
            "ssl": self.enable_ssl,
            "auto_scaling": self.enable_auto_scaling,
            "load_balancing": self.enable_load_balancing,
            "circuit_breakers": self.enable_circuit_breakers,
            "retry_logic": self.enable_retry_logic,
            "graceful_degradation": self.enable_graceful_degradation
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance-related configuration."""
        return {
            "production_level": self.production_level.value,
            "workers": self.workers,
            "max_connections": self.max_connections,
            "max_memory_mb": self.max_memory_mb,
            "compression_level": self.compression_level,
            "db_pool_size": self.db_pool_size,
            "redis_pool_size": self.redis_pool_size,
            "gc_threshold": self.gc_threshold,
            "enabled_optimizations": self.get_enabled_features()
        }
    
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get deployment-related configuration."""
        return {
            "environment": self.environment.value,
            "image": f"{self.container_registry}/{self.image_name}:{self.image_tag}",
            "kubernetes": {
                "namespace": self.k8s_namespace,
                "replicas": self.k8s_replicas,
                "resources": {
                    "requests": {
                        "cpu": self.k8s_cpu_request,
                        "memory": self.k8s_memory_request
                    },
                    "limits": {
                        "cpu": self.k8s_cpu_limit,
                        "memory": self.k8s_memory_limit
                    }
                }
            },
            "auto_scaling": {
                "enabled": self.enable_auto_scaling,
                "min_replicas": self.min_replicas,
                "max_replicas": self.max_replicas,
                "target_cpu": self.target_cpu_percent,
                "target_memory": self.target_memory_percent
            },
            "load_balancer": {
                "type": self.load_balancer_type.value,
                "enabled": self.enable_load_balancing
            }
        }
    
    class Config:
        env_prefix = "PROD_"
        env_file = ".env"
        case_sensitive = False


# Export main components
__all__ = [
    "ProductionSettings",
    "ProductionLevel",
    "DeploymentEnvironment",
    "DatabaseType",
    "LoadBalancerType"
] 