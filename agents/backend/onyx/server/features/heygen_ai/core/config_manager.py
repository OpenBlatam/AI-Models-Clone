#!/usr/bin/env python3
"""
HeyGen AI Configuration Manager

This module provides a unified configuration management system for the HeyGen AI platform.
It handles loading, validation, and access to configuration settings from YAML files,
environment variables, and command-line arguments.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
import yaml
import logging
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration Models
# =============================================================================

class SystemConfig(BaseModel):
    """System configuration settings."""
    name: str = "HeyGen AI"
    version: str = "2.0.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"


class PluginConfig(BaseModel):
    """Plugin system configuration."""
    enabled: bool = True
    auto_load: bool = True
    hot_reload: bool = False
    hot_reload_interval: float = 30.0
    directories: List[str] = field(default_factory=lambda: [
        "plugins", "extensions", "custom_models", "optimizations", "features"
    ])
    validation: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "allow_unsafe": False,
        "check_dependencies": True
    })
    cache: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "size": 100,
        "ttl": 3600
    })


class ModelConfig(BaseModel):
    """Model configuration settings."""
    default_device: str = "auto"
    default_precision: str = "fp32"
    optimization: Dict[str, bool] = field(default_factory=lambda: {
        "quantization": True,
        "pruning": True,
        "compilation": True,
        "mixed_precision": True
    })
    cache: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "directory": "models/cache",
        "max_size_gb": 10
    })


class PerformanceConfig(BaseModel):
    """Performance optimization settings."""
    optimization_level: str = "balanced"
    memory_management: Dict[str, Any] = field(default_factory=lambda: {
        "enable_garbage_collection": True,
        "gc_threshold": 0.8,
        "memory_pool": True
    })
    threading: Dict[str, int] = field(default_factory=lambda: {
        "max_workers": 4,
        "thread_pool_size": 8
    })
    gpu: Dict[str, Any] = field(default_factory=lambda: {
        "memory_fraction": 0.9,
        "allow_growth": True,
        "enable_mixed_precision": True
    })


class APIConfig(BaseModel):
    """API configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 30
    cors: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE"]
    })
    rate_limiting: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "requests_per_minute": 100,
        "burst_size": 20
    })


class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    type: str = "sqlite"
    url: str = "sqlite:///heygen_ai.db"
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


class CacheConfig(BaseModel):
    """Cache configuration settings."""
    type: str = "memory"
    redis: Dict[str, Any] = field(default_factory=lambda: {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": None
    })
    memory: Dict[str, Any] = field(default_factory=lambda: {
        "max_size_mb": 512,
        "ttl": 3600
    })


class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers: Dict[str, Any] = field(default_factory=lambda: {
        "console": {"enabled": True, "level": "INFO"},
        "file": {
            "enabled": True,
            "level": "DEBUG",
            "filename": "logs/heygen_ai.log",
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "syslog": {"enabled": False, "host": "localhost", "port": 514}
    })


class SecurityConfig(BaseModel):
    """Security configuration settings."""
    authentication: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "type": "jwt",
        "secret_key": "your-secret-key-here",
        "token_expiry": 3600
    })
    encryption: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "algorithm": "AES-256-GCM"
    })
    ssl: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "cert_file": "certs/cert.pem",
        "key_file": "certs/key.pem"
    })


class MonitoringConfig(BaseModel):
    """Monitoring configuration settings."""
    enabled: bool = True
    metrics: Dict[str, bool] = field(default_factory=lambda: {
        "prometheus": True,
        "grafana": False
    })
    health_checks: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "interval": 30
    })
    profiling: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "sampling_rate": 0.1
    })


class ExternalServicesConfig(BaseModel):
    """External services configuration."""
    openai: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "api_key": "",
        "base_url": "https://api.openai.com/v1"
    })
    elevenlabs: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "api_key": "",
        "base_url": "https://api.elevenlabs.io/v1"
    })
    cloud_storage: Dict[str, Any] = field(default_factory=lambda: {
        "type": "local",
        "local": {"directory": "storage"},
        "s3": {"bucket": "", "region": "", "access_key": "", "secret_key": ""}
    })


class DevelopmentConfig(BaseModel):
    """Development configuration settings."""
    hot_reload: bool = True
    debug_toolbar: bool = True
    profiling: bool = False
    testing: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "coverage": True,
        "parallel": True
    })


