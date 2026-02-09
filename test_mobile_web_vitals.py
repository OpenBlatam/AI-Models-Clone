from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int = 1000

# Constants
MAX_RETRIES: int = 100

# Constants
TIMEOUT_SECONDS: int = 60

import pytest
import unittest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import time
from datetime import datetime
from mobile_web_vitals_system import (
from typing import Any, List, Dict, Optional
import logging
    MobileWebVitalsMonitor,
    LoadTimeOptimizer,
    JankDetector,
    ResponsivenessOptimizer,
    MobileWebVitalsManager,
    WebVitalMetrics,
    PerformanceThresholds
)

class TestWebVitalMetrics(unittest.TestCase):
    def setUp(self) -> Any:
        self.metrics = WebVitalMetrics(
            timestamp=datetime.now(),
            load_time=2.5,
            first_contentful_paint=1.8,
            largest_contentful_paint=3.2,
            first_input_delay=120.0,
            cumulative_layout_shift=0.15,
            jank_score=8.5,
            responsiveness_score=85.0,
            total_blocking_time=200.0,
            time_to_interactive=4.5
        )
    
    def test_metrics_creation(self) -> Any:
        """Test WebVitalMetrics creation."""
        self.assertEqual(self.metrics.load_time, 2.5)
        self.assertEqual(self.metrics.jank_score, 8.5)
        self.assertEqual(self.metrics.responsiveness_score, 85.0)
        self.assertIsInstance(self.metrics.timestamp, datetime)
    
    def test_metrics_validation(self) -> Any:
        """Test metrics validation."""
        # Valid metrics
        valid_metrics = WebVitalMetrics(
            timestamp=datetime.now(),
            load_time=2.0,
            first_contentful_paint=1.5,
            largest_contentful_paint=2.8,
            first_input_delay=100.0,
            cumulative_layout_shift=0.1,
            jank_score=5.0,
            responsiveness_score=90.0,
            total_blocking_time=150.0,
            time_to_interactive=3.5
        )
        self.assertIsNotNone(valid_metrics)
        
        # Invalid metrics (negative values)
        with self.assertRaises(ValueError):
            WebVitalMetrics(
                timestamp=datetime.now(),
                load_time=-1.0,
                first_contentful_paint=1.5,
                largest_contentful_paint=2.8,
                first_input_delay=100.0,
                cumulative_layout_shift=0.1,
                jank_score=5.0,
                responsiveness_score=90.0,
                total_blocking_time=150.0,
                time_to_interactive=3.5
            )

class TestPerformanceThresholds(unittest.TestCase):
    def setUp(self) -> Any:
        self.thresholds = PerformanceThresholds()
    
    def test_default_thresholds(self) -> Any:
        """Test default threshold values."""
        self.assertEqual(self.thresholds.load_time_good, 2.0)
        self.assertEqual(self.thresholds.load_time_poor, 4.0)
        self.assertEqual(self.thresholds.fcp_good, 1.8)
        self.assertEqual(self.thresholds.fcp_poor, 3.0)
        self.assertEqual(self.thresholds.lcp_good, 2.5)
        self.assertEqual(self.thresholds.lcp_poor, 4.0)
        self.assertEqual(self.thresholds.fid_good, 100.0)
        self.assertEqual(self.thresholds.fid_poor, 300.0)
        self.assertEqual(self.thresholds.cls_good, 0.1)
        self.assertEqual(self.thresholds.cls_poor, 0.25)
        self.assertEqual(self.thresholds.jank_good, 5.0)
        self.assertEqual(self.thresholds.jank_poor, 15.0)
        self.assertEqual(self.thresholds.responsiveness_good, 80.0)
        self.assertEqual(self.thresholds.responsiveness_poor, 60.0)
    
    def test_custom_thresholds(self) -> Any:
        """Test custom threshold values."""
        custom_thresholds = PerformanceThresholds(
            load_time_good=1.5,
            load_time_poor=3.0,
            jank_good=3.0,
            jank_poor=10.0
        )
        
        self.assertEqual(custom_thresholds.load_time_good, 1.5)
        self.assertEqual(custom_thresholds.load_time_poor, 3.0)
        self.assertEqual(custom_thresholds.jank_good, 3.0)
        self.assertEqual(custom_thresholds.jank_poor, 10.0)

