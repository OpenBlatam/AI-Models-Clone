#!/bin/bash
# One-Click Deploy para AWS
# =========================
# Deployment completo en un solo comando

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables
SERVICE_NAME="${1:-shared-lib-service}"
DEPLOY_TYPE="${2:-lambda}"
STAGE="${3:-dev}"
REGION="${4:-us-east-1}"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   One-Click AWS Deployment            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Service: ${SERVICE_NAME}${NC}"
echo -e "${YELLOW}Type: ${DEPLOY_TYPE}${NC}"
echo -e "${YELLOW}Stage: ${STAGE}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo ""

# Verificar prerequisitos
echo -e "${BLUE}🔍 Verificando prerequisitos...${NC}"

# AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI no encontrado${NC}"
    echo "   Instala con: pip install awscli"
    exit 1
fi
echo -e "${GREEN}✅ AWS CLI${NC}"

# Credenciales
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials no configuradas${NC}"
    echo "   Configura con: aws configure"
    exit 1
fi
echo -e "${GREEN}✅ AWS Credentials${NC}"

# Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3${NC}"

echo ""

# Paso 1: Setup AWS Resources
echo -e "${BLUE}📦 Paso 1: Configurando recursos AWS...${NC}"
python3 aws/setup_aws.py ${SERVICE_NAME} ${REGION}
echo ""

# Paso 2: Deploy
echo -e "${BLUE}🚀 Paso 2: Deploying aplicación...${NC}"
case $DEPLOY_TYPE in
    lambda)
        if ! command -v serverless &> /dev/null; then
            echo -e "${YELLOW}⚠️  Instalando Serverless Framework...${NC}"
            npm install -g serverless serverless-python-requirements
        fi
        python3 aws/quick_deploy.py lambda ${SERVICE_NAME} ${STAGE} ${REGION}
        ;;
    ecs)
        if ! command -v docker &> /dev/null; then
            echo -e "${RED}❌ Docker no encontrado${NC}"
            exit 1
        fi
        python3 aws/quick_deploy.py ecs ${SERVICE_NAME} ${REGION}
        ;;
    *)
        echo -e "${RED}❌ Tipo no válido: ${DEPLOY_TYPE}${NC}"
        echo "   Opciones: lambda, ecs"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ Deployment Completado            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Mostrar información
if [ "$DEPLOY_TYPE" = "lambda" ]; then
    echo -e "${YELLOW}📊 Información del deployment:${NC}"
    serverless info --stage ${STAGE} 2>/dev/null || echo "   Ejecuta: serverless info --stage ${STAGE}"
fi

echo ""
echo -e "${BLUE}📝 Próximos pasos:${NC}"
echo "   1. Verificar health: curl https://tu-api-url/health"
echo "   2. Ver logs en CloudWatch"
echo "   3. Configurar monitoring y alertas"
echo ""




