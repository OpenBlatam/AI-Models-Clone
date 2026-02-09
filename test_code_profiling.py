#!/usr/bin/env python3
"""
🧪 Test Suite for Code Profiling & Bottleneck Detection System

This module provides comprehensive testing for the profiling system components:
- ProfilingConfig
- CodeProfiler
- Specialized monitors
- Integration with EnhancedUIDemosWithValidation
"""

import unittest
import tempfile
import os
import time
import numpy as np
import torch
import torch.nn as nn
from unittest.mock import Mock, patch, MagicMock

# Import the profiling system
from enhanced_ui_demos_with_validation import (
    ProfilingConfig, CodeProfiler, MemoryTracker, TimingProfiler,
    BottleneckDetector, IOMonitor, DataTransferMonitor, CPUMonitor,
    DataAugmentationMonitor, ModelMemoryProfiler, EnhancedUIDemosWithValidation
)

class TestProfilingConfig(unittest.TestCase):
    """Test ProfilingConfig dataclass."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        config = ProfilingConfig()
        
        self.assertTrue(config.enable_profiling)
        self.assertTrue(config.enable_detailed_profiling)
        self.assertEqual(config.profiling_output_dir, "./profiling_results")
        self.assertTrue(config.enable_data_loading_profiling)
        self.assertTrue(config.profile_data_preprocessing)
        self.assertTrue(config.enable_model_profiling)
        self.assertTrue(config.enable_bottleneck_detection)
        self.assertEqual(config.profiling_interval, 0.1)
        self.assertEqual(config.detailed_profiling_threshold, 0.1)
    
    def test_custom_configuration(self):
        """Test custom configuration values."""
        config = ProfilingConfig(
            enable_profiling=False,
            profiling_output_dir="/custom/path",
            profiling_interval=0.5,
            detailed_profiling_threshold=0.2
        )
        
        self.assertFalse(config.enable_profiling)
        self.assertEqual(config.profiling_output_dir, "/custom/path")
        self.assertEqual(config.profiling_interval, 0.5)
        self.assertEqual(config.detailed_profiling_threshold, 0.2)

class TestCodeProfiler(unittest.TestCase):
    """Test CodeProfiler main class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ProfilingConfig(
            profiling_output_dir=self.temp_dir,
            enable_profiling=True,
            enable_detailed_profiling=True
        )
        self.profiler = CodeProfiler(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.profiler.cleanup()
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test profiler initialization."""
        self.assertIsNotNone(self.profiler.profiling_data)
        self.assertIsNotNone(self.profiler.active_profilers)
        self.assertEqual(self.profiler.config, self.config)
    
    def test_start_profiling(self):
        """Test starting profiling for an operation."""
        self.profiler.start_profiling("test_operation", "test_type")
        
        self.assertIn("test_operation", self.profiler.active_profilers)
        operation_id = self.profiler.active_profilers["test_operation"]
        self.assertIn(operation_id, self.profiler.profiling_data)
        
        operation_data = self.profiler.profiling_data[operation_id]
        self.assertEqual(operation_data["operation_name"], "test_operation")
        self.assertEqual(operation_data["operation_type"], "test_type")
        self.assertIn("start_time", operation_data)
        self.assertIn("start_memory", operation_data)
    
    def test_end_profiling(self):
        """Test ending profiling for an operation."""
        self.profiler.start_profiling("test_operation", "test_type")
        self.profiler.end_profiling("test_operation")
        
        # Check that profiling was ended
        self.assertNotIn("test_operation", self.profiler.active_profilers)
        
        # Check that operation data was completed
        operation_id = list(self.profiler.profiling_data.keys())[0]
        operation_data = self.profiler.profiler.profiling_data[operation_id]
        self.assertIn("end_time", operation_data)
        self.assertIn("total_duration", operation_data)
        self.assertIn("memory_delta_mb", operation_data)
    
    def test_profile_sub_operation(self):
        """Test profiling sub-operations."""
        self.profiler.start_profiling("main_operation", "test_type")
        
        def test_function(x):
            time.sleep(0.1)  # Simulate work
            return x * 2
        
        result = self.profiler.profile_sub_operation(
            "main_operation", "sub_operation",
            test_function, 5
        )
        
        self.assertEqual(result, 10)
        
        # Check that sub-operation was recorded
        operation_id = self.profiler.active_profilers["main_operation"]
        operation_data = self.profiler.profiling_data[operation_id]
        self.assertGreater(len(operation_data["sub_operations"]), 0)
        
        self.profiler.end_profiling("main_operation")
    
    def test_get_profiling_report(self):
        """Test getting profiling reports."""
        # No operations profiled yet
        report = self.profiler.get_profiling_report()
        self.assertEqual(report["total_operations"], 0)
        
        # Profile an operation
        self.profiler.start_profiling("test_operation", "test_type")
        time.sleep(0.1)
        self.profiler.end_profiling("test_operation")
        
        # Get report
        report = self.profiler.get_profiling_report()
        self.assertEqual(report["total_operations"], 1)
        self.assertGreater(report["total_duration"], 0)
    
    def test_save_profiling_report(self):
        """Test saving profiling reports."""
        # Profile an operation
        self.profiler.start_profiling("test_operation", "test_type")
        time.sleep(0.1)
        self.profiler.end_profiling("test_operation")
        
        # Save report
        filename = "test_report.json"
        self.profiler.save_profiling_report(filename)
        
        # Check file was created
        filepath = os.path.join(self.temp_dir, filename)
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.assertIn("profiling_data", data)
            self.assertIn("summary", data)
    
    def test_bottleneck_detection(self):
        """Test automatic bottleneck detection."""
        self.profiler.start_profiling("slow_operation", "test_type")
        
        # Simulate slow operation
        time.sleep(1.1)  # Exceeds 1.0s threshold
        
        self.profiler.end_profiling("slow_operation")
        
        # Check for bottlenecks
        operation_id = list(self.profiler.profiling_data.keys())[0]
        operation_data = self.profiler.profiler.profiling_data[operation_id]
        
        self.assertGreater(len(operation_data["bottlenecks"]), 0)
        
        # Check bottleneck details
        bottleneck = operation_data["bottlenecks"][0]
        self.assertEqual(bottleneck["type"], "slow_operation")
        self.assertEqual(bottleneck["severity"], "medium")
    
    def test_optimization_suggestions(self):
        """Test optimization suggestion generation."""
        self.profiler.start_profiling("memory_intensive", "test_type")
        
        # Simulate memory-intensive operation
        large_array = np.random.randn(10000, 1000)
        processed = large_array * 2
        
        self.profiler.end_profiling("memory_intensive")
        
        # Check for optimization suggestions
        operation_id = list(self.profiler.profiling_data.keys())[0]
        operation_data = self.profiler.profiler.profiling_data[operation_id]
        
        self.assertGreater(len(operation_data["optimization_suggestions"]), 0)
        
        # Check suggestion details
        suggestion = operation_data["optimization_suggestions"][0]
        self.assertEqual(suggestion["type"], "memory_optimization")
        self.assertEqual(suggestion["priority"], "high")

class TestSpecializedMonitors(unittest.TestCase):
    """Test specialized monitoring components."""
    
    def test_memory_tracker(self):
        """Test MemoryTracker functionality."""
        tracker = MemoryTracker()
        
        # Start tracking
        tracker.start()
        time.sleep(0.1)
        
        # Stop tracking
        tracker.stop()
        
        # Check that memory history was recorded
        self.assertGreater(len(tracker.memory_history), 0)
        
        # Check memory history structure
        memory_entry = tracker.memory_history[0]
        self.assertIn("timestamp", memory_entry)
        self.assertIn("memory_mb", memory_entry)
    
    def test_timing_profiler(self):
        """Test TimingProfiler functionality."""
        profiler = TimingProfiler()
        
        # Start timer
        profiler.start_timer("test_timer")
        time.sleep(0.1)
        
        # End timer
        duration = profiler.end_timer("test_timer")
        
        # Check duration
        self.assertGreater(duration, 0.09)  # Should be close to 0.1s
        self.assertLess(duration, 0.2)      # Should not be much more than 0.1s
    
    def test_bottleneck_detector(self):
        """Test BottleneckDetector functionality."""
        detector = BottleneckDetector()
        
        # Test slow operation detection
        bottlenecks = detector.detect_bottleneck(
            "slow_op", 2.0, 50.0, 30.0
        )
        
        self.assertGreater(len(bottlenecks), 0)
        
        # Check bottleneck details
        bottleneck = bottlenecks[0]
        self.assertEqual(bottleneck["type"], "slow_operation")
        self.assertEqual(bottleneck["severity"], "medium")
    
    def test_cpu_monitor(self):
        """Test CPUMonitor functionality."""
        monitor = CPUMonitor()
        
        # Start monitoring
        monitor.start()
        time.sleep(0.1)
        
        # Stop monitoring
        monitor.stop()
        
        # Check that CPU history was recorded
        self.assertGreater(len(monitor.cpu_history), 0)
        
        # Check CPU history structure
        cpu_entry = monitor.cpu_history[0]
        self.assertIn("timestamp", cpu_entry)
        self.assertIn("cpu_percent", cpu_entry)

class TestProfilingIntegration(unittest.TestCase):
    """Test integration with EnhancedUIDemosWithValidation."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock configurations
        self.profiling_config = ProfilingConfig(
            profiling_output_dir=self.temp_dir,
            enable_profiling=True
        )
        
        # Mock other configurations
        with patch('enhanced_ui_demos_with_validation.PerformanceConfig'), \
             patch('enhanced_ui_demos_with_validation.MultiGPUConfig'), \
             patch('enhanced_ui_demos_with_validation.PyTorchDebugManager'), \
             patch('enhanced_ui_demos_with_validation.PerformanceOptimizer'), \
             patch('enhanced_ui_demos_with_validation.MultiGPUTrainer'), \
             patch('enhanced_ui_demos_with_validation.InputValidator'), \
             patch('enhanced_ui_demos_with_validation.ErrorHandler'):
            
            self.demos = EnhancedUIDemosWithValidation(
                profiling_config=self.profiling_config
            )
    
    def tearDown(self):
        """Clean up test environment."""
        self.demos.cleanup()
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_profiling_initialization(self):
        """Test that profiling is properly initialized."""
        self.assertIsNotNone(self.demos.code_profiler)
        self.assertEqual(self.demos.profiling_config, self.profiling_config)
    
    def test_profiling_interface_creation(self):
        """Test profiling interface creation."""
        interface = self.demos.create_profiling_interface()
        self.assertIsNotNone(interface)
    
    def test_profiling_cleanup(self):
        """Test that profiling is properly cleaned up."""
        # Start some profiling
        self.demos.code_profiler.start_profiling("test_operation", "test_type")
        
        # Cleanup
        self.demos.cleanup()
        
        # Check that profiling was cleaned up
        self.assertEqual(len(self.demos.code_profiler.active_profilers), 0)
        self.assertEqual(len(self.demos.code_profiler.profiling_data), 0)

class TestProfilingPerformance(unittest.TestCase):
    """Test profiling system performance and overhead."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = ProfilingConfig(
            enable_profiling=True,
            profiling_interval=0.01  # Fast profiling for testing
        )
        self.profiler = CodeProfiler(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.profiler.cleanup()
    
    def test_profiling_overhead(self):
        """Test that profiling adds minimal overhead."""
        # Baseline performance without profiling
        start_time = time.time()
        for _ in range(1000):
            _ = 2 + 2
        baseline_time = time.time() - start_time
        
        # Performance with profiling
        start_time = time.time()
        for i in range(1000):
            self.profiler.start_profiling(f"operation_{i}", "test")
            _ = 2 + 2
            self.profiler.end_profiling(f"operation_{i}")
        profiling_time = time.time() - start_time
        
        # Profiling overhead should be less than 50%
        overhead_ratio = profiling_time / baseline_time
        self.assertLess(overhead_ratio, 1.5)
    
    def test_memory_efficiency(self):
        """Test that profiling doesn't cause memory leaks."""
        initial_memory = self.profiler._get_current_memory_usage()
        
        # Run many profiling operations
        for i in range(100):
            self.profiler.start_profiling(f"operation_{i}", "test")
            time.sleep(0.001)
            self.profiler.end_profiling(f"operation_{i}")
        
        # Cleanup
        self.profiler.cleanup()
        
        # Check memory usage
        final_memory = self.profiler._get_current_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (< 10MB)
        self.assertLess(memory_increase, 10.0)

class TestProfilingEdgeCases(unittest.TestCase):
    """Test profiling system edge cases and error handling."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = ProfilingConfig(enable_profiling=True)
        self.profiler = CodeProfiler(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.profiler.cleanup()
    
    def test_nested_profiling(self):
        """Test nested profiling operations."""
        self.profiler.start_profiling("outer", "test")
        
        self.profiler.start_profiling("inner", "test")
        time.sleep(0.1)
        self.profiler.end_profiling("inner")
        
        self.profiler.end_profiling("outer")
        
        # Check that both operations were profiled
        self.assertEqual(len(self.profiler.profiling_data), 2)
    
    def test_profiling_with_exceptions(self):
        """Test profiling behavior with exceptions."""
        self.profiler.start_profiling("exception_test", "test")
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            pass
        finally:
            self.profiler.end_profiling("exception_test")
        
        # Check that profiling was completed despite exception
        operation_id = list(self.profiler.profiling_data.keys())[0]
        operation_data = self.profiler.profiler.profiling_data[operation_id]
        self.assertIn("total_duration", operation_data)
    
    def test_concurrent_profiling(self):
        """Test concurrent profiling operations."""
        import threading
        
        def profile_operation(name):
            self.profiler.start_profiling(name, "test")
            time.sleep(0.1)
            self.profiler.end_profiling(name)
        
        # Start multiple profiling threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=profile_operation, args=(f"thread_{i}",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all operations were profiled
        self.assertEqual(len(self.profiler.profiling_data), 5)
    
    def test_invalid_operation_names(self):
        """Test profiling with invalid operation names."""
        # Test empty string
        self.profiler.start_profiling("", "test")
        self.profiler.end_profiling("")
        
        # Test None
        with self.assertRaises(TypeError):
            self.profiler.start_profiling(None, "test")
        
        # Test very long names
        long_name = "a" * 1000
        self.profiler.start_profiling(long_name, "test")
        self.profiler.end_profiling(long_name)
        
        # Check that operations were handled
        self.assertGreater(len(self.profiler.profiling_data), 0)

def run_performance_benchmarks():
    """Run performance benchmarks for the profiling system."""
    print("🚀 Running Performance Benchmarks...")
    
    config = ProfilingConfig(enable_profiling=True)
    profiler = CodeProfiler(config)
    
    # Benchmark 1: Operation profiling overhead
    print("\n📊 Benchmark 1: Operation Profiling Overhead")
    
    # Without profiling
    start_time = time.time()
    for i in range(10000):
        _ = i * i
    baseline_time = time.time() - start_time
    
    # With profiling
    start_time = time.time()
    for i in range(10000):
        profiler.start_profiling(f"op_{i}", "test")
        _ = i * i
        profiler.end_profiling(f"op_{i}")
    profiling_time = time.time() - start_time
    
    overhead = (profiling_time - baseline_time) / baseline_time * 100
    print(f"Baseline time: {baseline_time:.4f}s")
    print(f"Profiling time: {profiling_time:.4f}s")
    print(f"Overhead: {overhead:.1f}%")
    
    # Benchmark 2: Memory profiling efficiency
    print("\n📊 Benchmark 2: Memory Profiling Efficiency")
    
    initial_memory = profiler._get_current_memory_usage()
    
    # Profile many operations
    for i in range(1000):
        profiler.start_profiling(f"mem_op_{i}", "test")
        large_array = np.random.randn(100, 100)
        _ = large_array.sum()
        profiler.end_profiling(f"mem_op_{i}")
    
    final_memory = profiler._get_current_memory_usage()
    memory_increase = final_memory - initial_memory
    
    print(f"Initial memory: {initial_memory:.2f}MB")
    print(f"Final memory: {final_memory:.2f}MB")
    print(f"Memory increase: {memory_increase:.2f}MB")
    
    # Cleanup
    profiler.cleanup()
    
    print("\n✅ Performance benchmarks completed!")

if __name__ == "__main__":
    # Run unit tests
    print("🧪 Running Unit Tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance benchmarks
    run_performance_benchmarks()
    
    print("\n🎉 All tests completed successfully!")
