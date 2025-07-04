"""
Video Models

Core video processing models with optimized serialization using high-performance libraries.
"""

from __future__ import annotations
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
import msgspec
import pydantic
import orjson
from enum import Enum
import structlog

logger = structlog.get_logger()

# =============================================================================
# SERIALIZATION CONFIGURATION
# =============================================================================

# Configure msgspec for optimal performance
MSGPEC_CONFIG = msgspec.Config(
    strict=True,
    struct=True,
    frozen=False,
    array_like=True,
    datetime_mode="iso8601",
    uuid_mode="hex",
    enum_mode="name"
)

# Configure orjson for optimal JSON performance
ORJSON_OPTIONS = orjson.OPT_NAIVE_UTC | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_INDENT_2

# =============================================================================
# BASE SERIALIZATION CLASSES
# =============================================================================

class MsgspecStruct(msgspec.Struct):
    """Base class for msgspec serialization with optimized configuration."""
    
    def __init_subclass__(cls, **kwargs):
        """Configure msgspec for optimal performance."""
        super().__init_subclass__(**kwargs)
        cls.__config__ = MSGPEC_CONFIG

class PydanticModel(pydantic.BaseModel):
    """Base class for pydantic models with optimized configuration."""
    
    class Config:
        """Optimized pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        extra = "forbid"
        validate_default = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Enum: lambda v: v.value
        }

# =============================================================================
# ENUMS
# =============================================================================

class VideoStatus(Enum):
    """Video processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VideoQuality(Enum):
    """Video quality levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

class VideoFormat(Enum):
    """Video formats."""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    FLV = "flv"

class Language(Enum):
    """Supported languages."""
    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"
    IT = "it"
    PT = "pt"
    RU = "ru"
    ZH = "zh"
    JA = "ja"
    KO = "ko"

# =============================================================================
# CORE MODELS
# =============================================================================

@dataclass(slots=True)
class VideoClipRequest(MsgspecStruct):
    """Request for video clip processing."""
    youtube_url: str
    language: str = "en"
    max_clip_length: int = 60
    min_clip_length: int = 15
    quality: VideoQuality = VideoQuality.HIGH
    format: VideoFormat = VideoFormat.MP4
    custom_params: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    priority: str = "normal"  # low, normal, high, urgent
    created_at: datetime = field(default_factory=datetime.now)

@dataclass(slots=True)
class VideoClip(MsgspecStruct):
    """Video clip data."""
    clip_id: str
    youtube_url: str
    title: str
    description: str
    duration: float
    language: str
    quality: VideoQuality
    format: VideoFormat
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    resolution: Optional[str] = None
    fps: Optional[float] = None
    bitrate: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass(slots=True)
class VideoClipResponse(MsgspecStruct):
    """Response for video clip processing."""
    success: bool
    clip_id: Optional[str] = None
    duration: Optional[float] = None
    language: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    resolution: Optional[str] = None
    processing_time: float = 0.0
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class VideoBatchRequest(MsgspecStruct):
    """Batch request for video processing."""
    requests: List[VideoClipRequest] = field(default_factory=list)
    batch_id: Optional[str] = None
    priority: str = "normal"
    max_workers: int = 8
    timeout: float = 300.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.batch_id:
            self.batch_id = f"batch_{int(self.created_at.timestamp())}"

@dataclass(slots=True)
class VideoBatchResponse(MsgspecStruct):
    """Batch response for video processing."""
    success: bool
    batch_id: str
    results: List[VideoClipResponse] = field(default_factory=list)
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

# =============================================================================
# ADVANCED MODELS
# =============================================================================

@dataclass(slots=True)
class VideoMetadata(MsgspecStruct):
    """Detailed video metadata."""
    clip_id: str
    title: str
    description: str
    channel_name: str
    channel_id: str
    view_count: int
    like_count: int
    dislike_count: int
    comment_count: int
    publish_date: datetime
    duration: float
    language: str
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    thumbnail_url: Optional[str] = None
    resolution: Optional[str] = None
    fps: Optional[float] = None
    bitrate: Optional[int] = None
    codec: Optional[str] = None
    audio_codec: Optional[str] = None
    extracted_at: datetime = field(default_factory=datetime.now)

@dataclass(slots=True)
class VideoProcessingConfig(MsgspecStruct):
    """Configuration for video processing."""
    # Quality settings
    target_quality: VideoQuality = VideoQuality.HIGH
    target_format: VideoFormat = VideoFormat.MP4
    target_resolution: str = "1920x1080"
    target_fps: float = 30.0
    target_bitrate: Optional[int] = None
    
    # Processing settings
    enable_audio: bool = True
    enable_subtitles: bool = True
    enable_thumbnails: bool = True
    enable_metadata: bool = True
    
    # Performance settings
    max_workers: int = 8
    chunk_size: int = 1000
    timeout: float = 300.0
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # Advanced settings
    use_gpu: bool = False
    use_hardware_acceleration: bool = True
    optimize_for_web: bool = True
    preserve_original: bool = False

@dataclass(slots=True)
class VideoProcessingResult(MsgspecStruct):
    """Detailed video processing result."""
    clip_id: str
    status: VideoStatus
    original_url: str
    processed_file_path: str
    file_size: int
    duration: float
    quality: VideoQuality
    format: VideoFormat
    resolution: str
    fps: float
    bitrate: int
    processing_time: float
    metadata: VideoMetadata
    thumbnails: List[str] = field(default_factory=list)
    subtitles: List[str] = field(default_factory=list)
    audio_tracks: List[str] = field(default_factory=list)
    error_log: List[str] = field(default_factory=list)
    warning_log: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

# =============================================================================
# BATCH PROCESSING MODELS
# =============================================================================

@dataclass(slots=True)
class VideoBatch(MsgspecStruct):
    """Batch of videos for processing."""
    videos: List[VideoClipRequest] = field(default_factory=list)
    batch_size: int = 0
    priority: str = "normal"
    config: VideoProcessingConfig = field(default_factory=VideoProcessingConfig)
    
    def __post_init__(self):
        self.batch_size = len(self.videos)

@dataclass(slots=True)
class VideoBatchResult(MsgspecStruct):
    """Result of batch video processing."""
    batch_id: str
    success: bool
    total_videos: int
    processed_videos: int
    failed_videos: int
    results: List[VideoProcessingResult] = field(default_factory=list)
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

# =============================================================================
# VALIDATION MODELS
# =============================================================================

@dataclass(slots=True)
class VideoValidationResult(MsgspecStruct):
    """Validation result for video processing."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    duration_score: float = 0.0
    format_score: float = 0.0
    overall_score: float = 0.0

