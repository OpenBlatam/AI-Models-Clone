from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
        from cybersecurity_toolkit.utils.happy_path_pattern import (
        from cybersecurity_toolkit.utils.network_helpers import (
        from cybersecurity_toolkit.scanners.port_scanner import scan_ports_async
from typing import Any, List, Dict, Optional
import logging
"""
Happy Path Pattern Demo
======================

Demonstrates the happy path pattern with:
- Early returns for error conditions
- Avoiding nested conditionals
- Keeping main success logic at the end
- Guard clauses for validation
- Clean, readable code structure
"""


# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demonstrate_happy_path_pattern():
    """Demonstrate the happy path pattern with various examples."""
    print("=" * 80)
    print("HAPPY PATH PATTERN DEMONSTRATION")
    print("=" * 80)
    
    try:
            HappyPathProcessor,
            demonstrate_happy_path_pattern as demo_pattern
        )
        
        print("✓ Happy Path Pattern Structure:")
        print("""
def function_with_happy_path(param) -> Any:
    # Guard clause 1: Check if param is provided
    if not param:
        raise ValidationError("Parameter required")
    
    # Guard clause 2: Check param type
    if not isinstance(param, expected_type):
        raise ValidationError("Invalid parameter type")
    
    # Guard clause 3: Check param value
    if param < min_value or param > max_value:
        raise ValidationError("Parameter out of range")
    
    # Happy path: All validation passed, main logic here
    result = process_parameter(param)
    return result
    """)
        
        print("\n✓ Benefits of Happy Path Pattern:")
        print("  - Early returns prevent deep nesting")
        print("  - Main success logic is clearly visible")
        print("  - Easier to read and understand")
        print("  - Reduces cognitive complexity")
        print("  - Makes debugging easier")
        print("  - Improves code maintainability")
        
        # Test data processing
        print("\n✓ Data Processing Example:")
        processor = HappyPathProcessor()
        
        try:
            valid_data = {
                "id": "user123",
                "content": "Hello, World!",
                "type": "text"
            }
            result = processor.process_data_happy_path(valid_data)
            print(f"  ✅ Success: {result['status']}")
            
            # Test invalid data
            invalid_data = {
                "id": "user123",
                "content": "A" * 1001,  # Too long
                "type": "text"
            }
            result = processor.process_data_happy_path(invalid_data)
        except Exception as e:
            print(f"  ❌ Validation error: {str(e)}")
        
        # Test network config validation
        print("\n✓ Network Config Validation Example:")
        try:
            valid_config = {
                "host": "example.com",
                "port": 443,
                "protocol": "https",
                "timeout": 30.0
            }
            result = processor.validate_network_config_happy_path(valid_config)
            print(f"  ✅ Success: {result['status']}")
            
            # Test invalid config
            invalid_config = {
                "host": "example.com",
                "port": 99999,  # Invalid port
                "protocol": "https"
            }
            result = processor.validate_network_config_happy_path(invalid_config)
        except Exception as e:
            print(f"  ❌ Validation error: {str(e)}")
        
        # Test user request processing
        print("\n✓ User Request Processing Example:")
        try:
            valid_request = {
                "auth_token": "valid_token_with_sufficient_length",
                "request_type": "read",
                "resource_id": "resource123",
                "data": {"key": "value"}
            }
            result = processor.process_user_request_happy_path(valid_request)
            print(f"  ✅ Success: {result['status']}")
            
            # Test invalid request
            invalid_request = {
                "auth_token": "short",  # Too short
                "request_type": "read",
                "resource_id": "resource123"
            }
            result = processor.process_user_request_happy_path(invalid_request)
        except Exception as e:
            print(f"  ❌ Validation error: {str(e)}")
        
        print("✅ Happy path pattern demonstrated successfully")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("  Make sure the cybersecurity toolkit modules are available")
        return False
    except Exception as e:
        print(f"❌ Happy path pattern demo failed: {e}")
        return False
    
    return True

def demonstrate_nested_vs_happy_path():
    """Compare nested conditionals vs happy path pattern."""
    print("\n" + "=" * 80)
    print("NESTED CONDITIONALS VS HAPPY PATH PATTERN")
    print("=" * 80)
    
    print("✓ Nested Conditionals (Avoid This):")
    print("""
def process_data_nested(data) -> Any:
    if data is not None:
        if isinstance(data, dict):
            if "id" in data:
                if "content" in data:
                    if len(data["content"]) <= 1000:
                        if data["type"] in ["text", "json"]:
                            # Main logic here (deeply nested)
                            return {"status": "success", "data": data}
                        else:
                            return {"status": "error", "message": "Invalid type"}
                    else:
                        return {"status": "error", "message": "Content too long"}
                else:
                    return {"status": "error", "message": "Missing content"}
            else:
                return {"status": "error", "message": "Missing id"}
        else:
            return {"status": "error", "message": "Invalid data type"}
    else:
        return {"status": "error", "message": "No data provided"}
    """)
    
    print("\n✓ Happy Path Pattern (Use This):")
    print("""
def process_data_happy_path(data) -> Any:
    # Guard clause 1: Check if data is provided
    if not data:
        raise ValidationError("No data provided")
    
    # Guard clause 2: Check data type
    if not isinstance(data, dict):
        raise ValidationError("Invalid data type")
    
    # Guard clause 3: Check required fields
    if "id" not in data:
        raise ValidationError("Missing id")
    
    if "content" not in data:
        raise ValidationError("Missing content")
    
    # Guard clause 4: Validate content length
    if len(data["content"]) > 1000:
        raise ValidationError("Content too long")
    
    # Guard clause 5: Validate type
    if data["type"] not in ["text", "json"]:
        raise ValidationError("Invalid type")
    
    # Happy path: All validation passed, main logic here
    return {"status": "success", "data": data}
    """)
    
    print("\n✓ Comparison Benefits:")
    print("  Nested Conditionals:")
    print("    - Hard to read and understand")
    print("    - High cognitive complexity")
    print("    - Difficult to maintain")
    print("    - Error handling mixed with logic")
    print("    - Deep nesting levels")
    
    print("\n  Happy Path Pattern:")
    print("    - Clear and readable")
    print("    - Low cognitive complexity")
    print("    - Easy to maintain")
    print("    - Clear separation of concerns")
    print("    - Main logic is obvious")

def demonstrate_guard_clauses():
    """Demonstrate guard clauses as part of happy path pattern."""
    print("\n" + "=" * 80)
    print("GUARD CLAUSES DEMONSTRATION")
    print("=" * 80)
    
    print("✓ Guard Clause Pattern:")
    print("""
def function_with_guard_clauses(param1, param2, param3) -> Any:
    # Guard clause 1: Validate param1
    if not param1:
        raise ValidationError("param1 is required")
    
    # Guard clause 2: Validate param2
    if not isinstance(param2, str):
        raise ValidationError("param2 must be a string")
    
    # Guard clause 3: Validate param3
    if param3 < 0 or param3 > 100:
        raise ValidationError("param3 must be between 0 and 100")
    
    # Guard clause 4: Check business rules
    if param1 == "admin" and param3 < 50:
        raise ValidationError("Admin requires higher permission level")
    
    # Happy path: All validation passed
    result = process_parameters(param1, param2, param3)
    return result
    """)
    
    print("\n✓ Guard Clause Benefits:")
    print("  - Early validation prevents invalid processing")
    print("  - Clear error messages for each validation failure")
    print("  - Reduces complexity of main logic")
    print("  - Makes function behavior predictable")
    print("  - Improves testability")

def demonstrate_network_helpers_happy_path():
    """Demonstrate happy path pattern in network helpers."""
    print("\n" + "=" * 80)
    print("NETWORK HELPERS HAPPY PATH DEMONSTRATION")
    print("=" * 80)
    
    try:
            validate_ip_address,
            validate_hostname,
            validate_network_target,
            check_connectivity_sync,
            resolve_hostname_to_ip,
            validate_port_range
        )
        
        print("✓ IP Address Validation:")
        # Test valid IP
        result = validate_ip_address("192.168.1.1")
        print(f"  ✅ Valid IP: {result['is_valid']}")
        
        # Test invalid IP
        result = validate_ip_address("invalid.ip")
        print(f"  ❌ Invalid IP: {result['error']}")
        
        print("\n✓ Hostname Validation:")
        # Test valid hostname
        result = validate_hostname("example.com")
        print(f"  ✅ Valid hostname: {result['is_valid']}")
        
        # Test invalid hostname
        result = validate_hostname("invalid..hostname")
        print(f"  ❌ Invalid hostname: {result['error']}")
        
        print("\n✓ Network Target Validation:")
        # Test valid target
        result = validate_network_target("example.com")
        print(f"  ✅ Valid target: {result['is_valid']} ({result['target_type']})")
        
        # Test invalid target
        result = validate_network_target("invalid..target")
        print(f"  ❌ Invalid target: {result['error']}")
        
        print("\n✓ Port Range Validation:")
        # Test valid port range
        result = validate_port_range(80, 443)
        print(f"  ✅ Valid port range: {result['is_valid']} ({result['port_count']} ports)")
        
        # Test invalid port range
        result = validate_port_range(99999, 100000)
        print(f"  ❌ Invalid port range: {result['error']}")
        
        print("✅ Network helpers happy path demonstrated successfully")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Network helpers demo failed: {e}")
        return False
    
    return True

