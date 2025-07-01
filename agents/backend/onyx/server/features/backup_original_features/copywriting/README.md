# Copywriting LLM Backend

## Descripción

Este módulo proporciona un backend avanzado para generación de copywriting usando modelos LLM (HuggingFace Transformers), con soporte para variantes (A/B testing), feedback estructurado, batch processing (Celery/Dask), métricas automáticas y extensibilidad para integración con sistemas de feedback y experimentación.

---

## Instalación y Dependencias

```bash
pip install fastapi celery[redis] transformers torch dask[distributed] pytest
```

- **FastAPI**: API REST.
- **Celery**: Procesamiento asíncrono/batch.
- **Dask**: Paralelismo distribuido (opcional).
- **Transformers/Torch**: Modelos LLM.
- **pytest**: Testing.

---

## Cómo lanzar el API y los workers

### 1. API FastAPI
```bash
uvicorn agents.backend.onyx.server.features.copywriting.api:router --reload
```

### 2. Worker Celery
```bash
celery -A agents.backend.onyx.server.features.copywriting.tasks.celery_app worker --loglevel=info
```

### 3. (Opcional) Dask Scheduler y Worker
```bash
dask-scheduler &
dask-worker tcp://localhost:8786 &
```

---

## Ejemplos de Requests

### Generar copywriting
```bash
curl -X POST "http://localhost:8000/copywriting/generate?model_name=gpt2" \
  -H "Content-Type: application/json" \
  -d '{
    "product_description": "Zapatos deportivos de alta gama",
    "target_platform": "Instagram",
    "tone": "inspirational",
    "language": "es"
  }'
```

### Batch (asíncrono)
```bash
curl -X POST "http://localhost:8000/copywriting/batch-generate" -d '[{...}, {...}]'
```

### Feedback
```bash
curl -X POST "http://localhost:8000/copywriting/feedback" \
  -H "Content-Type: application/json" \
  -d '{"variant_id": "variant_1", "feedback": {"type": "human", "score": 0.9, "comments": "Muy buen copy"}}'
```

---

## Cómo correr los tests

```bash
pytest agents/backend/onyx/server/features/copywriting/tests/
```

---

## Endpoints principales

- `POST /copywriting/generate` — Genera variantes de copywriting con LLM.
- `POST /copywriting/batch-generate` — Batch de generación (Celery, async/sync).
- `GET /copywriting/models` — Modelos disponibles.
- `GET /copywriting/task-status/{task_id}` — Estado/resultados de tareas Celery.
- `POST /copywriting/feedback` — Enviar feedback estructurado sobre variantes.

---

## Modelos de datos

- **CopywritingInput**: Input estructurado para generación.
- **CopywritingOutput**: Salida con variantes, métricas, tracking.
- **CopyVariant**: Variante generada (A/B), métricas, feedback.
- **Feedback**: Feedback humano/modelo, score, comentarios.

---

## Recomendaciones de despliegue

- Usa Redis como broker y backend para Celery.
- Separa los workers Celery y Dask en contenedores/servicios distintos.
- Usa variables de entorno para configuración sensible.
- Integra autenticación y métricas según tus necesidades.

---

## Contacto y soporte

Para dudas o mejoras, contacta al equipo de desarrollo o abre un issue en el repositorio. 