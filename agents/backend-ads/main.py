# app/main.py
import os
import httpx
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Body, Request as FastAPIRequest
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .models import AdsIaRequest, AdsResponse, BrandKitResponse, ErrorResponse
from .scraper import get_website_text
from .llm_interface import (
    generate_ads_direct,
    generate_brand_kit_direct,
    generate_custom_content_direct,
    LLM_MODEL_NAME,
    OLLAMA_API_BASE_URL
)

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    logger.info("Iniciando aplicación y cliente HTTPX...")
    # El timeout se puede ajustar globalmente aquí o por solicitud.
    # Un timeout de 2 minutos para el cliente puede ser razonable para LLMs.
    app_instance.state.httpx_client = httpx.AsyncClient(timeout=120.0)
    
    if not LLM_MODEL_NAME:
        logger.critical("DEEPSEEK_MODEL_NAME no está configurado. El LLM no funcionará.")
    else:
        logger.info(f"Configurado para usar LLM: {LLM_MODEL_NAME} en {OLLAMA_API_BASE_URL}")
        try:
            # Un simple GET a la URL base de Ollama (o similar) suele ser suficiente
            # para verificar conectividad básica, aunque no garantiza que el modelo esté cargado.
            # Ollama responde con "Ollama is running" en su raíz.
            api_check_url = OLLAMA_API_BASE_URL.rstrip('/')
            response = await app_instance.state.httpx_client.get(api_check_url, timeout=5.0) # Timeout corto para el health check
            if response.status_code == 200:
                logger.info(f"Conexión exitosa con el endpoint del LLM en {api_check_url}.")
            else:
                logger.warning(f"No se pudo confirmar la conexión con el LLM (status: {response.status_code} en {api_check_url}). Verifique URL y servicio.")
        except httpx.RequestError as e:
            logger.error(f"CRÍTICO: No se pudo conectar al endpoint del LLM en {OLLAMA_API_BASE_URL}. Error: {e}")
            logger.error("El servicio LLM podría no estar disponible o la URL es incorrecta.")
    
    yield

    logger.info("Cerrando cliente HTTPX y finalizando aplicación...")
    await app_instance.state.httpx_client.aclose()


app = FastAPI(title="Ads IA API - Direct LLM Integration", version="1.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción: CAMBIAR a ['http://tufrontend.com', 'https://tufrontend.com']
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"], # OPTIONS es necesario para preflight requests de CORS
    allow_headers=["Content-Type", "Authorization"], # Especificar los headers que permites
)


@app.post("/api/ads-ia",
          summary="Genera anuncios, brand kits o contenido personalizado desde una URL",
          responses={
              200: {"description": "Operación exitosa"},
              400: {"model": ErrorResponse, "description": "Solicitud incorrecta"},
              422: {"model": ErrorResponse, "description": "Error de validación de entrada"},
              500: {"model": ErrorResponse, "description": "Error interno del servidor"},
              503: {"model": ErrorResponse, "description": "Servicio LLM no disponible o no configurado"}
          })
async def process_ads_ia_request(payload: AdsIaRequest, http_request: FastAPIRequest):
    # El cliente HTTPX se obtiene del estado de la aplicación, gestionado por lifespan
    active_httpx_client: httpx.AsyncClient = http_request.app.state.httpx_client

    if not LLM_MODEL_NAME:
        logger.error("Intento de llamada a /api/ads-ia sin LLM_MODEL_NAME configurado.")
        raise HTTPException(status_code=503, detail={
            "error": "Servicio LLM no configurado",
            "details": "DEEPSEEK_MODEL_NAME no está configurado en el backend."
        })

    logger.info(f"API Call: type='{payload.type}', url='{payload.url}', prompt_present={bool(payload.prompt)}")
    
    website_text = get_website_text(str(payload.url))
    if not website_text and not payload.prompt: # Si no hay prompt, el texto web es esencial
        logger.warning(f"No se pudo extraer texto de la URL: {payload.url} y no se proporcionó prompt.")
        raise HTTPException(
            status_code=400,
            detail={"error": "Error al obtener contenido de la URL", "details": f"No se pudo extraer texto de {payload.url} y no se proveyó un prompt alternativo."}
        )
    effective_website_text = website_text if website_text else ""

    try:
        if payload.prompt:
            logger.info(f"Generando contenido personalizado...")
            generated_content = await generate_custom_content_direct(payload.prompt, effective_website_text, client=active_httpx_client)
            if not generated_content:
                 logger.error("Error al generar contenido personalizado: Respuesta vacía o error del LLM.")
                 raise HTTPException(status_code=500, detail={"error": "Error al generar contenido personalizado", "details": "Respuesta vacía o error del LLM."})
            return AdsResponse(ads=generated_content)

        elif payload.type == "ads":
            if not effective_website_text: # El scraper pudo haber devuelto None o ""
                 logger.warning(f"Contenido web necesario para anuncios, pero no se obtuvo de {payload.url}")
                 raise HTTPException(status_code=400, detail={"error": "Contenido web necesario para anuncios", "details": "No se pudo obtener contenido de la URL."})
            logger.info("Generando anuncios...")
            ads_list = await generate_ads_direct(effective_website_text, client=active_httpx_client)
            if not ads_list:
                 logger.error("Error al generar anuncios: Respuesta vacía o error del LLM.")
                 raise HTTPException(status_code=500, detail={"error": "Error al generar anuncios", "details": "Respuesta vacía o error del LLM."})
            return AdsResponse(ads=ads_list)

        elif payload.type == "brand-kit":
            if not effective_website_text:
                 logger.warning(f"Contenido web necesario para brand kit, pero no se obtuvo de {payload.url}")
                 raise HTTPException(status_code=400, detail={"error": "Contenido web necesario para brand kit", "details": "No se pudo obtener contenido de la URL."})
            logger.info("Generando brand kit...")
            brand_kit_string = await generate_brand_kit_direct(effective_website_text, client=active_httpx_client)
            if not brand_kit_string:
                logger.error("Error al generar brand kit: Respuesta vacía o error del LLM.")
                raise HTTPException(status_code=500, detail={"error": "Error al generar brand kit", "details": "Respuesta vacía o error del LLM."})
            return BrandKitResponse(brandKit=brand_kit_string)
        else:
            # Este caso no debería ocurrir debido a la validación de Pydantic en AdsIaRequest.type
            logger.error(f"Tipo de solicitud no válido recibido: {payload.type}")
            raise HTTPException(status_code=400, detail={"error": "Tipo de solicitud no válido"})

    except HTTPException as http_exc:
        # Re-lanzar excepciones HTTP para que FastAPI las maneje correctamente
        raise http_exc
    except Exception as e:
        logger.exception(f"Error inesperado en el servidor durante el procesamiento de {payload.url}: {e}")
        return JSONResponse(status_code=500, content=ErrorResponse(error="Error interno del servidor", details=str(e)).model_dump())

# Para ejecutar localmente (desde la carpeta `ads-ia-backend`):
# pip install -r requirements.txt
# cp .env.example .env  (y edita .env)
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000