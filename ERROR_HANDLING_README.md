# Error Handling and Input Validation System for Gradio Applications

## Overview

This comprehensive error handling system provides robust error management, input validation, and debugging capabilities for Gradio-based diffusion model interfaces. It ensures your applications are reliable, user-friendly, and maintainable.

## Features

### 🚨 **Comprehensive Error Handling**
- **Custom Exception Classes**: `ValidationError`, `ProcessingError` with severity levels
- **Error Severity Levels**: LOW, MEDIUM, HIGH, CRITICAL
- **Centralized Error Handler**: Tracks, logs, and manages all errors
- **User-Friendly Error Messages**: Clear, actionable error information

### 🔍 **Input Validation**
- **Prompt Validation**: Length, content, and format checking
- **Parameter Validation**: Guidance scale, inference steps, dimensions
- **Image Input Validation**: Format, size, and content verification
- **Harmful Content Detection**: Prevents malicious input

### 🛠️ **Developer Tools**
- **Error Monitoring Dashboard**: Real-time error tracking and statistics
- **Debugging Decorators**: Easy error handling and validation integration
- **Error History**: Persistent error logging and analysis
- **Performance Metrics**: Error frequency and impact analysis

## Architecture

### Core Components

```python
# Error severity levels
class ErrorSeverity(Enum):
    LOW = "low"           # Minor issues, warnings
    MEDIUM = "medium"     # Standard errors
    HIGH = "high"         # Serious issues
    CRITICAL = "critical" # Application-breaking errors

# Custom exceptions
class ValidationError(Exception):
    """Raised when input validation fails"""
    
class ProcessingError(Exception):
    """Raised when processing operations fail"""

# Error information container
@dataclass
class ErrorInfo:
    error_type: str
    message: str
    field: Optional[str] = None
    operation: Optional[str] = None
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    timestamp: float = None
    traceback: str = None
```

### Error Handler

```python
class ErrorHandler:
    """Centralized error handling for Gradio applications"""
    
    def handle_error(self, error: Exception, context: str = None) -> ErrorInfo:
        """Handle an error and return error information"""
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
    
    def clear_history(self):
        """Clear error history"""
```

### Input Validator

```python
class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_prompt(prompt: str, min_length: int = 3, max_length: int = 500) -> str:
        """Validate text prompt"""
    
    @staticmethod
    def validate_guidance_scale(value: float, min_val: float = 1.0, max_val: float = 20.0) -> float:
        """Validate guidance scale parameter"""
    
    @staticmethod
    def validate_inference_steps(value: int, min_val: int = 1, max_val: int = 200) -> int:
        """Validate inference steps parameter"""
    
    @staticmethod
    def validate_image_dimensions(width: int, height: int, min_size: int = 64, max_size: int = 2048) -> Tuple[int, int]:
        """Validate image dimensions"""
```

## Usage

### Basic Error Handling

```python
from core.gradio_error_handling import error_handler_decorator, ErrorHandler

# Create error handler
error_handler = ErrorHandler()

# Use decorator for automatic error handling
@error_handler_decorator("image_generation")
def generate_image(prompt: str):
    try:
        # Your generation logic here
        return generated_image
    except Exception as e:
        # Error is automatically handled by decorator
        raise
```

### Input Validation

```python
from core.gradio_error_handling import validation_decorator, InputValidator

# Apply validation rules
@validation_decorator({
    "prompt": InputValidator.validate_prompt,
    "guidance_scale": InputValidator.validate_guidance_scale,
    "inference_steps": InputValidator.validate_inference_steps
})
def safe_generation(prompt: str, guidance_scale: float, inference_steps: int):
    # Input is automatically validated before execution
    return generate_image(prompt, guidance_scale, inference_steps)
```

### Combined Error Handling and Validation

```python
@error_handler_decorator("text_to_image")
@validation_decorator({
    "prompt": InputValidator.validate_prompt,
    "guidance_scale": InputValidator.validate_guidance_scale,
    "inference_steps": InputValidator.validate_inference_steps
})
def safe_text_to_image_generation(prompt: str, guidance_scale: float, inference_steps: int):
    """Safe text-to-image generation with comprehensive error handling"""
    # Both validation and error handling are automatic
    return generate_image(prompt, guidance_scale, inference_steps)
```

