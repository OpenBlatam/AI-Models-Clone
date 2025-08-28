#!/usr/bin/env python3
"""
🚀 OPTIMIZED IMAGE PROCESSING DEMO
==================================

Demonstration of the optimized image processing system.
"""

import time
from PIL import Image, ImageDraw
from optimized_image_process import (
    OptimizedImageProcessor, ProcessingConfig, ProcessingMode, TaskType
)

def demo_basic_usage():
    """Basic usage demonstration."""
    print("🚀 Basic Usage Demo")
    print("=" * 50)
    
    # Create processor
    config = ProcessingConfig(
        mode=ProcessingMode.BALANCED,
        enable_ai=True,
        enable_caching=True
    )
    processor = OptimizedImageProcessor(config)
    
    # Create test image
    test_image = Image.new('RGB', (200, 200), color='red')
    
    # Process image
    result = processor.process_image(test_image, TaskType.ANALYSIS)
    
    print(f"✅ Success: {result.success}")
    print(f"⏱️ Time: {result.processing_time:.2f}s")
    print(f"📊 Confidence: {result.confidence:.2f}")
    
    if result.success:
        print(f"📋 Results: {result.data}")
    
    # Show metrics
    metrics = processor.get_metrics()
    print(f"📊 Metrics: {metrics}")

def demo_performance_comparison():
    """Compare different processing modes."""
    print("\n⚡ Performance Comparison")
    print("=" * 50)
    
    modes = [ProcessingMode.FAST, ProcessingMode.BALANCED, ProcessingMode.QUALITY]
    test_image = Image.new('RGB', (400, 300), color='blue')
    
    for mode in modes:
        config = ProcessingConfig(mode=mode, enable_ai=True, enable_caching=True)
        processor = OptimizedImageProcessor(config)
        
        start_time = time.time()
        result = processor.process_image(test_image, TaskType.ANALYSIS)
        total_time = time.time() - start_time
        
        print(f"\n🔧 {mode.value.upper()}:")
        print(f"   ⏱️ Time: {result.processing_time:.3f}s")
        print(f"   ✅ Success: {result.success}")
        print(f"   📊 Confidence: {result.confidence:.2f}")

def demo_caching():
    """Demonstrate caching effectiveness."""
    print("\n💾 Caching Demo")
    print("=" * 50)
    
    config = ProcessingConfig(enable_caching=True, cache_size=100)
    processor = OptimizedImageProcessor(config)
    test_image = Image.new('RGB', (100, 100), color='green')
    
    # First run
    result1 = processor.process_image(test_image, TaskType.VALIDATION)
    print(f"📸 First run: {result1.processing_time:.3f}s")
    
    # Second run (cached)
    result2 = processor.process_image(test_image, TaskType.VALIDATION)
    print(f"📸 Second run: {result2.processing_time:.3f}s")
    
    # Show cache metrics
    metrics = processor.get_metrics()
    print(f"📊 Cache hit rate: {metrics['cache_hit_rate']:.2%}")

if __name__ == "__main__":
    demo_basic_usage()
    demo_performance_comparison()
    demo_caching()
    print("\n�� Demo completed!")
