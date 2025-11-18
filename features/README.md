# Text Quality Detection and Document Monitoring System

## Descripción

Este módulo de características (features) implementa un sistema avanzado de detección de calidad de texto que puede identificar patrones de lenguaje agresivo, contenido de baja calidad y lenguaje excesivamente sumiso durante la creación de documentos.

## Características Principales

### 🔍 Detección de Calidad de Texto
- **Lenguaje Agresivo**: Detecta patrones condescendientes, demandantes y directamente agresivos
- **Lenguaje Sumiso**: Identifica disculpas excesivas, deferencia exagerada y autodepreciación
- **Calidad Baja**: Detecta lenguaje vago, palabras de relleno y expresiones poco profesionales
- **Contenido Repetitivo**: Identifica repeticiones excesivas y redundancias

### 📊 Monitoreo en Tiempo Real
- **Sesiones de Documento**: Seguimiento completo de sesiones de creación de documentos
- **Retroalimentación Instantánea**: Sugerencias en tiempo real durante la escritura
- **Análisis de Tendencias**: Historial de calidad y patrones de mejora
- **Alertas Inteligentes**: Notificaciones basadas en umbrales de calidad

### 🚀 API REST Completa
- **Endpoints RESTful**: API completa para integración con otros sistemas
- **Documentación Automática**: Documentación OpenAPI/Swagger integrada
- **Configuración Flexible**: Configuración basada en variables de entorno
- **Escalabilidad**: Diseño preparado para múltiples usuarios concurrentes

## Instalación

### Requisitos
- Python 3.8+
- Dependencias listadas en `requirements.txt`

### Instalación Rápida
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (opcional)
export TEXT_QUALITY_LANGUAGE=es
export DOC_MONITOR_ENABLE_LOGS=true
export FEATURES_DEBUG=false
```

## Uso Básico

### 1. Análisis de Texto Simple

```python
from features.text_quality_detector import TextQualityDetector

# Crear detector
detector = TextQualityDetector()

# Analizar texto
texto = "Eres completamente incorrecto y no entiendes nada sobre este tema."
resultado = detector.analyze_text(texto)

print(f"Puntuación de calidad: {resultado.overall_quality_score}")
print(f"Problemas detectados: {[issue.value for issue in resultado.issues]}")
print(f"Sugerencias: {resultado.suggestions}")
```

### 2. Monitoreo de Documentos

```python
from features.document_monitor import DocumentMonitor
import asyncio

async def ejemplo_monitoreo():
    # Crear monitor
    monitor = DocumentMonitor()
    
    # Iniciar sesión
    session = monitor.start_session("user123", "user123", "reporte")
    
    # Actualizar texto y obtener retroalimentación
    feedback = monitor.update_text("session_id", "Nuevo texto del documento")
    
    if feedback:
        print(f"Retroalimentación: {feedback['message']}")
        print(f"Sugerencias: {feedback['suggestions']}")
    
    # Finalizar sesión
    resumen = monitor.end_session("session_id")
    print(f"Resumen final: {resumen}")

# Ejecutar
asyncio.run(ejemplo_monitoreo())
```

### 3. Uso de la API

```bash
# Iniciar servidor API
python -m features.api

# Analizar texto
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "Tu texto aquí", "user_id": "user123"}'

# Iniciar sesión
curl -X POST "http://localhost:8000/session/start" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user123", "document_type": "reporte"}'
```

## Configuración

### Variables de Entorno

```bash
# Configuración de Calidad de Texto
TEXT_QUALITY_EXCELLENT_THRESHOLD=0.8
TEXT_QUALITY_GOOD_THRESHOLD=0.6
TEXT_QUALITY_WARNING_THRESHOLD=0.4
TEXT_QUALITY_CRITICAL_THRESHOLD=0.2
TEXT_QUALITY_LANGUAGE=es

# Configuración del Monitor de Documentos
DOC_MONITOR_CHECK_INTERVAL=2.0
DOC_MONITOR_SESSION_TIMEOUT=300.0
DOC_MONITOR_MIN_TEXT_LENGTH=10
DOC_MONITOR_MAX_SUGGESTIONS=5
DOC_MONITOR_ENABLE_LOGS=true

