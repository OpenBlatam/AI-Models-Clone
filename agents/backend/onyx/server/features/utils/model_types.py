"""
Model Types - Onyx Integration
Type definitions for model operations.
"""
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

# Type variables
T = TypeVar('T', bound='OnyxBaseModel')
M = TypeVar('M', bound='OnyxBaseModel')

# Basic types
JsonDict = Dict[str, Any]
JsonList = List[Any]
JsonValue = Union[str, int, float, bool, None, JsonDict, JsonList]

# Field types
FieldType = Union[str, int, float, bool, datetime, None]
FieldValue = Union[FieldType, List[FieldType], Dict[str, FieldType]]

# Model types
ModelId = Union[str, int]
ModelKey = str
ModelValue = Any
ModelData = Dict[str, Any]
ModelList = List[T]
ModelDict = Dict[ModelKey, T]

# Index types
IndexField = str
IndexValue = Any
IndexKey = str
IndexData = Dict[IndexField, IndexValue]
IndexList = List[IndexData]
IndexDict = Dict[IndexKey, IndexData]

# Cache types
CacheKey = str
CacheValue = Any
CacheData = Dict[CacheKey, CacheValue]
CacheList = List[CacheData]
CacheDict = Dict[CacheKey, CacheData]

# Validation types
ValidationRule = Dict[str, Any]
ValidationRules = Dict[str, ValidationRule]
ValidationError = str
ValidationErrors = List[ValidationError]

# Event types
EventName = str
EventData = Dict[str, Any]
EventHandler = Any
EventHandlers = Dict[EventName, List[EventHandler]]

# Status types
class ModelStatus(str, Enum):
    """Model status types."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"
    ARCHIVED = "archived"
    DRAFT = "draft"
    PUBLISHED = "published"
    PENDING = "pending"
    REJECTED = "rejected"
    APPROVED = "approved"

# Category types
class ModelCategory(str, Enum):
    """Model category types."""
    USER = "user"
    PRODUCT = "product"
    ORDER = "order"
    CUSTOMER = "customer"
    INVENTORY = "inventory"
    PAYMENT = "payment"
    SHIPPING = "shipping"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    SYSTEM = "system"

# Permission types
class ModelPermission(str, Enum):
    """Model permission types."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    OWNER = "owner"
    VIEWER = "viewer"
    EDITOR = "editor"
    MANAGER = "manager"

# Base model types
class OnyxBaseModel(BaseModel):
    """Base model type."""
    id: Optional[ModelId] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: ModelStatus = Field(default=ModelStatus.ACTIVE)
    category: ModelCategory = Field(default=ModelCategory.SYSTEM)
    permission: ModelPermission = Field(default=ModelPermission.VIEWER)
    version: str = Field(default="1.0.0")
    metadata: Optional[JsonDict] = None

# Model field types
class ModelField(BaseModel):
    """Model field type."""
    name: str
    type: str
    required: bool = False
    unique: bool = False
    default: Optional[Any] = None
    validation: Optional[ValidationRules] = None
    description: Optional[str] = None

# Model schema types
class ModelSchema(BaseModel):
    """Model schema type."""
    name: str
    fields: Dict[str, ModelField]
    indexes: Optional[List[IndexField]] = None
    cache: Optional[List[CacheKey]] = None
    validation: Optional[ValidationRules] = None
    events: Optional[EventHandlers] = None

# Model registry types
class ModelRegistry(BaseModel):
    """Model registry type."""
    models: Dict[str, Type[T]]
    schemas: Dict[str, ModelSchema]
    indexes: Dict[str, List[IndexField]]
    cache: Dict[str, List[CacheKey]]
    events: Dict[str, EventHandlers]

# Model cache types
class ModelCache(BaseModel):
    """Model cache type."""
    key: CacheKey
    value: CacheValue
    ttl: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Model index types
class ModelIndex(BaseModel):
    """Model index type."""
    field: IndexField
    value: IndexValue
    model_id: ModelId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Model event types
class ModelEvent(BaseModel):
    """Model event type."""
    name: EventName
    data: EventData
    model_id: ModelId
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Model validation types
class ModelValidation(BaseModel):
    """Model validation type."""
    rules: ValidationRules
    errors: ValidationErrors = Field(default_factory=list)
    is_valid: bool = Field(default=True)

# Model factory types
class ModelFactory(BaseModel):
    """Model factory type."""
    registry: ModelRegistry
    cache: Dict[CacheKey, ModelCache]
    indexes: Dict[IndexKey, ModelIndex]
    events: Dict[EventName, List[ModelEvent]]

# Example usage:
"""
from datetime import datetime
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create model with types
class UserModel(OnyxBaseModel):
    name: str
    email: str
    age: Optional[int] = None
    
    # Define schema
    schema = ModelSchema(
        name="user",
        fields={
            "name": ModelField(
                name="name",
                type="string",
                required=True,
                description="User's full name"
            ),
            "email": ModelField(
                name="email",
                type="string",
                required=True,
                unique=True,
                description="User's email address"
            ),
            "age": ModelField(
                name="age",
                type="integer",
                required=False,
                description="User's age"
            )
        },
        indexes=["email"],
        cache=["id", "email"],
        validation={
            "email": {
                "type": "string",
                "format": "email",
                "required": True
            },
            "age": {
                "type": "integer",
                "minimum": 0,
                "maximum": 150
            }
        }
    )
    
    def validate(self) -> ModelValidation:
        validation = ModelValidation(rules=self.schema.validation)
        
        # Validate email
        if not self.email or "@" not in self.email:
            validation.errors.append("Invalid email format")
            validation.is_valid = False
        
        # Validate age
        if self.age is not None and (self.age < 0 or self.age > 150):
            validation.errors.append("Age must be between 0 and 150")
            validation.is_valid = False
        
        return validation
    
    def get_indexes(self) -> List[ModelIndex]:
        indexes = []
        for field in self.schema.indexes:
            value = getattr(self, field)
            if value is not None:
                indexes.append(
                    ModelIndex(
                        field=field,
                        value=value,
                        model_id=self.id
                    )
                )
        return indexes
    
    def get_cache(self) -> List[ModelCache]:
        cache = []
        for key in self.schema.cache:
            value = getattr(self, key)
            if value is not None:
                cache.append(
                    ModelCache(
                        key=str(value),
                        value=self.model_dump()
                    )
                )
        return cache

# Create and use model with types
try:
    user = UserModel(
        name="John",
        email="john@example.com",
        age=30
    )
    
    # Validate
    validation = user.validate()
    if not validation.is_valid:
        logger.error(f"Validation errors: {validation.errors}")
    
    # Get indexes
    indexes = user.get_indexes()
    logger.info(f"Indexes: {indexes}")
    
    # Get cache
    cache = user.get_cache()
    logger.info(f"Cache: {cache}")
    
except Exception as e:
    logger.error(f"Error: {str(e)}")
""" 