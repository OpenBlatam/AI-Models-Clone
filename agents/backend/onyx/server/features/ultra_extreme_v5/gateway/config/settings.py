"""
🚀 ULTRA-EXTREME V5 - GATEWAY SETTINGS
=======================================

Ultra-extreme gateway configuration with:
- Environment-based settings
- Advanced security configuration
- Performance tuning
- Monitoring configuration
- Service discovery settings
"""

import os
from typing import List, Optional, Dict
from pydantic import BaseSettings, Field, validator
from pydantic.types import SecretStr


class GatewaySettings(BaseSettings):
    """Ultra-extreme gateway settings"""
    
    # Application settings
    APP_NAME: str = Field(default="Ultra-Extreme V5 Gateway", env="APP_NAME")
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="production", env="ENVIRONMENT")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=4, env="WORKERS")
    USE_UVLOOP: bool = Field(default=True, env="USE_UVLOOP")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Redis settings
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_MAX_CONNECTIONS: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    REDIS_CONNECT_TIMEOUT: int = Field(default=5, env="REDIS_CONNECT_TIMEOUT")
    REDIS_SOCKET_TIMEOUT: int = Field(default=5, env="REDIS_SOCKET_TIMEOUT")
    
    # Service discovery
    SERVICE_REGISTRY_KEY: str = Field(default="service_registry", env="SERVICE_REGISTRY_KEY")
    SERVICE_HEALTH_CHECK_INTERVAL: int = Field(default=30, env="SERVICE_HEALTH_CHECK_INTERVAL")
    SERVICE_TIMEOUT: int = Field(default=10, env="SERVICE_TIMEOUT")
    
    # HTTP client settings
    HTTP_CONNECT_TIMEOUT: int = Field(default=5, env="HTTP_CONNECT_TIMEOUT")
    HTTP_READ_TIMEOUT: int = Field(default=30, env="HTTP_READ_TIMEOUT")
    HTTP_WRITE_TIMEOUT: int = Field(default=30, env="HTTP_WRITE_TIMEOUT")
    HTTP_POOL_TIMEOUT: int = Field(default=30, env="HTTP_POOL_TIMEOUT")
    HTTP_MAX_KEEPALIVE_CONNECTIONS: int = Field(default=20, env="HTTP_MAX_KEEPALIVE_CONNECTIONS")
    HTTP_MAX_CONNECTIONS: int = Field(default=100, env="HTTP_MAX_CONNECTIONS")
    HTTP_KEEPALIVE_EXPIRY: int = Field(default=60, env="HTTP_KEEPALIVE_EXPIRY")
    
    # CORS settings
    CORS_ENABLED: bool = Field(default=True, env="CORS_ENABLED")
    CORS_ORIGINS: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    CORS_METHODS: List[str] = Field(default=["*"], env="CORS_METHODS")
    CORS_HEADERS: List[str] = Field(default=["*"], env="CORS_HEADERS")
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    RATE_LIMIT_BURST: int = Field(default=200, env="RATE_LIMIT_BURST")
    
    # Authentication
    AUTH_ENABLED: bool = Field(default=True, env="AUTH_ENABLED")
    AUTH_SECRET_KEY: SecretStr = Field(default="your-secret-key", env="AUTH_SECRET_KEY")
    AUTH_ALGORITHM: str = Field(default="HS256", env="AUTH_ALGORITHM")
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="AUTH_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Circuit breaker
    CIRCUIT_BREAKER_ENABLED: bool = Field(default=True, env="CIRCUIT_BREAKER_ENABLED")
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = Field(default=5, env="CIRCUIT_BREAKER_FAILURE_THRESHOLD")
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = Field(default=60, env="CIRCUIT_BREAKER_RECOVERY_TIMEOUT")
    CIRCUIT_BREAKER_EXPECTED_EXCEPTION: List[str] = Field(
        default=["httpx.TimeoutException", "httpx.ConnectError"],
        env="CIRCUIT_BREAKER_EXPECTED_EXCEPTION"
    )
    
    # Load balancing
    LOAD_BALANCER_ENABLED: bool = Field(default=True, env="LOAD_BALANCER_ENABLED")
    LOAD_BALANCER_STRATEGY: str = Field(default="round_robin", env="LOAD_BALANCER_STRATEGY")
    LOAD_BALANCER_HEALTH_CHECK_ENABLED: bool = Field(default=True, env="LOAD_BALANCER_HEALTH_CHECK_ENABLED")
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # Health checks
    HEALTH_CHECK_INTERVAL: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    HEALTH_CHECK_TIMEOUT: int = Field(default=5, env="HEALTH_CHECK_TIMEOUT")
    
    # Security
    SECURITY_HEADERS_ENABLED: bool = Field(default=True, env="SECURITY_HEADERS_ENABLED")
    SECURITY_HEADERS: Dict[str, str] = Field(
        default={
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        },
        env="SECURITY_HEADERS"
    )
    
    # Performance
    MAX_REQUEST_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_REQUEST_SIZE")  # 10MB
    REQUEST_TIMEOUT: int = Field(default=300, env="REQUEST_TIMEOUT")  # 5 minutes
    RESPONSE_TIMEOUT: int = Field(default=300, env="RESPONSE_TIMEOUT")  # 5 minutes
    
    # Caching
    CACHE_ENABLED: bool = Field(default=True, env="CACHE_ENABLED")
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    CACHE_MAX_SIZE: int = Field(default=1000, env="CACHE_MAX_SIZE")
    
    # Metrics
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    METRICS_INTERVAL: int = Field(default=60, env="METRICS_INTERVAL")
    
    # Tracing
    TRACING_ENABLED: bool = Field(default=True, env="TRACING_ENABLED")
    TRACING_SERVICE_NAME: str = Field(default="ultra-extreme-gateway", env="TRACING_SERVICE_NAME")
    
    # SSL/TLS
    SSL_ENABLED: bool = Field(default=False, env="SSL_ENABLED")
    SSL_CERT_FILE: Optional[str] = Field(default=None, env="SSL_CERT_FILE")
    SSL_KEY_FILE: Optional[str] = Field(default=None, env="SSL_KEY_FILE")
    
    # API Keys
    API_KEYS_ENABLED: bool = Field(default=True, env="API_KEYS_ENABLED")
    API_KEYS: List[str] = Field(default=[], env="API_KEYS")
    
    # Service endpoints
    CONTENT_SERVICE_URL: str = Field(default="http://localhost:8001", env="CONTENT_SERVICE_URL")
    OPTIMIZATION_SERVICE_URL: str = Field(default="http://localhost:8002", env="OPTIMIZATION_SERVICE_URL")
    AI_SERVICE_URL: str = Field(default="http://localhost:8003", env="AI_SERVICE_URL")
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("CORS_METHODS", pre=True)
    def parse_cors_methods(cls, v):
        """Parse CORS methods from string"""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @validator("CORS_HEADERS", pre=True)
    def parse_cors_headers(cls, v):
        """Parse CORS headers from string"""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v
    
    @validator("API_KEYS", pre=True)
    def parse_api_keys(cls, v):
        """Parse API keys from string"""
        if isinstance(v, str):
            return [key.strip() for key in v.split(",")]
        return v
    
    @validator("CIRCUIT_BREAKER_EXPECTED_EXCEPTION", pre=True)
    def parse_circuit_breaker_exceptions(cls, v):
        """Parse circuit breaker exceptions from string"""
        if isinstance(v, str):
            return [exc.strip() for exc in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = GatewaySettings()


def get_settings() -> GatewaySettings:
    """Get the settings instance"""
    return settings 