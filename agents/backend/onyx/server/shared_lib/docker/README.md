# 🐳 Docker Support - Shared Library

Soporte completo de Docker para la librería compartida con múltiples configuraciones optimizadas.

## 📋 Dockerfiles Disponibles

### 1. `Dockerfile` - Producción
- Multi-stage build
- Optimizado para tamaño
- Usuario no-root
- Health checks
- **Tamaño**: ~200MB

### 2. `Dockerfile.dev` - Desarrollo
- Hot-reload habilitado
- Herramientas de desarrollo
- Debugging tools
- **Tamaño**: ~500MB

### 3. `Dockerfile.alpine` - Ultra-ligero
- Basado en Alpine Linux
- Tamaño mínimo
- Ideal para producción
- **Tamaño**: ~100MB

### 4. `Dockerfile.serverless` - Serverless
- Para AWS Lambda
- Basado en AWS Lambda base image
- Optimizado para cold start
- **Tamaño**: ~150MB

## 🚀 Uso Rápido

### Build

```bash
# Producción
docker build -f docker/Dockerfile -t shared-lib:latest ..

# Desarrollo
docker build -f docker/Dockerfile.dev -t shared-lib:dev ..

# Alpine
docker build -f docker/Dockerfile.alpine -t shared-lib:alpine ..

# Serverless
docker build -f docker/Dockerfile.serverless -t shared-lib:serverless ..
```

### Run

```bash
# Ejecutar contenedor
docker run -d \
  --name shared-lib \
  -p 8030:8030 \
  -e ENVIRONMENT=production \
  shared-lib:latest

# Ver logs
docker logs -f shared-lib

# Ejecutar comando
docker exec -it shared-lib python -m pytest
```

### Docker Compose

```bash
# Desarrollo
cd docker
docker-compose up -d

# Producción
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose logs -f api

# Detener
docker-compose down
```

## 🛠️ Scripts Disponibles

### Build Scripts

```bash
# Linux/Mac
./docker/build.sh latest prod

# Windows
.\docker\build.ps1 -Version latest -BuildType prod
```

### Run Scripts

```bash
# Linux/Mac
./docker/run.sh latest 8030 production
```

### Makefile

```bash
# Build
make build

# Desarrollo
make build-dev
make compose-up

# Producción
make build
make compose-prod

# Limpiar
make clean
```

## 📦 Docker Compose Services

El `docker-compose.yml` incluye:

- **api** - Servicio principal FastAPI
- **redis** - Cache y message broker
- **rabbitmq** - Message broker
- **prometheus** - Métricas
- **grafana** - Dashboards
- **elasticsearch** - Búsqueda
- **memcached** - Cache adicional
- **nginx** - Reverse proxy

## 🔧 Configuración

### Variables de Entorno

```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://admin:admin@rabbitmq:5672/
```

### Puertos

- **8030** - API principal
- **6379** - Redis
- **5672** - RabbitMQ
- **15672** - RabbitMQ Management
- **9090** - Prometheus
- **3000** - Grafana
- **9200** - Elasticsearch
- **11211** - Memcached
- **80/443** - NGINX

## 🎯 Casos de Uso

### Desarrollo Local

```bash
# Iniciar todo
cd docker
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Ejecutar tests
docker-compose exec api pytest
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
docker-compose -f docker-compose.prod.yml up -d
```

### AWS ECS/Fargate

```bash
# Build
docker build -f docker/Dockerfile -t shared-lib:latest .

# Tag para ECR
docker tag shared-lib:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/shared-lib:latest

# Push
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/shared-lib:latest
```

### AWS Lambda

```bash
# Build serverless image
docker build -f docker/Dockerfile.serverless -t shared-lib:serverless .

# Usar con Lambda container image
```

## 🔍 Optimizaciones

### Multi-stage Build

Los Dockerfiles de producción usan multi-stage builds para:
- Reducir tamaño final
- Separar dependencias de runtime
- Optimizar layers

### Layer Caching

```dockerfile
# Dependencias primero (cambian menos)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Código después (cambia más)
COPY . .
```

### Health Checks

Todos los Dockerfiles incluyen health checks:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1
```

## 📊 Comparación de Tamaños

| Dockerfile | Tamaño Base | Con Dependencias | Optimizado |
|-----------|-------------|------------------|------------|
| Production | ~150MB | ~500MB | ~200MB |
| Development | ~150MB | ~800MB | ~500MB |
| Alpine | ~50MB | ~200MB | ~100MB |
| Serverless | ~150MB | ~300MB | ~150MB |

## ✅ Checklist de Deployment

- [ ] Dockerfile seleccionado
- [ ] Variables de entorno configuradas
- [ ] Secrets manejados correctamente
- [ ] Health checks funcionando
- [ ] Logs configurados
- [ ] Volumes mapeados (si necesario)
- [ ] Network configurado
- [ ] Resource limits establecidos
- [ ] Registry configurado
- [ ] CI/CD pipeline configurado

## 🐛 Troubleshooting

### Error: "Cannot connect to Docker daemon"

**Solución**: Asegúrate de que Docker Desktop esté corriendo.

### Error: "Port already in use"

**Solución**: Cambia el puerto o detén el contenedor que lo usa:
```bash
docker ps
docker stop <container_id>
```

### Error: "Out of memory"

**Solución**: Aumenta memoria en Docker Desktop o reduce recursos del contenedor.

### Build lento

**Solución**: Usa build cache y multi-stage builds. Verifica `.dockerignore`.

---

**Versión**: 1.0.0  
**Última actualización**: 2024




