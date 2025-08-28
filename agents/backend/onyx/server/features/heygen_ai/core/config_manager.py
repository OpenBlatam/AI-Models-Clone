"""
Centralized Configuration Management System
=========================================

Manages all configuration settings for the HeyGen AI system:
- Environment variables
- Configuration files
- Default values
- Validation and type conversion
- Hot reloading capabilities
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    name: str = "heygen_ai"
    user: str = "postgres"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


@dataclass
class CacheConfig:
    """Cache configuration"""
    redis_url: str = "redis://localhost:6379"
    memory_limit: int = 1000
    ttl_seconds: int = 3600
    enable_compression: bool = True
    compression_threshold: int = 1024


@dataclass
class APIConfig:
    """API configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 30
    max_requests: int = 1000
    cors_origins: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 60


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enable_health_checks: bool = True
    health_check_interval: int = 30
    enable_metrics: bool = True
    metrics_port: int = 9090
    enable_tracing: bool = False
    log_level: str = "INFO"


@dataclass
class SystemConfig:
    """System-wide configuration"""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    log_file: str = "logs/heygen_ai.log"
    max_log_size: int = 100 * 1024 * 1024  # 100MB
    backup_logs: int = 5
    temp_dir: str = "temp"
    data_dir: str = "data"


class ConfigManager:
    """Centralized configuration manager"""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None, skip_validation: bool = False):
        self.config_path = Path(config_path) if config_path else Path("config")
        self.config_file = self.config_path / "config.yaml"
        self.env_file = self.config_path / ".env"

        # Initialize configuration objects
        self.database = DatabaseConfig()
        self.cache = CacheConfig()
        self.api = APIConfig()
        self.security = SecurityConfig()
        self.monitoring = MonitoringConfig()
        self.system = SystemConfig()

        # Load configuration
        self._load_config()
        self._load_environment_variables()
        
        # Skip validation if requested (useful for testing)
        if not skip_validation:
            self._validate_config()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                # Update configuration objects
                self._update_config_from_dict(config_data)
                logger.info(f"Configuration loaded from {self.config_file}")
                
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        else:
            logger.info("No config file found, using defaults")
    
    def _load_environment_variables(self):
        """Load configuration from environment variables"""
        # Database
        if os.getenv("DB_HOST"):
            self.database.host = os.getenv("DB_HOST")
        if os.getenv("DB_PORT"):
            self.database.port = int(os.getenv("DB_PORT"))
        if os.getenv("DB_NAME"):
            self.database.name = os.getenv("DB_NAME")
        if os.getenv("DB_USER"):
            self.database.user = os.getenv("DB_USER")
        if os.getenv("DB_PASSWORD"):
            self.database.password = os.getenv("DB_PASSWORD")
        
        # Cache
        if os.getenv("REDIS_URL"):
            self.cache.redis_url = os.getenv("REDIS_URL")
        
        # API
        if os.getenv("API_HOST"):
            self.api.host = os.getenv("API_HOST")
        if os.getenv("API_PORT"):
            self.api.port = int(os.getenv("API_PORT"))
        if os.getenv("API_WORKERS"):
            self.api.workers = int(os.getenv("API_WORKERS"))
        
        # Security
        if os.getenv("SECRET_KEY"):
            self.security.secret_key = os.getenv("SECRET_KEY")
        if os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"):
            self.security.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
        
        # System
        if os.getenv("ENVIRONMENT"):
            env_str = os.getenv("ENVIRONMENT").lower()
            if env_str in [e.value for e in Environment]:
                self.system.environment = Environment(env_str)
        if os.getenv("DEBUG"):
            self.system.debug = os.getenv("DEBUG").lower() in ("true", "1", "yes")
        if os.getenv("LOG_LEVEL"):
            self.monitoring.log_level = os.getenv("LOG_LEVEL").upper()
        
        logger.info("Environment variables loaded")
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration objects from dictionary"""
        if "database" in config_data:
            for key, value in config_data["database"].items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)
        
        if "cache" in config_data:
            for key, value in config_data["cache"].items():
                if hasattr(self.cache, key):
                    setattr(self.cache, key, value)
        
        if "api" in config_data:
            for key, value in config_data["api"].items():
                if hasattr(self.api, key):
                    setattr(self.api, key, value)
        
        if "security" in config_data:
            for key, value in config_data["security"].items():
                if hasattr(self.security, key):
                    setattr(self.security, key, value)
        
        if "monitoring" in config_data:
            for key, value in config_data["monitoring"].items():
                if hasattr(self.monitoring, key):
                    setattr(self.monitoring, key, value)
        
        if "system" in config_data:
            for key, value in config_data["system"].items():
                if hasattr(self.system, key):
                    if key == "environment" and isinstance(value, str):
                        if value.lower() in [e.value for e in Environment]:
                            setattr(self.system, key, Environment(value.lower()))
                    else:
                        setattr(self.system, key, value)
    
    def _validate_config(self):
        """Validate configuration values"""
        errors = []
        
        # Database validation
        if not self.database.host:
            errors.append("Database host cannot be empty")
        if self.database.port < 1 or self.database.port > 65535:
            errors.append("Database port must be between 1 and 65535")
        if not self.database.name:
            errors.append("Database name cannot be empty")
        
        # API validation
        if self.api.port < 1 or self.api.port > 65535:
            errors.append("API port must be between 1 and 65535")
        if self.api.workers < 1:
            errors.append("API workers must be at least 1")
        
        # Security validation
        if not self.security.secret_key:
            errors.append("Secret key cannot be empty")
        if self.security.access_token_expire_minutes < 1:
            errors.append("Access token expire minutes must be at least 1")
        
        # Monitoring validation
        if self.monitoring.health_check_interval < 1:
            errors.append("Health check interval must be at least 1 second")
        if self.monitoring.metrics_port < 1 or self.monitoring.metrics_port > 65535:
            errors.append("Metrics port must be between 1 and 65535")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Configuration validation passed")
    
    def get_config(self) -> Dict[str, Any]:
        """Get complete configuration as dictionary"""
        return {
            "database": self.database.__dict__,
            "cache": self.cache.__dict__,
            "api": self.api.__dict__,
            "security": self.security.__dict__,
            "monitoring": self.monitoring.__dict__,
            "system": {
                **self.system.__dict__,
                "environment": self.system.environment.value
            }
        }
    
    def save_config(self, output_path: Optional[Union[str, Path]] = None):
        """Save current configuration to file"""
        if output_path is None:
            output_path = self.config_file
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = self.get_config()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
        
        logger.info(f"Configuration saved to {output_path}")
    
    def export_env_template(self, output_path: Optional[Union[str, Path]] = None):
        """Export environment variables template"""
        if output_path is None:
            output_path = self.config_path / ".env.template"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        env_template = """# HeyGen AI Environment Variables Template
