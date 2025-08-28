"""
Enhanced Tests for the Centralized Configuration Management System
================================================================

Test coverage for:
- Configuration validation and loading
- Environment variable handling
- Hot-reloading capabilities
- Configuration encryption
- File watching
- Error handling
"""

import pytest
import tempfile
import os
import yaml
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Import the configuration system
from core.config_manager import (
    Environment, ConfigValidationError, ConfigEncryptionError,
    DatabaseConfig, CacheConfig, APIConfig, SecurityConfig,
    MonitoringConfig, SystemConfig, ConfigManager,
    get_config, reload_config, save_config, export_env_template
)


class TestEnvironment:
    """Test environment enumeration"""
    
    def test_environment_values(self):
        """Test environment enum values"""
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.STAGING.value == "staging"
        assert Environment.PRODUCTION.value == "production"
        assert Environment.TESTING.value == "testing"
    
    def test_environment_comparison(self):
        """Test environment enum comparison"""
        assert Environment.DEVELOPMENT != Environment.PRODUCTION
        assert Environment.STAGING != Environment.TESTING


class TestDatabaseConfig:
    """Test database configuration dataclass"""
    
    def test_database_config_defaults(self):
        """Test database configuration default values"""
        config = DatabaseConfig()
        
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.name == "heygen_ai"
        assert config.user == "postgres"
        assert config.password == ""
        assert config.ssl_mode == "prefer"
        assert config.max_connections == 100
        assert config.connection_timeout == 30
        assert config.pool_size == 20
        assert config.retry_attempts == 3
    
    def test_database_config_validation_success(self):
        """Test successful database configuration validation"""
        config = DatabaseConfig(
            host="db.example.com",
            port=5433,
            name="test_db",
            user="test_user",
            password="secure_password"
        )
        
        errors = config.validate()
        assert len(errors) == 0
    
    def test_database_config_validation_failures(self):
        """Test database configuration validation failures"""
        config = DatabaseConfig(
            host="",  # Empty host
            port=70000,  # Invalid port
            name="",  # Empty name
            max_connections=0,  # Invalid max connections
            connection_timeout=0  # Invalid timeout
        )
        
        errors = config.validate()
        assert len(errors) == 5
        assert "Database host cannot be empty" in errors
        assert "Database port must be between 1 and 65535" in errors
        assert "Database name cannot be empty" in errors
        assert "Max connections must be greater than 0" in errors
        assert "Connection timeout must be greater than 0" in errors


class TestCacheConfig:
    """Test cache configuration dataclass"""
    
    def test_cache_config_defaults(self):
        """Test cache configuration default values"""
        config = CacheConfig()
        
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379
        assert config.redis_password == ""
        assert config.redis_db == 0
        assert config.memory_cache_size == 1000
        assert config.cache_ttl == 3600
        assert config.cache_strategy == "lru"
        assert config.enable_clustering is False
        assert config.cluster_nodes == []
    
    def test_cache_config_validation(self):
        """Test cache configuration validation"""
        config = CacheConfig(
            redis_host="",
            redis_port=70000,
            memory_cache_size=0,
            cache_ttl=0
        )
        
        errors = config.validate()
        assert len(errors) == 4


class TestAPIConfig:
    """Test API configuration dataclass"""
    
    def test_api_config_defaults(self):
        """Test API configuration default values"""
        config = APIConfig()
        
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.workers == 4
        assert config.timeout == 30
        assert config.rate_limit == 1000
        assert config.cors_origins == ["*"]
        assert config.enable_docs is True
        assert config.enable_metrics is True
        assert config.api_version == "v1"
        assert config.max_request_size == 100 * 1024 * 1024  # 100MB
    
    def test_api_config_validation(self):
        """Test API configuration validation"""
        config = APIConfig(
            host="",
            port=70000,
            workers=0,
            timeout=0,
            rate_limit=0
        )
        
        errors = config.validate()
        assert len(errors) == 5


class TestSecurityConfig:
    """Test security configuration dataclass"""
    
    def test_security_config_defaults(self):
        """Test security configuration default values"""
        config = SecurityConfig()
        
        assert config.secret_key == ""
        assert config.algorithm == "HS256"
        assert config.access_token_expire_minutes == 30
        assert config.refresh_token_expire_days == 7
        assert config.password_min_length == 8
        assert config.enable_2fa is True
        assert config.max_login_attempts == 5
        assert config.lockout_duration == 15
        assert config.enable_encryption is True
        assert config.encryption_key == ""
    
    def test_security_config_validation(self):
        """Test security configuration validation"""
        config = SecurityConfig(
            secret_key="short",  # Too short
            access_token_expire_minutes=0,
            refresh_token_expire_days=0,
            password_min_length=3,  # Too short
            max_login_attempts=0,
            lockout_duration=0
        )
        
        errors = config.validate()
        assert len(errors) == 6


