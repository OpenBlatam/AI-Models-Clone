# app/scraper.py
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from cachetools import cached, TTLCache
import logging
from functools import lru_cache
from config import settings # Importar la configuración
import httpx
import asyncio
from aiocache import cached, SimpleMemoryCache

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear un caché TTL (Time To Live)
# El caché se limpiará después de SCRAPER_CACHE_TTL_SECONDS
scraper_cache = TTLCache(maxsize=settings.SCRAPER_CACHE_SIZE, ttl=settings.SCRAPER_CACHE_TTL_SECONDS)

# Simple in-memory cache for scraping
SCRAPER_CACHE = {}
SCRAPER_CACHE_SIZE = 100

@cached(cache=scraper_cache) # Aplicar el caché a la función
@retry(
    stop=stop_after_attempt(3), # Reintentar hasta 3 veces
    wait=wait_exponential(multiplier=1, min=2, max=10), # Espera exponencial: 2s, 4s, 8s...
    reraise=True # Volver a lanzar la excepción original si todos los reintentos fallan
)
def get_website_text_with_retry_and_cache(url_str: str) -> str | None:
    """
    Fetches and extracts clean text content from a given URL, with retries and caching.
    """
    logger.info(f"Scraping URL: {url_str}")
    try:
        headers = {'User-Agent': settings.USER_AGENT_SCRAPER}
        response = requests.get(url_str, headers=headers, timeout=settings.SCRAPER_TIMEOUT_SECONDS)
        response.raise_for_status() # Lanza HTTPError para respuestas 4xx/5xx

        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' not in content_type:
            logger.warning(f"Contenido de {url_str} no es HTML (type: {content_type}). Intentando leer como texto.")
            return response.text[:settings.SCRAPER_MAX_CHARS] if response.text else None

        soup = BeautifulSoup(response.content, 'html.parser')

        for element_type in ["script", "style", "nav", "footer", "aside", "form", "header", "iframe", "noscript", "link", "meta"]:
            for element in soup.find_all(element_type):
                element.decompose()
        
        main_content_tags = ['article', 'main', '.main-content', '.post-content', '#content', '#main', '.entry-content']
        main_text = ""
        for tag_selector in main_content_tags:
            main_element = soup.select_one(tag_selector)
            if main_element:
                main_text = main_element.get_text(separator=' ', strip=True)
                break
        
        if not main_text:
            main_text = soup.get_text(separator=' ', strip=True)

        cleaned_text = ' '.join(main_text.split())
        logger.info(f"Contenido extraído de {url_str} (longitud: {len(cleaned_text)} chars).")
        return cleaned_text[:settings.SCRAPER_MAX_CHARS]

    except requests.exceptions.Timeout as e:
        logger.warning(f"Timeout scrapeando {url_str}: {e}")
        raise # Re-lanzar para que tenacity lo maneje
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error de request scrapeando {url_str}: {e}")
        raise # Re-lanzar para que tenacity lo maneje
    except Exception as e: # Captura otros errores inesperados
        logger.error(f"Error inesperado procesando HTML de {url_str}: {e}", exc_info=True)
        # No re-lanzamos errores no relacionados con requests para evitar reintentos innecesarios
        return None # O manejar de otra forma


def get_website_text(url_str: str) -> str | None:
    # Check cache first
    if url_str in SCRAPER_CACHE:
        return SCRAPER_CACHE[url_str]
    # ... existing scraping logic ...
    # After extracting text:
    text = ... # your scraping logic here
    # Limit to first 1500 chars
    text = text[:1500]
    # Store in cache
    if len(SCRAPER_CACHE) >= SCRAPER_CACHE_SIZE:
        SCRAPER_CACHE.pop(next(iter(SCRAPER_CACHE)))
    SCRAPER_CACHE[url_str] = text
    return text

    try:
        return get_website_text_with_retry_and_cache(url_str)
    except RetryError as e:
        logger.error(f"Fallaron todos los reintentos para scrape_url {url_str}: {e.last_attempt.exception()}")
        return None

# --- Scraping asíncrono y cacheado ---
@cached(ttl=settings.SCRAPER_CACHE_TTL_SECONDS, cache=SimpleMemoryCache)
async def get_website_text_async(url_str: str, timeout: int = None) -> str | None:
    """
    Versión asíncrona de scraping de texto web usando httpx y BeautifulSoup.
    Usa cache TTL en memoria. Timeout configurable.
    """
    logger.info(f"[async] Scraping URL: {url_str}")
    timeout = timeout or settings.SCRAPER_TIMEOUT_SECONDS
    try:
        async with httpx.AsyncClient(timeout=timeout, headers={'User-Agent': settings.USER_AGENT_SCRAPER}) as client:
            resp = await client.get(url_str)
            resp.raise_for_status()
            content_type = resp.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"Contenido de {url_str} no es HTML (type: {content_type}). Intentando leer como texto.")
                return resp.text[:settings.SCRAPER_MAX_CHARS] if resp.text else None
            soup = BeautifulSoup(resp.content, 'html.parser')
            for element_type in ["script", "style", "nav", "footer", "aside", "form", "header", "iframe", "noscript", "link", "meta"]:
                for element in soup.find_all(element_type):
                    element.decompose()
            main_content_tags = ['article', 'main', '.main-content', '.post-content', '#content', '#main', '.entry-content']
            main_text = ""
            for tag_selector in main_content_tags:
                main_element = soup.select_one(tag_selector)
                if main_element:
                    main_text = main_element.get_text(separator=' ', strip=True)
                    break
            if not main_text:
                main_text = soup.get_text(separator=' ', strip=True)
            cleaned_text = ' '.join(main_text.split())
            logger.info(f"[async] Contenido extraído de {url_str} (longitud: {len(cleaned_text)} chars).")
            return cleaned_text[:settings.SCRAPER_MAX_CHARS]
    except httpx.TimeoutException as e:
        logger.warning(f"[async] Timeout scrapeando {url_str}: {e}")
        return None
    except httpx.RequestError as e:
        logger.warning(f"[async] Error de request scrapeando {url_str}: {e}")
        return None
    except Exception as e:
        logger.error(f"[async] Error inesperado procesando HTML de {url_str}: {e}", exc_info=True)
        return None