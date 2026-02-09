"""
Advanced Orchestration Service with Microservices Management
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import httpx
from urllib.parse import urljoin
import yaml
import docker
from docker.errors import DockerException

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ServiceStatus(Enum):
    """Service status"""
    UNKNOWN = "unknown"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class ServiceType(Enum):
    """Service type"""
    API = "api"
    WORKER = "worker"
    SCHEDULER = "scheduler"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    STORAGE = "storage"
    MONITORING = "monitoring"
    GATEWAY = "gateway"
    CUSTOM = "custom"

class DeploymentStrategy(Enum):
    """Deployment strategy"""
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"

@dataclass
class ServiceDefinition:
    """Service definition"""
    id: str
    name: str
    service_type: ServiceType
    version: str
    image: str
    ports: List[int] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    networks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    health_check: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    replicas: int = 1
    restart_policy: str = "always"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ServiceInstance:
    """Service instance"""
    id: str
    service_definition_id: str
    name: str
    status: ServiceStatus
    container_id: Optional[str] = None
    host: Optional[str] = None
    ports: Dict[int, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    health_status: Optional[str] = None
    last_health_check: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Deployment:
    """Deployment configuration"""
    id: str
    name: str
    services: List[ServiceDefinition]
    strategy: DeploymentStrategy
    environment: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LoadBalancer:
    """Load balancer configuration"""
    id: str
    name: str
    service_ids: List[str]
    algorithm: str = "round_robin"
    health_check: Optional[Dict[str, Any]] = None
    ssl_config: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class AdvancedOrchestrationService:
    """Advanced Orchestration Service with Microservices Management"""
    
    def __init__(self):
        self.service_definitions = {}
        self.service_instances = {}
        self.deployments = {}
        self.load_balancers = {}
        self.docker_client = None
        self.health_check_tasks = {}
        self.deployment_queue = asyncio.Queue()
        self.scaling_queue = asyncio.Queue()
        
        # Initialize Docker client
        self._initialize_docker_client()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Advanced Orchestration Service initialized")
    
    def _initialize_docker_client(self):
        """Initialize Docker client"""
        try:
            self.docker_client = docker.from_env()
            # Test connection
            self.docker_client.ping()
            logger.info("Docker client initialized successfully")
            
        except DockerException as e:
            logger.warning(f"Docker client initialization failed: {e}")
            self.docker_client = None
        except Exception as e:
            logger.error(f"Error initializing Docker client: {e}")
            self.docker_client = None
    
    def _start_background_tasks(self):
        """Start background tasks"""
        try:
            # Start deployment processor
            asyncio.create_task(self._process_deployments())
            
            # Start scaling processor
            asyncio.create_task(self._process_scaling())
            
            # Start health check monitor
            asyncio.create_task(self._monitor_health_checks())
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
    
    async def _process_deployments(self):
        """Process deployment queue"""
        try:
            while True:
                try:
                    deployment = await asyncio.wait_for(self.deployment_queue.get(), timeout=1.0)
                    await self._execute_deployment(deployment)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing deployment: {e}")
                    
        except Exception as e:
            logger.error(f"Error in deployment processor: {e}")
    
    async def _process_scaling(self):
        """Process scaling queue"""
        try:
            while True:
                try:
                    scaling_request = await asyncio.wait_for(self.scaling_queue.get(), timeout=1.0)
                    await self._execute_scaling(scaling_request)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing scaling: {e}")
                    
        except Exception as e:
            logger.error(f"Error in scaling processor: {e}")
    
    async def _monitor_health_checks(self):
        """Monitor service health checks"""
        try:
            while True:
                try:
                    await asyncio.sleep(30)  # Check every 30 seconds
                    
                    for instance_id, instance in self.service_instances.items():
                        if instance.status == ServiceStatus.RUNNING:
                            await self._perform_health_check(instance)
                            
                except Exception as e:
                    logger.error(f"Error in health check monitor: {e}")
                    
        except Exception as e:
            logger.error(f"Error in health check monitor: {e}")
    
    async def create_service_definition(self, service_def: ServiceDefinition) -> str:
        """Create service definition"""
        try:
            service_id = str(uuid.uuid4())
            service_def.id = service_id
            
            self.service_definitions[service_id] = service_def
            
            logger.info(f"Service definition created: {service_id}")
            
            return service_id
            
        except Exception as e:
            logger.error(f"Error creating service definition: {e}")
            raise
    
    async def deploy_service(self, service_id: str, environment: str = "production") -> str:
        """Deploy a service"""
        try:
            if service_id not in self.service_definitions:
                raise ValueError(f"Service definition not found: {service_id}")
            
            service_def = self.service_definitions[service_id]
            
            # Create deployment
            deployment_id = str(uuid.uuid4())
            deployment = Deployment(
                id=deployment_id,
                name=f"{service_def.name}-{environment}",
                services=[service_def],
                strategy=DeploymentStrategy.ROLLING,
                environment=environment
            )
            
            self.deployments[deployment_id] = deployment
            
            # Add to deployment queue
            await self.deployment_queue.put(deployment)
            
            logger.info(f"Service deployment queued: {service_id}")
            
            return deployment_id
            
        except Exception as e:
            logger.error(f"Error deploying service: {e}")
            raise
    
    async def _execute_deployment(self, deployment: Deployment):
        """Execute deployment"""
        try:
            deployment.status = "running"
            
            for service_def in deployment.services:
                await self._deploy_service_instance(service_def, deployment.environment)
            
            deployment.status = "completed"
            deployment.updated_at = datetime.utcnow()
            
            logger.info(f"Deployment completed: {deployment.id}")
            
        except Exception as e:
            logger.error(f"Error executing deployment: {e}")
            deployment.status = "failed"
            deployment.updated_at = datetime.utcnow()
    
    async def _deploy_service_instance(self, service_def: ServiceDefinition, environment: str):
        """Deploy service instance"""
        try:
            if not self.docker_client:
                logger.warning("Docker client not available, using mock deployment")
                await self._mock_deploy_service(service_def)
                return
            
            # Create container configuration
            container_config = {
                'image': service_def.image,
                'environment': service_def.environment,
                'ports': {port: port for port in service_def.ports},
                'volumes': service_def.volumes,
                'networks': service_def.networks,
                'restart_policy': {'Name': service_def.restart_policy},
                'detach': True
            }
            
            # Add resource limits if specified
            if service_def.resources:
                container_config['mem_limit'] = service_def.resources.get('memory')
                container_config['cpu_quota'] = service_def.resources.get('cpu')
            
            # Create and start container
            container = self.docker_client.containers.run(**container_config)
            
            # Create service instance
            instance_id = str(uuid.uuid4())
            service_instance = ServiceInstance(
                id=instance_id,
                service_definition_id=service_def.id,
                name=f"{service_def.name}-{instance_id[:8]}",
                status=ServiceStatus.RUNNING,
                container_id=container.id,
                ports={port: port for port in service_def.ports},
                started_at=datetime.utcnow()
            )
            
            self.service_instances[instance_id] = service_instance
            
            # Start health check if configured
            if service_def.health_check:
                await self._start_health_check(service_instance, service_def.health_check)
            
            logger.info(f"Service instance deployed: {instance_id}")
            
        except Exception as e:
            logger.error(f"Error deploying service instance: {e}")
            raise
    
    async def _mock_deploy_service(self, service_def: ServiceDefinition):
        """Mock service deployment for testing"""
        try:
            instance_id = str(uuid.uuid4())
            service_instance = ServiceInstance(
                id=instance_id,
                service_definition_id=service_def.id,
                name=f"{service_def.name}-{instance_id[:8]}",
                status=ServiceStatus.RUNNING,
                ports={port: port for port in service_def.ports},
                started_at=datetime.utcnow()
            )
            
            self.service_instances[instance_id] = service_instance
            
            logger.info(f"Mock service instance deployed: {instance_id}")
            
        except Exception as e:
            logger.error(f"Error in mock deployment: {e}")
    
    async def _start_health_check(self, service_instance: ServiceInstance, health_check_config: Dict[str, Any]):
        """Start health check for service instance"""
        try:
            health_check_task = asyncio.create_task(
                self._health_check_loop(service_instance, health_check_config)
            )
            
            self.health_check_tasks[service_instance.id] = health_check_task
            
            logger.info(f"Health check started for service: {service_instance.id}")
            
        except Exception as e:
            logger.error(f"Error starting health check: {e}")
    
    async def _health_check_loop(self, service_instance: ServiceInstance, health_check_config: Dict[str, Any]):
        """Health check loop"""
        try:
            interval = health_check_config.get('interval', 30)
            timeout = health_check_config.get('timeout', 10)
            
            while service_instance.status == ServiceStatus.RUNNING:
                try:
                    await self._perform_health_check(service_instance)
                    await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Health check error for {service_instance.id}: {e}")
                    await asyncio.sleep(interval)
                    
        except Exception as e:
            logger.error(f"Error in health check loop: {e}")
    
    async def _perform_health_check(self, service_instance: ServiceInstance):
        """Perform health check on service instance"""
        try:
            # Get health check configuration
            service_def = self.service_definitions[service_instance.service_definition_id]
            health_check_config = service_def.health_check
            
            if not health_check_config:
                return
            
            health_check_type = health_check_config.get('type', 'http')
            
            if health_check_type == 'http':
                await self._http_health_check(service_instance, health_check_config)
            elif health_check_type == 'tcp':
                await self._tcp_health_check(service_instance, health_check_config)
            elif health_check_type == 'command':
                await self._command_health_check(service_instance, health_check_config)
            
            service_instance.last_health_check = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            service_instance.health_status = "unhealthy"
    
    async def _http_health_check(self, service_instance: ServiceInstance, health_check_config: Dict[str, Any]):
        """HTTP health check"""
        try:
            path = health_check_config.get('path', '/health')
            port = health_check_config.get('port', 8080)
            timeout = health_check_config.get('timeout', 10)
            
            url = f"http://localhost:{port}{path}"
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    service_instance.health_status = "healthy"
                    service_instance.status = ServiceStatus.HEALTHY
                else:
                    service_instance.health_status = "unhealthy"
                    service_instance.status = ServiceStatus.UNHEALTHY
                    
        except Exception as e:
            logger.error(f"HTTP health check failed: {e}")
            service_instance.health_status = "unhealthy"
            service_instance.status = ServiceStatus.UNHEALTHY
    
    async def _tcp_health_check(self, service_instance: ServiceInstance, health_check_config: Dict[str, Any]):
        """TCP health check"""
        try:
            import socket
            
            host = health_check_config.get('host', 'localhost')
            port = health_check_config.get('port', 8080)
            timeout = health_check_config.get('timeout', 10)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                service_instance.health_status = "healthy"
                service_instance.status = ServiceStatus.HEALTHY
            else:
                service_instance.health_status = "unhealthy"
                service_instance.status = ServiceStatus.UNHEALTHY
                
        except Exception as e:
            logger.error(f"TCP health check failed: {e}")
            service_instance.health_status = "unhealthy"
            service_instance.status = ServiceStatus.UNHEALTHY
    
    async def _command_health_check(self, service_instance: ServiceInstance, health_check_config: Dict[str, Any]):
        """Command health check"""
        try:
            import subprocess
            
            command = health_check_config.get('command')
            timeout = health_check_config.get('timeout', 10)
            
            if not command:
                return
            
            result = subprocess.run(
                command,
                shell=True,
                timeout=timeout,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                service_instance.health_status = "healthy"
                service_instance.status = ServiceStatus.HEALTHY
            else:
                service_instance.health_status = "unhealthy"
                service_instance.status = ServiceStatus.UNHEALTHY
                
        except Exception as e:
            logger.error(f"Command health check failed: {e}")
            service_instance.health_status = "unhealthy"
            service_instance.status = ServiceStatus.UNHEALTHY
    
    async def scale_service(self, service_id: str, replicas: int):
        """Scale service to specified number of replicas"""
        try:
            if service_id not in self.service_definitions:
                raise ValueError(f"Service definition not found: {service_id}")
            
            service_def = self.service_definitions[service_id]
            current_instances = [
                instance for instance in self.service_instances.values()
                if instance.service_definition_id == service_id and instance.status == ServiceStatus.RUNNING
            ]
            
            current_replicas = len(current_instances)
            
            if replicas > current_replicas:
                # Scale up
                for _ in range(replicas - current_replicas):
                    await self._deploy_service_instance(service_def, "production")
            
            elif replicas < current_replicas:
                # Scale down
                instances_to_remove = current_instances[:current_replicas - replicas]
                for instance in instances_to_remove:
                    await self.stop_service_instance(instance.id)
            
            service_def.replicas = replicas
            
            logger.info(f"Service scaled: {service_id} to {replicas} replicas")
            
        except Exception as e:
            logger.error(f"Error scaling service: {e}")
            raise
    
    async def stop_service_instance(self, instance_id: str) -> bool:
        """Stop service instance"""
        try:
            if instance_id not in self.service_instances:
                return False
            
            service_instance = self.service_instances[instance_id]
            
            # Stop health check
            if instance_id in self.health_check_tasks:
                self.health_check_tasks[instance_id].cancel()
                del self.health_check_tasks[instance_id]
            
            # Stop container if Docker is available
            if self.docker_client and service_instance.container_id:
                try:
                    container = self.docker_client.containers.get(service_instance.container_id)
                    container.stop()
                    container.remove()
                except Exception as e:
                    logger.warning(f"Error stopping container: {e}")
            
            # Update instance status
            service_instance.status = ServiceStatus.STOPPED
            service_instance.stopped_at = datetime.utcnow()
            
            logger.info(f"Service instance stopped: {instance_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping service instance: {e}")
            return False
    
    async def create_load_balancer(self, load_balancer: LoadBalancer) -> str:
        """Create load balancer"""
        try:
            lb_id = str(uuid.uuid4())
            load_balancer.id = lb_id
            
            self.load_balancers[lb_id] = load_balancer
            
            logger.info(f"Load balancer created: {lb_id}")
            
            return lb_id
            
        except Exception as e:
            logger.error(f"Error creating load balancer: {e}")
            raise
    
    async def get_service_status(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get service status"""
        try:
            if service_id not in self.service_definitions:
                return None
            
            service_def = self.service_definitions[service_id]
            instances = [
                instance for instance in self.service_instances.values()
                if instance.service_definition_id == service_id
            ]
            
            return {
                'service_id': service_id,
                'name': service_def.name,
                'type': service_def.service_type.value,
                'version': service_def.version,
                'replicas': service_def.replicas,
                'instances': len(instances),
                'running_instances': len([i for i in instances if i.status == ServiceStatus.RUNNING]),
                'healthy_instances': len([i for i in instances if i.health_status == "healthy"]),
                'instances_detail': [
                    {
                        'id': instance.id,
                        'status': instance.status.value,
                        'health_status': instance.health_status,
                        'started_at': instance.started_at.isoformat() if instance.started_at else None,
                        'last_health_check': instance.last_health_check.isoformat() if instance.last_health_check else None
                    }
                    for instance in instances
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return None
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status"""
        try:
            if deployment_id not in self.deployments:
                return None
            
            deployment = self.deployments[deployment_id]
            
            return {
                'deployment_id': deployment_id,
                'name': deployment.name,
                'environment': deployment.environment,
                'strategy': deployment.strategy.value,
                'status': deployment.status,
                'created_at': deployment.created_at.isoformat(),
                'updated_at': deployment.updated_at.isoformat(),
                'services_count': len(deployment.services)
            }
            
        except Exception as e:
            logger.error(f"Error getting deployment status: {e}")
            return None
    
    async def export_service_config(self, service_id: str, format: str = "yaml") -> str:
        """Export service configuration"""
        try:
            if service_id not in self.service_definitions:
                return ""
            
            service_def = self.service_definitions[service_id]
            
            config = {
                'service': {
                    'id': service_def.id,
                    'name': service_def.name,
                    'type': service_def.service_type.value,
                    'version': service_def.version,
                    'image': service_def.image,
                    'ports': service_def.ports,
                    'environment': service_def.environment,
                    'volumes': service_def.volumes,
                    'networks': service_def.networks,
                    'dependencies': service_def.dependencies,
                    'health_check': service_def.health_check,
                    'resources': service_def.resources,
                    'replicas': service_def.replicas,
                    'restart_policy': service_def.restart_policy,
                    'metadata': service_def.metadata
                }
            }
            
            if format.lower() == "yaml":
                return yaml.dump(config, default_flow_style=False)
            elif format.lower() == "json":
                return json.dumps(config, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
        except Exception as e:
            logger.error(f"Error exporting service config: {e}")
            return ""
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'service': 'Advanced Orchestration Service',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'docker': {
                    'available': self.docker_client is not None,
                    'connected': False
                },
                'services': {
                    'definitions': len(self.service_definitions),
                    'instances': len(self.service_instances),
                    'running_instances': len([i for i in self.service_instances.values() if i.status == ServiceStatus.RUNNING]),
                    'healthy_instances': len([i for i in self.service_instances.values() if i.health_status == "healthy"])
                },
                'deployments': {
                    'total': len(self.deployments),
                    'active': len([d for d in self.deployments.values() if d.status == "running"]),
                    'completed': len([d for d in self.deployments.values() if d.status == "completed"]),
                    'failed': len([d for d in self.deployments.values() if d.status == "failed"])
                },
                'load_balancers': {
                    'total': len(self.load_balancers)
                },
                'queues': {
                    'deployment_queue_size': self.deployment_queue.qsize(),
                    'scaling_queue_size': self.scaling_queue.qsize()
                },
                'health_checks': {
                    'active_checks': len(self.health_check_tasks)
                }
            }
            
            # Test Docker connection
            if self.docker_client:
                try:
                    self.docker_client.ping()
                    status['docker']['connected'] = True
                except:
                    status['docker']['connected'] = False
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'service': 'Advanced Orchestration Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


























