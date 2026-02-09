# Guía de Inicio Rápido - Face Swap Modules

## 🚀 Inicio Rápido en 5 Minutos

Esta guía te ayudará a comenzar rápidamente con los módulos refactorizados.

---

## 📦 Instalación Rápida

```bash
# Dependencias básicas (requeridas)
pip install opencv-python numpy

# Dependencias opcionales (recomendadas para mejor calidad)
pip install mediapipe face-alignment insightface

# Optimizaciones (opcional, para máximo rendimiento)
pip install numba

# Librerías avanzadas (opcional, para mejoras ultra-avanzadas)
pip install scikit-image scipy
```

---

## 🎯 Uso Básico (3 Líneas)

```python
from face_swap_modules import FaceDetector, LandmarkExtractor

detector = FaceDetector()
bbox = detector.detect(image)  # Detecta cara automáticamente

extractor = LandmarkExtractor()
landmarks = extractor.detect(image)  # Extrae landmarks automáticamente
```

---

## 🔥 Pipeline Completo (Ejemplo Mínimo)

```python
import cv2
from face_swap_modules import FaceSwapPipeline

# Cargar imágenes
source = cv2.imread("source.jpg")
target = cv2.imread("target.jpg")

# Crear pipeline
pipeline = FaceSwapPipeline(quality_mode='high')

# Procesar
result = pipeline.process(source, target)

# Guardar
cv2.imwrite("result.jpg", result)
```

---

## 📋 Ejemplos por Caso de Uso

### 1. Detección Simple

```python
from face_swap_modules import FaceDetector
import cv2

image = cv2.imread("photo.jpg")
detector = FaceDetector()
bbox = detector.detect(image)  # (x, y, width, height)

if bbox:
    x, y, w, h = bbox
    face = image[y:y+h, x:x+w]
    cv2.imwrite("face.jpg", face)
```

### 2. Análisis Facial

```python
from face_swap_modules import FaceDetector, LandmarkExtractor, FaceAnalyzer
import cv2

image = cv2.imread("photo.jpg")

detector = FaceDetector()
extractor = LandmarkExtractor()
analyzer = FaceAnalyzer()

bbox = detector.detect(image)
landmarks = extractor.detect(image)

# Analizar características
features = analyzer.analyze_facial_features_deep(image, landmarks)
expression = analyzer.analyze_facial_expression(landmarks)
symmetry = analyzer.analyze_facial_symmetry(image, landmarks)

print(f"Tono de piel: {features.get('skin_tone')}")
print(f"Apertura de ojos: {expression.get('eye_openness')}")
```

### 3. Corrección de Color

```python
from face_swap_modules import ColorCorrector
import cv2
import numpy as np

source = cv2.imread("source_face.jpg")
target = cv2.imread("target_face.jpg")
mask = np.ones((source.shape[0], source.shape[1]), dtype=np.float32)

corrector = ColorCorrector()

# Método 1: Histogram matching
corrected_hist = corrector.correct_color_histogram(source, target, mask)

# Método 2: LAB color space
corrected_lab = corrector.correct_color_lab(source, target, mask)

# Método 3: Combinación dual (recomendado)
corrected_dual = corrector.correct_color_dual(source, target, mask)

cv2.imwrite("corrected.jpg", corrected_dual)
```

### 4. Blending Avanzado

```python
from face_swap_modules import BlendingEngine
import cv2
import numpy as np

source = cv2.imread("source_face.jpg")
target = cv2.imread("target_face.jpg")
mask = np.ones((source.shape[0], source.shape[1]), dtype=np.float32) * 0.8

blender = BlendingEngine()

# Método 1: FFT blending
result_fft = blender.frequency_domain_blending(source, target, mask)

# Método 2: Poisson blending
result_poisson = blender.poisson_blending(source, target, mask)

# Método 3: Multi-scale blending
result_multiscale = blender.multi_scale_blending(source, target, mask)

# Método 4: Blending avanzado (recomendado)
result_advanced = blender.blend_advanced(source, target, mask)

# Método 5: Blending ultra-avanzado (máxima calidad)
result_ultra = blender.blend_ultra_advanced(source, target, mask)

cv2.imwrite("blended.jpg", result_ultra)
```

### 5. Mejora de Calidad

```python
from face_swap_modules import QualityEnhancer
import cv2

image = cv2.imread("face.jpg")
enhancer = QualityEnhancer()

# Análisis de calidad
metrics = enhancer.perceptual_quality_analysis(image)
print(f"Sharpness: {metrics['sharpness']}")
print(f"Contrast: {metrics['contrast']}")

# Mejora perceptual
enhanced = enhancer.enhance_perceptual_quality(image)

# Mejora de características faciales (requiere landmarks)
landmarks = extractor.detect(image)
enhanced_features = enhancer.enhance_facial_features(image, landmarks)

cv2.imwrite("enhanced.jpg", enhanced_features)
```

### 6. Pipeline Completo con Todas las Mejoras

