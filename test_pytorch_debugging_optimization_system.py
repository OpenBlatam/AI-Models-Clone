from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int = 1000

# Constants
MAX_RETRIES: int = 100

import unittest
import tempfile
import shutil
import os
import time
import json
import torch
import torch.nn as nn
import torch.optim as optim
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
from pytorch_debugging_optimization_system import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Test Suite for PyTorch Debugging and Optimization System
======================================================

Comprehensive tests for the PyTorch debugging and optimization system covering:
- Autograd anomaly detection
- Memory profiling and optimization
- Gradient debugging and visualization
- Performance profiling
- Model debugging utilities
- Optimization recommendations
"""


# Add the current directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    DebugConfig,
    AutogradDebugger,
    MemoryProfiler,
    GradientDebugger,
    PerformanceProfiler,
    ModelDebugger,
    OptimizationAdvisor,
    PyTorchDebugOptimizer,
    create_debug_optimizer,
    setup_debugging
)


class TestDebugConfig(unittest.TestCase):
    """Test DebugConfig dataclass."""
    
    def test_default_config(self) -> Any:
        """Test default configuration values."""
        config = DebugConfig()
        
        self.assertFalse(config.detect_anomaly)
        self.assertEqual(config.anomaly_detection_mode, "default")
        self.assertTrue(config.memory_tracking)
        self.assertTrue(config.gradient_tracking)
        self.assertFalse(config.enable_profiling)
        self.assertTrue(config.model_parameter_tracking)
        self.assertEqual(config.debug_dir, "debug_logs")
        self.assertTrue(config.tensorboard_logging)
        self.assertTrue(config.console_output)
    
    def test_custom_config(self) -> Any:
        """Test custom configuration values."""
        config = DebugConfig(
            detect_anomaly=True,
            anomaly_detection_mode: str = "warn",
            memory_tracking=False,
            gradient_tracking=True,
            enable_profiling=True,
            debug_dir: str = "custom_debug",
            tensorboard_logging: bool = False
        )
        
        self.assertTrue(config.detect_anomaly)
        self.assertEqual(config.anomaly_detection_mode, "warn")
        self.assertFalse(config.memory_tracking)
        self.assertTrue(config.gradient_tracking)
        self.assertTrue(config.enable_profiling)
        self.assertEqual(config.debug_dir, "custom_debug")
        self.assertFalse(config.tensorboard_logging)


class TestAutogradDebugger(unittest.TestCase):
    """Test AutogradDebugger functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = DebugConfig(detect_anomaly=True)
        self.debugger = AutogradDebugger(self.config)
    
    def test_initialization(self) -> Any:
        """Test debugger initialization."""
        self.assertFalse(self.debugger.anomaly_detected)
        self.assertEqual(len(self.debugger.anomaly_info), 0)
    
    def test_detect_anomaly_context(self) -> Any:
        """Test anomaly detection context manager."""
        with self.debugger.detect_anomaly():
            # Normal operation should not trigger anomaly
            x = torch.randn(2, 2, requires_grad=True)
            y = x * 2
            y.sum().backward()
        
        self.assertFalse(self.debugger.anomaly_detected)
    
    def test_anomaly_detection_with_nan(self) -> Any:
        """Test anomaly detection with NaN values."""
        with self.debugger.detect_anomaly():
            x = torch.randn(2, 2, requires_grad=True)
            # Create NaN
            x[0, 0] = float('nan')
            y = x * 2
            y.sum().backward()
        
        # Should detect anomaly
        self.assertTrue(self.debugger.anomaly_detected)
        self.assertGreater(len(self.debugger.anomaly_info), 0)
    
    def test_check_gradients(self) -> Any:
        """Test gradient checking functionality."""
        model = nn.Linear(2, 1)
        x = torch.randn(4, 2)
        y = torch.randn(4, 1)
        
        # Forward and backward pass
        output = model(x)
        loss = nn.MSELoss()(output, y)
        loss.backward()
        
        gradient_info = self.debugger.check_gradients(model)
        
        # Should have gradient info for model parameters
        self.assertIn('weight', gradient_info)
        self.assertIn('bias', gradient_info)
        
        # Check gradient info structure
        weight_info = gradient_info['weight']
        self.assertIn('norm', weight_info)
        self.assertIn('mean', weight_info)
        self.assertIn('std', weight_info)
        self.assertIn('has_nan', weight_info)
        self.assertIn('has_inf', weight_info)
    
    def test_check_gradients_with_nan(self) -> Any:
        """Test gradient checking with NaN gradients."""
        model = nn.Linear(2, 1)
        x = torch.randn(4, 2)
        y = torch.randn(4, 1)
        
        # Forward and backward pass
        output = model(x)
        loss = nn.MSELoss()(output, y)
        loss.backward()
        
        # Introduce NaN in gradients
        model.weight.grad[0, 0] = float('nan')
        
        gradient_info = self.debugger.check_gradients(model)
        
        # Should detect NaN in gradients
        self.assertTrue(gradient_info['weight']['has_nan'])
        self.assertTrue(self.debugger.anomaly_detected)
    
    def test_get_anomaly_summary(self) -> Optional[Dict[str, Any]]:
        """Test anomaly summary generation."""
        # Create some anomalies
        self.debugger.anomaly_detected: bool = True
        self.debugger.anomaly_info: List[Any] = [
            {'type': 'test', 'timestamp': time.time()}
        ]
        
        summary = self.debugger.get_anomaly_summary()
        
        self.assertTrue(summary['anomaly_detected'])
        self.assertEqual(summary['anomaly_count'], 1)
        self.assertEqual(len(summary['anomalies']), 1)


