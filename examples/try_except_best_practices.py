from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
BUFFER_SIZE = 1024

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import json
import logging
import time
import os
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import warnings
                    from transformers import AutoModel, AutoTokenizer
from typing import Any, List, Dict, Optional
import asyncio
"""
🛡️ Try-Except Best Practices for Data Loading and Model Inference
================================================================
Comprehensive guide and examples for proper error handling
in data loading and model inference operations.
"""

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for GPU availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")

class ErrorHandlingBestPractices:
    """Best practices for error handling in data loading and model inference."""
    
    @staticmethod
    def safe_file_operation(file_path: str, operation: str = "read") -> Dict[str, Any]:
        """
        Safe file operation with comprehensive error handling.
        
        Best Practice: Always check file existence and handle file-specific exceptions.
        """
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
        
        except ValueError as e:
            logger.error(f"Value error: {e}")
            return {
                "success": False,
                "error": "ValueError",
                "message": str(e),
                "suggestion": "Check file content and size"
            }
        
        except Exception as e:
            logger.error(f"Unexpected file error: {e}")
            return {
                "success": False,
                "error": "UnexpectedError",
                "message": str(e),
                "suggestion": "Try again or check file integrity"
            }
    
    @staticmethod
    def safe_csv_loading(file_path: str) -> Dict[str, Any]:
        """
        Safe CSV loading with comprehensive error handling.
        
        Best Practice: Handle pandas-specific exceptions and validate data structure.
        """
        try:
            # First check file operation
            file_check = ErrorHandlingBestPractices.safe_file_operation(file_path)
            if not file_check["success"]:
                return file_check
            
            # Load CSV with error handling
            logger.info(f"Loading CSV file: {file_path}")
            
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
            
            # Check data types
            if not data['text'].dtype == 'object':
                raise ValueError("Text column must be string type")
            
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
        
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {
                "success": False,
                "error": "ValueError",
                "message": str(e),
                "suggestion": "Check data structure and required columns"
            }
        
        except Exception as e:
            logger.error(f"Unexpected CSV error: {e}")
            return {
                "success": False,
                "error": "UnexpectedError",
                "message": str(e),
                "suggestion": "Check file integrity and try again"
            }
    
    @staticmethod
    def safe_model_loading(model_path: str, model_type: str = "pytorch") -> Dict[str, Any]:
        """
        Safe model loading with comprehensive error handling.
        
        Best Practice: Handle model-specific exceptions and memory management.
        """
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
        
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {
                "success": False,
                "error": "ValueError",
                "message": str(e),
                "suggestion": "Check model format and type"
            }
        
        except Exception as e:
            logger.error(f"Unexpected model loading error: {e}")
            return {
                "success": False,
                "error": "UnexpectedError",
                "message": str(e),
                "suggestion": "Check model file and try again"
            }
    
    @staticmethod
    def safe_inference(model: nn.Module, inputs: Dict[str, torch.Tensor], 
                      max_retries: int = 3) -> Dict[str, Any]:
        """
        Safe model inference with comprehensive error handling.
        
        Best Practice: Handle memory errors and implement retry logic.
        """
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
            
            except ValueError as e:
                logger.error(f"Value error during inference: {e}")
                return {
                    "success": False,
                    "error": "ValueError",
                    "message": str(e),
                    "suggestion": "Check input format and model requirements"
                }
            
            except Exception as e:
                logger.error(f"Unexpected inference error: {e}")
                if attempt == max_retries - 1:
                    return {
                        "success": False,
                        "error": "UnexpectedError",
                        "message": str(e),
                        "suggestion": "Check model and input integrity",
                        "attempts": max_retries
                    }
        
        return {
            "success": False,
            "error": "MaxRetriesExceeded",
            "message": f"Failed after {max_retries} attempts",
            "suggestion": "Check system resources and model compatibility"
        }
    
    @staticmethod
    def safe_batch_processing(data: List[Any], batch_size: int, 
                             process_func: callable) -> Dict[str, Any]:
        """
        Safe batch processing with comprehensive error handling.
        
        Best Practice: Handle batch-level errors and implement partial success handling.
        """
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

