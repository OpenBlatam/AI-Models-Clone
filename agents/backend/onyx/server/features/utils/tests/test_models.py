"""
Model Tests - Onyx Integration
Test suite for model operations and validations.
"""
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union, ClassVar
from datetime import datetime
import logging
import os
import pytest
from pydantic import BaseModel, ValidationError
from ..model_types import (
    JsonDict, JsonList, JsonValue, FieldType, FieldValue,
    ModelId, ModelKey, ModelValue, ModelData, ModelList, ModelDict,
    IndexField, IndexValue, IndexKey, IndexData, IndexList, IndexDict,
    CacheKey, CacheValue, CacheData, CacheList, CacheDict,
    ValidationRule, ValidationRules, ValidationError, ValidationErrors,
    EventName, EventData, EventHandler, EventHandlers,
    ModelStatus, ModelCategory, ModelPermission,
    OnyxBaseModel, ModelField, ModelSchema, ModelRegistry,
    ModelCache, ModelIndex, ModelEvent, ModelValidation, ModelFactory
)
from ..model_config import ModelConfig
from ..model_helpers import (
    validate_email, validate_url, validate_phone, validate_date, validate_datetime,
    validate_field_type, validate_field_value, validate_model_fields,
    create_model_index, create_model_cache, create_model_event,
    serialize_model, deserialize_model,
    get_model_indexes, get_model_cache, get_model_events,
    update_model_timestamps, update_model_status, update_model_version, update_model_metadata
)
from ..model_mixins import (
    TimestampMixin, SoftDeleteMixin, VersionMixin, AuditMixin,
    ValidationMixin, CacheMixin, SerializationMixin, IndexingMixin, LoggingMixin
)
from ..model_decorators import (
    register_model, cache_model, validate_model, track_changes,
    require_active, log_operations, enforce_version, validate_schema
)
from ..model_exceptions import (
    OnyxModelError, ValidationError, IndexingError, CacheError,
    SerializationError, VersionError, AuditError, SoftDeleteError,
    TimestampError, RegistryError, FactoryError
)

T = TypeVar('T', bound=OnyxBaseModel)

