# app/llm_interface.py
import logging
from .config import settings # Importar la configuración

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel as LangchainPydanticBaseModel, Field as LangchainField
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

if not settings.LLM_MODEL_NAME:
    logger.critical("LLM_MODEL_NAME no está configurado. Las funciones de LLM están deshabilitadas.")
    llm = None
else:
    try:
        llm = ChatOllama(
            model=settings.LLM_MODEL_NAME,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
            request_timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS,
            # ChatOllama puede tomar max_retries directamente si su cliente http lo soporta.
            # Si no, puedes envolver la llamada a .ainvoke con tenacity también.
            # Para ChatOllama (que usa httpx), httpx.Client tiene un argumento `max_retries`
            # pero no es directamente expuesto por ChatOllama.
            # Langchain Runnable tiene .with_retry()
            # Por ahora, si ChatOllama no tiene un `max_retries` directo, lo dejaremos así
            # y se podría añadir `.with_retry()` a cada chain.
            # Actualización: El cliente de Langchain para Ollama tiene `Ollama(..., num_predict=-1, stop=None, timeout=None, num_gpu=None, num_thread=None, base_url='http://localhost:11434', model='llama2', mirostat=None, mirostat_eta=None, mirostat_tau=None, num_ctx=None, repeat_last_n=None, repeat_penal
            # No veo `max_retries` directo. Usaremos `.with_retry()` en las cadenas.
        )
        logger.info(f"ChatOllama inicializado: model={settings.LLM_MODEL_NAME}, base_url={settings.OLLAMA_BASE_URL}")
    except Exception as e:
        logger.critical(f"Fallo al inicializar ChatOllama: {e}", exc_info=True)
        llm = None


# --- Definición de Estructura para Brand Kit ---
class BrandKitPydantic(LangchainPydanticBaseModel):
    brand_name: str = LangchainField(description="Nombre de la marca o empresa, si es evidente")
    slogan: str = LangchainField(description="Slogan principal de la marca, si se detecta")
    primary_colors: List[Dict[str, str]] = LangchainField(description="Lista de colores primarios, ej. [{'name': 'Azul Corporativo', 'hex': '#005A9C'}]")
    secondary_colors: List[Dict[str, str]] = LangchainField(description="Lista de colores secundarios/acento")
    main_typography: Dict[str, str] = LangchainField(description="Tipografía principal, ej. {'name': 'Montserrat', 'style': 'Sans-serif moderna y versátil'}")
    secondary_typography: Dict[str, str] = LangchainField(description="Tipografía secundaria")
    tone_of_voice: str = LangchainField(description="Tono de voz general descrito en 2-3 adjetivos")
    target_audience_keywords: List[str] = LangchainField(description="Palabras clave del público objetivo principal")
    logo_description: str = LangchainField(description="Descripción del logo si es visible o se describe")
    mission_vision_summary: str = LangchainField(description="Misión o visión resumida si se infiere")

# --- Output Parsers ---
str_output_parser = StrOutputParser()
json_output_parser = JsonOutputParser()
pydantic_brand_kit_parser = JsonOutputParser(pydantic_object=BrandKitPydantic)

# --- Cadenas LCEL ---

# 1. Cadena para Generar Anuncios
ads_prompt_template_text = """
System: {system_prompt}
User: Basado en el siguiente contenido de un sitio web, genera EXACTAMENTE 3 copys de anuncios concisos, atractivos y optimizados para redes sociales (Facebook, Instagram).
Cada copy debe ser independiente y estar en una nueva línea. NO uses numeración, viñetas, ni introducciones como "Aquí tienes los anuncios:".
Enfócate en un lenguaje persuasivo y directo.

Contenido del sitio web:
---
{website_content}
---
Anuncios Generados:
"""
ads_prompt = ChatPromptTemplate.from_template(ads_prompt_template_text)

def parse_newline_separated_list(text: str) -> List[str]:
    return [line.strip() for line in text.split('\n') if line.strip()]

if llm:
    ads_chain = (
        ads_prompt | llm | str_output_parser | parse_newline_separated_list
    ).with_retry( # Añadir reintentos a la cadena
        stop_after_attempt=settings.LLM_MAX_RETRIES,
        wait_exponential_jitter=True, # Jitter para evitar thundering herd
        # Puedes especificar qué excepciones reintentar, ej. httpx.ReadTimeout
    )
else:
    ads_chain = None

async def generate_ads_lcel(website_content: str) -> List[str]:
    if not ads_chain:
        logger.error("Ads chain no inicializada (LLM no configurado).")
        return []
    try:
        logger.info(f"Invocando ads_chain para contenido de {len(website_content)} chars.")
        result = await ads_chain.ainvoke({
            "system_prompt": "Eres un copywriter experto en anuncios de alto impacto para redes sociales.",
            "website_content": website_content
        })
        logger.info(f"ads_chain completado. {len(result)} anuncios generados.")
        return result
    except Exception as e:
        logger.error(f"Error en ads_chain: {e}", exc_info=True)
        return []

# 2. Cadena para Generar Brand Kit (JSON con Pydantic Parser)
brand_kit_json_prompt_template_text = """
System: {system_prompt}
User: Analiza el siguiente contenido de un sitio web y extrae un brand kit.
Debes formatear tu respuesta EXCLUSIVAMENTE como un objeto JSON válido que se ajuste al siguiente esquema Pydantic:
```json
{json_schema}