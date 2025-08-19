from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

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
from custom_error_factories_implementation import (
        import random
        import random
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Custom Error Types and Error Factories Runner Script
==================================================

This script demonstrates:
- Custom error types with specialized behavior
- Error factories for consistent error creation
- Error builders with fluent interfaces
- Domain-specific error types
- Error factory configuration and registry
- Error handling patterns with factories
"""

    # Custom error types
    MLTrainingError, DataProcessingError, APIError, FileOperationError,
    ECommerceError, FinancialError, HealthcareError,
    
    # Error factories
    ErrorFactory, ErrorBuilder, ValidationErrorFactory, MLTrainingErrorFactory,
    DataProcessingErrorFactory, APIErrorFactory, FileOperationErrorFactory,
    
    # Registry and configuration
    ErrorFactoryRegistry, ErrorContextManager, ErrorFactoryConfig,
    ConfigurableErrorFactory,
    
    # Decorators
    handle_errors_with_factory, log_errors_with_factory
)


def demonstrate_custom_error_types():
    """Demonstrate custom error types"""
    print("\n" + "="*60)
    print("Custom Error Types")
    print("="*60)
    
    # ML Training Error
    print("\n1. ML Training Error:")
    ml_error = MLTrainingError(
        message="GPU memory exceeded during model training",
        user_message="Model training failed due to insufficient GPU memory",
        model_name="bert-large",
        training_step="forward_pass",
        epoch=5,
        batch=32,
        loss=0.15
    )
    print(f"  Message: {ml_error.user_message}")
    print(f"  Model: {ml_error.model_name}")
    print(f"  Training Context: {ml_error.get_training_context()}")
    
    # Data Processing Error
    print("\n2. Data Processing Error:")
    data_error = DataProcessingError(
        message="Failed to process CSV file: invalid format",
        user_message="The data file format is not supported",
        data_source="user_uploads",
        processing_step="format_validation",
        record_count=1000
    )
    data_error.add_failed_record({"id": 1, "name": "test"}, "Invalid format")
    print(f"  Message: {data_error.user_message}")
    print(f"  Data Source: {data_error.data_source}")
    print(f"  Processing Summary: {data_error.get_processing_summary()}")
    
    # API Error
    print("\n3. API Error:")
    api_error = APIError(
        message="External API returned 503 Service Unavailable",
        user_message="The external service is temporarily unavailable",
        status_code=503,
        endpoint="/api/external/data",
        method="GET",
        request_data={"user_id": "123"},
        response_data={"error": "service_unavailable"}
    )
    print(f"  Message: {api_error.user_message}")
    print(f"  Status Code: {api_error.status_code}")
    print(f"  API Context: {api_error.get_api_context()}")
    
    # File Operation Error
    print("\n4. File Operation Error:")
    file_error = FileOperationError(
        message="Permission denied when writing to file",
        user_message="You don't have permission to write to this file",
        file_path="/var/log/app.log",
        operation="write",
        file_size=1024,
        file_type="log"
    )
    print(f"  Message: {file_error.user_message}")
    print(f"  File Path: {file_error.file_path}")
    print(f"  File Context: {file_error.get_file_context()}")


def demonstrate_error_factories():
    """Demonstrate error factory usage"""
    print("\n" + "="*60)
    print("Error Factories")
    print("="*60)
    
    # Create factories
    validation_factory = ValidationErrorFactory()
    ml_factory = MLTrainingErrorFactory()
    data_factory = DataProcessingErrorFactory()
    api_factory = APIErrorFactory()
    file_factory = FileOperationErrorFactory()
    
    print("\n1. Validation Error Factory:")
    validation_errors = [
        validation_factory.invalid_email("test@", "email"),
        validation_factory.required_field("username"),
        validation_factory.field_too_short("password", 8, 5),
        validation_factory.invalid_format("phone", "XXX-XXX-XXXX", "12345")
    ]
    
    for i, error in enumerate(validation_errors, 1):
        print(f"  Error {i}: {error.user_message}")
        if hasattr(error, 'field'):
            print(f"    Field: {error.field}")
    
    print("\n2. ML Training Error Factory:")
    ml_errors = [
        ml_factory.gpu_memory_exceeded("bert-large", "8GB", "4GB"),
        ml_factory.convergence_failed("cnn-model", 100, 0.85),
        ml_factory.data_loading_failed("transformer", "/data/train.csv", "File not found")
    ]
    
    for i, error in enumerate(ml_errors, 1):
        print(f"  Error {i}: {error.user_message}")
        print(f"    Model: {error.model_name}")
        print(f"    Step: {error.training_step}")
    
    print("\n3. Data Processing Error Factory:")
    data_errors = [
        data_factory.file_not_found("user_uploads", "/uploads/data.csv"),
        data_factory.invalid_format("api_data", "JSON", "XML"),
        data_factory.corrupted_data("database_export", 1000, 50)
    ]
    
    for i, error in enumerate(data_errors, 1):
        print(f"  Error {i}: {error.user_message}")
        print(f"    Source: {error.data_source}")
        print(f"    Step: {error.processing_step}")
    
    print("\n4. API Error Factory:")
    api_errors = [
        api_factory.timeout("/api/users", "GET", 30),
        api_factory.rate_limited("/api/data", "POST", 60),
        api_factory.server_error("/api/payment", "POST", 500, {"error": "internal_server_error"})
    ]
    
    for i, error in enumerate(api_errors, 1):
        print(f"  Error {i}: {error.user_message}")
        print(f"    Endpoint: {error.endpoint}")
        print(f"    Status: {error.status_code}")
    
    print("\n5. File Operation Error Factory:")
    file_errors = [
        file_factory.file_not_found("/data/config.json", "read"),
        file_factory.permission_denied("/var/log/app.log", "write"),
        file_factory.disk_full("/backup/data.bak", "write", 1024*1024*100, 1024*1024*50)
    ]
    
    for i, error in enumerate(file_errors, 1):
        print(f"  Error {i}: {error.user_message}")
        print(f"    File: {error.file_path}")
        print(f"    Operation: {error.operation}")


def demonstrate_error_builder():
    """Demonstrate error builder pattern"""
    print("\n" + "="*60)
    print("Error Builder Pattern")
    print("="*60)
    
    print("\n1. Building Validation Error:")
    validation_error = (ErrorBuilder(MLTrainingError)
                       .with_message("Custom ML training error occurred")
                       .with_user_message("Model training failed due to custom issue")
                       .with_severity(ErrorSeverity.HIGH)
                       .with_category(ErrorCategory.BUSINESS_LOGIC)
                       .with_context(ErrorContext.MODEL_TRAINING)
                       .with_data("model_name", "custom-model")
                       .with_data("training_step", "custom_step")
                       .with_data("epoch", 10)
                       .build())
    
    print(f"  Message: {validation_error.user_message}")
    print(f"  Severity: {validation_error.severity.value}")
    print(f"  Category: {validation_error.category.value}")
    print(f"  Context: {validation_error.context.value}")
    print(f"  Additional Data: {validation_error.additional_data}")
    
    print("\n2. Building API Error:")
    api_error = (ErrorBuilder(APIError)
                .with_message("Custom API error with builder")
                .with_user_message("API request failed")
                .with_severity(ErrorSeverity.MEDIUM)
                .with_data("status_code", 400)
                .with_data("endpoint", "/api/custom")
                .with_data("method", "POST")
                .build())
    
    print(f"  Message: {api_error.user_message}")
    print(f"  Status Code: {api_error.status_code}")
    print(f"  Endpoint: {api_error.endpoint}")


def demonstrate_error_registry():
    """Demonstrate error factory registry"""
    print("\n" + "="*60)
    print("Error Factory Registry")
    print("="*60)
    
    # Create registry
    registry = ErrorFactoryRegistry()
    
    # Register factories
    registry.register_factory("validation", ValidationErrorFactory())
    registry.register_factory("ml", MLTrainingErrorFactory())
    registry.register_factory("data", DataProcessingErrorFactory())
    registry.register_factory("api", APIErrorFactory())
    registry.register_factory("file", FileOperationErrorFactory())
    
    # Set default factory
    registry.set_default_factory(ValidationErrorFactory())
    
    print(f"\nRegistered factories: {registry.list_factories()}")
    
    # Create errors using registry
    print("\nCreating errors using registry:")
    
    error_types = [
        ("validation", {"message": "Registry validation error", "user_message": "Validation failed"}),
        ("ml", {"message": "Registry ML error", "user_message": "ML training failed", "model_name": "registry-model", "training_step": "registry_step"}),
        ("api", {"message": "Registry API error", "user_message": "API call failed", "status_code": 500, "endpoint": "/api/registry", "method": "GET"}),
        ("unknown", {"message": "Unknown factory error", "user_message": "Unknown error"})  # Uses default
    ]
    
    for factory_name, error_params in error_types:
        try:
            error = registry.create_error(factory_name, **error_params)
            print(f"  {factory_name}: {error.user_message}")
            print(f"    Type: {type(error).__name__}")
        except Exception as e:
            print(f"  {factory_name}: Failed to create error - {str(e)}")


def demonstrate_domain_specific_errors():
    """Demonstrate domain-specific error types"""
    print("\n" + "="*60)
    print("Domain-Specific Error Types")
    print("="*60)
    
    print("\n1. E-Commerce Error:")
    ecommerce_error = ECommerceError(
        message="Order processing failed: insufficient inventory",
        user_message="Sorry, this item is currently out of stock",
        order_id="ORD-12345",
        product_id="PROD-67890",
        customer_id="CUST-11111"
    )
    print(f"  Message: {ecommerce_error.user_message}")
    print(f"  Order ID: {ecommerce_error.order_id}")
    print(f"  Product ID: {ecommerce_error.product_id}")
    print(f"  Customer ID: {ecommerce_error.customer_id}")
    
    print("\n2. Financial Error:")
    financial_error = FinancialError(
        message="Payment processing failed: insufficient funds",
        user_message="Payment failed due to insufficient funds in your account",
        transaction_id="TXN-98765",
        amount=99.99,
        currency="USD",
        account_id="ACC-54321"
    )
    print(f"  Message: {financial_error.user_message}")
    print(f"  Transaction ID: {financial_error.transaction_id}")
    print(f"  Amount: {financial_error.amount} {financial_error.currency}")
    print(f"  Account ID: {financial_error.account_id}")
    
    print("\n3. Healthcare Error (HIPAA Compliant):")
    healthcare_error = HealthcareError(
        message="Patient record access denied: unauthorized user",
        user_message="Access to patient records is restricted",
        patient_id="PAT-12345",
        provider_id="PROV-67890",
        service_type="record_access"
    )
    print(f"  Message: {healthcare_error.user_message}")
    print(f"  Provider ID: {healthcare_error.provider_id}")
    print(f"  Service Type: {healthcare_error.service_type}")
    print(f"  HIPAA Context: {healthcare_error.get_hipaa_context()}")


def demonstrate_configurable_factory():
    """Demonstrate configurable error factory"""
    print("\n" + "="*60)
    print("Configurable Error Factory")
    print("="*60)
    
    # Create different configurations
    configs = [
        ErrorFactoryConfig(
            enable_logging=True,
            enable_metrics=True,
            alert_on_critical=True,
            error_threshold=3
        ),
        ErrorFactoryConfig(
            enable_logging=False,
            enable_metrics=True,
            alert_on_critical=False,
            error_threshold=10
        )
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\nConfiguration {i}:")
        print(f"  Logging: {config.enable_logging}")
        print(f"  Metrics: {config.enable_metrics}")
        print(f"  Alert on Critical: {config.alert_on_critical}")
        print(f"  Error Threshold: {config.error_threshold}")
        
        # Create factory with configuration
        factory = ConfigurableErrorFactory(MLTrainingError, config)
        
        # Create multiple errors to test threshold
        for j in range(5):
            error = factory.create_error(
                message=f"Config {i} test error {j}",
                user_message=f"Test error {j}",
                model_name=f"config-{i}-model",
                training_step="test"
            )
            print(f"    Error {j}: {error.user_message}")
            if hasattr(error, 'additional_data') and 'factory_config' in error.additional_data:
                print(f"      Factory Config: {error.additional_data['factory_config']}")


def demonstrate_error_context_manager():
    """Demonstrate error context manager with factories"""
    print("\n" + "="*60)
    print("Error Context Manager with Factories")
    print("="*60)
    
    # Create registry and context manager
    registry = ErrorFactoryRegistry()
    registry.register_factory("ml", MLTrainingErrorFactory())
    registry.register_factory("api", APIErrorFactory())
    
    context_manager = ErrorContextManager(registry)
    
    # Set context
    context_manager.set_context(
        user_id="context_user_123",
        session_id="context_session_456",
        request_id="context_req_789",
        operation="model_training",
        model_name="context-model"
    )
    
    print("\nUsing context manager with ML factory:")
    
    # This will be automatically converted to ML error if exception occurs
    try:
        with context_manager.error_context("ml"):
            # Simulate an error
            raise ValueError("GPU memory exceeded")
    except MLTrainingError as e:
        print(f"  Caught ML error: {e.user_message}")
        print(f"  Context: {e.additional_data}")
    
    print("\nUsing context manager with API factory:")
    
    try:
        with context_manager.error_context("api"):
            # Simulate an error
            raise ConnectionError("API connection failed")
    except APIError as e:
        print(f"  Caught API error: {e.user_message}")
        print(f"  Context: {e.additional_data}")


def demonstrate_error_decorators():
    """Demonstrate error decorators with factories"""
    print("\n" + "="*60)
    print("Error Decorators with Factories")
    print("="*60)
    
    # Create registry
    registry = ErrorFactoryRegistry()
    registry.register_factory("validation", ValidationErrorFactory())
    registry.register_factory("ml", MLTrainingErrorFactory())
    
    # Mock logger
    class MockLogger:
        def log_error(self, error) -> Any:
            print(f"    Logged: {error.user_message}")
    
    logger = MockLogger()
    
    print("\n1. Function with validation error handling:")
    
    @handle_errors_with_factory("validation", registry)
    def validate_user_data(data: Dict[str, Any]) -> bool:
        """Function that might raise validation errors"""
        if not data.get("email"):
            raise ValueError("Email is required")
        if not data.get("password"):
            raise ValueError("Password is required")
        return True
    
    try:
        result = validate_user_data({"name": "John"})  # Missing email and password
    except Exception as e:
        print(f"  Caught error: {e.user_message}")
        print(f"  Error type: {type(e).__name__}")
    
    print("\n2. Function with ML error logging:")
    
    @log_errors_with_factory("ml", registry, logger)
    def train_model(model_name: str) -> bool:
        """Function that might raise ML errors"""
        if model_name == "large-model":
            raise RuntimeError("GPU memory exceeded")
        return True
    
    try:
        result = train_model("large-model")
    except Exception as e:
        print(f"  Caught error: {e.user_message}")
        print(f"  Error type: {type(e).__name__}")


def demonstrate_error_patterns():
    """Demonstrate common error patterns with factories"""
    print("\n" + "="*60)
    print("Error Patterns with Factories")
    print("="*60)
    
    # Create factories
    validation_factory = ValidationErrorFactory()
    ml_factory = MLTrainingErrorFactory()
    api_factory = APIErrorFactory()
    
    print("\n1. Form Validation Pattern:")
    
    def validate_registration_form(data: Dict[str, Any]) -> List[Any]:
        """Validate registration form data"""
        errors = []
        
        # Email validation
        if not data.get("email"):
            errors.append(validation_factory.required_field("email"))
        elif "@" not in data["email"]:
            errors.append(validation_factory.invalid_email(data["email"], "email"))
        
        # Password validation
        if not data.get("password"):
            errors.append(validation_factory.required_field("password"))
        elif len(data["password"]) < 8:
            errors.append(validation_factory.field_too_short("password", 8, len(data["password"])))
        
        # Username validation
        if not data.get("username"):
            errors.append(validation_factory.required_field("username"))
        elif len(data["username"]) < 3:
            errors.append(validation_factory.field_too_short("username", 3, len(data["username"])))
        
        return errors
    
    # Test form validation
    test_data = [
        {"email": "invalid", "password": "123", "username": "a"},
        {"email": "test@example.com", "password": "password123", "username": "testuser"},
        {"email": "test@example.com", "password": "123", "username": "testuser"}
    ]
    
    for i, data in enumerate(test_data, 1):
        print(f"\n  Form {i} validation:")
        errors = validate_registration_form(data)
        if errors:
            for error in errors:
                print(f"    - {error.user_message}")
        else:
            print("    - Valid form")
    
    print("\n2. API Error Handling Pattern:")
    
    async def make_api_request(endpoint: str, method: str = "GET") -> Dict[str, Any]:
        """Simulate API request with error handling"""
        
        # Simulate different error scenarios
        scenarios = [
            (api_factory.timeout(endpoint, method, 30), "timeout"),
            (api_factory.rate_limited(endpoint, method, 60), "rate_limit"),
            (api_factory.server_error(endpoint, method, 500, {"error": "internal"}), "server_error")
        ]
        
        # Randomly select an error scenario
        error, scenario = random.choice(scenarios)
        
        # Simulate error occurrence
        if random.random() < 0.7:  # 70% chance of error
            raise error
        
        return {"status": "success", "data": {"message": "API call successful"}}
    
    # Test API error handling
    endpoints = ["/api/users", "/api/data", "/api/payment"]
    
    for endpoint in endpoints:
        print(f"\n  API request to {endpoint}:")
        try:
            result = make_api_request(endpoint)
            print(f"    Success: {result}")
        except Exception as e:
            print(f"    Error: {e.user_message}")
            print(f"    Status: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
    
    print("\n3. ML Training Error Pattern:")
    
    def train_ml_model(model_name: str, data_path: str) -> Dict[str, Any]:
        """Simulate ML model training with error handling"""
        
        # Simulate different training error scenarios
        scenarios = [
            (ml_factory.gpu_memory_exceeded(model_name, "8GB", "4GB"), "gpu_memory"),
            (ml_factory.convergence_failed(model_name, 100, 0.85), "convergence"),
            (ml_factory.data_loading_failed(model_name, data_path, "File not found"), "data_loading")
        ]
        
        # Simulate error occurrence
        if random.random() < 0.6:  # 60% chance of error
            error, scenario = random.choice(scenarios)
            raise error
        
        return {"status": "success", "model_name": model_name, "accuracy": 0.95}
    
    # Test ML training error handling
    models = ["bert-large", "cnn-model", "transformer"]
    
    for model in models:
        print(f"\n  Training {model}:")
        try:
            result = train_ml_model(model, f"/data/{model}.csv")
            print(f"    Success: {result}")
        except Exception as e:
            print(f"    Error: {e.user_message}")
            print(f"    Model: {e.model_name if hasattr(e, 'model_name') else 'N/A'}")
            print(f"    Step: {e.training_step if hasattr(e, 'training_step') else 'N/A'}")


def main():
    """Main function to run all custom error factory demonstrations"""
    print("Custom Error Types and Error Factories Demonstrations")
    print("=" * 80)
    
    try:
        # Core demonstrations
        demonstrate_custom_error_types()
        demonstrate_error_factories()
        demonstrate_error_builder()
        demonstrate_error_registry()
        demonstrate_domain_specific_errors()
        
        # Advanced demonstrations
        demonstrate_configurable_factory()
        demonstrate_error_context_manager()
        demonstrate_error_decorators()
        demonstrate_error_patterns()
        
        print("\n" + "="*80)
        print("All Custom Error Types and Error Factories Demonstrations Completed Successfully!")
        print("="*80)
        
        print("\n🎯 Key Benefits Demonstrated:")
        print("  ✅ Consistent error creation patterns")
        print("  ✅ Domain-specific error types")
        print("  ✅ Fluent builder interfaces")
        print("  ✅ Factory registry for centralized management")
        print("  ✅ Configurable error factories")
        print("  ✅ Context-aware error handling")
        print("  ✅ Decorator-based error management")
        print("  ✅ Reusable error patterns")
        
    except Exception as e:
        print(f"\nError during demonstrations: {str(e)}")
        traceback.print_exc()
        raise


match __name__:
    case "__main__":
    main() 