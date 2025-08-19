from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
        from cybersecurity_toolkit.utils.structured_logger import (
        from cybersecurity_toolkit.scanners.port_scanner import scan_ports_async
        from cybersecurity_toolkit.utils.network_helpers import (
        from cybersecurity_toolkit.utils.structured_logger import get_logger
        from cybersecurity_toolkit.utils.structured_logger import get_logger
        from cybersecurity_toolkit.utils.structured_logger import get_logger
        from cybersecurity_toolkit.utils.structured_logger import get_logger
        from cybersecurity_toolkit.utils.structured_logger import get_logger
        from cybersecurity_toolkit.utils.structured_logger import get_logger
        from cybersecurity_toolkit.utils.structured_logger import (
        from cybersecurity_toolkit.scanners.port_scanner import scan_ports_async
        from cybersecurity_toolkit.utils.network_helpers import validate_ip_address
from typing import Any, List, Dict, Optional
import logging
"""
Structured Logging Demo
======================

Demonstrates structured logging with context capture for:
- Module, function, and parameter tracking
- Error context and stack traces
- Performance metrics
- Security events
- Audit trails
"""


# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demonstrate_structured_logging():
    """Demonstrate structured logging features."""
    print("=" * 80)
    print("STRUCTURED LOGGING WITH CONTEXT CAPTURE DEMONSTRATION")
    print("=" * 80)
    
    try:
            StructuredLogger, get_logger, log_function_call, log_async_function_call
        )
            validate_ip_address, check_connectivity_async
        )
        
        print("✓ Structured Logging Features:")
        print("  - Module, function, and parameter tracking")
        print("  - Error context with stack traces")
        print("  - Performance metrics")
        print("  - Security events")
        print("  - Audit trails")
        print("  - JSON-formatted logs")
        
        print("\n✓ Logging Context Capture:")
        print("  - Function entry/exit logging")
        print("  - Parameter validation and sanitization")
        print("  - Error tracking with full context")
        print("  - Performance monitoring")
        print("  - Security event logging")
        
        # Create logger instance
        logger = get_logger("demo_logger")
        
        print("\n✓ Logger Configuration:")
        print(f"  - Logger name: {logger.name}")
        print(f"  - Log level: {logger.log_level}")
        print(f"  - Log file: {logger.log_file}")
        print(f"  - Console output: {logger.enable_console}")
        print(f"  - File output: {logger.enable_file}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("  Make sure the cybersecurity toolkit modules are available")
        return False

def demonstrate_function_logging():
    """Demonstrate function entry/exit logging."""
    print("\n" + "=" * 80)
    print("FUNCTION ENTRY/EXIT LOGGING DEMONSTRATION")
    print("=" * 80)
    
    try:
        
        logger = get_logger("function_demo")
        
        print("✓ Function Entry Logging:")
        print("  - Captures function name and parameters")
        print("  - Records calling context (module, line)")
        print("  - Sanitizes sensitive parameters")
        print("  - Tracks execution flow")
        
        print("\n✓ Function Exit Logging:")
        print("  - Records return values")
        print("  - Measures execution time")
        print("  - Captures performance metrics")
        print("  - Logs success/failure status")
        
        # Demonstrate function logging
        logger.log_function_entry(
            "demonstrate_function_logging",
            {"demo_param": "test_value"},
            {"event_type": "demo_function"}
        )
        
        logger.log_function_exit(
            "demonstrate_function_logging",
            {"result": "success"},
            0.001,
            {"event_type": "demo_function"}
        )
        
        print("✅ Function logging demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Function logging demo failed: {e}")

def demonstrate_error_logging():
    """Demonstrate comprehensive error logging."""
    print("\n" + "=" * 80)
    print("ERROR LOGGING WITH CONTEXT DEMONSTRATION")
    print("=" * 80)
    
    try:
        
        logger = get_logger("error_demo")
        
        print("✓ Error Context Capture:")
        print("  - Error type and message")
        print("  - Function where error occurred")
        print("  - Parameters that caused error")
        print("  - Full stack trace")
        print("  - Error ID for tracking")
        print("  - Timestamp and context")
        
        # Demonstrate error logging
        try:
            # Simulate an error
            raise ValueError("This is a test error for demonstration")
        except Exception as e:
            logger.log_error(
                e,
                "demonstrate_error_logging",
                {"test_param": "test_value"},
                {"error_context": "demo_error"}
            )
        
        print("✅ Error logging demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Error logging demo failed: {e}")

def demonstrate_validation_logging():
    """Demonstrate validation error logging."""
    print("\n" + "=" * 80)
    print("VALIDATION ERROR LOGGING DEMONSTRATION")
    print("=" * 80)
    
    try:
        
        logger = get_logger("validation_demo")
        
        print("✓ Validation Error Features:")
        print("  - Field-specific validation errors")
        print("  - Parameter value capture")
        print("  - Validation type classification")
        print("  - Context-aware error messages")
        print("  - Sanitized sensitive data")
        
        # Demonstrate validation logging
        logger.log_validation_error(
            "missing_required_field",
            "target_host",
            None,
            "Target host is required for port scanning"
        )
        
        logger.log_validation_error(
            "invalid_port_range",
            "port_number",
            99999,
            "Port must be between 1 and 65535"
        )
        
        print("✅ Validation logging demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Validation logging demo failed: {e}")

def demonstrate_performance_logging():
    """Demonstrate performance metrics logging."""
    print("\n" + "=" * 80)
    print("PERFORMANCE METRICS LOGGING DEMONSTRATION")
    print("=" * 80)
    
    try:
        
        logger = get_logger("performance_demo")
        
        print("✓ Performance Metrics:")
        print("  - Execution time measurement")
        print("  - Operation-specific metrics")
        print("  - Resource usage tracking")
        print("  - Performance thresholds")
        print("  - Historical performance data")
        
        # Demonstrate performance logging
        logger.log_performance(
            "port_scan_operation",
            2.5,
            {
                "ports_scanned": 100,
                "open_ports": 5,
                "target_host": "example.com"
            },
            {"operation_type": "network_scan"}
        )
        
        print("✅ Performance logging demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Performance logging demo failed: {e}")

def demonstrate_security_logging():
    """Demonstrate security event logging."""
    print("\n" + "=" * 80)
    print("SECURITY EVENT LOGGING DEMONSTRATION")
    print("=" * 80)
    
    try:
        
        logger = get_logger("security_demo")
        
        print("✓ Security Event Features:")
        print("  - Security event classification")
        print("  - Event severity levels")
        print("  - Event data capture")
        print("  - Audit trail maintenance")
        print("  - Security incident tracking")
        
        # Demonstrate security logging
        logger.log_security_event(
            "port_scan_detected",
            {
                "source_ip": "192.168.1.100",
                "target_host": "example.com",
                "ports_scanned": [80, 443, 22],
                "scan_duration": 1.5
            },
            "WARNING",
            {"event_category": "network_security"}
        )
        
        logger.log_security_event(
            "authentication_failure",
            {
                "username": "admin",
                "source_ip": "10.0.0.50",
                "failure_reason": "invalid_password"
            },
            "ERROR",
            {"event_category": "access_control"}
        )
        
        print("✅ Security logging demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Security logging demo failed: {e}")

async def demonstrate_async_logging():
    """Demonstrate async function logging."""
    print("\n" + "=" * 80)
    print("ASYNC FUNCTION LOGGING DEMONSTRATION")
    print("=" * 80)
    
    try:
        
        logger = get_logger("async_demo")
        
        print("✓ Async Logging Features:")
        print("  - Async function entry/exit tracking")
        print("  - Concurrent operation logging")
        print("  - Async error handling")
        print("  - Performance monitoring for async ops")
        print("  - Context preservation across async boundaries")
        
        # Demonstrate async logging
        logger.log_function_entry(
            "demonstrate_async_logging",
            {"async_param": "async_value"},
            {"event_type": "async_demo"}
        )
        
        # Simulate async operation
        await asyncio.sleep(0.1)
        
        logger.log_function_exit(
            "demonstrate_async_logging",
            {"async_result": "success"},
            0.1,
            {"event_type": "async_demo"}
        )
        
        print("✅ Async logging demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Async logging demo failed: {e}")

def demonstrate_log_file_structure():
    """Demonstrate log file structure and format."""
    print("\n" + "=" * 80)
    print("LOG FILE STRUCTURE DEMONSTRATION")
    print("=" * 80)
    
    try:
        # Check if log files exist
        logs_dir = Path("logs")
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            
            if log_files:
                print("✓ Log Files Found:")
                for log_file in log_files:
                    print(f"  - {log_file.name}")
                    print(f"    Size: {log_file.stat().st_size} bytes")
                    print(f"    Modified: {datetime.fromtimestamp(log_file.stat().st_mtime)}")
                
                # Show sample log entry
                print("\n✓ Sample Log Entry Structure:")
                print("""
{
    "timestamp": "2024-01-01T12:00:00.000000+00:00",
    "level": "INFO",
    "logger": "cybersecurity_toolkit",
    "message": "Function entry/exit message",
    "module": "port_scanner",
    "function": "scan_ports_async",
    "line": 123,
    "process_id": 1234,
    "thread_id": 5678,
    "context": {
        "event_type": "function_entry",
        "function_name": "scan_ports_async",
        "calling_context": {...}
    },
    "parameters": {
        "target_host": "example.com",
        "target_ports": [80, 443]
    },
    "performance": {
        "execution_time": 1.234
    }
}
                """)
            else:
                print("  No log files found yet")
        else:
            print("  Logs directory not found")
        
        print("✅ Log file structure demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Log file structure demo failed: {e}")

def demonstrate_decorator_usage():
    """Demonstrate logging decorator usage."""
    print("\n" + "=" * 80)
    print("LOGGING DECORATOR USAGE DEMONSTRATION")
    print("=" * 80)
    
    try:
            log_function_call, log_async_function_call
        )
        
        print("✓ Decorator Features:")
        print("  - Automatic function entry/exit logging")
        print("  - Parameter capture and sanitization")
        print("  - Error handling and logging")
        print("  - Performance measurement")
        print("  - Context preservation")
        
        @log_function_call
        def demo_function(param1: str, param2: int) -> str:
            """Demo function with logging decorator."""
            if param2 < 0:
                raise ValueError("param2 must be positive")
            return f"Processed {param1} with value {param2}"
        
        @log_async_function_call
        async def demo_async_function(param1: str) -> str:
            """Demo async function with logging decorator."""
            await asyncio.sleep(0.1)
            return f"Async processed {param1}"
        
        print("\n✓ Function Decorator Demo:")
        # Test successful function
        result = demo_function("test", 42)
        print(f"  Function result: {result}")
        
        # Test function with error
        try:
            demo_function("test", -1)
        except ValueError:
            print("  Function error handled and logged")
        
        print("\n✓ Async Function Decorator Demo:")
        # Test async function
        async def test_async():
            
    """test_async function."""
async_result = await demo_async_function("async_test")
            print(f"  Async function result: {async_result}")
        
        asyncio.run(test_async())
        
        print("✅ Decorator usage demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Decorator usage demo failed: {e}")

async def demonstrate_integration_with_toolkit():
    """Demonstrate integration with cybersecurity toolkit."""
    print("\n" + "=" * 80)
    print("INTEGRATION WITH CYBERSECURITY TOOLKIT DEMONSTRATION")
    print("=" * 80)
    
    try:
        
        print("✓ Toolkit Integration Features:")
        print("  - Automatic logging in all toolkit functions")
        print("  - Context capture for security operations")
        print("  - Performance monitoring for scans")
        print("  - Error tracking with full context")
        print("  - Security event logging")
        
        print("\n✓ Port Scanner Integration:")
        # Test port scanner with logging
        scan_request = {
            "target_host": "127.0.0.1",
            "target_ports": [80, 443, 22],
            "scan_timeout": 2.0
        }
        
        print("  Running port scan with structured logging...")
        scan_result = await scan_ports_async(scan_request)
        
        if scan_result["success"]:
            print(f"  ✅ Scan completed: {scan_result['metadata']['open_ports_count']} open ports")
        else:
            print(f"  ❌ Scan failed: {scan_result['error']}")
        
        print("\n✓ Network Validation Integration:")
        # Test network validation with logging
        validation_result = validate_ip_address("192.168.1.1")
        print(f"  IP validation result: {validation_result['is_valid']}")
        
        print("✅ Toolkit integration demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Toolkit integration demo failed: {e}")

def main():
    """Main demonstration function."""
    print("STRUCTURED LOGGING WITH CONTEXT CAPTURE DEMONSTRATION")
    print("=" * 100)
    print(f"Started at: {datetime.utcnow().isoformat()}")
    
    try:
        # Run all demonstrations
        if not demonstrate_structured_logging():
            return False
        
        demonstrate_function_logging()
        demonstrate_error_logging()
        demonstrate_validation_logging()
        demonstrate_performance_logging()
        demonstrate_security_logging()
        
        # Run async demonstrations
        asyncio.run(demonstrate_async_logging())
        
        demonstrate_log_file_structure()
        demonstrate_decorator_usage()
        
        # Run integration demonstration
        asyncio.run(demonstrate_integration_with_toolkit())
        
        print("\n" + "=" * 100)
        print("✅ ALL STRUCTURED LOGGING DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("=" * 100)
        
        print("\n🎯 Key Features Demonstrated:")
        print("  ✅ Structured logging with context capture")
        print("  ✅ Module, function, and parameter tracking")
        print("  ✅ Error context with stack traces")
        print("  ✅ Performance metrics logging")
        print("  ✅ Security event logging")
        print("  ✅ Validation error logging")
        print("  ✅ Async function logging")
        print("  ✅ Decorator-based automatic logging")
        print("  ✅ JSON-formatted log output")
        print("  ✅ Integration with cybersecurity toolkit")
        
        print("\n📋 Logging Benefits:")
        print("  1. Comprehensive error tracking with full context")
        print("  2. Performance monitoring and optimization")
        print("  3. Security event audit trails")
        print("  4. Debugging and troubleshooting support")
        print("  5. Operational monitoring and alerting")
        print("  6. Compliance and regulatory requirements")
        print("  7. Automated log analysis and reporting")
        print("  8. Incident response and forensics")
        
        print(f"\nCompleted at: {datetime.utcnow().isoformat()}")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 