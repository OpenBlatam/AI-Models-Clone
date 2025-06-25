# Onyx Features - Production Optimized System

## 🏗️ Arquitectura Enterprise

Este módulo proporciona una arquitectura enterprise completa optimizada para producción con las mejores librerías y patrones de diseño.

## 📁 Estructura del Proyecto

```
features/
├── __init__.py              # Módulo principal con factory patterns
├── config.py               # Configuración centralizada con pydantic + decouple
├── monitoring.py           # Sistema de monitoreo con Prometheus + Sentry
├── exceptions.py           # Manejo robusto de excepciones
├── utils.py               # Utilidades optimizadas con async support
├── requirements.txt       # Dependencias optimizadas para producción
├── image_process/         # Procesamiento de imágenes optimizado
│   ├── __init__.py
│   ├── validation.py      # Validación con magic bytes + pydantic
│   ├── extract.py         # Extracción optimizada
│   ├── image-sumary.py    # Procesamiento async con PIL optimizado
│   └── image-utils.py     # Utilidades de storage con retry logic
└── key_messages/          # Sistema de mensajes enterprise
    ├── __init__.py
    └── service.py         # Servicio async con caching + batch processing
```

## 🚀 Características de Producción

### ⚡ Performance Optimizations

- **Async/Await**: Soporte completo para operaciones asíncronas
- **Caching Multi-nivel**: TTL Cache, LRU Cache, Redis integration
- **Batch Processing**: Procesamiento en lotes con control de concurrencia
- **Connection Pooling**: Pool de conexiones optimizado para DB y Redis
- **Rate Limiting**: Control de límites de operaciones

### 📊 Monitoring & Observability

- **Prometheus Metrics**: Métricas detalladas de performance
- **Structured Logging**: Logs estructurados con correlación IDs
- **Health Checks**: Verificación de salud de servicios
- **Performance Tracking**: Seguimiento detallado de operaciones
- **Error Tracking**: Integración con Sentry para monitoreo de errores

### 🔒 Security & Reliability

- **Input Validation**: Validación robusta con pydantic
- **Retry Logic**: Reintentos con backoff exponencial
- **Circuit Breaker**: Protección contra fallos en cascada
- **Rate Limiting**: Control de tráfico
- **Error Handling**: Manejo centralizado de errores

### 🏭 Enterprise Features

- **Configuration Management**: Configuración por ambiente
- **Multi-environment Support**: Development, Staging, Production
- **Graceful Degradation**: Funcionamiento degradado en caso de fallas
- **Resource Management**: Manejo optimizado de recursos
- **Scalability**: Diseño para alta escalabilidad

## 📦 Librerías Principales

### Core Dependencies
```python
pydantic>=2.5.0           # Validación de datos
sqlalchemy>=2.0.0         # ORM optimizado
asyncio-pool>=0.7.0       # Pool de conexiones async
```

### Image Processing
```python
Pillow>=10.2.0            # Procesamiento de imágenes
opencv-python-headless    # Computer vision
pillow-heif>=0.13.0       # Formatos modernos (HEIF/AVIF)
python-magic>=0.4.27      # Detección de tipos MIME
```

### Monitoring & Performance
```python
prometheus-client>=0.19.0  # Métricas
structlog>=23.2.0         # Logging estructurado
sentry-sdk>=1.40.0        # Error tracking
psutil>=5.9.0             # System metrics
```

### Async & HTTP
```python
httpx>=0.26.0             # Cliente HTTP moderno
aiofiles>=23.2.1          # Archivos async
aioredis>=2.0.1           # Redis async
uvloop>=0.19.0            # Event loop optimizado
```

## 🔧 Configuración

### Variables de Entorno

```bash
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=secret

# Image Processing
IMG_MAX_FILE_SIZE_MB=100
IMG_MAX_VISION_SIZE_MB=20
IMG_ENABLE_OPTIMIZATION=true

# Monitoring
MONITORING_PROMETHEUS=true
SENTRY_DSN=https://your-sentry-dsn
METRICS_PORT=8000

# Security
SECRET_KEY=your-production-secret-key
JWT_ALGORITHM=HS256
```

## 📋 Uso

### Inicialización Básica

