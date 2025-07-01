import pytest
from uuid6 import UUID
from agents.backend.onyx.server.features.persona.models import Persona
from agents.backend.onyx.server.features.persona.schemas import PersonaCreate, PersonaRead

def test_persona_valid():
    persona = Persona(name="Ada Lovelace", description="Pioneer", attributes={"field": "math"})
    assert isinstance(persona.id, UUID)
    assert persona.name == "Ada Lovelace"
    assert persona.attributes == {"field": "math"}

def test_persona_empty_name_raises():
    with pytest.raises(ValueError):
        Persona(name="   ", description="Empty", attributes={})

def test_persona_attributes_not_dict():
    with pytest.raises(ValueError):
        Persona(name="Alan", description="Test", attributes=["not", "a", "dict"])

def test_persona_serialization():
    persona = Persona(name="Grace", description=None, attributes={})
    data = persona.model_dump_json()
    assert '"name":"Grace"' in data

def test_persona_create_valid():
    schema = PersonaCreate(name="Ada", description="Test")
    assert schema.name == "Ada"

def test_persona_create_invalid_name():
    with pytest.raises(ValueError):
        PersonaCreate(name="", description="Test")

def test_persona_read_valid():
    import uuid6
    schema = PersonaRead(id=uuid6.uuid7(), name="Alan", description=None, attributes={})
    assert schema.name == "Alan"
    assert isinstance(schema.id, type(uuid6.uuid7())) 