# Build Script para Docker (PowerShell)
# =====================================

param(
    [string]$Version = "latest",
    [string]$BuildType = "prod"
)

$ErrorActionPreference = "Stop"

Write-Host "🔨 Building Docker image..." -ForegroundColor Green

# Variables
$ImageName = "shared-lib"
$Dockerfile = "Dockerfile"
$Tag = "${ImageName}:${Version}"

# Seleccionar Dockerfile
switch ($BuildType) {
    "dev" {
        $Dockerfile = "Dockerfile.dev"
        $Tag = "${ImageName}:dev"
    }
    "alpine" {
        $Dockerfile = "Dockerfile.alpine"
        $Tag = "${ImageName}:alpine-${Version}"
    }
    "serverless" {
        $Dockerfile = "Dockerfile.serverless"
        $Tag = "${ImageName}:serverless-${Version}"
    }
    default {
        $Dockerfile = "Dockerfile"
        $Tag = "${ImageName}:${Version}"
    }
}

# Build
Write-Host "Building with docker/${Dockerfile}..." -ForegroundColor Yellow
docker build `
    -f "docker/${Dockerfile}" `
    -t $Tag `
    --build-arg VERSION=$Version `
    ..

Write-Host "✅ Image built: $Tag" -ForegroundColor Green

# Mostrar tamaño
Write-Host "Image size:" -ForegroundColor Yellow
docker images $Tag --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"




