"""
Ejemplo de main.py para usar con Docker
=======================================

Este es un ejemplo de cómo estructurar main.py para usar con los Dockerfiles.
"""

from fastapi import FastAPI
from shared_lib.middleware import setup_advanced_middleware

# Crear aplicación
app = FastAPI(
    title="Shared Library Example",
    description="Ejemplo de uso de shared_lib con Docker",
    version="1.0.0"
)

# Configurar middleware avanzado
setup_advanced_middleware(
    app,
    service_name="shared-lib-example",
    enable_opentelemetry=True
)

# Endpoints
@app.get("/")
async def root():
    """Health check"""
    return {
        "message": "Shared Library Example",
        "status": "running",
        "deployment": "Docker"
    }

@app.get("/health")
async def health():
    """Health check detallado"""
    return {
        "status": "healthy",
        "service": "shared-lib-example"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8030)




