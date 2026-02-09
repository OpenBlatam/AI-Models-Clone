# 🎯 START HERE - Guía de Inicio Rápido

## ⚡ Deployment en Un Comando

```bash
# AWS Lambda (Serverless)
./deploy lambda mi-servicio dev us-east-1

# AWS ECS (Containers)
./deploy ecs mi-servicio dev us-east-1

# Servicios Locales
./deploy local
```

## 📋 Prerequisitos (Una Vez)

```bash
# 1. AWS CLI
pip install awscli
aws configure

# 2. (Opcional) Serverless Framework para Lambda
npm install -g serverless serverless-python-requirements

# 3. (Opcional) Docker para ECS o local
# Instala Docker Desktop
```

## 🚀 Opciones de Comando

### Opción 1: Script Bash (Linux/Mac)

```bash
./deploy lambda mi-servicio dev
```

### Opción 2: Script PowerShell (Windows)

```powershell
.\deploy.ps1 lambda mi-servicio dev
```

### Opción 3: Python (Todas las plataformas)

```bash
python run.py deploy lambda mi-servicio dev
```

### Opción 4: Makefile

```bash
make deploy-lambda SERVICE_NAME=mi-servicio
```

## ✅ Lo que Hace Automáticamente

1. ✅ Verifica que todo esté instalado
2. ✅ Configura recursos AWS
3. ✅ Build y deploy
4. ✅ Muestra URL del API

## 🎯 Resultado

Después del comando:

```bash
# Ver información
serverless info --stage dev  # Para Lambda

# Probar API
curl https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/health
```

## 📚 Más Información

- **`README_DEPLOY.md`** - Todos los comandos disponibles
- **`aws/EASY_DEPLOY.md`** - Guía detallada paso a paso
- **`QUICK_START_AWS.md`** - Inicio rápido AWS
- **`README.md`** - Documentación completa

---

**¡Un comando y listo!** 🚀
