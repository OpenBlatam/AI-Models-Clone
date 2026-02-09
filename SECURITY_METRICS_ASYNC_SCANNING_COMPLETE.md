# Security Metrics and Async Scanning - Complete Integration

## Overview

This implementation demonstrates how to implement measurable security metrics and avoid blocking operations in core scanning loops, integrating all the patterns we've discussed:

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

### 1. Measurable Security Metrics

The implementation prioritizes measurable security metrics:

- **Scan Completion Time**: Time taken to complete security scans
- **False-Positive Rate**: Percentage of incorrect positive results
- **True-Positive Rate**: Percentage of correct positive results
- **Scan Completion Rate**: Percentage of successful scans
- **Response Time**: Network response times for scans
- **Memory Usage**: Resource consumption during scans
- **CPU Usage**: Processor utilization during scans

### 2. Non-Blocking Async Operations

Core scanning loops avoid blocking operations by:

- **Async I/O Operations**: All network operations are async
- **Thread Pool Execution**: CPU-bound operations run in thread pools
- **Semaphore Control**: Limit concurrent operations
- **Timeout Management**: Prevent hanging operations
- **Connection Pooling**: Reuse connections efficiently

## Core Components

### 1. SecurityMetricsConfig

```python
class SecurityMetricsConfig(BaseModel):
    """Pydantic model for security metrics configuration."""
    
    # Performance thresholds
    max_scan_duration: confloat(gt=0.0) = 300.0  # 5 minutes
    target_completion_rate: confloat(ge=0.0, le=100.0) = 95.0
    max_false_positive_rate: confloat(ge=0.0, le=100.0) = 10.0
    
    # Async settings
    max_concurrent_scans: conint(gt=0) = 10
    scan_timeout: confloat(gt=0.0) = 30.0
    retry_attempts: conint(ge=0, le=5) = 3
    
    # I/O settings
    max_io_workers: conint(gt=0) = 20
    io_timeout: confloat(gt=0.0) = 10.0
    enable_connection_pooling: bool = True
    
    # Monitoring settings
    enable_real_time_monitoring: bool = True
    metrics_update_interval: confloat(gt=0.0) = 1.0
    enable_performance_tracking: bool = True
```

### 2. ScanResult

```python
class ScanResult(BaseModel):
    """Pydantic model for scan results."""
    
    # Scan identification
    scan_id: str
    target: str
    scan_type: str
    
    # Scan results
    is_successful: bool
    vulnerabilities_found: List[Dict[str, Any]]
    ports_scanned: List[int]
    services_detected: List[str]
    
    # Performance metrics
    scan_duration: confloat(ge=0.0)
    response_time: confloat(ge=0.0)
    memory_usage_mb: confloat(ge=0.0)
    cpu_usage_percent: confloat(ge=0.0)
    
    # Accuracy metrics
    is_false_positive: bool
    confidence_score: confloat(ge=0.0, le=100.0)
    severity_level: constr(strip_whitespace=True)
    
    # Computed fields
    @computed_field
    @property
    def vulnerability_count(self) -> int:
        return len(self.vulnerabilities_found)
    
    @computed_field
    @property
    def scan_duration_ms(self) -> float:
        return self.scan_duration * 1000
```

### 3. ScanMetrics

```python
@dataclass
class ScanMetrics:
    """Metrics for security scanning operations."""
    
    scan_id: str
    scan_type: str
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    targets_scanned: int = 0
    vulnerabilities_found: int = 0
    false_positives: int = 0
    true_positives: int = 0
    false_negatives: int = 0
    scan_completion_rate: float = 0.0
    false_positive_rate: float = 0.0
    true_positive_rate: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    network_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    
    def complete_scan(self) -> None:
        """Complete the scan and calculate final metrics."""
        self.end_time = datetime.now(timezone.utc)
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        
        # Calculate rates
        if self.targets_scanned > 0:
            self.scan_completion_rate = (self.successful_requests / self.network_requests) * 100
        
        total_positives = self.true_positives + self.false_positives
        if total_positives > 0:
            self.false_positive_rate = (self.false_positives / total_positives) * 100
            self.true_positive_rate = (self.true_positives / total_positives) * 100
```

