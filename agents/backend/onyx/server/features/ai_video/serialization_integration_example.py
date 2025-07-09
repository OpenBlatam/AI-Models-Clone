"""
🚀 PYDANTIC SERIALIZATION INTEGRATION EXAMPLE - AI VIDEO SYSTEM
===============================================================

Complete integration example demonstrating optimized data serialization
and deserialization in a real AI Video application.

This example shows:
- Integration with FastAPI endpoints
- Real-world video processing pipeline
- Performance monitoring and optimization
- Caching and compression strategies
- Error handling and validation
"""

import asyncio
import time
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict, computed_field

# Import our optimized serialization system
from .pydantic_serialization_optimization import (
    OptimizedSerializer,
    SerializationCache,
    BatchSerializationOptimizer,
    SerializationPerformanceMonitor,
    SerializationConfig,
    SerializationFormat,
    CompressionType
)

# Import example models
from .pydantic_serialization_examples import (
    OptimizedVideoModel,
    VideoProcessingResult,
    VideoBatchRequest,
    VideoStatus,
    VideoQuality
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# 1. FASTAPI APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title="AI Video System - Optimized Serialization",
    description="FastAPI application with optimized Pydantic serialization",
    version="2.0.0"
)

# ============================================================================
# 2. SERIALIZATION SYSTEM INITIALIZATION
# ============================================================================

# Initialize serialization components
serialization_config = SerializationConfig(
    format=SerializationFormat.JSON,
    compression=CompressionType.GZIP,
    compression_threshold=1024,
    enable_caching=True,
    cache_ttl=3600,
    enable_stats=True
)

serializer = OptimizedSerializer(
    enable_caching=True,
    enable_compression=True
)

batch_optimizer = BatchSerializationOptimizer(serializer)
performance_monitor = SerializationPerformanceMonitor()

# Global cache for video data
video_cache = SerializationCache(max_size=2000, ttl=7200)  # 2 hours TTL

# ============================================================================
# 3. ENHANCED VIDEO MODELS
# ============================================================================

class VideoProcessingRequest(BaseModel):
    """Enhanced video processing request with optimized serialization."""
    
    model_config = ConfigDict(
        validate_assignment=False,
        extra="forbid",
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Path: str
        }
    )
    
    request_id: str = Field(..., description="Unique request identifier")
    video: OptimizedVideoModel = Field(..., description="Video to process")
    
    # Processing options
    quality_override: Optional[VideoQuality] = Field(default=None, description="Override video quality")
    priority: str = Field(default="normal", description="Processing priority")
    callback_url: Optional[str] = Field(default=None, description="Callback URL for completion")
    
    # Metadata
    user_id: str = Field(..., description="User identifier")
    project_id: Optional[str] = Field(default=None, description="Project identifier")
    tags: List[str] = Field(default_factory=list, description="Processing tags")
    
    @computed_field
    @property
    def estimated_processing_time(self) -> float:
        """Estimated processing time in seconds."""
        base_time = self.video.duration / 60 * 30  # 30 seconds per minute
        if self.quality_override == VideoQuality.ULTRA:
            base_time *= 2
        return base_time
    
    @computed_field
    @property
    def cache_key(self) -> str:
        """Generate cache key for this request."""
        return f"{self.user_id}:{self.video.video_id}:{self.quality_override or self.video.quality}"

