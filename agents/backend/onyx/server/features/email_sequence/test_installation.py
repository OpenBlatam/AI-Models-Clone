#!/usr/bin/env python3
"""
Test script to verify Email Sequence AI System installation
"""

import sys
from pathlib import Path

def test_imports():
    """Test all core imports."""
    print("🧪 Testing Email Sequence AI System Installation")
    print("=" * 50)
    
    # Test core ML/AI libraries
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
    except ImportError as e:
        print(f"❌ PyTorch: {e}")
        return False
    
    try:
        import transformers
        print(f"✅ Transformers: {transformers.__version__}")
    except ImportError as e:
        print(f"❌ Transformers: {e}")
        return False
    
    try:
        import datasets
        print(f"✅ Datasets: {datasets.__version__}")
    except ImportError as e:
        print(f"❌ Datasets: {e}")
        return False
    
    # Test data processing libraries
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy: {e}")
        return False
    
    try:
        import pandas as pd
        print(f"✅ Pandas: {pd.__version__}")
    except ImportError as e:
        print(f"❌ Pandas: {e}")
        return False
    
    try:
        import sklearn
        print(f"✅ Scikit-learn: {sklearn.__version__}")
    except ImportError as e:
        print(f"❌ Scikit-learn: {e}")
        return False
    
    # Test web interface
    try:
        import gradio
        print(f"✅ Gradio: {gradio.__version__}")
    except ImportError as e:
        print(f"❌ Gradio: {e}")
        return False
    
    # Test configuration and utilities
    try:
        import yaml
        print("✅ PyYAML")
    except ImportError as e:
        print(f"❌ PyYAML: {e}")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv")
    except ImportError as e:
        print(f"❌ python-dotenv: {e}")
        return False
    
    try:
        from loguru import logger
        print("✅ Loguru")
    except ImportError as e:
        print(f"❌ Loguru: {e}")
        return False
    
    try:
        from tqdm import tqdm
        print("✅ tqdm")
    except ImportError as e:
        print(f"❌ tqdm: {e}")
        return False
    
    try:
        from pydantic import BaseModel
        print("✅ Pydantic")
    except ImportError as e:
        print(f"❌ Pydantic: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality."""
    print("\n🔧 Testing Basic Functionality")
    print("=" * 50)
    
    # Test PyTorch tensor operations
    try:
        import torch
        x = torch.randn(2, 3)
        y = torch.randn(2, 3)
        z = x + y
        print("✅ PyTorch tensor operations")
    except Exception as e:
        print(f"❌ PyTorch tensor operations: {e}")
        return False
    
    # Test NumPy operations
    try:
        import numpy as np
        arr = np.random.randn(3, 3)
        result = np.linalg.inv(arr)
        print("✅ NumPy operations")
    except Exception as e:
        print(f"❌ NumPy operations: {e}")
        return False
    
    # Test Pandas operations
    try:
        import pandas as pd
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        result = df.describe()
        print("✅ Pandas operations")
    except Exception as e:
        print(f"❌ Pandas operations: {e}")
        return False
    
    # Test Transformers
    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("gpt2", use_fast=False)
        text = "Hello, world!"
        tokens = tokenizer.encode(text)
        print("✅ Transformers tokenizer")
    except Exception as e:
        print(f"❌ Transformers tokenizer: {e}")
        return False
    
    # Test Gradio
    try:
        import gradio as gr
        print("✅ Gradio import")
    except Exception as e:
        print(f"❌ Gradio import: {e}")
        return False
    
    return True

def test_system_info():
    """Display system information."""
    print("\n💻 System Information")
    print("=" * 50)
    
    import platform
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    print(f"Processor: {platform.processor()}")
    
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"GPU count: {torch.cuda.device_count()}")
    except ImportError:
        print("PyTorch not available")

def main():
    """Main test function."""
    print("🚀 Email Sequence AI System - Installation Test")
    print("=" * 60)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test functionality
        functionality_ok = test_basic_functionality()
        
        # Display system info
        test_system_info()
        
        if functionality_ok:
            print("\n🎉 All tests passed! Installation is successful.")
            print("\nNext steps:")
            print("1. Run the basic demo: python examples/basic_demo.py")
            print("2. Start training: python examples/training_example.py")
            print("3. Launch Gradio app: python examples/gradio_app.py")
            return True
        else:
            print("\n⚠️  Some functionality tests failed.")
            return False
    else:
        print("\n❌ Import tests failed. Please check your installation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 