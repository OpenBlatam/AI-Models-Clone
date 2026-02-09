"""
Professional Landmark Extractor
================================
Módulo para extracción de landmarks faciales usando múltiples librerías.
"""

import cv2
import numpy as np
from typing import Optional
from .lib_availability import (
    MEDIAPIPE_AVAILABLE, FACE_ALIGNMENT_AVAILABLE, INSIGHTFACE_AVAILABLE
)

if MEDIAPIPE_AVAILABLE:
    import mediapipe as mp


class ProfessionalLandmarkExtractor:
    """Extractor de landmarks faciales profesional."""
    
    def __init__(self, detector=None):
        """
        Inicializar extractor.
        
        Args:
            detector: Instancia de ProfessionalFaceDetector (opcional)
        """
        self.detector = detector
        self.face_mesh = None
        self.face_aligner = None
        self.insightface_app = None
        
        # Inicializar MediaPipe si está disponible
        if MEDIAPIPE_AVAILABLE:
            try:
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                )
            except Exception:
                self.face_mesh = None
        
        # Inicializar face-alignment si está disponible
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                import face_alignment
                self.face_aligner = face_alignment.FaceAlignment(
                    face_alignment.LandmarksType.TWO_D,
                    flip_input=False,
                    device='cpu'
                )
            except Exception:
                self.face_aligner = None
        
        # Usar InsightFace del detector si está disponible
        if detector and hasattr(detector, 'insightface_app'):
            self.insightface_app = detector.insightface_app
    
    def get_face_landmarks_mediapipe(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Obtiene landmarks usando MediaPipe."""
        if not MEDIAPIPE_AVAILABLE or self.face_mesh is None:
            return None
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            h, w = image.shape[:2]
            
            landmarks = np.array([
                [landmark.x * w, landmark.y * h]
                for landmark in face_landmarks.landmark
            ])
            
            return landmarks
        
        return None
    
    def get_face_landmarks_face_alignment(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Obtiene landmarks usando face-alignment."""
        if not FACE_ALIGNMENT_AVAILABLE or self.face_aligner is None:
            return None
        
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            landmarks = self.face_aligner.get_landmarks(rgb_image)
            
            if landmarks is not None and len(landmarks) > 0:
                return landmarks[0]
        except Exception:
            pass
        
        return None
    
    def get_face_landmarks_insightface(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Obtiene landmarks usando InsightFace."""
        if not INSIGHTFACE_AVAILABLE or self.insightface_app is None:
            return None
        
        try:
            faces = self.insightface_app.get(image)
            if faces and len(faces) > 0:
                face = faces[0]
                landmarks = face.landmark_2d_106  # 106 landmarks
                return landmarks
        except Exception:
            pass
        
        return None
    
    def get_face_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Obtiene landmarks usando el mejor método disponible."""
        # Prioridad: InsightFace > face-alignment > MediaPipe
        if INSIGHTFACE_AVAILABLE:
            result = self.get_face_landmarks_insightface(image)
            if result is not None:
                return result
        
        if FACE_ALIGNMENT_AVAILABLE:
            result = self.get_face_landmarks_face_alignment(image)
            if result is not None:
                return result
        
        if MEDIAPIPE_AVAILABLE:
            result = self.get_face_landmarks_mediapipe(image)
            if result is not None:
                return result
        
        return None






