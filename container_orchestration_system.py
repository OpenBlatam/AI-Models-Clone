"""
Sistema de Orquestación de Contenedores para Arquitectura Modular
Integra Docker y Kubernetes con el sistema de microservicios existente
"""

import asyncio
import docker
import json
import logging
import time
import yaml
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
import subprocess
import os
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContainerStatus(Enum):
    """Estados de los contenedores."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    EXITED = "exited"
    DEAD = "dead"

class ServiceType(Enum):
    """Tipos de servicios en contenedores."""
    WEB = "web"
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    WORKER = "worker"
    MONITORING = "monitoring"
    LOGGING = "logging"

@dataclass
class ContainerConfig:
    """Configuración de contenedor."""
    name: str
    image: str
    service_type: ServiceType
    ports: Dict[str, str] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    networks: List[str] = field(default_factory=list)
    restart_policy: str = "unless-stopped"
    memory_limit: str = "512m"
    cpu_limit: str = "0.5"
    health_check: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)

@dataclass
class ContainerInfo:
    """Información del contenedor."""
    id: str
    name: str
    status: ContainerStatus
    image: str
    ports: Dict[str, str]
    created: str
    state: str
    health: Optional[str] = None
    logs: List[str] = field(default_factory=list)

class ContainerManager:
    """Gestor de contenedores Docker."""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.containers: Dict[str, ContainerInfo] = {}
            self.running = False
            logger.info("✅ Cliente Docker conectado")
        except Exception as e:
            logger.error(f"❌ Error conectando a Docker: {e}")
            self.client = None
    
    async def start(self):
        """Iniciar gestor de contenedores."""
        if not self.client:
            logger.error("Cliente Docker no disponible")
            return False
        
        self.running = True
        logger.info("🚀 Gestor de contenedores iniciado")
        
        # Actualizar estado de contenedores existentes
        await self._update_containers_status()
        
        return True
    
    async def stop(self):
        """Detener gestor de contenedores."""
        self.running = False
        logger.info("🛑 Gestor de contenedores detenido")
    
    async def create_container(self, config: ContainerConfig) -> Optional[ContainerInfo]:
        """Crear y ejecutar un contenedor."""
        if not self.client:
            logger.error("Cliente Docker no disponible")
            return None
        
        try:
            # Configurar puertos
            port_bindings = {}
            for container_port, host_port in config.ports.items():
                port_bindings[container_port] = host_port
            
            # Configurar volúmenes
            volume_bindings = {}
            for volume in config.volumes:
                if ':' in volume:
                    host_path, container_path = volume.split(':', 1)
                    volume_bindings[host_path] = {'bind': container_path, 'mode': 'rw'}
            
            # Crear contenedor
            container = self.client.containers.run(
                image=config.image,
                name=config.name,
                ports=port_bindings,
                environment=config.environment,
                volumes=volume_bindings,
                networks=config.networks,
                restart_policy={"Name": config.restart_policy},
                mem_limit=config.memory_limit,
                cpu_period=100000,
                cpu_quota=int(float(config.cpu_limit) * 100000),
                detach=True,
                healthcheck=config.health_check
            )
            
            # Crear información del contenedor
            container_info = ContainerInfo(
                id=container.id,
                name=config.name,
                status=ContainerStatus.CREATED,
                image=config.image,
                ports=config.ports,
                created=container.attrs['Created'],
                state=container.attrs['State']['Status']
            )
            
            self.containers[config.name] = container_info
            logger.info(f"✅ Contenedor creado: {config.name}")
            
            return container_info
            
        except Exception as e:
            logger.error(f"Error creando contenedor {config.name}: {e}")
            return None
    
    async def start_container(self, container_name: str) -> bool:
        """Iniciar un contenedor existente."""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(container_name)
            container.start()
            
            # Actualizar estado
            if container_name in self.containers:
                self.containers[container_name].status = ContainerStatus.RUNNING
                self.containers[container_name].state = "running"
            
            logger.info(f"✅ Contenedor iniciado: {container_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando contenedor {container_name}: {e}")
            return False
    
    async def stop_container(self, container_name: str) -> bool:
        """Detener un contenedor."""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            
            # Actualizar estado
            if container_name in self.containers:
                self.containers[container_name].status = ContainerStatus.EXITED
                self.containers[container_name].state = "exited"
            
            logger.info(f"✅ Contenedor detenido: {container_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deteniendo contenedor {container_name}: {e}")
            return False
    
    async def remove_container(self, container_name: str) -> bool:
        """Eliminar un contenedor."""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(container_name)
            container.remove(force=True)
            
            # Remover de la lista
            if container_name in self.containers:
                del self.containers[container_name]
            
            logger.info(f"✅ Contenedor eliminado: {container_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando contenedor {container_name}: {e}")
            return False
    
    async def get_container_logs(self, container_name: str, tail: int = 100) -> List[str]:
        """Obtener logs de un contenedor."""
        if not self.client:
            return []
        
        try:
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=tail).decode('utf-8').split('\n')
            
            # Actualizar logs en la información del contenedor
            if container_name in self.containers:
                self.containers[container_name].logs = logs
            
            return logs
            
        except Exception as e:
            logger.error(f"Error obteniendo logs de {container_name}: {e}")
            return []
    
    async def get_container_stats(self, container_name: str) -> Optional[Dict[str, Any]]:
        """Obtener estadísticas de un contenedor."""
        if not self.client:
            return None
        
        try:
            container = self.client.containers.get(container_name)
            stats = container.stats(stream=False)
            
            # Procesar estadísticas
            cpu_stats = stats['cpu_stats']
            memory_stats = stats['memory_stats']
            
            return {
                'cpu_usage_percent': self._calculate_cpu_percent(stats),
                'memory_usage_bytes': memory_stats.get('usage', 0),
                'memory_limit_bytes': memory_stats.get('limit', 0),
                'network_rx_bytes': stats['networks']['eth0']['rx_bytes'],
                'network_tx_bytes': stats['networks']['eth0']['tx_bytes'],
                'block_read_bytes': stats['blkio_stats']['io_service_bytes_recursive'][0]['value'],
                'block_write_bytes': stats['blkio_stats']['io_service_bytes_recursive'][1]['value']
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de {container_name}: {e}")
            return None
    
    def _calculate_cpu_percent(self, stats: Dict[str, Any]) -> float:
        """Calcular porcentaje de CPU."""
        try:
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            
            if system_delta > 0 and cpu_delta > 0:
                return (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
            
            return 0.0
            
        except (KeyError, ZeroDivisionError):
            return 0.0
    
    async def _update_containers_status(self):
        """Actualizar estado de todos los contenedores."""
        if not self.client:
            return
        
        try:
            for container in self.client.containers.list(all=True):
                container_name = container.name
                
                # Crear o actualizar información del contenedor
                container_info = ContainerInfo(
                    id=container.id,
                    name=container_name,
                    status=ContainerStatus(container.status),
                    image=container.image.tags[0] if container.image.tags else container.image.id,
                    ports=container.ports,
                    created=container.attrs['Created'],
                    state=container.attrs['State']['Status'],
                    health=container.attrs['State'].get('Health', {}).get('Status')
                )
                
                self.containers[container_name] = container_info
            
            logger.info(f"✅ Estado de {len(self.containers)} contenedores actualizado")
            
        except Exception as e:
            logger.error(f"Error actualizando estado de contenedores: {e}")
    
    def get_all_containers(self) -> Dict[str, ContainerInfo]:
        """Obtener información de todos los contenedores."""
        return self.containers.copy()
    
    def get_container_info(self, container_name: str) -> Optional[ContainerInfo]:
        """Obtener información de un contenedor específico."""
        return self.containers.get(container_name)

class KubernetesManager:
    """Gestor de Kubernetes para orquestación avanzada."""
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        self.kubeconfig_path = kubeconfig_path
        self.running = False
        self.namespace = "default"
        
        # Verificar si kubectl está disponible
        self._check_kubectl()
    
    def _check_kubectl(self):
        """Verificar si kubectl está disponible."""
        try:
            result = subprocess.run(['kubectl', 'version', '--client'], 
                                  capture_output=True, text=True, check=True)
            logger.info("✅ kubectl disponible")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("⚠️ kubectl no disponible")
    
    async def start(self):
        """Iniciar gestor de Kubernetes."""
        self.running = True
        logger.info("🚀 Gestor de Kubernetes iniciado")
    
    async def stop(self):
        """Detener gestor de Kubernetes."""
        self.running = False
        logger.info("🛑 Gestor de Kubernetes detenido")
    
    async def create_deployment(self, name: str, image: str, replicas: int = 1, 
                               ports: List[int] = None, env_vars: Dict[str, str] = None) -> bool:
        """Crear un deployment en Kubernetes."""
        try:
            # Crear archivo YAML del deployment
            deployment_yaml = self._create_deployment_yaml(name, image, replicas, ports, env_vars)
            
            # Aplicar deployment
            result = await self._apply_yaml(deployment_yaml)
            
            if result:
                logger.info(f"✅ Deployment creado: {name}")
                return True
            else:
                logger.error(f"❌ Error creando deployment: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error creando deployment {name}: {e}")
            return False
    
    def _create_deployment_yaml(self, name: str, image: str, replicas: int,
                               ports: List[int], env_vars: Dict[str, str]) -> str:
        """Crear YAML para deployment."""
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': name,
                'namespace': self.namespace
            },
            'spec': {
                'replicas': replicas,
                'selector': {
                    'matchLabels': {
                        'app': name
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': name
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': name,
                            'image': image,
                            'ports': [{'containerPort': port} for port in (ports or [80])],
                            'env': [{'name': k, 'value': v} for k, v in (env_vars or {}).items()]
                        }]
                    }
                }
            }
        }
        
        return yaml.dump(deployment, default_flow_style=False)
    
    async def _apply_yaml(self, yaml_content: str) -> bool:
        """Aplicar YAML a Kubernetes."""
        try:
            # Crear archivo temporal
            temp_file = Path(f"/tmp/k8s_{int(time.time())}.yaml")
            temp_file.write_text(yaml_content)
            
            # Aplicar con kubectl
            result = subprocess.run(['kubectl', 'apply', '-f', str(temp_file)],
                                  capture_output=True, text=True, check=True)
            
            # Limpiar archivo temporal
            temp_file.unlink()
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error aplicando YAML: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error aplicando YAML: {e}")
            return False
    
    async def scale_deployment(self, name: str, replicas: int) -> bool:
        """Escalar un deployment."""
        try:
            result = subprocess.run(['kubectl', 'scale', 'deployment', name, 
                                   f'--replicas={replicas}', '-n', self.namespace],
                                  capture_output=True, text=True, check=True)
            
            logger.info(f"✅ Deployment {name} escalado a {replicas} réplicas")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error escalando deployment {name}: {e.stderr}")
            return False
    
    async def get_pods(self, namespace: str = None) -> List[Dict[str, Any]]:
        """Obtener pods de un namespace."""
        try:
            ns = namespace or self.namespace
            result = subprocess.run(['kubectl', 'get', 'pods', '-n', ns, '-o', 'json'],
                                  capture_output=True, text=True, check=True)
            
            pods_data = json.loads(result.stdout)
            return pods_data.get('items', [])
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error obteniendo pods: {e.stderr}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando respuesta: {e}")
            return []

class ContainerOrchestrator:
    """Orquestador principal de contenedores."""
    
    def __init__(self):
        self.docker_manager = ContainerManager()
        self.k8s_manager = KubernetesManager()
        self.running = False
        self.services: Dict[str, ContainerConfig] = {}
        
        # Configurar servicios por defecto
        self._setup_default_services()
    
    def _setup_default_services(self):
        """Configurar servicios por defecto."""
        # Servicio web
        web_service = ContainerConfig(
            name="web-service",
            image="nginx:alpine",
            service_type=ServiceType.WEB,
            ports={"80": "8080"},
            environment={"NGINX_HOST": "localhost"},
            volumes=["/tmp/nginx:/etc/nginx/conf.d"],
            networks=["bridge"]
        )
        
        # Servicio API
        api_service = ContainerConfig(
            name="api-service",
            image="python:3.9-slim",
            service_type=ServiceType.API,
            ports={"8000": "8001"},
            environment={"PYTHONPATH": "/app"},
            volumes=["/tmp/api:/app"],
            networks=["bridge"]
        )
        
        # Servicio de base de datos
        db_service = ContainerConfig(
            name="db-service",
            image="postgres:13",
            service_type=ServiceType.DATABASE,
            ports={"5432": "5432"},
            environment={
                "POSTGRES_DB": "appdb",
                "POSTGRES_USER": "user",
                "POSTGRES_PASSWORD": "password"
            },
            volumes=["/tmp/postgres:/var/lib/postgresql/data"],
            networks=["bridge"]
        )
        
        self.services["web-service"] = web_service
        self.services["api-service"] = api_service
        self.services["db-service"] = db_service
    
    async def start(self):
        """Iniciar orquestador de contenedores."""
        if self.running:
            return
        
        logger.info("🚀 Iniciando orquestador de contenedores...")
        
        # Iniciar gestores
        await self.docker_manager.start()
        await self.k8s_manager.start()
        
        self.running = True
        logger.info("✅ Orquestador de contenedores iniciado")
    
    async def stop(self):
        """Detener orquestador de contenedores."""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo orquestador de contenedores...")
        
        # Detener gestores
        await self.docker_manager.stop()
        await self.k8s_manager.stop()
        
        self.running = False
        logger.info("✅ Orquestador de contenedores detenido")
    
    async def deploy_service(self, service_name: str) -> bool:
        """Desplegar un servicio."""
        if service_name not in self.services:
            logger.error(f"Servicio {service_name} no encontrado")
            return False
        
        service_config = self.services[service_name]
        
        try:
            # Crear contenedor Docker
            container_info = await self.docker_manager.create_container(service_config)
            
            if container_info:
                logger.info(f"✅ Servicio {service_name} desplegado")
                return True
            else:
                logger.error(f"❌ Error desplegando servicio {service_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error desplegando servicio {service_name}: {e}")
            return False
    
    async def deploy_all_services(self) -> Dict[str, bool]:
        """Desplegar todos los servicios."""
        results = {}
        
        for service_name in self.services:
            results[service_name] = await self.deploy_service(service_name)
        
        return results
    
    async def scale_service(self, service_name: str, replicas: int) -> bool:
        """Escalar un servicio."""
        try:
            # Para Docker, crear múltiples contenedores
            if service_name in self.services:
                for i in range(replicas):
                    config = self.services[service_name]
                    config.name = f"{service_name}-{i+1}"
                    await self.docker_manager.create_container(config)
                
                logger.info(f"✅ Servicio {service_name} escalado a {replicas} réplicas")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error escalando servicio {service_name}: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema de contenedores."""
        return {
            'orchestrator_running': self.running,
            'docker_containers': len(self.docker_manager.get_all_containers()),
            'services_configured': len(self.services),
            'containers_info': {
                name: {
                    'status': info.status.value,
                    'state': info.state,
                    'health': info.health
                }
                for name, info in self.docker_manager.get_all_containers().items()
            }
        }

async def run_container_orchestration_demo():
    """Ejecutar demostración del sistema de orquestación de contenedores."""
    logger.info("🎯 Iniciando demostración del sistema de orquestación de contenedores...")
    
    # Crear orquestador
    orchestrator = ContainerOrchestrator()
    
    try:
        # Iniciar orquestador
        await orchestrator.start()
        
        # Simular operaciones
        await asyncio.sleep(2)
        
        # Obtener estado del sistema
        status = orchestrator.get_system_status()
        logger.info(f"Estado del sistema: {json.dumps(status, indent=2)}")
        
        # Desplegar servicios
        logger.info("🚀 Desplegando servicios...")
        results = await orchestrator.deploy_all_services()
        
        for service, success in results.items():
            if success:
                logger.info(f"✅ {service} desplegado exitosamente")
            else:
                logger.error(f"❌ {service} falló al desplegar")
        
        # Mantener sistema ejecutándose
        await asyncio.sleep(10)
        
    finally:
        # Detener orquestador
        await orchestrator.stop()
    
    logger.info("✅ Demostración del sistema de orquestación de contenedores completada")

if __name__ == "__main__":
    # Ejecutar demostración
    asyncio.run(run_container_orchestration_demo())
