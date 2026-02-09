# ☁️ Guía de Deployment en AWS

Guía completa paso a paso para desplegar servicios FastAPI en AWS.

## 📋 Tabla de Contenidos

1. [Prerequisitos](#prerequisitos)
2. [Lambda Deployment](#lambda-deployment)
3. [ECS/Fargate Deployment](#ecsfargate-deployment)
4. [API Gateway Setup](#api-gateway-setup)
5. [DynamoDB Setup](#dynamodb-setup)
6. [CloudWatch Setup](#cloudwatch-setup)
7. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisitos

### Instalar Herramientas

```bash
# AWS CLI
pip install awscli

# Serverless Framework
npm install -g serverless
npm install -g serverless-python-requirements

# SAM CLI
pip install aws-sam-cli

# Terraform (opcional)
# Descargar desde https://www.terraform.io/downloads
```

### Configurar AWS

```bash
aws configure
# AWS Access Key ID: tu_key
# AWS Secret Access Key: tu_secret
# Default region: us-east-1
# Default output format: json
```

---

## 2. Lambda Deployment

### Paso 1: Preparar Código

```python
# lambda_function.py
from mangum import Mangum
from main import app

handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    return handler(event, context)
```

### Paso 2: Generar Configuración

```python
from shared_lib.aws import create_serverless_config

create_serverless_config(
    service_name="music-analyzer-ai",
    output_dir=".",
    framework="serverless"
)
```

### Paso 3: Deploy

```bash
# Instalar dependencias
pip install -r requirements.txt

# Deploy
serverless deploy

# O con SAM
sam build
sam deploy --guided
```

### Paso 4: Verificar

```bash
# Obtener URL del API
serverless info

# Probar
curl https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/
```

---

## 3. ECS/Fargate Deployment

### Paso 1: Construir Docker Image

```bash
# Build
docker build -t music-analyzer-ai:latest .

# Tag para ECR
docker tag music-analyzer-ai:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/music-analyzer-ai:latest
```

### Paso 2: Push a ECR

```bash
# Login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/music-analyzer-ai:latest
```

### Paso 3: Crear Task Definition

```python
from shared_lib.aws import ECSDeployment
import json

task_def = ECSDeployment.generate_task_definition(
    family="music-analyzer-ai",
    image="123456789.dkr.ecr.us-east-1.amazonaws.com/music-analyzer-ai:latest",
    cpu="512",
    memory="1024"
)

# Guardar
with open("task-definition.json", "w") as f:
    json.dump(task_def, f, indent=2)
```

### Paso 4: Registrar y Desplegar

```bash
# Registrar task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Crear servicio
aws ecs create-service \
  --cluster mi-cluster \
  --service-name music-analyzer-ai \
  --task-definition music-analyzer-ai \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

## 4. API Gateway Setup

### Crear API

```python
from shared_lib.aws import aws_api_gateway

# Crear REST API
api_id = aws_api_gateway.create_rest_api(
    name="music-analyzer-api",
    description="Music Analyzer AI API"
)

# Crear integración Lambda
aws_api_gateway.create_lambda_integration(
    api_id=api_id,
    lambda_arn="arn:aws:lambda:us-east-1:123456789:function:music-analyzer-ai-api",
    method="ANY",
    path="{proxy+}"
)

# Desplegar
aws_api_gateway.deploy_api(api_id, "prod")

# Crear usage plan
aws_api_gateway.create_usage_plan(
    api_id=api_id,
    stage_name="prod",
    throttle_rate=100.0,
    throttle_burst=200
)
```

---

## 5. DynamoDB Setup

### Crear Tabla

```bash
aws dynamodb create-table \
  --table-name tracks \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### Usar en Código

```python
from shared_lib.aws import dynamodb_manager

# Configurar
dynamodb_manager.table_prefix = "prod_"

# Usar
await dynamodb_manager.put_item("tracks", {
    "id": "track-123",
    "name": "Song Name",
    "artist": "Artist Name"
})
```

---

## 6. CloudWatch Setup

### Crear Log Group

```bash
aws logs create-log-group --log-group-name /aws/lambda/music-analyzer-ai
```

### Configurar Métricas

```python
from shared_lib.aws import cloudwatch_metrics

# Métricas automáticas
cloudwatch_metrics.increment_counter("api_requests")
cloudwatch_metrics.record_latency("response_time", 0.5)
```

---

## 7. Troubleshooting

### Error: "Unable to import module"

**Solución**: Asegúrate de incluir todas las dependencias en el deployment package.

### Error: "Task failed to start"

**Solución**: Verifica que el security group permita tráfico saliente y que el task tenga permisos IAM adecuados.

### Error: "API Gateway timeout"

**Solución**: Aumenta el timeout en Lambda (máximo 15 minutos para API Gateway, 15 minutos para Lambda).

### Cold Start Lento

**Solución**: 
- Usar `serverless_handler` decorator
- Reducir tamaño del package
- Usar provisioned concurrency

---

## 🎯 Comandos Rápidos

```bash
# Deploy Lambda
serverless deploy

# Ver logs
serverless logs -f api --tail

# Invocar función
serverless invoke -f api --data '{"path": "/health"}'

# Deploy ECS
aws ecs update-service --cluster cluster --service service --force-new-deployment
```

---

**Última actualización**: 2024




