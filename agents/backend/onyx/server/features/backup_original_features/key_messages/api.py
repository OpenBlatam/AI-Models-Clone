"""
Key Messages API for Onyx.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import time
import logging

from onyx.server.auth_check import check_router_auth
from onyx.server.utils import BasicAuthenticationError
from onyx.utils.logger import setup_logger
from onyx.core.auth import get_current_user
from onyx.core.functions import format_response, handle_error
from onyx.server.features.key_messages.models import (
    KeyMessageRequest,
    KeyMessageResponse,
    MessageType,
    MessageTone,
    BatchKeyMessageRequest,
    BatchKeyMessageResponse
)
from onyx.server.features.key_messages.service import KeyMessageService

logger = setup_logger(__name__)

# Initialize router
router = APIRouter(prefix="/key-messages", tags=["key-messages"])

# Initialize service
service = KeyMessageService()

@router.post("/generate", response_model=KeyMessageResponse)
async def generate_response(
    request: KeyMessageRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate a key message response."""
    try:
        logger.info(f"Generating response for user {current_user.get('id')}")
        response = await service.generate_response(request)
        return response
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=KeyMessageResponse)
async def analyze_message(
    request: KeyMessageRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze a message and return insights."""
    try:
        logger.info(f"Analyzing message for user {current_user.get('id')}")
        analysis = await service.analyze_message(request)
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=BatchKeyMessageResponse)
async def generate_batch(
    request: BatchKeyMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate responses for multiple messages in batch."""
    try:
        logger.info(f"Batch generation for user {current_user.get('id')} - {len(request.messages)} messages")
        result = await service.generate_batch(request)
        return result
    except Exception as e:
        logger.error(f"Error in batch generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types", response_model=List[str])
async def get_message_types(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get available message types."""
    try:
        return [mt.value for mt in MessageType]
    except Exception as e:
        logger.error(f"Error getting message types: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tones", response_model=List[str])
async def get_message_tones(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get available message tones."""
    try:
        return [mt.value for mt in MessageTone]
    except Exception as e:
        logger.error(f"Error getting message tones: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache")
async def clear_cache(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Clear all caches."""
    try:
        logger.info(f"Clearing cache for user {current_user.get('id')}")
        await service.clear_cache()
        return {"status": "success", "message": "All caches cleared"}
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/stats")
async def get_cache_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get cache statistics."""
    try:
        stats = await service.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        return {
            "status": "healthy",
            "service": "key-messages",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoints for backward compatibility
@router.post("/generate-legacy")
async def generate_response_legacy(
    request: KeyMessageRequest,
    background_tasks: BackgroundTasks,
    http_request: Any = Depends(check_router_auth)
):
    """Legacy endpoint for generating responses (without user authentication)."""
    try:
        logger.info("Legacy generation request")
        response = await service.generate_response(request)
        return response
    except Exception as e:
        logger.error(f"Error in legacy generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-legacy")
async def analyze_message_legacy(
    request: KeyMessageRequest,
    background_tasks: BackgroundTasks,
    http_request: Any = Depends(check_router_auth)
):
    """Legacy endpoint for analyzing messages (without user authentication)."""
    try:
        logger.info("Legacy analysis request")
        analysis = await service.analyze_message(request)
        return analysis
    except Exception as e:
        logger.error(f"Error in legacy analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 