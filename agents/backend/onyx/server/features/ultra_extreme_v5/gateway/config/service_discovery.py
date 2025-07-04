"""
🚀 ULTRA-EXTREME V5 - SERVICE DISCOVERY
======================================

Ultra-extreme service discovery with:
- Redis-based distributed service registry
- Health monitoring and auto-healing
- Load balancing integration
- Service metadata management
- Real-time service updates
- Circuit breaker integration
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

import redis.asyncio as redis
import httpx
import structlog
from pydantic import BaseModel, Field


class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class ServiceType(Enum):
    """Service type enumeration"""
    CONTENT = "content"
    OPTIMIZATION = "optimization"
    AI = "ai"
    GATEWAY = "gateway"
    DATABASE = "database"
    CACHE = "cache"
    MONITORING = "monitoring"


@dataclass
class ServiceInstance:
    """Service instance data model"""
    id: str
    name: str
    type: ServiceType
    host: str
    port: int
    url: str
    status: ServiceStatus
    health_check_url: str
    metadata: Dict[str, Any]
    created_at: datetime
    last_health_check: datetime
    version: str
    region: str
    zone: str
    load_balancer_weight: float = 1.0
    max_connections: int = 100
    current_connections: int = 0
    response_time_avg: float = 0.0
    error_rate: float = 0.0
    uptime: float = 0.0


class ServiceRegistry(BaseModel):
    """Service registry configuration"""
    redis_url: str = Field(..., description="Redis connection URL")
    registry_key: str = Field(default="service_registry", description="Redis key for service registry")
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    health_check_timeout: int = Field(default=5, description="Health check timeout in seconds")
    service_ttl: int = Field(default=300, description="Service TTL in seconds")
    max_retries: int = Field(default=3, description="Maximum health check retries")
    retry_delay: int = Field(default=5, description="Delay between retries in seconds")


class ServiceDiscovery:
    """Ultra-extreme service discovery"""
    
    def __init__(self, redis_url: str, service_registry_key: str = "service_registry"):
        self.config = ServiceRegistry(
            redis_url=redis_url,
            registry_key=service_registry_key
        )
        self.logger = structlog.get_logger(__name__)
        
        # Redis client
        self.redis_client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Service cache
        self.services_cache: Dict[str, List[ServiceInstance]] = {}
        self.health_status_cache: Dict[str, ServiceStatus] = {}
        
        # Health check tasks
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        self.running = False
        
        # Performance metrics
        self.metrics = {
            "total_services": 0,
            "healthy_services": 0,
            "unhealthy_services": 0,
            "total_health_checks": 0,
            "failed_health_checks": 0,
            "average_response_time": 0.0,
            "last_update": datetime.utcnow()
        }
    
    async def start(self):
        """Start service discovery"""
        self.logger.info("Starting ultra-extreme service discovery")
        self.running = True
        
        # Load existing services from Redis
        await self._load_services_from_redis()
        
        # Start health monitoring
        asyncio.create_task(self._health_monitoring_loop())
        
        # Start metrics collection
        asyncio.create_task(self._metrics_collection_loop())
        
        self.logger.info("Service discovery started successfully")
    
    async def stop(self):
        """Stop service discovery"""
        self.logger.info("Stopping service discovery")
        self.running = False
        
        # Cancel health check tasks
        for task in self.health_check_tasks.values():
            task.cancel()
        
        # Close Redis client
        await self.redis_client.close()
        
        self.logger.info("Service discovery stopped")
    
    async def register_service(self, service_instance: ServiceInstance) -> bool:
        """Register a new service instance"""
        try:
            # Validate service instance
            if not self._validate_service_instance(service_instance):
                return False
            
            # Add to cache
            if service_instance.name not in self.services_cache:
                self.services_cache[service_instance.name] = []
            
            # Check if instance already exists
            existing_instances = self.services_cache[service_instance.name]
            for existing in existing_instances:
                if existing.id == service_instance.id:
                    # Update existing instance
                    existing_instances.remove(existing)
                    break
            
            # Add new instance
            existing_instances.append(service_instance)
            
            # Save to Redis
            await self._save_service_to_redis(service_instance)
            
            # Start health monitoring for this service
            await self._start_health_monitoring(service_instance)
            
            self.logger.info(
                "Service registered successfully",
                service_name=service_instance.name,
                instance_id=service_instance.id,
                url=service_instance.url
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "Failed to register service",
                service_name=service_instance.name,
                error=str(e)
            )
            return False
    
    async def deregister_service(self, service_name: str, instance_id: str) -> bool:
        """Deregister a service instance"""
        try:
            if service_name in self.services_cache:
                instances = self.services_cache[service_name]
                instances = [inst for inst in instances if inst.id != instance_id]
                
                if not instances:
                    del self.services_cache[service_name]
                else:
                    self.services_cache[service_name] = instances
            
            # Remove from Redis
            await self._remove_service_from_redis(service_name, instance_id)
            
            # Stop health monitoring
            task_key = f"{service_name}:{instance_id}"
            if task_key in self.health_check_tasks:
                self.health_check_tasks[task_key].cancel()
                del self.health_check_tasks[task_key]
            
            self.logger.info(
                "Service deregistered successfully",
                service_name=service_name,
                instance_id=instance_id
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "Failed to deregister service",
                service_name=service_name,
                instance_id=instance_id,
                error=str(e)
            )
            return False
    
    async def get_service_instances(self, service_name: str) -> List[ServiceInstance]:
        """Get all instances of a service"""
        try:
            # Get from cache first
            if service_name in self.services_cache:
                instances = self.services_cache[service_name]
                # Filter healthy instances
                healthy_instances = [
                    inst for inst in instances
                    if inst.status == ServiceStatus.HEALTHY
                ]
                return healthy_instances
            
            # Try to load from Redis
            await self._load_service_from_redis(service_name)
            
            if service_name in self.services_cache:
                instances = self.services_cache[service_name]
                healthy_instances = [
                    inst for inst in instances
                    if inst.status == ServiceStatus.HEALTHY
                ]
                return healthy_instances
            
            return []
            
        except Exception as e:
            self.logger.error(
                "Failed to get service instances",
                service_name=service_name,
                error=str(e)
            )
            return []
    
    async def get_available_services(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all available services"""
        try:
            services = {}
            for service_name, instances in self.services_cache.items():
                healthy_instances = [
                    inst for inst in instances
                    if inst.status == ServiceStatus.HEALTHY
                ]
                
                services[service_name] = [
                    {
                        "id": inst.id,
                        "url": inst.url,
                        "host": inst.host,
                        "port": inst.port,
                        "status": inst.status.value,
                        "version": inst.version,
                        "region": inst.region,
                        "zone": inst.zone,
                        "load_balancer_weight": inst.load_balancer_weight,
                        "current_connections": inst.current_connections,
                        "response_time_avg": inst.response_time_avg,
                        "error_rate": inst.error_rate,
                        "uptime": inst.uptime,
                        "last_health_check": inst.last_health_check.isoformat()
                    }
                    for inst in healthy_instances
                ]
            
            return services
            
        except Exception as e:
            self.logger.error("Failed to get available services", error=str(e))
            return {}
    
    async def get_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all services"""
        try:
            health_status = {}
            for service_name, instances in self.services_cache.items():
                total_instances = len(instances)
                healthy_instances = len([
                    inst for inst in instances
                    if inst.status == ServiceStatus.HEALTHY
                ])
                
                health_status[service_name] = {
                    "total_instances": total_instances,
                    "healthy_instances": healthy_instances,
                    "unhealthy_instances": total_instances - healthy_instances,
                    "health_percentage": (healthy_instances / total_instances * 100) if total_instances > 0 else 0,
                    "instances": [
                        {
                            "id": inst.id,
                            "status": inst.status.value,
                            "last_health_check": inst.last_health_check.isoformat(),
                            "response_time_avg": inst.response_time_avg,
                            "error_rate": inst.error_rate
                        }
                        for inst in instances
                    ]
                }
            
            return health_status
            
        except Exception as e:
            self.logger.error("Failed to get services health", error=str(e))
            return {}
    
    async def check_services_health(self) -> Dict[str, Any]:
        """Check health of all services"""
        try:
            unhealthy_services = []
            total_services = 0
            healthy_services = 0
            
            for service_name, instances in self.services_cache.items():
                total_services += len(instances)
                service_healthy = True
                
                for instance in instances:
                    if instance.status != ServiceStatus.HEALTHY:
                        service_healthy = False
                        unhealthy_services.append({
                            "service_name": service_name,
                            "instance_id": instance.id,
                            "status": instance.status.value,
                            "url": instance.url
                        })
                    else:
                        healthy_services += 1
            
            return {
                "total_services": total_services,
                "healthy_services": healthy_services,
                "unhealthy_services": len(unhealthy_services),
                "unhealthy_services_list": unhealthy_services,
                "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0
            }
            
        except Exception as e:
            self.logger.error("Failed to check services health", error=str(e))
            return {
                "total_services": 0,
                "healthy_services": 0,
                "unhealthy_services": 0,
                "unhealthy_services_list": [],
                "health_percentage": 0
            }
    
    def _validate_service_instance(self, service_instance: ServiceInstance) -> bool:
        """Validate service instance"""
        if not service_instance.id or not service_instance.name:
            return False
        
        if not service_instance.host or not service_instance.port:
            return False
        
        if not service_instance.url:
            return False
        
        return True
    
    async def _save_service_to_redis(self, service_instance: ServiceInstance):
        """Save service instance to Redis"""
        try:
            service_key = f"{self.config.registry_key}:{service_instance.name}:{service_instance.id}"
            service_data = {
                "id": service_instance.id,
                "name": service_instance.name,
                "type": service_instance.type.value,
                "host": service_instance.host,
                "port": service_instance.port,
                "url": service_instance.url,
                "status": service_instance.status.value,
                "health_check_url": service_instance.health_check_url,
                "metadata": json.dumps(service_instance.metadata),
                "created_at": service_instance.created_at.isoformat(),
                "last_health_check": service_instance.last_health_check.isoformat(),
                "version": service_instance.version,
                "region": service_instance.region,
                "zone": service_instance.zone,
                "load_balancer_weight": str(service_instance.load_balancer_weight),
                "max_connections": str(service_instance.max_connections),
                "current_connections": str(service_instance.current_connections),
                "response_time_avg": str(service_instance.response_time_avg),
                "error_rate": str(service_instance.error_rate),
                "uptime": str(service_instance.uptime)
            }
            
            await self.redis_client.hset(service_key, mapping=service_data)
            await self.redis_client.expire(service_key, self.config.service_ttl)
            
        except Exception as e:
            self.logger.error("Failed to save service to Redis", error=str(e))
    
    async def _remove_service_from_redis(self, service_name: str, instance_id: str):
        """Remove service instance from Redis"""
        try:
            service_key = f"{self.config.registry_key}:{service_name}:{instance_id}"
            await self.redis_client.delete(service_key)
        except Exception as e:
            self.logger.error("Failed to remove service from Redis", error=str(e))
    
    async def _load_services_from_redis(self):
        """Load all services from Redis"""
        try:
            pattern = f"{self.config.registry_key}:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                service_data = await self.redis_client.hgetall(key)
                if service_data:
                    service_instance = self._create_service_instance_from_data(service_data)
                    if service_instance:
                        if service_instance.name not in self.services_cache:
                            self.services_cache[service_instance.name] = []
                        self.services_cache[service_instance.name].append(service_instance)
            
            self.logger.info(f"Loaded {len(keys)} services from Redis")
            
        except Exception as e:
            self.logger.error("Failed to load services from Redis", error=str(e))
    
    async def _load_service_from_redis(self, service_name: str):
        """Load specific service from Redis"""
        try:
            pattern = f"{self.config.registry_key}:{service_name}:*"
            keys = await self.redis_client.keys(pattern)
            
            instances = []
            for key in keys:
                service_data = await self.redis_client.hgetall(key)
                if service_data:
                    service_instance = self._create_service_instance_from_data(service_data)
                    if service_instance:
                        instances.append(service_instance)
            
            if instances:
                self.services_cache[service_name] = instances
            
        except Exception as e:
            self.logger.error("Failed to load service from Redis", error=str(e))
    
    def _create_service_instance_from_data(self, data: Dict[str, str]) -> Optional[ServiceInstance]:
        """Create service instance from Redis data"""
        try:
            return ServiceInstance(
                id=data.get("id", ""),
                name=data.get("name", ""),
                type=ServiceType(data.get("type", "unknown")),
                host=data.get("host", ""),
                port=int(data.get("port", 0)),
                url=data.get("url", ""),
                status=ServiceStatus(data.get("status", "unknown")),
                health_check_url=data.get("health_check_url", ""),
                metadata=json.loads(data.get("metadata", "{}")),
                created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
                last_health_check=datetime.fromisoformat(data.get("last_health_check", datetime.utcnow().isoformat())),
                version=data.get("version", "1.0.0"),
                region=data.get("region", "default"),
                zone=data.get("zone", "default"),
                load_balancer_weight=float(data.get("load_balancer_weight", "1.0")),
                max_connections=int(data.get("max_connections", "100")),
                current_connections=int(data.get("current_connections", "0")),
                response_time_avg=float(data.get("response_time_avg", "0.0")),
                error_rate=float(data.get("error_rate", "0.0")),
                uptime=float(data.get("uptime", "0.0"))
            )
        except Exception as e:
            self.logger.error("Failed to create service instance from data", error=str(e))
            return None
    
    async def _start_health_monitoring(self, service_instance: ServiceInstance):
        """Start health monitoring for a service instance"""
        task_key = f"{service_instance.name}:{service_instance.id}"
        
        if task_key not in self.health_check_tasks:
            task = asyncio.create_task(
                self._health_check_loop_for_service(service_instance)
            )
            self.health_check_tasks[task_key] = task
    
    async def _health_monitoring_loop(self):
        """Main health monitoring loop"""
        while self.running:
            try:
                # Perform health checks for all services
                for service_name, instances in self.services_cache.items():
                    for instance in instances:
                        await self._perform_health_check(instance)
                
                # Update metrics
                await self._update_metrics()
                
                # Wait for next check
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                self.logger.error("Health monitoring error", error=str(e))
                await asyncio.sleep(60)
    
    async def _health_check_loop_for_service(self, service_instance: ServiceInstance):
        """Health check loop for specific service"""
        while self.running:
            try:
                await self._perform_health_check(service_instance)
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                self.logger.error(
                    "Service health check error",
                    service_name=service_instance.name,
                    instance_id=service_instance.id,
                    error=str(e)
                )
                await asyncio.sleep(self.config.retry_delay)
    
    async def _perform_health_check(self, service_instance: ServiceInstance):
        """Perform health check for service instance"""
        try:
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=self.config.health_check_timeout) as client:
                response = await client.get(service_instance.health_check_url)
                
                response_time = time.time() - start_time
                
                # Update service instance
                service_instance.last_health_check = datetime.utcnow()
                service_instance.response_time_avg = (
                    (service_instance.response_time_avg + response_time) / 2
                )
                
                if response.status_code == 200:
                    service_instance.status = ServiceStatus.HEALTHY
                    service_instance.error_rate = max(0, service_instance.error_rate - 0.1)
                else:
                    service_instance.status = ServiceStatus.UNHEALTHY
                    service_instance.error_rate = min(1.0, service_instance.error_rate + 0.2)
                
                # Save to Redis
                await self._save_service_to_redis(service_instance)
                
                self.metrics["total_health_checks"] += 1
                
        except Exception as e:
            service_instance.status = ServiceStatus.UNHEALTHY
            service_instance.error_rate = min(1.0, service_instance.error_rate + 0.3)
            service_instance.last_health_check = datetime.utcnow()
            
            await self._save_service_to_redis(service_instance)
            
            self.metrics["failed_health_checks"] += 1
            
            self.logger.warning(
                "Health check failed",
                service_name=service_instance.name,
                instance_id=service_instance.id,
                error=str(e)
            )
    
    async def _metrics_collection_loop(self):
        """Metrics collection loop"""
        while self.running:
            try:
                await self._update_metrics()
                await asyncio.sleep(60)  # Update metrics every minute
            except Exception as e:
                self.logger.error("Metrics collection error", error=str(e))
                await asyncio.sleep(60)
    
    async def _update_metrics(self):
        """Update performance metrics"""
        try:
            total_services = 0
            healthy_services = 0
            total_response_time = 0.0
            response_time_count = 0
            
            for service_name, instances in self.services_cache.items():
                total_services += len(instances)
                
                for instance in instances:
                    if instance.status == ServiceStatus.HEALTHY:
                        healthy_services += 1
                    
                    if instance.response_time_avg > 0:
                        total_response_time += instance.response_time_avg
                        response_time_count += 1
            
            self.metrics.update({
                "total_services": total_services,
                "healthy_services": healthy_services,
                "unhealthy_services": total_services - healthy_services,
                "average_response_time": total_response_time / response_time_count if response_time_count > 0 else 0.0,
                "last_update": datetime.utcnow()
            })
            
        except Exception as e:
            self.logger.error("Failed to update metrics", error=str(e))
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy() 