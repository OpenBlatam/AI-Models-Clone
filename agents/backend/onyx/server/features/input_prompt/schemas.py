import structlog
from pydantic import Field, field_validator, ConfigDict, BaseModel
from typing import Optional, Dict
from uuid import UUID
import orjson
from uuid6 import uuid7

logger = structlog.get_logger()

class ORJSONModel(BaseModel):
    model_config = ConfigDict(json_loads=orjson.loads, json_dumps=orjson.dumps)

class InputPromptCreate(ORJSONModel):
    """Schema for creating an InputPrompt (input)."""
    prompt: str = Field(..., min_length=1)
    metadata: dict | None = Field(default_factory=dict)

    @field_validator('prompt')
    def prompt_not_empty(cls, v):
        if not v or not v.strip():
            logger.error("InputPromptCreate prompt validation failed", value=v)
            raise ValueError("Prompt must not be empty")
        return v

    def __post_init_post_parse__(self):
        logger.info("InputPromptCreate instantiated", prompt=self.prompt)

class InputPromptRead(ORJSONModel):
    """Schema for reading an InputPrompt (output)."""
    id: UUID
    prompt: str
    metadata: dict | None

    def __post_init_post_parse__(self):
        logger.info("InputPromptRead instantiated", id=str(self.id), prompt=self.prompt) 