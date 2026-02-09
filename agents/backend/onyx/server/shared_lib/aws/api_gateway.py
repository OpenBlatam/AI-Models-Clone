"""
AWS API Gateway Integration
===========================

Integración completa con AWS API Gateway incluyendo:
- REST API creation
- HTTP API creation
- Usage plans
- API keys
- Request/Response transformation
- Integration con Lambda
"""

import logging
from typing import Dict, Optional, List, Any
import json

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None


class AWSAPIGatewayIntegration:
    """Integración con AWS API Gateway"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Configura cliente de boto3"""
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 no disponible. Instala con: pip install boto3")
            return
        
        try:
            self.client = boto3.client('apigateway', region_name=self.region)
            logger.info(f"AWS API Gateway client configurado para región: {self.region}")
        except Exception as e:
            logger.error(f"Error configurando cliente: {e}")
    
    def create_rest_api(
        self,
        name: str,
        description: str = "",
        endpoint_type: str = "REGIONAL"
    ) -> Optional[str]:
        """
        Crea un REST API en API Gateway
        
        Args:
            name: Nombre del API
            description: Descripción
            endpoint_type: REGIONAL, EDGE, o PRIVATE
            
        Returns:
            API ID o None si falla
        """
        if not self.client:
            return None
        
        try:
            response = self.client.create_rest_api(
                name=name,
                description=description,
                endpointConfiguration={
                    'types': [endpoint_type]
                },
                apiKeySource='HEADER',
                minimumCompressionSize=1024  # Comprimir respuestas > 1KB
            )
            
            api_id = response['id']
            logger.info(f"REST API creado: {api_id}")
            return api_id
        except ClientError as e:
            logger.error(f"Error creando REST API: {e}")
            return None
    
    def create_http_api(
        self,
        name: str,
        description: str = ""
    ) -> Optional[str]:
        """
        Crea un HTTP API (más económico que REST API)
        
        Args:
            name: Nombre del API
            description: Descripción
            
        Returns:
            API ID o None si falla
        """
        if not self.client:
            return None
        
        try:
            # HTTP API usa apigatewayv2
            v2_client = boto3.client('apigatewayv2', region_name=self.region)
            
            response = v2_client.create_api(
                Name=name,
                Description=description,
                ProtocolType='HTTP',
                CorsConfiguration={
                    'AllowOrigins': ['*'],
                    'AllowMethods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                    'AllowHeaders': ['*'],
                    'MaxAge': 3600
                }
            )
            
            api_id = response['ApiId']
            logger.info(f"HTTP API creado: {api_id}")
            return api_id
        except ClientError as e:
            logger.error(f"Error creando HTTP API: {e}")
            return None
    
    def create_lambda_integration(
        self,
        api_id: str,
        lambda_arn: str,
        method: str = "ANY",
        path: str = "{proxy+}"
    ) -> bool:
        """
        Crea integración Lambda para API Gateway
        
        Args:
            api_id: ID del API
            lambda_arn: ARN de la función Lambda
            method: Método HTTP
            path: Path del recurso
            
        Returns:
            True si éxito, False si falla
        """
        if not self.client:
            return False
        
        try:
            # Obtener root resource
            resources = self.client.get_resources(restApiId=api_id)
            root_resource = next(
                (r for r in resources['items'] if r['path'] == '/'),
                None
            )
            
            if not root_resource:
                logger.error("No se encontró root resource")
                return False
            
            # Crear recurso para proxy
            resource = self.client.create_resource(
                restApiId=api_id,
                parentId=root_resource['id'],
                pathPart=path.replace('{', '').replace('}', '').replace('+', '')
            )
            
            # Crear método
            self.client.put_method(
                restApiId=api_id,
                resourceId=resource['id'],
                httpMethod=method,
                authorizationType='NONE'
            )
            
            # Crear integración Lambda
            self.client.put_integration(
                restApiId=api_id,
                resourceId=resource['id'],
                httpMethod=method,
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=f"arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
            )
            
            logger.info(f"Integración Lambda creada para {lambda_arn}")
            return True
        except ClientError as e:
            logger.error(f"Error creando integración Lambda: {e}")
            return False
    
    def deploy_api(
        self,
        api_id: str,
        stage_name: str = "prod",
        stage_description: str = "Production stage"
    ) -> Optional[str]:
        """
        Despliega el API a un stage
        
        Args:
            api_id: ID del API
            stage_name: Nombre del stage
            stage_description: Descripción
            
        Returns:
            Deployment ID o None si falla
        """
        if not self.client:
            return None
        
        try:
            response = self.client.create_deployment(
                restApiId=api_id,
                stageName=stage_name,
                stageDescription=stage_description,
                description=f"Deployment to {stage_name}"
            )
            
            deployment_id = response['id']
            logger.info(f"API desplegado: {deployment_id}")
            return deployment_id
        except ClientError as e:
            logger.error(f"Error desplegando API: {e}")
            return None
    
    def create_usage_plan(
        self,
        api_id: str,
        stage_name: str,
        name: str = "default-plan",
        throttle_rate: float = 100.0,
        throttle_burst: int = 200,
        quota_limit: Optional[int] = None,
        quota_period: str = "DAY"
    ) -> Optional[str]:
        """
        Crea un usage plan con rate limiting
        
        Args:
            api_id: ID del API
            stage_name: Nombre del stage
            name: Nombre del plan
            throttle_rate: Rate limit por segundo
            throttle_burst: Burst limit
            quota_limit: Quota diaria/mensual
            quota_period: DAY o MONTH
            
        Returns:
            Usage Plan ID o None si falla
        """
        if not self.client:
            return None
        
        try:
            usage_plan_config = {
                "name": name,
                "apiStages": [{
                    "apiId": api_id,
                    "stage": stage_name
                }],
                "throttle": {
                    "rateLimit": throttle_rate,
                    "burstLimit": throttle_burst
                }
            }
            
            if quota_limit:
                usage_plan_config["quota"] = {
                    "limit": quota_limit,
                    "period": quota_period
                }
            
            response = self.client.create_usage_plan(**usage_plan_config)
            
            plan_id = response['id']
            logger.info(f"Usage plan creado: {plan_id}")
            return plan_id
        except ClientError as e:
            logger.error(f"Error creando usage plan: {e}")
            return None
    
    def create_api_key(
        self,
        name: str,
        description: str = "",
        enabled: bool = True
    ) -> Optional[tuple]:
        """
        Crea una API key
        
        Args:
            name: Nombre de la key
            description: Descripción
            enabled: Si está habilitada
            
        Returns:
            Tuple (key_id, key_value) o None si falla
        """
        if not self.client:
            return None
        
        try:
            response = self.client.create_api_key(
                name=name,
                description=description,
                enabled=enabled
            )
            
            key_id = response['id']
            key_value = response['value']
            
            logger.info(f"API key creada: {key_id}")
            return (key_id, key_value)
        except ClientError as e:
            logger.error(f"Error creando API key: {e}")
            return None
    
    def generate_swagger_spec(
        self,
        api_id: str,
        stage_name: str = "prod"
    ) -> Optional[Dict]:
        """
        Genera especificación Swagger del API
        
        Args:
            api_id: ID del API
            stage_name: Nombre del stage
            
        Returns:
            Swagger spec como dict o None si falla
        """
        if not self.client:
            return None
        
        try:
            response = self.client.get_export(
                restApiId=api_id,
                stageName=stage_name,
                exportType='swagger',
                accepts='application/json'
            )
            
            swagger_spec = json.loads(response['body'].read())
            logger.info("Swagger spec generado")
            return swagger_spec
        except ClientError as e:
            logger.error(f"Error generando Swagger spec: {e}")
            return None


# Instancia global
aws_api_gateway = AWSAPIGatewayIntegration()




