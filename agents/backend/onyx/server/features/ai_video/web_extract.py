import typing as t
import logging

def extract_web_content(url: str, debug: bool = False) -> t.Dict[str, t.Any]:
    """
    Extrae el contenido principal de una web: título, descripción, texto, imágenes, favicon, OpenGraph, keywords.
    Usa trafilatura si está disponible, si no fallback a requests+BeautifulSoup.
    Args:
        url: URL de la web a extraer.
        debug: Si True, imprime logs de debug.
    Returns:
        dict con claves: title, description, text, images, favicon, og_image, keywords, raw
    """
    logger = logging.getLogger("web_extract")
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    # 1. Trafiltura
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            result = trafilatura.extract(downloaded, output_format="json", with_metadata=True)
            if result:
                import json
                data = json.loads(result)
                if debug:
                    logger.debug(f"[trafilatura] Extracted: {data}")
                return {
                    "title": data.get("title"),
                    "description": data.get("description"),
                    "text": data.get("text"),
                    "images": data.get("image"),
                    "favicon": None,  # Trafiltura no extrae favicon
                    "og_image": None, # Trafiltura no extrae OpenGraph
                    "keywords": data.get("keywords"),
                    "raw": data
                }
    except ImportError:
        if debug:
            logger.debug("[trafilatura] Not installed, fallback to BeautifulSoup.")
    except Exception as e:
        if debug:
            logger.debug(f"[trafilatura] Error: {e}")
    # 2. Fallback: requests + BeautifulSoup
    try:
        import requests
        from bs4 import BeautifulSoup
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        # Description
        description = ""
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag and desc_tag.get("content"):
            description = desc_tag["content"].strip()
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            description = og_desc["content"].strip()
        # Text
        text = " ".join([p.get_text(separator=" ", strip=True) for p in soup.find_all("p")])
        # Images
        images = [img["src"] for img in soup.find_all("img") if img.get("src")]
        # OpenGraph image
        og_image = None
        og_img_tag = soup.find("meta", property="og:image")
        if og_img_tag and og_img_tag.get("content"):
            og_image = og_img_tag["content"]
            if og_image not in images:
                images.insert(0, og_image)
        # Favicon
        favicon = None
        icon_tag = soup.find("link", rel=lambda x: x and "icon" in x)
        if icon_tag and icon_tag.get("href"):
            favicon = icon_tag["href"]
        # Keywords
        keywords = None
        kw_tag = soup.find("meta", attrs={"name": "keywords"})
        if kw_tag and kw_tag.get("content"):
            keywords = [k.strip() for k in kw_tag["content"].split(",") if k.strip()]
        result = {
            "title": title,
            "description": description,
            "text": text,
            "images": images,
            "favicon": favicon,
            "og_image": og_image,
            "keywords": keywords,
            "raw": None
        }
        if debug:
            logger.debug(f"[BeautifulSoup] Extracted: {result}")
        return result
    except Exception as e:
        if debug:
            logger.debug(f"[BeautifulSoup] Error: {e}")
        return {"title": None, "description": None, "text": None, "images": [], "favicon": None, "og_image": None, "keywords": None, "raw": None} 