# Configuración General
FEATURES_DEBUG=false
FEATURES_LOG_LEVEL=INFO
FEATURES_API_PORT=8000
FEATURES_API_HOST=localhost
```

### Configuración Programática

```python
from features.config import FeaturesConfig, TextQualityConfig, DocumentMonitorConfig

# Configuración personalizada
config = FeaturesConfig(
    text_quality=TextQualityConfig(
        language="es",
        warning_threshold=0.3,
        critical_threshold=0.1
    ),
    document_monitor=DocumentMonitorConfig(
        check_interval=1.0,
        max_suggestions_per_session=3
    ),
    debug_mode=True
)
```

## Patrones de Detección

### Lenguaje Agresivo
- **Directo**: "Estás equivocado", "Eso es estúpido"
- **Condescendiente**: "Déjame explicarte", "Si supieras algo"
- **Demandante**: "Debes hacerlo", "Sin excusas"

### Lenguaje Sumiso
- **Disculpas Excesivas**: "Lo siento mucho", "Me disculpo profusamente"
- **Deferencia Exagerada**: "Si te place", "Si fuera tan amable"
- **Autodepreciación**: "Probablemente estoy equivocado", "No soy experto"

### Indicadores de Calidad Baja
- **Lenguaje Vago**: "De alguna manera", "Cosas", "Como que"
- **Palabras de Relleno**: "Um", "Eh", "Básicamente"
- **Poco Profesional**: "Increíble", "OMG", "Genial"

## API Endpoints

### Análisis de Texto
- `POST /analyze` - Analizar texto para problemas de calidad
- `GET /health` - Verificar estado del sistema

### Gestión de Sesiones
- `POST /session/start` - Iniciar nueva sesión de documento
- `POST /session/update` - Actualizar texto de sesión
- `GET /session/{id}/summary` - Obtener resumen de sesión
- `DELETE /session/{id}` - Finalizar sesión
- `GET /sessions` - Listar sesiones activas

### Configuración
- `GET /config` - Obtener configuración actual

## Ejemplos de Integración

### Integración con Editor de Texto

```python
class EditorIntegracion:
    def __init__(self):
        self.monitor = DocumentMonitor()
        self.session_id = None
    
    def iniciar_documento(self, user_id):
        self.session_id = f"doc_{int(time.time())}"
        self.monitor.start_session(self.session_id, user_id)
    
    def actualizar_texto(self, texto):
        if self.session_id:
            feedback = self.monitor.update_text(self.session_id, texto)
            if feedback and feedback['type'] != 'positive_feedback':
                self.mostrar_alerta(feedback['message'])
                self.mostrar_sugerencias(feedback['suggestions'])
    
    def finalizar_documento(self):
        if self.session_id:
            resumen = self.monitor.end_session(self.session_id)
            return resumen
```

### Integración con Sistema de Aprendizaje

```python
class SistemaAprendizaje:
    def __init__(self):
        self.detector = TextQualityDetector()
        self.historial_estudiante = {}
    
    def evaluar_escritura_estudiante(self, estudiante_id, texto):
        resultado = self.detector.analyze_text(texto)
        
        # Guardar en historial
        if estudiante_id not in self.historial_estudiante:
            self.historial_estudiante[estudiante_id] = []
        
        self.historial_estudiante[estudiante_id].append({
            'fecha': datetime.now(),
            'calidad': resultado.overall_quality_score,
            'problemas': [issue.value for issue in resultado.issues]
        })
        
        # Proporcionar retroalimentación educativa
        return self.generar_retroalimentacion_educativa(resultado)
    
    def generar_retroalimentacion_educativa(self, resultado):
        if resultado.overall_quality_score < 0.4:
            return {
                'tipo': 'necesita_mejora',
                'mensaje': 'Tu escritura necesita mejoras significativas.',
                'recursos': [
                    'Curso de escritura profesional',
                    'Guía de tono y estilo',
                    'Ejercicios de claridad'
                ]
            }
        elif resultado.overall_quality_score > 0.8:
            return {
                'tipo': 'excelente',
                'mensaje': '¡Excelente calidad de escritura!',
                'siguiente_nivel': 'Considera temas más avanzados'
            }
