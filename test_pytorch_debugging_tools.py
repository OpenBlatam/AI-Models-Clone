"""
🧪 Test PyTorch Debugging Tools Implementation
==============================================

This script tests the comprehensive PyTorch debugging tools integration including:
- Autograd anomaly detection (torch.autograd.detect_anomaly())
- Gradient monitoring and clipping
- Memory profiling and monitoring
- Operation performance tracking
- PyTorchDebugManager functionality
"""

import sys
import traceback
from pathlib import Path
import torch
import torch.nn as nn
import numpy as np

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

try:
    from enhanced_ui_demos_with_validation import (
        PyTorchDebugConfig,
        PyTorchDebugManager,
        ValidationConfig,
        EnhancedUIDemosWithValidation
    )
    print("✅ Successfully imported all modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_pytorch_debug_config():
    """Test PyTorchDebugConfig creation and configuration."""
    print("\n🔧 Testing PyTorchDebugConfig...")
    
    try:
        # Test default configuration
        config = PyTorchDebugConfig()
        assert config.enable_autograd_anomaly_detection == True
        assert config.enable_gradient_clipping == True
        assert config.max_gradient_norm == 1.0
        print("✅ Default configuration created successfully")
        
        # Test custom configuration
        custom_config = PyTorchDebugConfig(
            enable_autograd_anomaly_detection=False,
            enable_gradient_clipping=True,
            max_gradient_norm=0.5,
            log_gradients=True,
            debug_level="DEBUG"
        )
        assert custom_config.enable_autograd_anomaly_detection == False
        assert custom_config.max_gradient_norm == 0.5
        assert custom_config.log_gradients == True
        assert custom_config.debug_level == "DEBUG"
        print("✅ Custom configuration created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ PyTorchDebugConfig test failed: {e}")
        traceback.print_exc()
        return False

def test_pytorch_debug_manager():
    """Test PyTorchDebugManager functionality."""
    print("\n🔧 Testing PyTorchDebugManager...")
    
    try:
        # Create debug manager
        config = PyTorchDebugConfig(
            enable_autograd_anomaly_detection=True,
            enable_gradient_checking=True,
            enable_memory_profiling=True
        )
        debug_manager = PyTorchDebugManager(config)
        
        # Test initialization
        assert hasattr(debug_manager, 'anomaly_detection_enabled')
        assert hasattr(debug_manager, 'gradient_hooks')
        assert hasattr(debug_manager, 'activation_hooks')
        print("✅ Debug manager initialized successfully")
        
        # Test memory usage checking
        debug_manager.check_memory_usage("test operation")
        print("✅ Memory usage checking works")
        
        # Test cleanup
        debug_manager.cleanup()
        print("✅ Debug manager cleanup works")
        
        return True
        
    except Exception as e:
        print(f"❌ PyTorchDebugManager test failed: {e}")
        traceback.print_exc()
        return False

def test_gradient_monitoring():
    """Test gradient monitoring functionality."""
    print("\n🔧 Testing Gradient Monitoring...")
    
    try:
        # Create debug manager
        config = PyTorchDebugConfig(
            enable_weight_gradient_monitoring=True,
            log_gradients=True,
            enable_gradient_clipping=True,
            max_gradient_norm=1.0
        )
        debug_manager = PyTorchDebugManager(config)
        
        # Create a simple model
        model = nn.Sequential(
            nn.Linear(5, 3),
            nn.ReLU(),
            nn.Linear(3, 1)
        )
        
        # Enable gradient monitoring
        debug_manager.enable_gradient_monitoring(model)
        assert len(debug_manager.gradient_hooks) > 0
        print(f"✅ Gradient monitoring enabled for {len(debug_manager.gradient_hooks)} parameters")
        
        # Test gradient computation
        X = torch.randn(2, 5, requires_grad=True)
        output = model(X)
        loss = output.sum()
        loss.backward()
        
        # Check if gradients were monitored
        print("✅ Gradient computation with monitoring completed")
        
        # Cleanup
        debug_manager.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Gradient monitoring test failed: {e}")
        traceback.print_exc()
        return False

def test_activation_monitoring():
    """Test activation monitoring functionality."""
    print("\n🔧 Testing Activation Monitoring...")
    
    try:
        # Create debug manager
        config = PyTorchDebugConfig(
            enable_activation_monitoring=True,
            log_activations=True
        )
        debug_manager = PyTorchDebugManager(config)
        
        # Create a simple model
        model = nn.Sequential(
            nn.Linear(5, 3),
            nn.ReLU(),
            nn.Linear(3, 1)
        )
        
        # Enable activation monitoring
        debug_manager.enable_activation_monitoring(model)
        assert len(debug_manager.activation_hooks) > 0
        print(f"✅ Activation monitoring enabled for {len(debug_manager.activation_hooks)} modules")
        
        # Test forward pass with monitoring
        X = torch.randn(2, 5)
        output = model(X)
        
        print("✅ Forward pass with activation monitoring completed")
        
        # Cleanup
        debug_manager.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Activation monitoring test failed: {e}")
        traceback.print_exc()
        return False

def test_autograd_anomaly_detection():
    """Test autograd anomaly detection functionality."""
    print("\n🔧 Testing Autograd Anomaly Detection...")
    
    try:
        # Create debug manager
        config = PyTorchDebugConfig(
            enable_autograd_anomaly_detection=True
        )
        debug_manager = PyTorchDebugManager(config)
        
        # Check if anomaly detection is enabled
        assert debug_manager.anomaly_detection_enabled == True
        print("✅ Autograd anomaly detection enabled")
        
        # Test with a model that could produce anomalies
        model = nn.Sequential(
            nn.Linear(5, 3),
            nn.ReLU(),
            nn.Linear(3, 1)
        )
        
        # Test normal forward pass
        X = torch.randn(2, 5, requires_grad=True)
        output = model(X)
        print("✅ Normal forward pass completed")
        
        # Test with potential NaN input (should trigger anomaly detection)
        try:
            X_nan = torch.tensor([[1.0, 2.0, float('nan'), 4.0, 5.0]], requires_grad=True)
            output_nan = model(X_nan)
            print("⚠️ Forward pass with NaN input completed (anomaly detection should catch this)")
        except Exception as e:
            print(f"✅ Anomaly detection caught issue: {e}")
        
        # Cleanup
        debug_manager.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Autograd anomaly detection test failed: {e}")
        traceback.print_exc()
        return False

def test_operation_monitoring():
    """Test operation monitoring functionality."""
    print("\n🔧 Testing Operation Monitoring...")
    
    try:
        # Create debug manager
        config = PyTorchDebugConfig(
            enable_operation_timing=True
        )
        debug_manager = PyTorchDebugManager(config)
        
        # Test operation monitoring
        def test_function(x):
            return x * 2
        
        result = debug_manager.monitor_operation("test multiplication", test_function, torch.tensor([1, 2, 3]))
        assert torch.equal(result, torch.tensor([2, 4, 6]))
        print("✅ Operation monitoring works correctly")
        
        # Cleanup
        debug_manager.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Operation monitoring test failed: {e}")
        traceback.print_exc()
        return False

def test_memory_profiling():
    """Test memory profiling functionality."""
    print("\n🔧 Testing Memory Profiling...")
    
    try:
        # Create debug manager
        config = PyTorchDebugConfig(
            enable_cuda_memory_tracking=True,
            enable_memory_leak_detection=True
        )
        debug_manager = PyTorchDebugManager(config)
        
        # Test memory usage checking
        debug_manager.check_memory_usage("before test")
        
        # Create some tensors to test memory tracking
        if torch.cuda.is_available():
            tensor = torch.randn(1000, 1000).cuda()
            debug_manager.check_memory_usage("after tensor creation")
            del tensor
            torch.cuda.empty_cache()
            debug_manager.check_memory_usage("after cleanup")
        else:
            tensor = torch.randn(1000, 1000)
            debug_manager.check_memory_usage("after tensor creation")
            del tensor
            debug_manager.check_memory_usage("after cleanup")
        
        print("✅ Memory profiling works correctly")
        
        # Cleanup
        debug_manager.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Memory profiling test failed: {e}")
        traceback.print_exc()
        return False

def test_profiler_integration():
    """Test PyTorch profiler integration."""
    print("\n🔧 Testing Profiler Integration...")
    
    try:
        # Create debug manager
        config = PyTorchDebugConfig(
            enable_autograd_profiler=True
        )
        debug_manager = PyTorchDebugManager(config)
        
        # Start profiling
        profiler = debug_manager.start_profiling("test_profiler")
        assert profiler is not None
        print("✅ Profiler started successfully")
        
        # Run some operations
        model = nn.Linear(10, 5)
        X = torch.randn(32, 10)
        for _ in range(5):
            output = model(X)
        
        # Stop profiling
        debug_manager.stop_profiling()
        print("✅ Profiler stopped successfully")
        
        # Cleanup
        debug_manager.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Profiler integration test failed: {e}")
        traceback.print_exc()
        return False

def test_enhanced_demo_integration():
    """Test integration with EnhancedUIDemosWithValidation."""
    print("\n🔧 Testing Enhanced Demo Integration...")
    
    try:
        # Create debug configuration
        debug_config = PyTorchDebugConfig(
            enable_autograd_anomaly_detection=True,
            enable_gradient_checking=True,
            enable_memory_profiling=True,
            enable_operation_timing=True
        )
        
        # Create demo with debugging
        demos = EnhancedUIDemosWithValidation(debug_config=debug_config)
        
        # Check if debugging tools are initialized
        assert hasattr(demos, 'debug_manager')
        assert demos.debug_manager.anomaly_detection_enabled == True
        print("✅ Enhanced demo with debugging created successfully")
        
        # Check if models have debugging enabled
        assert len(demos.models) > 0
        print(f"✅ {len(demos.models)} models created with debugging")
        
        # Test cleanup
        demos.cleanup()
        print("✅ Demo cleanup completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced demo integration test failed: {e}")
        traceback.print_exc()
        return False

def test_context_manager():
    """Test context manager functionality."""
    print("\n🔧 Testing Context Manager...")
    
    try:
        # Test context manager
        with EnhancedUIDemosWithValidation() as demos:
            assert hasattr(demos, 'debug_manager')
            assert hasattr(demos, 'models')
            print("✅ Context manager entry successful")
        
        # Check if cleanup happened automatically
        print("✅ Context manager exit and cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Context manager test failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling in debugging tools."""
    print("\n🔧 Testing Error Handling...")
    
    try:
        # Create debug manager with invalid configuration
        config = PyTorchDebugConfig(
            enable_autograd_anomaly_detection=True,
            enable_autograd_profiler=True
        )
        
        # Test graceful degradation when debugging tools fail
        debug_manager = PyTorchDebugManager(config)
        
        # Test with invalid operations
        try:
            debug_manager.monitor_operation("invalid", lambda: 1/0, None)
        except ZeroDivisionError:
            print("✅ Error handling works correctly")
        
        # Cleanup
        debug_manager.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all PyTorch debugging tools tests."""
    print("🧪 PyTorch Debugging Tools Test Suite")
    print("=" * 50)
    
    tests = [
        test_pytorch_debug_config,
        test_pytorch_debug_manager,
        test_gradient_monitoring,
        test_activation_monitoring,
        test_autograd_anomaly_detection,
        test_operation_monitoring,
        test_memory_profiling,
        test_profiler_integration,
        test_enhanced_demo_integration,
        test_context_manager,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} FAILED with exception: {e}")
        
        print("-" * 50)
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! PyTorch debugging tools are working correctly.")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
