# Ejemplos de Uso - Face Swap Modules

## 📚 Colección Completa de Ejemplos

Esta guía proporciona ejemplos prácticos de uso de todos los módulos refactorizados.

---

## 🎯 Ejemplos por Módulo

### 1. FaceDetector

```python
from face_swap_modules import FaceDetector
import cv2

image = cv2.imread("photo.jpg")
detector = FaceDetector()

# Detección simple
bbox = detector.detect(image)
if bbox:
    x, y, w, h = bbox
    print(f"Cara detectada en: ({x}, {y}), tamaño: {w}x{h}")

# Compatibilidad hacia atrás
bbox = detector.detect_face(image)  # También funciona
```

---

### 2. LandmarkExtractor

```python
from face_swap_modules import LandmarkExtractor
import cv2

image = cv2.imread("photo.jpg")
extractor = LandmarkExtractor()

# Extracción simple
landmarks = extractor.detect(image)
if landmarks is not None:
    print(f"Landmarks extraídos: {len(landmarks)} puntos")
    print(f"Formato: {len(landmarks)} puntos")

# Compatibilidad hacia atrás
landmarks = extractor.get_landmarks(image)  # También funciona
```

---

### 3. FaceAnalyzer

```python
from face_swap_modules import FaceDetector, LandmarkExtractor, FaceAnalyzer
import cv2

image = cv2.imread("photo.jpg")
detector = FaceDetector()
extractor = LandmarkExtractor()
analyzer = FaceAnalyzer()

bbox = detector.detect(image)
landmarks = extractor.detect(image)

# Análisis de regiones
regions = analyzer.analyze_face_regions(image, landmarks)
print(f"Regiones detectadas: {list(regions.keys())}")

# Análisis de expresión
expression = analyzer.analyze_facial_expression(landmarks)
print(f"Apertura de ojos: {expression.get('eye_openness')}")

# Análisis profundo
features = analyzer.analyze_facial_features_deep(image, landmarks)
print(f"Tono de piel: {features.get('skin_tone')}")

# Análisis geométrico
geometry = analyzer.analyze_geometric_structure(landmarks)
print(f"Proporciones faciales: {geometry.get('proportions')}")

# Análisis de simetría
symmetry = analyzer.analyze_facial_symmetry(image, landmarks)
print(f"Simetría: {symmetry.get('symmetry_score')}")
```

---

### 4. ColorCorrector

```python
from face_swap_modules import ColorCorrector
import cv2
import numpy as np

source = cv2.imread("source_face.jpg")
target = cv2.imread("target_face.jpg")
mask = np.ones((source.shape[0], source.shape[1]), dtype=np.float32) * 0.8

corrector = ColorCorrector()

# Método 1: Histogram matching
corrected_hist = corrector.correct_color_histogram(source, target, mask)
cv2.imwrite("corrected_hist.jpg", corrected_hist)

# Método 2: LAB color space
corrected_lab = corrector.correct_color_lab(source, target, mask)
cv2.imwrite("corrected_lab.jpg", corrected_lab)

# Método 3: Combinación dual (recomendado)
corrected_dual = corrector.correct_color_dual(source, target, mask)
cv2.imwrite("corrected_dual.jpg", corrected_dual)

# Máscara de atención
attention_mask = corrector.create_attention_mask(target, landmarks)
cv2.imwrite("attention_mask.jpg", (attention_mask * 255).astype(np.uint8))
```

---

### 5. BlendingEngine

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
cv2.imwrite("blended_fft.jpg", result_fft)

# Método 2: Poisson blending
result_poisson = blender.poisson_blending(source, target, mask)
cv2.imwrite("blended_poisson.jpg", result_poisson)

# Método 3: Multi-scale blending
result_multiscale = blender.multi_scale_blending(source, target, mask, levels=6)
cv2.imwrite("blended_multiscale.jpg", result_multiscale)

