"""
Utilidades generales para la comunidad Lovable (optimizado)

Incluye funciones auxiliares para validación, formateo, sanitización, y más.

Este módulo proporciona funciones de utilidad reutilizables para:
- Sanitización de strings y datos
- Validación de formatos (UUID, emails, etc.)
- Normalización de datos
- Formateo de fechas y textos
- Cálculo de paginación
- Extracción de términos de búsqueda
- Construcción de filtros
"""

import re
import hashlib
from typing import List, Optional, Dict, Any, Tuple, Callable
from datetime import datetime, timedelta


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitiza un string eliminando espacios y limitando longitud.
    
    Args:
        value: String a sanitizar
        max_length: Longitud máxima (opcional)
        
    Returns:
        String sanitizado
    """
    if not value:
        return ""
    
    # Strip whitespace
    sanitized = value.strip()
    
    # Limitar longitud si se especifica
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_uuid_format(value: str) -> bool:
    """
    Valida que un string tenga formato UUID.
    
    Args:
        value: String a validar
        
    Returns:
        True si es un UUID válido
    """
    if not value:
        return False
    
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(value.strip()))


def normalize_tags(tags: Optional[List[str]]) -> Optional[List[str]]:
    """
    Normaliza una lista de tags (lowercase, strip, deduplicar).
    
    Args:
        tags: Lista de tags
        
    Returns:
        Lista normalizada o None
    """
    if not tags:
        return None
    
    normalized = []
    seen = set()
    
    for tag in tags:
        if tag:
            tag_clean = tag.strip().lower()
            if tag_clean and tag_clean not in seen:
                normalized.append(tag_clean)
                seen.add(tag_clean)
    
    return normalized if normalized else None


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Formatea un datetime a string.
    
    Args:
        dt: Datetime a formatear
        format_str: Formato (default: ISO-like)
        
    Returns:
        String formateado
    """
    if not dt:
        return ""
    return dt.strftime(format_str)


def calculate_pagination_info(
    page: int,
    page_size: int,
    total: int
) -> Dict[str, Any]:
    """
    Calcula información de paginación.
    
    Args:
        page: Página actual
        page_size: Tamaño de página
        total: Total de elementos
        
    Returns:
        Diccionario con información de paginación
    """
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "has_more": has_next
    }


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Trunca un texto a una longitud máxima.
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca
        
    Returns:
        Texto truncado
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_search_terms(query: str) -> List[str]:
    """
    Extrae términos de búsqueda de una query.
    
    Args:
        query: Query de búsqueda
        
    Returns:
        Lista de términos
    """
    if not query:
        return []
    
    # Dividir por espacios y limpiar
    terms = [term.strip().lower() for term in query.split() if term.strip()]
    
    return terms


def build_search_filter(search_terms: List[str], fields: List[str]) -> str:
    """
    Construye un filtro de búsqueda para SQL LIKE.
    
    Args:
        search_terms: Términos de búsqueda
        fields: Campos a buscar
        
    Returns:
        Patrón de búsqueda
    """
    if not search_terms:
        return ""
    
    # Combinar términos con OR
    patterns = []
    for term in search_terms:
        pattern = f"%{term}%"
        patterns.append(pattern)
    
    return " OR ".join(patterns)


def validate_page_params(page: int, page_size: int, max_page: int = 1000, max_page_size: int = 100) -> tuple[int, int]:
    """
    Valida y normaliza parámetros de paginación.
    
    Args:
        page: Página solicitada
        page_size: Tamaño de página solicitado
        max_page: Página máxima permitida
        max_page_size: Tamaño de página máximo permitido
        
    Returns:
        Tupla (page, page_size) validados
    """
    # Validar página
    if page < 1:
        page = 1
    elif page > max_page:
        page = max_page
    
    # Validar tamaño de página
    if page_size < 1:
        page_size = 20
    elif page_size > max_page_size:
        page_size = max_page_size
    
    return page, page_size


def generate_hash(value: str, algorithm: str = "sha256") -> str:
    """
    Genera un hash de un string (optimizado).
    
    Args:
        value: String a hashear
        algorithm: Algoritmo a usar (md5, sha1, sha256, sha512)
        
    Returns:
        Hash hexadecimal del string
    """
    if not value:
        return ""
    
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(value.encode('utf-8'))
    return hash_obj.hexdigest()


