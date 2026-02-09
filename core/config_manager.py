"""
Enhanced Centralized Configuration Management System
==================================================

Advanced configuration management with:
- Multi-environment support
- Hot-reloading capabilities
- Advanced validation
- Type safety
- Configuration encryption
- Audit logging
- Performance optimization
"""

import os
import yaml
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import lru_cache
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from cryptography.fernet import Fernet
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Environment(Enum):
    """Environment enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ConfigValidationError(Exception):
    """Configuration validation error"""
    pass


class ConfigEncryptionError(Exception):
    """Configuration encryption error"""
    pass


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    name: str = "heygen_ai"
    user: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"
    max_connections: int = 100
    connection_timeout: int = 30
    pool_size: int = 20
    retry_attempts: int = 3
    
    def validate(self) -> List[str]:
        """Validate database configuration"""
        errors = []
        if not self.host:
            errors.append("Database host cannot be empty")
        if self.port < 1 or self.port > 65535:
            errors.append("Database port must be between 1 and 65535")
        if not self.name:
            errors.append("Database name cannot be empty")
        if self.max_connections < 1:
            errors.append("Max connections must be greater than 0")
        if self.connection_timeout < 1:
            errors.append("Connection timeout must be greater than 0")
        return errors


@dataclass
class CacheConfig:
    """Cache configuration"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0
    memory_cache_size: int = 1000
    cache_ttl: int = 3600
    cache_strategy: str = "lru"
    enable_clustering: bool = False
    cluster_nodes: List[str] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """Validate cache configuration"""
        errors = []
        if not self.redis_host:
            errors.append("Redis host cannot be empty")
        if self.redis_port < 1 or self.redis_port > 65535:
            errors.append("Redis port must be between 1 and 65535")
        if self.memory_cache_size < 1:
            errors.append("Memory cache size must be greater than 0")
        if self.cache_ttl < 1:
            errors.append("Cache TTL must be greater than 0")
        return errors


