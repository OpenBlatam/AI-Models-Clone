#!/bin/bash
# Script de Deployment Automático para AWS
# =========================================
# Facilita el deployment en AWS Lambda, ECS, o EC2

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Variables
SERVICE_NAME="${SERVICE_NAME:-shared-lib-service}"
AWS_REGION="${AWS_REGION:-us-east-1}"
DEPLOYMENT_TYPE="${1:-lambda}"  # lambda, ecs, ec2
STAGE="${2:-dev}"

echo -e "${GREEN}🚀 AWS Deployment Script${NC}"
echo -e "${YELLOW}Service: ${SERVICE_NAME}${NC}"
echo -e "${YELLOW}Region: ${AWS_REGION}${NC}"
echo -e "${YELLOW}Type: ${DEPLOYMENT_TYPE}${NC}"
echo -e "${YELLOW}Stage: ${STAGE}${NC}"
echo ""

# Verificar AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI no está instalado${NC}"
    echo "Instala con: pip install awscli"
    exit 1
fi

# Verificar credenciales
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials no configuradas${NC}"
    echo "Configura con: aws configure"
    exit 1
fi

case $DEPLOYMENT_TYPE in
    lambda)
        echo -e "${GREEN}📦 Deploying to AWS Lambda...${NC}"
        
        # Verificar Serverless Framework
        if ! command -v serverless &> /dev/null; then
            echo -e "${YELLOW}⚠️  Serverless Framework no encontrado, instalando...${NC}"
            npm install -g serverless serverless-python-requirements
        fi
        
        # Generar configuración si no existe
        if [ ! -f "serverless.yml" ]; then
            echo -e "${YELLOW}📝 Generando serverless.yml...${NC}"
            python3 -c "
from shared_lib.aws import create_serverless_config
create_serverless_config('${SERVICE_NAME}', '.', 'serverless')
"
        fi
        
        # Deploy
        echo -e "${GREEN}🚀 Deploying...${NC}"
        serverless deploy --stage ${STAGE} --region ${AWS_REGION}
        
        echo -e "${GREEN}✅ Deployment completado${NC}"
        serverless info --stage ${STAGE}
        ;;
        
    ecs)
        echo -e "${GREEN}📦 Deploying to AWS ECS...${NC}"
        
        # Build Docker image
        echo -e "${YELLOW}🔨 Building Docker image...${NC}"
        docker build -f ../docker/Dockerfile -t ${SERVICE_NAME}:latest ..
        
        # Get AWS account ID
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        ECR_REPO="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${SERVICE_NAME}"
        
        # Create ECR repository if not exists
        echo -e "${YELLOW}📦 Creando ECR repository...${NC}"
        aws ecr describe-repositories --repository-names ${SERVICE_NAME} --region ${AWS_REGION} 2>/dev/null || \
        aws ecr create-repository --repository-name ${SERVICE_NAME} --region ${AWS_REGION}
        
        # Login to ECR
        echo -e "${YELLOW}🔐 Login a ECR...${NC}"
        aws ecr get-login-password --region ${AWS_REGION} | \
            docker login --username AWS --password-stdin ${ECR_REPO}
        
        # Tag and push
        echo -e "${YELLOW}📤 Pushing image...${NC}"
        docker tag ${SERVICE_NAME}:latest ${ECR_REPO}:latest
        docker push ${ECR_REPO}:latest
        
        echo -e "${GREEN}✅ Image pushed to ECR${NC}"
        echo -e "${YELLOW}📝 Siguiente paso: Crear task definition y service en ECS${NC}"
        echo -e "${YELLOW}   Usa: python3 -c \"from shared_lib.aws import ECSDeployment; import json; print(json.dumps(ECSDeployment.generate_task_definition('${SERVICE_NAME}', '${ECR_REPO}:latest'), indent=2))\" > task-definition.json${NC}"
        ;;
        
    ec2)
        echo -e "${GREEN}📦 Deploying to AWS EC2...${NC}"
        echo -e "${YELLOW}⚠️  EC2 deployment requiere configuración manual${NC}"
        echo -e "${YELLOW}   Usa docker-compose o sistema de init para ejecutar contenedores${NC}"
        ;;
        
    *)
        echo -e "${RED}❌ Tipo de deployment no válido: ${DEPLOYMENT_TYPE}${NC}"
        echo "Opciones: lambda, ecs, ec2"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Proceso completado${NC}"




