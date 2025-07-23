"""
🛡️ GUARD CLAUSES & EARLY VALIDATION EXAMPLES
============================================

Ejemplos prácticos de guard clauses y validación temprana en el AI Video System.
Demuestra el principio "fail fast" con validación al inicio de funciones.
"""

import asyncio
import time
import numpy as np
from pathlib import Path
import logging
from typing import Dict, Any, List, Optional, Tuple

from .guard_clauses import (
    guard_validation, guard_resources, guard_state,
    ValidationGuards, ResourceGuards, StateGuards,
    BoundaryGuards, SanityGuards, GuardClauseManager,
    fail_fast, require_not_none, require_not_empty,
    require_file_exists, require_valid_range,
    guard_context, resource_guard_context,
    get_guard_manager
)

from .early_validation import (
    early_validate, ValidationSchema, ValidationRule,
    ValidationType, ValidationLevel,
    TypeValidators, RangeValidators, FormatValidators,
    ExistenceValidators, SizeValidators, ContentValidators,
    RelationshipValidators, create_video_validation_schema,
    create_model_validation_schema, create_data_validation_schema
)

from .error_handling import (
    ValidationError, MemoryError, SystemError,
    ModelLoadingError, VideoProcessingError, DataValidationError
)

# =============================================================================
# GUARD CLAUSE EXAMPLES
# =============================================================================

# Ejemplo 1: Función con múltiples guard clauses
@guard_validation([
    lambda model_path, **kwargs: ValidationGuards.validate_file_exists(model_path),
    lambda batch_size, **kwargs: ValidationGuards.validate_batch_size(batch_size, 32)
])
@guard_resources(required_memory_mb=2048.0, max_cpu_percent=90.0)
def load_and_process_model(model_path: str, batch_size: int = 8) -> Dict[str, Any]:
    """
    Cargar y procesar modelo con guard clauses.
    
    Guard clauses aplicadas:
    - Validación: archivo existe, batch size válido
    - Recursos: memoria disponible, CPU no sobrecargado
    """
    # El código principal solo se ejecuta si todas las validaciones pasan
    print(f"✅ Cargando modelo: {model_path}")
    print(f"✅ Procesando con batch size: {batch_size}")
    
    # Simular carga de modelo
    time.sleep(1)
    
    return {
        "model_path": model_path,
        "batch_size": batch_size,
        "loaded": True,
        "parameters": 1000000
    }

# Ejemplo 2: Función con guard clauses de estado
def check_system_ready() -> bool:
    """Verificar que el sistema esté listo."""
    return True  # Simular sistema listo

@guard_state(
    state_checker=check_system_ready,
    error_message="Sistema no está listo para procesamiento"
)
def process_video_pipeline(video_path: str) -> Dict[str, Any]:
    """
    Procesar pipeline de video con verificación de estado.
    
    Guard clauses aplicadas:
    - Estado: sistema debe estar listo
    """
    print(f"✅ Procesando video: {video_path}")
    
    # Simular procesamiento
    time.sleep(2)
    
    return {
        "video_path": video_path,
        "processed": True,
        "duration": 30.0
    }

# Ejemplo 3: Función con guard clauses personalizadas
def validate_video_dimensions(width: int, height: int) -> bool:
    """Validar dimensiones de video."""
    return 64 <= width <= 4096 and 64 <= height <= 4096

@guard_validation([
    lambda video_data, **kwargs: ValidationGuards.validate_video_data(video_data),
    lambda width, height, **kwargs: validate_video_dimensions(width, height)
])
def process_video_frames(video_data: np.ndarray, width: int, height: int) -> np.ndarray:
    """
    Procesar frames de video con validación de dimensiones.
    
    Guard clauses aplicadas:
    - Validación: datos de video válidos, dimensiones razonables
    """
    print(f"✅ Procesando frames: {video_data.shape}")
    print(f"✅ Dimensiones: {width}x{height}")
    
    # Simular procesamiento
    processed_data = video_data * 1.1
    time.sleep(1)
    
    return processed_data

# =============================================================================
# EARLY VALIDATION EXAMPLES
# =============================================================================

# Ejemplo 4: Función con validación temprana usando esquema
video_schema = create_video_validation_schema()

