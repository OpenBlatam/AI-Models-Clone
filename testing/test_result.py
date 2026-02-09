"""
Test Result for Instagram Captions API v10.0
Detailed test results and reporting.
"""
import json
import yaml
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass, field
import traceback

class TestStatus(Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    RUNNING = "running"
    PENDING = "pending"

@dataclass
class TestResult:
    """Represents the result of a single test."""
    
    test_name: str
    test_class: Optional[str] = None
    test_module: Optional[str] = None
    status: TestStatus = TestStatus.PENDING
    execution_time: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Test details
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    priority: str = "normal"  # low, normal, high, critical
    
    # Results
    message: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    
    # Additional data
    metadata: Dict[str, Any] = field(default_factory=dict)
    assertions: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Union[int, float]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.start_time is None:
            self.start_time = datetime.now()
    
    def start(self):
        """Mark test as started."""
        self.status = TestStatus.RUNNING
        self.start_time = datetime.now()
    
    def finish(self, status: TestStatus, message: Optional[str] = None,
               error: Optional[Exception] = None, execution_time: Optional[float] = None):
        """Mark test as finished."""
        self.status = status
        self.end_time = datetime.now()
        
        if execution_time is not None:
            self.execution_time = execution_time
        elif self.start_time:
            self.execution_time = (self.end_time - self.start_time).total_seconds()
        
        if message:
            self.message = message
        
        if error:
            self.error_type = type(error).__name__
            self.error_message = str(error)
            self.traceback = traceback.format_exc()
    
    def add_assertion(self, assertion_type: str, expected: Any, actual: Any, 
                      passed: bool, message: Optional[str] = None):
        """Add an assertion result."""
        assertion = {
            'type': assertion_type,
            'expected': expected,
            'actual': actual,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.assertions.append(assertion)
    
    def add_performance_metric(self, metric_name: str, value: Union[int, float]):
        """Add a performance metric."""
        self.performance_metrics[metric_name] = value
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to the test result."""
        self.metadata[key] = value
    
    def is_successful(self) -> bool:
        """Check if the test was successful."""
        return self.status == TestStatus.PASSED
    
    def is_failure(self) -> bool:
        """Check if the test failed."""
        return self.status in [TestStatus.FAILED, TestStatus.ERROR]
    
    def is_skipped(self) -> bool:
        """Check if the test was skipped."""
        return self.status == TestStatus.SKIPPED
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the test result."""
        return {
            'test_name': self.test_name,
            'test_class': self.test_class,
            'test_module': self.test_module,
            'status': self.status.value,
            'execution_time': self.execution_time,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'description': self.description,
            'tags': self.tags,
            'priority': self.priority,
            'message': self.message,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'assertions_count': len(self.assertions),
            'passed_assertions': len([a for a in self.assertions if a['passed']]),
            'failed_assertions': len([a for a in self.assertions if not a['passed']]),
            'performance_metrics': self.performance_metrics,
            'metadata': self.metadata
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'test_name': self.test_name,
            'test_class': self.test_class,
            'test_module': self.test_module,
            'status': self.status.value,
            'execution_time': self.execution_time,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'description': self.description,
            'tags': self.tags,
            'priority': self.priority,
            'message': self.message,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'traceback': self.traceback,
            'assertions': self.assertions,
            'performance_metrics': self.performance_metrics,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str, indent=2)
    
    def to_yaml(self) -> str:
        """Convert to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, allow_unicode=True, indent=2)
    
    def export_to_file(self, file_path: str, format: str = "json") -> bool:
        """Export test result to file."""
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
            print(f"Error exporting test result: {e}")
            return False
    
    def get_formatted_output(self, include_traceback: bool = True) -> str:
        """Get formatted output for display."""
        lines = []
        
        # Header
        status_symbol = {
            TestStatus.PASSED: "✓",
            TestStatus.FAILED: "✗",
            TestStatus.ERROR: "⚠",
            TestStatus.SKIPPED: "○",
            TestStatus.RUNNING: "⟳",
            TestStatus.PENDING: "·"
        }.get(self.status, "?")
        
        lines.append(f"{status_symbol} {self.test_name}")
        
        if self.description:
            lines.append(f"  Description: {self.description}")
        
        # Status and timing
        lines.append(f"  Status: {self.status.value.upper()}")
        if self.execution_time > 0:
            lines.append(f"  Execution Time: {self.execution_time:.3f}s")
        
        # Message
        if self.message:
            lines.append(f"  Message: {self.message}")
        
        # Error details
        if self.error_message:
            lines.append(f"  Error: {self.error_type}: {self.error_message}")
            if include_traceback and self.traceback:
                lines.append("  Traceback:")
                for line in self.traceback.split('\n'):
                    if line.strip():
                        lines.append(f"    {line}")
        
        # Assertions summary
        if self.assertions:
            passed = len([a for a in self.assertions if a['passed']])
            total = len(self.assertions)
            lines.append(f"  Assertions: {passed}/{total} passed")
        
        # Performance metrics
        if self.performance_metrics:
            lines.append("  Performance Metrics:")
            for metric, value in self.performance_metrics.items():
                lines.append(f"    {metric}: {value}")
        
        # Tags
        if self.tags:
            lines.append(f"  Tags: {', '.join(self.tags)}")
        
        return '\n'.join(lines)
    
    def __str__(self) -> str:
        """String representation."""
        return f"TestResult({self.test_name}, {self.status.value}, {self.execution_time:.3f}s)"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"TestResult(test_name='{self.test_name}', status={self.status.value}, execution_time={self.execution_time})"






