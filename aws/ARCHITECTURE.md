# Arquitectura del Sistema de Despliegue

## 📐 Visión General

Sistema de despliegue automático con arquitectura modular, escalable y robusta diseñada para producción.

## 🏗️ Componentes Principales

### 1. Core Services

#### Webhook Listener (`webhook_listener.py`)
- **Responsabilidad**: Escucha webhooks de GitHub
- **Puerto**: 9000 (configurable)
- **Características**:
  - Verificación de firmas HMAC SHA256
  - Manejo de eventos push
  - Health check endpoint
  - Logging estructurado

#### Integrated Deployment (`integrated_deployment.py`)
- **Responsabilidad**: Orquesta todo el proceso de despliegue
- **Características**:
  - Coordinación de todos los servicios
  - Manejo de errores y retry
  - Integración con queue y scheduler

### 2. Deployment Services

#### Deployment Strategy (`deployment_strategy.py`)
- **Patrón**: Strategy Pattern
- **Estrategias**:
  - **Standard**: Stop old, start new
  - **Blue-Green**: Dos ambientes en paralelo
  - **Rolling**: Actualización gradual
  - **Canary**: Despliegue a subconjunto primero

#### Deployment Validator (`deployment_validator.py`)
- **Responsabilidad**: Validación pre-despliegue
- **Validaciones**:
  - Docker y Docker Compose
  - Espacio en disco y memoria
  - Red y conectividad
  - Permisos y configuración

#### Deployment Cache (`deployment_cache.py`)
- **Responsabilidad**: Gestión de caché
- **Características**:
  - Caché de imágenes Docker
  - Caché de artefactos de build
  - Limpieza automática

### 3. Monitoring & Analytics

#### Deployment Monitor (`deployment_monitor.py`)
- **Responsabilidad**: Tracking de despliegues
- **Puerto**: 9001
- **Datos**:
  - Historial de despliegues
  - Estadísticas (total, exitosos, fallidos)
  - Últimos 100 despliegues

#### Deployment Metrics (`deployment_metrics.py`)
- **Responsabilidad**: Métricas y analytics
- **Métricas**:
  - Tiempo promedio de despliegue
  - Tasa de éxito/fallo
  - Tendencias por día
  - Comparación de estrategias

### 4. Infrastructure Services

#### Health Checker (`health_checker.py`)
- **Responsabilidad**: Verificación de salud
- **Checks**:
  - Docker y contenedores
  - Aplicación (health endpoint)
  - Espacio en disco
  - Memoria
  - Directorio del proyecto

#### Backup Manager (`backup_manager.py`)
- **Responsabilidad**: Gestión de backups
- **Características**:
  - Backups automáticos pre-despliegue
  - Backup de Docker volumes
  - Restauración de backups
  - Limpieza automática

### 5. Advanced Features

#### Deployment Retry (`deployment_retry.py`)
- **Responsabilidad**: Retry logic con backoff
- **Estrategias**:
  - Exponential backoff
  - Linear backoff
  - Fixed delay
- **Configuración**: Max attempts, delays, multipliers

#### Deployment Queue (`deployment_queue.py`)
- **Responsabilidad**: Cola de despliegues
- **Características**:
  - Previene despliegues concurrentes
  - Priorización
  - Historial de requests
  - Persistencia en disco

#### Deployment Scheduler (`deployment_scheduler.py`)
- **Responsabilidad**: Programación de despliegues
- **Características**:
  - Horarios permitidos
  - Días permitidos
  - Límites por hora/día
  - Ventanas de mantenimiento

#### Deployment Optimizer (`deployment_optimizer.py`)
- **Responsabilidad**: Optimización del proceso
- **Optimizaciones**:
  - Docker build cache
  - Git operations
  - Limpieza de recursos
  - Recomendaciones

### 6. Communication Services

#### Deployment Notifier (`deployment_notifier.py`)
- **Responsabilidad**: Notificaciones
- **Canales**:
  - Slack
  - Discord
  - Webhooks personalizados

#### Deployment API (`deployment_api.py`)
- **Responsabilidad**: API RESTful
- **Puerto**: 9002
- **Endpoints**:
  - GET /api/status
  - GET /api/deployments
  - GET /api/metrics
  - GET /api/health
  - GET /api/backups
  - POST /api/backup
  - POST /api/restore/<name>

## 🔄 Flujo de Despliegue

```
1. Push a main branch
   ↓
2. GitHub Webhook → Webhook Listener
   ↓
3. Verificación de firma
   ↓
4. Deployment Queue (verificar si hay despliegue en curso)
   ↓
5. Deployment Scheduler (verificar si está permitido)
   ↓
6. Integrated Deployment
   ├── Backup Manager (crear backup)
   ├── Deployment Optimizer (optimizar recursos)
   ├── Deployment Validator (validar entorno)
   ├── Health Checker (verificar salud)
   ├── Deployment Strategy (ejecutar despliegue)
   │   └── Retry Handler (con retry logic)
   ├── Deployment Monitor (registrar resultado)
   ├── Deployment Metrics (registrar métricas)
   ├── Deployment Notifier (enviar notificaciones)
   └── Deployment Queue (marcar como completado)
```

## 📊 Arquitectura de Datos

### Estado Persistente

- **Deployment Monitor**: `/var/lib/deployment-monitor/state.json`
- **Deployment Metrics**: `/var/lib/deployment-metrics/metrics.json`
- **Deployment Queue**: `/var/lib/deployment-queue/queue.json`
- **Deployment Cache**: `/var/cache/deployment/`

### Logs

- **Webhook Listener**: `/var/log/github-webhook.log`
- **Deployment**: `/var/log/blatam-academy-deploy.log`
- **Deployment Check**: `/var/log/deployment-check.log`
- **Integrated Deployment**: `/var/log/integrated-deployment.log`

## 🔌 Integraciones

### GitHub
- Webhooks para triggers automáticos
- Verificación de firmas HMAC
- Soporte para repos privados (con token)

### Docker
- Build de imágenes
- Gestión de contenedores
- Backup de volumes
- Limpieza automática

### Notificaciones
- Slack webhooks
- Discord webhooks
- Webhooks personalizados

## 🎯 Principios de Diseño

1. **Separación de Responsabilidades**: Cada módulo tiene una responsabilidad única
2. **Patrón Strategy**: Estrategias de despliegue intercambiables
3. **Retry Logic**: Reintentos automáticos con backoff
4. **Queue Management**: Prevención de despliegues concurrentes
5. **Scheduling**: Control de cuándo se permiten despliegues
6. **Caching**: Optimización de builds
7. **Monitoring**: Tracking completo de métricas
8. **Validation**: Validación exhaustiva antes de desplegar

## 🚀 Escalabilidad

- **Horizontal**: Múltiples instancias EC2
- **Vertical**: Auto-scaling groups
- **Queue-based**: Sistema de cola para manejar carga
- **Caching**: Reduce tiempo de builds
- **Optimization**: Limpieza automática de recursos

## 🔒 Seguridad

- Verificación de firmas de webhooks
- Firewall configurado (UFW)
- Validación de permisos
- Backups automáticos
- Logs auditables

## 📈 Monitoreo

- Métricas de rendimiento
- Health checks
- Logs estructurados
- Notificaciones en tiempo real
- API para consultas
