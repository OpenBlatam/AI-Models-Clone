# Automated Testing with Edge Cases - Complete Integration

## Overview

This implementation demonstrates how to implement comprehensive automated testing with pytest and pytest-asyncio, including edge case testing and network layer mocking, integrating all the patterns we've discussed:

- **Type hints and Pydantic validation**
- **Async/sync patterns**
- **RORO pattern**
- **Named exports**
- **Error handling and validation**
- **Guard clauses and early returns**
- **Structured logging**
- **Custom exceptions**
- **Secure coding practices**

## Key Concepts

### 1. Edge Case Testing

Edge case testing ensures robust handling of:

- **Invalid Inputs**: Null values, empty strings, wrong types, malformed data
- **Boundary Conditions**: Minimum/maximum values, edge of valid ranges
- **Error Conditions**: Network failures, timeouts, permission errors
- **Concurrent Operations**: Race conditions, resource contention

### 2. Network Layer Mocking

Network mocking provides:

- **Controlled Testing**: Predictable network behavior
- **Error Simulation**: Network failures, timeouts, errors
- **Performance Testing**: Response time simulation
- **Isolation**: Tests independent of external services

### 3. Async Testing with pytest-asyncio

Async testing enables:

- **Concurrent Testing**: Multiple async operations
- **Real-world Scenarios**: Network operations, I/O testing
- **Performance Validation**: Async operation timing
- **Resource Management**: Memory and CPU monitoring

## Core Components

### 1. TestConfiguration

```python
class TestConfiguration(BaseModel):
    """Pydantic model for test configuration."""
    
    # Test identification
    test_suite_name: constr(strip_whitespace=True)
    test_environment: constr(strip_whitespace=True)
    
    # Test behavior
    enable_edge_case_testing: bool = True
    enable_network_mocking: bool = True
    enable_async_testing: bool = True
    enable_performance_testing: bool = True
    
    # Edge case settings
    test_invalid_inputs: bool = True
    test_boundary_conditions: bool = True
    test_error_conditions: bool = True
    test_concurrent_operations: bool = True
    
    # Mock settings
    mock_network_timeout: confloat(gt=0.0) = 5.0
    mock_network_error_rate: confloat(ge=0.0, le=1.0) = 0.1
    mock_response_delay: confloat(ge=0.0) = 0.1
    
    # Performance settings
    performance_threshold_ms: confloat(gt=0.0) = 1000.0
    memory_threshold_mb: confloat(gt=0.0) = 100.0
    cpu_threshold_percent: confloat(gt=0.0, le=100.0) = 50.0
```

### 2. TestResult

