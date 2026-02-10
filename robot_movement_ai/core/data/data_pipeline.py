"""
Data Pipeline System
=====================

Sistema de pipelines de procesamiento de datos.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Etapa del pipeline."""
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    VALIDATE = "validate"
    ENRICH = "enrich"


@dataclass
class PipelineStep:
    """Paso del pipeline."""
    step_id: str
    name: str
    stage: PipelineStage
    func: Callable
    depends_on: List[str] = field(default_factory=list)
    enabled: bool = True
    retry_count: int = 0
    timeout: Optional[float] = None


class DataPipeline:
    """
    Pipeline de procesamiento de datos.
    
    Procesa datos a través de múltiples etapas.
    """
    
    def __init__(self, pipeline_id: str, name: str):
        """
        Inicializar pipeline.
        
        Args:
            pipeline_id: ID único del pipeline
            name: Nombre del pipeline
        """
        self.pipeline_id = pipeline_id
        self.name = name
        self.steps: List[PipelineStep] = []
        self.execution_history: List[Dict[str, Any]] = []
    
    def add_step(
        self,
        step_id: str,
        name: str,
        stage: PipelineStage,
        func: Callable,
        depends_on: Optional[List[str]] = None,
        enabled: bool = True,
        retry_count: int = 0,
        timeout: Optional[float] = None
    ) -> PipelineStep:
        """
        Agregar paso al pipeline.
        
        Args:
            step_id: ID único del paso
            name: Nombre del paso
            stage: Etapa del pipeline
            func: Función a ejecutar
            depends_on: Pasos de los que depende
            enabled: Si está habilitado
            retry_count: Número de reintentos
            timeout: Timeout en segundos
            
        Returns:
            Paso creado
        """
        step = PipelineStep(
            step_id=step_id,
            name=name,
            stage=stage,
            func=func,
            depends_on=depends_on or [],
            enabled=enabled,
            retry_count=retry_count,
            timeout=timeout
        )
        
        self.steps.append(step)
        return step
    
    async def execute(
        self,
        data: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecutar pipeline.
        
        Args:
            data: Datos de entrada
            context: Contexto adicional
            
        Returns:
            Resultado de la ejecución
        """
        if context is None:
            context = {}
        
        execution_id = f"{self.pipeline_id}_{len(self.execution_history)}"
        logger.info(f"Executing pipeline: {self.name} ({execution_id})")
        
        current_data = data
        step_results = {}
        
        # Ordenar pasos por dependencias
        ordered_steps = self._topological_sort()
        
        for step in ordered_steps:
            if not step.enabled:
                continue
            
            try:
                # Ejecutar paso
                if step.timeout:
                    import asyncio
                    if asyncio.iscoroutinefunction(step.func):
                        result = await asyncio.wait_for(
                            step.func(current_data, context),
                            timeout=step.timeout
                        )
                    else:
                        loop = asyncio.get_event_loop()
                        result = await asyncio.wait_for(
                            loop.run_in_executor(None, step.func, current_data, context),
                            timeout=step.timeout
                        )
                else:
                    if asyncio.iscoroutinefunction(step.func):
                        result = await step.func(current_data, context)
                    else:
                        result = step.func(current_data, context)
                
                current_data = result
                step_results[step.step_id] = {
                    "status": "completed",
                    "result": result
                }
            
            except Exception as e:
                logger.error(f"Step failed: {step.name} - {e}")
                step_results[step.step_id] = {
                    "status": "failed",
                    "error": str(e)
                }
                
                # Reintentar si está configurado
                if step.retry_count > 0:
                    for attempt in range(step.retry_count):
                        try:
                            if asyncio.iscoroutinefunction(step.func):
                                result = await step.func(current_data, context)
                            else:
                                result = step.func(current_data, context)
                            
                            current_data = result
                            step_results[step.step_id] = {
                                "status": "completed",
                                "result": result,
                                "retries": attempt + 1
                            }
                            break
                        except Exception as retry_error:
                            if attempt == step.retry_count - 1:
                                step_results[step.step_id]["error"] = str(retry_error)
                            continue
                else:
                    break
        
        execution_result = {
            "execution_id": execution_id,
            "pipeline_id": self.pipeline_id,
            "status": "completed" if all(
                s.get("status") == "completed" for s in step_results.values()
            ) else "failed",
            "steps": step_results,
            "final_data": current_data
        }
        
        self.execution_history.append(execution_result)
        return execution_result
    
    def _topological_sort(self) -> List[PipelineStep]:
        """Ordenar pasos topológicamente según dependencias."""
        # Implementación simple de ordenamiento topológico
        ordered = []
        visited = set()
        temp_visited = set()
        
        def visit(step: PipelineStep):
            if step.step_id in temp_visited:
                return  # Ciclo detectado
            if step.step_id in visited:
                return
            
            temp_visited.add(step.step_id)
            
            # Visitar dependencias primero
            for dep_id in step.depends_on:
                dep_step = next((s for s in self.steps if s.step_id == dep_id), None)
                if dep_step:
                    visit(dep_step)
            
            temp_visited.remove(step.step_id)
            visited.add(step.step_id)
            ordered.append(step)
        
        for step in self.steps:
            if step.step_id not in visited:
                visit(step)
        
        return ordered
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener historial de ejecuciones."""
        return self.execution_history[-limit:]


class PipelineManager:
    """Gestor de pipelines."""
    
    def __init__(self):
        """Inicializar gestor."""
        self.pipelines: Dict[str, DataPipeline] = {}
    
    def create_pipeline(self, pipeline_id: str, name: str) -> DataPipeline:
        """Crear nuevo pipeline."""
        pipeline = DataPipeline(pipeline_id, name)
        self.pipelines[pipeline_id] = pipeline
        return pipeline
    
    def get_pipeline(self, pipeline_id: str) -> Optional[DataPipeline]:
        """Obtener pipeline."""
        return self.pipelines.get(pipeline_id)
    
    def list_pipelines(self) -> List[DataPipeline]:
        """Listar todos los pipelines."""
        return list(self.pipelines.values())


# Instancia global
_pipeline_manager: Optional[PipelineManager] = None


def get_pipeline_manager() -> PipelineManager:
    """Obtener instancia global del gestor de pipelines."""
    global _pipeline_manager
    if _pipeline_manager is None:
        _pipeline_manager = PipelineManager()
    return _pipeline_manager

