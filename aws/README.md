# AWS EC2 Auto-Deployment Setup

Sistema completo de despliegue automático en EC2 que se actualiza automáticamente cuando se hace push a la rama `main` de GitHub.

## 🚀 Características

- **Despliegue Automático**: Se actualiza automáticamente al hacer push a `main`
- **Webhook Listener**: Servicio que escucha webhooks de GitHub
- **Polling Alternativo**: Cron job que verifica cambios cada 5 minutos
- **Docker**: Configuración completa con Docker y Docker Compose
- **FastAPI Optimizado**: Configuración lista para producción
- **Seguridad**: Verificación de firmas de webhooks, firewall configurado
- **Monitoreo**: Logs centralizados, health checks, métricas detalladas
- **Rollback Automático**: Rollback automático si el despliegue falla
- **Backups Automáticos**: Crea backups antes de cada despliegue
- **Múltiples Estrategias**: Standard, Blue-Green, Rolling, Canary
- **Validación Pre-Despliegue**: Valida entorno antes de desplegar
- **Caché Inteligente**: Optimiza builds con caché de imágenes
- **Métricas y Analytics**: Tracking completo de despliegues
- **API RESTful**: API para gestionar despliegues programáticamente
- **Notificaciones**: Slack, Discord y webhooks personalizados
- **Circuit Breaker**: Previene fallos en cascada
- **Distributed Tracing**: Trazabilidad completa de operaciones
- **Performance Monitoring**: Monitoreo de rendimiento en tiempo real
- **Rollback Automático**: Rollback automático en caso de fallos
- **Feature Flags**: Rollouts graduales y A/B testing
- **Security Scanner**: Escaneo automático de vulnerabilidades
- **Cost Optimizer**: Análisis y optimización de costos
- **Chaos Engineering**: Pruebas de resiliencia del sistema

## 📁 Estructura del Proyecto

```
aws/
├── scripts/
│   ├── webhook_listener.py      # Servicio que escucha webhooks de GitHub
│   ├── auto_deploy.sh            # Script principal de despliegue
│   ├── ec2_user_data_auto_deploy.sh  # Script de inicialización de EC2
│   ├── check_and_deploy.sh      # Script para verificación periódica
│   ├── config.py                 # Módulo de configuración
│   └── utils.py                  # Utilidades compartidas
├── terraform/
│   ├── main.tf                   # Configuración principal de Terraform
│   ├── ec2.tf                    # Recursos de EC2
│   ├── networking.tf             # Configuración de red
│   ├── security_groups.tf       # Grupos de seguridad
│   └── variables.tf              # Variables de Terraform
├── docker-compose.yml            # Configuración de Docker Compose
├── Dockerfile                    # Dockerfile para FastAPI
└── README.md                     # Este archivo
```

## 🛠️ Configuración Inicial

### 1. Prerrequisitos

- Cuenta de AWS con permisos para crear recursos EC2
- Terraform instalado (>= 1.0)
- Clave SSH de AWS configurada
- Repositorio de GitHub con el código

### 2. Configurar Variables de Terraform

Copia el archivo de ejemplo y configura tus variables:

```bash
cd aws/terraform
cp terraform.tfvars.example terraform.tfvars
```

Edita `terraform.tfvars`:

```hcl
aws_region        = "us-east-1"
project_name      = "blatam-academy"
environment       = "production"
instance_type     = "t3.medium"
key_name          = "tu-clave-ssh"
min_size          = 1
max_size          = 3
desired_capacity  = 1
```

### 3. Configurar Variables de Entorno en Terraform

Edita `ec2.tf` para pasar variables al user data:

```hcl
user_data = base64encode(templatefile("${path.module}/../scripts/ec2_user_data_auto_deploy.sh", {
  project_name   = var.project_name
  environment    = var.environment
  github_repo    = "tu-usuario/tu-repositorio"
  github_branch  = "main"
  github_token   = var.github_token  # Opcional, para repos privados
  webhook_secret = var.webhook_secret
}))
```

### 4. Desplegar con Terraform

```bash
cd aws/terraform
terraform init
terraform plan
terraform apply
```

