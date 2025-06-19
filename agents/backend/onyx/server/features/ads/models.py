from onyx.core.models import OnyxBaseModel
from pydantic import field_validator, Field, ConfigDict, model_validator
from typing import Optional, Dict
from uuid import UUID, uuid4
import structlog
import orjson
from uuid6 import uuid7
from datetime import datetime

logger = structlog.get_logger()

class ORJSONModel(OnyxBaseModel):
    model_config = ConfigDict(json_loads=orjson.loads, json_dumps=orjson.dumps)

class Ad(ORJSONModel):
    """
    Modelo robusto de Ad para producción.
    """
    id: UUID = Field(default_factory=uuid7)
    title: str = Field(..., min_length=2, max_length=128, description="Título del anuncio")
    content: str = Field(..., min_length=1, description="Contenido del anuncio")
    metadata: dict | None = Field(default_factory=dict, description="Metadatos adicionales")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str | None = Field(default=None, description="Usuario que creó el registro")
    updated_by: str | None = Field(default=None, description="Último usuario que modificó el registro")
    source: str | None = Field(default=None, description="Origen del dato (api, import, etc)")

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

    @model_validator(mode="after")
    def check_title_and_content(self):
        if self.title and self.content and self.title in self.content:
            logger.warning("Content should not repeat the title", title=self.title)
        return self

    def audit_log(self):
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "source": self.source,
        }

    def to_dict(self):
        return self.model_dump()

    def to_json(self):
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str):
        return cls.model_validate_json(data)

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