# app/models.py
from pydantic import BaseModel
from typing import Literal, Optional, List

class AdsIaBaseRequest(BaseModel):
    url: str

class AdsRequest(AdsIaBaseRequest):
    type: Literal["ads"]
    prompt: Optional[str] = None

class BrandKitRequest(AdsIaBaseRequest):
    type: Literal["brand-kit"]

class ContentGenerationRequest(AdsIaBaseRequest): # No se usa directamente, AdsIaRequest cubre esto
    type: Literal["ads"]
    prompt: str

class AdsIaRequest(BaseModel):
    url: str
    type: Literal["ads", "brand-kit"]
    prompt: Optional[str] = None

class AdsResponse(BaseModel):
    ads: List[str]

class BrandKitResponse(BaseModel):
    brandKit: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

class RemoveBackgroundRequest(BaseModel):
    image_url: str | None = None  # URL of the image to process
    image_base64: str | None = None  # Alternatively, a base64-encoded image