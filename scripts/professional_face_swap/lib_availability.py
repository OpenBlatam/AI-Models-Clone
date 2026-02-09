"""
Library Availability Checker
=============================
Verifica disponibilidad de librerías especializadas para face swap profesional.
"""

import sys
from typing import Dict, Optional

# Intentar importar librerías especializadas
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    FACE_ALIGNMENT_AVAILABLE = False

try:
    from skimage import transform as sktransform
    from skimage import filters
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False

try:
    from PIL import Image, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import insightface
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

try:
    import albumentations as A
    ALBUMENTATIONS_AVAILABLE = True
except ImportError:
    ALBUMENTATIONS_AVAILABLE = False

try:
    import kornia
    KORNIA_AVAILABLE = True
except ImportError:
    KORNIA_AVAILABLE = False

try:
    from retinaface import RetinaFace
    RETINAFACE_AVAILABLE = True
except ImportError:
    RETINAFACE_AVAILABLE = False

try:
    import imageio
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False

try:
    from scipy import ndimage
    from scipy.spatial import distance
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import numba
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Crear decorador dummy si numba no está disponible
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

try:
    from skimage import segmentation, restoration
    SKIMAGE_ADVANCED_AVAILABLE = True
except ImportError:
    SKIMAGE_ADVANCED_AVAILABLE = False


class LibraryAvailability:
    """Mantiene estado de disponibilidad de librerías."""
    
    def __init__(self):
        self.mediapipe = MEDIAPIPE_AVAILABLE
        self.face_alignment = FACE_ALIGNMENT_AVAILABLE
        self.skimage = SKIMAGE_AVAILABLE
        self.pil = PIL_AVAILABLE
        self.insightface = INSIGHTFACE_AVAILABLE
        self.onnx = ONNX_AVAILABLE
        self.albumentations = ALBUMENTATIONS_AVAILABLE
        self.kornia = KORNIA_AVAILABLE
        self.retinaface = RETINAFACE_AVAILABLE
        self.imageio = IMAGEIO_AVAILABLE
        self.scipy = SCIPY_AVAILABLE
        self.numba = NUMBA_AVAILABLE
        self.skimage_advanced = SKIMAGE_ADVANCED_AVAILABLE
    
    def get_available_detectors(self) -> list:
        """Retorna lista de detectores disponibles."""
        detectors = []
        if self.insightface:
            detectors.append('insightface')
        if self.retinaface:
            detectors.append('retinaface')
        if self.mediapipe:
            detectors.append('mediapipe')
        detectors.append('opencv')  # Siempre disponible
        return detectors
    
    def get_available_landmark_extractors(self) -> list:
        """Retorna lista de extractores de landmarks disponibles."""
        extractors = []
        if self.face_alignment:
            extractors.append('face_alignment')
        if self.insightface:
            extractors.append('insightface')
        if self.mediapipe:
            extractors.append('mediapipe')
        return extractors


def check_library_availability() -> LibraryAvailability:
    """Verifica disponibilidad de todas las librerías."""
    return LibraryAvailability()






