"""
Configuration Management for HeyGen AI
======================================

Provides centralized configuration management with:
- Environment-based configuration
- Configuration validation
- Hot-reloading capabilities
- Multiple configuration sources
- Secure credential management
"""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import yaml
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class DatabaseType(str, Enum):
    """Database types"""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    SQLITE = "sqlite"


class CacheType(str, Enum):
    """Cache types"""
    REDIS = "redis"
    MEMORY = "memory"
    CDN = "cdn"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    
    type: DatabaseType
    host: str
    port: int
    username: str
    password: str
    database: str
    ssl_mode: str = "prefer"
    max_connections: int = 20
    connection_timeout: float = 30.0
    pool_size: int = 10
    retry_attempts: int = 3


@dataclass
class CacheConfig:
    """Cache configuration"""
    
    type: CacheType
    host: str
    port: int
    password: Optional[str] = None
    database: int = 0
    max_connections: int = 50
    connection_timeout: float = 5.0
    key_prefix: str = "heygen_ai:"
    default_ttl: int = 3600


@dataclass
class ExternalAPIConfig:
    """External API configuration"""
    
    elevenlabs_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    huggingface_token: Optional[str] = None
    replicate_api_token: Optional[str] = None
    youtube_api_key: Optional[str] = None
    instagram_access_token: Optional[str] = None
    tiktok_access_token: Optional[str] = None
    linkedin_access_token: Optional[str] = None
    facebook_access_token: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    google_cloud_credentials: Optional[str] = None
    azure_connection_string: Optional[str] = None


@dataclass
class SecurityConfig:
    """Security configuration"""
    
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    password_require_special_chars: bool = True
    password_require_numbers: bool = True
    password_require_uppercase: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    session_timeout_minutes: int = 60
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = 100
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=list)
    enable_ssl: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None


@dataclass
class PerformanceConfig:
    """Performance configuration"""
    
    max_concurrent_requests: int = 100
    request_timeout_seconds: float = 300.0
    enable_compression: bool = True
    compression_level: int = 6
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_background_processing: bool = True
    max_background_workers: int = 10
    enable_load_balancing: bool = True
    load_balancer_algorithm: str = "round_robin"
    enable_auto_scaling: bool = True
    min_instances: int = 1
    max_instances: int = 10
    cpu_threshold_percent: float = 70.0
    memory_threshold_percent: float = 80.0


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    
    enable_logging: bool = True
    log_level: str = "INFO"
    log_format: str = "json"
    log_file_path: Optional[str] = None
    enable_metrics: bool = True
    metrics_port: int = 9090
    metrics_path: str = "/metrics"
    enable_health_checks: bool = True
    health_check_interval_seconds: int = 30
    enable_tracing: bool = True
    tracing_endpoint: Optional[str] = None
    enable_alerting: bool = True
    alert_webhook_url: Optional[str] = None
    enable_dashboard: bool = True
    dashboard_port: int = 3000


@dataclass
class AIConfig:
    """AI model configuration"""
    
    stable_diffusion_model: str = "runwayml/stable-diffusion-v1-5"
    tts_model: str = "tts_models/en/ljspeech/tacotron2-DDC"
    whisper_model: str = "base"
    face_recognition_model: str = "hog"
    emotion_detection_model: str = "fer2013"
    gesture_recognition_model: str = "mediapipe"
    enable_gpu: bool = True
    gpu_memory_fraction: float = 0.8
    enable_mixed_precision: bool = True
    batch_size: int = 1
    max_sequence_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 1000


@dataclass
class VideoConfig:
    """Video processing configuration"""
    
    default_resolution: str = "1920x1080"
    default_fps: int = 30
    default_bitrate: str = "5000k"
    supported_formats: List[str] = field(default_factory=lambda: ["mp4", "avi", "mov", "mkv"])
    supported_codecs: List[str] = field(default_factory=lambda: ["h264", "h265", "vp9"])
    enable_hardware_acceleration: bool = True
    hardware_accelerator: str = "auto"
    max_video_duration_seconds: int = 3600
    enable_watermark: bool = False
    watermark_path: Optional[str] = None
    enable_compression: bool = True
    compression_quality: int = 85
    enable_thumbnail_generation: bool = True
    thumbnail_count: int = 3