class TestMonitoringConfig:
    """Test monitoring configuration dataclass"""
    
    def test_monitoring_config_defaults(self):
        """Test monitoring configuration default values"""
        config = MonitoringConfig()
        
        assert config.log_level == "INFO"
        assert config.enable_metrics is True
        assert config.metrics_port == 9090
        assert config.health_check_interval == 30
        assert config.enable_tracing is True
        assert config.tracing_endpoint == "http://localhost:14268/api/traces"
        assert config.enable_profiling is False
        assert config.profiling_interval == 60
        assert config.alert_thresholds == {}
    
    def test_monitoring_config_validation(self):
        """Test monitoring configuration validation"""
        config = MonitoringConfig(
            log_level="INVALID",
            metrics_port=70000,
            health_check_interval=0,
            profiling_interval=0
        )
        
        errors = config.validate()
        assert len(errors) == 4


class TestSystemConfig:
    """Test system configuration dataclass"""
    
    def test_system_config_defaults(self):
        """Test system configuration default values"""
        config = SystemConfig()
        
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is False
        assert config.log_file == "logs/heygen_ai.log"
        assert config.max_log_size == 100 * 1024 * 1024  # 100MB
        assert config.backup_logs == 5
        assert config.temp_dir == "temp"
        assert config.data_dir == "data"
        assert config.enable_backup is True
        assert config.backup_interval == 86400  # 24 hours
        assert config.max_backup_files == 10
    
    def test_system_config_validation(self):
        """Test system configuration validation"""
        config = SystemConfig(
            environment="invalid",  # Invalid environment
            max_log_size=1024,  # Too small
            backup_logs=0,
            backup_interval=1800,  # Too short
            max_backup_files=0
        )
        
        errors = config.validate()
        assert len(errors) == 5


