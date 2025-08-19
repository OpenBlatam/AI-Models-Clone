from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
        from cybersecurity_toolkit.exceptions.custom_exceptions import (
        from cybersecurity_toolkit.exceptions.custom_exceptions import (
        from cybersecurity_toolkit.exceptions.error_mapper import format_cli_error
        from cybersecurity_toolkit.exceptions.custom_exceptions import (
        from cybersecurity_toolkit.exceptions.error_mapper import format_cli_error
        from cybersecurity_toolkit.exceptions.custom_exceptions import (
        from cybersecurity_toolkit.exceptions.error_mapper import format_cli_error
        from cybersecurity_toolkit.exceptions.custom_exceptions import (
        from cybersecurity_toolkit.exceptions.error_mapper import format_cli_error
        from cybersecurity_toolkit.exceptions.custom_exceptions import (
        from cybersecurity_toolkit.exceptions.error_mapper import format_api_error
        from cybersecurity_toolkit.scanners.port_scanner import scan_ports_async
        from cybersecurity_toolkit.exceptions.error_mapper import format_cli_error
        from cybersecurity_toolkit.exceptions.custom_exceptions import (
        from cybersecurity_toolkit.exceptions.error_mapper import log_error
        from cybersecurity_toolkit.utils.structured_logger import get_logger
from typing import Any, List, Dict, Optional
import logging
"""
Custom Exceptions Demo
=====================

Demonstrates custom exceptions with user-friendly error messages for:
- CLI output formatting
- API response formatting
- Structured error logging
- Exception hierarchy
- Error code mapping
"""


# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demonstrate_exception_hierarchy():
    """Demonstrate the custom exception hierarchy."""
    print("=" * 80)
    print("CUSTOM EXCEPTION HIERARCHY DEMONSTRATION")
    print("=" * 80)
    
    try:
            CybersecurityToolkitError,
            ValidationError,
            NetworkError,
            ScanningError,
            CryptographicError,
            ConfigurationError,
            ResourceError,
            SecurityError
        )
        
        print("✓ Exception Hierarchy:")
        print("""
CybersecurityToolkitError (Base)
├── ValidationError
│   ├── MissingRequiredFieldError
│   ├── InvalidFieldTypeError
│   ├── FieldValueOutOfRangeError
│   └── InvalidFormatError
├── NetworkError
│   ├── ConnectionTimeoutError
│   ├── ConnectionRefusedError
│   ├── InvalidTargetError
│   └── DNSResolutionError
├── ScanningError
│   ├── PortScanError
│   ├── VulnerabilityScanError
│   └── ScanConfigurationError
├── CryptographicError
│   ├── EncryptionError
│   ├── DecryptionError
│   └── InvalidKeyError
├── ConfigurationError
│   ├── MissingConfigurationError
│   └── InvalidConfigurationError
├── ResourceError
│   ├── ResourceLimitExceededError
│   └── ResourceNotFoundError
└── SecurityError
    ├── AuthenticationError
    └── AuthorizationError
        """)
        
        print("✓ Exception Features:")
        print("  - Error codes for programmatic handling")
        print("  - Context preservation")
        print("  - User-friendly messages")
        print("  - Stack trace capture")
        print("  - Timestamp tracking")
        print("  - Error ID generation")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("  Make sure the cybersecurity toolkit modules are available")
        return False

def demonstrate_validation_exceptions():
    """Demonstrate validation exceptions with user-friendly messages."""
    print("\n" + "=" * 80)
    print("VALIDATION EXCEPTIONS DEMONSTRATION")
    print("=" * 80)
    
    try:
            MissingRequiredFieldError,
            InvalidFieldTypeError,
            FieldValueOutOfRangeError,
            InvalidFormatError
        )
        
        print("✓ Missing Required Field Error:")
        try:
            raise MissingRequiredFieldError(
                "target_host",
                context={"operation": "port_scan"}
            )
        except MissingRequiredFieldError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("\n✓ Invalid Field Type Error:")
        try:
            raise InvalidFieldTypeError(
                "target_ports",
                "not_a_list",
                "list",
                context={"operation": "port_scan"}
            )
        except InvalidFieldTypeError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("\n✓ Field Value Out of Range Error:")
        try:
            raise FieldValueOutOfRangeError(
                "port_number",
                99999,
                min_value=1,
                max_value=65535,
                context={"operation": "port_scan"}
            )
        except FieldValueOutOfRangeError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("\n✓ Invalid Format Error:")
        try:
            raise InvalidFormatError(
                "ip_address",
                "invalid.ip",
                "valid IPv4 or IPv6 address",
                context={"operation": "network_validation"}
            )
        except InvalidFormatError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("✅ Validation exceptions demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Validation exceptions demo failed: {e}")

def demonstrate_network_exceptions():
    """Demonstrate network exceptions with user-friendly messages."""
    print("\n" + "=" * 80)
    print("NETWORK EXCEPTIONS DEMONSTRATION")
    print("=" * 80)
    
    try:
            ConnectionTimeoutError,
            ConnectionRefusedError,
            InvalidTargetError,
            DNSResolutionError
        )
        
        print("✓ Connection Timeout Error:")
        try:
            raise ConnectionTimeoutError(
                target="example.com",
                port=80,
                timeout=5.0,
                context={"operation": "port_scan"}
            )
        except ConnectionTimeoutError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("\n✓ Connection Refused Error:")
        try:
            raise ConnectionRefusedError(
                target="localhost",
                port=9999,
                context={"operation": "port_scan"}
            )
        except ConnectionRefusedError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("\n✓ Invalid Target Error:")
        try:
            raise InvalidTargetError(
                target="invalid..hostname",
                reason="contains consecutive dots",
                context={"operation": "network_validation"}
            )
        except InvalidTargetError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("\n✓ DNS Resolution Error:")
        try:
            raise DNSResolutionError(
                hostname="nonexistent.example.com",
                context={"operation": "dns_lookup"}
            )
        except DNSResolutionError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("✅ Network exceptions demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Network exceptions demo failed: {e}")

def demonstrate_scanning_exceptions():
    """Demonstrate scanning exceptions with user-friendly messages."""
    print("\n" + "=" * 80)
    print("SCANNING EXCEPTIONS DEMONSTRATION")
    print("=" * 80)
    
    try:
            PortScanError,
            VulnerabilityScanError,
            ScanConfigurationError
        )
        
        print("✓ Port Scan Error:")
        try:
            raise PortScanError(
                target="example.com",
                ports=[80, 443, 22],
                reason="Network connectivity issues",
                context={"operation": "port_scan"}
            )
        except PortScanError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("\n✓ Vulnerability Scan Error:")
        try:
            raise VulnerabilityScanError(
                target="example.com",
                scan_type="web_vulnerability",
                reason="Target server not responding",
                context={"operation": "vulnerability_scan"}
            )
        except VulnerabilityScanError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("\n✓ Scan Configuration Error:")
        try:
            raise ScanConfigurationError(
                target="example.com",
                configuration_error="Invalid scan timeout value",
                context={"operation": "scan_configuration"}
            )
        except ScanConfigurationError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("✅ Scanning exceptions demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Scanning exceptions demo failed: {e}")

def demonstrate_cryptographic_exceptions():
    """Demonstrate cryptographic exceptions with user-friendly messages."""
    print("\n" + "=" * 80)
    print("CRYPTOGRAPHIC EXCEPTIONS DEMONSTRATION")
    print("=" * 80)
    
    try:
            EncryptionError,
            DecryptionError,
            InvalidKeyError
        )
        
        print("✓ Encryption Error:")
        try:
            raise EncryptionError(
                algorithm="AES-256",
                reason="Invalid encryption key length",
                context={"operation": "data_encryption"}
            )
        except EncryptionError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("\n✓ Decryption Error:")
        try:
            raise DecryptionError(
                algorithm="AES-256",
                reason="Corrupted encrypted data",
                context={"operation": "data_decryption"}
            )
        except DecryptionError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("\n✓ Invalid Key Error:")
        try:
            raise InvalidKeyError(
                key_type="encryption",
                reason="Key too short (minimum 32 bytes required)",
                context={"operation": "key_validation"}
            )
        except InvalidKeyError as e:
            cli_message = format_cli_error(e)
            print(f"  CLI Message: {cli_message}")
        
        print("✅ Cryptographic exceptions demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Cryptographic exceptions demo failed: {e}")

def demonstrate_api_error_formatting():
    """Demonstrate API error formatting."""
    print("\n" + "=" * 80)
    print("API ERROR FORMATTING DEMONSTRATION")
    print("=" * 80)
    
    try:
            MissingRequiredFieldError,
            ConnectionTimeoutError,
            PortScanError
        )
        
        print("✓ API Error Response Format:")
        
        # Test validation error
        try:
            raise MissingRequiredFieldError("target_host")
        except MissingRequiredFieldError as e:
            api_response = format_api_error(e)
            print(f"  Validation Error API Response:")
            print(f"    Status Code: {api_response['status_code']}")
            print(f"    Error Type: {api_response['error_type']}")
            print(f"    User Message: {api_response['user_message']}")
            print(f"    Error Code: {api_response['error_code']}")
        
        # Test network error
        try:
            raise ConnectionTimeoutError("example.com", 80, 5.0)
        except ConnectionTimeoutError as e:
            api_response = format_api_error(e)
            print(f"\n  Network Error API Response:")
            print(f"    Status Code: {api_response['status_code']}")
            print(f"    Error Type: {api_response['error_type']}")
            print(f"    User Message: {api_response['user_message']}")
            print(f"    Error Code: {api_response['error_code']}")
        
        # Test scanning error
        try:
            raise PortScanError("example.com", [80, 443], "Network issues")
        except PortScanError as e:
            api_response = format_api_error(e)
            print(f"\n  Scanning Error API Response:")
            print(f"    Status Code: {api_response['status_code']}")
            print(f"    Error Type: {api_response['error_type']}")
            print(f"    User Message: {api_response['user_message']}")
            print(f"    Error Code: {api_response['error_code']}")
        
        print("✅ API error formatting demonstrated successfully")
        
    except Exception as e:
        print(f"❌ API error formatting demo failed: {e}")

async def demonstrate_integration_with_port_scanner():
    """Demonstrate integration with port scanner using custom exceptions."""
    print("\n" + "=" * 80)
    print("INTEGRATION WITH PORT SCANNER DEMONSTRATION")
    print("=" * 80)
    
    try:
        
        print("✓ Port Scanner with Custom Exceptions:")
        
        # Test with invalid request (missing target_host)
        print("\n  Testing invalid request (missing target_host):")
        try:
            invalid_request = {
                "target_ports": [80, 443],
                "scan_timeout": 5.0
            }
            await scan_ports_async(invalid_request)
        except Exception as e:
            cli_message = format_cli_error(e)
            print(f"    Error: {cli_message}")
        
        # Test with invalid port range
        print("\n  Testing invalid port range:")
        try:
            invalid_ports_request = {
                "target_host": "127.0.0.1",
                "target_ports": [80, 99999, 443],  # Invalid port 99999
                "scan_timeout": 5.0
            }
            await scan_ports_async(invalid_ports_request)
        except Exception as e:
            cli_message = format_cli_error(e)
            print(f"    Error: {cli_message}")
        
        # Test with valid request (should work)
        print("\n  Testing valid request:")
        try:
            valid_request = {
                "target_host": "127.0.0.1",
                "target_ports": [80, 443, 22],
                "scan_timeout": 2.0
            }
            result = await scan_ports_async(valid_request)
            print(f"    Success: {result['metadata']['open_ports_count']} open ports found")
        except Exception as e:
            cli_message = format_cli_error(e)
            print(f"    Error: {cli_message}")
        
        print("✅ Port scanner integration demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Port scanner integration demo failed: {e}")

def demonstrate_error_logging():
    """Demonstrate structured error logging with custom exceptions."""
    print("\n" + "=" * 80)
    print("STRUCTURED ERROR LOGGING DEMONSTRATION")
    print("=" * 80)
    
    try:
            MissingRequiredFieldError,
            ConnectionTimeoutError
        )
        
        logger = get_logger("error_logging_demo")
        
        print("✓ Structured Error Logging:")
        
        # Test validation error logging
        try:
            raise MissingRequiredFieldError(
                "target_host",
                context={"operation": "demo_validation"}
            )
        except MissingRequiredFieldError as e:
            log_error(e, logger, {"demo_context": "validation_error"})
            print("    Validation error logged with structured information")
        
        # Test network error logging
        try:
            raise ConnectionTimeoutError(
                target="example.com",
                port=80,
                timeout=5.0,
                context={"operation": "demo_network"}
            )
        except ConnectionTimeoutError as e:
            log_error(e, logger, {"demo_context": "network_error"})
            print("    Network error logged with structured information")
        
        print("✅ Structured error logging demonstrated successfully")
        
    except Exception as e:
        print(f"❌ Structured error logging demo failed: {e}")

