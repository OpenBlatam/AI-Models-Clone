# Custom Error Types and Error Factories Implementation Summary

## Overview

This implementation provides **custom error types and error factories** for consistent error handling patterns. It builds upon the existing error logging system to create specialized error types, factory patterns for error creation, and domain-specific error handling.

## Key Features

### 1. Custom Error Types
- **Specialized error classes** for different domains and use cases
- **Rich error context** with domain-specific metadata
- **Consistent error patterns** across the application
- **Type-safe error handling** with proper inheritance

### 2. Error Factories
- **Factory pattern** for consistent error creation
- **Specialized factory classes** for different error types
- **Fluent builder interfaces** for complex error construction
- **Configuration-driven factories** for flexible error handling

### 3. Error Registry
- **Centralized factory management** with registry pattern
- **Default factory fallbacks** for unknown error types
- **Factory discovery** and registration mechanisms
- **Consistent error creation** across the application

### 4. Domain-Specific Errors
- **E-commerce errors** with order and product context
- **Financial errors** with transaction and account details
- **Healthcare errors** with HIPAA compliance
- **ML training errors** with model and training context

## Implementation Components

### Custom Error Types

#### 1. MLTrainingError
```python
class MLTrainingError(BaseAppException):
    """Machine Learning training specific error"""
    
    def __init__(
        self,
        message: str,
        user_message: str,
        model_name: str,
        training_step: str,
        epoch: Optional[int] = None,
        batch: Optional[int] = None,
        loss: Optional[float] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            user_message=user_message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            context=ErrorContext.MODEL_TRAINING,
            **kwargs
        )
        self.model_name = model_name
        self.training_step = training_step
        self.epoch = epoch
        self.batch = batch
        self.loss = loss
    
    def get_training_context(self) -> Dict[str, Any]:
        """Get training-specific context"""
        return {
            "model_name": self.model_name,
            "training_step": self.training_step,
            "epoch": self.epoch,
            "batch": self.batch,
            "loss": self.loss,
            "error_id": self.error_id,
            "timestamp": self.timestamp
        }
```

#### 2. DataProcessingError
```python
class DataProcessingError(BaseAppException):
    """Data processing specific error"""
    
    def __init__(
        self,
        message: str,
        user_message: str,
        data_source: str,
        processing_step: str,
        record_count: Optional[int] = None,
        failed_records: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            user_message=user_message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            context=ErrorContext.DATA_PROCESSING,
            **kwargs
        )
        self.data_source = data_source
        self.processing_step = processing_step
        self.record_count = record_count
        self.failed_records = failed_records or []
    
    def add_failed_record(self, record: Dict[str, Any], reason: str):
        """Add a failed record to the error context"""
        self.failed_records.append({
            "record": record,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get processing summary"""
        return {
            "data_source": self.data_source,
            "processing_step": self.processing_step,
            "total_records": self.record_count,
            "failed_records": len(self.failed_records),
            "success_rate": ((self.record_count - len(self.failed_records)) / self.record_count * 100) if self.record_count else 0
        }
```

#### 3. APIError
```python
class APIError(BaseAppException):
    """API-specific error with HTTP status codes"""
    
    def __init__(
        self,
        message: str,
        user_message: str,
        status_code: int,
        endpoint: str,
        method: str,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            user_message=user_message,
            severity=self._get_severity_from_status(status_code),
            category=ErrorCategory.EXTERNAL_API,
            context=ErrorContext.API_CALL,
            **kwargs
        )
        self.status_code = status_code
        self.endpoint = endpoint
        self.method = method
        self.request_data = request_data or {}
        self.response_data = response_data or {}
    
    def _get_severity_from_status(self, status_code: int) -> ErrorSeverity:
        """Map HTTP status code to error severity"""
        if status_code >= 500:
            return ErrorSeverity.HIGH
        elif status_code >= 400:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def get_api_context(self) -> Dict[str, Any]:
        """Get API-specific context"""
        return {
            "status_code": self.status_code,
            "endpoint": self.endpoint,
            "method": self.method,
            "request_data": self.request_data,
            "response_data": self.response_data
        }
```

