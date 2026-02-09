# 📚 Ejemplos de Uso - Shared Library

Ejemplos prácticos de cómo usar la librería compartida en diferentes escenarios.

## 1. Setup Básico

```python
from fastapi import FastAPI
from shared_lib import setup_advanced_middleware

app = FastAPI(title="Mi Servicio")

# Una línea para configurar todo el middleware avanzado
setup_advanced_middleware(
    app,
    service_name="mi_servicio",
    enable_opentelemetry=True
)
```

## 2. OAuth2 Security

```python
from fastapi import FastAPI, Depends
from shared_lib.security import (
    oauth2_security,
    get_current_active_user,
    require_role,
    User,
    Token,
    UserCreate
)

app = FastAPI()

# Registrar usuario
@app.post("/auth/register")
async def register(user_data: UserCreate):
    user = oauth2_security.create_user(user_data)
    return {"user_id": user.id, "username": user.username}

# Login
@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = oauth2_security.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    access_token = oauth2_security.create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    return Token(access_token=access_token, token_type="bearer")

# Endpoint protegido
@app.get("/protected")
async def protected(user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {user.username}"}

# Endpoint con rol requerido
@app.get("/admin")
async def admin(user: User = Depends(require_role("admin"))):
    return {"message": "Admin access"}
```

## 3. Async Workers

```python
from shared_lib.workers import WorkerManager, WorkerType

# Configurar worker manager
worker_manager = WorkerManager(
    worker_type=WorkerType.ASYNC,
    max_workers=5
)

@app.on_event("startup")
async def startup():
    await worker_manager.start()

@app.on_event("shutdown")
async def shutdown():
    await worker_manager.stop()

# Función de background
async def process_analysis(data):
    # Procesar datos
    return {"result": "processed"}

# Encolar tarea
@app.post("/analyze")
async def analyze(data: dict):
    task_id = await worker_manager.enqueue_task(
        process_analysis,
        data
    )
    return {"task_id": task_id}

# Verificar estado
@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    status = worker_manager.get_task_status(task_id)
    return status
```

## 4. Message Broker

```python
from shared_lib.messaging import MessageBrokerManager, BrokerType

# Configurar broker
broker = MessageBrokerManager(
    broker_type=BrokerType.REDIS,
    connection_url="redis://localhost:6379/0"
)

# Handler de eventos
def on_track_analyzed(message):
    print(f"Track analyzed: {message}")

# Suscribirse
broker.subscribe("track.analyzed", on_track_analyzed)

# Publicar evento
@app.post("/analyze/{track_id}")
async def analyze_track(track_id: str):
    # Análisis...
    result = {"track_id": track_id, "status": "analyzed"}
    
    # Publicar evento
    broker.publish("track.analyzed", result)
    
    return result
```

## 5. Database Adapters

```python
from shared_lib.database import DatabaseManager

# Configurar DynamoDB
db = DatabaseManager(
    adapter_type="dynamodb",
    region="us-east-1"
)

# Guardar
@app.post("/tracks/{track_id}")
async def save_track(track_id: str, data: dict):
    await db.put(track_id, data, "tracks")
    return {"status": "saved"}

# Obtener
@app.get("/tracks/{track_id}")
async def get_track(track_id: str):
    track = await db.get(track_id, "tracks")
    if not track:
        raise HTTPException(404, "Track not found")
    return track

# Query
@app.get("/tracks")
async def list_tracks(genre: str = None):
    filters = {}
    if genre:
        filters["genre"] = genre
    tracks = await db.query("tracks", **filters)
    return tracks
```

## 6. Elasticsearch

```python
from shared_lib.search import elasticsearch_client

# Indexar documento
@app.post("/index/{track_id}")
async def index_track(track_id: str, data: dict):
    elasticsearch_client.index_document("tracks", track_id, data)
    return {"status": "indexed"}

# Buscar
@app.get("/search")
async def search_tracks(q: str):
    results = elasticsearch_client.search_full_text(
        "tracks",
        q,
        fields=["name", "artist", "description"]
    )
    return results
```

## 7. Memcached

```python
from shared_lib.cache import memcached_client

@app.get("/track/{track_id}")
async def get_track(track_id: str):
    # Intentar obtener del caché
    cached = memcached_client.get(f"track:{track_id}")
    if cached:
        return cached
    
    # Si no está en caché, obtener de DB
    track = await get_track_from_db(track_id)
    
    # Guardar en caché
    memcached_client.set(f"track:{track_id}", track, expire=3600)
    
    return track
```

## 8. Serverless Optimization

```python
from shared_lib.serverless import serverless_handler, get_serverless_config

@serverless_handler
@app.post("/analyze")
async def analyze(data: dict):
    config = get_serverless_config()
    
    # Tu código aquí
    result = process_data(data)
    
    return result
```

## 9. Service Discovery

```python
from shared_lib.discovery import service_discovery, ServiceDiscoveryType

# Configurar discovery
service_discovery.discovery_type = ServiceDiscoveryType.CONSUL

# Registrar servicio
service_discovery.register_service(
    "music-analyzer",
    "api",
    8010,
    tags=["api", "music"]
)

# Descubrir servicios
instances = service_discovery.discover_service("material-service")
```

## 10. Inter-Service Communication

```python
from shared_lib.inter_service import service_registry, ServiceClient

# Registrar servicio
client = ServiceClient("material-service", discovery=service_discovery)
service_registry.register_service("material-service", client)

# Llamar servicio
@app.get("/materials")
async def get_materials():
    result = await service_registry.call_service(
        "material-service",
        "GET",
        "/api/v1/materials"
    )
    return result
```

## 11. Combinación Completa

```python
from fastapi import FastAPI, Depends
from shared_lib import (
    setup_advanced_middleware,
    WorkerManager,
    MessageBrokerManager,
    DatabaseManager,
    get_current_active_user,
    User
)

app = FastAPI()

# Setup completo
setup_advanced_middleware(app, service_name="music-analyzer")

worker_manager = WorkerManager()
message_broker = MessageBrokerManager()
db = DatabaseManager(adapter_type="dynamodb")

@app.on_event("startup")
async def startup():
    await worker_manager.start()
    # Configurar suscripciones
    message_broker.subscribe("track.analyzed", handle_analysis)

@app.post("/analyze/{track_id}")
async def analyze_track(
    track_id: str,
    user: User = Depends(get_current_active_user)
):
    # Encolar análisis en background
    task_id = await worker_manager.enqueue_task(
        analyze_track_background,
        track_id,
        user.id
    )
    
    return {"task_id": task_id}

async def analyze_track_background(track_id: str, user_id: str):
    # Análisis...
    result = {"track_id": track_id, "status": "analyzed"}
    
    # Guardar en DB
    await db.put(track_id, result, "analyses")
    
    # Publicar evento
    message_broker.publish("track.analyzed", result)
    
    return result
```

---

Estos ejemplos muestran cómo usar la librería compartida en diferentes escenarios.




