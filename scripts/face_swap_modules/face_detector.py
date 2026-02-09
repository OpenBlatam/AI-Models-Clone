"""
Face Detector Module
====================
Módulo para detección facial usando múltiples métodos con fallback automático.
Refactorizado para seguir principios SOLID y DRY.
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List
from .base import BaseDetector

# Importar librerías opcionales
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

try:
    import insightface
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False

try:
    from retinaface import RetinaFace
    RETINAFACE_AVAILABLE = True
except ImportError:
    RETINAFACE_AVAILABLE = False


class FaceDetector(BaseDetector):
    """
    Detector facial con múltiples métodos y fallback automático.
    
    Prioridad de métodos:
    1. InsightFace (más preciso)
    2. RetinaFace (buen balance)
    3. MediaPipe (rápido)
    4. OpenCV (fallback universal)
    """
    
    # Detection method priority order
    DETECTION_METHODS = ['insightface', 'retinaface', 'mediapipe', 'opencv']
    
    def __init__(self):
        """Initialize face detector with available models."""
        super().__init__()
        self._initialize_models()
        self._initialized = True
    
    def _initialize_models(self) -> None:
        """Initialize available detection models."""
        if MEDIAPIPE_AVAILABLE:
            self._models['mediapipe'] = mp.solutions.face_detection.FaceDetection(
                model_selection=1, 
                min_detection_confidence=0.5
            )
        
        if INSIGHTFACE_AVAILABLE:
            self._models['insightface'] = self._safe_execute(
                self._create_insightface_model
            )
    
    def _create_insightface_model(self):
        """Create and prepare InsightFace model."""
        model = insightface.app.FaceAnalysis(
            providers=['CPUExecutionProvider']
        )
        model.prepare(ctx_id=-1, det_size=(640, 640))
        return model
    
    def _detect_with_insightface(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect face using InsightFace (highest priority)."""
        if not self._is_model_available('insightface'):
            return None
        
        def _detect():
            faces = self._models['insightface'].get(image)
            if faces and len(faces) > 0:
                bbox = faces[0].bbox.astype(int)
                return (bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])
            return None
        
        return self._safe_execute(_detect)
    
    def _detect_with_retinaface(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect face using RetinaFace."""
        if not RETINAFACE_AVAILABLE:
            return None
        
        def _detect():
            faces = RetinaFace.detect_faces(image)
            if faces:
                face_key = list(faces.keys())[0]
                facial_area = faces[face_key]['facial_area']
                x, y, x2, y2 = facial_area
                return (x, y, x2 - x, y2 - y)
            return None
        
        return self._safe_execute(_detect)
    
    def _detect_with_mediapipe(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect face using MediaPipe."""
        if not self._is_model_available('mediapipe'):
            return None
        
        def _detect():
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self._models['mediapipe'].process(rgb_image)
            
            if results.detections and len(results.detections) > 0:
                detection = results.detections[0]
                bbox = detection.location_data.relative_bounding_box
                h, w = image.shape[:2]
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                return (x, y, width, height)
            return None
        
        return self._safe_execute(_detect)
    
    def _detect_with_opencv(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect face using OpenCV (universal fallback)."""
        def _detect():
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                x, y, w, h = faces[0]
                return (x, y, w, h)
            return None
        
        return self._safe_execute(_detect)
    
    def detect(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect face using the best available method with automatic fallback.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            Tuple of (x, y, width, height) or None if no face detected
        """
        # Validación de inputs
        if not isinstance(image, np.ndarray):
            raise TypeError("image debe ser np.ndarray")
        if image.size == 0:
            raise ValueError("image no puede estar vacío")
        if len(image.shape) < 2:
            raise ValueError("image debe tener al menos 2 dimensiones")
        
        # Try methods in priority order
        detection_methods = {
            'insightface': self._detect_with_insightface,
            'retinaface': self._detect_with_retinaface,
            'mediapipe': self._detect_with_mediapipe,
            'opencv': self._detect_with_opencv
        }
        
        for method_name in self.DETECTION_METHODS:
            if method_name in detection_methods:
                result = detection_methods[method_name](image)
                if result is not None:
                    return result
        
        return None
    
    # Alias for backward compatibility
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Alias for detect() method for backward compatibility."""
        return self.detect(image)
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Alias para detect() que retorna lista para compatibilidad.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            List of tuples (x, y, width, height) or empty list if no face detected
        """
        result = self.detect(image)
        return [result] if result is not None else []