# Método 4: Seamless cloning
result_seamless = blender.seamless_cloning(source, target, mask)
if result_seamless is not None:
    cv2.imwrite("blended_seamless.jpg", result_seamless)

# Método 5: Blending avanzado (recomendado)
result_advanced = blender.blend_advanced(source, target, mask)
cv2.imwrite("blended_advanced.jpg", result_advanced)

# Método 6: Blending ultra-avanzado (máxima calidad)
result_ultra = blender.blend_ultra_advanced(source, target, mask)
cv2.imwrite("blended_ultra.jpg", result_ultra)
```

---

### 6. QualityEnhancer

```python
from face_swap_modules import QualityEnhancer, LandmarkExtractor
import cv2

image = cv2.imread("face.jpg")
extractor = LandmarkExtractor()
enhancer = QualityEnhancer()

# Análisis de calidad
metrics = enhancer.perceptual_quality_analysis(image)
print(f"Sharpness: {metrics['sharpness']}")
print(f"Contrast: {metrics['contrast']}")
print(f"Brightness: {metrics['brightness']}")
print(f"Texture entropy: {metrics['texture_entropy']}")

# Mejora perceptual
enhanced = enhancer.enhance_perceptual_quality(image)
cv2.imwrite("enhanced_perceptual.jpg", enhanced)

# Mejora de detalles de alta frecuencia
mask = np.ones((image.shape[0], image.shape[1]), dtype=np.float32)
enhanced_hf = enhancer.enhance_high_frequency_details(image, mask)
cv2.imwrite("enhanced_hf.jpg", enhanced_hf)

# Mejora de características faciales
landmarks = extractor.detect(image)
enhanced_features = enhancer.enhance_facial_features(image, landmarks)
cv2.imwrite("enhanced_features.jpg", enhanced_features)

# Preservar características visuales
source = cv2.imread("source.jpg")
target = cv2.imread("target.jpg")
preserved = enhancer.preserve_visual_features(source, target, mask)
cv2.imwrite("preserved.jpg", preserved)
```

---

### 7. PostProcessor

```python
from face_swap_modules import PostProcessor
import cv2
import numpy as np

image = cv2.imread("face.jpg")
target = cv2.imread("target.jpg")
mask = np.ones((image.shape[0], image.shape[1]), dtype=np.float32)

processor = PostProcessor()

# Post-procesamiento avanzado
processed = processor.advanced_post_processing(image, target, mask)
cv2.imwrite("processed.jpg", processed)

# Reducción de artefactos
reduced = processor.reduce_artifacts_advanced(image, mask)
cv2.imwrite("reduced_artifacts.jpg", reduced)

# Mejora de detalles finos
enhanced = processor.enhance_fine_details(image, mask)
cv2.imwrite("enhanced_details.jpg", enhanced)

# Mejora final antes de guardar
final = processor.final_save_enhancement(image)
cv2.imwrite("final.jpg", final)

# Análisis de coherencia espacial
coherent = processor.analyze_spatial_coherence(image, mask)
cv2.imwrite("coherent.jpg", coherent)

# Ultra final enhancement (pipeline completo)
ultra_final = processor.ultra_final_enhancement(image, mask)
cv2.imwrite("ultra_final.jpg", ultra_final)
```

---

### 8. AdvancedEnhancements

```python
from face_swap_modules import AdvancedEnhancements, LandmarkExtractor
import cv2
import numpy as np

source = cv2.imread("source.jpg")
target = cv2.imread("target.jpg")
mask = np.ones((source.shape[0], source.shape[1]), dtype=np.float32)

extractor = LandmarkExtractor()
enhancer = AdvancedEnhancements()

source_landmarks = extractor.detect(source)
target_landmarks = extractor.detect(target)

# Aplicar todas las mejoras (pipeline completo)
result = enhancer.apply_all_enhancements(
    source, target, source_landmarks, target_landmarks, mask
)
cv2.imwrite("all_enhancements.jpg", result)

