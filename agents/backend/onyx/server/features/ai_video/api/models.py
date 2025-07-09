"""
Pydantic Models for AI Video API
===============================

Data models and validation for the AI video generation API.
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    """Job status enumeration."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VideoFormat(str, Enum):
    """Video format enumeration."""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WEBM = "webm"

class QualityLevel(str, Enum):
    """Quality level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""
    
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Text prompt describing the video to generate"
    )
    
    num_frames: int = Field(
        default=16,
        ge=8,
        le=64,
        description="Number of video frames to generate"
    )
    
    height: int = Field(
        default=512,
        ge=256,
        le=1024,
        description="Video height in pixels"
    )
    
    width: int = Field(
        default=512,
        ge=256,
        le=1024,
        description="Video width in pixels"
    )
    
    fps: int = Field(
        default=8,
        ge=1,
        le=30,
        description="Frames per second"
    )
    
    guidance_scale: float = Field(
        default=7.5,
        ge=1.0,
        le=20.0,
        description="Guidance scale for generation"
    )
    
    num_inference_steps: int = Field(
        default=50,
        ge=10,
        le=100,
        description="Number of inference steps"
    )
    
    quality: QualityLevel = Field(
        default=QualityLevel.MEDIUM,
        description="Quality level for generation"
    )
    
    format: VideoFormat = Field(
        default=VideoFormat.MP4,
        description="Output video format"
    )
    
    seed: Optional[int] = Field(
        default=None,
        ge=0,
        le=2**32-1,
        description="Random seed for reproducible generation"
    )
    
    negative_prompt: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Negative prompt to avoid certain elements"
    )
    
    @validator('height', 'width')
    def validate_dimensions(cls, v):
        """Validate that dimensions are divisible by 64."""
        if v % 64 != 0:
            raise ValueError('Height and width must be divisible by 64')
        return v
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate prompt content."""
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()
    
    @root_validator
    def validate_aspect_ratio(cls, values):
        """Validate aspect ratio constraints."""
        height = values.get('height')
        width = values.get('width')
        
        if height and width:
            aspect_ratio = width / height
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                raise ValueError('Aspect ratio must be between 0.5 and 2.0')
        
        return values

class VideoGenerationResponse(BaseModel):
    """Response model for video generation request."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Status message")
    estimated_time: Optional[int] = Field(None, description="Estimated processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.now, description="Job creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class JobStatusResponse(BaseModel):
    """Response model for job status."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    result_url: Optional[str] = Field(None, description="URL to download generated video")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class BatchGenerationRequest(BaseModel):
    """Request model for batch video generation."""
    
    requests: List[VideoGenerationRequest] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of video generation requests"
    )
    
    priority: Optional[str] = Field(
        default="normal",
        regex="^(low|normal|high|urgent)$",
        description="Processing priority"
    )
    
    @validator('requests')
    def validate_requests(cls, v):
        """Validate batch requests."""
        if len(v) > 10:
            raise ValueError('Maximum 10 requests allowed per batch')
        return v

class BatchGenerationResponse(BaseModel):
    """Response model for batch generation."""
    
    batch_id: str = Field(..., description="Unique batch identifier")
    job_ids: List[str] = Field(..., description="List of job identifiers")
    total_jobs: int = Field(..., description="Total number of jobs")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(default_factory=datetime.now, description="Batch creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VideoMetadata(BaseModel):
    """Model for video metadata."""
    
    job_id: str = Field(..., description="Job identifier")
    prompt: str = Field(..., description="Original prompt")
    parameters: Dict[str, Any] = Field(..., description="Generation parameters")
    file_size: int = Field(..., description="File size in bytes")
    duration: float = Field(..., description="Video duration in seconds")
    resolution: str = Field(..., description="Video resolution")
    format: str = Field(..., description="Video format")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class APIError(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HealthCheckResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    version: str = Field(..., description="API version")
    uptime: float = Field(..., description="Service uptime in seconds")
    memory_usage: Dict[str, float] = Field(..., description="Memory usage statistics")
    gpu_usage: Optional[Dict[str, float]] = Field(None, description="GPU usage statistics")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MetricsResponse(BaseModel):
    """API metrics response model."""
    
    total_jobs: int = Field(..., description="Total number of jobs")
    completed_jobs: int = Field(..., description="Number of completed jobs")
    failed_jobs: int = Field(..., description="Number of failed jobs")
    processing_jobs: int = Field(..., description="Number of jobs currently processing")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate")
    average_processing_time: Optional[float] = Field(None, description="Average processing time in seconds")
    total_requests: int = Field(..., description="Total API requests")
    active_users: int = Field(..., description="Number of active users")
    timestamp: datetime = Field(default_factory=datetime.now, description="Metrics timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserQuota(BaseModel):
    """User quota model."""
    
    user_id: str = Field(..., description="User identifier")
    daily_limit: int = Field(..., description="Daily job limit")
    daily_used: int = Field(..., description="Jobs used today")
    monthly_limit: int = Field(..., description="Monthly job limit")
    monthly_used: int = Field(..., description="Jobs used this month")
    remaining_daily: int = Field(..., description="Remaining daily jobs")
    remaining_monthly: int = Field(..., description="Remaining monthly jobs")
    reset_daily: datetime = Field(..., description="Daily reset timestamp")
    reset_monthly: datetime = Field(..., description="Monthly reset timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ModelConfig(BaseModel):
    """Model configuration model."""
    
    model_name: str = Field(..., description="Model name")
    model_version: str = Field(..., description="Model version")
    supported_formats: List[VideoFormat] = Field(..., description="Supported output formats")
    max_frames: int = Field(..., description="Maximum number of frames")
    max_resolution: str = Field(..., description="Maximum resolution")
    min_resolution: str = Field(..., description="Minimum resolution")
    supported_qualities: List[QualityLevel] = Field(..., description="Supported quality levels")
    default_parameters: Dict[str, Any] = Field(..., description="Default generation parameters")
    
class WebhookPayload(BaseModel):
    """Webhook payload model."""
    
    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Job status")
    result_url: Optional[str] = Field(None, description="Result URL")
    error_message: Optional[str] = Field(None, description="Error message")
    metadata: Optional[VideoMetadata] = Field(None, description="Video metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 