def demonstrate_best_practices():
    """Demonstrate all best practices for error handling."""
    print("🛡️ Try-Except Best Practices Demonstration")
    print("=" * 50)
    
    # 1. Safe file operation
    print("\n1. Safe File Operation:")
    file_result = ErrorHandlingBestPractices.safe_file_operation("nonexistent_file.txt")
    print(f"   Result: {file_result['success']}")
    if not file_result['success']:
        print(f"   Error: {file_result['error']}")
        print(f"   Suggestion: {file_result['suggestion']}")
    
    # 2. Safe CSV loading
    print("\n2. Safe CSV Loading:")
    csv_result = ErrorHandlingBestPractices.safe_csv_loading("nonexistent_file.csv")
    print(f"   Result: {csv_result['success']}")
    if not csv_result['success']:
        print(f"   Error: {csv_result['error']}")
        print(f"   Suggestion: {csv_result['suggestion']}")
    
    # 3. Safe model loading
    print("\n3. Safe Model Loading:")
    model_result = ErrorHandlingBestPractices.safe_model_loading("nonexistent_model.pth")
    print(f"   Result: {model_result['success']}")
    if not model_result['success']:
        print(f"   Error: {model_result['error']}")
        print(f"   Suggestion: {model_result['suggestion']}")
    
    # 4. Safe inference (with dummy model)
    print("\n4. Safe Inference:")
    try:
        # Create a dummy model for demonstration
        dummy_model = nn.Linear(10, 5)
        dummy_inputs = {"input": torch.randn(1, 10)}
        
        inference_result = ErrorHandlingBestPractices.safe_inference(dummy_model, dummy_inputs)
        print(f"   Result: {inference_result['success']}")
        if inference_result['success']:
            print(f"   Device: {inference_result['device']}")
            print(f"   Attempts: {inference_result['attempt']}")
    except Exception as e:
        print(f"   Error creating dummy model: {e}")
    
    # 5. Safe batch processing
    print("\n5. Safe Batch Processing:")
    
    def dummy_process_func(batch) -> Any:
        # Simulate processing with some failures
        if len(batch) > 5:
            return {"success": False, "error": "Batch too large"}
        return {"success": True, "results": [f"processed_{item}" for item in batch]}
    
    batch_result = ErrorHandlingBestPractices.safe_batch_processing(
        list(range(10)), batch_size=3, process_func=dummy_process_func
    )
    print(f"   Result: {batch_result['success']}")
    print(f"   Success Rate: {batch_result['success_rate']:.2%}")
    print(f"   Successful Batches: {batch_result['successful_batches']}")
    print(f"   Failed Batches: {batch_result['failed_batches']}")

def print_best_practices_summary():
    """Print a summary of best practices."""
    print("\n📋 Best Practices Summary:")
    print("=" * 30)
    
    practices = [
        "✅ Always check file existence before operations",
        "✅ Handle specific exceptions (FileNotFoundError, ValueError, etc.)",
        "✅ Implement retry logic for transient failures",
        "✅ Provide helpful error messages and suggestions",
        "✅ Log errors for debugging and monitoring",
        "✅ Validate inputs before processing",
        "✅ Implement fallback strategies (CPU fallback, batch size reduction)",
        "✅ Handle memory errors gracefully",
        "✅ Support partial success in batch processing",
        "✅ Use appropriate error types and messages",
        "✅ Check system resources before heavy operations",
        "✅ Implement timeout mechanisms for long operations",
        "✅ Provide clear recovery instructions to users",
        "✅ Monitor and track error patterns",
        "✅ Test error scenarios thoroughly"
    ]
    
    for practice in practices:
        print(f"   {practice}")

if __name__ == "__main__":
    demonstrate_best_practices()
    print_best_practices_summary()
    
    print("\n🎯 Key Takeaways:")
    print("- Use try-except blocks for all error-prone operations")
    print("- Handle specific exceptions rather than generic ones")
    print("- Provide clear error messages and recovery suggestions")
    print("- Implement retry logic and fallback strategies")
    print("- Log errors for debugging and monitoring")
    print("- Validate inputs and check system resources")
    print("- Support partial success in batch operations") 