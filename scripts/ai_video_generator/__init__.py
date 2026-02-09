"""
AI Video Generator - Módulo Refactorizado
==========================================
Módulo refactorizado para generación de videos con IA desde imágenes.
"""

from .image_enhancer import ImageEnhancer
from .ken_burns_effect import KenBurnsEffect
from .video_composer import VideoComposer
from .caption_extractor import CaptionExtractor
from .video_processor import VideoProcessor

__version__ = '2.0.0'
__all__ = [
    'ImageEnhancer',
    'KenBurnsEffect',
    'VideoComposer',
    'CaptionExtractor',
    'VideoProcessor'
]







