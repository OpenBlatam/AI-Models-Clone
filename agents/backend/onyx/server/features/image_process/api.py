from typing import List, Callable, TypeVar
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Response
import base64
import asyncio
import concurrent.futures
import os
import time
import hashlib
from functools import lru_cache

from .models import (
    ImageExtractRequest, ImageExtractResponse,
    ImageSummaryRequest, ImageSummaryResponse,
    ImageValidationRequest, ImageValidationResponse,
    ImageAnalysisResult,
)
from .service import ImageProcessService
from .config import config
from .fast_decode import decode_bytes_fast
from .image_utils import (
    validate_mime_declared_vs_actual,
    resize_max_side,
    dominant_color_hex,
)

# Metrics (optional)
try:  # pragma: no cover - optional dependency
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST  # type: ignore
    _METRICS_ENABLED = True
    _REQS = Counter("image_process_requests_total", "Total requests", ["endpoint", "status"])  # type: ignore
    _LAT = Histogram("image_process_request_duration_seconds", "Duration seconds", ["endpoint"])  # type: ignore
except Exception:  # pragma: no cover
    _METRICS_ENABLED = False

    class _Noop:
        def labels(self, *_, **__):
            return self

        def inc(self, *_: object, **__: object) -> None:
            return None

        def observe(self, *_: object, **__: object) -> None:
            return None

    _REQS = _Noop()  # type: ignore
    _LAT = _Noop()  # type: ignore

"""API endpoints for Image Process feature (Onyx)."""

router = APIRouter(prefix="/image-process", tags=["image-process"])
service = ImageProcessService()
# Adaptive pool: leave 1 core for event loop/OS, minimum 2
_cpu = max(os.cpu_count() or 2, 2)
_env_max = int(os.getenv("IMAGE_PROCESS_MAX_WORKERS", "0") or 0)
_max_workers = _env_max if _env_max > 0 else max(2, _cpu - 1)
EXEC = concurrent.futures.ThreadPoolExecutor(max_workers=_max_workers)


@lru_cache(maxsize=config.META_CACHE_SIZE)
def _build_metadata(raw: bytes, mime_type: str, max_side_px: int) -> dict:
    """Pure builder to enable efficient LRU caching of metadata.
    Safe to cache since output depends only on inputs.
    """
    im = decode_bytes_fast(raw, mime_type)
    validate_mime_declared_vs_actual(im, mime_type)
    im_resized = resize_max_side(im, max_side_px)
    return {
        "bands": im.getbands(),
        "size": im.size,
        "size_resized": im_resized.size,
        "mime": mime_type,
        "dominant_color": dominant_color_hex(im_resized),
    }


