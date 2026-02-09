"""
Landmark Extractor Module
==========================
Módulo para extracción de landmarks faciales usando múltiples métodos.
Refactorizado para seguir principios SOLID y DRY.
"""

import cv2
import numpy as np
from typing import Optional
from .base import BaseDetector

# Importar librerías opcionales
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
    import insightface
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False


class LandmarkExtractor(BaseDetector):
    """
    Extractor de landmarks faciales con múltiples métodos y fallback automático.
    
    Prioridad de métodos:
    1. InsightFace (106 puntos, más preciso)
    2. face-alignment (68 puntos, balanceado)
    3. MediaPipe (468 puntos, más detallado pero más lento)
    """
    
    # Extraction method priority order
    EXTRACTION_METHODS = ['insightface', 'face_alignment', 'mediapipe']
    
    def __init__(self):
        """Initialize landmark extractor with available models."""
        super().__init__()
        self._initialize_models()
        self._initialized = True
    
    def _initialize_models(self) -> None:
        """Initialize available landmark extraction models."""
        if MEDIAPIPE_AVAILABLE:
            self._models['mediapipe'] = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5
            )
        
        if FACE_ALIGNMENT_AVAILABLE:
            self._models['face_alignment'] = self._safe_execute(
                self._create_face_alignment_model
            )
        
        if INSIGHTFACE_AVAILABLE:
            self._models['insightface'] = self._safe_execute(
                self._create_insightface_model
            )
    
    def _create_face_alignment_model(self):
        """Create face-alignment model."""
        return face_alignment.FaceAlignment(
            face_alignment.LandmarksType.TWO_D,
            flip_input=False,
            device='cpu'
        )
    
    def _create_insightface_model(self):
        """Create and prepare InsightFace model."""
        model = insightface.app.FaceAnalysis(
            providers=['CPUExecutionProvider']
        )
        model.prepare(ctx_id=-1, det_size=(640, 640))
        return model
    
    def _extract_with_insightface(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract landmarks using InsightFace (106 points, highest priority)."""
        if not self._is_model_available('insightface'):
            return None
        
        def _extract():
            faces = self._models['insightface'].get(image)
            if faces and len(faces) > 0:
                return faces[0].landmark_2d_106.astype(np.float32)
            return None
        
        return self._safe_execute(_extract)
    
    def _extract_with_face_alignment(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract landmarks using face-alignment (68 points)."""
        if not self._is_model_available('face_alignment'):
            return None
        
        def _extract():
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            landmarks = self._models['face_alignment'].get_landmarks(rgb_image)
            if landmarks and len(landmarks) > 0:
                return landmarks[0].astype(np.float32)
            return None
        
        return self._safe_execute(_extract)
    
    def _extract_with_mediapipe(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract landmarks using MediaPipe (468 points)."""
        if not self._is_model_available('mediapipe'):
            return None
        
        def _extract():
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self._models['mediapipe'].process(rgb_image)
            
            if results.multi_face_landmarks and len(results.multi_face_landmarks) > 0:
                landmarks = results.multi_face_landmarks[0]
                h, w = image.shape[:2]
                points = np.array([
                    [landmark.x * w, landmark.y * h] 
                    for landmark in landmarks.landmark
                ], dtype=np.float32)
                return points
            return None
        
        return self._safe_execute(_extract)
    
    def detect(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract landmarks using the best available method with automatic fallback.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            Array of landmark points or None if extraction fails
        """
        # Validación de inputs
        if not isinstance(image, np.ndarray):
            raise TypeError("image debe ser np.ndarray")
        if image.size == 0:
            raise ValueError("image no puede estar vacío")
        if len(image.shape) < 2:
            raise ValueError("image debe tener al menos 2 dimensiones")
        
        # Try methods in priority order
        extraction_methods = {
            'insightface': self._extract_with_insightface,
            'face_alignment': self._extract_with_face_alignment,
            'mediapipe': self._extract_with_mediapipe
        }
        
        for method_name in self.EXTRACTION_METHODS:
            if method_name in extraction_methods:
                result = extraction_methods[method_name](image)
                if result is not None:
                    return result
        
        return None
    
    # Alias for backward compatibility
    def get_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Alias for detect() method for backward compatibility."""
        return self.detect(image)
    
    def extract_landmarks(self, image: np.ndarray, face_rect: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """
        Alias para get_landmarks() para compatibilidad con código legacy.
        
        Args:
            image: Input image as numpy array (BGR format)
            face_rect: Optional face bounding box (x, y, width, height) - ignorado, se detecta automáticamente
            
        Returns:
            Array of landmark points or None if extraction fails
        """
        # face_rect se ignora ya que get_landmarks detecta automáticamente
        return self.get_landmarks(image)








