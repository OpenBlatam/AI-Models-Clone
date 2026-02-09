#!/usr/bin/env python3
"""
Advanced Test Framework - Infrastructure Layer
============================================

Enterprise-grade testing framework with comprehensive test capabilities
including unit tests, integration tests, performance tests, contract tests,
and mutation testing.
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, Union, Callable
import threading
import statistics
import traceback
import inspect
import random
import string
from contextlib import asynccontextmanager
import pytest
import pytest_asyncio
from unittest.mock import Mock, MagicMock, patch, AsyncMock


class TestType(Enum):
    """Types of tests."""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    CONTRACT = "contract"
    MUTATION = "mutation"
    E2E = "e2e"
    SECURITY = "security"


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"


class TestPriority(Enum):
    """Test priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TestResult:
    """Test execution result."""
    
    test_id: str
    test_name: str
    test_type: TestType
    status: TestStatus
    duration_ms: float
    start_time: datetime
    end_time: datetime
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    coverage_percentage: Optional[float] = None


@dataclass
class TestSuite:
    """Test suite configuration."""
    
    name: str
    description: Optional[str] = None
    test_type: TestType
    priority: TestPriority = TestPriority.MEDIUM
    timeout_seconds: int = 300
    retry_count: int = 0
    parallel_execution: bool = False
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    enabled: bool = True


