# ⚡ Quick Start - AWS Deployment

## 🚀 Deployment en 1 Comando

```bash
# Lambda (Serverless) - Recomendado
./aws/one_click_deploy.sh mi-servicio lambda dev us-east-1

# ECS (Containers)
./aws/one_click_deploy.sh mi-servicio ecs dev us-east-1
```

## 📋 Prerequisitos (Una Vez)

```bash
# 1. Instalar AWS CLI
pip install awscli

# 2. Configurar credenciales
aws configure
# AWS Access Key ID: tu_key
# AWS Secret Access Key: tu_secret
# Default region: us-east-1
# Default output format: json

# 3. (Opcional) Instalar Serverless Framework para Lambda
npm install -g serverless serverless-python-requirements
```

## ✅ Eso es Todo!

El script hace automáticamente:
1. ✅ Verifica prerequisitos
2. ✅ Crea recursos AWS (DynamoDB, S3, CloudWatch, ECR)
3. ✅ Build y deploy
4. ✅ Muestra URL del API

## 🎯 Resultado

Después del deployment:

```bash
# Ver información
serverless info --stage dev  # Para Lambda

# Probar API
curl https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/health
```

## 📚 Más Información

- **`aws/EASY_DEPLOY.md`** - Guía detallada paso a paso
- **`aws/README_DEPLOY.md`** - Resumen de opciones
- **`aws/AWS_DEPLOYMENT_GUIDE.md`** - Guía completa

---

**¡Deployment en segundos!** 🚀




