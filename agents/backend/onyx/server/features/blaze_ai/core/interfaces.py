"""
Core interfaces and configuration for the Blaze AI module.

This module defines the fundamental interfaces, configuration classes,
and system modes that form the foundation of the Blaze AI architecture.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator

# =============================================================================
# Enums
# =============================================================================

class SystemMode(Enum):
    """System operation modes."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# =============================================================================
# Configuration Models
# =============================================================================

class DatabaseConfig(BaseModel):
    """Database configuration."""
    url: str = "sqlite:///blaze_ai.db"
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=0, le=200)
    pool_timeout: int = Field(default=30, ge=1, le=300)
    pool_recycle: int = Field(default=3600, ge=60, le=7200)
    echo: bool = False
    
    @validator('url')
    def validate_url(cls, v):
        """Validate database URL format."""
        if not v or not isinstance(v, str):
            raise ValueError("Database URL must be a non-empty string")
        return v

class CacheConfig(BaseModel):
    """Cache configuration."""
    redis_url: Optional[str] = None
    ttl: int = Field(default=3600, ge=60, le=86400)
    max_size: int = Field(default=10000, ge=100, le=1000000)
    enable_local_cache: bool = True
    enable_distributed_cache: bool = False
    
    @validator('redis_url')
    def validate_redis_url(cls, v):
        """Validate Redis URL if provided."""
        if v is not None and not v.startswith(('redis://', 'rediss://')):
            raise ValueError("Redis URL must start with redis:// or rediss://")
        return v

class SecurityConfig(BaseModel):
    """Security configuration."""
    enable_encryption: bool = False
    encryption_key: Optional[str] = None
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = Field(default=100, ge=1, le=10000)
    enable_audit_logging: bool = True
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])
    
    @validator('encryption_key')
    def validate_encryption_key(cls, v, values):
        """Validate encryption key if encryption is enabled."""
        if values.get('enable_encryption') and not v:
            raise ValueError("Encryption key is required when encryption is enabled")
        return v

class MonitoringConfig(BaseModel):
    """Monitoring and observability configuration."""
    enable_metrics: bool = True
    enable_tracing: bool = False
    enable_profiling: bool = False
    metrics_port: int = Field(default=9090, ge=1024, le=65535)
    prometheus_endpoint: str = "/metrics"
    health_check_interval: int = Field(default=30, ge=5, le=300)
    enable_alerting: bool = True

class ModelConfig(BaseModel):
    """Model-specific configuration."""
    device: str = "auto"
    precision: str = Field(default="float16", regex="^(float16|float32|bfloat16|int8)$")
    enable_amp: bool = True
    max_batch_size: int = Field(default=32, ge=1, le=512)
    model_cache_dir: Optional[str] = None
    enable_model_compilation: bool = False
    enable_quantization: bool = False
    
    @validator('device')
    def validate_device(cls, v):
        """Validate device specification."""
        valid_devices = ['auto', 'cpu', 'cuda', 'mps']
        if v not in valid_devices and not v.startswith('cuda:'):
            raise ValueError(f"Device must be one of {valid_devices} or cuda:N")
        return v

class APIConfig(BaseModel):
    """API configuration."""
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1024, le=65535)
    workers: int = Field(default=1, ge=1, le=32)
    enable_cors: bool = True
    enable_docs: bool = True
    api_prefix: str = "/api/v1"
    timeout: int = Field(default=30, ge=5, le=300)
    max_request_size: int = Field(default=10 * 1024 * 1024, ge=1024 * 1024, le=100 * 1024 * 1024)

class GradioConfig(BaseModel):
    """Gradio interface configuration."""
    enable_gradio: bool = True
    gradio_port: int = Field(default=7860, ge=1024, le=65535)
    share: bool = False
    auth: Optional[Dict[str, str]] = None

