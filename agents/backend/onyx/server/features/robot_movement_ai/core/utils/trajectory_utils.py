"""
Trajectory Utilities
====================

Utilidades para trabajar con trayectorias.
"""

import numpy as np
from typing import List, Optional
import logging

from ..trajectory_optimizer import TrajectoryPoint
from ..constants import MAX_JUMP_DISTANCE

logger = logging.getLogger(__name__)


def calculate_trajectory_distance(trajectory: List[TrajectoryPoint]) -> float:
    """
    Calcular distancia total de una trayectoria.
    
    Args:
        trajectory: Lista de puntos de trayectoria
        
    Returns:
        Distancia total en metros
    """
    if len(trajectory) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(1, len(trajectory)):
        distance = np.linalg.norm(
            trajectory[i].position - trajectory[i - 1].position
        )
        total_distance += distance
    
    return total_distance


def calculate_trajectory_curvature(trajectory: List[TrajectoryPoint]) -> float:
    """
    Calcular curvatura promedio de una trayectoria.
    
    Args:
        trajectory: Lista de puntos de trayectoria
        
    Returns:
        Curvatura promedio
    """
    if len(trajectory) < 3:
        return 0.0
    
    from .math_utils import calculate_curvature
    
    total_curvature = 0.0
    for i in range(1, len(trajectory) - 1):
        curvature = calculate_curvature(
            trajectory[i - 1].position,
            trajectory[i].position,
            trajectory[i + 1].position
        )
        total_curvature += curvature
    
    return total_curvature / (len(trajectory) - 2)


def smooth_trajectory(
    trajectory: List[TrajectoryPoint],
    window_size: int = 3
) -> List[TrajectoryPoint]:
    """
    Suavizar trayectoria usando filtro de media móvil.
    
    Args:
        trajectory: Trayectoria a suavizar
        window_size: Tamaño de la ventana
        
    Returns:
        Trayectoria suavizada
    """
    if len(trajectory) < window_size:
        return trajectory
    
    smoothed = [trajectory[0]]  # Mantener primer punto
    
    half_window = window_size // 2
    
    for i in range(1, len(trajectory) - 1):
        # Calcular ventana
        start_idx = max(0, i - half_window)
        end_idx = min(len(trajectory), i + half_window + 1)
        window = trajectory[start_idx:end_idx]
        
        # Promedio ponderado
        weights = np.array([0.25, 0.5, 0.25][:len(window)])
        weights = weights / weights.sum()
        
        smooth_pos = np.average(
            [p.position for p in window],
            axis=0,
            weights=weights
        )
        
        smoothed_point = TrajectoryPoint(
            position=smooth_pos,
            orientation=trajectory[i].orientation,
            velocity=trajectory[i].velocity,
            acceleration=trajectory[i].acceleration,
            timestamp=trajectory[i].timestamp
        )
        smoothed.append(smoothed_point)
    
    smoothed.append(trajectory[-1])  # Mantener último punto
    return smoothed


def validate_trajectory_continuity(
    trajectory: List[TrajectoryPoint],
    max_jump: float = MAX_JUMP_DISTANCE
) -> Tuple[bool, List[int]]:
    """
    Validar continuidad de una trayectoria.
    
    Args:
        trajectory: Trayectoria a validar
        max_jump: Distancia máxima permitida entre puntos consecutivos
        
    Returns:
        Tuple de (es_válida, lista_de_índices_problemáticos)
    """
    if len(trajectory) < 2:
        return True, []
    
    problematic_indices = []
    
    for i in range(1, len(trajectory)):
        prev_pos = trajectory[i - 1].position
        curr_pos = trajectory[i].position
        distance = np.linalg.norm(curr_pos - prev_pos)
        
        if distance > max_jump:
            problematic_indices.append(i)
            logger.warning(
                f"Large jump detected at point {i}: {distance:.3f}m "
                f"(max: {max_jump:.3f}m)"
            )
    
    return len(problematic_indices) == 0, problematic_indices






