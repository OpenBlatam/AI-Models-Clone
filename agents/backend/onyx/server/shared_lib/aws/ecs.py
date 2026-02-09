"""
AWS ECS/Fargate Deployment
===========================

Configuraciones para deployment en ECS/Fargate:
- Task definitions
- Service definitions
- Load balancer configuration
- Auto-scaling
"""

import json
from typing import Dict, Optional, List, Any


class ECSDeployment:
    """Configuración para deployment en ECS/Fargate"""
    
    @staticmethod
    def generate_task_definition(
        family: str,
        image: str,
        cpu: str = "256",
        memory: str = "512",
        port: int = 8030,
        environment_vars: Optional[Dict] = None,
        secrets: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Genera task definition para ECS
        
        Args:
            family: Nombre de la familia
            image: URI de la imagen Docker
            cpu: CPU units (256 = 0.25 vCPU)
            memory: Memoria en MB
            port: Puerto del contenedor
            environment_vars: Variables de entorno
            secrets: Secrets desde Secrets Manager
            
        Returns:
            Task definition como dict
        """
        task_def = {
            "family": family,
            "networkMode": "awsvpc",
            "requiresCompatibilities": ["FARGATE"],
            "cpu": cpu,
            "memory": memory,
            "containerDefinitions": [
                {
                    "name": family,
                    "image": image,
                    "essential": True,
                    "portMappings": [
                        {
                            "containerPort": port,
                            "protocol": "tcp"
                        }
                    ],
                    "environment": [
                        {"name": k, "value": v}
                        for k, v in (environment_vars or {}).items()
                    ],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": f"/ecs/{family}",
                            "awslogs-region": "us-east-1",
                            "awslogs-stream-prefix": "ecs"
                        }
                    },
                    "healthCheck": {
                        "command": [
                            "CMD-SHELL",
                            f"curl -f http://localhost:{port}/health || exit 1"
                        ],
                        "interval": 30,
                        "timeout": 5,
                        "retries": 3,
                        "startPeriod": 60
                    }
                }
            ]
        }
        
        if secrets:
            task_def["containerDefinitions"][0]["secrets"] = secrets
        
        return task_def
    
    @staticmethod
    def generate_service_definition(
        cluster: str,
        service_name: str,
        task_definition: str,
        desired_count: int = 2,
        subnets: List[str] = None,
        security_groups: List[str] = None,
        load_balancer_arn: Optional[str] = None,
        target_group_arn: Optional[str] = None
    ) -> Dict:
        """
        Genera service definition para ECS
        
        Args:
            cluster: Nombre del cluster
            service_name: Nombre del servicio
            task_definition: ARN de la task definition
            desired_count: Número deseado de tareas
            subnets: Lista de subnet IDs
            security_groups: Lista de security group IDs
            load_balancer_arn: ARN del load balancer
            target_group_arn: ARN del target group
            
        Returns:
            Service definition como dict
        """
        service_def = {
            "cluster": cluster,
            "serviceName": service_name,
            "taskDefinition": task_definition,
            "desiredCount": desired_count,
            "launchType": "FARGATE",
            "networkConfiguration": {
                "awsvpcConfiguration": {
                    "subnets": subnets or [],
                    "securityGroups": security_groups or [],
                    "assignPublicIp": "ENABLED"
                }
            },
            "deploymentConfiguration": {
                "maximumPercent": 200,
                "minimumHealthyPercent": 100
            },
            "healthCheckGracePeriodSeconds": 60
        }
        
        if load_balancer_arn and target_group_arn:
            service_def["loadBalancers"] = [
                {
                    "targetGroupArn": target_group_arn,
                    "containerName": service_name,
                    "containerPort": 8030
                }
            ]
        
        return service_def
    
    @staticmethod
    def generate_auto_scaling_config(
        service_name: str,
        min_capacity: int = 1,
        max_capacity: int = 10,
        target_cpu: int = 70,
        target_memory: int = 80
    ) -> Dict:
        """
        Genera configuración de auto-scaling
        
        Args:
            service_name: Nombre del servicio
            min_capacity: Capacidad mínima
            max_capacity: Capacidad máxima
            target_cpu: Target de CPU %
            target_memory: Target de memoria %
            
        Returns:
            Auto-scaling config como dict
        """
        return {
            "ServiceNamespace": "ecs",
            "ServiceName": service_name,
            "ScalableDimension": "ecs:service:DesiredCount",
            "MinCapacity": min_capacity,
            "MaxCapacity": max_capacity,
            "TargetTrackingScalingPolicies": [
                {
                    "PolicyName": "cpu-scaling",
                    "TargetTrackingScalingPolicyConfiguration": {
                        "PredefinedMetricSpecification": {
                            "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
                        },
                        "TargetValue": target_cpu,
                        "ScaleInCooldown": 300,
                        "ScaleOutCooldown": 60
                    }
                },
                {
                    "PolicyName": "memory-scaling",
                    "TargetTrackingScalingPolicyConfiguration": {
                        "PredefinedMetricSpecification": {
                            "PredefinedMetricType": "ECSServiceAverageMemoryUtilization"
                        },
                        "TargetValue": target_memory,
                        "ScaleInCooldown": 300,
                        "ScaleOutCooldown": 60
                    }
                }
            ]
        }




