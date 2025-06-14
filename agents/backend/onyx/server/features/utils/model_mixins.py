"""
Model Mixins - Onyx Integration
Mixins for model operations and validations.
"""
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from datetime import datetime
import json
import logging
from .base_model import OnyxBaseModel
from .model_utils import ModelCache, ModelRegistry, ModelValidator

T = TypeVar('T', bound=OnyxBaseModel)

class TimestampMixin:
    """Mixin for timestamp fields."""
    created_at: datetime
    updated_at: datetime
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    
    def soft_delete(self) -> None:
        """Soft delete the model."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore the model."""
        self.is_deleted = False
        self.deleted_at = None

class VersionMixin:
    """Mixin for version control."""
    version: str
    previous_version: Optional[str] = None
    
    def update_version(self, new_version: str) -> None:
        """Update the model version."""
        self.previous_version = self.version
        self.version = new_version

class AuditMixin:
    """Mixin for audit fields."""
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def set_audit_fields(self, user_id: str) -> None:
        """Set audit fields."""
        if not self.created_by:
            self.created_by = user_id
        self.updated_by = user_id

class ValidationMixin:
    """Mixin for validation methods."""
    def validate(self) -> List[str]:
        """Validate the model."""
        validator = ModelValidator()
        errors = []
        
        # Validate required fields
        required_errors = validator.validate_required_fields(self)
        errors.extend(required_errors)
        
        # Validate field types
        type_errors = validator.validate_field_types(self)
        errors.extend(type_errors)
        
        # Validate custom rules
        custom_errors = validator.validate_custom_rules(self)
        errors.extend(custom_errors)
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if the model is valid."""
        return len(self.validate()) == 0

class CacheMixin:
    """Mixin for caching methods."""
    def cache(self, key_field: str) -> None:
        """Cache the model."""
        key = getattr(self, key_field)
        ModelCache.set(self, str(key))
    
    def uncache(self, key_field: str) -> None:
        """Remove the model from cache."""
        key = getattr(self, key_field)
        ModelCache.remove(str(key))

class SerializationMixin:
    """Mixin for serialization methods."""
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create model from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """Create model from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

class IndexingMixin:
    """Mixin for indexing methods."""
    def index(self, indexer: Any) -> None:
        """Index the model."""
        if hasattr(self, 'index_fields'):
            for field in self.index_fields:
                value = getattr(self, field)
                if value is not None:
                    indexer.index_model(self, field, value)
    
    def unindex(self, indexer: Any) -> None:
        """Remove model from index."""
        if hasattr(self, 'index_fields'):
            for field in self.index_fields:
                value = getattr(self, field)
                if value is not None:
                    indexer.remove_index(self.__class__, field, value)

class LoggingMixin:
    """Mixin for logging methods."""
    def __init__(self, **data):
        super().__init__(**data)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def log_error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def log_warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def log_debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)

# Example usage:
"""
from datetime import datetime
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create model with mixins
class UserModel(
    OnyxBaseModel,
    TimestampMixin,
    SoftDeleteMixin,
    VersionMixin,
    AuditMixin,
    ValidationMixin,
    CacheMixin,
    SerializationMixin,
    IndexingMixin,
    LoggingMixin
):
    name: str
    email: str
    age: Optional[int] = None
    index_fields = ["email"]
    
    def __init__(self, **data):
        super().__init__(**data)
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.version = "1.0.0"

# Create and use model
user = UserModel(
    name="John",
    email="john@example.com",
    age=30
)

# Use mixin methods
user.set_audit_fields("user123")
user.cache("email")
user.log_info("User created successfully")

# Validate model
if user.is_valid():
    print("User is valid")
else:
    print("Validation errors:", user.validate())

# Serialize model
user_dict = user.to_dict()
user_json = user.to_json()

# Create from serialized data
new_user = UserModel.from_dict(user_dict)
new_user_from_json = UserModel.from_json(user_json)

# Soft delete
user.soft_delete()
print("Is deleted:", user.is_deleted)
print("Deleted at:", user.deleted_at)

# Restore
user.restore()
print("Is deleted:", user.is_deleted)
print("Deleted at:", user.deleted_at)

# Update version
user.update_version("1.1.0")
print("Current version:", user.version)
print("Previous version:", user.previous_version)
""" 