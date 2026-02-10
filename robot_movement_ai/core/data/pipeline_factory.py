"""
Pipeline Factory
================

Factory unificada para crear pipelines de diferentes tipos.
"""

import logging
from typing import Dict, Any, Optional, TypeVar, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class PipelineFactoryConfig:
    """Configuración de la factory."""
    enable_checkpointing: bool = True
    enable_metrics: bool = True
    enable_logging: bool = True
    default_timeout: float = 300.0


class UnifiedPipelineFactory:
    """
    Factory unificada para crear pipelines de diferentes tipos.
    """
    
    def __init__(self, config: Optional[PipelineFactoryConfig] = None):
        """
        Inicializar factory.
        
        Args:
            config: Configuración
        """
        self.config = config or PipelineFactoryConfig()
    
    def create_modular_pipeline(
        self,
        name: str,
        stages: Optional[list] = None,
        enable_checkpointing: Optional[bool] = None,
        enable_metrics: Optional[bool] = None
    ) -> Any:
        """
        Crear pipeline modular.
        
        Args:
            name: Nombre del pipeline
            stages: Lista de etapas (opcional)
            enable_checkpointing: Habilitar checkpointing
            enable_metrics: Habilitar métricas
            
        Returns:
            Pipeline modular
        """
        try:
            from .architecture.pipelines import PipelineBuilder
            
            builder = PipelineBuilder(name)
            
            if enable_checkpointing is None:
                enable_checkpointing = self.config.enable_checkpointing
            if enable_metrics is None:
                enable_metrics = self.config.enable_metrics
            
            if enable_checkpointing:
                from .architecture.pipelines.checkpointing import CheckpointManager
                checkpoint_manager = CheckpointManager()
                from .architecture.pipelines.checkpointing import PipelineWithCheckpointing
                pipeline = PipelineWithCheckpointing(name, checkpoint_manager)
            else:
                from .architecture.pipelines import Pipeline
                pipeline = Pipeline(name)
            
            if enable_metrics:
                from .architecture.pipelines.metrics import MetricsCollector
                from .architecture.pipelines.middleware import MetricsMiddleware
                collector = MetricsCollector()
                pipeline.add_middleware(MetricsMiddleware(collector))
            
            if self.config.enable_logging:
                from .architecture.pipelines.middleware import LoggingMiddleware
                pipeline.add_middleware(LoggingMiddleware())
            
            if stages:
                for stage in stages:
                    pipeline.add_stage(stage)
            
            return pipeline
            
        except ImportError as e:
            logger.error(f"Error creando pipeline modular: {e}")
            raise
    
    def create_training_pipeline(
        self,
        name: str,
        model: Any,
        config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Crear pipeline de entrenamiento.
        
        Args:
            name: Nombre del pipeline
            model: Modelo a entrenar
            config: Configuración de entrenamiento
            
        Returns:
            Pipeline de entrenamiento
        """
        try:
            from .architecture.pipelines_training import TrainingPipeline, TrainingConfig
            
            training_config = TrainingConfig(**config) if config else TrainingConfig()
            pipeline = TrainingPipeline(model, training_config)
            
            return pipeline
            
        except ImportError as e:
            logger.error(f"Error creando pipeline de entrenamiento: {e}")
            raise
    
    def create_inference_pipeline(
        self,
        name: str,
        model: Any,
        config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Crear pipeline de inferencia.
        
        Args:
            name: Nombre del pipeline
            model: Modelo para inferencia
            config: Configuración de inferencia
            
        Returns:
            Pipeline de inferencia
        """
        try:
            from .architecture.pipelines_inference import InferencePipeline, InferenceConfig
            
            inference_config = InferenceConfig(**config) if config else InferenceConfig()
            pipeline = InferencePipeline(model, inference_config)
            
            return pipeline
            
        except ImportError as e:
            logger.error(f"Error creando pipeline de inferencia: {e}")
            raise
    
    def create_hybrid_pipeline(
        self,
        name: str,
        modular_config: Dict[str, Any],
        dl_config: Dict[str, Any],
        integration_strategy: str = "sequential"
    ) -> Any:
        """
        Crear pipeline híbrido.
        
        Args:
            name: Nombre del pipeline
            modular_config: Configuración del pipeline modular
            dl_config: Configuración del pipeline DL
            integration_strategy: Estrategia de integración
            
        Returns:
            Pipeline híbrido
        """
        from .pipeline_integration import get_integrator
        
        integrator = get_integrator()
        
        # Crear pipelines individuales
        modular_pipeline = self.create_modular_pipeline(
            f"{name}_modular",
            **modular_config
        )
        
        if 'model' in dl_config:
            dl_pipeline = self.create_inference_pipeline(
                f"{name}_dl",
                dl_config['model'],
                dl_config.get('config')
            )
        else:
            raise ValueError("dl_config debe incluir 'model'")
        
        # Registrar en integrador
        integrator.register_modular_pipeline(f"{name}_modular", modular_pipeline)
        integrator.register_dl_pipeline(f"{name}_dl", dl_pipeline)
        
        # Crear híbrido
        hybrid = integrator.create_hybrid_pipeline(
            name,
            f"{name}_modular",
            f"{name}_dl",
            integration_strategy
        )
        
        return hybrid


# Instancia global de la factory
_global_factory: Optional[UnifiedPipelineFactory] = None


def get_factory(config: Optional[PipelineFactoryConfig] = None) -> UnifiedPipelineFactory:
    """
    Obtener instancia global de la factory.
    
    Args:
        config: Configuración (solo se usa en la primera llamada)
        
    Returns:
        Instancia de la factory
    """
    global _global_factory
    
    if _global_factory is None:
        _global_factory = UnifiedPipelineFactory(config)
    
    return _global_factory

