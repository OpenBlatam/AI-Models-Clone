"""
Data Transform - Transformación de Datos
=========================================

Utilidades para transformar y normalizar datos.
"""

import logging
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import re

logger = logging.getLogger(__name__)


def normalize_string(value: str, lower: bool = True, strip: bool = True) -> str:
    """
    Normalizar string.
    
    Args:
        value: String a normalizar
        lower: Convertir a minúsculas
        strip: Remover espacios
        
    Returns:
        String normalizado
    """
    if not isinstance(value, str):
        value = str(value)
    
    if lower:
        value = value.lower()
    
    if strip:
        value = value.strip()
    
    return value


def normalize_number(value: Any, default: float = 0.0) -> float:
    """
    Normalizar número.
    
    Args:
        value: Valor a normalizar
        default: Valor por defecto si falla
        
    Returns:
        Número normalizado
    """
    try:
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            # Remover caracteres no numéricos excepto punto y signo
            cleaned = re.sub(r'[^\d\.\-\+]', '', value)
            return float(cleaned) if cleaned else default
        else:
            return default
    except (ValueError, TypeError):
        return default


def normalize_boolean(value: Any, default: bool = False) -> bool:
    """
    Normalizar booleano.
    
    Args:
        value: Valor a normalizar
        default: Valor por defecto
        
    Returns:
        Booleano normalizado
    """
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
    elif isinstance(value, (int, float)):
        return bool(value)
    else:
        return default


def transform_dict(
    data: Dict[str, Any],
    mappings: Dict[str, Callable[[Any], Any]],
    default_transform: Optional[Callable[[Any], Any]] = None
) -> Dict[str, Any]:
    """
    Transformar diccionario con mapeos.
    
    Args:
        data: Diccionario a transformar
        mappings: Diccionario de mapeos {key: transform_function}
        default_transform: Transformación por defecto para keys no mapeadas
        
    Returns:
        Diccionario transformado
    """
    result = {}
    
    for key, value in data.items():
        if key in mappings:
            try:
                result[key] = mappings[key](value)
            except Exception as e:
                logger.warning(f"Error transforming {key}: {e}")
                result[key] = value
        elif default_transform:
            try:
                result[key] = default_transform(value)
            except Exception:
                result[key] = value
        else:
            result[key] = value
    
    return result


def flatten_dict(
    data: Dict[str, Any],
    separator: str = ".",
    prefix: str = ""
) -> Dict[str, Any]:
    """
    Aplanar diccionario anidado.
    
    Args:
        data: Diccionario a aplanar
        separator: Separador para keys anidadas
        prefix: Prefijo para keys
        
    Returns:
        Diccionario aplanado
    """
    result = {}
    
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        
        if isinstance(value, dict):
            result.update(flatten_dict(value, separator, new_key))
        else:
            result[new_key] = value
    
    return result


def unflatten_dict(
    data: Dict[str, Any],
    separator: str = "."
) -> Dict[str, Any]:
    """
    Desaplanar diccionario.
    
    Args:
        data: Diccionario aplanado
        separator: Separador usado en keys
        
    Returns:
        Diccionario anidado
    """
    result = {}
    
    for key, value in data.items():
        parts = key.split(separator)
        current = result
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
    
    return result


def filter_dict(
    data: Dict[str, Any],
    include_keys: Optional[List[str]] = None,
    exclude_keys: Optional[List[str]] = None,
    predicate: Optional[Callable[[str, Any], bool]] = None
) -> Dict[str, Any]:
    """
    Filtrar diccionario.
    
    Args:
        data: Diccionario a filtrar
        include_keys: Keys a incluir
        exclude_keys: Keys a excluir
        predicate: Función de predicado (key, value) -> bool
        
    Returns:
        Diccionario filtrado
    """
    result = {}
    
    for key, value in data.items():
        # Filtrar por include
        if include_keys and key not in include_keys:
            continue
        
        # Filtrar por exclude
        if exclude_keys and key in exclude_keys:
            continue
        
        # Filtrar por predicado
        if predicate and not predicate(key, value):
            continue
        
        result[key] = value
    
    return result


def merge_dicts(
    *dicts: Dict[str, Any],
    deep: bool = False
) -> Dict[str, Any]:
    """
    Fusionar múltiples diccionarios.
    
    Args:
        *dicts: Diccionarios a fusionar
        deep: Si hacer merge profundo (recursivo)
        
    Returns:
        Diccionario fusionado
    """
    result = {}
    
    for d in dicts:
        if deep:
            result = _deep_merge(result, d)
        else:
            result.update(d)
    
    return result


def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """Merge profundo de diccionarios"""
    result = base.copy()
    
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def sanitize_for_json(data: Any) -> Any:
    """
    Sanitizar datos para JSON.
    
    Convierte tipos no serializables a tipos JSON-compatibles.
    
    Args:
        data: Datos a sanitizar
        
    Returns:
        Datos sanitizados
    """
    if isinstance(data, dict):
        return {k: sanitize_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_for_json(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, (set, frozenset)):
        return list(data)
    elif hasattr(data, '__dict__'):
        return sanitize_for_json(data.__dict__)
    else:
        return data