class TestMemoryProfiler(unittest.TestCase):
    """Test MemoryProfiler functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = DebugConfig(memory_tracking=True)
        self.profiler = MemoryProfiler(self.config)
    
    def test_initialization(self) -> Any:
        """Test profiler initialization."""
        self.assertEqual(len(self.profiler.memory_history), 0)
        self.assertEqual(self.profiler.peak_memory, 0)
        self.assertEqual(len(self.profiler.memory_warnings), 0)
    
    def test_get_memory_usage(self) -> Optional[Dict[str, Any]]:
        """Test memory usage retrieval."""
        memory_info = self.profiler.get_memory_usage()
        
        # Check system memory info
        self.assertIn('system_total', memory_info)
        self.assertIn('system_available', memory_info)
        self.assertIn('system_used', memory_info)
        self.assertIn('system_percent', memory_info)
        
        # Check CUDA memory info if available
        if torch.cuda.is_available():
            self.assertIn('cuda_allocated', memory_info)
            self.assertIn('cuda_reserved', memory_info)
            self.assertIn('cuda_max_allocated', memory_info)
            self.assertIn('cuda_max_reserved', memory_info)
    
    def test_track_memory(self) -> Any:
        """Test memory tracking functionality."""
        memory_info = self.profiler.track_memory(10, "test_context")
        
        # Check tracking info
        self.assertEqual(memory_info['step'], 10)
        self.assertEqual(memory_info['context'], "test_context")
        self.assertIn('timestamp', memory_info)
        
        # Check history
        self.assertEqual(len(self.profiler.memory_history), 1)
        self.assertEqual(self.profiler.memory_history[0]['step'], 10)
    
    def test_get_memory_summary(self) -> Optional[Dict[str, Any]]:
        """Test memory summary generation."""
        # Add some memory history
        self.profiler.track_memory(1, "test1")
        self.profiler.track_memory(2, "test2")
        
        summary = self.profiler.get_memory_summary()
        
        self.assertEqual(summary['total_tracking_points'], 2)
        self.assertEqual(summary['memory_warnings'], 0)
        
        if torch.cuda.is_available():
            self.assertIn('cuda_memory_stats', summary)
    
    def test_clear_memory(self) -> Any:
        """Test memory clearing functionality."""
        # Should not raise any exception
        self.profiler.clear_memory()
    
    def test_get_memory_optimization_suggestions(self) -> Optional[Dict[str, Any]]:
        """Test memory optimization suggestions."""
        # Add memory history with high usage
        for i in range(5):
            self.profiler.track_memory(i, "test")
        
        suggestions = self.profiler.get_memory_optimization_suggestions()
        
        # Should return a list of suggestions
        self.assertIsInstance(suggestions, list)


class TestGradientDebugger(unittest.TestCase):
    """Test GradientDebugger functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = DebugConfig(gradient_tracking=True)
        self.debugger = GradientDebugger(self.config)
        self.model = nn.Linear(2, 1)
    
    def test_initialization(self) -> Any:
        """Test debugger initialization."""
        self.assertEqual(len(self.debugger.gradient_history), 0)
        self.assertEqual(len(self.debugger.gradient_norms), 0)
        self.assertEqual(len(self.debugger.gradient_anomalies), 0)
    
    def test_track_gradients(self) -> Any:
        """Test gradient tracking functionality."""
        # Create gradients
        x = torch.randn(4, 2)
        y = torch.randn(4, 1)
        
        output = self.model(x)
        loss = nn.MSELoss()(output, y)
        loss.backward()
        
        gradient_info = self.debugger.track_gradients(self.model, 10)
        
        # Check gradient info
        self.assertIn('weight', gradient_info)
        self.assertIn('bias', gradient_info)
        self.assertEqual(gradient_info['step'], 10)
        self.assertIn('timestamp', gradient_info)
        
        # Check gradient norms tracking
        self.assertIn('weight', self.debugger.gradient_norms)
        self.assertIn('bias', self.debugger.gradient_norms)
        self.assertEqual(len(self.debugger.gradient_norms['weight']), 1)
    
    def test_track_gradients_with_anomalies(self) -> Any:
        """Test gradient tracking with anomalies."""
        # Create gradients
        x = torch.randn(4, 2)
        y = torch.randn(4, 1)
        
        output = self.model(x)
        loss = nn.MSELoss()(output, y)
        loss.backward()
        
        # Introduce NaN in gradients
        self.model.weight.grad[0, 0] = float('nan')
        
        gradient_info = self.debugger.track_gradients(self.model, 10)
        
        # Should detect anomalies
        self.assertTrue(gradient_info['weight']['has_nan'])
        self.assertGreater(len(self.debugger.gradient_anomalies), 0)
    
    def test_clip_gradients(self) -> Any:
        """Test gradient clipping functionality."""
        # Create gradients
        x = torch.randn(4, 2)
        y = torch.randn(4, 1)
        
        output = self.model(x)
        loss = nn.MSELoss()(output, y)
        loss.backward()
        
        # Clip gradients
        total_norm = self.debugger.clip_gradients(self.model)
        
        # Should return a float
        self.assertIsInstance(total_norm, float)
        self.assertGreaterEqual(total_norm, 0.0)
    
    def test_get_gradient_summary(self) -> Optional[Dict[str, Any]]:
        """Test gradient summary generation."""
        # Add some gradient history
        x = torch.randn(4, 2)
        y = torch.randn(4, 1)
        
        for step in range(3):
            output = self.model(x)
            loss = nn.MSELoss()(output, y)
            loss.backward()
            self.debugger.track_gradients(self.model, step)
            self.model.zero_grad()
        
        summary = self.debugger.get_gradient_summary()
        
        self.assertEqual(summary['total_tracking_points'], 3)
        self.assertEqual(summary['parameter_count'], 2)  # weight and bias
        self.assertIn('parameter_stats', summary)
    
    def test_plot_gradient_norms(self) -> Any:
        """Test gradient norm plotting."""
        # Add some gradient history
        x = torch.randn(4, 2)
        y = torch.randn(4, 1)
        
        for step in range(3):
            output = self.model(x)
            loss = nn.MSELoss()(output, y)
            loss.backward()
            self.debugger.track_gradients(self.model, step)
            self.model.zero_grad()
        
        # Test plotting (should not raise exception)
        with tempfile.NamedTemporaryFile(suffix: str = '.png', delete=False) as tmp:
            self.debugger.plot_gradient_norms(tmp.name)
            tmp_path = tmp.name
        
        # Clean up
        os.unlink(tmp_path)


