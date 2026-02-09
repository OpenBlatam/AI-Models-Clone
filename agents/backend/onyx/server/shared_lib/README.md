# 🚀 Blatam Academy Shared Library

Librería compartida con utilidades avanzadas para FastAPI, microservicios y entornos serverless.

## 📦 Instalación

```bash
# La librería está en el mismo repositorio
# No requiere instalación adicional, solo importar
```

## 🚀 Deployment con Un Solo Comando

```bash
# Opción 1: Script bash (Linux/Mac)
./deploy lambda mi-servicio dev us-east-1

# Opción 2: Script PowerShell (Windows)
.\deploy.ps1 lambda mi-servicio dev us-east-1

# Opción 3: Python (Todas las plataformas)
python run.py deploy lambda mi-servicio dev us-east-1

# Opción 4: Makefile
make deploy-lambda SERVICE_NAME=mi-servicio STAGE=prod
```

**Esto automáticamente:**
- ✅ Verifica prerequisitos (AWS CLI, credenciales, etc.)
- ✅ Configura recursos AWS (DynamoDB, S3, CloudWatch, ECR)
- ✅ Genera configuraciones necesarias
- ✅ Build y deploy de la aplicación
- ✅ Muestra información del deployment

**Más opciones:**
- `./deploy ecs mi-servicio` - Deploy a ECS
- `./deploy local` - Servicios locales con Docker Compose
- `make deploy-local` - Iniciar servicios locales
- `python run.py setup mi-servicio` - Solo configurar recursos

Ver `README_DEPLOY.md` para todos los comandos disponibles.

## 🚀 Nuevas Mejoras (v2.0)

### Circuit Breaker Pattern
Protege servicios de fallos en cascada con estados CLOSED/OPEN/HALF_OPEN.

### Retry con Exponential Backoff
Retry inteligente con backoff exponencial y jitter para evitar thundering herd.

### Rate Limiting Avanzado
Múltiples algoritmos: Sliding Window (preciso) y Token Bucket (permite bursts).

### Health Checks Avanzados
Sistema completo de health checks para servicios y dependencias.

### Graceful Shutdown
Manejo elegante de shutdown con cleanup tasks y timeout configurable.

### Connection Pooling
Pool optimizado con limpieza automática, health checks y manejo de waiters.

Ver `IMPROVEMENTS.md` para ejemplos completos y documentación detallada.

## ☸️ Kubernetes & Monitoring

- `k8s/` – Deployment, Service, Ingress, HPA, PDB, Istio VirtualService, Linkerd ServiceProfile
- `monitoring/` – Prometheus rules, Alertmanager y dashboard Grafana

```bash
# Kubernetes
kubectl apply -n music-analyzer -f k8s/

# Monitoring
kubectl apply -n monitoring -f monitoring/prometheus-rules.yml
kubectl apply -n monitoring -f monitoring/alertmanager.yml
```

## 🎯 Uso Rápido

```python
from shared_lib import setup_advanced_middleware, WorkerManager, MessageBrokerManager

# En tu main.py de FastAPI
app = FastAPI()

# Configurar middleware avanzado
setup_advanced_middleware(
    app,
    service_name="mi_servicio",
    enable_opentelemetry=True
)

# Configurar workers
worker_manager = WorkerManager(worker_type=WorkerType.ASYNC)

# Configurar message broker
message_broker = MessageBrokerManager(broker_type=BrokerType.REDIS)
```

## 🐳 Docker Support

La librería incluye soporte completo de Docker:

- **4 Dockerfiles** optimizados (producción, desarrollo, alpine, serverless)
- **Docker Compose** con todos los servicios
- **Scripts de build** para diferentes plataformas
- **Multi-stage builds** para imágenes optimizadas

Ver `docker/README.md` y `DOCKER_GUIDE.md` para más detalles.

```bash
# Quick start
cd docker
docker-compose up -d
```

## 🚀 Nuevas Mejoras (v2.0)

### Circuit Breaker Pattern
Protege servicios de fallos en cascada con estados CLOSED/OPEN/HALF_OPEN.

