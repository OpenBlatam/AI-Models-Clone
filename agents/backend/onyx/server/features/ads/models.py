from onyx.core.models import OnyxBaseModel
from pydantic import field_validator, Field, ConfigDict
from typing import Optional, Dict
from uuid import UUID, uuid4
import structlog
import orjson
from uuid6 import uuid7

logger = structlog.get_logger()

class ORJSONModel(OnyxBaseModel):
    model_config = ConfigDict(json_loads=orjson.loads, json_dumps=orjson.dumps)

class Ad(ORJSONModel):
    """Ad domain model."""
    id: UUID = Field(default_factory=uuid7)
    title: str = Field(..., min_length=2, max_length=128)
    content: str = Field(..., min_length=1)
    metadata: dict | None = Field(default_factory=dict)

    @field_validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            logger.error("Ad title validation failed", value=v)
            raise ValueError("Title must not be empty")
        return v

    @field_validator('content')
    def content_not_empty(cls, v):
        if not v or not v.strip():
            logger.error("Ad content validation failed", value=v)
            raise ValueError("Content must not be empty")
        return v

    @field_validator('metadata')
    def metadata_is_dict(cls, v):
        if not isinstance(v, dict):
            logger.error("Ad metadata validation failed", value=v)
            raise ValueError("Metadata must be a dict")
        return v

    def __post_init_post_parse__(self):
        logger.info("Ad instantiated", id=str(self.id), title=self.title)

    class Config:
        frozen = True
        validate_assignment = True

    @field_validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title must not be empty')
        return v
    @field_validator('content')
    def content_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Content must not be empty')
        return v 