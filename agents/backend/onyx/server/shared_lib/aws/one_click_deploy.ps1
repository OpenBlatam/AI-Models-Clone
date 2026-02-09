# One-Click Deploy para AWS (PowerShell)
# ======================================

param(
    [string]$ServiceName = "shared-lib-service",
    [string]$DeployType = "lambda",
    [string]$Stage = "dev",
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║   One-Click AWS Deployment            ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""
Write-Host "Service: $ServiceName" -ForegroundColor Yellow
Write-Host "Type: $DeployType" -ForegroundColor Yellow
Write-Host "Stage: $Stage" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host ""

# Verificar prerequisitos
Write-Host "🔍 Verificando prerequisitos..." -ForegroundColor Blue

# AWS CLI
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "❌ AWS CLI no encontrado" -ForegroundColor Red
    Write-Host "   Instala con: pip install awscli"
    exit 1
}
Write-Host "✅ AWS CLI" -ForegroundColor Green

# Credenciales
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "✅ AWS Credentials" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS credentials no configuradas" -ForegroundColor Red
    Write-Host "   Configura con: aws configure"
    exit 1
}

# Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python" -ForegroundColor Green

Write-Host ""

# Paso 1: Setup
Write-Host "📦 Paso 1: Configurando recursos AWS..." -ForegroundColor Blue
python aws/setup_aws.py $ServiceName $Region
Write-Host ""

# Paso 2: Deploy
Write-Host "🚀 Paso 2: Deploying aplicación..." -ForegroundColor Blue
switch ($DeployType) {
    "lambda" {
        if (-not (Get-Command serverless -ErrorAction SilentlyContinue)) {
            Write-Host "⚠️  Instalando Serverless Framework..." -ForegroundColor Yellow
            npm install -g serverless serverless-python-requirements
        }
        python aws/quick_deploy.py lambda $ServiceName $Stage $Region
    }
    "ecs" {
        if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
            Write-Host "❌ Docker no encontrado" -ForegroundColor Red
            exit 1
        }
        python aws/quick_deploy.py ecs $ServiceName $Region
    }
    default {
        Write-Host "❌ Tipo no válido: $DeployType" -ForegroundColor Red
        Write-Host "   Opciones: lambda, ecs"
        exit 1
    }
}

Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ Deployment Completado            ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

if ($DeployType -eq "lambda") {
    Write-Host "📊 Información del deployment:" -ForegroundColor Yellow
    serverless info --stage $Stage 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Ejecuta: serverless info --stage $Stage"
    }
}

Write-Host ""
Write-Host "📝 Próximos pasos:" -ForegroundColor Blue
Write-Host "   1. Verificar health: curl https://tu-api-url/health"
Write-Host "   2. Ver logs en CloudWatch"
Write-Host "   3. Configurar monitoring y alertas"
Write-Host ""




