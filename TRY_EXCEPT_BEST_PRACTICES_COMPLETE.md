# 🛡️ Try-Except Best Practices for Data Loading and Model Inference

## 📋 Executive Summary

This document provides comprehensive best practices for implementing proper error handling with try-except blocks in data loading and model inference operations. The implementation includes robust error handling patterns, retry mechanisms, fallback strategies, and comprehensive logging.

### 🎯 Key Features Implemented

- **Safe File Operations**: Comprehensive file existence and permission checking
- **Data Loading Error Handling**: CSV, JSON, and model loading with specific exception handling
- **Model Inference Safety**: Memory management and retry logic for inference operations
- **Batch Processing**: Partial success handling and error recovery
- **Memory Management**: GPU memory monitoring and CPU fallback strategies
- **Comprehensive Logging**: Detailed error logging for debugging and monitoring

## 📁 Files Created

### Core Implementation
- `examples/try_except_demo.py` - Comprehensive demo with error handling examples
- `examples/try_except_best_practices.py` - Best practices implementation
- `TRY_EXCEPT_BEST_PRACTICES_COMPLETE.md` - This documentation

## 🏗️ Architecture Overview

### Core Components

#### SafeDataLoader Class
```python
class SafeDataLoader:
    """Safe data loading with comprehensive error handling."""
    
    def __init__(self):
        self.loaded_data = {}
        self.error_log = []
```

#### SafeModelInference Class
```python
class SafeModelInference:
    """Safe model inference with comprehensive error handling."""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.error_log = []
```

#### ErrorHandlingBestPractices Class
```python
class ErrorHandlingBestPractices:
    """Best practices for error handling in data loading and model inference."""
```

## 🛡️ Safe File Operations

### File Existence and Permission Checking
```python
@staticmethod
def safe_file_operation(file_path: str, operation: str = "read") -> Dict[str, Any]:
    """Safe file operation with comprehensive error handling."""
    try:
        # Check if file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file permissions
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"No read permission for file: {file_path}")
        
        # Check file size
        file_size = Path(file_path).stat().st_size
        if file_size == 0:
            raise ValueError(f"File is empty: {file_path}")
        
        # Check file size limit (e.g., 100MB)
        if file_size > 100 * 1024 * 1024:
            raise ValueError(f"File too large ({file_size / 1024 / 1024:.1f}MB): {file_path}")
        
        return {
            "success": True,
            "file_path": file_path,
            "file_size": file_size,
            "operation": operation
        }
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return {
            "success": False,
            "error": "FileNotFoundError",
            "message": str(e),
            "suggestion": "Check file path and ensure file exists"
        }
    
    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        return {
            "success": False,
            "error": "PermissionError",
            "message": str(e),
            "suggestion": "Check file permissions or run with appropriate privileges"
        }
```

### Error Handling Features
- **File Existence Check**: Verify file exists before operations
- **Permission Validation**: Check read/write permissions
- **File Size Validation**: Prevent loading empty or oversized files
- **Specific Exception Handling**: Handle FileNotFoundError, PermissionError, ValueError
- **Helpful Error Messages**: Provide actionable suggestions

## 📊 Safe Data Loading

