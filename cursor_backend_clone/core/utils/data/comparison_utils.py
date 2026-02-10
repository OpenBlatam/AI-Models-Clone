"""
Comparison Utils - Utilidades de Comparación
============================================

Utilidades para comparar y hacer diff de datos.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from difflib import unified_diff, SequenceMatcher
from statistics import mean

logger = logging.getLogger(__name__)


@dataclass
class DiffResult:
    """Resultado de diff"""
    added: List[Any] = field(default_factory=list)
    removed: List[Any] = field(default_factory=list)
    modified: List[Dict[str, Any]] = field(default_factory=list)
    unchanged: List[Any] = field(default_factory=list)
    similarity: float = 0.0


def compare_dicts(
    dict1: Dict[str, Any],
    dict2: Dict[str, Any],
    ignore_keys: Optional[List[str]] = None
) -> DiffResult:
    """
    Comparar dos diccionarios.
    
    Args:
        dict1: Primer diccionario
        dict2: Segundo diccionario
        ignore_keys: Keys a ignorar
        
    Returns:
        DiffResult con diferencias
    """
    ignore_keys = ignore_keys or []
    result = DiffResult()
    
    all_keys = set(dict1.keys()) | set(dict2.keys())
    
    for key in all_keys:
        if key in ignore_keys:
            continue
        
        val1 = dict1.get(key)
        val2 = dict2.get(key)
        
        if key not in dict1:
            result.added.append({key: val2})
        elif key not in dict2:
            result.removed.append({key: val1})
        elif val1 != val2:
            result.modified.append({
                "key": key,
                "old": val1,
                "new": val2
            })
        else:
            result.unchanged.append(key)
    
    # Calcular similitud
    if all_keys:
        result.similarity = len(result.unchanged) / len(all_keys)
    
    return result


def compare_lists(
    list1: List[Any],
    list2: List[Any],
    key_func: Optional[Callable[[Any], Any]] = None
) -> DiffResult:
    """
    Comparar dos listas.
    
    Args:
        list1: Primera lista
        list2: Segunda lista
        key_func: Función para obtener key de items (opcional)
        
    Returns:
        DiffResult con diferencias
    """
    result = DiffResult()
    
    if key_func:
        # Comparar usando keys
        dict1 = {key_func(item): item for item in list1}
        dict2 = {key_func(item): item for item in list2}
        
        all_keys = set(dict1.keys()) | set(dict2.keys())
        
        for key in all_keys:
            if key not in dict1:
                result.added.append(dict2[key])
            elif key not in dict2:
                result.removed.append(dict1[key])
            elif dict1[key] != dict2[key]:
                result.modified.append({
                    "key": key,
                    "old": dict1[key],
                    "new": dict2[key]
                })
            else:
                result.unchanged.append(dict1[key])
    else:
        # Comparación simple
        set1 = set(list1)
        set2 = set(list2)
        
        result.added = list(set2 - set1)
        result.removed = list(set1 - set2)
        result.unchanged = list(set1 & set2)
    
    # Calcular similitud
    total = len(list1) + len(list2)
    if total > 0:
        result.similarity = (len(result.unchanged) * 2) / total
    
    return result


def compare_strings(
    str1: str,
    str2: str
) -> Dict[str, Any]:
    """
    Comparar dos strings y obtener diff.
    
    Args:
        str1: Primer string
        str2: Segundo string
        
    Returns:
        Diccionario con información de diff
    """
    similarity = SequenceMatcher(None, str1, str2).ratio()
    
    diff_lines = list(unified_diff(
        str1.splitlines(keepends=True),
        str2.splitlines(keepends=True),
        lineterm=''
    ))
    
    return {
        "similarity": similarity,
        "diff_lines": diff_lines,
        "diff_count": len(diff_lines),
        "length_diff": len(str2) - len(str1)
    }


def deep_compare(
    obj1: Any,
    obj2: Any,
    path: str = ""
) -> List[Dict[str, Any]]:
    """
    Comparación profunda de objetos.
    
    Args:
        obj1: Primer objeto
        obj2: Segundo objeto
        path: Path actual (para recursión)
        
    Returns:
        Lista de diferencias
    """
    differences = []
    
    if type(obj1) != type(obj2):
        differences.append({
            "path": path,
            "type": "type_mismatch",
            "old": type(obj1).__name__,
            "new": type(obj2).__name__
        })
        return differences
    
    if isinstance(obj1, dict):
        all_keys = set(obj1.keys()) | set(obj2.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            if key not in obj1:
                differences.append({
                    "path": new_path,
                    "type": "added",
                    "value": obj2[key]
                })
            elif key not in obj2:
                differences.append({
                    "path": new_path,
                    "type": "removed",
                    "value": obj1[key]
                })
            else:
                differences.extend(deep_compare(obj1[key], obj2[key], new_path))
    
    elif isinstance(obj1, list):
        max_len = max(len(obj1), len(obj2))
        for i in range(max_len):
            new_path = f"{path}[{i}]"
            if i >= len(obj1):
                differences.append({
                    "path": new_path,
                    "type": "added",
                    "value": obj2[i]
                })
            elif i >= len(obj2):
                differences.append({
                    "path": new_path,
                    "type": "removed",
                    "value": obj1[i]
                })
            else:
                differences.extend(deep_compare(obj1[i], obj2[i], new_path))
    
    else:
        if obj1 != obj2:
            differences.append({
                "path": path,
                "type": "modified",
                "old": obj1,
                "new": obj2
            })
    
    return differences


def calculate_similarity(
    obj1: Any,
    obj2: Any
) -> float:
    """
    Calcular similitud entre dos objetos.
    
    Args:
        obj1: Primer objeto
        obj2: Segundo objeto
        
    Returns:
        Similitud (0-1)
    """
    if obj1 == obj2:
        return 1.0
    
    if type(obj1) != type(obj2):
        return 0.0
    
    if isinstance(obj1, str):
        return SequenceMatcher(None, obj1, obj2).ratio()
    
    if isinstance(obj1, (int, float)):
        if obj1 == 0 and obj2 == 0:
            return 1.0
        if obj1 == 0 or obj2 == 0:
            return 0.0
        return 1.0 - abs(obj1 - obj2) / max(abs(obj1), abs(obj2))
    
    if isinstance(obj1, dict):
        all_keys = set(obj1.keys()) | set(obj2.keys())
        if not all_keys:
            return 1.0
        
        similarities = [
            calculate_similarity(obj1.get(k), obj2.get(k))
            for k in all_keys
        ]
        return mean(similarities) if similarities else 0.0
    
    if isinstance(obj1, list):
        if len(obj1) != len(obj2):
            return 0.0
        if not obj1:
            return 1.0
        
        similarities = [
            calculate_similarity(obj1[i], obj2[i])
            for i in range(len(obj1))
        ]
        return mean(similarities) if similarities else 0.0
    
    return 0.0

