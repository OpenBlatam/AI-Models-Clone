# Guía de Instalación de Librerías

## 🚀 Instalación Rápida

### Opción 1: Instalación Completa (Recomendada)
```bash
cd C:\blatam-academy\scripts
pip install -r requirements.txt
```

### Opción 2: Instalación por Categorías

#### Esenciales (Mínimo para funcionar)
```bash
pip install numpy>=1.24.0 opencv-python>=4.8.0
pip install insightface>=0.7.3 onnxruntime>=1.15.0
```

#### Detección Facial (Elige al menos una)
```bash
# Opción A: InsightFace (MEJOR CALIDAD)
pip install insightface>=0.7.3 onnxruntime>=1.15.0

# Opción B: RetinaFace (BALANCE)
pip install retinaface>=0.0.16

# Opción C: MediaPipe (MÁS RÁPIDO)
pip install mediapipe>=0.10.0
```

#### Landmarks (Elige al menos una)
```bash
# Opción A: InsightFace (106 puntos)
pip install insightface>=0.7.3

# Opción B: face-alignment (68 puntos)
pip install face-alignment>=1.3.5

# Opción C: MediaPipe (468 puntos)
pip install mediapipe>=0.10.0
```

#### Procesamiento Avanzado
```bash
pip install scikit-image>=0.21.0 Pillow>=10.0.0
pip install scipy>=1.11.0
```

#### GPU Acceleration (Opcional pero recomendado)
```bash
# Para NVIDIA GPU
pip install onnxruntime-gpu>=1.15.0
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install kornia>=0.7.0
```

## 🔍 Verificar Instalación

```python
# Verificar librerías instaladas
import sys

libraries = {
    'numpy': 'numpy',
    'opencv': 'cv2',
    'insightface': 'insightface',
    'onnxruntime': 'onnxruntime',
    'retinaface': 'retinaface',
    'mediapipe': 'mediapipe',
    'face_alignment': 'face_alignment',
    'skimage': 'skimage',
    'scipy': 'scipy',
    'kornia': 'kornia',
    'torch': 'torch',
    'numba': 'numba'
}

print("📦 Librerías Instaladas:")
print("=" * 50)
for name, module in libraries.items():
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'N/A')
        print(f"✅ {name:20s} - Versión: {version}")
    except ImportError:
        print(f"❌ {name:20s} - NO INSTALADA")

print("\n💡 Para instalar librerías faltantes:")
print("   pip install -r requirements.txt")
```

## ⚙️ Configuración Especial

### Windows con GPU NVIDIA
```bash
# 1. Instalar CUDA Toolkit (https://developer.nvidia.com/cuda-downloads)
# 2. Instalar cuDNN (https://developer.nvidia.com/cudnn)
# 3. Instalar PyTorch con CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
# 4. Instalar ONNX Runtime GPU
pip install onnxruntime-gpu>=1.15.0
```

### Linux
```bash
# Similar a Windows, pero puede requerir:
sudo apt-get install python3-dev python3-pip
sudo apt-get install libopencv-dev
```

### macOS
```bash
# Usar Homebrew para dependencias
brew install python3
pip3 install -r requirements.txt
```

## 🐛 Solución de Problemas

### Error: "No module named 'insightface'"
```bash
pip install insightface onnxruntime
```

### Error: "ONNX Runtime not found"
```bash
# CPU version
pip install onnxruntime>=1.15.0

# GPU version (NVIDIA)
pip install onnxruntime-gpu>=1.15.0
```

### Error: "MediaPipe installation failed"
```bash
# Actualizar pip primero
pip install --upgrade pip
pip install mediapipe>=0.10.0
```

### Error: "dlib compilation failed"
```bash
# Opción 1: Usar conda (más fácil)
conda install -c conda-forge dlib

# Opción 2: Instalar dependencias primero (Linux)
sudo apt-get install cmake libopenblas-dev liblapack-dev
pip install dlib
```

### Error: "CUDA not available" (PyTorch)
```bash
# Verificar CUDA instalado
nvidia-smi

# Instalar PyTorch con CUDA correcto
# Para CUDA 11.8:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 📊 Comparación de Requisitos

| Librería | Tamaño | RAM | GPU | Velocidad |
|----------|--------|-----|-----|-----------|
| InsightFace | ~500MB | 2GB | Opcional | ⭐⭐⭐⭐ |
| RetinaFace | ~200MB | 1GB | No | ⭐⭐⭐⭐⭐ |
| MediaPipe | ~100MB | 500MB | No | ⭐⭐⭐⭐⭐ |
| face-alignment | ~300MB | 1.5GB | Opcional | ⭐⭐⭐ |

## ✅ Checklist de Instalación

- [ ] Python 3.8+ instalado
- [ ] pip actualizado (`pip install --upgrade pip`)
- [ ] NumPy y OpenCV instalados
- [ ] Al menos un detector facial (InsightFace/RetinaFace/MediaPipe)
- [ ] Al menos un extractor de landmarks
- [ ] scikit-image y scipy para procesamiento avanzado
- [ ] (Opcional) GPU drivers y CUDA si usas GPU
- [ ] (Opcional) PyTorch y Kornia para operaciones avanzadas

## 🎯 Instalación Mínima para Empezar

```bash
# Solo lo esencial para que funcione
pip install numpy opencv-python
pip install insightface onnxruntime
pip install mediapipe
```

Esto te dará:
- ✅ Detección facial (InsightFace + MediaPipe)
- ✅ Landmarks (InsightFace + MediaPipe)
- ✅ Funcionalidad básica completa

## 🚀 Instalación Completa para Máxima Calidad

```bash
# Todo lo necesario para máxima calidad
pip install -r requirements.txt
```

Esto incluye:
- ✅ Todas las librerías de detección
- ✅ Todas las librerías de landmarks
- ✅ Procesamiento avanzado
- ✅ Optimizaciones GPU
- ✅ Herramientas de desarrollo








