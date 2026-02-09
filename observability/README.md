# Observability Stack (Prometheus + Grafana)

## Requisitos
- Docker y Docker Compose
- La API corriendo localmente en `http://localhost:8000` con el endpoint `/api/v1/metrics/prometheus`

## Estructura
- `docker-compose.yml`: Orquesta Prometheus y Grafana
- `prometheus.yml`: Configuración de Prometheus (scrapea la API)
- `grafana/provisioning/datasources/datasource.yml`: Datasource Prometheus por defecto

## Uso
```bash
cd observability
docker compose up -d
```

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (user: admin / pass: admin)

Si tu API corre en otro host/puerto, ajusta `prometheus.yml` en `targets`.

## Notas
- En Docker (Windows/macOS) se usa `host.docker.internal` para alcanzar el host desde el contenedor.
- El scraping apunta a `/api/v1/metrics/prometheus`, ya expuesto por la API.
- Puedes importar dashboards de Grafana para FastAPI/Prometheus o crear los tuyos.