### CSV Loading with Error Handling
```python
@staticmethod
def safe_csv_loading(file_path: str) -> Dict[str, Any]:
    """Safe CSV loading with comprehensive error handling."""
    try:
        # First check file operation
        file_check = ErrorHandlingBestPractices.safe_file_operation(file_path)
        if not file_check["success"]:
            return file_check
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        data = None
        
        for encoding in encodings:
            try:
                data = pd.read_csv(file_path, encoding=encoding)
                logger.info(f"Successfully loaded CSV with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if data is None:
            raise UnicodeDecodeError("Could not decode CSV file with any encoding")
        
        # Validate data structure
        if data.empty:
            raise ValueError("CSV file contains no data")
        
        # Check for required columns
        required_columns = ['text', 'label']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for null values
        null_counts = data.isnull().sum()
        if null_counts.sum() > 0:
            logger.warning(f"Found null values: {null_counts.to_dict()}")
        
        return {
            "success": True,
            "data": data,
            "shape": data.shape,
            "columns": list(data.columns),
            "null_counts": null_counts.to_dict(),
            "file_path": file_path
        }
        
    except pd.errors.EmptyDataError as e:
        logger.error(f"Empty data error: {e}")
        return {
            "success": False,
            "error": "EmptyDataError",
            "message": str(e),
            "suggestion": "Check if CSV file contains data"
        }
    
    except pd.errors.ParserError as e:
        logger.error(f"Parser error: {e}")
        return {
            "success": False,
            "error": "ParserError",
            "message": str(e),
            "suggestion": "Check CSV format and delimiter"
        }
    
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error: {e}")
        return {
            "success": False,
            "error": "UnicodeDecodeError",
            "message": str(e),
            "suggestion": "Try different file encoding or check file format"
        }
```

### Key Features
- **Multiple Encoding Support**: Try different encodings automatically
- **Data Validation**: Check for required columns and data types
- **Null Value Detection**: Identify and report missing data
- **Pandas-Specific Exceptions**: Handle EmptyDataError, ParserError
- **Comprehensive Error Messages**: Provide specific suggestions for each error type

## 🤖 Safe Model Loading

### PyTorch Model Loading
```python
@staticmethod
def safe_model_loading(model_path: str, model_type: str = "pytorch") -> Dict[str, Any]:
    """Safe model loading with comprehensive error handling."""
    try:
        # First check file operation
        file_check = ErrorHandlingBestPractices.safe_file_operation(model_path)
        if not file_check["success"]:
            return file_check
        
        logger.info(f"Loading {model_type} model: {model_path}")
        
        # Check available memory
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory
            gpu_memory_gb = gpu_memory / 1024**3
            logger.info(f"Available GPU memory: {gpu_memory_gb:.1f}GB")
            
            if gpu_memory_gb < 2:
                logger.warning("Low GPU memory detected, consider using CPU")
        
        # Load model based on type
        if model_type == "pytorch":
            # Load PyTorch model
            model = torch.load(model_path, map_location=DEVICE)
            
            # Validate model
            if not isinstance(model, nn.Module):
                raise ValueError("Loaded file is not a valid PyTorch model")
            
            # Set model to evaluation mode
            model.eval()
            
            # Check model parameters
            total_params = sum(p.numel() for p in model.parameters())
            logger.info(f"Model loaded with {total_params:,} parameters")
            
        elif model_type == "transformers":
            # Load transformers model
            try:
                from transformers import AutoModel, AutoTokenizer
            except ImportError as e:
                raise ImportError(f"Transformers library not available: {e}")
            
            model = AutoModel.from_pretrained(model_path)
            model.to(DEVICE)
            model.eval()
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            total_params = sum(p.numel() for p in model.parameters())
            logger.info(f"Transformers model loaded with {total_params:,} parameters")
            
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        return {
            "success": True,
            "model": model,
            "model_type": model_type,
            "model_path": model_path,
            "device": str(DEVICE),
            "total_params": total_params if 'total_params' in locals() else None
        }
        
    except RuntimeError as e:
        logger.error(f"Runtime error loading model: {e}")
        if "out of memory" in str(e).lower():
            return {
                "success": False,
                "error": "OutOfMemoryError",
                "message": str(e),
                "suggestion": "Try loading model on CPU or reduce model size"
            }
        else:
            return {
                "success": False,
                "error": "RuntimeError",
                "message": str(e),
                "suggestion": "Check model compatibility and file integrity"
            }
    
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return {
            "success": False,
            "error": "ImportError",
            "message": str(e),
            "suggestion": "Install required libraries: pip install transformers torch"
        }
```

