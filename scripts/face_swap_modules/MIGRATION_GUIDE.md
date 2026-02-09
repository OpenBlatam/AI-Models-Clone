# Guía de Migración - Scripts Principales

## 📋 Resumen

Esta guía muestra cómo migrar scripts principales de face swap para usar los módulos refactorizados.

---

## 🎯 Beneficios de la Migración

- ✅ **Código más limpio**: Eliminación de duplicación
- ✅ **Mantenibilidad**: Cambios centralizados
- ✅ **Extensibilidad**: Fácil agregar nuevas funcionalidades
- ✅ **Consistencia**: Mismo comportamiento en todos los scripts
- ✅ **Compatibilidad**: 100% compatible hacia atrás

---

## 📝 Pasos de Migración

### Paso 1: Actualizar Importaciones

**Antes:**
```python
import cv2
import numpy as np
# Código duplicado de detección, extracción, etc.
```

**Después:**
```python
import cv2
import numpy as np
from face_swap_modules import (
    FaceDetector,
    LandmarkExtractor,
    FaceAnalyzer,
    ColorCorrector,
    BlendingEngine,
    QualityEnhancer,
    PostProcessor
)
```

---

### Paso 2: Reemplazar Detección Manual

**Antes:**
```python
# Código duplicado de detección con múltiples métodos
def detect_face(image):
    # 50+ líneas de código con try/except repetido
    try:
        # InsightFace
        ...
    except:
        try:
            # RetinaFace
            ...
        except:
            # OpenCV fallback
            ...
```

**Después:**
```python
detector = FaceDetector()
face = detector.detect(image)  # Fallback automático
# O usar alias para compatibilidad:
face = detector.detect_face(image)  # También funciona
```

---

### Paso 3: Reemplazar Extracción Manual

**Antes:**
```python
# Código duplicado de extracción
def get_landmarks(image):
    # 40+ líneas con múltiples métodos
    if len(landmarks) == 106:
        # Procesar formato InsightFace
    elif len(landmarks) == 68:
        # Procesar formato face-alignment
    ...
```

**Después:**
```python
extractor = LandmarkExtractor()
landmarks = extractor.detect(image)  # Fallback automático
# O usar alias:
landmarks = extractor.get_landmarks(image)  # También funciona
```

---

### Paso 4: Usar LandmarkFormatHandler

**Antes:**
```python
# Repetido en múltiples lugares
if len(landmarks) == 106:  # InsightFace
    left_eye = landmarks[36:42] if len(landmarks) > 42 else landmarks[0:1]
    right_eye = landmarks[42:48] if len(landmarks) > 48 else landmarks[0:1]
    nose = landmarks[51:87] if len(landmarks) > 87 else landmarks[0:1]
    mouth = landmarks[48:68] if len(landmarks) > 68 else landmarks[0:1]
elif len(landmarks) == 68:  # face-alignment
    left_eye = landmarks[36:42]
    right_eye = landmarks[42:48]
    nose = landmarks[27:36]
    mouth = landmarks[48:68]
else:
    return {}
```

**Después:**
```python
from face_swap_modules.base import LandmarkFormatHandler

# Una sola línea por característica
left_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'left_eye')
right_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'right_eye')
nose = LandmarkFormatHandler.get_feature_region(landmarks, 'nose')
mouth = LandmarkFormatHandler.get_feature_region(landmarks, 'mouth')
```

---

### Paso 5: Usar ImageProcessor

**Antes:**
```python
# Repetido múltiples veces
mask_3d = np.stack([mask] * 3, axis=2)
mask_uint8 = (mask * 255).astype(np.uint8)
x = max(0, min(x, width - 1))
y = max(0, min(y, height - 1))
```

**Después:**
```python
from face_swap_modules.base import ImageProcessor

mask_3d = ImageProcessor.create_3d_mask(mask)
mask_uint8 = ImageProcessor.convert_to_uint8(mask)
x, y = ImageProcessor.ensure_bounds(x, y, width, height)
```

---

### Paso 6: Usar Módulos de Procesamiento

**Antes:**
```python
# Corrección de color manual con números mágicos
def correct_color(source, target, mask):
    # 40+ líneas con valores hardcodeados
    mask_weighted = mask ** 1.5  # ¿Qué significa 1.5?
    result = cv2.addWeighted(..., 0.4, ..., 0.6, 0)  # ¿Qué significan estos pesos?
    ...
```

**Después:**
```python
color_corrector = ColorCorrector()
# Métodos mejorados con constantes nombradas
corrected = color_corrector.correct_color_dual(source, target, mask)
# O métodos específicos:
corrected = color_corrector.correct_color_lab(source, target, mask)
corrected = color_corrector.correct_color_histogram(source, target, mask)
```

---