```python
@dataclass
class TestResult:
    """Result of a test execution."""
    
    test_name: str
    test_suite: str
    is_successful: bool
    execution_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None
    test_data: Dict[str, Any] = field(default_factory=dict)
    edge_case_type: Optional[str] = None
    mock_network_calls: int = 0
    mock_network_errors: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### 3. EdgeCaseGenerator

```python
class EdgeCaseGenerator:
    """Generator for edge case test data."""
    
    @staticmethod
    def generate_invalid_inputs() -> List[Dict[str, Any]]:
        """Generate invalid input test cases."""
        return [
            {"input": None, "expected_error": "ValueError"},
            {"input": "", "expected_error": "ValueError"},
            {"input": "   ", "expected_error": "ValueError"},
            {"input": 0, "expected_error": "TypeError"},
            {"input": -1, "expected_error": "ValueError"},
            {"input": "invalid_ip", "expected_error": "ValueError"},
            {"input": "999.999.999.999", "expected_error": "ValueError"},
            {"input": "192.168.1", "expected_error": "ValueError"},
            {"input": "192.168.1.256", "expected_error": "ValueError"},
            {"input": "fe80::1%lo0", "expected_error": "ValueError"},  # IPv6 with scope
            {"input": "2001:db8::1/128", "expected_error": "ValueError"},  # IPv6 with CIDR
        ]
    
    @staticmethod
    def generate_boundary_conditions() -> List[Dict[str, Any]]:
        """Generate boundary condition test cases."""
        return [
            {"input": "0.0.0.0", "description": "Minimum valid IP"},
            {"input": "255.255.255.255", "description": "Maximum valid IP"},
            {"input": "127.0.0.1", "description": "Localhost"},
            {"input": "::1", "description": "IPv6 localhost"},
            {"input": "192.168.1.1", "description": "Private network"},
            {"input": "10.0.0.1", "description": "Private network"},
            {"input": "172.16.0.1", "description": "Private network"},
            {"input": "8.8.8.8", "description": "Public DNS"},
            {"input": "1.1.1.1", "description": "Public DNS"},
        ]
    
    @staticmethod
    def generate_error_conditions() -> List[Dict[str, Any]]:
        """Generate error condition test cases."""
        return [
            {"error_type": "ConnectionError", "description": "Network connection failed"},
            {"error_type": "TimeoutError", "description": "Network timeout"},
            {"error_type": "PermissionError", "description": "Permission denied"},
            {"error_type": "ValueError", "description": "Invalid value"},
            {"error_type": "TypeError", "description": "Invalid type"},
            {"error_type": "KeyError", "description": "Missing key"},
            {"error_type": "IndexError", "description": "Index out of range"},
            {"error_type": "AttributeError", "description": "Missing attribute"},
            {"error_type": "ImportError", "description": "Import failed"},
            {"error_type": "OSError", "description": "Operating system error"},
        ]
    
    @staticmethod
    def generate_concurrent_scenarios() -> List[Dict[str, Any]]:
        """Generate concurrent operation test scenarios."""
        return [
            {"scenario": "multiple_scans_same_target", "concurrency": 5},
            {"scenario": "multiple_targets_single_engine", "concurrency": 10},
            {"scenario": "mixed_scan_types", "concurrency": 3},
            {"scenario": "high_load_testing", "concurrency": 20},
            {"scenario": "resource_contention", "concurrency": 15},
        ]