### Key Features
- **Memory Monitoring**: Check GPU memory before loading
- **Model Validation**: Verify model type and structure
- **Multiple Model Types**: Support PyTorch and Transformers models
- **Memory Error Handling**: Provide CPU fallback suggestions
- **Parameter Counting**: Track model complexity

## 🔄 Safe Model Inference

### Inference with Retry Logic
```python
@staticmethod
def safe_inference(model: nn.Module, inputs: Dict[str, torch.Tensor], 
                  max_retries: int = 3) -> Dict[str, Any]:
    """Safe model inference with comprehensive error handling."""
    for attempt in range(max_retries):
        try:
            logger.info(f"Inference attempt {attempt + 1}/{max_retries}")
            
            # Validate inputs
            if not isinstance(inputs, dict):
                raise ValueError("Inputs must be a dictionary")
            
            if not inputs:
                raise ValueError("Inputs dictionary cannot be empty")
            
            # Check model state
            if not isinstance(model, nn.Module):
                raise ValueError("Model must be a PyTorch module")
            
            # Move inputs to correct device
            device_inputs = {}
            for key, value in inputs.items():
                if isinstance(value, torch.Tensor):
                    device_inputs[key] = value.to(DEVICE)
                else:
                    device_inputs[key] = value
            
            # Perform inference with gradient disabled
            with torch.no_grad():
                outputs = model(**device_inputs)
            
            logger.info("Inference completed successfully")
            
            return {
                "success": True,
                "outputs": outputs,
                "attempt": attempt + 1,
                "device": str(DEVICE)
            }
            
        except RuntimeError as e:
            logger.error(f"Runtime error during inference (attempt {attempt + 1}): {e}")
            
            if "out of memory" in str(e).lower():
                # Try to free memory
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                # Try with CPU if on GPU
                if DEVICE.type == 'cuda' and attempt < max_retries - 1:
                    logger.info("Trying inference on CPU")
                    try:
                        model_cpu = model.to('cpu')
                        cpu_inputs = {k: v.to('cpu') if isinstance(v, torch.Tensor) else v 
                                    for k, v in inputs.items()}
                        
                        with torch.no_grad():
                            outputs = model_cpu(**cpu_inputs)
                        
                        # Move model back to original device
                        model.to(DEVICE)
                        
                        logger.info("Inference completed on CPU")
                        return {
                            "success": True,
                            "outputs": outputs,
                            "attempt": attempt + 1,
                            "device": "cpu",
                            "note": "Fell back to CPU due to GPU memory"
                        }
                        
                    except Exception as cpu_e:
                        logger.error(f"CPU inference also failed: {cpu_e}")
                        model.to(DEVICE)  # Move back to original device
                
                if attempt == max_retries - 1:
                    return {
                        "success": False,
                        "error": "OutOfMemoryError",
                        "message": str(e),
                        "suggestion": "Try reducing batch size or input length",
                        "attempts": max_retries
                    }
            else:
                if attempt == max_retries - 1:
                    return {
                        "success": False,
                        "error": "RuntimeError",
                        "message": str(e),
                        "suggestion": "Check model and input compatibility",
                        "attempts": max_retries
                    }
```

### Key Features
- **Retry Logic**: Multiple attempts for transient failures
- **Memory Management**: Automatic GPU memory cleanup
- **CPU Fallback**: Automatic fallback to CPU when GPU memory is insufficient
- **Input Validation**: Validate input format and model state
- **Gradient Disabled**: Ensure inference doesn't consume unnecessary memory

## 📦 Safe Batch Processing

