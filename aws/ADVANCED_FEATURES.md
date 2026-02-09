# Funcionalidades Avanzadas

## 🔄 Circuit Breaker

El Circuit Breaker previene fallos en cascada al abrir el circuito cuando hay demasiados fallos consecutivos.

### Configuración

```bash
export CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
export CIRCUIT_BREAKER_SUCCESS_THRESHOLD=2
export CIRCUIT_BREAKER_TIMEOUT=60
```

### Estados

- **CLOSED**: Operación normal
- **OPEN**: Circuito abierto, rechaza requests
- **HALF_OPEN**: Probando si el servicio se recuperó

### Uso

El circuit breaker se integra automáticamente en el proceso de despliegue. Cuando el circuito está abierto, los despliegues se rechazan automáticamente para prevenir más fallos.

## 📊 Distributed Tracing

Sistema de trazabilidad distribuida para rastrear operaciones a través de todos los componentes.

### Características

- Traces únicos por despliegue
- Spans anidados para operaciones
- Tags y logs por span
- Historial de traces

### Ejemplo

```python
from deployment_tracing import DeploymentTracer

tracer = DeploymentTracer()
trace_id = tracer.start_trace("deployment")

with tracer.span("git_pull", trace_id):
    # Operación git pull
    
with tracer.span("docker_build", trace_id):
    # Operación docker build

trace_summary = tracer.finish_trace(trace_id)
```

## 📈 Performance Monitoring

Monitoreo de rendimiento en tiempo real durante los despliegues.

### Métricas Recopiladas

- CPU usage (promedio, máximo)
- Memory usage (promedio, máximo)
- Disk space
- Network I/O
- Docker containers/images count

### Uso

```python
from deployment_performance import DeploymentPerformanceMonitor

monitor = DeploymentPerformanceMonitor()
snapshot = monitor.take_snapshot()

# Durante despliegue
metrics = monitor.monitor_deployment(deployment_id, duration)

# Resumen
summary = monitor.get_performance_summary()
```

## 🔙 Automatic Rollback

Sistema de rollback automático que restaura el sistema cuando un despliegue falla.

### Políticas de Rollback

```python
from deployment_rollback_auto import RollbackPolicy

policy = RollbackPolicy(
    enabled=True,
    auto_rollback_on_failure=True,
    health_check_failures_threshold=3,
    health_check_interval=30,
    max_rollback_attempts=3
)
```

### Métodos de Rollback

1. **Backup Restore**: Restaura desde backup automático
2. **Docker Rollback**: Detiene nuevos contenedores, inicia anteriores
3. **Git Rollback**: Revierte al commit anterior

### Configuración

```bash
export AUTO_ROLLBACK_ENABLED=true
export AUTO_ROLLBACK_ON_FAILURE=true
```

## 🔗 Integración Completa

Todas las funcionalidades avanzadas se integran automáticamente en `integrated_deployment.py`:

1. **Tracing**: Se inicia automáticamente al comenzar el despliegue
2. **Performance Monitoring**: Toma snapshots durante el despliegue
3. **Circuit Breaker**: Protege contra fallos en cascada
4. **Automatic Rollback**: Se ejecuta automáticamente si el despliegue falla

## 📊 Visualización

### Traces

Los traces se guardan en `/var/lib/deployment-tracing/traces.json`

```bash
# Ver traces recientes
cat /var/lib/deployment-tracing/traces.json | jq '.[-5:]'
```

### Performance Metrics

Las métricas se guardan en `/var/lib/deployment-performance/metrics.json`

```bash
# Ver métricas recientes
cat /var/lib/deployment-performance/metrics.json | jq '.deployment_metrics[-5:]'
```

### Rollback History

El historial de rollbacks se guarda en `/var/lib/deployment-rollback/history.json`

```bash
# Ver historial de rollbacks
cat /var/lib/deployment-rollback/history.json | jq '.[-5:]'
```

## 🎯 Mejores Prácticas

1. **Circuit Breaker**: Configura thresholds apropiados para tu ambiente
2. **Tracing**: Usa tags descriptivos para facilitar debugging
3. **Performance Monitoring**: Revisa métricas regularmente para optimizar
4. **Rollback**: Siempre mantén backups recientes disponibles

## 🔧 Troubleshooting

### Circuit Breaker siempre abierto

- Verifica los logs para ver por qué fallan los despliegues
- Considera aumentar el `failure_threshold`
- Revisa la salud del sistema

### Traces no aparecen

- Verifica permisos en `/var/lib/deployment-tracing/`
- Revisa los logs del tracer
- Asegúrate de que el tracer esté inicializado

### Rollback falla

- Verifica que los backups existan
- Revisa permisos de Docker
- Verifica conectividad Git