```

## Monitoreo y Logs

### Logs de Calidad
El sistema genera automáticamente logs detallados de análisis de calidad:

```json
{
  "session_id": "session_1234567890",
  "user_id": "user123",
  "document_type": "reporte",
  "start_time": "2024-01-15T10:30:00",
  "end_time": "2024-01-15T11:00:00",
  "quality_history": [
    {
      "text": "Texto analizado...",
      "quality_score": 0.75,
      "issues": ["low_quality"],
      "severity": "medium",
      "suggestions": ["Mejorar claridad"]
    }
  ]
}
```

### Métricas del Sistema
- Número de sesiones activas
- Tiempo promedio de sesión
- Distribución de puntuaciones de calidad
- Problemas más comunes detectados

## Desarrollo y Contribución

### Estructura del Proyecto
```
features/
├── __init__.py              # Inicialización del módulo
├── text_quality_detector.py # Detector principal de calidad
├── document_monitor.py      # Monitor de documentos
├── config.py               # Configuración del sistema
├── api.py                  # API REST
├── requirements.txt        # Dependencias
└── README.md              # Documentación
```

### Agregar Nuevos Patrones

```python
# En text_quality_detector.py
def _load_custom_patterns(self) -> Dict[str, List[str]]:
    return {
        "nuevo_tipo": [
            r'\b(patrón\s+personalizado)',
            r'\b(otro\s+patrón)'
        ]
    }
```

### Testing

```bash
# Ejecutar tests
pytest tests/

# Tests con cobertura
pytest --cov=features tests/

# Tests específicos
pytest tests/test_text_quality_detector.py
```

## Casos de Uso

### 1. Plataforma Educativa
- Detección de plagio y calidad en ensayos
- Retroalimentación automática para estudiantes
- Análisis de progreso en escritura

### 2. Sistema de Comunicación Corporativa
- Revisión de emails y documentos
- Mejora de comunicación profesional
- Prevención de lenguaje inapropiado

### 3. Plataforma de Contenido
- Moderación automática de contenido
- Mejora de calidad de artículos
- Filtrado de contenido de baja calidad

### 4. Sistema de Soporte al Cliente
- Análisis de respuestas de agentes
- Mejora de comunicación con clientes
- Detección de tono inapropiado

## Limitaciones y Consideraciones

### Limitaciones Actuales
- Patrones principalmente en inglés y español
- Requiere texto mínimo de 10 caracteres
- Análisis basado en patrones regex (no ML avanzado)

### Consideraciones de Rendimiento
- Análisis en tiempo real puede impactar rendimiento
- Sesiones múltiples requieren gestión de memoria
- Logs pueden crecer rápidamente en sistemas grandes

### Privacidad y Seguridad
- Los textos se procesan en memoria
- Logs pueden contener contenido sensible
- Considerar encriptación para datos sensibles

## Roadmap Futuro

### Versión 2.0
- [ ] Integración con modelos de ML avanzados
- [ ] Soporte para más idiomas
- [ ] Análisis de sentimientos
- [ ] Detección de sesgo y discriminación

### Versión 2.1
- [ ] Dashboard web para administración
- [ ] Integración con bases de datos
- [ ] Sistema de notificaciones
- [ ] API GraphQL

### Versión 3.0
- [ ] Análisis de imágenes y documentos
- [ ] Integración con IA generativa
- [ ] Sistema de aprendizaje automático
- [ ] Análisis predictivo de calidad

## Soporte y Contacto

Para soporte técnico, reportar bugs o solicitar nuevas características:

- **Email**: support@blatam-academy.com
- **Documentación**: [docs.blatam-academy.com](https://docs.blatam-academy.com)
- **Issues**: [GitHub Issues](https://github.com/blatam-academy/issues)

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**Desarrollado por el equipo de Blatam Academy AI** 🚀


























