from pydantic import field_validator
from typing import Any

# Validador para campos string no vacíos
def not_empty_string(v: str) -> str:
    if not v.strip():
        raise ValueError("El campo no puede estar vacío")
    return v.strip()

# Validador para listas o listas vacías
def list_or_empty(v: Any):
    return v or []

# Validador para diccionarios o diccionarios vacíos
def dict_or_empty(v: Any):
    return v or {} 