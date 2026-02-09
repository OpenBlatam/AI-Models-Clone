#!/bin/bash
# Build Script para Docker
# ========================

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Variables
IMAGE_NAME="shared-lib"
VERSION="${1:-latest}"
BUILD_TYPE="${2:-prod}"

echo -e "${GREEN}🔨 Building Docker image...${NC}"

# Seleccionar Dockerfile según tipo
case $BUILD_TYPE in
  dev)
    DOCKERFILE="Dockerfile.dev"
    TAG="${IMAGE_NAME}:dev"
    ;;
  alpine)
    DOCKERFILE="Dockerfile.alpine"
    TAG="${IMAGE_NAME}:alpine-${VERSION}"
    ;;
  serverless)
    DOCKERFILE="Dockerfile.serverless"
    TAG="${IMAGE_NAME}:serverless-${VERSION}"
    ;;
  *)
    DOCKERFILE="Dockerfile"
    TAG="${IMAGE_NAME}:${VERSION}"
    ;;
esac

# Build
echo -e "${YELLOW}Building with ${DOCKERFILE}...${NC}"
docker build \
  -f docker/${DOCKERFILE} \
  -t ${TAG} \
  --build-arg VERSION=${VERSION} \
  ..

echo -e "${GREEN}✅ Image built: ${TAG}${NC}"

# Mostrar tamaño
echo -e "${YELLOW}Image size:${NC}"
docker images ${TAG} --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"




