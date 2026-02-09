# AI Continuous Document Generator - Documentación de API

## 1. Información General

### 1.1 Base URL
```
Producción: https://api.documentgenerator.com/v1
Desarrollo: https://dev-api.documentgenerator.com/v1
Local: http://localhost:3000/api/v1
```

### 1.2 Autenticación
Todas las APIs requieren autenticación mediante JWT Bearer Token:
```http
Authorization: Bearer <jwt-token>
```

### 1.3 Formato de Respuesta
```json
{
  "success": true,
  "data": {},
  "message": "Success message",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 1.4 Códigos de Estado HTTP
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

## 2. Autenticación

### 2.1 Registro de Usuario
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "firstName": "John",
  "lastName": "Doe",
  "company": "Acme Corp"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "user",
      "createdAt": "2024-01-15T10:30:00Z"
    },
    "tokens": {
      "accessToken": "jwt-access-token",
      "refreshToken": "jwt-refresh-token"
    }
  }
}
```

### 2.2 Inicio de Sesión
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "mfaToken": "123456" // Opcional para MFA
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "user",
      "mfaEnabled": true
    },
    "tokens": {
      "accessToken": "jwt-access-token",
      "refreshToken": "jwt-refresh-token"
    }
  }
}
```

### 2.3 Renovar Token
```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refreshToken": "jwt-refresh-token"
}
```

### 2.4 Configurar MFA
```http
POST /auth/mfa/setup
```

**Response:**
```json
{
  "success": true,
  "data": {
    "secret": "base32-secret",
    "qrCodeUrl": "data:image/png;base64,...",
    "backupCodes": ["code1", "code2", "code3"]
  }
}
```

## 3. Gestión de Documentos

### 3.1 Crear Documento
```http
POST /documents
```

**Request Body:**
```json
{
  "title": "Mi Documento",
  "template": "business-report",
  "content": "Contenido inicial del documento",
  "tags": ["importante", "reporte"],
  "isPublic": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "doc-uuid",
    "title": "Mi Documento",
    "content": "Contenido inicial del documento",
    "template": "business-report",
    "status": "draft",
    "tags": ["importante", "reporte"],
    "isPublic": false,
    "userId": "user-uuid",
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
  }
}
```

### 3.2 Obtener Documento
```http
GET /documents/{documentId}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "doc-uuid",
    "title": "Mi Documento",
    "content": "Contenido del documento",
    "template": "business-report",
    "status": "draft",
    "tags": ["importante", "reporte"],
    "isPublic": false,
    "userId": "user-uuid",
    "collaborators": [
      {
        "id": "user-uuid",
        "email": "collaborator@example.com",
        "role": "editor",
        "joinedAt": "2024-01-15T10:30:00Z"
      }
    ],
    "versions": [
      {
        "id": "version-uuid",
        "versionNumber": 1,
        "changesSummary": "Documento creado",
        "createdBy": "user-uuid",
        "createdAt": "2024-01-15T10:30:00Z"
      }
    ],
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
  }
}
```

### 3.3 Listar Documentos
```http
GET /documents?page=1&limit=20&search=reporte&template=business-report&status=draft
```

**Query Parameters:**
- `page` - Número de página (default: 1)
- `limit` - Elementos por página (default: 20, max: 100)
- `search` - Búsqueda en título y contenido
- `template` - Filtrar por plantilla
- `status` - Filtrar por estado
- `tags` - Filtrar por tags (separados por coma)
- `sortBy` - Campo para ordenar (title, createdAt, updatedAt)
- `sortOrder` - Orden (asc, desc)

**Response:**
```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "id": "doc-uuid",
        "title": "Mi Documento",
        "template": "business-report",
        "status": "draft",
        "tags": ["importante", "reporte"],
        "userId": "user-uuid",
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "totalPages": 1
    }
  }
}
```

### 3.4 Actualizar Documento
```http
PUT /documents/{documentId}
```

**Request Body:**
```json
{
  "title": "Mi Documento Actualizado",
  "content": "Contenido actualizado",
  "tags": ["importante", "reporte", "actualizado"],
  "status": "published"
}
```

### 3.5 Eliminar Documento
```http
DELETE /documents/{documentId}
```

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

## 4. Generación de Contenido con IA

### 4.1 Generar Contenido
```http
POST /documents/{documentId}/generate
```

**Request Body:**
```json
{
  "prompt": "Genera un resumen ejecutivo para este reporte",
  "template": "business-report",
  "context": "Información adicional del contexto",
  "options": {
    "tone": "professional",
    "length": "medium",
    "language": "es",
    "includeExamples": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "generatedContent": "Resumen ejecutivo generado por IA...",
    "metadata": {
      "model": "gpt-4",
      "tokensUsed": 150,
      "processingTime": 2.5,
      "confidence": 0.95
    }
  }
}
```

### 4.2 Generar Múltiples Opciones
```http
POST /documents/{documentId}/generate/options
```

**Request Body:**
```json
{
  "prompt": "Genera 3 versiones diferentes del párrafo de introducción",
  "count": 3,
  "variations": ["formal", "casual", "technical"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "options": [
      {
        "id": "option-1",
        "content": "Versión formal del contenido...",
        "style": "formal",
        "confidence": 0.92
      },
      {
        "id": "option-2",
        "content": "Versión casual del contenido...",
        "style": "casual",
        "confidence": 0.88
      },
      {
        "id": "option-3",
        "content": "Versión técnica del contenido...",
        "style": "technical",
        "confidence": 0.95
      }
    ]
  }
}
```

### 4.3 Mejorar Contenido Existente
```http
POST /documents/{documentId}/improve
```

**Request Body:**
```json
{
  "content": "Contenido a mejorar",
  "improvementType": "grammar", // grammar, clarity, conciseness, style
  "options": {
    "preserveOriginal": true,
    "suggestions": true
  }
}
```

## 5. Colaboración

### 5.1 Invitar Colaborador
```http
POST /documents/{documentId}/collaborators
```

**Request Body:**
```json
{
  "email": "collaborator@example.com",
  "role": "editor", // viewer, editor, admin
  "message": "Te invito a colaborar en este documento"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "invitation": {
      "id": "invitation-uuid",
      "email": "collaborator@example.com",
      "role": "editor",
      "status": "pending",
      "expiresAt": "2024-01-22T10:30:00Z"
    }
  }
}
```

### 5.2 Listar Colaboradores
```http
GET /documents/{documentId}/collaborators
```

**Response:**
```json
{
  "success": true,
  "data": {
    "collaborators": [
      {
        "id": "user-uuid",
        "email": "collaborator@example.com",
        "firstName": "Jane",
        "lastName": "Doe",
        "role": "editor",
        "status": "active",
        "joinedAt": "2024-01-15T10:30:00Z",
        "lastActive": "2024-01-15T12:00:00Z"
      }
    ]
  }
}
```

### 5.3 Actualizar Rol de Colaborador
```http
PUT /documents/{documentId}/collaborators/{userId}
```

**Request Body:**
```json
{
  "role": "admin"
}
```

### 5.4 Remover Colaborador
```http
DELETE /documents/{documentId}/collaborators/{userId}
```

## 6. Plantillas

### 6.1 Listar Plantillas Disponibles
```http
GET /templates
```

**Response:**
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "id": "business-report",
        "name": "Informe Empresarial",
        "description": "Plantilla para informes empresariales",
        "category": "business",
        "fields": [
          {
            "name": "executiveSummary",
            "label": "Resumen Ejecutivo",
            "type": "text",
            "required": true
          },
          {
            "name": "recommendations",
            "label": "Recomendaciones",
            "type": "list",
            "required": false
          }
        ],
        "preview": "Vista previa de la plantilla...",
        "createdAt": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

### 6.2 Obtener Plantilla
```http
GET /templates/{templateId}
```

### 6.3 Crear Plantilla Personalizada
```http
POST /templates
```

**Request Body:**
```json
{
  "name": "Mi Plantilla Personalizada",
  "description": "Descripción de la plantilla",
  "category": "custom",
  "content": "Contenido de la plantilla con {{variables}}",
  "fields": [
    {
      "name": "title",
      "label": "Título",
      "type": "text",
      "required": true
    }
  ]
}
```

## 7. Exportación

### 7.1 Exportar a PDF
```http
POST /documents/{documentId}/export/pdf
```

**Request Body:**
```json
{
  "options": {
    "format": "A4",
    "orientation": "portrait",
    "margins": "normal",
    "includeHeader": true,
    "includeFooter": true,
    "watermark": "DRAFT"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "downloadUrl": "https://api.documentgenerator.com/downloads/pdf-uuid",
    "expiresAt": "2024-01-15T11:30:00Z"
  }
}
```

### 7.2 Exportar a Word
```http
POST /documents/{documentId}/export/word
```

### 7.3 Exportar a HTML
```http
POST /documents/{documentId}/export/html
```

## 8. WebSocket para Colaboración en Tiempo Real

### 8.1 Conexión WebSocket
```javascript
const ws = new WebSocket('wss://api.documentgenerator.com/ws', {
  headers: {
    'Authorization': 'Bearer <jwt-token>'
  }
});
```

### 8.2 Eventos de Colaboración

#### Unirse a Documento
```json
{
  "type": "join_document",
  "documentId": "doc-uuid"
}
```

#### Cambio de Contenido
```json
{
  "type": "content_change",
  "documentId": "doc-uuid",
  "content": "Nuevo contenido",
  "position": 100,
  "userId": "user-uuid",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Posición del Cursor
```json
{
  "type": "cursor_position",
  "documentId": "doc-uuid",
  "position": 150,
  "userId": "user-uuid"
}
```

#### Usuario Conectado
```json
{
  "type": "user_joined",
  "documentId": "doc-uuid",
  "user": {
    "id": "user-uuid",
    "name": "John Doe",
    "color": "#FF5733"
  }
}
```

#### Usuario Desconectado
```json
{
  "type": "user_left",
  "documentId": "doc-uuid",
  "userId": "user-uuid"
}
```

## 9. Webhooks

### 9.1 Configurar Webhook
```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["document.created", "document.updated", "document.deleted"],
  "secret": "webhook-secret-key"
}
```

### 9.2 Eventos de Webhook

#### Documento Creado
```json
{
  "event": "document.created",
  "data": {
    "document": {
      "id": "doc-uuid",
      "title": "Mi Documento",
      "userId": "user-uuid",
      "createdAt": "2024-01-15T10:30:00Z"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Documento Actualizado
```json
{
  "event": "document.updated",
  "data": {
    "document": {
      "id": "doc-uuid",
      "title": "Mi Documento Actualizado",
      "userId": "user-uuid",
      "updatedAt": "2024-01-15T10:30:00Z"
    },
    "changes": {
      "title": "Mi Documento Actualizado",
      "content": "Contenido actualizado"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 10. Rate Limiting

### 10.1 Límites por Endpoint
- **Autenticación**: 5 requests/minuto por IP
- **Generación de IA**: 10 requests/minuto por usuario
- **Documentos**: 100 requests/minuto por usuario
- **General**: 1000 requests/minuto por IP

### 10.2 Headers de Rate Limiting
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## 11. SDKs y Ejemplos

### 11.1 JavaScript SDK
```javascript
import { DocumentGenerator } from '@documentgenerator/sdk';

const client = new DocumentGenerator({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.documentgenerator.com/v1'
});

// Crear documento
const document = await client.documents.create({
  title: 'Mi Documento',
  template: 'business-report'
});

// Generar contenido
const content = await client.documents.generate(document.id, {
  prompt: 'Genera un resumen ejecutivo'
});
```

### 11.2 Python SDK
```python
from documentgenerator import DocumentGenerator

client = DocumentGenerator(api_key='your-api-key')

# Crear documento
document = client.documents.create(
    title='Mi Documento',
    template='business-report'
)

# Generar contenido
content = client.documents.generate(
    document_id=document.id,
    prompt='Genera un resumen ejecutivo'
)
```

### 11.3 cURL Ejemplos
```bash
# Crear documento
curl -X POST https://api.documentgenerator.com/v1/documents \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Documento",
    "template": "business-report",
    "content": "Contenido inicial"
  }'

# Generar contenido
curl -X POST https://api.documentgenerator.com/v1/documents/doc-uuid/generate \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Genera un resumen ejecutivo",
    "template": "business-report"
  }'
```

Esta documentación de API proporciona una guía completa para integrar y usar el sistema de generación de documentos con IA.







