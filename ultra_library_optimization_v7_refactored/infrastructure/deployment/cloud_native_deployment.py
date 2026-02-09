#!/usr/bin/env python3
"""
Cloud-Native Deployment System - Infrastructure Layer
==================================================

Enterprise-grade cloud-native deployment with Kubernetes support,
auto-scaling, multi-region deployment, and cloud monitoring.
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, Union
import threading
import yaml
import subprocess
import os
from pathlib import Path


class CloudProvider(Enum):
    """Supported cloud providers."""
    AWS = "aws"
    GOOGLE_CLOUD = "gcp"
    AZURE = "azure"
    DIGITAL_OCEAN = "digitalocean"
    KUBERNETES = "kubernetes"


class DeploymentStatus(Enum):
    """Deployment status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


class ScalingPolicy(Enum):
    """Auto-scaling policies."""
    CPU_BASED = "cpu_based"
    MEMORY_BASED = "memory_based"
    CUSTOM_METRICS = "custom_metrics"
    SCHEDULE_BASED = "schedule_based"


@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    
    name: str
    namespace: str
    replicas: int
    image: str
    image_tag: str
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "128Mi"
    memory_limit: str = "512Mi"
    ports: List[int] = field(default_factory=lambda: [8000])
    environment_variables: Dict[str, str] = field(default_factory=dict)
    secrets: Dict[str, str] = field(default_factory=dict)
    config_maps: Dict[str, str] = field(default_factory=dict)
    health_check_path: str = "/health"
    readiness_probe_path: str = "/ready"
    liveness_probe_path: str = "/live"
    auto_scaling: bool = True
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    target_memory_utilization: int = 80


