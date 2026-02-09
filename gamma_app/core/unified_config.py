"""
Unified Configuration - Centralized configuration management
Consolidates all configuration settings into a single, optimized service
"""

import os
import yaml
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import asyncio
from datetime import datetime
import hashlib
import secrets

logger = logging.getLogger(__name__)

class Environment(Enum):
    """Environment Types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(Enum):
    """Log Levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class DatabaseConfig:
    """Database Configuration"""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    ssl_mode: str = "prefer"

@dataclass
class RedisConfig:
    """Redis Configuration"""
    url: str
    max_connections: int = 20
    retry_on_timeout: bool = True
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[int, int] = field(default_factory=dict)

@dataclass
class SecurityConfig:
    """Security Configuration"""
    secret_key: str
    jwt_secret: str
    encryption_key: str
    password_min_length: int = 8
    session_timeout: int = 3600
    max_login_attempts: int = 5
    lockout_duration: int = 900
    enable_2fa: bool = True
    enable_ip_blocking: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600

@dataclass
class AIConfig:
    """AI Configuration"""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    local_models_path: str = "./models"
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    enable_fine_tuning: bool = True
    enable_quantization: bool = True

@dataclass
class StorageConfig:
    """Storage Configuration"""
    local_path: str = "./storage"
    s3_bucket: Optional[str] = None
    s3_region: str = "us-east-1"
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = field(default_factory=lambda: [
        "jpg", "jpeg", "png", "gif", "pdf", "doc", "docx", "txt", "csv", "json"
    ])

@dataclass
class MonitoringConfig:
    """Monitoring Configuration"""
    enable_prometheus: bool = True
    prometheus_port: int = 9090
    enable_grafana: bool = True
    grafana_port: int = 3000
    log_level: LogLevel = LogLevel.INFO
    enable_structured_logging: bool = True
    log_file_path: str = "./logs/gamma_app.log"
    max_log_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class PerformanceConfig:
    """Performance Configuration"""
    max_workers: int = 10
    max_concurrent_requests: int = 100
    request_timeout: int = 30
    enable_caching: bool = True
    cache_ttl: int = 3600
    enable_compression: bool = True
    compression_level: int = 6

@dataclass
class IntegrationConfig:
    """Integration Configuration"""
    webhook_timeout: int = 30
    webhook_retry_attempts: int = 3
    webhook_retry_delay: int = 5
    api_timeout: int = 30
    api_retry_attempts: int = 3
    enable_ssl_verification: bool = True

@dataclass
class AdvancedConfig:
    """Advanced Configuration"""
    # Blockchain
    blockchain_networks: Dict[str, str] = field(default_factory=dict)
    enable_blockchain: bool = False
    
    # Quantum Computing
    quantum_backends: List[str] = field(default_factory=lambda: ["simulator"])
    enable_quantum: bool = False
    
    # IoT
    iot_broker_url: Optional[str] = None
    iot_username: Optional[str] = None
    iot_password: Optional[str] = None
    enable_iot: bool = False
    
    # AR/VR
    ar_vr_platforms: List[str] = field(default_factory=lambda: ["webxr"])
    enable_ar_vr: bool = False
    
    # Robotics
    robot_api_endpoints: Dict[str, str] = field(default_factory=dict)
    enable_robotics: bool = False
    
    # Metaverse
    metaverse_servers: List[str] = field(default_factory=list)
    enable_metaverse: bool = False
    
    # Biotech
    biotech_databases: List[str] = field(default_factory=list)
    enable_biotech: bool = False

@dataclass
class UnifiedConfig:
    """Unified Configuration"""
    environment: Environment
    app_name: str = "GammaApp"
    version: str = "1.0.0"
    debug: bool = False
    
    # Core configurations
    database: DatabaseConfig
    redis: RedisConfig
    security: SecurityConfig
    ai: AIConfig
    storage: StorageConfig
    monitoring: MonitoringConfig
    performance: PerformanceConfig
    integration: IntegrationConfig
    advanced: AdvancedConfig
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    config_hash: str = ""

