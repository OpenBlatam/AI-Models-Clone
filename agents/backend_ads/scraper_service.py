import httpx
from bs4 import BeautifulSoup
from aiocache import cached, SimpleMemoryCache
from config import settings
import logging

logger = logging.getLogger(__name__)

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