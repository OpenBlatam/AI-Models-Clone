"""
Robot Configuration
===================

Configuración centralizada para el sistema de movimiento robótico.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from ..core.exceptions import ConfigurationError


class RobotBrand(Enum):
    """Marcas de robots soportadas."""
    KUKA = "kuka"
    ABB = "abb"
    FANUC = "fanuc"
    UNIVERSAL_ROBOTS = "universal_robots"
    GENERIC = "generic"


@dataclass
class RobotConfig:
    """Configuración del sistema de movimiento robótico."""
    
    # General settings
    robot_brand: RobotBrand = RobotBrand.GENERIC
    ros_enabled: bool = True
    log_level: str = "INFO"
    
    # Performance settings
    feedback_frequency: int = 1000  # Hz
    trajectory_update_rate: int = 100  # Hz
    visual_processing_rate: int = 30  # FPS
    
    # Paths
    storage_path: str = field(default_factory=lambda: str(Path(__file__).parent.parent / "storage"))
    logs_directory: str = field(default_factory=lambda: str(Path(__file__).parent.parent / "logs"))
    models_directory: str = field(default_factory=lambda: str(Path(__file__).parent.parent / "models"))
    
    # ROS settings
    ros_master_uri: str = os.getenv("ROS_MASTER_URI", "http://localhost:11311")
    ros_node_name: str = "robot_movement_ai"
    
    # AI Model settings
    rl_model_path: Optional[str] = None
    cnn_model_path: Optional[str] = None
    ik_model_path: Optional[str] = None
    
    # Robot connection settings
    robot_ip: Optional[str] = os.getenv("ROBOT_IP", "192.168.1.100")
    robot_port: int = int(os.getenv("ROBOT_PORT", "30001"))
    connection_timeout: float = 10.0
    
    # Safety settings
    max_velocity: float = 1.0  # m/s
    max_acceleration: float = 2.0  # m/s²
    max_joint_velocity: float = 1.57  # rad/s
    collision_detection_enabled: bool = True
    emergency_stop_enabled: bool = True
    
    # Trajectory optimization
    trajectory_optimization_enabled: bool = True
    energy_optimization_enabled: bool = True
    vibration_compensation_enabled: bool = True
    
    # Visual processing
    camera_enabled: bool = True
    camera_resolution: tuple = (1920, 1080)
    object_detection_enabled: bool = True
    
    # Chat settings
    chat_enabled: bool = True
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4")
    llm_api_key: Optional[str] = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8010
    api_cors_enabled: bool = True
    api_cors_origins: list = field(default_factory=lambda: ["*"])
    
    def __post_init__(self):
        """Validar y crear directorios necesarios."""
        self._validate()
        self._create_directories()
    
    def _validate(self):
        """Validar configuración."""
        # Validar frecuencia de feedback
        if self.feedback_frequency <= 0 or self.feedback_frequency > 2000:
            raise ConfigurationError(
                f"Feedback frequency must be between 1 and 2000 Hz, got {self.feedback_frequency}"
            )
        
        # Validar límites de seguridad
        if self.max_velocity <= 0:
            raise ConfigurationError("Max velocity must be positive")
        
        if self.max_acceleration <= 0:
            raise ConfigurationError("Max acceleration must be positive")
        
        if self.max_joint_velocity <= 0:
            raise ConfigurationError("Max joint velocity must be positive")
        
        # Validar resolución de cámara
        if len(self.camera_resolution) != 2:
            raise ConfigurationError("Camera resolution must be a tuple of 2 elements")
        
        if any(r <= 0 for r in self.camera_resolution):
            raise ConfigurationError("Camera resolution values must be positive")
        
        # Validar puerto
        if not (1 <= self.api_port <= 65535):
            raise ConfigurationError(f"API port must be between 1 and 65535, got {self.api_port}")
        
        # Validar log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ConfigurationError(
                f"Log level must be one of {valid_log_levels}, got {self.log_level}"
            )
    
    def _create_directories(self):
        """Crear directorios necesarios."""
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
        Path(self.logs_directory).mkdir(parents=True, exist_ok=True)
        Path(self.models_directory).mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario."""
        return {
            "robot_brand": self.robot_brand.value,
            "ros_enabled": self.ros_enabled,
            "feedback_frequency": self.feedback_frequency,
            "trajectory_update_rate": self.trajectory_update_rate,
            "visual_processing_rate": self.visual_processing_rate,
            "max_velocity": self.max_velocity,
            "max_acceleration": self.max_acceleration,
            "collision_detection_enabled": self.collision_detection_enabled,
            "trajectory_optimization_enabled": self.trajectory_optimization_enabled,
        }

