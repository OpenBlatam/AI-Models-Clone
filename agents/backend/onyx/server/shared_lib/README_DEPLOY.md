# 🚀 Deployment con Un Solo Comando

## ⚡ Comando Único

```bash
# Opción 1: Script bash
./deploy lambda mi-servicio dev us-east-1

# Opción 2: Script PowerShell
.\deploy.ps1 lambda mi-servicio dev us-east-1

# Opción 3: Python
python run.py deploy lambda mi-servicio dev us-east-1

# Opción 4: Makefile
make deploy-lambda SERVICE_NAME=mi-servicio STAGE=prod
```

## 📋 Todos los Comandos Disponibles

### Deployment

```bash
# Lambda (Serverless)
./deploy lambda mi-servicio dev
make deploy-lambda SERVICE_NAME=mi-servicio

# ECS (Containers)
./deploy ecs mi-servicio
make deploy-ecs SERVICE_NAME=mi-servicio

# Local (Docker Compose)
./deploy local
make deploy-local
python run.py deploy local
```

### Setup

```bash
# Configurar recursos AWS
python run.py setup mi-servicio us-east-1
make setup SERVICE_NAME=mi-servicio
```

### Utilidades

```bash
# Tests
make test

# Limpiar
make clean

# Ayuda
make help
```

## 🎯 Ejemplos Completos

### Ejemplo 1: Deployment Lambda

```bash
# Un solo comando
./deploy lambda music-analyzer prod us-east-1

# Esto automáticamente:
# 1. Verifica prerequisitos
# 2. Configura recursos AWS
# 3. Genera configuraciones
# 4. Deploy
# 5. Muestra información
```

### Ejemplo 2: Deployment ECS

```bash
# Un solo comando
./deploy ecs music-analyzer dev us-east-1

# Esto automáticamente:
# 1. Verifica prerequisitos
# 2. Configura recursos AWS
# 3. Build Docker image
# 4. Push a ECR
# 5. Muestra información
```

### Ejemplo 3: Servicios Locales

```bash
# Un solo comando
./deploy local
# o
make deploy-local

# Inicia todos los servicios:
# - API (8030)
# - Redis (6379)
# - RabbitMQ (5672, UI 15672)
# - Prometheus (9090)
# - Grafana (3000)
# - Elasticsearch (9200)
# - Memcached (11211)
```

## 🔧 Variables de Entorno

```bash
# Configurar defaults
export SERVICE_NAME=mi-servicio
export STAGE=prod
export REGION=us-east-1

# Luego usar sin parámetros
./deploy lambda
```

## ✅ Lo que Hace Automáticamente

1. ✅ **Verifica prerequisitos**
   - AWS CLI
   - Credenciales AWS
   - Python
   - Docker (para ECS)
   - Serverless Framework (para Lambda)

2. ✅ **Configura recursos AWS**
   - DynamoDB tables
   - S3 buckets
   - CloudWatch log groups
   - ECR repositories

3. ✅ **Build y Deploy**
   - Genera configuraciones
   - Build Docker images (ECS)
   - Push a registries
   - Deploy a AWS

4. ✅ **Muestra información**
   - URLs del API
   - Comandos útiles
   - Próximos pasos

## 🎯 Comparación de Opciones

| Opción | Plataforma | Ventajas |
|--------|-----------|----------|
| `./deploy` | Linux/Mac | Más simple, bash nativo |
| `.\deploy.ps1` | Windows | PowerShell nativo |
| `python run.py` | Todas | Más flexible, Python |
| `make deploy` | Todas | Estándar, Makefile |

## 📚 Más Información

- **`aws/EASY_DEPLOY.md`** - Guía detallada
- **`aws/AWS_DEPLOYMENT_GUIDE.md`** - Guía completa
- **`QUICK_START_AWS.md`** - Inicio rápido

---

**¡Un comando y listo!** 🚀




