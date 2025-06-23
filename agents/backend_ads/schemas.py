from pydantic import BaseModel, root_validator
from typing import List, Dict, Any, Optional, Union
from validators import validate_urls_http

class BatchScrapeRequest(BaseModel):
    urls: List[str]

    @root_validator(pre=True)
    def validate_urls(cls, values):
        urls = values.get('urls', [])
        validate_urls_http(urls)
        return values

class BatchScrapeResult(BaseModel):
    trace_id: str
    results: Dict[str, Union[str, Dict[str, Any]]]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Any] = None

class AdsIaRequest(BaseModel):
    url: str
    type: str
    prompt: Optional[str] = None
    website_content: Optional[str] = None

class AdsResponse(BaseModel):
    ads: List[str]

class BrandKitResponse(BaseModel):
    brandKit: str

class AdsIaStreamRequest(BaseModel):
    url: str
    n_ads: Optional[int] = 1
    max_length: Optional[int] = 800
    website_content: Optional[str] = None 