### Error Factories

#### 1. ValidationErrorFactory
```python
class ValidationErrorFactory(ErrorFactory):
    """Factory for creating validation errors"""
    
    def __init__(self):
        self.error_type = ValidationError
    
    def create_error(self, **kwargs) -> ValidationError:
        """Create a validation error"""
        return ValidationError(**kwargs)
    
    def get_error_type(self) -> Type[BaseAppException]:
        return self.error_type
    
    def invalid_email(self, email: str, field: str = "email") -> ValidationError:
        """Create invalid email error"""
        return ValidationError(
            message=f"Invalid email format: {email}",
            user_message="Please enter a valid email address",
            field=field
        )
    
    def required_field(self, field: str) -> ValidationError:
        """Create required field error"""
        return ValidationError(
            message=f"Required field missing: {field}",
            user_message=f"The {field} field is required",
            field=field
        )
    
    def field_too_short(self, field: str, min_length: int, actual_length: int) -> ValidationError:
        """Create field too short error"""
        return ValidationError(
            message=f"Field {field} too short: {actual_length} < {min_length}",
            user_message=f"The {field} must be at least {min_length} characters long",
            field=field,
            additional_data={"min_length": min_length, "actual_length": actual_length}
        )
    
    def invalid_format(self, field: str, expected_format: str, actual_value: str) -> ValidationError:
        """Create invalid format error"""
        return ValidationError(
            message=f"Invalid format for {field}: {actual_value}, expected: {expected_format}",
            user_message=f"The {field} format is invalid. Expected: {expected_format}",
            field=field,
            additional_data={"expected_format": expected_format, "actual_value": actual_value}
        )
```

#### 2. MLTrainingErrorFactory
```python
class MLTrainingErrorFactory(ErrorFactory):
    """Factory for creating ML training errors"""
    
    def __init__(self):
        self.error_type = MLTrainingError
    
    def create_error(self, **kwargs) -> MLTrainingError:
        """Create an ML training error"""
        return MLTrainingError(**kwargs)
    
    def get_error_type(self) -> Type[BaseAppException]:
        return self.error_type
    
    def gpu_memory_exceeded(self, model_name: str, required_memory: str, available_memory: str) -> MLTrainingError:
        """Create GPU memory exceeded error"""
        return MLTrainingError(
            message=f"GPU memory exceeded for model {model_name}: required {required_memory}, available {available_memory}",
            user_message="Model training failed due to insufficient GPU memory. Please try with a smaller model or batch size.",
            model_name=model_name,
            training_step="memory_allocation",
            additional_data={"required_memory": required_memory, "available_memory": available_memory}
        )
    
    def convergence_failed(self, model_name: str, epochs: int, final_loss: float) -> MLTrainingError:
        """Create convergence failed error"""
        return MLTrainingError(
            message=f"Model {model_name} failed to converge after {epochs} epochs, final loss: {final_loss}",
            user_message="Model training failed to converge. Please check your data and hyperparameters.",
            model_name=model_name,
            training_step="convergence",
            epoch=epochs,
            loss=final_loss
        )
    
    def data_loading_failed(self, model_name: str, data_path: str, reason: str) -> MLTrainingError:
        """Create data loading failed error"""
        return MLTrainingError(
            message=f"Failed to load training data for model {model_name} from {data_path}: {reason}",
            user_message="Failed to load training data. Please check the data path and format.",
            model_name=model_name,
            training_step="data_loading",
            additional_data={"data_path": data_path, "reason": reason}
        )
```

### Error Builder Pattern

