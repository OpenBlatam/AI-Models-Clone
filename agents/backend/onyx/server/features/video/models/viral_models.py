"""
Viral Video Models

Advanced models for viral video content generation with enhanced video editing capabilities.
"""

from __future__ import annotations
from typing import List, Dict, Optional, Union, Literal
from dataclasses import dataclass, field
from datetime import datetime
import msgspec
from enum import Enum

# =============================================================================
# ENUMS
# =============================================================================

class TransitionType(Enum):
    """Types of video transitions."""
    FADE = "fade"
    SLIDE = "slide"
    ZOOM = "zoom"
    ROTATE = "rotate"
    FLIP = "flip"
    WIPE = "wipe"
    DISSOLVE = "dissolve"
    MORPH = "morph"
    GLITCH = "glitch"
    PIXELATE = "pixelate"

class ScreenDivisionType(Enum):
    """Types of screen divisions."""
    SPLIT_HORIZONTAL = "split_horizontal"
    SPLIT_VERTICAL = "split_vertical"
    GRID_2X2 = "grid_2x2"
    GRID_3X3 = "grid_3x3"
    PIP = "picture_in_picture"
    SIDE_BY_SIDE = "side_by_side"
    STACKED = "stacked"
    MOSAIC = "mosaic"
    CUSTOM = "custom"

class CaptionStyle(Enum):
    """Caption styling options."""
    BOLD = "bold"
    ITALIC = "italic"
    UNDERLINE = "underline"
    SHADOW = "shadow"
    OUTLINE = "outline"
    GRADIENT = "gradient"
    ANIMATED = "animated"
    GLOW = "glow"
    NEON = "neon"
    HANDWRITTEN = "handwritten"

class VideoEffect(Enum):
    """Video effects for viral content."""
    SLOW_MOTION = "slow_motion"
    FAST_FORWARD = "fast_forward"
    REVERSE = "reverse"
    LOOP = "loop"
    MIRROR = "mirror"
    INVERT = "invert"
    SEPIA = "sepia"
    BLACK_AND_WHITE = "black_and_white"
    VINTAGE = "vintage"
    NEON = "neon"
    GLITCH = "glitch"
    PIXELATE = "pixelate"
    BLUR = "blur"
    SHARPEN = "sharpen"
    SATURATE = "saturate"
    DESATURATE = "desaturate"

# =============================================================================
# CORE MODELS
# =============================================================================

@dataclass(slots=True)
class CaptionSegment(msgspec.Struct):
    """Individual caption segment with timing and styling."""
    text: str
    start_time: float
    end_time: float
    font_size: int = 24
    font_color: str = "#FFFFFF"
    background_color: Optional[str] = None
    position: str = "bottom"  # top, bottom, center, custom
    styles: List[CaptionStyle] = field(default_factory=list)
    animation: Optional[str] = None
    opacity: float = 1.0
    scale: float = 1.0
    rotation: float = 0.0
    x_offset: float = 0.0
    y_offset: float = 0.0

@dataclass(slots=True)
class ScreenDivision(msgspec.Struct):
    """Screen division configuration."""
    division_type: ScreenDivisionType
    sections: List[Dict[str, Union[str, float, int]]] = field(default_factory=list)
    border_width: int = 2
    border_color: str = "#000000"
    background_color: str = "#000000"
    aspect_ratio: str = "16:9"
    custom_layout: Optional[Dict] = None

@dataclass(slots=True)
class Transition(msgspec.Struct):
    """Video transition configuration."""
    transition_type: TransitionType
    duration: float = 1.0
    easing: str = "ease_in_out"
    direction: str = "left_to_right"
    intensity: float = 1.0
    custom_params: Optional[Dict] = None

@dataclass(slots=True)
class VideoEffect(msgspec.Struct):
    """Video effect configuration."""
    effect_type: VideoEffect
    intensity: float = 1.0
    duration: Optional[float] = None
    start_time: float = 0.0
    end_time: Optional[float] = None
    custom_params: Optional[Dict] = None

@dataclass(slots=True)
class ViralCaptionConfig(msgspec.Struct):
    """Configuration for viral caption generation."""
    # Caption settings
    max_caption_length: int = 100
    caption_duration: float = 3.0
    font_family: str = "Arial"
    base_font_size: int = 24
    caption_position: str = "bottom"
    
    # Styling
    use_animations: bool = True
    use_effects: bool = True
    use_transitions: bool = True
    use_screen_division: bool = False
    
    # Viral optimization
    viral_keywords: List[str] = field(default_factory=list)
    trending_topics: List[str] = field(default_factory=list)
    audience_interests: List[str] = field(default_factory=list)
    
    # Language and tone
    language: str = "en"
    tone: str = "casual"  # casual, formal, humorous, dramatic
    emoji_usage: bool = True
    
    # Advanced features
    auto_sync: bool = True
    background_music: Optional[str] = None
    sound_effects: List[str] = field(default_factory=list)

@dataclass(slots=True)
class ViralVideoVariant(msgspec.Struct):
    """Enhanced viral video variant with advanced editing."""
    variant_id: str
    title: str
    description: str
    viral_score: float
    engagement_prediction: float
    
    # Video editing components
    captions: List[CaptionSegment] = field(default_factory=list)
    screen_division: Optional[ScreenDivision] = None
    transitions: List[Transition] = field(default_factory=list)
    effects: List[VideoEffect] = field(default_factory=list)
    
    # Timing and synchronization
    total_duration: float
    caption_timing: Dict[str, float] = field(default_factory=dict)
    
    # Performance metrics
    estimated_views: int
    estimated_likes: int
    estimated_shares: int
    estimated_comments: int
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    target_audience: List[str] = field(default_factory=list)
    
    # Generation metadata
    created_at: datetime = field(default_factory=datetime.now)
    generation_time: float = 0.0
    model_version: str = "v2.0"

@dataclass(slots=True)
class ViralVideoBatchResponse(msgspec.Struct):
    """Enhanced batch response for viral video processing."""
    success: bool
    original_clip_id: str
    variants: List[ViralVideoVariant] = field(default_factory=list)
    
    # Processing metadata
    processing_time: float = 0.0
    total_variants_generated: int = 0
    successful_variants: int = 0
    
    # Quality metrics
    average_viral_score: float = 0.0
    best_viral_score: float = 0.0
    caption_quality_score: float = 0.0
    editing_quality_score: float = 0.0
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Batch processing info
    batch_id: Optional[str] = None
    experiment_id: Optional[str] = None

# =============================================================================
# ADVANCED EDITING MODELS
# =============================================================================

@dataclass(slots=True)
class VideoTimeline(msgspec.Struct):
    """Video timeline with precise editing control."""
    segments: List[Dict[str, Union[str, float, Dict]]] = field(default_factory=list)
    total_duration: float = 0.0
    fps: int = 30
    resolution: str = "1920x1080"
    
    def add_segment(self, segment: Dict):
        """Add a timeline segment."""
        self.segments.append(segment)
        self.total_duration = sum(s.get('duration', 0) for s in self.segments)

@dataclass(slots=True)
class AdvancedCaption(msgspec.Struct):
    """Advanced caption with rich formatting and effects."""
    text: str
    timing: Dict[str, float]
    styling: Dict[str, Union[str, int, float, List]] = field(default_factory=dict)
    animations: List[Dict[str, Union[str, float]]] = field(default_factory=list)
    effects: List[Dict[str, Union[str, float]]] = field(default_factory=list)
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0.5, "y": 0.9})
    size: Dict[str, float] = field(default_factory=lambda: {"width": 0.8, "height": 0.1})

@dataclass(slots=True)
class ScreenLayout(msgspec.Struct):
    """Advanced screen layout configuration."""
    layout_type: ScreenDivisionType
    sections: List[Dict[str, Union[str, float, Dict]]] = field(default_factory=list)
    background: Dict[str, Union[str, float]] = field(default_factory=dict)
    borders: Dict[str, Union[str, int]] = field(default_factory=dict)
    animations: List[Dict[str, Union[str, float]]] = field(default_factory=list)

@dataclass(slots=True)
class TransitionEffect(msgspec.Struct):
    """Advanced transition effect configuration."""
    effect_type: TransitionType
    parameters: Dict[str, Union[str, float, int]] = field(default_factory=dict)
    timing: Dict[str, float] = field(default_factory=dict)
    easing: str = "ease_in_out"
    custom_shader: Optional[str] = None

# =============================================================================
# BATCH PROCESSING MODELS
# =============================================================================

@dataclass(slots=True)
class ViralCaptionBatch(msgspec.Struct):
    """Batch of viral captions for processing."""
    captions: List[ViralCaptionConfig] = field(default_factory=list)
    batch_size: int = 0
    priority: str = "normal"  # low, normal, high, urgent
    
    def __post_init__(self):
        self.batch_size = len(self.captions)

@dataclass(slots=True)
class ViralCaptionBatchResponse(msgspec.Struct):
    """Response for batch caption processing."""
    success: bool
    processed_count: int
    successful_count: int
    failed_count: int
    results: List[ViralVideoVariant] = field(default_factory=list)
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)

# =============================================================================
# VALIDATION MODELS
# =============================================================================

@dataclass(slots=True)
class CaptionValidationResult(msgspec.Struct):
    """Validation result for captions."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    quality_score: float = 0.0

@dataclass(slots=True)
class VideoEditingValidationResult(msgspec.Struct):
    """Validation result for video editing."""
    is_valid: bool
    caption_validation: CaptionValidationResult
    transition_validation: List[str] = field(default_factory=list)
    effect_validation: List[str] = field(default_factory=list)
    layout_validation: List[str] = field(default_factory=list)
    overall_score: float = 0.0

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_default_caption_config() -> ViralCaptionConfig:
    """Create default caption configuration."""
    return ViralCaptionConfig(
        max_caption_length=100,
        caption_duration=3.0,
        font_family="Arial",
        base_font_size=24,
        caption_position="bottom",
        use_animations=True,
        use_effects=True,
        use_transitions=True,
        use_screen_division=False,
        viral_keywords=["viral", "trending", "must_see"],
        trending_topics=["tech", "entertainment", "news"],
        audience_interests=["young_adults", "social_media"],
        language="en",
        tone="casual",
        emoji_usage=True,
        auto_sync=True
    )

def create_split_screen_layout(division_type: ScreenDivisionType) -> ScreenDivision:
    """Create a split screen layout."""
    if division_type == ScreenDivisionType.SPLIT_HORIZONTAL:
        sections = [
            {"position": "top", "height": 0.5, "content": "main_video"},
            {"position": "bottom", "height": 0.5, "content": "captions"}
        ]
    elif division_type == ScreenDivisionType.SPLIT_VERTICAL:
        sections = [
            {"position": "left", "width": 0.7, "content": "main_video"},
            {"position": "right", "width": 0.3, "content": "captions"}
        ]
    elif division_type == ScreenDivisionType.GRID_2X2:
        sections = [
            {"position": "top_left", "width": 0.5, "height": 0.5, "content": "video_1"},
            {"position": "top_right", "width": 0.5, "height": 0.5, "content": "video_2"},
            {"position": "bottom_left", "width": 0.5, "height": 0.5, "content": "video_3"},
            {"position": "bottom_right", "width": 0.5, "height": 0.5, "content": "video_4"}
        ]
    else:
        sections = []
    
    return ScreenDivision(
        division_type=division_type,
        sections=sections,
        border_width=2,
        border_color="#000000",
        background_color="#000000"
    )

def create_viral_transition(transition_type: TransitionType) -> Transition:
    """Create a viral transition effect."""
    return Transition(
        transition_type=transition_type,
        duration=1.0,
        easing="ease_in_out",
        direction="left_to_right",
        intensity=1.0
    )

# =============================================================================
# SERIALIZATION
# =============================================================================

def to_dict(obj) -> Dict:
    """Convert model to dictionary."""
    return msgspec.to_builtins(obj)

def from_dict(data: Dict, cls) -> object:
    """Convert dictionary to model."""
    return msgspec.convert(data, cls)

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'TransitionType',
    'ScreenDivisionType', 
    'CaptionStyle',
    'VideoEffect',
    
    # Core models
    'CaptionSegment',
    'ScreenDivision',
    'Transition',
    'ViralCaptionConfig',
    'ViralVideoVariant',
    'ViralVideoBatchResponse',
    
    # Advanced models
    'VideoTimeline',
    'AdvancedCaption',
    'ScreenLayout',
    'TransitionEffect',
    
    # Batch models
    'ViralCaptionBatch',
    'ViralCaptionBatchResponse',
    
    # Validation models
    'CaptionValidationResult',
    'VideoEditingValidationResult',
    
    # Utility functions
    'create_default_caption_config',
    'create_split_screen_layout',
    'create_viral_transition',
    'to_dict',
    'from_dict'
] 