"""
DeepSeek Face Swap Enhancer
============================
Mejora los resultados de face swap usando análisis de DeepSeek y técnicas avanzadas.

Nota: Este módulo actúa como wrapper del archivo original para mantener compatibilidad
mientras se refactoriza gradualmente.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np

# Importar el módulo original para mantener compatibilidad
# En una refactorización completa, los métodos se moverían aquí
try:
    # Intentar importar desde el módulo original
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from deepseek_face_swap_enhancer import DeepSeekFaceSwapEnhancer as OriginalEnhancer
    ORIGINAL_AVAILABLE = True
except ImportError:
    ORIGINAL_AVAILABLE = False
    OriginalEnhancer = None

from .enhancement_pipeline import EnhancementPipeline
from .deepseek_api import DeepSeekAPI


class DeepSeekFaceSwapEnhancer:
    """
    Mejora los resultados de face swap usando análisis de DeepSeek y técnicas avanzadas.
    
    Esta es una versión refactorizada que usa el módulo original internamente
    mientras se migra gradualmente a la nueva estructura.
    """
    
    def __init__(
        self,
        api_key: str = "sk-051c14b97c2a4526a0c3c98be47f17cb",
        use_pipeline: bool = True,
        use_full_pipeline: bool = True
    ):
        """
        Inicializa el enhancer con la API key de DeepSeek.
        
        Args:
            api_key: API key de DeepSeek
            use_pipeline: Si True, usa el pipeline modular refactorizado
            use_full_pipeline: Si True, incluye todos los pasos de mejora. Si False, solo pasos esenciales.
        """
        self.api_key = api_key
        self.use_pipeline = use_pipeline
        self.use_full_pipeline = use_full_pipeline
        
        # Inicializar API client
        self.api_client = DeepSeekAPI(api_key=api_key)
        
        # Inicializar enhancer original para métodos de mejora
        if ORIGINAL_AVAILABLE:
            self._original_enhancer = OriginalEnhancer(
                api_key=api_key,
                use_pipeline=False,  # Usamos nuestro pipeline
                use_full_pipeline=use_full_pipeline
            )
        else:
            self._original_enhancer = None
            print("⚠ Advertencia: Módulo original no disponible. Algunas funciones pueden no estar disponibles.")
        
        # Inicializar pipeline refactorizado
        if use_pipeline:
            self.pipeline = EnhancementPipeline(self, use_full_pipeline=use_full_pipeline)
        else:
            self.pipeline = None
    
    def analyze_face_swap_quality(
        self,
        result_image: np.ndarray,
        source_image: np.ndarray,
        target_image: np.ndarray
    ) -> Dict[str, Any]:
        """
        Analiza la calidad del face swap usando DeepSeek.
        
        Args:
            result_image: Imagen resultante del face swap
            source_image: Imagen fuente
            target_image: Imagen objetivo
        
        Returns:
            Diccionario con análisis y sugerencias
        """
        return self.api_client.analyze_face_swap_quality(
            result_image, source_image, target_image
        )
    
    def apply_deepseek_improvements(
        self,
        result_image: np.ndarray,
        source_image: np.ndarray,
        target_image: np.ndarray,
        analysis: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """
        Aplica mejoras basadas en el análisis de DeepSeek.
        
        Args:
            result_image: Imagen resultante del face swap
            source_image: Imagen fuente
            target_image: Imagen objetivo
            analysis: Análisis de DeepSeek (si None, se analiza primero)
        
        Returns:
            Imagen mejorada
        """
        if self._original_enhancer:
            return self._original_enhancer.apply_deepseek_improvements(
                result_image, source_image, target_image, analysis
            )
        else:
            # Fallback básico si el módulo original no está disponible
            return result_image
    
    def enhance(
        self,
        result_image: np.ndarray,
        source_image: np.ndarray,
        target_image: np.ndarray
    ) -> np.ndarray:
        """
        Aplica todas las mejoras usando el pipeline.
        
        Args:
            result_image: Imagen resultante del face swap
            source_image: Imagen fuente
            target_image: Imagen objetivo
        
        Returns:
            Imagen mejorada
        """
        if self.pipeline:
            return self.pipeline.execute(result_image, source_image, target_image)
        else:
            # Usar método original si no hay pipeline
            if self._original_enhancer:
                return self._original_enhancer.apply_deepseek_improvements(
                    result_image, source_image, target_image
                )
            return result_image
    
    def __getattr__(self, name: str):
        """
        Delega métodos no implementados al enhancer original.
        Esto permite usar todos los métodos del módulo original mientras se refactoriza.
        """
        if self._original_enhancer and hasattr(self._original_enhancer, name):
            return getattr(self._original_enhancer, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")