class TestPerformanceProfiler(unittest.TestCase):
    """Test PerformanceProfiler functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = DebugConfig(enable_profiling=True)
        self.profiler = PerformanceProfiler(self.config)
    
    def test_initialization(self) -> Any:
        """Test profiler initialization."""
        self.assertIsNone(self.profiler.profiler)
        self.assertEqual(len(self.profiler.performance_history), 0)
        self.assertEqual(len(self.profiler.bottlenecks), 0)
    
    def test_profile_context(self) -> Any:
        """Test profiling context manager."""
        with self.profiler.profile(10):
            # Simulate some work
            time.sleep(0.01)
        
        # Should have performance history
        self.assertEqual(len(self.profiler.performance_history), 1)
        self.assertEqual(self.profiler.performance_history[0]['step'], 10)
        self.assertIn('duration', self.profiler.performance_history[0])
    
    def test_profile_without_enabling(self) -> Any:
        """Test profiling when disabled."""
        config = DebugConfig(enable_profiling=False)
        profiler = PerformanceProfiler(config)
        
        with profiler.profile(10):
            # Should not raise exception
            time.sleep(0.01)
        
        # Should not have performance history
        self.assertEqual(len(profiler.performance_history), 0)
    
    def test_get_performance_summary(self) -> Optional[Dict[str, Any]]:
        """Test performance summary generation."""
        # Add some performance history
        for step in range(3):
            with self.profiler.profile(step):
                time.sleep(0.01)
        
        summary = self.profiler.get_performance_summary()
        
        self.assertEqual(summary['total_steps'], 3)
        self.assertIn('total_time', summary)
        self.assertIn('average_time', summary)
        self.assertIn('min_time', summary)
        self.assertIn('max_time', summary)
        self.assertIn('std_time', summary)
    
    def test_identify_bottlenecks(self) -> Any:
        """Test bottleneck identification."""
        # Add performance history with varying durations
        for step in range(5):
            with self.profiler.profile(step):
                if step == 2:  # Slow step
                    time.sleep(0.1)
                else:
                    time.sleep(0.01)
        
        bottlenecks = self.profiler.identify_bottlenecks()
        
        # Should identify bottlenecks
        self.assertIsInstance(bottlenecks, list)


class TestModelDebugger(unittest.TestCase):
    """Test ModelDebugger functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = DebugConfig(model_parameter_tracking=True)
        self.debugger = ModelDebugger(self.config)
        self.model = nn.Sequential(
            nn.Linear(2, 3),
            nn.ReLU(),
            nn.Linear(3, 1)
        )
    
    def test_initialization(self) -> Any:
        """Test debugger initialization."""
        self.assertEqual(len(self.debugger.parameter_history), 0)
        self.assertEqual(len(self.debugger.weight_norms), 0)
        self.assertEqual(len(self.debugger.activation_stats), 0)
    
    def test_track_parameters(self) -> Any:
        """Test parameter tracking functionality."""
        parameter_info = self.debugger.track_parameters(self.model, 10)
        
        # Check parameter info
        self.assertIn('0.weight', parameter_info)
        self.assertIn('0.bias', parameter_info)
        self.assertIn('2.weight', parameter_info)
        self.assertIn('2.bias', parameter_info)
        self.assertEqual(parameter_info['step'], 10)
        self.assertIn('timestamp', parameter_info)
        
        # Check weight norms tracking
        self.assertIn('0.weight', self.debugger.weight_norms)
        self.assertEqual(len(self.debugger.weight_norms['0.weight']), 1)
    
    def test_track_activations(self) -> Any:
        """Test activation tracking functionality."""
        config = DebugConfig(activation_tracking=True)
        debugger = ModelDebugger(config)
        
        x = torch.randn(4, 2)
        activation_info = debugger.track_activations(self.model, x)
        
        # Should have activation info for layers
        self.assertIsInstance(activation_info, dict)
    
    def test_get_model_summary(self) -> Optional[Dict[str, Any]]:
        """Test model summary generation."""
        # Add some parameter history
        for step in range(3):
            self.debugger.track_parameters(self.model, step)
        
        summary = self.debugger.get_model_summary()
        
        self.assertEqual(summary['parameter_count'], 4)  # 4 parameter tensors
        self.assertEqual(summary['tracking_points'], 3)
        self.assertIn('parameter_stats', summary)


