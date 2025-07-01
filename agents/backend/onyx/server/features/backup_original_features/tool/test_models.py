import pytest
from uuid6 import UUID, uuid7
from agents.backend.onyx.server.features.tool.models import Tool
from agents.backend.onyx.server.features.tool.schemas import ToolCreate, ToolRead

def test_tool_valid():
    tool = Tool(name="ToolX", config={"param": 1})
    assert isinstance(tool.id, UUID)
    assert tool.name == "ToolX"
    assert tool.config == {"param": 1}

def test_tool_empty_name_raises():
    with pytest.raises(ValueError):
        Tool(name=" ", config={})

def test_tool_config_not_dict():
    with pytest.raises(ValueError):
        Tool(name="ToolX", config=[1,2,3])

def test_tool_serialization():
    tool = Tool(name="ToolX", config={})
    data = tool.model_dump_json()
    assert '"name":"ToolX"' in data

def test_tool_create_valid():
    schema = ToolCreate(name="ToolX", config={})
    assert schema.name == "ToolX"

def test_tool_create_invalid_name():
    with pytest.raises(ValueError):
        ToolCreate(name=" ", config={})

def test_tool_create_config_not_dict():
    with pytest.raises(ValueError):
        ToolCreate(name="ToolX", config=[1,2,3])

def test_tool_read_valid():
    schema = ToolRead(id=uuid7(), name="ToolX", config={})
    assert schema.name == "ToolX"
    assert isinstance(schema.id, UUID) 