@video_schema.to_decorator()
def process_video_file(video_path: str, batch_size: int = 8) -> Dict[str, Any]:
    """
    Procesar archivo de video con validación temprana.
    
    Validaciones aplicadas:
    - Archivo existe
    - Formato de video válido
    - Batch size en rango válido
    """
    print(f"✅ Archivo válido: {video_path}")
    print(f"✅ Batch size válido: {batch_size}")
    
    # Simular procesamiento
    time.sleep(1)
    
    return {
        "video_path": video_path,
        "batch_size": batch_size,
        "processed": True
    }

# Ejemplo 5: Función con validación temprana personalizada
@early_validate({
    "model_path": ValidationRule(
        name="model_exists",
        validation_type=ValidationType.EXISTENCE,
        validator=ExistenceValidators.file_exists,
        error_message="Modelo '{field}' no existe",
        required=True
    ),
    "model_config": ValidationRule(
        name="config_valid",
        validation_type=ValidationType.CONTENT,
        validator=lambda x: ContentValidators.required_keys(x, {"model_type", "batch_size"}),
        error_message="Configuración '{field}' debe contener 'model_type' y 'batch_size'",
        required=True
    ),
    "learning_rate": ValidationRule(
        name="lr_range",
        validation_type=ValidationType.RANGE,
        validator=lambda x: RangeValidators.between_zero_one(x),
        error_message="Learning rate '{field}' debe estar entre 0 y 1",
        required=True
    )
})
def train_model(model_path: str, model_config: Dict[str, Any], learning_rate: float) -> Dict[str, Any]:
    """
    Entrenar modelo con validación temprana completa.
    
    Validaciones aplicadas:
    - Modelo existe
    - Configuración válida
    - Learning rate en rango válido
    """
    print(f"✅ Modelo válido: {model_path}")
    print(f"✅ Configuración válida: {model_config}")
    print(f"✅ Learning rate válido: {learning_rate}")
    
    # Simular entrenamiento
    time.sleep(2)
    
    return {
        "model_path": model_path,
        "config": model_config,
        "learning_rate": learning_rate,
        "trained": True
    }

# Ejemplo 6: Función con validación de datos NumPy
@early_validate({
    "data": ValidationRule(
        name="data_type",
        validation_type=ValidationType.TYPE,
        validator=TypeValidators.is_numpy_array,
        error_message="Datos '{field}' deben ser array de NumPy",
        required=True
    ),
    "data": ValidationRule(
        name="data_content",
        validation_type=ValidationType.CONTENT,
        validator=ContentValidators.no_nan_values,
        error_message="Datos '{field}' no pueden contener valores NaN",
        required=True
    ),
    "data": ValidationRule(
        name="data_range",
        validation_type=ValidationType.CONTENT,
        validator=lambda x: ContentValidators.in_range_values(x, 0.0, 1.0),
        error_message="Datos '{field}' deben estar en rango [0, 1]",
        required=True
    )
})
def normalize_data(data: np.ndarray) -> np.ndarray:
    """
    Normalizar datos con validación temprana.
    
    Validaciones aplicadas:
    - Tipo NumPy array
    - Sin valores NaN
    - Valores en rango [0, 1]
    """
    print(f"✅ Datos válidos: {data.shape}")
    
    # Simular normalización
    normalized = data / np.max(data)
    time.sleep(0.5)
    
    return normalized

# =============================================================================
# FAIL FAST EXAMPLES
# =============================================================================

# Ejemplo 7: Función con fail fast manual
def process_batch_data(batch_data: List[np.ndarray], batch_size: int) -> np.ndarray:
    """
    Procesar datos en batch con fail fast manual.
    
    Fail fast aplicado:
    - Verificaciones al inicio de la función
    """
    # Fail fast: verificar entrada
    fail_fast(batch_data is not None, "batch_data no puede ser None")
    fail_fast(len(batch_data) > 0, "batch_data no puede estar vacío")
    fail_fast(batch_size > 0, "batch_size debe ser positivo")
    fail_fast(len(batch_data) == batch_size, f"batch_data debe tener {batch_size} elementos")
    
    # Fail fast: verificar cada elemento
    for i, data in enumerate(batch_data):
        fail_fast(isinstance(data, np.ndarray), f"Elemento {i} debe ser NumPy array")
        fail_fast(data.size > 0, f"Elemento {i} no puede estar vacío")
    
    print(f"✅ Procesando batch válido: {len(batch_data)} elementos")
    
    # Simular procesamiento
    result = np.concatenate(batch_data, axis=0)
    time.sleep(1)
    
    return result

