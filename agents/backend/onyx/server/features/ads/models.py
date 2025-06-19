from onyx.core.models import OnyxBaseModel
from pydantic import field_validator, Field, ConfigDict, model_validator
from uuid import UUID
from uuid6 import uuid7
from datetime import datetime
import structlog
import orjson
from agents.backend.onyx.server.features.utils.ml_data_pipeline import send_training_example_kafka

logger = structlog.get_logger()

class ORJSONModel(OnyxBaseModel):
    model_config = ConfigDict(json_loads=orjson.loads, json_dumps=orjson.dumps)

class Ad(ORJSONModel):
    __slots__ = (
        'id', 'title', 'content', 'metadata', 'created_at', 'updated_at', 'created_by', 'updated_by',
        'source', 'version', 'trace_id', 'is_deleted'
    )
    id: UUID = Field(default_factory=uuid7)
    title: str = Field(..., min_length=2, max_length=128, description="Título del anuncio")
    content: str = Field(..., min_length=1, description="Contenido del anuncio")
    metadata: dict = Field(default_factory=dict, description="Metadatos adicionales")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str | None = None
    updated_by: str | None = None
    source: str | None = None
    version: int = 1
    trace_id: str | None = None
    is_deleted: bool = False

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

    @field_validator('metadata', mode="before")
    @classmethod
    def dict_or_empty(cls, v):
        return v or {}

    @model_validator(mode="after")
    def check_timestamps(self):
        if self.created_at > self.updated_at:
            logger.warning("created_at is after updated_at", id=str(self.id))
        return self

    def audit_log(self):
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "source": self.source,
            "version": self.version,
            "trace_id": self.trace_id,
            "is_deleted": self.is_deleted,
        }

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.updated_at = datetime.utcnow()
        self.version += 1
        logger.info("Ad updated", id=str(self.id), version=self.version, trace_id=self.trace_id)

    def soft_delete(self):
        self.is_deleted = True
        self.update()
        logger.info("Ad soft deleted", id=str(self.id), trace_id=self.trace_id)

    def restore(self):
        self.is_deleted = False
        self.update()
        logger.info("Ad restored", id=str(self.id), trace_id=self.trace_id)

    def to_dict(self):
        return self.model_dump()

    def to_json(self):
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str):
        return cls.model_validate_json(data)

    def to_training_example(self):
        return {
            "input": self.title,
            "output": self.content,
            "metadata": self.metadata,
        }

    @classmethod
    def from_training_example(cls, example: dict):
        return cls(title=example["input"], content=example["output"], metadata=example.get("metadata", {}))

    def send_to_kafka(self, topic="ml_training_examples", bootstrap_servers=None):
        """
        Envía este ejemplo a un topic de Kafka para el pipeline ML/LLM automatizado.
        """
        send_training_example_kafka(self, topic=topic, bootstrap_servers=bootstrap_servers)

    # Ejemplo de uso:
    # ad = Ad(title="Oferta", content="Descuento especial")
    # ad.send_to_kafka(topic="ml_training_examples", bootstrap_servers=["localhost:9092"])

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