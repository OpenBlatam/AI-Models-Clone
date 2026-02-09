# 🚀 QUICK START GUIDE - Enterprise API

## ⚡ Inicio Rápido (5 minutos)

### 1. Instalación Express

```bash
# Navegar al directorio
cd agents/backend/onyx

# Instalar dependencias mínimas
pip install fastapi uvicorn redis

# Ejecutar demo inmediatamente
python enterprise_demo.py
```

**¡Listo!** La API está corriendo en http://localhost:8001

### 2. Probar Features Enterprise

Abre tu navegador y visita:

- **🏠 API Root**: http://localhost:8001
- **📚 Documentación**: http://localhost:8001/docs  
- **🏥 Health Check**: http://localhost:8001/health
- **📊 Estadísticas**: http://localhost:8001/stats
- **⚡ Cache Demo**: http://localhost:8001/api/cached
- **🔄 Circuit Breaker**: http://localhost:8001/api/protected

### 3. Headers de Respuesta Avanzados

Nota los headers enterprise en cada respuesta:
```http
X-Request-ID: uuid-único
X-Process-Time: 0.0234
X-Cache-Hit-Ratio: 0.850
X-Circuit-Breaker: CLOSED
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
```

## 🛠️ Setup Completo (Recomendado)

### 1. Instalación Completa

```bash
# Script de instalación automática (Unix/Linux/Mac)
./quick-start.sh install

# Windows - Manual
python -m venv venv
venv\Scripts\activate
pip install -r requirements-enterprise.txt
```

### 2. Configuración

```bash
# Copiar configuración de ejemplo
cp config.example .env

# Editar configuración (opcional)
# nano .env
```

### 3. Iniciar Redis (Opcional)

```bash
# Unix/Linux/Mac
redis-server

# Windows con Docker
docker run -d -p 6379:6379 redis:alpine

# O usar el script
./quick-start.sh redis
```

### 4. Modos de Ejecución

```bash
# Desarrollo (con hot reload)
./quick-start.sh dev

# Demo standalone
./quick-start.sh demo

# Producción con Docker
./quick-start.sh prod

# Testing y benchmarks
./quick-start.sh test
./quick-start.sh benchmark
```

## 📊 Monitoring y Métricas

### 1. Prometheus Metrics

```bash
# Iniciar stack de monitoreo
./quick-start.sh monitor

# Acceder a métricas
curl http://localhost:8001/metrics
```

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### 2. Performance Testing

```bash
# Apache Bench
ab -n 1000 -c 10 http://localhost:8001/

# curl simple
curl -w "@curl-format.txt" http://localhost:8001/api/cached
```

## 🔧 Comandos Útiles

### Desarrollo

```bash
# Desarrollo con reload
uvicorn enterprise_demo:app --reload --port 8001

# Debug mode
LOG_LEVEL=debug python enterprise_demo.py

# Sin rate limiting
RATE_LIMIT_ENABLED=false python enterprise_demo.py
```

### Testing

```bash
# Health check
curl http://localhost:8001/health | jq

# Circuit breaker test
for i in {1..10}; do curl http://localhost:8001/api/protected; done

# Cache performance
curl http://localhost:8001/api/cached  # Primera vez (miss)
curl http://localhost:8001/api/cached  # Segunda vez (hit)
```

### Producción

```bash
# Docker build
docker build -f docker/Dockerfile.enterprise -t enterprise-api .

# Docker run
docker run -p 8000:8000 -e ENVIRONMENT=production enterprise-api

# Con Redis externo
docker run -p 8000:8000 \
  -e REDIS_URL=redis://your-redis:6379 \
  enterprise-api
```

## 📈 Features Implementados

### ✅ Core Patterns

- **Circuit Breaker**: Protección automática contra fallos
- **Multi-tier Cache**: Memory + Redis con fallback
- **Rate Limiting**: Límites por IP/usuario distribuidos  
- **Health Checks**: Kubernetes-ready probes
- **Metrics**: Prometheus + custom metrics
- **Security Headers**: Headers enterprise estándar

### ✅ Performance

- **Async Everywhere**: Operaciones 100% asíncronas
- **Connection Pooling**: Redis con pool de conexiones
- **Compression**: GZip automático
- **JSON Optimization**: orjson para ultra-velocidad
- **Memory Management**: Weak references y LRU

### ✅ Observability

- **Request Tracing**: UUID únicos por request
- **Structured Logging**: Logs JSON estructurados  
- **Performance Monitoring**: Tiempo de respuesta automático
- **Error Tracking**: Manejo avanzado de excepciones
- **Statistics**: Métricas en tiempo real

## 🌐 Endpoints Disponibles

| Endpoint | Descripción | Features |
|----------|-------------|----------|
| `GET /` | Info del servicio | ✅ Básico |
| `GET /health` | Health check completo | ✅ K8s Ready |
| `GET /health/live` | Liveness probe | ✅ K8s Ready |
| `GET /health/ready` | Readiness probe | ✅ K8s Ready |
| `GET /stats` | Estadísticas detalladas | ✅ Monitoreo |
| `GET /metrics` | Métricas Prometheus | ✅ Observability |
| `GET /api/cached` | Demo de caching | ✅ Cache L1+L2 |
| `GET /api/protected` | Demo circuit breaker | ✅ Resilience |

## 🚨 Troubleshooting

### Redis No Disponible
```
⚠️ Redis connection failed - will use memory cache only
```
**Solución**: La API funciona sin Redis usando solo memoria cache

### Puerto en Uso
```
❌ Port 8001 is already in use!
```
**Solución**: Usar otro puerto: `--port 8002`

### Dependencias Faltantes
```
❌ FastAPI not found
```
**Solución**: `pip install -r requirements-enterprise.txt`

### Circuit Breaker Abierto
```
Service temporarily unavailable (Circuit Breaker OPEN)
```
**Solución**: Esperar 30-60s para auto-recovery o reiniciar

## 🔄 Integración con API Actual

### 1. Reemplazar Middleware

```python
# En tu main.py actual
from agents.backend.onyx.enterprise_demo import (
    SimpleCache, CircuitBreaker, RateLimiter
)

# Agregar components enterprise
cache = SimpleCache()
circuit_breaker = CircuitBreaker()
```

### 2. Health Checks

```python
@app.get("/health")
async def health():
    return await health_checker.run_checks()
```

### 3. Métricas

```python
from prometheus_client import Counter
request_count = Counter('requests_total', 'Total requests')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    request_count.inc()
    return await call_next(request)
```

## 📞 Soporte

### Logs Útiles

```bash
# Ver logs en tiempo real
tail -f /var/log/app.log

# Docker logs
docker logs -f enterprise-api

# Logs estructurados
LOG_LEVEL=debug STRUCTURED_LOGGING=true python enterprise_demo.py
```

### Debug Mode

```bash
# Activar modo debug completo
export ENVIRONMENT=development
export LOG_LEVEL=debug
export DEBUG=true
python enterprise_demo.py
```

---

## 🎯 Próximos Pasos

1. **✅ Demo Funcionando**: Ejecutar `python enterprise_demo.py`
2. **📊 Métricas**: Configurar Prometheus/Grafana
3. **🐳 Docker**: Containerizar para producción
4. **☁️ Deploy**: Kubernetes/Cloud deployment
5. **🔧 Customizar**: Adaptar a necesidades específicas

**¡La API enterprise está lista para producción con todos los patrones avanzados de microservicios!** 🚀 