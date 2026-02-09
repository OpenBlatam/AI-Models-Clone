"""
Error Handling and Input Validation for Gradio Applications
=========================================================

This module provides comprehensive error handling, input validation, and debugging
capabilities for Gradio-based diffusion model interfaces.
"""

import gradio as gr
import logging
import traceback
import time
import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from functools import wraps
from dataclasses import dataclass
from enum import Enum
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message: str, field: str = None, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        self.message = message
        self.field = field
        self.severity = severity
        super().__init__(self.message)

class ProcessingError(Exception):
    """Custom exception for processing errors."""
    def __init__(self, message: str, operation: str = None, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        self.message = message
        self.operation = operation
        self.severity = severity
        super().__init__(self.message)

@dataclass
class ErrorInfo:
    """Information about an error."""
    error_type: str
    message: str
    field: Optional[str] = None
    operation: Optional[str] = None
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    timestamp: float = None
    traceback: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_type": self.error_type,
            "message": self.message,
            "field": self.field,
            "operation": self.operation,
            "severity": self.severity.value,
            "timestamp": self.timestamp,
            "traceback": self.traceback
        }

class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_prompt(prompt: str, min_length: int = 3, max_length: int = 500) -> str:
        """Validate text prompt."""
        if not prompt or not isinstance(prompt, str):
            raise ValidationError("Prompt must be a non-empty string", "prompt", ErrorSeverity.HIGH)
        
        prompt = prompt.strip()
        if len(prompt) < min_length:
            raise ValidationError(f"Prompt must be at least {min_length} characters long", "prompt", ErrorSeverity.MEDIUM)
        
        if len(prompt) > max_length:
            raise ValidationError(f"Prompt must be no more than {max_length} characters long", "prompt", ErrorSeverity.MEDIUM)
        
        # Check for potentially harmful content
        harmful_patterns = [
            r'\b(hack|crack|steal|illegal|harmful)\b',
            r'<script>',
            r'javascript:',
            r'data:text/html'
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                raise ValidationError("Prompt contains potentially harmful content", "prompt", ErrorSeverity.HIGH)
        
        return prompt
    
    @staticmethod
    def validate_guidance_scale(value: float, min_val: float = 1.0, max_val: float = 20.0) -> float:
        """Validate guidance scale parameter."""
        if not isinstance(value, (int, float)):
            raise ValidationError("Guidance scale must be a number", "guidance_scale", ErrorSeverity.MEDIUM)
        
        if value < min_val or value > max_val:
            raise ValidationError(f"Guidance scale must be between {min_val} and {max_val}", "guidance_scale", ErrorSeverity.MEDIUM)
        
        return float(value)
    
    @staticmethod
    def validate_inference_steps(value: int, min_val: int = 1, max_val: int = 200) -> int:
        """Validate inference steps parameter."""
        if not isinstance(value, int):
            raise ValidationError("Inference steps must be an integer", "inference_steps", ErrorSeverity.MEDIUM)
        
        if value < min_val or value > max_val:
            raise ValidationError(f"Inference steps must be between {min_val} and {max_val}", "inference_steps", ErrorSeverity.MEDIUM)
        
        return int(value)
    
    @staticmethod
    def validate_image_dimensions(width: int, height: int, min_size: int = 64, max_size: int = 2048) -> Tuple[int, int]:
        """Validate image dimensions."""
        if not isinstance(width, int) or not isinstance(height, int):
            raise ValidationError("Width and height must be integers", "dimensions", ErrorSeverity.MEDIUM)
        
        if width < min_size or width > max_size:
            raise ValidationError(f"Width must be between {min_size} and {max_size} pixels", "width", ErrorSeverity.MEDIUM)
        
        if height < min_size or height > max_size:
            raise ValidationError(f"Height must be between {min_size} and {max_size} pixels", "height", ErrorSeverity.MEDIUM)
        
        # Check if dimensions are multiples of 64 (common requirement for diffusion models)
        if width % 64 != 0 or height % 64 != 0:
            logger.warning(f"Dimensions {width}x{height} are not multiples of 64, which may cause issues")
        
        return int(width), int(height)
    
    @staticmethod
    def validate_image_input(image: Any, required: bool = True) -> Optional[Image.Image]:
        """Validate image input."""
        if image is None:
            if required:
                raise ValidationError("Image is required", "image", ErrorSeverity.MEDIUM)
            return None
        
        if isinstance(image, Image.Image):
            return image
        elif isinstance(image, np.ndarray):
            try:
                return Image.fromarray(image)
            except Exception as e:
                raise ValidationError(f"Invalid image array: {str(e)}", "image", ErrorSeverity.MEDIUM)
        elif isinstance(image, str):
            try:
                return Image.open(image)
            except Exception as e:
                raise ValidationError(f"Invalid image path: {str(e)}", "image", ErrorSeverity.MEDIUM)
        else:
            raise ValidationError("Invalid image format", "image", ErrorSeverity.MEDIUM)
    
    @staticmethod
    def validate_seed(seed: Union[int, str]) -> int:
        """Validate random seed."""
        if isinstance(seed, str):
            if seed.lower() == "random":
                return -1
            try:
                seed = int(seed)
            except ValueError:
                raise ValidationError("Seed must be an integer or 'random'", "seed", ErrorSeverity.LOW)
        
        if not isinstance(seed, int):
            raise ValidationError("Seed must be an integer", "seed", ErrorSeverity.LOW)
        
        if seed < -1:
            raise ValidationError("Seed must be -1 (random) or a non-negative integer", "seed", ErrorSeverity.LOW)
        
        return seed

class ErrorHandler:
    """Centralized error handling for Gradio applications."""
    
    def __init__(self):
        self.error_history: List[ErrorInfo] = []
        self.max_error_history = 100
    
    def handle_error(self, error: Exception, context: str = None) -> ErrorInfo:
        """Handle an error and return error information."""
        error_info = ErrorInfo(
            error_type=type(error).__name__,
            message=str(error),
            operation=context,
            severity=self._determine_severity(error),
            traceback=traceback.format_exc()
        )
        
        # Log the error
        logger.error(f"Error in {context}: {error_info.message}")
        if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            logger.error(f"Traceback: {error_info.traceback}")
        
        # Store in history
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_error_history:
            self.error_history.pop(0)
        
        return error_info
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity based on error type."""
        if isinstance(error, ValidationError):
            return error.severity
        elif isinstance(error, ProcessingError):
            return error.severity
        elif isinstance(error, (ValueError, TypeError)):
            return ErrorSeverity.MEDIUM
        elif isinstance(error, (OSError, IOError)):
            return ErrorSeverity.HIGH
        else:
            return ErrorSeverity.MEDIUM
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors."""
        if not self.error_history:
            return {"total_errors": 0, "errors": []}
        
        severity_counts = {}
        for error in self.error_history:
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_errors": len(self.error_history),
            "severity_distribution": severity_counts,
            "recent_errors": [error.to_dict() for error in self.error_history[-10:]]
        }
    
    def clear_history(self):
        """Clear error history."""
        self.error_history.clear()

