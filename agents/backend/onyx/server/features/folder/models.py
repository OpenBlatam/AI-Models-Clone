from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator, field_validator, ConfigDict
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
    """Folder domain model."""
    id: UUID = Field(default_factory=uuid7)
    name: str = Field(..., min_length=2, max_length=128)
    parent_id: Optional[UUID] = None
    children: List[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            logger.error("Folder name validation failed", value=v)
            raise ValueError("Name must not be empty")
        return v

    @field_validator("children", mode="before")
    @classmethod
    def list_or_empty(cls, v):
        return v or []

    def __post_init_post_parse__(self):
        logger.info("Folder instantiated", id=str(self.id), name=self.name)

    class Config:
        frozen = True
        validate_assignment = True
