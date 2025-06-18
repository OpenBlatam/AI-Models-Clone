import pytest
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..base_model import OnyxBaseModel
from ..model_utils import (
    get_model_class,
    get_model_schema,
    get_model_indexes,
    get_model_cache,
    get_model_events,
    create_model_instance,
    validate_model_instance,
    index_model_instance,
    cache_model_instance,
    get_model_events_for_instance,
    update_model_instance,
    delete_model_instance,
    restore_model_instance,
    get_model_instances,
    count_model_instances,
    search_model_instances,
    batch_create_model_instances,
    batch_update_model_instances,
    batch_delete_model_instances,
    batch_restore_model_instances,
    get_model_statistics,
    get_model_audit_log,
    get_model_versions,
    get_model_relationships,
    get_model_dependencies,
    get_model_references
)
from ..model_exceptions import (
    RegistryError,
    ValidationError,
    IndexingError,
    CacheError,
    SoftDeleteError
)

# Test model classes
class TestModel(OnyxBaseModel):
    """Test model for utility functionality."""
    name: str
    email: str
    age: Optional[int] = None
    tags: List[str] = []
    
    index_fields = ["id", "name", "email"]
    search_fields = ["name", "email", "tags"]

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

# Test model registry functions
def test_get_model_class():
    """Test getting model class by name."""
    model_class = get_model_class("TestModel")
    assert model_class == TestModel
    
    with pytest.raises(RegistryError):
        get_model_class("NonExistentModel")

def test_get_model_schema():
    """Test getting model schema by name."""
    schema = get_model_schema("TestModel")
    assert "name" in schema
    assert "email" in schema
    assert "age" in schema
    assert "tags" in schema
    
    with pytest.raises(RegistryError):
        get_model_schema("NonExistentModel")

def test_get_model_indexes():
    """Test getting model indexes by name."""
    indexes = get_model_indexes("TestModel")
    assert "id" in indexes
    assert "name" in indexes
    assert "email" in indexes
    
    with pytest.raises(RegistryError):
        get_model_indexes("NonExistentModel")

def test_get_model_cache():
    """Test getting model cache by name."""
    cache = get_model_cache("TestModel")
    assert isinstance(cache, list)
    
    with pytest.raises(RegistryError):
        get_model_cache("NonExistentModel")

def test_get_model_events():
    """Test getting model events by name."""
    events = get_model_events("TestModel")
    assert isinstance(events, dict)
    
    with pytest.raises(RegistryError):
        get_model_events("NonExistentModel")

# Test model instance functions
def test_create_model_instance(test_model_data):
    """Test creating model instance."""
    model = create_model_instance("TestModel", test_model_data)
    assert isinstance(model, TestModel)
    assert model.name == test_model_data["name"]
    assert model.email == test_model_data["email"]
    assert model.age == test_model_data["age"]
    assert model.tags == test_model_data["tags"]

def test_validate_model_instance(test_model):
    """Test validating model instance."""
    validation = validate_model_instance(test_model)
    assert validation.is_valid is True
    
    # Test invalid model
    test_model.email = "invalid-email"
    validation = validate_model_instance(test_model)
    assert validation.is_valid is False

def test_index_model_instance(test_model):
    """Test indexing model instance."""
    indexes = index_model_instance(test_model)
    assert len(indexes) > 0
    assert any(index.field == "id" for index in indexes)
    assert any(index.field == "name" for index in indexes)
    assert any(index.field == "email" for index in indexes)

def test_cache_model_instance(test_model):
    """Test caching model instance."""
    cache = cache_model_instance(test_model)
    assert len(cache) > 0

def test_get_model_events_for_instance(test_model):
    """Test getting model events for instance."""
    events = get_model_events_for_instance(test_model, "created")
    assert isinstance(events, list)

def test_update_model_instance(test_model):
    """Test updating model instance."""
    update_data = {
        "name": "Updated Name",
        "age": 31
    }
    update_model_instance(test_model, update_data)
    assert test_model.name == update_data["name"]
    assert test_model.age == update_data["age"]
    assert test_model.updated_at > test_model.created_at

def test_delete_model_instance(test_model):
    """Test deleting model instance."""
    delete_model_instance(test_model)
    assert test_model.is_deleted is True
    assert test_model.deleted_at is not None

def test_restore_model_instance(test_model):
    """Test restoring model instance."""
    test_model.soft_delete()
    restore_model_instance(test_model)
    assert test_model.is_deleted is False
    assert test_model.deleted_at is None

# Test batch operations
def test_batch_create_model_instances():
    """Test batch creating model instances."""
    data_list = [
        {
            "name": "User 1",
            "email": "user1@example.com",
            "age": 25
        },
        {
            "name": "User 2",
            "email": "user2@example.com",
            "age": 30
        }
    ]
    models = batch_create_model_instances("TestModel", data_list)
    assert len(models) == 2
    assert models[0].name == data_list[0]["name"]
    assert models[1].name == data_list[1]["name"]

def test_batch_update_model_instances(test_model):
    """Test batch updating model instances."""
    data_list = [
        {
            "id": test_model.id,
            "name": "Updated User 1",
            "age": 26
        }
    ]
    models = batch_update_model_instances("TestModel", data_list)
    assert len(models) == 1
    assert models[0].name == data_list[0]["name"]
    assert models[0].age == data_list[0]["age"]

# Test model statistics and metadata
def test_get_model_statistics():
    """Test getting model statistics."""
    stats = get_model_statistics("TestModel")
    assert isinstance(stats, dict)
    assert "total" in stats
    assert "active" in stats
    assert "deleted" in stats
    assert "created_today" in stats
    assert "updated_today" in stats

def test_get_model_audit_log(test_model):
    """Test getting model audit log."""
    log = get_model_audit_log("TestModel", test_model.id)
    assert isinstance(log, list)

def test_get_model_versions(test_model):
    """Test getting model versions."""
    versions = get_model_versions("TestModel", test_model.id)
    assert isinstance(versions, list)

def test_get_model_relationships(test_model):
    """Test getting model relationships."""
    relationships = get_model_relationships("TestModel", test_model.id)
    assert isinstance(relationships, dict)

def test_get_model_dependencies(test_model):
    """Test getting model dependencies."""
    dependencies = get_model_dependencies("TestModel", test_model.id)
    assert isinstance(dependencies, list)

def test_get_model_references(test_model):
    """Test getting model references."""
    references = get_model_references("TestModel", test_model.id)
    assert isinstance(references, list) 