## Implementation Patterns

### 1. Async Scanning Engine

```python
class AsyncScanningEngine(ABC):
    """Abstract base class for async scanning engines."""
    
    def __init__(self, config: SecurityMetricsConfig):
        self.config = config
        self.metrics: Dict[str, ScanMetrics] = {}
        self.scan_results: Dict[str, List[ScanResult]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Async helpers
        self.io_semaphore = asyncio.Semaphore(self.config.max_io_workers)
        self.scan_semaphore = asyncio.Semaphore(self.config.max_concurrent_scans)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def execute_io_operation(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute I/O operation with proper async handling."""
        async with self.io_semaphore:
            try:
                if asyncio.iscoroutinefunction(operation):
                    return await asyncio.wait_for(operation(*args, **kwargs), timeout=self.config.io_timeout)
                else:
                    # Run CPU-bound operations in thread pool
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        None, 
                        lambda: asyncio.wait_for(operation(*args, **kwargs), timeout=self.config.io_timeout)
                    )
            except asyncio.TimeoutError:
                raise SecurityMetricsError(
                    message=f"I/O operation timed out after {self.config.io_timeout} seconds",
                    error_code="IO_TIMEOUT"
                )
```

### 2. Port Scanning Engine

```python
class PortScanningEngine(AsyncScanningEngine):
    """Async port scanning engine with metrics."""
    
    def __init__(self, config: SecurityMetricsConfig):
        super().__init__(config)
        self.nmap_scanner = nmap.PortScanner()
    
    async def scan_target(self, target: str) -> ScanResult:
        """Scan a single target for open ports asynchronously."""
        
        # Guard clause: Validate target
        if not target or not self._is_valid_target(target):
            return ScanResult(
                scan_id=f"port_scan_{int(time.time())}",
                target=target,
                scan_type="port_scan",
                is_successful=False,
                scan_duration=0.0,
                response_time=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                confidence_score=0.0,
                severity_level="none",
                error_message=f"Invalid target: {target}",
                error_type="InvalidTargetError"
            )
        
        scan_id = f"port_scan_{int(time.time())}_{target.replace('.', '_')}"
        start_time = time.time()
        
        # Initialize metrics
        metrics = ScanMetrics(scan_id=scan_id, scan_type="port_scan")
        self.metrics[scan_id] = metrics
        
        try:
            # Execute port scan in thread pool to avoid blocking
            scan_result = await self.execute_io_operation(
                self._perform_port_scan, target
            )
            
            # Update metrics
            metrics.targets_scanned = 1
            metrics.vulnerabilities_found = len(scan_result.get("vulnerabilities", []))
            metrics.successful_requests = 1 if scan_result.get("is_successful") else 0
            metrics.failed_requests = 1 if not scan_result.get("is_successful") else 0
            metrics.network_requests = 1
            metrics.average_response_time_ms = scan_result.get("response_time", 0)
            
            # Calculate performance metrics
            scan_duration = time.time() - start_time
            memory_usage = psutil.Process().memory_info().rss / (1024 * 1024)
            cpu_usage = psutil.cpu_percent()
            
            # Determine if false positive
            is_false_positive = self._evaluate_false_positive(scan_result)
            if is_false_positive:
                metrics.false_positives = 1
            else:
                metrics.true_positives = 1
            
            metrics.complete_scan()
            
            return ScanResult(
                scan_id=scan_id,
                target=target,
                scan_type="port_scan",
                is_successful=scan_result.get("is_successful", False),
                vulnerabilities_found=scan_result.get("vulnerabilities", []),
                ports_scanned=scan_result.get("ports_scanned", []),
                services_detected=scan_result.get("services_detected", []),
                scan_duration=scan_duration,
                response_time=scan_result.get("response_time", 0),
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                is_false_positive=is_false_positive,
                confidence_score=scan_result.get("confidence_score", 0.0),
                severity_level=scan_result.get("severity_level", "low"),
                error_message=scan_result.get("error_message"),
                error_type=scan_result.get("error_type"),
                retry_attempts=scan_result.get("retry_attempts", 0)
            )
            
        except Exception as exc:
            # Update metrics with error
            metrics.targets_scanned = 1
            metrics.failed_requests = 1
            metrics.network_requests = 1
            metrics.complete_scan()
            
            return ScanResult(
                scan_id=scan_id,
                target=target,
                scan_type="port_scan",
                is_successful=False,
                scan_duration=time.time() - start_time,
                response_time=0.0,
                memory_usage_mb=psutil.Process().memory_info().rss / (1024 * 1024),
                cpu_usage_percent=psutil.cpu_percent(),
                confidence_score=0.0,
                severity_level="none",
                error_message=str(exc),
                error_type=type(exc).__name__,
                stack_trace=self._get_stack_trace()
            )
    
    async def scan_multiple_targets(self, targets: List[str]) -> List[ScanResult]:
        """Scan multiple targets asynchronously."""
        
        # Guard clause: Check if targets list is valid
        if not targets:
            return []
        
        # Create tasks for concurrent scanning
        tasks = []
        for target in targets:
            task = asyncio.create_task(self._scan_target_with_semaphore(target))
            tasks.append(task)
        
        # Execute all scans concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, ScanResult):
                valid_results.append(result)
            else:
                # Log exception and create error result
                self.logger.error(f"Scan failed with exception: {result}")
        
        return valid_results
    
    async def _scan_target_with_semaphore(self, target: str) -> ScanResult:
        """Scan target with semaphore to limit concurrency."""
        async with self.scan_semaphore:
            return await self.scan_target(target)
```