# Ejemplo 8: Función con require_* helpers
def create_video_metadata(video_path: str, duration: float, fps: int) -> Dict[str, Any]:
    """
    Crear metadata de video con require_* helpers.
    
    Require helpers aplicados:
    - require_file_exists
    - require_valid_range
    """
    # Require helpers al inicio
    require_file_exists(video_path, "video_path")
    require_valid_range(duration, 0.1, 3600.0, "duration")  # 0.1s a 1h
    require_valid_range(fps, 1, 120, "fps")  # 1 a 120 fps
    
    print(f"✅ Creando metadata para: {video_path}")
    print(f"✅ Duración: {duration}s, FPS: {fps}")
    
    # Simular creación de metadata
    time.sleep(0.5)
    
    return {
        "video_path": video_path,
        "duration": duration,
        "fps": fps,
        "created": True
    }

# =============================================================================
# CONTEXT MANAGER EXAMPLES
# =============================================================================

# Ejemplo 9: Función con guard context
def process_with_guard_context(video_path: str) -> Dict[str, Any]:
    """
    Procesar con guard context manager.
    
    Guard context aplicado:
    - Verificación de estado del sistema
    """
    guard_manager = get_guard_manager()
    
    with guard_context(guard_manager, "video_processing"):
        print(f"✅ Sistema listo para procesar: {video_path}")
        
        # Simular procesamiento
        time.sleep(2)
        
        return {
            "video_path": video_path,
            "processed": True,
            "status": "success"
        }

# Ejemplo 10: Función con resource guard context
def memory_intensive_processing(data: np.ndarray) -> np.ndarray:
    """
    Procesamiento intensivo en memoria con resource guard.
    
    Resource guard aplicado:
    - Verificación de memoria disponible
    - Limpieza automática al final
    """
    with resource_guard_context(required_memory_mb=1024.0):
        print(f"✅ Memoria disponible para procesar: {data.shape}")
        
        # Simular procesamiento intensivo
        result = data * 2.0
        time.sleep(1)
        
        return result

# =============================================================================
# ASYNC EXAMPLES
# =============================================================================

# Ejemplo 11: Función async con guard clauses
@guard_validation([
    lambda video_path, **kwargs: ValidationGuards.validate_file_exists(video_path),
    lambda quality, **kwargs: RangeValidators.between_zero_one(quality)
])
async def async_process_video(video_path: str, quality: float = 0.8) -> Dict[str, Any]:
    """
    Procesar video de forma asíncrona con guard clauses.
    
    Guard clauses aplicadas:
    - Archivo existe
    - Calidad en rango [0, 1]
    """
    print(f"✅ Procesando video async: {video_path}")
    print(f"✅ Calidad: {quality}")
    
    # Simular procesamiento asíncrono
    await asyncio.sleep(2)
    
    return {
        "video_path": video_path,
        "quality": quality,
        "processed": True
    }

# Ejemplo 12: Función async con early validation
@early_validate({
    "model_path": ValidationRule(
        name="model_exists",
        validation_type=ValidationType.EXISTENCE,
        validator=ExistenceValidators.file_exists,
        error_message="Modelo '{field}' no existe",
        required=True
    ),
    "batch_size": ValidationRule(
        name="batch_size_range",
        validation_type=ValidationType.RANGE,
        validator=lambda x: RangeValidators.in_range(x, 1, 64),
        error_message="Batch size '{field}' debe estar entre 1 y 64",
        required=True
    )
})
async def async_load_model(model_path: str, batch_size: int = 16) -> Dict[str, Any]:
    """
    Cargar modelo de forma asíncrona con validación temprana.
    
    Validaciones aplicadas:
    - Modelo existe
    - Batch size en rango válido
    """
    print(f"✅ Cargando modelo async: {model_path}")
    print(f"✅ Batch size: {batch_size}")
    
    # Simular carga asíncrona
    await asyncio.sleep(1)
    
    return {
        "model_path": model_path,
        "batch_size": batch_size,
        "loaded": True
    }

