# Guía de Contribución - Face Swap Modules

## 🤝 Cómo Contribuir

Gracias por tu interés en contribuir a Face Swap Modules. Esta guía te ayudará a hacer contribuciones efectivas.

---

## 📋 Antes de Contribuir

### 1. Revisar Documentación

- ✅ Leer `README.md` para entender el proyecto
- ✅ Revisar `BEST_PRACTICES.md` para estándares de código
- ✅ Ver `ARCHITECTURE_DIAGRAM.md` para entender la estructura
- ✅ Consultar `TROUBLESHOOTING.md` si encuentras problemas

### 2. Verificar Estado

```bash
# Verificar dependencias
python check_dependencies.py

# Validar módulos
python validate_modules.py

# Ejecutar tests
python -m pytest tests/
```

---

## 🔧 Proceso de Contribución

### 1. Fork y Clone

```bash
# Fork el repositorio
# Clone tu fork
git clone <tu-fork-url>
cd face_swap_modules
```

### 2. Crear Rama

```bash
# Crear rama para tu contribución
git checkout -b feature/nueva-funcionalidad
# O
git checkout -b fix/correccion-bug
```

### 3. Desarrollo

#### Seguir Estándares

- ✅ Usar clases base cuando sea apropiado (`BaseDetector`)
- ✅ Usar utilidades centralizadas (`LandmarkFormatHandler`, `ImageProcessor`)
- ✅ Agregar type hints completos
- ✅ Agregar docstrings
- ✅ Seguir nomenclatura consistente
- ✅ Mantener compatibilidad hacia atrás

#### Ejemplo de Código Correcto

```python
from face_swap_modules.base import BaseDetector
from typing import Optional, Tuple
import numpy as np

class CustomDetector(BaseDetector):
    """
    Detector personalizado.
    
    Args:
        param: Descripción del parámetro
    """
    
    def detect(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detecta cara en imagen.
        
        Args:
            image: Imagen de entrada (BGR)
        
        Returns:
            Bounding box (x, y, width, height) o None
        """
        def _detect():
            # Tu lógica aquí
            return bbox
        
        return self._safe_execute(_detect)
```

### 4. Tests

#### Agregar Tests

```python
# tests/test_custom.py
import unittest
from face_swap_modules import CustomDetector
import numpy as np

class TestCustomDetector(unittest.TestCase):
    def setUp(self):
        self.detector = CustomDetector()
        self.test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    def test_detect(self):
        bbox = self.detector.detect(self.test_image)
        # Verificar resultado
        self.assertIsInstance(bbox, (tuple, type(None)))
```

#### Ejecutar Tests

```bash
# Todos los tests
python -m pytest tests/

# Test específico
python -m pytest tests/test_custom.py

# Con cobertura
python -m pytest tests/ --cov=face_swap_modules
```

### 5. Documentación

#### Actualizar Documentación

- ✅ Agregar ejemplos en `USAGE_EXAMPLES.md` si es nueva funcionalidad
- ✅ Actualizar `CHANGELOG.md` con cambios
- ✅ Actualizar `README.md` si es cambio importante
- ✅ Agregar docstrings completos

#### Formato de Changelog

```markdown
## [2.2.0] - 2024-12-XX

### ✨ Agregado
- Nuevo método `custom_detect()` en `CustomDetector`
- Soporte para formato de landmarks de 200 puntos

### 🔄 Cambiado
- Mejora en rendimiento de `detect()` método

### 🐛 Corregido
- Bug en validación de coordenadas
```

### 6. Validación

```bash
# Validar módulos
python validate_modules.py

# Verificar dependencias
python check_dependencies.py

# Generar reporte
python generate_report.py
```

### 7. Commit

#### Mensajes de Commit

```bash
# Formato recomendado
git commit -m "feat: agregar nuevo método de detección"
git commit -m "fix: corregir validación de landmarks"
git commit -m "docs: actualizar ejemplos de uso"
git commit -m "refactor: mejorar estructura de clase"
```

**Tipos de commit**:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Documentación
- `refactor`: Refactorización
- `test`: Tests
- `perf`: Mejora de rendimiento

### 8. Pull Request

#### Crear PR

1. Push a tu fork
2. Crear Pull Request
3. Incluir descripción clara:
   - Qué cambia
   - Por qué
   - Cómo probar
   - Referencias a issues (si aplica)

#### Template de PR

```markdown
## Descripción
Breve descripción de los cambios.

## Tipo de Cambio
- [ ] Nueva funcionalidad
- [ ] Corrección de bug
- [ ] Mejora de documentación
- [ ] Refactorización

## Cambios Realizados
- Cambio 1
- Cambio 2

## Testing
- [ ] Tests unitarios agregados
- [ ] Tests de integración ejecutados
- [ ] Validación manual realizada

## Checklist
- [ ] Código sigue estándares (`BEST_PRACTICES.md`)
- [ ] Tests agregados/actualizados
- [ ] Documentación actualizada
- [ ] Changelog actualizado
- [ ] Compatibilidad hacia atrás mantenida
```