@router.post("/extract", response_model=ImageExtractResponse)
async def extract_text(request: ImageExtractRequest):
    """Extract text from an image (URL o base64)."""
    response = await _run_service("extract", service.extract_text, request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return response


@router.post("/summarize", response_model=ImageSummaryResponse)
async def summarize_image(request: ImageSummaryRequest):
    """Summarize an image (URL o base64)."""
    response = await _run_service("summarize", service.summarize, request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return response


@router.post("/validate", response_model=ImageValidationResponse)
async def validate_image(request: ImageValidationRequest):
    """Validate an image (format, content, etc)."""
    response = await _run_service("validate", service.validate, request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return response


@router.post("/analyze", response_model=ImageAnalysisResult)
def analyze_image(request: ImageExtractRequest):
    """Análisis avanzado de imagen (IA, OCR, detección de objetos, etc.)."""
    return ImageProcessService.analyze(request)


# Optimized endpoints (batch and multipart) without breaking existing ones

@router.post("/summarize-batch", response_model=List[ImageSummaryResponse])
async def summarize_image_batch(requests: List[ImageSummaryRequest]):
    """Summarize multiple images in one call (amortizes overhead), parallelized."""
    if len(requests) > config.BATCH_MAX_ITEMS:
        raise HTTPException(status_code=400, detail="batch_too_large")
    with _LAT.labels("summarize-batch").time():  # type: ignore[attr-defined]
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(EXEC, service.summarize, req) for req in requests]
        responses = await asyncio.gather(*tasks)
    for r in responses:
        _REQS.labels("summarize-batch", "ok" if r.success else "error").inc()
    return responses


@router.post("/summary-multipart", response_model=ImageSummaryResponse)
async def summary_multipart(
    file: UploadFile = File(...),
    mime_type: str = Form(...),
    max_side_px: int = Form(config.DEFAULT_MAX_SIDE_PX),
    max_size_bytes: int = Form(config.MAX_BYTES),
):
    """Multipart variant to avoid base64 overhead. Wraps into existing summarize flow."""
    started_ns = time.perf_counter_ns()
    # Streamed read with early 413 enforcement
    chunks: list[bytes] = []
    total = 0
    chunk_size = 1_048_576  # 1 MiB
    while True:
        to_read = min(chunk_size, max(1, max_size_bytes - total))
        part = await file.read(to_read)
        if not part:
            break
        total += len(part)
        if total > max_size_bytes:
            raise HTTPException(status_code=413, detail="payload_too_large")
        chunks.append(part)
    raw = b"".join(chunks)
    if not raw:
        raise HTTPException(status_code=400, detail="empty_file")
    if len(raw) > max_size_bytes:
        raise HTTPException(status_code=413, detail="payload_too_large")
    # Basic content-type check to avoid obvious mismatches
    if file.content_type and mime_type and file.content_type != mime_type:
        raise HTTPException(status_code=400, detail="content_type_mismatch")
    # Enforce allowed MIME
    if mime_type not in config.ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="unsupported_mime")
    # Clamp side bounds
    if max_side_px < config.MIN_SIDE_PX:
        max_side_px = config.MIN_SIDE_PX
    if max_side_px > config.MAX_SIDE_PX:
        max_side_px = config.MAX_SIDE_PX
    # Fast decode path for basic validation and to populate metadata
    # Cache key by content hash + params
    try:
        meta = _build_metadata(raw, mime_type, max_side_px)
    except HTTPException:
        raise
    except Exception:  # pragma: no cover - best-effort
        meta = {"mime": mime_type}
    b64 = base64.b64encode(raw).decode()
    req = ImageSummaryRequest(image_url=None, image_base64=b64, summary_type="simple")
    resp = service.summarize(req)
    if not resp.success:
        raise HTTPException(status_code=400, detail=resp.error)
    # Attach metadata non-breaking
    if resp.metadata is None:
        resp.metadata = {}
    duration_ms = int((time.perf_counter_ns() - started_ns) / 1_000_000)
    resp.metadata.update({
        **meta,
        "size_bytes": len(raw),
        "summary_ms": duration_ms,
        "filename": (file.filename or ""),
    })
    # metrics
    _REQS.labels("summary-multipart", "ok" if resp.success else "error").inc()
    _LAT.labels("summary-multipart").observe(duration_ms / 1000.0)  # type: ignore[attr-defined]
    # metadata is LRU cached via _build_metadata
    return resp


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "max_workers": _max_workers,
        "allowed_mime": sorted(list(config.ALLOWED_MIME)),
        "default_max_side_px": config.DEFAULT_MAX_SIDE_PX,
        "meta_cache_size": config.META_CACHE_SIZE,
        "metrics": _METRICS_ENABLED,
    }


@router.get("/config")
def get_config() -> dict:
    """Expose current effective configuration for introspection."""
    return {
        "limits": {
            "max_bytes": config.MAX_BYTES,
            "min_side_px": config.MIN_SIDE_PX,
            "default_max_side_px": config.DEFAULT_MAX_SIDE_PX,
            "max_side_px": config.MAX_SIDE_PX,
            "batch_max_items": config.BATCH_MAX_ITEMS,
        },
        "cache": {
            "meta_cache_size": config.META_CACHE_SIZE,
        },
        "mime": sorted(list(config.ALLOWED_MIME)),
        "executor": {"max_workers": _max_workers},
        "features": {
            "enable_summary": config.ENABLE_SUMMARY,
            "enable_extraction": config.ENABLE_EXTRACTION,
            "enable_validation": config.ENABLE_VALIDATION,
        },
    }


TReq = TypeVar("TReq")
TResp = TypeVar("TResp")

async def _run_service(metric: str, func: Callable[[TReq], TResp], request: TReq) -> TResp:
    """Run CPU-bound service call in executor with metrics."""
    with _LAT.labels(metric).time():  # type: ignore[attr-defined]
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(EXEC, lambda: func(request))
    # Try to infer success field
    try:
        success = bool(getattr(response, "success", True))
    except Exception:
        success = True
    _REQS.labels(metric, "ok" if success else "error").inc()
    return response


@router.get("/metrics")
def metrics():  # pragma: no cover - optional export
    if not _METRICS_ENABLED:
        raise HTTPException(status_code=503, detail="metrics_unavailable")
    data = generate_latest()  # type: ignore
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)  # type: ignore