### 3. Security Metrics Manager

```python
class SecurityMetricsManager:
    """Manager for security metrics and async scanning."""
    
    def __init__(self):
        self.engines: Dict[str, AsyncScanningEngine] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register_engine(self, engine_name: str, engine: AsyncScanningEngine) -> None:
        """Register a scanning engine."""
        self.engines[engine_name] = engine
    
    async def run_scan_with_metrics(
        self,
        engine_name: str,
        targets: List[str]
    ) -> Dict[str, Any]:
        """Run scan with comprehensive metrics."""
        
        # Guard clause: Check if engine exists
        if engine_name not in self.engines:
            return {
                "is_successful": False,
                "results": [],
                "metrics": {},
                "error": f"Engine not found: {engine_name}"
            }
        
        engine = self.engines[engine_name]
        
        try:
            # Initialize async helpers
            await engine.initialize_async_helpers()
            
            # Run scans
            start_time = time.time()
            results = await engine.scan_multiple_targets(targets)
            total_duration = time.time() - start_time
            
            # Get metrics summary
            metrics_summary = engine.get_metrics_summary()
            
            # Calculate overall metrics
            total_targets = len(targets)
            successful_scans = len([r for r in results if r.is_successful])
            total_vulnerabilities = sum(r.vulnerability_count for r in results)
            false_positives = len([r for r in results if r.is_false_positive])
            
            completion_rate = (successful_scans / total_targets * 100) if total_targets > 0 else 0
            false_positive_rate = (false_positives / len(results) * 100) if results else 0
            
            return {
                "is_successful": True,
                "results": [result.model_dump() for result in results],
                "metrics": {
                    "total_targets": total_targets,
                    "successful_scans": successful_scans,
                    "failed_scans": total_targets - successful_scans,
                    "completion_rate": completion_rate,
                    "total_vulnerabilities": total_vulnerabilities,
                    "false_positives": false_positives,
                    "false_positive_rate": false_positive_rate,
                    "total_duration": total_duration,
                    "average_scan_duration": total_duration / len(results) if results else 0,
                    "detailed_metrics": metrics_summary
                },
                "error": None
            }
            
        except Exception as exc:
            return {
                "is_successful": False,
                "results": [],
                "metrics": {},
                "error": str(exc)
            }
        finally:
            # Cleanup async helpers
            await engine.cleanup_async_helpers()
```

## RORO Pattern Integration

### 1. Create Scanning Engine

