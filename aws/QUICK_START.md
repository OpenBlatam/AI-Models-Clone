# Quick Start Guide - AWS EC2 Auto-Deployment

Guía rápida para configurar el sistema de despliegue automático en EC2.

## 🚀 Inicio Rápido (5 minutos)

### 1. Configurar Terraform

```bash
cd aws/terraform
cp terraform.tfvars.example terraform.tfvars
# Edita terraform.tfvars con tus valores
```

### 2. Desplegar Infraestructura

```bash
terraform init
terraform plan
terraform apply
```

### 3. Configurar Webhook en GitHub

1. Ve a tu repositorio → Settings → Webhooks
2. Add webhook
3. URL: `http://TU-IP-EC2:9000/`
4. Secret: El mismo que configuraste en Terraform
5. Events: Just the push event

### 4. ¡Listo!

Cada push a `main` desplegará automáticamente.

## 📋 Comandos Útiles

### Verificar Estado

```bash
# Webhook listener
curl http://localhost:9000/

# Deployment monitor
curl http://localhost:9001/status

# Deployment API
curl http://localhost:9002/api/status
```

### Despliegue Manual

```bash
# Despliegue estándar
python3 aws/scripts/integrated_deployment.py

# Con estrategia específica
DEPLOYMENT_STRATEGY=blue_green python3 aws/scripts/integrated_deployment.py
```

### Ver Métricas

```bash
curl http://localhost:9002/api/metrics
```

### Crear Backup Manual

```bash
python3 -c "
from aws.scripts.backup_manager import BackupManager
bm = BackupManager()
print(bm.create_backup('/opt/blatam-academy'))
"
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# Estrategia de despliegue
export DEPLOYMENT_STRATEGY=blue_green

# Notificaciones
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK"
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR/WEBHOOK"

# Health check
export HEALTH_CHECK_URL="http://localhost:8000/health"
export HEALTH_CHECK_TIMEOUT=60
```

### Servicios Systemd

```bash
# Webhook listener
sudo systemctl status github-webhook-listener
sudo systemctl restart github-webhook-listener

# Ver logs
sudo journalctl -u github-webhook-listener -f
```

## 📊 Monitoreo

### Ver Logs

```bash
# Webhook
tail -f /var/log/github-webhook.log

# Despliegue
tail -f /var/log/blatam-academy-deploy.log

# Deployment check
tail -f /var/log/deployment-check.log
```

### Health Checks

```bash
# Health checker
python3 aws/scripts/health_checker.py

# Via API
curl http://localhost:9002/api/health
```

## 🆘 Troubleshooting Rápido

### El webhook no funciona

```bash
# Verificar servicio
sudo systemctl status github-webhook-listener

# Verificar puerto
sudo ufw status
curl http://localhost:9000/
```

### El despliegue falla

```bash
# Ver logs
tail -f /var/log/blatam-academy-deploy.log

# Validar entorno
python3 -c "
from aws.scripts.deployment_validator import DeploymentValidator
v = DeploymentValidator({'project_dir': '/opt/blatam-academy'})
passed, results = v.validate_all()
print('PASSED' if passed else 'FAILED')
for r in results:
    print(f\"{r.severity}: {r.message}\")
"
```

## 📚 Más Información

Ver [README.md](README.md) para documentación completa.
