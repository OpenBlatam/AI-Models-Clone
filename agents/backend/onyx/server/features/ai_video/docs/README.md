# AI Video Workflow System

Un sistema completo y modular para la generación automática de videos con IA, que extrae contenido de cualquier URL web y genera videos profesionales con avatares y voz en off.

## 🚀 Características Principales

- **Extracción Inteligente de Contenido**: Múltiples extractores con fallback automático
- **Sugerencias de IA**: Scripts, imágenes y estilos generados automáticamente
- **Generación de Videos**: Avatares realistas con voz en off
- **Workflow Completo**: Pipeline automatizado de principio a fin
- **Métricas Avanzadas**: Monitoreo en tiempo real y análisis de rendimiento
- **CLI Completa**: Interfaz de línea de comandos para gestión
- **Persistencia de Estado**: Reanudación de workflows interrumpidos
- **Arquitectura Modular**: Fácil extensión y personalización

## 📋 Tabla de Contenidos

- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Arquitectura](#arquitectura)
- [API Reference](#api-reference)
- [CLI](#cli)
- [Métricas y Monitoreo](#métricas-y-monitoreo)
- [Configuración Avanzada](#configuración-avanzada)
- [Troubleshooting](#troubleshooting)

## 🛠️ Instalación

### Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt`

### Instalación de Dependencias

```bash
# Instalar dependencias principales
pip install newspaper3k trafilatura beautifulsoup4 lxml parsel selectolax extruct

# Para métricas del sistema (opcional)
pip install psutil

# Para desarrollo
pip install pytest pytest-asyncio
```

### Estructura del Proyecto

```
ai_video/
├── __init__.py
├── web_extract.py          # Extracción de contenido web
├── suggestions.py          # Generación de sugerencias de IA
├── video_generator.py      # Generación de videos
├── video_workflow.py       # Orquestador principal
├── state_repository.py     # Persistencia de estado
├── metrics.py             # Sistema de métricas
└── README.md              # Esta documentación
```

## ⚡ Uso Rápido

### Ejemplo Básico

```python
from ai_video.video_workflow import run_full_workflow

# Generar video desde una URL
async def create_video():
    state = await run_full_workflow(
        url="https://example.com/article",
        avatar="john",
        workflow_id="my-video-001"
    )
    
    print(f"Video generado: {state.video_url}")
    print(f"Tiempo total: {state.timings.total:.2f}s")

# Ejecutar
import asyncio
asyncio.run(create_video())
```

### Uso con CLI

```bash
# Iniciar un nuevo workflow
python video_workflow.py start https://example.com --avatar john

# Ver estado de un workflow
python video_workflow.py status workflow_abc123

# Listar todos los workflows
python video_workflow.py list

# Reanudar workflow interrumpido
python video_workflow.py resume workflow_abc123
```

## 🏗️ Arquitectura

### Componentes Principales

1. **WebContentExtractor**: Extrae contenido de URLs web
2. **SuggestionEngine**: Genera sugerencias de IA
3. **VideoGenerator**: Crea videos con avatares
4. **VideoWorkflow**: Orquesta todo el proceso
5. **StateRepository**: Persiste el estado del workflow
6. **MetricsCollector**: Recopila métricas de rendimiento

### Flujo de Trabajo

```
URL → Extracción → Sugerencias → Generación → Video Final
  ↓        ↓           ↓            ↓           ↓
Estado → Métricas → Persistencia → Hooks → Resultado
```

### Patrones de Diseño

- **Dependency Injection**: Componentes intercambiables
- **Strategy Pattern**: Múltiples extractores y generadores
- **Observer Pattern**: Hooks para eventos del workflow
- **Repository Pattern**: Persistencia de estado
- **Factory Pattern**: Creación de componentes

## 📚 API Reference

### VideoWorkflow

Clase principal para orquestar la generación de videos.

```python
class VideoWorkflow:
    def __init__(
        self,
        extractor: WebContentExtractor,
        suggestion_engine: SuggestionEngine,
        video_generator: VideoGenerator,
        state_repository: StateRepository,
        hooks: Optional[WorkflowHooks] = None
    )
    
    async def execute(
        self,
        url: str,
        workflow_id: str,
        avatar: Optional[str] = None,
        user_edits: Optional[Dict[str, Any]] = None
    ) -> WorkflowState
```

### WebContentExtractor

Extrae contenido de URLs web con múltiples estrategias.

```python
class WebContentExtractor:
    async def extract(self, url: str) -> Optional[ExtractedContent]
    def get_last_used_extractor(self) -> Optional[str]
    def get_extractor_stats(self) -> Dict[str, Any]
```

### SuggestionEngine

Genera sugerencias de IA para scripts, imágenes y estilos.

```python
class SuggestionEngine:
    async def generate_suggestions(
        self, 
        content: ExtractedContent
    ) -> ContentSuggestions
```

### VideoGenerator

Genera videos con avatares y voz en off.

```python
class VideoGenerator:
    async def generate_video(
        self,
        content: ExtractedContent,
        suggestions: ContentSuggestions,
        avatar: Optional[str] = None,
        user_edits: Optional[Dict[str, Any]] = None
    ) -> VideoGenerationResult
```

## 🖥️ CLI

### Comandos Disponibles

#### `start` - Iniciar nuevo workflow

```bash
python video_workflow.py start <URL> [opciones]

Opciones:
  --workflow-id ID    ID personalizado para el workflow
  --avatar NAME       Avatar a usar para el video
  --debug            Habilitar logging detallado

Ejemplos:
  python video_workflow.py start https://example.com
  python video_workflow.py start https://example.com --avatar john --workflow-id my-video
```

#### `resume` - Reanudar workflow

```bash
python video_workflow.py resume <WORKFLOW_ID> [opciones]

Ejemplo:
  python video_workflow.py resume workflow_abc123
```

#### `list` - Listar workflows

```bash
python video_workflow.py list

Muestra todos los workflows con su estado y metadatos.
```

#### `status` - Ver estado detallado

```bash
python video_workflow.py status <WORKFLOW_ID>

Muestra información detallada de un workflow específico.
```

#### `clean` - Limpiar workflows antiguos

```bash
python video_workflow.py clean [opciones]

Opciones:
  --days N           Limpiar workflows más antiguos que N días
  --force           Confirmar eliminación sin preguntar

Ejemplos:
  python video_workflow.py clean --days 7 --force
  python video_workflow.py clean --force  # Limpiar todos
```

## 📊 Métricas y Monitoreo

### Métricas Disponibles

- **Extractores**: Tasa de éxito, tiempo promedio, rendimiento por dominio
- **Generadores**: Tasa de éxito, tiempo promedio, calidad de videos
- **Workflows**: Tiempo total, tasa de éxito, tiempos por etapa
- **Sistema**: Uso de CPU/memoria, tasa de errores, workflows activos

### Comandos de Métricas

```bash
# Ver reporte completo de rendimiento
python metrics.py report

# Ver estadísticas en tiempo real
python metrics.py stats

# Limpiar métricas antiguas
python metrics.py cleanup --days 30
```

### Integración de Métricas

```python
from ai_video.metrics import (
    record_extraction_metrics,
    record_generation_metrics,
    record_workflow_metrics
)

# Las métricas se registran automáticamente en el workflow
# También puedes registrarlas manualmente:

record_extraction_metrics(
    extractor_name="newspaper3k",
    success=True,
    duration=2.5,
    domain="example.com"
)
```

## ⚙️ Configuración Avanzada

### Hooks Personalizados

```python
from ai_video.video_workflow import VideoWorkflow, WorkflowHooks

def on_extraction_complete(content):
    print(f"Contenido extraído: {content.title}")

def on_workflow_complete(state):
    print(f"Workflow completado: {state.video_url}")

hooks = WorkflowHooks(
    on_extraction_complete=on_extraction_complete,
    on_workflow_complete=on_workflow_complete
)

workflow = VideoWorkflow(
    extractor=extractor,
    suggestion_engine=suggestion_engine,
    video_generator=video_generator,
    state_repository=state_repository,
    hooks=hooks
)
```

### Extractores Personalizados

```python
from ai_video.web_extract import BaseExtractor

class CustomExtractor(BaseExtractor):
    name = "custom_extractor"
    priority = 1
    
    async def extract(self, url: str) -> Optional[ExtractedContent]:
        # Implementar lógica de extracción personalizada
        pass

# Registrar el extractor
extractor = WebContentExtractor()
extractor.register_extractor(CustomExtractor())
```

### Generadores Personalizados

```python
from ai_video.video_generator import BaseVideoGenerator

class CustomVideoGenerator(BaseVideoGenerator):
    name = "custom_generator"
    
    async def generate_video(self, content, suggestions, avatar=None, user_edits=None):
        # Implementar lógica de generación personalizada
        pass
```

## 🔧 Troubleshooting

### Problemas Comunes

#### Error de Extracción

```bash
# Verificar conectividad
curl -I https://example.com

# Habilitar debug
python video_workflow.py start https://example.com --debug
```

#### Workflow Interrumpido

```bash
# Ver workflows disponibles
python video_workflow.py list

# Reanudar workflow
python video_workflow.py resume <WORKFLOW_ID>
```

#### Problemas de Rendimiento

```bash
# Ver métricas de rendimiento
python metrics.py report

# Limpiar datos antiguos
python metrics.py cleanup --days 7
```

### Logs y Debugging

```python
import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Verificación de Estado

```python
from ai_video.state_repository import FileStateRepository

# Cargar estado manualmente
repo = FileStateRepository(directory='.workflow_state')
state = repo.load('workflow_id')

print(f"Estado: {state.status}")
print(f"Error: {state.error}")
```

## 🤝 Contribución

### Desarrollo Local

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar tests: `pytest tests/`
4. Crear feature branch
5. Implementar cambios
6. Ejecutar tests y linting
7. Crear Pull Request

### Estructura de Tests

```
tests/
├── test_web_extract.py
├── test_suggestions.py
├── test_video_generator.py
├── test_video_workflow.py
├── test_state_repository.py
└── test_metrics.py
```

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues**: Crear issue en GitHub
- **Documentación**: Ver esta documentación
- **Ejemplos**: Ver directorio `examples/`
- **Comunidad**: Unirse al Discord/Slack del proyecto

---

**¡Disfruta generando videos increíbles con IA! 🎬✨** 