class TestDataGenerator:
    """Advanced test data generation utilities."""
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """Generate a random string."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_random_email() -> str:
        """Generate a random email address."""
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        domain = ''.join(random.choices(string.ascii_lowercase, k=6))
        return f"{username}@{domain}.com"
    
    @staticmethod
    def generate_random_post_data() -> Dict[str, Any]:
        """Generate random LinkedIn post data."""
        return {
            'topic': f"Test Topic {TestDataGenerator.generate_random_string(5)}",
            'content': f"This is a test post content with {TestDataGenerator.generate_random_string(20)}",
            'tone': random.choice(['professional', 'casual', 'friendly', 'formal']),
            'length': random.choice(['short', 'medium', 'long']),
            'hashtags': [f"#{TestDataGenerator.generate_random_string(5)}" for _ in range(3)],
            'call_to_action': f"Test CTA {TestDataGenerator.generate_random_string(10)}",
            'optimization_strategy': random.choice(['quantum', 'neuromorphic', 'federated'])
        }
    
    @staticmethod
    def generate_user_data() -> Dict[str, Any]:
        """Generate random user data."""
        return {
            'user_id': str(uuid.uuid4()),
            'username': TestDataGenerator.generate_random_string(8),
            'email': TestDataGenerator.generate_random_email(),
            'roles': random.choice([['user'], ['editor'], ['admin']]),
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def generate_performance_test_data(size: int = 100) -> List[Dict[str, Any]]:
        """Generate data for performance testing."""
        return [TestDataGenerator.generate_random_post_data() for _ in range(size)]


class TestCoverageTracker:
    """Test coverage tracking and analysis."""
    
    def __init__(self):
        self._covered_lines: Set[str] = set()
        self._total_lines: Set[str] = set()
        self._logger = logging.getLogger(__name__)
    
    def start_tracking(self, module_path: str) -> None:
        """Start tracking coverage for a module."""
        # In a real implementation, this would integrate with coverage.py
        self._logger.info(f"Started coverage tracking for {module_path}")
    
    def record_line(self, file_path: str, line_number: int) -> None:
        """Record a covered line."""
        self._covered_lines.add(f"{file_path}:{line_number}")
    
    def get_coverage_percentage(self) -> float:
        """Get current coverage percentage."""
        if not self._total_lines:
            return 0.0
        
        return len(self._covered_lines) / len(self._total_lines) * 100
    
    def get_coverage_report(self) -> Dict[str, Any]:
        """Get detailed coverage report."""
        return {
            'covered_lines': len(self._covered_lines),
            'total_lines': len(self._total_lines),
            'coverage_percentage': self.get_coverage_percentage(),
            'covered_files': len(set(line.split(':')[0] for line in self._covered_lines))
        }


class PerformanceTestRunner:
    """Advanced performance testing capabilities."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._metrics: List[Dict[str, float]] = []
    
    async def run_performance_test(self, test_func: Callable, 
                                 iterations: int = 100,
                                 warmup_iterations: int = 10) -> Dict[str, Any]:
        """Run a performance test with warmup and multiple iterations."""
        
        # Warmup phase
        self._logger.info(f"Running {warmup_iterations} warmup iterations...")
        for _ in range(warmup_iterations):
            await test_func()
        
        # Actual test phase
        self._logger.info(f"Running {iterations} test iterations...")
        durations = []
        
        for i in range(iterations):
            start_time = time.time()
            await test_func()
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            durations.append(duration)
            
            if (i + 1) % 10 == 0:
                self._logger.info(f"Completed {i + 1}/{iterations} iterations")
        
        # Calculate statistics
        stats = {
            'iterations': iterations,
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
            'avg_duration_ms': statistics.mean(durations),
            'median_duration_ms': statistics.median(durations),
            'std_deviation_ms': statistics.stdev(durations) if len(durations) > 1 else 0,
            'p95_duration_ms': sorted(durations)[int(len(durations) * 0.95)],
            'p99_duration_ms': sorted(durations)[int(len(durations) * 0.99)]
        }
        
        self._metrics.append(stats)
        return stats
    
    def get_performance_baseline(self) -> Dict[str, float]:
        """Get performance baseline from previous runs."""
        if not self._metrics:
            return {}
        
        # Calculate baseline from recent metrics
        recent_metrics = self._metrics[-10:]  # Last 10 runs
        
        baseline = {}
        for key in ['avg_duration_ms', 'p95_duration_ms', 'p99_duration_ms']:
            values = [m[key] for m in recent_metrics if key in m]
            if values:
                baseline[key] = statistics.mean(values)
        
        return baseline
    
    def check_performance_regression(self, current_stats: Dict[str, float],
                                   threshold_percentage: float = 20.0) -> Dict[str, Any]:
        """Check for performance regression."""
        baseline = self.get_performance_baseline()
        
        if not baseline:
            return {'regression_detected': False, 'message': 'No baseline available'}
        
        regression_detected = False
        regressions = []
        
        for metric in ['avg_duration_ms', 'p95_duration_ms', 'p99_duration_ms']:
            if metric in baseline and metric in current_stats:
                baseline_value = baseline[metric]
                current_value = current_stats[metric]
                percentage_change = ((current_value - baseline_value) / baseline_value) * 100
                
                if percentage_change > threshold_percentage:
                    regression_detected = True
                    regressions.append({
                        'metric': metric,
                        'baseline': baseline_value,
                        'current': current_value,
                        'percentage_change': percentage_change
                    })
        
        return {
            'regression_detected': regression_detected,
            'regressions': regressions,
            'threshold_percentage': threshold_percentage
        }