### 5. Configurar Webhook en GitHub

1. Ve a tu repositorio en GitHub
2. Settings → Webhooks → Add webhook
3. Configura:
   - **Payload URL**: `http://TU-IP-EC2:9000/`
   - **Content type**: `application/json`
   - **Secret**: El mismo que configuraste en `webhook_secret`
   - **Events**: Selecciona "Just the push event"
   - **Active**: ✓

## 🔧 Configuración del Servicio

### Variables de Entorno

El servicio webhook listener puede configurarse con estas variables:

```bash
# Requeridas
PROJECT_DIR=/opt/blatam-academy
DEPLOY_SCRIPT=/opt/blatam-academy/aws/scripts/auto_deploy.sh

# Opcionales
GITHUB_WEBHOOK_SECRET=tu-secreto-aqui
WEBHOOK_PORT=9000
TARGET_BRANCH=main
DEPLOYMENT_TIMEOUT=1800  # 30 minutos
LOG_FILE=/var/log/github-webhook.log
```

### Servicio Systemd

El servicio se configura automáticamente en el user data script. Para gestionarlo manualmente:

```bash
# Ver estado
sudo systemctl status github-webhook-listener

# Ver logs
sudo journalctl -u github-webhook-listener -f

# Reiniciar
sudo systemctl restart github-webhook-listener
```

## 📦 Despliegue Manual

Si necesitas desplegar manualmente:

```bash
cd /opt/blatam-academy
bash aws/scripts/auto_deploy.sh deploy
```

### Comandos Disponibles

```bash
# Desplegar
bash aws/scripts/auto_deploy.sh deploy

# Rollback
bash aws/scripts/auto_deploy.sh rollback

# Health check
bash aws/scripts/auto_deploy.sh health-check
```

## 📊 Servicios Adicionales

### Deployment Monitor

Servicio que rastrea el historial de despliegues y proporciona métricas:

```bash
# Iniciar monitor (puerto 9001 por defecto)
python3 aws/scripts/deployment_monitor.py

# Verificar estado
curl http://localhost:9001/status
```

### Health Checker

Verificador completo de salud del sistema:

```bash
# Ejecutar health checks
python3 aws/scripts/health_checker.py

# Verificar componentes:
# - Docker
# - Contenedores
# - Aplicación
# - Espacio en disco
# - Memoria
# - Directorio del proyecto
```

### Deployment Notifier

Sistema de notificaciones para Slack, Discord y webhooks:

```bash
# Configurar variables de entorno
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR/WEBHOOK/URL"

# Probar notificaciones
python3 aws/scripts/deployment_notifier.py
```

### Sistema Integrado

Script unificado que combina todos los servicios:

```bash
# Usar el sistema integrado para despliegues
python3 aws/scripts/integrated_deployment.py
```

Este script:
- **Crea backup automático** antes del despliegue
- Ejecuta **validación completa** del entorno
- Ejecuta **health checks** pre-despliegue
- Realiza el despliegue usando **estrategia configurable**
- Registra el resultado en el **monitor**
- Registra **métricas** de rendimiento
- Envía **notificaciones**
- Proporciona **métricas completas**

### Estrategias de Despliegue

El sistema soporta múltiples estrategias de despliegue:

```bash
# Estrategia estándar (default)
export DEPLOYMENT_STRATEGY=standard
python3 integrated_deployment.py

# Blue-Green deployment
export DEPLOYMENT_STRATEGY=blue_green
python3 integrated_deployment.py

# Rolling deployment
export DEPLOYMENT_STRATEGY=rolling
python3 integrated_deployment.py

# Canary deployment
export DEPLOYMENT_STRATEGY=canary
python3 integrated_deployment.py
```

## 🔍 Monitoreo y Logs

### Logs del Webhook Listener

```bash
tail -f /var/log/github-webhook.log
```

### Logs de Despliegue

```bash
tail -f /var/log/blatam-academy-deploy.log
```

### Logs de Verificación Periódica

```bash
tail -f /var/log/deployment-check.log
```

### Health Check

El servicio expone un endpoint de health check:

```bash
curl http://localhost:9000/
```

