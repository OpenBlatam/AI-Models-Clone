# AI Video FastAPI Microservice (Enterprise Ready)

## Endpoints principales

- `POST /api/v1/video` — Solicita la generación de un video AI (asíncrono, requiere JWT)
- `GET /api/v1/video/{request_id}/status` — Estado del job
- `GET /api/v1/video/{request_id}/logs` — Logs del job (paginado, filtrado)
- `POST /api/v1/video/{request_id}/cancel` — Cancelar job
- `POST /api/v1/video/{request_id}/retry` — Reintentar job
- `POST /api/v1/video/{request_id}/pause` — Pausar job
- `POST /api/v1/video/{request_id}/resume` — Reanudar job
- `DELETE /api/v1/video/{request_id}` — Eliminar job
- `GET /api/v1/jobs/search` — Buscar jobs por usuario, estado, fecha, etc.
- `GET /api/v1/logs/search` — Buscar logs por filtros avanzados
- `GET /api/v1/audit` — Auditoría de accesos (solo admin)
- `GET /api/v1/webhook_failures` — Fallos de webhooks
- `POST /api/v1/token/refresh` — Refresh token
- `POST /api/v1/token/revoke` — Revocar token
- `/metrics` — Métricas Prometheus (solo admin)
- `/health` — Healthcheck extendido
- `/docs` — Documentación OpenAPI enriquecida

## Persistencia
- Jobs, logs, auditoría y tokens revocados se almacenan en SQLite (fácil de migrar a PostgreSQL).
- Fallback automático a in-memory si la DB no está disponible.

## Seguridad
- JWT con scopes, expiración y revocación persistente.
- Rate limiting configurable por usuario y endpoint.
- Protección de endpoints sensibles (audit, metrics, jobs/search) solo para admin.

## Observabilidad
- Métricas Prometheus por usuario, endpoint, estado, errores, reintentos, cancelaciones.
- Propagación de trace_id/span_id a todos los logs, Celery y webhooks.

## Auditoría
- Todos los accesos a endpoints sensibles quedan registrados con usuario, IP, scope, timestamp y trace_id.
- Endpoint de consulta de auditoría solo para admin, con paginación y filtros.

## Webhooks
- Soporte para múltiples webhooks por job.
- Notificación en todos los cambios de estado.
- Fallos de webhooks quedan registrados y consultables.

## Ejemplo de request

```bash
curl -X POST "http://localhost:8000/api/v1/video" \
  -H "accept: application/json" \
  -H "Authorization: Bearer supersecrettoken" \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Crea un video demo", "user_id": "user1", "webhook_url": "http://requestbin.net/r/xxxx"}'
```

## Variables de entorno
- `DB_URL` — URL de la base de datos (por defecto: `sqlite:///./ai_video.db`)
- `CELERY_BROKER_URL` — URL de Redis (por defecto: `redis://localhost:6379/0`)
- `JWT_SECRET` — Secreto para firmar JWT
- `ALLOWED_ORIGINS` — Orígenes permitidos para CORS

## Notas
- El procesamiento es simulado (5s). Puedes conectar tu lógica real en `process_video_task`.
- Si envías `webhook_url`, recibirás notificación al finalizar el procesamiento y en cada cambio de estado.
- Si la base de datos no está disponible, el sistema sigue funcionando en modo demo (in-memory).
- Tracing OpenTelemetry y métricas Prometheus instrumentados.

## Autenticación
- Usa OAuth2/JWT (token de ejemplo: `supersecrettoken`)
- Header: `Authorization: Bearer supersecrettoken`

## Despliegue local (recomendado)

```bash
docker-compose up --build
```
Esto levanta:
- API FastAPI en `localhost:8000`
- Redis en `localhost:6379`
- Worker Celery

```bash
curl -X POST "http://localhost:8000/api/v1/video" \
  -H "accept: application/json" \
  -H "Authorization: Bearer supersecrettoken" \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Crea un video demo", "user_id": "user1", "webhook_url": "http://requestbin.net/r/xxxx"}'
```

## Notas
- El procesamiento es simulado (5s). Puedes conectar tu lógica real en `process_video_task`.
- Si envías `webhook_url`, recibirás notificación al finalizar el procesamiento.
- Métricas Prometheus expuestas en `/metrics`.
- Tracing OpenTelemetry ya instrumentado.
