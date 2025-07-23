"""
Core Examples

Demonstrates error handling, validation, logging, and monitoring functionality.
"""

import asyncio
import time
from datetime import datetime, timedelta

from ..core import (
    # Error Handling
    SecurityToolkitError, ValidationError, NetworkError, CryptoError,
    TargetValidationError, PortValidationError, TimeoutError,
    ErrorHandler, ErrorContext, RetryStrategy, CircuitBreaker,
    handle_security_error, format_error_message, create_error_context,
    
    # Validation
    TargetValidator, PortValidator, CredentialValidator, PayloadValidator,
    ValidationResult, ValidationContext, ValidationLevel,
    validate_target, validate_port, validate_credentials, validate_payload,
    
    # Logging
    SecurityLogger, LogConfig, LogContext, LogMetadata, StructuredLogger,
    setup_logging, get_logger, log_security_event, log_performance_metrics,
    
    # Monitoring
    PerformanceMonitor, HealthChecker, MetricsCollector, AlertManager,
    MetricType, AlertLevel, AlertChannel, track_performance, send_alert
)

def demonstrate_error_handling():
    """Demonstrate error handling system."""
    print("🚨 Error Handling Examples")
    print("-" * 30)
    
    # Create error handler
    handler = ErrorHandler()
    
    # Example 1: Basic error handling
    try:
        raise SecurityToolkitError("Test error", "TEST_ERROR")
    except SecurityToolkitError as e:
        context = create_error_context("test_operation", "test_module", "test_function")
        handler.handle_error(e, context)
        print(f"Handled error: {format_error_message(e)}")
    
    # Example 2: Validation error
    try:
        raise TargetValidationError("Invalid target format", "invalid@target")
    except TargetValidationError as e:
        context = create_error_context("validation", "validator", "validate_target")
        handler.handle_error(e, context)
        print(f"Validation error: {e.target}")
    
    # Example 3: Network error
    try:
        raise NetworkError("Connection timeout", "192.168.1.1", 80)
    except NetworkError as e:
        context = create_error_context("network_scan", "scanner", "scan_port")
        handler.handle_error(e, context)
        print(f"Network error: {e.target}:{e.port}")
    
    # Example 4: Crypto error
    try:
        raise CryptoError("Encryption failed", "encrypt", "AES-256")
    except CryptoError as e:
        context = create_error_context("crypto", "crypto_utils", "encrypt_data")
        handler.handle_error(e, context)
        print(f"Crypto error: {e.operation} with {e.algorithm}")
    
    # Get error statistics
    stats = handler.get_error_stats()
    print(f"\nError Statistics:")
    print(f"  Total errors: {stats['total_errors']}")
    print(f"  Error counts: {stats['error_counts']}")
    
    return handler

def demonstrate_retry_strategy():
    """Demonstrate retry strategy."""
    print("\n🔄 Retry Strategy Examples")
    print("-" * 30)
    
    # Create retry strategy
    retry_strategy = RetryStrategy(max_retries=3, base_delay=0.1)
    
    # Example 1: Successful operation
    async def successful_operation():
        return "Operation completed successfully"
    
    result = asyncio.run(retry_strategy.execute(successful_operation))
    print(f"Successful operation: {result}")
    
    # Example 2: Operation that fails initially then succeeds
    call_count = 0
    async def failing_then_successful():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise NetworkError("Temporary network issue", "192.168.1.1", 80)
        return "Operation succeeded after retries"
    
    result = asyncio.run(retry_strategy.execute(failing_then_successful))
    print(f"Retry operation: {result}")
    print(f"Attempts made: {call_count}")
    
    # Example 3: Operation that always fails
    async def always_failing():
        raise TimeoutError("Operation timeout", 5.0, "test_operation")
    
    try:
        asyncio.run(retry_strategy.execute(always_failing))
    except TimeoutError as e:
        print(f"Operation failed after retries: {e.message}")
    
    return retry_strategy