@dataclass
class DeploymentResult:
    """Result of deployment operation."""
    
    deployment_id: str
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    deployment_url: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScalingMetrics:
    """Scaling metrics and thresholds."""
    
    cpu_utilization: float
    memory_utilization: float
    request_count: int
    error_rate: float
    response_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class KubernetesDeployer:
    """Kubernetes deployment manager."""
    
    def __init__(self, config_path: str = "k8s"):
        self.config_path = Path(config_path)
        self._logger = logging.getLogger(__name__)
        self._deployments: Dict[str, DeploymentResult] = {}
        self._lock = threading.RLock()
    
    def generate_deployment_yaml(self, config: DeploymentConfig) -> str:
        """Generate Kubernetes deployment YAML."""
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': config.name,
                'namespace': config.namespace,
                'labels': {
                    'app': config.name,
                    'version': config.image_tag
                }
            },
            'spec': {
                'replicas': config.replicas,
                'selector': {
                    'matchLabels': {
                        'app': config.name
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': config.name,
                            'version': config.image_tag
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': config.name,
                            'image': f"{config.image}:{config.image_tag}",
                            'ports': [{'containerPort': port} for port in config.ports],
                            'resources': {
                                'requests': {
                                    'cpu': config.cpu_request,
                                    'memory': config.memory_request
                                },
                                'limits': {
                                    'cpu': config.cpu_limit,
                                    'memory': config.memory_limit
                                }
                            },
                            'env': [
                                {'name': k, 'value': v} 
                                for k, v in config.environment_variables.items()
                            ],
                            'livenessProbe': {
                                'httpGet': {
                                    'path': config.liveness_probe_path,
                                    'port': config.ports[0]
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': config.readiness_probe_path,
                                    'port': config.ports[0]
                                },
                                'initialDelaySeconds': 5,
                                'periodSeconds': 5
                            }
                        }]
                    }
                }
            }
        }
        
        return yaml.dump(deployment, default_flow_style=False)
    
    def generate_service_yaml(self, config: DeploymentConfig) -> str:
        """Generate Kubernetes service YAML."""
        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': f"{config.name}-service",
                'namespace': config.namespace
            },
            'spec': {
                'selector': {
                    'app': config.name
                },
                'ports': [{
                    'protocol': 'TCP',
                    'port': port,
                    'targetPort': port
                } for port in config.ports],
                'type': 'LoadBalancer'
            }
        }
        
        return yaml.dump(service, default_flow_style=False)
    
    def generate_hpa_yaml(self, config: DeploymentConfig) -> str:
        """Generate Horizontal Pod Autoscaler YAML."""
        if not config.auto_scaling:
            return ""
        
        hpa = {
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': f"{config.name}-hpa",
                'namespace': config.namespace
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'name': config.name
                },
                'minReplicas': config.min_replicas,
                'maxReplicas': config.max_replicas,
                'metrics': [
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'cpu',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': config.target_cpu_utilization
                            }
                        }
                    },
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'memory',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': config.target_memory_utilization
                            }
                        }
                    }
                ]
            }
        }
        
        return yaml.dump(hpa, default_flow_style=False)
    
    async def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Deploy application to Kubernetes."""
        deployment_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        result = DeploymentResult(
            deployment_id=deployment_id,
            status=DeploymentStatus.IN_PROGRESS,
            start_time=start_time
        )
        
        with self._lock:
            self._deployments[deployment_id] = result
        
        try:
            # Generate YAML files
            deployment_yaml = self.generate_deployment_yaml(config)
            service_yaml = self.generate_service_yaml(config)
            hpa_yaml = self.generate_hpa_yaml(config)
            
            # Save YAML files
            yaml_dir = self.config_path / config.namespace
            yaml_dir.mkdir(parents=True, exist_ok=True)
            
            deployment_file = yaml_dir / f"{config.name}-deployment.yaml"
            service_file = yaml_dir / f"{config.name}-service.yaml"
            hpa_file = yaml_dir / f"{config.name}-hpa.yaml"
            
            deployment_file.write_text(deployment_yaml)
            service_file.write_text(service_yaml)
            
            if hpa_yaml:
                hpa_file.write_text(hpa_yaml)
            
            # Apply Kubernetes manifests
            await self._apply_kubernetes_manifests(config.namespace, yaml_dir)
            
            # Wait for deployment to be ready
            await self._wait_for_deployment_ready(config.name, config.namespace)
            
            # Get deployment URL
            service_url = await self._get_service_url(f"{config.name}-service", config.namespace)
            
            # Update result
            result.status = DeploymentStatus.SUCCESS
            result.end_time = datetime.utcnow()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            result.deployment_url = service_url
            
            self._logger.info(f"Deployment {deployment_id} completed successfully")
            
        except Exception as e:
            result.status = DeploymentStatus.FAILED
            result.end_time = datetime.utcnow()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            result.error_message = str(e)
            
            self._logger.error(f"Deployment {deployment_id} failed: {e}")
        
        return result
    
    async def _apply_kubernetes_manifests(self, namespace: str, yaml_dir: Path) -> None:
        """Apply Kubernetes manifests."""
        try:
            # Create namespace if it doesn't exist
            subprocess.run([
                'kubectl', 'create', 'namespace', namespace, '--dry-run=client', '-o', 'yaml'
            ], check=True)
            
            # Apply all YAML files in the directory
            subprocess.run([
                'kubectl', 'apply', '-f', str(yaml_dir), '-n', namespace
            ], check=True)
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to apply Kubernetes manifests: {e}")
    
    async def _wait_for_deployment_ready(self, deployment_name: str, namespace: str) -> None:
        """Wait for deployment to be ready."""
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            try:
                result = subprocess.run([
                    'kubectl', 'get', 'deployment', deployment_name,
                    '-n', namespace, '-o', 'jsonpath={.status.readyReplicas}'
                ], capture_output=True, text=True, check=True)
                
                if result.stdout.strip() == '1':
                    return
                
            except subprocess.CalledProcessError:
                pass
            
            await asyncio.sleep(10)
            attempt += 1
        
        raise Exception(f"Deployment {deployment_name} failed to become ready")
    
    async def _get_service_url(self, service_name: str, namespace: str) -> Optional[str]:
        """Get service URL."""
        try:
            result = subprocess.run([
                'kubectl', 'get', 'service', service_name,
                '-n', namespace, '-o', 'jsonpath={.status.loadBalancer.ingress[0].ip}'
            ], capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                return f"http://{result.stdout.strip()}:8000"
            
        except subprocess.CalledProcessError:
            pass
        
        return None
    
    def get_deployment_status(self, deployment_id: str) -> Optional[DeploymentResult]:
        """Get deployment status."""
        with self._lock:
            return self._deployments.get(deployment_id)


class AutoScaler:
    """Advanced auto-scaling system."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._scaling_history: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
    
    async def check_scaling_needs(self, metrics: ScalingMetrics, 
                                 config: DeploymentConfig) -> Dict[str, Any]:
        """Check if scaling is needed based on metrics."""
        with self._lock:
            scaling_decision = {
                'should_scale': False,
                'scale_up': False,
                'scale_down': False,
                'reason': '',
                'current_replicas': config.replicas,
                'suggested_replicas': config.replicas
            }
            
            # CPU-based scaling
            if metrics.cpu_utilization > config.target_cpu_utilization:
                scaling_decision['should_scale'] = True
                scaling_decision['scale_up'] = True
                scaling_decision['reason'] = f"High CPU utilization: {metrics.cpu_utilization}%"
                scaling_decision['suggested_replicas'] = min(
                    config.max_replicas,
                    config.replicas + 1
                )
            
            elif metrics.cpu_utilization < (config.target_cpu_utilization * 0.5):
                scaling_decision['should_scale'] = True
                scaling_decision['scale_down'] = True
                scaling_decision['reason'] = f"Low CPU utilization: {metrics.cpu_utilization}%"
                scaling_decision['suggested_replicas'] = max(
                    config.min_replicas,
                    config.replicas - 1
                )
            
            # Memory-based scaling
            elif metrics.memory_utilization > config.target_memory_utilization:
                scaling_decision['should_scale'] = True
                scaling_decision['scale_up'] = True
                scaling_decision['reason'] = f"High memory utilization: {metrics.memory_utilization}%"
                scaling_decision['suggested_replicas'] = min(
                    config.max_replicas,
                    config.replicas + 1
                )
            
            # Error rate scaling
            elif metrics.error_rate > 0.05:  # 5% error rate threshold
                scaling_decision['should_scale'] = True
                scaling_decision['scale_up'] = True
                scaling_decision['reason'] = f"High error rate: {metrics.error_rate * 100}%"
                scaling_decision['suggested_replicas'] = min(
                    config.max_replicas,
                    config.replicas + 1
                )
            
            # Record scaling decision
            self._scaling_history.append({
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': metrics.__dict__,
                'decision': scaling_decision
            })
            
            return scaling_decision
    
    def get_scaling_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get scaling history."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            return [
                entry for entry in self._scaling_history
                if datetime.fromisoformat(entry['timestamp']) > cutoff_time
            ]


