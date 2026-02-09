# IA Generadora Continua de Documentos

## 📋 Descripción

Sistema de Inteligencia Artificial que genera múltiples documentos técnicos relacionados de forma continua a partir de una sola petición inicial. El sistema mantiene coherencia entre documentos, valida calidad automáticamente y proporciona seguimiento en tiempo real del progreso de generación.

## 🎯 Características Principales

### ✨ Generación Continua
- **Una sola petición** → **Múltiples documentos relacionados**
- Generación paralela para máxima eficiencia
- Coherencia inter-documental automática
- Validación de calidad en tiempo real

### 📚 Tipos de Documentos Soportados
- **Especificaciones Técnicas** - Documentos técnicos detallados
- **Documentación de API** - APIs REST completas
- **Guías de Implementación** - Pasos detallados de implementación
- **Casos de Prueba** - Tests unitarios e integración
- **Manuales de Usuario** - Documentación para usuarios finales
- **Diagramas de Arquitectura** - Representaciones visuales
- **Análisis de Seguridad** - Evaluaciones de seguridad
- **Guías de Despliegue** - Procesos de deployment
- **Troubleshooting** - Resolución de problemas

### 🔧 Características Avanzadas
- **Coherencia Automática** - Terminología unificada entre documentos
- **Referencias Cruzadas** - Enlaces automáticos entre documentos relacionados
- **Validación de Calidad** - Scoring automático de calidad y coherencia
- **Progreso en Tiempo Real** - WebSocket para seguimiento en vivo
- **Almacenamiento Estructurado** - Organización automática de archivos
- **Múltiples Proveedores IA** - Soporte para OpenAI, Anthropic, etc.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Document Generator                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Request   │  │   Context   │  │  Template   │        │
│  │  Processor  │  │  Manager    │  │   Engine    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Content   │  │   Quality   │  │   Output    │        │
│  │  Generator  │  │  Validator  │  │  Manager    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Storage   │  │   API       │  │  Monitoring │        │
│  │   System    │  │  Gateway    │  │   System    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```
ai-document-generator/
├── 📄 AI_CONTINUOUS_DOCUMENT_GENERATOR_SPECIFICATIONS.md
├── 📄 AI_CONTINUOUS_DOCUMENT_GENERATOR_IMPLEMENTATION_GUIDE.md
├── 📄 AI_CONTINUOUS_DOCUMENT_GENERATOR_EXAMPLE.py
├── 📄 AI_CONTINUOUS_DOCUMENT_GENERATOR_README.md
├── 📁 app/
│   ├── 📁 core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── 📁 models/
│   │   ├── document.py
│   │   ├── generation.py
│   │   └── user.py
│   ├── 📁 services/
│   │   ├── generator.py
│   │   ├── coherence.py
│   │   ├── quality.py
│   │   └── storage.py
│   ├── 📁 api/
│   │   ├── endpoints.py
│   │   ├── websocket.py
│   │   └── middleware.py
│   └── 📁 templates/
│       ├── technical_spec.md
│       ├── api_documentation.md
│       └── implementation_guide.md
├── 📁 tests/
├── 📁 docker/
├── 📁 docs/
├── 📄 requirements.txt
├── 📄 docker-compose.yml
└── 📄 README.md
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.9+
- Docker y Docker Compose
- API Key de OpenAI o Anthropic (opcional para demo)

### Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd ai-document-generator

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 4. Ejecutar con Docker
docker-compose up -d

# 5. O ejecutar directamente
python AI_CONTINUOUS_DOCUMENT_GENERATOR_EXAMPLE.py
```

### Variables de Entorno

```bash
# Configuración de IA
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Configuración de Base de Datos
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# Configuración de Almacenamiento
STORAGE_BACKEND=local
STORAGE_PATH=/app/storage

# Configuración de API
API_HOST=0.0.0.0
API_PORT=8000
```

## 💻 Uso Básico

### Ejemplo Simple

```python
import asyncio
from app.models.generation import ContinuousGenerationRequest
from app.models.document import DocumentType
from app.services.generator import ContinuousDocumentGenerator

async def generate_docs():
    # Crear petición
    request = ContinuousGenerationRequest(
        query="Genera documentación para una API REST de gestión de usuarios",
        document_types=[
            DocumentType.API_DOCUMENTATION,
            DocumentType.TECHNICAL_SPEC,
            DocumentType.IMPLEMENTATION_GUIDE
        ],
        max_documents=3
    )
    
    # Generar documentos
    generator = ContinuousDocumentGenerator()
    async with generator:
        documents = await generator.generate_continuous_documents(request)
    
    # Guardar documentos
    await generator.save_documents(documents, "output/")
    
    return documents

# Ejecutar
asyncio.run(generate_docs())
```