```python
from agents.backend.onyx.server.features import (
    get_config,
    create_key_message_service,
    validate_file_comprehensive,
    track_performance,
    monitor_operation
)

# Configuración
config = get_config()

# Servicios
message_service = create_key_message_service()

# Monitoreo
@track_performance("image_processing", "image_process")
async def process_image(image_data: bytes):
    async with monitor_operation("resize", "image_process"):
        # Tu lógica aquí
        pass
```

### Procesamiento de Imágenes

```python
from agents.backend.onyx.server.features.image_process import (
    validate_file_comprehensive,
    process_image_async,
    ValidationConfig
)

# Configuración personalizada
config = ValidationConfig(
    max_file_size_mb=50,
    strict_validation=True,
    use_magic_bytes=True
)

# Validación
result = validate_file_comprehensive(image_data, "image.jpg", config)
if result.is_valid:
    # Procesamiento
    processed_data, encoded = await process_image_async(image_data)
```

### Sistema de Mensajes

```python
from agents.backend.onyx.server.features.key_messages import (
    create_default_service,
    MessageType,
    MessagePriority
)

# Crear servicio
service = create_default_service()

# Crear mensaje
message = await service.create_message(
    content="Hello World",
    message_type=MessageType.HUMAN,
    priority=MessagePriority.NORMAL
)

# Procesamiento en lotes
batch = await service.create_batch([
    "Message 1",
    "Message 2",
    "Message 3"
])
```

## 📈 Métricas y Monitoreo

### Prometheus Metrics

- `onyx_requests_total` - Total de requests
- `onyx_request_duration_seconds` - Duración de requests
- `onyx_cache_operations_total` - Operaciones de cache
- `onyx_errors_total` - Total de errores
- `onyx_feature_usage_total` - Uso de features

### Health Checks

```bash
# Health check endpoint
GET /health

# Metrics endpoint  
GET /metrics

# Dashboard
GET /dashboard
```

## 🐳 Deployment

### Docker Support

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist

- [ ] Variables de entorno configuradas
- [ ] Secret keys cambiadas
- [ ] Base de datos configurada
- [ ] Redis configurado
- [ ] Monitoreo habilitado
- [ ] Logs centralizados
- [ ] Backups configurados
- [ ] SSL/TLS habilitado

## 🧪 Testing

```python
import pytest
from agents.backend.onyx.server.features import get_config

def test_config_loading():
    config = get_config()
    assert config.app_name == "Onyx Features"

@pytest.mark.asyncio
async def test_message_service():
    service = create_default_service()
    message = await service.create_message("Test")
    assert message.content == "Test"
```

## 📚 Mejores Prácticas

### 1. Error Handling
```python
from agents.backend.onyx.server.features.exceptions import (
    handle_exceptions,
    OnyxBaseException
)

@handle_exceptions
async def my_function():
    # Tu código aquí
    pass
```

### 2. Caching
```python
from agents.backend.onyx.server.features.utils import async_cached

@async_cached(ttl=3600)
async def expensive_operation(param: str):
    # Operación costosa
    return result
```

### 3. Configuration
```python
from agents.backend.onyx.server.features.config import get_config

config = get_config()
if config.environment == Environment.PRODUCTION:
    # Lógica específica de producción
    pass
```

## 🚀 Performance Tips

1. **Use async/await** para operaciones I/O
2. **Implementa caching** para operaciones costosas
3. **Usa batch processing** para múltiples elementos
4. **Monitorea métricas** constantemente
5. **Optimiza queries de DB** con índices apropiados
6. **Usa connection pooling** para DB y Redis
7. **Implementa rate limiting** para APIs públicas

## 🔧 Troubleshooting

### Problemas Comunes

**High Memory Usage**
- Verificar cache sizes
- Revisar memory leaks
- Optimizar batch sizes

**Slow Performance**
- Revisar métricas de Prometheus
- Analizar logs de performance
- Verificar DB queries

**Connection Issues**
- Verificar pool configurations
- Revisar network connectivity
- Analizar timeout settings

## 📞 Soporte

Para soporte técnico:
- Revisar logs en `/logs/`
- Consultar métricas en `/metrics`
- Verificar health checks en `/health`

---

**Versión**: 1.0.0
**Última actualización**: 2024
**Mantenido por**: Onyx Development Team 