class HeyGenAIConfig(BaseModel):
    """Complete HeyGen AI configuration."""
    system: SystemConfig = Field(default_factory=SystemConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)
    models: ModelConfig = Field(default_factory=ModelConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    external_services: ExternalServicesConfig = Field(default_factory=ExternalServicesConfig)
    development: DevelopmentConfig = Field(default_factory=DevelopmentConfig)


# =============================================================================
# Configuration Manager
# =============================================================================

class ConfigurationManager:
    """Manages HeyGen AI configuration loading and access."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config_path = Path(config_path) if config_path else self._find_config_file()
        self.config: Optional[HeyGenAIConfig] = None
        self._load_config()
        self._setup_logging()
    
    def _find_config_file(self) -> Path:
        """Find the configuration file in common locations."""
        search_paths = [
            Path("config/heygen_ai_config.yaml"),
            Path("heygen_ai_config.yaml"),
            Path("../config/heygen_ai_config.yaml"),
            Path("configs/heygen_ai_config.yaml")
        ]
        
        for path in search_paths:
            if path.exists():
                logger.info(f"Found config file: {path}")
                return path
        
        # Create default config if none exists
        default_path = Path("config/heygen_ai_config.yaml")
        logger.warning(f"No config file found, creating default at: {default_path}")
        self._create_default_config(default_path)
        return default_path
    
    def _create_default_config(self, path: Path):
        """Create a default configuration file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        default_config = {
            "system": {
                "name": "HeyGen AI",
                "version": "2.0.0",
                "environment": "development",
                "debug": True,
                "log_level": "INFO"
            },
            "plugins": {
                "enabled": True,
                "auto_load": True,
                "hot_reload": False,
                "directories": ["plugins", "extensions"]
            }
        }
        
        with open(path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        logger.info(f"Created default config file: {path}")
    
    def _load_config(self):
        """Load configuration from file and environment variables."""
        try:
            # Load from YAML file
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    yaml_config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from: {self.config_path}")
            else:
                yaml_config = {}
                logger.warning(f"Config file not found: {self.config_path}")
            
            # Override with environment variables
            env_config = self._load_from_environment()
            
            # Merge configurations
            merged_config = self._merge_configs(yaml_config, env_config)
            
            # Validate and create config object
            self.config = HeyGenAIConfig(**merged_config)
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Use default configuration
            self.config = HeyGenAIConfig()
            logger.info("Using default configuration")
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {}
        
        # System configuration
        if os.getenv("HEYGEN_AI_ENVIRONMENT"):
            env_config.setdefault("system", {})["environment"] = os.getenv("HEYGEN_AI_ENVIRONMENT")
        
        if os.getenv("HEYGEN_AI_DEBUG"):
            env_config.setdefault("system", {})["debug"] = os.getenv("HEYGEN_AI_DEBUG").lower() == "true"
        
        if os.getenv("HEYGEN_AI_LOG_LEVEL"):
            env_config.setdefault("system", {})["log_level"] = os.getenv("HEYGEN_AI_LOG_LEVEL")
        
        # API configuration
        if os.getenv("HEYGEN_AI_API_HOST"):
            env_config.setdefault("api", {})["host"] = os.getenv("HEYGEN_AI_API_HOST")
        
        if os.getenv("HEYGEN_AI_API_PORT"):
            env_config.setdefault("api", {})["port"] = int(os.getenv("HEYGEN_AI_API_PORT"))
        
        # Database configuration
        if os.getenv("HEYGEN_AI_DATABASE_URL"):
            env_config.setdefault("database", {})["url"] = os.getenv("HEYGEN_AI_DATABASE_URL")
        
        return env_config
    
    def _merge_configs(self, yaml_config: Dict[str, Any], env_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge YAML and environment configurations."""
        merged = yaml_config.copy()
        
        def deep_merge(base: Dict[str, Any], override: Dict[str, Any]):
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        
        deep_merge(merged, env_config)
        return merged
    
    def _setup_logging(self):
        """Setup logging based on configuration."""
        if not self.config:
            return
        
        log_config = self.config.logging
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_config.system.log_level.upper()),
            format=log_config.format,
            force=True
        )
        
        # Add file handler if enabled
        if log_config.handlers.get("file", {}).get("enabled", False):
            file_config = log_config.handlers["file"]
            log_file = Path(file_config["filename"])
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, file_config["level"].upper()))
            file_handler.setFormatter(logging.Formatter(log_config.format))
            
            logging.getLogger().addHandler(file_handler)
    
    def get_config(self) -> HeyGenAIConfig:
        """Get the current configuration."""
        return self.config
    
    def get_section(self, section: str) -> Any:
        """Get a specific configuration section."""
        if not self.config:
            return None
        
        if hasattr(self.config, section):
            return getattr(self.config, section)
        
        return None
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values."""
        if not self.config:
            return
        
        # Update configuration
        for key, value in updates.items():
            if hasattr(self.config, key):
                current_section = getattr(self.config, key)
                if isinstance(current_section, BaseModel):
                    # Update section
                    section_updates = current_section.dict()
                    section_updates.update(value)
                    setattr(self.config, key, type(current_section)(**section_updates))
                else:
                    setattr(self.config, key, value)
        
        # Save updated configuration
        self._save_config()
        logger.info("Configuration updated and saved")
    
    def _save_config(self):
        """Save current configuration to file."""
        if not self.config or not self.config_path:
            return
        
        try:
            # Convert to dict and save as YAML
            config_dict = self.config.dict()
            
            with open(self.config_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to: {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def reload_config(self):
        """Reload configuration from file."""
        logger.info("Reloading configuration...")
        self._load_config()
        self._setup_logging()
    
    def validate_config(self) -> bool:
        """Validate current configuration."""
        if not self.config:
            return False
        
        try:
            # Pydantic will validate the configuration
            self.config.dict()
            logger.info("Configuration validation passed")
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False


# =============================================================================
# Global Configuration Instance
# =============================================================================

_config_manager: Optional[ConfigurationManager] = None

def get_config_manager(config_path: Optional[Union[str, Path]] = None) -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_path)
    
    return _config_manager

def get_config() -> HeyGenAIConfig:
    """Get the current configuration."""
    return get_config_manager().get_config()

def get_config_section(section: str) -> Any:
    """Get a specific configuration section."""
    return get_config_manager().get_section(section)


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Initialize configuration manager
    config_manager = ConfigurationManager()
    
    # Get configuration
    config = config_manager.get_config()
    
    # Print configuration summary
    print("🚀 HeyGen AI Configuration Summary")
    print("=" * 50)
    print(f"System: {config.system.name} v{config.system.version}")
    print(f"Environment: {config.system.environment}")
    print(f"Debug: {config.system.debug}")
    print(f"Log Level: {config.system.log_level}")
    print(f"API: {config.api.host}:{config.api.port}")
    print(f"Database: {config.database.type}")
    print(f"Plugins: {'Enabled' if config.plugins.enabled else 'Disabled'}")
    
    # Validate configuration
    if config_manager.validate_config():
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration validation failed")
