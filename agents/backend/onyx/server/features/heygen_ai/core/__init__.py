from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .heygen_ai import HeyGenAI
from .avatar_manager import AvatarManager
from .voice_engine import VoiceEngine
from .video_renderer import VideoRenderer
from .script_generator import ScriptGenerator
from .langchain_manager import LangChainManager
from .advanced_ai_workflows import AdvancedAIWorkflows
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
HeyGen AI Core Module
Main entry point for the HeyGen AI equivalent system.
"""


__version__ = "1.0.0"
__author__ = "Blatam Academy"

__all__ = [
    "HeyGenAI",
    "AvatarManager", 
    "VoiceEngine",
    "VideoRenderer",
    "ScriptGenerator",
    "LangChainManager",
    "AdvancedAIWorkflows"
] 