@dataclass(slots=True)
class BatchValidationResult(MsgspecStruct):
    """Validation result for batch processing."""
    is_valid: bool
    valid_videos: int
    invalid_videos: int
    validation_results: List[VideoValidationResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    overall_score: float = 0.0

# =============================================================================
# HIGH-PERFORMANCE SERIALIZATION UTILITIES
# =============================================================================

class VideoSerializationManager:
    """High-performance serialization manager for video models."""
    
    def __init__(self):
        self.msgpack_encoder = msgspec.Encoder()
        self.msgpack_decoder = msgspec.Decoder()
        self.json_encoder = msgspec.Encoder(enc_hook=self._json_encoder_hook)
        self.json_decoder = msgspec.Decoder(dec_hook=self._json_decoder_hook)
    
    def _json_encoder_hook(self, obj):
        """Custom JSON encoder hook for special types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _json_decoder_hook(self, obj_type, obj):
        """Custom JSON decoder hook for special types."""
        if obj_type == datetime:
            return datetime.fromisoformat(obj)
        if obj_type == VideoStatus:
            return VideoStatus(obj)
        if obj_type == VideoQuality:
            return VideoQuality(obj)
        if obj_type == VideoFormat:
            return VideoFormat(obj)
        if obj_type == Language:
            return Language(obj)
        return obj
    
    def to_msgpack(self, obj: Any) -> bytes:
        """Serialize to MessagePack format."""
        try:
            return self.msgpack_encoder.encode(obj)
        except Exception as e:
            logger.error("Video MsgPack serialization failed", error=str(e))
            raise
    
    def from_msgpack(self, data: bytes, obj_type: type) -> Any:
        """Deserialize from MessagePack format."""
        try:
            return msgspec.convert(data, obj_type)
        except Exception as e:
            logger.error("Video MsgPack deserialization failed", error=str(e))
            raise
    
    def to_json(self, obj: Any) -> str:
        """Serialize to JSON format using orjson."""
        try:
            return orjson.dumps(obj, option=ORJSON_OPTIONS).decode('utf-8')
        except Exception as e:
            logger.error("Video JSON serialization failed", error=str(e))
            raise
    
    def from_json(self, data: str, obj_type: type) -> Any:
        """Deserialize from JSON format."""
        try:
            json_data = orjson.loads(data)
            return msgspec.convert(json_data, obj_type)
        except Exception as e:
            logger.error("Video JSON deserialization failed", error=str(e))
            raise
    
    def to_dict(self, obj: Any) -> Dict:
        """Convert to dictionary using msgspec."""
        try:
            return msgspec.to_builtins(obj)
        except Exception as e:
            logger.error("Video dict conversion failed", error=str(e))
            raise
    
    def from_dict(self, data: Dict, obj_type: type) -> Any:
        """Convert from dictionary using msgspec."""
        try:
            return msgspec.convert(data, obj_type)
        except Exception as e:
            logger.error("Video dict conversion failed", error=str(e))
            raise

# =============================================================================
# BATCH SERIALIZATION UTILITIES
# =============================================================================

class VideoBatchSerializationManager:
    """Optimized batch serialization for video models."""
    
    def __init__(self):
        self.serializer = VideoSerializationManager()
        self.msgpack_encoder = msgspec.Encoder()
        self.msgpack_decoder = msgspec.Decoder()
    
    def batch_to_msgpack(self, objects: List[Any]) -> bytes:
        """Serialize batch to MessagePack."""
        try:
            return self.msgpack_encoder.encode(objects)
        except Exception as e:
            logger.error("Video batch MsgPack serialization failed", error=str(e))
            raise
    
    def batch_from_msgpack(self, data: bytes, obj_type: type) -> List[Any]:
        """Deserialize batch from MessagePack."""
        try:
            return msgspec.convert(data, List[obj_type])
        except Exception as e:
            logger.error("Video batch MsgPack deserialization failed", error=str(e))
            raise
    
    def batch_to_json(self, objects: List[Any]) -> str:
        """Serialize batch to JSON."""
        try:
            return orjson.dumps(objects, option=ORJSON_OPTIONS).decode('utf-8')
        except Exception as e:
            logger.error("Video batch JSON serialization failed", error=str(e))
            raise
    
    def batch_from_json(self, data: str, obj_type: type) -> List[Any]:
        """Deserialize batch from JSON."""
        try:
            json_data = orjson.loads(data)
            return [msgspec.convert(item, obj_type) for item in json_data]
        except Exception as e:
            logger.error("Video batch JSON deserialization failed", error=str(e))
            raise

# =============================================================================
# PERFORMANCE BENCHMARKING
# =============================================================================

class VideoSerializationBenchmark:
    """Benchmark serialization performance for video models."""
    
    def __init__(self):
        self.serializer = VideoSerializationManager()
        self.batch_serializer = VideoBatchSerializationManager()
    
    def benchmark_serialization(self, obj: Any, iterations: int = 1000) -> Dict[str, float]:
        """Benchmark different serialization methods."""
        import time
        
        results = {}
        
        # MsgPack benchmark
        start_time = time.perf_counter()
        for _ in range(iterations):
            data = self.serializer.to_msgpack(obj)
            _ = self.serializer.from_msgpack(data, type(obj))
        msgpack_time = time.perf_counter() - start_time
        results['msgpack'] = msgpack_time
        
        # JSON benchmark
        start_time = time.perf_counter()
        for _ in range(iterations):
            data = self.serializer.to_json(obj)
            _ = self.serializer.from_json(data, type(obj))
        json_time = time.perf_counter() - start_time
        results['json'] = json_time
        
        # Dict benchmark
        start_time = time.perf_counter()
        for _ in range(iterations):
            data = self.serializer.to_dict(obj)
            _ = self.serializer.from_dict(data, type(obj))
        dict_time = time.perf_counter() - start_time
        results['dict'] = dict_time
        
        return results
    
    def benchmark_batch_serialization(self, objects: List[Any], iterations: int = 100) -> Dict[str, float]:
        """Benchmark batch serialization performance."""
        import time
        
        results = {}
        
        # MsgPack batch benchmark
        start_time = time.perf_counter()
        for _ in range(iterations):
            data = self.batch_serializer.batch_to_msgpack(objects)
            _ = self.batch_serializer.batch_from_msgpack(data, type(objects[0]))
        msgpack_time = time.perf_counter() - start_time
        results['msgpack_batch'] = msgpack_time
        
        # JSON batch benchmark
        start_time = time.perf_counter()
        for _ in range(iterations):
            data = self.batch_serializer.batch_to_json(objects)
            _ = self.batch_serializer.batch_from_json(data, type(objects[0]))
        json_time = time.perf_counter() - start_time
        results['json_batch'] = json_time
        
        return results

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_video_request(
    youtube_url: str,
    language: str = "en",
    max_clip_length: int = 60,
    quality: VideoQuality = VideoQuality.HIGH
) -> VideoClipRequest:
    """Create a video clip request."""
    return VideoClipRequest(
        youtube_url=youtube_url,
        language=language,
        max_clip_length=max_clip_length,
        quality=quality
    )

def create_video_batch(
    requests: List[VideoClipRequest],
    priority: str = "normal",
    max_workers: int = 8
) -> VideoBatchRequest:
    """Create a video batch request."""
    return VideoBatchRequest(
        requests=requests,
        priority=priority,
        max_workers=max_workers
    )

def create_processing_config(
    quality: VideoQuality = VideoQuality.HIGH,
    format: VideoFormat = VideoFormat.MP4,
    max_workers: int = 8
) -> VideoProcessingConfig:
    """Create a video processing configuration."""
    return VideoProcessingConfig(
        target_quality=quality,
        target_format=format,
        max_workers=max_workers
    )

# =============================================================================
# GLOBAL SERIALIZATION INSTANCES
# =============================================================================

# Global serialization managers for easy access
video_serializer = VideoSerializationManager()
video_batch_serializer = VideoBatchSerializationManager()
video_benchmark = VideoSerializationBenchmark()

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'VideoStatus',
    'VideoQuality',
    'VideoFormat',
    'Language',
    
    # Core models
    'VideoClipRequest',
    'VideoClip',
    'VideoClipResponse',
    'VideoBatchRequest',
    'VideoBatchResponse',
    
    # Advanced models
    'VideoMetadata',
    'VideoProcessingConfig',
    'VideoProcessingResult',
    
    # Batch models
    'VideoBatch',
    'VideoBatchResult',
    
    # Validation models
    'VideoValidationResult',
    'BatchValidationResult',
    
    # Serialization
    'VideoSerializationManager',
    'VideoBatchSerializationManager',
    'VideoSerializationBenchmark',
    'video_serializer',
    'video_batch_serializer',
    'video_benchmark',
    
    # Utility functions
    'create_video_request',
    'create_video_batch',
    'create_processing_config',
] 