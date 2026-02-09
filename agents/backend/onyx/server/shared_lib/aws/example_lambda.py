"""
Ejemplo de Lambda Function con Shared Library
==============================================

Ejemplo completo de cómo usar shared_lib en AWS Lambda.
"""

from fastapi import FastAPI
from shared_lib.middleware import setup_advanced_middleware
from shared_lib.aws import create_lambda_handler, dynamodb_manager, cloudwatch_metrics

# Crear aplicación FastAPI
app = FastAPI(
    title="Music Analyzer AI - Lambda",
    description="API desplegada en AWS Lambda",
    version="1.0.0"
)

# Configurar middleware avanzado
setup_advanced_middleware(
    app,
    service_name="music-analyzer-ai-lambda",
    enable_opentelemetry=True
)

# Endpoints
@app.get("/")
async def root():
    """Health check"""
    return {
        "message": "Music Analyzer AI - Lambda",
        "status": "running",
        "deployment": "AWS Lambda"
    }

@app.get("/health")
async def health():
    """Health check detallado"""
    return {
        "status": "healthy",
        "service": "music-analyzer-ai",
        "platform": "AWS Lambda"
    }

@app.post("/analyze/{track_id}")
async def analyze_track(track_id: str):
    """Analiza un track"""
    # Registrar métrica
    cloudwatch_metrics.increment_counter(
        "tracks_analyzed",
        dimensions={"service": "music-analyzer-ai"}
    )
    
    # Simular análisis
    result = {
        "track_id": track_id,
        "status": "analyzed",
        "features": {
            "tempo": 120,
            "key": "C",
            "mode": "major"
        }
    }
    
    # Guardar en DynamoDB (opcional)
    if dynamodb_manager:
        await dynamodb_manager.put_item(
            "tracks",
            {
                "id": track_id,
                **result
            }
        )
    
    return result

@app.get("/tracks/{track_id}")
async def get_track(track_id: str):
    """Obtiene un track"""
    if dynamodb_manager:
        track = await dynamodb_manager.get_item(
            "tracks",
            {"id": track_id}
        )
        if track:
            return track
    
    return {"error": "Track not found"}

# Crear handler Lambda
handler = create_lambda_handler(
    app,
    lifespan="off",
    enable_cors=True
)

# Para uso local (opcional)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




