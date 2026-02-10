"""
Data Pipeline System
====================
Sistema de pipeline de datos para transformación y procesamiento
"""

import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum


class TransformType(Enum):
    """Tipos de transformación"""
    FILTER = "filter"
    MAP = "map"
    REDUCE = "reduce"
    AGGREGATE = "aggregate"
    JOIN = "join"
    SORT = "sort"
    GROUP = "group"
    CUSTOM = "custom"


@dataclass
class TransformStep:
    """Paso de transformación"""
    id: str
    transform_type: TransformType
    config: Dict[str, Any]
    enabled: bool = True


@dataclass
class DataPipeline:
    """Pipeline de datos"""
    id: str
    name: str
    description: str
    steps: List[TransformStep]
    created_at: float
    last_run: Optional[float] = None
    run_count: int = 0


@dataclass
class PipelineResult:
    """Resultado de pipeline"""
    pipeline_id: str
    input_count: int
    output_count: int
    execution_time: float
    results: List[Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DataPipelineSystem:
    """
    Sistema de pipeline de datos
    """
    
    def __init__(self):
        self.pipelines: Dict[str, DataPipeline] = {}
        self.transform_handlers: Dict[TransformType, Callable] = {}
        self._init_default_handlers()
    
    def _init_default_handlers(self):
        """Inicializar handlers por defecto"""
        self.transform_handlers[TransformType.FILTER] = self._filter_transform
        self.transform_handlers[TransformType.MAP] = self._map_transform
        self.transform_handlers[TransformType.REDUCE] = self._reduce_transform
        self.transform_handlers[TransformType.AGGREGATE] = self._aggregate_transform
        self.transform_handlers[TransformType.SORT] = self._sort_transform
        self.transform_handlers[TransformType.GROUP] = self._group_transform
    
    def create_pipeline(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]]
    ) -> DataPipeline:
        """
        Crear pipeline de datos
        
        Args:
            name: Nombre del pipeline
            description: Descripción
            steps: Lista de pasos de transformación
        """
        pipeline_id = f"data_pipeline_{int(time.time())}"
        
        pipeline_steps = [
            TransformStep(
                id=f"step_{i}",
                transform_type=TransformType(s['type']),
                config=s.get('config', {}),
                enabled=s.get('enabled', True)
            )
            for i, s in enumerate(steps)
        ]
        
        pipeline = DataPipeline(
            id=pipeline_id,
            name=name,
            description=description,
            steps=pipeline_steps,
            created_at=time.time()
        )
        
        self.pipelines[pipeline_id] = pipeline
        return pipeline
    
    def register_transform_handler(
        self,
        transform_type: TransformType,
        handler: Callable
    ):
        """Registrar handler para transformación"""
        self.transform_handlers[transform_type] = handler
    
    def execute_pipeline(
        self,
        pipeline_id: str,
        data: List[Any]
    ) -> PipelineResult:
        """
        Ejecutar pipeline de datos
        
        Args:
            pipeline_id: ID del pipeline
            data: Datos de entrada
        """
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        pipeline = self.pipelines[pipeline_id]
        start_time = time.time()
        
        current_data = data.copy()
        input_count = len(current_data)
        
        # Ejecutar pasos en orden
        for step in pipeline.steps:
            if not step.enabled:
                continue
            
            handler = self.transform_handlers.get(step.transform_type)
            if not handler:
                raise ValueError(f"No handler for transform type {step.transform_type}")
            
            current_data = handler(current_data, step.config)
        
        execution_time = time.time() - start_time
        output_count = len(current_data) if isinstance(current_data, list) else 1
        
        result = PipelineResult(
            pipeline_id=pipeline_id,
            input_count=input_count,
            output_count=output_count,
            execution_time=execution_time,
            results=current_data if isinstance(current_data, list) else [current_data],
            metadata={
                'steps_executed': len([s for s in pipeline.steps if s.enabled]),
                'reduction_rate': (input_count - output_count) / input_count if input_count > 0 else 0
            }
        )
        
        pipeline.last_run = time.time()
        pipeline.run_count += 1
        
        return result
    
    def _filter_transform(self, data: List[Any], config: Dict[str, Any]) -> List[Any]:
        """Transformación de filtro"""
        condition = config.get('condition')
        if not condition:
            return data
        
        # Evaluar condición (simplificado)
        # En implementación real, usar evaluador de expresiones
        filtered = []
        for item in data:
            if self._evaluate_condition(item, condition):
                filtered.append(item)
        
        return filtered
    
    def _map_transform(self, data: List[Any], config: Dict[str, Any]) -> List[Any]:
        """Transformación de mapeo"""
        mapping = config.get('mapping')
        if not mapping:
            return data
        
        # Aplicar mapeo (simplificado)
        mapped = []
        for item in data:
            if isinstance(item, dict) and mapping in item:
                mapped.append(item[mapping])
            else:
                mapped.append(item)
        
        return mapped
    
    def _reduce_transform(self, data: List[Any], config: Dict[str, Any]) -> Any:
        """Transformación de reducción"""
        reducer = config.get('reducer', 'sum')
        initial = config.get('initial', 0)
        
        if reducer == 'sum':
            return sum(data) if all(isinstance(x, (int, float)) for x in data) else initial
        elif reducer == 'count':
            return len(data)
        elif reducer == 'avg':
            numeric_data = [x for x in data if isinstance(x, (int, float))]
            return sum(numeric_data) / len(numeric_data) if numeric_data else 0
        else:
            return initial
    
    def _aggregate_transform(self, data: List[Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Transformación de agregación"""
        group_by = config.get('group_by')
        aggregate = config.get('aggregate', {})
        
        if not group_by:
            return {'total': len(data)}
        
        # Agrupar y agregar (simplificado)
        groups = {}
        for item in data:
            if isinstance(item, dict) and group_by in item:
                key = item[group_by]
                if key not in groups:
                    groups[key] = []
                groups[key].append(item)
        
        result = {}
        for key, group_data in groups.items():
            result[key] = {
                'count': len(group_data),
                'data': group_data
            }
        
        return result
    
    def _sort_transform(self, data: List[Any], config: Dict[str, Any]) -> List[Any]:
        """Transformación de ordenamiento"""
        key = config.get('key')
        reverse = config.get('reverse', False)
        
        if key:
            # Ordenar por clave
            return sorted(data, key=lambda x: x.get(key) if isinstance(x, dict) else x, reverse=reverse)
        else:
            # Ordenar directamente
            return sorted(data, reverse=reverse)
    
    def _group_transform(self, data: List[Any], config: Dict[str, Any]) -> Dict[str, List[Any]]:
        """Transformación de agrupación"""
        group_by = config.get('group_by')
        if not group_by:
            return {'default': data}
        
        groups = {}
        for item in data:
            if isinstance(item, dict) and group_by in item:
                key = str(item[group_by])
                if key not in groups:
                    groups[key] = []
                groups[key].append(item)
            else:
                if 'default' not in groups:
                    groups['default'] = []
                groups['default'].append(item)
        
        return groups
    
    def _evaluate_condition(self, item: Any, condition: Dict[str, Any]) -> bool:
        """Evaluar condición (simplificado)"""
        # En implementación real, usar evaluador de expresiones completo
        field = condition.get('field')
        operator = condition.get('operator', '==')
        value = condition.get('value')
        
        if not field:
            return True
        
        item_value = item.get(field) if isinstance(item, dict) else item
        
        if operator == '==':
            return item_value == value
        elif operator == '!=':
            return item_value != value
        elif operator == '>':
            return item_value > value
        elif operator == '<':
            return item_value < value
        elif operator == '>=':
            return item_value >= value
        elif operator == '<=':
            return item_value <= value
        else:
            return True


# Instancia global
data_pipeline = DataPipelineSystem()

