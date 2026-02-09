"""
Professional Face Detector
==========================
Módulo para detección de caras usando múltiples librerías especializadas.
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from .lib_availability import (
    MEDIAPIPE_AVAILABLE, INSIGHTFACE_AVAILABLE, RETINAFACE_AVAILABLE
)

if MEDIAPIPE_AVAILABLE:
    import mediapipe as mp

if RETINAFACE_AVAILABLE:
    from retinaface import RetinaFace


class ProfessionalFaceDetector:
    """Detector de caras profesional usando múltiples librerías."""
    
    def __init__(self):
        """Inicializar detectores disponibles."""
        self.face_mesh = None
        self.face_cascade = None
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
        
        # Fallback a OpenCV
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Inicializar InsightFace si está disponible
        if INSIGHTFACE_AVAILABLE:
            try:
                import insightface
                self.insightface_app = insightface.app.FaceAnalysis(
                    providers=['CPUExecutionProvider']
                )
                self.insightface_app.prepare(ctx_id=0, det_size=(640, 640))
            except Exception:
                self.insightface_app = None
    
    def detect_face_mediapipe(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta cara usando MediaPipe."""
        if not MEDIAPIPE_AVAILABLE or self.face_mesh is None:
            return None
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            h, w = image.shape[:2]
            
            x_coords = [landmark.x * w for landmark in face_landmarks.landmark]
            y_coords = [landmark.y * h for landmark in face_landmarks.landmark]
            
            x_min, x_max = int(min(x_coords)), int(max(x_coords))
            y_min, y_max = int(min(y_coords)), int(max(y_coords))
            
            margin = 0.1
            width = x_max - x_min
            height = y_max - y_min
            x_min = max(0, int(x_min - width * margin))
            y_min = max(0, int(y_min - height * margin))
            x_max = min(w, int(x_max + width * margin))
            y_max = min(h, int(y_max + height * margin))
            
            return (x_min, y_min, x_max - x_min, y_max - y_min)
        
        return None
    
    def detect_face_insightface(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta cara usando InsightFace."""
        if not INSIGHTFACE_AVAILABLE or self.insightface_app is None:
            return None
        
        try:
            faces = self.insightface_app.get(image)
            if faces and len(faces) > 0:
                face = faces[0]
                bbox = face.bbox.astype(np.int32)
                x, y, x2, y2 = bbox
                return (x, y, x2 - x, y2 - y)
        except Exception:
            pass
        
        return None
    
    def detect_face_retinaface(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta cara usando RetinaFace."""
        if not RETINAFACE_AVAILABLE:
            return None
        
        try:
            faces = RetinaFace.detect_faces(image)
            if faces:
                face_key = list(faces.keys())[0]
                face_data = faces[face_key]
                facial_area = face_data['facial_area']
                x, y, x2, y2 = facial_area
                return (x, y, x2 - x, y2 - y)
        except Exception:
            pass
        
        return None
    
    def detect_face_opencv(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta cara usando OpenCV (fallback)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        gray_enhanced = clahe.apply(gray)
        
        faces = self.face_cascade.detectMultiScale(
            gray_enhanced,
            scaleFactor=1.05,
            minNeighbors=6,
            minSize=(100, 100)
        )
        
        if len(faces) > 0:
            faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            return tuple(faces[0])
        
        return None
    
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta cara usando el mejor método disponible."""
        # Prioridad: InsightFace > RetinaFace > MediaPipe > OpenCV
        if INSIGHTFACE_AVAILABLE:
            result = self.detect_face_insightface(image)
            if result:
                return result
        
        if RETINAFACE_AVAILABLE:
            result = self.detect_face_retinaface(image)
            if result:
                return result
        
        if MEDIAPIPE_AVAILABLE:
            result = self.detect_face_mediapipe(image)
            if result:
                return result
        
        return self.detect_face_opencv(image)






