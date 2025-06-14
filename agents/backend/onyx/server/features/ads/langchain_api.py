"""
API endpoints for LangChain integration with Onyx ads functionality.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from .langchain_service import LangChainService
from .db_service import AdsDBService
from .storage_service import StorageService
from .config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/langchain", tags=["langchain"])

# Request/Response Models
class ContentRequest(BaseModel):
    content: str = Field(..., description="Content to process")
    num_variations: Optional[int] = Field(3, description="Number of variations to generate")

class AudienceRequest(BaseModel):
    content: str = Field(..., description="Content to analyze")
    target_audience: Optional[str] = Field(None, description="Target audience description")

class CompetitorRequest(BaseModel):
    content: str = Field(..., description="Content to analyze")
    competitor_urls: List[str] = Field(..., description="List of competitor URLs")

class PerformanceRequest(BaseModel):
    content_id: str = Field(..., description="Content ID")
    metrics: Dict[str, Any] = Field(..., description="Performance metrics")

class RecommendationRequest(BaseModel):
    content: str = Field(..., description="Content to analyze")
    context: Dict[str, Any] = Field(..., description="Additional context")

# Dependencies
async def get_langchain_service() -> LangChainService:
    settings = get_settings()
    return LangChainService(
        llm=settings.get_llm(),
        embeddings=settings.get_embeddings()
    )

async def get_db_service() -> AdsDBService:
    return AdsDBService()

async def get_storage_service() -> StorageService:
    return StorageService()

# Endpoints
@router.post("/generate-ads")
async def generate_ads(
    request: ContentRequest,
    langchain_service: LangChainService = Depends(get_langchain_service),
    db_service: AdsDBService = Depends(get_db_service)
):
    """Generate ads using LangChain."""
    try:
        ads = await langchain_service.generate_ads(
            content=request.content,
            num_ads=request.num_variations
        )
        
        # Store in database
        for ad in ads:
            await db_service.create_ads_generation(
                content=ad,
                metadata={"source": "langchain", "original_content": request.content}
            )
        
        return {"ads": ads}
    except Exception as e:
        logger.error(f"Error generating ads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-brand-voice")
async def analyze_brand_voice(
    request: ContentRequest,
    langchain_service: LangChainService = Depends(get_langchain_service)
):
    """Analyze brand voice using LangChain."""
    try:
        analysis = await langchain_service.analyze_brand_voice(request.content)
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing brand voice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize-content")
async def optimize_content(
    request: AudienceRequest,
    langchain_service: LangChainService = Depends(get_langchain_service)
):
    """Optimize content for target audience using LangChain."""
    try:
        optimized = await langchain_service.optimize_content(
            content=request.content,
            target_audience=request.target_audience
        )
        return {"optimized_content": optimized}
    except Exception as e:
        logger.error(f"Error optimizing content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-variations")
async def generate_variations(
    request: ContentRequest,
    langchain_service: LangChainService = Depends(get_langchain_service),
    db_service: AdsDBService = Depends(get_db_service)
):
    """Generate content variations using LangChain."""
    try:
        variations = await langchain_service.generate_content_variations(
            content=request.content,
            num_variations=request.num_variations
        )
        
        # Store in database
        for variation in variations:
            await db_service.create_ads_generation(
                content=variation,
                metadata={"source": "langchain", "original_content": request.content}
            )
        
        return {"variations": variations}
    except Exception as e:
        logger.error(f"Error generating variations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-audience")
async def analyze_audience(
    request: ContentRequest,
    langchain_service: LangChainService = Depends(get_langchain_service)
):
    """Analyze audience from content using LangChain."""
    try:
        analysis = await langchain_service.analyze_audience(request.content)
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing audience: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-recommendations")
async def generate_recommendations(
    request: RecommendationRequest,
    langchain_service: LangChainService = Depends(get_langchain_service)
):
    """Generate recommendations using LangChain."""
    try:
        recommendations = await langchain_service.generate_recommendations(
            content=request.content,
            context=request.context
        )
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-competitors")
async def analyze_competitors(
    request: CompetitorRequest,
    langchain_service: LangChainService = Depends(get_langchain_service)
):
    """Analyze competitor content using LangChain."""
    try:
        analysis = await langchain_service.analyze_competitor_content(
            content=request.content,
            competitor_urls=request.competitor_urls
        )
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing competitors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-performance")
async def track_performance(
    request: PerformanceRequest,
    langchain_service: LangChainService = Depends(get_langchain_service),
    db_service: AdsDBService = Depends(get_db_service)
):
    """Track content performance using LangChain."""
    try:
        analysis = await langchain_service.track_content_performance(
            content_id=request.content_id,
            metrics=request.metrics
        )
        
        # Store in database
        await db_service.create_ads_analytics(
            ads_generation_id=request.content_id,
            metrics=request.metrics,
            analysis=analysis
        )
        
        return analysis
    except Exception as e:
        logger.error(f"Error tracking performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 