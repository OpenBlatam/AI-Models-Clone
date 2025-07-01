import pytest
from uuid6 import UUID, uuid7
from agents.backend.onyx.server.features.password.models import Password
from agents.backend.onyx.server.features.password.schemas import PasswordCreate, PasswordRead

def test_password_valid():
    pw = Password(value="supersecret", description="desc")
    assert isinstance(pw.id, UUID)
    assert pw.value == "supersecret"
    assert pw.description == "desc"

def test_password_empty_value_raises():
    with pytest.raises(ValueError):
        Password(value=" ", description=None)

def test_password_too_short_raises():
    with pytest.raises(ValueError):
        Password(value="short", description=None)

def test_password_serialization():
    pw = Password(value="supersecret", description=None)
    data = pw.model_dump_json()
    assert '"value":"supersecret"' in data

def test_password_create_valid():
    schema = PasswordCreate(value="supersecret", description=None)
    assert schema.value == "supersecret"

def test_password_create_invalid_value():
    with pytest.raises(ValueError):
        PasswordCreate(value=" ", description=None)
    with pytest.raises(ValueError):
        PasswordCreate(value="short", description=None)

def test_password_read_valid():
    schema = PasswordRead(id=uuid7(), description=None)
    assert isinstance(schema.id, UUID) 