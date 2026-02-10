"""
Data Validators
===============

Validadores de datos funcionales.
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DataValidator:
    """Validador de datos."""
    
    def __init__(self):
        """Inicializar validador."""
        self.validators: Dict[str, List[Callable]] = {}
        self._logger = logger
    
    def register_validator(self, field: str, validator: Callable):
        """
        Registrar validador para campo.
        
        Args:
            field: Nombre del campo
            validator: Función validadora
        """
        if field not in self.validators:
            self.validators[field] = []
        self.validators[field].append(validator)
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validar datos.
        
        Args:
            data: Datos a validar
        
        Returns:
            (es_válido, lista_de_errores)
        """
        errors = []
        
        for field, validators in self.validators.items():
            value = data.get(field)
            
            for validator in validators:
                try:
                    result = validator(value)
                    if isinstance(result, tuple):
                        is_valid, error_msg = result
                        if not is_valid:
                            errors.append(f"{field}: {error_msg}")
                    elif not result:
                        errors.append(f"{field}: Validation failed")
                except Exception as e:
                    errors.append(f"{field}: {str(e)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def required(value: Any) -> tuple[bool, Optional[str]]:
        """Validador de campo requerido."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, "Field is required"
        return True, None
    
    @staticmethod
    def min_length(min_len: int):
        """Validador de longitud mínima."""
        def validator(value: str) -> tuple[bool, Optional[str]]:
            if value and len(value) < min_len:
                return False, f"Must be at least {min_len} characters"
            return True, None
        return validator
    
    @staticmethod
    def max_length(max_len: int):
        """Validador de longitud máxima."""
        def validator(value: str) -> tuple[bool, Optional[str]]:
            if value and len(value) > max_len:
                return False, f"Must be at most {max_len} characters"
            return True, None
        return validator
    
    @staticmethod
    def in_range(min_val: float, max_val: float):
        """Validador de rango numérico."""
        def validator(value: float) -> tuple[bool, Optional[str]]:
            if value is not None and (value < min_val or value > max_val):
                return False, f"Must be between {min_val} and {max_val}"
            return True, None
        return validator




