"""
Configuration for Image Process feature.
"""
from pydantic import BaseSettings

class ImageProcessConfig(BaseSettings):
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_FORMATS: list = ["jpg", "jpeg", "png", "bmp", "gif"]
    ENABLE_SUMMARY: bool = True
    ENABLE_EXTRACTION: bool = True
    ENABLE_VALIDATION: bool = True
    CACHE_TTL_HOURS: int = 24

    class Config:
        env_prefix = "IMAGE_PROCESS_"
        case_sensitive = False

config = ImageProcessConfig() 