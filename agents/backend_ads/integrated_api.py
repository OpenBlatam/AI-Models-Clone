"""
Integrated API that combines all backend functionality including:
- Ads generation
- Brand kit creation
- Background removal
- Key messages
- Website scraping
- LLM integration
"""
import os
import httpx
import logging
from contextlib import asynccontextmanager
import datetime
import traceback
import numpy as np
import cv2
import pyvips
import psutil
from loguru import logger
from fastapi import FastAPI, HTTPException, Body, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import base64
import io
from PIL import Image

# Import all necessary components
from models import (
    AdsIaRequest, 
    AdsResponse, 
    BrandKitResponse, 
    ErrorResponse, 
    RemoveBackgroundRequest
)
from scraper import get_website_text
from llm_interface import (
    generate_ads_lcel,
    generate_brand_kit_lcel,
    generate_custom_content_lcel,
    generate_ads_lcel_streaming,
    generate_ads_lcel_streaming_parallel,
    DEEPSEEK_API_KEY,
    DEEPSEEK_MODEL_NAME
)
from config import settings
from key_messages.api import router as key_messages_router
from key_messages.llm_service import LLMKeyMessageService
from key_messages.models import MessageType, MessageTone
from model_mapping import ModelAdapter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize rembg session
try:
    from rembg import remove, new_session
    rembg_session = new_session("u2netp")
    rembg_session_fast = new_session("u2netp")
    rembg_session_std = new_session("u2net")
except ImportError:
    remove = None
    logger.warning("rembg library not installed. Background removal will not be available.")

ERROR_LOG_PATH = "integrated_errors.log"