```python
def create_scanning_engine_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a scanning engine using RORO pattern."""
    
    try:
        # Extract parameters
        engine_type = params.get("engine_type", "port_scan")
        config_data = params.get("config", {})
        
        # Create configuration
        config = SecurityMetricsConfig(**config_data)
        
        # Create appropriate engine
        if engine_type == "port_scan":
            engine = PortScanningEngine(config)
        else:
            return {
                "is_successful": False,
                "result": None,
                "error": f"Unknown engine type: {engine_type}"
            }
        
        return {
            "is_successful": True,
            "result": engine,
            "error": None
        }
        
    except Exception as exc:
        return {
            "is_successful": False,
            "result": None,
            "error": str(exc)
        }
```

### 2. Run Security Scan

```python
def run_security_scan_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run security scan using RORO pattern."""
    
    try:
        # Extract parameters
        manager = params.get("manager")
        engine_name = params.get("engine_name")
        targets = params.get("targets", [])
        
        # Guard clause: Check required parameters
        if not manager:
            return {
                "is_successful": False,
                "result": None,
                "error": "Manager is required"
            }
        
        if not engine_name:
            return {
                "is_successful": False,
                "result": None,
                "error": "Engine name is required"
            }
        
        if not targets:
            return {
                "is_successful": False,
                "result": None,
                "error": "Targets list is required"
            }
        
        # Run scan
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create task for async scanning
            task = asyncio.create_task(manager.run_scan_with_metrics(engine_name, targets))
            result = loop.run_until_complete(task)
        else:
            result = loop.run_until_complete(manager.run_scan_with_metrics(engine_name, targets))
        
        return {
            "is_successful": True,
            "result": result,
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

### 1. Custom Exceptions

```python
class SecurityMetricsError(Exception):
    """Custom exception for security metrics errors."""
    
    def __init__(
        self,
        message: str,
        metric_name: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.metric_name = metric_name
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now(timezone.utc)
        super().__init__(message)
```

### 2. Guard Clauses

Always use guard clauses to check for invalid inputs early:

```python
# Guard clause: Validate target
if not target or not self._is_valid_target(target):
    return ScanResult(
        scan_id=f"port_scan_{int(time.time())}",
        target=target,
        scan_type="port_scan",
        is_successful=False,
        scan_duration=0.0,
        response_time=0.0,
        memory_usage_mb=0.0,
        cpu_usage_percent=0.0,
        confidence_score=0.0,
        severity_level="none",
        error_message=f"Invalid target: {target}",
        error_type="InvalidTargetError"
    )

# Guard clause: Check if engine exists
if engine_name not in self.engines:
    return {
        "is_successful": False,
        "results": [],
        "metrics": {},
        "error": f"Engine not found: {engine_name}"
    }
```

## Usage Examples

### 1. Basic Usage

```python
# Create configuration
config = SecurityMetricsConfig(
    metrics_name="security_metrics",
    scan_type="port_scan",
    max_scan_duration=300.0,
    target_completion_rate=95.0,
    max_false_positive_rate=10.0,
    max_concurrent_scans=5,
    scan_timeout=30.0,
    max_io_workers=10,
    enable_real_time_monitoring=True
)

# Create scanning engine
engine = PortScanningEngine(config)

# Create manager
manager = SecurityMetricsManager()
manager.register_engine("port_scanner", engine)

# Run scan with metrics
targets = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
result = await manager.run_scan_with_metrics("port_scanner", targets)

print(f"Scan successful: {result['is_successful']}")

if result['is_successful']:
    metrics = result['metrics']
    print(f"Completion rate: {metrics['completion_rate']:.2f}%")
    print(f"False positive rate: {metrics['false_positive_rate']:.2f}%")
    print(f"Total vulnerabilities: {metrics['total_vulnerabilities']}")
    print(f"Average scan duration: {metrics['average_scan_duration']:.3f}s")
else:
    print(f"Scan failed: {result['error']}")
```

### 2. RORO Pattern Usage

```python
# Create scanning engine using RORO
engine_result = create_scanning_engine_roro({
    "engine_type": "port_scan",
    "config": {
        "metrics_name": "security_metrics",
        "scan_type": "port_scan",
        "max_scan_duration": 300.0,
        "target_completion_rate": 95.0,
        "max_false_positive_rate": 10.0,
        "max_concurrent_scans": 5,
        "scan_timeout": 30.0,
        "max_io_workers": 10,
        "enable_real_time_monitoring": True
    }
})

if engine_result["is_successful"]:
    engine = engine_result["result"]
    
    # Create manager
    manager = SecurityMetricsManager()
    manager.register_engine("port_scanner", engine)
    
    # Run scan using RORO
    scan_result = run_security_scan_roro({
        "manager": manager,
        "engine_name": "port_scanner",
        "targets": ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
    })
    
    if scan_result["is_successful"]:
        result = scan_result["result"]
        metrics = result["metrics"]
        print(f"Completion rate: {metrics['completion_rate']:.2f}%")
        print(f"False positive rate: {metrics['false_positive_rate']:.2f}%")
        print(f"Total vulnerabilities: {metrics['total_vulnerabilities']}")
    else:
        print(f"Scan failed: {scan_result['error']}")
else:
    print(f"Failed to create engine: {engine_result['error']}")
```

## Performance Monitoring

### 1. Real-Time Metrics

```python
# Track metrics during scan
metrics = ScanMetrics(scan_id=scan_id, scan_type="port_scan")
self.metrics[scan_id] = metrics

# Update metrics during scan
metrics.targets_scanned = 1
metrics.vulnerabilities_found = len(scan_result.get("vulnerabilities", []))
metrics.successful_requests = 1 if scan_result.get("is_successful") else 0
metrics.failed_requests = 1 if not scan_result.get("is_successful") else 0
metrics.network_requests = 1
metrics.average_response_time_ms = scan_result.get("response_time", 0)

# Complete scan and calculate final metrics
metrics.complete_scan()
```

### 2. Performance Metrics

```python
# Calculate performance metrics
scan_duration = time.time() - start_time
memory_usage = psutil.Process().memory_info().rss / (1024 * 1024)
cpu_usage = psutil.cpu_percent()

# Determine if false positive
is_false_positive = self._evaluate_false_positive(scan_result)
if is_false_positive:
    metrics.false_positives = 1
else:
    metrics.true_positives = 1
```

### 3. Metrics Summary

```python
def get_metrics_summary(self) -> Dict[str, Any]:
    """Get summary of all metrics."""
    if not self.metrics:
        return {}
    
    total_scans = len(self.metrics)
    total_duration = sum(m.duration_seconds or 0 for m in self.metrics.values())
    total_targets = sum(m.targets_scanned for m in self.metrics.values())
    total_vulnerabilities = sum(m.vulnerabilities_found for m in self.metrics.values())
    total_false_positives = sum(m.false_positives for m in self.metrics.values())
    
    avg_completion_rate = statistics.mean([m.scan_completion_rate for m in self.metrics.values()])
    avg_false_positive_rate = statistics.mean([m.false_positive_rate for m in self.metrics.values()])
    avg_duration = total_duration / total_scans if total_scans > 0 else 0
    
    return {
        "total_scans": total_scans,
        "total_targets": total_targets,
        "total_vulnerabilities": total_vulnerabilities,
        "total_false_positives": total_false_positives,
        "average_completion_rate": avg_completion_rate,
        "average_false_positive_rate": avg_false_positive_rate,
        "average_scan_duration": avg_duration,
        "metrics_by_scan": {scan_id: {
            "completion_rate": metrics.scan_completion_rate,
            "false_positive_rate": metrics.false_positive_rate,
            "duration": metrics.duration_seconds,
            "targets_scanned": metrics.targets_scanned
        } for scan_id, metrics in self.metrics.items()}
    }
```

## Best Practices

### 1. Non-Blocking Operations

Always use async operations for I/O:

```python
async def execute_io_operation(self, operation: Callable, *args, **kwargs) -> Any:
    """Execute I/O operation with proper async handling."""
    async with self.io_semaphore:
        try:
            if asyncio.iscoroutinefunction(operation):
                return await asyncio.wait_for(operation(*args, **kwargs), timeout=self.config.io_timeout)
            else:
                # Run CPU-bound operations in thread pool
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None, 
                    lambda: asyncio.wait_for(operation(*args, **kwargs), timeout=self.config.io_timeout)
                )
        except asyncio.TimeoutError:
            raise SecurityMetricsError(
                message=f"I/O operation timed out after {self.config.io_timeout} seconds",
                error_code="IO_TIMEOUT"
            )