## Gradio Integration

### Error Monitoring Tab

```python
from core.gradio_error_handling import GradioErrorHandler

# Add error monitoring to your interface
with gr.Tabs():
    # Your existing tabs...
    
    # Add error monitoring
    GradioErrorHandler.create_error_tab()
```

### Error Notifications

```python
from core.gradio_error_handling import GradioErrorHandler

# Create error notification component
error_notification = GradioErrorHandler.create_error_notification(error_info)
```

### Error Response Format

The system automatically creates standardized error responses:

```python
# Error response includes:
{
    "error": True,
    "error_type": "ValidationError",
    "message": "Prompt must be at least 3 characters long",
    "field": "prompt",
    "severity": "medium",
    "timestamp": 1234567890.123,
    "suggestions": [
        "Make sure your prompt is between 3-500 characters",
        "Use clear, descriptive language"
    ]
}
```

## Validation Rules

### Prompt Validation
- **Length**: 3-500 characters
- **Content**: Non-empty, non-harmful
- **Format**: String type
- **Security**: Blocks potentially harmful patterns

### Parameter Validation
- **Guidance Scale**: 1.0-20.0 (float)
- **Inference Steps**: 1-200 (integer)
- **Image Dimensions**: 64-2048 pixels (multiples of 64 recommended)
- **Seed**: -1 (random) or non-negative integer

### Image Validation
- **Format**: PIL Image, numpy array, or file path
- **Size**: Within specified bounds
- **Content**: Valid image data

## Error Severity Classification

### LOW
- Minor warnings
- Non-critical parameter issues
- Informational messages

### MEDIUM
- Standard validation errors
- Parameter range violations
- Format issues

### HIGH
- Security concerns
- Critical parameter failures
- Processing errors

### CRITICAL
- Application crashes
- System failures
- Unrecoverable errors

## Best Practices

### 1. **Use Decorators Consistently**
```python
# Always apply error handling and validation decorators
@error_handler_decorator("function_name")
@validation_decorator(validation_rules)
def your_function():
    pass
```

### 2. **Provide Context**
```python
# Always provide meaningful context for error handling
@error_handler_decorator("image_generation")
def generate_image():
    pass
```

### 3. **Handle Specific Errors**
```python
try:
    result = process_input(input_data)
except ValidationError as e:
    # Handle validation errors specifically
    handle_validation_error(e)
except ProcessingError as e:
    # Handle processing errors specifically
    handle_processing_error(e)
```

### 4. **Log Errors Appropriately**
```python
# Errors are automatically logged, but you can add custom logging
logger.info(f"Processing {input_type} with parameters: {params}")
```

### 5. **Provide User Feedback**
```python
# Use error notifications to inform users
error_notification = GradioErrorHandler.create_error_notification(error_info)
```

## Configuration

### Error Handler Settings

```python
# Configure error handler
error_handler = ErrorHandler()
error_handler.max_error_history = 200  # Store more errors
```

### Validation Rules Customization

```python
# Custom validation rules
custom_validation = {
    "prompt": lambda x: InputValidator.validate_prompt(x, min_length=5, max_length=300),
    "custom_param": lambda x: validate_custom_parameter(x)
}
```

### Logging Configuration

```python
import logging

# Configure logging level
logging.basicConfig(level=logging.INFO)

# Custom logger for errors
error_logger = logging.getLogger("error_handler")
error_logger.setLevel(logging.ERROR)
```

## Monitoring and Debugging

### Error Dashboard Features

1. **Real-time Error Tracking**
   - Live error count and severity distribution
   - Recent error details with timestamps
   - Error frequency analysis

2. **Error Analysis**
   - Error type categorization
   - Field-specific error tracking
   - Performance impact assessment

3. **Debugging Tools**
   - Full error tracebacks
   - Context information
   - Error reproduction steps

### Error Statistics

