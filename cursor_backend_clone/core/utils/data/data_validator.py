"""
Data Validator - Validador de Datos Avanzado
============================================

Sistema avanzado de validación de datos con múltiples reglas y tipos.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Regla de validación"""
    name: str
    validator: Callable[[Any], bool]
    error_message: str
    required: bool = False


@dataclass
class ValidationResult:
    """Resultado de validación"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validated_data: Optional[Any] = None


class DataValidator:
    """
    Validador de datos avanzado.
    
    Permite definir múltiples reglas de validación.
    """
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.transformers: List[Callable[[Any], Any]] = []
    
    def add_rule(
        self,
        name: str,
        validator: Callable[[Any], bool],
        error_message: str,
        required: bool = False
    ) -> None:
        """
        Agregar regla de validación.
        
        Args:
            name: Nombre de la regla
            validator: Función validadora
            error_message: Mensaje de error
            required: Si es requerida
        """
        rule = ValidationRule(
            name=name,
            validator=validator,
            error_message=error_message,
            required=required
        )
        self.rules.append(rule)
        logger.debug(f"✅ Validation rule added: {name}")
    
    def add_transformer(self, transformer: Callable[[Any], Any]) -> None:
        """
        Agregar transformador de datos.
        
        Args:
            transformer: Función transformadora
        """
        self.transformers.append(transformer)
    
    def validate(self, data: Any) -> ValidationResult:
        """
        Validar datos contra todas las reglas.
        
        Args:
            data: Datos a validar
            
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        # Aplicar transformadores
        transformed_data = data
        for transformer in self.transformers:
            try:
                transformed_data = transformer(transformed_data)
            except Exception as e:
                result.warnings.append(f"Transformer failed: {e}")
        
        # Validar con reglas
        for rule in self.rules:
            try:
                if not rule.validator(transformed_data):
                    result.is_valid = False
                    result.errors.append(rule.error_message)
            except Exception as e:
                result.is_valid = False
                result.errors.append(f"Validation error in {rule.name}: {e}")
        
        if result.is_valid:
            result.validated_data = transformed_data
        
        return result


# Validadores predefinidos
def validate_not_empty(value: Any) -> bool:
    """Validar que no esté vacío"""
    if value is None:
        return False
    if isinstance(value, str):
        return len(value.strip()) > 0
    if isinstance(value, (list, dict, set, tuple)):
        return len(value) > 0
    return True


def validate_length(value: Any, min_len: Optional[int] = None, max_len: Optional[int] = None) -> bool:
    """Validar longitud"""
    if not isinstance(value, (str, list, dict, set, tuple)):
        return False
    
    length = len(value)
    
    if min_len is not None and length < min_len:
        return False
    
    if max_len is not None and length > max_len:
        return False
    
    return True


def validate_range(value: Union[int, float], min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
    """Validar rango numérico"""
    if not isinstance(value, (int, float)):
        return False
    
    if min_val is not None and value < min_val:
        return False
    
    if max_val is not None and value > max_val:
        return False
    
    return True


def validate_pattern(value: str, pattern: str) -> bool:
    """Validar patrón regex"""
    if not isinstance(value, str):
        return False
    
    try:
        return bool(re.match(pattern, value))
    except re.error:
        return False


def validate_email(value: str) -> bool:
    """Validar email"""
    if not isinstance(value, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, value))


def validate_url(value: str) -> bool:
    """Validar URL"""
    if not isinstance(value, str):
        return False
    
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, value))


def validate_datetime_string(value: str, format: Optional[str] = None) -> bool:
    """Validar string de datetime"""
    if not isinstance(value, str):
        return False
    
    try:
        if format:
            datetime.strptime(value, format)
        else:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError):
        return False


def validate_in_list(value: Any, allowed_values: List[Any]) -> bool:
    """Validar que esté en lista"""
    return value in allowed_values


def validate_type(value: Any, expected_type: type) -> bool:
    """Validar tipo"""
    return isinstance(value, expected_type)


def validate_dict_structure(value: Dict[str, Any], required_keys: List[str]) -> bool:
    """Validar estructura de diccionario"""
    if not isinstance(value, dict):
        return False
    
    return all(key in value for key in required_keys)




