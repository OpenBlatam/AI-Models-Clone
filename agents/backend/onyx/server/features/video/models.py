import msgspec
import numpy as np
import orjson
try:
    import pandas as pd
except ImportError:
    pd = None
try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None
from agents.backend.onyx.server.features.utils import (
    OnyxBaseModel, validate_model, cache_model, log_operations, ModelStatus
)
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog
from prometheus_client import Counter
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser
from langchain.pydantic_v1 import BaseModel as LCBaseModel
from langchain.chains import SequentialChain
from langchain.memory import ConversationBufferMemory
from .viral_pipeline import generate_viral_variants

logger = structlog.get_logger()

class VideoClipRequest(OnyxBaseModel, msgspec.Struct, frozen=True, slots=True):
    """Request model for processing a YouTube video into clips with captions, logo, and emojis."""
    youtube_url: str
    language: str = "en"
    logo_path: Optional[str] = None
    max_clip_length: int = 60
    min_clip_length: int = 15
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: ModelStatus = ModelStatus.ACTIVE

    def as_tuple(self) -> tuple:
        return (self.youtube_url, self.language, self.logo_path, self.max_clip_length, self.min_clip_length)

    @staticmethod
    def batch_encode(items: List["VideoClipRequest"]) -> bytes:
        """Ultra-fast batch serialization using msgspec."""
        return msgspec.json.encode(items)

    @staticmethod
    def batch_decode(data: bytes) -> List["VideoClipRequest"]:
        """Ultra-fast batch deserialization using msgspec."""
        return msgspec.json.decode(data, type=List[VideoClipRequest])

    @staticmethod
    def batch_to_numpy(items: List["VideoClipRequest"]):
        return np.array([item.as_tuple() for item in items], dtype=object)

    @staticmethod
    def batch_to_pandas(items: List["VideoClipRequest"]):
        if pd is None:
            raise ImportError("pandas is not installed")
        return pd.DataFrame([item.__dict__ for item in items])

    @staticmethod
    def batch_to_parquet(items: List["VideoClipRequest"], path: str):
        if pd is None:
            raise ImportError("pandas is not installed")
        VideoClipRequest.batch_to_pandas(items).to_parquet(path)

    @staticmethod
    def batch_from_parquet(path: str) -> List["VideoClipRequest"]:
        if pd is None:
            raise ImportError("pandas is not installed")
        df = pd.read_parquet(path)
        return [VideoClipRequest(**d) for d in df.to_dict(orient="records")]

    @staticmethod
    def batch_validate_unique(items: List["VideoClipRequest"], key=lambda x: x.youtube_url):
        seen = set()
        for item in items:
            k = key(item)
            if k in seen:
                if sentry_sdk:
                    sentry_sdk.capture_message(f"Duplicate key found: {k}")
                raise ValueError(f"Duplicate key found: {k}")
            seen.add(k)

    # Métodos batch/ML/LLM y save igual que antes...
    @classmethod
    def batch_to_dicts(cls, objs: List["VideoClipRequest"]) -> List[dict]:
        Counter('videocliprequest_batch_to_dicts_total', 'Total batch_to_dicts calls').inc()
        logger.info("batch_to_dicts", count=len(objs))
        return [orjson.loads(orjson.dumps(obj.__dict__)) for obj in objs]

    @classmethod
    def batch_from_dicts(cls, dicts: List[dict]) -> List["VideoClipRequest"]:
        Counter('videocliprequest_batch_from_dicts_total', 'Total batch_from_dicts calls').inc()
        logger.info("batch_from_dicts", count=len(dicts))
        return [cls(**d) for d in dicts]

    @classmethod
    def batch_deduplicate(cls, objs: List["VideoClipRequest"], key="youtube_url") -> List["VideoClipRequest"]:
        seen = set()
        result = []
        for obj in objs:
            k = getattr(obj, key, None)
            if k not in seen:
                seen.add(k)
                result.append(obj)
        logger.info("batch_deduplicate", unique=len(result))
        return result

    @classmethod
    def to_training_example(cls, obj: "VideoClipRequest") -> dict:
        return orjson.loads(orjson.dumps(obj.__dict__))

    @classmethod
    def from_training_example(cls, data: dict) -> "VideoClipRequest":
        return cls(**data)

    @validate_model(validate_types=True, validate_custom=True)
    @cache_model(key_field="youtube_url")
    @log_operations()
    def save(self, user_context=None):
        super().save(user_context=user_context)

