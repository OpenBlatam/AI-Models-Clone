"""
Utils Module
============
Utilidades compartidas para todos los módulos
"""

import cv2
import numpy as np
from typing import Tuple, Optional


class ImageProcessor:
    """Utilidades para procesamiento de imágenes."""
    
    @staticmethod
    def create_3d_mask(mask: np.ndarray, channels: int = 3) -> np.ndarray:
        """Crea máscara 3D desde máscara 2D."""
        return np.stack([mask] * channels, axis=2)
    
    @staticmethod
    def convert_to_uint8(mask: np.ndarray) -> np.ndarray:
        """Convierte máscara float a uint8."""
        return (mask * 255).astype(np.uint8)
    
    @staticmethod
    def normalize_mask(mask: np.ndarray) -> np.ndarray:
        """Normaliza máscara a rango [0, 1]."""
        if mask.max() > 1.0:
            return mask / 255.0
        return mask
    
    @staticmethod
    def apply_gaussian_blur(image: np.ndarray, kernel_size: Tuple[int, int], 
                           sigma: float = 0) -> np.ndarray:
        """Aplica blur gaussiano."""
        return cv2.GaussianBlur(image, kernel_size, sigma)
    
    @staticmethod
    def apply_bilateral_filter(image: np.ndarray, d: int, sigma_color: float,
                              sigma_space: float) -> np.ndarray:
        """Aplica filtro bilateral."""
        return cv2.bilateralFilter(image, d, sigma_color, sigma_space)
    
    @staticmethod
    def convert_bgr_to_lab(image: np.ndarray) -> np.ndarray:
        """Convierte imagen BGR a LAB."""
        return cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    @staticmethod
    def convert_lab_to_bgr(image: np.ndarray) -> np.ndarray:
        """Convierte imagen LAB a BGR."""
        return cv2.cvtColor(image, cv2.COLOR_LAB2BGR)
    
    @staticmethod
    def convert_bgr_to_gray(image: np.ndarray) -> np.ndarray:
        """Convierte imagen BGR a escala de grises."""
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    @staticmethod
    def clip_image(image: np.ndarray, min_val: float = 0, 
                  max_val: float = 255) -> np.ndarray:
        """Recorta valores de imagen al rango especificado."""
        return np.clip(image, min_val, max_val).astype(np.uint8)


class LandmarkFormatHandler:
    """Maneja diferentes formatos de landmarks."""
    
    @staticmethod
    def get_eye_points(landmarks: np.ndarray) -> Optional[dict]:
        """Extrae puntos de ojos según formato de landmarks."""
        if landmarks is None or len(landmarks) < 5:
            return None
        
        points = {}
        
        try:
            if len(landmarks) == 106:  # InsightFace
                points['left_eye'] = landmarks[36:42] if len(landmarks) > 42 else landmarks[0:1]
                points['right_eye'] = landmarks[42:48] if len(landmarks) > 48 else landmarks[0:1]
            elif len(landmarks) == 68:  # face-alignment
                points['left_eye'] = landmarks[36:42]
                points['right_eye'] = landmarks[42:48]
            else:
                return None
        except:
            return None
        
        return points
    
    @staticmethod
    def get_nose_point(landmarks: np.ndarray) -> Optional[np.ndarray]:
        """Extrae punto de nariz según formato."""
        if landmarks is None or len(landmarks) < 5:
            return None
        
        try:
            if len(landmarks) == 106:
                return landmarks[86] if len(landmarks) > 86 else landmarks[0]
            elif len(landmarks) == 68:
                return landmarks[30]
        except:
            pass
        
        return None
    
    @staticmethod
    def get_mouth_points(landmarks: np.ndarray) -> Optional[np.ndarray]:
        """Extrae puntos de boca según formato."""
        if landmarks is None or len(landmarks) < 5:
            return None
        
        try:
            if len(landmarks) == 106:
                return landmarks[48:68] if len(landmarks) > 68 else landmarks[0:1]
            elif len(landmarks) == 68:
                return landmarks[48:68]
        except:
            pass
        
        return None