def main():
    """Main demonstration function."""
    print("CUSTOM EXCEPTIONS WITH USER-FRIENDLY MESSAGES DEMONSTRATION")
    print("=" * 100)
    print(f"Started at: {datetime.utcnow().isoformat()}")
    
    try:
        # Run all demonstrations
        if not demonstrate_exception_hierarchy():
            return False
        
        demonstrate_validation_exceptions()
        demonstrate_network_exceptions()
        demonstrate_scanning_exceptions()
        demonstrate_cryptographic_exceptions()
        demonstrate_api_error_formatting()
        
        # Run async demonstrations
        asyncio.run(demonstrate_integration_with_port_scanner())
        
        demonstrate_error_logging()
        
        print("\n" + "=" * 100)
        print("✅ ALL CUSTOM EXCEPTIONS DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("=" * 100)
        
        print("\n🎯 Key Features Demonstrated:")
        print("  ✅ Comprehensive exception hierarchy")
        print("  ✅ User-friendly error messages")
        print("  ✅ CLI error formatting")
        print("  ✅ API error response formatting")
        print("  ✅ Structured error logging")
        print("  ✅ Error code generation")
        print("  ✅ Context preservation")
        print("  ✅ Integration with port scanner")
        print("  ✅ Exception mapping to HTTP status codes")
        
        print("\n📋 Exception Benefits:")
        print("  1. Clear, user-friendly error messages")
        print("  2. Consistent error handling across modules")
        print("  3. Detailed context for debugging")
        print("  4. Programmatic error handling with error codes")
        print("  5. Structured logging for monitoring")
        print("  6. API-friendly error responses")
        print("  7. CLI-friendly error output")
        print("  8. Comprehensive exception hierarchy")
        
        print(f"\nCompleted at: {datetime.utcnow().isoformat()}")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 