### Retry con Exponential Backoff
Retry inteligente con backoff exponencial y jitter para evitar thundering herd.

### Rate Limiting Avanzado
Múltiples algoritmos: Sliding Window (preciso) y Token Bucket (permite bursts).

### Health Checks Avanzados
Sistema completo de health checks para servicios y dependencias.

### Graceful Shutdown
Manejo elegante de shutdown con cleanup tasks y timeout configurable.

### Connection Pooling
Pool optimizado con limpieza automática, health checks y manejo de waiters.

### Caching Avanzado
Sistema de caching con TTL, invalidación y múltiples backends.

### Métricas Avanzadas
Sistema completo de métricas (Counter, Gauge, Histogram) con exporters.

### Request Batching
Agrupa múltiples requests para optimizar throughput.

### Distributed Locks
Locks distribuidos para operaciones críticas con auto-extend.

### Feature Flags
Sistema de feature flags con percentage rollout y targeting.

Ver `IMPROVEMENTS.md` para ejemplos completos y documentación detallada.

## 📚 Módulos Disponibles

### 1. Middleware (`shared_lib.middleware`)
- **StructuredLoggingMiddleware**: Logging estructurado con JSON
- **SecurityHeadersMiddleware**: Headers de seguridad OWASP
- **PerformanceMonitoringMiddleware**: Monitoreo de performance
- **OpenTelemetryMiddleware**: Distributed tracing
- **RequestContextMiddleware**: Manejo de contexto de request

### 2. Security (`shared_lib.security`)
- **OAuth2Security**: Autenticación OAuth2 con JWT
- **get_current_active_user**: Dependency para obtener usuario actual
- **require_scope**: Dependency para requerir scopes
- **require_role**: Dependency para requerir roles

### 3. Workers (`shared_lib.workers`)
- **WorkerManager**: Gestor de workers
- **AsyncWorker**: Workers nativos con asyncio
- **CeleryWorker**: Soporte para Celery
- **RQWorker**: Soporte para Redis Queue

### 4. Messaging (`shared_lib.messaging`)
- **MessageBrokerManager**: Gestor de message brokers
- **RabbitMQBroker**: Integración RabbitMQ
- **KafkaBroker**: Integración Kafka
- **RedisPubSubBroker**: Redis Pub/Sub

### 5. Gateway (`shared_lib.gateway`)
- **KongGatewayManager**: Integración Kong API Gateway
- **AWSAPIGatewayManager**: Integración AWS API Gateway

### 6. Service Mesh (`shared_lib.service_mesh`)
- **ServiceMeshManager**: Gestor de service mesh
- **IstioConfig**: Configuración Istio
- **LinkerdConfig**: Configuración Linkerd

### 7. Database (`shared_lib.database`)
- **DatabaseManager**: Gestor de bases de datos
- **DynamoDBAdapter**: Adaptador AWS DynamoDB
- **CosmosDBAdapter**: Adaptador Azure Cosmos DB

### 8. Search (`shared_lib.search`)
- **ElasticsearchClient**: Cliente Elasticsearch
- Búsqueda full-text, agregaciones, bulk operations

### 9. Cache (`shared_lib.cache`)
- **MemcachedClient**: Cliente Memcached
- Caché de alta performance con TTL

### 10. Security OWASP (`shared_lib.security_owasp`)
- **OWASPSecurityValidator**: Validación OWASP
- **DDoSProtectionMiddleware**: Protección DDoS
- Input validation, sanitization

### 11. Serverless (`shared_lib.serverless`)
- **ServerlessConfig**: Configuración serverless
- **serverless_handler**: Decorator para optimización
- Cold start reduction, memory optimization

### 12. Logging (`shared_lib.logging`)
- **CentralizedLogging**: Logging centralizado
- **CloudWatchLogger**: Integración AWS CloudWatch
- **ELKLogger**: Integración ELK Stack

### 13. Discovery (`shared_lib.discovery`)
- **ServiceDiscoveryManager**: Gestor de service discovery
- **ConsulServiceDiscovery**: Consul
- **KubernetesServiceDiscovery**: Kubernetes
- **DNSServiceDiscovery**: DNS-based

