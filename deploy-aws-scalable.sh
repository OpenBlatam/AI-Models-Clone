#!/bin/bash

# Configuración
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="blatam-academy"
CLUSTER_NAME="blatam-cluster"
SERVICE_NAME="blatam-service"
MIN_CAPACITY=2
MAX_CAPACITY=20
DESIRED_CAPACITY=2
VPC_ID="vpc-xxxxx"  # Reemplazar con tu VPC ID
SUBNET_IDS="subnet-xxxxx,subnet-yyyyy"  # Reemplazar con tus subnet IDs

# Crear Application Load Balancer
ALB_ARN=$(aws elbv2 create-load-balancer \
  --name blatam-alb \
  --subnets ${SUBNET_IDS} \
  --security-groups sg-xxxxx \
  --scheme internet-facing \
  --type application \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

# Crear target group
TARGET_GROUP_ARN=$(aws elbv2 create-target-group \
  --name blatam-tg \
  --protocol HTTP \
  --port 3000 \
  --vpc-id ${VPC_ID} \
  --target-type ip \
  --health-check-path /api/health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 2 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Crear listener
aws elbv2 create-listener \
  --load-balancer-arn ${ALB_ARN} \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:${AWS_REGION}:${AWS_ACCOUNT_ID}:certificate/xxxxx \
  --default-actions Type=forward,TargetGroupArn=${TARGET_GROUP_ARN}

# Crear ElastiCache Redis
REDIS_ENDPOINT=$(aws elasticache create-replication-group \
  --replication-group-id blatam-redis \
  --replication-group-description "Redis cache for Blatam Academy" \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-clusters 2 \
  --automatic-failover-enabled \
  --query 'ReplicationGroup.PrimaryEndPoint.Address' \
  --output text)

# Crear CloudFront distribution
CLOUDFRONT_DOMAIN=$(aws cloudfront create-distribution \
  --cli-input-json file://cloudfront-config.json \
  --query 'Distribution.DomainName' \
  --output text)

# Crear repositorio ECR
aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} || \
aws ecr create-repository --repository-name ${ECR_REPOSITORY}

# Autenticar Docker con ECR
aws ecr get-login-password --region ${AWS_REGION} | \
docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Construir y subir imagen
docker build -t ${ECR_REPOSITORY} .
docker tag ${ECR_REPOSITORY}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest

# Crear cluster ECS
aws ecs create-cluster --cluster-name ${CLUSTER_NAME}

# Registrar task definition
TASK_DEFINITION=$(aws ecs register-task-definition \
  --cli-input-json file://aws-task-definition.json \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)

# Crear servicio con auto-scaling
aws ecs create-service \
  --cluster ${CLUSTER_NAME} \
  --service-name ${SERVICE_NAME} \
  --task-definition ${TASK_DEFINITION} \
  --desired-count ${DESIRED_CAPACITY} \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_IDS}],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=${TARGET_GROUP_ARN},containerName=blatam-academy,containerPort=3000" \
  --deployment-configuration "maximumPercent=200,minimumHealthyPercent=100" \
  --enable-execute-command

# Configurar auto-scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/${CLUSTER_NAME}/${SERVICE_NAME} \
  --min-capacity ${MIN_CAPACITY} \
  --max-capacity ${MAX_CAPACITY}

# Configurar políticas de auto-scaling
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/${CLUSTER_NAME}/${SERVICE_NAME} \
  --policy-name cpu-autoscaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 300
  }'

aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/${CLUSTER_NAME}/${SERVICE_NAME} \
  --policy-name memory-autoscaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageMemoryUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 300
  }'

aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/${CLUSTER_NAME}/${SERVICE_NAME} \
  --policy-name request-count-autoscaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 1000.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ALBRequestCountPerTarget"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 300
  }'

echo "Despliegue completado. La aplicación estará disponible en:"
echo "https://${CLOUDFRONT_DOMAIN}" 