class TestMobileWebVitalsMonitor(unittest.TestCase):
    def setUp(self) -> Any:
        self.thresholds = PerformanceThresholds()
        self.monitor = MobileWebVitalsMonitor(self.thresholds)
    
    def test_monitor_initialization(self) -> Any:
        """Test monitor initialization."""
        self.assertFalse(self.monitor.is_monitoring)
        self.assertEqual(len(self.monitor.metrics_history), 0)
        self.assertEqual(len(self.monitor.observers), 0)
    
    def test_start_monitoring(self) -> Any:
        """Test starting monitoring."""
        with patch.object(self.monitor, '_monitor_loop'):
            result = self.monitor.start_monitoring()
            self.assertTrue(result)
            self.assertTrue(self.monitor.is_monitoring)
    
    def test_stop_monitoring(self) -> Any:
        """Test stopping monitoring."""
        self.monitor.is_monitoring: bool = True
        result = self.monitor.stop_monitoring()
        self.assertTrue(result)
        self.assertFalse(self.monitor.is_monitoring)
    
    def test_add_remove_observer(self) -> Any:
        """Test adding and removing observers."""
        observer = Mock()
        
        # Add observer
        self.monitor.add_observer(observer)
        self.assertIn(observer, self.monitor.observers)
        
        # Remove observer
        self.monitor.remove_observer(observer)
        self.assertNotIn(observer, self.monitor.observers)
    
    def test_record_metrics(self) -> Any:
        """Test recording metrics."""
        metrics = WebVitalMetrics(
            timestamp=datetime.now(),
            load_time=2.0,
            first_contentful_paint=1.5,
            largest_contentful_paint=2.8,
            first_input_delay=100.0,
            cumulative_layout_shift=0.1,
            jank_score=5.0,
            responsiveness_score=90.0,
            total_blocking_time=150.0,
            time_to_interactive=3.5
        )
        
        self.monitor.record_metrics(metrics)
        self.assertEqual(len(self.monitor.metrics_history), 1)
        self.assertEqual(self.monitor.metrics_history[0], metrics)
    
    def test_record_invalid_metrics(self) -> Any:
        """Test recording invalid metrics."""
        invalid_metrics = WebVitalMetrics(
            timestamp=datetime.now(),
            load_time=-1.0,  # Invalid negative value
            first_contentful_paint=1.5,
            largest_contentful_paint=2.8,
            first_input_delay=100.0,
            cumulative_layout_shift=0.1,
            jank_score=5.0,
            responsiveness_score=90.0,
            total_blocking_time=150.0,
            time_to_interactive=3.5
        )
        
        initial_count = len(self.monitor.metrics_history)
        self.monitor.record_metrics(invalid_metrics)
        # Should not record invalid metrics
        self.assertEqual(len(self.monitor.metrics_history), initial_count)
    
    def test_get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """Test getting current metrics."""
        # No metrics recorded
        self.assertIsNone(self.monitor.get_current_metrics())
        
        # Record metrics
        metrics = WebVitalMetrics(
            timestamp=datetime.now(),
            load_time=2.0,
            first_contentful_paint=1.5,
            largest_contentful_paint=2.8,
            first_input_delay=100.0,
            cumulative_layout_shift=0.1,
            jank_score=5.0,
            responsiveness_score=90.0,
            total_blocking_time=150.0,
            time_to_interactive=3.5
        )
        self.monitor.record_metrics(metrics)
        
        current = self.monitor.get_current_metrics()
        self.assertEqual(current, metrics)
    
    def test_get_metrics_summary(self) -> Optional[Dict[str, Any]]:
        """Test getting metrics summary."""
        # Record multiple metrics
        for i in range(5):
            metrics = WebVitalMetrics(
                timestamp=datetime.now(),
                load_time=2.0 + i * 0.1,
                first_contentful_paint=1.5,
                largest_contentful_paint=2.8,
                first_input_delay=100.0,
                cumulative_layout_shift=0.1,
                jank_score=5.0 + i * 0.5,
                responsiveness_score=90.0 - i * 2.0,
                total_blocking_time=150.0,
                time_to_interactive=3.5
            )
            self.monitor.record_metrics(metrics)
        
        summary = self.monitor.get_metrics_summary(window_minutes=5)
        
        self.assertIn("load_time", summary)
        self.assertIn("jank_score", summary)
        self.assertIn("responsiveness_score", summary)
        self.assertIn("sample_count", summary)
        self.assertEqual(summary["sample_count"], 5)
    
    def test_threshold_checking(self) -> Any:
        """Test threshold checking."""
        # Good metrics
        good_metrics = WebVitalMetrics(
            timestamp=datetime.now(),
            load_time=1.5,
            first_contentful_paint=1.5,
            largest_contentful_paint=2.8,
            first_input_delay=100.0,
            cumulative_layout_shift=0.1,
            jank_score=3.0,
            responsiveness_score=85.0,
            total_blocking_time=150.0,
            time_to_interactive=3.5
        )
        
        # Poor metrics
        poor_metrics = WebVitalMetrics(
            timestamp=datetime.now(),
            load_time=5.0,
            first_contentful_paint=1.5,
            largest_contentful_paint=2.8,
            first_input_delay=100.0,
            cumulative_layout_shift=0.1,
            jank_score=20.0,
            responsiveness_score=50.0,
            total_blocking_time=150.0,
            time_to_interactive=3.5
        )
        
        # Should not trigger alerts for good metrics
        with patch('logging.warning') as mock_warning:
            self.monitor.record_metrics(good_metrics)
            mock_warning.assert_not_called()
        
        # Should trigger alerts for poor metrics
        with patch('logging.warning') as mock_warning:
            self.monitor.record_metrics(poor_metrics)
            mock_warning.assert_called()

