# app/models.py
from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional, List

class AdsIaBaseRequest(BaseModel):
    url: HttpUrl

class AdsRequest(AdsIaBaseRequest):
    type: Literal["ads"]
    prompt: Optional[str] = None

class BrandKitRequest(AdsIaBaseRequest):
    type: Literal["brand-kit"]

class ContentGenerationRequest(AdsIaBaseRequest): # No se usa directamente, AdsIaRequest cubre esto
    type: Literal["ads"]
    prompt: str

class AdsIaRequest(BaseModel):
    url: HttpUrl
    type: Literal["ads", "brand-kit"]
    prompt: Optional[str] = None

class AdsResponse(BaseModel):
    ads: List[str]

class BrandKitResponse(BaseModel):
    brandKit: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None