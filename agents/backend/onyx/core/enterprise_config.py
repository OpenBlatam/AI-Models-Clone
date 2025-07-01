"""
🚀 ENTERPRISE CONFIGURATION
==========================

Configuration management for enterprise-grade FastAPI applications
with microservices, serverless, and cloud-native patterns.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class SecurityConfig:
    """Security configuration for enterprise applications"""
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "change-me-in-production"))
    allowed_origins: List[str] = field(default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "*").split(","))
    trusted_hosts: List[str] = field(default_factory=lambda: os.getenv("TRUSTED_HOSTS", "*").split(","))
    oauth2_scheme: str = "Bearer"
    enable_https_redirect: bool = field(default_factory=lambda: os.getenv("ENABLE_HTTPS_REDIRECT", "false").lower() == "true")
    session_timeout: int = int(os.getenv("SESSION_TIMEOUT", "3600"))
    max_login_attempts: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    
    # Security headers
    enable_security_headers: bool = True
    content_security_policy: str = "default-src 'self'"
    hsts_max_age: int = 31536000

@dataclass
class CacheConfig:
    """Caching configuration with Redis and memory tiers"""
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    redis_max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
    default_ttl: int = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))
    memory_cache_size: int = int(os.getenv("MEMORY_CACHE_SIZE", "10000"))
    enable_compression: bool = field(default_factory=lambda: os.getenv("CACHE_COMPRESSION", "true").lower() == "true")
    compression_threshold: int = int(os.getenv("CACHE_COMPRESSION_THRESHOLD", "1024"))
    
    # Cache strategies
    enable_distributed_cache: bool = True
    enable_memory_cache: bool = True
    cache_warming_enabled: bool = True

@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    enabled: bool = field(default_factory=lambda: os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true")
    requests_per_minute: int = int(os.getenv("RATE_LIMIT_RPM", "1000"))
    requests_per_hour: int = int(os.getenv("RATE_LIMIT_RPH", "10000"))
    burst_size: int = int(os.getenv("RATE_LIMIT_BURST", "100"))
    
    # Advanced rate limiting
    per_user_limit: int = int(os.getenv("RATE_LIMIT_PER_USER", "100"))
    per_ip_limit: int = int(os.getenv("RATE_LIMIT_PER_IP", "500"))
    exempt_ips: List[str] = field(default_factory=lambda: os.getenv("RATE_LIMIT_EXEMPT_IPS", "").split(",") if os.getenv("RATE_LIMIT_EXEMPT_IPS") else [])

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = int(os.getenv("CB_FAILURE_THRESHOLD", "5"))
    recovery_timeout: int = int(os.getenv("CB_RECOVERY_TIMEOUT", "60"))
    half_open_max_calls: int = int(os.getenv("CB_HALF_OPEN_CALLS", "5"))
    slow_call_threshold: float = float(os.getenv("CB_SLOW_CALL_THRESHOLD", "5.0"))
    
    # Per-service configuration
    service_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    enable_metrics: bool = field(default_factory=lambda: os.getenv("ENABLE_METRICS", "true").lower() == "true")
    enable_tracing: bool = field(default_factory=lambda: os.getenv("ENABLE_TRACING", "true").lower() == "true")
    enable_logging: bool = field(default_factory=lambda: os.getenv("ENABLE_LOGGING", "true").lower() == "true")
    
    # Prometheus configuration
    metrics_endpoint: str = "/metrics"
    metrics_basic_auth: Optional[str] = os.getenv("METRICS_AUTH")
    
    # Tracing configuration
    jaeger_endpoint: Optional[str] = os.getenv("JAEGER_ENDPOINT")
    trace_sample_rate: float = float(os.getenv("TRACE_SAMPLE_RATE", "0.1"))
    
    # Logging configuration
    log_level: LogLevel = LogLevel(os.getenv("LOG_LEVEL", "INFO"))
    structured_logging: bool = field(default_factory=lambda: os.getenv("STRUCTURED_LOGGING", "true").lower() == "true")
    log_to_file: bool = field(default_factory=lambda: os.getenv("LOG_TO_FILE", "false").lower() == "true")
    log_file_path: str = os.getenv("LOG_FILE_PATH", "/var/log/app.log")

@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    max_workers: int = int(os.getenv("MAX_WORKERS", "10"))
    worker_connections: int = int(os.getenv("WORKER_CONNECTIONS", "1000"))
    keepalive_timeout: int = int(os.getenv("KEEPALIVE_TIMEOUT", "75"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Async configuration
    event_loop_policy: str = os.getenv("EVENT_LOOP_POLICY", "asyncio")
    enable_uvloop: bool = field(default_factory=lambda: os.getenv("ENABLE_UVLOOP", "true").lower() == "true")
    
    # Connection pooling
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    http_pool_connections: int = int(os.getenv("HTTP_POOL_CONNECTIONS", "50"))
    http_pool_maxsize: int = int(os.getenv("HTTP_POOL_MAXSIZE", "100"))

@dataclass
class ServerlessConfig:
    """Serverless optimization configuration"""
    cold_start_optimization: bool = field(default_factory=lambda: os.getenv("COLD_START_OPT", "true").lower() == "true")
    preload_modules: List[str] = field(default_factory=lambda: os.getenv("PRELOAD_MODULES", "").split(",") if os.getenv("PRELOAD_MODULES") else [])
    lazy_loading: bool = field(default_factory=lambda: os.getenv("LAZY_LOADING", "true").lower() == "true")
    minimize_imports: bool = field(default_factory=lambda: os.getenv("MINIMIZE_IMPORTS", "true").lower() == "true")
    
    # AWS Lambda specific
    lambda_timeout: int = int(os.getenv("LAMBDA_TIMEOUT", "300"))
    lambda_memory: int = int(os.getenv("LAMBDA_MEMORY", "512"))
    provisioned_concurrency: int = int(os.getenv("PROVISIONED_CONCURRENCY", "0"))

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./app.db"))
    echo: bool = field(default_factory=lambda: os.getenv("DB_ECHO", "false").lower() == "true")
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # Read replicas
    read_replica_urls: List[str] = field(default_factory=lambda: os.getenv("READ_replica_urls", "").split(",") if os.getenv("READ_replica_urls") else [])
    enable_read_replicas: bool = bool(field(default_factory=lambda: os.getenv("read_replica_urls", "")))

@dataclass
class EnterpriseConfig:
    """Main enterprise configuration combining all subsystems"""
    
    # Application basics
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Enterprise API"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))
    environment: Environment = field(default_factory=lambda: Environment(os.getenv("ENVIRONMENT", "development")))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    
    # Server configuration
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = int(os.getenv("PORT", "8000"))
    reload: bool = field(default_factory=lambda: os.getenv("RELOAD", "false").lower() == "true")
    
    # Sub-configurations
    security: SecurityConfig = field(default_factory=SecurityConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    serverless: ServerlessConfig = field(default_factory=ServerlessConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # API Gateway integration
    api_gateway_enabled: bool = field(default_factory=lambda: os.getenv("API_GATEWAY_ENABLED", "false").lower() == "true")
    api_gateway_url: Optional[str] = os.getenv("API_GATEWAY_URL")
    api_prefix: str = field(default_factory=lambda: os.getenv("API_PREFIX", "/api/v1"))
    
    # Health checks
    health_check_interval: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    enable_startup_probe: bool = field(default_factory=lambda: os.getenv("ENABLE_STARTUP_PROBE", "true").lower() == "true")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == Environment.DEVELOPMENT
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        if self.is_production:
            if self.security.secret_key == "change-me-in-production":
                issues.append("SECRET_KEY must be changed in production")
            
            if "*" in self.security.allowed_origins:
                issues.append("CORS origins should be restricted in production")
            
            if self.debug:
                issues.append("DEBUG should be False in production")
        
        if self.cache.redis_url == "redis://localhost:6379" and self.is_production:
            issues.append("Redis URL should point to production Redis instance")
        
        if self.monitoring.enable_metrics and not self.monitoring.metrics_basic_auth and self.is_production:
            issues.append("Metrics endpoint should be protected in production")
        
        return issues
    
    def get_uvicorn_config(self) -> Dict[str, Any]:
        """Get configuration for Uvicorn server"""
        config = {
            "host": self.host,
            "port": self.port,
            "reload": self.reload and self.is_development,
            "workers": 1 if self.is_development else self.performance.max_workers,
            "access_log": self.monitoring.enable_logging,
            "log_level": self.monitoring.log_level.lower(),
        }
        
        if self.performance.enable_uvloop:
            config["loop"] = "uvloop"
        
        return config

# Global configuration instance
config = EnterpriseConfig()

# Validate configuration on import
validation_issues = config.validate()
if validation_issues:
    import logging
    logger = logging.getLogger(__name__)
    for issue in validation_issues:
        logger.warning(f"Configuration issue: {issue}") 