def log_error(input_info: str, exc: Exception) -> None:
    """Log errors to file with timestamp and traceback."""
    with open(ERROR_LOG_PATH, "a") as f:
        f.write(f"[{datetime.datetime.now()}] INPUT: {input_info}\nEXCEPTION: {exc}\nTRACE:\n{traceback.format_exc()}\n{'-'*60}\n")

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Initialize and cleanup application resources."""
    logger.info("Initializing application and HTTPX client...")
    app_instance.state.httpx_client = httpx.AsyncClient(timeout=120.0)
    
    if not DEEPSEEK_API_KEY:
        logger.critical("DEEPSEEK_API_KEY not configured. LLM functionality will not work.")
    else:
        logger.info(f"Configured to use DeepSeek with model: {DEEPSEEK_MODEL_NAME}")
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
            response = await app_instance.state.httpx_client.get(
                f"{settings.DEEPSEEK_API_URL}/models",
                headers=headers,
                timeout=5.0
            )
            if response.status_code == 200:
                logger.info("Successfully connected to DeepSeek API.")
            else:
                logger.warning(f"Could not confirm DeepSeek connection (status: {response.status_code}).")
        except Exception as e:
            logger.error(f"CRITICAL: Could not connect to DeepSeek API. Error: {e}")
    
    yield

    logger.info("Closing HTTPX client and finalizing application...")
    await app_instance.state.httpx_client.aclose()

# Initialize FastAPI app
app = FastAPI(
    title="Integrated Ads & Content Generation API",
    description="API for generating ads, brand kits, removing backgrounds, and managing key messages",
    version="2.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS", "GET", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
app.add_middleware(GZipMiddleware, minimum_size=100)

# Include routers
app.include_router(key_messages_router)

class IntegratedRequest(BaseModel):
    """Combined request model for all functionality."""
    url: Optional[str] = None
    type: Optional[str] = None
    prompt: Optional[str] = None
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    message: Optional[str] = None
    message_type: Optional[MessageType] = None
    tone: Optional[MessageTone] = None
    target_audience: Optional[str] = None
    context: Optional[str] = None
    keywords: Optional[List[str]] = None
    max_length: Optional[int] = 10000

@app.post("/api/integrated/generate")
async def integrated_generation(
    request: IntegratedRequest,
    file: Optional[UploadFile] = File(None)
):
    """
    Integrated endpoint that handles all types of generation requests.
    """
    try:
        # Handle background removal
        if file or request.image_url or request.image_base64:
            if remove is None:
                raise HTTPException(
                    status_code=503,
                    detail="Background removal not available. Please install rembg."
                )
            
            image_bytes = None
            if file:
                image_bytes = await file.read()
            elif request.image_url:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(request.image_url)
                    if resp.status_code != 200:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Failed to download image: {resp.status_code}"
                        )
                    image_bytes = resp.content
            elif request.image_base64:
                try:
                    image_bytes = base64.b64decode(request.image_base64)
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid base64: {str(e)}"
                    )

            # Process image
            try:
                img_vips = pyvips.Image.new_from_buffer(image_bytes, "", access="sequential")
                max_size = 256
                scale = min(max_size / img_vips.width, max_size / img_vips.height, 1.0)
                if scale < 1.0:
                    img_vips = img_vips.resize(scale)
                png_bytes = img_vips.write_to_buffer(".png")
                input_image = Image.open(io.BytesIO(png_bytes))
            except Exception as e:
                logger.warning(f"pyvips failed: {e}, falling back to OpenCV")
                arr = np.frombuffer(image_bytes, np.uint8)
                img_cv = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
                if img_cv is None:
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to decode image"
                    )
                max_size = 256
                h, w = img_cv.shape[:2]
                scale = min(max_size / h, max_size / w, 1.0)
                if scale < 1.0:
                    img_cv = cv2.resize(img_cv, (int(w * scale), int(h * scale)))
                img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
                input_image = Image.fromarray(img_rgb)

            # Remove background
            output_image = remove(input_image, session=rembg_session_fast)
            has_alpha = output_image.mode == "RGBA" and np.array(output_image)[..., 3].max() > 0
            buffered = io.BytesIO()
            if has_alpha:
                output_image.save(buffered, format="PNG")
                mime = "image/png"
            else:
                output_image = output_image.convert("RGB")
                output_image.save(buffered, format="JPEG", quality=90)
                mime = "image/jpeg"
            
            return {
                "type": "background_removal",
                "image_base64": base64.b64encode(buffered.getvalue()).decode("utf-8"),
                "mime": mime
            }

        # Handle key messages
        elif request.message and request.message_type and request.tone:
            llm_service = LLMKeyMessageService()
            response = await llm_service.generate_message(
                message=request.message,
                message_type=request.message_type,
                tone=request.tone,
                target_audience=request.target_audience,
                context=request.context,
                keywords=request.keywords,
                max_length=request.max_length
            )
            return {
                "type": "key_message",
                "content": response
            }

        # Handle ads and brand kit generation
        elif request.url:
            website_text = get_website_text(request.url)
            if not website_text:
                website_text = ""

            if request.prompt:
                content = await generate_custom_content_lcel(request.prompt, website_text)
                return {
                    "type": "custom_content",
                    "content": content
                }
            
            # Convert to main backend request format
            main_request = ModelAdapter.to_main_ads_request(
                AdsIaRequest(
                    url=request.url,
                    type=request.type or "ads",
                    prompt=request.prompt
                )
            )
            
            # Generate ads using main backend format
            if request.type == "brand-kit":
                response = await generate_brand_kit_lcel(website_text)
                return {
                    "type": "brand_kit",
                    "content": response
                }
            else:
                response = await generate_ads_lcel(website_text)
                return {
                    "type": "ads",
                    "content": response
                }

        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid request. Please provide either an image, message, or URL."
            )

    except Exception as e:
        log_error(str(request), e)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/api/integrated/stream")
async def integrated_stream(request: IntegratedRequest):
    """
    Streamed response endpoint for long-running operations.
    """
    try:
        if not request.url:
            raise HTTPException(
                status_code=400,
                detail="URL is required for streaming"
            )

        website_text = get_website_text(request.url)
        if not website_text:
            website_text = ""

        # Convert to main backend request format
        main_request = ModelAdapter.to_main_ads_request(
            AdsIaRequest(
                url=request.url,
                type=request.type or "ads",
                prompt=request.prompt
            )
        )

        async def content_generator():
            try:
                async for chunk in generate_ads_lcel_streaming(website_text):
                    yield f"data: {chunk}\n\n"
            except Exception as e:
                logger.error(f"Error in stream: {e}")
                yield f"data: {str(e)}\n\n"

        return StreamingResponse(
            content_generator(),
            media_type="text/event-stream"
        )

    except Exception as e:
        log_error(str(request), e)
        raise HTTPException(
            status_code=500,
            detail=f"Error in stream: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 