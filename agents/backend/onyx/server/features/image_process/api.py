"""
API endpoints for Image Process feature (Onyx).
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from .models import (
    ImageExtractRequest, ImageExtractResponse,
    ImageSummaryRequest, ImageSummaryResponse,
    ImageValidationRequest, ImageValidationResponse,
    ImageAnalysisResult
)
from .service import ImageProcessService
from onyx.core.auth import get_current_user

router = APIRouter(prefix="/image-process", tags=["image-process"])
service = ImageProcessService()

@router.post("/extract", response_model=ImageExtractResponse)
async def extract_text(request: ImageExtractRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Extract text from an image (URL o base64)."""
    response = service.extract_text(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return response

@router.post("/summarize", response_model=ImageSummaryResponse)
async def summarize_image(request: ImageSummaryRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Summarize the content of an image."""
    response = service.summarize(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return response

@router.post("/validate", response_model=ImageValidationResponse)
async def validate_image(request: ImageValidationRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Validate an image (format, content, etc)."""
    response = service.validate(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return response

@router.post("/analyze", response_model=ImageAnalysisResult)
def analyze_image(request: ImageExtractRequest):
    """Análisis avanzado de imagen (IA, OCR, detección de objetos, etc.)."""
    return ImageProcessService.analyze(request) 