"""
Ejemplo de Ejecución - Shared Library
======================================

Ejemplo completo de cómo usar la librería compartida en un servicio FastAPI.
"""

import asyncio
import logging
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar librería compartida
try:
    from shared_lib.middleware import setup_advanced_middleware
    logger.info("✅ Shared library importada correctamente")
except ImportError as e:
    logger.error(f"❌ Error importando shared_lib: {e}")
    logger.error("Asegúrate de estar en el directorio correcto")
    raise

# Crear aplicación FastAPI
app = FastAPI(
    title="Ejemplo con Shared Library",
    description="Ejemplo de uso de la librería compartida",
    version="1.0.0"
)

# Configurar middleware avanzado
setup_advanced_middleware(
    app,
    service_name="ejemplo_servicio",
    enable_opentelemetry=True,
    opentelemetry_endpoint=None  # Configurar si tienes OTLP endpoint
)

# Endpoints de ejemplo
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Servicio con Shared Library",
        "status": "running",
        "features": {
            "middleware": "✅ Configurado",
            "logging": "✅ Estructurado",
            "tracing": "✅ OpenTelemetry",
            "security": "✅ Headers"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "ejemplo_servicio"
    }

@app.get("/test/{item_id}")
async def test_endpoint(item_id: str):
    """Endpoint de prueba"""
    return {
        "item_id": item_id,
        "message": "Endpoint funcionando correctamente",
        "features_active": [
            "Structured logging",
            "Performance monitoring",
            "Security headers",
            "Request ID tracking"
        ]
    }

# Intentar usar workers si están disponibles
try:
    from shared_lib.workers import WorkerManager, WorkerType
    
    worker_manager = WorkerManager(
        worker_type=WorkerType.ASYNC,
        max_workers=3
    )
    
    @app.on_event("startup")
    async def startup():
        await worker_manager.start()
        logger.info("✅ Workers iniciados")
    
    @app.on_event("shutdown")
    async def shutdown():
        await worker_manager.stop()
        logger.info("✅ Workers detenidos")
    
    @app.post("/async-task")
    async def create_async_task(data: dict):
        """Crea una tarea asíncrona"""
        async def process_task(data):
            await asyncio.sleep(1)  # Simular procesamiento
            return {"processed": data, "status": "completed"}
        
        task_id = await worker_manager.enqueue_task(process_task, data)
        return {"task_id": task_id, "status": "enqueued"}
    
    logger.info("✅ Workers disponibles")
    
except ImportError:
    logger.warning("⚠️  Workers no disponibles (opcional)")

# Intentar usar message broker si está disponible
try:
    from shared_lib.messaging import MessageBrokerManager, BrokerType
    
    message_broker = MessageBrokerManager(
        broker_type=BrokerType.REDIS,
        connection_url="redis://localhost:6379/0"
    )
    
    def handle_event(message):
        logger.info(f"Evento recibido: {message}")
    
    message_broker.subscribe("test.event", handle_event)
    
    @app.post("/publish-event")
    async def publish_event(data: dict):
        """Publica un evento"""
        message_broker.publish("test.event", data)
        return {"status": "published", "event": "test.event"}
    
    logger.info("✅ Message broker disponible")
    
except ImportError:
    logger.warning("⚠️  Message broker no disponible (opcional)")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Iniciando servidor de ejemplo...")
    logger.info("📡 Servidor disponible en http://localhost:8000")
    logger.info("📊 Docs disponibles en http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )




