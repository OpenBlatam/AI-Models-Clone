"""
Enhancement Pipeline
=====================
Gestiona el pipeline de mejoras de forma modular y organizada por categorías.
"""

import numpy as np
import inspect
from typing import List
from .enhancement_step import EnhancementStep


class EnhancementPipeline:
    """Gestiona el pipeline de mejoras de forma modular y organizada por categorías."""
    
    def __init__(self, enhancer_instance, use_full_pipeline: bool = True):
        """
        Inicializa el pipeline de mejoras.
        
        Args:
            enhancer_instance: Instancia de DeepSeekFaceSwapEnhancer
            use_full_pipeline: Si True, incluye todos los pasos. Si False, solo pasos esenciales.
        """
        self.enhancer = enhancer_instance
        self.steps: List[EnhancementStep] = []
        self.use_full_pipeline = use_full_pipeline
        self._setup_pipeline()
    
    def _setup_pipeline(self):
        """Configura todos los pasos del pipeline organizados por categorías."""
        self.steps = []
        
        # ============================================
        # CATEGORÍA 1: MEJORAS BÁSICAS ESENCIALES
        # ============================================
        self.steps.extend([
            EnhancementStep('_improve_color_matching'),
            EnhancementStep('_improve_lighting'),
            EnhancementStep('_improve_blending'),
            EnhancementStep('_improve_edge_seamless'),
        ])
        
        if self.use_full_pipeline:
            # Importar configuración completa del pipeline
            # Nota: En una refactorización completa, esto se movería a un archivo de configuración
            self._setup_full_pipeline()
    
    def _setup_full_pipeline(self):
        """
        Configura el pipeline completo con todas las categorías.
        Nota: Esta es una versión simplificada. El archivo original tiene muchas más categorías.
        """
        # Categoría 2: Preservación de textura
        self.steps.extend([
            EnhancementStep('_preserve_multi_scale_texture'),
            EnhancementStep('_enhance_skin_texture'),
        ])
        
        # Categoría 3: Corrección de color
        self.steps.extend([
            EnhancementStep('_color_consistency_improvement'),
            EnhancementStep('_professional_color_grading'),
        ])
        
        # Categoría 4: Iluminación
        self.steps.extend([
            EnhancementStep('_intelligent_lighting_adjustment'),
            EnhancementStep('_local_tone_mapping', requires_lib='skimage'),
        ])
        
        # Categoría 5: Blending
        self.steps.extend([
            EnhancementStep('_poisson_blending', requires_lib='scipy'),
            EnhancementStep('_ultra_advanced_blending_refinement'),
        ])
        
        # Nota: El archivo original tiene muchas más categorías y pasos.
        # En una refactorización completa, estos se organizarían en módulos separados.
    
    def execute(
        self,
        result: np.ndarray,
        source: np.ndarray,
        target: np.ndarray
    ) -> np.ndarray:
        """
        Ejecuta todos los pasos habilitados del pipeline.
        
        Args:
            result: Imagen resultante del face swap
            source: Imagen fuente
            target: Imagen objetivo
        
        Returns:
            Imagen mejorada
        """
        enhanced = result.copy()
        
        for step in self.steps:
            if step.can_run():
                try:
                    method = getattr(self.enhancer, step.method_name, None)
                    if method is None:
                        continue
                    
                    sig = inspect.signature(method)
                    params = list(sig.parameters.keys())
                    
                    # Remover 'self' de los parámetros
                    if 'self' in params:
                        params.remove('self')
                    
                    # Determinar qué parámetros pasar basado en la firma del método
                    if len(params) == 0:
                        continue
                    elif len(params) == 1:
                        enhanced = method(enhanced)
                    elif len(params) == 2:
                        try:
                            enhanced = method(enhanced, target)
                        except TypeError:
                            try:
                                enhanced = method(enhanced, source)
                            except TypeError:
                                enhanced = method(enhanced, target)
                    elif len(params) == 3:
                        if params[0] in ['result', 'image', 'img']:
                            enhanced = method(enhanced, source, target)
                        elif params[0] == 'source':
                            if 'mask' in params:
                                h, w = enhanced.shape[:2]
                                mask = np.ones((h, w), dtype=np.uint8) * 255
                                enhanced = method(source, target, mask)
                            else:
                                enhanced = method(source, target, enhanced)
                        else:
                            enhanced = method(enhanced, source, target)
                    else:
                        enhanced = method(enhanced, source, target)
                        
                except Exception as e:
                    # Continuar con el siguiente paso si hay error
                    continue
        
        return enhanced
    
    def get_enabled_steps_count(self) -> int:
        """Retorna el número de pasos habilitados."""
        return sum(1 for step in self.steps if step.can_run())
    
    def get_total_steps_count(self) -> int:
        """Retorna el número total de pasos configurados."""
        return len(self.steps)
    
    def enable_category(self, category_name: str):
        """Habilita todos los pasos de una categoría específica."""
        # Esta funcionalidad se puede expandir si se agregan tags a EnhancementStep
        pass
    
    def disable_category(self, category_name: str):
        """Deshabilita todos los pasos de una categoría específica."""
        # Esta funcionalidad se puede expandir si se agregan tags a EnhancementStep
        pass






