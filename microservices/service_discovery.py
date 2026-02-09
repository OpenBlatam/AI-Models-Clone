"""
Service Discovery Microservice
==============================

This module provides service discovery capabilities for the microservices architecture.
It handles automatic service registration, health checking, and service discovery.

Author: AI Assistant
Version: 10.1
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import logging

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Service status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"

@dataclass
class ServiceInfo:
    """Service information data class."""
    service_id: str
    name: str
    version: str
    host: str
    port: int
    status: ServiceStatus
    health_check_url: str
    metadata: Dict[str, Any]
    last_heartbeat: float
    created_at: float

class ServiceDiscovery:
    """
    Service Discovery implementation for microservices architecture.
    
    Provides automatic service registration, health checking, and service discovery
    with support for load balancing and failover.
    """
    
    def __init__(self, registry_host: str = "localhost", registry_port: int = 8080):
        """
        Initialize the service discovery.
        
        Args:
            registry_host: Host of the service registry
            registry_port: Port of the service registry
        """
        self.registry_host = registry_host
        self.registry_port = registry_port
        self.registry_url = f"http://{registry_host}:{registry_port}"
        self.services: Dict[str, ServiceInfo] = {}
        self.health_check_interval = 30  # seconds
        self.heartbeat_interval = 10  # seconds
        self.service_id = str(uuid.uuid4())
        self.is_running = False
        self._health_check_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        
    async def register_service(self, 
                             name: str, 
                             version: str, 
                             host: str, 
                             port: int,
                             health_check_url: str = "/health",
                             metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a service with the discovery system.
        
        Args:
            name: Service name
            version: Service version
            host: Service host
            port: Service port
            health_check_url: Health check endpoint
            metadata: Additional service metadata
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            service_info = ServiceInfo(
                service_id=self.service_id,
                name=name,
                version=version,
                host=host,
                port=port,
                status=ServiceStatus.STARTING,
                health_check_url=health_check_url,
                metadata=metadata or {},
                last_heartbeat=time.time(),
                created_at=time.time()
            )
            
            self.services[self.service_id] = service_info
            
            # Register with registry
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.registry_url}/services",
                    json=asdict(service_info)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Service {name} registered successfully")
                        return True
                    else:
                        logger.error(f"Failed to register service {name}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error registering service {name}: {e}")
            return False
    
    async def deregister_service(self, service_id: str) -> bool:
        """
        Deregister a service from the discovery system.
        
        Args:
            service_id: Service ID to deregister
            
        Returns:
            True if deregistration successful, False otherwise
        """
        try:
            if service_id in self.services:
                del self.services[service_id]
            
            # Deregister from registry
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.registry_url}/services/{service_id}"
                ) as response:
                    if response.status == 200:
                        logger.info(f"Service {service_id} deregistered successfully")
                        return True
                    else:
                        logger.error(f"Failed to deregister service {service_id}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error deregistering service {service_id}: {e}")
            return False
    
    async def discover_service(self, name: str, version: Optional[str] = None) -> List[ServiceInfo]:
        """
        Discover services by name and optionally version.
        
        Args:
            name: Service name to discover
            version: Optional service version filter
            
        Returns:
            List of matching service information
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.registry_url}/services/{name}"
                if version:
                    url += f"?version={version}"
                    
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [ServiceInfo(**service_data) for service_data in data]
                    else:
                        logger.warning(f"No services found for {name}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error discovering service {name}: {e}")
            return []
    
    async def get_service_health(self, service_id: str) -> Optional[ServiceStatus]:
        """
        Get the health status of a specific service.
        
        Args:
            service_id: Service ID to check
            
        Returns:
            Service status or None if not found
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.registry_url}/services/{service_id}/health"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return ServiceStatus(data.get("status", "unknown"))
                    else:
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting health for service {service_id}: {e}")
            return None
    
    async def _health_check_loop(self):
        """Background health check loop."""
        while self.is_running:
            try:
                for service_id, service_info in self.services.items():
                    # Check if service is still healthy
                    status = await self._check_service_health(service_info)
                    if status != service_info.status:
                        service_info.status = status
                        await self._update_service_status(service_id, status)
                        
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                
            await asyncio.sleep(self.health_check_interval)
    
    async def _heartbeat_loop(self):
        """Background heartbeat loop."""
        while self.is_running:
            try:
                for service_id, service_info in self.services.items():
                    service_info.last_heartbeat = time.time()
                    await self._send_heartbeat(service_id)
                    
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                
            await asyncio.sleep(self.heartbeat_interval)
    
    async def _check_service_health(self, service_info: ServiceInfo) -> ServiceStatus:
        """Check the health of a specific service."""
        try:
            health_url = f"http://{service_info.host}:{service_info.port}{service_info.health_check_url}"
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=5) as response:
                    if response.status == 200:
                        return ServiceStatus.HEALTHY
                    else:
                        return ServiceStatus.UNHEALTHY
                        
        except Exception as e:
            logger.warning(f"Health check failed for {service_info.name}: {e}")
            return ServiceStatus.UNHEALTHY
    
    async def _update_service_status(self, service_id: str, status: ServiceStatus):
        """Update service status in registry."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.registry_url}/services/{service_id}/status",
                    json={"status": status.value}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Updated status for service {service_id} to {status.value}")
                        
        except Exception as e:
            logger.error(f"Error updating status for service {service_id}: {e}")
    
    async def _send_heartbeat(self, service_id: str):
        """Send heartbeat to registry."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.registry_url}/services/{service_id}/heartbeat"
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Heartbeat failed for service {service_id}")
                        
        except Exception as e:
            logger.error(f"Error sending heartbeat for service {service_id}: {e}")
    
    async def start(self):
        """Start the service discovery system."""
        self.is_running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("Service discovery started")
    
    async def stop(self):
        """Stop the service discovery system."""
        self.is_running = False
        
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            
        # Deregister all services
        for service_id in list(self.services.keys()):
            await self.deregister_service(service_id)
            
        logger.info("Service discovery stopped")
    
    def get_service_info(self, service_id: str) -> Optional[ServiceInfo]:
        """Get service information by ID."""
        return self.services.get(service_id)
    
    def list_services(self) -> List[ServiceInfo]:
        """List all registered services."""
        return list(self.services.values())
    
    def get_healthy_services(self, name: str) -> List[ServiceInfo]:
        """Get all healthy services with the given name."""
        return [
            service for service in self.services.values()
            if service.name == name and service.status == ServiceStatus.HEALTHY
        ]


