# Guía de Solución de Problemas - Face Swap Modules

## 🔧 Problemas Comunes y Soluciones

Esta guía ayuda a resolver problemas comunes al usar los módulos refactorizados.

---

## ❌ Problemas de Instalación

### Error: "ModuleNotFoundError: No module named 'face_swap_modules'"

**Causa**: El módulo no está en el PYTHONPATH.

**Solución**:
```bash
# Opción 1: Instalar en modo desarrollo
cd scripts
pip install -e .

# Opción 2: Agregar al PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/scripts"

# Opción 3: Usar sys.path en el código
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
```

### Error: "No module named 'cv2'"

**Causa**: OpenCV no está instalado.

**Solución**:
```bash
pip install opencv-python
# O para versión headless (sin GUI)
pip install opencv-python-headless
```

### Error: "No module named 'numba'"

**Causa**: Numba no está instalado (opcional pero recomendado).

**Solución**:
```bash
pip install numba
```

**Nota**: El código funciona sin Numba, pero será más lento.

---

## 🔍 Problemas de Detección

### Problema: "No se detectaron caras"

**Posibles Causas**:
1. Imagen sin caras visibles
2. Resolución muy baja
3. Librerías de detección no instaladas

**Soluciones**:

**1. Verificar imagen**:
```python
import cv2
image = cv2.imread("photo.jpg")
print(f"Dimensiones: {image.shape}")
print(f"Tipo: {image.dtype}")

# Mostrar imagen para verificar
cv2.imshow("Imagen", image)
cv2.waitKey(0)
```

**2. Instalar librerías de detección**:
```bash
# Opción 1: MediaPipe (recomendado)
pip install mediapipe

# Opción 2: InsightFace
pip install insightface onnxruntime

# Opción 3: RetinaFace
pip install retinaface
```

**3. Usar método específico**:
```python
from face_swap_modules import FaceDetector

detector = FaceDetector()

# Forzar método específico
bbox = detector._detect_with_mediapipe(image)
# O
bbox = detector._detect_with_opencv(image)
```

### Problema: Detección lenta

**Solución**:
```python
# Usar método más rápido
detector = FaceDetector()
# OpenCV es generalmente más rápido
bbox = detector._detect_with_opencv(image)
```

---

## 📍 Problemas de Landmarks

### Problema: "No se pudieron extraer landmarks"

**Causas**:
1. Cara no detectada correctamente
2. Librerías de landmarks no instaladas
3. Formato de imagen incompatible

**Soluciones**:

**1. Verificar detección primero**:
```python
from face_swap_modules import FaceDetector, LandmarkExtractor

detector = FaceDetector()
extractor = LandmarkExtractor()

# Verificar detección
bbox = detector.detect(image)
if bbox is None:
    print("Error: No se detectó cara")
    return

# Luego extraer landmarks
landmarks = extractor.detect(image)
```

**2. Instalar librerías**:
```bash
# Face-alignment (recomendado)
pip install face-alignment

# InsightFace (alternativa)
pip install insightface onnxruntime
```

**3. Verificar formato de imagen**:
```python
# Convertir a RGB si es necesario
if len(image.shape) == 2:
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

# Asegurar tipo correcto
if image.dtype != np.uint8:
    image = (image * 255).astype(np.uint8)
```

---

## 🎨 Problemas de Procesamiento

### Problema: "ValueError: operands could not be broadcast together"

**Causa**: Dimensiones incompatibles entre imágenes.

**Solución**:
```python
# Verificar dimensiones
print(f"Source: {source.shape}")
print(f"Target: {target.shape}")

# Redimensionar si es necesario
if source.shape != target.shape:
    source = cv2.resize(source, (target.shape[1], target.shape[0]))
```

### Problema: Resultado con colores extraños

**Causa**: Espacios de color incorrectos.

**Solución**:
```python
# Asegurar BGR (OpenCV usa BGR, no RGB)
image = cv2.imread("photo.jpg")  # Ya está en BGR

# Si cargas con PIL, convertir
from PIL import Image
pil_image = Image.open("photo.jpg")
image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
```

### Problema: Máscara no funciona correctamente

**Causa**: Formato o rango de valores incorrecto.

**Solución**:
```python
from face_swap_modules.base import ImageProcessor

# Asegurar formato correcto
mask_2d = np.ones((h, w), dtype=np.float32) * 0.8
mask_3d = ImageProcessor.create_3d_mask(mask_2d)

# Verificar rango [0, 1]
mask = np.clip(mask, 0.0, 1.0)
```

---

