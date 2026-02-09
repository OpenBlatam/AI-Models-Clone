"""
Test Runner for Instagram Captions API v10.0
Test execution, results collection, and reporting.
"""
import time
import threading
import signal
import sys
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging
import json
import yaml
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

from .test_suite import TestSuite, TestCase
from .test_result import TestResult, TestStatus

logger = logging.getLogger(__name__)

@dataclass
class TestRunResult:
    """Represents the result of a test run."""
    
    suite_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0
    execution_time: float = 0.0
    
    # Test results
    test_results: List[TestResult] = field(default_factory=list)
    
    # Statistics
    success_rate: float = 0.0
    average_execution_time: float = 0.0
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    environment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate derived statistics."""
        if self.end_time and self.start_time:
            self.execution_time = (self.end_time - self.start_time).total_seconds()
        
        if self.total_tests > 0:
            self.success_rate = (self.passed_tests / self.total_tests) * 100
            
            if self.test_results:
                total_time = sum(result.execution_time for result in self.test_results)
                self.average_execution_time = total_time / len(self.test_results)
    
    def add_test_result(self, result: TestResult):
        """Add a test result."""
        self.test_results.append(result)
        self.total_tests += 1
        
        if result.status == TestStatus.PASSED:
            self.passed_tests += 1
        elif result.status == TestStatus.FAILED:
            self.failed_tests += 1
        elif result.status == TestStatus.SKIPPED:
            self.skipped_tests += 1
        elif result.status == TestStatus.ERROR:
            self.error_tests += 1
        
        # Recalculate statistics
        if self.total_tests > 0:
            self.success_rate = (self.passed_tests / self.total_tests) * 100
            
            if self.test_results:
                total_time = sum(result.execution_time for result in self.test_results)
                self.average_execution_time = total_time / len(self.test_results)
    
    def finish(self):
        """Mark test run as finished."""
        self.end_time = datetime.now()
        self.execution_time = (self.end_time - self.start_time).total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the test run."""
        return {
            'suite_name': self.suite_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'execution_time': self.execution_time,
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'skipped_tests': self.skipped_tests,
            'error_tests': self.error_tests,
            'success_rate': self.success_rate,
            'average_execution_time': self.average_execution_time,
            'tags': self.tags,
            'groups': self.groups,
            'environment': self.environment,
            'metadata': self.metadata
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'summary': self.get_summary(),
            'test_results': [result.to_dict() for result in self.test_results]
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str, indent=2)
    
    def to_yaml(self) -> str:
        """Convert to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, allow_unicode=True, indent=2)
    
    def export_to_file(self, file_path: str, format: str = "json") -> bool:
        """Export test run result to file."""
        try:
            if format.lower() == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.to_json())
            elif format.lower() == "yaml":
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.to_yaml())
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error exporting test run result: {e}")
            return False

class TestRunner:
    """Executes test suites and manages test runs."""
    
    def __init__(self, max_workers: int = 4, timeout: Optional[float] = None):
        self.max_workers = max_workers
        self.default_timeout = timeout
        self.test_runs: List[TestRunResult] = []
        self.current_run: Optional[TestRunResult] = None
        
        # Execution control
        self.stop_requested = False
        self.pause_requested = False
        
        # Progress tracking
        self.progress_callback: Optional[Callable] = None
        self.results_callback: Optional[Callable] = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, stopping test execution...")
        self.stop_requested = True
    
    def run_test_suite(self, test_suite: TestSuite, 
                       tags: Optional[List[str]] = None,
                       groups: Optional[List[str]] = None,
                       exclude_tags: Optional[List[str]] = None,
                       parallel: bool = False,
                       stop_on_failure: bool = False,
                       retry_failed: int = 0,
                       environment: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> TestRunResult:
        """Run a test suite."""
        # Create test run result
        self.current_run = TestRunResult(
            suite_name=test_suite.name,
            start_time=datetime.now(),
            tags=tags or [],
            groups=groups or [],
            environment=environment,
            metadata=metadata or {}
        )
        
        # Filter tests
        tests_to_run = test_suite.filter_tests(
            tags=tags,
            groups=groups,
            exclude_tags=exclude_tags
        )
        
        if not tests_to_run:
            logger.warning("No tests to run after filtering")
            self.current_run.finish()
            return self.current_run
        
        logger.info(f"Running {len(tests_to_run)} tests from suite '{test_suite.name}'")
        
        try:
            if parallel and len(tests_to_run) > 1:
                self._run_tests_parallel(test_suite, tests_to_run, stop_on_failure)
            else:
                self._run_tests_sequential(test_suite, tests_to_run, stop_on_failure)
            
            # Retry failed tests if requested
            if retry_failed > 0:
                self._retry_failed_tests(test_suite, retry_failed)
            
        except KeyboardInterrupt:
            logger.info("Test execution interrupted by user")
        except Exception as e:
            logger.error(f"Error during test execution: {e}")
            if self.current_run:
                self.current_run.add_test_result(
                    TestResult(
                        test_name="test_runner_error",
                        status=TestStatus.ERROR,
                        error_message=str(e),
                        traceback=traceback.format_exc()
                    )
                )
        
        finally:
            if self.current_run:
                self.current_run.finish()
                self.test_runs.append(self.current_run)
                
                # Update test suite statistics
                test_suite.passed_tests = self.current_run.passed_tests
                test_suite.failed_tests = self.current_run.failed_tests
                test_suite.skipped_tests = self.current_run.skipped_tests
                test_suite.error_tests = self.current_run.error_tests
                
                logger.info(f"Test run completed: {self.current_run.passed_tests}/{self.current_run.total_tests} passed")
        
        return self.current_run
    
    def _run_tests_sequential(self, test_suite: TestSuite, tests: List[TestCase], 
                             stop_on_failure: bool):
        """Run tests sequentially."""
        for test_case in tests:
            if self.stop_requested:
                break
            
            if self.pause_requested:
                while self.pause_requested and not self.stop_requested:
                    time.sleep(0.1)
            
            result = self._execute_test(test_case)
            if self.current_run:
                self.current_run.add_test_result(result)
            
            # Progress callback
            if self.progress_callback:
                self.progress_callback(test_case.name, result)
            
            # Stop on failure if requested
            if stop_on_failure and result.is_failure():
                logger.info(f"Stopping on failure: {test_case.name}")
                break
    
    def _run_tests_parallel(self, test_suite: TestSuite, tests: List[TestCase], 
                           stop_on_failure: bool):
        """Run tests in parallel."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tests
            future_to_test = {
                executor.submit(self._execute_test, test_case): test_case 
                for test_case in tests
            }
            
            completed_count = 0
            for future in as_completed(future_to_test):
                if self.stop_requested:
                    break
                
                test_case = future_to_test[future]
                try:
                    result = future.result()
                    if self.current_run:
                        self.current_run.add_test_result(result)
                    
                    # Progress callback
                    if self.progress_callback:
                        self.progress_callback(test_case.name, result)
                    
                    completed_count += 1
                    logger.debug(f"Completed {completed_count}/{len(tests)} tests")
                    
                    # Stop on failure if requested
                    if stop_on_failure and result.is_failure():
                        logger.info(f"Stopping on failure: {test_case.name}")
                        # Cancel remaining futures
                        for f in future_to_test:
                            f.cancel()
                        break
                
                except Exception as e:
                    logger.error(f"Error executing test {test_case.name}: {e}")
                    error_result = TestResult(
                        test_name=test_case.name,
                        status=TestStatus.ERROR,
                        error_message=str(e),
                        traceback=traceback.format_exc()
                    )
                    if self.current_run:
                        self.current_run.add_test_result(error_result)
    
    def _execute_test(self, test_case: TestCase) -> TestResult:
        """Execute a single test case."""
        result = TestResult(
            test_name=test_case.name,
            test_class=test_case.test_class.__name__ if test_case.test_class else None,
            test_module=test_case.test_function.__module__,
            description=test_case.description,
            tags=test_case.tag,
            priority=test_case.priority
        )
        
        # Check if test should be skipped
        if test_case.should_skip():
            result.finish(TestStatus.SKIPPED, "Test skipped by condition")
            return result
        
        # Start test execution
        result.start()
        start_time = time.time()
        
        try:
            # Setup
            if test_case.setup_function:
                test_case.setup_function()
            
            # Execute test
            if test_case.timeout:
                # TODO: Implement timeout mechanism
                test_result = test_case.test_function()
            else:
                test_result = test_case.test_function()
            
            # Teardown
            if test_case.teardown_function:
                test_case.teardown_function()
            
            # Test passed
            execution_time = time.time() - start_time
            result.finish(TestStatus.PASSED, execution_time=execution_time)
            
            # Add performance metric
            result.add_performance_metric("execution_time", execution_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            result.finish(TestStatus.ERROR, error=e, execution_time=execution_time)
            
            # Add performance metric
            result.add_performance_metric("execution_time", execution_time)
            
            logger.error(f"Test {test_case.name} failed: {e}")
        
        return result
    
    def _retry_failed_tests(self, test_suite: TestSuite, max_retries: int):
        """Retry failed tests."""
        if not self.current_run:
            return
        
        failed_tests = [result for result in self.current_run.test_results if result.is_failure()]
        if not failed_tests:
            return
        
        logger.info(f"Retrying {len(failed_tests)} failed tests (max {max_retries} retries)")
        
        for retry_count in range(1, max_retries + 1):
            if not failed_tests:
                break
            
            logger.info(f"Retry attempt {retry_count}")
            retry_tests = failed_tests.copy()
            failed_tests = []
            
            for result in retry_tests:
                test_name = result.test_name
                if test_name in test_suite.test_cases:
                    test_case = test_suite.test_cases[test_name]
                    
                    # Execute retry
                    retry_result = self._execute_test(test_case)
                    
                    if retry_result.is_successful():
                        # Replace failed result with successful one
                        for i, existing_result in enumerate(self.current_run.test_results):
                            if existing_result.test_name == test_name:
                                self.current_run.test_results[i] = retry_result
                                break
                        
                        # Update statistics
                        if result.status == TestStatus.FAILED:
                            self.current_run.failed_tests -= 1
                        elif result.status == TestStatus.ERROR:
                            self.current_run.error_tests -= 1
                        
                        self.current_run.passed_tests += 1
                        logger.info(f"Test {test_name} passed on retry {retry_count}")
                    else:
                        failed_tests.append(result)
                        logger.warning(f"Test {test_name} still failed on retry {retry_count}")
    
    def get_test_runs(self) -> List[TestRunResult]:
        """Get all test run results."""
        return self.test_runs.copy()
    
    def get_latest_run(self) -> Optional[TestRunResult]:
        """Get the most recent test run."""
        return self.test_runs[-1] if self.test_runs else None
    
    def get_run_statistics(self) -> Dict[str, Any]:
        """Get statistics across all test runs."""
        if not self.test_runs:
            return {}
        
        total_runs = len(self.test_runs)
        total_tests = sum(run.total_tests for run in self.test_runs)
        total_passed = sum(run.passed_tests for run in self.test_runs)
        total_failed = sum(run.failed_tests for run in self.test_runs)
        total_skipped = sum(run.skipped_tests for run in self.test_runs)
        total_errors = sum(run.error_tests for run in self.test_runs)
        
        return {
            'total_runs': total_runs,
            'total_tests': total_tests,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_skipped': total_skipped,
            'total_errors': total_errors,
            'overall_success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0,
            'average_tests_per_run': total_tests / total_runs if total_runs > 0 else 0,
            'latest_run': self.test_runs[-1].get_summary() if self.test_runs else None
        }
    
    def export_results(self, file_path: str, format: str = "json", 
                      run_index: Optional[int] = None) -> bool:
        """Export test results to file."""
        try:
            if run_index is not None:
                if 0 <= run_index < len(self.test_runs):
                    result = self.test_runs[run_index]
                else:
                    raise ValueError(f"Invalid run index: {run_index}")
            else:
                # Export latest run
                result = self.get_latest_run()
                if not result:
                    raise ValueError("No test runs available")
            
            return result.export_to_file(file_path, format)
            
        except Exception as e:
            logger.error(f"Failed to export results: {e}")
            return False
    
    def export_all_results(self, directory: str, format: str = "json") -> bool:
        """Export all test run results to a directory."""
        try:
            output_dir = Path(directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Export summary
            summary = self.get_run_statistics()
            summary_file = output_dir / f"test_summary.{format}"
            
            if format.lower() == "json":
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
            elif format.lower() == "yaml":
                with open(summary_file, 'w', encoding='utf-8') as f:
                    yaml.dump(summary, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            # Export individual runs
            for i, run in enumerate(self.test_runs):
                run_file = output_dir / f"run_{i:03d}_{run.suite_name}.{format}"
                run.export_to_file(str(run_file), format)
            
            logger.info(f"Exported all results to {directory}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export all results: {e}")
            return False
    
    def clear_results(self):
        """Clear all test run results."""
        self.test_runs.clear()
        self.current_run = None
        logger.info("Cleared all test run results")
    
    def set_progress_callback(self, callback: Callable[[str, TestResult], None]):
        """Set callback for test progress updates."""
        self.progress_callback = callback
    
    def set_results_callback(self, callback: Callable[[TestRunResult], None]):
        """Set callback for test run completion."""
        self.results_callback = callback
    
    def pause(self):
        """Pause test execution."""
        self.pause_requested = True
        logger.info("Test execution paused")
    
    def resume(self):
        """Resume test execution."""
        self.pause_requested = False
        logger.info("Test execution resumed")
    
    def stop(self):
        """Stop test execution."""
        self.stop_requested = True
        logger.info("Test execution stopped")
    
    def is_running(self) -> bool:
        """Check if tests are currently running."""
        return self.current_run is not None and not self.stop_requested
    
    def is_paused(self) -> bool:
        """Check if test execution is paused."""
        return self.pause_requested






