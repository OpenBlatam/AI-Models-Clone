"""
Basic Usage Example
===================

Ejemplo básico de uso del sistema de movimiento robótico.
"""

import numpy as np
from robot_movement_ai.config.robot_config import RobotConfig, RobotBrand
from robot_movement_ai.core.trajectory_optimizer import TrajectoryOptimizer, TrajectoryPoint
from robot_movement_ai.core.movement_engine import RobotMovementEngine
from robot_movement_ai.core.logging_config import setup_logging, get_logger

# Configurar logging
setup_logging(level="INFO", colored=True)
logger = get_logger(__name__)


def example_basic_trajectory_optimization():
    """Ejemplo básico de optimización de trayectoria."""
    logger.info("=== Ejemplo: Optimización Básica de Trayectoria ===")
    
    # Crear optimizador
    optimizer = TrajectoryOptimizer()
    
    # Definir punto inicial y objetivo
    start = TrajectoryPoint(
        position=np.array([0.0, 0.0, 0.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0]),
        timestamp=0.0
    )
    
    goal = TrajectoryPoint(
        position=np.array([1.0, 1.0, 1.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0]),
        timestamp=1.0
    )
    
    # Optimizar trayectoria
    trajectory = optimizer.optimize_trajectory(start, goal)
    
    logger.info(f"Trayectoria optimizada con {len(trajectory)} puntos")
    logger.info(f"Primer punto: {trajectory[0].position}")
    logger.info(f"Último punto: {trajectory[-1].position}")
    
    return trajectory


def example_trajectory_with_obstacles():
    """Ejemplo de optimización con obstáculos."""
    logger.info("=== Ejemplo: Optimización con Obstáculos ===")
    
    optimizer = TrajectoryOptimizer()
    
    start = TrajectoryPoint(
        position=np.array([0.0, 0.0, 0.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0])
    )
    
    goal = TrajectoryPoint(
        position=np.array([2.0, 2.0, 2.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0])
    )
    
    # Definir obstáculo (bounding box)
    obstacles = [
        np.array([0.8, 0.8, 0.8, 1.2, 1.2, 1.2])  # Obstáculo en el medio
    ]
    
    # Optimizar evitando obstáculos
    trajectory = optimizer.optimize_trajectory(start, goal, obstacles=obstacles)
    
    logger.info(f"Trayectoria optimizada evitando {len(obstacles)} obstáculos")
    
    return trajectory


def example_different_algorithms():
    """Ejemplo usando diferentes algoritmos."""
    logger.info("=== Ejemplo: Diferentes Algoritmos ===")
    
    from robot_movement_ai.core.constants import OptimizationAlgorithm
    
    optimizer = TrajectoryOptimizer()
    
    start = TrajectoryPoint(
        position=np.array([0.0, 0.0, 0.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0])
    )
    
    goal = TrajectoryPoint(
        position=np.array([1.0, 1.0, 1.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0])
    )
    
    # Probar diferentes algoritmos
    algorithms = [
        OptimizationAlgorithm.PPO,
        OptimizationAlgorithm.DQN,
        OptimizationAlgorithm.A_STAR,
        OptimizationAlgorithm.RRT,
        OptimizationAlgorithm.HEURISTIC
    ]
    
    for algorithm in algorithms:
        optimizer.algorithm = algorithm
        trajectory = optimizer.optimize_trajectory(start, goal)
        logger.info(f"Algoritmo {algorithm.value}: {len(trajectory)} puntos")


def example_trajectory_analysis():
    """Ejemplo de análisis de trayectoria."""
    logger.info("=== Ejemplo: Análisis de Trayectoria ===")
    
    optimizer = TrajectoryOptimizer()
    
    start = TrajectoryPoint(
        position=np.array([0.0, 0.0, 0.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0])
    )
    
    goal = TrajectoryPoint(
        position=np.array([1.0, 1.0, 1.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0])
    )
    
    trajectory = optimizer.optimize_trajectory(start, goal)
    
    # Analizar trayectoria
    analysis = optimizer.analyze_trajectory(trajectory)
    
    logger.info("Análisis de trayectoria:")
    logger.info(f"  Distancia total: {analysis['total_distance']:.3f}m")
    logger.info(f"  Duración: {analysis['duration']:.3f}s")
    logger.info(f"  Velocidad promedio: {analysis['average_speed']:.3f}m/s")
    logger.info(f"  Curvatura promedio: {analysis['average_curvature']:.6f}")
    
    return analysis


def example_serialization():
    """Ejemplo de serialización de trayectoria."""
    logger.info("=== Ejemplo: Serialización ===")
    
    from robot_movement_ai.core.serialization import (
        serialize_trajectory,
        deserialize_trajectory
    )
    
    optimizer = TrajectoryOptimizer()
    
    start = TrajectoryPoint(
        position=np.array([0.0, 0.0, 0.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0])
    )
    
    goal = TrajectoryPoint(
        position=np.array([1.0, 1.0, 1.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0])
    )
    
    trajectory = optimizer.optimize_trajectory(start, goal)
    
    # Serializar
    serialize_trajectory(trajectory, "example_trajectory.json", format="json")
    logger.info("Trayectoria serializada a example_trajectory.json")
    
    # Deserializar
    loaded_trajectory = deserialize_trajectory("example_trajectory.json")
    logger.info(f"Trayectoria deserializada con {len(loaded_trajectory)} puntos")
    
    return loaded_trajectory


def example_metrics():
    """Ejemplo de uso de métricas."""
    logger.info("=== Ejemplo: Métricas ===")
    
    from robot_movement_ai.core.metrics import get_metrics_collector
    
    optimizer = TrajectoryOptimizer()
    
    start = TrajectoryPoint(
        position=np.array([0.0, 0.0, 0.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0])
    )
    
    goal = TrajectoryPoint(
        position=np.array([1.0, 1.0, 1.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0])
    )
    
    # Optimizar varias veces
    for i in range(5):
        trajectory = optimizer.optimize_trajectory(start, goal)
    
    # Obtener métricas
    collector = get_metrics_collector()
    summary = collector.get_metrics_summary()
    
    logger.info("Resumen de métricas:")
    logger.info(f"  Total de métricas: {summary['total_metrics']}")
    logger.info(f"  Uptime: {summary['uptime_seconds']:.2f}s")
    
    if 'trajectory_optimization.requests' in summary['counters']:
        requests = summary['counters']['trajectory_optimization.requests']
        logger.info(f"  Requests: {requests['latest']}")
    
    return summary


if __name__ == "__main__":
    logger.info("Ejemplos de uso del Robot Movement AI")
    logger.info("=" * 60)
    
    try:
        # Ejecutar ejemplos
        example_basic_trajectory_optimization()
        print()
        
        example_trajectory_with_obstacles()
        print()
        
        example_different_algorithms()
        print()
        
        example_trajectory_analysis()
        print()
        
        example_serialization()
        print()
        
        example_metrics()
        print()
        
        logger.info("=" * 60)
        logger.info("Todos los ejemplos completados exitosamente!")
        
    except Exception as e:
        logger.error(f"Error en ejemplos: {e}", exc_info=True)






