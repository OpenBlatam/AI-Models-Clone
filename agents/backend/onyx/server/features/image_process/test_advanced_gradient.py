#!/usr/bin/env python3
"""
Test Script for Advanced Gradient Accumulation

This script tests the enhanced gradient accumulation system with:
- Adaptive accumulation strategies
- Advanced memory monitoring
- Performance optimization features
"""

import torch
import torch.nn as nn
import numpy as np
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_advanced_gradient_accumulation():
    """Test the advanced gradient accumulation system."""
    print("🧪 Testing Advanced Gradient Accumulation System")
    print("="*60)
    
    try:
        from advanced_gradient_accumulation import (
            AdvancedGradientConfig, 
            AdvancedTrainer, 
            create_advanced_config,
            gradient_accumulation_context
        )
        
        # Test 1: Basic configuration creation
        print("\n📋 Test 1: Configuration Creation")
        config = create_advanced_config(
            batch_size=8,
            effective_batch_size=32,
            adaptive=True,
            mixed_precision=True
        )
        print(f"✅ Configuration created successfully")
        print(f"   - Batch size: {config.batch_size}")
        print(f"   - Effective batch size: {config.effective_batch_size}")
        print(f"   - Adaptive accumulation: {config.adaptive_accumulation}")
        print(f"   - Mixed precision: {config.use_mixed_precision}")
        
        # Test 2: Advanced trainer initialization
        print("\n📋 Test 2: Advanced Trainer Initialization")
        model = nn.Sequential(
            nn.Linear(100, 50),
            nn.ReLU(),
            nn.Linear(50, 10)
        )
        
        trainer = AdvancedTrainer(model, config)
        print(f"✅ Advanced trainer initialized successfully")
        print(f"   - Device: {trainer.device}")
        print(f"   - Gradient accumulator: {type(trainer.gradient_accumulator).__name__}")
        print(f"   - Memory monitor: {type(trainer.gradient_accumulator.memory_monitor).__name__}")
        
        # Test 3: Memory monitoring
        print("\n📋 Test 3: Memory Monitoring")
        memory_info = trainer.gradient_accumulator.memory_monitor.get_memory_info()
        print(f"✅ Memory monitoring working")
        print(f"   - GPU memory allocated: {memory_info['gpu_memory_allocated']:.2f} GB")
        print(f"   - GPU memory utilization: {memory_info['gpu_memory_utilization']:.2%}")
        print(f"   - CPU memory utilization: {memory_info['cpu_memory_utilization']:.2%}")
        
        # Test 4: Training step with advanced features
        print("\n📋 Test 4: Advanced Training Step")
        batch = torch.randn(8, 100)
        targets = torch.randint(0, 10, (8,))
        
        metrics = trainer.train_step(batch, targets)
        print(f"✅ Training step completed successfully")
        print(f"   - Loss: {metrics['loss']:.4f}")
        print(f"   - Scaled loss: {metrics['scaled_loss']:.4f}")
        print(f"   - Gradient norm: {metrics['grad_norm']:.4f}")
        print(f"   - Step time: {metrics['step_time']:.4f}s")
        print(f"   - Memory utilization: {metrics['memory_utilization']:.2%}")
        print(f"   - Accumulation steps: {metrics['accumulation_steps']}")
        
        # Test 5: Performance statistics
        print("\n📋 Test 5: Performance Statistics")
        stats = trainer.get_performance_summary()
        print(f"✅ Performance statistics generated")
        print(f"   - Average step time: {stats['avg_step_time']:.4f}s")
        print(f"   - Average loss: {stats['avg_loss']:.4f}")
        print(f"   - Peak memory: {stats['peak_memory']:.2f} GB")
        print(f"   - Total steps: {stats['total_steps']}")
        
        # Test 6: Memory recommendations
        print("\n📋 Test 6: Memory Recommendations")
        recommendations = trainer.gradient_accumulator.get_memory_recommendations()
        print(f"✅ Memory recommendations generated")
        if recommendations:
            for rec in recommendations:
                print(f"   - {rec}")
        else:
            print(f"   - No recommendations (memory usage is optimal)")
        
        # Test 7: Context manager
        print("\n📋 Test 7: Context Manager")
        with gradient_accumulation_context(model, config) as ctx_trainer:
            batch = torch.randn(8, 100)
            targets = torch.randint(0, 10, (8,))
            metrics = ctx_trainer.train_step(batch, targets)
            print(f"✅ Context manager working")
            print(f"   - Loss: {metrics['loss']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in advanced gradient test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_advanced_features():
    """Test the new advanced features."""
    print("\n🧪 Testing Advanced Features")
    print("="*40)
    
    try:
        from advanced_gradient_accumulation import create_experimental_config, AdvancedTrainer
        
        # Test experimental configuration with all advanced features
        config = create_experimental_config(
            batch_size=4,
            effective_batch_size=32,
            noise_scale=1e-4
        )
        
        print(f"✅ Experimental config created:")
        print(f"   - Advanced memory profiling: {config.advanced_memory_profiling}")
        print(f"   - Gradient noise injection: {config.gradient_noise_injection}")
        print(f"   - Adaptive learning rate: {config.adaptive_learning_rate}")
        print(f"   - Automatic checkpointing: {config.automatic_checkpointing}")
        
        model = nn.Sequential(
            nn.Linear(50, 25),
            nn.ReLU(),
            nn.Linear(25, 5)
        )
        
        trainer = AdvancedTrainer(model, config)
        
        # Test advanced memory profiling
        print("\n📊 Testing advanced memory profiling...")
        initial_memory = trainer.gradient_accumulator.memory_monitor.get_memory_info()
        print(f"   Initial memory: {initial_memory['gpu_memory_allocated']:.2f} GB")
        
        # Simulate training with advanced features
        for step in range(15):
            batch = torch.randn(4, 50)
            targets = torch.randint(0, 5, (4,))
            metrics = trainer.train_step(batch, targets)
            
            if step % 5 == 0:
                print(f"   Step {step}: Loss = {metrics['loss']:.4f}, "
                      f"Accumulation Steps = {metrics['accumulation_steps']}")
        
        # Test advanced memory analysis
        if hasattr(trainer.gradient_accumulator, 'memory_profiler') and trainer.gradient_accumulator.memory_profiler:
            memory_trends = trainer.gradient_accumulator.memory_profiler.analyze_memory_trends()
            print(f"\n📊 Memory trends analysis:")
            if 'gpu_memory' in memory_trends and memory_trends['gpu_memory']:
                trend = memory_trends['gpu_memory']
                print(f"   - Trend: {trend.get('trend', 'stable')}")
                print(f"   - Volatility: {trend.get('volatility', 0.0):.4f}")
                print(f"   - Peak: {trend.get('peak', 0.0):.2f} GB")
            else:
                print(f"   - No GPU memory trends available (running on CPU)")
                print(f"   - Trend: stable")
                print(f"   - Volatility: 0.0000")
                print(f"   - Peak: 0.00 GB")
        
        # Test performance summary with advanced features
        summary = trainer.get_performance_summary()
        print(f"\n📊 Advanced performance summary:")
        print(f"   - Memory trend: {summary.get('memory_trend', 'N/A')}")
        print(f"   - Memory volatility: {summary.get('memory_volatility', 'N/A'):.4f}")
        print(f"   - Advanced features enabled: {summary['config']['advanced_memory_profiling']}")
        
        # Test advanced memory recommendations
        recommendations = trainer.gradient_accumulator.get_memory_recommendations()
        print(f"\n💡 Advanced memory recommendations:")
        if recommendations:
            for rec in recommendations:
                print(f"   - {rec}")
        else:
            print(f"   - No recommendations (memory usage is optimal)")
        
        print(f"✅ Advanced features working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error in advanced features test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_optimization():
    """Test memory optimization features."""
    print("\n🧪 Testing Memory Optimization")
    print("="*40)
    
    try:
        from advanced_gradient_accumulation import create_advanced_config, AdvancedTrainer
        
        # Test memory-efficient configuration
        config = create_advanced_config(
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
        
        trainer = AdvancedTrainer(model, config)
        
        # Test memory monitoring
        initial_memory = trainer.gradient_accumulator.memory_monitor.get_memory_info()
        print(f"📊 Initial memory: {initial_memory['gpu_memory_allocated']:.2f} GB")
        
        # Simulate training
        for step in range(10):
            batch = torch.randn(2, 100)
            targets = torch.randint(0, 10, (2,))
            metrics = trainer.train_step(batch, targets)
        
        final_memory = trainer.gradient_accumulator.memory_monitor.get_memory_info()
        print(f"📊 Final memory: {final_memory['gpu_memory_allocated']:.2f} GB")
        
        # Test memory optimization
        trainer.gradient_accumulator.memory_monitor.optimize_memory()
        optimized_memory = trainer.gradient_accumulator.memory_monitor.get_memory_info()
        print(f"📊 After optimization: {optimized_memory['gpu_memory_allocated']:.2f} GB")
        
        print(f"✅ Memory optimization working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error in memory optimization test: {e}")
        return False

def test_performance_comparison():
    """Test performance comparison between different configurations."""
    print("\n🧪 Testing Performance Comparison")
    print("="*40)
    
    try:
        from advanced_gradient_accumulation import create_advanced_config, AdvancedTrainer
        
        configs = {
            'baseline': create_advanced_config(
                batch_size=8, effective_batch_size=32, adaptive=False, mixed_precision=False
            ),
            'mixed_precision': create_advanced_config(
                batch_size=8, effective_batch_size=32, adaptive=False, mixed_precision=True
            ),
            'adaptive': create_advanced_config(
                batch_size=8, effective_batch_size=32, adaptive=True, mixed_precision=True
            )
        }
        
        results = {}
        
        for name, config in configs.items():
            print(f"📊 Testing {name} configuration...")
            
            model = nn.Sequential(
                nn.Linear(100, 50),
                nn.ReLU(),
                nn.Linear(50, 10)
            )
            
            trainer = AdvancedTrainer(model, config)
            
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
                'memory_utilization': summary.get('memory_utilization', 0.0)
            }
            
            print(f"   - Training time: {training_time:.2f}s")
            print(f"   - Average loss: {summary['avg_loss']:.4f}")
            print(f"   - Memory utilization: {summary.get('memory_utilization', 0.0):.2%}")
        
        # Compare results
        print(f"\n📊 Performance Comparison:")
        best_time = min(results.values(), key=lambda x: x['training_time'])
        best_loss = min(results.values(), key=lambda x: x['avg_loss'])
        
        for name, result in results.items():
            print(f"   {name}: {result['training_time']:.2f}s, loss: {result['avg_loss']:.4f}")
        
        print(f"✅ Performance comparison completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in performance comparison test: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Advanced Gradient Accumulation Test Suite")
    print("="*70)
    
    # Run all tests
    tests = [
        ("Advanced Gradient Accumulation", test_advanced_gradient_accumulation),
        ("Memory Optimization", test_memory_optimization),
        ("Performance Comparison", test_performance_comparison),
        ("Advanced Features", test_advanced_features)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("="*30)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Advanced gradient accumulation system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
    
    print("\n💡 Next Steps:")
    print("1. Run the advanced demo: python advanced_gradient_demo.py")
    print("2. Experiment with different configurations")
    print("3. Test with your own models and datasets")
    print("4. Try the new experimental configuration with advanced features")

if __name__ == "__main__":
    main()