# O usar métodos específicos:

# Ajuste de iluminación
result = enhancer.intelligent_lighting_adjustment(source, target, mask)

# Color grading
result = enhancer.intelligent_color_grading(source, target, mask)

# Armonía de color
result = enhancer.color_harmony_optimization(source, target, mask)

# Preservación de estilo neural
result = enhancer.neural_style_preservation(source, target, mask)

# Sharpening adaptativo
result = enhancer.adaptive_sharpening_multi_scale(target, mask)

# Super-resolution
result = enhancer.super_resolution_adaptive(target, scale=1.5)
```

---

### 9. Utilidades: LandmarkFormatHandler

```python
from face_swap_modules.base import LandmarkFormatHandler
from face_swap_modules import LandmarkExtractor
import cv2

image = cv2.imread("photo.jpg")
extractor = LandmarkExtractor()
landmarks = extractor.detect(image)

# Detectar formato
format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
print(f"Formato detectado: {format_type} puntos")

# Validar landmarks
is_valid = LandmarkFormatHandler.is_valid_landmarks(landmarks)
print(f"Landmarks válidos: {is_valid}")

# Obtener regiones
left_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'left_eye')
right_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'right_eye')
nose = LandmarkFormatHandler.get_feature_region(landmarks, 'nose')
mouth = LandmarkFormatHandler.get_feature_region(landmarks, 'mouth')

# Obtener puntos específicos
nose_tip = LandmarkFormatHandler.get_feature_point(landmarks, 'nose_tip')
face_center = LandmarkFormatHandler.get_feature_point(landmarks, 'face_center')
left_eye_center = LandmarkFormatHandler.get_feature_point(landmarks, 'left_eye_center')
right_eye_center = LandmarkFormatHandler.get_feature_point(landmarks, 'right_eye_center')
```

---

### 10. Utilidades: ImageProcessor

```python
from face_swap_modules.base import ImageProcessor
import cv2
import numpy as np

image = cv2.imread("photo.jpg")

# Crear máscara 3D
mask_2d = np.ones((100, 100), dtype=np.float32) * 0.5
mask_3d = ImageProcessor.create_3d_mask(mask_2d)  # (100, 100, 3)

# Convertir a uint8
mask_float = np.array([[0.0, 0.5, 1.0]], dtype=np.float32)
mask_uint8 = ImageProcessor.convert_to_uint8(mask_float)

# Validar coordenadas
x, y = ImageProcessor.ensure_bounds(150, 200, 100, 100)  # Retorna (100, 100)

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

## 🔥 Pipeline Completo

### Ejemplo 1: Pipeline Básico

```python
from face_swap_modules import FaceSwapPipeline
import cv2

source = cv2.imread("source.jpg")
target = cv2.imread("target.jpg")

pipeline = FaceSwapPipeline(quality_mode='high')
result = pipeline.process(source, target)
cv2.imwrite("result.jpg", result)
```

### Ejemplo 2: Pipeline Ultra Calidad

```python
from face_swap_modules import FaceSwapPipeline
import cv2

source = cv2.imread("source.jpg")
target = cv2.imread("target.jpg")

pipeline = FaceSwapPipeline(
    use_advanced_enhancements=True,
    quality_mode='ultra'
)
result = pipeline.process(source, target)
cv2.imwrite("result_ultra.jpg", result, [cv2.IMWRITE_JPEG_QUALITY, 100])
```

### Ejemplo 3: Procesamiento por Lotes

```python
from face_swap_modules import FaceSwapPipeline
from pathlib import Path
import cv2

source = cv2.imread("source.jpg")
target_dir = Path("target_images")
output_dir = Path("output")

# Cargar imágenes objetivo
target_images = []
for img_path in target_dir.glob("*.jpg"):
    target_images.append(cv2.imread(str(img_path)))

# Crear pipeline
pipeline = FaceSwapPipeline(quality_mode='high')

# Procesar por lotes
results = pipeline.process_batch(source, target_images, output_dir)
print(f"Procesadas: {sum(results.values())} imágenes")
```

