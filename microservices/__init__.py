"""
Microservices Architecture Package
=================================

This package contains the microservices implementation for the Instagram Captions API v10.0.
It provides service discovery, API gateway, load balancing, and distributed tracing capabilities.

Author: AI Assistant
Version: 10.1
"""

from .service_discovery import ServiceDiscovery
from .api_gateway import APIGateway
from .load_balancer import LoadBalancer
from .service_mesh import ServiceMesh
from .distributed_tracing import DistributedTracing

__all__ = [
    'ServiceDiscovery',
    'APIGateway', 
    'LoadBalancer',
    'ServiceMesh',
    'DistributedTracing'
]

__version__ = "10.1.0"