def error_handler_decorator(context: str = None):
    """Decorator for handling errors in Gradio functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get error handler instance
                error_handler = getattr(wrapper, '_error_handler', None)
                if error_handler is None:
                    error_handler = ErrorHandler()
                    wrapper._error_handler = error_handler
                
                # Handle the error
                error_info = error_handler.handle_error(e, context or func.__name__)
                
                # Return user-friendly error message
                return _create_error_response(error_info)
        
        return wrapper
    return decorator

def validation_decorator(validation_rules: Dict[str, Callable] = None):
    """Decorator for input validation."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Apply validation rules
                if validation_rules:
                    for field, validator in validation_rules.items():
                        if field in kwargs:
                            kwargs[field] = validator(kwargs[field])
                
                return func(*args, **kwargs)
            except ValidationError as e:
                return _create_validation_error_response(e)
            except Exception as e:
                return _create_error_response(ErrorInfo(
                    error_type="ValidationError",
                    message=str(e),
                    severity=ErrorSeverity.MEDIUM
                ))
        
        return wrapper
    return decorator

def _create_error_response(error_info: ErrorInfo) -> Tuple[Any, ...]:
    """Create a standardized error response for Gradio outputs."""
    # Create error image
    error_image = _create_error_image(error_info.message)
    
    # Create error info
    error_data = {
        "error": True,
        "error_type": error_info.error_type,
        "message": error_info.message,
        "severity": error_info.severity.value,
        "timestamp": error_info.timestamp,
        "suggestions": _get_error_suggestions(error_info)
    }
    
    # Return appropriate number of outputs based on function signature
    # This is a simplified approach - in practice, you'd need to inspect the function
    return error_image, error_data, 0, f"❌ Error: {error_info.message}"

