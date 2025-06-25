from fastapi import APIRouter, HTTPException, Query, Depends, Body, status, Request, Security
from .models import CopywritingInput, CopywritingOutput, Feedback, SectionFeedback, CopyVariantHistory, get_settings
from .service import CopywritingService
from .tasks import generate_copywriting_task
from typing import List, Optional
from celery.result import AsyncResult
import logging
import os

# Prometheus metrics
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# FastAPI Security
from fastapi.security.api_key import APIKeyHeader

settings = get_settings()

# Use settings.api_key in get_api_key
API_KEY = settings.api_key

# Use settings.allowed_cors_origins for CORS (in main app, but show here as comment)
# allow_origins=settings.allowed_cors_origins

# Use settings.redis_url for Redis (limiter/cache)
# redis = await aioredis.create_redis_pool(settings.redis_url)

# Use settings.mlflow_tracking_uri and settings.dask_scheduler_address as needed in other modules

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return api_key

# SQLAlchemy para persistencia de feedback
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from sqlalchemy.orm import Session

SQLITE_URL = os.environ.get("COPYWRITING_FEEDBACK_DB", "sqlite:///copywriting_feedback.db")
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class FeedbackDB(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(String, index=True)
    type = Column(String)
    score = Column(Float, nullable=True)
    comments = Column(Text, nullable=True)
    user_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    raw_json = Column(Text)

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/copywriting", tags=["copywriting"])
logger = logging.getLogger("copywriting.api")

AVAILABLE_MODELS = ["gpt2", "distilgpt2"]  # Puedes expandir esta lista
MAX_BATCH_SIZE = 20

# Instrumentator para métricas
instrumentator = Instrumentator() if PROMETHEUS_AVAILABLE else None

# Seguridad básica: placeholder para autenticación/roles
# from fastapi import Security, Depends
# def get_current_user(): ...

from fastapi import Depends
from fastapi_limiter.depends import RateLimiter
from fastapi_cache2.decorator import cache

def get_service(model_name: str = Query("gpt2", description="HuggingFace model name")):
    return CopywritingService(model_name=model_name)

@router.on_event("startup")
def _setup_metrics():
    if PROMETHEUS_AVAILABLE and instrumentator:
        import sys
        # Instrumenta solo si no está ya instrumentado
        if not getattr(sys.modules[__name__], "_instrumented", False):
            from fastapi import FastAPI
            app = router.routes[0].app if router.routes else None
            if isinstance(app, FastAPI):
                instrumentator.instrument(app).expose(app, endpoint="/copywriting/metrics", include_in_schema=True)
                setattr(sys.modules[__name__], "_instrumented", True)

@router.get("/metrics", include_in_schema=False)
def metrics():
    if PROMETHEUS_AVAILABLE and instrumentator:
        from fastapi.responses import PlainTextResponse
        return instrumentator.registry.generate_latest(), 200, {"Content-Type": "text/plain; version=0.0.4; charset=utf-8"}
    else:
        return {"error": "Prometheus metrics not available. Install prometheus_fastapi_instrumentator."}

@router.get("/models", summary="List available copywriting models", tags=["copywriting"])
@cache(expire=60)  # Cache this endpoint for 60 seconds
def list_models():
    """Devuelve los modelos de copywriting disponibles."""
    return {"available_models": AVAILABLE_MODELS}

@router.get("/task-status/{task_id}", summary="Get Celery task status/result", tags=["copywriting"])
def get_task_status(task_id: str):
    """Consulta el estado y resultado de una tarea de copywriting enviada por Celery."""
    result = AsyncResult(task_id)
    if result.state == "PENDING":
        return {"status": result.state}
    elif result.state == "SUCCESS":
        return {"status": result.state, "result": result.result}
    elif result.state == "FAILURE":
        return {"status": result.state, "error": str(result.info)}
    else:
        return {"status": result.state}

@router.post(
    "/batch-status",
    summary="Get status/results for multiple Celery tasks",
    tags=["copywriting"],
    responses={
        200: {"description": "Batch status/result for tasks", "content": {"application/json": {}}},
        401: {"description": "API Key inválida o ausente"},
    },
)
def batch_task_status(
    task_ids: List[str] = Body(..., description="List of Celery task IDs to check status for"),
    api_key: str = Depends(get_api_key)
):
    """
    Devuelve el estado y resultado de múltiples tareas de Celery.
    """
    results = []
    for task_id in task_ids:
        result = AsyncResult(task_id)
        results.append({
            "task_id": task_id,
            "status": result.state,
            "result": result.result if result.state == "SUCCESS" else None,
            "error": str(result.info) if result.state == "FAILURE" else None,
        })
    return {"tasks": results}

@router.post(
    "/generate",
    response_model=CopywritingOutput,
    summary="Genera copywriting con modelo LLM",
    tags=["copywriting"],
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],  # 5 requests per minute per IP
    responses={
        200: {"description": "Copywriting generado exitosamente", "model": CopywritingOutput},
        400: {"description": "Modelo no soportado o input inválido"},
        401: {"description": "API Key inválida o ausente"},
        500: {"description": "Error interno del modelo"},
    },
)
async def generate_copywriting(
    request: CopywritingInput = Body(..., example={
        "product_description": "Zapatos deportivos de alta gama",
        "target_platform": "Instagram",
        "tone": "inspirational",
        "target_audience": "Jóvenes activos",
        "key_points": ["Comodidad", "Estilo", "Durabilidad"],
        "instructions": "Enfatiza la innovación.",
        "restrictions": ["no mencionar precio"],
        "creativity_level": 0.8,
        "language": "es"
    }),
    model_name: str = Query("gpt2", description="Nombre del modelo HuggingFace a usar", enum=AVAILABLE_MODELS),
    service: CopywritingService = Depends(get_service),
    request_obj: Request = None,
    api_key: str = Depends(get_api_key)
):
    # TODO: Log this generation with MLflow for experiment tracking
    logger.info(f"/generate called from {request_obj.client.host if request_obj else 'unknown'} with model={model_name}")
    if model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Modelo '{model_name}' no soportado.")
    try:
        result = await service.generate(request)
        return result
    except Exception as e:
        logger.error(f"Error in /generate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/batch-generate",
    summary="Batch submit copywriting jobs via Celery",
    tags=["copywriting"],
    responses={
        200: {"description": "Batch procesado", "content": {"application/json": {}}},
        400: {"description": "Modelo no soportado o batch demasiado grande"},
        401: {"description": "API Key inválida o ausente"},
        500: {"description": "Error interno"},
    },
)
async def batch_generate_copywriting(
    requests: List[CopywritingInput] = Body(..., example=[{"product_description": "Zapatos...", "target_platform": "Instagram", "tone": "inspirational"}]),
    model_name: str = Query("gpt2", description="HuggingFace model name", enum=AVAILABLE_MODELS),
    wait: bool = Query(False, description="Wait for results (synchronous)"),
    api_key: str = Depends(get_api_key)
):
    """Batch submit copywriting jobs via Celery. Returns task IDs or results if wait=True."""
    if model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Modelo '{model_name}' no soportado.")
    if len(requests) > MAX_BATCH_SIZE:
        raise HTTPException(status_code=400, detail=f"El batch máximo permitido es {MAX_BATCH_SIZE}.")
    tasks = [generate_copywriting_task.delay(req.dict(), model_name=model_name) for req in requests]
    if wait:
        # Wait for all results (no recomendado para batches grandes)
        try:
            results = [t.get(timeout=120) for t in tasks]
        except Exception as e:
            logger.error(f"Error en batch wait: {e}")
            raise HTTPException(status_code=500, detail="Error procesando el batch: " + str(e))
        return {"results": results}
    else:
        return {"task_ids": [t.id for t in tasks]}