```python
class ErrorBuilder:
    """Fluent interface for building errors"""
    
    def __init__(self, error_type: Type[BaseAppException]):
        self.error_type = error_type
        self.message = ""
        self.user_message = ""
        self.severity = ErrorSeverity.MEDIUM
        self.category = ErrorCategory.UNKNOWN
        self.context = ErrorContext.USER_INPUT
        self.additional_data = {}
    
    def with_message(self, message: str) -> 'ErrorBuilder':
        """Set the technical message"""
        self.message = message
        return self
    
    def with_user_message(self, user_message: str) -> 'ErrorBuilder':
        """Set the user-friendly message"""
        self.user_message = user_message
        return self
    
    def with_severity(self, severity: ErrorSeverity) -> 'ErrorBuilder':
        """Set the error severity"""
        self.severity = severity
        return self
    
    def with_category(self, category: ErrorCategory) -> 'ErrorBuilder':
        """Set the error category"""
        self.category = category
        return self
    
    def with_context(self, context: ErrorContext) -> 'ErrorBuilder':
        """Set the error context"""
        self.context = context
        return self
    
    def with_data(self, key: str, value: Any) -> 'ErrorBuilder':
        """Add additional data"""
        self.additional_data[key] = value
        return self
    
    def build(self) -> BaseAppException:
        """Build and return the error"""
        return self.error_type(
            message=self.message,
            user_message=self.user_message,
            severity=self.severity,
            category=self.category,
            context=self.context,
            **self.additional_data
        )
```

### Error Factory Registry

```python
class ErrorFactoryRegistry:
    """Registry for managing error factories"""
    
    def __init__(self):
        self._factories: Dict[str, ErrorFactory] = {}
        self._default_factory: Optional[ErrorFactory] = None
    
    def register_factory(self, name: str, factory: ErrorFactory) -> None:
        """Register an error factory"""
        self._factories[name] = factory
    
    def get_factory(self, name: str) -> Optional[ErrorFactory]:
        """Get an error factory by name"""
        return self._factories.get(name)
    
    def set_default_factory(self, factory: ErrorFactory) -> None:
        """Set the default error factory"""
        self._default_factory = factory
    
    def create_error(self, factory_name: str, **kwargs) -> BaseAppException:
        """Create an error using a specific factory"""
        factory = self.get_factory(factory_name)
        if factory is None:
            if self._default_factory is None:
                raise ValueError(f"No factory found for '{factory_name}' and no default factory set")
            factory = self._default_factory
        
        return factory.create_error(**kwargs)
    
    def list_factories(self) -> List[str]:
        """List all registered factory names"""
        return list(self._factories.keys())
```

### Domain-Specific Error Types

#### 1. ECommerceError
```python
class ECommerceError(BaseAppException):
    """E-commerce specific error"""
    
    def __init__(
        self,
        message: str,
        user_message: str,
        order_id: Optional[str] = None,
        product_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            user_message=user_message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            context=ErrorContext.USER_INPUT,
            **kwargs
        )
        self.order_id = order_id
        self.product_id = product_id
        self.customer_id = customer_id
```

#### 2. FinancialError
```python
class FinancialError(BaseAppException):
    """Financial transaction specific error"""
    
    def __init__(
        self,
        message: str,
        user_message: str,
        transaction_id: Optional[str] = None,
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        account_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            user_message=user_message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            context=ErrorContext.USER_INPUT,
            **kwargs
        )
        self.transaction_id = transaction_id
        self.amount = amount
        self.currency = currency
        self.account_id = account_id
```

#### 3. HealthcareError
```python
class HealthcareError(BaseAppException):
    """Healthcare specific error with HIPAA compliance"""
    
    def __init__(
        self,
        message: str,
        user_message: str,
        patient_id: Optional[str] = None,
        provider_id: Optional[str] = None,
        service_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            user_message=user_message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            context=ErrorContext.USER_INPUT,
            **kwargs
        )
        self.patient_id = patient_id
        self.provider_id = provider_id
        self.service_type = service_type
    
    def get_hipaa_context(self) -> Dict[str, Any]:
        """Get HIPAA-compliant context (no PHI)"""
        return {
            "provider_id": self.provider_id,
            "service_type": self.service_type,
            "error_id": self.error_id,
            "timestamp": self.timestamp
        }
```

