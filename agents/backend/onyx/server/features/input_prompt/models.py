from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator, field_validator, ConfigDict
from typing import Dict, Optional, Any
from datetime import datetime
import logging
import structlog
import orjson

from onyx.db.models import InputPrompt
from onyx.utils.logger import setup_logger
from onyx.core.models import OnyxBaseModel
from uuid6 import uuid7

logger = structlog.get_logger()


class CreateInputPromptRequest(BaseModel):
    prompt: str
    content: str
    is_public: bool


class UpdateInputPromptRequest(BaseModel):
    prompt: str
    content: str
    active: bool


class InputPromptResponse(BaseModel):
    id: int
    prompt: str
    content: str
    active: bool


class InputPromptSnapshot(BaseModel):
    id: int
    prompt: str
    content: str
    active: bool
    user_id: UUID | None
    is_public: bool

    @classmethod
    def from_model(cls, input_prompt: InputPrompt) -> "InputPromptSnapshot":
        return InputPromptSnapshot(
            id=input_prompt.id,
            prompt=input_prompt.prompt,
            content=input_prompt.content,
            active=input_prompt.active,
            user_id=input_prompt.user_id,
            is_public=input_prompt.is_public,
        )


class ORJSONModel(OnyxBaseModel):
    model_config = ConfigDict(json_loads=orjson.loads, json_dumps=orjson.dumps)


class InputPrompt(ORJSONModel):
    """InputPrompt domain model."""
    id: UUID = Field(default_factory=uuid7)
    prompt: str = Field(..., min_length=1)
    metadata: dict | None = Field(default_factory=dict)

    @field_validator('prompt')
    def prompt_not_empty(cls, v):
        if not v or not v.strip():
            logger.error("InputPrompt prompt validation failed", value=v)
            raise ValueError("Prompt must not be empty")
        return v

    @field_validator('metadata')
    def metadata_is_dict(cls, v):
        if not isinstance(v, dict):
            logger.error("InputPrompt metadata validation failed", value=v)
            raise ValueError("Metadata must be a dict")
        return v

    def __post_init_post_parse__(self):
        logger.info("InputPrompt instantiated", id=str(self.id), prompt=self.prompt)

    class Config:
        frozen = True
        validate_assignment = True
