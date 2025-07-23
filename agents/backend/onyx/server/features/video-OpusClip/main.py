#!/usr/bin/env python3
"""
Video-OpusClip Main Application
Integrates FastAPI best practices, structured routes, async flows, and database operations
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# Import our custom modules
from fastapi_best_practices import (
    VideoCreateRequest, VideoUpdateRequest, VideoResponse, 
    BatchVideoRequest, BatchVideoResponse, ErrorResponse, HealthResponse,
    VideoRouter, FastAPIMiddleware, FastAPIErrorHandlers, create_fastapi_app
)
from structured_routes import (
    RouteRegistry, RouterFactory, CommonDependencies,
    create_structured_app
)
from async_flows import AsyncFlowManager, AsyncFlowConfig
from async_database import (
    DatabaseConfig, DatabaseType, AsyncDatabaseOperations,
    AsyncVideoDatabase, AsyncTransactionManager
)
from async_external_apis import (
    APIConfig, APIType, AsyncExternalAPIOperations,
    AsyncYouTubeAPI, AsyncOpenAIAPI, AsyncStabilityAIAPI, AsyncElevenLabsAPI
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_opusclip.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "Video-OpusClip"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Database settings
    database_url: str = "postgresql://postgres:password@localhost:5432/video_opusclip"
    database_type: str = "postgresql"
    
    # API settings
    youtube_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    stability_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    
    # Async flow settings
    max_concurrent_tasks: int = 100
    max_concurrent_connections: int = 50
    timeout: float = 30.0
    retry_attempts: int = 3
    
    class Config:
        env_file = ".env"

# Global instances
settings = Settings()
flow_manager: Optional[AsyncFlowManager] = None
db_ops: Optional[AsyncDatabaseOperations] = None
video_db: Optional[AsyncVideoDatabase] = None
tx_manager: Optional[AsyncTransactionManager] = None
youtube_api: Optional[AsyncYouTubeAPI] = None
openai_api: Optional[AsyncOpenAIAPI] = None
stability_api: Optional[AsyncStabilityAIAPI] = None
elevenlabs_api: Optional[AsyncElevenLabsAPI] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global flow_manager, db_ops, video_db, tx_manager
    global youtube_api, openai_api, stability_api, elevenlabs_api
    
    logger.info("Starting Video-OpusClip application...")
    
    try:
        # Initialize async flow manager
        flow_config = AsyncFlowConfig(
            max_concurrent_tasks=settings.max_concurrent_tasks,
            max_concurrent_connections=settings.max_concurrent_connections,
            timeout=settings.timeout,
            retry_attempts=settings.retry_attempts,
            enable_metrics=True,
            enable_circuit_breaker=True
        )
        flow_manager = AsyncFlowManager(flow_config)
        await flow_manager.start()
        logger.info("Async flow manager started")
        
        # Initialize database connections
        db_config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="video_opusclip",
            username="postgres",
            password="password"
        )
        
        if settings.database_type == "postgresql":
            db_ops = AsyncDatabaseOperations(DatabaseType.POSTGRESQL, db_config)
            video_db = AsyncVideoDatabase(db_ops)
            tx_manager = AsyncTransactionManager(db_ops)
            logger.info("Database connections initialized")
        
        # Initialize external APIs
        if settings.youtube_api_key:
            youtube_config = APIConfig(
                base_url="https://www.googleapis.com/youtube/v3",
                api_key=settings.youtube_api_key,
                rate_limit_per_minute=100
            )
            youtube_api = AsyncYouTubeAPI(youtube_config)
            logger.info("YouTube API initialized")
        
        if settings.openai_api_key:
            openai_config = APIConfig(
                base_url="https://api.openai.com/v1",
                api_key=settings.openai_api_key,
                rate_limit_per_minute=60
            )
            openai_api = AsyncOpenAIAPI(openai_config)
            logger.info("OpenAI API initialized")
        
        if settings.stability_api_key:
            stability_config = APIConfig(
                base_url="https://api.stability.ai/v1",
                api_key=settings.stability_api_key,
                rate_limit_per_minute=30
            )
            stability_api = AsyncStabilityAIAPI(stability_config)
            logger.info("Stability AI API initialized")
        
        if settings.elevenlabs_api_key:
            elevenlabs_config = APIConfig(
                base_url="https://api.elevenlabs.io/v1",
                api_key=settings.elevenlabs_api_key,
                rate_limit_per_minute=50
            )
            elevenlabs_api = AsyncElevenLabsAPI(elevenlabs_config)
            logger.info("ElevenLabs API initialized")
        
        logger.info("Video-OpusClip application started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        logger.info("Shutting down Video-OpusClip application...")
        
        # Cleanup resources
        if flow_manager:
            await flow_manager.shutdown()
        
        if db_ops:
            await db_ops.close()
        
        logger.info("Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-driven video processing system for short-form video platforms",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Setup error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR"
        ).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP exception: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.detail,
            error_code=f"HTTP_{exc.status_code}"
        ).dict()
    )

# Dependency injection
async def get_flow_manager() -> AsyncFlowManager:
    if not flow_manager:
        raise HTTPException(status_code=503, detail="Flow manager not available")
    return flow_manager

async def get_video_db() -> AsyncVideoDatabase:
    if not video_db:
        raise HTTPException(status_code=503, detail="Database not available")
    return video_db

async def get_tx_manager() -> AsyncTransactionManager:
    if not tx_manager:
        raise HTTPException(status_code=503, detail="Transaction manager not available")
    return tx_manager

async def get_youtube_api() -> Optional[AsyncYouTubeAPI]:
    return youtube_api

async def get_openai_api() -> Optional[AsyncOpenAIAPI]:
    return openai_api

async def get_stability_api() -> Optional[AsyncStabilityAIAPI]:
    return stability_api

async def get_elevenlabs_api() -> Optional[AsyncElevenLabsAPI]:
    return elevenlabs_api

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        success=True,
        message="Video-OpusClip is running",
        version=settings.app_version,
        status="healthy"
    )

# Video processing endpoints
@app.post("/videos", response_model=VideoResponse)
async def create_video(
    video_data: VideoCreateRequest,
    background_tasks: BackgroundTasks,
    flow_mgr: AsyncFlowManager = Depends(get_flow_manager),
    video_db_instance: AsyncVideoDatabase = Depends(get_video_db),
    youtube_api_instance: Optional[AsyncYouTubeAPI] = Depends(get_youtube_api),
    openai_api_instance: Optional[AsyncOpenAIAPI] = Depends(get_openai_api)
):
    """Create a new video processing job"""
    try:
        # Create video record
        video_record = {
            "title": video_data.title,
            "description": video_data.description,
            "url": video_data.url,
            "duration": video_data.duration,
            "resolution": video_data.resolution,
            "status": "pending",
            "priority": video_data.priority,
            "tags": video_data.tags
        }
        
        video_id = await video_db_instance.create_video_record(video_record)
        
        # Add background task for processing
        background_tasks.add_task(
            process_video_background,
            video_id,
            video_data,
            flow_mgr,
            video_db_instance,
            youtube_api_instance,
            openai_api_instance
        )
        
        return VideoResponse(
            success=True,
            message="Video processing job created",
            data={
                "id": video_id,
                "title": video_data.title,
                "status": "pending",
                "priority": video_data.priority
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to create video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    video_db_instance: AsyncVideoDatabase = Depends(get_video_db)
):
    """Get video by ID"""
    try:
        video = await video_db_instance.get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return VideoResponse(
            success=True,
            message="Video retrieved successfully",
            data=video
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/videos/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: str,
    video_data: VideoUpdateRequest,
    video_db_instance: AsyncVideoDatabase = Depends(get_video_db)
):
    """Update video status"""
    try:
        success = await video_db_instance.update_video_status(video_id, video_data.status)
        if not success:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return VideoResponse(
            success=True,
            message="Video updated successfully",
            data={"id": video_id, "status": video_data.status}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/videos/batch", response_model=BatchVideoResponse)
async def create_batch_videos(
    batch_data: BatchVideoRequest,
    background_tasks: BackgroundTasks,
    flow_mgr: AsyncFlowManager = Depends(get_flow_manager),
    video_db_instance: AsyncVideoDatabase = Depends(get_video_db)
):
    """Create multiple video processing jobs"""
    try:
        video_ids = []
        
        for video_data in batch_data.videos:
            video_record = {
                "title": video_data.title,
                "description": video_data.description,
                "url": video_data.url,
                "duration": video_data.duration,
                "resolution": video_data.resolution,
                "status": "pending",
                "priority": video_data.priority,
                "tags": video_data.tags
            }
            
            video_id = await video_db_instance.create_video_record(video_record)
            video_ids.append(video_id)
            
            # Add background task for each video
            background_tasks.add_task(
                process_video_background,
                video_id,
                video_data,
                flow_mgr,
                video_db_instance,
                None,
                None
            )
        
        return BatchVideoResponse(
            success=True,
            message=f"Created {len(video_ids)} video processing jobs",
            data={"video_ids": video_ids, "count": len(video_ids)}
        )
        
    except Exception as e:
        logger.error(f"Failed to create batch videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background processing function
async def process_video_background(
    video_id: str,
    video_data: VideoCreateRequest,
    flow_mgr: AsyncFlowManager,
    video_db_instance: AsyncVideoDatabase,
    youtube_api_instance: Optional[AsyncYouTubeAPI],
    openai_api_instance: Optional[AsyncOpenAIAPI]
):
    """Background video processing task"""
    try:
        logger.info(f"Starting background processing for video {video_id}")
        
        # Update status to processing
        await video_db_instance.update_video_status(video_id, "processing")
        
        # Create processing job
        job_data = {
            "video_id": video_id,
            "type": "video_processing",
            "status": "pending",
            "priority": video_data.priority,
            "parameters": {
                "title": video_data.title,
                "description": video_data.description,
                "url": video_data.url,
                "duration": video_data.duration,
                "resolution": video_data.resolution,
                "tags": video_data.tags
            }
        }
        
        job_id = await video_db_instance.create_processing_job(job_data)
        
        # Process video using async flow
        async def video_processing_workflow():
            # Step 1: Download video
            logger.info(f"Downloading video {video_id}")
            # Simulate download
            await asyncio.sleep(2)
            
            # Step 2: Extract metadata
            logger.info(f"Extracting metadata for video {video_id}")
            # Simulate metadata extraction
            await asyncio.sleep(1)
            
            # Step 3: Generate captions (if OpenAI API available)
            if openai_api_instance:
                logger.info(f"Generating captions for video {video_id}")
                try:
                    caption_prompt = f"Generate engaging captions for a video titled '{video_data.title}' with description: {video_data.description}"
                    captions = await openai_api_instance.generate_captions(
                        audio_text=caption_prompt,
                        style="casual",
                        language="en"
                    )
                    logger.info(f"Generated captions for video {video_id}")
                except Exception as e:
                    logger.warning(f"Failed to generate captions for video {video_id}: {e}")
            
            # Step 4: Create clips
            logger.info(f"Creating clips for video {video_id}")
            # Simulate clip creation
            await asyncio.sleep(3)
            
            # Step 5: Update status to completed
            await video_db_instance.update_video_status(video_id, "completed")
            await video_db_instance.update_job_status(job_id, "completed")
            
            logger.info(f"Completed processing for video {video_id}")
        
        # Execute workflow
        await flow_mgr.execute_workflow(video_processing_workflow)
        
    except Exception as e:
        logger.error(f"Background processing failed for video {video_id}: {e}")
        await video_db_instance.update_video_status(video_id, "failed")
        if 'job_id' in locals():
            await video_db_instance.update_job_status(job_id, "failed")

# Metrics endpoint
@app.get("/metrics")
async def get_metrics(
    flow_mgr: AsyncFlowManager = Depends(get_flow_manager)
):
    """Get system metrics"""
    try:
        metrics = flow_mgr.metrics_collector.get_metrics()
        return {
            "success": True,
            "message": "Metrics retrieved successfully",
            "data": metrics
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Main function
def main():
    """Main application entry point"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main() 