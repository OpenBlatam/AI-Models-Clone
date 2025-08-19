from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import asyncio
import time
import statistics
from typing import List, Dict, Any
from pydantic import Field
from coding_conventions_implementation import (
    from typing import List, Dict, Optional, Union, Tuple
    import logging
    from datetime import datetime
        import traceback
from typing import Any, List, Dict, Optional
"""
Coding Conventions Runner Script
===============================

This script demonstrates:
- Python naming conventions (PEP 8)
- FastAPI best practices and conventions
- Code organization and structure
- Documentation standards
- Type hints and annotations
- Error handling conventions
- Testing conventions
- Import organization
- Code formatting standards
"""

    UserCreate, UserUpdate, UserResponse, UserStatus, ErrorSeverity,
    UserService, UserRepository, ValidationException, NotFoundException,
    DatabaseException, AppException, validate_email_format, sanitize_input, generate_unique_id,
    format_datetime, parse_datetime, APIResponse, UserCredentials,
    MAX_RETRY_ATTEMPTS, DEFAULT_TIMEOUT, SUPPORTED_LANGUAGES
)


def demonstrate_naming_conventions():
    """Demonstrate Python naming conventions."""
    print("\n" + "="*60)
    print("Python Naming Conventions (PEP 8)")
    print("="*60)
    
    print("\n1. Constants (UPPER_CASE):")
    print(f"   - MAX_RETRY_ATTEMPTS: {MAX_RETRY_ATTEMPTS}")
    print(f"   - DEFAULT_TIMEOUT: {DEFAULT_TIMEOUT}")
    print(f"   - SUPPORTED_LANGUAGES: {SUPPORTED_LANGUAGES}")
    
    print("\n2. Variables and Functions (snake_case):")
    user_name = "john_doe"
    email_address = "john@example.com"
    is_active = True
    
    print(f"   - user_name: {user_name}")
    print(f"   - email_address: {email_address}")
    print(f"   - is_active: {is_active}")
    
    def calculate_user_score(user_id: int, activity_level: float) -> float:
        """Calculate user activity score."""
        base_score = 100
        return base_score * activity_level
    
    score = calculate_user_score(1, 0.85)
    print(f"   - calculate_user_score result: {score}")
    
    print("\n3. Classes (PascalCase):")
    class UserManager:
        """User management class."""
        
        def __init__(self, user_id: int):
            
    """__init__ function."""
self.user_id = user_id
            self._private_attribute = "private"
        
        def get_user_info(self) -> Dict[str, Any]:
            """Get user information."""
            return {"id": self.user_id, "name": "John Doe"}
    
    user_manager = UserManager(1)
    print(f"   - UserManager instance: {user_manager.get_user_info()}")
    
    print("\n4. Protected and Private Attributes:")
    print(f"   - Protected: _private_attribute (convention only)")
    print(f"   - Private: __really_private (name mangling)")


def demonstrate_type_hints():
    """Demonstrate type hints and annotations."""
    print("\n" + "="*60)
    print("Type Hints and Annotations")
    print("="*60)
    
    print("\n1. Basic Type Hints:")
    
    def greet_user(name: str, age: int, is_vip: bool = False) -> str:
        """Greet user with type hints."""
        prefix = "VIP" if is_vip else "User"
        return f"Hello {prefix} {name}, you are {age} years old"
    
    result = greet_user("Alice", 30, True)
    print(f"   - Function with type hints: {result}")
    
    print("\n2. Complex Type Hints:")
    
    
    def process_user_data(
        users: List[Dict[str, Any]],
        settings: Optional[Dict[str, str]] = None
    ) -> Tuple[int, List[str]]:
        """Process user data with complex types."""
        count = len(users)
        names = [user.get("name", "Unknown") for user in users]
        return count, names
    
    users_data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
    count, names = process_user_data(users_data)
    print(f"   - Processed {count} users: {names}")
    
    print("\n3. Union Types:")
    
    def format_value(value: Union[str, int, float]) -> str:
        """Format different types of values."""
        if isinstance(value, str):
            return f"String: {value}"
        elif isinstance(value, int):
            return f"Integer: {value}"
        else:
            return f"Float: {value:.2f}"
    
    print(f"   - String: {format_value('hello')}")
    print(f"   - Integer: {format_value(42)}")
    print(f"   - Float: {format_value(3.14159)}")


