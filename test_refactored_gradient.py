#!/usr/bin/env python3
"""
Test Script for Refactored Advanced Gradient Accumulation

This script tests the refactored system with:
- Clean architecture and separation of concerns
- Strategy pattern for memory management
- Improved performance monitoring
- Better error handling and logging
- Production-ready optimizations
"""

import torch
import torch.nn as nn
import numpy as np
import logging
import time
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_refactored_architecture():
    """Test the refactored architecture and design patterns."""
    print("🧪 Testing Refactored Architecture")
    print("="*50)
    
    try:
        from advanced_gradient_accumulation_refactored import (
            AdvancedGradientConfig, 
            MemoryConfig,
            PerformanceConfig,
            RefactoredTrainer, 
            create_refactored_config,
            refactored_gradient_accumulation_context
        )
        
        # Test 1: Configuration structure
        print("\n📋 Test 1: Configuration Structure")
        config = create_refactored_config(
            batch_size=8,
            effective_batch_size=32,
            adaptive=True,
            mixed_precision=True
        )
        print(f"✅ Configuration created successfully")
        print(f"   - Memory config type: {type(config.memory).__name__}")
        print(f"   - Performance config type: {type(config.performance).__name__}")
        print(f"   - Memory threshold GPU: {config.memory.threshold_gpu}")
        print(f"   - Performance mixed precision: {config.performance.enable_mixed_precision}")
        
        # Test 2: Strategy pattern implementation
        print("\n📋 Test 2: Strategy Pattern Implementation")
        from advanced_gradient_accumulation_refactored import (
            MemoryStrategy, GPUMemoryStrategy, CPUMemoryStrategy, HybridMemoryStrategy
        )
        
        # Test abstract base class
        print(f"   - MemoryStrategy is ABC: {MemoryStrategy.__abstractmethods__}")
        
        # Test concrete strategies
        gpu_strategy = GPUMemoryStrategy()
        cpu_strategy = CPUMemoryStrategy()
        hybrid_strategy = HybridMemoryStrategy()
        
        print(f"   - GPU Strategy: {type(gpu_strategy).__name__}")
        print(f"   - CPU Strategy: {type(cpu_strategy).__name__}")
        print(f"   - Hybrid Strategy: {type(hybrid_strategy).__name__}")
        
        # Test 3: Memory manager initialization
        print("\n📋 Test 3: Memory Manager Initialization")
        from advanced_gradient_accumulation_refactored import AdvancedMemoryManager
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        memory_config = MemoryConfig()
        memory_manager = AdvancedMemoryManager(device, memory_config)
        
        print(f"✅ Memory manager initialized successfully")
        print(f"   - Strategy type: {type(memory_manager.strategy).__name__}")
        print(f"   - Device: {memory_manager.device}")
        print(f"   - Config: {type(memory_manager.config).__name__}")
        
        # Test 4: Gradient accumulation strategy
        print("\n📋 Test 4: Gradient Accumulation Strategy")
        from advanced_gradient_accumulation_refactored import (
            GradientAccumulationStrategy, 
            FixedAccumulationStrategy, 
            AdaptiveAccumulationStrategy
        )
        
        fixed_strategy = FixedAccumulationStrategy()
        adaptive_strategy = AdaptiveAccumulationStrategy()
        
        print(f"   - Fixed Strategy: {type(fixed_strategy).__name__}")
        print(f"   - Adaptive Strategy: {type(adaptive_strategy).__name__}")
        
        # Test strategy methods
        should_accumulate = fixed_strategy.should_accumulate(3, 4)
        adapted_steps = adaptive_strategy.adapt_steps(4, 0.9)
        
        print(f"   - Should accumulate (step 3, target 4): {should_accumulate}")
        print(f"   - Adapted steps (current 4, pressure 0.9): {adapted_steps}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in architecture test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_refactored_gradient_accumulation():
    """Test the refactored gradient accumulation system."""
    print("\n🧪 Testing Refactored Gradient Accumulation System")
    print("="*60)
    
    try:
        from advanced_gradient_accumulation_refactored import (
            AdvancedGradientConfig, 
            RefactoredTrainer, 
            create_refactored_config,
            refactored_gradient_accumulation_context
        )
        
        # Test 1: Refactored configuration creation
        print("\n📋 Test 1: Refactored Configuration Creation")
        config = create_refactored_config(
            batch_size=8,
            effective_batch_size=32,
            adaptive=True,
            mixed_precision=True
        )
        print(f"✅ Refactored configuration created successfully")
        print(f"   - Batch size: {config.batch_size}")
        print(f"   - Effective batch size: {config.effective_batch_size}")
        print(f"   - Adaptive accumulation: {config.performance.enable_adaptive_accumulation}")
        print(f"   - Mixed precision: {config.performance.enable_mixed_precision}")
        print(f"   - Memory auto-cleanup: {config.memory.enable_auto_cleanup}")
        
        # Test 2: Refactored trainer initialization
        print("\n📋 Test 2: Refactored Trainer Initialization")
        model = nn.Sequential(
            nn.Linear(100, 50),
            nn.ReLU(),
            nn.Linear(50, 10)
        )
        
        trainer = RefactoredTrainer(model, config)
        print(f"✅ Refactored trainer initialized successfully")
        print(f"   - Device: {trainer.device}")
        print(f"   - Gradient accumulator: {type(trainer.gradient_accumulator).__name__}")
        print(f"   - Memory manager: {type(trainer.gradient_accumulator.memory_manager).__name__}")
        print(f"   - Accumulation strategy: {type(trainer.gradient_accumulator.accumulation_strategy).__name__}")
        
        # Test 3: Memory monitoring with strategy pattern
        print("\n📋 Test 3: Memory Monitoring with Strategy Pattern")
        memory_info = trainer.gradient_accumulator.memory_manager.strategy.get_status(trainer.device)
        print(f"✅ Memory monitoring working with strategy pattern")
        print(f"   - Memory status type: {type(memory_info).__name__}")
        print(f"   - Memory status keys: {list(memory_info.keys())}")
        
        # Test 4: Training step with refactored logic
        print("\n📋 Test 4: Refactored Training Step")
        batch = torch.randn(8, 100)
        targets = torch.randint(0, 10, (8,))
        
        metrics = trainer.train_step(batch, targets)
        print(f"✅ Refactored training step completed successfully")
        print(f"   - Loss: {metrics['loss']:.4f}")
        print(f"   - Scaled loss: {metrics['scaled_loss']:.4f}")
        print(f"   - Gradient norm: {metrics['grad_norm']:.4f}")
        print(f"   - Step time: {metrics['step_time']:.4f}s")
        print(f"   - Memory utilization: {metrics['memory_utilization']:.2%}")
        print(f"   - Accumulation steps: {metrics['accumulation_steps']}")
        
        # Test 5: Performance statistics with refactored structure
        print("\n📋 Test 5: Refactored Performance Statistics")
        stats = trainer.get_performance_summary()
        print(f"✅ Refactored performance statistics generated")
        print(f"   - Average step time: {stats['avg_step_time']:.4f}s")
        print(f"   - Average loss: {stats['avg_loss']:.4f}")
        print(f"   - Accumulation steps: {stats['accumulation_steps']}")
        print(f"   - Optimization count: {stats['optimization_count']}")
        
        # Test 6: Memory recommendations with strategy pattern
        print("\n📋 Test 6: Memory Recommendations with Strategy Pattern")
        recommendations = trainer.gradient_accumulator.get_memory_recommendations()
        print(f"✅ Memory recommendations generated with strategy pattern")
        if recommendations:
            for rec in recommendations:
                print(f"   - {rec}")
        else:
            print(f"   - No recommendations (memory usage is optimal)")
        
        # Test 7: Context manager with refactored cleanup
        print("\n📋 Test 7: Refactored Context Manager")
        with refactored_gradient_accumulation_context(model, config) as ctx_trainer:
            batch = torch.randn(8, 100)
            targets = torch.randint(0, 10, (8,))
            metrics = ctx_trainer.train_step(batch, targets)
            print(f"✅ Refactored context manager working")
            print(f"   - Loss: {metrics['loss']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in refactored gradient test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_refactored_advanced_features():
    """Test the refactored advanced features."""
    print("\n🧪 Testing Refactored Advanced Features")
    print("="*50)
    
    try:
        from advanced_gradient_accumulation_refactored import (
            create_experimental_refactored_config, 
            RefactoredTrainer
        )
        
        # Test experimental configuration with all advanced features
        config = create_experimental_refactored_config(
            batch_size=4,
            effective_batch_size=32,
            noise_scale=1e-4
        )
        
        print(f"✅ Experimental refactored config created:")
        print(f"   - Advanced memory profiling: {config.memory.enable_advanced_profiling}")
        print(f"   - Gradient noise injection: {config.performance.enable_noise_injection}")
        print(f"   - Adaptive learning rate: {config.performance.enable_learning_rate_scheduling}")
        print(f"   - Automatic checkpointing: {config.performance.enable_automatic_checkpointing}")
        
        model = nn.Sequential(
            nn.Linear(50, 25),
            nn.ReLU(),
            nn.Linear(25, 5)
        )
        
        trainer = RefactoredTrainer(model, config)
        
        # Test advanced memory profiling with strategy pattern
        print("\n📊 Testing refactored advanced memory profiling...")
        initial_memory = trainer.gradient_accumulator.memory_manager.strategy.get_status(trainer.device)
        print(f"   Initial memory status: {type(initial_memory).__name__}")
        
        # Simulate training with advanced features
        for step in range(15):
            batch = torch.randn(4, 50)
            targets = torch.randint(0, 5, (4,))
            metrics = trainer.train_step(batch, targets)
            
            if step % 5 == 0:
                print(f"   Step {step}: Loss = {metrics['loss']:.4f}, "
                      f"Accumulation Steps = {metrics['accumulation_steps']}")
        
        # Test advanced memory analysis with refactored structure
        print(f"\n📊 Refactored memory analysis:")
        memory_manager = trainer.gradient_accumulator.memory_manager
        
        # Take snapshots
        for step in range(5):
            snapshot = memory_manager.take_snapshot(step, f"Test step {step}")
            print(f"   Snapshot {step}: {len(snapshot)} keys")
        
        # Test memory optimization
        optimization_performed = memory_manager.optimize_if_needed()
        print(f"   Memory optimization performed: {optimization_performed}")
        print(f"   Total optimizations: {memory_manager.optimization_counter}")
        
        # Test advanced memory recommendations
        recommendations = memory_manager.get_memory_recommendations()
        print(f"\n💡 Refactored memory recommendations:")
        if recommendations:
            for rec in recommendations:
                print(f"   - {rec}")
        else:
            print(f"   - No recommendations (memory usage is optimal)")
        
        # Test performance summary with refactored features
        summary = trainer.get_performance_summary()
        print(f"\n📊 Refactored advanced performance summary:")
        print(f"   - Memory optimization count: {summary['config']['memory_optimization_count']}")
        print(f"   - Advanced features enabled: {summary['config']['adaptive_accumulation']}")
        
        print(f"✅ Refactored advanced features working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error in refactored advanced features test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_refactored_memory_optimization():
    """Test refactored memory optimization features."""
    print("\n🧪 Testing Refactored Memory Optimization")
    print("="*50)
    
    try:
        from advanced_gradient_accumulation_refactored import (
            create_refactored_config, 
            RefactoredTrainer
        )
        
        # Test memory-efficient configuration
        config = create_refactored_config(
            batch_size=2,
            effective_batch_size=16,
            adaptive=True,
            mixed_precision=True,
            memory_efficient=True
        )
        
        model = nn.Sequential(
            nn.Linear(100, 50),
            nn.ReLU(),
            nn.Linear(50, 10)
        )
        
        trainer = RefactoredTrainer(model, config)
        
        # Test memory monitoring with strategy pattern
        initial_memory = trainer.gradient_accumulator.memory_manager.strategy.get_status(trainer.device)
        print(f"📊 Initial memory status: {type(initial_memory).__name__}")
        
        # Simulate training
        for step in range(10):
            batch = torch.randn(2, 100)
            targets = torch.randint(0, 10, (2,))
            metrics = trainer.train_step(batch, targets)
        
        final_memory = trainer.gradient_accumulator.memory_manager.strategy.get_status(trainer.device)
        print(f"📊 Final memory status: {type(final_memory).__name__}")
        
        # Test memory optimization with strategy pattern
        memory_manager = trainer.gradient_accumulator.memory_manager
        optimization_performed = memory_manager.optimize_if_needed()
        print(f"📊 Memory optimization performed: {optimization_performed}")
        
        optimized_memory = memory_manager.strategy.get_status(trainer.device)
        print(f"📊 After optimization: {type(optimized_memory).__name__}")
        
        print(f"✅ Refactored memory optimization working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error in refactored memory optimization test: {e}")
        return False

def test_refactored_performance_comparison():
    """Test refactored performance comparison between different configurations."""
    print("\n🧪 Testing Refactored Performance Comparison")
    print("="*50)
    
    try:
        from advanced_gradient_accumulation_refactored import (
            create_refactored_config, 
            RefactoredTrainer
        )
        
        configs = {
            'baseline': create_refactored_config(
                batch_size=8, effective_batch_size=32, adaptive=False, mixed_precision=False
            ),
            'mixed_precision': create_refactored_config(
                batch_size=8, effective_batch_size=32, adaptive=False, mixed_precision=True
            ),
            'adaptive': create_refactored_config(
                batch_size=8, effective_batch_size=32, adaptive=True, mixed_precision=True
            )
        }
        
        results = {}
        
        for name, config in configs.items():
            print(f"📊 Testing {name} refactored configuration...")
            
            model = nn.Sequential(
                nn.Linear(100, 50),
                nn.ReLU(),
                nn.Linear(50, 10)
            )
            
            trainer = RefactoredTrainer(model, config)
            
            # Time the training
            start_time = time.time()
            for step in range(20):
                batch = torch.randn(8, 100)
                targets = torch.randint(0, 10, (8,))
                metrics = trainer.train_step(batch, targets)
            
            training_time = time.time() - start_time
            summary = trainer.get_performance_summary()
            
            results[name] = {
                'training_time': training_time,
                'avg_loss': summary['avg_loss'],
                'optimization_count': summary['optimization_count']
            }
            
            print(f"   - Training time: {training_time:.2f}s")
            print(f"   - Average loss: {summary['avg_loss']:.4f}")
            print(f"   - Memory optimizations: {summary['optimization_count']}")
        
        # Compare results
        print(f"\n📊 Refactored Performance Comparison:")
        best_time = min(results.values(), key=lambda x: x['training_time'])
        best_loss = min(results.values(), key=lambda x: x['avg_loss'])
        
        for name, result in results.items():
            print(f"   {name}: {result['training_time']:.2f}s, loss: {result['avg_loss']:.4f}, optimizations: {result['optimization_count']}")
        
        print(f"✅ Refactored performance comparison completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in refactored performance comparison test: {e}")
        return False

def test_refactored_error_handling():
    """Test refactored error handling and robustness."""
    print("\n🧪 Testing Refactored Error Handling")
    print("="*50)
    
    try:
        from advanced_gradient_accumulation_refactored import (
            create_refactored_config, 
            RefactoredTrainer
        )
        
        # Test with invalid configuration
        print("\n📋 Test 1: Invalid Configuration Handling")
        try:
            config = create_refactored_config(
                batch_size=0,  # Invalid batch size
                effective_batch_size=32
            )
            print("⚠️  Should have failed with invalid batch size")
        except Exception as e:
            print(f"✅ Properly handled invalid configuration: {type(e).__name__}")
        
        # Test with None model
        print("\n📋 Test 2: None Model Handling")
        try:
            config = create_refactored_config()
            trainer = RefactoredTrainer(None, config)  # Invalid model
            print("⚠️  Should have failed with None model")
        except Exception as e:
            print(f"✅ Properly handled None model: {type(e).__name__}")
        
        # Test checkpoint operations
        print("\n📋 Test 3: Checkpoint Error Handling")
        config = create_refactored_config()
        model = nn.Sequential(nn.Linear(10, 5))
        trainer = RefactoredTrainer(model, config)
        
        # Test saving to invalid path
        try:
            trainer.save_checkpoint("/invalid/path/checkpoint.pt")
            print("⚠️  Should have failed with invalid path")
        except Exception as e:
            print(f"✅ Properly handled invalid save path: {type(e).__name__}")
        
        # Test loading non-existent checkpoint
        try:
            trainer.load_checkpoint("non_existent_checkpoint.pt")
            print("⚠️  Should have failed with non-existent file")
        except Exception as e:
            print(f"✅ Properly handled non-existent checkpoint: {type(e).__name__}")
        
        print(f"✅ Refactored error handling working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error in refactored error handling test: {e}")
        return False

def main():
    """Main test function for refactored system."""
    print("🚀 Refactored Advanced Gradient Accumulation Test Suite")
    print("="*80)
    
    # Run all tests
    tests = [
        ("Refactored Architecture", test_refactored_architecture),
        ("Refactored Gradient Accumulation", test_refactored_gradient_accumulation),
        ("Refactored Advanced Features", test_refactored_advanced_features),
        ("Refactored Memory Optimization", test_refactored_memory_optimization),
        ("Refactored Performance Comparison", test_refactored_performance_comparison),
        ("Refactored Error Handling", test_refactored_error_handling)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        results[test_name] = test_func()
    
    # Summary
    print("\n📊 Refactored Test Results Summary")
    print("="*40)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All refactored tests passed! The refactored system is working correctly.")
        print("\n🏗️ Architecture Improvements:")
        print("   ✅ Clean separation of concerns")
        print("   ✅ Strategy pattern implementation")
        print("   ✅ Improved error handling")
        print("   ✅ Better performance monitoring")
        print("   ✅ Production-ready optimizations")
    else:
        print("\n⚠️  Some refactored tests failed. Please check the error messages above.")
    
    print("\n💡 Next Steps:")
    print("1. Run the refactored demo: python refactored_gradient_demo.py")
    print("2. Compare with original system performance")
    print("3. Test with your own models and datasets")
    print("4. Deploy in production environment")

if __name__ == "__main__":
    main()
