"""
Tests for Guard Clauses

Tests error and edge-case checking with guard clauses.
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock

from ..core import (
    # Guard Clause Types
    GuardType, GuardSeverity,
    
    # Guard Clause Decorators
    guard_against_none, guard_against_empty, guard_against_invalid_type,
    guard_against_invalid_range, guard_against_invalid_format,
    guard_against_timeout, guard_against_rate_limit,
    
    # Guard Clause Utilities
    guard_target, guard_port, guard_credentials, guard_payload,
    guard_config, guard_network_params, guard_crypto_params,
    
    # Composite Guard Clauses
    guard_scan_parameters, guard_attack_parameters, guard_report_parameters,
    
    # Guard Clause Context
    GuardContext, apply_guards, guard_function_signature,
    
    # Error Handling
    ValidationError, SecurityToolkitError, TimeoutError
)

class TestGuardClauseDecorators:
    """Test suite for guard clause decorators."""
    
    def test_guard_against_none(self):
        """Test guard against None values."""
        @guard_against_none("target")
        def test_function(target: str, port: int):
            return f"Target: {target}, Port: {port}"
        
        # Valid call
        result = test_function("192.168.1.1", 80)
        assert result == "Target: 192.168.1.1, Port: 80"
        
        # Invalid call with None
        with pytest.raises(ValidationError) as exc_info:
            test_function(None, 80)
        assert "cannot be None" in str(exc_info.value)
        assert exc_info.value.field == "target"
    
    def test_guard_against_empty(self):
        """Test guard against empty values."""
        @guard_against_empty("payload")
        def test_function(payload: str):
            return f"Payload: {payload}"
        
        # Valid call
        result = test_function("test payload")
        assert result == "Payload: test payload"
        
        # Invalid calls
        with pytest.raises(ValidationError):
            test_function("")
        
        with pytest.raises(ValidationError):
            test_function("   ")
        
        with pytest.raises(ValidationError):
            test_function([])
        
        with pytest.raises(ValidationError):
            test_function({})
    
    def test_guard_against_invalid_type(self):
        """Test guard against invalid types."""
        @guard_against_invalid_type("port", int)
        def test_function(port: int):
            return f"Port: {port}"
        
        # Valid call
        result = test_function(80)
        assert result == "Port: 80"
        
        # Invalid call
        with pytest.raises(ValidationError) as exc_info:
            test_function("80")
        assert "must be of type int" in str(exc_info.value)
        assert exc_info.value.field == "port"
        assert exc_info.value.value == "80"
    
    def test_guard_against_invalid_range(self):
        """Test guard against invalid ranges."""
        @guard_against_invalid_range("timeout", min_value=1.0, max_value=300.0)
        def test_function(timeout: float):
            return f"Timeout: {timeout}"
        
        # Valid calls
        result = test_function(30.0)
        assert result == "Timeout: 30.0"
        
        result = test_function(1.0)
        assert result == "Timeout: 1.0"
        
        result = test_function(300.0)
        assert result == "Timeout: 300.0"
        
        # Invalid calls
        with pytest.raises(ValidationError):
            test_function(0.5)
        
        with pytest.raises(ValidationError):
            test_function(500.0)
        
        with pytest.raises(ValidationError):
            test_function("invalid")
    
    def test_guard_against_invalid_format(self):
        """Test guard against invalid format."""
        @guard_against_invalid_format("email", r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        def test_function(email: str):
            return f"Email: {email}"
        
        # Valid call
        result = test_function("test@example.com")
        assert result == "Email: test@example.com"
        
        # Invalid call
        with pytest.raises(ValidationError) as exc_info:
            test_function("invalid-email")
        assert "invalid format" in str(exc_info.value)
        assert exc_info.value.field == "email"
    
    @pytest.mark.asyncio
    async def test_guard_against_timeout(self):
        """Test guard against timeout."""
        @guard_against_timeout("timeout", default_timeout=30.0)
        async def test_function(timeout: float = 30.0):
            await asyncio.sleep(0.1)
            return "Success"
        
        # Valid call
        result = await test_function(1.0)
        assert result == "Success"
        
        # Invalid timeout
        with pytest.raises(ValidationError):
            await test_function(-1.0)
        
        # Timeout exceeded
        with pytest.raises(TimeoutError):
            await test_function(0.01)
    
    def test_guard_against_rate_limit(self):
        """Test guard against rate limiting."""
        @guard_against_rate_limit(max_calls=2, time_window=1.0)
        def test_function():
            return "Success"
        
        # Valid calls
        result1 = test_function()
        result2 = test_function()
        assert result1 == "Success"
        assert result2 == "Success"
        
        # Rate limit exceeded
        with pytest.raises(SecurityToolkitError) as exc_info:
            test_function()
        assert "Rate limit exceeded" in str(exc_info.value)
        assert exc_info.value.error_code == "RATE_LIMIT_ERROR"

class TestGuardUtilities:
    """Test suite for guard utility functions."""
    
    def test_guard_target(self):
        """Test target validation."""
        # Valid targets
        guard_target("192.168.1.1")
        guard_target("example.com")
        guard_target("https://api.example.com")
        guard_target("192.168.1.0/24")
        
        # Invalid targets
        with pytest.raises(ValidationError):
            guard_target(None)
        
        with pytest.raises(ValidationError):
            guard_target("")
        
        with pytest.raises(ValidationError):
            guard_target("invalid@target")
        
        with pytest.raises(ValidationError):
            guard_target(123)
    
    def test_guard_port(self):
        """Test port validation."""
        # Valid ports
        guard_port(80)
        guard_port(443)
        guard_port(22)
        guard_port(65535)
        
        # Invalid ports
        with pytest.raises(ValidationError):
            guard_port(None)
        
        with pytest.raises(ValidationError):
            guard_port(0)
        
        with pytest.raises(ValidationError):
            guard_port(70000)
        
        with pytest.raises(ValidationError):
            guard_port(-1)
        
        with pytest.raises(ValidationError):
            guard_port("80")
    
    def test_guard_credentials(self):
        """Test credential validation."""
        # Valid credentials dict
        guard_credentials({"username": "admin", "password": "password123"})
        
        # Valid credentials string
        guard_credentials("admin:password123")
        
        # Invalid credentials
        with pytest.raises(ValidationError):
            guard_credentials(None)
        
        with pytest.raises(ValidationError):
            guard_credentials({"username": "admin"})  # Missing password
        
        with pytest.raises(ValidationError):
            guard_credentials({"username": "", "password": "pass"})  # Empty username
        
        with pytest.raises(ValidationError):
            guard_credentials("invalid")  # No colon
        
        with pytest.raises(ValidationError):
            guard_credentials(":password")  # Empty username
        
        with pytest.raises(ValidationError):
            guard_credentials("username:")  # Empty password
    
    def test_guard_payload(self):
        """Test payload validation."""
        # Valid payload dict
        guard_payload({"content": "test payload", "type": "test"})
        
        # Valid payload string
        guard_payload("test payload")
        
        # Invalid payload
        with pytest.raises(ValidationError):
            guard_payload(None)
        
        with pytest.raises(ValidationError):
            guard_payload({"type": "test"})  # Missing content
        
        with pytest.raises(ValidationError):
            guard_payload({"content": "", "type": "test"})  # Empty content
        
        with pytest.raises(ValidationError):
            guard_payload("")  # Empty string
        
        with pytest.raises(ValidationError):
            guard_payload("x" * 2000000)  # Too large
    
    def test_guard_config(self):
        """Test configuration validation."""
        # Valid config
        guard_config({"timeout": 30, "retries": 3})
        
        # Invalid config
        with pytest.raises(ValidationError):
            guard_config(None)
        
        with pytest.raises(ValidationError):
            guard_config("invalid")
        
        with pytest.raises(ValidationError):
            guard_config({"timeout": 30})  # Missing retries
        
        with pytest.raises(ValidationError):
            guard_config({"timeout": -1, "retries": 3})  # Invalid timeout
        
        with pytest.raises(ValidationError):
            guard_config({"timeout": 30, "retries": "invalid"})  # Invalid retries
    
    def test_guard_network_params(self):
        """Test network parameters validation."""
        # Valid parameters
        guard_network_params("192.168.1.1")
        guard_network_params("192.168.1.1", 80)
        guard_network_params("192.168.1.1", 80, 30.0)
        
        # Invalid parameters
        with pytest.raises(ValidationError):
            guard_network_params("invalid@target", 80, 30.0)
        
        with pytest.raises(ValidationError):
            guard_network_params("192.168.1.1", 70000, 30.0)
        
        with pytest.raises(ValidationError):
            guard_network_params("192.168.1.1", 80, -1.0)
    
    def test_guard_crypto_params(self):
        """Test cryptographic parameters validation."""
        # Valid parameters
        guard_crypto_params("hash")
        guard_crypto_params("hash", "sha256")
        guard_crypto_params("hash", "sha256", "test data")
        
        # Invalid parameters
        with pytest.raises(ValidationError):
            guard_crypto_params(None)
        
        with pytest.raises(ValidationError):
            guard_crypto_params("invalid_operation")
        
        with pytest.raises(ValidationError):
            guard_crypto_params("hash", "invalid_algorithm")
        
        with pytest.raises(ValidationError):
            guard_crypto_params("hash", "sha256", "")

class TestCompositeGuardClauses:
    """Test suite for composite guard clauses."""
    
    def test_guard_scan_parameters(self):
        """Test scan parameters validation."""
        # Valid parameters
        guard_scan_parameters("192.168.1.1", [80, 443], "port_scan", {"timeout": 30, "retries": 3})
        
        # Invalid parameters
        with pytest.raises(ValidationError):
            guard_scan_parameters("invalid@target", [80, 443], "port_scan", {"timeout": 30, "retries": 3})
        
        with pytest.raises(ValidationError):
            guard_scan_parameters("192.168.1.1", [70000], "port_scan", {"timeout": 30, "retries": 3})
        
        with pytest.raises(ValidationError):
            guard_scan_parameters("192.168.1.1", [80, 443], "invalid_scan_type", {"timeout": 30, "retries": 3})
        
        with pytest.raises(ValidationError):
            guard_scan_parameters("192.168.1.1", [80, 443], "port_scan", {"timeout": -1, "retries": 3})
    
    def test_guard_attack_parameters(self):
        """Test attack parameters validation."""
        # Valid parameters
        guard_attack_parameters("192.168.1.1", "brute_force", {"content": "test"}, {"username": "admin", "password": "pass"})
        
        # Invalid parameters
        with pytest.raises(ValidationError):
            guard_attack_parameters("invalid@target", "brute_force", {"content": "test"}, {"username": "admin", "password": "pass"})
        
        with pytest.raises(ValidationError):
            guard_attack_parameters("192.168.1.1", "invalid_attack", {"content": "test"}, {"username": "admin", "password": "pass"})
        
        with pytest.raises(ValidationError):
            guard_attack_parameters("192.168.1.1", "brute_force", "", {"username": "admin", "password": "pass"})
        
        with pytest.raises(ValidationError):
            guard_attack_parameters("192.168.1.1", "brute_force", {"content": "test"}, "invalid_credentials")
    
    def test_guard_report_parameters(self):
        """Test report parameters validation."""
        # Valid parameters
        guard_report_parameters("html", "detailed", ["executive_summary", "findings"])
        
        # Invalid parameters
        with pytest.raises(ValidationError):
            guard_report_parameters("invalid_format", "detailed", ["executive_summary", "findings"])
        
        with pytest.raises(ValidationError):
            guard_report_parameters("html", "invalid_level", ["executive_summary", "findings"])
        
        with pytest.raises(ValidationError):
            guard_report_parameters("html", "detailed", ["invalid_section"])

class TestGuardContext:
    """Test suite for guard context manager."""
    
    def test_guard_context_basic(self):
        """Test basic guard context usage."""
        with GuardContext("test_operation", "test_module", "test_function") as guard:
            # Apply guards
            guard.apply_guard(guard_target, "192.168.1.1")
            guard.apply_guard(guard_port, 80)
            
            # Should not raise any exceptions
            assert len(guard.guards_applied) == 2
    
    def test_guard_context_with_error(self):
        """Test guard context with error handling."""
        with pytest.raises(ValidationError):
            with GuardContext("test_operation", "test_module", "test_function") as guard:
                guard.apply_guard(guard_target, "invalid@target")
    
    def test_guard_context_error_context(self):
        """Test guard context adds error context."""
        try:
            with GuardContext("test_operation", "test_module", "test_function") as guard:
                guard.apply_guard(guard_target, "invalid@target")
        except ValidationError as e:
            assert hasattr(e, 'context')
            assert e.context["operation"] == "test_operation"
            assert e.context["module"] == "test_module"
            assert e.context["function"] == "test_function"
            assert e.context["guard"] == "guard_target"

class TestApplyGuards:
    """Test suite for apply_guards decorator."""
    
    def test_apply_guards_sync(self):
        """Test apply_guards with sync function."""
        @apply_guards(guard_target, guard_port)
        def test_function(target: str, port: int):
            return f"Target: {target}, Port: {port}"
        
        # Valid call
        result = test_function("192.168.1.1", 80)
        assert result == "Target: 192.168.1.1, Port: 80"
        
        # Invalid call
        with pytest.raises(ValidationError):
            test_function("invalid@target", 80)
    
    @pytest.mark.asyncio
    async def test_apply_guards_async(self):
        """Test apply_guards with async function."""
        @apply_guards(guard_target, guard_port)
        async def test_function(target: str, port: int):
            await asyncio.sleep(0.1)
            return f"Target: {target}, Port: {port}"
        
        # Valid call
        result = await test_function("192.168.1.1", 80)
        assert result == "Target: 192.168.1.1, Port: 80"
        
        # Invalid call
        with pytest.raises(ValidationError):
            await test_function("invalid@target", 80)

class TestFunctionSignatureGuards:
    """Test suite for function signature guards."""
    
    def test_guard_function_signature_sync(self):
        """Test function signature guards with sync function."""
        @guard_function_signature
        def test_function(data: str, count: int, enabled: bool = True):
            return f"Data: {data}, Count: {count}, Enabled: {enabled}"
        
        # Valid call
        result = test_function("test", 5, True)
        assert result == "Data: test, Count: 5, Enabled: True"
        
        # Invalid calls
        with pytest.raises(ValidationError):
            test_function(123, 5, True)  # Wrong type for data
        
        with pytest.raises(ValidationError):
            test_function("test", "5", True)  # Wrong type for count
        
        with pytest.raises(ValidationError):
            test_function("test", 5, "not_bool")  # Wrong type for enabled
    
    @pytest.mark.asyncio
    async def test_guard_function_signature_async(self):
        """Test function signature guards with async function."""
        @guard_function_signature
        async def test_function(data: str, timeout: float):
            await asyncio.sleep(0.1)
            return f"Data: {data}, Timeout: {timeout}"
        
        # Valid call
        result = await test_function("test", 30.0)
        assert result == "Data: test, Timeout: 30.0"
        
        # Invalid call
        with pytest.raises(ValidationError):
            await test_function(123, 30.0)  # Wrong type for data

class TestGuardClauseIntegration:
    """Integration tests for guard clauses."""
    
    def test_multiple_guards_integration(self):
        """Test integration of multiple guard types."""
        @guard_against_none("target")
        @guard_against_invalid_type("port", int)
        @guard_against_invalid_range("timeout", 1.0, 300.0)
        def scan_target(target: str, port: int, timeout: float):
            guard_target(target)
            guard_port(port)
            return f"Scanning {target}:{port} with timeout {timeout}"
        
        # Valid call
        result = scan_target("192.168.1.1", 80, 30.0)
        assert result == "Scanning 192.168.1.1:80 with timeout 30.0"
        
        # Multiple validation errors
        with pytest.raises(ValidationError):
            scan_target(None, "80", -1.0)
    
    def test_guard_clauses_with_error_recovery(self):
        """Test guard clauses with error recovery."""
        from ..core import RetryStrategy
        
        @guard_against_none("target")
        @guard_against_invalid_type("port", int)
        def scan_with_retry(target: str, port: int):
            guard_target(target)
            guard_port(port)
            return f"Scanned {target}:{port}"
        
        retry_strategy = RetryStrategy(max_retries=2, base_delay=0.1)
        
        # Valid call
        result = retry_strategy.execute(scan_with_retry, "192.168.1.1", 80)
        assert result == "Scanned 192.168.1.1:80"
        
        # Invalid call should fail immediately (no retry for validation errors)
        with pytest.raises(ValidationError):
            retry_strategy.execute(scan_with_retry, None, 80)
    
    def test_guard_clauses_with_logging(self):
        """Test guard clauses with logging integration."""
        from ..core import SecurityLogger, LogContext
        
        logger = SecurityLogger("test_logger")
        
        @guard_against_none("target")
        def scan_with_logging(target: str):
            guard_target(target)
            context = LogContext("scan", "test", "scan_with_logging")
            logger.info(f"Scanning target: {target}", context)
            return f"Scanned {target}"
        
        # Valid call
        result = scan_with_logging("192.168.1.1")
        assert result == "Scanned 192.168.1.1"
        
        # Invalid call
        with pytest.raises(ValidationError):
            scan_with_logging(None)
    
    def test_guard_clauses_with_monitoring(self):
        """Test guard clauses with monitoring integration."""
        from ..core import PerformanceMonitor, MetricType
        
        monitor = PerformanceMonitor()
        
        @guard_against_none("target")
        def scan_with_monitoring(target: str):
            guard_target(target)
            monitor.record_metric("scan_attempts", 1, MetricType.COUNTER)
            return f"Scanned {target}"
        
        # Valid call
        result = scan_with_monitoring("192.168.1.1")
        assert result == "Scanned 192.168.1.1"
        assert monitor.get_counter("scan_attempts") == 1
        
        # Invalid call
        with pytest.raises(ValidationError):
            scan_with_monitoring(None)
        # Should not increment counter for validation errors
        assert monitor.get_counter("scan_attempts") == 1

class TestGuardClauseEdgeCases:
    """Test edge cases for guard clauses."""
    
    def test_guard_with_complex_types(self):
        """Test guards with complex data types."""
        @guard_against_empty("data")
        def process_complex_data(data: dict):
            return f"Processed {len(data)} items"
        
        # Valid complex data
        result = process_complex_data({"key1": "value1", "key2": "value2"})
        assert result == "Processed 2 items"
        
        # Invalid complex data
        with pytest.raises(ValidationError):
            process_complex_data({})
        
        with pytest.raises(ValidationError):
            process_complex_data([])
    
    def test_guard_with_nested_validation(self):
        """Test guards with nested validation."""
        def validate_nested_config(config: dict):
            if "network" not in config:
                raise ValidationError("Missing network config")
            
            network = config["network"]
            guard_target(network.get("target"))
            guard_port(network.get("port"))
        
        @apply_guards(validate_nested_config)
        def scan_with_nested_config(config: dict):
            return f"Scanning {config['network']['target']}:{config['network']['port']}"
        
        # Valid nested config
        valid_config = {"network": {"target": "192.168.1.1", "port": 80}}
        result = scan_with_nested_config(valid_config)
        assert result == "Scanning 192.168.1.1:80"
        
        # Invalid nested config
        invalid_config = {"network": {"target": "invalid@target", "port": 80}}
        with pytest.raises(ValidationError):
            scan_with_nested_config(invalid_config)
    
    def test_guard_performance(self):
        """Test guard clause performance."""
        import time
        
        @guard_against_none("target")
        @guard_against_invalid_type("port", int)
        @guard_against_invalid_range("timeout", 1.0, 300.0)
        def performance_test(target: str, port: int, timeout: float):
            return f"Test: {target}:{port} ({timeout}s)"
        
        # Measure performance
        start_time = time.time()
        for _ in range(1000):
            performance_test("192.168.1.1", 80, 30.0)
        end_time = time.time()
        
        # Should complete quickly (less than 1 second for 1000 calls)
        assert end_time - start_time < 1.0
    
    def test_guard_memory_usage(self):
        """Test guard clause memory usage."""
        import sys
        
        @guard_against_none("data")
        def memory_test(data: str):
            return f"Data: {data}"
        
        # Measure memory usage
        initial_memory = sys.getsizeof(memory_test)
        
        # Create many instances
        functions = [memory_test for _ in range(1000)]
        
        # Memory usage should be reasonable
        total_memory = sum(sys.getsizeof(f) for f in functions)
        assert total_memory < 1000000  # Less than 1MB

class TestGuardClauseBestPractices:
    """Test best practices for guard clauses."""
    
    def test_guard_order_matters(self):
        """Test that guard order affects error messages."""
        @guard_against_none("target")
        @guard_against_invalid_type("target", str)
        def test_order(target: str):
            return f"Target: {target}"
        
        # Should fail on None check first
        with pytest.raises(ValidationError) as exc_info:
            test_order(None)
        assert "cannot be None" in str(exc_info.value)
    
    def test_guard_specificity(self):
        """Test guard clause specificity."""
        @guard_against_invalid_range("port", 1, 65535)
        @guard_against_invalid_type("port", int)
        def test_specificity(port: int):
            return f"Port: {port}"
        
        # Should fail on type check first (more specific)
        with pytest.raises(ValidationError) as exc_info:
            test_specificity("invalid")
        assert "must be of type int" in str(exc_info.value)
    
    def test_guard_error_messages(self):
        """Test guard clause error messages."""
        @guard_against_none("target", "Target parameter is required")
        def test_error_message(target: str):
            return f"Target: {target}"
        
        with pytest.raises(ValidationError) as exc_info:
            test_error_message(None)
        assert "Target parameter is required" in str(exc_info.value)
    
    def test_guard_context_preservation(self):
        """Test that guard context is preserved."""
        @guard_against_none("target")
        def test_context(target: str):
            guard_target(target)
            return f"Target: {target}"
        
        with pytest.raises(ValidationError) as exc_info:
            test_context("invalid@target")
        
        # Should have context from both decorator and utility
        assert exc_info.value.field == "target" 