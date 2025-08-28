from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

import asyncio
import time
from typing import Dict, Any
from ..validators import ValidationRequest, ValidationRules, validate_and_sanitize_input
from ..crypto import KeyGenerationRequest, EncryptionRequest, generate_secure_key, encrypt_data
from ..network import PortRangeScanRequest, scan_port_range_async
from ..logging import SecurityEvent, LoggerConfig, create_security_logger, log_security_event_async
from ..intelligence import IPReputationRequest, check_ip_reputation_async
from ..testing import SecurityTestRequest, run_security_tests_async
from typing import Any, List, Dict, Optional
import logging
"""
Usage Examples

Demonstrates how to use the cybersecurity toolkit with proper async/await patterns.
"""


# Import from the main package

async def run_basic_examples() -> Dict[str, Any]:
    """Run basic security examples."""
    print("🔐 Running Basic Security Examples...")
    
    results = {}
    
    # 1. Input Validation (CPU-bound)
    print("1. Testing Input Validation...")
    validation_request = ValidationRequest(
        input_text="<script>alert('xss')</script>",
        validation_rules=ValidationRules(length=True, pattern=True, xss=True),
        max_length=1000
    )
    validation_result = validate_and_sanitize_input(validation_request)
    results["validation"] = validation_result
    print(f"   Validation result: {validation_result.is_safe}")
    
    # 2. Key Generation (CPU-bound)
    print("2. Testing Key Generation...")
    key_request = KeyGenerationRequest(
        key_length=32,
        key_type="hex"
    )
    key_result = generate_secure_key(key_request)
    results["key_generation"] = key_result
    print(f"   Generated key: {key_result.encoded_key[:16]}...")
    
    # 3. Encryption (CPU-bound)
    print("3. Testing Encryption...")
    encryption_request = EncryptionRequest(
        plaintext="Secret message",
        key=key_result.key,
        encryption_type="fernet"
    )
    encryption_result = encrypt_data(encryption_request)
    results["encryption"] = encryption_result
    print(f"   Encrypted data length: {encryption_result.encrypted_length}")
    
    return results

async def run_async_examples() -> Dict[str, Any]:
    """Run async security examples."""
    print("🔄 Running Async Security Examples...")
    
    results = {}
    
    # 1. Port Scanning (I/O-bound)
    print("1. Testing Port Scanning...")
    port_scan_request = PortRangeScanRequest(
        target_host="localhost",
        start_port=80,
        end_port=90,
        max_workers=5
    )
    scan_result = await scan_port_range_async(port_scan_request)
    results["port_scan"] = scan_result
    print(f"   Found {scan_result.open_port_count} open ports")
    
    # 2. Security Logging (I/O-bound)
    print("2. Testing Security Logging...")
    logger_config = LoggerConfig(
        log_level="INFO",
        log_format="json",
        log_file_path="security_example.log"
    )
    logger_setup = create_security_logger(logger_config)
    
    security_event = SecurityEvent(
        event_type="login_attempt",
        source_ip="192.168.1.1",
        user_id="user123",
        severity="WARNING",
        details={"success": False, "reason": "invalid_password"}
    )
    
    log_result = await log_security_event_async({
        "logger": logger_setup["logger"],
        "event": security_event
    })
    results["logging"] = log_result
    print(f"   Logged event: {log_result.logged}")
    
    # 3. Threat Intelligence (I/O-bound)
    print("3. Testing Threat Intelligence...")
    ip_request = IPReputationRequest(
        ip_address="8.8.8.8"
    )
    ip_result = await check_ip_reputation_async(ip_request)
    results["threat_intelligence"] = ip_result
    print(f"   IP reputation check completed: {ip_result.is_private}")
    
    return results

async def run_advanced_examples() -> Dict[str, Any]:
    """Run advanced security examples."""
    print("🚀 Running Advanced Security Examples...")
    
    results = {}
    
    # 1. Security Testing (I/O-bound)
    print("1. Testing Security Testing Framework...")
    test_request = SecurityTestRequest(
        base_url="http://localhost:8000",
        test_endpoints=["/api/users", "/api/admin"],
        test_types=["sql_injection", "xss"]
    )
    test_result = await run_security_tests_async(test_request)
    results["security_testing"] = test_result
    print(f"   Security test completed: {test_result.risk_level} risk")
    
    # 2. Comprehensive Security Assessment
    print("2. Running Comprehensive Security Assessment...")
    
    # Run all examples concurrently
    basic_results, async_results, test_results = await asyncio.gather(
        run_basic_examples(),
        run_async_examples(),
        run_security_tests_async(test_request)
    )
    
    # Compile comprehensive report
    comprehensive_report = {
        "basic_tests": basic_results,
        "async_tests": async_results,
        "security_tests": test_results,
        "assessment_timestamp": time.time(),
        "overall_risk_level": test_results.risk_level
    }
    
    results["comprehensive_assessment"] = comprehensive_report
    print(f"   Comprehensive assessment completed: {comprehensive_report['overall_risk_level']} risk")
    
    return results

async def main():
    """Main function to run all examples."""
    print("🔒 Cybersecurity Toolkit Examples")
    print("=" * 50)
    
    try:
        # Run all example categories
        basic_results = await run_basic_examples()
        print("\n" + "=" * 50)
        
        async_results = await run_async_examples()
        print("\n" + "=" * 50)
        
        advanced_results = await run_advanced_examples()
        print("\n" + "=" * 50)
        
        print("✅ All examples completed successfully!")
        
        # Summary
        print("\n📊 Summary:")
        print(f"   Basic tests: {len(basic_results)} completed")
        print(f"   Async tests: {len(async_results)} completed")
        print(f"   Advanced tests: {len(advanced_results)} completed")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        raise

match __name__:
    case "__main__":
    asyncio.run(main()) 