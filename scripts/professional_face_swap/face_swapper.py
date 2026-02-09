"""
Professional Face Swap
=======================
Clase principal para face swap profesional usando módulos refactorizados.
"""

import sys
import os
from pathlib import Path

# Importar el archivo original como fallback para métodos complejos
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from face_swap_professional import ProfessionalFaceSwap as OriginalProfessionalFaceSwap
    ORIGINAL_AVAILABLE = True
except ImportError:
    ORIGINAL_AVAILABLE = False
    OriginalProfessionalFaceSwap = None

from .detector import ProfessionalFaceDetector
from .landmark_extractor import ProfessionalLandmarkExtractor
from .lib_availability import check_library_availability


class ProfessionalFaceSwap:
    """
    Face swap profesional refactorizado.
    
    Esta clase usa módulos refactorizados para detección y landmarks,
    y delega métodos complejos al archivo original para mantener compatibilidad.
    """
    
    def __init__(self):
        """Inicializar face swap profesional."""
        self.lib_availability = check_library_availability()
        self.detector = ProfessionalFaceDetector()
        self.landmark_extractor = ProfessionalLandmarkExtractor(detector=self.detector)
        
        # Crear instancia del original para métodos complejos
        if ORIGINAL_AVAILABLE:
            self._original = OriginalProfessionalFaceSwap()
        else:
            self._original = None
            print("⚠ Archivo original no disponible, funcionalidad limitada")
    
    def detect_face(self, image):
        """Detecta cara usando el detector refactorizado."""
        return self.detector.detect_face(image)
    
    def get_face_landmarks(self, image):
        """Obtiene landmarks usando el extractor refactorizado."""
        return self.landmark_extractor.get_face_landmarks(image)
    
    def swap_faces_professional(self, source_image, target_image):
        """
        Face swap profesional.
        
        Delega al método original para mantener toda la funcionalidad avanzada.
        """
        if self._original:
            return self._original.swap_faces_professional(source_image, target_image)
        else:
            # Fallback básico si el original no está disponible
            raise NotImplementedError(
                "swap_faces_professional requiere el archivo original. "
                "Asegúrate de que face_swap_professional.py esté disponible."
            )
    
    def __getattr__(self, name):
        """
        Delega métodos no implementados al original.
        
        Esto permite usar todos los métodos del original mientras
        se refactorizan gradualmente.
        """
        if self._original and hasattr(self._original, name):
            return getattr(self._original, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")