def is_valid_email(email: str) -> bool:
    """
    Valida si un string es un email válido (optimizado).
    
    Args:
        email: String a validar
        
    Returns:
        True si es un email válido
    """
    if not email:
        return False
    
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    return bool(email_pattern.match(email.strip()))


def slugify(text: str) -> str:
    """
    Convierte un texto a slug (optimizado).
    
    Args:
        text: Texto a convertir
        
    Returns:
        Slug del texto
    """
    if not text:
        return ""
    
    # Convertir a lowercase
    slug = text.lower().strip()
    
    # Reemplazar espacios y caracteres especiales con guiones
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remover guiones al inicio y final
    slug = slug.strip('-')
    
    return slug


def parse_date_range(date_from: Optional[str], date_to: Optional[str]) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Parsea un rango de fechas desde strings (optimizado).
    
    Args:
        date_from: Fecha de inicio (formato: YYYY-MM-DD)
        date_to: Fecha de fin (formato: YYYY-MM-DD)
        
    Returns:
        Tupla (datetime_from, datetime_to) o (None, None)
    """
    dt_from = None
    dt_to = None
    
    if date_from:
        try:
            dt_from = datetime.strptime(date_from, "%Y-%m-%d")
        except ValueError:
            pass
    
    if date_to:
        try:
            dt_to = datetime.strptime(date_to, "%Y-%m-%d")
            # Agregar tiempo al final del día
            dt_to = dt_to.replace(hour=23, minute=59, second=59)
        except ValueError:
            pass
    
    return dt_from, dt_to


def calculate_time_ago(dt: datetime) -> str:
    """
    Calcula tiempo transcurrido desde una fecha (optimizado).
    
    Args:
        dt: Fecha de referencia
        
    Returns:
        String con tiempo transcurrido (ej: "2 hours ago")
    """
    if not dt:
        return ""
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Divide una lista en chunks de tamaño fijo (optimizado).
    
    Args:
        items: Lista a dividir
        chunk_size: Tamaño de cada chunk
        
    Returns:
        Lista de chunks
    """
    if not items or chunk_size <= 0:
        return []
    
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def remove_duplicates(items: List[Any], key: Optional[Callable[[Any], Any]] = None) -> List[Any]:
    """
    Remueve duplicados de una lista manteniendo orden (optimizado).
    
    Args:
        items: Lista con posibles duplicados
        key: Función para extraer clave de comparación (opcional)
        
    Returns:
        Lista sin duplicados
    """
    if not items:
        return []
    
    if key:
        seen = set()
        result = []
        for item in items:
            item_key = key(item)
            if item_key not in seen:
                seen.add(item_key)
                result.append(item)
        return result
    else:
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result


def safe_int(value: Any, default: int = 0) -> int:
    """
    Convierte un valor a int de forma segura (optimizado).
    
    Args:
        value: Valor a convertir
        default: Valor por defecto si falla
        
    Returns:
        Entero o valor por defecto
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Convierte un valor a float de forma segura (optimizado).
    
    Args:
        value: Valor a convertir
        default: Valor por defecto si falla
        
    Returns:
        Float o valor por defecto
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def format_bytes(bytes_size: int) -> str:
    """
    Formatea un tamaño en bytes a formato legible (optimizado).
    
    Args:
        bytes_size: Tamaño en bytes
        
    Returns:
        String formateado (ej: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def get_percentage(value: int, total: int, decimals: int = 2) -> float:
    """
    Calcula el porcentaje de un valor sobre un total (optimizado).
    
    Args:
        value: Valor
        total: Total
        decimals: Número de decimales
        
    Returns:
        Porcentaje redondeado
    """
    if total == 0:
        return 0.0
    
    percentage = (value / total) * 100
    return round(percentage, decimals)


def mask_email(email: str) -> str:
    """
    Enmascara un email para privacidad (optimizado).
    
    Args:
        email: Email a enmascarar
        
    Returns:
        Email enmascarado (ej: "u***@example.com")
    """
    if not email or '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    
    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def validate_url(url: str) -> bool:
    """
    Valida si un string es una URL válida (optimizado).
    
    Args:
        url: String a validar
        
    Returns:
        True si es una URL válida
    """
    if not url:
        return False
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(url_pattern.match(url.strip()))