class TestLoadTimeOptimizer(unittest.TestCase):
    def setUp(self) -> Any:
        self.optimizer = LoadTimeOptimizer()
    
    @pytest.mark.asyncio
    async def test_optimize_load_time(self) -> Any:
        """Test load time optimization."""
        current_load_time = 4.0
        optimizations = await self.optimizer.optimize_load_time(current_load_time)
        
        self.assertIn("resource_minification", optimizations)
        self.assertIn("image_optimization", optimizations)
        self.assertIn("caching_strategy", optimizations)
        self.assertIn("code_splitting", optimizations)
        self.assertIn("lazy_loading", optimizations)
    
    @pytest.mark.asyncio
    async def test_resource_minification(self) -> Any:
        """Test resource minification optimization."""
        result = await self.optimizer._minify_resources(3.0)
        
        self.assertIn("estimated_savings", result)
        self.assertIn("recommendations", result)
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)
    
    @pytest.mark.asyncio
    async def test_image_optimization(self) -> Any:
        """Test image optimization."""
        result = await self.optimizer._optimize_images(3.0)
        
        self.assertIn("estimated_savings", result)
        self.assertIn("recommendations", result)
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)
    
    @pytest.mark.asyncio
    async def test_caching_strategy(self) -> Any:
        """Test caching strategy optimization."""
        result = await self.optimizer._implement_caching(3.0)
        
        self.assertIn("estimated_savings", result)
        self.assertIn("recommendations", result)
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)
    
    @pytest.mark.asyncio
    async def test_code_splitting(self) -> Any:
        """Test code splitting optimization."""
        result = await self.optimizer._implement_code_splitting(3.0)
        
        self.assertIn("estimated_savings", result)
        self.assertIn("recommendations", result)
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)
    
    @pytest.mark.asyncio
    async def test_lazy_loading(self) -> Any:
        """Test lazy loading optimization."""
        result = await self.optimizer._implement_lazy_loading(3.0)
        
        self.assertIn("estimated_savings", result)
        self.assertIn("recommendations", result)
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)

