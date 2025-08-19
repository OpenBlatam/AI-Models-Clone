from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

# Constants
BUFFER_SIZE = 1024

import time
import json
import traceback
from typing import Dict, List, Any
from error_logging_implementation import (
import random
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Error Logging and User-Friendly Error Messages Runner Script
==========================================================

This script demonstrates:
- Comprehensive error logging with structured data
- User-friendly error messages for different scenarios
- Error handling patterns and best practices
- Error monitoring and reporting
- Production-ready error management
"""

    # Core classes
    ErrorLogger, ErrorHandler, ErrorContextManager, ErrorReporter,
    
    # Custom exceptions
    BaseAppException, ValidationError, AuthenticationError, AuthorizationError,
    DatabaseError, ExternalAPIError, ConfigurationError, ModelTrainingError,
    
    # Enums and data models
    ErrorSeverity, ErrorCategory, ErrorContext, ErrorDetails, LogEntry,
    
    # Utilities
    UserFriendlyMessages, handle_errors, log_errors
)


def demonstrate_basic_error_logging():
    """Demonstrate basic error logging functionality"""
    print("\n" + "="*60)
    print("Basic Error Logging")
    print("="*60)
    
    # Initialize error logging system
    logger = ErrorLogger(
        log_file="logs/basic_errors.log",
        log_level="INFO",
        enable_console=True,
        enable_file=True,
        enable_json=True
    )
    
    error_handler = ErrorHandler(logger)
    
    # Test different error types
    test_cases = [
        {
            "name": "Validation Error",
            "error": ValidationError(
                message="Email validation failed: invalid format 'test@'",
                user_message="Please enter a valid email address",
                field="email"
            )
        },
        {
            "name": "Authentication Error",
            "error": AuthenticationError(
                message="Login failed: invalid credentials for user 'test@example.com'",
                user_message="Invalid email or password. Please try again."
            )
        },
        {
            "name": "Database Error",
            "error": DatabaseError(
                message="Database connection timeout after 30 seconds",
                user_message="Database connection failed. Please try again later."
            )
        },
        {
            "name": "External API Error",
            "error": ExternalAPIError(
                message="Payment gateway API returned 503 Service Unavailable",
                user_message="Payment service is temporarily unavailable. Please try again in a few minutes."
            )
        },
        {
            "name": "Configuration Error",
            "error": ConfigurationError(
                message="Missing required configuration: DATABASE_URL",
                user_message="System configuration error. Please contact support."
            )
        }
    ]
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        response = error_handler.handle_error(
            error=case['error'],
            user_id="user123",
            session_id="session456",
            request_id="req789"
        )
        print(f"  Response: {json.dumps(response, indent=2)}")


def demonstrate_error_categories_and_severities():
    """Demonstrate different error categories and severities"""
    print("\n" + "="*60)
    print("Error Categories and Severities")
    print("="*60)
    
    logger = ErrorLogger(log_file="logs/categories.log")
    error_handler = ErrorHandler(logger)
    
    # Test all error categories and severities
    test_cases = [
        {
            "name": "Low Severity Validation",
            "error": ValidationError(
                message="Optional field validation warning",
                user_message="Please check the optional field format"
            )
        },
        {
            "name": "Medium Severity External API",
            "error": ExternalAPIError(
                message="External service rate limit warning",
                user_message="Service is experiencing high load. Please try again later."
            )
        },
        {
            "name": "High Severity Database",
            "error": DatabaseError(
                message="Critical database connection failure",
                user_message="Database connection failed. Please try again later."
            )
        },
        {
            "name": "Critical Severity Configuration",
            "error": ConfigurationError(
                message="System cannot start due to missing critical configuration",
                user_message="System configuration error. Please contact support."
            )
        }
    ]
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        response = error_handler.handle_error(
            error=case['error'],
            user_id="user123"
        )
        print(f"  Severity: {case['error'].severity.value}")
        print(f"  Category: {case['error'].category.value}")
        print(f"  User Message: {case['error'].user_message}")


def demonstrate_error_context_and_tracking():
    """Demonstrate error context and tracking"""
    print("\n" + "="*60)
    print("Error Context and Tracking")
    print("="*60)
    
    logger = ErrorLogger(log_file="logs/context.log")
    error_handler = ErrorHandler(logger)
    
    # Simulate different contexts
    contexts = [
        {
            "name": "User Registration",
            "user_id": "new_user_123",
            "session_id": "session_registration",
            "request_id": "req_register_456",
            "context": {"operation": "user_registration", "step": "email_validation"}
        },
        {
            "name": "Payment Processing",
            "user_id": "existing_user_789",
            "session_id": "session_payment",
            "request_id": "req_payment_101",
            "context": {"operation": "payment_processing", "amount": 99.99, "currency": "USD"}
        },
        {
            "name": "Model Training",
            "user_id": "ml_user_456",
            "session_id": "session_training",
            "request_id": "req_training_202",
            "context": {"operation": "model_training", "model_type": "neural_network", "epochs": 100}
        }
    ]
    
    for ctx in contexts:
        print(f"\n{ctx['name']}:")
        
        # Simulate different errors for each context
        errors = [
            ValidationError("Email format invalid", "Please enter a valid email address"),
            ExternalAPIError("Payment gateway timeout", "Payment service temporarily unavailable"),
            ModelTrainingError("GPU memory exceeded", "Model training failed due to insufficient resources")
        ]
        
        for i, error in enumerate(errors):
            response = error_handler.handle_error(
                error=error,
                user_id=ctx['user_id'],
                session_id=ctx['session_id'],
                request_id=ctx['request_id'],
                context=ctx['context']
            )
            print(f"  Error {i+1}: {error.category.value} - {response['error']['message']}")


def demonstrate_user_friendly_messages():
    """Demonstrate user-friendly error messages"""
    print("\n" + "="*60)
    print("User-Friendly Error Messages")
    print("="*60)
    
    # Test different message categories
    message_categories = [
        ("validation", "required_field"),
        ("validation", "invalid_email"),
        ("validation", "password_too_short"),
        ("authentication", "invalid_credentials"),
        ("authentication", "account_locked"),
        ("authorization", "insufficient_permissions"),
        ("authorization", "admin_required"),
        ("database", "connection_failed"),
        ("database", "duplicate_entry"),
        ("network", "connection_timeout"),
        ("network", "server_unavailable"),
        ("external_api", "service_unavailable"),
        ("external_api", "rate_limit_exceeded"),
        ("system", "internal_error"),
        ("system", "maintenance_mode")
    ]
    
    print("\nUser-Friendly Messages by Category:")
    for category, error_type in message_categories:
        message = UserFriendlyMessages.get_message(category, error_type)
        print(f"  {category}.{error_type}: {message}")


def demonstrate_error_monitoring_and_reporting():
    """Demonstrate error monitoring and reporting"""
    print("\n" + "="*60)
    print("Error Monitoring and Reporting")
    print("="*60)
    
    logger = ErrorLogger(log_file="logs/monitoring.log")
    error_handler = ErrorHandler(logger)
    error_reporter = ErrorReporter(logger)
    
    # Simulate multiple errors over time
    print("\nSimulating error scenarios...")
    
    # Validation errors (common)
    for i in range(5):
        error = ValidationError(
            message=f"Field validation failed: iteration {i}",
            user_message="Please check your input and try again"
        )
        error_handler.handle_error(error, user_id=f"user_{i}")
        error_reporter.report_error(error)
    
    # Database errors (less common)
    for i in range(2):
        error = DatabaseError(
            message=f"Database timeout: iteration {i}",
            user_message="Database connection failed. Please try again later."
        )
        error_handler.handle_error(error, user_id=f"user_{i}")
        error_reporter.report_error(error)
    
    # Critical configuration error (rare)
    error = ConfigurationError(
        message="Critical system configuration missing",
        user_message="System configuration error. Please contact support."
    )
    error_handler.handle_error(error, user_id="admin")
    error_reporter.report_error(error)
    
    # Get and display error statistics
    print("\nError Statistics:")
    stats = error_reporter.get_error_stats()
    print(f"  Total Errors: {stats['total_errors']}")
    print(f"  Errors by Category: {json.dumps(stats['errors_by_category'], indent=4)}")
    print(f"  Errors by Severity: {json.dumps(stats['errors_by_severity'], indent=4)}")
    
    print("\nError Summary:")
    summary = error_reporter.get_error_summary()
    print(f"  Total Errors: {summary['total_errors']}")
    print(f"  Top Categories: {summary['top_categories']}")
    print(f"  Severity Distribution: {summary['severity_distribution']}")
    print(f"  Recent Error Count: {summary['recent_error_count']}")


def demonstrate_error_context_manager():
    """Demonstrate error context manager usage"""
    print("\n" + "="*60)
    print("Error Context Manager")
    print("="*60)
    
    logger = ErrorLogger(log_file="logs/context_manager.log")
    error_handler = ErrorHandler(logger)
    context_manager = ErrorContextManager(error_handler)
    
    # Set context for a user session
    context_manager.set_context(
        user_id="user_context_123",
        session_id="session_context_456",
        request_id="req_context_789",
        operation="data_processing",
        step="validation"
    )
    
    print("\nUsing context manager for error handling:")
    
    # This will be automatically logged with context
    try:
        with context_manager.error_context():
            # Simulate an error
            raise ValidationError(
                message="Context manager test error",
                user_message="Test error with context"
            )
    except ValidationError:
        print("  Error handled with context manager")


def demonstrate_error_decorators():
    """Demonstrate error decorators"""
    print("\n" + "="*60)
    print("Error Decorators")
    print("="*60)
    
    logger = ErrorLogger(log_file="logs/decorators.log")
    error_handler = ErrorHandler(logger)
    
    # Function with automatic error handling
    @handle_errors(error_handler)
    def process_user_data(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Function that might raise errors"""
        if not data.get("email"):
            raise ValidationError(
                message="Email is required for user data processing",
                user_message="Email address is required"
            )
        
        if data.get("age", 0) < 18:
            raise ValidationError(
                message="User must be 18 or older",
                user_message="You must be 18 or older to use this service"
            )
        
        return {"status": "success", "user_id": user_id}
    
    # Function with automatic error logging
    @log_errors(logger)
    def risky_operation() -> int:
        """Function that logs errors but doesn't handle them"""
        return 1 / 0
    
    print("\nTesting error handling decorator:")
    try:
        result = process_user_data("user_decorator", {"name": "John"})  # Missing email
    except ValidationError as e:
        print(f"  Caught validation error: {e.user_message}")
    
    print("\nTesting error logging decorator:")
    try:
        result = risky_operation()
    except ZeroDivisionError:
        print("  ZeroDivisionError was logged but re-raised")


def demonstrate_production_error_handling():
    """Demonstrate production-ready error handling"""
    print("\n" + "="*60)
    print("Production Error Handling")
    print("="*60)
    
    # Production logger with file rotation and JSON logging
    logger = ErrorLogger(
        log_file="logs/production_errors.log",
        log_level="WARNING",  # Only log warnings and above in production
        enable_console=False,  # Disable console in production
        enable_file=True,
        enable_json=True,
        max_file_size=5 * 1024 * 1024,  # 5MB
        backup_count=10
    )
    
    error_handler = ErrorHandler(logger)
    error_reporter = ErrorReporter(logger)
    
    # Simulate production error scenarios
    production_scenarios = [
        {
            "name": "High Volume Validation Errors",
            "error_class": ValidationError,
            "count": 10,
            "message": "Email format invalid",
            "user_message": "Please enter a valid email address"
        },
        {
            "name": "Database Connection Issues",
            "error_class": DatabaseError,
            "count": 3,
            "message": "Database connection pool exhausted",
            "user_message": "Service temporarily unavailable. Please try again."
        },
        {
            "name": "External Service Failures",
            "error_class": ExternalAPIError,
            "count": 5,
            "message": "Payment gateway service down",
            "user_message": "Payment processing temporarily unavailable."
        }
    ]
    
    print("\nSimulating production error scenarios:")
    
    for scenario in production_scenarios:
        print(f"\n{scenario['name']}:")
        for i in range(scenario['count']):
            error = scenario['error_class'](
                message=f"{scenario['message']} - instance {i+1}",
                user_message=scenario['user_message']
            )
            error_handler.handle_error(
                error=error,
                user_id=f"prod_user_{i}",
                request_id=f"prod_req_{i}"
            )
            error_reporter.report_error(error)
        
        print(f"  Generated {scenario['count']} {scenario['error_class'].__name__} errors")
    
    # Show production error summary
    print("\nProduction Error Summary:")
    summary = error_reporter.get_error_summary()
    print(f"  Total Errors: {summary['total_errors']}")
    print(f"  Top Categories: {summary['top_categories']}")
    print(f"  Severity Distribution: {summary['severity_distribution']}")


def demonstrate_error_recovery_strategies():
    """Demonstrate error recovery strategies"""
    print("\n" + "="*60)
    print("Error Recovery Strategies")
    print("="*60)
    
    logger = ErrorLogger(log_file="logs/recovery.log")
    error_handler = ErrorHandler(logger)
    
    def retry_operation(operation: callable, max_retries: int = 3, delay: float = 1.0):
        """Retry operation with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    # Last attempt failed, log and re-raise
                    error_handler.handle_error(e, user_id="retry_user")
                    raise
                
                # Log retry attempt
                logger.log_warning(
                    f"Operation failed, retrying in {delay}s (attempt {attempt + 1}/{max_retries})",
                    error_id=str(e.error_id) if hasattr(e, 'error_id') else None
                )
                time.sleep(delay)
                delay *= 2  # Exponential backoff
    
    def fallback_operation():
        """Fallback operation when primary fails"""
        return {"status": "fallback", "message": "Using fallback service"}
    
    def circuit_breaker(operation: callable, failure_threshold: int = 5):
        """Simple circuit breaker pattern"""
        failure_count = 0
        
        def protected_operation():
            
    """protected_operation function."""
nonlocal failure_count
            try:
                result = operation()
                failure_count = 0  # Reset on success
                return result
            except Exception as e:
                failure_count += 1
                if failure_count >= failure_threshold:
                    logger.log_critical(
                        f"Circuit breaker opened after {failure_count} failures",
                        error_id=str(e.error_id) if hasattr(e, 'error_id') else None
                    )
                    return fallback_operation()
                raise
        
        return protected_operation
    
    print("\n1. Retry Strategy with Exponential Backoff:")
    try:
        def failing_operation():
            
    """failing_operation function."""
raise ExternalAPIError(
                message="External service temporarily unavailable",
                user_message="Service temporarily unavailable. Please try again."
            )
        
        result = retry_operation(failing_operation, max_retries=3, delay=0.1)
        print("  Retry strategy completed")
    except Exception as e:
        print(f"  All retry attempts failed: {e.user_message}")
    
    print("\n2. Circuit Breaker Pattern:")
    def unreliable_operation():
        
    """unreliable_operation function."""
        if random.random() < 0.8:  # 80% failure rate
            raise ExternalAPIError(
                message="Unreliable service failed",
                user_message="Service temporarily unavailable"
            )
        return {"status": "success"}
    
    protected_operation = circuit_breaker(unreliable_operation, failure_threshold=3)
    
    for i in range(10):
        try:
            result = protected_operation()
            print(f"  Attempt {i+1}: {result['status']}")
        except Exception as e:
            print(f"  Attempt {i+1}: Failed")


def demonstrate_error_analysis():
    """Demonstrate error analysis and insights"""
    print("\n" + "="*60)
    print("Error Analysis and Insights")
    print("="*60)
    
    logger = ErrorLogger(log_file="logs/analysis.log")
    error_reporter = ErrorReporter(logger)
    
    # Simulate errors for analysis
    error_patterns = [
        # Validation errors (most common)
        (ValidationError, 15, "Email validation failed"),
        (ValidationError, 12, "Password too short"),
        (ValidationError, 8, "Invalid phone number"),
        
        # Authentication errors
        (AuthenticationError, 5, "Invalid credentials"),
        (AuthenticationError, 3, "Account locked"),
        
        # Database errors
        (DatabaseError, 4, "Connection timeout"),
        (DatabaseError, 2, "Query timeout"),
        
        # External API errors
        (ExternalAPIError, 6, "Service unavailable"),
        (ExternalAPIError, 3, "Rate limit exceeded"),
        
        # Critical errors
        (ConfigurationError, 1, "Missing configuration"),
    ]
    
    print("\nGenerating error patterns for analysis...")
    
    for error_class, count, message in error_patterns:
        for i in range(count):
            error = error_class(
                message=f"{message} - instance {i+1}",
                user_message=f"Error occurred: {message}"
            )
            error_reporter.report_error(error)
    
    # Analyze error patterns
    stats = error_reporter.get_error_stats()
    
    print("\nError Analysis:")
    print(f"  Total Errors: {stats['total_errors']}")
    
    print("\n  Error Distribution by Category:")
    for category, count in stats['errors_by_category'].items():
        percentage = (count / stats['total_errors']) * 100
        print(f"    {category}: {count} ({percentage:.1f}%)")
    
    print("\n  Error Distribution by Severity:")
    for severity, count in stats['errors_by_severity'].items():
        percentage = (count / stats['total_errors']) * 100
        print(f"    {severity}: {count} ({percentage:.1f}%)")
    
    print("\n  Recent Error Trends:")
    recent_errors = stats['recent_errors'][-10:]  # Last 10 errors
    for error in recent_errors:
        print(f"    {error['timestamp']}: {error['category']} - {error['severity']}")


def main():
    """Main function to run all error logging demonstrations"""
    print("Error Logging and User-Friendly Error Messages Demonstrations")
    print("=" * 80)
    
    try:
        # Core demonstrations
        demonstrate_basic_error_logging()
        demonstrate_error_categories_and_severities()
        demonstrate_error_context_and_tracking()
        demonstrate_user_friendly_messages()
        demonstrate_error_monitoring_and_reporting()
        
        # Advanced demonstrations
        demonstrate_error_context_manager()
        demonstrate_error_decorators()
        demonstrate_production_error_handling()
        demonstrate_error_recovery_strategies()
        demonstrate_error_analysis()
        
        print("\n" + "="*80)
        print("All Error Logging Demonstrations Completed Successfully!")
        print("="*80)
        
        print("\n📁 Check the 'logs/' directory for generated log files:")
        print("  - basic_errors.log")
        print("  - categories.log")
        print("  - context.log")
        print("  - monitoring.log")
        print("  - context_manager.log")
        print("  - decorators.log")
        print("  - production_errors.log")
        print("  - recovery.log")
        print("  - analysis.log")
        print("  - *_json.log (structured JSON logs)")
        
    except Exception as e:
        print(f"\nError during demonstrations: {str(e)}")
        traceback.print_exc()
        raise


match __name__:
    case "__main__":
    main() 