def demonstrate_pydantic_models():
    """Demonstrate Pydantic model conventions."""
    print("\n" + "="*60)
    print("Pydantic Model Conventions")
    print("="*60)
    
    print("\n1. Model Creation and Validation:")
    
    try:
        user_create = UserCreate(
            username="john_doe",
            email="john@example.com",
            password="SecurePass123",
            full_name="John Doe"
        )
        print(f"   - Valid user created: {user_create.username}")
        print(f"   - Model dump: {user_create.model_dump()}")
    except Exception as e:
        print(f"   - Validation error: {e}")
    
    print("\n2. Model Validation Errors:")
    
    try:
        invalid_user = UserCreate(
            username="jo",  # Too short
            email="invalid-email",
            password="weak",  # Too weak
            full_name="John Doe"
        )
    except Exception as e:
        print(f"   - Expected validation error: {e}")
    
    print("\n3. Model Inheritance:")
    
    class AdminUserCreate(UserCreate):
        """Admin user creation model."""
        
        role: str = Field(..., description="Admin role")
        permissions: List[str] = Field(default_factory=list, description="Admin permissions")
    
    admin_user = AdminUserCreate(
        username="admin",
        email="admin@example.com",
        password="AdminPass123",
        full_name="System Admin",
        role="super_admin",
        permissions=["read", "write", "delete"]
    )
    print(f"   - Admin user created: {admin_user.role}")
    print(f"   - Permissions: {admin_user.permissions}")


def demonstrate_error_handling():
    """Demonstrate error handling conventions."""
    print("\n" + "="*60)
    print("Error Handling Conventions")
    print("="*60)
    
    print("\n1. Custom Exceptions:")
    
    try:
        raise ValidationException("Invalid email format", "email")
    except ValidationException as e:
        print(f"   - Validation error: {e.message} (field: {e.field})")
    
    try:
        raise NotFoundException("User", 123)
    except NotFoundException as e:
        print(f"   - Not found error: {e.message}")
    
    try:
        raise DatabaseException("Connection failed", "connect")
    except DatabaseException as e:
        print(f"   - Database error: {e.message} (operation: {e.operation})")
    
    print("\n2. Exception Hierarchy:")
    
    exceptions = [
        ValidationException("Test validation error"),
        NotFoundException("Resource", 1),
        DatabaseException("Test database error"),
        AppException("Test base exception")
    ]
    
    for exc in exceptions:
        print(f"   - {type(exc).__name__}: {exc.message} (code: {exc.error_code})")
    
    print("\n3. Error Handling Patterns:")
    
    def safe_divide(a: float, b: float) -> float:
        """Safe division with error handling."""
        try:
            return a / b
        except ZeroDivisionError:
            raise ValidationException("Division by zero is not allowed")
        except Exception as e:
            raise AppException(f"Unexpected error: {str(e)}")
    
    try:
        result = safe_divide(10, 2)
        print(f"   - Safe division result: {result}")
    except AppException as e:
        print(f"   - Division error: {e.message}")
    
    try:
        result = safe_divide(10, 0)
    except AppException as e:
        print(f"   - Division by zero error: {e.message}")


async def demonstrate_service_layer():
    """Demonstrate service layer conventions."""
    print("\n" + "="*60)
    print("Service Layer Conventions")
    print("="*60)
    
    print("\n1. Service Creation and Usage:")
    
    
    # Create logger
    logger = logging.getLogger("demo_service")
    logger.setLevel(logging.INFO)
    
    # Create repository and service
    repository = UserRepository(session=None)
    service = UserService(logger, repository)
    
    print("   - Service and repository created successfully")
    
    print("\n2. Service Operations:")
    
    # Create user
    user_data = UserCreate(
        username="demo_user",
        email="demo@example.com",
        password="DemoPass123",
        full_name="Demo User"
    )
    
    try:
        user = await service.create_user(user_data)
        print(f"   - User created: {user.username}")
        
        # Get user
        retrieved_user = await service.get_user_by_id(user.id)
        print(f"   - User retrieved: {retrieved_user.username}")
        
        # Update user
        update_data = UserUpdate(
            full_name="Updated Demo User",
            status=UserStatus.INACTIVE
        )
        updated_user = await service.update_user(user.id, update_data)
        print(f"   - User updated: {updated_user.full_name}")
        
        # Delete user
        success = await service.delete_user(user.id)
        print(f"   - User deleted: {success}")
        
    except Exception as e:
        print(f"   - Service operation error: {e}")


