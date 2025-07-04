"""
Video Processing API

FastAPI-based API for video processing with LangChain integration.
Enhanced with intelligent content analysis and optimization for short-form videos.
"""

from __future__ import annotations
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import time
import asyncio

from .models.video_models import (
    VideoClipRequest,
    VideoClipResponse,
    VideoClipBatchRequest,
    VideoClipBatchResponse
)
from .models.viral_models import (
    ViralVideoVariant,
    ViralVideoBatchResponse,
    ViralCaptionConfig,
    LangChainAnalysis,
    ContentOptimization,
    ShortVideoOptimization,
    ContentType,
    EngagementType,
    create_default_caption_config
)
from .processors.video_processor import VideoProcessor, VideoProcessorConfig
from .processors.viral_processor import ViralVideoProcessor, ViralProcessorConfig
from .processors.langchain_processor import (
    LangChainVideoProcessor,
    LangChainConfig,
    create_langchain_processor,
    create_optimized_langchain_processor
)
from .processors.batch_processor import BatchVideoProcessor, BatchProcessorConfig
from .utils.parallel_utils import HybridParallelProcessor, ParallelConfig

logger = structlog.get_logger()

# =============================================================================
# API CONFIGURATION
# =============================================================================

app = FastAPI(
    title="Video Processing API",
    description="Advanced video processing with LangChain integration for intelligent content optimization",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================

def get_video_processor() -> VideoProcessor:
    """Get video processor instance."""
    config = VideoProcessorConfig(
        max_workers=4,
        batch_size=5,
        enable_audit_logging=True
    )
    return VideoProcessor(config)

def get_viral_processor() -> ViralVideoProcessor:
    """Get viral processor instance."""
    config = ViralProcessorConfig(
        max_variants=10,
        enable_langchain=True,
        enable_screen_division=True,
        enable_transitions=True,
        enable_effects=True
    )
    return ViralVideoProcessor(config)

def get_langchain_processor() -> LangChainVideoProcessor:
    """Get LangChain processor instance."""
    config = LangChainConfig(
        model_name="gpt-4",
        enable_content_analysis=True,
        enable_engagement_analysis=True,
        enable_viral_analysis=True,
        enable_title_optimization=True,
        enable_caption_optimization=True,
        enable_timing_optimization=True,
        batch_size=5,
        max_retries=3,
        use_agents=True,
        use_memory=True
    )
    return LangChainVideoProcessor(config)

def get_batch_processor() -> BatchVideoProcessor:
    """Get batch processor instance."""
    config = BatchProcessorConfig(
        max_workers=8,
        batch_size=10,
        enable_parallel_processing=True
    )
    return BatchVideoProcessor(config)

# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "features": [
            "video_processing",
            "viral_optimization", 
            "langchain_integration",
            "batch_processing",
            "parallel_processing"
        ],
        "timestamp": time.time()
    }

# =============================================================================
# VIDEO PROCESSING ENDPOINTS
# =============================================================================

@app.post("/api/v1/video/process", response_model=VideoClipResponse)
async def process_video(
    request: VideoClipRequest,
    processor: VideoProcessor = Depends(get_video_processor)
):
    """Process a single video clip."""
    try:
        start_time = time.perf_counter()
        
        response = processor.process_video(request)
        
        processing_time = time.perf_counter() - start_time
        
        logger.info(
            "Video processing completed",
            youtube_url=request.youtube_url,
            processing_time=processing_time,
            success=response.success
        )
        
        return response
        
    except Exception as e:
        logger.error("Video processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/video/batch", response_model=VideoClipBatchResponse)