class CoreConfig(BaseModel):
    """Main configuration class for the Blaze AI module."""
    system_mode: SystemMode = Field(default=SystemMode.DEVELOPMENT, description="System operation mode")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # Core settings
    data_dir: str = Field(default="./data", description="Data directory")
    models_dir: str = Field(default="./models", description="Models directory")
    checkpoints_dir: str = Field(default="./checkpoints", description="Checkpoints directory")
    
    # Performance settings
    enable_async: bool = Field(default=True, description="Enable async operations")
    max_concurrent_requests: int = Field(default=100, ge=1, le=1000, description="Maximum concurrent requests")
    enable_circuit_breaker: bool = Field(default=True, description="Enable circuit breaker")
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting")
    enable_caching: bool = Field(default=True, description="Enable caching")
    
    # Nested configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig, description="Database configuration")
    cache: CacheConfig = Field(default_factory=CacheConfig, description="Cache configuration")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="Security configuration")
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig, description="Monitoring configuration")
    model: ModelConfig = Field(default_factory=ModelConfig, description="Model configuration")
    api: APIConfig = Field(default_factory=APIConfig, description="API configuration")
    gradio: GradioConfig = Field(default_factory=GradioConfig, description="Gradio configuration")
    
    @validator('data_dir', 'models_dir', 'checkpoints_dir')
    def validate_directories(cls, v):
        """Ensure directories exist."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path.absolute())
    
    @root_validator
    def validate_config_consistency(cls, values):
        """Validate configuration consistency."""
        # Check if Gradio port conflicts with API port
        if (values.get('gradio', {}).get('enable_gradio') and 
            values.get('api', {}).get('port') == values.get('gradio', {}).get('gradio_port')):
            raise ValueError("Gradio port cannot be the same as API port")
        
        # Check if metrics port conflicts with other ports
        api_port = values.get('api', {}).get('port')
        gradio_port = values.get('gradio', {}).get('gradio_port')
        metrics_port = values.get('monitoring', {}).get('metrics_port')
        
        if metrics_port in [api_port, gradio_port]:
            raise ValueError("Metrics port cannot conflict with API or Gradio ports")
        
        return values
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"  # Prevent additional fields

# =============================================================================
# Service Management
# =============================================================================

class ServiceContainer:
    """Dependency injection container for services."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._aliases: Dict[str, str] = {}
    
    def register_service(self, name: str, service: Any, aliases: Optional[List[str]] = None) -> None:
        """Register a service instance."""
        self._services[name] = service
        
        # Register aliases
        if aliases:
            for alias in aliases:
                self._aliases[alias] = name
    
    def register_factory(self, name: str, factory: callable, aliases: Optional[List[str]] = None) -> None:
        """Register a service factory."""
        self._factories[name] = factory
        
        # Register aliases
        if aliases:
            for alias in aliases:
                self._aliases[alias] = name
    
    def register_singleton(self, name: str, service: Any, aliases: Optional[List[str]] = None) -> None:
        """Register a singleton service."""
        self._singletons[name] = service
        
        # Register aliases
        if aliases:
            for alias in aliases:
                self._aliases[alias] = name
    
    def get_service(self, name: str) -> Any:
        """Get a service by name."""
        # Resolve aliases
        actual_name = self._aliases.get(name, name)
        
        # Check singletons first
        if actual_name in self._singletons:
            return self._singletons[actual_name]
        
        # Check registered services
        if actual_name in self._services:
            return self._services[actual_name]
        
        # Check factories
        if actual_name in self._factories:
            service = self._factories[actual_name]()
            self._services[actual_name] = service
            return service
        
        raise KeyError(f"Service '{name}' not found")
    
    def has_service(self, name: str) -> bool:
        """Check if a service exists."""
        actual_name = self._aliases.get(name, name)
        return (actual_name in self._services or 
                actual_name in self._factories or 
                actual_name in self._singletons)
    
    def remove_service(self, name: str) -> None:
        """Remove a service."""
        actual_name = self._aliases.get(name, name)
        self._services.pop(actual_name, None)
        self._factories.pop(actual_name, None)
        self._singletons.pop(actual_name, None)
        
        # Remove aliases
        aliases_to_remove = [k for k, v in self._aliases.items() if v == actual_name]
        for alias in aliases_to_remove:
            self._aliases.pop(alias, None)
    
    def clear(self) -> None:
        """Clear all services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._aliases.clear()
    
    def list_services(self) -> Dict[str, List[str]]:
        """List all registered services by category."""
        return {
            "services": list(self._services.keys()),
            "factories": list(self._factories.keys()),
            "singletons": list(self._singletons.keys()),
            "aliases": list(self._aliases.keys())
        }

# =============================================================================
# Health Monitoring
# =============================================================================

class HealthStatus(BaseModel):
    """Health status information for a component."""
    component: str
    status: str
    message: str
    timestamp: float
    details: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status values."""
        valid_statuses = ['healthy', 'unhealthy', 'degraded', 'unknown']
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v

class SystemHealth:
    """System health monitoring and reporting."""
    
    def __init__(self):
        self.components: Dict[str, HealthStatus] = {}
        self.overall_status: str = "unknown"
        self.last_update: float = 0.0
        self._lock = asyncio.Lock()
    
    async def update_component(self, component: str, status: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Update component health status."""
        import time
        async with self._lock:
            self.components[component] = HealthStatus(
                component=component,
                status=status,
                message=message,
                timestamp=time.time(),
                details=details or {}
            )
            self.last_update = time.time()
            await self._update_overall_status()
    
    def get_component_status(self, component: str) -> Optional[HealthStatus]:
        """Get status of a specific component."""
        return self.components.get(component)
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report."""
        import time
        return {
            "overall_status": self.overall_status,
            "timestamp": time.time(),
            "last_update": self.last_update,
            "components": {name: status.dict() for name, status in self.components.items()},
            "summary": {
                "total_components": len(self.components),
                "healthy_components": len([c for c in self.components.values() if c.status == "healthy"]),
                "unhealthy_components": len([c for c in self.components.values() if c.status == "unhealthy"]),
                "degraded_components": len([c for c in self.components.values() if c.status == "degraded"])
            }
        }
    
    async def _update_overall_status(self) -> None:
        """Update overall system status based on component statuses."""
        if not self.components:
            self.overall_status = "unknown"
            return
        
        statuses = [comp.status for comp in self.components.values()]
        
        if "unhealthy" in statuses:
            self.overall_status = "unhealthy"
        elif "degraded" in statuses:
            self.overall_status = "degraded"
        else:
            self.overall_status = "healthy"

# Export main classes
__all__ = [
    "SystemMode",
    "LogLevel",
    "DatabaseConfig",
    "CacheConfig", 
    "SecurityConfig",
    "MonitoringConfig",
    "ModelConfig",
    "APIConfig",
    "GradioConfig",
    "CoreConfig",
    "ServiceContainer",
    "HealthStatus",
    "SystemHealth"
]


