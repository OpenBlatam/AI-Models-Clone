from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID

class AdCreate(BaseModel):
    """Schema for creating an Ad (input)."""
    title: str = Field(..., min_length=2, max_length=128)
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict] = Field(default_factory=dict)

class AdRead(BaseModel):
    """Schema for reading an Ad (output)."""
    id: UUID
    title: str
    content: str
    metadata: Optional[Dict] 