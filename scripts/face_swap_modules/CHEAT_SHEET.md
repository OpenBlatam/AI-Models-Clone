# Cheat Sheet - Face Swap Modules

## 📋 Referencia Rápida

Guía de referencia rápida para uso común de los módulos.

---

## 🚀 Inicio Rápido

### Instalación

```bash
pip install opencv-python numpy
pip install mediapipe face-alignment  # Opcional
pip install numba  # Para optimizaciones
```

### Import Básico

```python
from face_swap_modules import (
    FaceDetector, LandmarkExtractor, FaceAnalyzer,
    ColorCorrector, BlendingEngine, QualityEnhancer,
    PostProcessor, FaceSwapPipeline
)
```

---

## 🔍 Detección y Landmarks

### Detección Simple

```python
detector = FaceDetector()
bbox = detector.detect(image)  # (x, y, width, height)
```

### Extracción de Landmarks

```python
extractor = LandmarkExtractor()
landmarks = extractor.detect(image)  # np.ndarray
```

### Análisis Facial

```python
analyzer = FaceAnalyzer()
regions = analyzer.analyze_face_regions(image, landmarks)
features = analyzer.analyze_facial_features_deep(image, landmarks)
```

---

## 🎨 Corrección de Color

### Métodos Disponibles

```python
corrector = ColorCorrector()

# Histogram matching
corrected = corrector.correct_color_histogram(source, target, mask)

# LAB color space
corrected = corrector.correct_color_lab(source, target, mask)

# Dual (recomendado)
corrected = corrector.correct_color_dual(source, target, mask)
```

---

## 🔄 Blending

### Métodos Disponibles

```python
blender = BlendingEngine()

# Multi-scale
result = blender.multi_scale_blending(source, target, mask)

# Advanced
result = blender.blend_advanced(source, target, mask)

# Ultra advanced
result = blender.blend_ultra_advanced(source, target, mask)
```

---

## ⚡ Pipeline Completo

### Uso Básico

```python
pipeline = FaceSwapPipeline(quality_mode='high')
result = pipeline.process(source, target)
```

### Modos de Calidad

```python
# Fast
pipeline = FaceSwapPipeline(quality_mode='fast')

# High (recomendado)
pipeline = FaceSwapPipeline(quality_mode='high')

# Ultra (máxima calidad)
pipeline = FaceSwapPipeline(quality_mode='ultra', use_advanced_enhancements=True)
```

---

## 🛠️ Utilidades

### LandmarkFormatHandler

```python
from face_swap_modules.base import LandmarkFormatHandler

# Detectar formato
format_type = LandmarkFormatHandler.get_landmark_format(landmarks)

# Obtener regiones
left_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'left_eye')
nose = LandmarkFormatHandler.get_feature_region(landmarks, 'nose')
mouth = LandmarkFormatHandler.get_feature_region(landmarks, 'mouth')

# Validar
is_valid = LandmarkFormatHandler.is_valid_landmarks(landmarks)
```

### ImageProcessor

```python
from face_swap_modules.base import ImageProcessor

# Máscara 3D
mask_3d = ImageProcessor.create_3d_mask(mask_2d)

# Conversiones
lab = ImageProcessor.convert_bgr_to_lab(image)
gray = ImageProcessor.convert_bgr_to_gray(image)

# Filtros
blurred = ImageProcessor.apply_gaussian_blur(image, (5, 5))
filtered = ImageProcessor.apply_bilateral_filter(image, 5, 50, 50)
```

---

## 📊 Constantes Comunes

```python
from face_swap_modules.constants import (
    LANDMARK_FORMAT_INSIGHTFACE,      # 106
    LANDMARK_FORMAT_FACE_ALIGNMENT,   # 68
    LANDMARK_FORMAT_MEDIAPIPE,        # 468
    GAUSSIAN_BLUR_KERNEL_SIZE,        # (5, 5)
    GAUSSIAN_BLUR_SIGMA,              # 0.5
)
```

---

## ⚡ Optimizaciones

### Verificar Numba

```python
from face_swap_modules.optimizations import is_numba_available

if is_numba_available():
    print("Optimizaciones activas")
```

### Funciones Optimizadas

```python
from face_swap_modules.optimizations import (
    fast_gaussian_blur_1d,
    fast_mask_blending,
    fast_histogram_matching,
)
```

---

## 🎯 Casos de Uso Comunes

### Caso 1: Detección Simple

```python
detector = FaceDetector()
bbox = detector.detect(image)
if bbox:
    x, y, w, h = bbox
    face = image[y:y+h, x:x+w]
```

### Caso 2: Pipeline Completo

```python
pipeline = FaceSwapPipeline(quality_mode='high')
result = pipeline.process(source, target)
cv2.imwrite("result.jpg", result)
```

### Caso 3: Procesamiento Personalizado

```python
detector = FaceDetector()
extractor = LandmarkExtractor()
corrector = ColorCorrector()
blender = BlendingEngine()

bbox = detector.detect(image)
landmarks = extractor.detect(image)
corrected = corrector.correct_color_dual(source, target, mask)
result = blender.blend_advanced(corrected, target, mask)
```

---

## 🔧 Comandos Útiles

### Validación

```bash
python validate_modules.py
python check_dependencies.py
python generate_report.py
```

### Tests

```bash
python -m pytest tests/
python -m pytest tests/test_base.py
python -m pytest tests/test_integration.py
```

### Benchmark

```bash
python benchmark.py
python benchmark.py -n 20 -o results.txt
```

### Demo

```bash
python demo.py source.jpg target.jpg
python demo.py source.jpg target.jpg -o output_dir
```

---

## 📚 Documentación Rápida

| Necesitas | Ver |
|-----------|-----|
| Inicio rápido | `QUICK_START.md` |
| Ejemplos | `USAGE_EXAMPLES.md` |
| Mejores prácticas | `BEST_PRACTICES.md` |
| Solución de problemas | `TROUBLESHOOTING.md` |
| Estructura completa | `COMPLETE_REFACTORED_STRUCTURE.md` |
| Validación | `FINAL_VALIDATION_REPORT.md` |

---

## 🎨 Tips Rápidos

### Rendimiento

- ✅ Instalar Numba para optimizaciones
- ✅ Usar modo 'fast' para velocidad
- ✅ Reducir resolución si es necesario

### Calidad

- ✅ Usar modo 'ultra' para máxima calidad
- ✅ Habilitar mejoras avanzadas
- ✅ Usar `blend_ultra_advanced()`

### Debugging

- ✅ Validar antes de procesar
- ✅ Guardar resultados intermedios
- ✅ Usar `validate_modules.py`

---

## ⚠️ Errores Comunes

### "No se detectaron caras"
→ Instalar mediapipe o insightface

### "No se pudieron extraer landmarks"
→ Instalar face-alignment

### "ModuleNotFoundError"
→ Verificar PYTHONPATH o ejecutar `python setup.py`

### Rendimiento lento
→ Instalar Numba: `pip install numba`

---

**Versión**: 2.1.0  
**Última actualización**: Referencia rápida