# =============================================================================
# COMPLEX EXAMPLES
# =============================================================================

# Ejemplo 13: Pipeline completo con múltiples guard clauses
class VideoProcessingPipeline:
    """Pipeline de procesamiento de video con guard clauses."""
    
    def __init__(self):
        self.guard_manager = get_guard_manager()
        self.state_guards = StateGuards()
        self.state_guards.set_initialized(True)
    
    @guard_validation([
        lambda video_path, **kwargs: ValidationGuards.validate_file_exists(video_path),
        lambda video_path, **kwargs: ValidationGuards.validate_video_format(video_path),
        lambda batch_size, **kwargs: ValidationGuards.validate_batch_size(batch_size, 16)
    ])
    @guard_resources(required_memory_mb=2048.0, max_cpu_percent=85.0)
    def process_video(self, video_path: str, batch_size: int = 8) -> Dict[str, Any]:
        """
        Procesar video con pipeline completo.
        
        Guard clauses aplicadas:
        - Validación: archivo existe, formato válido, batch size válido
        - Recursos: memoria disponible, CPU no sobrecargado
        """
        print(f"🚀 Iniciando pipeline para: {video_path}")
        
        # Paso 1: Cargar video
        video_data = self._load_video(video_path)
        
        # Paso 2: Procesar frames
        processed_data = self._process_frames(video_data, batch_size)
        
        # Paso 3: Guardar resultado
        output_path = self._save_result(processed_data, video_path)
        
        return {
            "input_path": video_path,
            "output_path": output_path,
            "batch_size": batch_size,
            "processed": True
        }
    
    def _load_video(self, video_path: str) -> np.ndarray:
        """Cargar video con validación."""
        require_file_exists(video_path, "video_path")
        print(f"📹 Cargando video: {video_path}")
        
        # Simular carga
        time.sleep(1)
        return np.random.rand(100, 256, 256, 3)
    
    def _process_frames(self, video_data: np.ndarray, batch_size: int) -> np.ndarray:
        """Procesar frames con validación."""
        fail_fast(isinstance(video_data, np.ndarray), "video_data debe ser NumPy array")
        fail_fast(video_data.size > 0, "video_data no puede estar vacío")
        fail_fast(batch_size > 0, "batch_size debe ser positivo")
        
        print(f"⚙️ Procesando {len(video_data)} frames con batch size {batch_size}")
        
        # Simular procesamiento
        time.sleep(2)
        return video_data * 1.1
    
    def _save_result(self, processed_data: np.ndarray, original_path: str) -> str:
        """Guardar resultado con validación."""
        fail_fast(isinstance(processed_data, np.ndarray), "processed_data debe ser NumPy array")
        fail_fast(processed_data.size > 0, "processed_data no puede estar vacío")
        
        output_path = str(Path(original_path).with_suffix('.processed.mp4'))
        print(f"💾 Guardando resultado: {output_path}")
        
        # Simular guardado
        time.sleep(1)
        return output_path

# Ejemplo 14: Función con validación de esquema personalizado
def create_custom_validation_schema() -> ValidationSchema:
    """Crear esquema de validación personalizado."""
    schema = ValidationSchema("custom_validation")
    
    # Validar entrada de usuario
    schema.add_rule("user_input", ValidationRule(
        name="user_input_not_empty",
        validation_type=ValidationType.EXISTENCE,
        validator=ExistenceValidators.not_empty,
        error_message="Entrada de usuario '{field}' no puede estar vacía",
        required=True
    ))
    
    schema.add_rule("user_input", ValidationRule(
        name="user_input_length",
        validation_type=ValidationType.SIZE,
        validator=lambda x: SizeValidators.string_length(x, 1, 1000),
        error_message="Entrada de usuario '{field}' debe tener entre 1 y 1000 caracteres",
        required=True
    ))
    
    # Validar configuración
    schema.add_rule("config", ValidationRule(
        name="config_dict",
        validation_type=ValidationType.TYPE,
        validator=TypeValidators.is_dict,
        error_message="Configuración '{field}' debe ser diccionario",
        required=True
    ))
    
    schema.add_rule("config", ValidationRule(
        name="config_required_keys",
        validation_type=ValidationType.CONTENT,
        validator=lambda x: ContentValidators.required_keys(x, {"mode", "quality"}),
        error_message="Configuración '{field}' debe contener 'mode' y 'quality'",
        required=True
    ))
    
    return schema

