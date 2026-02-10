"""
Statistics - Estadísticas Avanzadas
===================================

Utilidades para cálculo de estadísticas y análisis de datos.
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from statistics import mean, median, stdev, variance
from collections import Counter
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """
    Calcular estadísticas básicas de una lista de valores.
    
    Args:
        values: Lista de valores numéricos
        
    Returns:
        Diccionario con estadísticas
    """
    if not values:
        return {}
    
    sorted_values = sorted(values)
    n = len(values)
    
    # Percentiles
    def percentile(data: List[float], p: float) -> float:
        """Calcular percentil"""
        if not data:
            return 0.0
        k = (len(data) - 1) * p
        f = int(k)
        c = k - f
        if f + 1 < len(data):
            return data[f] + (data[f + 1] - data[f]) * c
        return data[f]
    
    return {
        "count": n,
        "min": min(values),
        "max": max(values),
        "mean": mean(values),
        "median": median(values),
        "stdev": stdev(values) if n > 1 else 0.0,
        "variance": variance(values) if n > 1 else 0.0,
        "p25": percentile(sorted_values, 0.25),
        "p50": percentile(sorted_values, 0.50),
        "p75": percentile(sorted_values, 0.75),
        "p90": percentile(sorted_values, 0.90),
        "p95": percentile(sorted_values, 0.95),
        "p99": percentile(sorted_values, 0.99),
        "range": max(values) - min(values)
    }


def calculate_trend(values: List[float]) -> Dict[str, Any]:
    """
    Calcular tendencia de valores.
    
    Args:
        values: Lista de valores en orden temporal
        
    Returns:
        Diccionario con información de tendencia
    """
    if len(values) < 2:
        return {"trend": "insufficient_data"}
    
    # Calcular pendiente simple
    first_half = values[:len(values)//2]
    second_half = values[len(values)//2:]
    
    first_avg = mean(first_half) if first_half else 0
    second_avg = mean(second_half) if second_half else 0
    
    change = second_avg - first_avg
    change_percent = (change / first_avg * 100) if first_avg != 0 else 0
    
    if abs(change_percent) < 1:
        trend = "stable"
    elif change_percent > 0:
        trend = "increasing"
    else:
        trend = "decreasing"
    
    return {
        "trend": trend,
        "change": change,
        "change_percent": change_percent,
        "first_half_avg": first_avg,
        "second_half_avg": second_avg
    }


def calculate_frequency(items: List[Any]) -> Dict[Any, int]:
    """
    Calcular frecuencia de items.
    
    Args:
        items: Lista de items
        
    Returns:
        Diccionario con frecuencias
    """
    return dict(Counter(items))


def calculate_correlation(x: List[float], y: List[float]) -> Optional[float]:
    """
    Calcular correlación de Pearson entre dos listas.
    
    Args:
        x: Primera lista de valores
        y: Segunda lista de valores
        
    Returns:
        Coeficiente de correlación (-1 a 1) o None si no se puede calcular
    """
    if len(x) != len(y) or len(x) < 2:
        return None
    
    try:
        n = len(x)
        mean_x = mean(x)
        mean_y = mean(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        denominator_y = sum((y[i] - mean_y) ** 2 for i in range(n))
        
        denominator = (denominator_x * denominator_y) ** 0.5
        
        if denominator == 0:
            return None
        
        return numerator / denominator
    except Exception:
        return None


def group_by(
    items: List[Dict[str, Any]],
    key: str
) -> Dict[Any, List[Dict[str, Any]]]:
    """
    Agrupar items por clave.
    
    Args:
        items: Lista de diccionarios
        key: Clave para agrupar
        
    Returns:
        Diccionario agrupado
    """
    grouped = {}
    
    for item in items:
        group_key = item.get(key)
        if group_key not in grouped:
            grouped[group_key] = []
        grouped[group_key].append(item)
    
    return grouped


def aggregate_by(
    items: List[Dict[str, Any]],
    group_key: str,
    aggregate_key: str,
    operation: str = "sum"
) -> Dict[Any, float]:
    """
    Agregar valores por grupo.
    
    Args:
        items: Lista de diccionarios
        group_key: Clave para agrupar
        aggregate_key: Clave para agregar
        operation: Operación (sum, avg, min, max, count)
        
    Returns:
        Diccionario con valores agregados
    """
    grouped = group_by(items, group_key)
    result = {}
    
    for key, group_items in grouped.items():
        values = [item.get(aggregate_key, 0) for item in group_items if aggregate_key in item]
        
        if not values:
            result[key] = 0
            continue
        
        if operation == "sum":
            result[key] = sum(values)
        elif operation == "avg":
            result[key] = mean(values)
        elif operation == "min":
            result[key] = min(values)
        elif operation == "max":
            result[key] = max(values)
        elif operation == "count":
            result[key] = len(values)
        else:
            result[key] = 0
    
    return result


def calculate_rate(
    count: int,
    duration_seconds: float
) -> float:
    """
    Calcular tasa (por segundo).
    
    Args:
        count: Cantidad
        duration_seconds: Duración en segundos
        
    Returns:
        Tasa por segundo
    """
    if duration_seconds <= 0:
        return 0.0
    return count / duration_seconds


def calculate_growth_rate(
    initial: float,
    final: float,
    duration_seconds: float
) -> float:
    """
    Calcular tasa de crecimiento.
    
    Args:
        initial: Valor inicial
        final: Valor final
        duration_seconds: Duración en segundos
        
    Returns:
        Tasa de crecimiento por segundo
    """
    if duration_seconds <= 0 or initial == 0:
        return 0.0
    
    return ((final - initial) / initial) / duration_seconds




