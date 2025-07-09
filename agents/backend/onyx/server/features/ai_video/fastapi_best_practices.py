"""
🚀 FASTAPI BEST PRACTICES - AI VIDEO SYSTEM
===========================================

Complete implementation following FastAPI documentation best practices
for Data Models, Path Operations, and Middleware.

Features:
- Pydantic models with proper validation
- RESTful path operations with correct HTTP methods
- Comprehensive middleware stack
- Dependency injection patterns
- Error handling and status codes
- Performance monitoring
- Security middleware
"""

from fastapi import (
    FastAPI, APIRouter, HTTPException, status, Depends, 
    Request, Response, BackgroundTasks, Query, Path
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, ConfigDict, computed_field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import time
import json
import logging
import asyncio
from pathlib import Path as FilePath

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# 1. PYDANTIC DATA MODELS
# ============================================================================

class VideoStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VideoQuality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

class ProcessingPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class VideoData(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            FilePath: str
        }
    )
    
    video_id: str = Field(..., min_length=1, max_length=50, description="Video identifier")
    title: str = Field(..., max_length=200, description="Video title")
    duration: float = Field(..., ge=0, le=3600, description="Duration in seconds")
    quality: VideoQuality = Field(default=VideoQuality.MEDIUM, description="Video quality")
    priority: ProcessingPriority = Field(default=ProcessingPriority.NORMAL, description="Processing priority")
    
    description: Optional[str] = Field(default=None, max_length=1000, description="Video description")
    tags: List[str] = Field(default_factory=list, description="Video tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @computed_field
    @property
    def duration_minutes(self) -> float:
        return self.duration / 60
    
    @computed_field
    @property
    def file_size_mb(self) -> float:
        quality_multiplier = {"low": 0.5, "medium": 1.0, "high": 2.0, "ultra": 4.0}
        return 10 * quality_multiplier[self.quality] * (self.duration / 60)
    
    @validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        return [tag.strip().lower() for tag in v if tag.strip()]

class VideoResponse(BaseModel):
    video_id: str = Field(..., description="Video identifier")
    status: VideoStatus = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    
    video_url: Optional[str] = Field(None, description="Video download URL")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @computed_field
    @property
    def is_completed(self) -> bool:
        return self.status == VideoStatus.COMPLETED
    
    @computed_field
    @property
    def is_failed(self) -> bool:
        return self.status == VideoStatus.FAILED

class BatchVideoRequest(BaseModel):
    videos: List[VideoData] = Field(..., min_length=1, max_length=100, description="List of videos to process")
    batch_name: Optional[str] = Field(default=None, max_length=100, description="Batch name")
    priority: ProcessingPriority = Field(default=ProcessingPriority.NORMAL, description="Batch priority")
    
    @validator('videos')
    @classmethod
    def validate_batch_size(cls, v: List[VideoData]) -> List[VideoData]:
        if len(v) > 100:
            raise ValueError("Batch size cannot exceed 100 videos")
        return v
    
    @computed_field
    @property
    def total_duration(self) -> float:
        return sum(video.duration for video in self.videos)
    
    @computed_field
    @property
    def estimated_processing_time(self) -> float:
        return self.total_duration / 60 * 30  # 30 seconds per minute

class BatchVideoResponse(BaseModel):
    batch_id: str = Field(..., description="Batch identifier")
    batch_name: Optional[str] = Field(None, description="Batch name")
    
    total_videos: int = Field(..., description="Total number of videos")
    completed_videos: int = Field(..., ge=0, description="Number of completed videos")
    failed_videos: int = Field(..., ge=0, description="Number of failed videos")
    processing_videos: int = Field(..., ge=0, description="Number of processing videos")
    
    overall_progress: float = Field(..., ge=0.0, le=100.0, description="Overall progress percentage")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    
    status: VideoStatus = Field(..., description="Overall batch status")
    message: str = Field(..., description="Status message")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @computed_field
    @property
    def success_rate(self) -> float:
        if self.total_videos == 0:
            return 0.0
        return self.completed_videos / self.total_videos

class ErrorResponse(BaseModel):
    error_code: str = Field(..., description="Error code")
    error_type: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")

class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of items to return")

class VideoListResponse(BaseModel):
    items: List[VideoResponse] = Field(..., description="List of videos")
    total: int = Field(..., description="Total number of videos")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items returned")
    has_next: bool = Field(..., description="Whether there are more items")
    has_previous: bool = Field(..., description="Whether there are previous items")

# ============================================================================
# 2. DEPENDENCIES
# ============================================================================

class VideoService:
    def __init__(self):
        self.processing_queue: Dict[str, VideoData] = {}
        self.results_cache: Dict[str, VideoResponse] = {}
    
    async def process_video(self, video_data: VideoData) -> VideoResponse:
        # Simulate processing
        await asyncio.sleep(0.1)
        
        result = VideoResponse(
            video_id=video_data.video_id,
            status=VideoStatus.COMPLETED,
            message="Video processed successfully",
            video_url=f"/videos/{video_data.video_id}/download",
            thumbnail_url=f"/videos/{video_data.video_id}/thumbnail",
            processing_time=0.1
        )
        
        self.results_cache[video_data.video_id] = result
        return result
    
    async def process_batch(self, batch_request: BatchVideoRequest) -> BatchVideoResponse:
        batch_id = f"batch_{int(time.time())}"
        
        # Process videos concurrently
        tasks = [self.process_video(video) for video in batch_request.videos]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        completed = sum(1 for r in results if isinstance(r, VideoResponse) and r.is_completed)
        failed = sum(1 for r in results if isinstance(r, Exception))
        processing = len(batch_request.videos) - completed - failed
        
        return BatchVideoResponse(
            batch_id=batch_id,
            batch_name=batch_request.batch_name,
            total_videos=len(batch_request.videos),
            completed_videos=completed,
            failed_videos=failed,
            processing_videos=processing,
            overall_progress=(completed / len(batch_request.videos)) * 100,
            status=VideoStatus.COMPLETED if failed == 0 else VideoStatus.FAILED,
            message=f"Batch processed: {completed} completed, {failed} failed"
        )
    
    async def get_video(self, video_id: str) -> Optional[VideoResponse]:
        return self.results_cache.get(video_id)
    
    async def list_videos(
        self, 
        skip: int = 0, 
        limit: int = 100,
        quality: Optional[VideoQuality] = None
    ) -> VideoListResponse:
        videos = list(self.results_cache.values())
        
        # Filter by quality if specified
        if quality:
            videos = [v for v in videos if hasattr(v, 'quality') and v.quality == quality]
        
        total = len(videos)
        items = videos[skip:skip + limit]
        has_next = skip + limit < total
        has_previous = skip > 0
        
        return VideoListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=has_next,
            has_previous=has_previous
        )
    
    async def update_video(self, video_id: str, video_data: VideoData) -> Optional[VideoResponse]:
        if video_id in self.results_cache:
            updated = VideoResponse(
                video_id=video_id,
                status=VideoStatus.COMPLETED,
                message="Video updated successfully",
                video_url=f"/videos/{video_id}/download",
                thumbnail_url=f"/videos/{video_id}/thumbnail"
            )
            self.results_cache[video_id] = updated
            return updated
        return None
    
    async def delete_video(self, video_id: str) -> bool:
        if video_id in self.results_cache:
            del self.results_cache[video_id]
            return True
        return False