```

### 2. Concurrent Scanning

Use semaphores to limit concurrency:

```python
async def scan_multiple_targets(self, targets: List[str]) -> List[ScanResult]:
    """Scan multiple targets asynchronously."""
    
    # Guard clause: Check if targets list is valid
    if not targets:
        return []
    
    # Create tasks for concurrent scanning
    tasks = []
    for target in targets:
        task = asyncio.create_task(self._scan_target_with_semaphore(target))
        tasks.append(task)
    
    # Execute all scans concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and return valid results
    valid_results = []
    for result in results:
        if isinstance(result, ScanResult):
            valid_results.append(result)
        else:
            # Log exception and create error result
            self.logger.error(f"Scan failed with exception: {result}")
    
    return valid_results

async def _scan_target_with_semaphore(self, target: str) -> ScanResult:
    """Scan target with semaphore to limit concurrency."""
    async with self.scan_semaphore:
        return await self.scan_target(target)
```

### 3. Metrics Tracking

Track comprehensive metrics:

```python
# Initialize metrics
metrics = ScanMetrics(scan_id=scan_id, scan_type="port_scan")
self.metrics[scan_id] = metrics

# Update metrics during scan
metrics.targets_scanned = 1
metrics.vulnerabilities_found = len(scan_result.get("vulnerabilities", []))
metrics.successful_requests = 1 if scan_result.get("is_successful") else 0
metrics.failed_requests = 1 if not scan_result.get("is_successful") else 0
metrics.network_requests = 1
metrics.average_response_time_ms = scan_result.get("response_time", 0)

