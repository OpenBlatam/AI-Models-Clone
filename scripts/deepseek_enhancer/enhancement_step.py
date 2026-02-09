"""
Enhancement Step
================
Representa un paso de mejora con su configuración.
"""

from typing import Optional
from .lib_availability import SCIPY_AVAILABLE, SKIMAGE_AVAILABLE, PIL_AVAILABLE, NUMBA_AVAILABLE


class EnhancementStep:
    """Representa un paso de mejora con su configuración."""
    
    def __init__(
        self,
        method_name: str,
        enabled: bool = True,
        requires_lib: Optional[str] = None,
        category: Optional[str] = None
    ):
        """
        Inicializa un paso de mejora.
        
        Args:
            method_name: Nombre del método a ejecutar
            enabled: Si el paso está habilitado
            requires_lib: Librería requerida ('scipy', 'skimage', 'pil', 'numba')
            category: Categoría del paso (para organización)
        """
        self.method_name = method_name
        self.enabled = enabled
        self.requires_lib = requires_lib  # 'scipy', 'skimage', 'pil', 'numba'
        self.category = category  # Categoría para organización
    
    def can_run(self) -> bool:
        """
        Verifica si el paso puede ejecutarse.
        
        Returns:
            True si el paso puede ejecutarse
        """
        if not self.enabled:
            return False
        if self.requires_lib == 'scipy' and not SCIPY_AVAILABLE:
            return False
        if self.requires_lib == 'skimage' and not SKIMAGE_AVAILABLE:
            return False
        if self.requires_lib == 'pil' and not PIL_AVAILABLE:
            return False
        if self.requires_lib == 'numba' and not NUMBA_AVAILABLE:
            return False
        return True
    
    def __repr__(self) -> str:
        """Representación del paso para debugging."""
        lib_str = f", lib={self.requires_lib}" if self.requires_lib else ""
        cat_str = f", cat={self.category}" if self.category else ""
        enabled_str = "✓" if self.enabled else "✗"
        return f"<EnhancementStep: {enabled_str} {self.method_name}{lib_str}{cat_str}>"






