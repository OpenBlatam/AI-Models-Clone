from fastapi import APIRouter, HTTPException, Body, Request as FastAPIRequest
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, AnyUrl, ValidationError, root_validator
from typing import List, Optional, Union
from models import AdsIaRequest, AdsResponse, BrandKitResponse, ErrorResponse
from scraper_service import get_website_text_async
from llm_interface import (
    generate_ads_lcel,
    generate_brand_kit_lcel,
    generate_custom_content_lcel,
    generate_ads_lcel_streaming,
    generate_ads_lcel_streaming_parallel,
    DEEPSEEK_API_KEY
)
from config import settings
import logging
import asyncio
import uuid
import re
from schemas import AdsIaStreamRequest
from generation_service import generate_ads, generate_brand_kit, generate_custom_content

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

MAX_BATCH_URLS = getattr(settings, 'MAX_BATCH_URLS', 20)
MAX_TEXT_CHARS = getattr(settings, 'MAX_TEXT_CHARS', 1500)

class BatchScrapeRequest(BaseModel):
    urls: List[str]

    @root_validator(pre=True)
    def validate_urls(cls, values):
        urls = values.get('urls', [])
        valid_urls = []
        url_pattern = re.compile(r'^https?://')
        for url in urls:
            if not isinstance(url, str) or not url_pattern.match(url):
                raise ValueError(f"URL inválida o no soportada: {url}")
            # Opcional: más reglas de sanitización aquí
            valid_urls.append(url)
        values['urls'] = valid_urls
        return values

@router.post("/api/ads-ia",
    summary="Genera anuncios, brand kits o contenido personalizado desde una URL",
    response_model=Union[AdsResponse, BrandKitResponse, ErrorResponse],
    responses={
        200: {"description": "Operación exitosa"},
        400: {"model": ErrorResponse, "description": "Solicitud incorrecta"},
        422: {"model": ErrorResponse, "description": "Error de validación de entrada"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"},
        503: {"model": ErrorResponse, "description": "Servicio DeepSeek no disponible o no configurado"}
    })
async def process_ads_ia_request(payload: AdsIaRequest, http_request: FastAPIRequest):
    trace_id = http_request.headers.get("x-trace-id") or str(uuid.uuid4())
    logger.info({"event": "ads-ia-request", "trace_id": trace_id, "url": str(payload.url), "type": payload.type, "prompt": payload.prompt})
    if not DEEPSEEK_API_KEY:
        return ErrorResponse(error="Servicio DeepSeek no configurado", details="DEEPSEEK_API_KEY no está configurado en el backend.")
    website_text = payload.website_content or await get_website_text_async(str(payload.url)) or ""
    try:
        if payload.prompt:
            generated_content = await generate_custom_content(payload.prompt, website_text)
            return AdsResponse(ads=generated_content)
        elif payload.type == "ads":
            if not website_text:
                return ErrorResponse(error="Contenido web necesario para anuncios", details="No se pudo obtener contenido de la URL.")
            ads_list = await generate_ads(website_text)
            return AdsResponse(ads=ads_list)
        elif payload.type == "brand-kit":
            if not website_text:
                return ErrorResponse(error="Contenido web necesario para brand kit", details="No se pudo obtener contenido de la URL.")
            brand_kit_string = await generate_brand_kit(website_text)
            return BrandKitResponse(brandKit=brand_kit_string)
        else:
            return ErrorResponse(error="Tipo de solicitud no válido")
    except Exception as e:
        logger.error({"event": "ads-ia-error", "trace_id": trace_id, "error": str(e)})
        return ErrorResponse(error="Error interno del servidor", details=str(e))

@router.post("/api/ads-ia/stream",
    summary="Genera anuncios en streaming desde una URL (SSE)",
    response_model=None,
    responses={
        200: {"description": "Stream de anuncios (SSE)"},
        400: {"model": ErrorResponse, "description": "Solicitud incorrecta"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    })
async def process_ads_ia_stream(payload: AdsIaStreamRequest, http_request: FastAPIRequest):
    trace_id = http_request.headers.get("x-trace-id") or str(uuid.uuid4())
    logger.info({"event": "ads-ia-stream", "trace_id": trace_id, "url": str(payload.url), "n_ads": payload.n_ads, "max_length": payload.max_length})
    website_content = payload.website_content or await get_website_text_async(payload.url)
    if website_content:
        website_content = website_content[:payload.max_length or 800]
    else:
        website_content = ""
    async def ad_generator():
        async for ad in generate_ads_lcel_streaming_parallel(website_content or "", n_ads=payload.n_ads or 1):
            yield ad
    return StreamingResponse(ad_generator(), media_type="text/event-stream")

@router.post("/api/ads-ia/batch",
    summary="Scrapea múltiples URLs en paralelo y devuelve su texto web",
    responses={
        200: {
            "description": "Operación exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "trace_id": "abc-123",
                        "results": {
                            "https://ok.com": "Texto web...",
                            "https://fail.com": {"error": "Timeout", "details": "..."}
                        }
                    }
                }
            }
        },
        400: {"model": ErrorResponse, "description": "Solicitud incorrecta", "content": {"application/json": {"example": {"error": "URL inválida o no soportada: ftp://maliciosa.com", "details": None}}}},
        500: {"model": ErrorResponse, "description": "Error interno del servidor", "content": {"application/json": {"example": {"error": "Error interno del servidor", "details": "..."}}}}
    })
