# 🚀 Mejoras Avanzadas - Shared Library

## ✨ Nuevas Características

### 1. Circuit Breaker Pattern

Protege servicios de fallos en cascada.

```python
from shared_lib import CircuitBreaker

# Crear circuit breaker
breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60.0,
    expected_exception=Exception
)

# Usar como decorator
@breaker
async def call_external_service():
    response = await http_client.get("https://api.example.com")
    return response.json()

# O manualmente
try:
    result = await breaker._call(call_external_service)
except Exception as e:
    # Circuit breaker está abierto
    logger.error(f"Service unavailable: {e}")
```

**Estados:**
- **CLOSED**: Normal, requests pasan
- **OPEN**: Fallando, requests bloqueados
- **HALF_OPEN**: Probando si el servicio se recuperó

### 2. Retry con Exponential Backoff

Retry inteligente con backoff exponencial y jitter.

```python
from shared_lib import retry, RetryConfig

# Configuración personalizada
config = RetryConfig(
    max_attempts=5,
    initial_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True,
    retryable_exceptions=(ConnectionError, TimeoutError)
)

@retry(config=config)
async def fetch_data():
    response = await http_client.get("https://api.example.com")
    return response.json()

# O con función helper
from shared_lib.utils.retry import retry_async

result = await retry_async(
    fetch_data,
    config=RetryConfig(max_attempts=3)
)
```

**Características:**
- Exponential backoff: `delay = initial * (base ^ attempt)`
- Jitter para evitar thundering herd
- Configuración flexible de excepciones

### 3. Rate Limiting Avanzado

Múltiples algoritmos de rate limiting.

```python
from shared_lib import RateLimiter, TokenBucket, SlidingWindow

# Sliding Window (más preciso)
limiter = RateLimiter(
    max_requests=100,
    window_seconds=60.0,
    algorithm="sliding_window"
)

# Token Bucket (permite bursts)
limiter = RateLimiter(
    max_requests=100,
    window_seconds=60.0,
    algorithm="token_bucket",
    burst_capacity=200
)

# Usar en endpoint
@app.get("/api/data")
async def get_data(request: Request):
    result = await limiter.check()
    
    if not result.allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "message": "Rate limit exceeded",
                "retry_after": result.retry_after
            },
            headers={
                "X-RateLimit-Limit": str(limiter.max_requests),
                "X-RateLimit-Remaining": str(result.remaining),
                "X-RateLimit-Reset": str(int(result.reset_time)),
                "Retry-After": str(int(result.retry_after)) if result.retry_after else None
            }
        )
    
    return {"data": "your data"}
```

**Algoritmos:**
- **Sliding Window**: Más preciso, cuenta requests en ventana deslizante
- **Token Bucket**: Permite bursts, tokens se recargan continuamente

### 4. Health Checks Avanzados

Sistema completo de health checks.

```python
from shared_lib import HealthChecker, HealthStatus

# Crear checker
checker = HealthChecker(service_name="music-analyzer")

# Registrar checks
@checker.register("database", timeout=5.0)
async def check_database():
    # Verificar conexión
    await db.execute("SELECT 1")
    return HealthStatus.HEALTHY

@checker.register("redis", timeout=2.0)
async def check_redis():
    await redis_client.ping()
    return HealthStatus.HEALTHY

@checker.register("external_api", timeout=3.0)
async def check_external_api():
    response = await http_client.get("https://api.example.com/health")
    if response.status_code == 200:
        return HealthStatus.HEALTHY
    return HealthStatus.UNHEALTHY

# Endpoint de health
@app.get("/health")
async def health():
    return await checker.check_all()

# Resultado:
# {
#   "service": "music-analyzer",
#   "status": "healthy",
#   "timestamp": 1234567890.123,
#   "checks": {
#     "database": {
#       "status": "healthy",
#       "response_time_ms": 12.34,
#       "timestamp": 1234567890.123
#     },
#     "redis": {...},
#     "external_api": {...}
#   }
# }
```

**Estados:**
- **HEALTHY**: Todo funcionando
- **UNHEALTHY**: Algo falló
- **DEGRADED**: Funcional pero con problemas
- **UNKNOWN**: Estado desconocido

### 5. Graceful Shutdown

Manejo elegante de shutdown.

```python
from shared_lib import GracefulShutdown, create_lifespan

# Crear shutdown handler
shutdown = GracefulShutdown(timeout=30.0)

# Registrar tareas de cleanup
@shutdown.register
async def close_database():
    await db.close()

@shutdown.register
async def close_redis():
    await redis_client.close()

@shutdown.register
async def stop_workers():
    await worker_manager.stop()

# Usar en FastAPI
app = FastAPI(lifespan=create_lifespan(shutdown))

# O manualmente
async with shutdown.lifespan():
    # Tu aplicación
    pass
```

**Características:**
- Manejo de señales (SIGTERM, SIGINT)
- Timeout configurable
- Cleanup tasks en paralelo
- Integración con FastAPI lifespan

