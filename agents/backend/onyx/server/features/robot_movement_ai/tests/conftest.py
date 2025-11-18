"""
Pytest Configuration and Fixtures
==================================

Fixtures compartidas para tests.
"""

import pytest
import numpy as np
from typing import Generator

from ..config.robot_config import RobotConfig, RobotBrand
from ..core.trajectory_optimizer import TrajectoryOptimizer, TrajectoryPoint
from ..core.movement_engine import RobotMovementEngine


@pytest.fixture
def robot_config() -> RobotConfig:
    """Fixture para configuración de robot."""
    return RobotConfig(
        robot_brand=RobotBrand.GENERIC,
        ros_enabled=False,
        camera_enabled=False,
        feedback_frequency=100,
        api_port=8011  # Puerto diferente para tests
    )


@pytest.fixture
def trajectory_optimizer() -> TrajectoryOptimizer:
    """Fixture para trajectory optimizer."""
    return TrajectoryOptimizer()


@pytest.fixture
def sample_start_point() -> TrajectoryPoint:
    """Fixture para punto inicial de trayectoria."""
    return TrajectoryPoint(
        position=np.array([0.0, 0.0, 0.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0]),
        timestamp=0.0
    )


@pytest.fixture
def sample_goal_point() -> TrajectoryPoint:
    """Fixture para punto objetivo de trayectoria."""
    return TrajectoryPoint(
        position=np.array([1.0, 1.0, 1.0]),
        orientation=np.array([0.0, 0.0, 0.0, 1.0]),
        timestamp=1.0
    )


@pytest.fixture
def sample_obstacles() -> list:
    """Fixture para obstáculos de prueba."""
    return [
        np.array([0.3, 0.3, 0.3, 0.7, 0.7, 0.7])  # Obstáculo en el medio
    ]


@pytest.fixture
def movement_engine(robot_config: RobotConfig) -> RobotMovementEngine:
    """Fixture para movement engine."""
    return RobotMovementEngine(robot_config)


@pytest.fixture(autouse=True)
def reset_metrics():
    """Resetear métricas antes de cada test."""
    from ..core.metrics import get_metrics_collector
    collector = get_metrics_collector()
    # Resetear todas las métricas conocidas
    yield
    # Cleanup después del test si es necesario






