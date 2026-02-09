# 🚀 Deployment Fácil en AWS

Guía simplificada para desplegar en AWS en 3 pasos.

## ⚡ Quick Start (3 Pasos)

### Paso 1: Configurar AWS

```bash
# Instalar AWS CLI (si no está instalado)
pip install awscli

# Configurar credenciales
aws configure
# AWS Access Key ID: tu_key
# AWS Secret Access Key: tu_secret
# Default region: us-east-1
# Default output format: json
```

### Paso 2: Configurar Recursos

```bash
# Automático - crea DynamoDB, S3, CloudWatch, ECR
python aws/setup_aws.py mi-servicio us-east-1
```

### Paso 3: Deploy

```bash
# Opción A: Lambda (Serverless)
python aws/quick_deploy.py lambda mi-servicio dev us-east-1

# Opción B: ECS (Containers)
python aws/quick_deploy.py ecs mi-servicio us-east-1

# Opción C: Scripts bash/PowerShell
./aws/deploy.sh lambda dev
# o
.\aws\deploy.ps1 -DeploymentType lambda -Stage dev
```

## 🎯 Opciones de Deployment

### 1. AWS Lambda (Serverless) - Recomendado para empezar

**Ventajas:**
- ✅ Sin servidores que gestionar
- ✅ Pago por uso
- ✅ Escalado automático
- ✅ Deployment en segundos

**Comandos:**

```bash
# Setup (una vez)
python aws/setup_aws.py mi-servicio

# Deploy
python aws/quick_deploy.py lambda mi-servicio dev

# Ver URL
serverless info --stage dev
```

**Resultado:**
- API disponible en: `https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/`
- Logs en CloudWatch
- Métricas automáticas

### 2. AWS ECS/Fargate (Containers)

**Ventajas:**
- ✅ Control total
- ✅ Mejor para cargas constantes
- ✅ Docker nativo

**Comandos:**

```bash
# Setup
python aws/setup_aws.py mi-servicio

# Deploy
python aws/quick_deploy.py ecs mi-servicio

# Crear task definition y service
# (ver guía completa en AWS_DEPLOYMENT_GUIDE.md)
```

### 3. AWS EC2 (VPS Tradicional)

**Ventajas:**
- ✅ Control completo
- ✅ Flexibilidad máxima

**Comandos:**

```bash
# Build image
docker build -f docker/Dockerfile -t mi-servicio:latest .

# Push a ECR
# (ver guía completa)
```

## 📋 Checklist Pre-Deployment

- [ ] AWS CLI instalado y configurado
- [ ] Credenciales AWS configuradas (`aws configure`)
- [ ] Docker instalado (para ECS)
- [ ] Serverless Framework instalado (para Lambda)
- [ ] Permisos IAM adecuados

## 🔧 Configuración Automática

### Setup Completo

```bash
# 1. Configurar recursos AWS
python aws/setup_aws.py mi-servicio us-east-1

# Esto crea automáticamente:
# - DynamoDB table: mi-servicio-table
# - S3 bucket: mi-servicio-bucket-us-east-1
# - CloudWatch log groups
# - ECR repository: mi-servicio
```

### Variables de Entorno

```bash
# Opcional: configurar variables
export SERVICE_NAME=mi-servicio
export AWS_REGION=us-east-1
export STAGE=prod

# Luego usar scripts
./aws/deploy.sh lambda prod
```

## 🎯 Ejemplos Completos

### Ejemplo 1: Lambda Simple

```bash
# 1. Setup
python aws/setup_aws.py music-analyzer us-east-1

# 2. Deploy
python aws/quick_deploy.py lambda music-analyzer dev us-east-1

# 3. Probar
curl https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/health
```

### Ejemplo 2: ECS con Docker

```bash
# 1. Setup
python aws/setup_aws.py music-analyzer us-east-1

# 2. Deploy image
python aws/quick_deploy.py ecs music-analyzer us-east-1

# 3. Crear task definition (ver AWS_DEPLOYMENT_GUIDE.md)
```

## 🔍 Verificación Post-Deployment

### Lambda

```bash
# Ver información
serverless info --stage dev

# Ver logs
serverless logs -f api --tail

# Invocar función
serverless invoke -f api --data '{"path": "/health"}'
```

### ECS

```bash
# Ver servicios
aws ecs list-services --cluster mi-cluster

# Ver logs
aws logs tail /ecs/mi-servicio --follow
```

## 🐛 Troubleshooting

### Error: "AWS credentials not configured"

```bash
aws configure
# Ingresa tus credenciales
```

### Error: "Serverless Framework not found"

```bash
npm install -g serverless serverless-python-requirements
```

### Error: "Docker not running"

```bash
# Iniciar Docker Desktop
# Verificar: docker ps
```

### Error: "Permission denied"

```bash
# Verificar permisos IAM
aws iam get-user
# Asegúrate de tener permisos para:
# - Lambda, ECS, ECR, DynamoDB, S3, CloudWatch
```

## 📊 Monitoreo

### CloudWatch

```bash
# Ver logs
aws logs tail /aws/lambda/mi-servicio --follow

# Ver métricas
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=mi-servicio-api-dev \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

## ✅ Post-Deployment

1. **Verificar Health**
   ```bash
   curl https://tu-api-url/health
   ```

2. **Configurar Domain (Opcional)**
   ```bash
   # Usar Route 53 o CloudFront
   ```

3. **Configurar Alarms**
   ```bash
   # En CloudWatch Console
   ```

4. **Configurar CI/CD**
   ```bash
   # GitHub Actions, GitLab CI, etc.
   ```

## 🎯 Siguiente Paso

Una vez desplegado:

1. Lee `AWS_DEPLOYMENT_GUIDE.md` para detalles avanzados
2. Configura CI/CD para deployments automáticos
3. Configura monitoring y alertas
4. Optimiza costos según uso

---

**¡Deployment en 3 pasos!** 🚀




