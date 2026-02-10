"""
Data Validator System
=====================

Sistema de validación de datos avanzado.
"""

import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationType(Enum):
    """Tipo de validación."""
    REQUIRED = "required"
    TYPE = "type"
    RANGE = "range"
    PATTERN = "pattern"
    CUSTOM = "custom"


@dataclass
class ValidationRule:
    """Regla de validación."""
    field_name: str
    validation_type: ValidationType
    validator: Callable[[Any], bool]
    error_message: str
    required: bool = True


@dataclass
class ValidationResult:
    """Resultado de validación."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validated_data: Optional[Dict[str, Any]] = None


class DataValidator:
    """
    Validador de datos.
    
    Valida datos con reglas configurables.
    """
    
    def __init__(self):
        """Inicializar validador."""
        self.rules: Dict[str, List[ValidationRule]] = {}
        self.validation_history: List[Dict[str, Any]] = []
    
    def add_rule(
        self,
        schema_name: str,
        field_name: str,
        validation_type: ValidationType,
        validator: Callable[[Any], bool],
        error_message: str,
        required: bool = True
    ) -> ValidationRule:
        """
        Agregar regla de validación.
        
        Args:
            schema_name: Nombre del esquema
            field_name: Nombre del campo
            validation_type: Tipo de validación
            validator: Función validadora
            error_message: Mensaje de error
            required: Si es requerido
            
        Returns:
            Regla creada
        """
        if schema_name not in self.rules:
            self.rules[schema_name] = []
        
        rule = ValidationRule(
            field_name=field_name,
            validation_type=validation_type,
            validator=validator,
            error_message=error_message,
            required=required
        )
        
        self.rules[schema_name].append(rule)
        logger.info(f"Added validation rule: {schema_name}.{field_name}")
        
        return rule
    
    def validate(
        self,
        schema_name: str,
        data: Dict[str, Any],
        strict: bool = True
    ) -> ValidationResult:
        """
        Validar datos.
        
        Args:
            schema_name: Nombre del esquema
            data: Datos a validar
            strict: Si es estricto (falla en primer error)
            
        Returns:
            Resultado de validación
        """
        if schema_name not in self.rules:
            return ValidationResult(
                valid=False,
                errors=[f"Schema '{schema_name}' not found"]
            )
        
        errors = []
        warnings = []
        validated_data = {}
        
        for rule in self.rules[schema_name]:
            field_value = data.get(rule.field_name)
            
            # Verificar requerido
            if rule.required and field_value is None:
                errors.append(f"{rule.field_name}: {rule.error_message}")
                if strict:
                    break
                continue
            
            if field_value is not None:
                # Validar valor
                try:
                    if not rule.validator(field_value):
                        errors.append(f"{rule.field_name}: {rule.error_message}")
                        if strict:
                            break
                    else:
                        validated_data[rule.field_name] = field_value
                except Exception as e:
                    errors.append(f"{rule.field_name}: Validation error - {str(e)}")
                    if strict:
                        break
        
        result = ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_data=validated_data if len(errors) == 0 else None
        )
        
        # Registrar en historial
        self.validation_history.append({
            "schema_name": schema_name,
            "valid": result.valid,
            "errors_count": len(errors),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        
        return result
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de validación."""
        if not self.validation_history:
            return {
                "total_validations": 0,
                "success_rate": 0.0
            }
        
        total = len(self.validation_history)
        successful = sum(1 for v in self.validation_history if v["valid"])
        
        return {
            "total_validations": total,
            "successful_validations": successful,
            "failed_validations": total - successful,
            "success_rate": successful / total if total > 0 else 0.0
        }


# Instancia global
_data_validator: Optional[DataValidator] = None


def get_data_validator() -> DataValidator:
    """Obtener instancia global del validador de datos."""
    global _data_validator
    if _data_validator is None:
        _data_validator = DataValidator()
    return _data_validator