### Batch Processing with Partial Success
```python
@staticmethod
def safe_batch_processing(data: List[Any], batch_size: int, 
                         process_func: callable) -> Dict[str, Any]:
    """Safe batch processing with comprehensive error handling."""
    try:
        logger.info(f"Starting batch processing of {len(data)} items with batch size {batch_size}")
        
        # Validate inputs
        if not data:
            raise ValueError("Data list cannot be empty")
        
        if batch_size <= 0:
            raise ValueError("Batch size must be positive")
        
        if not callable(process_func):
            raise ValueError("Process function must be callable")
        
        results = []
        errors = []
        successful_batches = 0
        failed_batches = 0
        
        # Process in batches
        for i in range(0, len(data), batch_size):
            batch_data = data[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(data) + batch_size - 1) // batch_size
            
            try:
                logger.info(f"Processing batch {batch_num}/{total_batches}")
                
                # Process batch
                batch_result = process_func(batch_data)
                
                if batch_result.get("success"):
                    results.extend(batch_result.get("results", []))
                    successful_batches += 1
                    logger.info(f"Batch {batch_num} completed successfully")
                else:
                    errors.append({
                        "batch_num": batch_num,
                        "error": batch_result.get("error"),
                        "message": batch_result.get("message")
                    })
                    failed_batches += 1
                    logger.error(f"Batch {batch_num} failed: {batch_result.get('error')}")
            
            except Exception as e:
                errors.append({
                    "batch_num": batch_num,
                    "error": "BatchProcessingError",
                    "message": str(e)
                })
                failed_batches += 1
                logger.error(f"Batch {batch_num} failed with exception: {e}")
        
        # Calculate success rate
        total_batches = successful_batches + failed_batches
        success_rate = successful_batches / total_batches if total_batches > 0 else 0
        
        return {
            "success": success_rate > 0,  # Partial success is still success
            "total_items": len(data),
            "processed_items": len(results),
            "successful_batches": successful_batches,
            "failed_batches": failed_batches,
            "success_rate": success_rate,
            "results": results,
            "errors": errors
        }
        
    except ValueError as e:
        logger.error(f"Validation error in batch processing: {e}")
        return {
            "success": False,
            "error": "ValueError",
            "message": str(e),
            "suggestion": "Check input parameters"
        }
    
    except Exception as e:
        logger.error(f"Unexpected batch processing error: {e}")
        return {
            "success": False,
            "error": "UnexpectedError",
            "message": str(e),
            "suggestion": "Check system resources and try again"
        }
```

### Key Features
- **Partial Success Handling**: Continue processing even if some batches fail
- **Error Tracking**: Track errors for each failed batch
- **Success Rate Calculation**: Monitor processing success rate
- **Batch-Level Error Handling**: Handle errors at batch level
- **Comprehensive Reporting**: Provide detailed processing statistics

## 🚀 Usage Examples

### Basic Error Handling
```python
# Safe file operation
file_result = ErrorHandlingBestPractices.safe_file_operation("data.csv")
if not file_result["success"]:
    print(f"Error: {file_result['error']}")
    print(f"Suggestion: {file_result['suggestion']}")

# Safe CSV loading
csv_result = ErrorHandlingBestPractices.safe_csv_loading("data.csv")
if csv_result["success"]:
    data = csv_result["data"]
    print(f"Loaded {data.shape[0]} rows")
else:
    print(f"Error: {csv_result['error']}")
```

### Model Loading and Inference
```python
# Safe model loading
model_result = ErrorHandlingBestPractices.safe_model_loading("model.pth")
if model_result["success"]:
    model = model_result["model"]
    
    # Safe inference
    inputs = {"input": torch.randn(1, 10)}
    inference_result = ErrorHandlingBestPractices.safe_inference(model, inputs)
    
    if inference_result["success"]:
        outputs = inference_result["outputs"]
        print(f"Inference successful on {inference_result['device']}")
    else:
        print(f"Inference error: {inference_result['error']}")
```

