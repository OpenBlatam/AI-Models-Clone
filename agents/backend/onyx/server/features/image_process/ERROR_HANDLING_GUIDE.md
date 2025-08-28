# 🛡️ Comprehensive Error Handling Guide

## Overview
This guide covers the comprehensive error handling and debugging strategies implemented in the Enhanced Gradio Image Processing System.

## 🚨 Error Handling Architecture

### 1. Centralized Error Handler (`GradioErrorHandler`)

#### **Error Decorator Pattern**
```python
@GradioErrorHandler.handle_error
def process_image(self, image_input, ...):
    # Function implementation
    pass
```

**Benefits:**
- Automatic error logging with timestamps
- Consistent error response format
- Centralized error handling logic
- Automatic traceback capture

#### **Input Validation Methods**
- `validate_image_input()`: Comprehensive image validation
- `validate_configuration_parameters()`: Parameter validation
- Type checking and range validation
- Format and size constraints

### 2. PyTorch-Specific Error Handling

#### **GPU Memory Management**
```python
try:
    output_tensor = self.model(input_tensor)
except RuntimeError as error:
    if "out of memory" in str(error):
        torch.cuda.empty_cache()
        raise RuntimeError("GPU out of memory. Try smaller image or restart.")
```

#### **Device Setup Errors**
```python
try:
    if torch.cuda.is_available():
        device = torch.device('cuda')
        # Configure CUDA settings
    else:
        device = torch.device('cpu')
except Exception as error:
    logger.error(f"Device setup failed: {error}")
    return torch.device('cpu')  # Fallback to CPU
```

#### **Model Initialization Errors**
```python
try:
    self.model = create_optimized_model(config)
    self.model.to(self.device)
    self.model.eval()
except Exception as error:
    logger.error(f"Model initialization failed: {error}")
    logger.error(traceback.format_exc())
    raise
```

### 3. Image Processing Error Handling

#### **Preprocessing Validation**
```python
def preprocess_image(self, image_array: np.ndarray) -> torch.Tensor:
    try:
        # Validate input array
        if image_array is None:
            raise ValueError("Input image array is None")
        
        # Check for invalid values
        if np.isnan(image_array).any() or np.isinf(image_array).any():
            raise ValueError("Image contains NaN or infinite values")
        
        # Process image...
        
    except Exception as error:
        logger.error(f"Image preprocessing failed: {error}")
        logger.error(traceback.format_exc())
        raise
```

#### **Postprocessing Validation**
```python
def postprocess_tensor(self, tensor: torch.Tensor) -> np.ndarray:
    try:
        # Validate input tensor
        if torch.isnan(tensor).any() or torch.isinf(tensor).any():
            raise ValueError("Invalid tensor values in output")
        
        # Process tensor...
        
    except Exception as error:
        logger.error(f"Tensor postprocessing failed: {error}")
        logger.error(traceback.format_exc())
        raise
```

## 🔍 Debugging Tools

### 1. PyTorch Anomaly Detection
```python
# Enable for debugging (disable in production)
if self.debug_mode:
    torch.autograd.set_detect_anomaly(True)
    logger.info("CUDA anomaly detection enabled")
```

### 2. Comprehensive Logging
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gradio_demo.log'),
        logging.StreamHandler()
    ]
)
```

### 3. Performance Monitoring
```python
def _start_performance_monitoring(self):
    """Background performance monitoring"""
    def monitor_loop():
        while True:
            try:
                # Monitor system resources
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                # Monitor GPU if available
                if torch.cuda.is_available():
                    gpu_memory_allocated = torch.cuda.memory_allocated() / 1e9
                    self.gpu_memory_usage.append({
                        'timestamp': time.time(),
                        'allocated_gb': gpu_memory_allocated
                    })
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as error:
                logger.error(f"Performance monitoring error: {error}")
                time.sleep(10)
```

## 📊 Error Response Format

### **Standard Error Response**
```python
{
    "status": "error",
    "error_message": "Detailed error description",
    "error_type": "RuntimeError",
    "processing_time": "0.123s",
    "timestamp": "2024-01-01T12:00:00"
}
```

### **Success Response**
```python
{
    "status": "success",
    "processing_time": "0.456s",
    "input_size": "256x256",
    "output_size": "256x256",
    "quality_score": "0.85",
    "device": "cuda:0",
    "mixed_precision": "enabled"
}
```

## 🚀 Error Recovery Strategies

### 1. **Automatic Fallbacks**
- GPU → CPU fallback on device errors
- Mixed precision → full precision on compatibility issues
- Large image → resized image on memory errors

### 2. **Graceful Degradation**
- Return original image on processing failure
- Continue processing other images in batch
- Maintain system stability during errors

### 3. **Resource Management**
```python
@contextmanager
def _memory_management(self):
    """Context manager for memory management"""
    try:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        yield
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
```

## 📝 Error Logging Best Practices

### 1. **Structured Logging**
```python
logger.error(f"Processing failed for image {image_id}: {str(error)}")
logger.error(f"Error type: {type(error).__name__}")
logger.error(f"Error details: {traceback.format_exc()}")
```

### 2. **Context Information**
```python
error_context = {
    'function': 'process_single_image',
    'image_size': f"{image.shape[1]}x{image.shape[0]}",
    'device': str(self.device),
    'processing_type': processing_type,
    'timestamp': time.time()
}
logger.error(f"Error context: {error_context}")
```

### 3. **Performance Metrics**
```python
def _update_performance_metrics(self, processing_time: float, success: bool):
    """Track success/failure rates and timing"""
    self.performance_metrics['total_processed'] += 1
    
    if success:
        self.performance_metrics['successful_processing'] += 1
    else:
        self.performance_metrics['failed_processing'] += 1
    
    # Update average processing time
    if self.performance_metrics['successful_processing'] > 0:
        current_avg = self.performance_metrics['average_processing_time']
        total_successful = self.performance_metrics['successful_processing']
        self.performance_metrics['average_processing_time'] = (
            (current_avg * (total_successful - 1) + processing_time) / total_successful
        )