async def demonstrate_port_scanner_happy_path():
    """Demonstrate happy path pattern in port scanner."""
    print("\n" + "=" * 80)
    print("PORT SCANNER HAPPY PATH DEMONSTRATION")
    print("=" * 80)
    
    try:
        
        print("✓ Port Scanner with Happy Path Pattern:")
        
        # Test with invalid request (missing target_host)
        print("\n  Testing invalid request (missing target_host):")
        try:
            invalid_request = {
                "target_ports": [80, 443],
                "scan_timeout": 5.0
            }
            await scan_ports_async(invalid_request)
        except Exception as e:
            print(f"    ❌ Validation error: {str(e)}")
        
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
            print(f"    ❌ Validation error: {str(e)}")
        
        # Test with valid request (should work)
        print("\n  Testing valid request:")
        try:
            valid_request = {
                "target_host": "127.0.0.1",
                "target_ports": [80, 443, 22],
                "scan_timeout": 2.0
            }
            result = await scan_ports_async(valid_request)
            print(f"    ✅ Success: {result['metadata']['open_ports_count']} open ports found")
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
        
        print("✅ Port scanner happy path demonstrated successfully")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Port scanner demo failed: {e}")
        return False
    
    return True

def demonstrate_real_world_examples():
    """Demonstrate real-world examples of happy path pattern."""
    print("\n" + "=" * 80)
    print("REAL-WORLD HAPPY PATH EXAMPLES")
    print("=" * 80)
    
    print("✓ User Authentication Example:")
    print("""
def authenticate_user(username, password, session_data) -> Any:
    # Guard clause 1: Check if credentials are provided
    if not username or not password:
        raise AuthenticationError("Username and password required")
    
    # Guard clause 2: Validate username format
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise AuthenticationError("Invalid username format")
    
    # Guard clause 3: Check if user exists
    user = get_user_by_username(username)
    if not user:
        raise AuthenticationError("User not found")
    
    # Guard clause 4: Check if account is locked
    if user.is_locked:
        raise AuthenticationError("Account is locked")
    
    # Guard clause 5: Verify password
    if not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid password")
    
    # Guard clause 6: Check if session is valid
    if not is_valid_session(session_data):
        raise AuthenticationError("Invalid session")
    
    # Happy path: All validation passed, authenticate user
    session = create_user_session(user)
    return {"status": "authenticated", "session": session}
    """)
    
    print("\n✓ File Processing Example:")
    print("""
def process_file(file_path, output_format, options) -> Any:
    # Guard clause 1: Check if file path is provided
    if not file_path:
        raise ValidationError("File path is required")
    
    # Guard clause 2: Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Guard clause 3: Check if file is readable
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read file: {file_path}")
    
    # Guard clause 4: Validate output format
    valid_formats = ["json", "xml", "csv", "yaml"]
    if output_format not in valid_formats:
        raise ValidationError(f"Invalid output format. Must be one of: {valid_formats}")
    
    # Guard clause 5: Check file size
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValidationError(f"File too large: {file_size} bytes")
    
    # Happy path: All validation passed, process file
    content = read_file_content(file_path)
    processed_data = transform_content(content, options)
    output = format_output(processed_data, output_format)
    return {"status": "processed", "output": output}
    """)
    
    print("\n✓ API Request Processing Example:")
    print("""
async def process_api_request(request_data, user_context) -> Any:
    # Guard clause 1: Validate request structure
    if not isinstance(request_data, dict):
        raise ValidationError("Request must be a dictionary")
    
    # Guard clause 2: Check required fields
    required_fields = ["action", "data", "timestamp"]
    for field in required_fields:
        if field not in request_data:
            raise ValidationError(f"Missing required field: {field}")
    
    # Guard clause 3: Validate action
    valid_actions = ["create", "read", "update", "delete"]
    if request_data["action"] not in valid_actions:
        raise ValidationError(f"Invalid action. Must be one of: {valid_actions}")
    
    # Guard clause 4: Check user permissions
    if not has_permission(user_context, request_data["action"]):
        raise AuthorizationError(f"Insufficient permissions for {request_data['action']}")
    
    # Guard clause 5: Validate timestamp
    if not is_valid_timestamp(request_data["timestamp"]):
        raise ValidationError("Invalid timestamp")
    
    # Guard clause 6: Rate limiting
    if is_rate_limited(user_context):
        raise RateLimitError("Rate limit exceeded")
    
    # Happy path: All validation passed, process request
    result = execute_action(request_data["action"], request_data["data"])
    return {"status": "success", "result": result}
    """)

