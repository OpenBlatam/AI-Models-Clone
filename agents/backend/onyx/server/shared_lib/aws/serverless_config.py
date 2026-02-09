"""
Serverless Configuration for AWS
=================================

Configuraciones para deployment serverless en AWS:
- Serverless Framework
- SAM (Serverless Application Model)
- Terraform
- CloudFormation
"""

import json
import yaml
from typing import Dict, Optional, List, Any
from pathlib import Path


class ServerlessConfig:
    """Configuración para Serverless Framework"""
    
    @staticmethod
    def generate_serverless_yml(
        service_name: str,
        runtime: str = "python3.11",
        region: str = "us-east-1",
        memory_size: int = 512,
        timeout: int = 30,
        environment_vars: Optional[Dict] = None
    ) -> str:
        """
        Genera archivo serverless.yml
        
        Args:
            service_name: Nombre del servicio
            runtime: Runtime de Python
            region: Región de AWS
            memory_size: Memoria en MB
            timeout: Timeout en segundos
            environment_vars: Variables de entorno
            
        Returns:
            Contenido del archivo serverless.yml
        """
        config = {
            "service": service_name,
            "frameworkVersion": "3",
            "provider": {
                "name": "aws",
                "runtime": runtime,
                "region": region,
                "stage": "${opt:stage, 'dev'}",
                "memorySize": memory_size,
                "timeout": timeout,
                "apiGateway": {
                    "shouldStartNameWithService": True,
                    "minimumCompressionSize": 1024
                },
                "environment": environment_vars or {},
                "iam": {
                    "role": {
                        "statements": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "logs:CreateLogGroup",
                                    "logs:CreateLogStream",
                                    "logs:PutLogEvents"
                                ],
                                "Resource": "arn:aws:logs:*:*:*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "dynamodb:GetItem",
                                    "dynamodb:PutItem",
                                    "dynamodb:UpdateItem",
                                    "dynamodb:DeleteItem",
                                    "dynamodb:Query",
                                    "dynamodb:Scan"
                                ],
                                "Resource": "arn:aws:dynamodb:*:*:table/*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "s3:GetObject",
                                    "s3:PutObject",
                                    "s3:DeleteObject"
                                ],
                                "Resource": "arn:aws:s3:::${self:custom.bucket}/*"
                            }
                        ]
                    }
                }
            },
            "functions": {
                "api": {
                    "handler": "lambda_function.lambda_handler",
                    "events": [
                        {
                            "http": {
                                "path": "{proxy+}",
                                "method": "ANY",
                                "cors": True
                            }
                        },
                        {
                            "http": {
                                "path": "/",
                                "method": "ANY",
                                "cors": True
                            }
                        }
                    ]
                }
            },
            "custom": {
                "bucket": "${self:service}-${self:provider.stage}-bucket"
            },
            "plugins": [
                "serverless-python-requirements"
            ]
        }
        
        return yaml.dump(config, default_flow_style=False, sort_keys=False)
    
    @staticmethod
    def generate_sam_template(
        service_name: str,
        runtime: str = "python3.11",
        memory_size: int = 512,
        timeout: int = 30
    ) -> Dict:
        """
        Genera template SAM (Serverless Application Model)
        
        Args:
            service_name: Nombre del servicio
            runtime: Runtime de Python
            memory_size: Memoria en MB
            timeout: Timeout en segundos
            
        Returns:
            Template SAM como dict
        """
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Transform": "AWS::Serverless-2016-10-31",
            "Description": f"{service_name} - Serverless API",
            "Globals": {
                "Function": {
                    "Runtime": runtime,
                    "MemorySize": memory_size,
                    "Timeout": timeout,
                    "Environment": {
                        "Variables": {
                            "PYTHONUNBUFFERED": "1"
                        }
                    }
                },
                "Api": {
                    "Cors": {
                        "AllowMethods": "'*'",
                        "AllowHeaders": "'*'",
                        "AllowOrigin": "'*'"
                    },
                    "MinimumCompressionSize": 1024
                }
            },
            "Resources": {
                "ApiFunction": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {
                        "CodeUri": ".",
                        "Handler": "lambda_function.lambda_handler",
                        "Events": {
                            "ApiEvent": {
                                "Type": "Api",
                                "Properties": {
                                    "Path": "/{proxy+}",
                                    "Method": "ANY"
                                }
                            },
                            "RootApiEvent": {
                                "Type": "Api",
                                "Properties": {
                                    "Path": "/",
                                    "Method": "ANY"
                                }
                            }
                        },
                        "Policies": [
                            "AWSLambdaBasicExecutionRole",
                            {
                                "DynamoDBCrudPolicy": {
                                    "TableName": "${DynamoDBTable}"
                                }
                            },
                            {
                                "S3ReadPolicy": {
                                    "BucketName": "${S3Bucket}"
                                }
                            }
                        ]
                    }
                },
                "DynamoDBTable": {
                    "Type": "AWS::DynamoDB::Table",
                    "Properties": {
                        "TableName": f"{service_name}-table",
                        "BillingMode": "PAY_PER_REQUEST",
                        "AttributeDefinitions": [
                            {
                                "AttributeName": "id",
                                "AttributeType": "S"
                            }
                        ],
                        "KeySchema": [
                            {
                                "AttributeName": "id",
                                "KeyType": "HASH"
                            }
                        ]
                    }
                },
                "S3Bucket": {
                    "Type": "AWS::S3::Bucket",
                    "Properties": {
                        "BucketName": f"{service_name}-bucket"
                    }
                }
            },
            "Outputs": {
                "ApiUrl": {
                    "Description": "API Gateway endpoint URL",
                    "Value": {
                        "Fn::Sub": "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
                    }
                },
                "DynamoDBTableName": {
                    "Description": "DynamoDB Table Name",
                    "Value": {"Ref": "DynamoDBTable"}
                }
            }
        }
        
        return template


def create_serverless_config(
    service_name: str,
    output_dir: str = ".",
    framework: str = "serverless"
) -> Dict[str, str]:
    """
    Crea archivos de configuración serverless
    
    Args:
        service_name: Nombre del servicio
        output_dir: Directorio de salida
        framework: "serverless" o "sam"
        
    Returns:
        Dict con paths de archivos creados
    """
    output_path = Path(output_dir)
    created_files = {}
    
    if framework == "serverless":
        # Serverless Framework
        serverless_yml = ServerlessConfig.generate_serverless_yml(service_name)
        serverless_path = output_path / "serverless.yml"
        serverless_path.write_text(serverless_yml)
        created_files["serverless.yml"] = str(serverless_path)
        
        # Lambda function template
        lambda_template = f'''"""
Lambda Function para {service_name}
"""
from mangum import Mangum
from main import app

handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    return handler(event, context)
'''
        lambda_path = output_path / "lambda_function.py"
        lambda_path.write_text(lambda_template)
        created_files["lambda_function.py"] = str(lambda_path)
    
    elif framework == "sam":
        # SAM Template
        sam_template = ServerlessConfig.generate_sam_template(service_name)
        sam_path = output_path / "template.yaml"
        sam_path.write_text(yaml.dump(sam_template, default_flow_style=False))
        created_files["template.yaml"] = str(sam_path)
    
    return created_files