class UnifiedConfigService:
    """
    Unified Configuration Service - Centralized configuration management
    Handles loading, validation, hot-reloading, and management of all configurations
    """
    
    def __init__(self, config_path: str = "./config"):
        self.config_path = Path(config_path)
        self.config_file = self.config_path / "config.yaml"
        self.env_file = self.config_path / ".env"
        self.secrets_file = self.config_path / "secrets.yaml"
        
        self.current_config: Optional[UnifiedConfig] = None
        self.config_watchers: List[callable] = []
        self.watch_task: Optional[asyncio.Task] = None
        
        # Create config directory if it doesn't exist
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("UnifiedConfigService initialized")
    
    async def load_config(self, environment: Environment = None) -> UnifiedConfig:
        """Load configuration from files and environment variables"""
        try:
            # Determine environment
            if environment is None:
                env_str = os.getenv("GAMMA_APP_ENV", "development")
                environment = Environment(env_str)
            
            # Load base configuration
            config_data = await self._load_config_file()
            
            # Override with environment-specific config
            env_config = await self._load_environment_config(environment)
            config_data.update(env_config)
            
            # Override with environment variables
            config_data = self._apply_environment_overrides(config_data)
            
            # Load secrets
            secrets = await self._load_secrets()
            config_data.update(secrets)
            
            # Create configuration object
            config = self._create_config_object(config_data, environment)
            
            # Validate configuration
            await self._validate_config(config)
            
            # Generate config hash
            config.config_hash = self._generate_config_hash(config)
            
            self.current_config = config
            logger.info(f"Configuration loaded for environment: {environment.value}")
            
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    async def _load_config_file(self) -> Dict[str, Any]:
        """Load base configuration file"""
        try:
            if self.config_file.exists():
                async with aiofiles.open(self.config_file, 'r') as f:
                    content = await f.read()
                    return yaml.safe_load(content) or {}
            else:
                # Create default config file
                await self._create_default_config()
                return {}
                
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            return {}
    
    async def _load_environment_config(self, environment: Environment) -> Dict[str, Any]:
        """Load environment-specific configuration"""
        try:
            env_config_file = self.config_path / f"{environment.value}.yaml"
            
            if env_config_file.exists():
                async with aiofiles.open(env_config_file, 'r') as f:
                    content = await f.read()
                    return yaml.safe_load(content) or {}
            
            return {}
            
        except Exception as e:
            logger.error(f"Error loading environment config: {e}")
            return {}
    
    def _apply_environment_overrides(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides"""
        try:
            # Database overrides
            if os.getenv("DATABASE_URL"):
                config_data.setdefault("database", {})["url"] = os.getenv("DATABASE_URL")
            
            if os.getenv("REDIS_URL"):
                config_data.setdefault("redis", {})["url"] = os.getenv("REDIS_URL")
            
            # Security overrides
            if os.getenv("SECRET_KEY"):
                config_data.setdefault("security", {})["secret_key"] = os.getenv("SECRET_KEY")
            
            if os.getenv("JWT_SECRET"):
                config_data.setdefault("security", {})["jwt_secret"] = os.getenv("JWT_SECRET")
            
            # AI overrides
            if os.getenv("OPENAI_API_KEY"):
                config_data.setdefault("ai", {})["openai_api_key"] = os.getenv("OPENAI_API_KEY")
            
            if os.getenv("ANTHROPIC_API_KEY"):
                config_data.setdefault("ai", {})["anthropic_api_key"] = os.getenv("ANTHROPIC_API_KEY")
            
            # Storage overrides
            if os.getenv("S3_BUCKET"):
                config_data.setdefault("storage", {})["s3_bucket"] = os.getenv("S3_BUCKET")
            
            if os.getenv("S3_ACCESS_KEY"):
                config_data.setdefault("storage", {})["s3_access_key"] = os.getenv("S3_ACCESS_KEY")
            
            if os.getenv("S3_SECRET_KEY"):
                config_data.setdefault("storage", {})["s3_secret_key"] = os.getenv("S3_SECRET_KEY")
            
            return config_data
            
        except Exception as e:
            logger.error(f"Error applying environment overrides: {e}")
            return config_data
    
    async def _load_secrets(self) -> Dict[str, Any]:
        """Load secrets from secrets file"""
        try:
            if self.secrets_file.exists():
                async with aiofiles.open(self.secrets_file, 'r') as f:
                    content = await f.read()
                    return yaml.safe_load(content) or {}
            
            return {}
            
        except Exception as e:
            logger.error(f"Error loading secrets: {e}")
            return {}
    
    def _create_config_object(self, config_data: Dict[str, Any], environment: Environment) -> UnifiedConfig:
        """Create UnifiedConfig object from data"""
        try:
            # Create sub-configurations
            database_config = DatabaseConfig(**config_data.get("database", {}))
            redis_config = RedisConfig(**config_data.get("redis", {}))
            security_config = SecurityConfig(**config_data.get("security", {}))
            ai_config = AIConfig(**config_data.get("ai", {}))
            storage_config = StorageConfig(**config_data.get("storage", {}))
            monitoring_config = MonitoringConfig(**config_data.get("monitoring", {}))
            performance_config = PerformanceConfig(**config_data.get("performance", {}))
            integration_config = IntegrationConfig(**config_data.get("integration", {}))
            advanced_config = AdvancedConfig(**config_data.get("advanced", {}))
            
            # Create main configuration
            config = UnifiedConfig(
                environment=environment,
                app_name=config_data.get("app_name", "GammaApp"),
                version=config_data.get("version", "1.0.0"),
                debug=config_data.get("debug", False),
                database=database_config,
                redis=redis_config,
                security=security_config,
                ai=ai_config,
                storage=storage_config,
                monitoring=monitoring_config,
                performance=performance_config,
                integration=integration_config,
                advanced=advanced_config
            )
            
            return config
            
        except Exception as e:
            logger.error(f"Error creating config object: {e}")
            raise
    
    async def _validate_config(self, config: UnifiedConfig):
        """Validate configuration"""
        try:
            # Validate required fields
            if not config.security.secret_key:
                raise ValueError("Secret key is required")
            
            if not config.database.url:
                raise ValueError("Database URL is required")
            
            if not config.redis.url:
                raise ValueError("Redis URL is required")
            
            # Validate URLs
            if not config.database.url.startswith(("postgresql://", "sqlite://")):
                raise ValueError("Invalid database URL format")
            
            if not config.redis.url.startswith(("redis://", "rediss://")):
                raise ValueError("Invalid Redis URL format")
            
            # Validate numeric ranges
            if config.performance.max_workers < 1:
                raise ValueError("Max workers must be at least 1")
            
            if config.security.password_min_length < 6:
                raise ValueError("Password minimum length must be at least 6")
            
            logger.info("Configuration validation passed")
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    def _generate_config_hash(self, config: UnifiedConfig) -> str:
        """Generate hash for configuration"""
        try:
            config_str = json.dumps(config.__dict__, default=str, sort_keys=True)
            return hashlib.sha256(config_str.encode()).hexdigest()[:16]
            
        except Exception as e:
            logger.error(f"Error generating config hash: {e}")
            return ""
    
    async def _create_default_config(self):
        """Create default configuration file"""
        try:
            default_config = {
                "app_name": "GammaApp",
                "version": "1.0.0",
                "debug": False,
                
                "database": {
                    "url": "postgresql://user:password@localhost:5432/gamma_app",
                    "pool_size": 10,
                    "max_overflow": 20,
                    "pool_timeout": 30,
                    "pool_recycle": 3600,
                    "echo": False,
                    "ssl_mode": "prefer"
                },
                
                "redis": {
                    "url": "redis://localhost:6379/0",
                    "max_connections": 20,
                    "retry_on_timeout": True,
                    "socket_keepalive": True
                },
                
                "security": {
                    "secret_key": secrets.token_urlsafe(32),
                    "jwt_secret": secrets.token_urlsafe(32),
                    "encryption_key": secrets.token_urlsafe(32),
                    "password_min_length": 8,
                    "session_timeout": 3600,
                    "max_login_attempts": 5,
                    "lockout_duration": 900,
                    "enable_2fa": True,
                    "enable_ip_blocking": True,
                    "rate_limit_requests": 100,
                    "rate_limit_window": 3600
                },
                
                "ai": {
                    "local_models_path": "./models",
                    "max_tokens": 2048,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "enable_fine_tuning": True,
                    "enable_quantization": True
                },
                
                "storage": {
                    "local_path": "./storage",
                    "max_file_size": 104857600,  # 100MB
                    "allowed_extensions": [
                        "jpg", "jpeg", "png", "gif", "pdf", "doc", "docx", "txt", "csv", "json"
                    ]
                },
                
                "monitoring": {
                    "enable_prometheus": True,
                    "prometheus_port": 9090,
                    "enable_grafana": True,
                    "grafana_port": 3000,
                    "log_level": "INFO",
                    "enable_structured_logging": True,
                    "log_file_path": "./logs/gamma_app.log",
                    "max_log_size": 10485760,  # 10MB
                    "backup_count": 5
                },
                
                "performance": {
                    "max_workers": 10,
                    "max_concurrent_requests": 100,
                    "request_timeout": 30,
                    "enable_caching": True,
                    "cache_ttl": 3600,
                    "enable_compression": True,
                    "compression_level": 6
                },
                
                "integration": {
                    "webhook_timeout": 30,
                    "webhook_retry_attempts": 3,
                    "webhook_retry_delay": 5,
                    "api_timeout": 30,
                    "api_retry_attempts": 3,
                    "enable_ssl_verification": True
                },
                
                "advanced": {
                    "enable_blockchain": False,
                    "enable_quantum": False,
                    "enable_iot": False,
                    "enable_ar_vr": False,
                    "enable_robotics": False,
                    "enable_metaverse": False,
                    "enable_biotech": False
                }
            }
            
            async with aiofiles.open(self.config_file, 'w') as f:
                await f.write(yaml.dump(default_config, default_flow_style=False))
            
            logger.info("Default configuration file created")
            
        except Exception as e:
            logger.error(f"Error creating default config: {e}")
    
    async def save_config(self, config: UnifiedConfig):
        """Save configuration to file"""
        try:
            config.updated_at = datetime.now()
            config.config_hash = self._generate_config_hash(config)
            
            # Convert to dictionary
            config_dict = {
                "app_name": config.app_name,
                "version": config.version,
                "debug": config.debug,
                "database": config.database.__dict__,
                "redis": config.redis.__dict__,
                "security": {k: v for k, v in config.security.__dict__.items() if not k.startswith('_')},
                "ai": config.ai.__dict__,
                "storage": config.storage.__dict__,
                "monitoring": config.monitoring.__dict__,
                "performance": config.performance.__dict__,
                "integration": config.integration.__dict__,
                "advanced": config.advanced.__dict__
            }
            
            # Save to file
            async with aiofiles.open(self.config_file, 'w') as f:
                await f.write(yaml.dump(config_dict, default_flow_style=False))
            
            self.current_config = config
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    async def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        try:
            if not self.current_config:
                raise ValueError("No configuration loaded")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(self.current_config, key):
                    setattr(self.current_config, key, value)
            
            # Save updated configuration
            await self.save_config(self.current_config)
            
            # Notify watchers
            await self._notify_config_watchers()
            
            logger.info("Configuration updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            raise
    
    def add_config_watcher(self, callback: callable):
        """Add configuration change watcher"""
        self.config_watchers.append(callback)
    
    async def _notify_config_watchers(self):
        """Notify all configuration watchers"""
        for callback in self.config_watchers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.current_config)
                else:
                    callback(self.current_config)
            except Exception as e:
                logger.error(f"Error in config watcher: {e}")
    
    async def start_config_watching(self):
        """Start watching for configuration file changes"""
        try:
            if self.watch_task:
                return
            
            self.watch_task = asyncio.create_task(self._watch_config_files())
            logger.info("Configuration watching started")
            
        except Exception as e:
            logger.error(f"Error starting config watching: {e}")
    
    async def stop_config_watching(self):
        """Stop watching for configuration file changes"""
        try:
            if self.watch_task:
                self.watch_task.cancel()
                self.watch_task = None
                logger.info("Configuration watching stopped")
                
        except Exception as e:
            logger.error(f"Error stopping config watching: {e}")
    
    async def _watch_config_files(self):
        """Watch for configuration file changes"""
        try:
            last_modified = {}
            
            while True:
                config_files = [
                    self.config_file,
                    self.secrets_file,
                    self.config_path / f"{self.current_config.environment.value}.yaml"
                ]
                
                for config_file in config_files:
                    if config_file.exists():
                        current_modified = config_file.stat().st_mtime
                        
                        if config_file in last_modified and current_modified > last_modified[config_file]:
                            logger.info(f"Configuration file {config_file.name} changed, reloading...")
                            await self.load_config(self.current_config.environment)
                            await self._notify_config_watchers()
                        
                        last_modified[config_file] = current_modified
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
        except asyncio.CancelledError:
            logger.info("Configuration watching cancelled")
        except Exception as e:
            logger.error(f"Error in config watching: {e}")
    
    def get_config(self) -> Optional[UnifiedConfig]:
        """Get current configuration"""
        return self.current_config
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get specific configuration value"""
        try:
            if not self.current_config:
                return default
            
            keys = key.split('.')
            value = self.current_config
            
            for k in keys:
                if hasattr(value, k):
                    value = getattr(value, k)
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting config value {key}: {e}")
            return default
    
    async def export_config(self, format: str = "yaml") -> str:
        """Export configuration in specified format"""
        try:
            if not self.current_config:
                raise ValueError("No configuration loaded")
            
            config_dict = {
                "app_name": self.current_config.app_name,
                "version": self.current_config.version,
                "debug": self.current_config.debug,
                "environment": self.current_config.environment.value,
                "database": self.current_config.database.__dict__,
                "redis": self.current_config.redis.__dict__,
                "security": {k: v for k, v in self.current_config.security.__dict__.items() if not k.startswith('_')},
                "ai": self.current_config.ai.__dict__,
                "storage": self.current_config.storage.__dict__,
                "monitoring": self.current_config.monitoring.__dict__,
                "performance": self.current_config.performance.__dict__,
                "integration": self.current_config.integration.__dict__,
                "advanced": self.current_config.advanced.__dict__,
                "created_at": self.current_config.created_at.isoformat(),
                "updated_at": self.current_config.updated_at.isoformat(),
                "config_hash": self.current_config.config_hash
            }
            
            if format == "yaml":
                return yaml.dump(config_dict, default_flow_style=False)
            elif format == "json":
                return json.dumps(config_dict, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return ""
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for configuration service"""
        try:
            return {
                "status": "healthy",
                "config_loaded": self.current_config is not None,
                "config_file_exists": self.config_file.exists(),
                "secrets_file_exists": self.secrets_file.exists(),
                "watching_active": self.watch_task is not None,
                "watchers_count": len(self.config_watchers),
                "environment": self.current_config.environment.value if self.current_config else None,
                "config_hash": self.current_config.config_hash if self.current_config else None
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}


