### API REST

```bash
# Generar documentos
curl -X POST "http://localhost:8000/api/continuous-generate/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Genera documentación para un sistema de microservicios",
    "document_types": ["technical_specification", "api_documentation"],
    "max_documents": 2
  }'

# Obtener plantillas disponibles
curl "http://localhost:8000/api/continuous-generate/templates"

# Obtener estadísticas
curl "http://localhost:8000/api/continuous-generate/stats"
```

### WebSocket para Progreso en Tiempo Real

```javascript
const ws = new WebSocket('ws://localhost:8000/api/continuous-generate/ws/continuous-generate');

ws.onopen = function() {
    // Enviar petición
    ws.send(JSON.stringify({
        query: "Genera documentación para una API REST",
        document_types: ["api_documentation", "technical_spec"],
        max_documents: 2
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'progress') {
        console.log(`Progreso: ${data.progress}% - ${data.message}`);
    } else if (data.type === 'document_complete') {
        console.log(`Documento completado: ${data.document.title}`);
    } else if (data.type === 'complete') {
        console.log('Generación completada!');
    }
};
```

## 📊 Ejemplos de Uso

### 1. Documentación de API REST

```python
request = ContinuousGenerationRequest(
    query="Genera documentación completa para una API REST de gestión de usuarios con autenticación JWT, operaciones CRUD, y sistema de roles",
    document_types=[
        DocumentType.TECHNICAL_SPEC,
        DocumentType.API_DOCUMENTATION,
        DocumentType.IMPLEMENTATION_GUIDE,
        DocumentType.TEST_CASES,
        DocumentType.SECURITY_ANALYSIS
    ],
    context={
        "framework": "FastAPI",
        "database": "PostgreSQL",
        "authentication": "JWT"
    }
)
```

**Resultado**: 5 documentos coherentes y relacionados:
- Especificación Técnica del sistema
- Documentación completa de la API
- Guía de implementación paso a paso
- Casos de prueba unitarios e integración
- Análisis de seguridad y mejores prácticas

### 2. Arquitectura de Microservicios

```python
request = ContinuousGenerationRequest(
    query="Crea documentación para una arquitectura de microservicios con API Gateway, service mesh, y base de datos distribuida",
    document_types=[
        DocumentType.ARCHITECTURE_DIAGRAM,
        DocumentType.TECHNICAL_SPEC,
        DocumentType.IMPLEMENTATION_GUIDE,
        DocumentType.DEPLOYMENT_GUIDE,
        DocumentType.PERFORMANCE_REPORT
    ],
    context={
        "pattern": "microservices",
        "gateway": "Kong",
        "service_mesh": "Istio",
        "database": "CockroachDB"
    }
)
```

**Resultado**: 5 documentos especializados:
- Diagrama de arquitectura detallado
- Especificación técnica completa
- Guía de implementación
- Proceso de despliegue
- Análisis de rendimiento

### 3. Sistema de E-commerce

```python
request = ContinuousGenerationRequest(
    query="Genera documentación para un sistema de e-commerce con carrito de compras, procesamiento de pagos, y gestión de inventario",
    document_types=[
        DocumentType.TECHNICAL_SPEC,
        DocumentType.API_DOCUMENTATION,
        DocumentType.USER_MANUAL,
        DocumentType.TEST_CASES,
        DocumentType.SECURITY_ANALYSIS
    ]
)
```

## 🔧 Configuración Avanzada

### Personalización de Plantillas

```python
# Crear plantilla personalizada
custom_template = """
# {title}

## Introducción Personalizada
{introduction}

## Sección Específica
{custom_section}

## Conclusión
{conclusion}
"""

# Usar en generación
request.custom_requirements = {
    "template": custom_template,
    "custom_section": "Contenido específico del dominio"
}
```

### Configuración de Calidad

```python
# Ajustar umbrales de calidad
generator = ContinuousDocumentGenerator()
generator.quality_threshold = 0.8  # Más estricto
generator.coherence_threshold = 0.9  # Mayor coherencia requerida
```

### Múltiples Proveedores IA