### Ejemplo 4: Desde Línea de Comandos

```bash
# Uso básico
python face_swap_modules/face_swap_pipeline.py source.jpg target.jpg -o result.jpg

# Modo ultra calidad
python face_swap_modules/face_swap_pipeline.py source.jpg target.jpg -o result.jpg -q ultra

# Sin mejoras avanzadas (más rápido)
python face_swap_modules/face_swap_pipeline.py source.jpg target.jpg -o result.jpg --no-advanced
```

---

## 🎨 Ejemplos Avanzados

### Ejemplo 1: Pipeline Personalizado

```python
from face_swap_modules import (
    FaceDetector, LandmarkExtractor, ColorCorrector,
    BlendingEngine, QualityEnhancer, PostProcessor
)
import cv2
import numpy as np

source = cv2.imread("source.jpg")
target = cv2.imread("target.jpg")

# Inicializar componentes
detector = FaceDetector()
extractor = LandmarkExtractor()
color_corrector = ColorCorrector()
blender = BlendingEngine()
enhancer = QualityEnhancer()
processor = PostProcessor()

# Proceso personalizado
source_bbox = detector.detect(source)
target_bbox = detector.detect(target)
source_landmarks = extractor.detect(source)
target_landmarks = extractor.detect(target)

# Extraer caras
source_face = source[source_bbox[1]:source_bbox[1]+source_bbox[3],
                     source_bbox[0]:source_bbox[0]+source_bbox[2]]
target_face = target[target_bbox[1]:target_bbox[1]+target_bbox[3],
                     target_bbox[0]:target_bbox[0]+target_bbox[2]]

# Redimensionar
source_face = cv2.resize(source_face, (target_face.shape[1], target_face.shape[0]))

# Crear máscara
mask = np.ones((target_face.shape[0], target_face.shape[1]), dtype=np.float32) * 0.8

# Corrección de color
corrected = color_corrector.correct_color_dual(source_face, target_face, mask)

# Blending
blended = blender.blend_ultra_advanced(corrected, target_face, mask)

# Mejora de calidad
enhanced = enhancer.enhance_facial_features(blended, target_landmarks)

# Post-procesamiento
final = processor.ultra_final_enhancement(enhanced, mask)

# Integrar
result = target.copy()
result[target_bbox[1]:target_bbox[1]+target_bbox[3],
       target_bbox[0]:target_bbox[0]+target_bbox[2]] = final

cv2.imwrite("result_custom.jpg", result)
```

### Ejemplo 2: Análisis Comparativo

```python
from face_swap_modules import FaceAnalyzer, LandmarkExtractor
import cv2

image1 = cv2.imread("face1.jpg")
image2 = cv2.imread("face2.jpg")

extractor = LandmarkExtractor()
analyzer = FaceAnalyzer()

landmarks1 = extractor.detect(image1)
landmarks2 = extractor.detect(image2)

# Analizar ambas caras
features1 = analyzer.analyze_facial_features_deep(image1, landmarks1)
features2 = analyzer.analyze_facial_features_deep(image2, landmarks2)

# Comparar
print(f"Tono de piel 1: {features1.get('skin_tone')}")
print(f"Tono de piel 2: {features2.get('skin_tone')}")
print(f"Diferencia: {abs(features1.get('skin_tone', 0) - features2.get('skin_tone', 0))}")
```

---

## 📚 Más Información

- **Guía de inicio rápido**: Ver `QUICK_START.md`
- **Ejemplos completos**: Ver `example_usage.py`
- **Pipeline completo**: Ver `face_swap_pipeline.py`
- **Documentación completa**: Ver `README.md`

---

**¡Disfruta usando los módulos refactorizados!** 🎉








