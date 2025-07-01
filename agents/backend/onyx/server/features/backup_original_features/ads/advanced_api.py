"""
Advanced Onyx API endpoints for ads module.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from onyx.core.auth import get_current_user
from onyx.core.functions import format_response, handle_error
from onyx.server.features.ads.advanced import (
    AdvancedAdsService,
    AITrainingData,
    ContentOptimization,
    AudienceInsights,
    BrandVoiceAnalysis,
    ContentPerformance
)

router = APIRouter(prefix="/ads/advanced", tags=["ads-advanced"])

class TrainingDataRequest(BaseModel):
    """Request model for AI training data."""
    training_data: List[AITrainingData]

class ContentOptimizationRequest(BaseModel):
    """Request model for content optimization."""
    content: str
    optimization_type: str

class BrandVoiceAnalysisRequest(BaseModel):
    """Request model for brand voice analysis."""
    content_samples: List[str]

class CompetitorAnalysisRequest(BaseModel):
    """Request model for competitor analysis."""
    competitor_urls: List[str]

class ContentVariationsRequest(BaseModel):
    """Request model for content variations."""
    content: str
    variations: int = 3

@router.post("/train-ai")
async def train_ai_model(
    request: TrainingDataRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Train AI model with provided data."""
    try:
        service = AdvancedAdsService(request.app.state.httpx_client)
        result = await service.train_ai_model(request.training_data)
        return format_response(result)
    except Exception as e:
        raise handle_error(e)

@router.post("/optimize-content")
async def optimize_content(
    request: ContentOptimizationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Optimize content based on type."""
    try:
        service = AdvancedAdsService(request.app.state.httpx_client)
        result = await service.optimize_content(
            content=request.content,
            optimization_type=request.optimization_type
        )
        return format_response(result.dict())
    except Exception as e:
        raise handle_error(e)

@router.get("/audience/{segment_id}")
async def analyze_audience(
    segment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze audience segment."""
    try:
        service = AdvancedAdsService(request.app.state.httpx_client)
        result = await service.analyze_audience(segment_id)
        return format_response(result.dict())
    except Exception as e:
        raise handle_error(e)

@router.post("/brand-voice")
async def analyze_brand_voice(
    request: BrandVoiceAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze brand voice from content samples."""
    try:
        service = AdvancedAdsService(request.app.state.httpx_client)
        result = await service.analyze_brand_voice(request.content_samples)
        return format_response(result.dict())
    except Exception as e:
        raise handle_error(e)

@router.get("/performance/{content_id}")
async def track_content_performance(
    content_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Track content performance metrics."""
    try:
        service = AdvancedAdsService(request.app.state.httpx_client)
        result = await service.track_content_performance(content_id)
        return format_response(result.dict())
    except Exception as e:
        raise handle_error(e)

@router.post("/recommendations")
async def generate_ai_recommendations(
    content: str,
    context: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate AI-powered recommendations for content."""
    try:
        service = AdvancedAdsService(request.app.state.httpx_client)
        result = await service.generate_ai_recommendations(content, context)
        return format_response({"recommendations": result})
    except Exception as e:
        raise handle_error(e)

@router.get("/impact/{content_id}")
async def analyze_content_impact(
    content_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze content impact across channels."""
    try:
        service = AdvancedAdsService(request.app.state.httpx_client)
        result = await service.analyze_content_impact(content_id)
        return format_response(result)
    except Exception as e:
        raise handle_error(e)

@router.post("/audience/optimize/{segment_id}")
async def optimize_audience_targeting(
    segment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Optimize audience targeting for a segment."""
    try:
        service = AdvancedAdsService(request.app.state.httpx_client)
        result = await service.optimize_audience_targeting(segment_id)
        return format_response(result)
    except Exception as e:
        raise handle_error(e)

@router.post("/variations")
async def generate_content_variations(
    request: ContentVariationsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate variations of content for A/B testing."""
    try:
        service = AdvancedAdsService(request.app.state.httpx_client)
        result = await service.generate_content_variations(
            content=request.content,
            variations=request.variations
        )
        return format_response({"variations": result})
    except Exception as e:
        raise handle_error(e)

@router.post("/competitor")
async def analyze_competitor_content(
    request: CompetitorAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze competitor content and strategies."""
    try:
        service = AdvancedAdsService(request.app.state.httpx_client)
        result = await service.analyze_competitor_content(request.competitor_urls)
        return format_response(result)
    except Exception as e:
        raise handle_error(e) 