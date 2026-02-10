"""
Collection Utils - Utilidades de Colecciones
============================================

Utilidades para manipulación de colecciones (listas, diccionarios, sets).
"""

import logging
from typing import List, Dict, Any, Optional, Callable, Set, Tuple
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Dividir lista en chunks.
    
    Args:
        items: Lista a dividir
        chunk_size: Tamaño de cada chunk
        
    Returns:
        Lista de chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def flatten_list(nested_list: List[Any]) -> List[Any]:
    """
    Aplanar lista anidada.
    
    Args:
        nested_list: Lista anidada
        
    Returns:
        Lista aplanada
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def unique_list(items: List[Any], key: Optional[Callable[[Any], Any]] = None) -> List[Any]:
    """
    Obtener lista única preservando orden.
    
    Args:
        items: Lista de items
        key: Función para obtener key de comparación (opcional)
        
    Returns:
        Lista única
    """
    if key is None:
        seen = set()
        return [x for x in items if not (x in seen or seen.add(x))]
    else:
        seen = set()
        result = []
        for item in items:
            k = key(item)
            if k not in seen:
                seen.add(k)
                result.append(item)
        return result


def group_by_key(items: List[Dict[str, Any]], key: str) -> Dict[Any, List[Dict[str, Any]]]:
    """
    Agrupar items por clave.
    
    Args:
        items: Lista de diccionarios
        key: Clave para agrupar
        
    Returns:
        Diccionario agrupado
    """
    grouped = defaultdict(list)
    for item in items:
        grouped[item.get(key)].append(item)
    return dict(grouped)


def group_by_function(items: List[Any], key_func: Callable[[Any], Any]) -> Dict[Any, List[Any]]:
    """
    Agrupar items por función.
    
    Args:
        items: Lista de items
        key_func: Función para obtener key
        
    Returns:
        Diccionario agrupado
    """
    grouped = defaultdict(list)
    for item in items:
        grouped[key_func(item)].append(item)
    return dict(grouped)


def sort_by_key(items: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """
    Ordenar items por clave.
    
    Args:
        items: Lista de diccionarios
        key: Clave para ordenar
        reverse: Si ordenar en reversa
        
    Returns:
        Lista ordenada
    """
    return sorted(items, key=lambda x: x.get(key, ""), reverse=reverse)


def sort_by_function(items: List[Any], key_func: Callable[[Any], Any], reverse: bool = False) -> List[Any]:
    """
    Ordenar items por función.
    
    Args:
        items: Lista de items
        key_func: Función para obtener key
        reverse: Si ordenar en reversa
        
    Returns:
        Lista ordenada
    """
    return sorted(items, key=key_func, reverse=reverse)


def filter_dict(dictionary: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Filtrar diccionario por keys.
    
    Args:
        dictionary: Diccionario a filtrar
        keys: Lista de keys a mantener
        
    Returns:
        Diccionario filtrado
    """
    return {k: v for k, v in dictionary.items() if k in keys}


def exclude_keys(dictionary: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Excluir keys de diccionario.
    
    Args:
        dictionary: Diccionario
        keys: Lista de keys a excluir
        
    Returns:
        Diccionario sin keys excluidas
    """
    return {k: v for k, v in dictionary.items() if k not in keys}


def invert_dict(dictionary: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Invertir diccionario (keys -> values, values -> keys).
    
    Args:
        dictionary: Diccionario a invertir
        
    Returns:
        Diccionario invertido
    """
    return {v: k for k, v in dictionary.items()}


def merge_dicts(*dicts: Dict[str, Any], deep: bool = False) -> Dict[str, Any]:
    """
    Fusionar múltiples diccionarios.
    
    Args:
        *dicts: Diccionarios a fusionar
        deep: Si hacer merge profundo
        
    Returns:
        Diccionario fusionado
    """
    if not dicts:
        return {}
    
    result = dicts[0].copy()
    
    for d in dicts[1:]:
        if deep:
            for k, v in d.items():
                if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                    result[k] = merge_dicts(result[k], v, deep=True)
                else:
                    result[k] = v
        else:
            result.update(d)
    
    return result


def get_nested_value(dictionary: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Obtener valor anidado de diccionario usando path.
    
    Args:
        dictionary: Diccionario
        path: Path separado por puntos (ej: "user.profile.name")
        default: Valor por defecto
        
    Returns:
        Valor encontrado o default
    """
    keys = path.split(".")
    value = dictionary
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default
    
    return value


def set_nested_value(dictionary: Dict[str, Any], path: str, value: Any) -> None:
    """
    Establecer valor anidado en diccionario usando path.
    
    Args:
        dictionary: Diccionario
        path: Path separado por puntos
        value: Valor a establecer
    """
    keys = path.split(".")
    current = dictionary
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def partition_list(items: List[Any], predicate: Callable[[Any], bool]) -> Tuple[List[Any], List[Any]]:
    """
    Particionar lista en dos según predicado.
    
    Args:
        items: Lista de items
        predicate: Función predicado
        
    Returns:
        Tupla (items que cumplen, items que no cumplen)
    """
    true_items = []
    false_items = []
    
    for item in items:
        if predicate(item):
            true_items.append(item)
        else:
            false_items.append(item)
    
    return true_items, false_items


def zip_dicts(*dicts: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Hacer zip de diccionarios (combinar por keys).
    
    Args:
        *dicts: Diccionarios a combinar
        
    Returns:
        Lista de diccionarios combinados
    """
    all_keys = set()
    for d in dicts:
        all_keys.update(d.keys())
    
    result = []
    for key in all_keys:
        combined = {}
        for i, d in enumerate(dicts):
            if key in d:
                combined[f"dict_{i}_{key}"] = d[key]
        result.append(combined)
    
    return result


def count_by_key(items: List[Dict[str, Any]], key: str) -> Dict[Any, int]:
    """
    Contar items por clave.
    
    Args:
        items: Lista de diccionarios
        key: Clave para contar
        
    Returns:
        Diccionario con conteos
    """
    counter = Counter(item.get(key) for item in items)
    return dict(counter)


def find_duplicates(items: List[Any]) -> List[Any]:
    """
    Encontrar duplicados en lista.
    
    Args:
        items: Lista de items
        
    Returns:
        Lista de items duplicados
    """
    seen = set()
    duplicates = []
    
    for item in items:
        if item in seen:
            if item not in duplicates:
                duplicates.append(item)
        else:
            seen.add(item)
    
    return duplicates


def remove_duplicates(items: List[Any], preserve_order: bool = True) -> List[Any]:
    """
    Remover duplicados de lista.
    
    Args:
        items: Lista de items
        preserve_order: Si preservar orden
        
    Returns:
        Lista sin duplicados
    """
    if preserve_order:
        return unique_list(items)
    else:
        return list(set(items))


def batch_process(items: List[Any], batch_size: int, processor: Callable[[List[Any]], Any]) -> List[Any]:
    """
    Procesar items en batches.
    
    Args:
        items: Lista de items
        batch_size: Tamaño de batch
        processor: Función procesadora
        
    Returns:
        Lista de resultados
    """
    results = []
    chunks = chunk_list(items, batch_size)
    
    for chunk in chunks:
        result = processor(chunk)
        if isinstance(result, list):
            results.extend(result)
        else:
            results.append(result)
    
    return results