async def batch_scrape_ads_ia(
    req: BatchScrapeRequest = Body(..., embed=True, description=f"Lista de URLs a scrapear. Máximo permitido: {MAX_BATCH_URLS}. Solo http/https."),
    max_concurrency: int = 10,
    timeout: int = 7,
    http_request: FastAPIRequest = None
):
    """
    Scrapea múltiples URLs en paralelo usando get_website_text_async y asyncio.gather.
    - **urls**: lista de URLs a scrapear (máximo permitido: {MAX_BATCH_URLS}, solo http/https).
    - **max_concurrency**: máximo de tareas concurrentes (default 10, máximo recomendado 20).
    - **timeout**: timeout por URL en segundos (default 7).
    - **trace_id**: ID de trazabilidad para correlación de logs.
    - **max_text_chars**: máximo de caracteres retornados por URL ({MAX_TEXT_CHARS}).
    - Devuelve error 400 si alguna URL es inválida o peligrosa.
    """
    urls = req.urls
    trace_id = http_request.headers.get("x-trace-id") if http_request else str(uuid.uuid4())
    logger.info({"event": "batch-ads-ia-scrape", "trace_id": trace_id, "n_urls": len(urls), "max_concurrency": max_concurrency, "timeout": timeout})
    if not urls or not isinstance(urls, list):
        return JSONResponse(status_code=400, content=ErrorResponse(error="Lista de URLs vacía o inválida", details=None).model_dump())
    if len(urls) > MAX_BATCH_URLS:
        return JSONResponse(status_code=400, content=ErrorResponse(error=f"Demasiadas URLs (máx {MAX_BATCH_URLS})", details=None).model_dump())
    sem = asyncio.Semaphore(max_concurrency)
    async def scrape_one(url):
        async with sem:
            try:
                text = await asyncio.wait_for(get_website_text_async(url, timeout=timeout), timeout=timeout+1)
                if text is None:
                    return url, {"error": "No se pudo extraer texto", "details": None}
                return url, text[:MAX_TEXT_CHARS]
            except asyncio.TimeoutError:
                logger.warning({"event": "batch-scrape-timeout", "trace_id": trace_id, "url": url})
                return url, {"error": "Timeout", "details": f"Timeout de {timeout}s"}
            except Exception as e:
                logger.warning({"event": "batch-scrape-error", "trace_id": trace_id, "url": url, "error": str(e)})
                return url, {"error": str(type(e).__name__), "details": str(e)}
    results = await asyncio.gather(*(scrape_one(url) for url in urls))
    return {"trace_id": trace_id, "results": dict(results)}

@router.get("/health", summary="Healthcheck simple para monitoreo", response_description="OK si el servicio está vivo")
async def healthcheck():
    """
    Endpoint de healthcheck para monitoreo. Devuelve 200 OK si el servicio responde.
    Úsalo para monitoreo de uptime y despliegue en cloud/Kubernetes.
    """
    return {"status": "ok"}

@router.get("/readiness", summary="Readiness para orquestadores", response_description="OK si el servicio está listo")
async def readiness():
    """
    Endpoint de readiness para orquestadores (Kubernetes, etc). Devuelve 200 OK si el servicio está listo para recibir tráfico.
    """
    return {"ready": True} 