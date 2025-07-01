from fastapi import APIRouter, HTTPException
from .models import SEOScrapeRequest, SEOScrapeResponse
from .service import SEOService

router = APIRouter(prefix="/seo", tags=["seo"])

@router.post("/scrape", response_model=SEOScrapeResponse)
def scrape(request: SEOScrapeRequest):
    """Realiza scraping SEO de una URL."""
    response = SEOService.scrape(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return response 