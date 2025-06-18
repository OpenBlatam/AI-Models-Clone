"""
Base Model - Onyx Integration
Base model with validation, caching, events, and permissions.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
import time
from .base_types import CACHE_TTL, VALIDATION_TIMEOUT
from .validation_mixin import ValidationMixin
from .cache_mixin import CacheMixin
from .event_mixin import EventMixin
from .index_mixin import IndexMixin
from .permission_mixin import PermissionMixin
from .status_mixin import StatusMixin
from .model_field import ModelField, FieldConfig
from .model_schema import ModelSchema, SchemaConfig

T = TypeVar('T')

class OnyxBaseModel(ValidationMixin, CacheMixin, EventMixin, IndexMixin, PermissionMixin, StatusMixin):
    """Base model with validation, caching, events, and permissions."""
    
    def __init__(
        self,
        schema: ModelSchema,
        data: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None
    ):
        """Initialize model."""
        self.schema = schema
        self.id = id
        self._data = data or schema.get_defaults()
        self._cache = {}
        self._cache_timestamps = {}
    
    def validate(self) -> List[str]:
        """Validate model data."""
        return self.schema.validate(self._data)
    
    def get_field(self, field_name: str) -> Optional[Any]:
        """Get field value."""
        return self._data.get(field_name)
    
    def set_field(self, field_name: str, value: Any) -> None:
        """Set field value."""
        if field_name not in self.schema.fields:
            raise ValueError(f"Unknown field: {field_name}")
        
        field = self.schema.fields[field_name]
        errors = field.validate(value)
        
        if errors:
            raise ValueError(f"Invalid value for {field_name}: {', '.join(errors)}")
        
        self._data[field_name] = value
        self.clear_cache()
    
    def get_data(self) -> Dict[str, Any]:
        """Get all data."""
        return self._data.copy()
    
    def set_data(self, data: Dict[str, Any]) -> None:
        """Set all data."""
        errors = self.schema.validate(data)
        
        if errors:
            raise ValueError(f"Invalid data: {', '.join(errors)}")
        
        self._data = data.copy()
        self.clear_cache()
    
    @lru_cache(maxsize=128)
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = self.schema.to_dict(self._data)
        if self.id:
            result['id'] = self.id
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], schema: ModelSchema) -> OnyxBaseModel:
        """Create model from dictionary."""
        id = data.pop('id', None)
        model_data = schema.from_dict(data)
        return cls(schema=schema, data=model_data, id=id)
    
    def clear_cache(self) -> None:
        """Clear model cache."""
        self._cache.clear()
        self._cache_timestamps.clear()
        self.to_dict.cache_clear()
    
    def __getattr__(self, name: str) -> Any:
        """Get attribute."""
        if name in self.schema.fields:
            return self.get_field(name)
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute."""
        if name in self.schema.fields:
            self.set_field(name, value)
        else:
            super().__setattr__(name, value)
    
    def __eq__(self, other: Any) -> bool:
        """Check equality."""
        if not isinstance(other, OnyxBaseModel):
            return False
        return self.id == other.id and self._data == other._data
    
    def __hash__(self) -> int:
        """Get hash."""
        return hash((self.id, tuple(sorted(self._data.items()))))

# Generic model with type parameter
class OnyxGenericModel(GenericModel, Generic[T]):
    """Generic model for Onyx with type parameters."""
    
    data: T
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def create(cls, data: T, **metadata) -> "OnyxGenericModel[T]":
        """Create a generic model instance."""
        return cls(data=data, metadata=metadata)
    
    def update(self, data: T) -> None:
        """Update the model data."""
        self.data = data
        self.metadata["updated_at"] = datetime.utcnow()

# Example usage:
"""
from datetime import datetime, timedelta
from typing import List, Optional

# Create a model with specific mixins
class UserModel(
    OnyxBaseModel,
    TimestampMixin,
    IdentifierMixin,
    StatusMixin
):
    name: str
    email: str
    age: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    
    # Configure indexing
    index_fields = ["id", "email"]
    search_fields = ["name", "tags"]
    cache_ttl = 3600  # 1 hour
    
    @validator("email")
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()
    
    @validator("age")
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 0 or v > 150):
            raise ValueError("Invalid age")
        return v

# Create a model with all mixins
class ProductModel(OnyxBaseModel):
    name: str
    price: float
    category: str
    in_stock: bool = True
    
    # Configure indexing
    index_fields = ["id", "category"]
    search_fields = ["name"]
    
    @validator("price")
    def validate_price(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v

# Create a generic model
class UserData:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

user_data = UserData("John", "john@example.com")
generic_model = OnyxGenericModel.create(
    data=user_data,
    created_at=datetime.utcnow()
)

# Create and use models
user = UserModel(
    name="John Doe",
    email="john@example.com",
    age=30,
    tags=["premium", "verified"]
)

product = ProductModel(
    name="Laptop",
    price=999.99,
    category="Electronics"
)

# Use mixin functionality
user.activate()
user.increment_version()
user.index(RedisIndexer())

product.deactivate()
product.update_index(RedisIndexer())

# Serialize models
user_dict = user.to_dict()
user_json = user.to_json()

# Validate models
user_errors = user.validate_fields()
is_valid = user.is_valid()

# Use generic model
generic_model.update(UserData("John Updated", "john.updated@example.com"))
""" 