import asyncio
from typing import List, Dict, Any, Callable

async def batch_scrape_urls(
    urls: List[str],
    max_concurrency: int,
    timeout: int,
    max_text_chars: int,
    trace_id: str,
    scrape_func: Callable[[str, int], Any],
) -> Dict[str, Any]:
    sem = asyncio.Semaphore(max_concurrency)
    async def scrape_one(url):
        async with sem:
            try:
                text = await asyncio.wait_for(scrape_func(url, timeout=timeout), timeout=timeout+1)
                if text is None:
                    return url, {"error": "No se pudo extraer texto", "details": None}
                return url, text[:max_text_chars]
            except asyncio.TimeoutError:
                return url, {"error": "Timeout", "details": f"Timeout de {timeout}s"}
            except Exception as e:
                return url, {"error": str(type(e).__name__), "details": str(e)}
    results = await asyncio.gather(*(scrape_one(url) for url in urls))
    return dict(results) 