## Usage Examples

### Basic Factory Usage
```python
# Create factories
validation_factory = ValidationErrorFactory()
ml_factory = MLTrainingErrorFactory()
api_factory = APIErrorFactory()

# Create errors using factories
email_error = validation_factory.invalid_email("test@", "email")
gpu_error = ml_factory.gpu_memory_exceeded("bert-large", "8GB", "4GB")
timeout_error = api_factory.timeout("/api/users", "GET", 30)

print(f"Email error: {email_error.user_message}")
print(f"GPU error: {gpu_error.user_message}")
print(f"Timeout error: {timeout_error.user_message}")
```

### Error Builder Usage
```python
# Build a custom error using the builder pattern
custom_error = (ErrorBuilder(MLTrainingError)
               .with_message("Custom ML training error occurred")
               .with_user_message("Model training failed due to custom issue")
               .with_severity(ErrorSeverity.HIGH)
               .with_category(ErrorCategory.BUSINESS_LOGIC)
               .with_context(ErrorContext.MODEL_TRAINING)
               .with_data("model_name", "custom-model")
               .with_data("training_step", "custom_step")
               .with_data("epoch", 10)
               .build())

print(f"Custom error: {custom_error.user_message}")
print(f"Error data: {custom_error.additional_data}")
```

### Factory Registry Usage
```python
# Create registry
registry = ErrorFactoryRegistry()

# Register factories
registry.register_factory("validation", ValidationErrorFactory())
registry.register_factory("ml", MLTrainingErrorFactory())
registry.register_factory("api", APIErrorFactory())

# Set default factory
registry.set_default_factory(ValidationErrorFactory())

# Create errors using registry
validation_error = registry.create_error("validation", 
                                       message="Test validation error",
                                       user_message="Validation failed")

# Create error with unknown factory (uses default)
default_error = registry.create_error("unknown", 
                                    message="Test default error",
                                    user_message="Default error")

print(f"Registered factories: {registry.list_factories()}")
```

### Context Manager with Factories
```python
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

# Use context manager for automatic error conversion
try:
    with context_manager.error_context("ml"):
        # This will be automatically converted to ML error if exception occurs
        raise ValueError("GPU memory exceeded")
except MLTrainingError as e:
    print(f"Caught ML error: {e.user_message}")
    print(f"Context: {e.additional_data}")
```

### Error Decorators with Factories
```python
# Create registry
registry = ErrorFactoryRegistry()
registry.register_factory("validation", ValidationErrorFactory())
registry.register_factory("ml", MLTrainingErrorFactory())

# Function with automatic error handling
@handle_errors_with_factory("validation", registry)
def validate_user_data(data: Dict[str, Any]) -> bool:
    """Function that might raise validation errors"""
    if not data.get("email"):
        raise ValueError("Email is required")
    if not data.get("password"):
        raise ValueError("Password is required")
    return True

# Function with automatic error logging
@log_errors_with_factory("ml", registry, logger)
def train_model(model_name: str) -> bool:
    """Function that might raise ML errors"""
    if model_name == "large-model":
        raise RuntimeError("GPU memory exceeded")
    return True

# Test the functions
try:
    result = validate_user_data({"name": "John"})  # Missing email and password
except Exception as e:
    print(f"Caught error: {e.user_message}")
    print(f"Error type: {type(e).__name__}")
```

### Configurable Error Factory
```python
# Create configuration
config = ErrorFactoryConfig(
    enable_logging=True,
    enable_metrics=True,
    alert_on_critical=True,
    error_threshold=5
)

# Create configurable factory
factory = ConfigurableErrorFactory(ValidationError, config)

# Create multiple errors to test threshold
for i in range(7):
    error = factory.create_error(
        message=f"Test error {i}",
        user_message=f"Test error {i}"
    )
    print(f"Error {i}: {error.user_message}")
```

## Error Patterns