# Test fixtures
@pytest.fixture
def test_model_data():
    """Test model data fixture."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "age": 30,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "version": "1.0.0",
        "is_deleted": False,
        "deleted_at": None
    }

@pytest.fixture
def test_model(test_model_data):
    """Test model fixture."""
    return TestModel(**test_model_data)

# Test model
class TestModel(
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
    
    # Define schema
    schema: ClassVar[ModelSchema] = ModelSchema(
        name="test",
        fields={
            "name": ModelField(
                name="name",
                type="string",
                required=True,
                description="Test name"
            ),
            "email": ModelField(
                name="email",
                type="string",
                required=True,
                unique=True,
                description="Test email"
            ),
            "age": ModelField(
                name="age",
                type="integer",
                required=False,
                description="Test age"
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

# Test model creation
def test_create_model(test_model_data):
    """Test model creation."""
    model = TestModel(**test_model_data)
    assert model.name == test_model_data["name"]
    assert model.email == test_model_data["email"]
    assert model.age == test_model_data["age"]
    assert model.created_at is not None
    assert model.updated_at is not None
    assert model.version == "1.0.0"
    assert model.is_deleted is False
    assert model.deleted_at is None

# Test model validation
def test_validate_model_fields(test_model):
    """Test model fields validation."""
    validation = test_model.validate()
    assert len(validation) == 0
    
    # Test invalid email
    test_model.email = "invalid-email"
    validation = test_model.validate()
    assert len(validation) > 0
    assert any("email" in error for error in validation)
    
    # Test invalid age
    test_model.age = 200
    validation = test_model.validate()
    assert len(validation) > 0
    assert any("age" in error for error in validation)

# Test model operations
def test_model_operations(test_model):
    """Test model operations."""
    # Test update
    new_name = "Updated Name"
    test_model.name = new_name
    assert test_model.name == new_name
    assert test_model.updated_at is not None
    
    # Test soft delete
    test_model.soft_delete()
    assert test_model.is_deleted is True
    assert test_model.deleted_at is not None
    
    # Test restore
    test_model.restore()
    assert test_model.is_deleted is False
    assert test_model.deleted_at is None

# Test model serialization
def test_serialize_model(test_model):
    """Test model serialization."""
    data = test_model.to_dict()
    assert data["name"] == test_model.name
    assert data["email"] == test_model.email
    assert data["age"] == test_model.age
    assert data["created_at"] is not None
    assert data["updated_at"] is not None
    assert data["version"] == test_model.version
    assert data["is_deleted"] == test_model.is_deleted
    assert data["deleted_at"] == test_model.deleted_at

# Test model deserialization
def test_deserialize_model(test_model_data):
    """Test model deserialization."""
    model = TestModel.from_dict(test_model_data)
    assert model.name == test_model_data["name"]
    assert model.email == test_model_data["email"]
    assert model.age == test_model_data["age"]

# Test model caching
def test_model_cache(test_model):
    """Test model caching."""
    # Test cache set
    test_model.cache("email")
    # Note: Actual cache implementation would be tested here
    # This is just a placeholder for the cache functionality

# Test model indexing
def test_model_index(test_model):
    """Test model indexing."""
    # Test index set
    test_model.index(None)  # Pass None as indexer since we're not implementing actual indexing
    # Note: Actual index implementation would be tested here
    # This is just a placeholder for the indexing functionality

# Test model mixins
def test_model_mixins(test_model):
    """Test model mixins."""
    # Test TimestampMixin
    assert test_model.created_at is not None
    assert test_model.updated_at is not None
    test_model.update_timestamp()
    assert test_model.updated_at is not None
    
    # Test SoftDeleteMixin
    assert test_model.is_deleted is False
    test_model.soft_delete()
    assert test_model.is_deleted is True
    test_model.restore()
    assert test_model.is_deleted is False
    
    # Test VersionMixin
    assert test_model.version is not None
    test_model.update_version("2.0.0")
    assert test_model.version == "2.0.0"
    
    # Test AuditMixin
    test_model.set_audit_fields("test_user")
    assert test_model.created_by == "test_user"
    assert test_model.updated_by == "test_user"
    
    # Test ValidationMixin
    assert test_model.is_valid() is True
    test_model.email = "invalid-email"
    assert test_model.is_valid() is False
    
    # Test CacheMixin
    test_model.cache("email")
    # Note: Actual cache implementation would be tested here
    
    # Test SerializationMixin
    data = test_model.to_dict()
    assert isinstance(data, dict)
    json_str = test_model.to_json()
    assert isinstance(json_str, str)
    
    # Test IndexingMixin
    test_model.index(None)  # Pass None as indexer
    # Note: Actual index implementation would be tested here
    
    # Test LoggingMixin
    test_model.log_info("Test info message")
    test_model.log_error("Test error message")
    test_model.log_warning("Test warning message")
    test_model.log_debug("Test debug message")

# Test validation
def test_validate_email():
    """Test email validation."""
    assert TestModel(email="test@example.com").is_valid() is True
    assert TestModel(email="invalid-email").is_valid() is False

def test_validate_age():
    """Test age validation."""
    assert TestModel(name="Test", email="test@example.com", age=30).is_valid() is True
    assert TestModel(name="Test", email="test@example.com", age=200).is_valid() is False
    assert TestModel(name="Test", email="test@example.com", age=-1).is_valid() is False

def test_validate_url():
    """Test URL validation."""
    assert validate_url("https://example.com") is True
    assert validate_url("invalid-url") is False

def test_validate_phone():
    """Test phone validation."""
    assert validate_phone("+1234567890") is True
    assert validate_phone("invalid-phone") is False

def test_validate_date():
    """Test date validation."""
    assert validate_date("2024-01-01") is True
    assert validate_date("invalid-date") is False

def test_validate_datetime():
    """Test datetime validation."""
    assert validate_datetime("2024-01-01T12:00:00Z") is True
    assert validate_datetime("invalid-datetime") is False

def test_validate_field_type():
    """Test field type validation."""
    assert validate_field_type("test", "string") is True
    assert validate_field_type(123, "integer") is True
    assert validate_field_type(123.45, "float") is True
    assert validate_field_type(True, "boolean") is True
    assert validate_field_type([1, 2, 3], "array") is True
    assert validate_field_type({"key": "value"}, "object") is True
    assert validate_field_type("test@example.com", "email") is True
    assert validate_field_type("https://example.com", "url") is True
    assert validate_field_type("+1234567890", "phone") is True
    assert validate_field_type("2024-01-01", "date") is True
    assert validate_field_type("2024-01-01T12:00:00Z", "datetime") is True
    assert validate_field_type("test", "invalid") is False

def test_validate_field_value():
    """Test field value validation."""
    # Test required field
    errors = validate_field_value(None, {"required": True})
    assert len(errors) > 0
    
    # Test type validation
    errors = validate_field_value("test", {"type": "integer"})
    assert len(errors) > 0
    
    # Test minimum value
    errors = validate_field_value(5, {"type": "integer", "minimum": 10})
    assert len(errors) > 0
    
    # Test maximum value
    errors = validate_field_value(20, {"type": "integer", "maximum": 10})
    assert len(errors) > 0
    
    # Test min length
    errors = validate_field_value("test", {"type": "string", "min_length": 10})
    assert len(errors) > 0
    
    # Test max length
    errors = validate_field_value("test" * 10, {"type": "string", "max_length": 10})
    assert len(errors) > 0
    
    # Test pattern
    errors = validate_field_value("test", {"type": "string", "pattern": r"^\d+$"})
    assert len(errors) > 0
    
    # Test enum
    errors = validate_field_value("test", {"type": "string", "enum": ["value1", "value2"]})
    assert len(errors) > 0

def test_validate_model_fields(test_model):
    """Test model fields validation."""
    validation = validate_model_fields(test_model, test_model.schema)
    assert validation.is_valid is True
    
    # Test invalid email
    test_model.email = "invalid-email"
    validation = validate_model_fields(test_model, test_model.schema)
    assert validation.is_valid is False
    
    # Test invalid age
    test_model.age = 200
    validation = validate_model_fields(test_model, test_model.schema)
    assert validation.is_valid is False

# Test model operations
def test_create_model_index(test_model):
    """Test model index creation."""
    index = create_model_index(test_model, "email", test_model.email)
    assert index.field == "email"
    assert index.value == test_model.email
    assert index.model_id == test_model.id

def test_create_model_cache(test_model):
    """Test model cache creation."""
    cache = create_model_cache(test_model, "email", test_model.email)
    assert cache.key == "email"
    assert cache.value == test_model.email

def test_create_model_event(test_model):
    """Test model event creation."""
    event = create_model_event(test_model, "created", {"action": "create"})
    assert event.name == "created"
    assert event.data["action"] == "create"
    assert event.model_id == test_model.id

def test_serialize_model(test_model):
    """Test model serialization."""
    data = serialize_model(test_model)
    assert data["name"] == test_model.name
    assert data["email"] == test_model.email
    assert data["age"] == test_model.age

def test_deserialize_model(test_model_data):
    """Test model deserialization."""
    model = deserialize_model(TestModel, test_model_data)
    assert model.name == test_model_data["name"]
    assert model.email == test_model_data["email"]
    assert model.age == test_model_data["age"]

def test_get_model_indexes(test_model):
    """Test model indexes retrieval."""
    indexes = get_model_indexes(test_model, test_model.schema)
    assert len(indexes) == 1
    assert indexes[0].field == "email"
    assert indexes[0].value == test_model.email

def test_get_model_cache(test_model):
    """Test model cache retrieval."""
    cache = get_model_cache(test_model, test_model.schema)
    assert len(cache) == 2
    assert any(c.key == str(test_model.id) for c in cache)
    assert any(c.key == test_model.email for c in cache)

def test_get_model_events(test_model):
    """Test model events retrieval."""
    events = get_model_events(test_model, test_model.schema, "created")
    assert len(events) == 0  # No event handlers defined

# Test model updates
def test_update_model_timestamps(test_model):
    """Test model timestamps update."""
    update_model_timestamps(test_model)
    assert test_model.created_at is not None
    assert test_model.updated_at is not None

def test_update_model_status(test_model):
    """Test model status update."""
    update_model_status(test_model, ModelStatus.INACTIVE)
    assert test_model.status == ModelStatus.INACTIVE

def test_update_model_version(test_model):
    """Test model version update."""
    update_model_version(test_model, "1.1.0")
    assert test_model.version == "1.1.0"

def test_update_model_metadata(test_model):
    """Test model metadata update."""
    metadata = {"source": "test", "tags": ["test"]}
    update_model_metadata(test_model, metadata)
    assert test_model.metadata == metadata

# Test model decorators
def test_register_model():
    """Test model registration."""
    assert TestModel in ModelRegistry.models.values()

def test_cache_model(test_model):
    """Test model caching."""
    @cache_model("email")
    def test_method(self):
        return self.email
    
    test_method(test_model)

def test_validate_model(test_model):
    """Test model validation."""
    @validate_model(validate_types=True, validate_custom=True)
    def test_method(self):
        return self.email
    
    test_method(test_model)
    
    test_model.email = "invalid-email"
    with pytest.raises(ValidationError):
        test_method(test_model)

def test_track_changes(test_model):
    """Test change tracking."""
    @track_changes
    def test_method(self):
        self.name = "Updated Name"
    
    test_method(test_model)
    assert test_model.name == "Updated Name"

def test_require_active(test_model):
    """Test active requirement."""
    @require_active
    def test_method(self):
        return self.email
    
    test_method(test_model)
    
    test_model.status = ModelStatus.INACTIVE
    with pytest.raises(ValueError):
        test_method(test_model)

def test_log_operations(test_model):
    """Test operation logging."""
    @log_operations(logging.getLogger(__name__))
    def test_method(self):
        return self.email
    
    test_method(test_model)

def test_enforce_version(test_model):
    """Test version enforcement."""
    @enforce_version("1.0.0")
    def test_method(self):
        return self.email
    
    test_method(test_model)
    
    test_model.version = "1.1.0"
    with pytest.raises(ValueError):
        test_method(test_model)

def test_validate_schema(test_model):
    """Test schema validation."""
    @validate_schema(test_model.schema.validation)
    def test_method(self):
        return self.email
    
    test_method(test_model)
    
    test_model.email = "invalid-email"
    with pytest.raises(ValidationError):
        test_method(test_model)

# Test model exceptions
def test_validation_error():
    """Test validation error."""
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError("Validation failed", ["Invalid email"])
    assert str(exc_info.value) == "Validation failed"
    assert exc_info.value.errors == ["Invalid email"]

def test_indexing_error():
    """Test indexing error."""
    with pytest.raises(IndexingError) as exc_info:
        raise IndexingError("Indexing failed", "email", "test@example.com")
    assert str(exc_info.value) == "Indexing failed"
    assert exc_info.value.field == "email"
    assert exc_info.value.value == "test@example.com"

def test_cache_error():
    """Test cache error."""
    with pytest.raises(CacheError) as exc_info:
        raise CacheError("Caching failed", "email")
    assert str(exc_info.value) == "Caching failed"
    assert exc_info.value.key == "email"

def test_serialization_error():
    """Test serialization error."""
    with pytest.raises(SerializationError) as exc_info:
        raise SerializationError("Serialization failed", {"key": "value"})
    assert str(exc_info.value) == "Serialization failed"
    assert exc_info.value.data == {"key": "value"}

def test_version_error():
    """Test version error."""
    with pytest.raises(VersionError) as exc_info:
        raise VersionError("Version mismatch", "1.0.0", "1.1.0")
    assert str(exc_info.value) == "Version mismatch"
    assert exc_info.value.current_version == "1.0.0"
    assert exc_info.value.required_version == "1.1.0"

def test_audit_error():
    """Test audit error."""
    with pytest.raises(AuditError) as exc_info:
        raise AuditError("Audit failed", "user123")
    assert str(exc_info.value) == "Audit failed"
    assert exc_info.value.user_id == "user123"

def test_soft_delete_error():
    """Test soft delete error."""
    with pytest.raises(SoftDeleteError) as exc_info:
        raise SoftDeleteError("Soft delete failed", True)
    assert str(exc_info.value) == "Soft delete failed"
    assert exc_info.value.is_deleted is True

def test_timestamp_error():
    """Test timestamp error."""
    with pytest.raises(TimestampError) as exc_info:
        raise TimestampError("Timestamp error", "2024-01-01")
    assert str(exc_info.value) == "Timestamp error"
    assert exc_info.value.timestamp == "2024-01-01"

def test_registry_error():
    """Test registry error."""
    with pytest.raises(RegistryError) as exc_info:
        raise RegistryError("Registry error", "TestModel")
    assert str(exc_info.value) == "Registry error"
    assert exc_info.value.model_name == "TestModel"

def test_factory_error():
    """Test factory error."""
    with pytest.raises(FactoryError) as exc_info:
        raise FactoryError("Factory error", TestModel)
    assert str(exc_info.value) == "Factory error"
    assert exc_info.value.model_type == TestModel 