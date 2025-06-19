from pydantic import BaseModel, Field, validator
from typing import Optional
from ...utils.base_model import OnyxBaseModel
from pydantic import field_validator, ConfigDict, model_validator
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
    """
    Modelo robusto de Password para producción.
    """
    id: UUID = Field(default_factory=uuid7)
    value: str = Field(..., min_length=8, max_length=128, description="Contraseña segura")
    description: str | None = Field(default=None, description="Descripción opcional")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str | None = Field(default=None, description="Usuario que creó el registro")
    updated_by: str | None = Field(default=None, description="Último usuario que modificó el registro")
    source: str | None = Field(default=None, description="Origen del dato (api, import, etc)")

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

    @model_validator(mode="after")
    def check_value_and_description(self):
        if self.value and self.description and self.value in (self.description or ""):
            logger.warning("Description should not contain the password value", value=self.value)
        return self

    def __post_init_post_parse__(self):
        logger.info("Password instantiated", id=str(self.id), description=self.description)

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
