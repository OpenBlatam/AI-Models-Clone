from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
TIMEOUT_SECONDS = 60

# Constants
BUFFER_SIZE = 1024

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import json
import logging
import time
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import warnings
                from transformers import AutoTokenizer, AutoModel
from typing import Any, List, Dict, Optional
import asyncio
"""
🛡️ Try-Except Blocks Demo for Error-Prone Operations
===================================================
Demonstrating proper error handling with try-except blocks
for data loading and model inference operations.
"""

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for GPU availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")

class SafeDataLoader:
    """Safe data loading with comprehensive error handling."""
    
    def __init__(self) -> Any:
        self.loaded_data = {}
        self.error_log = []
    
    def load_csv_data(self, file_path: str) -> Dict[str, Any]:
        """Safely load CSV data with error handling."""
        try:
            logger.info(f"Attempting to load CSV file: {file_path}")
            
            # Check if file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            
            # Load CSV data
            data = pd.read_csv(file_path)
            
            # Validate data structure
            if data.empty:
                raise ValueError("CSV file is empty")
            
            # Check for required columns
            required_columns = ['text', 'label']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert to dictionary
            result = {
                "data": data.to_dict('records'),
                "shape": data.shape,
                "columns": list(data.columns),
                "file_path": file_path,
                "load_time": time.time()
            }
            
            logger.info(f"Successfully loaded CSV data: {data.shape}")
            return result
            
        except FileNotFoundError as e:
            logger.error(f"File not found error: {e}")
            return {
                "success": False,
                "error": "File not found",
                "message": str(e),
                "suggestion": "Please check the file path and ensure the file exists."
            }
        
        except pd.errors.EmptyDataError as e:
            logger.error(f"Empty data error: {e}")
            return {
                "success": False,
                "error": "Empty data",
                "message": str(e),
                "suggestion": "The CSV file appears to be empty. Please check the file content."
            }
        
        except pd.errors.ParserError as e:
            logger.error(f"Parser error: {e}")
            return {
                "success": False,
                "error": "Parser error",
                "message": str(e),
                "suggestion": "The CSV file format is invalid. Please check the file format."
            }
        
        except ValueError as e:
            logger.error(f"Value error: {e}")
            return {
                "success": False,
                "error": "Validation error",
                "message": str(e),
                "suggestion": "The data format is invalid. Please check the required columns."
            }
        
        except Exception as e:
            logger.error(f"Unexpected error loading CSV: {e}")
            return {
                "success": False,
                "error": "Unexpected error",
                "message": str(e),
                "suggestion": "An unexpected error occurred. Please try again."
            }
    
    def load_json_data(self, file_path: str) -> Dict[str, Any]:
        """Safely load JSON data with error handling."""
        try:
            logger.info(f"Attempting to load JSON file: {file_path}")
            
            # Check if file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"JSON file not found: {file_path}")
            
            # Load JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                data = json.load(f)
            
            # Validate data structure
            if not isinstance(data, (dict, list)):
                raise ValueError("JSON data must be an object or array")
            
            result = {
                "data": data,
                "type": type(data).__name__,
                "file_path": file_path,
                "load_time": time.time()
            }
            
            logger.info(f"Successfully loaded JSON data: {type(data).__name__}")
            return result
            
        except FileNotFoundError as e:
            logger.error(f"File not found error: {e}")
            return {
                "success": False,
                "error": "File not found",
                "message": str(e),
                "suggestion": "Please check the file path and ensure the file exists."
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {
                "success": False,
                "error": "JSON decode error",
                "message": str(e),
                "suggestion": "The JSON file format is invalid. Please check the file content."
            }
        
        except ValueError as e:
            logger.error(f"Value error: {e}")
            return {
                "success": False,
                "error": "Validation error",
                "message": str(e),
                "suggestion": "The data format is invalid."
            }
        
        except Exception as e:
            logger.error(f"Unexpected error loading JSON: {e}")
            return {
                "success": False,
                "error": "Unexpected error",
                "message": str(e),
                "suggestion": "An unexpected error occurred. Please try again."
            }
    
    def load_torch_model(self, model_path: str) -> Dict[str, Any]:
        """Safely load PyTorch model with error handling."""
        try:
            logger.info(f"Attempting to load PyTorch model: {model_path}")
            
            # Check if file exists
            if not Path(model_path).exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # Check available memory
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.get_device_properties(0).total_memory
                if gpu_memory < 2 * 1024**3:  # Less than 2GB
                    logger.warning("Low GPU memory detected, consider using CPU")
            
            # Load model
            model = torch.load(model_path, map_location=DEVICE)
            
            # Validate model
            if not isinstance(model, nn.Module):
                raise ValueError("Loaded file is not a valid PyTorch model")
            
            # Set model to evaluation mode
            model.eval()
            
            result = {
                "model": model,
                "model_path": model_path,
                "device": str(DEVICE),
                "load_time": time.time(),
                "model_type": type(model).__name__
            }
            
            logger.info(f"Successfully loaded PyTorch model: {type(model).__name__}")
            return result
            
        except FileNotFoundError as e:
            logger.error(f"File not found error: {e}")
            return {
                "success": False,
                "error": "File not found",
                "message": str(e),
                "suggestion": "Please check the model path and ensure the file exists."
            }
        
        except RuntimeError as e:
            logger.error(f"Runtime error loading model: {e}")
            if "out of memory" in str(e).lower():
                return {
                    "success": False,
                    "error": "Out of memory",
                    "message": str(e),
                    "suggestion": "Try reducing batch size or use CPU instead of GPU."
                }
            else:
                return {
                    "success": False,
                    "error": "Runtime error",
                    "message": str(e),
                    "suggestion": "The model file may be corrupted or incompatible."
                }
        
        except ValueError as e:
            logger.error(f"Value error: {e}")
            return {
                "success": False,
                "error": "Validation error",
                "message": str(e),
                "suggestion": "The loaded file is not a valid PyTorch model."
            }
        
        except Exception as e:
            logger.error(f"Unexpected error loading model: {e}")
            return {
                "success": False,
                "error": "Unexpected error",
                "message": str(e),
                "suggestion": "An unexpected error occurred. Please try again."
            }

class SafeModelInference:
    """Safe model inference with comprehensive error handling."""
    
    def __init__(self) -> Any:
        self.model = None
        self.tokenizer = None
        self.error_log = []
    
    def load_model_and_tokenizer(self, model_name: str) -> Dict[str, Any]:
        """Safely load model and tokenizer with error handling."""
        try:
            logger.info(f"Attempting to load model and tokenizer: {model_name}")
            
            # Import transformers safely
            try:
            except ImportError as e:
                raise ImportError(f"Transformers library not available: {e}")
            
            # Load tokenizer
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                logger.info("Tokenizer loaded successfully")
            except Exception as e:
                logger.error(f"Error loading tokenizer: {e}")
                raise RuntimeError(f"Failed to load tokenizer: {e}")
            
            # Load model
            try:
                self.model = AutoModel.from_pretrained(model_name)
                self.model.to(DEVICE)
                self.model.eval()
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                raise RuntimeError(f"Failed to load model: {e}")
            
            return {
                "success": True,
                "model_name": model_name,
                "device": str(DEVICE),
                "load_time": time.time()
            }
            
        except ImportError as e:
            logger.error(f"Import error: {e}")
            return {
                "success": False,
                "error": "Import error",
                "message": str(e),
                "suggestion": "Please install the required libraries: pip install transformers torch"
            }
        
        except RuntimeError as e:
            logger.error(f"Runtime error: {e}")
            return {
                "success": False,
                "error": "Runtime error",
                "message": str(e),
                "suggestion": "Check your internet connection and model name."
            }
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": "Unexpected error",
                "message": str(e),
                "suggestion": "An unexpected error occurred. Please try again."
            }
    
    def safe_inference(self, text: str, max_length: int = 512) -> Dict[str, Any]:
        """Safely perform model inference with error handling."""
        try:
            logger.info(f"Performing inference on text: {text[:50]}...")
            
            # Validate inputs
            if not text or not text.strip():
                raise ValueError("Text input cannot be empty")
            
            if max_length <= 0 or max_length > 2048:
                raise ValueError("Max length must be between 1 and 2048")
            
            # Check if model is loaded
            if self.model is None or self.tokenizer is None:
                raise RuntimeError("Model and tokenizer must be loaded before inference")
            
            # Tokenize input
            try:
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    max_length=max_length,
                    truncation=True,
                    padding=True
                )
                inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
                logger.info("Text tokenized successfully")
            except Exception as e:
                logger.error(f"Tokenization error: {e}")
                raise RuntimeError(f"Failed to tokenize text: {e}")
            
            # Perform inference
            try:
                with torch.no_grad():
                    outputs = self.model(**inputs)
                logger.info("Inference completed successfully")
            except RuntimeError as e:
                if "out of memory" in str(e).lower():
                    logger.error("GPU out of memory during inference")
                    # Try with CPU
                    try:
                        self.model.to('cpu')
                        inputs = {k: v.to('cpu') for k, v in inputs.items()}
                        with torch.no_grad():
                            outputs = self.model(**inputs)
                        self.model.to(DEVICE)
                        logger.info("Inference completed on CPU")
                    except Exception as cpu_e:
                        raise RuntimeError(f"Failed to run inference on CPU: {cpu_e}")
                else:
                    raise e
            
            # Process outputs
            try:
                # Extract features (last hidden state)
                features = outputs.last_hidden_state.mean(dim=1)
                result = {
                    "success": True,
                    "features": features.cpu().numpy(),
                    "input_length": len(text),
                    "output_shape": features.shape,
                    "inference_time": time.time()
                }
                logger.info("Output processing completed")
                return result
                
            except Exception as e:
                logger.error(f"Output processing error: {e}")
                raise RuntimeError(f"Failed to process model outputs: {e}")
            
        except ValueError as e:
            logger.error(f"Value error during inference: {e}")
            return {
                "success": False,
                "error": "Validation error",
                "message": str(e),
                "suggestion": "Please check your input parameters."
            }
        
        except RuntimeError as e:
            logger.error(f"Runtime error during inference: {e}")
            return {
                "success": False,
                "error": "Runtime error",
                "message": str(e),
                "suggestion": "Try reducing input length or using a smaller model."
            }
        
        except Exception as e:
            logger.error(f"Unexpected error during inference: {e}")
            return {
                "success": False,
                "error": "Unexpected error",
                "message": str(e),
                "suggestion": "An unexpected error occurred. Please try again."
            }
    
    def batch_inference(self, texts: List[str], batch_size: int = 8) -> Dict[str, Any]:
        """Safely perform batch inference with error handling."""
        try:
            logger.info(f"Performing batch inference on {len(texts)} texts")
            
            # Validate inputs
            if not texts:
                raise ValueError("Text list cannot be empty")
            
            if batch_size <= 0 or batch_size > 32:
                raise ValueError("Batch size must be between 1 and 32")
            
            # Check if model is loaded
            if self.model is None or self.tokenizer is None:
                raise RuntimeError("Model and tokenizer must be loaded before inference")
            
            results = []
            total_time = time.time()
            
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                try:
                    # Tokenize batch
                    inputs = self.tokenizer(
                        batch_texts,
                        return_tensors="pt",
                        max_length=512,
                        truncation=True,
                        padding=True
                    )
                    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
                    
                    # Perform inference
                    with torch.no_grad():
                        outputs = self.model(**inputs)
                    
                    # Process outputs
                    features = outputs.last_hidden_state.mean(dim=1)
                    batch_results = features.cpu().numpy()
                    
                    results.extend(batch_results)
                    logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
                    
                except RuntimeError as e:
                    if "out of memory" in str(e).lower():
                        logger.warning("GPU out of memory, reducing batch size")
                        # Try with smaller batch
                        smaller_batch_size = batch_size // 2
                        if smaller_batch_size >= 1:
                            return self.batch_inference(texts, smaller_batch_size)
                        else:
                            raise RuntimeError("Cannot reduce batch size further")
                    else:
                        raise e
            
            total_time = time.time() - total_time
            
            return {
                "success": True,
                "results": results,
                "num_texts": len(texts),
                "batch_size": batch_size,
                "total_time": total_time,
                "avg_time_per_text": total_time / len(texts)
            }
            
        except ValueError as e:
            logger.error(f"Value error during batch inference: {e}")
            return {
                "success": False,
                "error": "Validation error",
                "message": str(e),
                "suggestion": "Please check your input parameters."
            }
        
        except RuntimeError as e:
            logger.error(f"Runtime error during batch inference: {e}")
            return {
                "success": False,
                "error": "Runtime error",
                "message": str(e),
                "suggestion": "Try reducing batch size or input length."
            }
        
        except Exception as e:
            logger.error(f"Unexpected error during batch inference: {e}")
            return {
                "success": False,
                "error": "Unexpected error",
                "message": str(e),
                "suggestion": "An unexpected error occurred. Please try again."
            }

