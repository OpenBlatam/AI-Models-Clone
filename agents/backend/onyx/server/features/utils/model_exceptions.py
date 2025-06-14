"""
Model Exceptions - Onyx Integration
Custom exceptions for model operations.
"""
from typing import Any, Dict, List, Optional, Type, Union

class OnyxModelError(Exception):
    """Base exception for Onyx model errors."""
    pass

class ValidationError(OnyxModelError):
    """Exception raised for validation errors."""
    def __init__(self, message: str, errors: Optional[List[str]] = None):
        self.message = message
        self.errors = errors or []
        super().__init__(self.message)

class IndexingError(OnyxModelError):
    """Exception raised for indexing errors."""
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)

class CacheError(OnyxModelError):
    """Exception raised for caching errors."""
    def __init__(self, message: str, key: Optional[str] = None):
        self.message = message
        self.key = key
        super().__init__(self.message)

class SerializationError(OnyxModelError):
    """Exception raised for serialization errors."""
    def __init__(self, message: str, data: Optional[Dict[str, Any]] = None):
        self.message = message
        self.data = data
        super().__init__(self.message)

class VersionError(OnyxModelError):
    """Exception raised for version errors."""
    def __init__(self, message: str, current_version: Optional[str] = None, required_version: Optional[str] = None):
        self.message = message
        self.current_version = current_version
        self.required_version = required_version
        super().__init__(self.message)

class AuditError(OnyxModelError):
    """Exception raised for audit errors."""
    def __init__(self, message: str, user_id: Optional[str] = None):
        self.message = message
        self.user_id = user_id
        super().__init__(self.message)

class SoftDeleteError(OnyxModelError):
    """Exception raised for soft delete errors."""
    def __init__(self, message: str, is_deleted: Optional[bool] = None):
        self.message = message
        self.is_deleted = is_deleted
        super().__init__(self.message)

class TimestampError(OnyxModelError):
    """Exception raised for timestamp errors."""
    def __init__(self, message: str, timestamp: Optional[str] = None):
        self.message = message
        self.timestamp = timestamp
        super().__init__(self.message)

class RegistryError(OnyxModelError):
    """Exception raised for registry errors."""
    def __init__(self, message: str, model_name: Optional[str] = None):
        self.message = message
        self.model_name = model_name
        super().__init__(self.message)

class FactoryError(OnyxModelError):
    """Exception raised for factory errors."""
    def __init__(self, message: str, model_type: Optional[Type] = None):
        self.message = message
        self.model_type = model_type
        super().__init__(self.message)

# Example usage:
"""
from datetime import datetime
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create model with error handling
class UserModel(OnyxBaseModel):
    name: str
    email: str
    age: Optional[int] = None
    
    def validate(self) -> None:
        errors = []
        
        # Validate name
        if not self.name:
            errors.append("Name is required")
        
        # Validate email
        if not self.email or "@" not in self.email:
            errors.append("Invalid email format")
        
        # Validate age
        if self.age is not None and (self.age < 0 or self.age > 150):
            errors.append("Age must be between 0 and 150")
        
        if errors:
            raise ValidationError("Validation failed", errors)
    
    def cache(self, key: str) -> None:
        try:
            # Cache implementation
            pass
        except Exception as e:
            raise CacheError(f"Failed to cache model: {str(e)}", key)
    
    def index(self, field: str, value: Any) -> None:
        try:
            # Indexing implementation
            pass
        except Exception as e:
            raise IndexingError(f"Failed to index model: {str(e)}", field, value)
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            return self.model_dump()
        except Exception as e:
            raise SerializationError(f"Failed to serialize model: {str(e)}", self.model_dump())

# Create and use model with error handling
try:
    user = UserModel(
        name="John",
        email="john@example.com",
        age=30
    )
    
    # Validate
    user.validate()
    
    # Cache
    user.cache("email")
    
    # Index
    user.index("email", user.email)
    
    # Serialize
    user_dict = user.to_dict()
    
except ValidationError as e:
    logger.error(f"Validation error: {e.message}")
    logger.error(f"Errors: {e.errors}")
except CacheError as e:
    logger.error(f"Cache error: {e.message}")
    logger.error(f"Key: {e.key}")
except IndexingError as e:
    logger.error(f"Indexing error: {e.message}")
    logger.error(f"Field: {e.field}, Value: {e.value}")
except SerializationError as e:
    logger.error(f"Serialization error: {e.message}")
    logger.error(f"Data: {e.data}")
except OnyxModelError as e:
    logger.error(f"Model error: {e.message}")
""" 