### 14. Inter-Service (`shared_lib.inter_service`)
- **ServiceRegistry**: Registro de servicios
- **ServiceClient**: Cliente para comunicación entre servicios
- **RESTClient**: Cliente REST asíncrono

## 🔧 Ejemplos de Uso

### Middleware Avanzado

```python
from shared_lib.middleware import setup_advanced_middleware

app = FastAPI()
setup_advanced_middleware(
    app,
    service_name="mi_servicio",
    enable_opentelemetry=True,
    opentelemetry_endpoint="http://localhost:4317"
)
```

### OAuth2 Security

```python
from shared_lib.security import get_current_active_user, require_role

@app.get("/protected")
async def protected_endpoint(user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {user.username}"}

@app.get("/admin")
async def admin_endpoint(user: User = Depends(require_role("admin"))):
    return {"message": "Admin access"}
```

### Async Workers

```python
from shared_lib.workers import WorkerManager, WorkerType

worker_manager = WorkerManager(
    worker_type=WorkerType.ASYNC,
    max_workers=5
)

await worker_manager.start()

# Encolar tarea
task_id = await worker_manager.enqueue_task(
    my_background_task,
    arg1, arg2
)
```

### Message Broker

```python
from shared_lib.messaging import MessageBrokerManager, BrokerType

broker = MessageBrokerManager(
    broker_type=BrokerType.RABBITMQ,
    connection_url="amqp://guest:guest@localhost:5672/"
)

# Publicar mensaje
broker.publish("event.created", {"data": "value"})

# Suscribirse
def handle_event(message):
    print(f"Event: {message}")

broker.subscribe("event.created", handle_event)
```

### Database Adapters

```python
from shared_lib.database import DatabaseManager

# DynamoDB
db = DatabaseManager(
    adapter_type="dynamodb",
    region="us-east-1"
)

await db.put("key", {"data": "value"}, "table")
data = await db.get("key", "table")
```

### Elasticsearch

```python
from shared_lib.search import elasticsearch_client

# Indexar
elasticsearch_client.index_document(
    "index",
    "doc_id",
    {"field": "value"}
)

# Buscar
results = elasticsearch_client.search_full_text(
    "index",
    "query text"
)
```

### Memcached

```python
from shared_lib.cache import memcached_client

# Guardar
memcached_client.set("key", {"data": "value"}, expire=3600)

# Obtener
cached = memcached_client.get("key")
```

## 📋 Dependencias

Ver `requirements.txt` en la raíz del proyecto para todas las dependencias.

Principales:
- `opentelemetry-api>=1.21.0`
- `python-jose[cryptography]>=3.3.0`
- `celery>=5.3.4`
- `pika>=1.3.2`
- `boto3>=1.28.0`
- `elasticsearch>=8.10.0`
- `pymemcache>=4.0.0`

## 🎯 Integración en Proyectos

### Para proyectos nuevos:

```python
from shared_lib import (
    setup_advanced_middleware,
    WorkerManager,
    MessageBrokerManager,
    get_serverless_config
)

app = FastAPI(title="Mi Servicio")

# Configurar todo
setup_advanced_middleware(app, service_name="mi_servicio")
worker_manager = WorkerManager()
message_broker = MessageBrokerManager()
```

### Para proyectos existentes:

```python
# Agregar al inicio de main.py
from shared_lib.middleware import setup_advanced_middleware

# Después de crear la app FastAPI
setup_advanced_middleware(app, service_name="nombre_del_servicio")
```

## 📝 Documentación Completa

Cada módulo tiene documentación detallada. Ver:
- `shared_lib/middleware/` - Middleware avanzado
- `shared_lib/security/` - Seguridad OAuth2
- `shared_lib/workers/` - Workers asíncronos
- `shared_lib/messaging/` - Message brokers
- etc.

## 🤝 Contribuir

Esta librería es compartida entre todos los proyectos de Blatam Academy. 
Al hacer mejoras, asegúrate de que sean compatibles con todos los servicios.

## 📄 Licencia

Propietaria - Blatam Academy

---

**Versión**: 1.0.0  
**Última actualización**: 2024