def demonstrate_circuit_breaker():
    """Demonstrate circuit breaker pattern."""
    print("\n⚡ Circuit Breaker Examples")
    print("-" * 30)
    
    # Create circuit breaker
    circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1.0)
    
    # Example 1: Successful operation
    async def successful_operation():
        return "Success"
    
    result = asyncio.run(circuit_breaker.execute(successful_operation))
    print(f"Circuit breaker state: {circuit_breaker.state}")
    print(f"Operation result: {result}")
    
    # Example 2: Failing operation that opens circuit
    async def failing_operation():
        raise NetworkError("Service unavailable", "api.example.com", 443)
    
    # First failure
    try:
        asyncio.run(circuit_breaker.execute(failing_operation))
    except NetworkError:
        print(f"First failure - Circuit state: {circuit_breaker.state}")
    
    # Second failure - circuit opens
    try:
        asyncio.run(circuit_breaker.execute(failing_operation))
    except NetworkError:
        print(f"Second failure - Circuit state: {circuit_breaker.state}")
    
    # Circuit should now be open
    try:
        asyncio.run(circuit_breaker.execute(successful_operation))
    except SecurityToolkitError as e:
        print(f"Circuit is open: {e.message}")
    
    # Wait for recovery timeout
    print("Waiting for circuit to recover...")
    await asyncio.sleep(1.1)
    
    # Circuit should be half-open now
    result = asyncio.run(circuit_breaker.execute(successful_operation))
    print(f"After recovery - Circuit state: {circuit_breaker.state}")
    print(f"Operation result: {result}")
    
    return circuit_breaker

def demonstrate_validation():
    """Demonstrate validation system."""
    print("\n✅ Validation Examples")
    print("-" * 30)
    
    # Example 1: Target validation
    print("Target Validation:")
    targets = ["192.168.1.1", "example.com", "https://api.example.com", "invalid@target"]
    
    for target in targets:
        result = validate_target(target)
        status = "✅" if result.is_valid else "❌"
        print(f"  {status} {target}: {result.is_valid}")
        if not result.is_valid:
            print(f"    Errors: {result.errors}")
    
    # Example 2: Port validation
    print("\nPort Validation:")
    ports = [80, 443, 22, 70000, -1]
    
    for port in ports:
        result = validate_port(port)
        status = "✅" if result.is_valid else "❌"
        print(f"  {status} Port {port}: {result.is_valid}")
        if not result.is_valid:
            print(f"    Errors: {result.errors}")
    
    # Example 3: Credential validation
    print("\nCredential Validation:")
    credentials = [
        {"username": "admin", "password": "password123"},
        {"username": "", "password": "password123"},
        "admin:password123",
        "invalid_credentials"
    ]
    
    for creds in credentials:
        result = validate_credentials(creds)
        status = "✅" if result.is_valid else "❌"
        print(f"  {status} {creds}: {result.is_valid}")
        if not result.is_valid:
            print(f"    Errors: {result.errors}")
    
    # Example 4: Payload validation
    print("\nPayload Validation:")
    payloads = [
        {"content": "normal payload", "type": "test"},
        {"content": "<script>alert('xss')</script>", "type": "xss"},
        "simple string payload",
        "x" * 2000000  # Very large payload
    ]
    
    for payload in payloads:
        result = validate_payload(payload)
        status = "✅" if result.is_valid else "❌"
        print(f"  {status} {type(payload).__name__}: {result.is_valid}")
        if result.warnings:
            print(f"    Warnings: {result.warnings}")
    
    # Example 5: Custom validation context
    print("\nCustom Validation Context:")
    context = ValidationContext(
        level=ValidationLevel.STRICT,
        mode=ValidationMode.SYNC,
        strict_mode=True
    )
    
    validator = TargetValidator(context)
    result = validator.validate("192.168.1.1")
    print(f"  Strict validation result: {result.is_valid}")
    print(f"  Metadata: {result.metadata}")
    
    return {
        "targets": targets,
        "ports": ports,
        "credentials": credentials,
        "payloads": payloads
    }