Respuesta:
```json
{
  "status": "ok",
  "service": "github-webhook-listener",
  "timestamp": "2024-01-01T00:00:00",
  "project_dir": "/opt/blatam-academy",
  "deploy_script": "/opt/blatam-academy/aws/scripts/auto_deploy.sh",
  "target_branch": "main"
}
```

## 🐳 Docker

### Construir Imagen

```bash
cd aws
docker build -f Dockerfile -t blatam-academy:latest ..
```

### Ejecutar con Docker Compose

```bash
cd aws
docker-compose up -d
```

### Verificar Contenedores

```bash
docker-compose ps
docker-compose logs -f app
```

## 🔒 Seguridad

### Firewall

El script configura automáticamente UFW con estos puertos abiertos:
- `22` (SSH)
- `80` (HTTP)
- `443` (HTTPS)
- `8000` (FastAPI)
- `9000` (Webhook Listener)

### Webhook Secret

**IMPORTANTE**: Configura siempre un secreto para los webhooks en producción:

1. Genera un secreto seguro:
   ```bash
   openssl rand -hex 32
   ```

2. Configúralo en:
   - Variable de Terraform `webhook_secret`
   - Variable de entorno `GITHUB_WEBHOOK_SECRET`
   - Secret del webhook en GitHub

## 🚨 Troubleshooting

### El webhook no se activa

1. Verifica que el servicio esté corriendo:
   ```bash
   sudo systemctl status github-webhook-listener
   ```

2. Verifica los logs:
   ```bash
   sudo journalctl -u github-webhook-listener -n 50
   ```

3. Verifica que el puerto esté abierto:
   ```bash
   sudo ufw status
   curl http://localhost:9000/
   ```

4. Verifica la configuración del webhook en GitHub (Settings → Webhooks)

### El despliegue falla

1. Verifica los logs:
   ```bash
   tail -f /var/log/blatam-academy-deploy.log
   ```

2. Verifica que Docker esté corriendo:
   ```bash
   sudo systemctl status docker
   ```

3. Verifica el espacio en disco:
   ```bash
   df -h
   ```

4. Intenta un despliegue manual para ver errores detallados:
   ```bash
   bash /opt/blatam-academy/aws/scripts/auto_deploy.sh deploy
   ```

### El repositorio no se clona

1. Verifica que `GITHUB_REPO` esté configurado correctamente
2. Para repos privados, verifica que `GITHUB_TOKEN` tenga permisos
3. Verifica la conectividad:
   ```bash
   ping github.com
   ```

## 📝 Mejores Prácticas

1. **Siempre usa secrets**: Nunca dejes el webhook sin secreto en producción
2. **Monitorea los logs**: Revisa regularmente los logs para detectar problemas
3. **Prueba en staging primero**: Usa un ambiente de staging antes de producción
4. **Backups**: Configura backups regulares de datos importantes
5. **Health checks**: Implementa health checks en tu aplicación FastAPI
6. **Rollback plan**: Ten un plan de rollback documentado

## 🔄 Flujo de Despliegue

1. **Push a main** → GitHub envía webhook
2. **Webhook Listener** → Recibe y verifica el webhook
3. **Auto Deploy Script** → Ejecuta el despliegue:
   - Pull del código más reciente
   - Build de imágenes Docker
   - Stop de contenedores actuales
   - Start de nuevos contenedores
   - Health check
   - Rollback si falla

## 📚 Documentación Adicional

- **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)**: Funcionalidades avanzadas (Circuit Breaker, Tracing, Performance, Rollback)
- **[ENTERPRISE_FEATURES.md](ENTERPRISE_FEATURES.md)**: Funcionalidades enterprise (Feature Flags, Security, Cost, Chaos)
- **[GOVERNANCE_FEATURES.md](GOVERNANCE_FEATURES.md)**: Funcionalidades de governance (Compliance, Approval, Multi-Region, DR)
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Arquitectura del sistema
- **[QUICK_START.md](QUICK_START.md)**: Guía rápida de inicio

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GitHub Webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks)

## 🤝 Contribuir

Para contribuir a este proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