### 6. Connection Pooling

Pool de conexiones optimizado.

```python
from shared_lib import ConnectionPool, PoolConfig

# Configurar pool
config = PoolConfig(
    min_size=2,
    max_size=10,
    max_idle_time=300.0,
    connection_timeout=5.0
)

# Crear pool
async def create_db_connection():
    return await asyncpg.connect(DATABASE_URL)

async def close_db_connection(conn):
    await conn.close()

pool = ConnectionPool(
    create_db_connection,
    close_db_connection,
    config
)

# Usar
async with pool.acquire() as conn:
    result = await conn.fetch("SELECT * FROM users")

# Cleanup al finalizar
await pool.close_all()
```

**Características:**
- Tamaño mínimo y máximo configurable
- Limpieza automática de conexiones idle
- Health checks periódicos
- Timeout de conexión
- Manejo de waiters cuando el pool está lleno

## 🎯 Ejemplo Completo

```python
from fastapi import FastAPI, HTTPException
from shared_lib import (
    setup_advanced_middleware,
    CircuitBreaker,
    retry,
    RetryConfig,
    RateLimiter,
    HealthChecker,
    GracefulShutdown,
    create_lifespan
)

# Crear app
app = FastAPI()

# Setup middleware
setup_advanced_middleware(app, service_name="music-analyzer")

# Circuit breaker para API externa
api_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60.0
)

# Rate limiter
rate_limiter = RateLimiter(
    max_requests=100,
    window_seconds=60.0
)

# Health checker
health_checker = HealthChecker("music-analyzer")

@health_checker.register("database")
async def check_db():
    # Check database
    return HealthStatus.HEALTHY

# Graceful shutdown
shutdown = GracefulShutdown()

@shutdown.register
async def cleanup():
    # Cleanup tasks
    pass

app = FastAPI(lifespan=create_lifespan(shutdown))

# Endpoint con retry y circuit breaker
@retry(RetryConfig(max_attempts=3))
@api_breaker
async def call_external_api():
    # Llamada a API externa
    pass

# Endpoint con rate limiting
@app.get("/api/data")
async def get_data(request: Request):
    result = await rate_limiter.check()
    if not result.allowed:
        raise HTTPException(429, "Rate limit exceeded")
    return {"data": "value"}

# Health endpoint
@app.get("/health")
async def health():
    return await health_checker.check_all()
```

## 📊 Comparación de Algoritmos

### Rate Limiting

| Algoritmo | Precisión | Burst | Complejidad |
|-----------|-----------|-------|-------------|
| Sliding Window | Alta | No | Media |
| Token Bucket | Media | Sí | Baja |

### Retry Strategies

| Estrategia | Ventajas | Uso |
|------------|----------|-----|
| Exponential Backoff | Evita sobrecarga | APIs externas |
| Fixed Delay | Simple | Operaciones rápidas |
| Linear Backoff | Predecible | Testing |

## ✅ Beneficios

1. **Resiliencia**: Circuit breakers y retries protegen de fallos
2. **Performance**: Connection pooling reduce overhead
3. **Observabilidad**: Health checks detallados
4. **Control**: Rate limiting preciso
5. **Confiabilidad**: Graceful shutdown sin pérdida de datos

## 🔧 Configuración Recomendada

### Producción

```python
# Circuit Breaker
breaker = CircuitBreaker(
    failure_threshold=10,
    timeout=120.0
)

# Rate Limiter
limiter = RateLimiter(
    max_requests=1000,
    window_seconds=60.0,
    algorithm="sliding_window"
)

# Connection Pool
pool_config = PoolConfig(
    min_size=5,
    max_size=50,
    max_idle_time=600.0
)

# Graceful Shutdown
shutdown = GracefulShutdown(timeout=60.0)
```

### Desarrollo

```python
# Configuraciones más permisivas
breaker = CircuitBreaker(
    failure_threshold=3,
    timeout=30.0
)

limiter = RateLimiter(
    max_requests=10000,
    window_seconds=60.0
)
```

## 🆕 Más Mejoras (v2.1)

### 7. Caching Avanzado

Sistema de caching con TTL, invalidación y múltiples backends.

```python
from shared_lib import Cache, InMemoryCache, CacheConfig

# Crear cache
cache = Cache(InMemoryCache(), CacheConfig(ttl=3600))

# Usar como decorator
@cache.cached(ttl=1800)
async def expensive_operation(param: str):
    # Operación costosa
    return result

# O manualmente
await cache.set("key", value, ttl=3600)
value = await cache.get("key")

# Get or set
value = await cache.get_or_set(
    "user:123",
    fetch_user,
    123,
    ttl=3600
)

# Invalidar
await cache.invalidate("user:*")
```

**Características:**
- TTL configurable
- Invalidación por patrón
- Múltiples backends (Memory, Redis, etc.)
- Serialización automática

### 8. Métricas Avanzadas

Sistema completo de métricas con múltiples tipos.