class HeyGenAIConfig(BaseSettings):
    """Main configuration class for HeyGen AI"""
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    version: str = "4.0.0"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Database
    database: DatabaseConfig = Field(default_factory=lambda: DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        username="heygen_ai",
        password="password",
        database="heygen_ai"
    ))
    
    # Cache
    cache: CacheConfig = Field(default_factory=lambda: CacheConfig(
        type=CacheType.REDIS,
        host="localhost",
        port=6379
    ))
    
    # External APIs
    external_apis: ExternalAPIConfig = Field(default_factory=ExternalAPIConfig)
    
    # Security
    security: SecurityConfig = Field(default_factory=lambda: SecurityConfig(
        secret_key="your-secret-key-here"
    ))
    
    # Performance
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    
    # Monitoring
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    # AI Models
    ai: AIConfig = Field(default_factory=AIConfig)
    
    # Video Processing
    video: VideoConfig = Field(default_factory=VideoConfig)
    
    # File paths
    data_dir: str = "./data"
    models_dir: str = "./models"
    temp_dir: str = "./temp"
    exports_dir: str = "./exports"
    logs_dir: str = "./logs"
    
    # Feature flags
    enable_avatar_generation: bool = True
    enable_voice_synthesis: bool = True
    enable_video_rendering: bool = True
    enable_real_time_collaboration: bool = True
    enable_advanced_analytics: bool = True
    enable_enterprise_features: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("security")
    def validate_security_config(cls, v):
        """Validate security configuration"""
        if not v.secret_key or v.secret_key == "your-secret-key-here":
            raise ValueError("Secret key must be set and not use default value")
        return v
    
    @validator("database")
    def validate_database_config(cls, v):
        """Validate database configuration"""
        if not v.host or not v.username or not v.password:
            raise ValueError("Database host, username, and password are required")
        return v