### Form Validation Pattern
```python
def validate_registration_form(data: Dict[str, Any]) -> List[Any]:
    """Validate registration form data"""
    errors = []
    validation_factory = ValidationErrorFactory()
    
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
    print(f"Form {i} validation:")
    errors = validate_registration_form(data)
    if errors:
        for error in errors:
            print(f"  - {error.user_message}")
    else:
        print("  - Valid form")
```

### API Error Handling Pattern
```python
def make_api_request(endpoint: str, method: str = "GET") -> Dict[str, Any]:
    """Simulate API request with error handling"""
    import random
    
    api_factory = APIErrorFactory()
    
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
    print(f"API request to {endpoint}:")
    try:
        result = make_api_request(endpoint)
        print(f"  Success: {result}")
    except Exception as e:
        print(f"  Error: {e.user_message}")
        print(f"  Status: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
```

### ML Training Error Pattern
```python
def train_ml_model(model_name: str, data_path: str) -> Dict[str, Any]:
    """Simulate ML model training with error handling"""
    import random
    
    ml_factory = MLTrainingErrorFactory()
    
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
    print(f"Training {model}:")
    try:
        result = train_ml_model(model, f"/data/{model}.csv")
        print(f"  Success: {result}")
    except Exception as e:
        print(f"  Error: {e.user_message}")
        print(f"  Model: {e.model_name if hasattr(e, 'model_name') else 'N/A'}")
        print(f"  Step: {e.training_step if hasattr(e, 'training_step') else 'N/A'}")
```

## Benefits

### 1. Consistent Error Creation
- **Standardized patterns** for creating errors across the application
- **Type-safe error handling** with proper inheritance
- **Consistent error messages** and user-friendly descriptions
- **Reusable error factories** for common error scenarios

### 2. Domain-Specific Error Handling
- **Specialized error types** for different domains (ML, API, E-commerce, etc.)
- **Rich error context** with domain-specific metadata
- **HIPAA compliance** for healthcare applications
- **Financial transaction safety** for payment processing

### 3. Flexible Error Management
- **Factory registry** for centralized error management
- **Configurable factories** for different environments
- **Builder pattern** for complex error construction
- **Context managers** for automatic error conversion

### 4. Improved Developer Experience
- **Fluent interfaces** for error creation
- **Decorator-based error handling** for simplified code
- **Factory discovery** and registration mechanisms
- **Comprehensive error patterns** for common scenarios

### 5. Production Readiness
- **Error threshold monitoring** with configurable limits
- **Automatic error conversion** for unknown exceptions
- **Context-aware error handling** with rich metadata
- **Performance optimized** error creation

## Best Practices

### 1. Error Factory Design
- **Single responsibility** for each factory
- **Consistent naming** conventions for factory methods
- **Default values** for common error scenarios
- **Extensible design** for new error types

### 2. Error Type Design
- **Rich context** with domain-specific metadata
- **Consistent inheritance** from base exception classes
- **Type-safe error handling** with proper type hints
- **User-friendly messages** separate from technical details

### 3. Registry Management
- **Centralized registration** of all error factories
- **Default factory fallbacks** for unknown error types
- **Factory discovery** mechanisms for dynamic loading
- **Consistent error creation** across the application

### 4. Error Patterns
- **Reusable patterns** for common error scenarios
- **Domain-specific patterns** for different business areas
- **Consistent error handling** across similar operations
- **Pattern documentation** for team adoption

## Conclusion

This custom error types and error factories implementation provides a comprehensive solution for consistent error handling across different domains and use cases. It combines specialized error types, factory patterns, builder interfaces, and registry management to create a robust and flexible error handling system.

Key benefits include:
- **Consistent error creation** with standardized patterns
- **Domain-specific error handling** with rich context
- **Flexible error management** with factory registry
- **Improved developer experience** with fluent interfaces
- **Production readiness** with monitoring and configuration

The implementation follows best practices for error handling and provides a solid foundation for building reliable, maintainable applications with consistent error management across different domains and use cases. 