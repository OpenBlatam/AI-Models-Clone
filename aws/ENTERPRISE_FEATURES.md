# Enterprise Features

## 🚩 Feature Flags

Sistema de feature flags para rollouts graduales y A/B testing.

### Características

- **Boolean Flags**: Activación/desactivación simple
- **Percentage Rollout**: Rollout gradual por porcentaje
- **User List**: Activación para usuarios específicos
- **Environment-based**: Flags por ambiente

### Uso

```python
from deployment_feature_flags import FeatureFlagsManager, FeatureFlagType

manager = FeatureFlagsManager()

# Crear flag
manager.create_flag(
    name="new_feature",
    enabled=True,
    flag_type=FeatureFlagType.PERCENTAGE,
    percentage=10  # 10% rollout
)

# Verificar flag
if manager.is_enabled("new_feature", context={'user_id': 'user123'}):
    # Usar nueva feature
    pass

# Aumentar rollout gradualmente
manager.set_percentage("new_feature", 25)  # 25%
manager.set_percentage("new_feature", 50)  # 50%
manager.set_percentage("new_feature", 100) # 100%
```

### Configuración

Los flags se guardan en `/var/lib/feature-flags/flags.json`

## 🔒 Security Scanner

Escaneo automático de seguridad antes de cada despliegue.

### Escaneos Realizados

1. **Dockerfile Analysis**:
   - Usuario root
   - Secrets expuestos
   - Tags no fijados

2. **Dependency Scanning**:
   - Vulnerabilidades conocidas
   - Versiones desactualizadas
   - Dependencias comprometidas

3. **Secret Detection**:
   - Passwords en código
   - API keys
   - AWS credentials
   - Otros secrets

### Configuración

```bash
# Bloquear despliegue si hay issues críticos
# Configurado en integrated_deployment.py
max_critical = 0
max_high = 2
```

### Ejemplo

```python
from deployment_security_scanner import SecurityScanner

scanner = SecurityScanner('/opt/blatam-academy')
results = scanner.scan_all()

if scanner.should_block_deployment(max_critical=0, max_high=2):
    print("Deployment blocked due to security issues")
```

## 💰 Cost Optimizer

Análisis y optimización de costos de despliegue.

### Análisis Realizados

1. **Docker Resources**:
   - Imágenes no utilizadas
   - Contenedores detenidos
   - Recursos huérfanos

2. **Disk Usage**:
   - Uso de disco
   - Espacio disponible
   - Recomendaciones de limpieza

3. **Dockerfile Optimization**:
   - Multi-stage builds
   - .dockerignore
   - Tamaño de imagen

### Recomendaciones

- **Critical**: Acción inmediata requerida
- **High**: Alta prioridad
- **Medium**: Prioridad media
- **Low**: Baja prioridad

### Ejemplo

```python
from deployment_cost_optimizer import CostOptimizer

optimizer = CostOptimizer('/opt/blatam-academy')
results = optimizer.analyze_all()

high_priority = optimizer.get_high_priority_recommendations()
for rec in high_priority:
    print(f"{rec.priority}: {rec.description}")
    print(f"Action: {rec.action}")
```

## 🧪 Chaos Engineering

Experimentos de caos para probar resiliencia del sistema.

### Tipos de Experimentos

- **CPU Stress**: Estrés de CPU
- **Memory Stress**: Estrés de memoria
- **Network Latency**: Latencia de red
- **Network Packet Loss**: Pérdida de paquetes
- **Container Kill**: Matar contenedores
- **Disk Fill**: Llenar disco

### Uso

```python
from deployment_chaos_engineering import (
    ChaosEngineer, 
    ChaosExperiment, 
    ChaosExperimentType
)

engineer = ChaosEngineer()

experiment = ChaosExperiment(
    name="cpu_stress_test",
    experiment_type=ChaosExperimentType.CPU_STRESS,
    duration=60,  # seconds
    intensity=75,  # 0-100
    enabled=True
)

result = engineer.run_experiment(experiment)
```

### Requisitos

- `stress-ng` para CPU/Memory stress
- `tc` (traffic control) para network experiments
- Permisos apropiados

## 🔗 Integración Completa

Todas las funcionalidades enterprise se integran automáticamente:

1. **Security Scanner**: Se ejecuta antes de cada despliegue
2. **Cost Optimizer**: Analiza costos y proporciona recomendaciones
3. **Feature Flags**: Disponible para controlar features en producción

## 📊 Monitoreo

### Feature Flags

```bash
# Ver flags
cat /var/lib/feature-flags/flags.json | jq
```

### Security Issues

Los issues de seguridad se reportan en los logs y pueden bloquear despliegues.

### Cost Recommendations

Las recomendaciones de costo se muestran en los logs y se guardan para análisis.

## 🎯 Mejores Prácticas

1. **Feature Flags**: Usa percentage rollout para features nuevas
2. **Security**: Revisa y corrige issues antes de desplegar
3. **Cost Optimization**: Implementa recomendaciones de alta prioridad
4. **Chaos Engineering**: Ejecuta experimentos en ambientes de staging primero

## 🔧 Troubleshooting

### Feature Flags no funcionan

- Verifica permisos en `/var/lib/feature-flags/`
- Revisa el contexto pasado a `is_enabled()`

### Security Scanner bloquea despliegues

- Revisa los issues reportados
- Corrige issues críticos/altos
- Considera ajustar thresholds si es necesario

### Cost Optimizer no encuentra optimizaciones

- Asegúrate de tener recursos Docker activos
- Verifica permisos de lectura