class ConfigurationManager:
    """
    Manages configuration loading, validation, and hot-reloading.
    
    Supports multiple configuration sources and provides a unified interface
    for accessing configuration values.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config: Optional[HeyGenAIConfig] = None
        self.config_file_observer: Optional[Observer] = None
        self.config_watchers: List[callable] = []
        
        # Load configuration
        self._load_configuration()
        
        # Setup file watching if enabled
        if self.config and self.config.monitoring.enable_logging:
            self._setup_config_watching()
    
    def _load_configuration(self) -> None:
        """Load configuration from multiple sources."""
        try:
            # Try to load from file first
            if self.config_path and Path(self.config_path).exists():
                self.config = self._load_from_file(self.config_path)
                logger.info(f"Configuration loaded from file: {self.config_path}")
            else:
                # Load from environment variables
                self.config = HeyGenAIConfig()
                logger.info("Configuration loaded from environment variables")
            
            # Validate configuration
            self._validate_configuration()
            
            # Create directories
            self._create_directories()
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Use default configuration
            self.config = HeyGenAIConfig()
    
    def _load_from_file(self, file_path: str) -> HeyGenAIConfig:
        """Load configuration from a file."""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        elif file_path.suffix.lower() in [".yml", ".yaml"]:
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {file_path.suffix}")
        
        # Convert to HeyGenAIConfig
        return HeyGenAIConfig(**config_data)
    
    def _validate_configuration(self) -> None:
        """Validate the loaded configuration."""
        if not self.config:
            raise ValueError("Configuration not loaded")
        
        # Validate required directories
        required_dirs = [
            self.config.data_dir,
            self.config.models_dir,
            self.config.temp_dir,
            self.config.exports_dir,
            self.config.logs_dir
        ]
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                logger.warning(f"Directory does not exist: {dir_path}")
    
    def _create_directories(self) -> None:
        """Create required directories if they don't exist."""
        if not self.config:
            return
        
        directories = [
            self.config.data_dir,
            self.config.models_dir,
            self.config.temp_dir,
            self.config.exports_dir,
            self.config.logs_dir
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def _setup_config_watching(self) -> None:
        """Setup file watching for configuration changes."""
        if not self.config_path:
            return
        
        try:
            self.config_file_observer = Observer()
            event_handler = ConfigFileEventHandler(self)
            self.config_file_observer.schedule(
                event_handler, 
                path=Path(self.config_path).parent, 
                recursive=False
            )
            self.config_file_observer.start()
            logger.info("Configuration file watching enabled")
            
        except Exception as e:
            logger.warning(f"Failed to setup configuration file watching: {e}")
    
    def get_config(self) -> HeyGenAIConfig:
        """Get the current configuration."""
        if not self.config:
            raise RuntimeError("Configuration not loaded")
        return self.config
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value by key path.
        
        Args:
            key_path: Dot-separated key path (e.g., "database.host")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self.config:
            return default
        
        keys = key_path.split(".")
        value = self.config
        
        try:
            for key in keys:
                value = getattr(value, key)
            return value
        except AttributeError:
            return default
    
    def set_value(self, key_path: str, value: Any) -> bool:
        """
        Set a configuration value by key path.
        
        Args:
            key_path: Dot-separated key path
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        if not self.config:
            return False
        
        keys = key_path.split(".")
        obj = self.config
        
        try:
            # Navigate to the parent object
            for key in keys[:-1]:
                obj = getattr(obj, key)
            
            # Set the value
            setattr(obj, keys[-1], value)
            return True
            
        except AttributeError:
            return False
    
    def reload_configuration(self) -> bool:
        """Reload configuration from source."""
        try:
            old_config = self.config
            self._load_configuration()
            
            # Notify watchers
            if old_config != self.config:
                self._notify_config_changed()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def add_config_watcher(self, callback: callable) -> None:
        """Add a configuration change watcher."""
        self.config_watchers.append(callback)
    
    def remove_config_watcher(self, callback: callable) -> None:
        """Remove a configuration change watcher."""
        if callback in self.config_watchers:
            self.config_watchers.remove(callback)
    
    def _notify_config_changed(self) -> None:
        """Notify all configuration change watchers."""
        for watcher in self.config_watchers:
            try:
                watcher(self.config)
            except Exception as e:
                logger.error(f"Error in configuration watcher: {e}")
    
    def export_config(self, format: str = "json") -> str:
        """
        Export configuration to string format.
        
        Args:
            format: Output format (json, yaml)
            
        Returns:
            Configuration as string
        """
        if not self.config:
            raise RuntimeError("Configuration not loaded")
        
        config_dict = self.config.dict()
        
        if format.lower() == "json":
            return json.dumps(config_dict, indent=2, default=str)
        elif format.lower() in ["yml", "yaml"]:
            return yaml.dump(config_dict, default_flow_style=False, default_representer=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def save_config(self, file_path: Optional[str] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            file_path: Path to save configuration (uses current path if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.config:
            return False
        
        file_path = file_path or self.config_path
        if not file_path:
            return False
        
        try:
            file_path = Path(file_path)
            config_dict = self.config.dict()
            
            if file_path.suffix.lower() == ".json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(config_dict, f, indent=2, default=str)
            elif file_path.suffix.lower() in [".yml", ".yaml"]:
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(config_dict, f, default_flow_style=False, default_representer=str)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            logger.info(f"Configuration saved to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the configuration manager."""
        if self.config_file_observer:
            self.config_file_observer.stop()
            self.config_file_observer.join()
            logger.info("Configuration file watching stopped")


class ConfigFileEventHandler(FileSystemEventHandler):
    """File system event handler for configuration file changes."""
    
    def __init__(self, config_manager: ConfigurationManager):
        """Initialize the event handler."""
        self.config_manager = config_manager
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and event.src_path.endswith(('.json', '.yml', '.yaml')):
            logger.info(f"Configuration file modified: {event.src_path}")
            # Debounce the reload to avoid multiple rapid reloads
            asyncio.create_task(self._debounced_reload())
    
    async def _debounced_reload(self):
        """Debounced configuration reload."""
        await asyncio.sleep(1)  # Wait 1 second before reloading
        self.config_manager.reload_configuration()


# Global configuration instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigurationManager:
    """Get or create the global configuration manager."""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_path)
    
    return _config_manager


def get_config() -> HeyGenAIConfig:
    """Get the current configuration."""
    return get_config_manager().get_config()


def get_config_value(key_path: str, default: Any = None) -> Any:
    """Get a configuration value by key path."""
    return get_config_manager().get_value(key_path, default)






