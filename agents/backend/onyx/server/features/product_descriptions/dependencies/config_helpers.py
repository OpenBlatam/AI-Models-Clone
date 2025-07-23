import yaml
import json
import jsonschema
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import os
from dataclasses import dataclass
from functools import lru_cache

@dataclass
class SecurityConfig:
    """Security configuration schema"""
    max_scan_duration: int = 300
    rate_limit_per_minute: int = 60
    allowed_ports: List[int] = None
    blocked_ips: List[str] = None
    
    def __post_init__(self):
        if self.allowed_ports is None:
            self.allowed_ports = [22, 80, 443, 8080, 8443]
        if self.blocked_ips is None:
            self.blocked_ips = []

@dataclass
class DatabaseConfig:
    """Database configuration schema"""
    host: str = "localhost"
    port: int = 5432
    database: str = "security_tools"
    username: str = ""
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20

@dataclass
class LoggingConfig:
    """Logging configuration schema"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

class ConfigManager:
    """Configuration manager with YAML and JSON schema validation"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yaml"
        self._config_cache = {}
        self._schema_cache = {}
        
        # Default JSON schemas
        self.schemas = {
            "security": {
                "type": "object",
                "properties": {
                    "max_scan_duration": {"type": "integer", "minimum": 1, "maximum": 3600},
                    "rate_limit_per_minute": {"type": "integer", "minimum": 1, "maximum": 1000},
                    "allowed_ports": {"type": "array", "items": {"type": "integer"}},
                    "blocked_ips": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["max_scan_duration", "rate_limit_per_minute"]
            },
            "database": {
                "type": "object",
                "properties": {
                    "host": {"type": "string"},
                    "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                    "database": {"type": "string"},
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                    "pool_size": {"type": "integer", "minimum": 1, "maximum": 100},
                    "max_overflow": {"type": "integer", "minimum": 0}
                },
                "required": ["host", "database"]
            },
            "logging": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                    "format": {"type": "string"},
                    "file_path": {"type": "string"},
                    "max_file_size": {"type": "integer", "minimum": 1024},
                    "backup_count": {"type": "integer", "minimum": 0}
                },
                "required": ["level"]
            }
        }
    
    def load_yaml_config(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            return config or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in {file_path}: {e}")
    
    def save_yaml_config(self, config: Dict[str, Any], file_path: str) -> None:
        """Save configuration to YAML file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False, indent=2)
        except Exception as e:
            raise IOError(f"Failed to save configuration to {file_path}: {e}")
    
    def validate_config_section(self, config: Dict[str, Any], section: str) -> bool:
        """Validate configuration section against JSON schema"""
        if section not in self.schemas:
            return True  # No schema defined, assume valid
        
        try:
            jsonschema.validate(instance=config, schema=self.schemas[section])
            return True
        except jsonschema.ValidationError as e:
            raise ValueError(f"Configuration validation failed for {section}: {e}")
    
    def validate_full_config(self, config: Dict[str, Any]) -> bool:
        """Validate entire configuration"""
        for section, section_config in config.items():
            if section in self.schemas:
                self.validate_config_section(section_config, section)
        return True
    
    @lru_cache(maxsize=1)
    def get_config(self) -> Dict[str, Any]:
        """Get cached configuration"""
        if not self._config_cache:
            config = self.load_yaml_config(self.config_path)
            self.validate_full_config(config)
            self._config_cache = config
        return self._config_cache
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get specific configuration section"""
        config = self.get_config()
        return config.get(section, {})
    
    def update_section(self, section: str, new_config: Dict[str, Any]) -> None:
        """Update specific configuration section"""
        config = self.get_config()
        if section in self.schemas:
            self.validate_config_section(new_config, section)
        
        config[section] = new_config
        self.save_yaml_config(config, self.config_path)
        self._config_cache.clear()  # Clear cache
    
    def create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        default_config = {
            "security": {
                "max_scan_duration": 300,
                "rate_limit_per_minute": 60,
                "allowed_ports": [22, 80, 443, 8080, 8443],
                "blocked_ips": []
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "security_tools",
                "username": "",
                "password": "",
                "pool_size": 10,
                "max_overflow": 20
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_path": None,
                "max_file_size": 10 * 1024 * 1024,
                "backup_count": 5
            },
            "scanning": {
                "default_timeout": 5.0,
                "max_concurrent_scans": 10,
                "retry_attempts": 3,
                "retry_delay": 1.0
            },
            "reporting": {
                "output_format": "json",
                "include_timestamps": True,
                "include_metadata": True,
                "max_report_size": 1024 * 1024  # 1MB
            }
        }
        return default_config
    
    def initialize_config(self) -> None:
        """Initialize configuration file with defaults"""
        if not os.path.exists(self.config_path):
            default_config = self.create_default_config()
            self.save_yaml_config(default_config, self.config_path)
    
    def reload_config(self) -> None:
        """Reload configuration from file"""
        self._config_cache.clear()
        return self.get_config()
    
    def get_env_overrides(self) -> Dict[str, Any]:
        """Get configuration overrides from environment variables"""
        overrides = {}
        
        # Security overrides
        if max_duration := os.getenv("SECURITY_MAX_SCAN_DURATION"):
            overrides.setdefault("security", {})["max_scan_duration"] = int(max_duration)
        
        if rate_limit := os.getenv("SECURITY_RATE_LIMIT"):
            overrides.setdefault("security", {})["rate_limit_per_minute"] = int(rate_limit)
        
        # Database overrides
        if db_host := os.getenv("DB_HOST"):
            overrides.setdefault("database", {})["host"] = db_host
        
        if db_port := os.getenv("DB_PORT"):
            overrides.setdefault("database", {})["port"] = int(db_port)
        
        if db_name := os.getenv("DB_NAME"):
            overrides.setdefault("database", {})["database"] = db_name
        
        # Logging overrides
        if log_level := os.getenv("LOG_LEVEL"):
            overrides.setdefault("logging", {})["level"] = log_level
        
        return overrides
    
    def apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration"""
        overrides = self.get_env_overrides()
        if overrides:
            config = self.get_config()
            for section, section_overrides in overrides.items():
                if section not in config:
                    config[section] = {}
                config[section].update(section_overrides)
            
            self.save_yaml_config(config, self.config_path)
            self._config_cache.clear()

# FastAPI dependency for configuration
def get_config_manager() -> ConfigManager:
    """FastAPI dependency for configuration manager"""
    return ConfigManager()

def get_security_config(config_manager: ConfigManager = Depends(get_config_manager)) -> SecurityConfig:
    """Get security configuration"""
    security_data = config_manager.get_section("security")
    return SecurityConfig(**security_data)

def get_database_config(config_manager: ConfigManager = Depends(get_config_manager)) -> DatabaseConfig:
    """Get database configuration"""
    db_data = config_manager.get_section("database")
    return DatabaseConfig(**db_data)

def get_logging_config(config_manager: ConfigManager = Depends(get_config_manager)) -> LoggingConfig:
    """Get logging configuration"""
    logging_data = config_manager.get_section("logging")
    return LoggingConfig(**logging_data) 