```python
from face_swap_modules import FaceSwapPipeline
import cv2

source = cv2.imread("source.jpg")
target = cv2.imread("target.jpg")

# Pipeline con calidad ultra (todas las mejoras)
pipeline = FaceSwapPipeline(
    use_advanced_enhancements=True,
    quality_mode='ultra'
)

result = pipeline.process(source, target)
cv2.imwrite("result_ultra.jpg", result, [cv2.IMWRITE_JPEG_QUALITY, 100])
```

---

## ⚡ Modos de Calidad

### Modo 'fast' (Rápido)
```python
pipeline = FaceSwapPipeline(quality_mode='fast')
```
- ✅ Más rápido
- ✅ Calidad buena
- ❌ Sin mejoras avanzadas

### Modo 'high' (Alta Calidad)
```python
pipeline = FaceSwapPipeline(quality_mode='high')
```
- ✅ Balance velocidad/calidad
- ✅ Mejoras de calidad habilitadas
- ✅ Post-procesamiento completo

### Modo 'ultra' (Ultra Calidad)
```python
pipeline = FaceSwapPipeline(quality_mode='ultra')
```
- ✅ Máxima calidad
- ✅ Todas las mejoras avanzadas
- ⚠️ Más lento

---

## 🛠️ Uso de Utilidades

### LandmarkFormatHandler

```python
from face_swap_modules.base import LandmarkFormatHandler

# Detectar formato
format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
# Retorna: 106, 68, 468, o None

# Obtener regiones
left_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'left_eye')
right_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'right_eye')
nose = LandmarkFormatHandler.get_feature_region(landmarks, 'nose')
mouth = LandmarkFormatHandler.get_feature_region(landmarks, 'mouth')

# Obtener puntos específicos
nose_tip = LandmarkFormatHandler.get_feature_point(landmarks, 'nose_tip')
face_center = LandmarkFormatHandler.get_feature_point(landmarks, 'face_center')

# Validar landmarks
is_valid = LandmarkFormatHandler.is_valid_landmarks(landmarks)
```

### ImageProcessor

```python
from face_swap_modules.base import ImageProcessor

# Crear máscara 3D
mask_2d = np.ones((100, 100), dtype=np.float32)
mask_3d = ImageProcessor.create_3d_mask(mask_2d)  # (100, 100, 3)

# Convertir a uint8
mask_float = np.array([[0.0, 0.5, 1.0]], dtype=np.float32)
mask_uint8 = ImageProcessor.convert_to_uint8(mask_float)

# Validar coordenadas
x, y = ImageProcessor.ensure_bounds(150, 200, 100, 100)  # (100, 100)

# Conversiones de color
lab = ImageProcessor.convert_bgr_to_lab(image)
gray = ImageProcessor.convert_bgr_to_gray(image)
bgr = ImageProcessor.convert_lab_to_bgr(lab)

# Filtros
blurred = ImageProcessor.apply_gaussian_blur(image, (5, 5))
filtered = ImageProcessor.apply_bilateral_filter(image, 5, 50, 50)

# Clipping
clipped = ImageProcessor.clip_image(image)
```

---

## 🎨 Mejoras Avanzadas

### Usar AdvancedEnhancements

```python
from face_swap_modules import AdvancedEnhancements

enhancer = AdvancedEnhancements()

# Aplicar todas las mejoras
result = enhancer.apply_all_enhancements(
    source, target, source_landmarks, target_landmarks, mask
)

# O usar métodos específicos
result = enhancer.intelligent_lighting_adjustment(source, target, mask)
result = enhancer.color_harmony_optimization(source, result, mask)
result = enhancer.adaptive_sharpening_multi_scale(result, mask)
```

---

## 📊 Optimizaciones (Automáticas)

Las optimizaciones con Numba se usan automáticamente si está disponible:

```python
from face_swap_modules import is_numba_available

if is_numba_available():
    print("✓ Optimizaciones Numba activas (hasta 10x más rápido)")
else:
    print("⚠ Numba no disponible, usando versión estándar")
```

---

## 🔍 Validación

Antes de usar, valida que todo funciona:

```bash
python face_swap_modules/validate_modules.py
```

---

## 📚 Más Información

- **Documentación completa**: Ver `README.md`
- **Ejemplos detallados**: Ver `example_usage.py`
- **Guía de migración**: Ver `MIGRATION_GUIDE.md`
- **Estructura completa**: Ver `COMPLETE_REFACTORED_STRUCTURE.md`

---

## 🆘 Solución de Problemas

### Error: "No se detectaron caras"
- Verifica que las imágenes contengan caras visibles
- Prueba con imágenes de mayor resolución
- Asegúrate de tener mediapipe o insightface instalado

### Error: "No se pudieron extraer landmarks"
- Instala face-alignment o insightface
- Verifica que las caras estén bien detectadas

### Rendimiento lento
- Instala Numba: `pip install numba`
- Usa modo 'fast' o 'high' en lugar de 'ultra'
- Deshabilita mejoras avanzadas: `use_advanced_enhancements=False`

---

**¡Listo para comenzar!** 🎉