```

## 🧪 Testing Error Scenarios

### 1. **Input Validation Tests**
```python
def test_invalid_image_inputs():
    """Test various invalid image inputs"""
    test_cases = [
        None,  # No image
        np.zeros((32, 32)),  # Too small
        np.zeros((8192, 8192)),  # Too large
        np.full((256, 256), 300, dtype=np.uint8),  # Invalid pixel values
        np.full((256, 256), np.nan),  # NaN values
    ]
    
    for test_case in test_cases:
        is_valid, message, _ = GradioErrorHandler.validate_image_input(test_case)
        assert not is_valid, f"Should reject: {test_case}"
```

### 2. **Configuration Validation Tests**
```python
def test_invalid_configurations():
    """Test various invalid configurations"""
    invalid_configs = [
        {'processing_type': 'invalid_type'},
        {'quality_threshold': 1.5},  # Out of range
        {'enhancement_factor': 25.0},  # Out of range
        {'batch_size': 100},  # Too large
    ]
    
    for config in invalid_configs:
        is_valid, message, _ = GradioErrorHandler.validate_configuration_parameters(config)
        assert not is_valid, f"Should reject: {config}"
```

## 🔧 Troubleshooting Common Issues

### 1. **GPU Out of Memory**
**Symptoms:** `RuntimeError: CUDA out of memory`
**Solutions:**
- Reduce image size
- Enable mixed precision
- Set memory fraction: `torch.cuda.set_per_process_memory_fraction(0.8)`
- Clear cache: `torch.cuda.empty_cache()`

### 2. **Model Loading Failures**
**Symptoms:** `Model initialization failed`
**Solutions:**
- Check model file paths
- Verify PyTorch version compatibility
- Check available memory
- Use CPU fallback if GPU fails

### 3. **Input Validation Errors**
**Symptoms:** `Image validation failed`
**Solutions:**
- Check image format (JPG, PNG, BMP, TIFF)
- Verify image dimensions (64x64 to 4096x4096)
- Ensure valid pixel values
- Convert color modes if needed

### 4. **Performance Issues**
**Symptoms:** Slow processing, high memory usage
**Solutions:**
- Enable mixed precision
- Optimize batch sizes
- Monitor resource usage
- Use appropriate device (GPU vs CPU)

## 📈 Monitoring and Alerting

### 1. **Real-time Metrics**
- Processing success rate
- Average processing time
- Memory usage trends
- Error frequency patterns

### 2. **Alert Thresholds**
```python
def check_system_health(self):
    """Check system health and alert on issues"""
    error_rate = self.performance_metrics['failed_processing'] / max(1, self.performance_metrics['total_processed'])
    
    if error_rate > 0.1:  # 10% error rate threshold
        logger.warning(f"High error rate detected: {error_rate:.1%}")
    
    if self.performance_metrics['average_processing_time'] > 10.0:  # 10 second threshold
        logger.warning("Slow processing detected")
```

### 3. **Health Check Endpoint**
```python
def get_system_status(self) -> str:
    """Comprehensive system health check"""
    try:
        status = "**System Status Report**\n\n"
        
        # Model status
        status += f"- Model Status: {'✅ Loaded' if self.model_manager.model else '❌ Not Loaded'}\n"
        status += f"- Device: {self.model_manager.device}\n"
        status += f"- Mixed Precision: {'✅ Enabled' if self.model_manager.mixed_precision_enabled else '❌ Disabled'}\n"
        
        # Performance metrics
        status += f"- Success Rate: {(self.performance_metrics['successful_processing'] / max(1, self.performance_metrics['total_processed'])) * 100:.1f}%\n"
        status += f"- Average Processing Time: {self.performance_metrics['average_processing_time']:.3f} seconds\n"
        
        return status
        
    except Exception as error:
        return f"Status check failed: {str(error)}"
```

## 🎯 Best Practices Summary

1. **Always use try-except blocks** for critical operations
2. **Log errors with context** and stack traces
3. **Provide user-friendly error messages**
4. **Implement automatic fallbacks** where possible
5. **Monitor system health** continuously
6. **Test error scenarios** thoroughly
7. **Use structured logging** for better debugging
8. **Implement graceful degradation** for better user experience
9. **Track performance metrics** for optimization
10. **Document error handling** strategies clearly

This comprehensive error handling system ensures the Gradio demo is robust, user-friendly, and maintainable in production environments.
