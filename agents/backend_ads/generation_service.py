import logging
from typing import List, Callable, Any, Optional, Dict
from llm_interface import (
    generate_ads_lcel,
    generate_brand_kit_lcel,
    generate_custom_content_lcel
)
import uuid
import asyncio
from aiocache import cached

logger = logging.getLogger(__name__)

# --- Mensajes de error internacionalizados ---
ERRORS_I18N = {
    "es": {
        "short_text": "Texto demasiado corto.",
        "long_text": "Texto demasiado largo.",
        "short_prompt": "Prompt demasiado corto.",
        "long_prompt": "Prompt demasiado largo.",
        "llm_error": "Error al generar contenido: respuesta vacía o error de LLM.",
        "cancelled": "La generación fue cancelada por el usuario o el sistema.",
    },
    "en": {
        "short_text": "Text too short.",
        "long_text": "Text too long.",
        "short_prompt": "Prompt too short.",
        "long_prompt": "Prompt too long.",
        "llm_error": "Error generating content: empty response or LLM error.",
        "cancelled": "Generation was cancelled by user or system.",
    }
}

def get_error_msg(key: str, lang: str = "es") -> str:
    return ERRORS_I18N.get(lang, ERRORS_I18N["es"]).get(key, key)

# --- Decorador para logging estructurado, trace_id, i18n y métricas ---
def log_with_trace(func: Callable) -> Callable:
    async def wrapper(*args, trace_id: Optional[str] = None, lang: str = "es", extra_log: Optional[Dict] = None, metrics_cb: Optional[Callable] = None, timeout: Optional[float] = None, **kwargs):
        trace_id = trace_id or str(uuid.uuid4())
        log_data = {"event": func.__name__ + "_start", "trace_id": trace_id, "lang": lang}
        if extra_log:
            log_data.update(extra_log)
        logger.info(log_data)
        try:
            coro = func(*args, trace_id=trace_id, lang=lang, **kwargs)
            if timeout:
                result = await asyncio.wait_for(coro, timeout=timeout)
            else:
                result = await coro
            logger.info({"event": func.__name__ + "_success", "trace_id": trace_id})
            if metrics_cb:
                metrics_cb(func.__name__, success=True)
            return result
        except asyncio.CancelledError:
            logger.warning({"event": func.__name__ + "_cancelled", "trace_id": trace_id})
            if metrics_cb:
                metrics_cb(func.__name__, success=False, error="cancelled")
            return {"error": get_error_msg("cancelled", lang), "details": None, "trace_id": trace_id}
        except Exception as e:
            logger.error({"event": func.__name__ + "_error", "trace_id": trace_id, "error": str(e)})
            if metrics_cb:
                metrics_cb(func.__name__, success=False, error=str(e))
            return {"error": str(e), "details": None, "trace_id": trace_id}
    return wrapper

@log_with_trace
async def generate_ads(
    text: str,
    trace_id: Optional[str] = None,
    lang: str = "es",
    llm_func: Callable[[str], Any] = generate_ads_lcel,
    **kwargs
) -> Any:
    """
    Genera una lista de anuncios a partir de texto web.
    Args:
        text (str): Texto web limpio (min 10, max 2000 chars).
        trace_id (str, opcional): ID de trazabilidad para logging.
        lang (str): Idioma para mensajes de error ("es" o "en").
        llm_func: función de generación (mockeable en tests).
        timeout: timeout opcional para la generación.
        metrics_cb: callback opcional para métricas.
    Returns:
        List[str] o dict de error.
    Ejemplo de uso:
        ads = await generate_ads("Texto web...", trace_id="abc-123", lang="en")
    Ejemplo de error:
        {"error": "Text too short.", "details": None, "trace_id": "abc-123"}
    """
    if not isinstance(text, str) or len(text) < 10:
        raise ValueError(get_error_msg("short_text", lang))
    if len(text) > 2000:
        raise ValueError(get_error_msg("long_text", lang))
    ads_list = await llm_func(text)
    if not ads_list:
        raise ValueError(get_error_msg("llm_error", lang))
    return ads_list

@log_with_trace
async def generate_brand_kit(
    text: str,
    trace_id: Optional[str] = None,
    lang: str = "es",
    llm_func: Callable[[str], Any] = generate_brand_kit_lcel,
    **kwargs
) -> Any:
    """
    Genera un brand kit a partir de texto web.
    Args:
        text (str): Texto web limpio (min 10, max 2000 chars).
        trace_id (str, opcional): ID de trazabilidad para logging.
        lang (str): Idioma para mensajes de error ("es" o "en").
        llm_func: función de generación (mockeable en tests).
        timeout: timeout opcional para la generación.
        metrics_cb: callback opcional para métricas.
    Returns:
        str o dict de error.
    """
    if not isinstance(text, str) or len(text) < 10:
        raise ValueError(get_error_msg("short_text", lang))
    if len(text) > 2000:
        raise ValueError(get_error_msg("long_text", lang))
    brand_kit = await llm_func(text)
    if not brand_kit:
        raise ValueError(get_error_msg("llm_error", lang))
    return brand_kit

# --- Cache de generación para máxima velocidad ---
def _custom_content_cache_key(func, prompt, text, lang, **kwargs):
    return f"custom_content|{prompt}|{text}|{lang}"

@cached(ttl=120, key_builder=_custom_content_cache_key)
@log_with_trace
async def generate_custom_content(
    prompt: str,
    text: str,
    trace_id: Optional[str] = None,
    lang: str = "es",
    llm_func: Callable[[str, str], Any] = generate_custom_content_lcel,
    **kwargs
) -> Any:
    """
    Genera contenido personalizado a partir de un prompt y texto web.
    Args:
        prompt (str): Prompt de usuario (min 5, max 500 chars).
        text (str): Texto web limpio (min 10, max 2000 chars).
        trace_id (str, opcional): ID de trazabilidad para logging.
        lang (str): Idioma para mensajes de error ("es" o "en").
        llm_func: función de generación (mockeable en tests).
        timeout: timeout opcional para la generación.
        metrics_cb: callback opcional para métricas.
    Returns:
        List[str] o dict de error.
    """
    if not isinstance(prompt, str) or len(prompt) < 5:
        raise ValueError(get_error_msg("short_prompt", lang))
    if len(prompt) > 500:
        raise ValueError(get_error_msg("long_prompt", lang))
    if not isinstance(text, str) or len(text) < 10:
        raise ValueError(get_error_msg("short_text", lang))
    if len(text) > 2000:
        raise ValueError(get_error_msg("long_text", lang))
    content = await llm_func(prompt, text)
    if not content:
        raise ValueError(get_error_msg("llm_error", lang))
    return content

# --- Ejemplo de paralelismo para batch ---
async def batch_generate_custom_content(prompts_texts: List[Dict[str, str]], lang: str = "es", **kwargs) -> List[Any]:
    """
    Genera múltiples contenidos personalizados en paralelo.
    prompts_texts: lista de dicts {"prompt": ..., "text": ...}
    """
    tasks = [generate_custom_content(d["prompt"], d["text"], lang=lang, **kwargs) for d in prompts_texts]
    return await asyncio.gather(*tasks) 