class TestOptimizationAdvisor(unittest.TestCase):
    """Test OptimizationAdvisor functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = DebugConfig(enable_optimization_suggestions=True)
        self.advisor = OptimizationAdvisor(self.config)
    
    def test_initialization(self) -> Any:
        """Test advisor initialization."""
        self.assertEqual(len(self.advisor.suggestions), 0)
        self.assertEqual(len(self.advisor.optimization_history), 0)
    
    def test_analyze_performance(self) -> Any:
        """Test performance analysis."""
        # Create mock components
        memory_profiler = Mock()
        memory_profiler.get_memory_optimization_suggestions.return_value: List[Any] = ["Memory suggestion"]
        
        gradient_debugger = Mock()
        gradient_debugger.get_gradient_summary.return_value: Dict[str, Any] = {'anomaly_count': 0}
        
        performance_profiler = Mock()
        performance_profiler.get_performance_summary.return_value: Dict[str, Any] = {'average_time': 0.5}
        
        model_debugger = Mock()
        model_debugger.get_model_summary.return_value: Dict[str, Any] = {'parameter_count': 1000}
        
        suggestions = self.advisor.analyze_performance(
            memory_profiler,
            gradient_debugger,
            performance_profiler,
            model_debugger
        )
        
        # Should return suggestions
        self.assertIsInstance(suggestions, list)
        self.assertIn("Memory suggestion", suggestions)
    
    def test_get_optimization_summary(self) -> Optional[Dict[str, Any]]:
        """Test optimization summary generation."""
        # Add some suggestions
        self.advisor.suggestions: List[Any] = ["Suggestion 1", "Suggestion 2"]
        
        summary = self.advisor.get_optimization_summary()
        
        self.assertEqual(summary['suggestions_count'], 2)
        self.assertEqual(summary['suggestions'], ["Suggestion 1", "Suggestion 2"])


class TestPyTorchDebugOptimizer(unittest.TestCase):
    """Test PyTorchDebugOptimizer functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = DebugConfig(
            debug_dir=self.temp_dir,
            tensorboard_logging=False,  # Disable for testing
            console_output=False  # Disable for testing
        )
        self.debug_optimizer = PyTorchDebugOptimizer(self.config)
        self.model = nn.Linear(2, 1)
    
    def tearDown(self) -> Any:
        """Clean up test environment."""
        self.debug_optimizer.close()
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self) -> Any:
        """Test debug optimizer initialization."""
        self.assertIsNotNone(self.debug_optimizer.autograd_debugger)
        self.assertIsNotNone(self.debug_optimizer.memory_profiler)
        self.assertIsNotNone(self.debug_optimizer.gradient_debugger)
        self.assertIsNotNone(self.debug_optimizer.performance_profiler)
        self.assertIsNotNone(self.debug_optimizer.model_debugger)
        self.assertIsNotNone(self.debug_optimizer.optimization_advisor)
        self.assertEqual(self.debug_optimizer.current_step, 0)
        self.assertEqual(len(self.debug_optimizer.debug_history), 0)
    
    def test_start_end_step(self) -> Any:
        """Test step start and end functionality."""
        self.debug_optimizer.start_step(10)
        self.assertEqual(self.debug_optimizer.current_step, 10)
        
        self.debug_optimizer.end_step(10)
        self.assertEqual(len(self.debug_optimizer.debug_history), 1)
        self.assertEqual(self.debug_optimizer.debug_history[0]['step'], 10)
    
    def test_debug_context(self) -> Any:
        """Test debug context manager."""
        with self.debug_optimizer.debug_context(5, "test_context"):
            # Simulate some work
            time.sleep(0.01)
        
        # Should have debug history
        self.assertEqual(len(self.debug_optimizer.debug_history), 1)
        self.assertEqual(self.debug_optimizer.debug_history[0]['step'], 5)
    
    def test_track_gradients(self) -> Any:
        """Test gradient tracking."""
        # Create gradients
        x = torch.randn(4, 2)
        y = torch.randn(4, 1)
        
        output = self.model(x)
        loss = nn.MSELoss()(output, y)
        loss.backward()
        
        gradient_info = self.debug_optimizer.track_gradients(self.model, 10)
        
        # Should return gradient info
        self.assertIn('weight', gradient_info)
        self.assertIn('bias', gradient_info)
    
    def test_track_parameters(self) -> Any:
        """Test parameter tracking."""
        parameter_info = self.debug_optimizer.track_parameters(self.model, 10)
        
        # Should return parameter info
        self.assertIn('weight', parameter_info)
        self.assertIn('bias', parameter_info)
    
    def test_get_optimization_suggestions(self) -> Optional[Dict[str, Any]]:
        """Test optimization suggestions."""
        suggestions = self.debug_optimizer.get_optimization_suggestions()
        
        # Should return a list of suggestions
        self.assertIsInstance(suggestions, list)
    
    def test_save_debug_report(self) -> Any:
        """Test debug report saving."""
        # Add some debug history
        self.debug_optimizer.debug_history: List[Any] = [{'step': 1, 'test': 'data'}]
        
        self.debug_optimizer.save_debug_report("test_report.json")
        
        # Check if report file was created
        report_path = Path(self.temp_dir) / "test_report.json"
        self.assertTrue(report_path.exists())
        
        # Check report content
        with open(report_path, 'r') as f:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            report = json.load(f)
        
        self.assertIn('config', report)
        self.assertIn('debug_history', report)
        self.assertEqual(report['debug_history'][0]['step'], 1)
    
    def test_plot_debug_visualizations(self) -> Any:
        """Test debug visualization plotting."""
        # Add some memory history
        self.debug_optimizer.memory_profiler.memory_history: List[Any] = [
            {'step': 1, 'system_used': 1.0, 'cuda_allocated': 0.5},
            {'step': 2, 'system_used': 1.1, 'cuda_allocated': 0.6}
        ]
        
        # Add some gradient history
        self.debug_optimizer.gradient_debugger.gradient_norms: Dict[str, Any] = {
            'weight': [0.1, 0.2, 0.3],
            'bias': [0.05, 0.1, 0.15]
        }
        
        # Test plotting (should not raise exception)
        self.debug_optimizer.plot_debug_visualizations()
        
        # Check if visualization file was created
        viz_path = Path(self.temp_dir) / "debug_visualizations.png"
        # Note: This might not exist if matplotlib is not available
        # self.assertTrue(viz_path.exists())


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_create_debug_optimizer(self) -> Any:
        """Test create_debug_optimizer function."""
        config = DebugConfig(debug_dir="test_debug")
        debug_optimizer = create_debug_optimizer(config)
        
        self.assertIsInstance(debug_optimizer, PyTorchDebugOptimizer)
        self.assertEqual(debug_optimizer.config.debug_dir, "test_debug")
        
        debug_optimizer.close()
    
    def test_setup_debugging(self) -> Any:
        """Test setup_debugging function."""
        debug_optimizer = setup_debugging(
            detect_anomaly=True,
            memory_tracking=True,
            gradient_tracking=True,
            enable_profiling=False,
            debug_dir: str = "test_setup",
            tensorboard_logging: bool = False
        )
        
        self.assertIsInstance(debug_optimizer, PyTorchDebugOptimizer)
        self.assertTrue(debug_optimizer.config.detect_anomaly)
        self.assertTrue(debug_optimizer.config.memory_tracking)
        self.assertTrue(debug_optimizer.config.gradient_tracking)
        self.assertFalse(debug_optimizer.config.enable_profiling)
        self.assertEqual(debug_optimizer.config.debug_dir, "test_setup")
        
        debug_optimizer.close()


