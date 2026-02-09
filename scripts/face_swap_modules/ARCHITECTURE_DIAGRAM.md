# Diagrama de Arquitectura - Módulos Refactorizados

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    Face Swap Modules                         │
│                  (Arquitectura Refactorizada)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌──────────────────┐    ┌──────────────┐
│ Base Classes  │    │  Core Modules    │    │  Utilities   │
│  & Utilities  │    │  (Refactored)    │    │  (Shared)    │
└───────────────┘    └──────────────────┘    └──────────────┘
```

## 📦 Estructura de Clases

### **Capa Base (Abstracciones)**

```
BaseDetector (ABC)
├── _safe_execute()          # Manejo de errores consistente
├── _is_model_available()    # Verificación de modelos
└── detect() [abstract]       # Método principal (a implementar)

LandmarkFormatHandler (Static)
├── get_landmark_format()     # Detecta formato (106/68/468)
├── get_feature_region()      # Obtiene región (ojos, boca, etc.)
├── get_feature_point()       # Obtiene punto específico
└── is_valid_landmarks()      # Valida landmarks

ImageProcessor (Static)
├── ensure_bounds()          # Valida coordenadas
├── create_3d_mask()         # Convierte máscara 2D→3D
└── convert_to_uint8()       # Conversión de tipos
```

### **Capa de Módulos (Implementaciones)**

```
FaceDetector (extends BaseDetector)
├── __init__()                    # Inicializa modelos
├── _initialize_models()          # Carga modelos disponibles
├── _detect_with_insightface()    # Método InsightFace
├── _detect_with_retinaface()     # Método RetinaFace
├── _detect_with_mediapipe()      # Método MediaPipe
├── _detect_with_opencv()         # Método OpenCV (fallback)
├── detect()                      # Método principal (fallback automático)
└── detect_face() [alias]         # Compatibilidad hacia atrás

LandmarkExtractor (extends BaseDetector)
├── __init__()                    # Inicializa modelos
├── _initialize_models()          # Carga modelos disponibles
├── _extract_with_insightface()   # Extracción InsightFace (106 pts)
├── _extract_with_face_alignment()# Extracción face-alignment (68 pts)
├── _extract_with_mediapipe()    # Extracción MediaPipe (468 pts)
├── detect()                      # Método principal (fallback automático)
└── get_landmarks() [alias]       # Compatibilidad hacia atrás

FaceAnalyzer
├── analyze_face_regions()        # Analiza regiones faciales
├── analyze_facial_expression()   # Analiza expresión
├── analyze_facial_features_deep()# Análisis profundo
├── analyze_geometric_structure() # Estructura geométrica
└── analyze_facial_symmetry()     # Simetría facial
    └── [Usa LandmarkFormatHandler para todo]

ColorCorrector
├── correct_color_histogram()    # Corrección por histograma
├── correct_color_lab()          # Corrección LAB estadística
├── correct_color_dual()         # Combinación de métodos
├── create_attention_mask()       # Máscara de atención
└── [Métodos helper privados]
    ├── _calculate_weighted_mean()
    ├── _calculate_weighted_std()
    ├── _apply_lab_transformation()
    └── _blend_luminosity()

BlendingEngine
├── frequency_domain_blending()  # Blending FFT
├── poisson_blending()           # Blending Poisson
├── multi_scale_blending()       # Blending multi-escala
├── seamless_cloning()           # Cloning OpenCV
├── blend_advanced()             # Combinación inteligente
└── [Métodos helper privados]
    ├── _blend_gradients()
    ├── _reconstruct_from_gradients()
    ├── _preserve_color_saturation()
    ├── _calculate_mask_center()
    ├── _try_seamless_clone_methods()
    └── _simple_blend()

QualityEnhancer
├── perceptual_quality_analysis()    # Análisis perceptual
├── enhance_perceptual_quality()     # Mejora perceptual
├── enhance_high_frequency_details()  # Mejora detalles HF
├── enhance_facial_features()        # Mejora características
├── preserve_visual_features()       # Preserva características
└── [Métodos helper privados]
    ├── _enhance_sharpness()
    ├── _enhance_contrast()
    ├── _enhance_texture()
    ├── _create_attention_mask()
    ├── _create_detail_mask()
    ├── _apply_adaptive_sharpening()
    └── _apply_source_details()

PostProcessor
├── advanced_post_processing()      # Post-procesamiento avanzado
├── reduce_artifacts_advanced()    # Reducción de artefactos
├── enhance_fine_details()          # Mejora detalles finos
├── final_save_enhancement()       # Mejora final
└── analyze_spatial_coherence()    # Análisis de coherencia
    └── [Métodos helper privados]
        ├── _apply_bilateral_filtering()
        ├── _restore_multi_scale_details()
        ├── _enhance_contrast_and_saturation()
        ├── _detect_artifacts()
        ├── _smooth_artifacts()
        └── _smooth_low_coherence_regions()