class VideoProcessingResponse(BaseModel):
    """Response model for video processing."""
    
    model_config = ConfigDict(
        validate_assignment=False,
        extra="forbid",
        use_enum_values=True
    )
    
    request_id: str = Field(..., description="Request identifier")
    status: VideoStatus = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    
    # Processing information
    processing_result: Optional[VideoProcessingResult] = Field(default=None, description="Processing result")
    estimated_completion: Optional[datetime] = Field(default=None, description="Estimated completion time")
    
    # Performance metrics
    serialization_time: Optional[float] = Field(default=None, description="Serialization time in seconds")
    cache_hit: bool = Field(default=False, description="Whether cache was hit")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class BatchProcessingResponse(BaseModel):
    """Response model for batch processing."""
    
    model_config = ConfigDict(
        validate_assignment=False,
        extra="forbid",
        use_enum_values=True
    )
    
    batch_id: str = Field(..., description="Batch identifier")
    total_requests: int = Field(..., description="Total number of requests")
    successful_requests: int = Field(..., description="Number of successful requests")
    failed_requests: int = Field(..., description="Number of failed requests")
    
    # Processing information
    requests: List[VideoProcessingResponse] = Field(..., description="Individual request results")
    overall_status: VideoStatus = Field(..., description="Overall batch status")
    
    # Performance metrics
    total_processing_time: float = Field(..., description="Total processing time in seconds")
    avg_serialization_time: float = Field(..., description="Average serialization time")
    cache_hit_rate: float = Field(..., description="Cache hit rate")
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.now, description="Start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    
    @computed_field
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return self.successful_requests / self.total_requests if self.total_requests > 0 else 0.0
    
    @computed_field
    @property
    def processing_duration(self) -> Optional[float]:
        """Calculate processing duration."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

# ============================================================================
# 4. SERIALIZATION UTILITIES
# ============================================================================

async def serialize_with_monitoring(data: BaseModel, operation: str) -> bytes:
    """Serialize data with performance monitoring."""
    async with performance_monitor.monitor_serialization(operation, len(str(data))):
        return await serializer.serialize(data, {"exclude_none": True, "use_enum_values": True})

async def deserialize_with_monitoring(data: bytes, model_class: type, operation: str):
    """Deserialize data with performance monitoring."""
    async with performance_monitor.monitor_serialization(operation, len(data)):
        return await serializer.deserialize(data, model_class)

async def get_cached_or_serialize(data: BaseModel, cache_key: str) -> tuple[bytes, bool]:
    """Get cached data or serialize and cache."""
    # Check cache first
    cached_data = await video_cache.get(data, {})
    if cached_data is not None:
        return cached_data, True
    
    # Serialize and cache
    serialized_data = await serialize_with_monitoring(data, "video_serialization")
    await video_cache.set(data, {}, serialized_data)
    
    return serialized_data, False

# ============================================================================
# 5. VIDEO PROCESSING SERVICE
# ============================================================================

class VideoProcessingService:
    """Service for video processing with optimized serialization."""
    
    def __init__(self):
        self.processing_queue: Dict[str, VideoProcessingRequest] = {}
        self.results_cache: Dict[str, VideoProcessingResult] = {}
    
    async def process_video(self, request: VideoProcessingRequest) -> VideoProcessingResponse:
        """Process a single video with optimized serialization."""
        start_time = time.time()
        
        try:
            # Check if already processed
            if request.request_id in self.results_cache:
                result = self.results_cache[request.request_id]
                return VideoProcessingResponse(
                    request_id=request.request_id,
                    status=VideoStatus.COMPLETED,
                    message="Video already processed",
                    processing_result=result,
                    cache_hit=True
                )
            
            # Serialize request with monitoring
            serialization_start = time.time()
            serialized_request, cache_hit = await get_cached_or_serialize(
                request, request.cache_key
            )
            serialization_time = time.time() - serialization_start
            
            # Simulate processing
            await asyncio.sleep(request.estimated_processing_time / 100)  # Scale down for demo
            
            # Create processing result
            processing_result = VideoProcessingResult(
                video_id=request.video.video_id,
                status=VideoStatus.COMPLETED,
                processing_time=request.estimated_processing_time,
                output_url=f"/output/{request.video.video_id}.mp4",
                thumbnail_url=f"/thumbnails/{request.video.video_id}.jpg",
                file_size=int(request.video.file_size_mb * 1024 * 1024),
                resolution="1920x1080",
                format="mp4",
                completed_at=datetime.now()
            )
            
            # Cache result
            self.results_cache[request.request_id] = processing_result
            
            # Create response
            response = VideoProcessingResponse(
                request_id=request.request_id,
                status=VideoStatus.COMPLETED,
                message="Video processed successfully",
                processing_result=processing_result,
                estimated_completion=datetime.now() + timedelta(seconds=request.estimated_processing_time),
                serialization_time=serialization_time,
                cache_hit=cache_hit
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing video {request.request_id}: {e}")
            return VideoProcessingResponse(
                request_id=request.request_id,
                status=VideoStatus.FAILED,
                message=f"Processing failed: {str(e)}",
                serialization_time=time.time() - start_time
            )
    
    async def process_batch(self, batch_request: VideoBatchRequest) -> BatchProcessingResponse:
        """Process a batch of videos with optimized serialization."""
        start_time = time.time()
        
        # Serialize batch request
        serialization_start = time.time()
        serialized_batch = await batch_optimizer.serialize_batch(
            batch_request.videos,
            {"exclude_none": True, "use_enum_values": True}
        )
        avg_serialization_time = (time.time() - serialization_start) / len(batch_request.videos)
        
        # Process each video
        processing_tasks = []
        for video in batch_request.videos:
            request = VideoProcessingRequest(
                request_id=f"{batch_request.batch_id}_{video.video_id}",
                video=video,
                quality_override=batch_request.quality_override,
                priority=batch_request.priority,
                user_id=batch_request.user_id or "anonymous",
                project_id=batch_request.project_id
            )
            processing_tasks.append(self.process_video(request))
        
        # Execute all processing tasks
        results = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
        # Process results
        successful_requests = []
        failed_requests = []
        
        for result in results:
            if isinstance(result, Exception):
                failed_requests.append(VideoProcessingResponse(
                    request_id="unknown",
                    status=VideoStatus.FAILED,
                    message=f"Processing failed: {str(result)}"
                ))
            else:
                if result.status == VideoStatus.COMPLETED:
                    successful_requests.append(result)
                else:
                    failed_requests.append(result)
        
        # Calculate cache hit rate
        cache_hits = sum(1 for r in successful_requests if r.cache_hit)
        cache_hit_rate = cache_hits / len(successful_requests) if successful_requests else 0.0
        
        # Create batch response
        batch_response = BatchProcessingResponse(
            batch_id=batch_request.batch_id,
            total_requests=len(batch_request.videos),
            successful_requests=len(successful_requests),
            failed_requests=len(failed_requests),
            requests=successful_requests + failed_requests,
            overall_status=VideoStatus.COMPLETED if failed_requests == 0 else VideoStatus.FAILED,
            total_processing_time=time.time() - start_time,
            avg_serialization_time=avg_serialization_time,
            cache_hit_rate=cache_hit_rate,
            completed_at=datetime.now()
        )
        
        return batch_response

# Initialize service
video_service = VideoProcessingService()

# ============================================================================
# 6. FASTAPI ENDPOINTS
# ============================================================================

@app.post("/api/v1/videos/process", response_model=VideoProcessingResponse)
async def process_video(request: VideoProcessingRequest):
    """Process a single video with optimized serialization."""
    try:
        # Validate request
        if not request.video.title or not request.video.title.strip():
            raise HTTPException(status_code=400, detail="Video title is required")
        
        # Process video
        result = await video_service.process_video(request)
        
        # Log performance metrics
        logger.info(f"Video processing completed: {request.request_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in process_video endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/videos/batch", response_model=BatchProcessingResponse)
async def process_video_batch(batch_request: VideoBatchRequest):
    """Process a batch of videos with optimized serialization."""
    try:
        # Validate batch request
        if len(batch_request.videos) > 100:
            raise HTTPException(status_code=400, detail="Batch size cannot exceed 100 videos")
        
        # Process batch
        result = await video_service.process_batch(batch_request)
        
        # Log performance metrics
        logger.info(f"Batch processing completed: {batch_request.batch_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in process_video_batch endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/performance/stats")
async def get_performance_stats():
    """Get serialization performance statistics."""
    try:
        # Get performance reports
        performance_report = performance_monitor.get_performance_report()
        serializer_stats = serializer.get_stats()
        batch_stats = batch_optimizer.get_batch_stats()
        cache_stats = video_cache.get_stats()
        
        return {
            "performance_report": performance_report,
            "serializer_stats": serializer_stats,
            "batch_stats": batch_stats,
            "cache_stats": cache_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/cache/clear")
async def clear_cache():
    """Clear all caches."""
    try:
        await video_cache.clear()
        await serializer.clear_cache()
        
        return {"message": "All caches cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "serialization_system": "optimized"
    }

# ============================================================================
# 7. BACKGROUND TASKS
# ============================================================================

async def background_video_processing(request: VideoProcessingRequest):
    """Background task for video processing."""
    try:
        # Process video in background
        result = await video_service.process_video(request)
        
        # Log completion
        logger.info(f"Background processing completed: {request.request_id}")
        
        # Here you could send webhook notifications, update database, etc.
        
    except Exception as e:
        logger.error(f"Background processing failed: {request.request_id} - {e}")

@app.post("/api/v1/videos/process-async")
async def process_video_async(request: VideoProcessingRequest, background_tasks: BackgroundTasks):
    """Process video asynchronously."""
    try:
        # Add to background tasks
        background_tasks.add_task(background_video_processing, request)
        
        return {
            "request_id": request.request_id,
            "status": "queued",
            "message": "Video processing queued for background processing",
            "estimated_completion": datetime.now() + timedelta(seconds=request.estimated_processing_time)
        }
        
    except Exception as e:
        logger.error(f"Error queuing video processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 8. MIDDLEWARE FOR PERFORMANCE MONITORING
# ============================================================================

@app.middleware("http")
async def performance_middleware(request, call_next):
    """Middleware for performance monitoring."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    processing_time = time.time() - start_time
    
    # Add performance headers
    response.headers["X-Processing-Time"] = str(processing_time)
    response.headers["X-Serialization-System"] = "optimized"
    
    # Log slow requests
    if processing_time > 1.0:
        logger.warning(f"Slow request: {request.url.path} took {processing_time:.4f}s")
    
    return response

