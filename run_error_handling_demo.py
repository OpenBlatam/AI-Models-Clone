#!/usr/bin/env python3
"""
Error Handling and Input Validation Demo for Gradio Applications
==============================================================

This script demonstrates the comprehensive error handling system for
Gradio-based diffusion model interfaces.
"""

import gradio as gr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time
import json
import traceback
from typing import List, Dict, Any, Optional, Tuple, Union, Callable
from functools import wraps
from dataclasses import dataclass
from enum import Enum
import re

# Import the error handling system
try:
    from core.gradio_error_handling import (
        InputValidator, ErrorHandler, ErrorSeverity, ValidationError, ProcessingError,
        error_handler_decorator, validation_decorator, GradioErrorHandler
    )
    print("✅ Successfully imported error handling system")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Creating simplified error handling system for demo...")
    
    # Simplified error handling classes for demo
    class ErrorSeverity(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
    
    class ValidationError(Exception):
        def __init__(self, message: str, field: str = None, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
            self.message = message
            self.field = field
            self.severity = severity
            super().__init__(self.message)
    
    class ProcessingError(Exception):
        def __init__(self, message: str, operation: str = None, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
            self.message = message
            self.operation = operation
            self.severity = severity
            super().__init__(self.message)
    
    @dataclass
    class ErrorInfo:
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
        @staticmethod
        def validate_prompt(prompt: str, min_length: int = 3, max_length: int = 500) -> str:
            if not prompt or not isinstance(prompt, str):
                raise ValidationError("Prompt must be a non-empty string", "prompt", ErrorSeverity.HIGH)
            
            prompt = prompt.strip()
            if len(prompt) < min_length:
                raise ValidationError(f"Prompt must be at least {min_length} characters long", "prompt", ErrorSeverity.MEDIUM)
            
            if len(prompt) > max_length:
                raise ValidationError(f"Prompt must be no more than {max_length} characters long", "prompt", ErrorSeverity.MEDIUM)
            
            return prompt
        
        @staticmethod
        def validate_guidance_scale(value: float, min_val: float = 1.0, max_val: float = 20.0) -> float:
            if not isinstance(value, (int, float)):
                raise ValidationError("Guidance scale must be a number", "guidance_scale", ErrorSeverity.MEDIUM)
            
            if value < min_val or value > max_val:
                raise ValidationError(f"Guidance scale must be between {min_val} and {max_val}", "guidance_scale", ErrorSeverity.MEDIUM)
            
            return float(value)
        
        @staticmethod
        def validate_inference_steps(value: int, min_val: int = 1, max_val: int = 200) -> int:
            if not isinstance(value, int):
                raise ValidationError("Inference steps must be an integer", "inference_steps", ErrorSeverity.MEDIUM)
            
            if value < min_val or value > max_val:
                raise ValidationError(f"Inference steps must be between {min_val} and {max_val}", "inference_steps", ErrorSeverity.MEDIUM)
            
            return int(value)
    
    class ErrorHandler:
        def __init__(self):
            self.error_history: List[ErrorInfo] = []
            self.max_error_history = 100
        
        def handle_error(self, error: Exception, context: str = None) -> ErrorInfo:
            error_info = ErrorInfo(
                error_type=type(error).__name__,
                message=str(error),
                operation=context,
                severity=self._determine_severity(error),
                traceback=traceback.format_exc()
            )
            
            self.error_history.append(error_info)
            if len(self.error_history) > self.max_error_history:
                self.error_history.pop(0)
            
            return error_info
        
        def _determine_severity(self, error: Exception) -> ErrorSeverity:
            if isinstance(error, ValidationError):
                return error.severity
            elif isinstance(error, ProcessingError):
                return error.severity
            elif isinstance(error, (ValueError, TypeError)):
                return ErrorSeverity.MEDIUM
            else:
                return ErrorSeverity.MEDIUM
        
        def get_error_summary(self) -> Dict[str, Any]:
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
            self.error_history.clear()
    
    def error_handler_decorator(context: str = None):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_handler = getattr(wrapper, '_error_handler', None)
                    if error_handler is None:
                        error_handler = ErrorHandler()
                        wrapper._error_handler = error_handler
                    
                    error_info = error_handler.handle_error(e, context or func.__name__)
                    return _create_error_response(error_info)
            return wrapper
        return decorator
    
    def validation_decorator(validation_rules: Dict[str, Callable] = None):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
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
        error_image = _create_error_image(error_info.message)
        error_data = {
            "error": True,
            "error_type": error_info.error_type,
            "message": error_info.message,
            "severity": error_info.severity.value,
            "timestamp": error_info.timestamp
        }
        return error_image, error_data, 0, f"❌ Error: {error_info.message}"
    
    def _create_validation_error_response(error: ValidationError) -> Tuple[Any, ...]:
        error_info = ErrorInfo(
            error_type="ValidationError",
            message=error.message,
            field=error.field,
            severity=error.severity
        )
        return _create_error_response(error_info)
    
    def _create_error_image(message: str) -> Image.Image:
        width, height = 512, 512
        img = Image.new('RGB', (width, height), color='#ffebee')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.ellipse([width//2 - 50, height//2 - 80, width//2 + 50, height//2 + 20], 
                     fill='#f44336', outline='#d32f2f', width=3)
        draw.text((width//2 - 10, height//2 - 60), "!", fill='white', font=font)
        
        text = message[:50] + "..." if len(message) > 50 else message
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = height//2 + 40
        draw.text((x, y), text, fill='#d32f2f', font=font)
        
        return img

def create_error_handling_demo():
    """Create a comprehensive error handling demo interface."""
    
    # Create error handler instance
    error_handler = ErrorHandler()
    
    def test_validation(prompt: str, guidance_scale: float, inference_steps: int):
        """Test input validation with various inputs."""
        results = []
        
        # Test prompt validation
        try:
            validated_prompt = InputValidator.validate_prompt(prompt)
            results.append(f"✅ Prompt validation passed: '{validated_prompt}'")
        except ValidationError as e:
            results.append(f"❌ Prompt validation failed: {e.message}")
            error_handler.handle_error(e, "prompt_validation")
        
        # Test guidance scale validation
        try:
            validated_guidance = InputValidator.validate_guidance_scale(guidance_scale)
            results.append(f"✅ Guidance scale validation passed: {validated_guidance}")
        except ValidationError as e:
            results.append(f"❌ Guidance scale validation failed: {e.message}")
            error_handler.handle_error(e, "guidance_validation")
        
        # Test inference steps validation
        try:
            validated_steps = InputValidator.validate_inference_steps(inference_steps)
            results.append(f"✅ Inference steps validation passed: {validated_steps}")
        except ValidationError as e:
            results.append(f"❌ Inference steps validation failed: {e.message}")
            error_handler.handle_error(e, "steps_validation")
        
        return "\n".join(results)
    
    @error_handler_decorator("image_generation")
    @validation_decorator({
        "prompt": InputValidator.validate_prompt,
        "guidance_scale": InputValidator.validate_guidance_scale,
        "inference_steps": InputValidator.validate_inference_steps
    })
    def safe_image_generation(prompt: str, guidance_scale: float, inference_steps: int):
        """Safe image generation with error handling."""
        # Simulate some potential errors
        if "error" in prompt.lower():
            raise ProcessingError("Simulated processing error for demonstration", "image_generation", ErrorSeverity.MEDIUM)
        
        if guidance_scale > 15:
            raise ValueError("High guidance scale may cause issues")
        
        # Create demo image
        width, height = 512, 512
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add gradient background
        for y in range(height):
            for x in range(width):
                r = int(255 * (x / width) * (guidance_scale / 20.0))
                g = int(255 * (y / height) * (inference_steps / 100.0))
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
        
        # Add parameter info
        param_text = f"Guidance: {guidance_scale}, Steps: {inference_steps}"
        bbox = draw.textbbox((0, 0), param_text, font=font)
        param_width = bbox[2] - bbox[0]
        param_height = bbox[3] - bbox[1]
        
        param_x = (width - param_width) // 2
        param_y = height - param_height - 20
        
        draw.text((param_x, param_y), param_text, fill=(255, 255, 255), font=font)
        
        return img, {"status": "success", "prompt": prompt, "guidance": guidance_scale, "steps": inference_steps}, 100, "✅ Generation completed successfully!"
    
    def get_error_summary():
        """Get error summary for display."""
        return error_handler.get_error_summary()
    
    def clear_error_history():
        """Clear error history."""
        error_handler.clear_history()
        return {"total_errors": 0, "errors": []}
    
    # Create the interface
    with gr.Blocks(
        title="🐛 Error Handling and Input Validation Demo",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .demo-header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .error-notification {
            background: #ffebee;
            border: 2px solid #f44336;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            color: #d32f2f;
        }
        .success-notification {
            background: #e8f5e8;
            border: 2px solid #4caf50;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            color: #2e7d32;
        }
        """
    ) as demo:
        
        # Header
        gr.HTML("""
        <div class="demo-header">
            <h1>🐛 Error Handling and Input Validation Demo</h1>
            <p>Test the comprehensive error handling system for Gradio applications</p>
        </div>
        """)
        
        with gr.Tabs():
            
            # Input Validation Testing Tab
            with gr.Tab("🔍 Input Validation Testing"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🧪 Test Input Validation")
                        
                        # Test inputs
                        test_prompt = gr.Textbox(
                            label="Test Prompt",
                            placeholder="Enter a prompt to test validation...",
                            lines=3
                        )
                        
                        test_guidance = gr.Slider(0, 25, 7.5, label="Test Guidance Scale", step=0.5)
                        test_steps = gr.Slider(0, 250, 50, label="Test Inference Steps", step=1)
                        
                        test_validation_button = gr.Button("🧪 Test Validation", variant="primary")
                        
                        # Validation results
                        validation_results = gr.Textbox(
                            label="Validation Results",
                            lines=8,
                            interactive=False
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 📋 Validation Rules")
                        
                        gr.Markdown("""
                        **Prompt Validation:**
                        - Must be 3-500 characters
                        - Cannot be empty
                        - Must be a string
                        
                        **Guidance Scale:**
                        - Must be 1.0-20.0
                        - Must be a number
                        
                        **Inference Steps:**
                        - Must be 1-200
                        - Must be an integer
                        """)
                        
                        gr.Markdown("### 💡 Try These Test Cases:")
                        gr.Markdown("""
                        **Valid Inputs:**
                        - Prompt: "A beautiful landscape"
                        - Guidance: 7.5
                        - Steps: 50
                        
                        **Invalid Inputs:**
                        - Prompt: "" (empty)
                        - Guidance: 25.0 (too high)
                        - Steps: 0 (too low)
                        """)
                
                # Event handler
                test_validation_button.click(
                    fn=test_validation,
                    inputs=[test_prompt, test_guidance, test_steps],
                    outputs=[validation_results]
                )
            
            # Safe Image Generation Tab
            with gr.Tab("🎨 Safe Image Generation"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎯 Generation Parameters")
                        
                        gen_prompt = gr.Textbox(
                            label="Generation Prompt",
                            placeholder="Describe what you want to generate...",
                            lines=3
                        )
                        
                        gen_guidance = gr.Slider(1.0, 20.0, 7.5, label="Guidance Scale", step=0.5)
                        gen_steps = gr.Slider(10, 100, 50, label="Inference Steps", step=5)
                        
                        # Add a checkbox to trigger errors for testing
                        trigger_error = gr.Checkbox(
                            label="Trigger Error (for testing)",
                            value=False,
                            info="Check this to simulate an error"
                        )
                        
                        generate_button = gr.Button("🎨 Generate Image", variant="primary", size="lg")
                        
                        # Progress and status
                        progress_bar = gr.Slider(0, 100, 0, label="Generation Progress", interactive=False)
                        status_output = gr.Textbox(label="Status", interactive=False)
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 🖼️ Generated Result")
                        
                        output_image = gr.Image(label="Generated Image", height=400)
                        generation_info = gr.JSON(label="Generation Information")
                
                # Event handler
                def prepare_generation(prompt: str, guidance: float, steps: int, trigger: bool):
                    if trigger:
                        prompt = f"error: {prompt}"  # This will trigger the error
                    return prompt, guidance, steps
                
                generate_button.click(
                    fn=prepare_generation,
                    inputs=[gen_prompt, gen_guidance, gen_steps, trigger_error],
                    outputs=[gen_prompt, gen_guidance, gen_steps]
                ).then(
                    fn=safe_image_generation,
                    inputs=[gen_prompt, gen_guidance, gen_steps],
                    outputs=[output_image, generation_info, progress_bar, status_output]
                )
            
            # Error Monitoring Tab
            with gr.Tab("📊 Error Monitoring"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🚨 Error Management")
                        
                        refresh_button = gr.Button("🔄 Refresh Error Log", variant="secondary")
                        clear_button = gr.Button("🗑️ Clear History", variant="secondary")
                        
                        gr.Markdown("#### 📊 Error Statistics")
                        error_stats = gr.JSON(label="Error Statistics", interactive=False)
                    
                    with gr.Column(scale=2):
                        gr.Markdown("### 📝 Recent Errors")
                        error_log = gr.JSON(label="Error Log", interactive=False)
                
                # Event handlers
                refresh_button.click(
                    fn=get_error_summary,
                    outputs=[error_stats, error_log]
                )
                
                clear_button.click(
                    fn=clear_error_history,
                    outputs=[error_stats, error_log]
                )
            
            # Error Simulation Tab
            with gr.Tab("🎭 Error Simulation"):
                gr.Markdown("### 🎭 Simulate Different Types of Errors")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 🔍 Validation Errors")
                        
                        # Test empty prompt
                        empty_prompt_button = gr.Button("Test Empty Prompt", variant="secondary")
                        empty_prompt_result = gr.Textbox(label="Result", interactive=False)
                        
                        # Test invalid guidance
                        invalid_guidance_button = gr.Button("Test Invalid Guidance", variant="secondary")
                        invalid_guidance_result = gr.Textbox(label="Result", interactive=False)
                        
                        # Test invalid steps
                        invalid_steps_button = gr.Button("Test Invalid Steps", variant="secondary")
                        invalid_steps_result = gr.Textbox(label="Result", interactive=False)
                    
                    with gr.Column(scale=1):
                        gr.Markdown("#### ⚠️ Processing Errors")
                        
                        # Test processing error
                        processing_error_button = gr.Button("Test Processing Error", variant="secondary")
                        processing_error_result = gr.Textbox(label="Result", interactive=False)
                        
                        # Test value error
                        value_error_button = gr.Button("Test Value Error", variant="secondary")
                        value_error_result = gr.Textbox(label="Result", interactive=False)
                
                # Event handlers for error simulation
                def simulate_empty_prompt():
                    try:
                        InputValidator.validate_prompt("")
                    except ValidationError as e:
                        error_handler.handle_error(e, "empty_prompt_test")
                        return f"❌ Validation Error: {e.message}"
                    return "✅ No error occurred"
                
                def simulate_invalid_guidance():
                    try:
                        InputValidator.validate_guidance_scale(25.0)
                    except ValidationError as e:
                        error_handler.handle_error(e, "invalid_guidance_test")
                        return f"❌ Validation Error: {e.message}"
                    return "✅ No error occurred"
                
                def simulate_invalid_steps():
                    try:
                        InputValidator.validate_inference_steps(0)
                    except ValidationError as e:
                        error_handler.handle_error(e, "invalid_steps_test")
                        return f"❌ Validation Error: {e.message}"
                    return "✅ No error occurred"
                
                def simulate_processing_error():
                    try:
                        raise ProcessingError("Simulated processing error", "processing_test", ErrorSeverity.MEDIUM)
                    except ProcessingError as e:
                        error_handler.handle_error(e, "processing_error_test")
                        return f"❌ Processing Error: {e.message}"
                    return "✅ No error occurred"
                
                def simulate_value_error():
                    try:
                        raise ValueError("Simulated value error for testing")
                    except ValueError as e:
                        error_handler.handle_error(e, "value_error_test")
                        return f"❌ Value Error: {e.message}"
                    return "✅ No error occurred"
                
                empty_prompt_button.click(fn=simulate_empty_prompt, outputs=[empty_prompt_result])
                invalid_guidance_button.click(fn=simulate_invalid_guidance, outputs=[invalid_guidance_result])
                invalid_steps_button.click(fn=simulate_invalid_steps, outputs=[invalid_steps_result])
                processing_error_button.click(fn=simulate_processing_error, outputs=[processing_error_result])
                value_error_button.click(fn=simulate_value_error, outputs=[value_error_result])
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 20px; color: #666;">
            <p>Error Handling Demo - Built with ❤️ using Gradio</p>
        </div>
        """)
    
    return demo

if __name__ == "__main__":
    # Create and launch the error handling demo
    demo = create_error_handling_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )
