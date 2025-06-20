"""
Video Models

Core video processing models with optimized batch operations and validation.
"""

from datetime import datetime
from typing import List, Optional

import msgspec
from agents.backend.onyx.server.features.utils import (
    OnyxBaseModel, validate_model, cache_model, log_operations, ModelStatus
)

from ..utils.batch_utils import OptimizedBatchMixin, _optimized_batch_timeit
from ..utils.validation import (
    validate_youtube_url,
    validate_language,
    validate_video_clip_times,
    validate_caption
)

# =============================================================================
# VIDEO CLIP REQUEST MODEL
# =============================================================================

class VideoClipRequest(OnyxBaseModel, msgspec.Struct, OptimizedBatchMixin, frozen=True, slots=True):
    """Optimized request model for processing YouTube videos into clips."""
    
    youtube_url: str
    language: str = "en"
    logo_path: Optional[str] = None
    max_clip_length: int = 60
    min_clip_length: int = 15
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: ModelStatus = ModelStatus.ACTIVE

    def __post_init__(self):
        """Optimized validation with caching."""
        validate_youtube_url(self.youtube_url)
        validate_language(self.language)

    def as_tuple(self) -> tuple:
        return (self.youtube_url, self.language, self.logo_path, 
                self.max_clip_length, self.min_clip_length)

    # Batch operations with timing decorators
    @_optimized_batch_timeit
    @classmethod
    def batch_encode(cls, items: List["VideoClipRequest"]) -> bytes:
        return super().batch_encode(items)

    @_optimized_batch_timeit
    @classmethod
    def batch_decode(cls, data: bytes) -> List["VideoClipRequest"]:
        return super().batch_decode(data)

    @_optimized_batch_timeit
    @classmethod
    def batch_to_numpy(cls, items: List["VideoClipRequest"]):
        return super().batch_to_numpy(items)

    @_optimized_batch_timeit
    @classmethod
    def batch_to_pandas(cls, items: List["VideoClipRequest"]):
        return super().batch_to_pandas(items)

    @_optimized_batch_timeit
    @classmethod
    def batch_to_parquet(cls, items: List["VideoClipRequest"], path: str):
        return super().batch_to_parquet(items, path)

    @_optimized_batch_timeit
    @classmethod
    def batch_from_parquet(cls, path: str) -> List["VideoClipRequest"]:
        return super().batch_from_parquet(path)

    @_optimized_batch_timeit
    @classmethod
    def batch_validate_unique(cls, items: List["VideoClipRequest"], 
                            key=lambda x: x.youtube_url):
        return super().batch_validate_unique(items, key)

    @_optimized_batch_timeit
    @classmethod
    def batch_to_dicts(cls, items: List["VideoClipRequest"]) -> List[dict]:
        return super().batch_to_dicts(items)

    @_optimized_batch_timeit
    @classmethod
    def batch_from_dicts(cls, dicts: List[dict]) -> List["VideoClipRequest"]:
        return super().batch_from_dicts(dicts)

    @_optimized_batch_timeit
    @classmethod
    def batch_deduplicate(cls, items: List["VideoClipRequest"], 
                         key="youtube_url") -> List["VideoClipRequest"]:
        return super().batch_deduplicate(items, key)

    @validate_model(validate_types=True, validate_custom=True)
    @cache_model(key_field="youtube_url")
    @log_operations()
    def save(self, user_context=None):
        super().save(user_context=user_context)

# =============================================================================
# VIDEO CLIP MODEL
# =============================================================================

