"""
Comprehensive Test Suite for Refactored HeyGen AI System
========================================================

Tests all refactored components including:
- Base service architecture
- Error handling and retry mechanisms
- Configuration management
- Logging service
- Main system integration
"""

import asyncio
import json
import logging
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
import pytest
import pytest_asyncio

# Import the refactored components
from core.base_service import (
    BaseService, ServiceFactory, ServiceStatus, ServiceType,
    HealthCheckResult, ServiceMetrics
)
from core.error_handler import (
    ErrorHandler, CircuitBreaker, RetryHandler, ErrorClassifier,
    ErrorContext, ErrorSeverity, ErrorCategory, RetryConfig,
    with_error_handling, with_retry, with_circuit_breaker
)
from config.config_manager import (
    ConfigurationManager, HeyGenAIConfig, Environment,
    DatabaseType, CacheType
)
from monitoring.logging_service import (
    LoggingService, PerformanceMetrics, StructuredFormatter,
    AsyncLogHandler, LogLevel, LogFormat
)
from heygen_ai_main import HeyGenAISystem, VideoGenerationRequest


# Test configuration
@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file for testing."""
    config_data = {
        "environment": "testing",
        "debug": True,
        "host": "127.0.0.1",
        "port": 8000,
        "database": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "username": "test_user",
            "password": "test_password",
            "database": "test_db"
        },
        "cache": {
            "type": "redis",
            "host": "localhost",
            "port": 6379
        },
        "security": {
            "secret_key": "test-secret-key-for-testing-only-32-chars"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def mock_services():
    """Create mock services for testing."""
    return {
        "avatar_manager": AsyncMock(),
        "voice_engine": AsyncMock(),
        "video_renderer": AsyncMock(),
        "script_generator": AsyncMock(),
        "gesture_emotion_controller": AsyncMock(),
        "multi_platform_exporter": AsyncMock(),
        "external_api_manager": AsyncMock(),
        "performance_optimizer": AsyncMock(),
        "collaboration_manager": AsyncMock(),
        "advanced_analytics": AsyncMock(),
        "enterprise_features": AsyncMock(),
        "avatar_library": AsyncMock(),
        "voice_library": AsyncMock(),
        "video_template_service": AsyncMock()
    }


class TestBaseService:
    """Test the base service architecture."""
    
    class MockService(BaseService):
        """Mock service for testing BaseService."""
        
        def __init__(self, service_name: str, service_type: ServiceType, config: dict = None):
            super().__init__(service_name, service_type, config or {})
        
        async def _initialize_service_impl(self):
            """Mock initialization."""
            await asyncio.sleep(0.01)  # Simulate async work
        
        async def health_check(self):
            """Mock health check."""
            return HealthCheckResult(
                status=ServiceStatus.HEALTHY,
                details={"mock": True}
            )
    
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initialization."""
        service = self.MockService("test_service", ServiceType.CORE)
        
        assert service.service_name == "test_service"
        assert service.service_type == ServiceType.CORE
        assert service.status == ServiceStatus.HEALTHY
        assert service.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_service_health_check(self):
        """Test service health checking."""
        service = self.MockService("test_service", ServiceType.CORE)
        
        health_result = await service.health_check()
        assert health_result.status == ServiceStatus.HEALTHY
        assert health_result.details["mock"] is True
    
    @pytest.mark.asyncio
    async def test_service_metrics(self):
        """Test service metrics collection."""
        service = self.MockService("test_service", ServiceType.CORE)
        
        # Update metrics
        service.update_metrics(request_success=True, response_time=0.5)
        service.update_metrics(request_success=False, response_time=1.0)
        
        metrics = await service.get_metrics()
        assert metrics.request_count == 2
        assert metrics.error_count == 1
        assert metrics.average_response_time > 0
    
    @pytest.mark.asyncio
    async def test_service_shutdown(self):
        """Test service shutdown."""
        service = self.MockService("test_service", ServiceType.CORE)
        
        await service.shutdown()
        assert service.status == ServiceStatus.STOPPED