```python
from shared_lib import MetricsCollector, MetricType

metrics = MetricsCollector(service_name="music-analyzer")

# Counter
metrics.increment("requests_total", labels={"method": "GET"})

# Gauge
metrics.set_gauge("active_connections", 42)

# Histogram
metrics.observe("request_duration_seconds", 0.5)

# Timer context
async with metrics.timer("operation_duration"):
    await do_operation()

# Obtener métricas
all_metrics = metrics.get_metrics()
```

**Tipos de métricas:**
- **Counter**: Incrementos (requests, errors)
- **Gauge**: Valores actuales (connections, memory)
- **Histogram**: Distribuciones (latency, size)
- **Summary**: Estadísticas agregadas

### 9. Request Batching

Agrupa múltiples requests para optimizar.

```python
from shared_lib import BatchProcessor, BatchConfig

# Crear processor
async def fetch_users(user_ids: List[str]) -> List[User]:
    # Fetch batch de users
    return users

processor = BatchProcessor(
    fetch_users,
    BatchConfig(max_batch_size=50, max_wait_time=0.2)
)

# Usar - automáticamente agrupa
user1 = await processor.process("user-123")
user2 = await processor.process("user-456")
# Se ejecutan en un solo batch
```

**Ventajas:**
- Reduce número de requests
- Mejora throughput
- Configuración flexible

### 10. Distributed Locks

Locks distribuidos para operaciones críticas.

```python
from shared_lib import DistributedLock, RedisLockBackend

# Crear lock
lock = DistributedLock(RedisLockBackend(redis_client))

# Usar con context manager
async with lock.acquire("resource:123", ttl=30.0):
    # Operación crítica
    await process_resource("123")
    # Lock se libera automáticamente

# Auto-extend incluido
```

**Características:**
- Auto-extend de TTL
- Retry automático
- Release seguro
- Múltiples backends (Redis, etc.)

### 11. Feature Flags

Sistema de feature flags para control de features.

```python
from shared_lib import FeatureFlagManager, FeatureFlag, FeatureFlagType

flags = FeatureFlagManager()

# Registrar flag
flags.register(FeatureFlag(
    name="new_feature",
    enabled=True,
    flag_type=FeatureFlagType.PERCENTAGE,
    percentage=50.0  # 50% de usuarios
))

# Verificar
if await flags.is_enabled("new_feature", user_id="123"):
    # Usar nueva feature
    pass

# Targeting específico
flags.register(FeatureFlag(
    name="beta_feature",
    enabled=True,
    flag_type=FeatureFlagType.TARGETING,
    targeting={"user_ids": ["user-1", "user-2"]}
))
```

**Tipos:**
- **BOOLEAN**: On/Off simple
- **PERCENTAGE**: Rollout gradual
- **TARGETING**: Usuarios específicos

## 🎯 Ejemplo Completo con Todas las Mejoras

```python
from fastapi import FastAPI, Request
from shared_lib import (
    setup_advanced_middleware,
    CircuitBreaker,
    retry,
    RetryConfig,
    RateLimiter,
    HealthChecker,
    GracefulShutdown,
    create_lifespan,
    Cache,
    InMemoryCache,
    MetricsCollector,
    BatchProcessor,
    DistributedLock,
    FeatureFlagManager
)

# Crear app
app = FastAPI()

# Setup
setup_advanced_middleware(app, service_name="music-analyzer")

# Cache
cache = Cache(InMemoryCache())

# Metrics
metrics = MetricsCollector("music-analyzer")

# Feature flags
flags = FeatureFlagManager()

# Circuit breaker
breaker = CircuitBreaker(failure_threshold=5)

# Rate limiter
limiter = RateLimiter(max_requests=100, window_seconds=60.0)

# Health checker
health = HealthChecker("music-analyzer")

# Graceful shutdown
shutdown = GracefulShutdown()

app = FastAPI(lifespan=create_lifespan(shutdown))

# Endpoint con todas las mejoras
@app.get("/api/tracks/{track_id}")
async def get_track(track_id: str, request: Request):
    # Rate limiting
    rate_result = await limiter.check()
    if not rate_result.allowed:
        raise HTTPException(429, "Rate limit exceeded")
    
    # Feature flag
    if not await flags.is_enabled("track_api", user_id=request.headers.get("user-id")):
        raise HTTPException(404, "Not found")
    
    # Cache
    cached = await cache.get(f"track:{track_id}")
    if cached:
        metrics.increment("cache_hits")
        return cached
    
    # Circuit breaker + retry
    @retry(RetryConfig(max_attempts=3))
    @breaker
    async def fetch_track():
        async with metrics.timer("track_fetch_duration"):
            # Fetch track
            return track
    
    track = await fetch_track()
    
    # Guardar en cache
    await cache.set(f"track:{track_id}", track, ttl=3600)
    metrics.increment("cache_misses")
    
    return track
```

---

**Versión**: 2.1.0  
**Última actualización**: 2024