# Global service instance
video_service = VideoService()

# Dependencies
async def get_video_service() -> VideoService:
    return video_service

async def get_current_user(request: Request):
    # Simulate authentication
    auth_header = request.headers.get("authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    return {"user_id": "user_123", "username": "test_user"}

# ============================================================================
# 3. ROUTERS
# ============================================================================

video_router = APIRouter(prefix="/videos", tags=["videos"])

@video_router.post(
    "/process",
    response_model=VideoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Process a video with AI enhancement",
    description="Process a single video using AI algorithms for enhancement and optimization.",
    response_description="Video processing result with status and metadata",
    responses={
        201: {"description": "Video processing started successfully"},
        400: {"description": "Bad request", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def process_video(
    video_data: VideoData,
    background_tasks: BackgroundTasks,
    video_service: VideoService = Depends(get_video_service),
    current_user: dict = Depends(get_current_user)
) -> VideoResponse:
    """
    Process a video with AI enhancement.
    
    - **video_data**: Video information and processing parameters
    - **background_tasks**: FastAPI background tasks for async processing
    
    Returns:
    - **VideoResponse**: Processing result with status and metadata
    """
    try:
        # Validate input
        if not video_data.title or not video_data.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video title is required"
            )
        
        # Process video
        result = await video_service.process_video(video_data)
        
        # Add background task for cleanup
        background_tasks.add_task(cleanup_temp_files, video_data.video_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Video processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during video processing"
        )

@video_router.post(
    "/batch-process",
    response_model=BatchVideoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Process multiple videos in batch",
    description="Process multiple videos concurrently with batch optimization.",
    response_description="Batch processing result with progress information"
)
async def process_video_batch(
    batch_request: BatchVideoRequest,
    video_service: VideoService = Depends(get_video_service),
    current_user: dict = Depends(get_current_user)
) -> BatchVideoResponse:
    """
    Process multiple videos in batch.
    
    - **batch_request**: Batch processing request with video list
    
    Returns:
    - **BatchVideoResponse**: Batch processing result with progress
    """
    try:
        return await video_service.process_batch(batch_request)
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during batch processing"
        )

@video_router.get(
    "/{video_id}",
    response_model=VideoResponse,
    status_code=status.HTTP_200_OK,
    summary="Get video by ID",
    description="Retrieve video information and processing status by video ID.",
    responses={
        200: {"description": "Video found successfully"},
        404: {"description": "Video not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def get_video(
    video_id: str = Path(..., description="Unique video identifier", min_length=1),
    video_service: VideoService = Depends(get_video_service),
    current_user: dict = Depends(get_current_user)
) -> VideoResponse:
    """
    Get video by ID.
    
    - **video_id**: Unique identifier for the video
    
    Returns:
    - **VideoResponse**: Video information and status
    """
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )
    return video

@video_router.get(
    "/",
    response_model=VideoListResponse,
    status_code=status.HTTP_200_OK,
    summary="List videos with pagination",
    description="Retrieve a paginated list of videos with optional filtering."
)
async def list_videos(
    skip: int = Query(0, ge=0, description="Number of videos to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of videos to return"),
    quality: Optional[VideoQuality] = Query(None, description="Filter by video quality"),
    video_service: VideoService = Depends(get_video_service),
    current_user: dict = Depends(get_current_user)
) -> VideoListResponse:
    """
    List videos with pagination and filtering.
    
    - **skip**: Number of videos to skip for pagination
    - **limit**: Maximum number of videos to return
    - **quality**: Optional filter by video quality
    
    Returns:
    - **VideoListResponse**: Paginated list of videos
    """
    return await video_service.list_videos(skip=skip, limit=limit, quality=quality)

@video_router.put(
    "/{video_id}",
    response_model=VideoResponse,
    status_code=status.HTTP_200_OK,
    summary="Update video information",
    description="Update video metadata and processing parameters."
)
async def update_video(
    video_id: str = Path(..., description="Unique video identifier"),
    video_update: VideoData = ...,
    video_service: VideoService = Depends(get_video_service),
    current_user: dict = Depends(get_current_user)
) -> VideoResponse:
    """
    Update video information.
    
    - **video_id**: Unique identifier for the video
    - **video_update**: Updated video information
    
    Returns:
    - **VideoResponse**: Updated video information
    """
    updated_video = await video_service.update_video(video_id, video_update)
    if not updated_video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )
    return updated_video

@video_router.delete(
    "/{video_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete video",
    description="Delete a video and all associated resources."
)
async def delete_video(
    video_id: str = Path(..., description="Unique video identifier"),
    video_service: VideoService = Depends(get_video_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete video.
    
    - **video_id**: Unique identifier for the video
    
    Returns:
    - **204 No Content**: Video deleted successfully
    """
    success = await video_service.delete_video(video_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )

# Analytics router
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])

@analytics_router.get(
    "/performance",
    summary="Get system performance metrics",
    description="Retrieve performance metrics for the AI Video system."
)
async def get_performance_metrics(
    current_user: dict = Depends(get_current_user)
):
    """Get system performance metrics."""
    return {
        "total_videos_processed": len(video_service.results_cache),
        "success_rate": 0.95,
        "average_processing_time": 0.15,
        "system_uptime": 3600,
        "active_requests": 5
    }

# Health router
health_router = APIRouter(prefix="/health", tags=["health"])

@health_router.get(
    "/",
    summary="Health check",
    description="Check system health and status."
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "database": "healthy",
            "cache": "healthy",
            "ai_processing": "healthy"
        }
    }

# ============================================================================
# 4. MIDDLEWARE
# ============================================================================

def create_middleware_stack(app: FastAPI):
    """Create and configure middleware stack."""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://yourdomain.com"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "yourdomain.com", "*.yourdomain.com"]
    )
    
    # Performance monitoring middleware
    @app.middleware("http")
    async def performance_middleware(request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")
        
        # Log response
        logger.info(
            f"Response: {response.status_code} "
            f"took {process_time:.4f}s "
            f"for {request.method} {request.url.path}"
        )
        
        # Log slow requests
        if process_time > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.4f}s"
            )
        
        return response
    
    # Error handling middleware
    @app.middleware("http")
    async def error_handling_middleware(request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log error
            logger.error(
                f"Unhandled error in {request.method} {request.url.path}: {str(e)}",
                exc_info=True
            )
            
            # Return error response
            error_response = {
                "error_code": "INTERNAL_ERROR",
                "error_type": "server_error",
                "message": "An unexpected error occurred",
                "timestamp": datetime.now().isoformat(),
                "request_id": request.headers.get("X-Request-ID", "unknown")
            }
            
            return Response(
                content=json.dumps(error_response),
                status_code=500,
                media_type="application/json"
            )
    
    # Request validation middleware
    @app.middleware("http")
    async def validation_middleware(request: Request, call_next):
        # Validate request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            return Response(
                content=json.dumps({
                    "error_code": "PAYLOAD_TOO_LARGE",
                    "error_type": "validation_error",
                    "message": "Request payload too large",
                    "timestamp": datetime.now().isoformat()
                }),
                status_code=413,
                media_type="application/json"
            )
        
        # Validate content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                return Response(
                    content=json.dumps({
                        "error_code": "INVALID_CONTENT_TYPE",
                        "error_type": "validation_error",
                        "message": "Content-Type must be application/json",
                        "timestamp": datetime.now().isoformat()
                    }),
                    status_code=415,
                    media_type="application/json"
                )
        
        return await call_next(request)

# ============================================================================
# 5. BACKGROUND TASKS
# ============================================================================

async def cleanup_temp_files(video_id: str):
    """Background task to cleanup temporary files."""
    try:
        await asyncio.sleep(1)  # Simulate cleanup
        logger.info(f"Cleaned up temporary files for video {video_id}")
    except Exception as e:
        logger.error(f"Error cleaning up files for video {video_id}: {e}")

# ============================================================================
# 6. MAIN APPLICATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 AI Video System starting up...")
    # Initialize resources (database, cache, etc.)
    yield
    # Shutdown
    logger.info("🛑 AI Video System shutting down...")
    # Cleanup resources

# Create FastAPI app
app = FastAPI(
    title="AI Video System",
    description="High-performance video processing API with AI enhancement",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
create_middleware_stack(app)

# Include routers
app.include_router(video_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(health_router)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Video System API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 