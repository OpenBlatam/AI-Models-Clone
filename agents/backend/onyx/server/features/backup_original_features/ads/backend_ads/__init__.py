"""
Backend Ads - ULTRA Fast Integration
Direct integration without any middleware.
"""
from .api import router as backend_ads_router
from .service import BackendAdsService

__all__ = ["backend_ads_router", "BackendAdsService"] 