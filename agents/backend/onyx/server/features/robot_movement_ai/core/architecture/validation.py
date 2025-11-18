"""
Validation Layer
================

Validación con Pydantic para requests, responses y configuración.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

try:
    from pydantic import BaseModel, Field, validator, root_validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Fallback básico
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        class Config:
            pass

logger = logging.getLogger(__name__)


if PYDANTIC_AVAILABLE:
    class RouteRequestModel(BaseModel):
        """Modelo validado para request de ruta."""
        start_node: str = Field(..., min_length=1, description="Nodo de inicio")
        end_node: str = Field(..., min_length=1, description="Nodo de fin")
        strategy: str = Field(default="shortest_path", description="Estrategia de routing")
        constraints: Optional[Dict[str, Any]] = Field(default=None, description="Restricciones")
        metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadatos adicionales")
        
        @validator('start_node', 'end_node')
        def validate_nodes(cls, v):
            if not v or not v.strip():
                raise ValueError("Nodo no puede estar vacío")
            return v.strip()
        
        @validator('strategy')
        def validate_strategy(cls, v):
            allowed = ["shortest_path", "fastest_path", "least_cost", "load_balanced", 
                      "adaptive", "deep_learning", "transformer", "llm_optimized", 
                      "gnn_based", "reinforcement_learning"]
            if v not in allowed:
                logger.warning(f"Estrategia '{v}' no está en la lista permitida")
            return v
        
        class Config:
            json_schema_extra = {
                "example": {
                    "start_node": "A",
                    "end_node": "B",
                    "strategy": "shortest_path",
                    "constraints": {"max_distance": 100}
                }
            }
    
    class RouteResponseModel(BaseModel):
        """Modelo validado para response de ruta."""
        route: List[str] = Field(..., min_items=2, description="Ruta encontrada")
        metrics: Dict[str, float] = Field(..., description="Métricas de la ruta")
        confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza de la ruta")
        metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadatos adicionales")
        
        @validator('route')
        def validate_route(cls, v):
            if len(v) < 2:
                raise ValueError("Ruta debe tener al menos 2 nodos")
            return v
        
        @validator('metrics')
        def validate_metrics(cls, v):
            required = ["distance", "time", "cost"]
            for key in required:
                if key not in v:
                    raise ValueError(f"Métrica requerida '{key}' no encontrada")
            return v
        
        class Config:
            json_schema_extra = {
                "example": {
                    "route": ["A", "B", "C"],
                    "metrics": {"distance": 10.0, "time": 5.0, "cost": 2.0},
                    "confidence": 0.9
                }
            }
    
    class ModelConfigModel(BaseModel):
        """Modelo validado para configuración de modelo."""
        input_dim: int = Field(..., gt=0, description="Dimensión de entrada")
        hidden_dims: List[int] = Field(..., min_items=1, description="Dimensiones ocultas")
        output_dim: int = Field(..., gt=0, description="Dimensión de salida")
        dropout: float = Field(default=0.2, ge=0.0, le=1.0, description="Tasa de dropout")
        activation: str = Field(default="relu", description="Función de activación")
        use_batch_norm: bool = Field(default=True, description="Usar batch normalization")
        
        @validator('hidden_dims')
        def validate_hidden_dims(cls, v):
            if any(d <= 0 for d in v):
                raise ValueError("Dimensiones ocultas deben ser positivas")
            return v
        
        class Config:
            json_schema_extra = {
                "example": {
                    "input_dim": 20,
                    "hidden_dims": [128, 256, 128],
                    "output_dim": 4,
                    "dropout": 0.2
                }
            }
    
    class TrainingConfigModel(BaseModel):
        """Modelo validado para configuración de entrenamiento."""
        epochs: int = Field(..., gt=0, description="Número de épocas")
        batch_size: int = Field(..., gt=0, description="Tamaño de batch")
        learning_rate: float = Field(..., gt=0.0, description="Learning rate")
        weight_decay: float = Field(default=1e-5, ge=0.0, description="Weight decay")
        optimizer: str = Field(default="adam", description="Optimizador")
        scheduler: Optional[str] = Field(default=None, description="Scheduler")
        early_stopping_patience: Optional[int] = Field(default=None, description="Patience para early stopping")
        use_mixed_precision: bool = Field(default=True, description="Usar mixed precision")
        
        @validator('optimizer')
        def validate_optimizer(cls, v):
            allowed = ["adam", "adamw", "sgd", "rmsprop"]
            if not v.lower() in allowed:
                raise ValueError(f"Optimizador '{v}' no permitido. Permitidos: {allowed}")
            return v.lower()
        
        class Config:
            json_schema_extra = {
                "example": {
                    "epochs": 100,
                    "batch_size": 32,
                    "learning_rate": 1e-3,
                    "optimizer": "adamw"
                }
            }
    
    class ValidationResult(BaseModel):
        """Resultado de validación."""
        is_valid: bool
        errors: List[str] = Field(default_factory=list)
        warnings: List[str] = Field(default_factory=list)
        data: Optional[Dict[str, Any]] = None
        
        class Config:
            json_schema_extra = {
                "example": {
                    "is_valid": True,
                    "errors": [],
                    "warnings": []
                }
            }
    
    def validate_route_request(data: Dict[str, Any]) -> ValidationResult:
        """
        Validar request de ruta.
        
        Args:
            data: Datos del request
            
        Returns:
            Resultado de validación
        """
        try:
            model = RouteRequestModel(**data)
            return ValidationResult(
                is_valid=True,
                data=model.dict()
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[str(e)]
            )
    
    def validate_route_response(data: Dict[str, Any]) -> ValidationResult:
        """
        Validar response de ruta.
        
        Args:
            data: Datos del response
            
        Returns:
            Resultado de validación
        """
        try:
            model = RouteResponseModel(**data)
            return ValidationResult(
                is_valid=True,
                data=model.dict()
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[str(e)]
            )

else:
    # Fallback sin Pydantic
    class RouteRequestModel:
        def __init__(self, **kwargs):
            self.start_node = kwargs.get('start_node', '')
            self.end_node = kwargs.get('end_node', '')
            self.strategy = kwargs.get('strategy', 'shortest_path')
            self.constraints = kwargs.get('constraints')
            self.metadata = kwargs.get('metadata')
        
        def dict(self):
            return {
                'start_node': self.start_node,
                'end_node': self.end_node,
                'strategy': self.strategy,
                'constraints': self.constraints,
                'metadata': self.metadata
            }
    
    class RouteResponseModel:
        def __init__(self, **kwargs):
            self.route = kwargs.get('route', [])
            self.metrics = kwargs.get('metrics', {})
            self.confidence = kwargs.get('confidence', 1.0)
            self.metadata = kwargs.get('metadata')
        
        def dict(self):
            return {
                'route': self.route,
                'metrics': self.metrics,
                'confidence': self.confidence,
                'metadata': self.metadata
            }
    
    def validate_route_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validación básica sin Pydantic."""
        if not data.get('start_node') or not data.get('end_node'):
            return {'is_valid': False, 'errors': ['start_node y end_node son requeridos']}
        return {'is_valid': True, 'data': data}
    
    def validate_route_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validación básica sin Pydantic."""
        if not data.get('route') or len(data.get('route', [])) < 2:
            return {'is_valid': False, 'errors': ['route debe tener al menos 2 nodos']}
        return {'is_valid': True, 'data': data}