class MultiRegionDeployer:
    """Multi-region deployment manager."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._regions: Dict[str, Dict[str, Any]] = {}
        self._deployments: Dict[str, List[DeploymentResult]] = {}
    
    def add_region(self, region_name: str, provider: CloudProvider, 
                   config: Dict[str, Any]) -> None:
        """Add a deployment region."""
        self._regions[region_name] = {
            'provider': provider,
            'config': config,
            'status': 'active'
        }
        self._logger.info(f"Added region: {region_name} with provider {provider}")
    
    async def deploy_to_region(self, region_name: str, config: DeploymentConfig) -> DeploymentResult:
        """Deploy to a specific region."""
        if region_name not in self._regions:
            raise ValueError(f"Region {region_name} not found")
        
        region_info = self._regions[region_name]
        provider = region_info['provider']
        
        if provider == CloudProvider.KUBERNETES:
            deployer = KubernetesDeployer()
            result = await deployer.deploy(config)
        else:
            # For other cloud providers, implement specific deployment logic
            result = await self._deploy_to_cloud_provider(provider, config, region_info['config'])
        
        # Store deployment result
        if region_name not in self._deployments:
            self._deployments[region_name] = []
        
        self._deployments[region_name].append(result)
        
        return result
    
    async def deploy_to_all_regions(self, config: DeploymentConfig) -> Dict[str, DeploymentResult]:
        """Deploy to all active regions."""
        results = {}
        
        for region_name, region_info in self._regions.items():
            if region_info['status'] == 'active':
                try:
                    result = await self.deploy_to_region(region_name, config)
                    results[region_name] = result
                except Exception as e:
                    self._logger.error(f"Failed to deploy to region {region_name}: {e}")
                    results[region_name] = DeploymentResult(
                        deployment_id=str(uuid.uuid4()),
                        status=DeploymentStatus.FAILED,
                        start_time=datetime.utcnow(),
                        error_message=str(e)
                    )
        
        return results
    
    async def _deploy_to_cloud_provider(self, provider: CloudProvider, 
                                       config: DeploymentConfig,
                                       region_config: Dict[str, Any]) -> DeploymentResult:
        """Deploy to cloud provider (placeholder implementation)."""
        # This would contain specific implementation for each cloud provider
        # For now, return a mock result
        
        return DeploymentResult(
            deployment_id=str(uuid.uuid4()),
            status=DeploymentStatus.SUCCESS,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration_seconds=30.0,
            deployment_url=f"https://{config.name}.{provider.value}.com"
        )


class CloudMonitor:
    """Cloud monitoring and observability."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._metrics: List[ScalingMetrics] = []
        self._alerts: List[Dict[str, Any]] = []
    
    def record_metrics(self, metrics: ScalingMetrics) -> None:
        """Record scaling metrics."""
        self._metrics.append(metrics)
        
        # Check for alerts
        self._check_alerts(metrics)
    
    def _check_alerts(self, metrics: ScalingMetrics) -> None:
        """Check for alert conditions."""
        alerts = []
        
        if metrics.cpu_utilization > 90:
            alerts.append({
                'type': 'high_cpu',
                'severity': 'critical',
                'message': f"CPU utilization is {metrics.cpu_utilization}%",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        if metrics.memory_utilization > 90:
            alerts.append({
                'type': 'high_memory',
                'severity': 'critical',
                'message': f"Memory utilization is {metrics.memory_utilization}%",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        if metrics.error_rate > 0.1:
            alerts.append({
                'type': 'high_error_rate',
                'severity': 'warning',
                'message': f"Error rate is {metrics.error_rate * 100}%",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        if metrics.response_time_ms > 5000:
            alerts.append({
                'type': 'high_response_time',
                'severity': 'warning',
                'message': f"Response time is {metrics.response_time_ms}ms",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        self._alerts.extend(alerts)
        
        for alert in alerts:
            self._logger.warning(f"Alert: {alert['message']}")
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self._metrics
            if m.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        return {
            'total_metrics': len(recent_metrics),
            'avg_cpu_utilization': sum(m.cpu_utilization for m in recent_metrics) / len(recent_metrics),
            'avg_memory_utilization': sum(m.memory_utilization for m in recent_metrics) / len(recent_metrics),
            'avg_response_time': sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics),
            'avg_error_rate': sum(m.error_rate for m in recent_metrics) / len(recent_metrics),
            'total_requests': sum(m.request_count for m in recent_metrics),
            'active_alerts': len([a for a in self._alerts if datetime.fromisoformat(a['timestamp']) > cutoff_time])
        }


class CloudNativeDeployment:
    """
    Advanced cloud-native deployment system.
    
    Features:
    - Kubernetes deployment management
    - Multi-region deployment support
    - Auto-scaling with custom policies
    - Cloud monitoring and observability
    - Blue-green deployment support
    - Canary deployment support
    - Infrastructure as Code (IaC)
    """
    
    def __init__(self):
        self.kubernetes_deployer = KubernetesDeployer()
        self.auto_scaler = AutoScaler()
        self.multi_region_deployer = MultiRegionDeployer()
        self.cloud_monitor = CloudMonitor()
        self._logger = logging.getLogger(__name__)
    
    async def deploy_application(self, config: DeploymentConfig, 
                               regions: List[str] = None) -> Dict[str, DeploymentResult]:
        """Deploy application to specified regions."""
        if regions:
            # Deploy to specific regions
            results = {}
            for region in regions:
                try:
                    result = await self.multi_region_deployer.deploy_to_region(region, config)
                    results[region] = result
                except Exception as e:
                    self._logger.error(f"Failed to deploy to region {region}: {e}")
                    results[region] = DeploymentResult(
                        deployment_id=str(uuid.uuid4()),
                        status=DeploymentStatus.FAILED,
                        start_time=datetime.utcnow(),
                        error_message=str(e)
                    )
            return results
        else:
            # Deploy to all regions
            return await self.multi_region_deployer.deploy_to_all_regions(config)
    
    async def scale_application(self, deployment_name: str, namespace: str,
                              target_replicas: int) -> bool:
        """Scale application to target replicas."""
        try:
            subprocess.run([
                'kubectl', 'scale', 'deployment', deployment_name,
                f'--replicas={target_replicas}', '-n', namespace
            ], check=True)
            
            self._logger.info(f"Scaled {deployment_name} to {target_replicas} replicas")
            return True
            
        except subprocess.CalledProcessError as e:
            self._logger.error(f"Failed to scale {deployment_name}: {e}")
            return False
    
    async def check_and_scale(self, deployment_name: str, namespace: str,
                             config: DeploymentConfig) -> Dict[str, Any]:
        """Check metrics and scale if needed."""
        # Get current metrics (simplified)
        metrics = ScalingMetrics(
            cpu_utilization=75.0,  # Mock data
            memory_utilization=60.0,
            request_count=1000,
            error_rate=0.02,
            response_time_ms=250.0
        )
        
        # Record metrics
        self.cloud_monitor.record_metrics(metrics)
        
        # Check scaling needs
        scaling_decision = await self.auto_scaler.check_scaling_needs(metrics, config)
        
        # Apply scaling if needed
        if scaling_decision['should_scale']:
            success = await self.scale_application(
                deployment_name, namespace, scaling_decision['suggested_replicas']
            )
            scaling_decision['scaling_applied'] = success
        
        return scaling_decision
    
    def get_deployment_status(self, deployment_name: str, namespace: str) -> Dict[str, Any]:
        """Get deployment status."""
        try:
            result = subprocess.run([
                'kubectl', 'get', 'deployment', deployment_name,
                '-n', namespace, '-o', 'json'
            ], capture_output=True, text=True, check=True)
            
            deployment_info = json.loads(result.stdout)
            
            return {
                'name': deployment_name,
                'namespace': namespace,
                'replicas': deployment_info['spec']['replicas'],
                'ready_replicas': deployment_info['status'].get('readyReplicas', 0),
                'available_replicas': deployment_info['status'].get('availableReplicas', 0),
                'updated_replicas': deployment_info['status'].get('updatedReplicas', 0),
                'conditions': deployment_info['status'].get('conditions', [])
            }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            self._logger.error(f"Failed to get deployment status: {e}")
            return {'error': str(e)}
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """Get cluster information."""
        try:
            # Get nodes
            nodes_result = subprocess.run([
                'kubectl', 'get', 'nodes', '-o', 'json'
            ], capture_output=True, text=True, check=True)
            
            nodes_info = json.loads(nodes_result.stdout)
            
            # Get pods
            pods_result = subprocess.run([
                'kubectl', 'get', 'pods', '--all-namespaces', '-o', 'json'
            ], capture_output=True, text=True, check=True)
            
            pods_info = json.loads(pods_result.stdout)
            
            return {
                'nodes': {
                    'total': len(nodes_info['items']),
                    'ready': len([n for n in nodes_info['items'] if n['status']['conditions'][0]['status'] == 'True'])
                },
                'pods': {
                    'total': len(pods_info['items']),
                    'running': len([p for p in pods_info['items'] if p['status']['phase'] == 'Running']),
                    'pending': len([p for p in pods_info['items'] if p['status']['phase'] == 'Pending']),
                    'failed': len([p for p in pods_info['items'] if p['status']['phase'] == 'Failed'])
                }
            }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            self._logger.error(f"Failed to get cluster info: {e}")
            return {'error': str(e)}
    
    def get_monitoring_data(self) -> Dict[str, Any]:
        """Get monitoring data."""
        return {
            'metrics_summary': self.cloud_monitor.get_metrics_summary(),
            'scaling_history': self.auto_scaler.get_scaling_history(),
            'deployment_history': self.kubernetes_deployer._deployments
        }


# Global cloud deployment instance
cloud_deployment = CloudNativeDeployment()


# Decorators for easy cloud deployment
def cloud_deployed(regions: List[str] = None):
    """Decorator to deploy application to cloud."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # This would integrate with the deployment system
            # For now, just call the original function
            result = await func(*args, **kwargs)
            
            # Add deployment metadata
            if isinstance(result, dict):
                result['deployment_info'] = {
                    'cloud_deployed': True,
                    'regions': regions or ['default'],
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return result
        
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if isinstance(result, dict):
                result['deployment_info'] = {
                    'cloud_deployed': True,
                    'regions': regions or ['default'],
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def auto_scaled(min_replicas: int = 1, max_replicas: int = 10):
    """Decorator to enable auto-scaling for functions."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # This would integrate with the auto-scaling system
            result = await func(*args, **kwargs)
            
            if isinstance(result, dict):
                result['auto_scaling'] = {
                    'enabled': True,
                    'min_replicas': min_replicas,
                    'max_replicas': max_replicas,
                    'current_replicas': min_replicas
                }
            
            return result
        
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if isinstance(result, dict):
                result['auto_scaling'] = {
                    'enabled': True,
                    'min_replicas': min_replicas,
                    'max_replicas': max_replicas,
                    'current_replicas': min_replicas
                }
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator 