from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import asyncio
import json
import time
from typing import Dict, Any, List
from fastapi_best_practices_implementation import (
from typing import Any, List, Dict, Optional
import logging
"""
FastAPI Best Practices Runner Script
===================================

This script demonstrates FastAPI best practices including:
- Type hints and Pydantic models
- Async/sync function separation
- Error handling patterns
- Clean conditional statements
- File structure organization
"""

    # Models
    UserCreate, UserResponse, ModelTrainingRequest, ModelTrainingResponse,
    PredictionRequest, PredictionResponse, ErrorResponse,
    
    # Utilities
    DatabaseManager, validate_file_path, generate_request_id,
    log_request_info, log_error,
    
    # Functions
    calculate_model_metrics, validate_model_config, preprocess_input_data,
    train_model_async, predict_async, create_user_async,
    
    # Demonstrations
    demonstrate_type_hints, demonstrate_conditional_statements, demonstrate_error_handling
)


def demonstrate_pydantic_models():
    """Demonstrate Pydantic model validation"""
    print("\n" + "="*60)
    print("Pydantic Models and Validation")
    print("="*60)
    
    # Valid user creation
    print("\n1. Valid User Creation:")
    try:
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="SecurePass123"
        )
        print(f"  ✅ Valid user: {user_data.email}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Invalid email
    print("\n2. Invalid Email:")
    try:
        user_data = UserCreate(
            email="invalid-email",
            username="testuser",
            password="SecurePass123"
        )
    except Exception as e:
        print(f"  ❌ Expected error: {e}")
    
    # Invalid password
    print("\n3. Invalid Password:")
    try:
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="weak"
        )
    except Exception as e:
        print(f"  ❌ Expected error: {e}")
    
    # Valid model training request
    print("\n4. Valid Model Training Request:")
    try:
        training_request = ModelTrainingRequest(
            model_type="neural_network",
            training_data_path="data/train.csv",
            epochs=50,
            batch_size=32,
            learning_rate=0.001
        )
        print(f"  ✅ Valid training request: {training_request.model_type}")
    except Exception as e:
        print(f"  ❌ Error: {e}")


def demonstrate_type_hints_usage():
    """Demonstrate type hints usage"""
    print("\n" + "="*60)
    print("Type Hints Usage")
    print("="*60)
    
    # Demonstrate type hints
    demonstrate_type_hints()
    print("  ✅ Type hints demonstrated successfully")
    
    # Test type validation
    print("\n1. Type Validation Examples:")
    
    # Valid input
    try:
        metrics = calculate_model_metrics([0.1, 0.2, 0.3], [0.1, 0.2, 0.3])
        print(f"  ✅ Metrics calculated: {metrics}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Invalid input
    try:
        metrics = calculate_model_metrics([], [])
    except Exception as e:
        print(f"  ❌ Expected error: {e}")


def demonstrate_async_sync_functions():
    """Demonstrate async and sync function usage"""
    print("\n" + "="*60)
    print("Async and Sync Functions")
    print("="*60)
    
    async def run_async_demo():
        """Run async function demonstrations"""
        db = DatabaseManager()
        
        # Create user
        print("\n1. Creating User (Async):")
        try:
            user_data = UserCreate(
                email="async@example.com",
                username="asyncuser",
                password="SecurePass123"
            )
            user = await create_user_async(user_data, db)
            print(f"  ✅ User created: {user.username}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        # Train model
        print("\n2. Training Model (Async):")
        try:
            training_request = ModelTrainingRequest(
                model_type="transformer",
                training_data_path="data/train.csv",
                epochs=10
            )
            model = await train_model_async(training_request)
            print(f"  ✅ Model trained: {model.model_id}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        # Make prediction
        print("\n3. Making Prediction (Async):")
        try:
            prediction_request = PredictionRequest(
                model_id="model_123",
                input_data=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            )
            prediction = await predict_async(prediction_request, db)
            print(f"  ✅ Prediction made: {prediction.predictions}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Run async demo
    asyncio.run(run_async_demo())


def demonstrate_error_handling():
    """Demonstrate error handling patterns"""
    print("\n" + "="*60)
    print("Error Handling Patterns")
    print("="*60)
    
    # Demonstrate error handling
    demonstrate_error_handling()
    print("  ✅ Error handling patterns demonstrated")
    
    # Test early returns
    print("\n1. Early Return Pattern:")
    
    def process_data(data: List[int]) -> str:
        # Early error handling
        if not data:
            return "No data provided"
        
        if len(data) > 100:
            return "Too much data"
        
        if any(x < 0 for x in data):
            return "Negative values not allowed"
        
        # Happy path last
        return f"Processed {len(data)} items"
    
    test_cases = [
        [],
        [1, 2, 3, 4, 5] * 25,  # 125 items
        [1, -2, 3],
        [1, 2, 3, 4, 5]
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        result = process_data(test_data)
        print(f"  Test {i}: {result}")


def demonstrate_conditional_statements():
    """Demonstrate clean conditional statements"""
    print("\n" + "="*60)
    print("Clean Conditional Statements")
    print("="*60)
    
    # Demonstrate conditional statements
    demonstrate_conditional_statements()
    print("  ✅ Conditional statements demonstrated")
    
    # Test single-line conditionals
    print("\n1. Single-line Conditionals:")
    
    user_status = {
        "active": True,
        "verified": True,
        "premium": False
    }
    
    # Clean single-line conditionals
    if user_status["active"]: print("  ✅ User is active")
    if user_status["verified"]: print("  ✅ User is verified")
    if user_status["premium"]: print("  ✅ User is premium")
    if not user_status["premium"]: print("  ℹ️  User is not premium")


def demonstrate_utilities():
    """Demonstrate utility functions"""
    print("\n" + "="*60)
    print("Utility Functions")
    print("="*60)
    
    # Request ID generation
    print("\n1. Request ID Generation:")
    request_ids = [generate_request_id() for _ in range(3)]
    for i, req_id in enumerate(request_ids, 1):
        print(f"  Request {i}: {req_id}")
    
    # File path validation
    print("\n2. File Path Validation:")
    test_paths = [
        "data/train.csv",
        "nonexistent/file.txt",
        "README.md"
    ]
    
    for path in test_paths:
        is_valid = validate_file_path(path)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"  {path}: {status}")
    
    # Logging
    print("\n3. Logging Functions:")
    log_request_info("test_123", "/api/users", "GET")
    log_error("test_123", Exception("Test error"), "demo_function")
    print("  ✅ Logging functions called")


def demonstrate_data_processing():
    """Demonstrate data processing functions"""
    print("\n" + "="*60)
    print("Data Processing Functions")
    print("="*60)
    
    # Input data preprocessing
    print("\n1. Input Data Preprocessing:")
    test_data = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    
    # Without preprocessing
    processed_data = preprocess_input_data(test_data)
    print(f"  Original: {test_data}")
    print(f"  Processed: {processed_data}")
    
    # With normalization
    processed_data = preprocess_input_data(test_data, {"normalize": True})
    print(f"  Normalized: {processed_data}")
    
    # Model configuration validation
    print("\n2. Model Configuration Validation:")
    valid_config = {
        "model_type": "neural_network",
        "layers": [784, 512, 10],
        "activation": "relu"
    }
    
    try:
        is_valid = validate_model_config(valid_config)
        print(f"  ✅ Valid config: {is_valid}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Invalid config
    invalid_config = {
        "model_type": "neural_network",
        "layers": "invalid",
        "activation": "invalid"
    }
    
    try:
        is_valid = validate_model_config(invalid_config)
    except Exception as e:
        print(f"  ❌ Expected error: {e}")


def demonstrate_performance():
    """Demonstrate performance characteristics"""
    print("\n" + "="*60)
    print("Performance Analysis")
    print("="*60)
    
    # Test async function performance
    async def performance_test():
        
    """performance_test function."""
start_time = time.time()
        
        # Run multiple async operations
        tasks = []
        for i in range(5):
            training_request = ModelTrainingRequest(
                model_type=f"model_{i}",
                training_data_path="data/train.csv",
                epochs=5
            )
            task = train_model_async(training_request)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average time per operation: {total_time/5:.2f}s")
        print(f"  Successful operations: {sum(1 for r in results if not isinstance(r, Exception))}")
    
    asyncio.run(performance_test())


def demonstrate_file_structure():
    """Demonstrate file structure organization"""
    print("\n" + "="*60)
    print("File Structure Organization")
    print("="*60)
    
    structure = """
    fastapi_best_practices/
    ├── main.py                          # Main application entry point
    ├── requirements.txt                 # Dependencies
    ├── README.md                        # Documentation
    ├── routers/                         # Route definitions
    │   ├── __init__.py
    │   ├── user_routes.py              # User-related routes
    │   ├── model_routes.py             # Model-related routes
    │   └── prediction_routes.py        # Prediction-related routes
    ├── models/                          # Pydantic models
    │   ├── __init__.py
    │   ├── user_models.py              # User data models
    │   ├── model_models.py             # Model data models
    │   └── common_models.py            # Shared models
    ├── services/                        # Business logic
    │   ├── __init__.py
    │   ├── user_service.py             # User operations
    │   ├── model_service.py            # Model operations
    │   └── prediction_service.py       # Prediction operations
    ├── utils/                           # Utility functions
    │   ├── __init__.py
    │   ├── validation.py               # Validation utilities
    │   ├── logging.py                  # Logging utilities
    │   └── helpers.py                  # Helper functions
    ├── dependencies/                    # FastAPI dependencies
    │   ├── __init__.py
    │   ├── database.py                 # Database dependencies
    │   └── auth.py                     # Authentication dependencies
    ├── exceptions/                      # Custom exceptions
    │   ├── __init__.py
    │   └── custom_exceptions.py        # Custom exception classes
    ├── static/                          # Static files
    │   ├── css/
    │   ├── js/
    │   └── images/
    └── tests/                           # Test files
        ├── __init__.py
        ├── test_routes.py              # Route tests
        ├── test_models.py              # Model tests
        └── test_services.py            # Service tests
    """
    
    print(structure)


def main():
    """Main function to run all demonstrations"""
    print("FastAPI Best Practices Demonstrations")
    print("=" * 80)
    
    try:
        # Core demonstrations
        demonstrate_pydantic_models()
        demonstrate_type_hints_usage()
        demonstrate_async_sync_functions()
        demonstrate_error_handling()
        demonstrate_conditional_statements()
        demonstrate_utilities()
        demonstrate_data_processing()
        demonstrate_performance()
        demonstrate_file_structure()
        
        print("\n" + "="*80)
        print("All FastAPI Best Practices Demonstrations Completed Successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"\nError during demonstrations: {str(e)}")
        raise


match __name__:
    case "__main__":
    main() 