def demonstrate_utility_functions():
    """Demonstrate utility function conventions."""
    print("\n" + "="*60)
    print("Utility Function Conventions")
    print("="*60)
    
    print("\n1. Input Validation:")
    
    emails = [
        "valid@example.com",
        "invalid-email",
        "test@domain",
        "user.name@company.co.uk"
    ]
    
    for email in emails:
        is_valid = validate_email_format(email)
        print(f"   - {email}: {'Valid' if is_valid else 'Invalid'}")
    
    print("\n2. Input Sanitization:")
    
    inputs = [
        "Normal text",
        "<script>alert('xss')</script>",
        "User input with 'quotes' and \"double quotes\"",
        "Text with <b>HTML</b> tags"
    ]
    
    for input_text in inputs:
        sanitized = sanitize_input(input_text)
        print(f"   - Original: {input_text}")
        print(f"   - Sanitized: {sanitized}")
    
    print("\n3. ID Generation:")
    
    unique_ids = [generate_unique_id() for _ in range(3)]
    for i, uid in enumerate(unique_ids, 1):
        print(f"   - ID {i}: {uid}")
    
    print("\n4. DateTime Formatting:")
    
    
    now = datetime.utcnow()
    formatted = format_datetime(now)
    parsed = parse_datetime(formatted)
    
    print(f"   - Original: {now}")
    print(f"   - Formatted: {formatted}")
    print(f"   - Parsed: {parsed}")


def demonstrate_data_structures():
    """Demonstrate data structure conventions."""
    print("\n" + "="*60)
    print("Data Structure Conventions")
    print("="*60)
    
    print("\n1. Enums:")
    
    print("   - User Statuses:")
    for status in UserStatus:
        print(f"     * {status.value}")
    
    print("   - Error Severities:")
    for severity in ErrorSeverity:
        print(f"     * {severity.value}")
    
    print("\n2. Data Classes:")
    
    credentials = UserCredentials(
        username="test_user",
        password="test_password",
        email="test@example.com"
    )
    
    print(f"   - Credentials object: {credentials}")
    print(f"   - Is valid: {credentials.is_valid()}")
    
    print("\n3. API Response Structure:")
    
    responses = [
        APIResponse(
            success=True,
            message="Operation completed successfully",
            data={"user_id": 123, "username": "john_doe"}
        ),
        APIResponse(
            success=False,
            message="Validation failed",
            data={"errors": ["Invalid email format"]}
        )
    ]
    
    for i, response in enumerate(responses, 1):
        print(f"   - Response {i}:")
        print(f"     * Success: {response.success}")
        print(f"     * Message: {response.message}")
        print(f"     * Timestamp: {response.timestamp}")


