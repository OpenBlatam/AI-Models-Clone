#!/bin/bash
# Run Script para Docker
# =====================

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Variables
IMAGE_NAME="shared-lib"
VERSION="${1:-latest}"
PORT="${2:-8030}"
ENV="${3:-development}"

echo -e "${GREEN}🚀 Running Docker container...${NC}"

# Ejecutar contenedor
docker run -d \
  --name ${IMAGE_NAME}-container \
  -p ${PORT}:8030 \
  -e ENVIRONMENT=${ENV} \
  -e LOG_LEVEL=INFO \
  ${IMAGE_NAME}:${VERSION}

echo -e "${GREEN}✅ Container running${NC}"
echo -e "${YELLOW}Access: http://localhost:${PORT}${NC}"
echo -e "${YELLOW}Logs: docker logs -f ${IMAGE_NAME}-container${NC}"