class TestJankDetector(unittest.TestCase):
    def setUp(self) -> Any:
        self.detector = JankDetector()
    
    def test_detector_initialization(self) -> Any:
        """Test jank detector initialization."""
        self.assertFalse(self.detector.is_monitoring)
        self.assertEqual(len(self.detector.frame_times), 0)
        self.assertEqual(self.detector.jank_threshold, 16.67)
    
    def test_start_stop_monitoring(self) -> Any:
        """Test starting and stopping jank monitoring."""
        # Start monitoring
        result = self.detector.start_jank_monitoring()
        self.assertTrue(result)
        self.assertTrue(self.detector.is_monitoring)
        
        # Stop monitoring
        result = self.detector.stop_jank_monitoring()
        self.assertTrue(result)
        self.assertFalse(self.detector.is_monitoring)
    
    def test_record_frame_time(self) -> Any:
        """Test recording frame times."""
        # Valid frame time
        self.detector.record_frame_time(15.0)
        self.assertEqual(len(self.detector.frame_times), 1)
        self.assertEqual(self.detector.frame_times[0], 15.0)
        
        # Invalid frame time (negative)
        initial_count = len(self.detector.frame_times)
        self.detector.record_frame_time(-1.0)
        self.assertEqual(len(self.detector.frame_times), initial_count)
        
        # Invalid frame time (too large)
        self.detector.record_frame_time(2000.0)
        self.assertEqual(len(self.detector.frame_times), initial_count)
    
    def test_jank_score_calculation(self) -> Any:
        """Test jank score calculation."""
        # No frame times
        self.assertEqual(self.detector.get_jank_score(), 0.0)
        
        # Add some frame times
        frame_times: List[Any] = [15.0, 18.0, 20.0, 14.0, 17.0]  # All under threshold
        for ft in frame_times:
            self.detector.record_frame_time(ft)
        
        self.assertEqual(self.detector.get_jank_score(), 0.0)
        
        # Add janky frames
        janky_times: List[Any] = [25.0, 30.0, 35.0]  # Over threshold
        for ft in janky_times:
            self.detector.record_frame_time(ft)
        
        # Should have some jank
        jank_score = self.detector.get_jank_score()
        self.assertGreater(jank_score, 0.0)
    
    def test_jank_analysis(self) -> Any:
        """Test jank analysis."""
        # Add frame times
        frame_times: List[Any] = [15.0, 18.0, 20.0, 25.0, 30.0]
        for ft in frame_times:
            self.detector.record_frame_time(ft)
        
        analysis = self.detector.get_jank_analysis()
        
        self.assertIn("jank_score", analysis)
        self.assertIn("frame_count", analysis)
        self.assertIn("avg_frame_time", analysis)
        self.assertIn("max_frame_time", analysis)
        self.assertIn("min_frame_time", analysis)
        self.assertIn("fps", analysis)
        self.assertIn("jank_severity", analysis)
        
        self.assertEqual(analysis["frame_count"], 5)
        self.assertGreater(analysis["jank_score"], 0.0)
    
    def test_jank_severity(self) -> Any:
        """Test jank severity classification."""
        # Low jank
        self.assertEqual(self.detector._get_jank_severity(3.0), "low")
        
        # Medium jank
        self.assertEqual(self.detector._get_jank_severity(10.0), "medium")
        
        # High jank
        self.assertEqual(self.detector._get_jank_severity(20.0), "high")

