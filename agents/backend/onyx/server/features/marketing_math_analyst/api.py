from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict

from .analyst import MarketingMathAnalyst, AnalysisRequest, AnalysisResult
from .researcher import Researcher
from .social_connectors import TikTokConnector, FacebookConnector, YouTubeAdsConnector

router = APIRouter(prefix="/marketing-analyst", tags=["marketing-analyst"])

# Dependency Injection Setup
# In a real app, these would come from config/env vars
OPENROUTER_KEY = "mock_key"
TRUTHGPT_URL = "http://localhost:8000"

def get_analyst():
    researcher = Researcher(OPENROUTER_KEY, TRUTHGPT_URL)
    return MarketingMathAnalyst(researcher)

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_content(
    request: AnalysisRequest,
    analyst: MarketingMathAnalyst = Depends(get_analyst)
):
    """
    Analyze text or content using Marketing Math principles.
    """
    try:
        result = await analyst.analyze_campaign(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connect/{platform}")
async def connect_platform(platform: str, api_key: str):
    """
    Test connection to a social media platform.
    """
    try:
        if platform == "tiktok":
            connector = TikTokConnector(api_key)
        elif platform == "facebook":
            connector = FacebookConnector(api_key)
        elif platform == "youtube":
            connector = YouTubeAdsConnector(api_key)
        else:
            raise HTTPException(status_code=400, detail="Unsupported platform")
            
        # Just a simple connectivity check (mocked)
        insights = await connector.get_audience_insights()
        return {"status": "connected", "platform": platform, "insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