async def process_video_batch(
    request: VideoClipBatchRequest,
    processor: BatchVideoProcessor = Depends(get_batch_processor)
):
    """Process multiple video clips in batch."""
    try:
        start_time = time.perf_counter()
        
        response = processor.process_batch(request.requests)
        
        processing_time = time.perf_counter() - start_time
        
        logger.info(
            "Batch video processing completed",
            batch_size=len(request.requests),
            processing_time=processing_time,
            successful_count=len([r for r in response if r.success])
        )
        
        return VideoClipBatchResponse(
            responses=response,
            processing_time=processing_time,
            total_requests=len(request.requests),
            successful_requests=len([r for r in response if r.success])
        )
        
    except Exception as e:
        logger.error("Batch video processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# VIRAL PROCESSING ENDPOINTS
# =============================================================================

@app.post("/api/v1/viral/process", response_model=ViralVideoBatchResponse)
async def process_viral_variants(
    request: VideoClipRequest,
    n_variants: int = 5,
    audience_profile: Optional[Dict[str, Any]] = None,
    use_langchain: bool = True,
    processor: ViralVideoProcessor = Depends(get_viral_processor)
):
    """Generate viral video variants with optional LangChain optimization."""
    try:
        start_time = time.perf_counter()
        
        response = processor.process_viral_variants(
            request=request,
            n_variants=n_variants,
            audience_profile=audience_profile,
            use_langchain=use_langchain
        )
        
        processing_time = time.perf_counter() - start_time
        
        logger.info(
            "Viral processing completed",
            youtube_url=request.youtube_url,
            variants_generated=response.successful_variants,
            average_viral_score=response.average_viral_score,
            processing_time=processing_time,
            langchain_used=use_langchain
        )
        
        return response
        
    except Exception as e:
        logger.error("Viral processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/viral/batch", response_model=List[ViralVideoBatchResponse])
async def process_viral_batch(
    requests: List[VideoClipRequest],
    n_variants_per_request: int = 5,
    audience_profiles: Optional[List[Dict[str, Any]]] = None,
    use_langchain: bool = True,
    processor: ViralVideoProcessor = Depends(get_viral_processor)
):
    """Process multiple videos for viral variants in batch."""
    try:
        start_time = time.perf_counter()
        
        responses = processor.process_batch(
            requests=requests,
            n_variants_per_request=n_variants_per_request,
            audience_profiles=audience_profiles
        )
        
        processing_time = time.perf_counter() - start_time
        
        logger.info(
            "Viral batch processing completed",
            total_requests=len(requests),
            variants_per_request=n_variants_per_request,
            processing_time=processing_time,
            successful_requests=len([r for r in responses if r.success]),
            langchain_used=use_langchain
        )
        
        return responses
        
    except Exception as e:
        logger.error("Viral batch processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# LANGCHAIN ENDPOINTS
# =============================================================================

@app.post("/api/v1/langchain/analyze", response_model=LangChainAnalysis)
async def analyze_content_with_langchain(
    request: VideoClipRequest,
    audience_profile: Optional[Dict[str, Any]] = None,
    processor: LangChainVideoProcessor = Depends(get_langchain_processor)
):
    """Analyze video content using LangChain for intelligent insights."""
    try:
        start_time = time.perf_counter()
        
        # Create a temporary response to get analysis
        temp_response = processor.process_video_with_langchain(
            request=request,
            n_variants=1,
            audience_profile=audience_profile
        )
        
        analysis_time = time.perf_counter() - start_time
        
        if not temp_response.variants or not temp_response.variants[0].langchain_analysis:
            raise HTTPException(status_code=500, detail="LangChain analysis failed")
        
        analysis = temp_response.variants[0].langchain_analysis
        
        logger.info(
            "LangChain analysis completed",
            youtube_url=request.youtube_url,
            content_type=analysis.content_type.value,
            viral_potential=analysis.viral_potential,
            engagement_score=analysis.engagement_score,
            analysis_time=analysis_time
        )
        
        return analysis
        
    except Exception as e:
        logger.error("LangChain analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/langchain/optimize", response_model=ContentOptimization)
async def optimize_content_with_langchain(
    request: VideoClipRequest,
    audience_profile: Optional[Dict[str, Any]] = None,
    processor: LangChainVideoProcessor = Depends(get_langchain_processor)
):
    """Optimize video content using LangChain for maximum engagement."""
    try:
        start_time = time.perf_counter()
        
        # Create a temporary response to get optimization
        temp_response = processor.process_video_with_langchain(
            request=request,
            n_variants=1,
            audience_profile=audience_profile
        )
        
        optimization_time = time.perf_counter() - start_time
        
        if not temp_response.variants or not temp_response.variants[0].content_optimization:
            raise HTTPException(status_code=500, detail="LangChain optimization failed")
        
        optimization = temp_response.variants[0].content_optimization
        
        logger.info(
            "LangChain optimization completed",
            youtube_url=request.youtube_url,
            optimal_title=optimization.optimal_title,
            optimal_tags_count=len(optimization.optimal_tags),
            optimal_hashtags_count=len(optimization.optimal_hashtags),
            optimization_time=optimization_time
        )
        
        return optimization
        
    except Exception as e:
        logger.error("LangChain optimization failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/langchain/short-video", response_model=ShortVideoOptimization)
async def optimize_short_video_with_langchain(
    request: VideoClipRequest,
    audience_profile: Optional[Dict[str, Any]] = None,
    processor: LangChainVideoProcessor = Depends(get_langchain_processor)
):
    """Optimize specifically for short-form video platforms."""
    try:
        start_time = time.perf_counter()
        
        # Create a temporary response to get short video optimization
        temp_response = processor.process_video_with_langchain(
            request=request,
            n_variants=1,
            audience_profile=audience_profile
        )
        
        optimization_time = time.perf_counter() - start_time
        
        if not temp_response.variants or not temp_response.variants[0].short_video_optimization:
            raise HTTPException(status_code=500, detail="Short video optimization failed")
        
        short_opt = temp_response.variants[0].short_video_optimization
        
        logger.info(
            "Short video optimization completed",
            youtube_url=request.youtube_url,
            optimal_clip_length=short_opt.optimal_clip_length,
            hook_duration=short_opt.hook_duration,
            vertical_format=short_opt.vertical_format,
            optimization_time=optimization_time
        )
        
        return short_opt
        
    except Exception as e:
        logger.error("Short video optimization failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/langchain/process", response_model=ViralVideoBatchResponse)
async def process_with_langchain(
    request: VideoClipRequest,
    n_variants: int = 5,
    audience_profile: Optional[Dict[str, Any]] = None,
    processor: LangChainVideoProcessor = Depends(get_langchain_processor)
):
    """Process video with full LangChain optimization pipeline."""
    try:
        start_time = time.perf_counter()
        
        response = processor.process_video_with_langchain(
            request=request,
            n_variants=n_variants,
            audience_profile=audience_profile
        )
        
        processing_time = time.perf_counter() - start_time
        
        logger.info(
            "LangChain processing completed",
            youtube_url=request.youtube_url,
            variants_generated=response.successful_variants,
            average_viral_score=response.average_viral_score,
            ai_enhancement_score=response.ai_enhancement_score,
            langchain_analysis_time=response.langchain_analysis_time,
            content_optimization_time=response.content_optimization_time,
            total_processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error("LangChain processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/langchain/batch", response_model=List[ViralVideoBatchResponse])
async def process_langchain_batch(
    requests: List[VideoClipRequest],
    n_variants_per_request: int = 3,
    audience_profiles: Optional[List[Dict[str, Any]]] = None,
    processor: LangChainVideoProcessor = Depends(get_langchain_processor)
):
    """Process multiple videos with LangChain optimization in batch."""
    try:
        start_time = time.perf_counter()
        
        responses = []
        for i, request in enumerate(requests):
            audience_profile = audience_profiles[i] if audience_profiles and i < len(audience_profiles) else None
            
            response = processor.process_video_with_langchain(
                request=request,
                n_variants=n_variants_per_request,
                audience_profile=audience_profile
            )
            responses.append(response)
        
        processing_time = time.perf_counter() - start_time
        
        logger.info(
            "LangChain batch processing completed",
            total_requests=len(requests),
            variants_per_request=n_variants_per_request,
            processing_time=processing_time,
            successful_requests=len([r for r in responses if r.success])
        )
        
        return responses
        
    except Exception as e:
        logger.error("LangChain batch processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# CONFIGURATION ENDPOINTS
# =============================================================================

@app.get("/api/v1/config/langchain")
async def get_langchain_config():
    """Get current LangChain configuration."""
    return {
        "model_name": "gpt-4",
        "enable_content_analysis": True,
        "enable_engagement_analysis": True,
        "enable_viral_analysis": True,
        "enable_title_optimization": True,
        "enable_caption_optimization": True,
        "enable_timing_optimization": True,
        "batch_size": 5,
        "max_retries": 3,
        "use_agents": True,
        "use_memory": True
    }

@app.get("/api/v1/config/viral")
async def get_viral_config():
    """Get current viral processing configuration."""
    return {
        "max_variants": 10,
        "min_viral_score": 0.3,
        "enable_langchain": True,
        "enable_screen_division": True,
        "enable_transitions": True,
        "enable_effects": True,
        "enable_animations": True
    }

@app.get("/api/v1/config/video")
async def get_video_config():
    """Get current video processing configuration."""
    return {
        "max_workers": 4,
        "batch_size": 5,
        "enable_audit_logging": True,
        "enable_performance_tracking": True
    }

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@app.post("/api/v1/utils/validate")
async def validate_video_request(request: VideoClipRequest):
    """Validate a video processing request."""
    try:
        # Basic validation
        if not request.youtube_url:
            raise ValueError("YouTube URL is required")
        
        if request.max_clip_length <= 0:
            raise ValueError("Max clip length must be positive")
        
        if request.max_clip_length > 600:  # 10 minutes
            raise ValueError("Max clip length cannot exceed 10 minutes")
        
        return {
            "valid": True,
            "message": "Request is valid",
            "request": request
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": str(e),
            "request": request
        }

@app.get("/api/v1/utils/content-types")
async def get_content_types():
    """Get available content types for LangChain analysis."""
    return {
        "content_types": [ct.value for ct in ContentType],
        "engagement_types": [et.value for et in EngagementType]
    }

@app.post("/api/v1/utils/estimate-processing-time")
async def estimate_processing_time(
    n_variants: int = 5,
    use_langchain: bool = True,
    batch_size: int = 1
):
    """Estimate processing time for video generation."""
    try:
        # Base processing time
        base_time = 2.0  # seconds per variant
        
        # LangChain overhead
        langchain_overhead = 5.0 if use_langchain else 0.0
        
        # Batch processing efficiency
        batch_efficiency = 0.8 if batch_size > 1 else 1.0
        
        # Calculate estimated time
        estimated_time = (base_time * n_variants + langchain_overhead) * batch_efficiency
        
        return {
            "estimated_time_seconds": estimated_time,
            "estimated_time_minutes": estimated_time / 60,
            "n_variants": n_variants,
            "use_langchain": use_langchain,
            "batch_size": batch_size,
            "factors": {
                "base_processing": base_time * n_variants,
                "langchain_overhead": langchain_overhead,
                "batch_efficiency": batch_efficiency
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": time.time()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler."""
    logger.error("HTTP exception", status_code=exc.status_code, detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP error",
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time()
        }
    )

# =============================================================================
# STARTUP AND SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Video Processing API starting up", version="3.0.0")
    
    # Initialize processors
    try:
        # Test processor initialization
        video_processor = get_video_processor()
        viral_processor = get_viral_processor()
        langchain_processor = get_langchain_processor()
        batch_processor = get_batch_processor()
        
        logger.info("All processors initialized successfully")
        
    except Exception as e:
        logger.error("Failed to initialize processors", error=str(e))
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Video Processing API shutting down")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 