```python
# Usar diferentes proveedores
openai_generator = ContinuousDocumentGenerator(ai_provider="openai")
anthropic_generator = ContinuousDocumentGenerator(ai_provider="anthropic")
mock_generator = ContinuousDocumentGenerator(ai_provider="mock")  # Para testing
```

## 📈 Monitoreo y Métricas

### Métricas Disponibles

- **Tiempo de Generación** - Duración total del proceso
- **Calidad Promedio** - Score de calidad de documentos
- **Coherencia** - Nivel de coherencia entre documentos
- **Tasa de Éxito** - Porcentaje de generaciones exitosas
- **Tipos Populares** - Documentos más solicitados

### Dashboard de Monitoreo

```bash
# Acceder a métricas
curl "http://localhost:8000/api/continuous-generate/stats"

# Prometheus metrics
curl "http://localhost:8000/metrics"

# Grafana dashboard
open "http://localhost:3000"
```

## 🧪 Testing

### Tests Unitarios

```bash
# Ejecutar tests
pytest tests/

# Con cobertura
pytest --cov=app tests/

# Tests específicos
pytest tests/test_generator.py -v
```

### Tests de Integración

```bash
# Tests de API
pytest tests/test_integration.py

# Tests de WebSocket
pytest tests/test_websocket.py
```

## 🚀 Despliegue

### Docker

```bash
# Construir imagen
docker build -t ai-document-generator .

# Ejecutar contenedor
docker run -p 8000:8000 ai-document-generator
```

### Docker Compose

```bash
# Despliegue completo
docker-compose up -d

# Ver logs
docker-compose logs -f

# Escalar
docker-compose up -d --scale ai-document-generator=3
```

### Kubernetes

```bash
# Aplicar configuración
kubectl apply -f k8s/

# Verificar despliegue
kubectl get pods

# Escalar
kubectl scale deployment ai-document-generator --replicas=5
```

## 🔒 Seguridad

### Autenticación

```python
# Configurar autenticación
from app.core.security import get_current_user

@router.post("/generate")
async def generate_docs(
    request: ContinuousGenerationRequest,
    current_user = Depends(get_current_user)
):
    # Solo usuarios autenticados pueden generar documentos
    pass
```

### Rate Limiting

```python
# Configurar límites
from app.core.rate_limiter import RateLimiter

rate_limiter = RateLimiter(
    requests_per_minute=10,
    requests_per_hour=100
)
```

### Validación de Contenido

```python
# Filtrar contenido sensible
from app.core.content_filter import ContentFilter

content_filter = ContentFilter()
if not content_filter.is_safe(request.query):
    raise HTTPException(status_code=400, detail="Contenido no permitido")
```

## 📚 Documentación Adicional

### Especificaciones Técnicas Completas
- [Especificaciones Técnicas](./AI_CONTINUOUS_DOCUMENT_GENERATOR_SPECIFICATIONS.md)
- [Guía de Implementación](./AI_CONTINUOUS_DOCUMENT_GENERATOR_IMPLEMENTATION_GUIDE.md)

### Ejemplos Prácticos
- [Ejemplo Completo](./AI_CONTINUOUS_DOCUMENT_GENERATOR_EXAMPLE.py)

### API Reference
- [Endpoints REST](./docs/api/endpoints.md)
- [WebSocket API](./docs/api/websocket.md)
- [Modelos de Datos](./docs/api/models.md)

## 🤝 Contribución

### Cómo Contribuir

1. **Fork** el repositorio
2. **Crear** una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crear** un Pull Request

### Estándares de Código

```bash
# Formatear código
black app/
isort app/

# Linting
flake8 app/
mypy app/

# Tests
pytest tests/ --cov=app
```

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

### Problemas Comunes

**Q: ¿Cómo configuro mi API key de OpenAI?**
A: Agrega `OPENAI_API_KEY=tu_key` en tu archivo `.env`

**Q: ¿Por qué falla la generación?**
A: Verifica que tu API key sea válida y que tengas créditos disponibles

**Q: ¿Cómo personalizo las plantillas?**
A: Modifica los archivos en `app/templates/` o usa `custom_requirements`

### Contacto

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@blatam-academy.com

## 🎉 Agradecimientos

- **OpenAI** por la API de GPT
- **Anthropic** por Claude API
- **FastAPI** por el framework web
- **Comunidad** de desarrolladores que contribuyen

---

**Desarrollado con ❤️ por Blatam Academy**

*Sistema de Especificaciones Técnicas - Versión 1.0.0*


















