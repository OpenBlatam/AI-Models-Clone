"""
Base Module
===========
Clase base para detectores y utilidades compartidas siguiendo principios SOLID y DRY
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Callable, Any, Tuple
import cv2
import numpy as np


class BaseDetector(ABC):
    """
    Clase base abstracta para detectores.
    Proporciona funcionalidad común y manejo de errores.
    """
    
    def __init__(self):
        """Initialize base detector."""
        self._models: Dict[str, Any] = {}
        self._initialized = False
    
    def _is_model_available(self, model_name: str) -> bool:
        """Check if a model is available and initialized."""
        return model_name in self._models and self._models[model_name] is not None
    
    def _safe_execute(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        """
        Execute a function safely, catching and handling errors.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result of function or None if error occurs
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log error at debug level for better debugging without exposing in production
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Error in {func.__name__}: {e}", exc_info=True)
            return None
    
    @abstractmethod
    def detect(self, image: np.ndarray) -> Optional[Any]:
        """
        Abstract method for detection/extraction.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Detection/extraction result or None
        """
        pass
    
    def get_available_models(self) -> list:
        """Get list of available model names."""
        return list(self._models.keys())
    
    def is_initialized(self) -> bool:
        """Check if detector is initialized."""
        return self._initialized


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
    
    @staticmethod
    def ensure_bounds(x: int, y: int, width: int, height: int) -> Tuple[int, int]:
        """Asegura que las coordenadas estén dentro de los límites de la imagen."""
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        return x, y


class LandmarkFormatHandler:
    """Maneja diferentes formatos de landmarks con métodos completos."""
    
    @staticmethod
    def is_valid_landmarks(landmarks: Optional[np.ndarray]) -> bool:
        """Verifica si los landmarks son válidos."""
        return landmarks is not None and len(landmarks) >= 5
    
    @staticmethod
    def get_landmark_format(landmarks: np.ndarray) -> Optional[str]:
        """Detecta el formato de landmarks."""
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return None
        
        if len(landmarks) == 106:
            return 'insightface'
        elif len(landmarks) == 68:
            return 'face_alignment'
        elif len(landmarks) == 468:
            return 'mediapipe'
        else:
            return 'unknown'
    
    @staticmethod
    def get_eye_points(landmarks: np.ndarray) -> Optional[dict]:
        """Extrae puntos de ojos según formato de landmarks."""
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return None
        
        points = {}
        
        try:
            format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
            
            if format_type == 'insightface':
                points['left_eye'] = landmarks[36:42] if len(landmarks) > 42 else landmarks[0:1]
                points['right_eye'] = landmarks[42:48] if len(landmarks) > 48 else landmarks[0:1]
            elif format_type == 'face_alignment':
                points['left_eye'] = landmarks[36:42]
                points['right_eye'] = landmarks[42:48]
            elif format_type == 'mediapipe':
                # MediaPipe usa índices diferentes
                if len(landmarks) > 468:
                    points['left_eye'] = landmarks[33:42]
                    points['right_eye'] = landmarks[263:272]
            else:
                return None
        except Exception:
            return None
        
        return points if points else None
    
    @staticmethod
    def get_nose_point(landmarks: np.ndarray) -> Optional[np.ndarray]:
        """Extrae punto de nariz según formato."""
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return None
        
        try:
            format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
            
            if format_type == 'insightface':
                return landmarks[86] if len(landmarks) > 86 else landmarks[0]
            elif format_type == 'face_alignment':
                return landmarks[30]
            elif format_type == 'mediapipe':
                return landmarks[4] if len(landmarks) > 4 else landmarks[0]
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def get_mouth_points(landmarks: np.ndarray) -> Optional[np.ndarray]:
        """Extrae puntos de boca según formato."""
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return None
        
        try:
            format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
            
            if format_type == 'insightface':
                return landmarks[48:68] if len(landmarks) > 68 else landmarks[0:1]
            elif format_type == 'face_alignment':
                return landmarks[48:68]
            elif format_type == 'mediapipe':
                return landmarks[61:68] if len(landmarks) > 68 else landmarks[0:1]
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def get_feature_region(landmarks: np.ndarray, feature: str) -> Optional[np.ndarray]:
        """Obtiene región de una característica facial específica."""
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return None
        
        try:
            if feature == 'left_eye':
                eye_points = LandmarkFormatHandler.get_eye_points(landmarks)
                return eye_points.get('left_eye') if eye_points else None
            elif feature == 'right_eye':
                eye_points = LandmarkFormatHandler.get_eye_points(landmarks)
                return eye_points.get('right_eye') if eye_points else None
            elif feature == 'nose':
                return LandmarkFormatHandler.get_nose_point(landmarks)
            elif feature == 'mouth':
                return LandmarkFormatHandler.get_mouth_points(landmarks)
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def get_feature_point(landmarks: np.ndarray, feature: str) -> Optional[np.ndarray]:
        """Obtiene punto central de una característica facial."""
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return None
        
        try:
            format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
            
            if feature == 'face_center':
                # Calcular centro facial como promedio de puntos clave
                left_eye_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'left_eye_center')
                right_eye_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'right_eye_center')
                nose_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'nose_tip')
                
                if all([left_eye_pt is not None, right_eye_pt is not None, nose_pt is not None]):
                    return (left_eye_pt + right_eye_pt + nose_pt) / 3.0
                return None
            
            elif feature == 'left_eye_center':
                left_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'left_eye')
                return np.mean(left_eye, axis=0) if left_eye is not None and len(left_eye) > 0 else None
            
            elif feature == 'right_eye_center':
                right_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'right_eye')
                return np.mean(right_eye, axis=0) if right_eye is not None and len(right_eye) > 0 else None
            
            elif feature == 'nose_tip':
                return LandmarkFormatHandler.get_nose_point(landmarks)
            
            elif feature == 'mouth_center':
                mouth = LandmarkFormatHandler.get_mouth_points(landmarks)
                return np.mean(mouth, axis=0) if mouth is not None and len(mouth) > 0 else None
            
            elif feature == 'mouth_left':
                mouth = LandmarkFormatHandler.get_mouth_points(landmarks)
                if mouth is not None and len(mouth) > 0:
                    format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
                    if format_type in ['insightface', 'face_alignment']:
                        return mouth[0] if len(mouth) > 0 else None
                return None
            
            elif feature == 'mouth_right':
                mouth = LandmarkFormatHandler.get_mouth_points(landmarks)
                if mouth is not None and len(mouth) > 0:
                    format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
                    if format_type in ['insightface', 'face_alignment']:
                        return mouth[6] if len(mouth) > 6 else mouth[-1]
                return None
            
            elif feature == 'chin':
                format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
                if format_type == 'insightface':
                    return landmarks[8] if len(landmarks) > 8 else None
                elif format_type == 'face_alignment':
                    return landmarks[8]
                elif format_type == 'mediapipe':
                    return landmarks[175] if len(landmarks) > 175 else None
        except Exception:
            pass
        
        return None