def demonstrate_logging():
    """Demonstrate logging system."""
    print("\n📝 Logging Examples")
    print("-" * 30)
    
    # Setup logging
    config = LogConfig(
        level=LogLevel.INFO,
        format=LogFormat.STRUCTURED,
        enable_console=True,
        enable_file=False
    )
    
    logger = SecurityLogger("example_logger", config)
    
    # Example 1: Basic logging
    print("Basic Logging:")
    logger.info("Application started")
    logger.warning("Configuration file not found, using defaults")
    logger.error("Failed to connect to database")
    
    # Example 2: Logging with context
    print("\nLogging with Context:")
    context = LogContext(
        operation="port_scan",
        module="scanner",
        function="scan_target",
        request_id="req_123",
        target="192.168.1.1"
    )
    
    logger.info("Starting port scan", context)
    logger.info("Port scan completed", context)
    
    # Example 3: Logging with metadata
    print("\nLogging with Metadata:")
    metadata = LogMetadata(
        severity="high",
        category="security",
        tags=["vulnerability", "sql_injection"],
        source_ip="192.168.1.100"
    )
    
    logger.security_event(
        "vulnerability_detected",
        "SQL injection vulnerability found in login form",
        "high",
        metadata=metadata
    )
    
    # Example 4: Structured logger
    print("\nStructured Logger:")
    structured_logger = StructuredLogger("structured_example")
    
    # Set correlation ID
    structured_logger.set_correlation_id("corr_456")
    
    # Set session data
    structured_logger.set_session_data("user_id", "user_789")
    structured_logger.set_session_data("session_id", "sess_123")
    
    # Log operation
    context = structured_logger.log_operation_start("data_processing", "processor", "process_data")
    time.sleep(0.1)  # Simulate processing
    structured_logger.log_operation_end(context, success=True, duration=0.1)
    
    # Example 5: Performance logging
    print("\nPerformance Logging:")
    logger.performance_metric("database_query", 0.5)
    logger.performance_metric("file_upload", 2.3)
    logger.performance_metric("api_call", 0.8)
    
    # Example 6: Audit logging
    print("\nAudit Logging:")
    logger.audit_event(
        action="user_login",
        resource="/login",
        user_id="admin"
    )
    
    logger.audit_event(
        action="file_access",
        resource="/etc/passwd",
        user_id="admin"
    )
    
    return logger

def demonstrate_monitoring():
    """Demonstrate monitoring system."""
    print("\n📊 Monitoring Examples")
    print("-" * 30)
    
    # Create performance monitor
    monitor = PerformanceMonitor()
    
    # Example 1: Record different types of metrics
    print("Recording Metrics:")
    
    # Counter metrics
    monitor.record_metric("requests_total", 1, MetricType.COUNTER)
    monitor.record_metric("requests_total", 1, MetricType.COUNTER)
    monitor.record_metric("errors_total", 1, MetricType.COUNTER)
    
    # Gauge metrics
    monitor.record_metric("active_connections", 15, MetricType.GAUGE)
    monitor.record_metric("memory_usage_percent", 75.5, MetricType.GAUGE)
    
    # Histogram metrics
    monitor.record_metric("request_duration", 0.1, MetricType.HISTOGRAM)
    monitor.record_metric("request_duration", 0.3, MetricType.HISTOGRAM)
    monitor.record_metric("request_duration", 0.2, MetricType.HISTOGRAM)
    
    # Summary metrics
    monitor.record_metric("response_size", 1024, MetricType.SUMMARY)
    monitor.record_metric("response_size", 2048, MetricType.SUMMARY)
    monitor.record_metric("response_size", 512, MetricType.SUMMARY)
    
    # Example 2: Get metric statistics
    print("\nMetric Statistics:")
    
    print(f"  Total requests: {monitor.get_counter('requests_total')}")
    print(f"  Active connections: {monitor.get_gauge('active_connections')}")
    
    histogram_stats = monitor.get_histogram_stats("request_duration")
    print(f"  Request duration stats: {histogram_stats}")
    
    summary_stats = monitor.get_summary("response_size")
    print(f"  Response size stats: {summary_stats}")
    
    # Example 3: Health checks
    print("\nHealth Checks:")
    checker = HealthChecker()
    
    # Add health checks
    async def database_health_check():
        # Simulate database check
        await asyncio.sleep(0.1)
        return True
    
    async def api_health_check():
        # Simulate API check
        await asyncio.sleep(0.1)
        return {"healthy": True, "message": "API is responding"}
    
    async def failing_health_check():
        # Simulate failing check
        raise Exception("Service unavailable")
    
    checker.add_health_check("database", database_health_check)
    checker.add_health_check("api", api_health_check)
    checker.add_health_check("external_service", failing_health_check)
    
    # Run health checks
    results = asyncio.run(checker.run_all_health_checks())
    
    for name, result in results.items():
        status = "✅" if result.status == "healthy" else "❌"
        print(f"  {status} {name}: {result.status} - {result.message}")
    
    # Example 4: Alert management
    print("\nAlert Management:")
    alert_manager = AlertManager()
    
    # Add alert handler
    alerts_sent = []
    def log_alert(alert):
        alerts_sent.append(alert)
        print(f"    Alert sent: {alert.title} ({alert.level.value})")
    
    alert_manager.add_alert_handler(AlertChannel.LOG, log_alert)
    
    # Create alerts
    alert_manager.create_alert(
        "High CPU Usage",
        "CPU usage is above 90%",
        AlertLevel.WARNING
    )
    
    alert_manager.create_alert(
        "Database Connection Failed",
        "Unable to connect to database",
        AlertLevel.ERROR
    )
    
    alert_manager.create_alert(
        "Security Breach Detected",
        "Unauthorized access attempt detected",
        AlertLevel.CRITICAL
    )
    
    print(f"  Total alerts sent: {len(alerts_sent)}")
    
    # Example 5: Performance tracking decorator
    print("\nPerformance Tracking:")
    
    @track_performance("example_operation")
    async def example_operation():
        await asyncio.sleep(0.1)
        return "Operation completed"
    
    result = await example_operation()
    print(f"  Operation result: {result}")
    
    # Get all metrics
    all_metrics = monitor.get_all_metrics()
    print(f"\nAll Metrics Summary:")
    print(f"  Counters: {len(all_metrics['counters'])}")
    print(f"  Gauges: {len(all_metrics['gauges'])}")
    print(f"  Histograms: {len(all_metrics['histograms'])}")
    print(f"  Summaries: {len(all_metrics['summaries'])}")
    
    return {
        "monitor": monitor,
        "checker": checker,
        "alert_manager": alert_manager
    }