def demo_data_loading():
    """Demo data loading with error handling."""
    print("🔄 Demo: Data Loading with Error Handling")
    print("=" * 50)
    
    loader = SafeDataLoader()
    
    # Test CSV loading
    print("\n1. Testing CSV loading...")
    csv_result = loader.load_csv_data("nonexistent_file.csv")
    if not csv_result.get("success", True):
        print(f"❌ Error: {csv_result['error']}")
        print(f"   Message: {csv_result['message']}")
        print(f"   Suggestion: {csv_result['suggestion']}")
    
    # Test JSON loading
    print("\n2. Testing JSON loading...")
    json_result = loader.load_json_data("nonexistent_file.json")
    if not json_result.get("success", True):
        print(f"❌ Error: {json_result['error']}")
        print(f"   Message: {json_result['message']}")
        print(f"   Suggestion: {json_result['suggestion']}")
    
    # Test PyTorch model loading
    print("\n3. Testing PyTorch model loading...")
    model_result = loader.load_torch_model("nonexistent_model.pth")
    if not model_result.get("success", True):
        print(f"❌ Error: {model_result['error']}")
        print(f"   Message: {model_result['message']}")
        print(f"   Suggestion: {model_result['suggestion']}")

def demo_model_inference():
    """Demo model inference with error handling."""
    print("\n🔄 Demo: Model Inference with Error Handling")
    print("=" * 50)
    
    inference = SafeModelInference()
    
    # Test model loading
    print("\n1. Testing model loading...")
    load_result = inference.load_model_and_tokenizer("bert-base-uncased")
    if load_result.get("success"):
        print("✅ Model loaded successfully")
        
        # Test single inference
        print("\n2. Testing single inference...")
        inference_result = inference.safe_inference("Hello world!")
        if inference_result.get("success"):
            print("✅ Single inference successful")
            print(f"   Output shape: {inference_result['output_shape']}")
        else:
            print(f"❌ Inference error: {inference_result['error']}")
            print(f"   Message: {inference_result['message']}")
        
        # Test batch inference
        print("\n3. Testing batch inference...")
        texts = ["Hello world!", "How are you?", "Nice to meet you!"]
        batch_result = inference.batch_inference(texts, batch_size=2)
        if batch_result.get("success"):
            print("✅ Batch inference successful")
            print(f"   Processed {batch_result['num_texts']} texts")
            print(f"   Average time per text: {batch_result['avg_time_per_text']:.3f}s")
        else:
            print(f"❌ Batch inference error: {batch_result['error']}")
            print(f"   Message: {batch_result['message']}")
    else:
        print(f"❌ Model loading error: {load_result['error']}")
        print(f"   Message: {load_result['message']}")
        print(f"   Suggestion: {load_result['suggestion']}")

