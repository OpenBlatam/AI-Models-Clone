"""
🔧 CONFIGURACIÓN DE PRODUCCIÓN - BLOG POSTS SYSTEM
=================================================

Configuración empresarial con:
- Variables de entorno para diferentes environments
- Configuración de cache multinivel
- Configuración de métricas y monitoreo
- Configuración de logging estructurado
- Configuración de rate limiting y circuit breakers
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"
    TESTING = "testing"

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class CacheConfig:
    """Cache configuration"""
    memory_ttl: int = 3600  # 1 hour
    redis_ttl: int = 7200   # 2 hours
    max_memory_size: int = 10000
    redis_url: str = "redis://localhost:6379"
    redis_max_connections: int = 100
    cluster_enabled: bool = False
    cluster_nodes: List[str] = None
    
    def __post_init__(self):
        self.redis_url = os.getenv("REDIS_URL", self.redis_url)
        self.redis_max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", self.redis_max_connections))
        self.cluster_enabled = os.getenv("REDIS_CLUSTER_ENABLED", "false").lower() == "true"

@dataclass
class AIConfig:
    """AI providers configuration"""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    
    # Rate limiting
    requests_per_minute: int = 100
    max_concurrent_requests: int = 20
    timeout_seconds: int = 30
    
    # Circuit breaker
    failure_threshold: int = 5
    recovery_timeout: int = 60
    
    def __post_init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        
        self.requests_per_minute = int(os.getenv("AI_REQUESTS_PER_MINUTE", self.requests_per_minute))
        self.max_concurrent_requests = int(os.getenv("AI_MAX_CONCURRENT", self.max_concurrent_requests))
        self.timeout_seconds = int(os.getenv("AI_TIMEOUT_SECONDS", self.timeout_seconds))

@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    
    sentry_enabled: bool = False
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "production"
    
    health_check_interval: int = 30
    metrics_collection_interval: int = 10
    
    def __post_init__(self):
        self.prometheus_enabled = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", self.prometheus_port))
        
        self.sentry_enabled = os.getenv("SENTRY_ENABLED", "false").lower() == "true"
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        self.sentry_environment = os.getenv("SENTRY_ENVIRONMENT", self.sentry_environment)

@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    cors_origins: List[str] = None
    cors_credentials: bool = True
    cors_methods: List[str] = None
    cors_headers: List[str] = None
    
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600  # 1 hour
    
    def __post_init__(self):
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", self.jwt_secret_key)
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", self.jwt_algorithm)
        self.jwt_expiration_hours = int(os.getenv("JWT_EXPIRATION_HOURS", self.jwt_expiration_hours))
        
        cors_origins_env = os.getenv("CORS_ORIGINS")
        if cors_origins_env:
            self.cors_origins = cors_origins_env.split(",")
        else:
            self.cors_origins = ["*"]  # Allow all in development
            
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", self.rate_limit_requests))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", self.rate_limit_window))

@dataclass
class DatabaseConfig:
    """Database configuration (if needed)"""
    url: Optional[str] = None
    min_pool_size: int = 5
    max_pool_size: int = 20
    pool_timeout: int = 30
    
    def __post_init__(self):
        self.url = os.getenv("DATABASE_URL")
        self.min_pool_size = int(os.getenv("DB_MIN_POOL_SIZE", self.min_pool_size))
        self.max_pool_size = int(os.getenv("DB_MAX_POOL_SIZE", self.max_pool_size))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", self.pool_timeout))

@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    max_requests: int = 1000
    max_requests_jitter: int = 100
    timeout: int = 120
    keepalive: int = 5
    
    # Performance settings
    uvloop_enabled: bool = True
    http2_enabled: bool = True
    
    def __post_init__(self):
        self.host = os.getenv("HOST", self.host)
        self.port = int(os.getenv("PORT", self.port))
        self.workers = int(os.getenv("WORKERS", self.workers))
        self.max_requests = int(os.getenv("MAX_REQUESTS", self.max_requests))
        self.timeout = int(os.getenv("TIMEOUT", self.timeout))
        
        self.uvloop_enabled = os.getenv("UVLOOP_ENABLED", "true").lower() == "true"
        self.http2_enabled = os.getenv("HTTP2_ENABLED", "true").lower() == "true"

class ProductionConfig:
    """Main production configuration"""
    
    def __init__(self, env: Environment = None):
        self.environment = env or Environment(os.getenv("ENVIRONMENT", "development"))
        
        # Initialize all configurations
        self.cache = CacheConfig()
        self.ai = AIConfig()
        self.monitoring = MonitoringConfig()
        self.security = SecurityConfig()
        self.database = DatabaseConfig()
        self.server = ServerConfig()
        
        # Adjust settings based on environment
        self._adjust_for_environment()
    
    def _adjust_for_environment(self):
        """Adjust configuration based on environment"""
        
        if self.environment == Environment.PRODUCTION:
            # Production optimizations
            self.server.workers = max(2, os.cpu_count())
            self.cache.max_memory_size = 50000
            self.ai.requests_per_minute = 500
            self.monitoring.prometheus_enabled = True
            self.monitoring.sentry_enabled = True
            
        elif self.environment == Environment.STAGING:
            # Staging optimizations
            self.server.workers = 2
            self.cache.max_memory_size = 20000
            self.ai.requests_per_minute = 200
            
        elif self.environment == Environment.DEVELOPMENT:
            # Development settings
            self.server.workers = 1
            self.cache.max_memory_size = 5000
            self.ai.requests_per_minute = 100
            self.monitoring.prometheus_enabled = False
            self.security.cors_origins = ["*"]
            
        elif self.environment == Environment.TESTING:
            # Testing settings
            self.server.workers = 1
            self.cache.redis_url = "redis://localhost:6380"  # Test Redis
            self.ai.requests_per_minute = 50
            self.monitoring.prometheus_enabled = False
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        
        log_level = LogLevel(os.getenv("LOG_LEVEL", "INFO")).value
        
        if self.environment == Environment.PRODUCTION:
            # Structured JSON logging for production
            return {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "json": {
                        "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
                        "datefmt": "%Y-%m-%d %H:%M:%S"
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "json",
                        "level": log_level
                    },
                    "file": {
                        "class": "logging.handlers.RotatingFileHandler",
                        "filename": "logs/blog_system.log",
                        "maxBytes": 10485760,  # 10MB
                        "backupCount": 5,
                        "formatter": "json",
                        "level": log_level
                    }
                },
                "root": {
                    "level": log_level,
                    "handlers": ["console", "file"]
                }
            }
        else:
            # Simple logging for development
            return {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "simple": {
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "simple",
                        "level": log_level
                    }
                },
                "root": {
                    "level": log_level,
                    "handlers": ["console"]
                }
            }
    
    def get_uvicorn_config(self) -> Dict[str, Any]:
        """Get Uvicorn server configuration"""
        return {
            "host": self.server.host,
            "port": self.server.port,
            "workers": self.server.workers if self.environment == Environment.PRODUCTION else 1,
            "loop": "uvloop" if self.server.uvloop_enabled else "asyncio",
            "http": "h11",  # HTTP/1.1 by default, h2 for HTTP/2
            "access_log": self.environment != Environment.PRODUCTION,
            "use_colors": self.environment == Environment.DEVELOPMENT,
            "reload": self.environment == Environment.DEVELOPMENT,
            "log_config": self.get_logging_config()
        }
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check required API keys for production
        if self.environment == Environment.PRODUCTION:
            if not self.ai.openai_api_key:
                issues.append("OPENAI_API_KEY is required for production")
            
            if self.security.jwt_secret_key == "your-secret-key-change-in-production":
                issues.append("JWT_SECRET_KEY must be changed for production")
            
            if self.monitoring.sentry_enabled and not self.monitoring.sentry_dsn:
                issues.append("SENTRY_DSN is required when Sentry is enabled")
        
        # Validate cache configuration
        if self.cache.redis_max_connections < 1:
            issues.append("Redis max connections must be at least 1")
        
        # Validate server configuration
        if self.server.port < 1 or self.server.port > 65535:
            issues.append("Server port must be between 1 and 65535")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "environment": self.environment.value,
            "cache": self.cache.__dict__,
            "ai": {k: v for k, v in self.ai.__dict__.items() if "key" not in k.lower()},
            "monitoring": self.monitoring.__dict__,
            "security": {k: v for k, v in self.security.__dict__.items() if "key" not in k.lower()},
            "database": self.database.__dict__,
            "server": self.server.__dict__
        }

# Global configuration instance
config = ProductionConfig()

# Validation on import
validation_issues = config.validate()
if validation_issues:
    print("⚠️  Configuration Issues:")
    for issue in validation_issues:
        print(f"   - {issue}")
    
    if config.environment == Environment.PRODUCTION:
        raise ValueError("Configuration validation failed for production environment")

# Export commonly used settings
ENVIRONMENT = config.environment
CACHE_CONFIG = config.cache
AI_CONFIG = config.ai
MONITORING_CONFIG = config.monitoring
SECURITY_CONFIG = config.security
SERVER_CONFIG = config.server

# Helper functions
def is_production() -> bool:
    return config.environment == Environment.PRODUCTION

def is_development() -> bool:
    return config.environment == Environment.DEVELOPMENT

def get_config() -> ProductionConfig:
    return config 