@router.post(
    "/feedback",
    summary="Envía feedback sobre una variante de copywriting (incluye feedback granular por sección e historial de variantes)",
    tags=["copywriting"],
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        202: {"description": "Feedback recibido"},
        400: {"description": "Input inválido"},
        401: {"description": "API Key inválida o ausente"},
    },
)
async def submit_feedback(
    variant_id: str = Body(..., embed=True, description="ID de la variante a la que se da feedback"),
    feedback: Feedback = Body(..., description="Feedback estructurado sobre la variante"),
    section_feedback: Optional[list[SectionFeedback]] = Body(None, description="Feedback granular por sección (opcional)"),
    variant_history: Optional[CopyVariantHistory] = Body(None, description="Historial de la variante (opcional)"),
    api_key: str = Depends(get_api_key)
):
    """
    Recibe feedback sobre una variante de copywriting. Persiste en SQLite. Ahora soporta feedback granular por sección e historial de variantes.
    """
    logger.info(f"Feedback recibido para variante {variant_id}: {feedback}")
    db = SessionLocal()
    try:
        feedback_data = feedback.dict()
        if section_feedback:
            feedback_data["section_feedback"] = [sf.dict() for sf in section_feedback]
        if variant_history:
            feedback_data["variant_history"] = variant_history.dict()
        db_feedback = FeedbackDB(
            variant_id=variant_id,
            type=feedback.type.value,
            score=feedback.score,
            comments=feedback.comments,
            user_id=feedback.user_id,
            timestamp=datetime.fromisoformat(feedback.timestamp) if feedback.timestamp else datetime.utcnow(),
            raw_json=json.dumps(feedback_data)
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        logger.info(f"Feedback guardado con id={db_feedback.id}")
        return {"status": "accepted", "variant_id": variant_id, "feedback_id": db_feedback.id}
    except Exception as e:
        db.rollback()
        logger.error(f"Error guardando feedback: {e}")
        raise HTTPException(status_code=500, detail="Error guardando feedback")
    finally:
        db.close()

# --- FastAPI-Filter for advanced filtering ---
# pip install fastapi-filter
from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter

# FeedbackFilter for advanced filtering
class FeedbackFilter(Filter):
    variant_id: str | None = None
    user_id: str | None = None
    type: str | None = None
    score__gte: float | None = None
    score__lte: float | None = None
    timestamp__gte: str | None = None
    timestamp__lte: str | None = None

    class Constants(Filter.Constants):
        model = FeedbackDB

@router.get(
    "/feedback",
    summary="Consulta feedback guardado (incluye feedback granular por sección e historial de variantes si existe)",
    tags=["copywriting"],
    response_model=List[dict],
    responses={
        200: {"description": "Lista de feedback"},
        401: {"description": "API Key inválida o ausente"},
    },
)
def list_feedback(
    feedback_filter: FeedbackFilter = FilterDepends(FeedbackFilter),
    skip: int = Query(0, ge=0, description="Salto de paginación"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados"),
    api_key: str = Depends(get_api_key),
    # Backward compatibility for old query params
    variant_id: str | None = Query(None, description="Filtrar por variant_id"),
    user_id: str | None = Query(None, description="Filtrar por user_id"),
):
    """
    Devuelve feedback guardado, filtrable por cualquier campo, con paginación y filtros avanzados. Incluye feedback granular por sección e historial de variantes si existe.
    """
    db: Session = SessionLocal()
    try:
        query = db.query(FeedbackDB)
        # Apply FastAPI-Filter
        query = feedback_filter.filter(query)
        # Backward compatibility: apply old filters if present
        if variant_id:
            query = query.filter(FeedbackDB.variant_id == variant_id)
        if user_id:
            query = query.filter(FeedbackDB.user_id == user_id)
        results = query.order_by(FeedbackDB.timestamp.desc()).offset(skip).limit(limit).all()
        return [
            {
                "id": f.id,
                "variant_id": f.variant_id,
                "type": f.type,
                "score": f.score,
                "comments": f.comments,
                "user_id": f.user_id,
                "timestamp": f.timestamp.isoformat() if f.timestamp else None,
                "raw_json": f.raw_json,
                "section_feedback": json.loads(f.raw_json).get("section_feedback") if f.raw_json else None,
                "variant_history": json.loads(f.raw_json).get("variant_history") if f.raw_json else None
            }
            for f in results
        ]
    finally:
        db.close()

@router.get(
    "/variant-history/{variant_id}",
    summary="Consulta el historial de una variante de copywriting (si existe)",
    tags=["copywriting"],
    response_model=Optional[dict],
    responses={
        200: {"description": "Historial de la variante (si existe)"},
        404: {"description": "No se encontró historial para ese variant_id"},
        401: {"description": "API Key inválida o ausente"},
    },
)
def get_variant_history(
    variant_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    Devuelve el historial de una variante de copywriting, si fue almacenado junto con el feedback.
    """
    db: Session = SessionLocal()
    try:
        feedbacks = db.query(FeedbackDB).filter(FeedbackDB.variant_id == variant_id).order_by(FeedbackDB.timestamp.desc()).all()
        for f in feedbacks:
            raw = f.raw_json
            if raw:
                data = json.loads(raw)
                if "variant_history" in data:
                    return data["variant_history"]
        raise HTTPException(status_code=404, detail="No se encontró historial para ese variant_id")
    finally:
        db.close()

@router.get(
    "/optimization-results/{tracking_id}",
    summary="Consulta los resultados de optimización asociados a un tracking_id (si existen)",
    tags=["copywriting"],
    response_model=Optional[dict],
    responses={
        200: {"description": "Resultados de optimización (si existen)"},
        404: {"description": "No se encontraron resultados para ese tracking_id"},
        401: {"description": "API Key inválida o ausente"},
    },
)
def get_optimization_results(
    tracking_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    Devuelve los resultados de optimización asociados a un tracking_id, si fueron almacenados junto con el feedback o el output.
    """
    db: Session = SessionLocal()
    try:
        # Buscar en feedbacks
        feedbacks = db.query(FeedbackDB).filter(FeedbackDB.raw_json.contains(tracking_id)).order_by(FeedbackDB.timestamp.desc()).all()
        for f in feedbacks:
            raw = f.raw_json
            if raw:
                data = json.loads(raw)
                if "optimization_results" in data:
                    return data["optimization_results"]
        # (Opcional) Aquí podrías buscar en outputs generados si los guardas en otra tabla
        raise HTTPException(status_code=404, detail="No se encontraron resultados para ese tracking_id")
    finally:
        db.close()

@router.post(
    "/refactor",
    response_model=CopywritingOutput,
    summary="Refactoriza un texto usando el modelo LLM",
    tags=["copywriting"],
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    responses={
        200: {"description": "Texto refactorizado exitosamente", "model": CopywritingOutput},
        400: {"description": "Modelo no soportado o input inválido"},
        401: {"description": "API Key inválida o ausente"},
        500: {"description": "Error interno del modelo"},
    },
)
async def refactor_copywriting(
    text: str = Body(..., embed=True, description="Texto a refactorizar"),
    model_name: str = Query("gpt2", description="Nombre del modelo HuggingFace a usar", enum=AVAILABLE_MODELS),
    service: CopywritingService = Depends(get_service),
    request_obj: Request = None,
    api_key: str = Depends(get_api_key)
):
    """
    Refactoriza un texto usando el modelo LLM, reutilizando la lógica de generación con la instrucción 'refactor'.
    """
    logger.info(f"/refactor called from {request_obj.client.host if request_obj else 'unknown'} with model={model_name}")
    if model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Modelo '{model_name}' no soportado.")
    try:
        request = CopywritingInput(
            product_description=text,
            target_platform="refactor",
            tone="informative",
            instructions="refactor",
            language="es"
        )
        result = await service.generate(request)
        return result
    except Exception as e:
        logger.error(f"Error in /refactor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/optimiza",
    response_model=CopywritingOutput,
    summary="Optimiza un texto usando el modelo LLM",
    tags=["copywriting"],
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    responses={
        200: {"description": "Texto optimizado exitosamente", "model": CopywritingOutput},
        400: {"description": "Modelo no soportado o input inválido"},
        401: {"description": "API Key inválida o ausente"},
        500: {"description": "Error interno del modelo"},
    },
)
async def optimiza_copywriting(
    text: str = Body(..., embed=True, description="Texto a optimizar"),
    model_name: str = Query("gpt2", description="Nombre del modelo HuggingFace a usar", enum=AVAILABLE_MODELS),
    service: CopywritingService = Depends(get_service),
    request_obj: Request = None,
    api_key: str = Depends(get_api_key)
):
    """
    Optimiza un texto usando el modelo LLM, reutilizando la lógica de generación con la instrucción 'optimiza'.
    """
    logger.info(f"/optimiza called from {request_obj.client.host if request_obj else 'unknown'} with model={model_name}")
    if model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Modelo '{model_name}' no soportado.")
    try:
        request = CopywritingInput(
            product_description=text,
            target_platform="optimiza",
            tone="informative",
            instructions="optimiza",
            language="es"
        )
        result = await service.generate(request)
        return result
    except Exception as e:
        logger.error(f"Error in /optimiza: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/optimiza-con-librerias",
    response_model=CopywritingOutput,
    summary="Optimiza un texto con librerías usando el modelo LLM",
    tags=["copywriting"],
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    responses={
        200: {"description": "Texto optimizado con librerías exitosamente", "model": CopywritingOutput},
        400: {"description": "Modelo no soportado o input inválido"},
        401: {"description": "API Key inválida o ausente"},
        500: {"description": "Error interno del modelo"},
    },
)
async def optimiza_con_librerias_copywriting(
    text: str = Body(..., embed=True, description="Texto a optimizar con librerías"),
    model_name: str = Query("gpt2", description="Nombre del modelo HuggingFace a usar", enum=AVAILABLE_MODELS),
    service: CopywritingService = Depends(get_service),
    request_obj: Request = None,
    api_key: str = Depends(get_api_key)
):
    """
    Optimiza un texto usando el modelo LLM, reutilizando la lógica de generación con la instrucción 'optimiza con librerias'.
    """
    logger.info(f"/optimiza-con-librerias called from {request_obj.client.host if request_obj else 'unknown'} with model={model_name}")
    if model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Modelo '{model_name}' no soportado.")
    try:
        request = CopywritingInput(
            product_description=text,
            target_platform="optimiza-con-librerias",
            tone="informative",
            instructions="optimiza con librerias",
            language="es"
        )
        result = await service.generate(request)
        return result
    except Exception as e:
        logger.error(f"Error in /optimiza-con-librerias: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 