"""
Módulos de Face Swap Professional
==================================
Estructura modular refactorizada para mejor organización y mantenibilidad.
Sigue principios SOLID y DRY para código limpio y mantenible.
"""

from .face_detector import FaceDetector
from .landmark_extractor import LandmarkExtractor
from .face_analyzer import FaceAnalyzer
from .color_corrector import ColorCorrector
from .blending_engine import BlendingEngine
from .quality_enhancer import QualityEnhancer
from .post_processor import PostProcessor
from .advanced_enhancements import AdvancedEnhancements

# Export base classes and utilities for advanced usage
from .base import BaseDetector, LandmarkFormatHandler, ImageProcessor

# Export FaceSwapPipeline (debe ir después de los otros imports para evitar circular)
try:
    from .face_swap_pipeline import FaceSwapPipeline
except ImportError:
    # Si hay importación circular, intentar importar después
    FaceSwapPipeline = None

# Export optimizations if available
try:
    from .optimizations import (
        fast_gaussian_blur_1d,
        fast_bilateral_filter_grayscale,
        fast_histogram_matching,
        fast_laplacian_variance,
        fast_mask_blending,
        is_numba_available
    )
    OPTIMIZATIONS_AVAILABLE = True
except ImportError:
    OPTIMIZATIONS_AVAILABLE = False

__all__ = [
    'FaceDetector',
    'LandmarkExtractor',
    'FaceAnalyzer',
    'ColorCorrector',
    'BlendingEngine',
    'QualityEnhancer',
    'PostProcessor',
    'AdvancedEnhancements',
    'BaseDetector',
    'LandmarkFormatHandler',
    'ImageProcessor',
]

# Agregar FaceSwapPipeline si está disponible (después de definir __all__ para evitar circular)
if FaceSwapPipeline is not None:
    __all__.append('FaceSwapPipeline')

# Add optimizations to __all__ if available
if OPTIMIZATIONS_AVAILABLE:
    __all__.extend([
        'fast_gaussian_blur_1d',
        'fast_bilateral_filter_grayscale',
        'fast_histogram_matching',
        'fast_laplacian_variance',
        'fast_mask_blending',
        'is_numba_available'
    ])

__version__ = '2.1.0'








