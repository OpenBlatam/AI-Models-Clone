"""Centralized configuration for the image_process feature.

Minimal, framework-free to avoid runtime dependencies in tests.
"""


class ImageProcessConfig:
    # Limits
    MAX_BYTES: int = 10_000_000
    DEFAULT_MAX_SIDE_PX: int = 2048

    # MIME/Formats
    ALLOWED_MIME: set[str] = {"image/png", "image/jpeg", "image/webp"}

    # Feature flags
    ENABLE_SUMMARY: bool = True
    ENABLE_EXTRACTION: bool = True
    ENABLE_VALIDATION: bool = True

    # Caching/other
    CACHE_TTL_HOURS: int = 24
    META_CACHE_SIZE: int = 256
    BATCH_MAX_ITEMS: int = 32
    MIN_SIDE_PX: int = 32
    MAX_SIDE_PX: int = 8192


config = ImageProcessConfig()