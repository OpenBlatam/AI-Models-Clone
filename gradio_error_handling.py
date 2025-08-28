import logging
import traceback
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image
import cv2
import os
import json

logger = logging.getLogger(__name__)

class GradioInputValidator:
    """Advanced input validation for Gradio applications"""
    
    @staticmethod
    def validate_image_file(file_path: str) -> Tuple[bool, str, Optional[np.ndarray]]:
        """Validate image file path and load image"""
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}", None
            
            if not os.path.isfile(file_path):
                return False, f"Path is not a file: {file_path}", None
            
            # Check file size (max 50MB)
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:
                return False, f"File too large: {file_size / (1024*1024):.1f}MB (max 50MB)", None
            
            # Check file extension
            valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in valid_extensions:
                return False, f"Unsupported file format: {file_ext}. Supported: {', '.join(valid_extensions)}", None
            
            # Try to load image
            try:
                image = cv2.imread(file_path)
                if image is None:
                    return False, f"Failed to load image: {file_path}", None
                
                # Convert BGR to RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                return True, "Image loaded successfully", image
                
            except Exception as e:
                return False, f"Image loading error: {str(e)}", None
                
        except Exception as e:
            return False, f"File validation error: {str(e)}", None
    
    @staticmethod
    def validate_image_array(image: np.ndarray) -> Tuple[bool, str, Optional[np.ndarray]]:
        """Validate numpy array as image"""
        try:
            if image is None:
                return False, "Image array is None", None
            
            if not isinstance(image, np.ndarray):
                return False, f"Image must be numpy array, got {type(image)}", None
            
            # Check dimensions
            if len(image.shape) < 2:
                return False, "Image must have at least 2 dimensions", None
            
            if len(image.shape) > 3:
                return False, f"Image has too many dimensions: {len(image.shape)}", None
            
            # Check shape
            height, width = image.shape[:2]
            if height <= 0 or width <= 0:
                return False, f"Invalid image dimensions: {height}x{width}", None
            
            if height < 32 or width < 32:
                return False, f"Image too small: {height}x{width} (minimum 32x32)", None
            
            if height > 8192 or width > 8192:
                return False, f"Image too large: {height}x{width} (maximum 8192x8192)", None
            
            # Check data type and values
            if image.dtype == np.uint8:
                if np.any(image > 255) or np.any(image < 0):
                    return False, "Invalid pixel values for uint8 (0-255)", None
            elif image.dtype == np.float32 or image.dtype == np.float64:
                if np.any(image > 1.0) or np.any(image < 0.0):
                    return False, "Invalid pixel values for float (0.0-1.0)", None
            else:
                return False, f"Unsupported data type: {image.dtype}", None
            
            # Check for NaN or infinite values
            if np.any(np.isnan(image)) or np.any(np.isinf(image)):
                return False, "Image contains NaN or infinite values", None
            
            return True, "Image array is valid", image
            
        except Exception as e:
            return False, f"Array validation error: {str(e)}", None
    
    @staticmethod
    def validate_pil_image(image: Image.Image) -> Tuple[bool, str, Optional[np.ndarray]]:
        """Validate PIL Image and convert to numpy array"""
        try:
            if image is None:
                return False, "PIL Image is None", None
            
            if not isinstance(image, Image.Image):
                return False, f"Input must be PIL Image, got {type(image)}", None
            
            # Check mode
            valid_modes = {'RGB', 'RGBA', 'L', 'LA', 'P'}
            if image.mode not in valid_modes:
                return False, f"Unsupported image mode: {image.mode}. Supported: {', '.join(valid_modes)}", None
            
            # Check size
            width, height = image.size
            if width < 32 or height < 32:
                return False, f"Image too small: {width}x{height} (minimum 32x32)", None
            
            if width > 8192 or height > 8192:
                return False, f"Image too large: {width}x{height} (maximum 8192x8192)", None
            
            # Convert to numpy array
            try:
                image_array = np.array(image)
                return True, "PIL Image converted successfully", image_array
            except Exception as e:
                return False, f"Failed to convert PIL Image to array: {str(e)}", None
                
        except Exception as e:
            return False, f"PIL Image validation error: {str(e)}", None
    
    @staticmethod
    def validate_processing_config(config: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate processing configuration parameters"""
        try:
            validated_config = {}
            
            # Processing type validation
            if 'processing_type' in config:
                valid_types = ['enhancement', 'denoising', 'super_resolution', 'style_transfer', 'color_correction']
                processing_type = str(config['processing_type']).lower()
                if processing_type not in valid_types:
                    return False, f"Invalid processing type: {processing_type}. Must be one of: {', '.join(valid_types)}", {}
                validated_config['processing_type'] = processing_type
            
            # Enhancement factor validation
            if 'enhancement_factor' in config:
                try:
                    factor = float(config['enhancement_factor'])
                    if not (0.1 <= factor <= 20.0):
                        return False, f"Enhancement factor must be between 0.1 and 20.0, got {factor}", {}
                    validated_config['enhancement_factor'] = factor
                except (ValueError, TypeError):
                    return False, f"Enhancement factor must be a number, got {config['enhancement_factor']}", {}
            
            # Quality threshold validation
            if 'quality_threshold' in config:
                try:
                    threshold = float(config['quality_threshold'])
                    if not (0.0 <= threshold <= 1.0):
                        return False, f"Quality threshold must be between 0.0 and 1.0, got {threshold}", {}
                    validated_config['quality_threshold'] = threshold
                except (ValueError, TypeError):
                    return False, f"Quality threshold must be a number, got {config['quality_threshold']}", {}
            
            # Batch size validation
            if 'batch_size' in config:
                try:
                    batch_size = int(config['batch_size'])
                    if not (1 <= batch_size <= 100):
                        return False, f"Batch size must be between 1 and 100, got {batch_size}", {}
                    validated_config['batch_size'] = batch_size
                except (ValueError, TypeError):
                    return False, f"Batch size must be an integer, got {config['batch_size']}", {}
            
            # Device validation
            if 'device' in config:
                device = str(config['device']).lower()
                valid_devices = ['auto', 'cpu', 'cuda', 'mps']
                if device not in valid_devices:
                    return False, f"Invalid device: {device}. Must be one of: {', '.join(valid_devices)}", {}
                validated_config['device'] = device
            
            return True, "Configuration is valid", validated_config
            
        except Exception as e:
            return False, f"Configuration validation error: {str(e)}", {}

class GradioErrorHandler:
    """Comprehensive error handling for Gradio applications"""
    
    def __init__(self, log_errors: bool = True, show_traceback: bool = False):
        self.log_errors = log_errors
        self.show_traceback = show_traceback
        self.error_count = 0
        self.error_history = []
    
    def handle_error(self, func):
        """Decorator for comprehensive error handling"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                self.error_count += 1
                error_info = {
                    'function': func.__name__,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'timestamp': time.time(),
                    'args': str(args)[:200],  # Truncate long args
                    'kwargs': str(kwargs)[:200]  # Truncate long kwargs
                }
                
                if self.show_traceback:
                    error_info['traceback'] = traceback.format_exc()
                
                self.error_history.append(error_info)
                
                if self.log_errors:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    if self.show_traceback:
                        logger.error(traceback.format_exc())
                
                # Return user-friendly error message
                error_msg = f"Error: {str(e)}"
                if hasattr(e, '__class__') and e.__class__.__name__ == 'ValidationError':
                    error_msg = str(e)
                elif "CUDA" in str(e) or "GPU" in str(e):
                    error_msg = "GPU processing error. Please try CPU mode or check GPU drivers."
                elif "memory" in str(e).lower():
                    error_msg = "Memory error. Please try with smaller images or reduce batch size."
                elif "timeout" in str(e).lower():
                    error_msg = "Processing timeout. Please try with smaller images."
                
                return None, error_msg, None
                
            finally:
                # Log performance if needed
                execution_time = time.time() - start_time
                if execution_time > 10.0:  # Log slow operations
                    logger.warning(f"Slow operation in {func.__name__}: {execution_time:.2f}s")
        
        return wrapper
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered"""
        if not self.error_history:
            return {"total_errors": 0, "recent_errors": []}
        
        recent_errors = self.error_history[-10:]  # Last 10 errors
        
        error_types = {}
        for error in self.error_history:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_errors": self.error_count,
            "recent_errors": recent_errors,
            "error_type_distribution": error_types,
            "last_error_time": self.error_history[-1]['timestamp'] if self.error_history else None
        }
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
        self.error_count = 0

class GradioInputSanitizer:
    """Sanitize and normalize inputs for Gradio applications"""
    
    @staticmethod
    def sanitize_image_input(image_input) -> Optional[np.ndarray]:
        """Sanitize various image input types to numpy array"""
        try:
            if image_input is None:
                return None
            
            # Handle PIL Image
            if isinstance(image_input, Image.Image):
                return np.array(image_input)
            
            # Handle numpy array
            elif isinstance(image_input, np.ndarray):
                return image_input.copy()
            
            # Handle file path
            elif isinstance(image_input, str):
                if os.path.exists(image_input):
                    image = cv2.imread(image_input)
                    if image is not None:
                        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    return None
                return None
            
            # Handle file object (from Gradio file upload)
            elif hasattr(image_input, 'name') and hasattr(image_input, 'read'):
                try:
                    image = Image.open(image_input)
                    return np.array(image)
                except Exception:
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Image sanitization failed: {e}")
            return None
    
    @staticmethod
    def normalize_image(image: np.ndarray, target_dtype: np.dtype = np.float32) -> np.ndarray:
        """Normalize image to target data type and range"""
        try:
            if image is None:
                return None
            
            # Convert to target dtype
            if image.dtype != target_dtype:
                if target_dtype == np.float32 or target_dtype == np.float64:
                    if image.dtype == np.uint8:
                        image = image.astype(target_dtype) / 255.0
                    else:
                        image = image.astype(target_dtype)
                else:
                    image = image.astype(target_dtype)
            
            # Ensure proper range
            if target_dtype == np.float32 or target_dtype == np.float64:
                if np.any(image > 1.0):
                    image = np.clip(image, 0.0, 1.0)
                if np.any(image < 0.0):
                    image = np.clip(image, 0.0, 1.0)
            
            return image
            
        except Exception as e:
            logger.error(f"Image normalization failed: {e}")
            return None
    
    @staticmethod
    def sanitize_config_input(config_input: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize configuration input"""
        try:
            sanitized = {}
            
            for key, value in config_input.items():
                if value is None:
                    continue
                
                # Sanitize string values
                if isinstance(value, str):
                    sanitized[key] = value.strip()
                # Sanitize numeric values
                elif isinstance(value, (int, float)):
                    sanitized[key] = value
                # Sanitize boolean values
                elif isinstance(value, bool):
                    sanitized[key] = value
                # Sanitize list values
                elif isinstance(value, list):
                    sanitized[key] = [str(item).strip() if isinstance(item, str) else item for item in value]
                else:
                    sanitized[key] = str(value)
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Config sanitization failed: {e}")
            return {}

class GradioPerformanceMonitor:
    """Monitor performance of Gradio operations"""
    
    def __init__(self):
        self.operation_times = {}
        self.memory_usage = {}
        self.error_rates = {}
    
    def monitor_operation(self, operation_name: str):
        """Decorator to monitor operation performance"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = self._get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                except Exception:
                    success = False
                    raise
                finally:
                    execution_time = time.time() - start_time
                    end_memory = self._get_memory_usage()
                    
                    self._record_metrics(operation_name, execution_time, 
                                      end_memory - start_memory, success)
                
                return result
            return wrapper
        return decorator
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def _record_metrics(self, operation: str, time: float, memory: float, success: bool):
        """Record operation metrics"""
        if operation not in self.operation_times:
            self.operation_times[operation] = []
            self.memory_usage[operation] = []
            self.error_rates[operation] = {'total': 0, 'errors': 0}
        
        self.operation_times[operation].append(time)
        self.memory_usage[operation].append(memory)
        self.error_rates[operation]['total'] += 1
        if not success:
            self.error_rates[operation]['errors'] += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {}
        
        for operation in self.operation_times:
            times = self.operation_times[operation]
            memory = self.memory_usage[operation]
            errors = self.error_rates[operation]
            
            if times:
                summary[operation] = {
                    'avg_time': np.mean(times),
                    'min_time': np.min(times),
                    'max_time': np.max(times),
                    'total_operations': len(times),
                    'avg_memory': np.mean(memory) if memory else 0.0,
                    'error_rate': errors['errors'] / errors['total'] if errors['total'] > 0 else 0.0
                }
        
        return summary

# Global instances
input_validator = GradioInputValidator()
error_handler = GradioErrorHandler(log_errors=True, show_traceback=False)
input_sanitizer = GradioInputSanitizer()
performance_monitor = GradioPerformanceMonitor() 