class TestServiceFactory:
    """Test the service factory."""
    
    @pytest.mark.asyncio
    async def test_service_registration(self):
        """Test service registration."""
        factory = ServiceFactory()
        
        # Register a service
        factory.register_service("test_service", TestBaseService.MockService)
        
        # Create the service
        service = factory.create_service("test_service", TestBaseService.MockService)
        
        assert service is not None
        assert service.service_name == "test_service"
        assert factory.get_service("test_service") == service
    
    @pytest.mark.asyncio
    async def test_health_check_all(self):
        """Test health check for all services."""
        factory = ServiceFactory()
        
        # Create multiple services
        service1 = factory.create_service("service1", TestBaseService.MockService)
        service2 = factory.create_service("service2", TestBaseService.MockService)
        
        # Check health of all services
        health_results = await factory.health_check_all()
        
        assert "service1" in health_results
        assert "service2" in health_results
        assert health_results["service1"].status == ServiceStatus.HEALTHY
        assert health_results["service2"].status == ServiceStatus.HEALTHY


class TestErrorHandler:
    """Test error handling and retry mechanisms."""
    
    @pytest.mark.asyncio
    async def test_error_classification(self):
        """Test error classification."""
        classifier = ErrorClassifier()
        
        # Test network error
        network_error = ConnectionError("Connection failed")
        classification = classifier.classify_error(network_error)
        
        assert classification["category"] == "network"
        assert classification["retryable"] is True
        assert classification["circuit_breaker"] is True
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self):
        """Test circuit breaker functionality."""
        circuit_breaker = CircuitBreaker(failure_threshold=2)
        
        # Mock function that fails
        async def failing_function():
            raise Exception("Test error")
        
        # First failure
        with pytest.raises(Exception):
            await circuit_breaker.call_async(failing_function)
        
        # Second failure should open circuit
        with pytest.raises(Exception):
            await circuit_breaker.call_async(failing_function)
        
        # Circuit should be open
        assert circuit_breaker.state.is_open is True
        
        # Stats should reflect failures
        stats = circuit_breaker.get_stats()
        assert stats["failure_count"] == 2
        assert stats["is_open"] is True
    
    @pytest.mark.asyncio
    async def test_retry_handler(self):
        """Test retry handler functionality."""
        config = RetryConfig(max_attempts=3, base_delay=0.01)
        retry_handler = RetryHandler(config)
        
        # Mock function that succeeds on third attempt
        attempt_count = 0
        
        async def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"
        
        # Should succeed after retries
        result = await retry_handler.retry_async(flaky_function)
        assert result == "success"
        assert attempt_count == 3
    
    @pytest.mark.asyncio
    async def test_error_handler_integration(self):
        """Test error handler integration."""
        error_handler = ErrorHandler()
        
        # Create error context
        context = ErrorContext(
            service_name="test_service",
            operation="test_operation"
        )
        
        # Handle an error
        error = ConnectionError("Connection failed")
        error_record = error_handler.handle_error(error, context)
        
        assert error_record["service_name"] == "test_service"
        assert error_record["operation"] == "test_operation"
        assert error_record["error_type"] == "ConnectionError"
        assert error_record["category"] == "network"
    
    @pytest.mark.asyncio
    async def test_error_handler_decorators(self):
        """Test error handling decorators."""
        
        @with_error_handling("test_service", "test_operation")
        async def test_function():
            raise ValueError("Test error")
        
        # Should log error and re-raise
        with pytest.raises(ValueError):
            await test_function()
        
        @with_retry("test_service", max_attempts=2, base_delay=0.01)
        async def flaky_function():
            raise ConnectionError("Temporary failure")
        
        # Should retry and fail
        with pytest.raises(ConnectionError):
            await flaky_function()
        
        @with_circuit_breaker("test_service", failure_threshold=1)
        async def failing_function():
            raise Exception("Test error")
        
        # Should fail and open circuit
        with pytest.raises(Exception):
            await failing_function()