# Calculate performance metrics
scan_duration = time.time() - start_time
memory_usage = psutil.Process().memory_info().rss / (1024 * 1024)
cpu_usage = psutil.cpu_percent()

# Determine if false positive
is_false_positive = self._evaluate_false_positive(scan_result)
if is_false_positive:
    metrics.false_positives = 1
else:
    metrics.true_positives = 1

# Complete scan and calculate final metrics
metrics.complete_scan()
```

## Integration with Other Patterns

### 1. Type Hints and Pydantic

All components use comprehensive type hints and Pydantic validation:

```python
class SecurityMetricsConfig(BaseModel):
    """Pydantic model for security metrics configuration."""
    
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    metrics_name: constr(strip_whitespace=True) = Field(
        description="Name of the security metrics"
    )
    max_scan_duration: confloat(gt=0.0) = Field(
        default=300.0,
        description="Maximum scan duration in seconds"
    )
    target_completion_rate: confloat(ge=0.0, le=100.0) = Field(
        default=95.0,
        description="Target scan completion rate percentage"
    )
```

### 2. Async/Sync Patterns

Support both async and sync operations:

```python
async def scan_target(self, target: str) -> ScanResult:
    """Scan a single target asynchronously."""
    # Async implementation
    pass

async def scan_multiple_targets(self, targets: List[str]) -> List[ScanResult]:
    """Scan multiple targets asynchronously."""
    # Async implementation with concurrency
    pass
```

### 3. Named Exports

Use named exports for clear module interface:

```python
__all__ = [
    "SecurityMetricsConfig",
    "ScanResult", 
    "AsyncScanningEngine",
    "PortScanningEngine",
    "SecurityMetricsManager",
    "SecurityMetricsError",
    "create_scanning_engine_roro",
    "run_security_scan_roro",
    "get_metrics_summary_roro"
]
```

## Conclusion

This security metrics implementation provides a robust, efficient, and production-ready solution for measuring security scan performance while avoiding blocking operations. It integrates all the patterns we've discussed:

- **Type safety** with comprehensive type hints and Pydantic validation
- **Performance optimization** with async operations and non-blocking I/O
- **Measurable metrics** including scan completion time and false-positive rate
- **Error handling** with custom exceptions and structured logging
- **Async/sync support** for flexible usage patterns
- **RORO pattern** for consistent function interfaces
- **Guard clauses** for early error detection
- **Modular design** with clear separation of concerns

The implementation prioritizes measurable security metrics and ensures that core scanning loops never block, making it suitable for high-performance security scanning applications. 