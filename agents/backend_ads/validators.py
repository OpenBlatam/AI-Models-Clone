import re
from typing import List

def validate_urls_http(urls: List[str]) -> List[str]:
    """
    Valida y sanitiza una lista de URLs. Solo permite http/https, sin espacios ni esquemas peligrosos.
    Lanza ValueError si alguna URL es inválida.
    """
    url_pattern = re.compile(r'^https?://')
    for url in urls:
        if not isinstance(url, str) or not url_pattern.match(url) or ' ' in url:
            raise ValueError(f"URL inválida o no soportada: {url}")
    return urls 