def demo_error_scenarios():
    """Demo various error scenarios."""
    print("\n🔄 Demo: Error Scenarios")
    print("=" * 50)
    
    inference = SafeModelInference()
    
    # Test empty text
    print("\n1. Testing empty text input...")
    result = inference.safe_inference("")
    if not result.get("success"):
        print(f"❌ Expected error: {result['error']}")
        print(f"   Message: {result['message']}")
    
    # Test invalid max_length
    print("\n2. Testing invalid max_length...")
    result = inference.safe_inference("Hello world!", max_length=0)
    if not result.get("success"):
        print(f"❌ Expected error: {result['error']}")
        print(f"   Message: {result['message']}")
    
    # Test inference without loading model
    print("\n3. Testing inference without loading model...")
    result = inference.safe_inference("Hello world!")
    if not result.get("success"):
        print(f"❌ Expected error: {result['error']}")
        print(f"   Message: {result['message']}")

if __name__ == "__main__":
    print("🛡️ Try-Except Blocks Demo for Error-Prone Operations")
    print("=" * 60)
    
    # Run demos
    demo_data_loading()
    demo_model_inference()
    demo_error_scenarios()
    
    print("\n✅ Demo completed successfully!")
    print("\nKey takeaways:")
    print("- Always use try-except blocks for file operations")
    print("- Handle specific exceptions (FileNotFoundError, ValueError, etc.)")
    print("- Provide helpful error messages and suggestions")
    print("- Implement fallback strategies (CPU fallback, batch size reduction)")
    print("- Log errors for debugging")
    print("- Validate inputs before processing") 