class VideoClip(OnyxBaseModel, msgspec.Struct, frozen=True, slots=True):
    """Model for a single video clip with caption and emojis."""
    start: float
    end: float
    caption: str
    emojis: List[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: ModelStatus = ModelStatus.ACTIVE

    def as_tuple(self) -> tuple:
        return (self.start, self.end, self.caption, self.emojis)

    @staticmethod
    def batch_encode(items: List["VideoClip"]) -> bytes:
        return msgspec.json.encode(items)

    @staticmethod
    def batch_decode(data: bytes) -> List["VideoClip"]:
        return msgspec.json.decode(data, type=List[VideoClip])

    @staticmethod
    def batch_to_numpy(items: List["VideoClip"]):
        return np.array([item.as_tuple() for item in items], dtype=object)

    @staticmethod
    def batch_to_pandas(items: List["VideoClip"]):
        if pd is None:
            raise ImportError("pandas is not installed")
        return pd.DataFrame([item.__dict__ for item in items])

    @staticmethod
    def batch_to_parquet(items: List["VideoClip"], path: str):
        if pd is None:
            raise ImportError("pandas is not installed")
        VideoClip.batch_to_pandas(items).to_parquet(path)

    @staticmethod
    def batch_from_parquet(path: str) -> List["VideoClip"]:
        if pd is None:
            raise ImportError("pandas is not installed")
        df = pd.read_parquet(path)
        return [VideoClip(**d) for d in df.to_dict(orient="records")]

    @staticmethod
    def batch_validate_unique(items: List["VideoClip"], key=lambda x: x.caption):
        seen = set()
        for item in items:
            k = key(item)
            if k in seen:
                if sentry_sdk:
                    sentry_sdk.capture_message(f"Duplicate key found: {k}")
                raise ValueError(f"Duplicate key found: {k}")
            seen.add(k)

    @classmethod
    def batch_to_dicts(cls, objs: List["VideoClip"]) -> List[dict]:
        Counter('videoclip_batch_to_dicts_total', 'Total batch_to_dicts calls').inc()
        logger.info("batch_to_dicts", count=len(objs))
        return [orjson.loads(orjson.dumps(obj.__dict__)) for obj in objs]

    @classmethod
    def batch_from_dicts(cls, dicts: List[dict]) -> List["VideoClip"]:
        Counter('videoclip_batch_from_dicts_total', 'Total batch_from_dicts calls').inc()
        logger.info("batch_from_dicts", count=len(dicts))
        return [cls(**d) for d in dicts]

    @classmethod
    def batch_deduplicate(cls, objs: List["VideoClip"], key="caption") -> List["VideoClip"]:
        seen = set()
        result = []
        for obj in objs:
            k = getattr(obj, key, None)
            if k not in seen:
                seen.add(k)
                result.append(obj)
        logger.info("batch_deduplicate", unique=len(result))
        return result

    @classmethod
    def to_training_example(cls, obj: "VideoClip") -> dict:
        return orjson.loads(orjson.dumps(obj.__dict__))

    @classmethod
    def from_training_example(cls, data: dict) -> "VideoClip":
        return cls(**data)

    @validate_model(validate_types=True, validate_custom=True)
    @cache_model(key_field="caption")
    @log_operations()
    def save(self, user_context=None):
        super().save(user_context=user_context)

class VideoClipResponse(OnyxBaseModel, msgspec.Struct, frozen=True, slots=True):
    """Response model with the list of generated video clips."""
    youtube_url: str
    clips: List[VideoClip]
    logo_path: Optional[str]
    language: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: ModelStatus = ModelStatus.ACTIVE

    def as_tuple(self) -> tuple:
        return (self.youtube_url, self.clips, self.logo_path, self.language)

    @staticmethod
    def batch_encode(items: List["VideoClipResponse"]) -> bytes:
        return msgspec.json.encode(items)

    @staticmethod
    def batch_decode(data: bytes) -> List["VideoClipResponse"]:
        return msgspec.json.decode(data, type=List[VideoClipResponse])

    @staticmethod
    def batch_to_numpy(items: List["VideoClipResponse"]):
        return np.array([item.as_tuple() for item in items], dtype=object)

    @staticmethod
    def batch_to_pandas(items: List["VideoClipResponse"]):
        if pd is None:
            raise ImportError("pandas is not installed")
        return pd.DataFrame([item.__dict__ for item in items])

    @staticmethod
    def batch_to_parquet(items: List["VideoClipResponse"], path: str):
        if pd is None:
            raise ImportError("pandas is not installed")
        VideoClipResponse.batch_to_pandas(items).to_parquet(path)

    @staticmethod
    def batch_from_parquet(path: str) -> List["VideoClipResponse"]:
        if pd is None:
            raise ImportError("pandas is not installed")
        df = pd.read_parquet(path)
        return [VideoClipResponse(**d) for d in df.to_dict(orient="records")]

    @staticmethod
    def batch_validate_unique(items: List["VideoClipResponse"], key=lambda x: x.youtube_url):
        seen = set()
        for item in items:
            k = key(item)
            if k in seen:
                if sentry_sdk:
                    sentry_sdk.capture_message(f"Duplicate key found: {k}")
                raise ValueError(f"Duplicate key found: {k}")
            seen.add(k)

    @classmethod
    def batch_to_dicts(cls, objs: List["VideoClipResponse"]) -> List[dict]:
        Counter('videoclipresponse_batch_to_dicts_total', 'Total batch_to_dicts calls').inc()
        logger.info("batch_to_dicts", count=len(objs))
        return [orjson.loads(orjson.dumps(obj.__dict__)) for obj in objs]

    @classmethod
    def batch_from_dicts(cls, dicts: List[dict]) -> List["VideoClipResponse"]:
        Counter('videoclipresponse_batch_from_dicts_total', 'Total batch_from_dicts calls').inc()
        logger.info("batch_from_dicts", count=len(dicts))
        return [cls(**d) for d in dicts]

    @classmethod
    def batch_deduplicate(cls, objs: List["VideoClipResponse"], key="youtube_url") -> List["VideoClipResponse"]:
        seen = set()
        result = []
        for obj in objs:
            k = getattr(obj, key, None)
            if k not in seen:
                seen.add(k)
                result.append(obj)
        logger.info("batch_deduplicate", unique=len(result))
        return result

    @classmethod
    def to_training_example(cls, obj: "VideoClipResponse") -> dict:
        return orjson.loads(orjson.dumps(obj.__dict__))

    @classmethod
    def from_training_example(cls, data: dict) -> "VideoClipResponse":
        return cls(**data)

    @validate_model(validate_types=True, validate_custom=True)
    @cache_model(key_field="youtube_url")
    @log_operations()
    def save(self, user_context=None):
        super().save(user_context=user_context)

class VideoClipProcessor:
    """Processing logic for extracting clips, captions, logo, and emojis from a YouTube video."""
    @staticmethod
    def process(request: VideoClipRequest) -> VideoClipResponse:
        # --- Stub logic: Replace with real video/audio/LLM processing ---
        dummy_clips = [
            VideoClip(start=0, end=20, caption="Welcome to the video!", emojis=["👋", "🎬"]),
            VideoClip(start=21, end=40, caption="Key moment explained.", emojis=["💡", "✨"]),
            VideoClip(start=41, end=60, caption="Don't forget to subscribe!", emojis=["🔔", "👍"]),
        ]
        return VideoClipResponse(
            youtube_url=request.youtube_url,
            clips=dummy_clips,
            logo_path=request.logo_path,
            language=request.language
        )

class ViralClipVariant(OnyxBaseModel, msgspec.Struct, frozen=True, slots=True):
    """Variante viral de un clip corto generado a partir de un video largo."""
    start: float
    end: float
    caption: str
    emojis: list[str]
    hashtags: list[str]
    logo_style: str
    cta: str
    format: str
    viral_score: float
    tone: str
    variant_id: str
    experiment_id: str
    audience_profile: dict
    metadata: dict = {}

    def as_tuple(self) -> tuple:
        return (self.start, self.end, self.caption, self.emojis, self.hashtags, self.logo_style, self.cta, self.format, self.viral_score, self.tone, self.variant_id, self.experiment_id, self.audience_profile)

    @staticmethod
    def batch_encode(items: list["ViralClipVariant"]) -> bytes:
        return msgspec.json.encode(items)

    @staticmethod
    def batch_decode(data: bytes) -> list["ViralClipVariant"]:
        return msgspec.json.decode(data, type=list[ViralClipVariant])

    @staticmethod
    def batch_to_numpy(items: list["ViralClipVariant"]):
        return np.array([item.as_tuple() for item in items], dtype=object)

    @staticmethod
    def batch_to_pandas(items: list["ViralClipVariant"]):
        if pd is None:
            raise ImportError("pandas is not installed")
        return pd.DataFrame([item.__dict__ for item in items])

    @staticmethod
    def batch_to_parquet(items: list["ViralClipVariant"], path: str):
        if pd is None:
            raise ImportError("pandas is not installed")
        ViralClipVariant.batch_to_pandas(items).to_parquet(path)

    @staticmethod
    def batch_from_parquet(path: str) -> list["ViralClipVariant"]:
        if pd is None:
            raise ImportError("pandas is not installed")
        df = pd.read_parquet(path)
        return [ViralClipVariant(**d) for d in df.to_dict(orient="records")]

    @staticmethod
    def batch_validate_unique(items: list["ViralClipVariant"], key=lambda x: (x.start, x.end)):
        seen = set()
        for item in items:
            k = key(item)
            if k in seen:
                if sentry_sdk:
                    sentry_sdk.capture_message(f"Duplicate key found: {k}")
                raise ValueError(f"Duplicate key found: {k}")
            seen.add(k)

class CaptionOutput(LCBaseModel):
    caption: str
    emojis: list[str]
    hashtags: list[str]
    cta: str

class ViralVideoBatchResponse(OnyxBaseModel, msgspec.Struct, frozen=True, slots=True):
    """Respuesta batch con variantes virales generadas."""
    youtube_url: str
    variants: list[ViralClipVariant]
    original_duration: float
    language: str
    batch_id: str
    created_at: datetime
    source_video_stats: dict

    def as_tuple(self) -> tuple:
        return (self.youtube_url, self.variants, self.original_duration, self.language, self.batch_id, self.created_at, self.source_video_stats)

    @staticmethod
    def batch_encode(items: list["ViralVideoBatchResponse"]) -> bytes:
        return msgspec.json.encode(items)

    @staticmethod
    def batch_decode(data: bytes) -> list["ViralVideoBatchResponse"]:
        return msgspec.json.decode(data, type=list[ViralVideoBatchResponse])

    @staticmethod
    def batch_to_numpy(items: list["ViralVideoBatchResponse"]):
        return np.array([item.as_tuple() for item in items], dtype=object)

    @staticmethod
    def batch_to_pandas(items: list["ViralVideoBatchResponse"]):
        if pd is None:
            raise ImportError("pandas is not installed")
        return pd.DataFrame([item.__dict__ for item in items])

    @staticmethod
    def batch_to_parquet(items: list["ViralVideoBatchResponse"], path: str):
        if pd is None:
            raise ImportError("pandas is not installed")
        ViralVideoBatchResponse.batch_to_pandas(items).to_parquet(path)

    @staticmethod
    def batch_from_parquet(path: str) -> list["ViralVideoBatchResponse"]:
        if pd is None:
            raise ImportError("pandas is not installed")
        df = pd.read_parquet(path)
        return [ViralVideoBatchResponse(**d) for d in df.to_dict(orient="records")]

class ViralVideoProcessor:
    """Pipeline para generar variantes virales de un video largo."""
    @staticmethod
    @log_operations()
    def process(request: VideoClipRequest, n_variants: int = 10, audience_profile: dict = None, experiment_id: str = None) -> ViralVideoBatchResponse:
        return generate_viral_variants(request, n_variants, audience_profile, experiment_id) 