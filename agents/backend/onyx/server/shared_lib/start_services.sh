#!/bin/bash
# Script de Inicio de Servicios
# ==============================
# Inicia todos los servicios necesarios para la librería compartida

set -e

echo "🚀 Iniciando servicios para shared_lib..."

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

echo -e "${GREEN}✅ Docker y Docker Compose disponibles${NC}"

# Iniciar servicios con Docker Compose
echo -e "${YELLOW}📦 Iniciando servicios con Docker Compose...${NC}"

# Crear docker-compose.yml si no existe
if [ ! -f "docker-compose.yml" ]; then
    echo "⚠️  docker-compose.yml no encontrado, creando uno básico..."
    cat > docker-compose.yml << EOF
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
EOF
fi

# Iniciar servicios
docker-compose up -d

echo -e "${GREEN}✅ Servicios iniciados${NC}"
echo ""
echo "📊 Servicios disponibles:"
echo "  - Redis: localhost:6379"
echo "  - RabbitMQ: localhost:5672"
echo "  - RabbitMQ Management: http://localhost:15672 (admin/admin)"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "Para detener: docker-compose down"




