# Image Process Feature

Este módulo proporciona endpoints y utilidades para extracción de texto, resumen y validación de imágenes.

## Endpoints principales

- `POST /image-process/extract` — Extrae texto de una imagen (URL o base64)
- `POST /image-process/summarize` — Resume el contenido de una imagen
- `POST /image-process/validate` — Valida formato, tamaño y contenido de una imagen

## Ejemplo de uso

### Extracción de texto
```json
POST /image-process/extract
{
  "image_url": "https://ejemplo.com/imagen.jpg"
}
```

### Resumen de imagen
```json
POST /image-process/summarize
{
  "image_url": "https://ejemplo.com/imagen.jpg",
  "summary_type": "simple"
}
```

### Validación de imagen
```json
POST /image-process/validate
{
  "image_url": "https://ejemplo.com/imagen.jpg",
  "validation_type": "default"
}
```

## Modelos principales

- `ImageExtractRequest`, `ImageExtractResponse`
- `ImageSummaryRequest`, `ImageSummaryResponse`
- `ImageValidationRequest`, `ImageValidationResponse`

## Configuración

Variables de entorno:
- `IMAGE_PROCESS_MAX_IMAGE_SIZE_MB` (por defecto 10)
- `IMAGE_PROCESS_ALLOWED_FORMATS` (por defecto jpg, jpeg, png, bmp, gif)
- `IMAGE_PROCESS_ENABLE_SUMMARY` (por defecto True)
- `IMAGE_PROCESS_ENABLE_EXTRACTION` (por defecto True)
- `IMAGE_PROCESS_ENABLE_VALIDATION` (por defecto True)
- `IMAGE_PROCESS_CACHE_TTL_HOURS` (por defecto 24)

## Integración

Importa el router en el servidor principal:
```python
from onyx.server.features.image_process import image_process_router
include_router_with_global_prefix_prepended(application, image_process_router)
```

## Tests

Incluye tests unitarios para cada función y pruebas de integración para los endpoints.

## Extensión

Puedes agregar nuevos métodos de análisis, OCR avanzado, integración con IA, etc. siguiendo el patrón modular del servicio y API. 