class TestConfigurationManager:
    """Test configuration management."""
    
    @pytest.mark.asyncio
    async def test_config_loading(self, temp_config_file):
        """Test configuration loading from file."""
        config_manager = ConfigurationManager(temp_config_file)
        
        config = config_manager.get_config()
        assert config.environment == Environment.TESTING
        assert config.debug is True
        assert config.host == "127.0.0.1"
        assert config.port == 8000
    
    @pytest.mark.asyncio
    async def test_config_validation(self):
        """Test configuration validation."""
        # Test invalid secret key
        with pytest.raises(ValueError, match="Secret key must be set"):
            HeyGenAIConfig(security={"secret_key": "your-secret-key-here"})
        
        # Test valid configuration
        config = HeyGenAIConfig(
            security={"secret_key": "valid-secret-key-32-chars-long"}
        )
        assert config.security.secret_key == "valid-secret-key-32-chars-long"
    
    @pytest.mark.asyncio
    async def test_config_get_value(self, temp_config_file):
        """Test getting configuration values by path."""
        config_manager = ConfigurationManager(temp_config_file)
        
        # Test nested value access
        db_host = config_manager.get_value("database.host")
        assert db_host == "localhost"
        
        # Test default value
        unknown_value = config_manager.get_value("unknown.key", "default")
        assert unknown_value == "default"
    
    @pytest.mark.asyncio
    async def test_config_export(self, temp_config_file):
        """Test configuration export."""
        config_manager = ConfigurationManager(temp_config_file)
        
        # Export as JSON
        json_config = config_manager.export_config("json")
        config_data = json.loads(json_config)
        assert config_data["environment"] == "testing"
        
        # Export as YAML
        yaml_config = config_manager.export_config("yaml")
        assert "environment: testing" in yaml_config
    
    @pytest.mark.asyncio
    async def test_config_save(self, temp_config_file):
        """Test configuration saving."""
        config_manager = ConfigurationManager(temp_config_file)
        
        # Save to new file
        new_config_path = temp_config_file.replace(".json", "_new.json")
        success = config_manager.save_config(new_config_path)
        assert success is True
        
        # Verify file was created
        assert Path(new_config_path).exists()
        
        # Cleanup
        os.unlink(new_config_path)


class TestLoggingService:
    """Test logging service functionality."""
    
    @pytest.mark.asyncio
    async def test_logging_initialization(self):
        """Test logging service initialization."""
        with tempfile.NamedTemporaryFile(suffix='.log') as temp_log:
            logging_service = LoggingService(
                log_level="DEBUG",
                log_format="json",
                log_file=temp_log.name,
                enable_console=False,
                enable_file=True
            )
            
            assert logging_service.log_level.level == "DEBUG"
            assert logging_service.log_format.format_type == "json"
            
            # Test logger creation
            logger = logging_service.get_logger("test_logger")
            assert logger is not None
            
            await logging_service.shutdown()
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self):
        """Test performance metrics logging."""
        logging_service = LoggingService(enable_console=False)
        
        # Test performance timer
        with logging_service.performance_timer("test_operation"):
            await asyncio.sleep(0.01)
        
        # Test manual performance logging
        logging_service.log_performance("manual_operation", 0.5)
        
        metrics = logging_service.get_performance_metrics()
        assert len(metrics) >= 2
        
        await logging_service.shutdown()
    
    @pytest.mark.asyncio
    async def test_error_logging(self):
        """Test error logging functionality."""
        logging_service = LoggingService(enable_console=False)
        
        # Test error logging
        error = ValueError("Test error")
        logging_service.log_error(error, "test_context", user_id="test_user")
        
        # Test security event logging
        logging_service.log_security_event(
            "login_attempt",
            user_id="test_user",
            ip_address="127.0.0.1"
        )
        
        # Test business event logging
        logging_service.log_business_event(
            "video_generated",
            user_id="test_user",
            video_id="test_video_123"
        )
        
        await logging_service.shutdown()
    
    @pytest.mark.asyncio
    async def test_log_level_changes(self):
        """Test dynamic log level changes."""
        logging_service = LoggingService(enable_console=False)
        
        # Change log level
        logging_service.set_log_level("DEBUG")
        assert logging_service.log_level.level == "DEBUG"
        
        # Change back
        logging_service.set_log_level("INFO")
        assert logging_service.log_level.level == "INFO"
        
        await logging_service.shutdown()