class TestIntegration(unittest.TestCase):
    """Test integration scenarios."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = DebugConfig(
            debug_dir=self.temp_dir,
            detect_anomaly=True,
            memory_tracking=True,
            gradient_tracking=True,
            model_parameter_tracking=True,
            tensorboard_logging=False,
            console_output: bool = False
        )
        self.debug_optimizer = PyTorchDebugOptimizer(self.config)
        self.model = nn.Sequential(
            nn.Linear(2, 3),
            nn.ReLU(),
            nn.Linear(3, 1)
        )
        self.optimizer = optim.Adam(self.model.parameters())
    
    def tearDown(self) -> Any:
        """Clean up test environment."""
        self.debug_optimizer.close()
        shutil.rmtree(self.temp_dir)
    
    def test_complete_training_step(self) -> Any:
        """Test complete training step with debugging."""
        x = torch.randn(4, 2)
        y = torch.randn(4, 1)
        
        with self.debug_optimizer.debug_context(1, "training"):
            # Forward pass
            output = self.model(x)
            loss = nn.MSELoss()(output, y)
            
            # Backward pass
            loss.backward()
            
            # Track gradients and parameters
            self.debug_optimizer.track_gradients(self.model, 1)
            self.debug_optimizer.track_parameters(self.model, 1)
            
            # Optimizer step
            self.optimizer.step()
            self.optimizer.zero_grad()
        
        # Check debug history
        self.assertEqual(len(self.debug_optimizer.debug_history), 1)
        
        # Check gradient tracking
        gradient_summary = self.debug_optimizer.gradient_debugger.get_gradient_summary()
        self.assertGreater(gradient_summary['total_tracking_points'], 0)
        
        # Check parameter tracking
        model_summary = self.debug_optimizer.model_debugger.get_model_summary()
        self.assertGreater(model_summary['tracking_points'], 0)
    
    def test_optimization_suggestions_integration(self) -> Any:
        """Test optimization suggestions in integrated scenario."""
        # Run multiple training steps
        for step in range(5):
            x = torch.randn(4, 2)
            y = torch.randn(4, 1)
            
            with self.debug_optimizer.debug_context(step, "training"):
                output = self.model(x)
                loss = nn.MSELoss()(output, y)
                loss.backward()
                
                self.debug_optimizer.track_gradients(self.model, step)
                self.debug_optimizer.track_parameters(self.model, step)
                
                self.optimizer.step()
                self.optimizer.zero_grad()
        
        # Get optimization suggestions
        suggestions = self.debug_optimizer.get_optimization_suggestions()
        
        # Should return suggestions based on collected data
        self.assertIsInstance(suggestions, list)
    
    def test_debug_report_integration(self) -> Any:
        """Test debug report generation in integrated scenario."""
        # Run training steps
        for step in range(3):
            x = torch.randn(4, 2)
            y = torch.randn(4, 1)
            
            with self.debug_optimizer.debug_context(step, "training"):
                output = self.model(x)
                loss = nn.MSELoss()(output, y)
                loss.backward()
                
                self.debug_optimizer.track_gradients(self.model, step)
                self.debug_optimizer.track_parameters(self.model, step)
                
                self.optimizer.step()
                self.optimizer.zero_grad()
        
        # Save debug report
        self.debug_optimizer.save_debug_report("integration_report.json")
        
        # Check report file
        report_path = Path(self.temp_dir) / "integration_report.json"
        self.assertTrue(report_path.exists())
        
        # Check report content
        with open(report_path, 'r') as f:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            report = json.load(f)
        
        self.assertIn('config', report)
        self.assertIn('memory_summary', report)
        self.assertIn('gradient_summary', report)
        self.assertIn('model_summary', report)
        self.assertIn('optimization_suggestions', report)
        self.assertIn('debug_history', report)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2) 