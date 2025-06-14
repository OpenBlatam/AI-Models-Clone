"""
Base Model - Onyx Integration
Enhanced modular base model with mixins and utilities.
"""
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, ClassVar
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, ConfigDict, validator, root_validator
from pydantic.generics import GenericModel
import json
import hashlib
from .redis_indexer import RedisIndexer

T = TypeVar('T')

# Mixins for common functionality
class TimestampMixin:
    """Mixin for timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("updated_at", pre=True, always=True)
    def update_timestamp(cls, v: datetime) -> datetime:
        """Update timestamp on model changes."""
        return datetime.utcnow()

class IdentifierMixin:
    """Mixin for identifier fields."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: int = Field(default=1)
    
    def increment_version(self) -> None:
        """Increment the model version."""
        self.version += 1

class StatusMixin:
    """Mixin for status fields."""
    is_active: bool = Field(default=True)
    status: str = Field(default="active")
    
    def activate(self) -> None:
        """Activate the model."""
        self.is_active = True
        self.status = "active"
    
    def deactivate(self) -> None:
        """Deactivate the model."""
        self.is_active = False
        self.status = "inactive"

class IndexingMixin:
    """Mixin for indexing functionality."""
    index_fields: ClassVar[List[str]] = ["id"]
    search_fields: ClassVar[List[str]] = []
    cache_ttl: ClassVar[int] = 3600  # 1 hour default
    
    def get_index_data(self) -> Dict[str, Any]:
        """Get data for indexing."""
        return {
            field: getattr(self, field)
            for field in self.index_fields
            if hasattr(self, field)
        }
    
    def get_search_data(self) -> Dict[str, Any]:
        """Get data for searching."""
        return {
            field: getattr(self, field)
            for field in self.search_fields
            if hasattr(self, field)
        }
    
    def index(self, indexer: RedisIndexer) -> None:
        """Index the model."""
        indexer.index_model(
            model=self,
            model_name=self.__class__.__name__,
            index_fields=self.index_fields
        )
    
    def remove_index(self, indexer: RedisIndexer) -> None:
        """Remove model from index."""
        indexer.remove_model(
            model_name=self.__class__.__name__,
            model_id=self.id
        )
    
    def update_index(self, indexer: RedisIndexer) -> None:
        """Update model in index."""
        indexer.update_index(
            model=self,
            model_name=self.__class__.__name__,
            index_fields=self.index_fields
        )

class ValidationMixin:
    """Mixin for validation functionality."""
    def validate_fields(self) -> List[str]:
        """Validate model fields and return list of errors."""
        errors = []
        for field_name, field in self.model_fields.items():
            try:
                value = getattr(self, field_name)
                if field.is_required() and value is None:
                    errors.append(f"{field_name} is required")
            except Exception as e:
                errors.append(f"Error validating {field_name}: {str(e)}")
        return errors
    
    def is_valid(self) -> bool:
        """Check if the model is valid."""
        return len(self.validate_fields()) == 0

class SerializationMixin:
    """Mixin for serialization functionality."""
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary with metadata."""
        return {
            "id": self.id,
            "data": self.model_dump(),
            "metadata": {
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "version": self.version,
                "is_active": self.is_active,
                "hash": self.generate_hash()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OnyxBaseModel":
        """Create model from dictionary with metadata."""
        model_data = data["data"]
        metadata = data["metadata"]
        
        model = cls(**model_data)
        model.created_at = metadata["created_at"]
        model.updated_at = metadata["updated_at"]
        model.version = metadata["version"]
        model.is_active = metadata["is_active"]
        
        return model
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "OnyxBaseModel":
        """Create model from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def generate_hash(self) -> str:
        """Generate a unique hash for the model."""
        data = self.model_dump(exclude={"created_at", "updated_at"})
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

# Base model with all mixins
class OnyxBaseModel(
    BaseModel,
    TimestampMixin,
    IdentifierMixin,
    StatusMixin,
    IndexingMixin,
    ValidationMixin,
    SerializationMixin
):
    """Enhanced base model for Onyx with all mixins."""
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            uuid.UUID: str
        },
        validate_assignment=True,
        extra="forbid"
    )
    
    @root_validator(pre=True)
    def set_defaults(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set default values for model fields."""
        if "id" not in values:
            values["id"] = str(uuid.uuid4())
        if "created_at" not in values:
            values["created_at"] = datetime.utcnow()
        if "updated_at" not in values:
            values["updated_at"] = datetime.utcnow()
        return values

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