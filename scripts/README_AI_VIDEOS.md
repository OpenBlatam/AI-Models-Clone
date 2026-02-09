# 🎬 Generador de Videos con IA

Sistema avanzado para crear videos animados con IA a partir de imágenes usando técnicas profesionales.

## ✨ Características

- **Efecto Ken Burns**: Zoom y pan suave automático
- **Mejora de Imágenes con IA**: Mejora automática de contraste, saturación y nitidez
- **Transiciones Suaves**: Fade in/out automático
- **Videos Individuales**: Un video por cada imagen
- **Videos Compilados**: Múltiples imágenes en un solo video
- **Optimizado para TikTok**: Resolución vertical 1080x1920
- **Alta Calidad**: 30 FPS, bitrate optimizado

## 📋 Requisitos

### Instalación de Dependencias

```bash
pip install -r requirements_ai_videos.txt
```

### Requisitos del Sistema

- Python 3.8+
- FFmpeg (se instala automáticamente con imageio-ffmpeg)
- Al menos 4GB de RAM
- Espacio en disco: ~50MB por video

## 🚀 Uso Rápido

### Crear todos los videos (individuales + compilados)

```bash
python create_ai_videos_from_images.py
```

### Solo videos individuales

```bash
python create_ai_videos_from_images.py --no-compilations
```

### Solo compilaciones

```bash
python create_ai_videos_from_images.py --no-individual
```

### Personalizar duración

```bash
python create_ai_videos_from_images.py --duration 5.0
```

### Sin efecto Ken Burns (más rápido)

```bash
python create_ai_videos_from_images.py --no-ken-burns
```

## 📁 Estructura de Salida

```
videos_ai_69caylin/
├── individual/
│   ├── 2023-05-30_17-23-28_UTC_Cs4CMhSNQjM_ai.mp4
│   ├── 2023-05-31_11-25-27_UTC_Cs5-BIzt0Xl_ai.mp4
│   └── ...
└── compilations/
    ├── compilation_001_10_images.mp4
    ├── compilation_002_10_images.mp4
    └── ...
```

## ⚙️ Opciones Avanzadas

### Configuración Personalizada

```bash
python create_ai_videos_from_images.py \
    --images-dir ./mis_imagenes \
    --output-dir ./mis_videos \
    --duration 4.0 \
    --images-per-compilation 15 \
    --no-ken-burns
```

### Parámetros Disponibles

- `--images-dir`: Directorio con las imágenes (default: `./instagram_downloads/69caylin`)
- `--output-dir`: Directorio de salida (default: `./videos_ai_69caylin`)
- `--duration`: Duración por imagen en segundos (default: 3.0)
- `--images-per-compilation`: Imágenes por compilación (default: 10)
- `--no-individual`: No crear videos individuales
- `--no-compilations`: No crear videos compilados
- `--no-ken-burns`: Desactivar animación (más rápido)

## 🎨 Técnicas de IA Utilizadas

### 1. Mejora de Imágenes
- Aumento de contraste inteligente
- Mejora de saturación
- Nitidez mejorada con filtros avanzados

### 2. Efecto Ken Burns
- Zoom suave automático (1.0x a 1.3x)
- Pan horizontal y vertical aleatorio
- Interpolación suave (ease-in-out)

### 3. Transiciones
- Fade in/out automático
- Transiciones entre imágenes suaves
- Duración optimizada

## 📊 Rendimiento

- **Velocidad**: ~2-5 segundos por imagen (con Ken Burns)
- **Calidad**: 1080x1920, 30 FPS, 8000k bitrate
- **Tamaño**: ~5-15 MB por video individual

## 🔧 Solución de Problemas

### Error: "moviepy no está instalado"

```bash
pip install moviepy
```

### Error: "FFmpeg no encontrado"

```bash
pip install imageio-ffmpeg
```

### Videos muy grandes

Reduce el bitrate editando el código:
```python
bitrate='4000k'  # En lugar de '8000k'
```

### Proceso muy lento

- Usa `--no-ken-burns` para desactivar animación
- Reduce `--duration` a 2.0 segundos
- Procesa en lotes más pequeños

### Error de memoria

- Procesa menos imágenes a la vez
- Cierra otras aplicaciones
- Usa `--no-individual` para solo crear compilaciones

## 💡 Consejos

1. **Para TikTok**: Los videos están optimizados para formato vertical (1080x1920)
2. **Calidad vs Velocidad**: Ken Burns mejora la calidad pero es más lento
3. **Organización**: Los videos se guardan en carpetas separadas (individual/compilations)
4. **Re-procesamiento**: El script salta videos que ya existen

## 🎯 Casos de Uso

### Publicación en TikTok
- Crea videos individuales para posts diarios
- Usa compilaciones para contenido especial

### Redes Sociales
- Videos verticales para Instagram Reels
- Videos horizontales (cambiar resolución en código)

### Presentaciones
- Compilaciones largas para mostrar portfolios
- Videos individuales para galerías

## 📝 Notas

- Los videos se crean sin audio (puedes agregarlo después)
- El formato es MP4 (H.264) compatible con todas las plataformas
- Las imágenes se mejoran automáticamente antes de crear el video
- El efecto Ken Burns es aleatorio para cada imagen (más natural)

## 🔄 Integración con TikTok Scheduler

Los videos generados pueden usarse directamente con el TikTok Scheduler:

1. Genera los videos con este script
2. Actualiza el TikTok Scheduler para usar videos en lugar de imágenes
3. Los videos ya están optimizados para TikTok (vertical, alta calidad)

## 📚 Recursos

- [MoviePy Documentation](https://zulko.github.io/moviepy/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)








