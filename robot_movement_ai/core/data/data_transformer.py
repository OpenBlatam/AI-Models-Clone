"""
Data Transformer System
=======================

Sistema de transformación de datos.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TransformationRule:
    """Regla de transformación."""
    rule_id: str
    name: str
    transformer: Callable[[Any], Any]
    input_type: Optional[type] = None
    output_type: Optional[type] = None
    enabled: bool = True


class DataTransformer:
    """
    Transformador de datos.
    
    Transforma datos usando reglas configurables.
    """
    
    def __init__(self):
        """Inicializar transformador."""
        self.rules: Dict[str, TransformationRule] = {}
        self.transformation_history: List[Dict[str, Any]] = []
    
    def add_rule(
        self,
        rule_id: str,
        name: str,
        transformer: Callable[[Any], Any],
        input_type: Optional[type] = None,
        output_type: Optional[type] = None,
        enabled: bool = True
    ) -> TransformationRule:
        """
        Agregar regla de transformación.
        
        Args:
            rule_id: ID único de la regla
            name: Nombre de la regla
            transformer: Función transformadora
            input_type: Tipo de entrada (opcional)
            output_type: Tipo de salida (opcional)
            enabled: Si está habilitada
            
        Returns:
            Regla creada
        """
        rule = TransformationRule(
            rule_id=rule_id,
            name=name,
            transformer=transformer,
            input_type=input_type,
            output_type=output_type,
            enabled=enabled
        )
        
        self.rules[rule_id] = rule
        logger.info(f"Added transformation rule: {name} ({rule_id})")
        
        return rule
    
    def transform(
        self,
        data: Any,
        rule_id: Optional[str] = None,
        chain: Optional[List[str]] = None
    ) -> Any:
        """
        Transformar datos.
        
        Args:
            data: Datos a transformar
            rule_id: ID de regla única (opcional)
            chain: Cadena de reglas a aplicar (opcional)
            
        Returns:
            Datos transformados
        """
        if rule_id:
            # Aplicar regla única
            if rule_id not in self.rules:
                raise ValueError(f"Transformation rule not found: {rule_id}")
            
            rule = self.rules[rule_id]
            if not rule.enabled:
                return data
            
            try:
                result = rule.transformer(data)
                self._record_transformation(rule_id, data, result)
                return result
            except Exception as e:
                logger.error(f"Error in transformation {rule_id}: {e}")
                raise
        
        elif chain:
            # Aplicar cadena de transformaciones
            result = data
            for rule_id in chain:
                if rule_id not in self.rules:
                    logger.warning(f"Rule not found: {rule_id}, skipping")
                    continue
                
                rule = self.rules[rule_id]
                if not rule.enabled:
                    continue
                
                try:
                    result = rule.transformer(result)
                    self._record_transformation(rule_id, data, result)
                except Exception as e:
                    logger.error(f"Error in transformation {rule_id}: {e}")
                    raise
            
            return result
        
        else:
            raise ValueError("Either rule_id or chain must be provided")
    
    def _record_transformation(self, rule_id: str, input_data: Any, output_data: Any) -> None:
        """Registrar transformación."""
        self.transformation_history.append({
            "rule_id": rule_id,
            "input_type": type(input_data).__name__,
            "output_type": type(output_data).__name__,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
    
    def get_transformation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener historial de transformaciones."""
        return self.transformation_history[-limit:]


# Instancia global
_data_transformer: Optional[DataTransformer] = None


def get_data_transformer() -> DataTransformer:
    """Obtener instancia global del transformador de datos."""
    global _data_transformer
    if _data_transformer is None:
        _data_transformer = DataTransformer()
    return _data_transformer






