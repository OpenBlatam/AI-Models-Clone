from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator, field_validator, ConfigDict, model_validator
from typing import List, Optional
from datetime import datetime
import logging
import structlog
import orjson

from onyx.server.query_and_chat.models import ChatSessionDetails
from onyx.core.models import OnyxBaseModel

logger = structlog.get_logger()


class UserFolderSnapshot(BaseModel):
    folder_id: int
    folder_name: str | None
    display_priority: int
    chat_sessions: list[ChatSessionDetails]


class GetUserFoldersResponse(BaseModel):
    folders: list[UserFolderSnapshot]


class FolderCreationRequest(BaseModel):
    folder_name: str | None = None


class FolderUpdateRequest(BaseModel):
    folder_name: str | None = None


class FolderChatSessionRequest(BaseModel):
    chat_session_id: UUID


class DeleteFolderOptions(BaseModel):
    including_chats: bool = False


class ORJSONModel(OnyxBaseModel):
    model_config = ConfigDict(json_loads=orjson.loads, json_dumps=orjson.dumps)


class Folder(ORJSONModel):
    """
    Modelo robusto de Folder para producción.
    """
    id: UUID = Field(default_factory=uuid7)
    name: str = Field(..., min_length=2, max_length=128, description="Nombre de la carpeta")
    parent_id: UUID | None = Field(default=None, description="ID de la carpeta padre")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str | None = Field(default=None, description="Usuario que creó el registro")
    updated_by: str | None = Field(default=None, description="Último usuario que modificó el registro")
    source: str | None = Field(default=None, description="Origen del dato (api, import, etc)")

    @field_validator('name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            logger.error("Folder name validation failed", value=v)
            raise ValueError("Name must not be empty")
        return v

    @model_validator(mode="after")
    def check_name_and_parent(self):
        if self.parent_id and self.id == self.parent_id:
            logger.warning("Folder cannot be its own parent", id=str(self.id))
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

    class Config:
        frozen = True
        validate_assignment = True