def demonstrate_integration():
    """Demonstrate integration of all core components."""
    print("\n🔗 Integration Examples")
    print("-" * 30)
    
    # Setup components
    logger = SecurityLogger("integration_example")
    monitor = PerformanceMonitor()
    alert_manager = AlertManager()
    
    # Add alert handler
    def integration_alert_handler(alert):
        logger.security_event(
            "alert_triggered",
            f"Alert: {alert.title}",
            alert.level.value
        )
    
    alert_manager.add_alert_handler(AlertChannel.LOG, integration_alert_handler)
    
    # Example 1: Complete operation with all monitoring
    print("Complete Operation Monitoring:")
    
    async def monitored_operation():
        start_time = time.time()
        
        # Log operation start
        context = LogContext("integration_test", "integration", "test_operation")
        logger.info("Starting monitored operation", context)
        
        try:
            # Simulate work
            await asyncio.sleep(0.2)
            
            # Record performance metric
            duration = time.time() - start_time
            monitor.record_metric("integration_operation_duration", duration, MetricType.HISTOGRAM)
            
            # Log success
            logger.info("Operation completed successfully", context)
            
            return "Success"
        
        except Exception as e:
            # Log error
            logger.error(f"Operation failed: {e}", context)
            
            # Record error metric
            monitor.record_metric("integration_operation_errors", 1, MetricType.COUNTER)
            
            # Send alert
            alert_manager.create_alert(
                "Operation Failed",
                f"Integration operation failed: {e}",
                AlertLevel.ERROR
            )
            
            raise
    
    # Run operation
    try:
        result = await monitored_operation()
        print(f"  Operation result: {result}")
    except Exception as e:
        print(f"  Operation failed: {e}")
    
    # Example 2: Validation with error handling and logging
    print("\nValidation with Error Handling:")
    
    def validate_with_logging(target, port, credentials):
        context = LogContext("validation", "integration", "validate_inputs")
        
        # Validate target
        target_result = validate_target(target)
        if not target_result.is_valid:
            logger.error(f"Target validation failed: {target_result.errors}", context)
            raise TargetValidationError("Invalid target", target)
        
        # Validate port
        port_result = validate_port(port)
        if not port_result.is_valid:
            logger.error(f"Port validation failed: {port_result.errors}", context)
            raise PortValidationError("Invalid port", port)
        
        # Validate credentials
        cred_result = validate_credentials(credentials)
        if not cred_result.is_valid:
            logger.error(f"Credential validation failed: {cred_result.errors}", context)
            raise ValidationError("Invalid credentials")
        
        logger.info("All validations passed", context)
        return True
    
    # Test validation
    try:
        validate_with_logging("192.168.1.1", 80, {"username": "admin", "password": "pass"})
        print("  Validation successful")
    except Exception as e:
        print(f"  Validation failed: {e}")
    
    # Example 3: Performance monitoring with alerts
    print("\nPerformance Monitoring with Alerts:")
    
    # Check for slow operations
    histogram_stats = monitor.get_histogram_stats("integration_operation_duration")
    if histogram_stats and histogram_stats.get("mean", 0) > 0.1:
        alert_manager.create_alert(
            "Slow Operation Detected",
            f"Operation took {histogram_stats['mean']:.3f} seconds on average",
            AlertLevel.WARNING
        )
        print("  Performance alert sent")
    
    # Example 4: Error recovery with monitoring
    print("\nError Recovery with Monitoring:")
    
    retry_strategy = RetryStrategy(max_retries=2, base_delay=0.1)
    
    async def recoverable_operation():
        # Simulate operation that might fail
        if time.time() % 3 < 1:  # Fail occasionally
            raise NetworkError("Temporary network issue", "api.example.com", 443)
        return "Operation succeeded"
    
    try:
        result = await retry_strategy.execute(recoverable_operation)
        logger.info("Recoverable operation succeeded")
        monitor.record_metric("recovery_success", 1, MetricType.COUNTER)
    except Exception as e:
        logger.error(f"Recoverable operation failed: {e}")
        monitor.record_metric("recovery_failure", 1, MetricType.COUNTER)
        alert_manager.create_alert(
            "Recovery Failed",
            f"Operation failed after retries: {e}",
            AlertLevel.ERROR
        )
    
    # Summary
    print("\nIntegration Summary:")
    all_metrics = monitor.get_all_metrics()
    print(f"  Total metrics recorded: {sum(len(v) for v in all_metrics.values())}")
    print(f"  Alerts sent: {len(alert_manager.alerts)}")
    
    return {
        "logger": logger,
        "monitor": monitor,
        "alert_manager": alert_manager,
        "retry_strategy": retry_strategy
    }