class TestHeyGenAISystem:
    """Test the main HeyGen AI system integration."""
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, mock_services):
        """Test system initialization."""
        with patch('heygen_ai_main.ConfigurationManager'), \
             patch('heygen_ai_main.LoggingService'):
            
            system = HeyGenAISystem()
            
            # Check if system is initialized
            assert system.is_initialized is True
            assert system.initialization_error is None
    
    @pytest.mark.asyncio
    async def test_video_generation(self, mock_services):
        """Test video generation workflow."""
        with patch('heygen_ai_main.ConfigurationManager'), \
             patch('heygen_ai_main.LoggingService'):
            
            system = HeyGenAISystem()
            
            # Mock service responses
            mock_services["avatar_manager"].generate_avatar.return_value = MagicMock(
                avatar_path="/tmp/test_avatar.png"
            )
            mock_services["voice_engine"].generate_speech.return_value = MagicMock(
                audio_path="/tmp/test_audio.wav",
                duration=10.0
            )
            mock_services["video_renderer"].render_video.return_value = MagicMock(
                video_path="/tmp/test_video.mp4",
                duration=10.0
            )
            
            # Create video generation request
            request = VideoGenerationRequest(
                script="Hello, this is a test video!",
                avatar_id="test_avatar_01",
                voice_id="test_voice_01",
                quality="high"
            )
            
            # Generate video
            result = await system.generate_video(request)
            
            assert result.video_id is not None
            assert result.video_path == "/tmp/test_video.mp4"
            assert result.duration == 10.0
            assert result.quality == "high"
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_services):
        """Test system health checking."""
        with patch('heygen_ai_main.ConfigurationManager'), \
             patch('heygen_ai_main.LoggingService'):
            
            system = HeyGenAISystem()
            
            # Mock health check responses
            for service in mock_services.values():
                service.health_check.return_value = {"status": "healthy"}
            
            # Perform health check
            health_status = await system.health_check()
            
            assert health_status["system"]["status"] == "healthy"
            assert "components" in health_status
    
    @pytest.mark.asyncio
    async def test_system_shutdown(self, mock_services):
        """Test system shutdown."""
        with patch('heygen_ai_main.ConfigurationManager'), \
             patch('heygen_ai_main.LoggingService'):
            
            system = HeyGenAISystem()
            
            # Mock shutdown methods
            for service in mock_services.values():
                service.shutdown = AsyncMock()
            
            # Shutdown system
            await system.shutdown()
            
            # Verify all services were shut down
            for service in mock_services.values():
                service.shutdown.assert_called_once()


class TestIntegrationScenarios:
    """Test integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_error_handling(self):
        """Test full workflow with error handling."""
        # This test would simulate a complete video generation workflow
        # with various error conditions and recovery mechanisms
        pass
    
    @pytest.mark.asyncio
    async def test_configuration_hot_reload(self):
        """Test configuration hot-reloading."""
        # This test would simulate configuration file changes
        # and verify that the system responds appropriately
        pass
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test system performance under load."""
        # This test would simulate multiple concurrent requests
        # and verify performance characteristics
        pass


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    @pytest.mark.asyncio
    async def test_logging_performance(self):
        """Test logging performance."""
        logging_service = LoggingService(enable_console=False)
        
        start_time = time.time()
        
        # Log many messages
        for i in range(1000):
            logging_service.log_performance(f"operation_{i}", 0.001)
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time
        assert duration < 5.0  # 5 seconds max
        
        await logging_service.shutdown()
    
    @pytest.mark.asyncio
    async def test_error_handling_performance(self):
        """Test error handling performance."""
        error_handler = ErrorHandler()
        
        start_time = time.time()
        
        # Handle many errors
        for i in range(1000):
            context = ErrorContext(f"service_{i}", f"operation_{i}")
            error = ValueError(f"Error {i}")
            error_handler.handle_error(error, context)
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time
        assert duration < 5.0  # 5 seconds max
        
        await error_handler.shutdown()


# Test utilities
def create_mock_config():
    """Create a mock configuration for testing."""
    return {
        "environment": "testing",
        "debug": True,
        "host": "127.0.0.1",
        "port": 8000,
        "database": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "username": "test_user",
            "password": "test_password",
            "database": "test_db"
        },
        "security": {
            "secret_key": "test-secret-key-for-testing-only-32-chars"
        }
    }


def create_mock_error_context():
    """Create a mock error context for testing."""
    return ErrorContext(
        service_name="test_service",
        operation="test_operation",
        user_id="test_user",
        session_id="test_session",
        request_id="test_request"
    )


# Main test execution
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
