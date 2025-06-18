import pytest
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID

from ..model_types import (
    ModelStatus,
    ModelCategory,
    ModelPermission,
    ModelRegistry,
    OnyxBaseModel,
    ModelField,
    ModelSchema,
    ModelCache,
    ModelIndex,
    ModelEvent,
    ModelValidation,
    ModelFactory
)

# Test model classes
class TestModel(OnyxBaseModel):
    """Test model for type functionality."""
    name: str
    email: str
    age: Optional[int] = None
    tags: List[str] = []

@pytest.fixture
def test_model_data():
    """Create test model data."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "age": 30,
        "tags": ["test", "example"]
    }

@pytest.fixture
def test_model(test_model_data):
    """Create a test model instance."""
    return TestModel(**test_model_data)

# Test enums
def test_model_status():
    """Test model status enum."""
    assert ModelStatus.ACTIVE == "active"
    assert ModelStatus.INACTIVE == "inactive"
    assert ModelStatus.DELETED == "deleted"
    assert ModelStatus.ARCHIVED == "archived"
    assert ModelStatus.DRAFT == "draft"
    assert ModelStatus.PUBLISHED == "published"
    assert ModelStatus.PENDING == "pending"
    assert ModelStatus.REJECTED == "rejected"
    assert ModelStatus.APPROVED == "approved"

def test_model_category():
    """Test model category enum."""
    assert ModelCategory.USER == "user"
    assert ModelCategory.PRODUCT == "product"
    assert ModelCategory.ORDER == "order"
    assert ModelCategory.CUSTOMER == "customer"
    assert ModelCategory.INVENTORY == "inventory"
    assert ModelCategory.PAYMENT == "payment"
    assert ModelCategory.SHIPPING == "shipping"
    assert ModelCategory.MARKETING == "marketing"
    assert ModelCategory.ANALYTICS == "analytics"
    assert ModelCategory.SYSTEM == "system"

def test_model_permission():
    """Test model permission enum."""
    assert ModelPermission.READ == "read"
    assert ModelPermission.WRITE == "write"
    assert ModelPermission.DELETE == "delete"
    assert ModelPermission.ADMIN == "admin"
    assert ModelPermission.OWNER == "owner"
    assert ModelPermission.VIEWER == "viewer"
    assert ModelPermission.EDITOR == "editor"
    assert ModelPermission.MANAGER == "manager"

# Test model registry
def test_model_registry():
    """Test model registry."""
    # Register model
    ModelRegistry.register(TestModel)
    
    # Get model
    model_class = ModelRegistry.get_model("testmodel")
    assert model_class == TestModel
    
    # List models
    models = ModelRegistry.list_models()
    assert "testmodel" in models

# Test base model
def test_onyx_base_model(test_model):
    """Test OnyxBaseModel functionality."""
    # Test default values
    assert isinstance(test_model.id, str)
    assert isinstance(test_model.created_at, datetime)
    assert isinstance(test_model.updated_at, datetime)
    assert test_model.status == ModelStatus.ACTIVE
    assert test_model.category == ModelCategory.SYSTEM
    assert test_model.permission == ModelPermission.VIEWER
    assert test_model.version == "1.0.0"
    assert test_model.is_deleted is False
    assert test_model.deleted_at is None
    
    # Test is_active property
    assert test_model.is_active is True
    
    # Test validation
    assert test_model.is_valid() is True
    
    # Test status change
    test_model.status = ModelStatus.INACTIVE
    assert test_model.is_active is False
    
    # Test soft delete
    test_model.is_deleted = True
    test_model.deleted_at = datetime.utcnow()
    assert test_model.is_active is False

# Test model field
def test_model_field():
    """Test ModelField functionality."""
    field = ModelField(
        name="test_field",
        type="string",
        required=True,
        unique=True,
        description="Test field",
        default="default",
        validation={"min_length": 2}
    )
    
    assert field.name == "test_field"
    assert field.type == "string"
    assert field.required is True
    assert field.unique is True
    assert field.description == "Test field"
    assert field.default == "default"
    assert field.validation == {"min_length": 2}

# Test model schema
def test_model_schema():
    """Test ModelSchema functionality."""
    schema = ModelSchema(
        name="test_schema",
        fields={
            "name": ModelField(name="name", type="string", required=True),
            "email": ModelField(name="email", type="string", required=True)
        },
        indexes=["name", "email"],
        cache=["id", "email"],
        validation={
            "name": {"min_length": 2},
            "email": {"pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}
        }
    )
    
    assert schema.name == "test_schema"
    assert "name" in schema.fields
    assert "email" in schema.fields
    assert "name" in schema.indexes
    assert "email" in schema.indexes
    assert "id" in schema.cache
    assert "email" in schema.cache
    assert "name" in schema.validation
    assert "email" in schema.validation

# Test model cache
def test_model_cache():
    """Test ModelCache functionality."""
    cache = ModelCache(
        key="test_key",
        value={"name": "Test", "value": 42},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    assert cache.key == "test_key"
    assert cache.value["name"] == "Test"
    assert cache.value["value"] == 42
    assert isinstance(cache.created_at, datetime)
    assert isinstance(cache.updated_at, datetime)

# Test model index
def test_model_index():
    """Test ModelIndex functionality."""
    index = ModelIndex(
        field="name",
        value="Test",
        model_id="123",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    assert index.field == "name"
    assert index.value == "Test"
    assert index.model_id == "123"
    assert isinstance(index.created_at, datetime)
    assert isinstance(index.updated_at, datetime)

# Test model event
def test_model_event():
    """Test ModelEvent functionality."""
    event = ModelEvent(
        name="created",
        data={"action": "create"},
        model_id="123"
    )
    
    assert event.name == "created"
    assert event.data["action"] == "create"
    assert event.model_id == "123"
    assert isinstance(event.created_at, datetime)

# Test model validation
def test_model_validation():
    """Test ModelValidation functionality."""
    validation = ModelValidation(
        is_valid=True,
        errors=[]
    )
    
    assert validation.is_valid is True
    assert len(validation.errors) == 0
    
    validation = ModelValidation(
        is_valid=False,
        errors=["Invalid email", "Invalid age"]
    )
    
    assert validation.is_valid is False
    assert len(validation.errors) == 2
    assert "Invalid email" in validation.errors
    assert "Invalid age" in validation.errors

# Test model factory
def test_model_factory():
    """Test ModelFactory functionality."""
    # Register model
    ModelRegistry.register(TestModel)
    
    # Create model
    model = ModelFactory.create("testmodel", name="Test", email="test@example.com")
    assert isinstance(model, TestModel)
    assert model.name == "Test"
    assert model.email == "test@example.com"
    
    # Validate model
    validation = ModelFactory.validate("testmodel", name="Test", email="invalid-email")
    assert validation.is_valid is False
    assert len(validation.errors) > 0 