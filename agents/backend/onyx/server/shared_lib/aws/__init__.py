"""
AWS Integration Module
======================

Integraciones específicas para AWS:
- Lambda handlers
- API Gateway
- DynamoDB
- S3
- CloudWatch
- ECS/Fargate
- Serverless Framework
"""

from .lambda_handler import create_lambda_handler, LambdaHandler
from .api_gateway import AWSAPIGatewayIntegration
from .dynamodb import DynamoDBManager
from .s3 import S3Manager
from .cloudwatch import CloudWatchLogger, CloudWatchMetrics
from .ecs import ECSDeployment
from .serverless_config import ServerlessConfig, create_serverless_config

__all__ = [
    "create_lambda_handler",
    "LambdaHandler",
    "AWSAPIGatewayIntegration",
    "DynamoDBManager",
    "S3Manager",
    "CloudWatchLogger",
    "CloudWatchMetrics",
    "ECSDeployment",
    "ServerlessConfig",
    "create_serverless_config",
]




