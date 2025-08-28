"""
HeyGen AI - Main System Orchestrator
====================================

Enterprise-grade AI video generation system that integrates all core managers
and services for comprehensive avatar generation, voice synthesis, video rendering,
and advanced features with robust error handling and monitoring.
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
from .core.base_service import BaseService, ServiceType, HealthCheckResult, ServiceStatus
from .core.error_handler import ErrorHandler, with_error_handling, with_retry
from .core.config_manager import ConfigurationManager, HeyGenAIConfig
from .monitoring.logging_service import LoggingService

# Core managers
from .core.avatar_manager import AvatarManager, AvatarGenerationRequest, AvatarGenerationResult
from .core.voice_engine import VoiceEngine, VoiceGenerationRequest, VoiceGenerationResult
from .core.video_renderer import VideoRenderer, VideoRenderRequest, VideoRenderResult

# Phase 2 services
from .core.gesture_emotion_controller import GestureEmotionController, GestureRequest, EmotionRequest
from .core.multi_platform_exporter import MultiPlatformExporter, PlatformType, ExportConfig, VideoFormat

# Phase 3 services
from .core.external_api_integration import ExternalAPIManager
from .core.performance_optimizer import PerformanceOptimizer

# Phase 4 enterprise services
from .core.real_time_collaboration import CollaborationManager
from .core.advanced_analytics import AdvancedAnalyticsSystem
from .core.enterprise_features import EnterpriseFeatures

# Library services
from .data.avatar_library.avatar_library_service import AvatarLibraryService
from .data.voice_library.voice_library_service import VoiceLibraryService
from .data.video_templates.video_template_service import VideoTemplateService

logger = logging.getLogger(__name__)


@dataclass
class VideoGenerationRequest:
    """Complete request for video generation."""
    
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Avatar configuration
    avatar_prompt: str = ""
    avatar_style: str = "realistic"
    avatar_gender: str = "neutral"
    avatar_age_range: str = "adult"
    avatar_ethnicity: str = "diverse"
    avatar_expression: str = "neutral"
    
    # Voice configuration
    voice_text: str = ""
    voice_model_id: str = ""
    voice_language: str = "en"
    voice_emotion: str = "neutral"
    voice_speed: float = 1.0
    voice_pitch: float = 0.0
    
    # Video configuration
    video_resolution: str = "1920x1080"
    video_fps: int = 30
    video_quality: str = "high"
    video_format: str = "mp4"
    
    # Gesture and emotion
    gestures: List[str] = field(default_factory=list)
    emotions: List[str] = field(default_factory=list)
    
    # Export configuration
    export_platforms: List[str] = field(default_factory=list)
    
    # Custom attributes
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class VideoGenerationResult:
    """Complete result of video generation."""
    
    request_id: str
    avatar_path: str
    audio_path: str
    video_path: str
    export_paths: Dict[str, str]
    metadata: Dict[str, Any]
    total_generation_time: float
    quality_score: float
    timestamp: datetime = field(default_factory=datetime.now)


class HeyGenAISystem(BaseService):
    """Main orchestrator for the HeyGen AI system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the HeyGen AI system."""
        super().__init__("HeyGenAISystem", ServiceType.CORE, config)
        
        # Configuration
        self.config_manager = ConfigurationManager()
        self.system_config: Optional[HeyGenAIConfig] = None
        
        # Error handling
        self.error_handler = ErrorHandler()
        
        # Logging service
        self.logging_service = LoggingService()
        
        # Core managers
        self.avatar_manager: Optional[AvatarManager] = None
        self.voice_engine: Optional[VoiceEngine] = None
        self.video_renderer: Optional[VideoRenderer] = None
        
        # Phase 2 services
        self.gesture_emotion_controller: Optional[GestureEmotionController] = None
        self.multi_platform_exporter: Optional[MultiPlatformExporter] = None
        
        # Phase 3 services
        self.external_api_manager: Optional[ExternalAPIManager] = None
        self.performance_optimizer: Optional[PerformanceOptimizer] = None
        
        # Phase 4 enterprise services
        self.collaboration_manager: Optional[CollaborationManager] = None
        self.advanced_analytics: Optional[AdvancedAnalyticsSystem] = None
        self.enterprise_features: Optional[EnterpriseFeatures] = None
        
        # Library services
        self.avatar_library: Optional[AvatarLibraryService] = None
        self.voice_library: Optional[VoiceLibraryService] = None
        self.video_templates: Optional[VideoTemplateService] = None
        
        # Performance tracking
        self.system_stats = {
            "total_videos_generated": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "average_generation_time": 0.0,
            "total_processing_time": 0.0
        }

    async def _initialize_service_impl(self) -> None:
        """Initialize all HeyGen AI services."""
        try:
            logger.info("Initializing HeyGen AI system...")
            
            # Load configuration
            await self._load_configuration()
            
            # Initialize core managers
            await self._initialize_core_managers()
            
            # Initialize Phase 2 services
            await self._initialize_phase2_services()
            
            # Initialize Phase 3 services
            await self._initialize_phase3_services()
            
            # Initialize Phase 4 enterprise services
            await self._initialize_phase4_services()
            
            # Initialize library services
            await self._initialize_library_services()
            
            # Validate system health
            await self._validate_system_health()
            
            logger.info("HeyGen AI system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize HeyGen AI system: {e}")
            raise

    async def _load_configuration(self) -> None:
        """Load system configuration."""
        try:
            self.system_config = await self.config_manager.load_config()
            logger.info("System configuration loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load configuration, using defaults: {e}")
            self.system_config = HeyGenAIConfig()

    async def _initialize_core_managers(self) -> None:
        """Initialize core AI managers."""
        try:
            logger.info("Initializing core managers...")
            
            self.avatar_manager = AvatarManager()
            self.voice_engine = VoiceEngine()
            self.video_renderer = VideoRenderer()
            
            # Wait for all core managers to be ready
            await asyncio.gather(
                self.avatar_manager.health_check(),
                self.voice_engine.health_check(),
                self.video_renderer.health_check()
            )
            
            logger.info("Core managers initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize core managers: {e}")
            raise

    async def _initialize_phase2_services(self) -> None:
        """Initialize Phase 2 services."""
        try:
            logger.info("Initializing Phase 2 services...")
            
            self.gesture_emotion_controller = GestureEmotionController()
            self.multi_platform_exporter = MultiPlatformExporter()
            
            # Wait for Phase 2 services to be ready
            await asyncio.gather(
                self.gesture_emotion_controller.health_check(),
                self.multi_platform_exporter.health_check()
            )
            
            logger.info("Phase 2 services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Phase 2 services: {e}")
            raise

    async def _initialize_phase3_services(self) -> None:
        """Initialize Phase 3 services."""
        try:
            logger.info("Initializing Phase 3 services...")
            
            self.external_api_manager = ExternalAPIManager()
            self.performance_optimizer = PerformanceOptimizer()
            
            # Wait for Phase 3 services to be ready
            await asyncio.gather(
                self.external_api_manager.health_check_all(),
                self.performance_optimizer.get_performance_stats()
            )
            
            logger.info("Phase 3 services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Phase 3 services: {e}")
            raise

    async def _initialize_phase4_services(self) -> None:
        """Initialize Phase 4 enterprise services."""
        try:
            logger.info("Initializing Phase 4 enterprise services...")
            
            self.collaboration_manager = CollaborationManager()
            self.advanced_analytics = AdvancedAnalyticsSystem()
            self.enterprise_features = EnterpriseFeatures()
            
            # Wait for Phase 4 services to be ready
            await asyncio.gather(
                self.collaboration_manager.health_check(),
                self.advanced_analytics.health_check(),
                self.enterprise_features.health_check()
            )
            
            logger.info("Phase 4 enterprise services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Phase 4 services: {e}")
            raise

    async def _initialize_library_services(self) -> None:
        """Initialize library services."""
        try:
            logger.info("Initializing library services...")
            
            self.avatar_library = AvatarLibraryService()
            self.voice_library = VoiceLibraryService()
            self.video_templates = VideoTemplateService()
            
            # Wait for library services to be ready
            await asyncio.gather(
                self.avatar_library.health_check(),
                self.voice_library.health_check(),
                self.video_templates.health_check()
            )
            
            logger.info("Library services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize library services: {e}")
            raise

    async def _validate_system_health(self) -> None:
        """Validate overall system health."""
        try:
            health_status = await self.health_check()
            if health_status.status == ServiceStatus.UNHEALTHY:
                raise RuntimeError("System health check failed")
            logger.info("System health validation passed")
        except Exception as e:
            logger.error(f"System health validation failed: {e}")
            raise

    @with_error_handling
    @with_retry(max_attempts=3)
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Generate a complete video with avatar, voice, and effects."""
        start_time = time.time()
        
        try:
            logger.info(f"Starting video generation for request {request.request_id}")
            
            # Validate request
            if not request.avatar_prompt:
                raise ValueError("Avatar prompt is required")
            
            if not request.voice_text:
                raise ValueError("Voice text is required")
            
            # Step 1: Generate avatar
            logger.info("Generating avatar...")
            avatar_request = AvatarGenerationRequest(
                prompt=request.avatar_prompt,
                style=request.avatar_style,
                gender=request.avatar_gender,
                age_range=request.avatar_age_range,
                ethnicity=request.avatar_ethnicity,
                expression=request.avatar_expression
            )
            avatar_result = await self.avatar_manager.generate_avatar(avatar_request)
            
            # Step 2: Generate voice
            logger.info("Generating voice...")
            voice_request = VoiceGenerationRequest(
                text=request.voice_text,
                voice_model_id=request.voice_model_id,
                language=request.voice_language,
                emotion=request.voice_emotion,
                speed=request.voice_speed,
                pitch=request.voice_pitch
            )
            voice_result = await self.voice_engine.generate_speech(voice_request)
            
            # Step 3: Generate video with lip-sync
            logger.info("Generating video with lip-sync...")
            video_path = await self.avatar_manager.generate_avatar_video(
                avatar_path=avatar_result.avatar_path,
                audio_path=voice_result.audio_path,
                lip_sync_enabled=True,
                gesture_enabled=bool(request.gestures)
            )
            
            # Step 4: Apply gestures and emotions
            if request.gestures or request.emotions:
                logger.info("Applying gestures and emotions...")
                await self._apply_gestures_and_emotions(request, video_path)
            
            # Step 5: Render final video
            logger.info("Rendering final video...")
            video_request = VideoRenderRequest(
                video_path=video_path,
                audio_path=voice_result.audio_path,
                output_path=f"./exports/video_{request.request_id}.{request.video_format}",
                config=self._create_video_config(request)
            )
            video_result = await self.video_renderer.render_video(video_request)
            
            # Step 6: Export for platforms
            export_paths = {}
            if request.export_platforms:
                logger.info("Exporting for platforms...")
                export_paths = await self._export_for_platforms(
                    video_result.output_path, request.export_platforms
                )
            
            # Calculate total generation time
            total_generation_time = time.time() - start_time
            quality_score = self._calculate_overall_quality(
                avatar_result, voice_result, video_result, total_generation_time
            )
            
            # Update statistics
            self._update_generation_stats(total_generation_time, True)
            
            # Create result
            result = VideoGenerationResult(
                request_id=request.request_id,
                avatar_path=avatar_result.avatar_path,
                audio_path=voice_result.audio_path,
                video_path=video_result.output_path,
                export_paths=export_paths,
                metadata={
                    "avatar_metadata": avatar_result.metadata,
                    "voice_metadata": voice_result.metadata,
                    "video_metadata": video_result.metadata,
                    "gestures_applied": len(request.gestures),
                    "emotions_applied": len(request.emotions),
                    "export_platforms": request.export_platforms
                },
                total_generation_time=total_generation_time,
                quality_score=quality_score
            )
            
            logger.info(f"Video generation completed successfully in {total_generation_time:.2f}s")
            return result
            
        except Exception as e:
            self._update_generation_stats(time.time() - start_time, False)
            logger.error(f"Video generation failed: {e}")
            raise

    async def _apply_gestures_and_emotions(self, request: VideoGenerationRequest, video_path: str) -> None:
        """Apply gestures and emotions to the video."""
        try:
            # Apply gestures
            for gesture in request.gestures:
                gesture_request = GestureRequest(gesture_type=gesture)
                await self.gesture_emotion_controller.generate_gesture(gesture_request)
            
            # Apply emotions
            for emotion in request.emotions:
                emotion_request = EmotionRequest(emotion_type=emotion)
                await self.gesture_emotion_controller.generate_emotion(emotion_request)
                
        except Exception as e:
            logger.warning(f"Failed to apply gestures and emotions: {e}")

    def _create_video_config(self, request: VideoGenerationRequest):
        """Create video configuration from request."""
        from .core.video_renderer import VideoConfig
        
        return VideoConfig(
            resolution=request.video_resolution,
            fps=request.video_fps,
            quality=request.video_quality,
            format=request.video_format
        )

    async def _export_for_platforms(self, video_path: str, platforms: List[str]) -> Dict[str, str]:
        """Export video for different platforms."""
        try:
            export_paths = {}
            for platform in platforms:
                if platform in ["youtube", "tiktok", "instagram", "linkedin", "facebook"]:
                    platform_type = PlatformType(platform.upper())
                    export_config = ExportConfig(
                        platform=platform_type,
                        quality="high",
                        format=VideoFormat.MP4
                    )
                    export_path = await self.multi_platform_exporter.export_video(
                        video_path, export_config
                    )
                    export_paths[platform] = export_path
            
            return export_paths
            
        except Exception as e:
            logger.warning(f"Failed to export for platforms: {e}")
            return {}

    def _calculate_overall_quality(
        self, 
        avatar_result: AvatarGenerationResult,
        voice_result: VoiceGenerationResult,
        video_result: VideoRenderResult,
        total_time: float
    ) -> float:
        """Calculate overall quality score."""
        # Weighted average of individual quality scores
        weights = {
            "avatar": 0.3,
            "voice": 0.2,
            "video": 0.3,
            "performance": 0.2
        }
        
        avatar_score = avatar_result.quality_score
        voice_score = voice_result.quality_score
        video_score = video_result.quality_score
        
        # Performance score (faster is better, up to a point)
        performance_score = 1.0
        if total_time > 60.0:  # More than 1 minute
            performance_score = 0.8
        elif total_time < 10.0:  # Less than 10 seconds
            performance_score = 1.1
        
        overall_score = (
            avatar_score * weights["avatar"] +
            voice_score * weights["voice"] +
            video_score * weights["video"] +
            performance_score * weights["performance"]
        )
        
        return min(1.0, max(0.0, overall_score))

    def _update_generation_stats(self, generation_time: float, success: bool):
        """Update generation statistics."""
        self.system_stats["total_videos_generated"] += 1
        
        if success:
            self.system_stats["successful_generations"] += 1
            self.system_stats["total_processing_time"] += generation_time
        else:
            self.system_stats["failed_generations"] += 1
        
        # Update average generation time
        current_avg = self.system_stats["average_generation_time"]
        total_successful = self.system_stats["successful_generations"]
        
        if total_successful > 0:
            self.system_stats["average_generation_time"] = (
                (current_avg * (total_successful - 1) + generation_time) / total_successful
            )

    async def health_check(self) -> HealthCheckResult:
        """Check the health of the entire HeyGen AI system."""
        try:
            # Check base service health
            base_health = await super().health_check()
            
            # Check all services
            service_health = {}
            overall_status = ServiceStatus.HEALTHY
            
            # Core managers
            if self.avatar_manager:
                service_health["avatar_manager"] = await self.avatar_manager.health_check()
                if service_health["avatar_manager"].status == ServiceStatus.UNHEALTHY:
                    overall_status = ServiceStatus.DEGRADED
            
            if self.voice_engine:
                service_health["voice_engine"] = await self.voice_engine.health_check()
                if service_health["voice_engine"].status == ServiceStatus.UNHEALTHY:
                    overall_status = ServiceStatus.DEGRADED
            
            if self.video_renderer:
                service_health["video_renderer"] = await self.video_renderer.health_check()
                if service_health["video_renderer"].status == ServiceStatus.UNHEALTHY:
                    overall_status = ServiceStatus.DEGRADED
            
            # Phase 2 services
            if self.gesture_emotion_controller:
                service_health["gesture_emotion_controller"] = await self.gesture_emotion_controller.health_check()
                if service_health["gesture_emotion_controller"].status == ServiceStatus.UNHEALTHY:
                    overall_status = ServiceStatus.DEGRADED
            
            if self.multi_platform_exporter:
                service_health["multi_platform_exporter"] = await self.multi_platform_exporter.health_check()
                if service_health["multi_platform_exporter"].status == ServiceStatus.UNHEALTHY:
                    overall_status = ServiceStatus.DEGRADED
            
            # Phase 3 services
            if self.external_api_manager:
                service_health["external_api_manager"] = await self.external_api_manager.health_check_all()
            
            if self.performance_optimizer:
                service_health["performance_optimizer"] = await self.performance_optimizer.get_performance_stats()
            
            # Phase 4 enterprise services
            if self.collaboration_manager:
                service_health["collaboration_manager"] = await self.collaboration_manager.health_check()
                if service_health["collaboration_manager"].status == ServiceStatus.UNHEALTHY:
                    overall_status = ServiceStatus.DEGRADED
            
            if self.advanced_analytics:
                service_health["advanced_analytics"] = await self.advanced_analytics.health_check()
                if service_health["advanced_analytics"].status == ServiceStatus.UNHEALTHY:
                    overall_status = ServiceStatus.DEGRADED
            
            if self.enterprise_features:
                service_health["enterprise_features"] = await self.enterprise_features.health_check()
                if service_health["enterprise_features"].status == ServiceStatus.UNHEALTHY:
                    overall_status = ServiceStatus.DEGRADED
            
            # Library services
            if self.avatar_library:
                service_health["avatar_library"] = await self.avatar_library.health_check()
            
            if self.voice_library:
                service_health["voice_library"] = await self.voice_library.health_check()
            
            if self.video_templates:
                service_health["video_templates"] = await self.video_templates.health_check()
            
            # Update base health
            base_health.status = overall_status
            base_health.details.update({
                "services": service_health,
                "system_stats": self.system_stats,
                "configuration": {
                    "environment": self.system_config.environment if self.system_config else "unknown",
                    "version": self.system_config.version if self.system_config else "unknown"
                }
            })
            
            return base_health
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                error_message=str(e)
            )

    async def get_avatar_library_data(self) -> Dict[str, Any]:
        """Get avatar library information."""
        if self.avatar_library:
            return await self.avatar_library.get_library_info()
        return {"error": "Avatar library not available"}

    async def get_voice_library_data(self) -> Dict[str, Any]:
        """Get voice library information."""
        if self.voice_library:
            return await self.voice_library.get_library_info()
        return {"error": "Voice library not available"}

    async def get_video_templates(self) -> List[Dict[str, Any]]:
        """Get available video templates."""
        if self.video_templates:
            return await self.video_templates.get_templates()
        return []

    async def get_export_platforms(self) -> List[str]:
        """Get supported export platforms."""
        if self.multi_platform_exporter:
            return await self.multi_platform_exporter.get_supported_platforms()
        return []

    async def shutdown(self) -> None:
        """Gracefully shutdown the HeyGen AI system."""
        try:
            logger.info("Shutting down HeyGen AI system...")
            
            # Cleanup services
            if self.avatar_manager:
                await self.avatar_manager.cleanup_temp_files()
            
            if self.voice_engine:
                await self.voice_engine.cleanup_temp_files()
            
            if self.video_renderer:
                await self.video_renderer.cleanup_temp_files()
            
            if self.gesture_emotion_controller:
                await self.gesture_emotion_controller.cleanup_temp_files()
            
            logger.info("HeyGen AI system shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global instance for easy access
heygen_ai_system: Optional[HeyGenAISystem] = None


async def get_heygen_ai_system() -> HeyGenAISystem:
    """Get or create the global HeyGen AI system instance."""
    global heygen_ai_system
    
    if heygen_ai_system is None:
        heygen_ai_system = HeyGenAISystem()
        await heygen_ai_system._initialize_service_impl()
    
    return heygen_ai_system


async def shutdown_heygen_ai_system() -> None:
    """Shutdown the global HeyGen AI system instance."""
    global heygen_ai_system
    
    if heygen_ai_system:
        await heygen_ai_system.shutdown()
        heygen_ai_system = None
