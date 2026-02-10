"""
Pipeline Integration
====================

Utilidades para integrar los diferentes sistemas de pipelines.
"""

import logging
from typing import Dict, Any, Optional, List, TypeVar
from pathlib import Path

logger = logging.getLogger(__name__)

T = TypeVar('T')


class PipelineIntegrator:
    """
    Integrador de diferentes sistemas de pipelines.
    """
    
    def __init__(self):
        """Inicializar integrador."""
        self.modular_pipelines: Dict[str, Any] = {}
        self.dl_pipelines: Dict[str, Any] = {}
        self.integrated_pipelines: Dict[str, Any] = {}
    
    def register_modular_pipeline(
        self,
        name: str,
        pipeline: Any
    ) -> None:
        """
        Registrar pipeline modular.
        
        Args:
            name: Nombre del pipeline
            pipeline: Instancia del pipeline modular
        """
        self.modular_pipelines[name] = pipeline
        logger.info(f"Pipeline modular registrado: {name}")
    
    def register_dl_pipeline(
        self,
        name: str,
        pipeline: Any
    ) -> None:
        """
        Registrar pipeline de deep learning.
        
        Args:
            name: Nombre del pipeline
            pipeline: Instancia del pipeline DL
        """
        self.dl_pipelines[name] = pipeline
        logger.info(f"Pipeline DL registrado: {name}")
    
    def create_hybrid_pipeline(
        self,
        name: str,
        modular_pipeline_name: str,
        dl_pipeline_name: str,
        integration_strategy: str = "sequential"
    ) -> Any:
        """
        Crear pipeline híbrido que combina modular y DL.
        
        Args:
            name: Nombre del pipeline híbrido
            modular_pipeline_name: Nombre del pipeline modular
            dl_pipeline_name: Nombre del pipeline DL
            integration_strategy: Estrategia de integración (sequential, parallel, conditional)
            
        Returns:
            Pipeline híbrido
        """
        modular_pipeline = self.modular_pipelines.get(modular_pipeline_name)
        dl_pipeline = self.dl_pipelines.get(dl_pipeline_name)
        
        if not modular_pipeline:
            raise ValueError(f"Pipeline modular '{modular_pipeline_name}' no encontrado")
        if not dl_pipeline:
            raise ValueError(f"Pipeline DL '{dl_pipeline_name}' no encontrado")
        
        try:
            from .architecture.pipelines import Pipeline, FunctionStage
            
            hybrid = Pipeline(name)
            
            if integration_strategy == "sequential":
                # Ejecutar modular primero, luego DL
                def preprocess_with_modular(data: T, context: Dict[str, Any] = None) -> T:
                    return modular_pipeline.process(data, context)
                
                def process_with_dl(data: T, context: Dict[str, Any] = None) -> T:
                    return dl_pipeline.infer(data) if hasattr(dl_pipeline, 'infer') else dl_pipeline(data)
                
                hybrid.add_stage(FunctionStage(preprocess_with_modular, name="modular_preprocess"))
                hybrid.add_stage(FunctionStage(process_with_dl, name="dl_process"))
            
            elif integration_strategy == "parallel":
                # Ejecutar en paralelo y combinar resultados
                from .architecture.pipelines import ParallelExecutor
                hybrid.set_executor(ParallelExecutor())
                
                def process_modular(data: T, context: Dict[str, Any] = None) -> T:
                    return modular_pipeline.process(data, context)
                
                def process_dl(data: T, context: Dict[str, Any] = None) -> T:
                    return dl_pipeline.infer(data) if hasattr(dl_pipeline, 'infer') else dl_pipeline(data)
                
                hybrid.add_stage(FunctionStage(process_modular, name="modular"))
                hybrid.add_stage(FunctionStage(process_dl, name="dl"))
            
            self.integrated_pipelines[name] = hybrid
            logger.info(f"Pipeline híbrido creado: {name}")
            return hybrid
            
        except ImportError as e:
            logger.error(f"Error importando componentes modulares: {e}")
            raise
    
    def wrap_dl_pipeline_as_modular(
        self,
        name: str,
        dl_pipeline: Any
    ) -> Any:
        """
        Envolver pipeline DL como pipeline modular.
        
        Args:
            name: Nombre del pipeline
            dl_pipeline: Pipeline DL
            
        Returns:
            Pipeline modular que envuelve el DL
        """
        try:
            from .architecture.pipelines import Pipeline, FunctionStage
            
            wrapped = Pipeline(name)
            
            def dl_wrapper(data: T, context: Dict[str, Any] = None) -> T:
                if hasattr(dl_pipeline, 'infer'):
                    return dl_pipeline.infer(data)
                elif hasattr(dl_pipeline, 'process'):
                    return dl_pipeline.process(data)
                elif callable(dl_pipeline):
                    return dl_pipeline(data)
                else:
                    raise ValueError("Pipeline DL no tiene método de inferencia reconocido")
            
            wrapped.add_stage(FunctionStage(dl_wrapper, name="dl_inference"))
            
            logger.info(f"Pipeline DL envuelto como modular: {name}")
            return wrapped
            
        except ImportError as e:
            logger.error(f"Error importando componentes modulares: {e}")
            raise
    
    def wrap_modular_pipeline_as_dl(
        self,
        name: str,
        modular_pipeline: Any
    ) -> Any:
        """
        Envolver pipeline modular como pipeline DL.
        
        Args:
            name: Nombre del pipeline
            modular_pipeline: Pipeline modular
            
        Returns:
            Wrapper que expone interfaz DL
        """
        class ModularAsDL:
            def __init__(self, pipeline: Any, name: str):
                self.pipeline = pipeline
                self.name = name
            
            def infer(self, data: T) -> T:
                """Interfaz de inferencia DL."""
                return self.pipeline.process(data)
            
            def train(self, data: T) -> None:
                """Interfaz de entrenamiento DL (no implementado)."""
                raise NotImplementedError("Pipeline modular no soporta entrenamiento")
        
        wrapped = ModularAsDL(modular_pipeline, name)
        logger.info(f"Pipeline modular envuelto como DL: {name}")
        return wrapped
    
    def get_integration_info(self) -> Dict[str, Any]:
        """
        Obtener información de integración.
        
        Returns:
            Diccionario con información de pipelines registrados
        """
        return {
            'modular_pipelines': list(self.modular_pipelines.keys()),
            'dl_pipelines': list(self.dl_pipelines.keys()),
            'integrated_pipelines': list(self.integrated_pipelines.keys())
        }


# Instancia global del integrador
_global_integrator: Optional[PipelineIntegrator] = None


def get_integrator() -> PipelineIntegrator:
    """
    Obtener instancia global del integrador.
    
    Returns:
        Instancia del integrador
    """
    global _global_integrator
    
    if _global_integrator is None:
        _global_integrator = PipelineIntegrator()
    
    return _global_integrator

