"""
Environment Manager for Instagram Captions API v10.0
Environment-specific configurations and management.
"""
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
import shutil

logger = logging.getLogger(__name__)

class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
    LOCAL = "local"

class EnvironmentConfig:
    """Configuration for a specific environment."""
    
    def __init__(self, name: str, env: Environment):
        self.name = name
        self.environment = env
        self.config: Dict[str, Any] = {}
        self.env_vars: Dict[str, str] = {}
        self.secrets: Dict[str, str] = {}
        self.features: Dict[str, bool] = {}
        self.dependencies: List[str] = []

class EnvironmentManager:
    """Manages environment-specific configurations."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.environments: Dict[str, EnvironmentConfig] = {}
        self.current_environment: Optional[Environment] = None
        self.config_dir = self.base_path / "config" / "environments"
        
        self._initialize_environments()
        self._detect_current_environment()
    
    def _initialize_environments(self):
        """Initialize default environment configurations."""
        # Development environment
        dev_config = EnvironmentConfig("development", Environment.DEVELOPMENT)
        dev_config.config = {
            "debug": True,
            "log_level": "DEBUG",
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "instagram_captions_dev",
                "user": "postgres",
                "password": "dev_password"
            },
            "api": {
                "host": "127.0.0.1",
                "port": 8000,
                "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"]
            },
            "security": {
                "secret_key": "dev-secret-key-change-in-production",
                "access_token_expire_minutes": 60,
                "password_min_length": 6
            },
            "performance": {
                "max_workers": 2,
                "batch_size": 50,
                "cache_ttl_seconds": 1800
            }
        }
        dev_config.env_vars = {
            "ENVIRONMENT": "development",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": "instagram_captions_dev",
            "DATABASE_USER": "postgres",
            "DATABASE_PASSWORD": "dev_password",
            "API_HOST": "127.0.0.1",
            "API_PORT": "8000"
        }
        dev_config.features = {
            "hot_reload": True,
            "detailed_logging": True,
            "development_tools": True,
            "mock_services": True
        }
        dev_config.dependencies = ["postgresql", "redis"]
        
        # Staging environment
        staging_config = EnvironmentConfig("staging", Environment.STAGING)
        staging_config.config = {
            "debug": False,
            "log_level": "INFO",
            "database": {
                "host": "staging-db.example.com",
                "port": 5432,
                "name": "instagram_captions_staging",
                "user": "staging_user",
                "password": "staging_password"
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "cors_origins": ["https://staging.example.com"]
            },
            "security": {
                "secret_key": "staging-secret-key-change-in-production",
                "access_token_expire_minutes": 30,
                "password_min_length": 8
            },
            "performance": {
                "max_workers": 4,
                "batch_size": 100,
                "cache_ttl_seconds": 3600
            }
        }
        staging_config.env_vars = {
            "ENVIRONMENT": "staging",
            "DEBUG": "false",
            "LOG_LEVEL": "INFO",
            "DATABASE_HOST": "staging-db.example.com",
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": "instagram_captions_staging",
            "DATABASE_USER": "staging_user",
            "DATABASE_PASSWORD": "staging_password",
            "API_HOST": "0.0.0.0",
            "API_PORT": "8000"
        }
        staging_config.features = {
            "hot_reload": False,
            "detailed_logging": True,
            "development_tools": False,
            "mock_services": False
        }
        staging_config.dependencies = ["postgresql", "redis", "monitoring"]
        
        # Production environment
        prod_config = EnvironmentConfig("production", Environment.PRODUCTION)
        prod_config.config = {
            "debug": False,
            "log_level": "WARNING",
            "database": {
                "host": "prod-db.example.com",
                "port": 5432,
                "name": "instagram_captions_prod",
                "user": "prod_user",
                "password": "prod_password"
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "cors_origins": ["https://example.com", "https://www.example.com"]
            },
            "security": {
                "secret_key": "production-secret-key-change-this",
                "access_token_expire_minutes": 15,
                "password_min_length": 12
            },
            "performance": {
                "max_workers": 8,
                "batch_size": 200,
                "cache_ttl_seconds": 7200
            }
        }
        prod_config.env_vars = {
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "LOG_LEVEL": "WARNING",
            "DATABASE_HOST": "prod-db.example.com",
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": "instagram_captions_prod",
            "DATABASE_USER": "prod_user",
            "DATABASE_PASSWORD": "prod_password",
            "API_HOST": "0.0.0.0",
            "API_PORT": "8000"
        }
        prod_config.features = {
            "hot_reload": False,
            "detailed_logging": False,
            "development_tools": False,
            "mock_services": False
        }
        prod_config.dependencies = ["postgresql", "redis", "monitoring", "backup", "ssl"]
        
        # Testing environment
        test_config = EnvironmentConfig("testing", Environment.TESTING)
        test_config.config = {
            "debug": True,
            "log_level": "DEBUG",
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "instagram_captions_test",
                "user": "test_user",
                "password": "test_password"
            },
            "api": {
                "host": "127.0.0.1",
                "port": 8001,
                "cors_origins": ["http://localhost:3001"]
            },
            "security": {
                "secret_key": "test-secret-key-not-for-production",
                "access_token_expire_minutes": 5,
                "password_min_length": 4
            },
            "performance": {
                "max_workers": 1,
                "batch_size": 10,
                "cache_ttl_seconds": 300
            }
        }
        test_config.env_vars = {
            "ENVIRONMENT": "testing",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": "instagram_captions_test",
            "DATABASE_USER": "test_user",
            "DATABASE_PASSWORD": "test_password",
            "API_HOST": "127.0.0.1",
            "API_PORT": "8001"
        }
        test_config.features = {
            "hot_reload": False,
            "detailed_logging": True,
            "development_tools": False,
            "mock_services": True
        }
        test_config.dependencies = ["postgresql", "test_framework"]
        
        # Local environment
        local_config = EnvironmentConfig("local", Environment.LOCAL)
        local_config.config = {
            "debug": True,
            "log_level": "DEBUG",
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "instagram_captions_local",
                "user": "postgres",
                "password": "local_password"
            },
            "api": {
                "host": "127.0.0.1",
                "port": 8000,
                "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"]
            },
            "security": {
                "secret_key": "local-secret-key-not-for-production",
                "access_token_expire_minutes": 120,
                "password_min_length": 6
            },
            "performance": {
                "max_workers": 1,
                "batch_size": 25,
                "cache_ttl_seconds": 900
            }
        }
        local_config.env_vars = {
            "ENVIRONMENT": "local",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": "instagram_captions_local",
            "DATABASE_USER": "postgres",
            "DATABASE_PASSWORD": "local_password",
            "API_HOST": "127.0.0.1",
            "API_PORT": "8000"
        }
        local_config.features = {
            "hot_reload": True,
            "detailed_logging": True,
            "development_tools": True,
            "mock_services": True
        }
        local_config.dependencies = ["postgresql", "docker"]
        
        # Add all environments
        self.environments = {
            "development": dev_config,
            "staging": staging_config,
            "production": prod_config,
            "testing": test_config,
            "local": local_config
        }
        
        logger.info("Environment configurations initialized")
    
    def _detect_current_environment(self):
        """Detect the current environment from various sources."""
        # Check environment variable first
        env_var = os.getenv("ENVIRONMENT", "").lower()
        if env_var in self.environments:
            self.current_environment = self.environments[env_var].environment
            logger.info(f"Environment detected from ENVIRONMENT variable: {env_var}")
            return
        
        # Check for common environment indicators
        if os.getenv("FLASK_ENV") == "development":
            self.current_environment = Environment.DEVELOPMENT
            logger.info("Environment detected from FLASK_ENV: development")
            return
        
        if os.getenv("NODE_ENV") == "development":
            self.current_environment = Environment.DEVELOPMENT
            logger.info("Environment detected from NODE_ENV: development")
            return
        
        # Check for common development indicators
        if os.path.exists(".env.development"):
            self.current_environment = Environment.DEVELOPMENT
            logger.info("Environment detected from .env.development file")
            return
        
        if os.path.exists("docker-compose.yml") or os.path.exists("docker-compose.yaml"):
            self.current_environment = Environment.LOCAL
            logger.info("Environment detected from Docker Compose files")
            return
        
        # Check hostname for production/staging indicators
        hostname = os.getenv("HOSTNAME", "").lower()
        if "prod" in hostname or "production" in hostname:
            self.current_environment = Environment.PRODUCTION
            logger.info("Environment detected from hostname: production")
            return
        
        if "staging" in hostname or "stage" in hostname:
            self.current_environment = Environment.STAGING
            logger.info("Environment detected from hostname: staging")
            return
        
        # Default to development
        self.current_environment = Environment.DEVELOPMENT
        logger.info("Environment defaulted to: development")
    
    def get_current_environment(self) -> Environment:
        """Get the current environment."""
        return self.current_environment
    
    def set_current_environment(self, environment: Environment):
        """Set the current environment."""
        self.current_environment = environment
        logger.info(f"Environment set to: {environment.value}")
    
    def get_environment_config(self, environment_name: Optional[str] = None) -> EnvironmentConfig:
        """Get configuration for a specific environment."""
        if environment_name is None:
            environment_name = self.current_environment.value
        
        if environment_name not in self.environments:
            raise ValueError(f"Unknown environment: {environment_name}")
        
        return self.environments[environment_name]
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get configuration for the current environment."""
        env_name = self.current_environment.value
        return self.environments[env_name].config
    
    def get_current_env_vars(self) -> Dict[str, str]:
        """Get environment variables for the current environment."""
        env_name = self.current_environment.value
        return self.environments[env_name].env_vars
    
    def get_current_features(self) -> Dict[str, bool]:
        """Get features for the current environment."""
        env_name = self.current_environment.value
        return self.environments[env_name].features
    
    def get_current_dependencies(self) -> List[str]:
        """Get dependencies for the current environment."""
        env_name = self.current_environment.value
        return self.environments[env_name].dependencies
    
    def create_environment_files(self, environment_name: str, output_dir: Optional[str] = None):
        """Create configuration files for a specific environment."""
        if environment_name not in self.environments:
            raise ValueError(f"Unknown environment: {environment_name}")
        
        env_config = self.environments[environment_name]
        output_path = Path(output_dir) if output_dir else self.base_path
        
        # Create .env file
        env_file_path = output_path / f".env.{environment_name}"
        self._create_env_file(env_file_path, env_config.env_vars)
        
        # Create YAML config file
        yaml_file_path = output_path / f"config.{environment_name}.yaml"
        self._create_yaml_file(yaml_file_path, env_config.config)
        
        # Create JSON config file
        json_file_path = output_path / f"config.{environment_name}.json"
        self._create_json_file(json_file_path, env_config.config)
        
        logger.info(f"Environment files created for {environment_name}")
    
    def _create_env_file(self, file_path: Path, env_vars: Dict[str, str]):
        """Create a .env file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Environment Configuration for {file_path.stem}\n")
                f.write(f"# Generated by EnvironmentManager\n\n")
                
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            logger.debug(f"Created .env file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error creating .env file {file_path}: {e}")
            raise
    
    def _create_yaml_file(self, file_path: Path, config: Dict[str, Any]):
        """Create a YAML configuration file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2, allow_unicode=True)
            
            logger.debug(f"Created YAML file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error creating YAML file {file_path}: {e}")
            raise
    
    def _create_json_file(self, file_path: Path, config: Dict[str, Any]):
        """Create a JSON configuration file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Created JSON file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error creating JSON file {file_path}: {e}")
            raise
    
    def create_all_environment_files(self, output_dir: Optional[str] = None):
        """Create configuration files for all environments."""
        for env_name in self.environments:
            self.create_environment_files(env_name, output_dir)
        
        logger.info("Created configuration files for all environments")
    
    def validate_environment(self, environment_name: str) -> List[str]:
        """Validate an environment configuration."""
        if environment_name not in self.environments:
            return [f"Unknown environment: {environment_name}"]
        
        env_config = self.environments[environment_name]
        errors = []
        
        # Validate required configuration sections
        required_sections = ["database", "api", "security", "performance"]
        for section in required_sections:
            if section not in env_config.config:
                errors.append(f"Missing required configuration section: {section}")
        
        # Validate database configuration
        if "database" in env_config.config:
            db_config = env_config.config["database"]
            required_db_fields = ["host", "port", "name", "user"]
            for field in required_db_fields:
                if field not in db_config:
                    errors.append(f"Missing required database field: {field}")
            
            if "port" in db_config:
                try:
                    port = int(db_config["port"])
                    if port < 1 or port > 65535:
                        errors.append("Database port must be between 1 and 65535")
                except (ValueError, TypeError):
                    errors.append("Database port must be a valid integer")
        
        # Validate API configuration
        if "api" in env_config.config:
            api_config = env_config.config["api"]
            if "port" in api_config:
                try:
                    port = int(api_config["port"])
                    if port < 1 or port > 65535:
                        errors.append("API port must be between 1 and 65535")
                except (ValueError, TypeError):
                    errors.append("API port must be a valid integer")
        
        # Validate security configuration
        if "security" in env_config.config:
            security_config = env_config.config["security"]
            if "secret_key" in security_config:
                secret_key = security_config["secret_key"]
                if len(secret_key) < 16:
                    errors.append("Secret key must be at least 16 characters long")
        
        return errors
    
    def validate_all_environments(self) -> Dict[str, List[str]]:
        """Validate all environment configurations."""
        validation_results = {}
        
        for env_name in self.environments:
            validation_results[env_name] = self.validate_environment(env_name)
        
        return validation_results
    
    def get_environment_summary(self) -> Dict[str, Any]:
        """Get a summary of all environments."""
        summary = {
            "current_environment": self.current_environment.value if self.current_environment else None,
            "available_environments": list(self.environments.keys()),
            "environment_details": {}
        }
        
        for env_name, env_config in self.environments.items():
            summary["environment_details"][env_name] = {
                "type": env_config.environment.value,
                "features": env_config.features,
                "dependencies": env_config.dependencies,
                "validation_errors": self.validate_environment(env_name)
            }
        
        return summary
    
    def copy_environment(self, source_env: str, target_env: str):
        """Copy configuration from one environment to another."""
        if source_env not in self.environments:
            raise ValueError(f"Source environment not found: {source_env}")
        
        if target_env in self.environments:
            logger.warning(f"Target environment {target_env} already exists, overwriting")
        
        # Create new environment config
        source_config = self.environments[source_env]
        new_config = EnvironmentConfig(target_env, source_config.environment)
        
        # Deep copy configuration
        new_config.config = self._deep_copy_dict(source_config.config)
        new_config.env_vars = source_config.env_vars.copy()
        new_config.secrets = source_config.secrets.copy()
        new_config.features = source_config.features.copy()
        new_config.dependencies = source_config.dependencies.copy()
        
        # Update environment-specific values
        new_config.env_vars["ENVIRONMENT"] = target_env
        if "ENVIRONMENT" in new_config.config:
            new_config.config["ENVIRONMENT"] = target_env
        
        self.environments[target_env] = new_config
        logger.info(f"Environment {source_env} copied to {target_env}")
    
    def _deep_copy_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Deep copy a dictionary."""
        if not isinstance(data, dict):
            return data
        
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._deep_copy_dict(value)
            elif isinstance(value, list):
                result[key] = [self._deep_copy_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
        
        return result