class ContractTestRunner:
    """Contract testing for API compatibility."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._contracts: Dict[str, Dict[str, Any]] = {}
    
    def define_contract(self, contract_name: str, 
                       request_schema: Dict[str, Any],
                       response_schema: Dict[str, Any]) -> None:
        """Define an API contract."""
        self._contracts[contract_name] = {
            'request_schema': request_schema,
            'response_schema': response_schema,
            'created_at': datetime.utcnow().isoformat()
        }
        self._logger.info(f"Defined contract: {contract_name}")
    
    async def test_contract(self, contract_name: str, 
                           request_data: Dict[str, Any],
                           response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test if request/response matches the contract."""
        if contract_name not in self._contracts:
            raise ValueError(f"Contract not found: {contract_name}")
        
        contract = self._contracts[contract_name]
        
        # Validate request schema
        request_valid = self._validate_schema(request_data, contract['request_schema'])
        
        # Validate response schema
        response_valid = self._validate_schema(response_data, contract['response_schema'])
        
        return {
            'contract_name': contract_name,
            'request_valid': request_valid,
            'response_valid': response_valid,
            'overall_valid': request_valid and response_valid,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Simple schema validation (in production, use JSON Schema)."""
        try:
            # Basic validation - check required fields
            required_fields = schema.get('required', [])
            for field in required_fields:
                if field not in data:
                    return False
            
            # Check field types
            for field, field_schema in schema.get('properties', {}).items():
                if field in data:
                    expected_type = field_schema.get('type')
                    if expected_type and not isinstance(data[field], self._get_python_type(expected_type)):
                        return False
            
            return True
        except Exception as e:
            self._logger.error(f"Schema validation error: {e}")
            return False
    
    def _get_python_type(self, json_type: str) -> Type:
        """Convert JSON schema type to Python type."""
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict
        }
        return type_mapping.get(json_type, object)


class MutationTestRunner:
    """Mutation testing for code quality."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._mutations: List[Dict[str, Any]] = []
    
    def create_mutation(self, original_code: str, mutation_type: str) -> str:
        """Create a mutation of the original code."""
        if mutation_type == "change_operator":
            # Change comparison operators
            mutations = {
                '==': '!=',
                '!=': '==',
                '<': '>=',
                '>': '<=',
                '<=': '>',
                '>=': '<'
            }
            for old_op, new_op in mutations.items():
                if old_op in original_code:
                    return original_code.replace(old_op, new_op)
        
        elif mutation_type == "change_constant":
            # Change numeric constants
            import re
            numbers = re.findall(r'\b\d+\b', original_code)
            if numbers:
                number = numbers[0]
                new_number = str(int(number) + 1)
                return original_code.replace(number, new_number, 1)
        
        elif mutation_type == "remove_statement":
            # Remove lines (simplified)
            lines = original_code.split('\n')
            if len(lines) > 1:
                return '\n'.join(lines[1:])  # Remove first line
        
        return original_code
    
    async def run_mutation_test(self, test_func: Callable, 
                               original_code: str,
                               mutation_types: List[str] = None) -> Dict[str, Any]:
        """Run mutation testing."""
        if mutation_types is None:
            mutation_types = ["change_operator", "change_constant", "remove_statement"]
        
        results = {
            'total_mutations': 0,
            'killed_mutations': 0,
            'survived_mutations': 0,
            'mutation_score': 0.0,
            'mutations': []
        }
        
        for mutation_type in mutation_types:
            mutated_code = self.create_mutation(original_code, mutation_type)
            
            if mutated_code != original_code:
                results['total_mutations'] += 1
                
                try:
                    # Test with original code
                    original_result = await test_func()
                    
                    # Test with mutated code (simulated)
                    # In a real implementation, you would actually apply the mutation
                    mutated_result = await test_func()
                    
                    # Check if mutation was killed (tests failed)
                    if original_result != mutated_result:
                        results['killed_mutations'] += 1
                        status = "killed"
                    else:
                        results['survived_mutations'] += 1
                        status = "survived"
                    
                    results['mutations'].append({
                        'type': mutation_type,
                        'status': status,
                        'original_code': original_code,
                        'mutated_code': mutated_code
                    })
                
                except Exception as e:
                    results['killed_mutations'] += 1
                    results['mutations'].append({
                        'type': mutation_type,
                        'status': 'killed',
                        'error': str(e)
                    })
        
        # Calculate mutation score
        if results['total_mutations'] > 0:
            results['mutation_score'] = (results['killed_mutations'] / results['total_mutations']) * 100
        
        return results


class AdvancedTestFramework:
    """
    Advanced test framework with comprehensive testing capabilities.
    
    Features:
    - Unit, integration, performance, contract, and mutation testing
    - Test data generation
    - Coverage tracking
    - Performance regression detection
    - Contract validation
    - Mutation testing
    - Parallel test execution
    - Test result aggregation and reporting
    """
    
    def __init__(self):
        self.coverage_tracker = TestCoverageTracker()
        self.performance_runner = PerformanceTestRunner()
        self.contract_runner = ContractTestRunner()
        self.mutation_runner = MutationTestRunner()
        self.data_generator = TestDataGenerator()
        
        self._test_results: List[TestResult] = []
        self._test_suites: Dict[str, TestSuite] = {}
        self._logger = logging.getLogger(__name__)
        self._lock = threading.RLock()
    
    def register_test_suite(self, suite: TestSuite) -> None:
        """Register a test suite."""
        with self._lock:
            self._test_suites[suite.name] = suite
            self._logger.info(f"Registered test suite: {suite.name}")
    
    async def run_unit_test(self, test_func: Callable, test_name: str,
                           timeout_seconds: int = 30) -> TestResult:
        """Run a unit test."""
        test_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Start coverage tracking
            self.coverage_tracker.start_tracking(test_name)
            
            # Run test with timeout
            if asyncio.iscoroutinefunction(test_func):
                result = await asyncio.wait_for(test_func(), timeout=timeout_seconds)
            else:
                result = test_func()
            
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=TestType.UNIT,
                status=TestStatus.PASSED,
                duration_ms=duration_ms,
                start_time=start_time,
                end_time=end_time,
                coverage_percentage=self.coverage_tracker.get_coverage_percentage()
            )
        
        except asyncio.TimeoutError:
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=TestType.UNIT,
                status=TestStatus.TIMEOUT,
                duration_ms=duration_ms,
                start_time=start_time,
                end_time=end_time,
                error_message="Test timed out"
            )
        
        except Exception as e:
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=TestType.UNIT,
                status=TestStatus.FAILED,
                duration_ms=duration_ms,
                start_time=start_time,
                end_time=end_time,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
    
    async def run_integration_test(self, test_func: Callable, test_name: str,
                                 dependencies: List[str] = None) -> TestResult:
        """Run an integration test."""
        test_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Check dependencies
            if dependencies:
                for dep in dependencies:
                    if not await self._check_dependency(dep):
                        raise ValueError(f"Dependency not available: {dep}")
            
            # Run test
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=TestType.INTEGRATION,
                status=TestStatus.PASSED,
                duration_ms=duration_ms,
                start_time=start_time,
                end_time=end_time
            )
        
        except Exception as e:
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=TestType.INTEGRATION,
                status=TestStatus.FAILED,
                duration_ms=duration_ms,
                start_time=start_time,
                end_time=end_time,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
    
    async def run_performance_test(self, test_func: Callable, test_name: str,
                                 iterations: int = 100) -> TestResult:
        """Run a performance test."""
        test_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Run performance test
            performance_stats = await self.performance_runner.run_performance_test(
                test_func, iterations
            )
            
            # Check for performance regression
            regression_check = self.performance_runner.check_performance_regression(
                performance_stats
            )
            
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            status = TestStatus.PASSED
            error_message = None
            
            if regression_check['regression_detected']:
                status = TestStatus.FAILED
                error_message = f"Performance regression detected: {regression_check['regressions']}"
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=TestType.PERFORMANCE,
                status=status,
                duration_ms=duration_ms,
                start_time=start_time,
                end_time=end_time,
                error_message=error_message,
                performance_metrics=performance_stats,
                metadata={'regression_check': regression_check}
            )
        
        except Exception as e:
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=TestType.PERFORMANCE,
                status=TestStatus.FAILED,
                duration_ms=duration_ms,
                start_time=start_time,
                end_time=end_time,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
    
    async def run_contract_test(self, contract_name: str, test_func: Callable,
                               test_name: str) -> TestResult:
        """Run a contract test."""
        test_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Run test function to get request/response data
            if asyncio.iscoroutinefunction(test_func):
                request_data, response_data = await test_func()
            else:
                request_data, response_data = test_func()
            
            # Test contract
            contract_result = await self.contract_runner.test_contract(
                contract_name, request_data, response_data
            )
            
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            status = TestStatus.PASSED if contract_result['overall_valid'] else TestStatus.FAILED
            error_message = None
            
            if not contract_result['overall_valid']:
                error_message = f"Contract validation failed: {contract_result}"
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=TestType.CONTRACT,
                status=status,
                duration_ms=duration_ms,
                start_time=start_time,
                end_time=end_time,
                error_message=error_message,
                metadata={'contract_result': contract_result}
            )
        
        except Exception as e:
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=TestType.CONTRACT,
                status=TestStatus.FAILED,
                duration_ms=duration_ms,
                start_time=start_time,
                end_time=end_time,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
    
    async def run_mutation_test(self, test_func: Callable, test_name: str,
                               original_code: str) -> TestResult:
        """Run a mutation test."""
        test_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Run mutation testing
            mutation_results = await self.mutation_runner.run_mutation_test(
                test_func, original_code
            )
            
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Determine status based on mutation score
            status = TestStatus.PASSED
            error_message = None
            
            if mutation_results['mutation_score'] < 80.0:
                status = TestStatus.FAILED
                error_message = f"Low mutation score: {mutation_results['mutation_score']}%"
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=TestType.MUTATION,
                status=status,
                duration_ms=duration_ms,
                start_time=start_time,
                end_time=end_time,
                error_message=error_message,
                metadata={'mutation_results': mutation_results}
            )
        
        except Exception as e:
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=TestType.MUTATION,
                status=TestStatus.FAILED,
                duration_ms=duration_ms,
                start_time=start_time,
                end_time=end_time,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
    
    async def run_test_suite(self, suite_name: str) -> List[TestResult]:
        """Run a complete test suite."""
        if suite_name not in self._test_suites:
            raise ValueError(f"Test suite not found: {suite_name}")
        
        suite = self._test_suites[suite_name]
        results = []
        
        self._logger.info(f"Running test suite: {suite_name}")
        
        # Run tests based on suite configuration
        if suite.parallel_execution:
            # Run tests in parallel
            tasks = []
            # In a real implementation, you would create actual test tasks here
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Run tests sequentially
            # In a real implementation, you would run actual tests here
            pass
        
        return results
    
    def get_test_results(self, test_type: Optional[TestType] = None,
                        status: Optional[TestStatus] = None) -> List[TestResult]:
        """Get test results with optional filtering."""
        with self._lock:
            results = self._test_results.copy()
            
            if test_type:
                results = [r for r in results if r.test_type == test_type]
            
            if status:
                results = [r for r in results if r.status == status]
            
            return results
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get comprehensive test summary."""
        with self._lock:
            total_tests = len(self._test_results)
            passed_tests = len([r for r in self._test_results if r.status == TestStatus.PASSED])
            failed_tests = len([r for r in self._test_results if r.status == TestStatus.FAILED])
            skipped_tests = len([r for r in self._test_results if r.status == TestStatus.SKIPPED])
            
            avg_duration = statistics.mean([r.duration_ms for r in self._test_results]) if self._test_results else 0
            
            return {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'skipped_tests': skipped_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'average_duration_ms': avg_duration,
                'coverage_percentage': self.coverage_tracker.get_coverage_percentage(),
                'test_suites': len(self._test_suites)
            }
    
    async def _check_dependency(self, dependency: str) -> bool:
        """Check if a dependency is available."""
        # In a real implementation, this would check actual dependencies
        # For now, return True
        return True


# Global test framework instance
test_framework = AdvancedTestFramework()


# Decorators for easy test creation
def unit_test(test_name: str, timeout_seconds: int = 30):
    """Decorator to create a unit test."""
    def decorator(func):
        async def wrapper():
            return await test_framework.run_unit_test(func, test_name, timeout_seconds)
        return wrapper
    return decorator


def integration_test(test_name: str, dependencies: List[str] = None):
    """Decorator to create an integration test."""
    def decorator(func):
        async def wrapper():
            return await test_framework.run_integration_test(func, test_name, dependencies)
        return wrapper
    return decorator


def performance_test(test_name: str, iterations: int = 100):
    """Decorator to create a performance test."""
    def decorator(func):
        async def wrapper():
            return await test_framework.run_performance_test(func, test_name, iterations)
        return wrapper
    return decorator


def contract_test(contract_name: str, test_name: str):
    """Decorator to create a contract test."""
    def decorator(func):
        async def wrapper():
            return await test_framework.run_contract_test(contract_name, func, test_name)
        return wrapper
    return decorator


def mutation_test(test_name: str, original_code: str):
    """Decorator to create a mutation test."""
    def decorator(func):
        async def wrapper():
            return await test_framework.run_mutation_test(func, test_name, original_code)
        return wrapper
    return decorator 