```

## 🔄 Flujo de Dependencias

```
┌─────────────────┐
│  FaceDetector   │──┐
└─────────────────┘  │
                     ├──> BaseDetector
┌─────────────────┐  │
│LandmarkExtractor│──┘
└─────────────────┘

┌─────────────────┐
│  FaceAnalyzer   │──┐
└─────────────────┘  │
                     ├──> LandmarkFormatHandler
┌─────────────────┐  │
│ ColorCorrector  │──┤
└─────────────────┘  │
                     │
┌─────────────────┐  │
│QualityEnhancer  │──┘
└─────────────────┘

┌─────────────────┐
│ ColorCorrector  │──┐
└─────────────────┘  │
                     ├──> ImageProcessor
┌─────────────────┐  │
│BlendingEngine   │──┤
└─────────────────┘  │
                     │
┌─────────────────┐  │
│QualityEnhancer  │──┤
└─────────────────┘  │
                     │
┌─────────────────┐  │
│ PostProcessor   │──┘
└─────────────────┘
```

## 🎯 Patrones de Diseño Aplicados

### 1. **Template Method Pattern**
- `BaseDetector` define el esqueleto del algoritmo
- Subclases implementan pasos específicos

### 2. **Strategy Pattern**
- Múltiples métodos de detección/extraction
- Selección automática con fallback

### 3. **Facade Pattern**
- `LandmarkFormatHandler` simplifica acceso a formatos
- `ImageProcessor` simplifica operaciones de imagen

### 4. **Single Responsibility**
- Cada clase tiene una responsabilidad única
- Métodos helper para tareas específicas

## 📊 Métricas de Arquitectura

| Aspecto | Valor |
|---------|-------|
| **Clases Base** | 3 |
| **Módulos Principales** | 7 |
| **Métodos Helper** | 33 |
| **Constantes Extraídas** | 43 |
| **Nivel de Acoplamiento** | Bajo |
| **Nivel de Cohesión** | Alto |
| **Líneas Duplicadas** | 0 |
| **Compatibilidad Hacia Atrás** | 100% |

## 🔍 Flujo de Ejecución Típico

```
1. Inicialización
   ├──> FaceDetector.__init__()
   │    └──> BaseDetector.__init__()
   │         └──> _initialize_models()
   │
   └──> LandmarkExtractor.__init__()
        └──> BaseDetector.__init__()
             └──> _initialize_models()

2. Detección
   └──> detector.detect(image)
        └──> _detect_with_insightface()
             └──> _safe_execute(_detect)
                  └──> [Fallback automático si falla]

3. Extracción
   └──> extractor.detect(image)
        └──> _extract_with_insightface()
             └──> _safe_execute(_extract)
                  └──> [Fallback automático si falla]

4. Análisis
   └──> analyzer.analyze_face_regions(image, landmarks)
        └──> LandmarkFormatHandler.get_feature_region()
             └──> [Manejo automático de formatos]

5. Procesamiento
   └──> color_corrector.correct_color_dual(...)
        ├──> correct_color_histogram()
        ├──> correct_color_lab()
        │    ├──> _calculate_weighted_mean()
        │    ├──> _calculate_weighted_std()
        │    ├──> _apply_lab_transformation()
        │    └──> _blend_luminosity()
        └──> ImageProcessor.create_3d_mask()
```

## 🎨 Ventajas de la Arquitectura

1. **Modularidad**: Cada módulo es independiente y reutilizable
2. **Extensibilidad**: Fácil agregar nuevos métodos o formatos
3. **Mantenibilidad**: Cambios localizados y claros
4. **Testabilidad**: Componentes pequeños y enfocados
5. **Consistencia**: Patrones uniformes en todo el código
6. **Simplicidad**: Sin sobre-ingeniería, solo lo necesario

## 🔮 Extensiones Futuras

La arquitectura permite fácilmente:

1. **Nuevos Formatos de Landmarks**
   - Solo actualizar `LandmarkFormatHandler`

2. **Nuevos Métodos de Detección**
   - Extender `BaseDetector` y agregar método `_detect_with_*`

3. **Nuevos Algoritmos de Blending**
   - Agregar método a `BlendingEngine`

4. **Nuevas Utilidades**
   - Agregar métodos estáticos a `ImageProcessor`

5. **Nuevos Módulos**
   - Seguir el patrón establecido








