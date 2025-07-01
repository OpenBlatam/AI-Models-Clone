"""
API endpoints for AI operations.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from ...services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])

class ContentRequest(BaseModel):
    content: str
    num_variations: int = 3

class AudienceRequest(BaseModel):
    content: str
    target_audience: str

class CompetitorRequest(BaseModel):
    content: str
    competitor_urls: List[str]

class MetricsRequest(BaseModel):
    content_id: str
    metrics: Dict[str, Any]

class ContextRequest(BaseModel):
    content: str
    context: Dict[str, Any]

@router.post("/generate-ads")
async def generate_ads(request: ContentRequest):
    """Generate ads from content."""
    try:
        service = AIService()
        ads = await service.generate_ads(request.content, request.num_variations)
        return {"ads": ads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-brand-voice")
async def analyze_brand_voice(request: ContentRequest):
    """Analyze brand voice from content."""
    try:
        service = AIService()
        analysis = await service.analyze_brand_voice(request.content)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize-content")
async def optimize_content(request: AudienceRequest):
    """Optimize content for target audience."""
    try:
        service = AIService()
        optimized = await service.optimize_content(request.content, request.target_audience)
        return {"optimized_content": optimized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-variations")
async def generate_variations(request: ContentRequest):
    """Generate content variations."""
    try:
        service = AIService()
        variations = await service.generate_content_variations(request.content, request.num_variations)
        return {"variations": variations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-audience")
async def analyze_audience(request: ContentRequest):
    """Analyze audience from content."""
    try:
        service = AIService()
        analysis = await service.analyze_audience(request.content)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-recommendations")
async def generate_recommendations(request: ContextRequest):
    """Generate recommendations based on content and context."""
    try:
        service = AIService()
        recommendations = await service.generate_recommendations(request.content, request.context)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-competitors")
async def analyze_competitors(request: CompetitorRequest):
    """Analyze competitor content."""
    try:
        service = AIService()
        analysis = await service.analyze_competitor_content(request.content, request.competitor_urls)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-performance")
async def track_performance(request: MetricsRequest):
    """Track content performance."""
    try:
        service = AIService()
        analysis = await service.track_content_performance(request.content_id, request.metrics)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 