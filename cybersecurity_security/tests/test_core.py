"""
Tests for Core Module

Tests error handling, validation, logging, and monitoring functionality.
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from ..core import (
    # Error Handling
    SecurityToolkitError, ValidationError, ConfigurationError, NetworkError,
    CryptoError, ScanError, AttackError, ReportError, TargetValidationError,
    PortValidationError, CredentialValidationError, PayloadValidationError,
    TimeoutError, ConnectionError, AuthenticationError, AuthorizationError,
    RateLimitError, ResourceNotFoundError, ErrorHandler, ErrorContext,
    ErrorSeverity, ErrorCategory, RetryStrategy, CircuitBreaker,
    FallbackHandler, ErrorRecoveryManager, handle_security_error,
    log_error, format_error_message, create_error_context,
    
    # Validation
    BaseValidator, TargetValidator, PortValidator, CredentialValidator,
    PayloadValidator, ConfigValidator, NetworkValidator, CryptoValidator,
    ValidationRule, ValidationResult, ValidationContext, ValidationLevel,
    ValidationMode, ValidationSchema, FieldValidator, CustomValidator,
    CompositeValidator, validate_target, validate_port, validate_credentials,
    validate_payload, validate_config, validate_network_target, validate_crypto_params,
    
    # Logging
    SecurityLogger, LogLevel, LogFormat, LogHandler, StructuredLogger,
    LogConfig, LogContext, LogMetadata, LogFilter, setup_logging,
    get_logger, log_operation, log_security_event, log_performance_metrics,
    
    # Monitoring
    PerformanceMonitor, HealthChecker, MetricsCollector, AlertManager,
    MetricType, HealthStatus, AlertLevel, AlertChannel, track_performance,
    check_health, collect_metrics, send_alert, monitor_operation
)

class TestErrorHandling:
    """Test suite for error handling."""
    
    def test_base_exception_creation(self):
        """Test base exception creation."""
        error = SecurityToolkitError(
            message="Test error",
            error_code="TEST_ERROR",
            context={"test": "data"}
        )
        
        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.context == {"test": "data"}
        assert error.timestamp is not None
        assert error.traceback is not None
    
    def test_base_exception_to_dict(self):
        """Test exception serialization."""
        error = SecurityToolkitError("Test error", "TEST_ERROR")
        error_dict = error.to_dict()
        
        assert error_dict["error_type"] == "SecurityToolkitError"
        assert error_dict["message"] == "Test error"
        assert error_dict["error_code"] == "TEST_ERROR"
        assert "timestamp" in error_dict
        assert "traceback" in error_dict
    
    def test_validation_error(self):
        """Test validation error."""
        error = ValidationError(
            message="Invalid input",
            field="username",
            value="invalid@user"
        )
        
        assert error.field == "username"
        assert error.value == "invalid@user"
        assert error.error_code == "VALIDATION_ERROR"
    
    def test_network_error(self):
        """Test network error."""
        error = NetworkError(
            message="Connection failed",
            target="192.168.1.1",
            port=80
        )
        
        assert error.target == "192.168.1.1"
        assert error.port == 80
        assert error.error_code == "NETWORK_ERROR"
    
    def test_crypto_error(self):
        """Test crypto error."""
        error = CryptoError(
            message="Encryption failed",
            operation="encrypt",
            algorithm="AES-256"
        )
        
        assert error.operation == "encrypt"
        assert error.algorithm == "AES-256"
        assert error.error_code == "CRYPTO_ERROR"
    
    def test_specific_exceptions(self):
        """Test specific exception types."""
        # Target validation error
        target_error = TargetValidationError("Invalid target", "invalid@target")
        assert target_error.target == "invalid@target"
        
        # Port validation error
        port_error = PortValidationError("Invalid port", 70000)
        assert port_error.port == 70000
        
        # Credential validation error
        cred_error = CredentialValidationError("Invalid credentials", "admin")
        assert cred_error.username == "admin"
        
        # Payload validation error
        payload_error = PayloadValidationError("Invalid payload", "sql_injection")
        assert payload_error.payload_type == "sql_injection"
        
        # Timeout error
        timeout_error = TimeoutError("Operation timed out", 30.0, "scan")
        assert timeout_error.timeout == 30.0
        assert timeout_error.operation == "scan"
        
        # Connection error
        conn_error = ConnectionError("Connection failed", "192.168.1.1", 80)
        assert conn_error.target == "192.168.1.1"
        assert conn_error.port == 80
        
        # Authentication error
        auth_error = AuthenticationError("Authentication failed", "ssh")
        assert auth_error.service == "ssh"
        
        # Authorization error
        authz_error = AuthorizationError("Access denied", "/admin")
        assert authz_error.resource == "/admin"
        
        # Rate limit error
        rate_error = RateLimitError("Rate limited", 60.0)
        assert rate_error.retry_after == 60.0
        
        # Resource not found error
        not_found_error = ResourceNotFoundError("Resource not found", "file", "config.json")
        assert not_found_error.resource_type == "file"
        assert not_found_error.resource_id == "config.json"
    
    def test_error_context(self):
        """Test error context creation."""
        context = ErrorContext(
            operation="test_operation",
            module="test_module",
            function="test_function",
            request_id="req_123",
            user_id="user_456",
            target="192.168.1.1"
        )
        
        assert context.operation == "test_operation"
        assert context.module == "test_module"
        assert context.function == "test_function"
        assert context.request_id == "req_123"
        assert context.user_id == "user_456"
        assert context.target == "192.168.1.1"
        assert context.timestamp is not None
    
    def test_error_context_to_dict(self):
        """Test error context serialization."""
        context = ErrorContext(
            operation="test_operation",
            module="test_module",
            function="test_function"
        )
        
        context_dict = context.to_dict()
        assert context_dict["operation"] == "test_operation"
        assert context_dict["module"] == "test_module"
        assert context_dict["function"] == "test_function"
        assert "timestamp" in context_dict
    
    def test_error_handler(self):
        """Test error handler."""
        handler = ErrorHandler()
        
        # Test error handling
        error = SecurityToolkitError("Test error")
        context = ErrorContext("test", "test", "test")
        
        handler.handle_error(error, context)
        
        # Check error counts
        stats = handler.get_error_stats()
        assert stats["total_errors"] == 1
        assert stats["error_counts"]["SecurityToolkitError"] == 1
    
    def test_retry_strategy(self):
        """Test retry strategy."""
        strategy = RetryStrategy(max_retries=2, base_delay=0.1)
        
        # Test successful operation
        async def successful_operation():
            return "success"
        
        result = asyncio.run(strategy.execute(successful_operation))
        assert result == "success"
        
        # Test failing operation
        call_count = 0
        async def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = asyncio.run(strategy.execute(failing_operation))
        assert result == "success"
        assert call_count == 3
    
    def test_circuit_breaker(self):
        """Test circuit breaker."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        
        # Test successful operation
        async def successful_operation():
            return "success"
        
        result = asyncio.run(breaker.execute(successful_operation))
        assert result == "success"
        assert breaker.state == "CLOSED"
        
        # Test failing operation
        async def failing_operation():
            raise Exception("Failure")
        
        # First failure
        with pytest.raises(Exception):
            asyncio.run(breaker.execute(failing_operation))
        assert breaker.state == "CLOSED"
        
        # Second failure - circuit opens
        with pytest.raises(Exception):
            asyncio.run(breaker.execute(failing_operation))
        assert breaker.state == "OPEN"
        
        # Circuit should block subsequent calls
        with pytest.raises(SecurityToolkitError):
            asyncio.run(breaker.execute(successful_operation))
    
    def test_fallback_handler(self):
        """Test fallback handler."""
        async def primary_operation():
            raise Exception("Primary failed")
        
        async def fallback_operation():
            return "fallback success"
        
        handler = FallbackHandler(fallback_operation)
        result = asyncio.run(handler.execute(primary_operation))
        assert result == "fallback success"
    
    def test_error_recovery_manager(self):
        """Test error recovery manager."""
        manager = ErrorRecoveryManager()
        
        # Add strategies
        retry_strategy = RetryStrategy(max_retries=1, base_delay=0.1)
        manager.add_retry_strategy("retry", retry_strategy)
        
        async def test_operation():
            return "success"
        
        result = asyncio.run(manager.execute_with_recovery(test_operation, "retry"))
        assert result == "success"
    
    def test_utility_functions(self):
        """Test utility functions."""
        # Test format_error_message
        error = SecurityToolkitError("Test error", "TEST_ERROR")
        message = format_error_message(error)
        assert "[TEST_ERROR] Test error" in message
        
        # Test create_error_context
        context = create_error_context("test", "test", "test", request_id="123")
        assert context.operation == "test"
        assert context.request_id == "123"

