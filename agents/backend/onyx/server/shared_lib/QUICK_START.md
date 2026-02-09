# 🚀 Quick Start - Shared Library

Guía rápida para usar la librería compartida en tus proyectos FastAPI.

## 1. Importar la Librería

```python
# Opción 1: Importar todo
from shared_lib import (
    setup_advanced_middleware,
    WorkerManager,
    MessageBrokerManager
)

# Opción 2: Importar módulos específicos
from shared_lib.middleware import setup_advanced_middleware
from shared_lib.security import get_current_active_user
from shared_lib.workers import WorkerManager
```

## 2. Configurar en main.py

```python
from fastapi import FastAPI
from shared_lib import setup_advanced_middleware

app = FastAPI(title="Mi Servicio")

# Configurar middleware (una línea)
setup_advanced_middleware(
    app,
    service_name="mi_servicio",
    enable_opentelemetry=True
)
```

## 3. Usar OAuth2 (Opcional)

```python
from shared_lib.security import get_current_active_user, User

@app.get("/protected")
async def protected(user: User = Depends(get_current_active_user)):
    return {"user": user.username}
```

## 4. Usar Workers (Opcional)

```python
from shared_lib.workers import WorkerManager, WorkerType

worker_manager = WorkerManager(worker_type=WorkerType.ASYNC)

@app.on_event("startup")
async def startup():
    await worker_manager.start()

# Encolar tarea
task_id = await worker_manager.enqueue_task(my_function, arg1, arg2)
```

## 5. Usar Message Broker (Opcional)

```python
from shared_lib.messaging import MessageBrokerManager, BrokerType

broker = MessageBrokerManager(broker_type=BrokerType.REDIS)

# Publicar
broker.publish("event.name", {"data": "value"})

# Suscribirse
broker.subscribe("event.name", handler_function)
```

## ✅ Eso es todo!

La librería está lista para usar. Los módulos opcionales solo se cargan si los necesitas.




