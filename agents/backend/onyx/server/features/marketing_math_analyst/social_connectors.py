import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class SocialMediaConnector(ABC):
    """Abstract base class for social media connectors."""
    
    @abstractmethod
    async def get_campaign_data(self, campaign_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_audience_insights(self) -> Dict[str, Any]:
        pass

from .config import settings

class TikTokConnector(SocialMediaConnector):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TIKTOK_API_KEY

    async def get_campaign_data(self, campaign_id: str) -> Dict[str, Any]:
        logger.info(f"Fetching TikTok campaign: {campaign_id}")
        if self.api_key == "mock_key":
            logger.warning("Using Mock TikTok Data (No API Key provided)")
            return {
                "platform": "tiktok",
                "campaign_id": campaign_id,
                "views": 15000,
                "likes": 1200,
                "shares": 300,
                "conversion_rate": 0.025
            }
        # Implement real API call here
        return {}

    async def get_audience_insights(self) -> Dict[str, Any]:
        return {"demographics": "Gen Z", "top_interests": ["Music", "Comedy"]}

class FacebookConnector(SocialMediaConnector):
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or settings.FACEBOOK_ACCESS_TOKEN

    async def get_campaign_data(self, campaign_id: str) -> Dict[str, Any]:
        logger.info(f"Fetching FB campaign: {campaign_id}")
        if self.access_token == "mock_key":
             return {
                "platform": "facebook",
                "campaign_id": campaign_id,
                "impressions": 50000,
                "clicks": 800,
                "cpc": 0.45
            }
        return {}

    async def get_audience_insights(self) -> Dict[str, Any]:
        return {"demographics": "Mixed", "top_interests": ["Tech", "News"]}

class YouTubeAdsConnector(SocialMediaConnector):
    def __init__(self, client_secret: Optional[str] = None):
        self.client_secret = client_secret or settings.YOUTUBE_CLIENT_SECRET

    async def get_campaign_data(self, campaign_id: str) -> Dict[str, Any]:
        logger.info(f"Fetching YouTube campaign: {campaign_id}")
        if self.client_secret == "mock_key":
            return {
                "platform": "youtube",
                "campaign_id": campaign_id,
                "views": 25000,
                "view_rate": 0.35,
                "cpv": 0.05
            }
        return {}

    async def get_audience_insights(self) -> Dict[str, Any]:
        return {"demographics": "Broad", "top_interests": ["Education", "Entertainment"]}