class TestValidation:
    """Test suite for validation."""
    
    def test_validation_result(self):
        """Test validation result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        
        # Add error
        result.add_error("Test error")
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Test error" in result.errors
        
        # Add warning
        result.add_warning("Test warning")
        assert len(result.warnings) == 1
        assert "Test warning" in result.warnings
    
    def test_validation_context(self):
        """Test validation context."""
        context = ValidationContext(
            level=ValidationLevel.STRICT,
            mode=ValidationMode.ASYNC,
            strict_mode=True
        )
        
        assert context.level == ValidationLevel.STRICT
        assert context.mode == ValidationMode.ASYNC
        assert context.strict_mode is True
    
    def test_target_validator(self):
        """Test target validator."""
        validator = TargetValidator()
        
        # Valid IP
        result = validator.validate("192.168.1.1")
        assert result.is_valid is True
        assert result.metadata["type"] == "ip"
        
        # Valid domain
        result = validator.validate("example.com")
        assert result.is_valid is True
        assert result.metadata["type"] == "domain"
        
        # Valid URL
        result = validator.validate("https://example.com")
        assert result.is_valid is True
        assert result.metadata["type"] == "url"
        
        # Valid network
        result = validator.validate("192.168.1.0/24")
        assert result.is_valid is True
        assert result.metadata["type"] == "network"
        
        # Invalid target
        result = validator.validate("invalid@target")
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_port_validator(self):
        """Test port validator."""
        validator = PortValidator()
        
        # Valid port
        result = validator.validate(80)
        assert result.is_valid is True
        assert result.metadata["port"] == 80
        assert result.metadata["is_common"] is True
        
        # Invalid port
        result = validator.validate(70000)
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Port range validation
        result = validator.validate_range(80, 443)
        assert result.is_valid is True
        
        result = validator.validate_range(443, 80)
        assert result.is_valid is False
    
    def test_credential_validator(self):
        """Test credential validator."""
        validator = CredentialValidator()
        
        # Valid credentials dict
        creds = {"username": "admin", "password": "password123"}
        result = validator.validate(creds)
        assert result.is_valid is True
        assert result.metadata["username"] == "admin"
        assert result.metadata["password_length"] == 12
        
        # Valid credentials string
        creds_str = "admin:password123"
        result = validator.validate(creds_str)
        assert result.is_valid is True
        assert result.metadata["username"] == "admin"
        
        # Invalid credentials
        result = validator.validate("invalid")
        assert result.is_valid is False
    
    def test_payload_validator(self):
        """Test payload validator."""
        validator = PayloadValidator()
        
        # Valid payload dict
        payload = {
            "content": "test payload",
            "type": "test",
            "encoding": "utf-8"
        }
        result = validator.validate(payload)
        assert result.is_valid is True
        assert result.metadata["size"] > 0
        
        # Valid payload string
        result = validator.validate("test payload")
        assert result.is_valid is True
        
        # Payload with dangerous pattern
        dangerous_payload = "<script>alert('xss')</script>"
        result = validator.validate(dangerous_payload)
        assert result.is_valid is True
        assert len(result.warnings) > 0
    
    def test_config_validator(self):
        """Test config validator."""
        validator = ConfigValidator()
        
        # Add required field
        validator.add_required_field("timeout")
        validator.add_optional_field("retries")
        
        # Valid config
        config = {"timeout": 30}
        result = validator.validate(config)
        assert result.is_valid is True
        
        # Missing required field
        config = {"retries": 3}
        result = validator.validate(config)
        assert result.is_valid is False
    
    def test_network_validator(self):
        """Test network validator."""
        validator = NetworkValidator()
        
        # Valid network dict
        network = {
            "target": "192.168.1.1",
            "port": 80,
            "timeout": 30
        }
        result = validator.validate(network)
        assert result.is_valid is True
        
        # Valid network string
        result = validator.validate("192.168.1.1:80")
        assert result.is_valid is True
        
        # Invalid network
        result = validator.validate("invalid:network")
        assert result.is_valid is False
    
    def test_crypto_validator(self):
        """Test crypto validator."""
        validator = CryptoValidator()
        
        # Valid crypto params
        crypto = {
            "operation": "hash",
            "algorithm": "sha256",
            "data": "test data"
        }
        result = validator.validate(crypto)
        assert result.is_valid is True
        
        # Invalid operation
        crypto = {"operation": "invalid"}
        result = validator.validate(crypto)
        assert result.is_valid is False
    
    def test_validation_rule(self):
        """Test validation rule."""
        def is_positive(value):
            return isinstance(value, (int, float)) and value > 0
        
        rule = ValidationRule("positive", is_positive, "Value must be positive")
        
        assert rule.apply(5) is True
        assert rule.apply(-1) is False
        assert "positive" in rule.get_error_message(-1)
    
    def test_field_validator(self):
        """Test field validator."""
        def is_positive(value):
            return isinstance(value, (int, float)) and value > 0
        
        rule = ValidationRule("positive", is_positive, "Value must be positive")
        validator = FieldValidator("test_field", [rule])
        
        result = validator.validate(5)
        assert result.is_valid is True
        
        result = validator.validate(-1)
        assert result.is_valid is False
        assert "test_field" in result.errors[0]
    
    def test_custom_validator(self):
        """Test custom validator."""
        def custom_check(value):
            return isinstance(value, str) and len(value) > 5
        
        validator = CustomValidator("length_check", custom_check, "String too short")
        
        result = validator.validate("long string")
        assert result.is_valid is True
        
        result = validator.validate("short")
        assert result.is_valid is False
    
    def test_composite_validator(self):
        """Test composite validator."""
        target_validator = TargetValidator()
        port_validator = PortValidator()
        
        composite = CompositeValidator([target_validator, port_validator])
        
        # This should fail because it's not a valid target
        result = composite.validate("invalid")
        assert result.is_valid is False
    
    def test_validation_schema(self):
        """Test validation schema."""
        schema = ValidationSchema("test_schema")
        
        # Add field validator
        def is_positive(value):
            return isinstance(value, (int, float)) and value > 0
        
        rule = ValidationRule("positive", is_positive, "Value must be positive")
        field_validator = FieldValidator("timeout", [rule])
        schema.add_field_validator("timeout", field_validator)
        
        # Valid data
        data = {"timeout": 30}
        result = schema.validate(data)
        assert result.is_valid is True
        
        # Invalid data
        data = {"timeout": -1}
        result = schema.validate(data)
        assert result.is_valid is False
    
    def test_utility_functions(self):
        """Test validation utility functions."""
        # Test validate_target
        result = validate_target("192.168.1.1")
        assert result.is_valid is True
        
        result = validate_target("invalid")
        assert result.is_valid is False
        
        # Test validate_port
        result = validate_port(80)
        assert result.is_valid is True
        
        result = validate_port(70000)
        assert result.is_valid is False
        
        # Test validate_credentials
        result = validate_credentials({"username": "admin", "password": "pass"})
        assert result.is_valid is True
        
        # Test validate_payload
        result = validate_payload("test payload")
        assert result.is_valid is True
        
        # Test validate_config
        result = validate_config({"test": "value"})
        assert result.is_valid is True
        
        # Test validate_network_target
        result = validate_network_target("192.168.1.1:80")
        assert result.is_valid is True
        
        # Test validate_crypto_params
        result = validate_crypto_params({"operation": "hash", "algorithm": "sha256"})
        assert result.is_valid is True

class TestLogging:
    """Test suite for logging."""
    
    def test_log_config(self):
        """Test log configuration."""
        config = LogConfig(
            level=LogLevel.INFO,
            format=LogFormat.JSON,
            output_file="test.log",
            enable_console=True
        )
        
        assert config.level == LogLevel.INFO
        assert config.format == LogFormat.JSON
        assert config.output_file == "test.log"
        assert config.enable_console is True
    
    def test_log_context(self):
        """Test log context."""
        context = LogContext(
            operation="test_operation",
            module="test_module",
            function="test_function",
            request_id="req_123"
        )
        
        assert context.operation == "test_operation"
        assert context.module == "test_module"
        assert context.function == "test_function"
        assert context.request_id == "req_123"
        assert context.timestamp is not None
    
    def test_log_metadata(self):
        """Test log metadata."""
        metadata = LogMetadata(
            severity="high",
            category="security",
            tags=["test", "security"],
            source_ip="192.168.1.1"
        )
        
        assert metadata.severity == "high"
        assert metadata.category == "security"
        assert "test" in metadata.tags
        assert metadata.source_ip == "192.168.1.1"
    
    def test_security_logger(self):
        """Test security logger."""
        logger = SecurityLogger("test_logger")
        
        # Test basic logging
        logger.info("Test message")
        logger.warning("Test warning")
        logger.error("Test error")
        
        # Test with context
        context = LogContext("test", "test", "test")
        logger.info("Test with context", context)
        
        # Test with metadata
        metadata = LogMetadata(severity="high", category="test")
        logger.info("Test with metadata", metadata=metadata)
    
    def test_structured_logger(self):
        """Test structured logger."""
        logger = StructuredLogger("test_structured")
        
        # Test correlation ID
        logger.set_correlation_id("corr_123")
        assert logger.correlation_id == "corr_123"
        
        # Test session data
        logger.set_session_data("user_id", "user_123")
        assert logger.get_session_data("user_id") == "user_123"
        
        # Test operation logging
        context = logger.log_operation_start("test_op", "test", "test")
        assert context.operation == "test_op"
        
        logger.log_operation_end(context, success=True, duration=1.0)
        
        # Test exception logging
        try:
            raise ValueError("Test exception")
        except Exception as e:
            logger.log_exception(e, context)
    
    def test_log_filters(self):
        """Test log filters."""
        # Test basic filter
        filter_obj = LogFilter(
            include_levels=["ERROR", "CRITICAL"],
            exclude_modules=["test_module"]
        )
        
        # Test security filter
        security_filter = SecurityLogFilter()
        assert security_filter.include_levels == ["WARNING", "ERROR", "CRITICAL"]
    
    def test_utility_functions(self):
        """Test logging utility functions."""
        # Test setup_logging
        logger = setup_logging("test_setup")
        assert isinstance(logger, SecurityLogger)
        
        # Test get_logger
        logger = get_logger("test_get")
        assert isinstance(logger, SecurityLogger)
        
        # Test log_security_event
        log_security_event("test_event", "Test security event", "info")
        
        # Test log_performance_metrics
        log_performance_metrics("test_operation", 1.5)

class TestMonitoring:
    """Test suite for monitoring."""
    
    def test_performance_monitor(self):
        """Test performance monitor."""
        monitor = PerformanceMonitor()
        
        # Record metrics
        monitor.record_metric("test_counter", 1, MetricType.COUNTER)
        monitor.record_metric("test_gauge", 42.5, MetricType.GAUGE)
        monitor.record_metric("test_histogram", 1.0, MetricType.HISTOGRAM)
        monitor.record_metric("test_summary", 10.0, MetricType.SUMMARY)
        
        # Get metrics
        assert monitor.get_counter("test_counter") == 1
        assert monitor.get_gauge("test_gauge") == 42.5
        
        histogram_stats = monitor.get_histogram_stats("test_histogram")
        assert histogram_stats["count"] == 1
        assert histogram_stats["min"] == 1.0
        
        summary = monitor.get_summary("test_summary")
        assert summary["count"] == 1
        assert summary["sum"] == 10.0
    
    def test_health_checker(self):
        """Test health checker."""
        checker = HealthChecker()
        
        # Add health check
        async def test_health_check():
            return True
        
        checker.add_health_check("test_check", test_health_check)
        
        # Run health check
        results = asyncio.run(checker.run_all_health_checks())
        assert "test_check" in results
        assert results["test_check"].status == "healthy"
        
        # Test failing health check
        async def failing_health_check():
            raise Exception("Health check failed")
        
        checker.add_health_check("failing_check", failing_health_check)
        results = asyncio.run(checker.run_all_health_checks())
        assert results["failing_check"].status == "unhealthy"
    
    def test_metrics_collector(self):
        """Test metrics collector."""
        collector = MetricsCollector()
        
        # Test metrics collection
        metrics = asyncio.run(collector.collect_system_metrics())
        assert "cpu" in metrics
        assert "memory" in metrics
        assert "disk" in metrics
    
    def test_alert_manager(self):
        """Test alert manager."""
        manager = AlertManager()
        
        # Test alert handler
        alerts_sent = []
        def test_handler(alert):
            alerts_sent.append(alert)
        
        manager.add_alert_handler(AlertChannel.LOG, test_handler)
        
        # Create alert
        alert = manager.create_alert(
            "Test Alert",
            "This is a test alert",
            AlertLevel.INFO
        )
        
        assert alert.title == "Test Alert"
        assert alert.message == "This is a test alert"
        assert alert.level == AlertLevel.INFO
        assert len(alerts_sent) == 1
        
        # Test alert rules
        def test_condition():
            return True
        
        manager.add_alert_rule(
            "test_rule",
            test_condition,
            AlertLevel.WARNING,
            [AlertChannel.LOG]
        )
        
        # Get alerts
        alerts = manager.get_alerts(level=AlertLevel.INFO)
        assert len(alerts) == 1
    
    def test_decorators(self):
        """Test monitoring decorators."""
        # Test track_performance
        @track_performance("test_operation")
        async def test_operation():
            await asyncio.sleep(0.1)
            return "success"
        
        result = asyncio.run(test_operation())
        assert result == "success"
        
        # Test monitor_operation
        @monitor_operation("monitored_operation")
        async def monitored_operation():
            await asyncio.sleep(0.1)
            return "success"
        
        result = asyncio.run(monitored_operation())
        assert result == "success"
    
    def test_utility_functions(self):
        """Test monitoring utility functions."""
        # Test send_alert
        alert = send_alert("Test Alert", "Test message", AlertLevel.INFO)
        assert alert.title == "Test Alert"
        assert alert.message == "Test message"
        assert alert.level == AlertLevel.INFO

class TestIntegration:
    """Integration tests for core components."""
    
    def test_error_handling_with_validation(self):
        """Test error handling with validation."""
        # Create error handler
        handler = ErrorHandler()
        
        # Test validation error
        try:
            result = validate_target("invalid@target")
            if not result.is_valid:
                raise TargetValidationError("Invalid target", "invalid@target")
        except TargetValidationError as e:
            context = create_error_context("validation", "test", "test")
            handler.handle_error(e, context)
        
        # Check error stats
        stats = handler.get_error_stats()
        assert stats["total_errors"] == 1
    
    def test_logging_with_monitoring(self):
        """Test logging with monitoring."""
        # Setup logger
        logger = SecurityLogger("integration_test")
        
        # Setup monitor
        monitor = PerformanceMonitor()
        
        # Log performance metric
        monitor.record_metric("test_operation", 1.5, MetricType.HISTOGRAM)
        logger.performance_metric("test_operation", 1.5)
        
        # Check metrics
        stats = monitor.get_histogram_stats("test_operation")
        assert stats["count"] == 1
        assert stats["mean"] == 1.5
    
    def test_validation_with_logging(self):
        """Test validation with logging."""
        # Setup logger
        logger = SecurityLogger("validation_test")
        
        # Test validation with logging
        context = LogContext("validation", "test", "test")
        
        result = validate_target("192.168.1.1")
        if result.is_valid:
            logger.info("Target validation successful", context)
        else:
            logger.error("Target validation failed", context)
        
        assert result.is_valid is True
    
    def test_monitoring_with_alerting(self):
        """Test monitoring with alerting."""
        # Setup monitor
        monitor = PerformanceMonitor()
        
        # Setup alert manager
        manager = AlertManager()
        
        # Record slow operation
        monitor.record_metric("slow_operation", 10.0, MetricType.HISTOGRAM)
        
        # Check if alert should be sent
        stats = monitor.get_histogram_stats("slow_operation")
        if stats["mean"] > 5.0:
            alert = manager.create_alert(
                "Slow Operation Detected",
                f"Operation took {stats['mean']:.2f} seconds",
                AlertLevel.WARNING
            )
            assert alert.level == AlertLevel.WARNING
    
    def test_comprehensive_error_handling(self):
        """Test comprehensive error handling."""
        # Setup error recovery manager
        manager = ErrorRecoveryManager()
        
        # Add retry strategy
        retry_strategy = RetryStrategy(max_retries=2, base_delay=0.1)
        manager.add_retry_strategy("retry", retry_strategy)
        
        # Setup logger
        logger = SecurityLogger("comprehensive_test")
        
        # Test operation with error handling
        call_count = 0
        async def test_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("Temporary network error", "192.168.1.1", 80)
            return "success"
        
        try:
            result = asyncio.run(manager.execute_with_recovery(test_operation, "retry"))
            assert result == "success"
            logger.info("Operation completed successfully")
        except Exception as e:
            logger.error(f"Operation failed: {e}")
            raise
        
        assert call_count == 3 