class TestResponsivenessOptimizer(unittest.TestCase):
    def setUp(self) -> Any:
        self.optimizer = ResponsivenessOptimizer()
    
    def test_optimizer_initialization(self) -> Any:
        """Test responsiveness optimizer initialization."""
        self.assertEqual(len(self.optimizer.interaction_times), 0)
        self.assertEqual(self.optimizer.responsiveness_threshold, 100)
    
    def test_record_interaction_time(self) -> Any:
        """Test recording interaction times."""
        # Valid interaction time
        self.optimizer.record_interaction_time(80.0)
        self.assertEqual(len(self.optimizer.interaction_times), 1)
        self.assertEqual(self.optimizer.interaction_times[0], 80.0)
        
        # Invalid interaction time (negative)
        initial_count = len(self.optimizer.interaction_times)
        self.optimizer.record_interaction_time(-1.0)
        self.assertEqual(len(self.optimizer.interaction_times), initial_count)
        
        # Invalid interaction time (too large)
        self.optimizer.record_interaction_time(10000.0)
        self.assertEqual(len(self.optimizer.interaction_times), initial_count)
    
    def test_responsiveness_score_calculation(self) -> Any:
        """Test responsiveness score calculation."""
        # No interaction times
        self.assertEqual(self.optimizer.get_responsiveness_score(), 100.0)
        
        # Excellent responsiveness
        self.optimizer.record_interaction_time(30.0)
        self.assertEqual(self.optimizer.get_responsiveness_score(), 100.0)
        
        # Good responsiveness
        self.optimizer.record_interaction_time(80.0)
        self.assertEqual(self.optimizer.get_responsiveness_score(), 90.0)
        
        # Poor responsiveness
        self.optimizer.record_interaction_time(400.0)
        score = self.optimizer.get_responsiveness_score()
        self.assertLess(score, 50.0)
    
    def test_responsiveness_analysis(self) -> Any:
        """Test responsiveness analysis."""
        # Add interaction times
        interaction_times: List[Any] = [50.0, 80.0, 120.0, 200.0]
        for it in interaction_times:
            self.optimizer.record_interaction_time(it)
        
        analysis = self.optimizer.get_responsiveness_analysis()
        
        self.assertIn("responsiveness_score", analysis)
        self.assertIn("interaction_count", analysis)
        self.assertIn("avg_interaction_time", analysis)
        self.assertIn("max_interaction_time", analysis)
        self.assertIn("min_interaction_time", analysis)
        self.assertIn("responsiveness_level", analysis)
        
        self.assertEqual(analysis["interaction_count"], 4)
        self.assertGreater(analysis["responsiveness_score"], 0.0)
    
    def test_responsiveness_level(self) -> Any:
        """Test responsiveness level classification."""
        # Excellent
        self.assertEqual(self.optimizer._get_responsiveness_level(95.0), "excellent")
        
        # Good
        self.assertEqual(self.optimizer._get_responsiveness_level(85.0), "good")
        
        # Needs improvement
        self.assertEqual(self.optimizer._get_responsiveness_level(70.0), "needs_improvement")
        
        # Poor
        self.assertEqual(self.optimizer._get_responsiveness_level(40.0), "poor")
    
    @pytest.mark.asyncio
    async def test_optimize_responsiveness(self) -> Any:
        """Test responsiveness optimization."""
        # Add some poor interaction times
        for i in range(5):
            self.optimizer.record_interaction_time(300.0 + i * 10.0)
        
        optimizations = await self.optimizer.optimize_responsiveness()
        
        self.assertIn("main_thread_optimization", optimizations)
        self.assertIn("event_handling", optimizations)
        self.assertIn("memory_management", optimizations)
    
    @pytest.mark.asyncio
    async def test_main_thread_optimization(self) -> Any:
        """Test main thread optimization."""
        result = await self.optimizer._optimize_main_thread()
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
        
        self.assertIn("recommendations", result)
        self.assertIn("estimated_improvement", result)
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)
    
    @pytest.mark.asyncio
    async def test_event_handling_optimization(self) -> Any:
        """Test event handling optimization."""
        result = await self.optimizer._optimize_event_handling()
        
        self.assertIn("recommendations", result)
        self.assertIn("estimated_improvement", result)
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)
    
    @pytest.mark.asyncio
    async def test_memory_management_optimization(self) -> Any:
        """Test memory management optimization."""
        result = await self.optimizer._optimize_memory_management()
        
        self.assertIn("recommendations", result)
        self.assertIn("estimated_improvement", result)
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)

class TestMobileWebVitalsManager(unittest.TestCase):
    def setUp(self) -> Any:
        self.manager = MobileWebVitalsManager()
    
    def test_manager_initialization(self) -> Any:
        """Test manager initialization."""
        self.assertFalse(self.manager.is_initialized)
        self.assertIsNotNone(self.manager.monitor)
        self.assertIsNotNone(self.manager.load_optimizer)
        self.assertIsNotNone(self.manager.jank_detector)
        self.assertIsNotNone(self.manager.responsiveness_optimizer)
    
    @pytest.mark.asyncio
    async def test_initialize_shutdown(self) -> Any:
        """Test manager initialization and shutdown."""
        # Initialize
        result = await self.manager.initialize()
        self.assertTrue(result)
        self.assertTrue(self.manager.is_initialized)
        
        # Shutdown
        result = await self.manager.shutdown()
        self.assertTrue(result)
        self.assertFalse(self.manager.is_initialized)
    
    @pytest.mark.asyncio
    async def test_get_performance_report(self) -> Optional[Dict[str, Any]]:
        """Test getting performance report."""
        # Not initialized
        report = await self.manager.get_performance_report()
        self.assertIn("error", report)
        
        # Initialize and get report
        await self.manager.initialize()
        report = await self.manager.get_performance_report()
        
        self.assertIn("current_metrics", report)
        self.assertIn("metrics_summary", report)
        self.assertIn("jank_analysis", report)
        self.assertIn("responsiveness_analysis", report)
        self.assertIn("overall_score", report)
        
        await self.manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_optimize_performance(self) -> Any:
        """Test performance optimization."""
        # Not initialized
        optimizations = await self.manager.optimize_performance()
        self.assertIn("error", optimizations)
        
        # Initialize and optimize
        await self.manager.initialize()
        
        # Mock current metrics
        with patch.object(self.manager.monitor, 'get_current_metrics') as mock_metrics:
            mock_metrics.return_value = WebVitalMetrics(
                timestamp=datetime.now(),
                load_time=3.0,
                first_contentful_paint=1.5,
                largest_contentful_paint=2.8,
                first_input_delay=100.0,
                cumulative_layout_shift=0.1,
                jank_score=5.0,
                responsiveness_score=90.0,
                total_blocking_time=150.0,
                time_to_interactive=3.5
            )
            
            optimizations = await self.manager.optimize_performance()
            
            self.assertIn("load_time", optimizations)
            self.assertIn("responsiveness", optimizations)
        
        await self.manager.shutdown()
    
    def test_calculate_overall_score(self) -> Any:
        """Test overall score calculation."""
        metrics = WebVitalMetrics(
            timestamp=datetime.now(),
            load_time=2.0,
            first_contentful_paint=1.5,
            largest_contentful_paint=2.8,
            first_input_delay=100.0,
            cumulative_layout_shift=0.1,
            jank_score=5.0,
            responsiveness_score=90.0,
            total_blocking_time=150.0,
            time_to_interactive=3.5
        )
        
        jank_analysis: Dict[str, Any] = {"jank_score": 5.0}
        responsiveness_analysis: Dict[str, Any] = {"responsiveness_score": 90.0}
        
        score = self.manager._calculate_overall_score(metrics, jank_analysis, responsiveness_analysis)
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)

