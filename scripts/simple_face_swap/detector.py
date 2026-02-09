"""
Simple Face Detector
====================
Detector de caras simple usando solo OpenCV.
"""

import cv2
import numpy as np
from typing import Tuple, Optional


class SimpleFaceDetector:
    """Detector de caras simple usando solo OpenCV."""
    
    def __init__(self):
        """Inicializar detector."""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
    
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detecta una cara en la imagen.
        
        Args:
            image: Imagen de entrada (BGR)
        
        Returns:
            Bounding box (x, y, width, height) o None
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detectar caras
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        if len(faces) > 0:
            # Retornar la cara más grande
            faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            return tuple(faces[0])
        
        return None
    
    def extract_face(self, image: np.ndarray, size: int = 256) -> Optional[np.ndarray]:
        """
        Extrae y redimensiona una cara.
        
        Args:
            image: Imagen de entrada
            size: Tamaño de salida
        
        Returns:
            Cara extraída y redimensionada o None
        """
        face_location = self.detect_face(image)
        if face_location is None:
            return None
        
        x, y, w, h = face_location
        
        # Expandir región
        margin = 0.2
        x_expanded = max(0, int(x - w * margin))
        y_expanded = max(0, int(y - h * margin))
        w_expanded = min(image.shape[1] - x_expanded, int(w * (1 + 2 * margin)))
        h_expanded = min(image.shape[0] - y_expanded, int(h * (1 + 2 * margin)))
        
        # Extraer región
        face_region = image[y_expanded:y_expanded+h_expanded,
                           x_expanded:x_expanded+w_expanded]
        
        # Redimensionar
        face_resized = cv2.resize(face_region, (size, size))
        
        return face_resized






