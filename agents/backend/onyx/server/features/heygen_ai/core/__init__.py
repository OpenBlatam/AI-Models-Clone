"""
HeyGen AI Core Module
Main entry point for the HeyGen AI equivalent system.
"""

from .heygen_ai import HeyGenAI
from .avatar_manager import AvatarManager
from .voice_engine import VoiceEngine
from .video_renderer import VideoRenderer
from .script_generator import ScriptGenerator
from .langchain_manager import LangChainManager
from .advanced_ai_workflows import AdvancedAIWorkflows

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