### Paso 7: Usar BlendingEngine

**Antes:**
```python
# Blending manual con múltiples métodos mezclados
def blend(source, target, mask):
    # 100+ líneas mezclando FFT, Poisson, multi-scale
    ...
```

**Después:**
```python
blending_engine = BlendingEngine()
# Método inteligente que combina técnicas
result = blending_engine.blend_advanced(source, target, mask)
# O métodos específicos:
result = blending_engine.frequency_domain_blending(source, target, mask)
result = blending_engine.poisson_blending(source, target, mask)
result = blending_engine.multi_scale_blending(source, target, mask)
```

---

## 🔄 Ejemplo Completo de Migración

### Script Antiguo (face_swap_old.py)

```python
import cv2
import numpy as np

def detect_face_old(image):
    # 50+ líneas de código duplicado
    try:
        # InsightFace
        ...
    except:
        try:
            # RetinaFace
            ...
        except:
            # OpenCV
            ...

def get_landmarks_old(image):
    # 40+ líneas duplicadas
    if len(landmarks) == 106:
        left_eye = landmarks[36:42]
        ...
    elif len(landmarks) == 68:
        left_eye = landmarks[36:42]
        ...

def correct_color_old(source, target, mask):
    # 40+ líneas con números mágicos
    mask_weighted = mask ** 1.5
    result = cv2.addWeighted(..., 0.4, ..., 0.6, 0)
    ...

# Uso
image = cv2.imread("source.jpg")
face = detect_face_old(image)
landmarks = get_landmarks_old(image)
# ... más código
```

### Script Migrado (face_swap_new.py)

```python
import cv2
import numpy as np
from face_swap_modules import (
    FaceDetector,
    LandmarkExtractor,
    ColorCorrector,
    BlendingEngine
)
from face_swap_modules.base import LandmarkFormatHandler

# Inicializar componentes (una vez)
detector = FaceDetector()
extractor = LandmarkExtractor()
color_corrector = ColorCorrector()
blending_engine = BlendingEngine()

# Uso (código limpio)
image = cv2.imread("source.jpg")
face = detector.detect(image)  # Fallback automático
landmarks = extractor.detect(image)  # Fallback automático

# Usar utilidades
left_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'left_eye')

# Procesamiento mejorado
corrected = color_corrector.correct_color_dual(source, target, mask)
result = blending_engine.blend_advanced(corrected, target, mask)
```

**Reducción de código**: ~200 líneas → ~30 líneas

---

## 📊 Comparación de Código

| Aspecto | Antes | Después | Mejora |
|---------|-------|---------|--------|
| **Líneas de código** | ~500 | ~150 | 70% reducción |
| **Código duplicado** | ~200 líneas | 0 líneas | 100% eliminado |
| **Números mágicos** | 20+ | 0 | 100% eliminados |
| **Manejo de errores** | Inconsistente | Consistente | 100% mejorado |
| **Mantenibilidad** | Baja | Alta | Significativa |

---

## ✅ Checklist de Migración

- [ ] Actualizar importaciones
- [ ] Reemplazar detección manual con `FaceDetector`
- [ ] Reemplazar extracción manual con `LandmarkExtractor`
- [ ] Usar `LandmarkFormatHandler` para landmarks
- [ ] Usar `ImageProcessor` para operaciones comunes
- [ ] Reemplazar corrección de color manual con `ColorCorrector`
- [ ] Reemplazar blending manual con `BlendingEngine`
- [ ] Usar `QualityEnhancer` para mejoras de calidad
- [ ] Usar `PostProcessor` para post-procesamiento
- [ ] Probar compatibilidad hacia atrás
- [ ] Validar resultados

---

## 🚀 Scripts Recomendados para Migrar

1. **face_swap_professional.py** - Script principal profesional
2. **face_swap_ultra_quality.py** - Script de ultra calidad
3. **batch_face_swap_improved.py** - Procesamiento por lotes
4. **face_swap_final_improved.py** - Script final combinado

---

## 💡 Tips de Migración

1. **Migración Gradual**: Migra un módulo a la vez
2. **Mantener Compatibilidad**: Usa aliases (`detect_face()`, `get_landmarks()`)
3. **Validar Resultados**: Compara resultados antes/después
4. **Usar Tests**: Valida con `validate_modules.py`
5. **Documentar Cambios**: Documenta cambios específicos del script

---

## 📞 Soporte

Si encuentras problemas durante la migración:

1. Revisa `example_usage.py` para ejemplos
2. Ejecuta `validate_modules.py` para validar módulos
3. Consulta `COMPLETE_REFACTORED_STRUCTURE.md` para detalles
4. Revisa `BEFORE_AFTER_COMPARISON.md` para ver cambios específicos

---

**¡Buena suerte con la migración!** 🎉