### Batch Processing
```python
def process_batch(batch_data):
    # Simulate batch processing
    if len(batch_data) > 5:
        return {"success": False, "error": "Batch too large"}
    return {"success": True, "results": [f"processed_{item}" for item in batch_data]}

# Safe batch processing
batch_result = ErrorHandlingBestPractices.safe_batch_processing(
    list(range(10)), batch_size=3, process_func=process_batch
)

if batch_result["success"]:
    print(f"Success rate: {batch_result['success_rate']:.2%}")
    print(f"Processed {batch_result['processed_items']} items")
else:
    print(f"Batch processing failed: {batch_result['error']}")
```

## 🔧 Best Practices Summary

### Error Handling Best Practices
1. **Always use try-except blocks** for error-prone operations
2. **Handle specific exceptions** rather than generic ones
3. **Provide helpful error messages** and recovery suggestions
4. **Implement retry logic** for transient failures
5. **Log errors for debugging** and monitoring
6. **Validate inputs** before processing
7. **Implement fallback strategies** (CPU fallback, batch size reduction)
8. **Support partial success** in batch operations
9. **Use appropriate error types** and messages
10. **Check system resources** before heavy operations

### Data Loading Best Practices
1. **Check file existence** before operations
2. **Validate file permissions** and size
3. **Handle encoding issues** with multiple encoding attempts
4. **Validate data structure** and required columns
5. **Check for null values** and data quality issues
6. **Handle pandas-specific exceptions** (EmptyDataError, ParserError)
7. **Provide clear error messages** for each error type

### Model Inference Best Practices
1. **Monitor memory usage** before inference
2. **Implement retry logic** for transient failures
3. **Provide CPU fallback** when GPU memory is insufficient
4. **Validate model state** and input format
5. **Use torch.no_grad()** for inference
6. **Handle memory errors** gracefully
7. **Track inference attempts** and success rates

### Batch Processing Best Practices
1. **Support partial success** handling
2. **Track batch-level errors** separately
3. **Calculate success rates** for monitoring
4. **Provide detailed error reporting**
5. **Implement batch size optimization**
6. **Handle batch-level exceptions** gracefully
7. **Monitor processing progress** and performance

## 🎯 Key Benefits

### Reliability
- **Robust Error Handling**: Prevents crashes and data loss
- **Retry Logic**: Handles transient failures automatically
- **Fallback Strategies**: Provides alternative processing paths
- **Partial Success**: Continues processing despite some failures

### Performance
- **Memory Management**: Optimizes GPU memory usage
- **CPU Fallback**: Ensures processing continues when GPU memory is insufficient
- **Batch Optimization**: Efficient batch processing with error handling
- **Resource Monitoring**: Prevents resource exhaustion

### Maintainability
- **Comprehensive Logging**: Detailed error tracking for debugging
- **Clear Error Messages**: Easy-to-understand error descriptions
- **Modular Design**: Reusable error handling components
- **Well-Documented**: Clear documentation and examples

### User Experience
- **Helpful Suggestions**: Actionable error recovery instructions
- **Progress Tracking**: Real-time processing status updates
- **Error Recovery**: Automatic recovery from common errors
- **Transparent Reporting**: Clear success/failure reporting

## 🚀 Future Enhancements

### Planned Features
1. **Advanced Retry Strategies**: Exponential backoff and circuit breaker patterns
2. **Distributed Error Handling**: Multi-node error tracking and recovery
3. **Error Prediction**: Machine learning for error prediction and prevention
4. **Automated Recovery**: Self-healing systems for common errors
5. **Performance Optimization**: Automatic performance tuning based on error patterns

### Advanced Capabilities
1. **Error Visualization**: Interactive error analysis dashboards
2. **Predictive Error Prevention**: AI-powered error prevention
3. **Custom Error Handlers**: User-defined error handling strategies
4. **Error Recovery Automation**: Automated error recovery workflows
5. **Real-time Error Monitoring**: Live error tracking and alerting

The try-except best practices implementation provides a comprehensive solution for building reliable, robust, and maintainable data loading and model inference systems with proper error handling and recovery mechanisms. 