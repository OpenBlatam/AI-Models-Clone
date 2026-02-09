"""
DeepSeek Face Swap Enhancer - Versión Refactorizada
====================================================
Versión refactorizada usando módulos separados.

Este script mantiene compatibilidad con el original mientras usa la nueva estructura modular.
"""

from deepseek_enhancer import DeepSeekFaceSwapEnhancer

# Re-exportar para compatibilidad
__all__ = ['DeepSeekFaceSwapEnhancer']

# Ejemplo de uso
if __name__ == "__main__":
    import cv2
    import numpy as np
    
    # Inicializar enhancer
    # NOTA: La API key debe configurarse como variable de entorno DEEPSEEK_API_KEY
    # o pasarse como parámetro. NO hardcodear en el código.
    enhancer = DeepSeekFaceSwapEnhancer(
        api_key=None,  # Usará variable de entorno DEEPSEEK_API_KEY
        use_pipeline=True,
        use_full_pipeline=True
    )
    
    # Ejemplo de uso
    # result = cv2.imread("result.jpg")
    # source = cv2.imread("source.jpg")
    # target = cv2.imread("target.jpg")
    # 
    # enhanced = enhancer.enhance(result, source, target)
    # cv2.imwrite("enhanced.jpg", enhanced)
    
    print("✅ DeepSeek Face Swap Enhancer (Refactorizado) listo para usar")






