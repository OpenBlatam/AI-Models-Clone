#!/usr/bin/env python3
"""
Test script for code profiling integration with Gradio app.
"""

import sys
import os
import json
import torch
import numpy as np
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_code_profiling_imports():
    """Test that code profiling system can be imported."""
    print("Testing code profiling imports...")
    
    try:
        from code_profiling_system import (
            CodeProfiler, DataLoadingProfiler, PreprocessingProfiler,
            ProfilingConfig, ProfilingResult, profile_function,
            profile_data_loading, profile_preprocessing
        )
        print("✅ Code profiling system imports successful")
        return True
    except ImportError as e:
        print(f"❌ Code profiling system import failed: {e}")
        return False

def test_gradio_app_imports():
    """Test that Gradio app can import code profiling system."""
    print("\nTesting Gradio app imports...")
    
    try:
        # Import the gradio app module
        import gradio_app
        print("✅ Gradio app import successful")
        
        # Check if CODE_PROFILING_AVAILABLE is defined
        if hasattr(gradio_app, 'CODE_PROFILING_AVAILABLE'):
            print(f"✅ CODE_PROFILING_AVAILABLE: {gradio_app.CODE_PROFILING_AVAILABLE}")
        else:
            print("❌ CODE_PROFILING_AVAILABLE not found")
            return False
            
        return True
    except ImportError as e:
        print(f"❌ Gradio app import failed: {e}")
        return False

def test_profiling_interface_functions():
    """Test that profiling interface functions exist."""
    print("\nTesting profiling interface functions...")
    
    try:
        import gradio_app
        
        # Check if interface functions exist
        required_functions = [
            'profile_function_interface',
            'profile_data_loading_interface',
            'profile_preprocessing_interface',
            'analyze_bottlenecks_interface',
            'get_profiling_recommendations_interface',
            'export_profiling_results_interface'
        ]
        
        for func_name in required_functions:
            if hasattr(gradio_app, func_name):
                print(f"✅ {func_name} found")
            else:
                print(f"❌ {func_name} not found")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error testing interface functions: {e}")
        return False

def test_basic_profiling():
    """Test basic profiling functionality."""
    print("\nTesting basic profiling functionality...")
    
    try:
        from code_profiling_system import CodeProfiler, ProfilingConfig
        
        # Create a simple test function
        def test_function(x):
            return x * 2
        
        # Create profiling configuration
        config = ProfilingConfig(
            enable_gpu_profiling=False,
            enable_memory_profiling=True,
            num_iterations=5,
            export_results=False
        )
        
        # Create profiler and run test
        profiler = CodeProfiler(config)
        result = profiler.profile_function(test_function, 10, config)
        
        print(f"✅ Basic profiling successful")
        print(f"   - Function name: {result.function_name}")
        print(f"   - Execution time: {result.execution_time:.4f}s")
        print(f"   - Memory usage: {result.memory_usage:.2f} MB")
        
        return True
    except Exception as e:
        print(f"❌ Basic profiling failed: {e}")
        return False

def test_data_loading_profiling():
    """Test data loading profiling functionality."""
    print("\nTesting data loading profiling...")
    
    try:
        from code_profiling_system import DataLoadingProfiler, ProfilingConfig
        from torch.utils.data import DataLoader, TensorDataset
        
        # Create sample data
        data = torch.randn(100, 10)
        labels = torch.randint(0, 2, (100,))
        dataset = TensorDataset(data, labels)
        dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
        
        # Create profiling configuration
        config = ProfilingConfig(
            enable_gpu_profiling=False,
            enable_memory_profiling=True,
            num_iterations=3,
            export_results=False
        )
        
        # Create profiler and run test
        profiler = DataLoadingProfiler(config)
        result = profiler.profile_dataloader(dataloader, num_epochs=1)
        
        print(f"✅ Data loading profiling successful")
        print(f"   - Total time: {result.execution_time:.4f}s")
        print(f"   - Memory usage: {result.memory_usage:.2f} MB")
        
        return True
    except Exception as e:
        print(f"❌ Data loading profiling failed: {e}")
        return False

def test_preprocessing_profiling():
    """Test preprocessing profiling functionality."""
    print("\nTesting preprocessing profiling...")
    
    try:
        from code_profiling_system import PreprocessingProfiler, ProfilingConfig
        
        # Create a simple preprocessing function
        def preprocess_data(data):
            return [float(x) for x in data]
        
        # Create profiling configuration
        config = ProfilingConfig(
            enable_gpu_profiling=False,
            enable_memory_profiling=True,
            num_iterations=5,
            export_results=False
        )
        
        # Create profiler and run test
        profiler = PreprocessingProfiler(config)
        sample_input = [1, 2, 3, 4, 5]
        result = profiler.profile_preprocessing_function(preprocess_data, sample_input)
        
        print(f"✅ Preprocessing profiling successful")
        print(f"   - Function name: {result.function_name}")
        print(f"   - Execution time: {result.execution_time:.4f}s")
        print(f"   - Memory usage: {result.memory_usage:.2f} MB")
        
        return True
    except Exception as e:
        print(f"❌ Preprocessing profiling failed: {e}")
        return False

def test_bottleneck_analysis():
    """Test bottleneck analysis functionality."""
    print("\nTesting bottleneck analysis...")
    
    try:
        from code_profiling_system import CodeProfiler
        
        # Create profiler
        profiler = CodeProfiler()
        
        # Create sample profiling results
        sample_results = {
            'function_name': 'test_function',
            'execution_time': 0.1,
            'memory_usage': 50.0,
            'cpu_usage': 25.0,
            'gpu_usage': 0.0,
            'io_operations': 10
        }
        
        # Analyze bottlenecks
        analysis = profiler.analyze_bottlenecks(sample_results)
        
        print(f"✅ Bottleneck analysis successful")
        print(f"   - Bottlenecks found: {len(analysis.get('bottlenecks', []))}")
        print(f"   - Recommendations: {len(analysis.get('recommendations', []))}")
        
        return True
    except Exception as e:
        print(f"❌ Bottleneck analysis failed: {e}")
        return False

def test_optimization_recommendations():
    """Test optimization recommendations functionality."""
    print("\nTesting optimization recommendations...")
    
    try:
        from code_profiling_system import CodeProfiler
        
        # Create profiler
        profiler = CodeProfiler()
        
        # Get recommendations
        recommendations = profiler.get_optimization_recommendations()
        
        print(f"✅ Optimization recommendations successful")
        print(f"   - Recommendations count: {len(recommendations)}")
        
        return True
    except Exception as e:
        print(f"❌ Optimization recommendations failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Code Profiling Integration with Gradio App")
    print("=" * 60)
    
    tests = [
        test_code_profiling_imports,
        test_gradio_app_imports,
        test_profiling_interface_functions,
        test_basic_profiling,
        test_data_loading_profiling,
        test_preprocessing_profiling,
        test_bottleneck_analysis,
        test_optimization_recommendations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Code profiling integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 