# Copy this file to .env and fill in your values

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=heygen_ai
DB_USER=postgres
DB_PASSWORD=your_password_here

# Cache Configuration
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Security Configuration
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# System Configuration
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(env_template)
        
        logger.info(f"Environment template exported to {output_path}")
    
    def reload_config(self, skip_validation: bool = False):
        """Reload configuration from files and environment"""
        logger.info("Reloading configuration...")
        self._load_config()
        self._load_environment_variables()
        
        # Skip validation if requested
        if not skip_validation:
            self._validate_config()
            
        logger.info("Configuration reloaded successfully")
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        if self.database.password:
            return f"postgresql://{self.database.user}:{self.database.password}@{self.database.host}:{self.database.port}/{self.database.name}"
        else:
            return f"postgresql://{self.database.user}@{self.database.host}:{self.database.port}/{self.database.name}"
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.system.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.system.environment == Environment.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.system.environment == Environment.TESTING


# Global configuration instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get global configuration instance"""
    return config


def reload_config():
    """Reload global configuration"""
    config.reload_config()


if __name__ == "__main__":
    # Example usage
    print("Current Configuration:")
    print(json.dumps(config.get_config(), indent=2, default=str))
    
    # Export template
    config.export_env_template()
    
    # Save current config
    config.save_config()