custom_schema = create_custom_validation_schema()

@custom_schema.to_decorator()
def process_user_request(user_input: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesar solicitud de usuario con validación personalizada.
    
    Validaciones aplicadas:
    - Entrada de usuario no vacía y longitud válida
    - Configuración válida con campos requeridos
    """
    print(f"✅ Procesando solicitud: {user_input[:50]}...")
    print(f"✅ Configuración: {config}")
    
    # Simular procesamiento
    time.sleep(1)
    
    return {
        "user_input": user_input,
        "config": config,
        "processed": True,
        "result": "success"
    }

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def run_guard_clause_examples():
    """Ejecutar ejemplos de guard clauses."""
    print("🛡️ Ejecutando ejemplos de guard clauses...")
    
    # Ejemplo 1: Guard clauses básicas
    try:
        result = load_and_process_model("model.pt", batch_size=16)
        print(f"✅ Resultado: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Ejemplo 2: Guard clauses de estado
    try:
        result = process_video_pipeline("video.mp4")
        print(f"✅ Resultado: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Ejemplo 3: Guard clauses personalizadas
    try:
        video_data = np.random.rand(10, 256, 256, 3)
        result = process_video_frames(video_data, width=256, height=256)
        print(f"✅ Resultado: {result.shape}")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_early_validation_examples():
    """Ejecutar ejemplos de validación temprana."""
    print("⚡ Ejecutando ejemplos de validación temprana...")
    
    # Ejemplo 4: Validación con esquema
    try:
        result = process_video_file("video.mp4", batch_size=8)
        print(f"✅ Resultado: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Ejemplo 5: Validación personalizada
    try:
        config = {"model_type": "diffusion", "batch_size": 16}
        result = train_model("model.pt", config, learning_rate=0.001)
        print(f"✅ Resultado: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Ejemplo 6: Validación de datos
    try:
        data = np.random.rand(100, 256, 256, 3)
        result = normalize_data(data)
        print(f"✅ Resultado: {result.shape}")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_fail_fast_examples():
    """Ejecutar ejemplos de fail fast."""
    print("🚨 Ejecutando ejemplos de fail fast...")
    
    # Ejemplo 7: Fail fast manual
    try:
        batch_data = [np.random.rand(10, 10) for _ in range(4)]
        result = process_batch_data(batch_data, batch_size=4)
        print(f"✅ Resultado: {result.shape}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Ejemplo 8: Require helpers
    try:
        result = create_video_metadata("video.mp4", duration=30.0, fps=30)
        print(f"✅ Resultado: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")

async def run_async_examples():
    """Ejecutar ejemplos asíncronos."""
    print("🔄 Ejecutando ejemplos asíncronos...")
    
    # Ejemplo 11: Async con guard clauses
    try:
        result = await async_process_video("video.mp4", quality=0.9)
        print(f"✅ Resultado: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Ejemplo 12: Async con validación temprana
    try:
        result = await async_load_model("model.pt", batch_size=32)
        print(f"✅ Resultado: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_complex_examples():
    """Ejecutar ejemplos complejos."""
    print("🏗️ Ejecutando ejemplos complejos...")
    
    # Ejemplo 13: Pipeline completo
    try:
        pipeline = VideoProcessingPipeline()
        result = pipeline.process_video("video.mp4", batch_size=8)
        print(f"✅ Pipeline completado: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Ejemplo 14: Validación personalizada
    try:
        config = {"mode": "fast", "quality": 0.8}
        result = process_user_request("Procesar video con alta calidad", config)
        print(f"✅ Solicitud procesada: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Ejecutar todos los ejemplos
    run_guard_clause_examples()
    run_early_validation_examples()
    run_fail_fast_examples()
    
    # Ejecutar ejemplos asíncronos
    asyncio.run(run_async_examples())
    
    # Ejecutar ejemplos complejos
    run_complex_examples() 