"""
Core Value Objects
=================

This module contains all value objects for the AI Video system.
Value objects are immutable objects that represent concepts in the domain.
"""

from .video_config import VideoConfig
from .avatar_config import AvatarConfig
from .script_config import ScriptConfig
from .image_sync_config import ImageSyncConfig
from .template_config import TemplateConfig

__all__ = [
    "VideoConfig",
    "AvatarConfig", 
    "ScriptConfig",
    "ImageSyncConfig",
    "TemplateConfig",
] 