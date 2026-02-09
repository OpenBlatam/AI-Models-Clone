# Comando Único de Deployment (PowerShell)
# =======================================
# Uso: .\deploy.ps1 [tipo] [servicio] [stage] [region]
# Ejemplo: .\deploy.ps1 lambda mi-servicio prod us-east-1

param(
    [string]$DeployType = "lambda",
    [string]$ServiceName = "shared-lib-service",
    [string]$Stage = "dev",
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║   🚀 Deployment Automatizado              ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""
Write-Host "Tipo: $DeployType" -ForegroundColor Yellow
Write-Host "Servicio: $ServiceName" -ForegroundColor Yellow
Write-Host "Stage: $Stage" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host ""

# Función para verificar comandos
function Test-Command {
    param([string]$Command, [string]$Name, [string]$InstallCmd)
    
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        Write-Host "❌ $Name no está instalado" -ForegroundColor Red
        Write-Host "   Instala con: $InstallCmd"
        return $false
    }
    return $true
}

# Verificar prerequisitos
Write-Host "🔍 Verificando prerequisitos..." -ForegroundColor Blue

# AWS CLI
if (-not (Test-Command "aws" "AWS CLI" "pip install awscli")) {
    exit 1
}
Write-Host "✅ AWS CLI" -ForegroundColor Green

# Credenciales AWS
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "✅ AWS Credentials" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS credentials no configuradas" -ForegroundColor Red
    Write-Host "   Configura con: aws configure"
    exit 1
}

# Python
if (-not (Test-Command "python" "Python" "Instala Python 3.11+")) {
    exit 1
}
Write-Host "✅ Python" -ForegroundColor Green

# Verificaciones específicas
switch ($DeployType) {
    "lambda" {
        if (-not (Test-Command "serverless" "Serverless Framework" "npm install -g serverless")) {
            Write-Host "⚠️  Instalando Serverless Framework..." -ForegroundColor Yellow
            npm install -g serverless serverless-python-requirements
        }
        Write-Host "✅ Serverless Framework" -ForegroundColor Green
    }
    "ecs" {
        if (-not (Test-Command "docker" "Docker" "Instala Docker Desktop")) {
            exit 1
        }
        Write-Host "✅ Docker" -ForegroundColor Green
    }
    default {
        Write-Host "❌ Tipo no válido: $DeployType" -ForegroundColor Red
        Write-Host "   Opciones: lambda, ecs, local"
        exit 1
    }
}

Write-Host ""

# Paso 1: Setup
Write-Host "📦 Paso 1/3: Configurando recursos AWS..." -ForegroundColor Blue
python aws/setup_aws.py $ServiceName $Region
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Algunos recursos pueden ya existir, continuando..." -ForegroundColor Yellow
}
Write-Host ""

# Paso 2: Build
if ($DeployType -eq "ecs") {
    Write-Host "🔨 Paso 2/3: Building Docker image..." -ForegroundColor Blue
    docker build -f docker/Dockerfile -t "${ServiceName}:latest" ..
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error en build" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Build completado" -ForegroundColor Green
    Write-Host ""
}

# Paso 3: Deploy
Write-Host "🚀 Paso 3/3: Deploying..." -ForegroundColor Blue
switch ($DeployType) {
    "lambda" {
        python aws/quick_deploy.py lambda $ServiceName $Stage $Region
    }
    "ecs" {
        python aws/quick_deploy.py ecs $ServiceName $Region
    }
    "local" {
        Write-Host "📦 Iniciando servicios locales con Docker Compose..." -ForegroundColor Yellow
        Set-Location docker
        docker-compose up -d
        Write-Host "✅ Servicios iniciados" -ForegroundColor Green
        Write-Host "   API: http://localhost:8030" -ForegroundColor Yellow
        Write-Host "   Docs: http://localhost:8030/docs" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ Deployment Completado                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Mostrar información
if ($DeployType -eq "lambda") {
    Write-Host "📊 Información del deployment:" -ForegroundColor Yellow
    serverless info --stage $Stage 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Ejecuta: serverless info --stage $Stage"
    }
} elseif ($DeployType -eq "ecs") {
    Write-Host "📝 Siguiente paso:" -ForegroundColor Yellow
    Write-Host "   Crea task definition y service en ECS"
    Write-Host "   Ver: aws/AWS_DEPLOYMENT_GUIDE.md"
}

Write-Host ""
Write-Host "📚 Documentación:" -ForegroundColor Blue
Write-Host "   - aws/EASY_DEPLOY.md"
Write-Host "   - aws/AWS_DEPLOYMENT_GUIDE.md"
Write-Host ""




