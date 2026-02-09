"""
Avatar Manager for HeyGen AI
============================

Manages avatar generation, lip-sync, and facial enhancements using
specialized services for enterprise-grade performance.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
import uuid

# Core imports
from .base_service import BaseService, ServiceType, HealthCheckResult, ServiceStatus
from .error_handler import ErrorHandler, with_error_handling, with_retry
from .config_manager import ConfigurationManager
from .logging_service import LoggingService

# Service imports
from .face_processing_service import FaceProcessingService
from .diffusion_pipeline_service import DiffusionPipelineService
from .lip_sync_service import LipSyncService
from .avatar_model_repository import AvatarModelRepository
from .image_processing_service import ImageProcessingService
from .video_generation_service import VideoGenerationService

logger = logging.getLogger(__name__)


@dataclass
class AvatarGenerationRequest:
    """Request for avatar generation."""
    
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str = ""
    style: str = "realistic"
    gender: str = "neutral"
    age_range: str = "adult"
    ethnicity: str = "diverse"
    expression: str = "neutral"
    lighting: str = "studio"
    background: str = "professional"
    quality: str = "high"
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AvatarGenerationResult:
    """Result of avatar generation."""
    
    request_id: str
    avatar_path: str
    metadata: Dict[str, Any]
    generation_time: float
    quality_score: float
    timestamp: datetime = field(default_factory=datetime.now)


class AvatarManager(BaseService):
    """Orchestrator for avatar generation and management."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the avatar manager."""
        super().__init__("AvatarManager", ServiceType.CORE, config)
        
        # Initialize services
        self.face_processing: Optional[FaceProcessingService] = None
        self.diffusion_pipeline: Optional[DiffusionPipelineService] = None
        self.lip_sync: Optional[LipSyncService] = None
        self.avatar_repository: Optional[AvatarModelRepository] = None
        self.image_processing: Optional[ImageProcessingService] = None
        self.video_generation: Optional[VideoGenerationService] = None
        
        # Error handling
        self.error_handler = ErrorHandler()
        
        # Configuration
        self.config_manager = ConfigurationManager()
        
        # Logging
        self.logging_service = LoggingService()
        
        # Performance tracking
        self.generation_stats = {
            "total_generated": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "average_generation_time": 0.0
        }

    async def _initialize_service_impl(self) -> None:
        """Initialize avatar generation services."""
        try:
            logger.info("Initializing avatar generation services...")
            
            # Initialize specialized services
            self.face_processing = FaceProcessingService()
            self.diffusion_pipeline = DiffusionPipelineService()
            self.lip_sync = LipSyncService()
            self.avatar_repository = AvatarModelRepository()
            self.image_processing = ImageProcessingService()
            self.video_generation = VideoGenerationService()
            
            # Wait for all services to be ready
            await asyncio.gather(
                self.face_processing.health_check(),
                self.diffusion_pipeline.health_check(),
                self.lip_sync.health_check(),
                self.avatar_repository.health_check(),
                self.image_processing.health_check(),
                self.video_generation.health_check()
            )
            
            logger.info("All avatar services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize avatar services: {e}")
            raise

    @with_error_handling
    @with_retry(max_attempts=3)
    async def generate_avatar(self, request: AvatarGenerationRequest) -> AvatarGenerationResult:
        """Generate an avatar based on the request."""
        start_time = time.time()
        
        try:
            logger.info(f"Generating avatar for request {request.request_id}")
            
            # Validate request
            if not request.prompt:
                raise ValueError("Avatar generation prompt is required")
            
            # Generate avatar using diffusion pipeline
            if not self.diffusion_pipeline:
                raise RuntimeError("Diffusion pipeline service not initialized")
            
            avatar_path = await self.diffusion_pipeline.generate_avatar(
                prompt=request.prompt,
                style=request.style,
                gender=request.gender,
                age_range=request.age_range,
                ethnicity=request.ethnicity,
                expression=request.expression,
                lighting=request.lighting,
                background=request.background,
                quality=request.quality
            )
            
            # Apply facial enhancements
            if self.face_processing and avatar_path:
                avatar_path = await self.face_processing.enhance_facial_features(avatar_path)
            
            # Calculate generation time and quality
            generation_time = time.time() - start_time
            quality_score = self._calculate_quality_score(request, generation_time)
            
            # Update statistics
            self._update_generation_stats(generation_time, True)
            
            # Create result
            result = AvatarGenerationResult(
                request_id=request.request_id,
                avatar_path=avatar_path,
                metadata={
                    "prompt": request.prompt,
                    "style": request.style,
                    "generation_time": generation_time,
                    "quality_score": quality_score,
                    "services_used": ["diffusion_pipeline", "face_processing"]
                },
                generation_time=generation_time,
                quality_score=quality_score
            )
            
            logger.info(f"Avatar generated successfully in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            self._update_generation_stats(time.time() - start_time, False)
            logger.error(f"Avatar generation failed: {e}")
            raise

    @with_error_handling
    async def generate_avatar_video(
        self, 
        avatar_path: str, 
        audio_path: str,
        lip_sync_enabled: bool = True,
        gesture_enabled: bool = False
    ) -> str:
        """Generate a video with the avatar speaking the audio."""
        try:
            logger.info(f"Generating avatar video for {avatar_path}")
            
            if not self.video_generation:
                raise RuntimeError("Video generation service not initialized")
            
            # Generate video with lip-sync
            video_path = await self.video_generation.create_avatar_video(
                avatar_path=avatar_path,
                audio_path=audio_path,
                lip_sync_enabled=lip_sync_enabled,
                gesture_enabled=gesture_enabled
            )
            
            logger.info(f"Avatar video generated successfully: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Avatar video generation failed: {e}")
            raise

    async def health_check(self) -> HealthCheckResult:
        """Check the health of all avatar services."""
        try:
            # Check base service health
            base_health = await super().health_check()
            
            # Check individual services
            service_health = {}
            overall_status = ServiceStatus.HEALTHY
            
            services = {
                "face_processing": self.face_processing,
                "diffusion_pipeline": self.diffusion_pipeline,
                "lip_sync": self.lip_sync,
                "avatar_repository": self.avatar_repository,
                "image_processing": self.image_processing,
                "video_generation": self.video_generation
            }
            
            for service_name, service in services.items():
                if service:
                    try:
                        health = await service.health_check()
                        service_health[service_name] = health
                        if health.status == ServiceStatus.UNHEALTHY:
                            overall_status = ServiceStatus.DEGRADED
                    except Exception as e:
                        service_health[service_name] = HealthCheckResult(
                            status=ServiceStatus.UNHEALTHY,
                            error_message=str(e)
                        )
                        overall_status = ServiceStatus.DEGRADED
                else:
                    service_health[service_name] = HealthCheckResult(
                        status=ServiceStatus.UNHEALTHY,
                        error_message="Service not initialized"
                    )
                    overall_status = ServiceStatus.DEGRADED
            
            # Update base health with service details
            base_health.status = overall_status
            base_health.details.update({
                "services": service_health,
                "generation_stats": self.generation_stats
            })
            
            return base_health
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                error_message=str(e)
            )

    def _calculate_quality_score(self, request: AvatarGenerationRequest, generation_time: float) -> float:
        """Calculate quality score based on request and performance."""
        base_score = 0.8
        
        # Adjust for quality setting
        quality_multipliers = {
            "low": 0.7,
            "medium": 0.85,
            "high": 1.0,
            "ultra": 1.2
        }
        base_score *= quality_multipliers.get(request.quality, 1.0)
        
        # Adjust for generation time (faster is better, up to a point)
        if generation_time < 5.0:
            base_score *= 1.1
        elif generation_time > 30.0:
            base_score *= 0.9
        
        # Adjust for prompt complexity
        if len(request.prompt) > 100:
            base_score *= 1.05
        
        return min(1.0, max(0.0, base_score))

    def _update_generation_stats(self, generation_time: float, success: bool):
        """Update generation statistics."""
        self.generation_stats["total_generated"] += 1
        
        if success:
            self.generation_stats["successful_generations"] += 1
        else:
            self.generation_stats["failed_generations"] += 1
        
        # Update average generation time
        current_avg = self.generation_stats["average_generation_time"]
        total_successful = self.generation_stats["successful_generations"]
        
        if total_successful > 0:
            self.generation_stats["average_generation_time"] = (
                (current_avg * (total_successful - 1) + generation_time) / total_successful
            )

    async def get_available_styles(self) -> List[str]:
        """Get available avatar styles."""
        return [
            "realistic", "cartoon", "anime", "3d", "sketch", 
            "watercolor", "oil_painting", "digital_art"
        ]

    async def get_available_expressions(self) -> List[str]:
        """Get available facial expressions."""
        return [
            "neutral", "happy", "sad", "angry", "surprised", 
            "confused", "excited", "calm", "professional"
        ]

    async def cleanup_temp_files(self) -> None:
        """Clean up temporary files."""
        try:
            # This would clean up temporary files created during generation
            logger.info("Cleaning up temporary avatar files")
            # Implementation would depend on the specific services
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")
