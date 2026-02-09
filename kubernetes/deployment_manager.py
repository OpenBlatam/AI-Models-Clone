"""
Kubernetes Deployment Manager
============================

This module provides Kubernetes deployment management capabilities for the Instagram Captions API v10.0.
It handles container deployment, scaling, and orchestration.

Author: AI Assistant
Version: 10.1
"""

import yaml
import json
import time
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class DeploymentStatus(Enum):
    """Deployment status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    SUCCEEDED = "succeeded"
    UNKNOWN = "unknown"

@dataclass
class DeploymentConfig:
    """Deployment configuration data class."""
    name: str
    namespace: str
    replicas: int
    image: str
    image_tag: str
    ports: List[int]
    environment_vars: Dict[str, str]
    resource_limits: Dict[str, str]
    resource_requests: Dict[str, str]
    health_check_path: str
    liveness_probe: bool = True
    readiness_probe: bool = True
    auto_scaling: bool = False
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_utilization: int = 70

class DeploymentManager:
    """
    Kubernetes Deployment Manager implementation.
    
    Provides container deployment, scaling, and orchestration capabilities
    with support for auto-scaling and health monitoring.
    """
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """
        Initialize the deployment manager.
        
        Args:
            kubeconfig_path: Path to kubeconfig file
        """
        try:
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path)
            else:
                config.load_incluster_config()
            
            self.apps_v1 = client.AppsV1Api()
            self.core_v1 = client.CoreV1Api()
            self.autoscaling_v1 = client.AutoscalingV1Api()
            
            logger.info("Kubernetes client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise
    
    async def create_deployment(self, deployment_config: DeploymentConfig) -> bool:
        """
        Create a Kubernetes deployment.
        
        Args:
            deployment_config: Deployment configuration
            
        Returns:
            True if deployment created successfully, False otherwise
        """
        try:
            # Create deployment object
            deployment = self._create_deployment_object(deployment_config)
            
            # Create the deployment
            result = self.apps_v1.create_namespaced_deployment(
                namespace=deployment_config.namespace,
                body=deployment
            )
            
            logger.info(f"Deployment {deployment_config.name} created successfully")
            
            # Create HorizontalPodAutoscaler if auto-scaling is enabled
            if deployment_config.auto_scaling:
                await self._create_horizontal_pod_autoscaler(deployment_config)
            
            return True
            
        except ApiException as e:
            logger.error(f"Failed to create deployment {deployment_config.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error creating deployment {deployment_config.name}: {e}")
            return False
    
    async def update_deployment(self, deployment_config: DeploymentConfig) -> bool:
        """
        Update an existing Kubernetes deployment.
        
        Args:
            deployment_config: Updated deployment configuration
            
        Returns:
            True if deployment updated successfully, False otherwise
        """
        try:
            # Get current deployment
            current_deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_config.name,
                namespace=deployment_config.namespace
            )
            
            # Update deployment object
            updated_deployment = self._create_deployment_object(deployment_config)
            updated_deployment.metadata.resource_version = current_deployment.metadata.resource_version
            
            # Update the deployment
            result = self.apps_v1.replace_namespaced_deployment(
                name=deployment_config.name,
                namespace=deployment_config.namespace,
                body=updated_deployment
            )
            
            logger.info(f"Deployment {deployment_config.name} updated successfully")
            return True
            
        except ApiException as e:
            logger.error(f"Failed to update deployment {deployment_config.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating deployment {deployment_config.name}: {e}")
            return False
    
    async def delete_deployment(self, name: str, namespace: str) -> bool:
        """
        Delete a Kubernetes deployment.
        
        Args:
            name: Deployment name
            namespace: Deployment namespace
            
        Returns:
            True if deployment deleted successfully, False otherwise
        """
        try:
            # Delete the deployment
            result = self.apps_v1.delete_namespaced_deployment(
                name=name,
                namespace=namespace
            )
            
            logger.info(f"Deployment {name} deleted successfully")
            return True
            
        except ApiException as e:
            logger.error(f"Failed to delete deployment {name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting deployment {name}: {e}")
            return False
    
    async def scale_deployment(self, name: str, namespace: str, replicas: int) -> bool:
        """
        Scale a Kubernetes deployment.
        
        Args:
            name: Deployment name
            namespace: Deployment namespace
            replicas: Number of replicas
            
        Returns:
            True if scaling successful, False otherwise
        """
        try:
            # Create scale object
            scale = client.V1Scale(
                spec=client.V1ScaleSpec(replicas=replicas)
            )
            
            # Scale the deployment
            result = self.apps_v1.patch_namespaced_deployment_scale(
                name=name,
                namespace=namespace,
                body=scale
            )
            
            logger.info(f"Deployment {name} scaled to {replicas} replicas")
            return True
            
        except ApiException as e:
            logger.error(f"Failed to scale deployment {name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error scaling deployment {name}: {e}")
            return False
    
    async def get_deployment_status(self, name: str, namespace: str) -> Optional[DeploymentStatus]:
        """
        Get deployment status.
        
        Args:
            name: Deployment name
            namespace: Deployment namespace
            
        Returns:
            Deployment status or None if not found
        """
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=name,
                namespace=namespace
            )
            
            if deployment.status.conditions:
                for condition in deployment.status.conditions:
                    if condition.type == "Available" and condition.status == "True":
                        return DeploymentStatus.RUNNING
                    elif condition.type == "Progressing" and condition.status == "False":
                        return DeploymentStatus.FAILED
            
            return DeploymentStatus.PENDING
            
        except ApiException as e:
            logger.error(f"Failed to get deployment status for {name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting deployment status for {name}: {e}")
            return None
    
    async def get_deployment_info(self, name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed deployment information.
        
        Args:
            name: Deployment name
            namespace: Deployment namespace
            
        Returns:
            Deployment information dictionary or None if not found
        """
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=name,
                namespace=namespace
            )
            
            return {
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "replicas": deployment.spec.replicas,
                "available_replicas": deployment.status.available_replicas,
                "ready_replicas": deployment.status.ready_replicas,
                "updated_replicas": deployment.status.updated_replicas,
                "image": deployment.spec.template.spec.containers[0].image,
                "creation_timestamp": deployment.metadata.creation_timestamp.isoformat(),
                "labels": deployment.metadata.labels,
                "annotations": deployment.metadata.annotations
            }
            
        except ApiException as e:
            logger.error(f"Failed to get deployment info for {name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting deployment info for {name}: {e}")
            return None
    
    async def list_deployments(self, namespace: str) -> List[Dict[str, Any]]:
        """
        List all deployments in a namespace.
        
        Args:
            namespace: Namespace to list deployments from
            
        Returns:
            List of deployment information dictionaries
        """
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace=namespace)
            
            deployment_list = []
            for deployment in deployments.items:
                deployment_list.append({
                    "name": deployment.metadata.name,
                    "namespace": deployment.metadata.namespace,
                    "replicas": deployment.spec.replicas,
                    "available_replicas": deployment.status.available_replicas,
                    "ready_replicas": deployment.status.ready_replicas,
                    "image": deployment.spec.template.spec.containers[0].image,
                    "creation_timestamp": deployment.metadata.creation_timestamp.isoformat()
                })
            
            return deployment_list
            
        except ApiException as e:
            logger.error(f"Failed to list deployments in namespace {namespace}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error listing deployments in namespace {namespace}: {e}")
            return []
    
    async def wait_for_deployment_ready(self, name: str, namespace: str, timeout: int = 300) -> bool:
        """
        Wait for deployment to be ready.
        
        Args:
            name: Deployment name
            namespace: Deployment namespace
            timeout: Timeout in seconds
            
        Returns:
            True if deployment is ready within timeout, False otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = await self.get_deployment_status(name, namespace)
            
            if status == DeploymentStatus.RUNNING:
                logger.info(f"Deployment {name} is ready")
                return True
            elif status == DeploymentStatus.FAILED:
                logger.error(f"Deployment {name} failed")
                return False
            
            await asyncio.sleep(5)
        
        logger.warning(f"Deployment {name} not ready within {timeout} seconds")
        return False
    
    def _create_deployment_object(self, deployment_config: DeploymentConfig) -> client.V1Deployment:
        """Create Kubernetes deployment object."""
        # Create container
        container = client.V1Container(
            name=deployment_config.name,
            image=f"{deployment_config.image}:{deployment_config.image_tag}",
            ports=[client.V1ContainerPort(container_port=port) for port in deployment_config.ports],
            env=[client.V1EnvVar(name=k, value=v) for k, v in deployment_config.environment_vars.items()],
            resources=client.V1ResourceRequirements(
                limits=deployment_config.resource_limits,
                requests=deployment_config.resource_requests
            )
        )
        
        # Add health checks
        if deployment_config.liveness_probe:
            container.liveness_probe = client.V1Probe(
                http_get=client.V1HTTPGetAction(
                    path=deployment_config.health_check_path,
                    port=deployment_config.ports[0]
                ),
                initial_delay_seconds=30,
                period_seconds=10
            )
        
        if deployment_config.readiness_probe:
            container.readiness_probe = client.V1Probe(
                http_get=client.V1HTTPGetAction(
                    path=deployment_config.health_check_path,
                    port=deployment_config.ports[0]
                ),
                initial_delay_seconds=5,
                period_seconds=5
            )
        
        # Create pod template
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": deployment_config.name}),
            spec=client.V1PodSpec(containers=[container])
        )
        
        # Create deployment spec
        spec = client.V1DeploymentSpec(
            replicas=deployment_config.replicas,
            template=template,
            selector=client.V1LabelSelector(match_labels={"app": deployment_config.name})
        )
        
        # Create deployment
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=deployment_config.name),
            spec=spec
        )
        
        return deployment
    
    async def _create_horizontal_pod_autoscaler(self, deployment_config: DeploymentConfig):
        """Create HorizontalPodAutoscaler for auto-scaling."""
        try:
            hpa = client.V1HorizontalPodAutoscaler(
                api_version="autoscaling/v1",
                kind="HorizontalPodAutoscaler",
                metadata=client.V1ObjectMeta(name=f"{deployment_config.name}-hpa"),
                spec=client.V1HorizontalPodAutoscalerSpec(
                    scale_target_ref=client.V1CrossVersionObjectReference(
                        api_version="apps/v1",
                        kind="Deployment",
                        name=deployment_config.name
                    ),
                    min_replicas=deployment_config.min_replicas,
                    max_replicas=deployment_config.max_replicas,
                    target_cpu_utilization_percentage=deployment_config.target_cpu_utilization
                )
            )
            
            self.autoscaling_v1.create_namespaced_horizontal_pod_autoscaler(
                namespace=deployment_config.namespace,
                body=hpa
            )
            
            logger.info(f"HorizontalPodAutoscaler created for {deployment_config.name}")
            
        except Exception as e:
            logger.error(f"Failed to create HorizontalPodAutoscaler for {deployment_config.name}: {e}")
    
    async def get_deployment_logs(self, name: str, namespace: str, tail_lines: int = 100) -> List[str]:
        """
        Get deployment logs.
        
        Args:
            name: Deployment name
            namespace: Deployment namespace
            tail_lines: Number of lines to retrieve
            
        Returns:
            List of log lines
        """
        try:
            # Get pods for the deployment
            pods = self.core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app={name}"
            )
            
            logs = []
            for pod in pods.items:
                pod_logs = self.core_v1.read_namespaced_pod_log(
                    name=pod.metadata.name,
                    namespace=namespace,
                    tail_lines=tail_lines
                )
                logs.extend(pod_logs.split('\n'))
            
            return logs
            
        except Exception as e:
            logger.error(f"Failed to get logs for deployment {name}: {e}")
            return []
    
    def generate_deployment_yaml(self, deployment_config: DeploymentConfig) -> str:
        """
        Generate YAML configuration for deployment.
        
        Args:
            deployment_config: Deployment configuration
            
        Returns:
            YAML string representation
        """
        deployment = self._create_deployment_object(deployment_config)
        
        # Convert to dict
        deployment_dict = client.ApiClient().sanitize_for_serialization(deployment)
        
        # Generate YAML
        return yaml.dump(deployment_dict, default_flow_style=False)


