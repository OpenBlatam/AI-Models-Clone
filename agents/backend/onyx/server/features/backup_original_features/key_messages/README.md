# Key Messages Feature

Este módulo proporciona funcionalidades para generar y analizar mensajes clave utilizando inteligencia artificial.

## Características

- **Generación de mensajes**: Crea mensajes optimizados basados en tipo, tono y contexto
- **Análisis de mensajes**: Analiza mensajes existentes para obtener insights
- **Procesamiento por lotes**: Procesa múltiples mensajes de forma eficiente
- **Caché inteligente**: Almacena respuestas para mejorar el rendimiento
- **Múltiples tipos de mensaje**: Marketing, educativo, promocional, informativo, etc.
- **Variedad de tonos**: Profesional, casual, amigable, autoritario, conversacional

## Endpoints

### Generación de mensajes

#### POST `/key-messages/generate`
Genera un mensaje optimizado basado en los parámetros proporcionados.

**Request Body:**
```json
{
  "message": "Texto original del mensaje",
  "message_type": "marketing",
  "tone": "professional",
  "target_audience": "Profesionales de marketing",
  "context": "Campaña de lanzamiento de producto",
  "keywords": ["innovación", "tecnología", "futuro"],
  "max_length": 200,
  "industry": "Tecnología",
  "call_to_action": "Regístrate ahora"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "original_message": "Texto original",
    "response": "Mensaje generado optimizado",
    "message_type": "marketing",
    "tone": "professional",
    "created_at": "2024-01-01T00:00:00",
    "word_count": 45,
    "character_count": 250,
    "keywords_used": ["innovación", "tecnología"],
    "sentiment_score": 0.8,
    "readability_score": 0.9,
    "processing_time": 0.5,
    "suggestions": []
  },
  "processing_time": 0.5
}
```

### Análisis de mensajes

#### POST `/key-messages/analyze`
Analiza un mensaje y proporciona insights sobre su efectividad.

**Request Body:** (mismo formato que generate)

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "original_message": "Mensaje original",
    "response": "Análisis detallado del mensaje...",
    "message_type": "marketing",
    "tone": "professional",
    "created_at": "2024-01-01T00:00:00",
    "word_count": 25,
    "character_count": 150,
    "keywords_used": ["palabra1", "palabra2"],
    "sentiment_score": 0.7,
    "readability_score": 0.8,
    "processing_time": 0.3,
    "suggestions": ["Sugerencia 1", "Sugerencia 2"]
  },
  "processing_time": 0.3,
  "metadata": {
    "analysis": true
  }
}
```

### Procesamiento por lotes

#### POST `/key-messages/batch`
Procesa múltiples mensajes de forma eficiente.

**Request Body:**
```json
{
  "messages": [
    {
      "message": "Mensaje 1",
      "message_type": "marketing",
      "tone": "professional"
    },
    {
      "message": "Mensaje 2",
      "message_type": "educational",
      "tone": "friendly"
    }
  ],
  "batch_size": 10
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "success": true,
      "data": { /* GeneratedResponse */ },
      "processing_time": 0.5
    }
  ],
  "total_processed": 2,
  "failed_count": 0,
  "processing_time": 1.2
}
```

### Endpoints de utilidad

#### GET `/key-messages/types`
Obtiene los tipos de mensaje disponibles.

#### GET `/key-messages/tones`
Obtiene los tonos disponibles.

#### DELETE `/key-messages/cache`
Limpia el caché de respuestas.

#### GET `/key-messages/cache/stats`
Obtiene estadísticas del caché.

#### GET `/key-messages/health`
Verifica el estado del servicio.

## Tipos de mensaje

- `marketing`: Mensajes promocionales y de marketing
- `educational`: Contenido educativo e informativo
- `promotional`: Promociones y ofertas especiales
- `informational`: Información general y noticias
- `call_to_action`: Llamadas a la acción
- `social_media`: Contenido para redes sociales
- `email`: Mensajes para correo electrónico
- `website`: Contenido para sitios web

## Tonos disponibles

- `professional`: Formal y profesional
- `casual`: Informal y relajado
- `friendly`: Amigable y cercano
- `authoritative`: Autoritario y confiable
- `conversational`: Conversacional y natural
- `enthusiastic`: Entusiasta y motivador
- `urgent`: Urgente y apremiante
- `calm`: Tranquilo y sereno

## Configuración

El módulo se puede configurar mediante variables de entorno:

```bash
# Configuración de caché
KEY_MESSAGES_CACHE_TTL_HOURS=24
KEY_MESSAGES_CACHE_MAX_SIZE=1000

# Configuración de LLM
KEY_MESSAGES_LLM_PROVIDER=deepseek
KEY_MESSAGES_LLM_MODEL=deepseek-chat
KEY_MESSAGES_LLM_MAX_TOKENS=2000
KEY_MESSAGES_LLM_TEMPERATURE=0.7

# Configuración de procesamiento por lotes
KEY_MESSAGES_MAX_BATCH_SIZE=50
KEY_MESSAGES_BATCH_TIMEOUT_SECONDS=300

# Límites de tasa
KEY_MESSAGES_RATE_LIMIT_REQUESTS_PER_MINUTE=100
KEY_MESSAGES_RATE_LIMIT_BURST_SIZE=20

# Configuración de logging
KEY_MESSAGES_LOG_LEVEL=INFO

# Flags de características
KEY_MESSAGES_ENABLE_CACHING=true
KEY_MESSAGES_ENABLE_BATCH_PROCESSING=true
KEY_MESSAGES_ENABLE_ANALYSIS=true
KEY_MESSAGES_ENABLE_LEGACY_ENDPOINTS=true
```

## Uso en el código

```python
from onyx.server.features.key_messages.service import KeyMessageService
from onyx.server.features.key_messages.models import KeyMessageRequest, MessageType, MessageTone

# Inicializar servicio
service = KeyMessageService()

# Crear request
request = KeyMessageRequest(
    message="Nuestro nuevo producto revoluciona la industria",
    message_type=MessageType.MARKETING,
    tone=MessageTone.PROFESSIONAL,
    target_audience="Profesionales de tecnología",
    keywords=["innovación", "revolución", "tecnología"]
)

# Generar respuesta
response = await service.generate_response(request)

# Analizar mensaje
analysis = await service.analyze_message(request)
```

## Características avanzadas

### Caché inteligente
- Almacena respuestas generadas para mejorar el rendimiento
- TTL configurable (por defecto 24 horas)
- Limpieza automática de entradas expiradas

### Procesamiento concurrente
- Procesamiento asíncrono de múltiples mensajes
- Control de concurrencia para evitar sobrecarga
- Timeouts configurables

### Análisis de sentimiento
- Evaluación automática del sentimiento del mensaje
- Puntuación de legibilidad
- Sugerencias de mejora

### Endpoints legacy
- Compatibilidad con versiones anteriores
- Autenticación básica para endpoints legacy
- Migración gradual a nuevos endpoints

## Monitoreo y métricas

El módulo incluye:
- Logging detallado de todas las operaciones
- Métricas de rendimiento y tiempo de respuesta
- Estadísticas de caché
- Endpoint de health check
- Manejo de errores robusto

## Seguridad

- Autenticación de usuarios para endpoints principales
- Validación de entrada en todos los endpoints
- Límites de tasa para prevenir abuso
- Sanitización de datos de entrada
- Logging de auditoría para operaciones sensibles 