## ⚡ Problemas de Rendimiento

### Problema: Procesamiento muy lento

**Soluciones**:

**1. Instalar Numba**:
```bash
pip install numba
```

**2. Usar modo 'fast'**:
```python
from face_swap_modules import FaceSwapPipeline

pipeline = FaceSwapPipeline(quality_mode='fast')
result = pipeline.process(source, target)
```

**3. Reducir resolución**:
```python
# Redimensionar antes de procesar
scale = 0.5
small_source = cv2.resize(source, None, fx=scale, fy=scale)
small_target = cv2.resize(target, None, fx=scale, fy=scale)

# Procesar
result = pipeline.process(small_source, small_target)

# Redimensionar resultado
result = cv2.resize(result, (target.shape[1], target.shape[0]))
```

**4. Deshabilitar mejoras avanzadas**:
```python
pipeline = FaceSwapPipeline(
    quality_mode='high',
    use_advanced_enhancements=False
)
```

### Problema: Uso excesivo de memoria

**Solución**:
```python
# Procesar en chunks si la imagen es muy grande
def process_large_image(image, chunk_size=512):
    h, w = image.shape[:2]
    chunks = []
    for y in range(0, h, chunk_size):
        for x in range(0, w, chunk_size):
            chunk = image[y:y+chunk_size, x:x+chunk_size]
            # Procesar chunk
            processed_chunk = process(chunk)
            chunks.append((y, x, processed_chunk))
    # Reconstruir imagen
    return reconstruct(chunks)
```

---

## 🐛 Problemas de Código

### Error: "AttributeError: 'NoneType' object has no attribute..."

**Causa**: Variable es None cuando se espera un valor.

**Solución**:
```python
# Siempre validar antes de usar
bbox = detector.detect(image)
if bbox is None:
    print("No se detectó cara")
    return

x, y, w, h = bbox  # Ahora es seguro
```

### Error: "TypeError: unsupported operand type(s)"

**Causa**: Tipos de datos incompatibles.

**Solución**:
```python
# Convertir a tipos correctos
image = image.astype(np.uint8)
mask = mask.astype(np.float32)

# Verificar tipos
print(f"Image dtype: {image.dtype}")
print(f"Mask dtype: {mask.dtype}")
```

---

## 📊 Problemas de Validación

### Error en validate_modules.py

**Solución**:
```bash
# Verificar dependencias primero
python check_dependencies.py

# Instalar dependencias faltantes
python setup.py

# Luego validar
python validate_modules.py
```

---

## 🔄 Problemas de Compatibilidad

### Error: "API changed" o métodos no encontrados

**Causa**: Cambio de versión o API.

**Solución**:
```python
# Verificar versión
from face_swap_modules import __version__
print(f"Versión: {__version__}")

# Usar métodos compatibles
# Los métodos antiguos siguen funcionando (aliases)
bbox = detector.detect_face(image)  # Funciona
bbox = detector.detect(image)  # Nuevo método
```

---

## 💡 Consejos de Debugging

### 1. Activar logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from face_swap_modules import FaceDetector
detector = FaceDetector()
bbox = detector.detect(image)
```

### 2. Verificar paso a paso

```python
# Paso 1: Cargar imagen
image = cv2.imread("photo.jpg")
assert image is not None, "No se pudo cargar imagen"

# Paso 2: Detectar
bbox = detector.detect(image)
print(f"Bbox: {bbox}")

# Paso 3: Extraer landmarks
if bbox:
    landmarks = extractor.detect(image)
    print(f"Landmarks: {landmarks.shape if landmarks is not None else None}")
```

### 3. Guardar resultados intermedios

```python
# Guardar cada paso para debugging
cv2.imwrite("01_original.jpg", image)
cv2.imwrite("02_detected.jpg", image_with_bbox)
cv2.imwrite("03_landmarks.jpg", image_with_landmarks)
```

---

## 📞 Obtener Ayuda

### Recursos

1. **Documentación**: Ver `README.md` y `QUICK_START.md`
2. **Ejemplos**: Ver `example_usage.py` y `USAGE_EXAMPLES.md`
3. **Mejores prácticas**: Ver `BEST_PRACTICES.md`
4. **Validación**: Ejecutar `python validate_modules.py`

### Información para Reportar Problemas

Si el problema persiste, incluir:
- Versión de Python: `python --version`
- Versión del módulo: `from face_swap_modules import __version__`
- Mensaje de error completo
- Código que reproduce el problema
- Resultado de `python check_dependencies.py`

---

**Última actualización**: v2.1.0








