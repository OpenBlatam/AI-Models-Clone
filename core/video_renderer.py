"""
Video Renderer for HeyGen AI
============================

Provides comprehensive video rendering capabilities with advanced effects,
quality optimization, and multi-format support for enterprise-grade performance.
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

# Video processing imports
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, ImageClip
    from moviepy.video.fx import resize, crop, rotate, fadein, fadeout
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class VideoConfig:
    """Video configuration settings."""
    
    resolution: str = "1920x1080"
    fps: int = 30
    bitrate: str = "5000k"
    codec: str = "h264"
    format: str = "mp4"
    quality: str = "high"
    enable_hardware_acceleration: bool = True
    enable_compression: bool = True
    compression_quality: int = 85


@dataclass
class VideoEffect:
    """Video effect configuration."""
    
    effect_type: str
    parameters: Dict[str, Any]
    start_time: float = 0.0
    duration: float = 0.0
    intensity: float = 1.0


@dataclass
class VideoRenderRequest:
    """Request for video rendering."""
    
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    video_path: str = ""
    audio_path: Optional[str] = None
    output_path: str = ""
    config: VideoConfig = field(default_factory=VideoConfig)
    effects: List[VideoEffect] = field(default_factory=list)
    background: Optional[str] = None
    watermark: Optional[str] = None
    subtitle_path: Optional[str] = None
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class VideoRenderResult:
    """Result of video rendering."""
    
    request_id: str
    output_path: str
    duration: float
    file_size: int
    metadata: Dict[str, Any]
    render_time: float
    quality_score: float
    timestamp: datetime = field(default_factory=datetime.now)


class VideoRenderer(BaseService):
    """Comprehensive video rendering service."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the video renderer."""
        super().__init__("VideoRenderer", ServiceType.CORE, config)
        
        # Video configuration
        self.default_config = VideoConfig()
        
        # Error handling
        self.error_handler = ErrorHandler()
        
        # Configuration manager
        self.config_manager = ConfigurationManager()
        
        # Logging service
        self.logging_service = LoggingService()
        
        # Performance tracking
        self.render_stats = {
            "total_rendered": 0,
            "successful_renders": 0,
            "failed_renders": 0,
            "average_render_time": 0.0,
            "total_video_duration": 0.0
        }
        
        # Supported formats and codecs
        self.supported_formats = ["mp4", "avi", "mov", "mkv", "webm", "flv"]
        self.supported_codecs = ["h264", "h265", "vp9", "vp8", "av1"]
        self.quality_presets = {
            "low": {"bitrate": "1000k", "compression": 60},
            "medium": {"bitrate": "3000k", "compression": 75},
            "high": {"bitrate": "5000k", "compression": 85},
            "ultra": {"bitrate": "8000k", "compression": 95}
        }

    async def _initialize_service_impl(self) -> None:
        """Initialize video rendering services."""
        try:
            logger.info("Initializing video rendering services...")
            
            # Check dependencies
            await self._check_dependencies()
            
            # Initialize video processing
            await self._initialize_video_processing()
            
            # Validate configuration
            await self._validate_configuration()
            
            logger.info("Video renderer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize video renderer: {e}")
            raise

    async def _check_dependencies(self) -> None:
        """Check required dependencies."""
        missing_deps = []
        
        if not MOVIEPY_AVAILABLE:
            missing_deps.append("moviepy")
        
        if not OPENCV_AVAILABLE:
            missing_deps.append("opencv-python")
        
        if not PIL_AVAILABLE:
            missing_deps.append("Pillow")
        
        if missing_deps:
            logger.warning(f"Missing video processing dependencies: {missing_deps}")
            logger.warning("Some video features may not be available")

    async def _initialize_video_processing(self) -> None:
        """Initialize video processing capabilities."""
        try:
            # Test basic video operations
            if MOVIEPY_AVAILABLE:
                # Create a simple test video
                test_clip = VideoFileClip("test.mp4") if Path("test.mp4").exists() else None
                if test_clip:
                    test_clip.close()
            
            logger.info("Video processing initialized successfully")
            
        except Exception as e:
            logger.warning(f"Video processing initialization had issues: {e}")

    async def _validate_configuration(self) -> None:
        """Validate video renderer configuration."""
        if not self.default_config:
            raise RuntimeError("Video configuration not set")
        
        if not self.supported_formats:
            raise RuntimeError("No supported video formats configured")

    @with_error_handling
    @with_retry(max_attempts=3)
    async def render_video(self, request: VideoRenderRequest) -> VideoRenderResult:
        """Render a video with the specified configuration and effects."""
        start_time = time.time()
        
        try:
            logger.info(f"Rendering video for request {request.request_id}")
            
            # Validate request
            if not request.video_path or not Path(request.video_path).exists():
                raise ValueError(f"Video file not found: {request.video_path}")
            
            if not request.output_path:
                raise ValueError("Output path is required")
            
            # Load video
            video_clip = await self._load_video(request.video_path)
            
            # Load audio if provided
            audio_clip = None
            if request.audio_path and Path(request.audio_path).exists():
                audio_clip = await self._load_audio(request.audio_path)
            
            # Synchronize audio and video
            if audio_clip:
                video_clip = await self._synchronize_audio_video(video_clip, audio_clip)
            
            # Apply background if specified
            if request.background:
                video_clip = await self._composite_background(video_clip, request.background)
            
            # Apply effects
            if request.effects:
                video_clip = await self._apply_video_effects(video_clip, request.effects)
            
            # Apply watermark if specified
            if request.watermark:
                video_clip = await self._apply_watermark(video_clip, request.watermark)
            
            # Optimize video quality
            video_clip = await self._optimize_video_quality(video_clip, request.config)
            
            # Render final video
            output_path = await self._render_final_video(video_clip, request.output_path, request.config)
            
            # Calculate metrics
            render_time = time.time() - start_time
            duration = video_clip.duration
            file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0
            quality_score = self._calculate_quality_score(request, render_time, duration)
            
            # Update statistics
            self._update_render_stats(render_time, True, duration)
            
            # Create result
            result = VideoRenderResult(
                request_id=request.request_id,
                output_path=output_path,
                duration=duration,
                file_size=file_size,
                metadata={
                    "resolution": request.config.resolution,
                    "fps": request.config.fps,
                    "codec": request.config.codec,
                    "effects_applied": len(request.effects),
                    "render_time": render_time,
                    "quality_score": quality_score
                },
                render_time=render_time,
                quality_score=quality_score
            )
            
            # Cleanup
            video_clip.close()
            if audio_clip:
                audio_clip.close()
            
            logger.info(f"Video rendered successfully in {render_time:.2f}s")
            return result
            
        except Exception as e:
            self._update_render_stats(time.time() - start_time, False, 0.0)
            logger.error(f"Video rendering failed: {e}")
            raise

    async def _load_video(self, video_path: str):
        """Load video file."""
        if not MOVIEPY_AVAILABLE:
            raise RuntimeError("MoviePy not available for video loading")
        
        try:
            video_clip = VideoFileClip(video_path)
            logger.debug(f"Loaded video: {video_path}")
            return video_clip
        except Exception as e:
            logger.error(f"Failed to load video {video_path}: {e}")
            raise

    async def _load_audio(self, audio_path: str):
        """Load audio file."""
        if not MOVIEPY_AVAILABLE:
            raise RuntimeError("MoviePy not available for audio loading")
        
        try:
            audio_clip = AudioFileClip(audio_path)
            logger.debug(f"Loaded audio: {audio_path}")
            return audio_clip
        except Exception as e:
            logger.error(f"Failed to load audio {audio_path}: {e}")
            raise

    async def _synchronize_audio_video(self, video_clip, audio_clip):
        """Synchronize audio and video."""
        try:
            # Ensure video duration matches audio duration
            if video_clip.duration != audio_clip.duration:
                # Trim to the shorter duration
                min_duration = min(video_clip.duration, audio_clip.duration)
                video_clip = video_clip.subclip(0, min_duration)
                audio_clip = audio_clip.subclip(0, min_duration)
            
            # Set audio to video
            video_clip = video_clip.set_audio(audio_clip)
            logger.debug("Audio and video synchronized")
            return video_clip
            
        except Exception as e:
            logger.warning(f"Audio-video synchronization failed: {e}")
            return video_clip

    async def _composite_background(self, video_clip, background_path: str):
        """Composite video with background."""
        try:
            if not Path(background_path).exists():
                logger.warning(f"Background file not found: {background_path}")
                return video_clip
            
            # Load background
            background_clip = ImageClip(background_path, duration=video_clip.duration)
            
            # Resize background to match video
            background_clip = background_clip.resize(video_clip.size)
            
            # Composite video over background
            composite = CompositeVideoClip([background_clip, video_clip])
            logger.debug("Background composited successfully")
            return composite
            
        except Exception as e:
            logger.warning(f"Background compositing failed: {e}")
            return video_clip

    async def _apply_video_effects(self, video_clip, effects: List[VideoEffect]):
        """Apply video effects."""
        try:
            for effect in effects:
                if effect.effect_type == "fade_in":
                    video_clip = video_clip.fx(fadein, effect.duration)
                elif effect.effect_type == "fade_out":
                    video_clip = video_clip.fx(fadeout, effect.duration)
                elif effect.effect_type == "resize":
                    width = effect.parameters.get("width", video_clip.w)
                    height = effect.parameters.get("height", video_clip.h)
                    video_clip = video_clip.resize((width, height))
                elif effect.effect_type == "rotate":
                    angle = effect.parameters.get("angle", 0)
                    video_clip = video_clip.fx(rotate, angle)
                elif effect.effect_type == "crop":
                    x1 = effect.parameters.get("x1", 0)
                    y1 = effect.parameters.get("y1", 0)
                    x2 = effect.parameters.get("x2", video_clip.w)
                    y2 = effect.parameters.get("y2", video_clip.h)
                    video_clip = video_clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)
            
            logger.debug(f"Applied {len(effects)} video effects")
            return video_clip
            
        except Exception as e:
            logger.warning(f"Video effects application failed: {e}")
            return video_clip

    async def _apply_watermark(self, video_clip, watermark_path: str):
        """Apply watermark to video."""
        try:
            if not Path(watermark_path).exists():
                logger.warning(f"Watermark file not found: {watermark_path}")
                return video_clip
            
            # Load watermark
            watermark_clip = ImageClip(watermark_path, duration=video_clip.duration)
            
            # Position watermark (bottom right corner)
            watermark_clip = watermark_clip.set_position(("right", "bottom"))
            
            # Composite watermark over video
            composite = CompositeVideoClip([video_clip, watermark_clip])
            logger.debug("Watermark applied successfully")
            return composite
            
        except Exception as e:
            logger.warning(f"Watermark application failed: {e}")
            return video_clip

    async def _optimize_video_quality(self, video_clip, config: VideoConfig):
        """Optimize video quality based on configuration."""
        try:
            # Apply quality preset
            quality_preset = self.quality_presets.get(config.quality, self.quality_presets["high"])
            
            # Resize if needed
            if config.resolution != "auto":
                width, height = map(int, config.resolution.split("x"))
                if video_clip.size != (width, height):
                    video_clip = video_clip.resize((width, height))
            
            # Set FPS
            if config.fps != video_clip.fps:
                video_clip = video_clip.set_fps(config.fps)
            
            logger.debug("Video quality optimized")
            return video_clip
            
        except Exception as e:
            logger.warning(f"Video quality optimization failed: {e}")
            return video_clip

    async def _render_final_video(self, video_clip, output_path: str, config: VideoConfig):
        """Render the final video."""
        try:
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Render with configuration
            video_clip.write_videofile(
                output_path,
                fps=config.fps,
                codec=config.codec,
                bitrate=config.bitrate,
                verbose=False,
                logger=None
            )
            
            logger.debug(f"Final video rendered to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Final video rendering failed: {e}")
            raise

    def _calculate_quality_score(self, request: VideoRenderRequest, render_time: float, duration: float) -> float:
        """Calculate quality score for rendered video."""
        base_score = 0.8
        
        # Adjust for quality setting
        quality_multipliers = {
            "low": 0.7,
            "medium": 0.85,
            "high": 1.0,
            "ultra": 1.2
        }
        base_score *= quality_multipliers.get(request.config.quality, 1.0)
        
        # Adjust for render time
        if render_time < duration * 0.5:  # Faster than real-time
            base_score *= 1.1
        elif render_time > duration * 2.0:  # Slower than real-time
            base_score *= 0.9
        
        # Adjust for effects complexity
        if request.effects:
            base_score *= (1.0 + len(request.effects) * 0.05)
        
        # Adjust for resolution
        if request.config.resolution in ["4K", "3840x2160"]:
            base_score *= 1.1
        
        return min(1.0, max(0.0, base_score))

    def _update_render_stats(self, render_time: float, success: bool, duration: float):
        """Update rendering statistics."""
        self.render_stats["total_rendered"] += 1
        
        if success:
            self.render_stats["successful_renders"] += 1
            self.render_stats["total_video_duration"] += duration
        else:
            self.render_stats["failed_renders"] += 1
        
        # Update average render time
        current_avg = self.render_stats["average_render_time"]
        total_successful = self.render_stats["successful_renders"]
        
        if total_successful > 0:
            self.render_stats["average_render_time"] = (
                (current_avg * (total_successful - 1) + render_time) / total_successful
            )

    async def health_check(self) -> HealthCheckResult:
        """Check the health of the video renderer."""
        try:
            # Check base service health
            base_health = await super().health_check()
            
            # Check dependencies
            dependencies = {
                "moviepy": MOVIEPY_AVAILABLE,
                "opencv": OPENCV_AVAILABLE,
                "pillow": PIL_AVAILABLE
            }
            
            # Check video processing
            video_health = {
                "supported_formats": self.supported_formats,
                "supported_codecs": self.supported_codecs,
                "quality_presets": list(self.quality_presets.keys())
            }
            
            # Update base health
            base_health.details.update({
                "dependencies": dependencies,
                "video_processing": video_health,
                "render_stats": self.render_stats
            })
            
            return base_health
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                error_message=str(e)
            )

    def get_supported_formats(self) -> List[str]:
        """Get supported video formats."""
        return self.supported_formats.copy()

    def get_supported_codecs(self) -> List[str]:
        """Get supported video codecs."""
        return self.supported_codecs.copy()

    def get_quality_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get available quality presets."""
        return self.quality_presets.copy()

    def get_default_effects(self) -> List[VideoEffect]:
        """Get default video effects."""
        return [
            VideoEffect("fade_in", {"duration": 1.0}, 0.0, 1.0),
            VideoEffect("fade_out", {"duration": 1.0}, 0.0, 1.0)
        ]

    async def cleanup_temp_files(self) -> None:
        """Clean up temporary video files."""
        try:
            temp_dir = Path("./temp")
            if temp_dir.exists():
                for video_file in temp_dir.glob("*.mp4"):
                    if video_file.name.startswith("temp_"):
                        video_file.unlink()
                        logger.debug(f"Cleaned up temp file: {video_file}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")
