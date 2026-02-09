# Modelo de Face Swap

Modelo simple y entrenable para hacer intercambio de caras (face swap) en cualquier imagen.

## Características

- ✅ Detección automática de caras
- ✅ Alineación facial usando landmarks
- ✅ Modelo CNN entrenable
- ✅ Blending suave para resultados naturales
- ✅ Funciona con cualquier imagen
- ✅ Dos versiones: completa y simplificada (sin dlib)

## Versiones Disponibles

### 1. Versión Completa (`face_swap_model.py`)
- Requiere: dlib, face_recognition
- Mayor precisión en detección
- Mejor alineación facial

### 2. Versión Simple (`face_swap_simple.py`) ⭐ RECOMENDADA
- Solo requiere: OpenCV, PyTorch
- Más fácil de instalar
- Funciona sin problemas en Windows

## Instalación

```bash
pip install -r requirements_face_swap.txt
```

**Nota para Windows:** dlib puede requerir instalación adicional:
1. Instalar Visual Studio Build Tools
2. `pip install cmake`
3. `pip install dlib`

## Uso Rápido

### Opción 1: Demo Rápido (Sin Entrenar)

```bash
# Probar con imágenes descargadas de Instagram
python quick_face_swap_demo.py
```

### Opción 2: Versión Simple (Recomendada)

#### 1. Entrenar el Modelo

```bash
# Entrenar con imágenes de la carpeta instagram_downloads
python face_swap_simple.py --mode train \
    --image-dir instagram_downloads/bunnyrose.me \
    --epochs 30 \
    --batch-size 4

# El modelo se guardará como face_swap_simple_model.pth
```

#### 2. Hacer Face Swap

```bash
# Intercambiar caras entre dos imágenes
python face_swap_simple.py --mode swap \
    --source imagen1.jpg \
    --target imagen2.jpg \
    --output resultado.jpg \
    --model face_swap_simple_model.pth
```

### Opción 3: Versión Completa (Con dlib)

#### 1. Entrenar el Modelo

```bash
python face_swap_model.py --mode train \
    --image-dir instagram_downloads/bunnyrose.me \
    --epochs 50 \
    --batch-size 4
```

#### 2. Hacer Face Swap

```bash
python face_swap_model.py --mode swap \
    --source imagen1.jpg \
    --target imagen2.jpg \
    --output resultado.jpg \
    --model face_swap_model.pth
```

## Uso Programático

### Versión Simple (Recomendada)

```python
from face_swap_simple import SimpleFaceSwapPipeline
import cv2

# Inicializar pipeline
pipeline = SimpleFaceSwapPipeline(model_path="face_swap_simple_model.pth")

# Cargar imágenes
source_img = cv2.imread("cara_fuente.jpg")
target_img = cv2.imread("imagen_destino.jpg")

# Hacer face swap
result = pipeline.swap_faces(source_img, target_img)

# Guardar resultado
cv2.imwrite("resultado.jpg", result)
```

### Versión Completa

```python
from face_swap_model import FaceSwapPipeline
import cv2

# Inicializar pipeline
pipeline = FaceSwapPipeline(model_path="face_swap_model.pth")

# Cargar imágenes
source_img = cv2.imread("cara_fuente.jpg")
target_img = cv2.imread("imagen_destino.jpg")

# Hacer face swap
result = pipeline.swap_faces(source_img, target_img)

# Guardar resultado
cv2.imwrite("resultado.jpg", result)
```

## Arquitectura del Modelo

El modelo utiliza:
- **Encoder-Dual**: Dos encoders separados para cara fuente y destino
- **Fusion Layer**: Combina características de ambas caras
- **Decoder**: Genera la cara intercambiada
- **Blending**: Integración suave en la imagen destino

## Parámetros de Entrenamiento

- **Epochs**: 50 (recomendado)
- **Batch Size**: 4-8 (depende de tu GPU)
- **Learning Rate**: 0.0002 (por defecto)
- **Input Size**: 256x256 píxeles

## Mejoras Futuras

- [ ] Soporte para múltiples caras
- [ ] Mejora de calidad con GANs
- [ ] Interfaz Gradio
- [ ] Soporte para video

## Notas

- El modelo funciona mejor con caras frontales
- Se recomienda entrenar con al menos 20-30 imágenes
- Los resultados mejoran con más épocas de entrenamiento
- Si no tienes modelo entrenado, el script usará detección básica

## Solución de Problemas

**Error: No se detecta cara**
- Asegúrate de que las imágenes tengan caras visibles
- Prueba con imágenes más grandes o mejor iluminación

**Error: dlib no se instala**
- Usa la versión sin dlib (solo OpenCV)
- El modelo funcionará pero con menor precisión

**Resultados poco realistas**
- Entrena el modelo con más épocas
- Usa más imágenes de entrenamiento
- Ajusta el learning rate








