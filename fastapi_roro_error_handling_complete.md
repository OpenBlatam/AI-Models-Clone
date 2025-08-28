# FastAPI RORO Integration with Comprehensive Error Handling - Complete Documentation

## Overview

This document provides comprehensive documentation for the enhanced FastAPI integration that implements the RORO (Receive an Object, Return an Object) pattern with comprehensive error handling, custom error types, error factories, and user-friendly error messages.

## 🎯 **Core Features**

### ✅ **Custom Error Types and Enums**
The implementation includes a comprehensive error classification system:

#### **Error Severity Levels**
```python
class ErrorSeverity(Enum):
    """Error severity levels for logging and handling."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

#### **Error Categories**
```python
class ErrorCategory(Enum):
    """Error categories for classification and handling."""
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RESOURCE_NOT_FOUND = "resource_not_found"
    NETWORK = "network"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL_SERVER = "internal_server"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    UNKNOWN = "unknown"
```

#### **Error Codes**
```python
class ErrorCode(Enum):
    """Error codes for consistent error handling."""
    # Validation Errors
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_DATA_TYPE = "INVALID_DATA_TYPE"
    INVALID_FORMAT = "INVALID_FORMAT"
    
    # Configuration Errors
    CONFIG_NOT_FOUND = "CONFIG_NOT_FOUND"
    CONFIG_INVALID = "CONFIG_INVALID"
    CONFIG_MISSING = "CONFIG_MISSING"
    
    # Resource Errors
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    TRAINING_NOT_FOUND = "TRAINING_NOT_FOUND"
    RESOURCE_NOT_AVAILABLE = "RESOURCE_NOT_AVAILABLE"
    
    # System Errors
    COMPONENT_NOT_AVAILABLE = "COMPONENT_NOT_AVAILABLE"
    SYSTEM_NOT_INITIALIZED = "SYSTEM_NOT_INITIALIZED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    
    # External Service Errors
    EXTERNAL_SERVICE_UNAVAILABLE = "EXTERNAL_SERVICE_UNAVAILABLE"
    EXTERNAL_SERVICE_TIMEOUT = "EXTERNAL_SERVICE_TIMEOUT"
    
    # Authentication/Authorization Errors
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_TOKEN = "INVALID_TOKEN"
    
    # Rate Limiting Errors
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
```

### ✅ **Custom Error Classes**

#### **Base API Error**
```python
class APIError(Exception):
    """Base custom error class for API errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        http_status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.user_message = user_message or message
        self.http_status_code = http_status_code
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        return {
            "error": {
                "code": self.error_code.value,
                "category": self.category.value,
                "severity": self.severity.value,
                "message": self.user_message,
                "details": self.details,
                "timestamp": self.timestamp.isoformat(),
                "traceback": self.traceback if self.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else None
            }
        }
```

#### **Specialized Error Types**
- **`ValidationError`**: For input validation failures
- **`ConfigurationError`**: For configuration issues
- **`ResourceNotFoundError`**: For missing resources
- **`ComponentError`**: For component availability issues
- **`SystemError`**: For system-level issues

### ✅ **Error Factory Pattern**

#### **Error Factory Class**
```python
class ErrorFactory:
    """Factory for creating consistent errors with proper logging."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def create_validation_error(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationError:
        """Create a validation error with proper logging."""
        error = ValidationError(message, field, value)
        self._log_error(error, context)
        return error
    
    def create_configuration_error(
        self,
        message: str,
        config_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ConfigurationError:
        """Create a configuration error with proper logging."""
        error = ConfigurationError(message, config_path)
        self._log_error(error, context)
        return error
    
    def create_resource_not_found_error(
        self,
        resource_type: str,
        resource_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ResourceNotFoundError:
        """Create a resource not found error with proper logging."""
        error = ResourceNotFoundError(resource_type, resource_id)
        self._log_error(error, context)
        return error
    
    def create_component_error(
        self,
        component_name: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ComponentError:
        """Create a component error with proper logging."""
        error = ComponentError(component_name, reason)
        self._log_error(error, context)
        return error
    
    def create_system_error(
        self,
        message: str,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> SystemError:
        """Create a system error with proper logging."""
        error = SystemError(message, operation)
        self._log_error(error, context)
        return error
    
    def create_generic_error(
        self,
        message: str,
        error_code: ErrorCode,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        http_status_code: int = 500,
        context: Optional[Dict[str, Any]] = None
    ) -> APIError:
        """Create a generic API error with proper logging."""
        error = APIError(
            message=message,
            error_code=error_code,
            category=category,
            severity=severity,
            details=details,
            user_message=user_message,
            http_status_code=http_status_code
        )
        self._log_error(error, context)
        return error
    
    def _log_error(self, error: APIError, context: Optional[Dict[str, Any]] = None):
        """Log error with appropriate level based on severity."""
        log_message = f"[{error.error_code.value}] {error.message}"
        
        if context:
            log_message += f" | Context: {json.dumps(context)}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, exc_info=True)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message, exc_info=True)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
```

### ✅ **Enhanced Guard Clause Validator**

#### **Guard Clause Validator with Error Factory**
```python
class GuardClauseValidator:
    """Utility class for implementing guard clauses with custom error handling."""
    
    def __init__(self, error_factory: ErrorFactory):
        self.error_factory = error_factory
    
    def validate_required_component(
        self,
        component: Any,
        component_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Guard clause for required component validation with custom error."""
        if component is None:
            raise self.error_factory.create_component_error(
                component_name=component_name,
                reason="Component is None",
                context=context
            )
    
    def validate_string_parameter(
        self,
        value: Any,
        param_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Guard clause for string parameter validation with custom error."""
        if value is None:
            raise self.error_factory.create_validation_error(
                message=f"{param_name} cannot be None",
                field=param_name,
                context=context
            )
        if not isinstance(value, str):
            raise self.error_factory.create_validation_error(
                message=f"{param_name} must be a string, got {type(value).__name__}",
                field=param_name,
                value=value,
                context=context
            )
        if not value.strip():
            raise self.error_factory.create_validation_error(
                message=f"{param_name} cannot be empty",
                field=param_name,
                value=value,
                context=context
            )
```

## 🏗️ **Architecture Components**

### **1. Custom Exception Handlers**

#### **API Error Handler**
```python
@self.app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Handle custom API errors with proper logging and user-friendly responses."""
    # Log the error
    if self.logger:
        self.logger.error(f"API Error: {exc.message}", exc_info=True)
    
    # Return consistent error response
    return JSONResponse(
        status_code=exc.http_status_code,
        content={
            "is_successful": False,
            "error": exc.to_dict()["error"],
            "metadata": {
                "request_path": str(request.url),
                "request_method": request.method,
                "timestamp": datetime.now().isoformat()
            }
        }
    )
```

#### **Validation Error Handler**
```python
@self.app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors with detailed information."""
    if self.logger:
        self.logger.warning(f"Validation Error: {exc.message}")
    
    return JSONResponse(
        status_code=400,
        content={
            "is_successful": False,
            "error": exc.to_dict()["error"],
            "metadata": {
                "request_path": str(request.url),
                "request_method": request.method,
                "validation_details": exc.details
            }
        }
    )
```

#### **Generic Error Handler**
```python
@self.app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    """Handle unexpected errors with proper logging."""
    # Create a system error for unexpected exceptions
    system_error = self.error_factory.create_system_error(
        message=str(exc),
        operation="unexpected_exception",
        context={
            "request_path": str(request.url),
            "request_method": request.method,
            "exception_type": type(exc).__name__
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "is_successful": False,
            "error": system_error.to_dict()["error"],
            "metadata": {
                "request_path": str(request.url),
                "request_method": request.method,
                "timestamp": datetime.now().isoformat()
            }
        }
    )
```

### **2. Enhanced Route Handlers with Error Handling**

#### **Root Endpoint with Error Handling**
```python
@self.app.get("/", response_model=HealthCheckResponse)
async def root():
    """Root endpoint with health check using comprehensive error handling."""
    try:
        # Guard clause for application state
        self.guard_validator.validate_application_state(self, {
            "endpoint": "root",
            "operation": "health_check"
        })
        
        uptime = time.time() - self.start_time
        
        return HealthCheckResponse(
            is_successful=True,
            result={"message": "Enhanced Deep Learning API with RORO Pattern and Comprehensive Error Handling"},
            status="healthy",
            version="1.0.0",
            uptime=uptime,
            metadata={
                "framework": "FastAPI",
                "pattern": "RORO",
                "error_handling": "comprehensive",
                "device": str(self.device_manager('auto')) if self.device_manager else "unknown"
            }
        )
    
    except APIError as e:
        # Re-raise for custom exception handler
        raise
    except Exception as e:
        # Convert to system error
        raise self.error_factory.create_system_error(
            message=f"Root endpoint error: {str(e)}",
            operation="root_health_check"
        )
```

#### **Model Information Endpoint with Error Handling**
```python
@self.app.post("/model/info", response_model=ROROResponse)
async def get_model_info(request: ModelInfoRequest):
    """Get model information using RORO pattern with comprehensive error handling."""
    try:
        model_id = request.model_id or request.params.get('model_id')
        
        # Guard clause for model ID validation
        self.guard_validator.validate_string_parameter(
            model_id, "Model ID", {
                "endpoint": "model_info",
                "request_params": request.params
            }
        )
        
        # Get model info using RORO pattern
        model_info_result = self._get_model_info_roro({
            'model_id': model_id,
            'include_parameters': request.include_parameters,
            'include_architecture': request.include_architecture
        })
        
        if not model_info_result['is_successful']:
            raise self.error_factory.create_generic_error(
                message=model_info_result['error'],
                error_code=ErrorCode.MODEL_NOT_FOUND,
                category=ErrorCategory.RESOURCE_NOT_FOUND,
                severity=ErrorSeverity.LOW,
                context={"endpoint": "model_info", "model_id": model_id}
            )
        
        return ROROResponse(
            is_successful=True,
            result=model_info_result['result'],
            metadata={
                "model_id": model_id,
                "requested_info": {
                    "parameters": request.include_parameters,
                    "architecture": request.include_architecture
                },
                "error_handling": "comprehensive"
            }
        )
    
    except APIError as e:
        raise
    except Exception as e:
        raise self.error_factory.create_system_error(
            message=f"Model info error: {str(e)}",
            operation="get_model_info"
        )
```

## 📋 **Error Response Format**

### **Standard Error Response Structure**
```json
{
    "is_successful": false,
    "error": {
        "code": "MODEL_NOT_FOUND",
        "category": "resource_not_found",
        "severity": "low",
        "message": "Model with ID 'transformer_model' not found",
        "details": {
            "resource_type": "Model",
            "resource_id": "transformer_model"
        },
        "timestamp": "2024-01-15T10:30:45.123456",
        "traceback": null
    },
    "metadata": {
        "request_path": "http://localhost:8000/model/info",
        "request_method": "POST",
        "timestamp": "2024-01-15T10:30:45.123456"
    }
}
```

### **Error Severity-Based Logging**
- **CRITICAL**: Full traceback logged with critical level
- **HIGH**: Full traceback logged with error level
- **MEDIUM**: Warning level logging
- **LOW**: Info level logging

## 🚀 **Benefits of Comprehensive Error Handling**

### **1. Consistent Error Responses**
- **Standardized Format**: All errors follow the same structure
- **User-Friendly Messages**: Clear, actionable error messages
- **Detailed Context**: Rich metadata for debugging
- **Proper HTTP Status Codes**: Appropriate status codes for each error type

### **2. Comprehensive Logging**
- **Severity-Based Logging**: Different log levels based on error severity
- **Context Information**: Rich context for debugging
- **Traceback Management**: Full tracebacks for critical errors only
- **Structured Logging**: JSON-formatted log messages

### **3. Error Classification**
- **Categorized Errors**: Errors classified by type and severity
- **Error Codes**: Consistent error codes for programmatic handling
- **Error Categories**: Logical grouping of related errors
- **Severity Levels**: Appropriate handling based on error impact

### **4. User-Friendly Error Messages**
- **Clear Descriptions**: Easy-to-understand error messages
- **Actionable Information**: Guidance on how to fix the error
- **Context Preservation**: Maintains technical details for debugging
- **Localized Messages**: User-appropriate vs. technical messages

### **5. Production Readiness**
- **Graceful Degradation**: System continues to function when possible
- **Error Recovery**: Proper error handling and recovery mechanisms
- **Monitoring Integration**: Error tracking for monitoring systems
- **Debugging Support**: Rich error information for troubleshooting

## 📊 **Usage Examples**

### **Example 1: Validation Error**
```python
# Request with invalid model_id
{
    "model_id": None,
    "include_parameters": true
}

# Error Response
{
    "is_successful": false,
    "error": {
        "code": "INVALID_INPUT",
        "category": "validation",
        "severity": "low",
        "message": "Validation error: Model ID cannot be None",
        "details": {
            "field": "Model ID",
            "value": null
        },
        "timestamp": "2024-01-15T10:30:45.123456"
    }
}
```

### **Example 2: Resource Not Found Error**
```python
# Request for non-existent model
{
    "model_id": "non_existent_model",
    "include_parameters": true
}

# Error Response
{
    "is_successful": false,
    "error": {
        "code": "MODEL_NOT_FOUND",
        "category": "resource_not_found",
        "severity": "low",
        "message": "Model with ID 'non_existent_model' not found",
        "details": {
            "resource_type": "Model",
            "resource_id": "non_existent_model"
        },
        "timestamp": "2024-01-15T10:30:45.123456"
    }
}
```

### **Example 3: System Error**
```python
# Internal system error
{
    "is_successful": false,
    "error": {
        "code": "INTERNAL_ERROR",
        "category": "internal_server",
        "severity": "critical",
        "message": "An internal system error occurred. Please try again later.",
        "details": {
            "operation": "perform_inference"
        },
        "timestamp": "2024-01-15T10:30:45.123456",
        "traceback": "Traceback (most recent call last):\n..."
    }
}
```

## 🔧 **Error Factory Usage**

### **Creating Specific Error Types**
```python
# Validation Error
validation_error = error_factory.create_validation_error(
    message="Invalid input data",
    field="input_data",
    value=invalid_data,
    context={"endpoint": "inference", "operation": "predict"}
)

# Configuration Error
config_error = error_factory.create_configuration_error(
    message="Configuration file not found",
    config_path="/path/to/config.yaml",
    context={"operation": "load_config"}
)

# Resource Not Found Error
resource_error = error_factory.create_resource_not_found_error(
    resource_type="Model",
    resource_id="transformer_model",
    context={"endpoint": "model_info"}
)

# Component Error
component_error = error_factory.create_component_error(
    component_name="Metric Tracker",
    reason="Failed to initialize",
    context={"operation": "setup_dependencies"}
)

# System Error
system_error = error_factory.create_system_error(
    message="Unexpected error during training",
    operation="start_training",
    context={"training_id": "training_123"}
)
```

### **Creating Generic Errors**
```python
# Generic API Error
generic_error = error_factory.create_generic_error(
    message="Custom error message",
    error_code=ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE,
    category=ErrorCategory.EXTERNAL_SERVICE,
    severity=ErrorSeverity.HIGH,
    details={"service": "external_api", "endpoint": "/api/data"},
    user_message="External service is temporarily unavailable",
    http_status_code=503,
    context={"operation": "fetch_external_data"}
)
```

## 🎯 **Best Practices Implemented**

### **1. Error Classification**
- **Consistent Categories**: Logical grouping of error types
- **Severity Levels**: Appropriate handling based on impact
- **Error Codes**: Programmatic error identification
- **Context Preservation**: Rich metadata for debugging

### **2. User-Friendly Messages**
- **Clear Descriptions**: Easy-to-understand error messages
- **Actionable Guidance**: Help users understand how to fix issues
- **Technical Details**: Preserved for debugging when needed
- **Localized Content**: User-appropriate vs. technical messages

### **3. Comprehensive Logging**
- **Severity-Based**: Different log levels for different error types
- **Context Rich**: Detailed context information for debugging
- **Structured Format**: Consistent log message structure
- **Traceback Management**: Full tracebacks for critical errors

### **4. Production Readiness**
- **Graceful Degradation**: System continues to function when possible
- **Error Recovery**: Proper error handling and recovery
- **Monitoring Integration**: Error tracking for observability
- **Debugging Support**: Rich error information for troubleshooting

### **5. Consistent Error Handling**
- **Standardized Responses**: All errors follow the same format
- **Proper HTTP Codes**: Appropriate status codes for each error
- **Error Factory Pattern**: Consistent error creation
- **Exception Handlers**: Centralized error processing

## 🚀 **Getting Started**

### **1. Installation**
```bash
pip install fastapi uvicorn pydantic torch numpy
```

### **2. Basic Usage**
```python
from fastapi_roro_error_handling import create_fastapi_roro_app

# Create the application
app = create_fastapi_roro_app()

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app.app, host="0.0.0.0", port=8000)
```

### **3. API Documentation**
- **Swagger UI**: Available at `http://localhost:8000/docs`
- **ReDoc**: Available at `http://localhost:8000/redoc`
- **Health Check**: Available at `http://localhost:8000/health`

## 📈 **Performance Benefits**

### **1. Improved Error Handling**
- **Fast Error Detection**: Errors caught and handled early
- **Reduced Debugging Time**: Rich error information
- **Better User Experience**: Clear, actionable error messages
- **Production Stability**: Graceful error handling

### **2. Enhanced Monitoring**
- **Structured Logging**: Easy to parse and analyze
- **Error Tracking**: Comprehensive error metrics
- **Debugging Support**: Rich context information
- **Alerting Integration**: Severity-based alerting

### **3. Maintainable Code**
- **Consistent Patterns**: Standardized error handling
- **Reusable Components**: Error factory and validators
- **Clear Separation**: Technical vs. user messages
- **Easy Extension**: Simple to add new error types

## 🔧 **Extending the System**

### **Adding New Error Types**
```python
class CustomError(APIError):
    """Custom error for specific use case."""
    
    def __init__(self, custom_field: str, custom_value: Any):
        super().__init__(
            message=f"Custom error: {custom_field}",
            error_code=ErrorCode.INVALID_INPUT,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            details={"custom_field": custom_field, "custom_value": custom_value},
            user_message="A custom error occurred",
            http_status_code=400
        )
```

### **Adding New Error Factory Methods**
```python
def create_custom_error(
    self,
    custom_field: str,
    custom_value: Any,
    context: Optional[Dict[str, Any]] = None
) -> CustomError:
    """Create a custom error with proper logging."""
    error = CustomError(custom_field, custom_value)
    self._log_error(error, context)
    return error
```

### **Adding New Exception Handlers**
```python
@self.app.exception_handler(CustomError)
async def custom_error_handler(request: Request, exc: CustomError):
    """Handle custom errors with specific logic."""
    if self.logger:
        self.logger.warning(f"Custom Error: {exc.message}")
    
    return JSONResponse(
        status_code=exc.http_status_code,
        content={
            "is_successful": False,
            "error": exc.to_dict()["error"],
            "metadata": {
                "request_path": str(request.url),
                "request_method": request.method,
                "custom_handler": True
            }
        }
    )
```

## 🎉 **Conclusion**

This enhanced FastAPI integration with comprehensive error handling provides:

1. **Robust Error Management**: Custom error types and error factories
2. **User-Friendly Messages**: Clear, actionable error responses
3. **Comprehensive Logging**: Severity-based logging with rich context
4. **Production Readiness**: Graceful error handling and recovery
5. **Consistent Patterns**: Standardized error handling across the application
6. **Extensibility**: Easy to add new error types and handlers

The implementation successfully combines the RORO pattern with comprehensive error handling to create a modern, maintainable, and production-ready API system that provides excellent user experience and developer support. 