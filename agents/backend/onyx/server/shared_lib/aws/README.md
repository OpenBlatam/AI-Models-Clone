# ☁️ AWS Integration - Shared Library

Integración completa con servicios de AWS para deployment serverless y cloud-native.

## 🚀 Características

### ✅ Implementado

1. **Lambda Handler** - Optimizado para AWS Lambda
2. **API Gateway** - REST y HTTP APIs
3. **DynamoDB** - Gestor completo con queries optimizados
4. **S3** - Upload, download, presigned URLs
5. **CloudWatch** - Logging y métricas
6. **ECS/Fargate** - Task y service definitions
7. **Serverless Config** - Serverless Framework y SAM
8. **Terraform** - Infraestructura como código

## 📦 Módulos

### 1. Lambda Handler (`aws/lambda_handler.py`)

```python
from shared_lib.aws import create_lambda_handler
from fastapi import FastAPI

app = FastAPI()
handler = create_lambda_handler(app)

# En lambda_function.py
def lambda_handler(event, context):
    return handler(event, context)
```

### 2. API Gateway (`aws/api_gateway.py`)

```python
from shared_lib.aws import aws_api_gateway

# Crear REST API
api_id = aws_api_gateway.create_rest_api(
    name="mi-api",
    description="Mi API"
)

# Crear integración Lambda
aws_api_gateway.create_lambda_integration(
    api_id=api_id,
    lambda_arn="arn:aws:lambda:...",
    method="ANY",
    path="{proxy+}"
)

# Desplegar
aws_api_gateway.deploy_api(api_id, "prod")

# Crear usage plan con rate limiting
aws_api_gateway.create_usage_plan(
    api_id=api_id,
    stage_name="prod",
    throttle_rate=100.0,
    throttle_burst=200
)
```

### 3. DynamoDB (`aws/dynamodb.py`)

```python
from shared_lib.aws import dynamodb_manager

# Guardar
await dynamodb_manager.put_item(
    "tracks",
    {"id": "track-123", "name": "Song Name"}
)

# Obtener
track = await dynamodb_manager.get_item(
    "tracks",
    {"id": "track-123"}
)

# Query
from boto3.dynamodb.conditions import Key
tracks = await dynamodb_manager.query(
    "tracks",
    Key("artist").eq("Artist Name")
)

# Batch operations
await dynamodb_manager.batch_write_items(
    "tracks",
    [{"id": f"track-{i}", "name": f"Song {i}"} for i in range(10)]
)
```

### 4. S3 (`aws/s3.py`)

```python
from shared_lib.aws import s3_manager

# Upload
s3_manager.upload_file(
    bucket="my-bucket",
    key="tracks/track-123.mp3",
    file_path="/local/path/file.mp3"
)

# Download
s3_manager.download_file(
    bucket="my-bucket",
    key="tracks/track-123.mp3",
    file_path="/local/path/downloaded.mp3"
)

# Presigned URL
url = s3_manager.generate_presigned_url(
    bucket="my-bucket",
    key="tracks/track-123.mp3",
    expiration=3600
)
```

### 5. CloudWatch (`aws/cloudwatch.py`)

```python
from shared_lib.aws import cloudwatch_logger, cloudwatch_metrics

# Logging
cloudwatch_logger.log(
    "Track analyzed",
    level="INFO",
    track_id="track-123",
    duration=1.5
)

# Métricas
cloudwatch_metrics.increment_counter(
    "tracks_analyzed",
    value=1.0,
    dimensions={"service": "music-analyzer"}
)

cloudwatch_metrics.record_latency(
    "analysis_latency",
    latency_seconds=1.5
)
```

## 🚀 Deployment Options

### Opción 1: Serverless Framework

```bash
# Generar configuración
python -c "from shared_lib.aws import create_serverless_config; create_serverless_config('mi-servicio')"

# Deploy
serverless deploy
```

### Opción 2: SAM (Serverless Application Model)

```bash
# Generar template
python -c "from shared_lib.aws import ServerlessConfig; import yaml; print(yaml.dump(ServerlessConfig.generate_sam_template('mi-servicio')))" > template.yaml

# Build y deploy
sam build
sam deploy --guided
```

### Opción 3: Terraform

```bash
cd shared_lib/aws/terraform
terraform init
terraform plan
terraform apply
```

### Opción 4: ECS/Fargate

```python
from shared_lib.aws import ECSDeployment

# Generar task definition
task_def = ECSDeployment.generate_task_definition(
    family="mi-servicio",
    image="123456789.dkr.ecr.us-east-1.amazonaws.com/mi-servicio:latest",
    cpu="512",
    memory="1024"
)

# Guardar y usar con AWS CLI o boto3
```

## 📋 Configuración AWS

### Credenciales

```bash
# Opción 1: AWS CLI
aws configure

# Opción 2: Variables de entorno
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1

# Opción 3: IAM Role (en Lambda/ECS)
# Automático si está en AWS
```

### Permisos IAM Requeridos

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "apigateway:*",
        "lambda:*",
        "dynamodb:*",
        "s3:*",
        "logs:*",
        "cloudwatch:*",
        "ecs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🎯 Ejemplo Completo Lambda

### 1. Crear lambda_function.py

```python
from mangum import Mangum
from main import app

handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    return handler(event, context)
```

### 2. Deploy con Serverless Framework

```yaml
# serverless.yml (generado automáticamente)
service: music-analyzer-ai
provider:
  name: aws
  runtime: python3.11
functions:
  api:
    handler: lambda_function.lambda_handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

### 3. Deploy

```bash
serverless deploy
```

## 📊 Monitoreo

### CloudWatch Logs

```python
# Los logs estructurados se envían automáticamente a CloudWatch
from shared_lib.aws import cloudwatch_logger

cloudwatch_logger.log("Event occurred", level="INFO", data={"key": "value"})
```

### CloudWatch Metrics

```python
from shared_lib.aws import cloudwatch_metrics

# Métricas personalizadas
cloudwatch_metrics.put_metric(
    "api_requests",
    value=1.0,
    unit="Count",
    dimensions={"endpoint": "/api/v1/analyze"}
)
```

## 🔧 Optimizaciones Lambda

### Cold Start Reduction

```python
# Usar serverless_handler decorator
from shared_lib.serverless import serverless_handler

@serverless_handler
@app.post("/analyze")
async def analyze(data: dict):
    # Código optimizado para Lambda
    return {"result": "analyzed"}
```

### Connection Pooling

```python
# Reutilizar conexiones
from shared_lib.serverless import get_serverless_config

config = get_serverless_config()
# Usa connection pooling automáticamente
```

## 📝 Archivos Generados

Al usar `create_serverless_config()`:

- `serverless.yml` - Configuración Serverless Framework
- `lambda_function.py` - Handler Lambda
- `template.yaml` - SAM template (si se especifica)
- `terraform/` - Archivos Terraform

## ✅ Checklist de Deployment

- [ ] AWS CLI configurado
- [ ] Credenciales configuradas
- [ ] IAM roles con permisos adecuados
- [ ] Docker image construida (para ECS)
- [ ] Configuración serverless generada
- [ ] Variables de entorno configuradas
- [ ] CloudWatch log groups creados
- [ ] API Gateway configurado
- [ ] DynamoDB tables creadas
- [ ] S3 buckets creados

## 🎯 Quick Start

```bash
# 1. Configurar AWS
aws configure

# 2. Generar configuración
python -c "from shared_lib.aws import create_serverless_config; create_serverless_config('mi-servicio')"

# 3. Deploy
serverless deploy
```

---

**Versión**: 1.0.0  
**Última actualización**: 2024




