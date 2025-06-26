# Onyx Blog Posts System

Sistema completo de generación de blog posts para la plataforma Onyx, implementando principios de Clean Architecture con integración OpenRouter y LangChain.

## 🚀 Características

- **8 Tipos de Blog**: Técnico, Tutorial, Noticias, Opinión, Reseña, Guía, Caso de Estudio, Anuncio
- **7 Tonos de Escritura**: Profesional, Casual, Amigable, Autoritativo, Conversacional, Educativo, Inspiracional  
- **4 Opciones de Longitud**: Corto (300-600), Medio (600-1200), Largo (1200-2500), Extendido (2500-5000) palabras
- **6+ Modelos de IA**: GPT-4 Turbo, GPT-4o, Claude-3 Sonnet/Haiku, Gemini Pro, Mistral Large

## 🏗️ Arquitectura

El sistema sigue principios de Clean Architecture:

```
blog_posts/
├── interfaces/          # Contratos abstractos y tipos de dominio
├── core/               # Lógica de negocio pura
├── adapters/           # Integraciones externas
├── use_cases/          # Servicios de aplicación
├── factories/          # Inyección de dependencias
├── presenters/         # Capa de presentación
└── __init__.py         # Interfaz principal del módulo
```

## 🔧 Instalación

### Configuración del Entorno

```bash
# Variables de entorno requeridas
export OPENROUTER_API_KEY="tu_clave_openrouter"
export ONYX_URL="https://tu-instancia-onyx.com"
export ONYX_API_KEY="tu_clave_onyx"
```

## 🚀 Uso Rápido

### Generación Básica de Blog

```python
from onyx.server.features.blog_posts import create_blog_system, BlogSpec, GenerationParams

# Crear sistema
factory = create_blog_system(
    api_key="tu-clave-openrouter",
    environment="development"
)

# Generar blog post
use_case = factory.create_generate_blog_use_case()

spec = BlogSpec(
    topic="Inteligencia Artificial en Marketing Digital 2025",
    blog_type=BlogType.TECHNICAL,
    tone=BlogTone.PROFESSIONAL,
    length=BlogLength.MEDIUM,
    keywords=("ia", "marketing", "automatización"),
    language="es"
)

params = GenerationParams(
    model=AIModel.GPT_4_TURBO,
    include_seo=True,
    temperature=0.7
)

result = await use_case.execute(spec, params)

# Presentar resultado
presenter = UnifiedBlogPresenter()
api_response = await presenter.present_for_api(result)

# Limpiar recursos
await factory.cleanup()
```

### Función de Conveniencia

```python
from onyx.server.features.blog_posts import create_blog_post

result = await create_blog_post(
    topic="IA en el Marketing Digital",
    api_key="tu-clave",
    blog_type="technical",
    tone="professional", 
    length="medium",
    include_seo=True
)

print(f"Blog generado: {result['content']['title']}")
print(f"Puntuación de calidad: {result['metrics']['quality_score']}")
```

## 📊 Componentes Principales

### Interfaces (`interfaces/`)
- Tipos de dominio y enums (BlogType, BlogTone, BlogLength, AIModel)
- Objetos de valor (BlogSpec, BlogContent, SEOData, BlogResult)
- Interfaces abstractas para todas las capas

### Core (`core/`)
- **BlogContentValidator**: Validación de especificaciones y contenido
- **BlogQualityAnalyzer**: Algoritmo de puntuación de calidad
- **CoreBlogGenerator**: Orquestador principal de generación
- **CoreSEOGenerator**: Generación de metadatos SEO

### Adapters (`adapters/`)
- **OpenRouterAdapter**: Cliente API completo de OpenRouter
- **AdvancedPromptBuilder**: Motor de plantillas para prompts
- **JSONContentParser**: Análisis de respuestas de IA
- **MemoryCacheAdapter**: Implementación de caché LRU
- **OnyxIntegrationAdapter**: Integración con plataforma Onyx

