# 📚 Referencia de API - AI Search Model

## 🔗 Endpoints Base

**URL Base**: `http://localhost:8000`

## 📋 Endpoints Disponibles

### 🏥 Health Check
```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "services": {
    "search_engine": "active",
    "vector_database": "active",
    "document_processor": "active"
  },
  "timestamp": "2025-01-13T21:18:00"
}
```

---

### 🔍 Búsqueda de Documentos
```http
POST /search
```

**Parámetros:**
```json
{
  "query": "string (requerido)",
  "search_type": "semantic|keyword|hybrid (opcional, default: semantic)",
  "limit": "integer (opcional, default: 10, max: 100)",
  "filters": {
    "document_type": "string (opcional)",
    "category": "string (opcional)",
    "tags": ["array de strings (opcional)"]
  }
}
```

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "inteligencia artificial",
    "search_type": "semantic",
    "limit": 5,
    "filters": {
      "document_type": "text"
    }
  }'
```

**Respuesta:**
```json
{
  "results": [
    {
      "document_id": "doc_abc123",
      "title": "Introducción a la IA",
      "content": "Contenido completo...",
      "score": 0.95,
      "metadata": {
        "category": "tecnologia",
        "tags": ["IA", "inteligencia artificial"]
      },
      "snippet": "La inteligencia artificial es...",
      "search_type": "semantic",
      "semantic_score": 0.95,
      "keyword_score": 0.0
    }
  ],
  "total_results": 1,
  "query": "inteligencia artificial",
  "search_time": 0.123,
  "timestamp": "2025-01-13T21:18:00"
}
```

---

### 📄 Gestión de Documentos

#### Crear/Indexar Documento
```http
POST /documents
```

**Parámetros:**
```json
{
  "title": "string (requerido)",
  "content": "string (requerido)",
  "document_type": "text|markdown|html|json (opcional, default: text)",
  "metadata": {
    "category": "string (opcional)",
    "tags": ["array de strings (opcional)"],
    "author": "string (opcional)"
  }
}
```

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Documento",
    "content": "Contenido del documento...",
    "document_type": "text",
    "metadata": {
      "category": "ejemplo",
      "tags": ["test", "demo"]
    }
  }'
```

**Respuesta:**
```json
{
  "document_id": "doc_abc123",
  "status": "success",
  "message": "Documento indexado correctamente"
}
```

#### Obtener Documento
```http
GET /documents/{document_id}
```

**Ejemplo:**
```bash
curl "http://localhost:8000/documents/doc_abc123"
```

**Respuesta:**
```json
{
  "document_id": "doc_abc123",
  "title": "Mi Documento",
  "content": "Contenido del documento...",
  "original_content": "Contenido original...",
  "document_type": "text",
  "metadata": {
    "category": "ejemplo",
    "tags": ["test", "demo"]
  },
  "created_at": "2025-01-13T21:18:00",
  "updated_at": "2025-01-13T21:18:00",
  "content_length": 150,
  "word_count": 25
}
```

#### Listar Documentos
```http
GET /documents?limit=10&offset=0
```

**Parámetros de Query:**
- `limit`: Número de documentos (default: 10, max: 100)
- `offset`: Desplazamiento para paginación (default: 0)

**Ejemplo:**
```bash
curl "http://localhost:8000/documents?limit=5&offset=0"
```

**Respuesta:**
```json
{
  "documents": [
    {
      "document_id": "doc_abc123",
      "title": "Mi Documento",
      "document_type": "text",
      "created_at": "2025-01-13T21:18:00",
      "content_length": 150,
      "word_count": 25
    }
  ],
  "total_count": 1,
  "limit": 5,
  "offset": 0
}
```

#### Eliminar Documento
```http
DELETE /documents/{document_id}
```

**Ejemplo:**
```bash
curl -X DELETE "http://localhost:8000/documents/doc_abc123"
```

**Respuesta:**
```json
{
  "message": "Documento eliminado correctamente"
}
```

---

### 📊 Estadísticas del Sistema
```http
GET /stats
```

**Ejemplo:**
```bash
curl "http://localhost:8000/stats"
```

**Respuesta:**
```json
{
  "total_documents": 150,
  "total_embeddings": 150,
  "documents_by_type": {
    "text": 100,
    "markdown": 30,
    "html": 20
  },
  "average_content_length": 2500.5,
  "average_word_count": 450.2,
  "database_size_bytes": 1024000,
  "embeddings_size_bytes": 2048000,
  "last_updated": "2025-01-13T21:18:00"
}
```

---

## 🔧 Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| `200` | OK - Solicitud exitosa |
| `201` | Created - Documento creado |
| `400` | Bad Request - Parámetros inválidos |
| `404` | Not Found - Recurso no encontrado |
| `422` | Unprocessable Entity - Error de validación |
| `500` | Internal Server Error - Error del servidor |
| `503` | Service Unavailable - Servicio no disponible |

---

## 🚨 Manejo de Errores

### Formato de Error
```json
{
  "detail": "Descripción del error"
}
```

### Errores Comunes

#### 400 - Bad Request
```json
{
  "detail": "Solicitud inválida"
}
```

#### 404 - Not Found
```json
{
  "detail": "Documento no encontrado"
}
```

#### 422 - Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 - Internal Server Error
```json
{
  "detail": "Error interno del servidor"
}
```

---

## 🔐 Autenticación (Opcional)

Si `API_KEY_REQUIRED=true` en la configuración:

```bash
curl -H "Authorization: Bearer tu_api_key" \
  "http://localhost:8000/search"
```

---

## 📝 Ejemplos de Uso

### Búsqueda Básica
```bash
# Búsqueda semántica simple
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning"}'
```

### Búsqueda con Filtros
```bash
# Buscar solo documentos de tipo markdown
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python",
    "search_type": "hybrid",
    "limit": 20,
    "filters": {
      "document_type": "markdown"
    }
  }'
```

### Indexar Múltiples Documentos
```bash
# Script para indexar varios documentos
for file in *.txt; do
  curl -X POST "http://localhost:8000/documents" \
    -H "Content-Type: application/json" \
    -d "{
      \"title\": \"$(basename $file .txt)\",
      \"content\": \"$(cat $file)\",
      \"document_type\": \"text\"
    }"
done
```

### Monitoreo del Sistema
```bash
# Verificar estado cada 30 segundos
while true; do
  curl -s "http://localhost:8000/health" | jq '.status'
  sleep 30
done
```

---

## 🧪 Testing de la API

### Con curl
```bash
# Test completo
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}' \
  -w "Tiempo: %{time_total}s\n"
```

### Con Python
```python
import requests

# Búsqueda
response = requests.post('http://localhost:8000/search', json={
    'query': 'inteligencia artificial',
    'search_type': 'semantic',
    'limit': 5
})

print(response.json())
```

### Con JavaScript
```javascript
// Búsqueda
const response = await fetch('http://localhost:8000/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'inteligencia artificial',
    search_type: 'semantic',
    limit: 5
  })
});

const data = await response.json();
console.log(data);
```

---

## 📖 Documentación Interactiva

Visita `http://localhost:8000/docs` para la documentación interactiva de Swagger UI donde puedes probar todos los endpoints directamente desde el navegador.



























