from pydantic import BaseModel, Field, validator
from typing import Optional
from ...utils.base_model import OnyxBaseModel
from pydantic import field_validator
from uuid import UUID, uuid4
from datetime import datetime
import logging
import structlog
import orjson
from uuid6 import uuid7

logger = structlog.get_logger()


class UserResetRequest(BaseModel):
    user_email: str


class UserResetResponse(BaseModel):
    user_id: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class PasswordResetRequest(OnyxBaseModel):
    """Password reset request model with OnyxBaseModel, Pydantic v2, and orjson serialization."""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(...)
    token: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    @field_validator("token")
    @classmethod
    def token_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Token cannot be empty")
        return v.strip()


class ORJSONModel(OnyxBaseModel):
    model_config = ConfigDict(json_loads=orjson.loads, json_dumps=orjson.dumps)


class Password(ORJSONModel):
    """Production-grade Password domain model with strong validation and logging."""
    id: UUID = Field(default_factory=uuid7)
    value: str = Field(..., min_length=8, max_length=128)
    description: str | None = None

    def __repr__(self) -> str:
        return f"<Password id={self.id} description={self.description!r}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Password):
            return False
        return self.id == other.id and self.value == other.value

    @field_validator('value')
    def password_strong(cls, v):
        if not v or not v.strip():
            logger.error("Password value validation failed", value=v)
            raise ValueError("Password must not be empty")
        if len(v) < 8:
            logger.error("Password value validation failed: too short", value=v)
            raise ValueError("Password must be at least 8 characters")
        return v

    def __post_init_post_parse__(self):
        logger.info("Password instantiated", id=str(self.id), description=self.description)

    class Config:
        frozen = True
        validate_assignment = True