def _create_validation_error_response(error: ValidationError) -> Tuple[Any, ...]:
    """Create a response for validation errors."""
    error_info = ErrorInfo(
        error_type="ValidationError",
        message=error.message,
        field=error.field,
        severity=error.severity
    )
    return _create_error_response(error_info)

def _create_error_image(message: str) -> Image.Image:
    """Create an error image for display."""
    width, height = 512, 512
    
    # Create error image
    img = Image.new('RGB', (width, height), color='#ffebee')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # Add error icon
    draw.ellipse([width//2 - 50, height//2 - 80, width//2 + 50, height//2 + 20], 
                 fill='#f44336', outline='#d32f2f', width=3)
    draw.text((width//2 - 10, height//2 - 60), "!", fill='white', font=font)
    
    # Add error message
    lines = _wrap_text(message, font, width - 40)
    y_offset = height//2 + 40
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y_offset), line, fill='#d32f2f', font=font)
        y_offset += 30
    
    return img

def _wrap_text(text: str, font, max_width: int) -> List[str]:
    """Wrap text to fit within max_width."""
    if not font:
        return [text]
    
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines[:5]  # Limit to 5 lines

def _get_error_suggestions(error_info: ErrorInfo) -> List[str]:
    """Get suggestions for resolving the error."""
    suggestions = []
    
    if error_info.error_type == "ValidationError":
        if error_info.field == "prompt":
            suggestions.extend([
                "Make sure your prompt is between 3-500 characters",
                "Avoid special characters or harmful content",
                "Use clear, descriptive language"
            ])
        elif error_info.field == "guidance_scale":
            suggestions.extend([
                "Use values between 1.0 and 20.0",
                "Lower values (1-5) for more creativity",
                "Higher values (10-20) for more precision"
            ])
        elif error_info.field == "inference_steps":
            suggestions.extend([
                "Use values between 10 and 100",
                "More steps = better quality but slower",
                "Fewer steps = faster but lower quality"
            ])
        elif error_info.field == "dimensions":
            suggestions.extend([
                "Use dimensions between 64 and 2048 pixels",
                "Multiples of 64 work best",
                "Square images (512x512) are recommended"
            ])
    elif error_info.error_type == "ProcessingError":
        suggestions.extend([
            "Check your internet connection",
            "Try reducing image dimensions",
            "Wait a moment and try again"
        ])
    else:
        suggestions.extend([
            "Check your input parameters",
            "Try refreshing the page",
            "Contact support if the problem persists"
        ])
    
    return suggestions

class GradioErrorHandler:
    """Gradio-specific error handling utilities."""
    
    @staticmethod
    def create_error_tab() -> gr.Tab:
        """Create an error monitoring tab."""
        with gr.Tab("🐛 Error Monitor", id="error_monitor"):
            gr.Markdown("### 🚨 Error Monitoring and Debugging")
            
            with gr.Row():
                with gr.Column(scale=1):
                    refresh_button = gr.Button("🔄 Refresh Error Log", variant="secondary")
                    clear_button = gr.Button("🗑️ Clear History", variant="secondary")
                    
                    gr.Markdown("#### 📊 Error Statistics")
                    error_stats = gr.JSON(label="Error Statistics", interactive=False)
                
                with gr.Column(scale=2):
                    gr.Markdown("#### 📝 Recent Errors")
                    error_log = gr.JSON(label="Error Log", interactive=False)
            
            # Event handlers
            refresh_button.click(
                fn=lambda: _get_error_handler().get_error_summary(),
                outputs=[error_stats, error_log]
            )
            
            clear_button.click(
                fn=lambda: _get_error_handler().clear_history(),
                outputs=[error_stats, error_log]
            )
        
        return gr.Tab("🐛 Error Monitor", id="error_monitor")
    
    @staticmethod
    def create_error_notification(error_info: ErrorInfo) -> gr.HTML:
        """Create an error notification component."""
        severity_colors = {
            ErrorSeverity.LOW: "#4caf50",
            ErrorSeverity.MEDIUM: "#ff9800",
            ErrorSeverity.HIGH: "#f44336",
            ErrorSeverity.CRITICAL: "#9c27b0"
        }
        
        color = severity_colors.get(error_info.severity, "#ff9800")
        
        html = f"""
        <div style="
            background: {color};
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <h4 style="margin: 0 0 10px 0;">⚠️ {error_info.error_type}</h4>
            <p style="margin: 0 0 10px 0;">{error_info.message}</p>
            <small style="opacity: 0.8;">
                Severity: {error_info.severity.value} | 
                Time: {time.strftime('%H:%M:%S', time.localtime(error_info.timestamp))}
            </small>
        </div>
        """
        
        return gr.HTML(html)

def _get_error_handler() -> ErrorHandler:
    """Get or create a global error handler."""
    if not hasattr(_get_error_handler, '_instance'):
        _get_error_handler._instance = ErrorHandler()
    return _get_error_handler._instance

# Example usage functions
@error_handler_decorator("text_to_image_generation")
@validation_decorator({
    "prompt": InputValidator.validate_prompt,
    "guidance_scale": InputValidator.validate_guidance_scale,
    "inference_steps": InputValidator.validate_inference_steps,
    "width": lambda x: InputValidator.validate_image_dimensions(x, 512)[0],
    "height": lambda x: InputValidator.validate_image_dimensions(512, x)[1],
    "seed": InputValidator.validate_seed
})
def safe_text_to_image_generation(
    prompt: str,
    guidance_scale: float = 7.5,
    inference_steps: int = 50,
    width: int = 512,
    height: int = 512,
    seed: int = -1
) -> Tuple[Image.Image, Dict[str, Any], int, str]:
    """Safe text-to-image generation with error handling."""
    # Your actual generation logic would go here
    # For now, we'll create a demo image
    img = _create_demo_image(prompt, width, height)
    
    generation_info = {
        "prompt": prompt,
        "guidance_scale": guidance_scale,
        "inference_steps": inference_steps,
        "width": width,
        "height": height,
        "seed": seed,
        "status": "success"
    }
    
    return img, generation_info, 100, "✅ Generation completed successfully!"

def _create_demo_image(prompt: str, width: int, height: int) -> Image.Image:
    """Create a demo image for demonstration purposes."""
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add gradient background
    for y in range(height):
        for x in range(width):
            r = int(255 * (x / width))
            g = int(255 * (y / height))
            b = int(255 * 0.5)
            img_array[y, x] = [r, g, b]
    
    img = Image.fromarray(img_array)
    
    # Add text
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    text = prompt[:30] + "..." if len(prompt) > 30 else prompt
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Add white text with black outline
    draw.text((x-1, y-1), text, fill=(0, 0, 0), font=font)
    draw.text((x+1, y-1), text, fill=(0, 0, 0), font=font)
    draw.text((x-1, y+1), text, fill=(0, 0, 0), font=font)
    draw.text((x+1, y+1), text, fill=(0, 0, 0), font=font)
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    return img

if __name__ == "__main__":
    # Test the error handling system
    print("Testing error handling system...")
    
    # Test validation
    try:
        InputValidator.validate_prompt("")
    except ValidationError as e:
        print(f"Validation error: {e.message}")
    
    try:
        InputValidator.validate_guidance_scale(25.0)
    except ValidationError as e:
        print(f"Validation error: {e.message}")
    
    # Test error handler
    error_handler = ErrorHandler()
    try:
        raise ValueError("Test error")
    except Exception as e:
        error_info = error_handler.handle_error(e, "test_function")
        print(f"Error handled: {error_info.message}")
    
    print("Error handling system test completed!")