class VideoClip(OnyxBaseModel, msgspec.Struct, OptimizedBatchMixin, frozen=True, slots=True):
    """Optimized model for a single video clip with caption and emojis."""
    
    start: float
    end: float
    caption: str
    emojis: List[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: ModelStatus = ModelStatus.ACTIVE

    def __post_init__(self):
        """Optimized validation."""
        validate_video_clip_times(self.start, self.end)
        validate_caption(self.caption)

    def as_tuple(self) -> tuple:
        return (self.start, self.end, self.caption, self.emojis)

    # Batch operations with timing decorators
    @_optimized_batch_timeit
    @classmethod
    def batch_encode(cls, items: List["VideoClip"]) -> bytes:
        return super().batch_encode(items)

    @_optimized_batch_timeit
    @classmethod
    def batch_decode(cls, data: bytes) -> List["VideoClip"]:
        return super().batch_decode(data)

    @_optimized_batch_timeit
    @classmethod
    def batch_to_numpy(cls, items: List["VideoClip"]):
        return super().batch_to_numpy(items)

    @_optimized_batch_timeit
    @classmethod
    def batch_to_pandas(cls, items: List["VideoClip"]):
        return super().batch_to_pandas(items)

    @_optimized_batch_timeit
    @classmethod
    def batch_to_parquet(cls, items: List["VideoClip"], path: str):
        return super().batch_to_parquet(items, path)

    @_optimized_batch_timeit
    @classmethod
    def batch_from_parquet(cls, path: str) -> List["VideoClip"]:
        return super().batch_from_parquet(path)

    @_optimized_batch_timeit
    @classmethod
    def batch_validate_unique(cls, items: List["VideoClip"], 
                            key=lambda x: x.caption):
        return super().batch_validate_unique(items, key)

    @_optimized_batch_timeit
    @classmethod
    def batch_to_dicts(cls, items: List["VideoClip"]) -> List[dict]:
        return super().batch_to_dicts(items)

    @_optimized_batch_timeit
    @classmethod
    def batch_from_dicts(cls, dicts: List[dict]) -> List["VideoClip"]:
        return super().batch_from_dicts(dicts)

    @_optimized_batch_timeit
    @classmethod
    def batch_deduplicate(cls, items: List["VideoClip"], 
                         key="caption") -> List["VideoClip"]:
        return super().batch_deduplicate(items, key)

    @validate_model(validate_types=True, validate_custom=True)
    @cache_model(key_field="caption")
    @log_operations()
    def save(self, user_context=None):
        super().save(user_context=user_context)

# =============================================================================
# VIDEO CLIP RESPONSE MODEL
# =============================================================================

class VideoClipResponse(OnyxBaseModel, msgspec.Struct, OptimizedBatchMixin, frozen=True, slots=True):
    """Optimized response model with the list of generated video clips."""
    
    youtube_url: str
    clips: List[VideoClip]
    logo_path: Optional[str]
    language: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: ModelStatus = ModelStatus.ACTIVE

    def as_tuple(self) -> tuple:
        return (self.youtube_url, self.clips, self.logo_path, self.language)

    # Batch operations with timing decorators
    @_optimized_batch_timeit
    @classmethod
    def batch_encode(cls, items: List["VideoClipResponse"]) -> bytes:
        return super().batch_encode(items)

    @_optimized_batch_timeit
    @classmethod
    def batch_decode(cls, data: bytes) -> List["VideoClipResponse"]:
        return super().batch_decode(data)

    @_optimized_batch_timeit
    @classmethod
    def batch_to_numpy(cls, items: List["VideoClipResponse"]):
        return super().batch_to_numpy(items)

    @_optimized_batch_timeit
    @classmethod
    def batch_to_pandas(cls, items: List["VideoClipResponse"]):
        return super().batch_to_pandas(items)

    @_optimized_batch_timeit
    @classmethod
    def batch_to_parquet(cls, items: List["VideoClipResponse"], path: str):
        return super().batch_to_parquet(items, path)

    @_optimized_batch_timeit
    @classmethod
    def batch_from_parquet(cls, path: str) -> List["VideoClipResponse"]:
        return super().batch_from_parquet(path)

    @_optimized_batch_timeit
    @classmethod
    def batch_validate_unique(cls, items: List["VideoClipResponse"], 
                            key=lambda x: x.youtube_url):
        return super().batch_validate_unique(items, key)

    @_optimized_batch_timeit
    @classmethod
    def batch_to_dicts(cls, items: List["VideoClipResponse"]) -> List[dict]:
        return super().batch_to_dicts(items)

    @_optimized_batch_timeit
    @classmethod
    def batch_from_dicts(cls, dicts: List[dict]) -> List["VideoClipResponse"]:
        return super().batch_from_dicts(dicts)

    @_optimized_batch_timeit
    @classmethod
    def batch_deduplicate(cls, items: List["VideoClipResponse"], 
                         key="youtube_url") -> List["VideoClipResponse"]:
        return super().batch_deduplicate(items, key)

    @validate_model(validate_types=True, validate_custom=True)
    @cache_model(key_field="youtube_url")
    @log_operations()
    def save(self, user_context=None):
        super().save(user_context=user_context) 