```

## Implementation Patterns

### 1. Network Mock Manager

```python
class NetworkMockManager:
    """Manager for network layer mocking."""
    
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.mock_calls = 0
        self.mock_errors = 0
        self.mock_responses = {}
    
    def create_network_mock(self) -> AsyncMock:
        """Create a mock network client."""
        mock_client = AsyncMock()
        
        async def mock_request(*args, **kwargs):
            self.mock_calls += 1
            
            # Simulate network delay
            await asyncio.sleep(self.config.mock_response_delay)
            
            # Simulate network errors
            if self.mock_errors / max(self.mock_calls, 1) < self.config.mock_network_error_rate:
                self.mock_errors += 1
                raise ConnectionError("Mock network error")
            
            # Return mock response
            return Mock(
                status=200,
                json=AsyncMock(return_value={"success": True}),
                text=AsyncMock(return_value="Mock response")
            )
        
        mock_client.request = mock_request
        mock_client.get = mock_request
        mock_client.post = mock_request
        mock_client.put = mock_request
        mock_client.delete = mock_request
        
        return mock_client
    
    def create_siem_mock(self) -> AsyncMock:
        """Create a mock SIEM client."""
        mock_siem = AsyncMock()
        
        async def mock_send_logs(events: List[Any]) -> None:
            self.mock_calls += 1
            
            # Simulate network delay
            await asyncio.sleep(self.config.mock_response_delay)
            
            # Simulate network errors
            if self.mock_errors / max(self.mock_calls, 1) < self.config.mock_network_error_rate:
                self.mock_errors += 1
                raise ConnectionError("Mock SIEM error")
            
            # Store mock response
            self.mock_responses[f"siem_{self.mock_calls}"] = {
                "events_count": len(events),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        mock_siem.send_logs = mock_send_logs
        return mock_siem
```

### 2. Test Suite Manager

```python
class TestSuiteManager:
    """Manager for test suite execution."""
    
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.test_results: List[TestResult] = []
        self.edge_case_generator = EdgeCaseGenerator()
        self.network_mock_manager = NetworkMockManager(config)
    
    async def run_edge_case_tests(self) -> List[TestResult]:
        """Run edge case tests."""
        results = []
        
        if self.config.test_invalid_inputs:
            results.extend(await self._test_invalid_inputs())
        
        if self.config.test_boundary_conditions:
            results.extend(await self._test_boundary_conditions())
        
        if self.config.test_error_conditions:
            results.extend(await self._test_error_conditions())
        
        if self.config.test_concurrent_operations:
            results.extend(await self._test_concurrent_operations())
        
        return results
    
    async def _test_invalid_inputs(self) -> List[TestResult]:
        """Test with invalid inputs."""
        results = []
        test_cases = self.edge_case_generator.generate_invalid_inputs()
        
        for i, test_case in enumerate(test_cases):
            test_name = f"test_invalid_input_{i}"
            start_time = time.time()
            
            try:
                # Test with invalid input
                with pytest.raises(Exception) as exc_info:
                    await self._execute_test_with_input(test_case["input"])
                
                # Verify expected error
                assert str(exc_info.type.__name__) == test_case["expected_error"]
                
                results.append(TestResult(
                    test_name=test_name,
                    test_suite="invalid_inputs",
                    is_successful=True,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    memory_usage_mb=self._get_memory_usage(),
                    cpu_usage_percent=self._get_cpu_usage(),
                    test_data=test_case,
                    edge_case_type="invalid_input"
                ))
                
            except Exception as exc:
                results.append(TestResult(
                    test_name=test_name,
                    test_suite="invalid_inputs",
                    is_successful=False,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    memory_usage_mb=self._get_memory_usage(),
                    cpu_usage_percent=self._get_cpu_usage(),
                    error_message=str(exc),
                    error_type=type(exc).__name__,
                    test_data=test_case,
                    edge_case_type="invalid_input"
                ))
        
        return results
```

### 3. Pytest Test Classes

```python
class TestSecurityMetrics:
    """Test class for security metrics functionality."""
    
    @pytest.fixture
    def test_config(self):
        """Fixture for test configuration."""
        return TestConfiguration(
            test_suite_name="security_metrics_tests",
            test_environment="unit",
            enable_edge_case_testing=True,
            enable_network_mocking=True,
            enable_async_testing=True,
            enable_performance_testing=True
        )
    
    @pytest.fixture
    def security_metrics_config(self):
        """Fixture for security metrics configuration."""
        return SecurityMetricsConfig(
            metrics_name="test_metrics",
            scan_type="port_scan",
            max_scan_duration=300.0,
            target_completion_rate=95.0,
            max_false_positive_rate=10.0,
            max_concurrent_scans=5,
            scan_timeout=30.0,
            max_io_workers=10,
            enable_real_time_monitoring=True
        )
    
    @pytest.fixture
    def port_scanning_engine(self, security_metrics_config):
        """Fixture for port scanning engine."""
        return PortScanningEngine(security_metrics_config)
    
    @pytest_asyncio.fixture
    async def mock_network_client(self, test_config):
        """Fixture for mock network client."""
        network_mock_manager = NetworkMockManager(test_config)
        return network_mock_manager.create_network_mock()
    
    @pytest.mark.asyncio
    async def test_security_metrics_config_validation(self, test_config):
        """Test security metrics configuration validation."""
        # Test valid configuration
        config = SecurityMetricsConfig(
            metrics_name="test_metrics",
            scan_type="port_scan"
        )
        assert config.metrics_name == "test_metrics"
        assert config.scan_type == "port_scan"
        
        # Test invalid scan type
        with pytest.raises(ValueError):
            SecurityMetricsConfig(
                metrics_name="test_metrics",
                scan_type="invalid_scan_type"
            )
    
    @pytest.mark.asyncio
    async def test_scan_target_with_valid_input(self, port_scanning_engine):
        """Test scanning target with valid input."""
        target = "192.168.1.1"
        result = await port_scanning_engine.scan_target(target)
        
        assert result is not None
        assert isinstance(result, ScanResult)
        assert result.target == target
        assert result.scan_type == "port_scan"
    
    @pytest.mark.asyncio
    async def test_scan_target_with_invalid_input(self, port_scanning_engine):
        """Test scanning target with invalid input."""
        target = "invalid_ip"
        result = await port_scanning_engine.scan_target(target)
        
        assert result is not None
        assert isinstance(result, ScanResult)
        assert result.is_successful is False
        assert result.error_message is not None
    
    @pytest.mark.asyncio
    async def test_network_mocking(self, mock_network_client):
        """Test network layer mocking."""
        # Test successful request
        response = await mock_network_client.get("https://example.com")
        assert response.status == 200
        
        # Test error handling
        with patch.object(mock_network_client, 'get', side_effect=ConnectionError("Mock error")):
            with pytest.raises(ConnectionError):
                await mock_network_client.get("https://example.com")
```

## RORO Pattern Integration

### 1. Create Test Suite Manager

```python
def create_test_suite_manager_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a test suite manager using RORO pattern."""
    
    try:
        # Extract parameters
        config_data = params.get("config", {})
        
        # Create configuration
        config = TestConfiguration(**config_data)
        
        # Create test suite manager
        manager = TestSuiteManager(config)
        
        return {
            "is_successful": True,
            "result": manager,
            "error": None
        }
        
    except Exception as exc:
        return {
            "is_successful": False,
            "result": None,
            "error": str(exc)
        }
```

### 2. Run Edge Case Tests

```python
def run_edge_case_tests_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run edge case tests using RORO pattern."""
    
    try:
        # Extract parameters
        manager = params.get("manager")
        
        # Guard clause: Check required parameters
        if not manager:
            return {
                "is_successful": False,
                "result": None,
                "error": "Manager is required"
            }
        
        # Run tests
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create task for async testing
            task = asyncio.create_task(manager.run_edge_case_tests())
            results = loop.run_until_complete(task)
        else:
            results = loop.run_until_complete(manager.run_edge_case_tests())
        
        return {
            "is_successful": True,
            "result": [result.__dict__ for result in results],
            "error": None
        }
        
    except Exception as exc:
        return {
            "is_successful": False,
            "result": None,
            "error": str(exc)
        }
```

### 3. Get Test Statistics

```python
def get_test_statistics_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get test statistics using RORO pattern."""
    
    try:
        # Extract parameters
        manager = params.get("manager")
        
        # Guard clause: Check required parameters
        if not manager:
            return {
                "is_successful": False,
                "result": None,
                "error": "Manager is required"
            }
        
        # Calculate statistics
        total_tests = len(manager.test_results)
        successful_tests = len([r for r in manager.test_results if r.is_successful])
        failed_tests = total_tests - successful_tests
        
        avg_execution_time = sum(r.execution_time_ms for r in manager.test_results) / max(total_tests, 1)
        avg_memory_usage = sum(r.memory_usage_mb for r in manager.test_results) / max(total_tests, 1)
        avg_cpu_usage = sum(r.cpu_usage_percent for r in manager.test_results) / max(total_tests, 1)
        
        # Get network mock statistics
        network_stats = manager.network_mock_manager.get_mock_statistics()
        
        return {
            "is_successful": True,
            "result": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "average_execution_time_ms": avg_execution_time,
                "average_memory_usage_mb": avg_memory_usage,
                "average_cpu_usage_percent": avg_cpu_usage,
                "network_mock_statistics": network_stats
            },
            "error": None
        }
        
    except Exception as exc:
        return {
            "is_successful": False,
            "result": None,
            "error": str(exc)
        }
```

## Error Handling and Validation

### 1. Guard Clauses

Always use guard clauses to check for invalid inputs early:

```python
# Guard clause: Check required parameters
if not manager:
    return {
        "is_successful": False,
        "result": None,
        "error": "Manager is required"
    }

# Guard clause: Check if test configuration is valid
if not config_data:
    return {
        "is_successful": False,
        "result": None,
        "error": "Configuration data is required"
    }
```

### 2. Exception Handling

Comprehensive exception handling in tests:

```python
try:
    # Test with invalid input
    with pytest.raises(Exception) as exc_info:
        await self._execute_test_with_input(test_case["input"])
    
    # Verify expected error
    assert str(exc_info.type.__name__) == test_case["expected_error"]
    
    results.append(TestResult(
        test_name=test_name,
        test_suite="invalid_inputs",
        is_successful=True,
        execution_time_ms=(time.time() - start_time) * 1000,
        memory_usage_mb=self._get_memory_usage(),
        cpu_usage_percent=self._get_cpu_usage(),
        test_data=test_case,
        edge_case_type="invalid_input"
    ))
    
except Exception as exc:
    results.append(TestResult(
        test_name=test_name,
        test_suite="invalid_inputs",
        is_successful=False,
        execution_time_ms=(time.time() - start_time) * 1000,
        memory_usage_mb=self._get_memory_usage(),
        cpu_usage_percent=self._get_cpu_usage(),
        error_message=str(exc),
        error_type=type(exc).__name__,
        test_data=test_case,
        edge_case_type="invalid_input"
    ))
```

## Usage Examples

### 1. Basic Usage

```python
# Create test configuration
config = TestConfiguration(
    test_suite_name="comprehensive_tests",
    test_environment="unit",
    enable_edge_case_testing=True,
    enable_network_mocking=True,
    enable_async_testing=True,
    enable_performance_testing=True,
    test_invalid_inputs=True,
    test_boundary_conditions=True,
    test_error_conditions=True,
    test_concurrent_operations=True,
    mock_network_timeout=5.0,
    mock_network_error_rate=0.1,
    mock_response_delay=0.1,
    performance_threshold_ms=1000.0,
    memory_threshold_mb=100.0,
    cpu_threshold_percent=50.0
)

# Create test suite manager
manager = TestSuiteManager(config)

# Run edge case tests
results = await manager.run_edge_case_tests()

# Print results
print(f"Total tests run: {len(results)}")
successful_tests = len([r for r in results if r.is_successful])
print(f"Successful tests: {successful_tests}")
print(f"Failed tests: {len(results) - successful_tests}")

# Print network mock statistics
network_stats = manager.network_mock_manager.get_mock_statistics()
print(f"Network mock calls: {network_stats['total_calls']}")
print(f"Network mock errors: {network_stats['total_errors']}")
print(f"Network error rate: {network_stats['error_rate']:.2%}")
```

### 2. RORO Pattern Usage

```python
# Create test suite manager using RORO
manager_result = create_test_suite_manager_roro({
    "config": {
        "test_suite_name": "comprehensive_tests",
        "test_environment": "unit",
        "enable_edge_case_testing": True,
        "enable_network_mocking": True,
        "enable_async_testing": True,
        "enable_performance_testing": True,
        "test_invalid_inputs": True,
        "test_boundary_conditions": True,
        "test_error_conditions": True,
        "test_concurrent_operations": True,
        "mock_network_timeout": 5.0,
        "mock_network_error_rate": 0.1,
        "mock_response_delay": 0.1,
        "performance_threshold_ms": 1000.0,
        "memory_threshold_mb": 100.0,
        "cpu_threshold_percent": 50.0
    }
})

if manager_result["is_successful"]:
    manager = manager_result["result"]
    
    # Run edge case tests using RORO
    test_result = run_edge_case_tests_roro({
        "manager": manager
    })
    
    if test_result["is_successful"]:
        results = test_result["result"]
        print(f"Tests completed: {len(results)}")
        
        # Get test statistics using RORO
        stats_result = get_test_statistics_roro({
            "manager": manager
        })
        
        if stats_result["is_successful"]:
            stats = stats_result["result"]
            print(f"Success rate: {stats['success_rate']:.2f}%")
            print(f"Average execution time: {stats['average_execution_time_ms']:.2f}ms")
            print(f"Average memory usage: {stats['average_memory_usage_mb']:.2f}MB")
            print(f"Average CPU usage: {stats['average_cpu_usage_percent']:.2f}%")
        else:
            print(f"Failed to get statistics: {stats_result['error']}")
    else:
        print(f"Tests failed: {test_result['error']}")
else:
    print(f"Failed to create manager: {manager_result['error']}")
```

### 3. Pytest Test Execution

```bash
# Run all tests
pytest automated_testing_edge_cases.py -v

# Run specific test class
pytest automated_testing_edge_cases.py::TestSecurityMetrics -v

# Run specific test method
pytest automated_testing_edge_cases.py::TestSecurityMetrics::test_scan_target_with_valid_input -v

# Run with coverage
pytest automated_testing_edge_cases.py --cov=. --cov-report=html

# Run with performance profiling
pytest automated_testing_edge_cases.py --durations=10
```

## Best Practices

### 1. Edge Case Testing

Always test edge cases:

```python
# Test invalid inputs
test_cases = [
    {"input": None, "expected_error": "ValueError"},
    {"input": "", "expected_error": "ValueError"},
    {"input": "   ", "expected_error": "ValueError"},
    {"input": 0, "expected_error": "TypeError"},
    {"input": -1, "expected_error": "ValueError"},
    {"input": "invalid_ip", "expected_error": "ValueError"},
]

for test_case in test_cases:
    with pytest.raises(Exception) as exc_info:
        await execute_test_with_input(test_case["input"])
    assert str(exc_info.type.__name__) == test_case["expected_error"]
```

### 2. Network Mocking

Use comprehensive network mocking:

```python
# Create network mock
mock_client = AsyncMock()

async def mock_request(*args, **kwargs):
    # Simulate network delay
    await asyncio.sleep(0.1)
    
    # Simulate network errors
    if random.random() < 0.1:  # 10% error rate
        raise ConnectionError("Mock network error")
    
    # Return mock response
    return Mock(
        status=200,
        json=AsyncMock(return_value={"success": True}),
        text=AsyncMock(return_value="Mock response")
    )

mock_client.request = mock_request
```

### 3. Async Testing

Use pytest-asyncio for async testing:

```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test async operation."""
    result = await async_function()
    assert result is not None
    assert result["status"] == "success"

@pytest_asyncio.fixture
async def mock_async_client():
    """Fixture for mock async client."""
    return AsyncMock()
```

### 4. Performance Testing

Monitor performance metrics:

```python
def _get_memory_usage(self) -> float:
    """Get current memory usage in MB."""
    try:
        import psutil
        return psutil.Process().memory_info().rss / (1024 * 1024)
    except ImportError:
        return 0.0

def _get_cpu_usage(self) -> float:
    """Get current CPU usage percentage."""
    try:
        import psutil
        return psutil.cpu_percent()
    except ImportError:
        return 0.0
```

## Integration with Other Patterns

### 1. Type Hints and Pydantic

All components use comprehensive type hints and Pydantic validation:

```python
class TestConfiguration(BaseModel):
    """Pydantic model for test configuration."""
    
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    test_suite_name: constr(strip_whitespace=True) = Field(
        description="Name of the test suite"
    )
    test_environment: constr(strip_whitespace=True) = Field(
        description="Test environment (unit, integration, e2e)"
    )
    enable_edge_case_testing: bool = Field(
        default=True,
        description="Enable edge case testing"
    )
```

### 2. Async/Sync Patterns

Support both async and sync testing:

```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test async operation."""
    result = await async_function()
    assert result is not None

def test_sync_operation():
    """Test sync operation."""
    result = sync_function()
    assert result is not None
```

### 3. Named Exports

Use named exports for clear module interface:

```python
__all__ = [
    "TestConfiguration",
    "TestResult", 
    "EdgeCaseGenerator",
    "NetworkMockManager",
    "TestSuiteManager",
    "TestSecurityMetrics",
    "TestStructuredLogging",
    "TestEdgeCases",
    "create_test_suite_manager_roro",
    "run_edge_case_tests_roro",
    "get_test_statistics_roro"
]
```

## Conclusion

This automated testing implementation provides a robust, comprehensive, and production-ready solution for testing with edge cases and network mocking. It integrates all the patterns we've discussed:

- **Type safety** with comprehensive type hints and Pydantic validation
- **Edge case testing** with invalid inputs, boundary conditions, and error conditions
- **Network mocking** with controlled behavior and error simulation
- **Async testing** with pytest-asyncio for real-world scenarios
- **Performance monitoring** with memory and CPU tracking
- **Error handling** with comprehensive exception handling
- **Async/sync support** for flexible testing patterns
- **RORO pattern** for consistent function interfaces
- **Guard clauses** for early error detection
- **Modular design** with clear separation of concerns

The implementation is ready for production use and provides comprehensive testing capabilities for complex systems. 