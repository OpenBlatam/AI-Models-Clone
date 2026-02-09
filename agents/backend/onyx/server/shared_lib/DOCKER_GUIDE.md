# 🐳 Docker Guide - Shared Library

Guía completa para usar Docker con la librería compartida.

## 🚀 Quick Start

### 1. Build y Run Básico

```bash
# Build
docker build -f docker/Dockerfile -t shared-lib:latest ..

# Run
docker run -d -p 8030:8030 --name shared-lib shared-lib:latest

# Ver logs
docker logs -f shared-lib

# Acceder
curl http://localhost:8030/health
```

### 2. Docker Compose (Recomendado)

```bash
# Desarrollo
cd docker
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener
docker-compose down
```

## 📋 Dockerfiles Disponibles

| Dockerfile | Uso | Tamaño | Características |
|-----------|-----|--------|----------------|
| `Dockerfile` | Producción | ~200MB | Multi-stage, optimizado |
| `Dockerfile.dev` | Desarrollo | ~500MB | Hot-reload, debugging |
| `Dockerfile.alpine` | Producción ligera | ~100MB | Alpine-based, mínimo |
| `Dockerfile.serverless` | AWS Lambda | ~150MB | Lambda-optimized |

## 🛠️ Comandos Útiles

### Build

```bash
# Producción
make build
# o
docker build -f docker/Dockerfile -t shared-lib:latest ..

# Desarrollo
make build-dev
# o
docker build -f docker/Dockerfile.dev -t shared-lib:dev ..

# Alpine
make build-alpine
# o
docker build -f docker/Dockerfile.alpine -t shared-lib:alpine ..
```

### Run

```bash
# Básico
docker run -d -p 8030:8030 shared-lib:latest

# Con variables de entorno
docker run -d \
  -p 8030:8030 \
  -e ENVIRONMENT=production \
  -e LOG_LEVEL=INFO \
  shared-lib:latest

# Con volúmenes
docker run -d \
  -p 8030:8030 \
  -v $(pwd):/app \
  shared-lib:dev
```

### Docker Compose

```bash
# Desarrollo
docker-compose -f docker/docker-compose.yml up -d

# Producción
docker-compose -f docker/docker-compose.prod.yml up -d

# Testing
docker-compose -f docker/docker-compose.test.yml up --abort-on-container-exit

# Ver logs
docker-compose logs -f api

# Ejecutar comando
docker-compose exec api python -m pytest

# Detener
docker-compose down
```

## 🔧 Configuración

### Variables de Entorno

```bash
# En docker-compose.yml o docker run
ENVIRONMENT=production
LOG_LEVEL=INFO
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://admin:admin@rabbitmq:5672/
```

### Puertos

- **8030** - API principal
- **6379** - Redis
- **5672** - RabbitMQ
- **15672** - RabbitMQ Management UI
- **9090** - Prometheus
- **3000** - Grafana
- **9200** - Elasticsearch
- **11211** - Memcached
- **80/443** - NGINX

## 📦 Servicios Incluidos

El `docker-compose.yml` incluye:

1. **api** - Servicio FastAPI principal
2. **redis** - Cache y message broker
3. **rabbitmq** - Message broker con UI
4. **prometheus** - Métricas
5. **grafana** - Dashboards
6. **elasticsearch** - Búsqueda
7. **memcached** - Cache adicional
8. **nginx** - Reverse proxy

## 🎯 Casos de Uso

### Desarrollo Local

```bash
# Iniciar todo
cd docker
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f api

# Ejecutar tests
docker-compose exec api pytest

# Acceder a servicios
# API: http://localhost:8030
# RabbitMQ UI: http://localhost:15672 (admin/admin)
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

### Producción

```bash
# Build
docker build -f docker/Dockerfile -t shared-lib:1.0.0 .

# Tag para registry
docker tag shared-lib:1.0.0 registry.example.com/shared-lib:1.0.0

# Push
docker push registry.example.com/shared-lib:1.0.0

# Deploy
docker-compose -f docker/docker-compose.prod.yml up -d
```

### Testing

```bash
# Ejecutar tests
docker-compose -f docker/docker-compose.test.yml up --abort-on-container-exit

# Ver coverage
docker-compose -f docker/docker-compose.test.yml exec test cat htmlcov/index.html
```

## 🔍 Optimizaciones

### Multi-stage Build

Los Dockerfiles de producción usan multi-stage builds:

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
# Instalar dependencias

# Stage 2: Runtime
FROM python:3.11-slim
# Solo copiar lo necesario
```

### Layer Caching

```dockerfile
# Dependencias primero (cambian menos)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Código después (cambia más)
COPY . .
```

### .dockerignore

El `.dockerignore` excluye:
- `__pycache__/`
- `.venv/`
- `.git/`
- `*.log`
- Archivos temporales

## 📊 Comparación de Tamaños

| Tipo | Tamaño Base | Con Dependencias | Optimizado |
|------|-------------|------------------|------------|
| Production | ~150MB | ~500MB | ~200MB |
| Development | ~150MB | ~800MB | ~500MB |
| Alpine | ~50MB | ~200MB | ~100MB |
| Serverless | ~150MB | ~300MB | ~150MB |

## ✅ Checklist

- [ ] Dockerfile seleccionado
- [ ] Variables de entorno configuradas
- [ ] Secrets manejados (usar secrets de Docker)
- [ ] Health checks funcionando
- [ ] Logs configurados
- [ ] Volumes mapeados (si necesario)
- [ ] Network configurado
- [ ] Resource limits establecidos
- [ ] Registry configurado
- [ ] CI/CD pipeline configurado

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Ver qué usa el puerto
lsof -i :8030  # Mac/Linux
netstat -ano | findstr :8030  # Windows

# Detener contenedor
docker stop shared-lib
```

### Out of Memory

```bash
# Aumentar memoria en Docker Desktop
# O reducir recursos del contenedor en docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
```

### Build Lento

```bash
# Usar build cache
docker build --cache-from shared-lib:latest -f docker/Dockerfile -t shared-lib:latest ..

# Verificar .dockerignore
cat docker/.dockerignore
```

### Cannot Connect to Docker Daemon

```bash
# Verificar Docker Desktop está corriendo
docker ps

# Reiniciar Docker Desktop
```

## 🎯 Integración con CI/CD

### GitHub Actions

```yaml
- name: Build Docker image
  run: docker build -f docker/Dockerfile -t shared-lib:${{ github.sha }} .

- name: Push to registry
  run: docker push registry.example.com/shared-lib:${{ github.sha }}
```

### GitLab CI

```yaml
build:
  script:
    - docker build -f docker/Dockerfile -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

---

**Versión**: 1.0.0  
**Última actualización**: 2024