def demonstrate_documentation_standards():
    """Demonstrate documentation standards."""
    print("\n" + "="*60)
    print("Documentation Standards")
    print("="*60)
    
    print("\n1. Function Documentation:")
    
    def process_user_data(
        user_id: int,
        include_metadata: bool = False,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Process user data with optional metadata.
        
        This function retrieves and processes user data from the database.
        It supports optional metadata inclusion and configurable retry attempts.
        
        Args:
            user_id: The unique identifier of the user
            include_metadata: Whether to include additional metadata (default: False)
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            Dict containing processed user data
            
        Raises:
            ValueError: If user_id is invalid
            DatabaseException: If database operation fails
            
        Example:
            >>> data = process_user_data(123, include_metadata=True)
            >>> print(data['username'])
            'john_doe'
        """
        if user_id <= 0:
            raise ValueError("user_id must be positive")
        
        # Simulate processing
        result = {
            "user_id": user_id,
            "username": f"user_{user_id}",
            "email": f"user_{user_id}@example.com"
        }
        
        if include_metadata:
            result["metadata"] = {
                "created_at": "2024-01-01T00:00:00Z",
                "last_login": "2024-01-15T10:30:00Z"
            }
        
        return result
    
    print("   - Function documented with:")
    print("     * Clear description")
    print("     * Parameter documentation")
    print("     * Return value documentation")
    print("     * Exception documentation")
    print("     * Usage example")
    
    print("\n2. Class Documentation:")
    
    class DataProcessor:
        """
        A data processing utility class.
        
        This class provides methods for processing various types of data
        with configurable options and error handling.
        
        Attributes:
            batch_size: Number of items to process in each batch
            timeout: Maximum time to wait for processing operations
        """
        
        def __init__(self, batch_size: int = 100, timeout: int = 30):
            """
            Initialize the data processor.
            
            Args:
                batch_size: Number of items per batch
                timeout: Processing timeout in seconds
            """
            self.batch_size = batch_size
            self.timeout = timeout
        
        def process_batch(self, items: List[Any]) -> List[Any]:
            """
            Process a batch of items.
            
            Args:
                items: List of items to process
                
            Returns:
                List of processed items
                
            Raises:
                ValueError: If items list is empty
            """
            if not items:
                raise ValueError("Items list cannot be empty")
            
            # Simulate processing
            return [f"processed_{item}" for item in items]
    
    print("   - Class documented with:")
    print("     * Class description")
    print("     * Attribute documentation")
    print("     * Method documentation")


def demonstrate_code_organization():
    """Demonstrate code organization conventions."""
    print("\n" + "="*60)
    print("Code Organization Conventions")
    print("="*60)
    
    print("\n1. Import Organization:")
    print("   - Standard library imports first")
    print("   - Third-party imports second")
    print("   - Local application imports last")
    print("   - Alphabetical order within each group")
    print("   - Use absolute imports when possible")
    
    print("\n2. File Structure:")
    print("   - Constants and configuration at the top")
    print("   - Enums and data classes")
    print("   - Abstract base classes")
    print("   - Concrete implementations")
    print("   - Utility functions")
    print("   - Main application logic")
    
    print("\n3. Function and Method Order:")
    print("   - Public methods first")
    print("   - Protected methods second")
    print("   - Private methods last")
    print("   - Related methods grouped together")
    
    print("\n4. Class Organization:")
    print("   - Class-level attributes")
    print("   - __init__ method")
    print("   - Public methods")
    print("   - Protected methods")
    print("   - Private methods")
    print("   - Magic methods")


def main():
    """Main function to run all coding conventions demonstrations."""
    print("Coding Conventions Implementation Demonstrations")
    print("=" * 80)
    
    try:
        # Core demonstrations
        demonstrate_naming_conventions()
        demonstrate_type_hints()
        demonstrate_pydantic_models()
        demonstrate_error_handling()
        demonstrate_utility_functions()
        demonstrate_data_structures()
        demonstrate_documentation_standards()
        demonstrate_code_organization()
        
        # Run async demonstrations
        print("\n" + "="*80)
        print("Running Async Demonstrations...")
        print("="*80)
        
        asyncio.run(demonstrate_service_layer())
        
        print("\n" + "="*80)
        print("All Coding Conventions Demonstrations Completed Successfully!")
        print("="*80)
        
        print("\n🎯 Key Coding Conventions Demonstrated:")
        print("  ✅ Python naming conventions (PEP 8)")
        print("  ✅ Type hints and annotations")
        print("  ✅ Pydantic model best practices")
        print("  ✅ Error handling patterns")
        print("  ✅ Service layer architecture")
        print("  ✅ Utility function design")
        print("  ✅ Data structure conventions")
        print("  ✅ Documentation standards")
        print("  ✅ Code organization principles")
        print("  ✅ FastAPI best practices")
        
        print("\n📋 Best Practices Summary:")
        print("  1. Use descriptive names (snake_case for variables/functions)")
        print("  2. Use type hints for all function parameters and return values")
        print("  3. Create custom exceptions for domain-specific errors")
        print("  4. Document all public functions and classes")
        print("  5. Organize code logically with clear separation of concerns")
        print("  6. Use Pydantic models for data validation and serialization")
        print("  7. Follow consistent error handling patterns")
        print("  8. Use constants for configuration values")
        print("  9. Implement proper logging throughout the application")
        print("  10. Write clean, readable, and maintainable code")
        
    except Exception as e:
        print(f"\nError during demonstrations: {str(e)}")
        traceback.print_exc()
        raise


match __name__:
    case "__main__":
    main() 