# Mejores Prácticas - Face Swap Modules

## 📚 Guía de Mejores Prácticas

Este documento describe las mejores prácticas para usar y extender los módulos refactorizados.

---

## 🎯 Principios de Uso

### 1. Usar Clases Base Cuando Sea Apropiado

**✅ Bueno:**
```python
from face_swap_modules.base import BaseDetector

class CustomDetector(BaseDetector):
    def detect(self, image):
        # Tu lógica personalizada
        return self._safe_execute(self._custom_detect, image)
```

**❌ Evitar:**
```python
# No reinventar la rueda
class CustomDetector:
    def __init__(self):
        # Duplicar lógica de inicialización
        pass
```

### 2. Usar Utilidades Centralizadas

**✅ Bueno:**
```python
from face_swap_modules.base import LandmarkFormatHandler, ImageProcessor

# Usar utilidades centralizadas
format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
mask_3d = ImageProcessor.create_3d_mask(mask_2d)
```

**❌ Evitar:**
```python
# No duplicar lógica
if len(landmarks) == 106:
    # Lógica duplicada
elif len(landmarks) == 68:
    # Lógica duplicada
```

### 3. Manejo de Errores Consistente

**✅ Bueno:**
```python
from face_swap_modules import FaceDetector

detector = FaceDetector()
bbox = detector.detect(image)

if bbox is None:
    # Manejar caso de no detección
    print("No se detectó cara")
    return
```

**❌ Evitar:**
```python
# No asumir que siempre habrá detección
bbox = detector.detect(image)
x, y, w, h = bbox  # Puede fallar si bbox es None
```

---

## 🔧 Extensión de Módulos

### Agregar Nuevo Método de Detección

**Patrón Recomendado:**
```python
from face_swap_modules.base import BaseDetector
from typing import Optional, Tuple
import numpy as np

class FaceDetector(BaseDetector):
    def _detect_with_nuevo_metodo(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Implementa nuevo método de detección."""
        def _detect():
            # Tu lógica de detección aquí
            # Retorna: (x, y, width, height) o None
            return bbox
        
        return self._safe_execute(_detect)
    
    # Agregar a la lista de métodos
    DETECTION_METHODS = ['insightface', 'retinaface', 'mediapipe', 'opencv', 'nuevo_metodo']
```

### Agregar Nuevo Formato de Landmarks

**Patrón Recomendado:**
```python
# En base.py - LandmarkFormatHandler
NUEVO_FORMATO_200 = 200

NUEVO_FORMATO_INDICES = {
    'left_eye': (50, 60),
    'right_eye': (70, 80),
    'nose': (90, 100),
    'mouth': (110, 120),
    # ... más índices
}

# Actualizar get_landmark_format()
@staticmethod
def get_landmark_format(landmarks: np.ndarray) -> Optional[int]:
    if len(landmarks) == 106:
        return 106
    elif len(landmarks) == 68:
        return 68
    elif len(landmarks) == 468:
        return 468
    elif len(landmarks) == 200:  # NUEVO
        return 200
    return None
```

---

## 📝 Convenciones de Código

### Nomenclatura

**✅ Bueno:**
```python
# Constantes en MAYÚSCULAS
LANDMARK_FORMAT_INSIGHTFACE = 106
GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)

# Métodos en snake_case
def detect_face_regions():
    pass

# Clases en PascalCase
class FaceDetector:
    pass
```

**❌ Evitar:**
```python
# Magic numbers
if len(landmarks) == 106:  # ¿Qué significa 106?

# Nombres ambiguos
def process():  # ¿Qué procesa?
    pass
```

### Type Hints

**✅ Bueno:**
```python
from typing import Optional, Tuple
import numpy as np

def detect_face(image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """Detecta cara en imagen."""
    pass
```

**❌ Evitar:**
```python
# Sin type hints
def detect_face(image):
    pass
```

### Docstrings

**✅ Bueno:**
```python
def correct_color_dual(
    source: np.ndarray, 
    target: np.ndarray, 
    mask: np.ndarray
) -> np.ndarray:
    """
    Corrige color usando método dual (histogram + LAB).
    
    Args:
        source: Imagen fuente
        target: Imagen objetivo
        mask: Máscara de blending
    
    Returns:
        Imagen corregida
    """
    pass
```

**❌ Evitar:**
```python
# Sin documentación
def correct_color_dual(source, target, mask):
    pass
```

---

