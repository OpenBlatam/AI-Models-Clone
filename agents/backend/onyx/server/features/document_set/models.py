from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator, field_validator, ConfigDict, model_validator
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog
import orjson

from onyx.db.models import DocumentSet as DocumentSetDBModel
from onyx.server.documents.models import ConnectorCredentialPairDescriptor
from onyx.server.documents.models import ConnectorSnapshot
from onyx.server.documents.models import CredentialSnapshot
from onyx.core.models import OnyxBaseModel

logger = structlog.get_logger()

class ORJSONModel(OnyxBaseModel):
    model_config = ConfigDict(json_loads=orjson.loads, json_dumps=orjson.dumps)

class DocumentSetCreationRequest(BaseModel):
    name: str
    description: str
    cc_pair_ids: list[int]
    is_public: bool
    # For Private Document Sets, who should be able to access these
    users: list[UUID] = Field(default_factory=list)
    groups: list[int] = Field(default_factory=list)


class DocumentSetUpdateRequest(BaseModel):
    id: int
    description: str
    cc_pair_ids: list[int]
    is_public: bool
    # For Private Document Sets, who should be able to access these
    users: list[UUID]
    groups: list[int]


class CheckDocSetPublicRequest(BaseModel):
    """Note that this does not mean that the Document Set itself is to be viewable by everyone
    Rather, this refers to the CC-Pairs in the Document Set, and if every CC-Pair is public
    """

    document_set_ids: list[int]


class CheckDocSetPublicResponse(BaseModel):
    is_public: bool


class DocumentSet(ORJSONModel):
    """
    Modelo robusto de DocumentSet para producción.
    """
    id: UUID = Field(default_factory=uuid7)
    name: str = Field(..., min_length=2, max_length=128, description="Nombre del set de documentos")
    documents: list[str] = Field(default_factory=list, description="Lista de documentos")
    metadata: dict = Field(default_factory=dict, description="Metadatos adicionales")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str | None = Field(default=None, description="Usuario que creó el registro")
    updated_by: str | None = Field(default=None, description="Último usuario que modificó el registro")
    source: str | None = Field(default=None, description="Origen del dato (api, import, etc)")

    @field_validator('name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            logger.error("DocumentSet name validation failed", value=v)
            raise ValueError("Name must not be empty")
        return v

    @field_validator('documents')
    def documents_is_list(cls, v):
        if not isinstance(v, list):
            logger.error("DocumentSet documents validation failed", value=v)
            raise ValueError("Documents must be a list")
        return v

    @field_validator('metadata')
    def metadata_is_dict(cls, v):
        if not isinstance(v, dict):
            logger.error("DocumentSet metadata validation failed", value=v)
            raise ValueError("Metadata must be a dict")
        return v

    @model_validator(mode="after")
    def check_documents_and_metadata(self):
        if self.documents and not isinstance(self.metadata, dict):
            logger.warning("Metadata should be a dict if documents exist", documents=self.documents)
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
        logger.info("DocumentSet instantiated", id=str(self.id), name=self.name)

    @field_validator("documents", mode="before")
    @classmethod
    def list_or_empty(cls, v):
        return v or []

    @field_validator("metadata", mode="before")
    @classmethod
    def dict_or_empty(cls, v):
        return v or {}

    @classmethod
    def from_model(cls, document_set_model: DocumentSetDBModel) -> "DocumentSet":
        return cls(
            id=document_set_model.id,
            name=document_set_model.name,
            description=document_set_model.description,
            cc_pair_descriptors=[
                ConnectorCredentialPairDescriptor(
                    id=cc_pair.id,
                    name=cc_pair.name,
                    connector=ConnectorSnapshot.from_connector_db_model(
                        cc_pair.connector
                    ),
                    credential=CredentialSnapshot.from_credential_db_model(
                        cc_pair.credential
                    ),
                    access_type=cc_pair.access_type,
                )
                for cc_pair in document_set_model.connector_credential_pairs
            ],
            is_up_to_date=document_set_model.is_up_to_date,
            is_public=document_set_model.is_public,
            users=[user.id for user in document_set_model.users],
            groups=[group.id for group in document_set_model.groups],
        )

    class Config:
        frozen = True
        validate_assignment = True