```python
# Get comprehensive error statistics
stats = error_handler.get_error_summary()

# Example output:
{
    "total_errors": 15,
    "severity_distribution": {
        "low": 2,
        "medium": 8,
        "high": 4,
        "critical": 1
    },
    "recent_errors": [
        {
            "error_type": "ValidationError",
            "message": "Invalid prompt length",
            "field": "prompt",
            "severity": "medium",
            "timestamp": 1234567890.123
        }
    ]
}
```

## Integration Examples

### Basic Gradio Interface

```python
import gradio as gr
from core.gradio_error_handling import (
    error_handler_decorator, validation_decorator, InputValidator
)

@error_handler_decorator("text_to_image")
@validation_decorator({
    "prompt": InputValidator.validate_prompt,
    "guidance_scale": InputValidator.validate_guidance_scale
})
def generate_image(prompt: str, guidance_scale: float):
    # Your generation logic here
    return generated_image

# Create interface
with gr.Blocks() as demo:
    prompt_input = gr.Textbox(label="Prompt")
    guidance_input = gr.Slider(1, 20, 7.5, label="Guidance Scale")
    generate_button = gr.Button("Generate")
    output_image = gr.Image(label="Result")
    
    generate_button.click(
        fn=generate_image,
        inputs=[prompt_input, guidance_input],
        outputs=[output_image]
    )

demo.launch()
```

### Advanced Interface with Error Monitoring

```python
import gradio as gr
from core.gradio_error_handling import GradioErrorHandler

def create_advanced_interface():
    with gr.Blocks() as demo:
        with gr.Tabs():
            # Main functionality
            with gr.Tab("Generate"):
                # Your generation interface
                pass
            
            # Error monitoring
            GradioErrorHandler.create_error_tab()
    
    return demo
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```python
   # Ensure proper import path
   from core.gradio_error_handling import InputValidator
   ```

2. **Validation Failures**
   ```python
   # Check validation rules
   try:
       InputValidator.validate_prompt("")
   except ValidationError as e:
       print(f"Validation failed: {e.message}")
   ```

3. **Error Handler Not Working**
   ```python
   # Ensure decorators are applied correctly
   @error_handler_decorator("context_name")
   def your_function():
       pass
   ```

### Debug Mode

```python
# Enable debug mode for detailed error information
import logging
logging.basicConfig(level=logging.DEBUG)

# Check error handler state
print(f"Total errors: {len(error_handler.error_history)}")
```

## Performance Considerations

### Error History Management
- **Default Limit**: 100 errors stored
- **Configurable**: Adjust based on memory constraints
- **Automatic Cleanup**: Old errors are automatically removed

### Validation Performance
- **Efficient Checks**: Minimal performance impact
- **Early Exit**: Validation stops on first failure
- **Caching**: Repeated validations are optimized

### Memory Usage
- **Error Storage**: Minimal memory footprint
- **Traceback Management**: Optional full traceback storage
- **Garbage Collection**: Automatic cleanup of old errors

## Security Features

### Input Sanitization
- **Harmful Pattern Detection**: Blocks malicious input
- **Content Filtering**: Prevents injection attacks
- **Size Limits**: Prevents resource exhaustion

### Error Information Control
- **Sensitive Data Filtering**: Removes sensitive information from error messages
- **User-Friendly Messages**: Provides helpful information without exposing internals
- **Audit Logging**: Tracks all validation and error events

## Future Enhancements

### Planned Features
1. **Machine Learning Error Prediction**
2. **Automated Error Resolution**
3. **Performance Impact Analysis**
4. **Integration with External Monitoring**
5. **Advanced Error Visualization**

### Extension Points
1. **Custom Validation Rules**
2. **Error Response Formatters**
3. **External Error Handlers**
4. **Error Recovery Strategies**

## Conclusion

This error handling and input validation system provides a robust foundation for building reliable Gradio applications. By implementing these patterns, you'll create applications that are:

- **Reliable**: Comprehensive error handling prevents crashes
- **User-Friendly**: Clear error messages guide users
- **Maintainable**: Centralized error management simplifies debugging
- **Secure**: Input validation prevents malicious attacks
- **Scalable**: Efficient error handling supports high-traffic applications

Start implementing these patterns in your Gradio applications today to build more robust and professional interfaces!
