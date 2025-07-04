"""
Core Domain Entities
===================

This module contains all domain entities for the AI Video system.
Entities represent the core business objects with identity and lifecycle.
"""

from .template import Template
from .avatar import Avatar
from .video import Video
from .script import Script
from .user import User

__all__ = [
    "Template",
    "Avatar", 
    "Video",
    "Script",
    "User",
] 