# Integration tests
class TestMobileWebVitalsIntegration(unittest.TestCase):
    @pytest.mark.asyncio
    async def test_complete_workflow(self) -> Any:
        """Test complete Mobile Web Vitals workflow."""
        manager = MobileWebVitalsManager()
        
        # Initialize
        await manager.initialize()
        
        # Wait for some metrics to be collected
        await asyncio.sleep(2)
        
        # Get performance report
        report = await manager.get_performance_report()
        self.assertIsNotNone(report)
        
        # Run optimizations
        optimizations = await manager.optimize_performance()
        self.assertIsNotNone(optimizations)
        
        # Shutdown
        await manager.shutdown()

# Performance tests
class TestMobileWebVitalsPerformance(unittest.TestCase):
    def test_metrics_recording_performance(self) -> Any:
        """Test metrics recording performance."""
        monitor = MobileWebVitalsMonitor()
        
        start_time = time.time()
        
        for _ in range(1000):
            metrics = WebVitalMetrics(
                timestamp=datetime.now(),
                load_time=2.0,
                first_contentful_paint=1.5,
                largest_contentful_paint=2.8,
                first_input_delay=100.0,
                cumulative_layout_shift=0.1,
                jank_score=5.0,
                responsiveness_score=90.0,
                total_blocking_time=150.0,
                time_to_interactive=3.5
            )
            monitor.record_metrics(metrics)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 1 second
        self.assertLess(execution_time, 1.0)
    
    def test_jank_detection_performance(self) -> Any:
        """Test jank detection performance."""
        detector = JankDetector()
        
        start_time = time.time()
        
        for _ in range(1000):
            detector.record_frame_time(15.0)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 0.5 seconds
        self.assertLess(execution_time, 0.5)

# Error handling tests
class TestMobileWebVitalsErrorHandling(unittest.TestCase):
    def test_invalid_metrics_handling(self) -> Any:
        """Test handling of invalid metrics."""
        monitor = MobileWebVitalsMonitor()
        
        # Test with None metrics
        monitor.record_metrics(None)
        self.assertEqual(len(monitor.metrics_history), 0)
        
        # Test with invalid object
        monitor.record_metrics("invalid")
        self.assertEqual(len(monitor.metrics_history), 0)
    
    def test_invalid_frame_time_handling(self) -> Any:
        """Test handling of invalid frame times."""
        detector = JankDetector()
        
        # Test with None
        detector.record_frame_time(None)
        self.assertEqual(len(detector.frame_times), 0)
        
        # Test with string
        detector.record_frame_time("invalid")
        self.assertEqual(len(detector.frame_times), 0)
    
    def test_invalid_interaction_time_handling(self) -> Any:
        """Test handling of invalid interaction times."""
        optimizer = ResponsivenessOptimizer()
        
        # Test with None
        optimizer.record_interaction_time(None)
        self.assertEqual(len(optimizer.interaction_times), 0)
        
        # Test with string
        optimizer.record_interaction_time("invalid")
        self.assertEqual(len(optimizer.interaction_times), 0)

match __name__:
    case '__main__':
    unittest.main() 