async def main():
    """Main function to run all core examples."""
    print("🔧 Cybersecurity Core Toolkit Examples")
    print("=" * 60)
    print("📋 Error handling, validation, logging, and monitoring demonstration")
    print("=" * 60)
    
    try:
        # Run all demonstrations
        results = {}
        
        print("\n🚨 Error Handling")
        results["error_handling"] = demonstrate_error_handling()
        
        print("\n🔄 Retry Strategy")
        results["retry_strategy"] = demonstrate_retry_strategy()
        
        print("\n⚡ Circuit Breaker")
        results["circuit_breaker"] = await demonstrate_circuit_breaker()
        
        print("\n✅ Validation")
        results["validation"] = demonstrate_validation()
        
        print("\n📝 Logging")
        results["logging"] = demonstrate_logging()
        
        print("\n📊 Monitoring")
        results["monitoring"] = await demonstrate_monitoring()
        
        print("\n🔗 Integration")
        results["integration"] = await demonstrate_integration()
        
        print("\n" + "=" * 60)
        print("✅ All core examples completed successfully!")
        
        # Summary
        print("\n📊 Core Components Summary:")
        print(f"   Error Handling: {len(results['error_handling'].error_counts)} error types")
        print(f"   Validation: {len(results['validation'])} validation examples")
        print(f"   Logging: Structured logging with context and metadata")
        print(f"   Monitoring: {len(results['monitoring']['monitor'].get_all_metrics()['counters'])} metrics")
        print(f"   Integration: Complete workflow demonstration")
        
        # Component types summary
        print("\n🏗️ Core Component Types Demonstrated:")
        print("   • Error Handling (Exceptions, Handlers, Recovery)")
        print("   • Validation (Validators, Rules, Schemas)")
        print("   • Logging (Structured, Context, Metadata)")
        print("   • Monitoring (Metrics, Health Checks, Alerts)")
        print("   • Integration (Combined workflows)")
        
        # Features summary
        print("\n✨ Features Demonstrated:")
        print("   • Comprehensive error handling with context")
        print("   • Retry strategies and circuit breakers")
        print("   • Input validation with custom rules")
        print("   • Structured logging with security events")
        print("   • Performance monitoring and alerting")
        print("   • Integration of all components")
        print("   • Error recovery mechanisms")
        print("   • Health checking and metrics collection")
        print("   • Audit logging and security events")
        print("   • Real-time monitoring and alerting")
        
        # Use cases summary
        print("\n🎯 Use Cases Demonstrated:")
        print("   • Security tool error handling")
        print("   • Input validation and sanitization")
        print("   • Performance monitoring and optimization")
        print("   • Security event logging and tracking")
        print("   • System health monitoring")
        print("   • Alert management and notification")
        print("   • Error recovery and resilience")
        print("   • Audit trail and compliance")
        print("   • Real-time monitoring and metrics")
        print("   • Integrated security operations")
        
    except Exception as e:
        print(f"❌ Error running core examples: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 