@dataclass
class APIConfig:
    """API configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 30
    rate_limit: int = 1000
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    enable_docs: bool = True
    enable_metrics: bool = True
    api_version: str = "v1"
    max_request_size: int = 100 * 1024 * 1024  # 100MB
    
    def validate(self) -> List[str]:
        """Validate API configuration"""
        errors = []
        if not self.host:
            errors.append("API host cannot be empty")
        if self.port < 1 or self.port > 65535:
            errors.append("API port must be between 1 and 65535")
        if self.workers < 1:
            errors.append("Workers must be greater than 0")
        if self.timeout < 1:
            errors.append("Timeout must be greater than 0")
        if self.rate_limit < 1:
            errors.append("Rate limit must be greater than 0")
        return errors


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    enable_2fa: bool = True
    max_login_attempts: int = 5
    lockout_duration: int = 15
    enable_encryption: bool = True
    encryption_key: str = ""
    
    def validate(self) -> List[str]:
        """Validate security configuration"""
        errors = []
        if not self.secret_key:
            errors.append("Secret key cannot be empty")
        if len(self.secret_key) < 32:
            errors.append("Secret key must be at least 32 characters long")
        if self.access_token_expire_minutes < 1:
            errors.append("Access token expire minutes must be greater than 0")
        if self.refresh_token_expire_days < 1:
            errors.append("Refresh token expire days must be greater than 0")
        if self.password_min_length < 6:
            errors.append("Password minimum length must be at least 6")
        if self.max_login_attempts < 1:
            errors.append("Max login attempts must be greater than 0")
        if self.lockout_duration < 1:
            errors.append("Lockout duration must be greater than 0")
        return errors


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    log_level: str = "INFO"
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    enable_tracing: bool = True
    tracing_endpoint: str = "http://localhost:14268/api/traces"
    enable_profiling: bool = False
    profiling_interval: int = 60
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    
    def validate(self) -> List[str]:
        """Validate monitoring configuration"""
        errors = []
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"Log level must be one of: {', '.join(valid_log_levels)}")
        if self.metrics_port < 1 or self.metrics_port > 65535:
            errors.append("Metrics port must be between 1 and 65535")
        if self.health_check_interval < 1:
            errors.append("Health check interval must be greater than 0")
        if self.profiling_interval < 1:
            errors.append("Profiling interval must be greater than 0")
        return errors


@dataclass
class SystemConfig:
    """System configuration"""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    log_file: str = "logs/heygen_ai.log"
    max_log_size: int = 100 * 1024 * 1024  # 100MB
    backup_logs: int = 5
    temp_dir: str = "temp"
    data_dir: str = "data"
    enable_backup: bool = True
    backup_interval: int = 86400  # 24 hours
    max_backup_files: int = 10
    
    def validate(self) -> List[str]:
        """Validate system configuration"""
        errors = []
        if not isinstance(self.environment, Environment):
            errors.append("Environment must be a valid Environment enum value")
        if self.max_log_size < 1024 * 1024:  # 1MB
            errors.append("Max log size must be at least 1MB")
        if self.backup_logs < 1:
            errors.append("Backup logs must be greater than 0")
        if self.backup_interval < 3600:  # 1 hour
            errors.append("Backup interval must be at least 1 hour")
        if self.max_backup_files < 1:
            errors.append("Max backup files must be greater than 0")
        return errors


class ConfigFileWatcher(FileSystemEventHandler):
    """Watch for configuration file changes"""
    
    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        self.last_modified = 0
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.yaml'):
            current_time = time.time()
            if current_time - self.last_modified > 1:  # Debounce
                self.last_modified = current_time
                logger.info(f"Configuration file changed: {event.src_path}")
                self.config_manager.reload_config()


class ConfigManager:
    """Enhanced centralized configuration manager"""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None, 
                 skip_validation: bool = False,
                 enable_watcher: bool = True,
                 enable_encryption: bool = False):
        self.config_path = Path(config_path) if config_path else Path("config")
        self.config_file = self.config_path / "config.yaml"
        self.env_file = self.config_path / ".env"
        self.enable_encryption = enable_encryption
        self.encryption_key = None
        self.file_hash = None
        self.last_loaded = 0
        self.reload_callbacks: List[Callable] = []
        
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
        
        # Setup file watcher
        if enable_watcher:
            self._setup_file_watcher()
        
        # Generate encryption key if needed
        if self.enable_encryption:
            self._setup_encryption()
        
        logger.info(f"Configuration manager initialized for environment: {self.system.environment.value}")
    
    def _setup_encryption(self):
        """Setup encryption for sensitive configuration"""
        try:
            if not self.security.encryption_key:
                # Generate a new key
                key = Fernet.generate_key()
                self.security.encryption_key = base64.urlsafe_b64encode(key).decode()
                logger.info("Generated new encryption key")
            else:
                # Use existing key
                key = base64.urlsafe_b64decode(self.security.encryption_key.encode())
            
            self.encryption_key = Fernet(key)
            logger.info("Encryption setup completed")
        except Exception as e:
            logger.error(f"Failed to setup encryption: {e}")
            raise ConfigEncryptionError(f"Encryption setup failed: {e}")
    
    def _setup_file_watcher(self):
        """Setup file system watcher for configuration changes"""
        try:
            self.observer = Observer()
            event_handler = ConfigFileWatcher(self)
            self.observer.schedule(event_handler, str(self.config_path), recursive=False)
            self.observer.start()
            logger.info("Configuration file watcher started")
        except Exception as e:
            logger.warning(f"Failed to setup file watcher: {e}")
    
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                # Update configuration objects
                if config_data:
                    self._update_config_from_dict(config_data)
                
                # Calculate file hash for change detection
                self.file_hash = self._calculate_file_hash()
                self.last_loaded = time.time()
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.warning(f"Configuration file not found: {self.config_file}")
                
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigValidationError(f"Configuration loading failed: {e}")
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration objects from dictionary"""
        # Update database config
        if 'database' in config_data:
            for key, value in config_data['database'].items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)
        
        # Update cache config
        if 'cache' in config_data:
            for key, value in config_data['cache'].items():
                if hasattr(self.cache, key):
                    setattr(self.cache, key, value)
        
        # Update API config
        if 'api' in config_data:
            for key, value in config_data['api'].items():
                if hasattr(self.api, key):
                    setattr(self.api, key, value)
        
        # Update security config
        if 'security' in config_data:
            for key, value in config_data['security'].items():
                if hasattr(self.security, key):
                    setattr(self.security, key, value)
        
        # Update monitoring config
        if 'monitoring' in config_data:
            for key, value in config_data['monitoring'].items():
                if hasattr(self.monitoring, key):
                    setattr(self.monitoring, key, value)
        
        # Update system config
        if 'system' in config_data:
            for key, value in config_data['system'].items():
                if hasattr(self.system, key):
                    if key == 'environment' and isinstance(value, str):
                        try:
                            setattr(self.system, key, Environment(value))
                        except ValueError:
                            logger.warning(f"Invalid environment value: {value}")
                    else:
                        setattr(self.system, key, value)
    
    def _load_environment_variables(self):
        """Load configuration from environment variables"""
        # Database
        if os.getenv('DB_HOST'):
            self.database.host = os.getenv('DB_HOST')
        if os.getenv('DB_PORT'):
            self.database.port = int(os.getenv('DB_PORT'))
        if os.getenv('DB_NAME'):
            self.database.name = os.getenv('DB_NAME')
        if os.getenv('DB_USER'):
            self.database.user = os.getenv('DB_USER')
        if os.getenv('DB_PASSWORD'):
            self.database.password = os.getenv('DB_PASSWORD')
        
        # API
        if os.getenv('API_HOST'):
            self.api.host = os.getenv('API_HOST')
        if os.getenv('API_PORT'):
            self.api.port = int(os.getenv('API_PORT'))
        
        # Security
        if os.getenv('SECRET_KEY'):
            self.security.secret_key = os.getenv('SECRET_KEY')
        
        # System
        if os.getenv('ENVIRONMENT'):
            try:
                self.system.environment = Environment(os.getenv('ENVIRONMENT'))
            except ValueError:
                logger.warning(f"Invalid environment value: {os.getenv('ENVIRONMENT')}")
        
        if os.getenv('DEBUG'):
            self.system.debug = os.getenv('DEBUG').lower() in ('true', '1', 'yes')
        
        logger.info("Environment variables loaded")
    
    def _validate_config(self):
        """Validate all configuration objects"""
        errors = []
        
        # Validate each configuration section
        errors.extend(self.database.validate())
        errors.extend(self.cache.validate())
        errors.extend(self.api.validate())
        errors.extend(self.security.validate())
        errors.extend(self.monitoring.validate())
        errors.extend(self.system.validate())
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ConfigValidationError(error_msg)
        
        logger.info("Configuration validation passed")
    
    def _calculate_file_hash(self) -> str:
        """Calculate hash of configuration file for change detection"""
        try:
            with open(self.config_file, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def reload_config(self, skip_validation: bool = False):
        """Reload configuration from files and environment"""
        logger.info("Reloading configuration...")
        
        # Check if file has actually changed
        current_hash = self._calculate_file_hash()
        if current_hash == self.file_hash:
            logger.info("Configuration file unchanged, skipping reload")
            return
        
        # Reload configuration
        self._load_config()
        self._load_environment_variables()
        
        # Skip validation if requested
        if not skip_validation:
            self._validate_config()
        
        # Notify callbacks
        self._notify_reload_callbacks()
        
        logger.info("Configuration reloaded successfully")
    
    def add_reload_callback(self, callback: Callable):
        """Add callback to be called when configuration is reloaded"""
        self.reload_callbacks.append(callback)
        logger.debug(f"Added reload callback: {callback}")
    
    def remove_reload_callback(self, callback: Callable):
        """Remove reload callback"""
        if callback in self.reload_callbacks:
            self.reload_callbacks.remove(callback)
            logger.debug(f"Removed reload callback: {callback}")
    
    def _notify_reload_callbacks(self):
        """Notify all reload callbacks"""
        for callback in self.reload_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in reload callback {callback}: {e}")
    
    def save_config(self, config_data: Optional[Dict[str, Any]] = None) -> bool:
        """Save configuration to YAML file"""
        try:
            # Ensure config directory exists
            self.config_path.mkdir(parents=True, exist_ok=True)
            
            # Prepare configuration data
            if config_data is None:
                config_data = {
                    'database': asdict(self.database),
                    'cache': asdict(self.cache),
                    'api': asdict(self.api),
                    'security': asdict(self.security),
                    'monitoring': asdict(self.monitoring),
                    'system': asdict(self.system)
                }
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            # Update file hash
            self.file_hash = self._calculate_file_hash()
            self.last_loaded = time.time()
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def export_env_template(self, output_file: Optional[str] = None) -> str:
        """Export environment variables template"""
        template = f"""# Environment Variables Template
# Generated from configuration on {time.strftime('%Y-%m-%d %H:%M:%S')}

# Database Configuration
DB_HOST={self.database.host}
DB_PORT={self.database.port}
DB_NAME={self.database.name}
DB_USER={self.database.user}
DB_PASSWORD={self.database.password}

# API Configuration
API_HOST={self.api.host}
API_PORT={self.api.port}

# Security Configuration
SECRET_KEY={self.security.secret_key}

# System Configuration
ENVIRONMENT={self.system.environment.value}
DEBUG={str(self.system.debug).lower()}
"""
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(template)
                logger.info(f"Environment template exported to {output_file}")
            except Exception as e:
                logger.error(f"Failed to export environment template: {e}")
        
        return template
    
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
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            'environment': self.system.environment.value,
            'debug': self.system.debug,
            'database_host': self.database.host,
            'api_host': self.api.host,
            'api_port': self.api.port,
            'log_level': self.monitoring.log_level,
            'last_loaded': self.last_loaded,
            'file_hash': self.file_hash,
            'reload_callbacks_count': len(self.reload_callbacks)
        }
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive configuration value"""
        if not self.encryption_key:
            raise ConfigEncryptionError("Encryption not enabled")
        
        try:
            encrypted = self.encryption_key.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise ConfigEncryptionError(f"Encryption failed: {e}")
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt an encrypted configuration value"""
        if not self.encryption_key:
            raise ConfigEncryptionError("Encryption not enabled")
        
        try:
            encrypted = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = self.encryption_key.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            raise ConfigEncryptionError(f"Decryption failed: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'observer') and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info("Configuration file watcher stopped")


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_config(skip_validation: bool = False):
    """Reload global configuration"""
    config = get_config()
    config.reload_config(skip_validation)


def save_config(config_data: Optional[Dict[str, Any]] = None) -> bool:
    """Save global configuration"""
    config = get_config()
    return config.save_config(config_data)


def export_env_template(output_file: Optional[str] = None) -> str:
    """Export environment variables template"""
    config = get_config()
    return config.export_env_template(output_file)


if __name__ == "__main__":
    # Example usage
    try:
        config = ConfigManager()
        print(f"Configuration loaded for environment: {config.system.environment.value}")
        print(f"Database host: {config.database.host}")
        print(f"API port: {config.api.port}")
        
        # Export environment template
        template = config.export_env_template()
        print("\nEnvironment template:")
        print(template)
        
    except Exception as e:
        print(f"Error: {e}")