## 🚀 Optimización de Rendimiento

### Usar Numba Cuando Sea Posible

**✅ Bueno:**
```python
from face_swap_modules.optimizations import (
    fast_gaussian_blur_1d,
    fast_mask_blending
)

# Usar funciones optimizadas
blurred = fast_gaussian_blur_1d(image, sigma=1.0)
blended = fast_mask_blending(source, target, mask)
```

### Evitar Operaciones Innecesarias

**✅ Bueno:**
```python
# Validar antes de procesar
if LandmarkFormatHandler.is_valid_landmarks(landmarks):
    regions = analyzer.analyze_face_regions(image, landmarks)
```

**❌ Evitar:**
```python
# Procesar sin validar
regions = analyzer.analyze_face_regions(image, landmarks)  # Puede fallar
```

---

## 🧪 Testing

### Tests Unitarios

**✅ Bueno:**
```python
import unittest
from face_swap_modules.base import LandmarkFormatHandler
import numpy as np

class TestLandmarkFormatHandler(unittest.TestCase):
    def test_get_landmark_format(self):
        landmarks = np.random.rand(106, 2)
        format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
        self.assertEqual(format_type, 106)
```

### Tests de Integración

**✅ Bueno:**
```python
def test_pipeline_integration(self):
    pipeline = FaceSwapPipeline(quality_mode='high')
    result = pipeline.process(source_image, target_image)
    self.assertIsNotNone(result)
    self.assertEqual(result.shape, target_image.shape)
```

---

## 📚 Documentación

### Documentar Cambios

**✅ Bueno:**
```python
def nuevo_metodo(self, param: int) -> str:
    """
    Descripción clara del método.
    
    Args:
        param: Descripción del parámetro
    
    Returns:
        Descripción del retorno
    
    Example:
        >>> detector = FaceDetector()
        >>> result = detector.nuevo_metodo(42)
        >>> print(result)
    """
    pass
```

### Actualizar Changelog

**✅ Bueno:**
```markdown
## [2.2.0] - 2024-12-XX

### ✨ Agregado
- Nuevo método `nuevo_metodo()` en `FaceDetector`
- Soporte para formato de landmarks de 200 puntos
```

---

## 🔒 Seguridad y Robustez

### Validación de Entradas

**✅ Bueno:**
```python
def process_image(image: np.ndarray) -> np.ndarray:
    """Procesa imagen con validación."""
    if image is None:
        raise ValueError("Imagen no puede ser None")
    if len(image.shape) != 3:
        raise ValueError("Imagen debe ser 3D (H, W, C)")
    # ... procesamiento
```

### Manejo de Errores

**✅ Bueno:**
```python
try:
    result = pipeline.process(source, target)
except ValueError as e:
    print(f"Error de validación: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
    raise
```

---

## 🎨 Estilo de Código

### Formato

**✅ Bueno:**
```python
# Usar formateador automático (black, autopep8)
# Líneas máximo 88-100 caracteres
# 4 espacios de indentación
```

### Imports

**✅ Bueno:**
```python
# Imports estándar primero
import sys
from pathlib import Path

# Imports de terceros
import numpy as np
import cv2

# Imports locales
from face_swap_modules import FaceDetector
from face_swap_modules.base import LandmarkFormatHandler
```

---

## ✅ Checklist de Mejores Prácticas

### Al Escribir Código
- [ ] Usar clases base cuando sea apropiado
- [ ] Usar utilidades centralizadas
- [ ] Agregar type hints
- [ ] Agregar docstrings
- [ ] Validar entradas
- [ ] Manejar errores apropiadamente

### Al Extender Funcionalidad
- [ ] Seguir patrones existentes
- [ ] Mantener compatibilidad hacia atrás
- [ ] Agregar tests
- [ ] Actualizar documentación
- [ ] Actualizar changelog

### Al Refactorizar
- [ ] Mantener SRP
- [ ] Eliminar duplicación (DRY)
- [ ] Mejorar legibilidad
- [ ] No sobre-ingeniería
- [ ] Actualizar documentación

---

## 📖 Recursos Adicionales

- **Guía de inicio rápido**: `QUICK_START.md`
- **Ejemplos completos**: `USAGE_EXAMPLES.md`
- **Guía de migración**: `MIGRATION_GUIDE.md`
- **Estructura completa**: `COMPLETE_REFACTORED_STRUCTURE.md`

---

**Última actualización**: v2.1.0