---

## 📝 Estándares de Código

### Nomenclatura

```python
# Constantes: MAYÚSCULAS
CONSTANT_VALUE = 42

# Clases: PascalCase
class FaceDetector:
    pass

# Métodos: snake_case
def detect_face():
    pass

# Variables: snake_case
face_bbox = (x, y, w, h)
```

### Type Hints

```python
from typing import Optional, Tuple
import numpy as np

def process_image(
    image: np.ndarray,
    param: int = 10
) -> Optional[np.ndarray]:
    """Procesa imagen."""
    pass
```

### Docstrings

```python
def method_name(param1: type, param2: type) -> return_type:
    """
    Descripción breve del método.
    
    Descripción más detallada si es necesario.
    
    Args:
        param1: Descripción del parámetro 1
        param2: Descripción del parámetro 2
    
    Returns:
        Descripción del valor de retorno
    
    Raises:
        ValueError: Cuando ocurre error de validación
    
    Example:
        >>> detector = FaceDetector()
        >>> bbox = detector.detect(image)
        >>> print(bbox)
    """
    pass
```

---

## 🎯 Áreas de Contribución

### Nuevas Funcionalidades

1. **Nuevos métodos de detección**
   - Seguir patrón de `BaseDetector`
   - Agregar a `DETECTION_METHODS`
   - Documentar en `USAGE_EXAMPLES.md`

2. **Nuevos formatos de landmarks**
   - Actualizar `LandmarkFormatHandler`
   - Agregar constantes en `constants.py`
   - Documentar índices

3. **Nuevas optimizaciones**
   - Agregar a `optimizations.py`
   - Usar decoradores Numba
   - Agregar fallback

### Mejoras de Documentación

- Ejemplos adicionales
- Tutoriales paso a paso
- Diagramas mejorados
- Traducciones

### Tests

- Cobertura adicional
- Tests de rendimiento
- Tests de integración
- Tests de edge cases

### Optimizaciones

- Mejoras de rendimiento
- Reducción de memoria
- Paralelización adicional

---

## ✅ Checklist de Contribución

### Antes de Enviar PR

- [ ] Código sigue `BEST_PRACTICES.md`
- [ ] Type hints completos
- [ ] Docstrings en todos los métodos
- [ ] Tests agregados/actualizados
- [ ] Tests pasan (`python -m pytest tests/`)
- [ ] Validación pasa (`python validate_modules.py`)
- [ ] Documentación actualizada
- [ ] Changelog actualizado
- [ ] Compatibilidad hacia atrás mantenida
- [ ] Sin errores de linter
- [ ] Código revisado personalmente

---

## 🐛 Reportar Bugs

### Información Necesaria

1. **Descripción clara del problema**
2. **Pasos para reproducir**
3. **Comportamiento esperado**
4. **Comportamiento actual**
5. **Versión**: `from face_swap_modules import __version__`
6. **Entorno**:
   - Python: `python --version`
   - OS: `uname -a` o `systeminfo`
   - Dependencias: `python check_dependencies.py`
7. **Código que reproduce el problema**
8. **Traceback completo** (si aplica)

### Template de Bug Report

```markdown
## Descripción
Descripción clara del bug.

## Pasos para Reproducir
1. Paso 1
2. Paso 2
3. Paso 3

## Comportamiento Esperado
Qué debería pasar.

## Comportamiento Actual
Qué pasa actualmente.

## Entorno
- Versión: 2.1.0
- Python: 3.9.0
- OS: Windows 10
- Dependencias: [resultado de check_dependencies.py]

## Código
```python
# Código que reproduce el problema
```

## Traceback
```
Traceback completo aquí
```
```

---

## 💡 Sugerencias de Mejora

### Proponer Mejoras

1. Crear issue con etiqueta "enhancement"
2. Describir la mejora claramente
3. Explicar beneficios
4. Proponer implementación (opcional)

### Template de Feature Request

```markdown
## Descripción
Descripción de la mejora propuesta.

## Motivación
Por qué esta mejora es útil.

## Propuesta
Cómo implementar la mejora.

## Alternativas Consideradas
Otras opciones consideradas.

## Impacto
- Compatibilidad hacia atrás
- Rendimiento
- Complejidad
```

---

## 📚 Recursos

### Documentación

- `README.md` - Guía principal
- `BEST_PRACTICES.md` - Estándares de código
- `QUICK_START.md` - Inicio rápido
- `USAGE_EXAMPLES.md` - Ejemplos completos
- `ARCHITECTURE_DIAGRAM.md` - Arquitectura

### Herramientas

- `validate_modules.py` - Validar módulos
- `check_dependencies.py` - Verificar dependencias
- `generate_report.py` - Generar reporte
- `benchmark.py` - Benchmark de rendimiento

---

## 🙏 Agradecimientos

Gracias por contribuir a Face Swap Modules. Tu contribución hace que el proyecto sea mejor para todos.

---

**Última actualización**: v2.1.0