### Use Cases (`use_cases/`)
- **GenerateBlogUseCase**: Flujo de generación de blog único
- **GenerateBatchUseCase**: Procesamiento por lotes con control de concurrencia
- **AnalyzeContentUseCase**: Análisis de contenido y evaluación de calidad

### Factories (`factories/`)
- **BlogSystemFactory**: Contenedor principal de inyección de dependencias
- Factories específicos por ambiente (Development, Production, Testing)
- Gestión de configuración y verificación de salud

### Presenters (`presenters/`)
- **APIResponsePresenter**: Formato de respuesta para API REST
- **DashboardPresenter**: Formato de datos para UI/dashboard
- **ExportPresenter**: Exportación a Markdown, HTML, JSON
- **UnifiedBlogPresenter**: Interfaz única para todos los formatos

## 🔬 Características Avanzadas

### Procesamiento por Lotes
```python
specs = [
    BlogSpec(topic="IA en Retail", blog_type=BlogType.CASE_STUDY, ...),
    BlogSpec(topic="Machine Learning", blog_type=BlogType.TUTORIAL, ...),
    BlogSpec(topic="Futuro del AI", blog_type=BlogType.OPINION, ...)
]

batch_use_case = factory.create_generate_batch_use_case()
results = await batch_use_case.execute(specs, params, max_concurrency=3)
```

### Análisis de Contenido
```python
analyze_use_case = factory.create_analyze_content_use_case()
analysis = await analyze_use_case.execute(
    content="Tu contenido existente aquí...",
    keywords=["ia", "automatización"]
)
```

### Monitoreo de Salud
```python
health = await factory.health_check()
metrics = await factory.create_metrics_collector().get_metrics()
```

## 🔧 Configuración

### Variables de Entorno

```bash
# Configuración OpenRouter
OPENROUTER_API_KEY=tu_clave_api_aqui
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
APP_NAME=onyx-blog-posts

# Configuración de Caché
CACHE_MAX_SIZE=1000              # Número de elementos en caché
CACHE_DEFAULT_TTL=3600           # TTL del caché en segundos

# Integración Onyx
ONYX_URL=http://localhost:8080
ONYX_API_KEY=clave_api_opcional

# Configuración de Rendimiento
MAX_CONCURRENCY=5                # Concurrencia de procesamiento por lotes
REQUEST_TIMEOUT=120              # Timeout de solicitud en segundos

# Banderas de Características
ENABLE_CACHING=true
ENABLE_METRICS=true
ENABLE_ONYX_INTEGRATION=true
```

## 📈 Métricas y Monitoreo

El sistema incluye recopilación integral de métricas:

- Tiempo de generación y tasas de éxito
- Uso de tokens y costos
- Puntuaciones de calidad y distribuciones
- Patrones de uso de modelos
- Salud del sistema y tiempo de actividad

```python
metrics = await factory.create_metrics_collector().get_metrics()
```

## 📤 Formatos de Exportación

Múltiples formatos de exportación soportados:

```python
presenter = UnifiedBlogPresenter()

# Markdown
markdown = await presenter.present_for_export(result, "markdown")

# HTML con SEO
html = await presenter.present_for_export(result, "html") 

# JSON
json_data = await presenter.present_for_export(result, "json")
```

## 🧪 Testing

```python
from onyx.server.features.blog_posts import TestingFactory

factory = TestingFactory()
# Todas las dependencias externas simuladas para testing
```

## 📄 Licencia

Este módulo es parte de la plataforma Onyx y sigue los mismos términos de licencia.

## 🆘 Soporte

Para problemas y soporte:
- Verificar salud del sistema: `await factory.health_check()`
- Monitorear métricas: `await metrics_collector.get_metrics()`
- Revisar logs: Logging estándar de Python a 'onyx.blog_posts'

## 📝 Versión

**Versión**: 2.0.0 (Arquitectura Limpia Refactorizada)  
**Compatible con**: Plataforma Onyx 3.x+  
**Última Actualización**: Enero 2025
