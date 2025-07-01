"""
API endpoints for integrated Onyx and ads functionality.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from ...services.integrated_service import IntegratedService
from ..config.providers import ProvidersConfig

router = APIRouter(prefix="/integrated", tags=["integrated"])

class ContentRequest(BaseModel):
    content: str
    context: Dict[str, Any] = {}

class CompetitorRequest(BaseModel):
    content: str
    competitor_urls: List[str]

class MetricsRequest(BaseModel):
    content_id: str
    metrics: Dict[str, Any]

@router.post("/process-content")
async def process_content(request: ContentRequest):
    """Process content using Onyx capabilities."""
    try:
        service = IntegratedService()
        result = await service.process_content(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-ads")
async def generate_ads(request: ContentRequest):
    """Generate ads using content and context."""
    try:
        service = IntegratedService()
        ads = await service.generate_ads_with_context(request.content, request.context)
        return {"ads": ads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-competitors")
async def analyze_competitors(request: CompetitorRequest):
    """Analyze competitors using Onyx capabilities."""
    try:
        service = IntegratedService()
        analysis = await service.analyze_competitors_with_onyx(
            request.content,
            request.competitor_urls
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-performance")
async def track_performance(request: MetricsRequest):
    """Track performance using Onyx capabilities."""
    try:
        service = IntegratedService()
        analysis = await service.track_performance_with_onyx(
            request.content_id,
            request.metrics
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 