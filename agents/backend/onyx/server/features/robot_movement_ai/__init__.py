"""
Robot Movement AI - Plataforma IA de Movimiento Robótico
==========================================================

Sistema avanzado de IA para control y optimización de movimiento robótico
mediante chat, con soporte para múltiples marcas y protocolos.

Características principales:
- Algoritmos de reinforcement learning para optimización de trayectorias
- Redes neuronales convolucionales para procesamiento visual
- Modelos predictivos para cinemática inversa
- Sistema de feedback en tiempo real a 1000Hz
- Integración con ROS (Robot Operating System)
- APIs RESTful para integración
- SDK para Python, C++, y MATLAB
- Soporte para KUKA, ABB, Fanuc, Universal Robots
"""

__version__ = "1.0.0"
__author__ = "Blatam Academy"

from .core.movement_engine import RobotMovementEngine
from .core.trajectory_optimizer import TrajectoryOptimizer
from .core.inverse_kinematics import InverseKinematicsSolver
from .core.visual_processor import VisualProcessor
from .core.real_time_feedback import RealTimeFeedbackSystem
from .api.robot_api import create_robot_app
from .chat.chat_controller import ChatRobotController

__all__ = [
    "RobotMovementEngine",
    "TrajectoryOptimizer",
    "InverseKinematicsSolver",
    "VisualProcessor",
    "RealTimeFeedbackSystem",
    "create_robot_app",
    "ChatRobotController",
]