# ============================================================================
# 9. STARTUP AND SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    logger.info("🚀 AI Video System with Optimized Serialization starting up...")
    
    # Initialize performance monitoring
    logger.info("📊 Performance monitoring initialized")
    
    # Log system configuration
    logger.info(f"🔧 Serialization config: {serialization_config}")
    logger.info(f"💾 Cache TTL: {video_cache.ttl} seconds")
    logger.info(f"📦 Batch optimization enabled: {batch_optimizer is not None}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 AI Video System shutting down...")
    
    # Clear caches
    await video_cache.clear()
    await serializer.clear_cache()
    
    # Log final statistics
    performance_report = performance_monitor.get_performance_report()
    logger.info(f"📈 Final performance report: {performance_report}")

# ============================================================================
# 10. USAGE EXAMPLES
# ============================================================================

async def example_usage():
    """Example usage of the integrated system."""
    
    # Example 1: Process single video
    video_request = VideoProcessingRequest(
        request_id="req_001",
        video=OptimizedVideoModel(
            video_id="video_001",
            title="Sample Video",
            duration=180.0,
            quality=VideoQuality.HIGH,
            tags=["sample", "demo"],
            metadata={"quality": "high", "format": "mp4"}
        ),
        user_id="user_123",
        project_id="project_456"
    )
    
    # Example 2: Process batch
    batch_request = VideoBatchRequest(
        batch_id="batch_001",
        videos=[
            OptimizedVideoModel(
                video_id=f"batch_video_{i}",
                title=f"Batch Video {i}",
                duration=120.0 + i * 10,
                quality=VideoQuality.MEDIUM,
                tags=["batch", "processing"]
            )
            for i in range(5)
        ],
        user_id="user_123",
        priority="high"
    )
    
    print("✅ Integration example ready!")
    print("📝 Use the FastAPI endpoints to test the system:")
    print("   - POST /api/v1/videos/process")
    print("   - POST /api/v1/videos/batch")
    print("   - GET /api/v1/performance/stats")
    print("   - POST /api/v1/cache/clear")

if __name__ == "__main__":
    import uvicorn
    
    # Run the FastAPI application
    uvicorn.run(
        "serialization_integration_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 