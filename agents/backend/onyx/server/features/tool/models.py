"""
Tool Models - Onyx Integration
Enhanced models for tools with advanced features.
"""
from typing import Dict, List, Optional, Union, Any, TypeVar, Generic
from datetime import datetime
from pydantic import Field, validator, root_validator
from ...utils.base_model import OnyxBaseModel
from uuid import uuid4

T = TypeVar('T')

class Header(OnyxBaseModel):
    """Enhanced header model."""
    
    key: str
    value: str
    description: Optional[str] = None
    is_required: bool = Field(default=False)
    is_secret: bool = Field(default=False)
    
    # Configure indexing
    index_fields = ["key"]
    search_fields = ["description"]
    
    @validator("key")
    def validate_key(cls, v: str) -> str:
        """Validate header key."""
        if not v.strip():
            raise ValueError("Header key cannot be empty")
        return v.strip()
    
    @validator("value")
    def validate_value(cls, v: str) -> str:
        """Validate header value."""
        if not v.strip():
            raise ValueError("Header value cannot be empty")
        return v.strip()

class ToolDefinition(OnyxBaseModel):
    """Enhanced tool definition model."""
    
    name: str
    version: str
    description: str
    category: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    headers: List[Header] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Configure indexing
    index_fields = ["name", "version", "category"]
    search_fields = ["description", "input_schema", "output_schema"]
    
    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate tool name."""
        if not v.strip():
            raise ValueError("Tool name cannot be empty")
        return v.strip()
    
    @validator("version")
    def validate_version(cls, v: str) -> str:
        """Validate version format."""
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError("Version must be in format: major.minor.patch")
        try:
            [int(p) for p in parts]
        except ValueError:
            raise ValueError("Version parts must be integers")
        return v
    
    @validator("category")
    def validate_category(cls, v: str) -> str:
        """Validate category."""
        allowed_categories = ["api", "utility", "integration", "custom"]
        if v not in allowed_categories:
            raise ValueError(f"Category must be one of: {', '.join(allowed_categories)}")
        return v
    
    def get_required_headers(self) -> List[Header]:
        """Get required headers."""
        return [h for h in self.headers if h.is_required]
    
    def get_secret_headers(self) -> List[Header]:
        """Get secret headers."""
        return [h for h in self.headers if h.is_secret]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data against schema."""
        # TODO: Implement schema validation
        return True
    
    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """Validate output data against schema."""
        # TODO: Implement schema validation
        return True

class ToolSnapshot(OnyxBaseModel):
    """Enhanced tool snapshot model."""
    
    id: str
    name: str
    version: str
    description: str
    category: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    headers: List[Header]
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    # Configure indexing
    index_fields = ["id", "name", "version", "category"]
    search_fields = ["description"]
    
    @classmethod
    def from_definition(cls, definition: ToolDefinition) -> "ToolSnapshot":
        """Create snapshot from definition."""
        return cls(
            id=str(uuid4()),
            name=definition.name,
            version=definition.version,
            description=definition.description,
            category=definition.category,
            input_schema=definition.input_schema,
            output_schema=definition.output_schema,
            headers=definition.headers,
            parameters=definition.parameters,
            metadata=definition.metadata,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    def to_definition(self) -> ToolDefinition:
        """Convert snapshot to definition."""
        return ToolDefinition(
            name=self.name,
            version=self.version,
            description=self.description,
            category=self.category,
            input_schema=self.input_schema,
            output_schema=self.output_schema,
            headers=self.headers,
            parameters=self.parameters,
            metadata=self.metadata
        )

class CustomToolCreate(OnyxBaseModel):
    """Enhanced custom tool creation model."""
    
    definition: ToolDefinition
    is_public: bool = Field(default=False)
    owner_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Configure indexing
    index_fields = ["owner_id"]
    search_fields = ["definition"]
    
    @validator("definition")
    def validate_definition(cls, v: ToolDefinition) -> ToolDefinition:
        """Validate tool definition."""
        if not v.name or not v.version:
            raise ValueError("Tool definition must have name and version")
        return v

class ToolUpdate(OnyxBaseModel):
    """Enhanced tool update model."""
    
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    headers: Optional[List[Header]] = None
    parameters: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Configure indexing
    index_fields = ["name", "version", "category"]
    search_fields = ["description"]
    
    @validator("name")
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate tool name."""
        if v is not None and not v.strip():
            raise ValueError("Tool name cannot be empty")
        return v.strip() if v else v
    
    @validator("version")
    def validate_version(cls, v: Optional[str]) -> Optional[str]:
        """Validate version format."""
        if v is not None:
            parts = v.split(".")
            if len(parts) != 3:
                raise ValueError("Version must be in format: major.minor.patch")
            try:
                [int(p) for p in parts]
            except ValueError:
                raise ValueError("Version parts must be integers")
        return v
    
    @validator("category")
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        """Validate category."""
        if v is not None:
            allowed_categories = ["api", "utility", "integration", "custom"]
            if v not in allowed_categories:
                raise ValueError(f"Category must be one of: {', '.join(allowed_categories)}")
        return v

# Example usage:
"""
# Create header
header = Header(
    key="Authorization",
    value="Bearer token123",
    description="API authentication token",
    is_required=True,
    is_secret=True
)

# Create tool definition
tool_def = ToolDefinition(
    name="Weather API",
    version="1.0.0",
    description="Get weather information for a location",
    category="api",
    input_schema={
        "type": "object",
        "properties": {
            "location": {"type": "string"},
            "units": {"type": "string", "enum": ["metric", "imperial"]}
        },
        "required": ["location"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "temperature": {"type": "number"},
            "humidity": {"type": "number"},
            "description": {"type": "string"}
        }
    },
    headers=[header],
    parameters={
        "base_url": "https://api.weather.com",
        "timeout": 30
    }
)

# Create tool snapshot
snapshot = ToolSnapshot.from_definition(tool_def)

# Create custom tool
custom_tool = CustomToolCreate(
    definition=tool_def,
    is_public=True,
    owner_id="user123"
)

# Update tool
tool_update = ToolUpdate(
    name="Weather API v2",
    version="2.0.0",
    description="Enhanced weather information API"
)

# Index models
redis_indexer = RedisIndexer()
tool_def.index(redis_indexer)
snapshot.index(redis_indexer)
custom_tool.index(redis_indexer)
"""
