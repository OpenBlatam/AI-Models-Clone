# Script de Deployment Automático para AWS (PowerShell)
# =====================================================

param(
    [string]$DeploymentType = "lambda",
    [string]$Stage = "dev",
    [string]$ServiceName = $env:SERVICE_NAME,
    [string]$AwsRegion = $env:AWS_REGION
)

$ErrorActionPreference = "Stop"

# Valores por defecto
if (-not $ServiceName) { $ServiceName = "shared-lib-service" }
if (-not $AwsRegion) { $AwsRegion = "us-east-1" }

Write-Host "🚀 AWS Deployment Script" -ForegroundColor Green
Write-Host "Service: $ServiceName" -ForegroundColor Yellow
Write-Host "Region: $AwsRegion" -ForegroundColor Yellow
Write-Host "Type: $DeploymentType" -ForegroundColor Yellow
Write-Host "Stage: $Stage" -ForegroundColor Yellow
Write-Host ""

# Verificar AWS CLI
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "❌ AWS CLI no está instalado" -ForegroundColor Red
    Write-Host "Instala con: pip install awscli"
    exit 1
}

# Verificar credenciales
try {
    aws sts get-caller-identity | Out-Null
} catch {
    Write-Host "❌ AWS credentials no configuradas" -ForegroundColor Red
    Write-Host "Configura con: aws configure"
    exit 1
}

switch ($DeploymentType) {
    "lambda" {
        Write-Host "📦 Deploying to AWS Lambda..." -ForegroundColor Green
        
        # Verificar Serverless Framework
        if (-not (Get-Command serverless -ErrorAction SilentlyContinue)) {
            Write-Host "⚠️  Serverless Framework no encontrado, instalando..." -ForegroundColor Yellow
            npm install -g serverless serverless-python-requirements
        }
        
        # Generar configuración
        if (-not (Test-Path "serverless.yml")) {
            Write-Host "📝 Generando serverless.yml..." -ForegroundColor Yellow
            python -c "from shared_lib.aws import create_serverless_config; create_serverless_config('$ServiceName', '.', 'serverless')"
        }
        
        # Deploy
        Write-Host "🚀 Deploying..." -ForegroundColor Green
        serverless deploy --stage $Stage --region $AwsRegion
        
        Write-Host "✅ Deployment completado" -ForegroundColor Green
        serverless info --stage $Stage
    }
    
    "ecs" {
        Write-Host "📦 Deploying to AWS ECS..." -ForegroundColor Green
        
        # Build Docker image
        Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
        docker build -f ../docker/Dockerfile -t "${ServiceName}:latest" ..
        
        # Get AWS account ID
        $AccountId = (aws sts get-caller-identity --query Account --output text)
        $EcrRepo = "${AccountId}.dkr.ecr.${AwsRegion}.amazonaws.com/${ServiceName}"
        
        # Create ECR repository
        Write-Host "📦 Creando ECR repository..." -ForegroundColor Yellow
        try {
            aws ecr describe-repositories --repository-names $ServiceName --region $AwsRegion | Out-Null
        } catch {
            aws ecr create-repository --repository-name $ServiceName --region $AwsRegion
        }
        
        # Login to ECR
        Write-Host "🔐 Login a ECR..." -ForegroundColor Yellow
        $LoginCommand = aws ecr get-login-password --region $AwsRegion
        $LoginCommand | docker login --username AWS --password-stdin $EcrRepo
        
        # Tag and push
        Write-Host "📤 Pushing image..." -ForegroundColor Yellow
        docker tag "${ServiceName}:latest" "${EcrRepo}:latest"
        docker push "${EcrRepo}:latest"
        
        Write-Host "✅ Image pushed to ECR" -ForegroundColor Green
    }
    
    default {
        Write-Host "❌ Tipo de deployment no válido: $DeploymentType" -ForegroundColor Red
        Write-Host "Opciones: lambda, ecs, ec2"
        exit 1
    }
}

Write-Host ""
Write-Host "✅ Proceso completado" -ForegroundColor Green