class TestConfigManager:
    """Test configuration manager"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary configuration directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_config_manager_initialization(self, temp_config_dir):
        """Test configuration manager initialization"""
        config_manager = ConfigManager(
            config_path=temp_config_dir,
            skip_validation=True,
            enable_watcher=False,
            enable_encryption=False
        )
        
        assert config_manager.config_path == temp_config_dir
        assert config_manager.config_file == temp_config_dir / "config.yaml"
        assert config_manager.env_file == temp_config_dir / ".env"
        assert config_manager.enable_encryption is False
        assert config_manager.file_hash is None
        assert config_manager.last_loaded == 0
        assert len(config_manager.reload_callbacks) == 0
    
    def test_config_manager_with_config_file(self, temp_config_dir):
        """Test configuration manager with config file"""
        # Create a config file
        config_data = {
            'database': {
                'host': 'test-db.example.com',
                'port': 5433,
                'name': 'test_db'
            },
            'api': {
                'host': '127.0.0.1',
                'port': 9000
            },
            'system': {
                'environment': 'testing',
                'debug': True
            }
        }
        
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config_manager = ConfigManager(
            config_path=temp_config_dir,
            skip_validation=True,
            enable_watcher=False
        )
        
        # Check that config was loaded
        assert config_manager.database.host == "test-db.example.com"
        assert config_manager.database.port == 5433
        assert config_manager.database.name == "test_db"
        assert config_manager.api.host == "127.0.0.1"
        assert config_manager.api.port == 9000
        assert config_manager.system.environment == Environment.TESTING
        assert config_manager.system.debug is True
    
    def test_config_manager_environment_variables(self, temp_config_dir):
        """Test configuration manager with environment variables"""
        # Set environment variables
        os.environ['DB_HOST'] = 'env-db.example.com'
        os.environ['DB_PORT'] = '5434'
        os.environ['API_HOST'] = '0.0.0.0'
        os.environ['ENVIRONMENT'] = 'staging'
        os.environ['DEBUG'] = 'true'
        
        try:
            config_manager = ConfigManager(
                config_path=temp_config_dir,
                skip_validation=True,
                enable_watcher=False
            )
            
            # Check that environment variables were loaded
            assert config_manager.database.host == "env-db.example.com"
            assert config_manager.database.port == 5434
            assert config_manager.api.host == "0.0.0.0"
            assert config_manager.system.environment == Environment.STAGING
            assert config_manager.system.debug is True
            
        finally:
            # Clean up environment variables
            del os.environ['DB_HOST']
            del os.environ['DB_PORT']
            del os.environ['API_HOST']
            del os.environ['ENVIRONMENT']
            del os.environ['DEBUG']
    
    def test_config_manager_validation_failure(self, temp_config_dir):
        """Test configuration manager validation failure"""
        # Create invalid config
        config_data = {
            'security': {
                'secret_key': ''  # Empty secret key
            }
        }
        
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Should raise validation error
        with pytest.raises(ConfigValidationError):
            ConfigManager(
                config_path=temp_config_dir,
                skip_validation=False,
                enable_watcher=False
            )
    
    def test_config_manager_reload_config(self, temp_config_dir):
        """Test configuration reloading"""
        # Create initial config
        config_data = {
            'database': {
                'host': 'initial.example.com'
            }
        }
        
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config_manager = ConfigManager(
            config_path=temp_config_dir,
            skip_validation=True,
            enable_watcher=False
        )
        
        assert config_manager.database.host == "initial.example.com"
        
        # Update config file
        config_data['database']['host'] = 'updated.example.com'
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Reload config
        config_manager.reload_config(skip_validation=True)
        
        assert config_manager.database.host == "updated.example.com"
    
    def test_config_manager_save_config(self, temp_config_dir):
        """Test configuration saving"""
        config_manager = ConfigManager(
            config_path=temp_config_dir,
            skip_validation=True,
            enable_watcher=False
        )
        
        # Modify some values
        config_manager.database.host = "saved.example.com"
        config_manager.api.port = 9999
        
        # Save config
        success = config_manager.save_config()
        assert success is True
        
        # Verify file was created
        config_file = temp_config_dir / "config.yaml"
        assert config_file.exists()
        
        # Load and verify
        with open(config_file, 'r') as f:
            saved_data = yaml.safe_load(f)
        
        assert saved_data['database']['host'] == "saved.example.com"
        assert saved_data['api']['port'] == 9999
    
    def test_config_manager_export_env_template(self, temp_config_dir):
        """Test environment template export"""
        config_manager = ConfigManager(
            config_path=temp_config_dir,
            skip_validation=True,
            enable_watcher=False
        )
        
        # Export template
        template = config_manager.export_env_template()
        
        # Check template content
        assert "DB_HOST=" in template
        assert "DB_PORT=" in template
        assert "API_HOST=" in template
        assert "ENVIRONMENT=" in template
        assert "DEBUG=" in template
    
    def test_config_manager_get_database_url(self, temp_config_dir):
        """Test database URL generation"""
        config_manager = ConfigManager(
            config_path=temp_config_dir,
            skip_validation=True,
            enable_watcher=False
        )
        
        # Test without password
        url = config_manager.get_database_url()
        assert "postgresql://postgres@localhost:5432/heygen_ai" in url
        
        # Test with password
        config_manager.database.password = "secret"
        url = config_manager.get_database_url()
        assert "postgresql://postgres:secret@localhost:5432/heygen_ai" in url
    
    def test_config_manager_environment_checks(self, temp_config_dir):
        """Test environment checking methods"""
        config_manager = ConfigManager(
            config_path=temp_config_dir,
            skip_validation=True,
            enable_watcher=False
        )
        
        # Default is development
        assert config_manager.is_development() is True
        assert config_manager.is_production() is False
        assert config_manager.is_testing() is False
        
        # Change to production
        config_manager.system.environment = Environment.PRODUCTION
        assert config_manager.is_production() is True
        assert config_manager.is_development() is False
    
    def test_config_manager_get_config_summary(self, temp_config_dir):
        """Test configuration summary generation"""
        config_manager = ConfigManager(
            config_path=temp_config_dir,
            skip_validation=True,
            enable_watcher=False
        )
        
        summary = config_manager.get_config_summary()
        
        assert "environment" in summary
        assert "debug" in summary
        assert "database_host" in summary
        assert "api_host" in summary
        assert "api_port" in summary
        assert "log_level" in summary
        assert "last_loaded" in summary
        assert "file_hash" in summary
        assert "reload_callbacks_count" in summary
    
    def test_config_manager_reload_callbacks(self, temp_config_dir):
        """Test reload callback functionality"""
        config_manager = ConfigManager(
            config_path=temp_config_dir,
            skip_validation=True,
            enable_watcher=False
        )
        
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        # Add callback
        config_manager.add_reload_callback(test_callback)
        assert len(config_manager.reload_callbacks) == 1
        
        # Remove callback
        config_manager.remove_reload_callback(test_callback)
        assert len(config_manager.reload_callbacks) == 0
        
        # Test callback execution
        config_manager.add_reload_callback(test_callback)
        config_manager.reload_config(skip_validation=True)
        assert callback_called is True
    
    def test_config_manager_cleanup(self, temp_config_dir):
        """Test configuration manager cleanup"""
        config_manager = ConfigManager(
            config_path=temp_config_dir,
            skip_validation=True,
            enable_watcher=False
        )
        
        # Cleanup should not raise errors
        config_manager.cleanup()


class TestGlobalFunctions:
    """Test global convenience functions"""
    
    @patch('core.config_manager._config_manager')
    def test_get_config(self, mock_config_manager):
        """Test get_config function"""
        config = get_config()
        assert config == mock_config_manager
    
    @patch('core.config_manager._config_manager')
    def test_reload_config(self, mock_config_manager):
        """Test reload_config function"""
        reload_config(skip_validation=True)
        mock_config_manager.reload_config.assert_called_once_with(skip_validation=True)
    
    @patch('core.config_manager._config_manager')
    def test_save_config(self, mock_config_manager):
        """Test save_config function"""
        mock_config_manager.save_config.return_value = True
        
        result = save_config()
        assert result is True
        mock_config_manager.save_config.assert_called_once_with(None)
    
    @patch('core.config_manager._config_manager')
    def test_export_env_template(self, mock_config_manager):
        """Test export_env_template function"""
        mock_config_manager.export_env_template.return_value = "template content"
        
        result = export_env_template()
        assert result == "template content"
        mock_config_manager.export_env_template.assert_called_once_with(None)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
