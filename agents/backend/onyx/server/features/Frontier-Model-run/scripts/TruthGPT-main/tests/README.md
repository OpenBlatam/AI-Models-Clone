# TruthGPT Test Suite

## Descripción
Suite completa de tests para TruthGPT con 189+ tests organizados en 11 módulos.

## Estructura

```
tests/
├── __init__.py
├── conftest.py              # Configuración pytest
├── test_utils.py            # Utilidades compartidas
├── test_helpers.py          # Helpers y decoradores
├── test_core.py             # Tests de componentes core (13 tests)
├── test_optimization.py    # Tests de optimización (24 tests)
├── test_models.py           # Tests de modelos (18 tests)
├── test_training.py         # Tests de entrenamiento (23 tests)
├── test_inference.py        # Tests de inferencia (26 tests)
├── test_monitoring.py        # Tests de monitoreo (24 tests)
├── test_integration.py      # Tests de integración (9 tests)
├── test_edge_cases.py       # Tests de casos límite (18 tests)
├── test_performance.py      # Tests de rendimiento (10 tests)
├── test_security.py         # Tests de seguridad (10 tests)
└── test_compatibility.py    # Tests de compatibilidad (12 tests)
```

## Categorías de Tests

### Core Components
Tests básicos de inicialización y configuración.
```bash
python run_unified_tests.py core
```

### Optimization
Tests del motor de optimización.
```bash
python run_unified_tests.py optimization
```

### Models
Tests de gestión de modelos.
```bash
python run_unified_tests.py models
```

### Training
Tests del sistema de entrenamiento.
```bash
python run_unified_tests.py training
```

### Inference
Tests del motor de inferencia.
```bash
python run_unified_tests.py inference
```

### Monitoring
Tests del sistema de monitoreo.
```bash
python run_unified_tests.py monitoring
```

### Integration
Tests de integración end-to-end.
```bash
python run_unified_tests.py integration
```

### Edge Cases
Tests de casos límite y estrés.
```bash
python run_unified_tests.py edge
```

### Performance
Tests de rendimiento y benchmarks.
```bash
python run_unified_tests.py performance
```

### Security
Tests de seguridad y validación.
```bash
python run_unified_tests.py security
```

### Compatibility
Tests de compatibilidad multiplataforma.
```bash
python run_unified_tests.py compatibility
```

## Ejecutar Tests

### Todos los Tests
```bash
python run_unified_tests.py
```

### Categoría Específica
```bash
python run_unified_tests.py <categoria>
```

### Con Opciones Avanzadas
```bash
python run_tests_improved.py all --verbose --save-report
```

## Utilidades

### test_utils.py
Funciones utilitarias compartidas:
- `create_test_model()` - Crear modelos de prueba
- `create_test_dataset()` - Crear datasets de prueba
- `create_test_tokenizer()` - Crear tokenizers de prueba
- `assert_model_valid()` - Validar modelos
- `TestTimer` - Medir tiempo de ejecución

### test_helpers.py
Decoradores y helpers:
- `@retry_on_failure` - Reintentar tests
- `@skip_if_no_cuda` - Saltar si no hay CUDA
- `@performance_test` - Validar rendimiento
- `@memory_profiler` - Perfilar memoria

## Estadísticas

- **Total de Tests**: 189+
- **Archivos de Test**: 11
- **Categorías**: 9
- **Utilidades**: 30+
- **Cobertura**: Alta

## Mejores Prácticas

1. **Usar utilidades compartidas**: Usa `test_utils` para código común
2. **Decoradores útiles**: Aprovecha los decoradores de `test_helpers`
3. **Validaciones robustas**: Usa `assert_model_valid()` y similares
4. **Logging**: Usa `logger.info()` para mensajes informativos
5. **Cleanup**: Limpia recursos en `tearDown()` si es necesario

## Troubleshooting

### Import Errors
Asegúrate de ejecutar desde el directorio `TruthGPT-main`:
```bash
cd TruthGPT-main
python run_unified_tests.py
```

### Dependencies Missing
Instala dependencias:
```bash
pip install torch numpy psutil
```

### CUDA Tests Failing
Algunos tests requieren CUDA. Se saltan automáticamente si no está disponible.

## Contribuir

Al agregar nuevos tests:
1. Usa las utilidades de `test_utils.py`
2. Sigue el formato de tests existentes
3. Agrega logging informativo
4. Actualiza este README si agregas nuevas categorías