def main():
    """Main demonstration function."""
    print("HAPPY PATH PATTERN IMPLEMENTATION DEMONSTRATION")
    print("=" * 100)
    print(f"Started at: {datetime.utcnow().isoformat()}")
    
    try:
        # Run all demonstrations
        if not demonstrate_happy_path_pattern():
            return False
        
        demonstrate_nested_vs_happy_path()
        demonstrate_guard_clauses()
        
        if not demonstrate_network_helpers_happy_path():
            return False
        
        # Run async demonstrations
        if not asyncio.run(demonstrate_port_scanner_happy_path()):
            return False
        
        demonstrate_real_world_examples()
        
        print("\n" + "=" * 100)
        print("✅ HAPPY PATH PATTERN DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("=" * 100)
        
        print("\n🎯 Key Patterns Demonstrated:")
        print("  ✅ Early returns for error conditions")
        print("  ✅ Avoiding nested conditionals")
        print("  ✅ Keeping main success logic at the end")
        print("  ✅ Guard clauses for validation")
        print("  ✅ Clean, readable code structure")
        print("  ✅ Reduced cognitive complexity")
        print("  ✅ Real-world examples")
        
        print("\n📋 Best Practices:")
        print("  1. Use guard clauses at the beginning of functions")
        print("  2. Return early on error conditions")
        print("  3. Keep the main success logic at the end")
        print("  4. Avoid deep nesting of conditionals")
        print("  5. Use descriptive error messages")
        print("  6. Separate validation from business logic")
        print("  7. Make the happy path obvious and clear")
        print("  8. Improve code readability and maintainability")
        
        print(f"\nCompleted at: {datetime.utcnow().isoformat()}")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 