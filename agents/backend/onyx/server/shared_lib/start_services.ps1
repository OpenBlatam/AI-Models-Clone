# Script de Inicio de Servicios (PowerShell)
# ===========================================
# Inicia todos los servicios necesarios para la librería compartida

Write-Host "🚀 Iniciando servicios para shared_lib..." -ForegroundColor Green

# Verificar Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker no está instalado" -ForegroundColor Red
    exit 1
}

# Verificar Docker Compose
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose no está instalado" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker y Docker Compose disponibles" -ForegroundColor Green

# Crear docker-compose.yml si no existe
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "⚠️  docker-compose.yml no encontrado, creando uno básico..." -ForegroundColor Yellow
    
    $dockerComposeContent = @"
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=admin
      - RABBITMQ_DEFAULT_PASS=admin
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  redis_data:
  rabbitmq_data:
  prometheus_data:
  grafana_data:
"@
    
    $dockerComposeContent | Out-File -FilePath "docker-compose.yml" -Encoding UTF8
}

# Iniciar servicios
Write-Host "📦 Iniciando servicios con Docker Compose..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "✅ Servicios iniciados" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Servicios disponibles:"
Write-Host "  - Redis: localhost:6379"
Write-Host "  - RabbitMQ: localhost:5672"
Write-Host "  - RabbitMQ Management: http://localhost:15672 (admin/admin)"
Write-Host "  - Prometheus: http://localhost:9090"
Write-Host "  - Grafana: http://localhost:3000 (admin/admin)"
Write-Host ""
Write-Host "Para detener: docker-compose down"




